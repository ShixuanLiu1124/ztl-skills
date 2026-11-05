import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


COLORS = {
    "light_direction": (245, 166, 76, 235),
    "subject_position": (116, 181, 148, 225),
    "camera_position": (229, 112, 92, 235),
    "composition_line": (99, 168, 193, 225),
    "negative_space": (99, 168, 193, 42),
    "pose_direction": (245, 166, 76, 235),
}


def load_font(size):
    configured = os.environ.get("LENSMIND_FONT")
    candidates = [
        configured,
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    raise RuntimeError(
        "No usable font found. Install a CJK font or set LENSMIND_FONT to a .ttf/.ttc file."
    )


def find_image(samples_dir, image_id):
    for directory in samples_dir.iterdir():
        if not directory.is_dir():
            continue
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = directory / f"{image_id}{ext}"
            if candidate.exists():
                return candidate
    raise FileNotFoundError(f"Image not found for image_id={image_id}")


def pt(coord, width, height):
    return int(coord["x"] * width), int(coord["y"] * height)


def scale_rect(coords, width, height):
    return (
        int(coords["x"] * width),
        int(coords["y"] * height),
        int((coords["x"] + coords["width"]) * width),
        int((coords["y"] + coords["height"]) * height),
    )


def readable_text_color(color):
    r, g, b = color[:3]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (20, 20, 20, 255) if luminance > 150 else (255, 255, 255, 255)


def label_box(draw, xy, text, font, image_size):
    width, height = image_size
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_x = 11
    pad_y = 7

    x = max(8, min(x, width - text_w - pad_x * 2 - 8))
    y = max(8, min(y, height - text_h - pad_y * 2 - 8))
    return (x, y, x + text_w + pad_x * 2, y + text_h + pad_y * 2), pad_x, pad_y


def boxes_overlap(first, second, gap=8):
    return not (
        first[2] + gap <= second[0]
        or second[2] + gap <= first[0]
        or first[3] + gap <= second[1]
        or second[3] + gap <= first[1]
    )


def draw_label(draw, xy, text, font, image_size, color, occupied=None):
    """Draw a quiet dark label and pick the least-colliding nearby position."""
    if occupied is None:
        occupied = []
    x, y = xy
    bbox, pad_x, pad_y = label_box(draw, (x, y), text, font, image_size)
    width, height = image_size
    box_w = bbox[2] - bbox[0]
    box_h = bbox[3] - bbox[1]
    candidates = [
        (x, y), (x + 18, y - box_h - 8), (x + 18, y + box_h // 2),
        (x - box_w - 18, y + box_h // 2), (x - box_w - 8, y - box_h - 8),
        (x - box_w // 2, y + 18), (x - box_w // 2, y - box_h - 18),
    ]
    best = None
    best_score = None
    for candidate in candidates:
        candidate_box, _, _ = label_box(draw, candidate, text, font, image_size)
        overlap_count = sum(boxes_overlap(candidate_box, item) for item in occupied)
        edge_penalty = sum(
            max(0, 12 - value) for value in candidate_box[:2]
        ) + max(0, candidate_box[2] - width + 12) + max(0, candidate_box[3] - height + 12)
        score = overlap_count * 10000 + edge_penalty
        if best_score is None or score < best_score:
            best_score = score
            best = (candidate_box, candidate)

    box, _ = best
    draw.rounded_rectangle(
        box,
        radius=9,
        fill=(20, 23, 27, 218),
        outline=color[:3] + (210,),
        width=2,
    )
    # A small accent bar makes categories scannable without adding another loud color.
    draw.rounded_rectangle(
        (box[0], box[1], box[0] + 4, box[3]),
        radius=2,
        fill=color,
    )
    draw.text((box[0] + pad_x + 2, box[1] + pad_y - 1), text, font=font, fill=(248, 248, 246, 255))
    if occupied is not None:
        occupied.append(box)
    return box


def hex_to_rgba(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def wrap_text(draw, text, font, max_width):
    if not text:
        return []
    lines = []
    current = ""
    for char in text:
        candidate = current + char
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def append_style_summary(image, summary, shooting, font, small_font):
    if not summary:
        return image
    draw_probe = ImageDraw.Draw(image)
    width, height = image.size
    label = summary.get("label", "")
    hint = summary.get("shooting_hint", "")
    palette = summary.get("palette", [])[:4]
    shooting_parts = []
    if shooting:
        for key in ("camera_angle", "framing", "light_temperature", "light_quality"):
            value = shooting.get(key)
            if value:
                shooting_parts.append(value)
    shooting_text = "  ·  ".join(shooting_parts)

    pad = max(18, round(width * 0.018))
    swatch = max(24, round(width * 0.028))
    text_max_width = width - pad * 2
    hint_lines = wrap_text(draw_probe, hint, small_font, text_max_width)
    shooting_lines = wrap_text(draw_probe, shooting_text, small_font, text_max_width)
    line_h = small_font.size + 8
    panel_h = pad * 5 + swatch + 54 + line_h * (max(1, len(hint_lines)) + len(shooting_lines))

    canvas = Image.new("RGB", (width, height + panel_h), (22, 22, 22))
    canvas.paste(image, (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")
    y = height

    draw.rectangle((0, y, width, y + panel_h), fill=(20, 23, 27, 255))
    draw.line((0, y, width, y), fill=(245, 166, 76, 210), width=3)
    draw.text((pad, y + pad - 2), label, font=font, fill=(248, 248, 246, 255))

    swatch_x = pad
    swatch_y = y + pad * 2 + font.size + 10
    for item in palette:
        color = hex_to_rgba(item.get("hex", "#FFFFFF"))
        draw.rounded_rectangle(
            (swatch_x, swatch_y, swatch_x + swatch, swatch_y + swatch),
            radius=6,
            fill=color,
            outline=(255, 255, 255, 180),
            width=2,
        )
        swatch_x += swatch + 8

    if hint:
        text_x = pad
        text_y = swatch_y + swatch + pad
        for line in hint_lines:
            draw.text((text_x, text_y), line, font=small_font, fill=(248, 248, 246, 235))
            text_y += line_h

    if shooting_text:
        text_y = swatch_y + swatch + pad + line_h * max(1, len(hint_lines)) + 4
        for line in shooting_lines:
            draw.text((pad, text_y), line, font=small_font, fill=(178, 186, 190, 235))
            text_y += line_h
    return canvas


def draw_arrow(draw, start, end, color, width):
    draw.line([start, end], fill=color, width=width)
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux = dx / length
    uy = dy / length
    head = max(16, width * 4)
    left = (int(ex - ux * head - uy * head * 0.55), int(ey - uy * head + ux * head * 0.55))
    right = (int(ex - ux * head + uy * head * 0.55), int(ey - uy * head - ux * head * 0.55))
    draw.polygon([end, left, right], fill=color)


def midpoint(points):
    if not points:
        return 0, 0
    x = sum(point[0] for point in points) // len(points)
    y = sum(point[1] for point in points) // len(points)
    return x, y


def render_one(json_path, samples_dir, output_dir):
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    image_id = data["image_id"]
    image_path = find_image(samples_dir, image_id)

    base = Image.open(image_path).convert("RGBA")
    width, height = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    occupied_labels = []

    line_width = max(4, round(min(width, height) * 0.006))
    font = load_font(max(22, round(width * 0.026)))
    small_font = load_font(max(16, round(width * 0.018)))

    for annotation in data.get("annotations", []):
        label = annotation.get("label", "")
        ann_type = annotation.get("type")
        category = annotation.get("category", "")
        coords = annotation.get("coordinates", {})
        color = COLORS.get(category, (255, 255, 255, 255))
        label_anchor = None

        if ann_type == "arrow":
            start = pt(coords["from"], width, height)
            end = pt(coords["to"], width, height)
            draw_arrow(draw, start, end, color, line_width)
            mid = midpoint([start, end])
            label_anchor = (mid[0] + 10, mid[1] - 18)
        elif ann_type == "rect":
            rect = scale_rect(coords, width, height)
            if category == "negative_space":
                draw.rectangle(rect, fill=color, outline=(100, 181, 246, 180), width=line_width)
            else:
                draw.rectangle(rect, outline=color, width=line_width)
            label_anchor = (rect[0] + 8, rect[1] + 8)
        elif ann_type == "point":
            center = (int(coords["x"] * width), int(coords["y"] * height))
            radius = max(10, line_width * 2)
            draw.ellipse(
                (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
                fill=color,
                outline=(255, 255, 255, 230),
                width=max(2, line_width // 2),
            )
            label_anchor = (center[0] + radius + 8, center[1] - radius)
        elif ann_type == "camera_position":
            center = (int(coords["x"] * width), int(coords["y"] * height))
            radius = max(12, line_width * 2)
            draw.ellipse(
                (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
                fill=color,
                outline=(255, 255, 255, 230),
                width=max(2, line_width // 2),
            )
            target = coords.get("target")
            if target:
                draw_arrow(draw, center, pt(target, width, height), color, max(3, line_width - 1))
            label_anchor = (center[0] + radius + 8, center[1] - radius)
        elif ann_type in {"line", "polyline"}:
            points = [pt(p, width, height) for p in coords.get("points", [])]
            if len(points) >= 2:
                draw.line(points, fill=color, width=line_width, joint="curve")
                mid = midpoint(points)
                label_anchor = (mid[0] + 10, mid[1] - 18)
        elif ann_type == "polygon":
            points = [pt(p, width, height) for p in coords.get("points", [])]
            if len(points) >= 3:
                draw.polygon(points, fill=color[:3] + (35,))
                if category != "negative_space":
                    draw.line(points + [points[0]], fill=color[:3] + (100,), width=max(2, line_width // 2))
                label_anchor = (points[0][0] + 8, points[0][1] + 8)

        if label and label_anchor:
            draw_label(draw, label_anchor, label, font, base.size, color, occupied_labels)

    result = Image.alpha_composite(base, overlay).convert("RGB")
    result = append_style_summary(result, data.get("style_summary"), data.get("shooting_summary"), font, small_font)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{image_id}-annotated.jpg"
    result.save(out_path, quality=94)
    return out_path


def resolve_paths(annotations_dir, image_id=None, file_path=None):
    if image_id and file_path:
        raise SystemExit("Use either --image-id or --file, not both.")
    if image_id:
        return [annotations_dir / f"{image_id}.json"]
    if file_path:
        return [Path(file_path)]
    return sorted(path for path in annotations_dir.glob("*.json") if not path.name.startswith("_"))


def main():
    parser = argparse.ArgumentParser(description="Render LensMind teaching annotation images.")
    parser.add_argument("--root", default=".", help="LensMind workspace root.")
    parser.add_argument("--image-id", help="Render annotations/<image-id>.json only.")
    parser.add_argument("--file", help="Render one JSON file instead of all annotations.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    annotations_dir = root / "annotations"
    samples_dir = root / "samples"
    output_dir = root / "outputs" / "annotations"
    paths = resolve_paths(annotations_dir, args.image_id, args.file)

    outputs = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")
        outputs.append(render_one(path, samples_dir, output_dir))
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
