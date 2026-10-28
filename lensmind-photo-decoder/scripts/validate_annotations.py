import argparse
import json
from pathlib import Path


ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_TYPES = {"arrow", "point", "line", "rect", "polygon", "polyline", "camera_position"}
REQUIRED_ANNOTATION_FIELDS = {"id", "type", "category", "label", "description", "confidence", "coordinates"}
REQUIRED_RENDERING_RULES = {
    "coordinate_system",
    "max_annotations",
    "avoid_face_overlap",
    "confidence_enum",
    "show_label_on_image",
    "show_description_on_hover",
}
REQUIRED_STYLE_FIELDS = {"label", "description", "palette", "shooting_hint"}
REQUIRED_SHOOTING_FIELDS = {
    "camera_angle",
    "framing",
    "camera_distance",
    "light_temperature",
    "light_quality",
    "lens_feel",
}


def find_image(samples_dir, image_id):
    if not samples_dir.exists():
        return None
    for directory in samples_dir.iterdir():
        if not directory.is_dir():
            continue
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = directory / f"{image_id}{ext}"
            if candidate.exists():
                return candidate
    return None


def check_point(point, path, errors):
    if not isinstance(point, dict):
        errors.append(f"{path}: expected object")
        return
    for axis in ("x", "y"):
        value = point.get(axis)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            errors.append(f"{path}.{axis}: expected number in 0-1")


def check_coordinates(annotation, errors):
    ann_type = annotation.get("type")
    coords = annotation.get("coordinates")
    if not isinstance(coords, dict):
        errors.append(f"{annotation.get('id')}: coordinates must be object")
        return

    prefix = annotation.get("id", "annotation")
    if ann_type == "arrow":
        check_point(coords.get("from"), f"{prefix}.coordinates.from", errors)
        check_point(coords.get("to"), f"{prefix}.coordinates.to", errors)
    elif ann_type in {"point", "camera_position"}:
        check_point(coords, f"{prefix}.coordinates", errors)
        if "target" in coords:
            check_point(coords.get("target"), f"{prefix}.coordinates.target", errors)
    elif ann_type == "rect":
        for key in ("x", "y", "width", "height"):
            value = coords.get(key)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"{prefix}.coordinates.{key}: expected number in 0-1")
    elif ann_type in {"line", "polygon", "polyline"}:
        points = coords.get("points")
        if not isinstance(points, list) or len(points) < 2:
            errors.append(f"{prefix}.coordinates.points: expected at least 2 points")
        else:
            for index, point in enumerate(points):
                check_point(point, f"{prefix}.coordinates.points[{index}]", errors)


def validate_file(path, samples_dir):
    errors = []
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    image_id = data.get("image_id")
    if not image_id:
        errors.append("image_id missing")
    elif find_image(samples_dir, image_id) is None:
        errors.append(f"image file not found for image_id={image_id}")

    if data.get("version") != "LensMind Visual Annotation JSON v0.4":
        errors.append("version must be LensMind Visual Annotation JSON v0.4")

    style = data.get("style_summary")
    if not isinstance(style, dict):
        errors.append("style_summary missing")
    else:
        missing = REQUIRED_STYLE_FIELDS - set(style)
        if missing:
            errors.append(f"style_summary missing: {sorted(missing)}")
        palette = style.get("palette")
        if not isinstance(palette, list) or not 3 <= len(palette) <= 4:
            errors.append("style_summary.palette must contain 3-4 colors")

    shooting = data.get("shooting_summary")
    if not isinstance(shooting, dict):
        errors.append("shooting_summary missing")
    else:
        missing = REQUIRED_SHOOTING_FIELDS - set(shooting)
        if missing:
            errors.append(f"shooting_summary missing: {sorted(missing)}")

    annotations = data.get("annotations")
    if not isinstance(annotations, list):
        errors.append("annotations must be array")
    else:
        if len(annotations) > 6:
            errors.append("annotations must contain at most 6 items")
        for annotation in annotations:
            missing = REQUIRED_ANNOTATION_FIELDS - set(annotation)
            if missing:
                errors.append(f"{annotation.get('id', '<missing id>')}: missing {sorted(missing)}")
            if annotation.get("type") not in ALLOWED_TYPES:
                errors.append(f"{annotation.get('id')}: invalid type {annotation.get('type')}")
            if annotation.get("confidence") not in ALLOWED_CONFIDENCE:
                errors.append(f"{annotation.get('id')}: invalid confidence {annotation.get('confidence')}")
            check_coordinates(annotation, errors)

    rules = data.get("rendering_rules")
    if not isinstance(rules, dict):
        errors.append("rendering_rules missing")
    else:
        missing = REQUIRED_RENDERING_RULES - set(rules)
        if missing:
            errors.append(f"rendering_rules missing: {sorted(missing)}")

    return errors


def resolve_paths(annotations_dir, image_id=None, file_path=None):
    if image_id and file_path:
        raise SystemExit("Use either --image-id or --file, not both.")
    if image_id:
        return [annotations_dir / f"{image_id}.json"]
    if file_path:
        return [Path(file_path)]
    return sorted(path for path in annotations_dir.glob("*.json") if not path.name.startswith("_"))


def main():
    parser = argparse.ArgumentParser(description="Validate LensMind Visual Annotation JSON v0.4 files.")
    parser.add_argument("--root", default=".", help="LensMind workspace root.")
    parser.add_argument("--image-id", help="Validate annotations/<image-id>.json only.")
    parser.add_argument("--file", help="Validate one JSON file instead of all annotations.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    samples_dir = root / "samples"
    annotations_dir = root / "annotations"
    paths = resolve_paths(annotations_dir, args.image_id, args.file)

    failed = False
    for path in paths:
        if not path.exists():
            failed = True
            print(f"FAIL {path.name}")
            print(f"  - file not found: {path}")
            continue
        errors = validate_file(path, samples_dir)
        if errors:
            failed = True
            print(f"FAIL {path.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path.name}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
