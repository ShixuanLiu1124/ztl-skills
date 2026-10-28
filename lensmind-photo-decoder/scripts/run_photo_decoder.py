import argparse
import json
import subprocess
import sys
from pathlib import Path


def find_image(samples_dir, image_id):
    for directory in samples_dir.iterdir():
        if not directory.is_dir():
            continue
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = directory / f"{image_id}{ext}"
            if candidate.exists():
                return candidate
    return None


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def first_annotation(annotations, *categories):
    wanted = set(categories)
    for item in annotations:
        if item.get("category") in wanted:
            return item
    return {}


def annotations_by_category(annotations, *categories):
    wanted = set(categories)
    return [item for item in annotations if item.get("category") in wanted]


def line(label, text):
    return f"- {label}: {text}" if text else ""


def join_nonempty(lines):
    return "\n".join(item for item in lines if item)


def palette_text(palette):
    parts = []
    for item in palette:
        if isinstance(item, dict):
            parts.append(f"{item.get('name', '')} {item.get('hex', '')}".strip())
    return " / ".join(parts)


def read_optional_text(path):
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig").strip()


def estimate_line(estimates, key, label):
    item = estimates.get(key, {})
    if not isinstance(item, dict):
        return ""
    value = item.get("value", "")
    confidence = item.get("confidence", "")
    note = item.get("note", "")
    if not value and not note:
        return ""
    suffix = []
    if confidence:
        suffix.append(f"confidence: {confidence}")
    if note:
        suffix.append(f"basis: {note}")
    return f"- {label}: {value}" + (f" ({'; '.join(suffix)})" if suffix else "")


def write_report(root, image_id, image_path, json_path, output_path, analysis_file=None):
    data = load_json(json_path)
    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{image_id}-analysis.md"

    style = data.get("style_summary", {})
    shooting = data.get("shooting_summary", {})
    light_analysis = data.get("light_analysis", {})
    technical = data.get("technical_estimate", {})
    annotations = data.get("annotations", [])

    light = first_annotation(annotations, "light_direction")
    subject = first_annotation(annotations, "subject_position")
    camera = first_annotation(annotations, "camera_position")
    pose = first_annotation(annotations, "pose_direction")
    composition_items = annotations_by_category(annotations, "composition_line", "negative_space")

    light_direction = light_analysis.get("direction") or light.get("description", "")
    light_evidence = light_analysis.get("evidence", "")
    light_adjustment = light_analysis.get("shooting_adjustment", "")
    light_confidence = light_analysis.get("confidence", "")

    composition_lines = [
        f"- {item.get('label', 'composition')}: {item.get('description', '')}"
        for item in composition_items[:3]
    ]
    annotation_lines = [
        f"- {item.get('label', '')}: {item.get('description', '')}".strip()
        for item in annotations[:6]
        if item.get("label") or item.get("description")
    ]
    parameter_lines = join_nonempty([
        estimate_line(technical, "focal_length", "focal length"),
        estimate_line(technical, "aperture", "aperture"),
        estimate_line(technical, "shutter_speed", "shutter speed"),
        estimate_line(technical, "iso", "ISO"),
        estimate_line(technical, "white_balance", "white balance"),
    ])
    if not parameter_lines:
        parameter_lines = "- focal length / aperture / shutter / ISO: not estimated yet; add `technical_estimate` with confidence when visible."

    optional_analysis = read_optional_text(analysis_file)

    report = f"""# {image_id} Photo Decoder Report

## 1. Summary

{style.get("label", "Untitled style")}

{style.get("description", "")}

## 2. Why It Works

{join_nonempty([
    line("composition", subject.get("description", "")),
    line("light", light_direction or f'{shooting.get("light_temperature", "")}, {shooting.get("light_quality", "")}'.strip(", ")),
    line("space", " ".join(item.get("description", "") for item in composition_items[:2]).strip()),
])}

## 3. How To Shoot

- scene: {style.get("shooting_hint", "")}
- subject position: {subject.get("description", "")}
- camera position: {camera.get("description", "")}
- framing: {shooting.get("framing", "")}; {shooting.get("camera_angle", "")}; {shooting.get("camera_distance", "")}
- light: {shooting.get("light_temperature", "")}; {shooting.get("light_quality", "")}

## 4. Light

- direction: {light_direction or "Needs image-level judgment."}
- confidence: {light_confidence or "not set"}
- basis: {light_evidence or "not set"}
- temperature: {shooting.get("light_temperature", "")}
- quality: {shooting.get("light_quality", "")}
- shooting adjustment: {light_adjustment or "Turn the face toward the main light first, then adjust camera position or add gentle fill."}

## 5. Composition And Camera

{join_nonempty(composition_lines)}
- camera: {camera.get("description", "")}
- framing: {shooting.get("framing", "")}

## 6. Pose And Direction

- pose: {pose.get("description", "")}
- field direction: Relax the body, turn slightly with the light or scene line, keep hands soft, and avoid staring stiffly into the lens.

## 7. Color And Post

- palette: {palette_text(style.get("palette", []))}
- post direction: Keep the main color mood, control saturation and contrast, and separate skin tone from environment color.

## 8. Technical Estimate

- lens feel: {shooting.get("lens_feel", "")}
{parameter_lines}

## 9. Booking Fit

- fit: portrait / mood portrait / location-based content / style-library reference.
- shoot planner: suitable after adding exact location, time, wardrobe, and on-set prompts.

## 10. Annotation Summary

{chr(10).join(annotation_lines)}

## 11. Extra Notes

{optional_analysis if optional_analysis else f"No extra notes. For fuller step 1-3 analysis, save notes to reports/{image_id}-notes.md and rerun."}

## Files

- image: {image_path}
- json: {json_path}
- annotated image: {output_path}

## Visual Check

- face overlap: pending manual check
- bottom panel: pending manual check
- labels readable: pending manual check
- arrows understandable: pending manual check
- style summary useful: pending manual check
"""
    report_path.write_text(report, encoding="utf-8")
    return report_path


def run(cmd):
    completed = subprocess.run(cmd, check=False, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main():
    parser = argparse.ArgumentParser(description="Run one LensMind Photo Decoder sample.")
    parser.add_argument("image_id", help="Sample image_id, for example portrait-3.")
    parser.add_argument("--root", default=".", help="LensMind workspace root.")
    parser.add_argument("--skip-render", action="store_true", help="Only validate and write the text report.")
    parser.add_argument("--analysis-file", help="Optional markdown/text analysis to embed in the report.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    image_path = find_image(root / "samples", args.image_id)
    json_path = root / "annotations" / f"{args.image_id}.json"
    output_path = root / "outputs" / "annotations" / f"{args.image_id}-annotated.jpg"
    analysis_file = Path(args.analysis_file) if args.analysis_file else root / "reports" / f"{args.image_id}-notes.md"

    if image_path is None:
        raise SystemExit(f"Image not found for image_id={args.image_id}")
    if not json_path.exists():
        raise SystemExit(f"JSON not found: {json_path}")

    script_dir = Path(__file__).resolve().parent
    python = sys.executable
    run([python, str(script_dir / "validate_annotations.py"), "--root", str(root), "--image-id", args.image_id])
    if not args.skip_render:
        run([python, str(script_dir / "render_annotations.py"), "--root", str(root), "--image-id", args.image_id])

    report_path = write_report(
        root,
        args.image_id,
        image_path,
        json_path,
        output_path if output_path.exists() else "",
        analysis_file if analysis_file.exists() else None,
    )
    print(f"report: {report_path}")
    if output_path.exists():
        print(f"annotated: {output_path}")


if __name__ == "__main__":
    main()
