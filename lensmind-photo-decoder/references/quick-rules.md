# Quick Rules

Read this file for daily sample runs. Read full references only when schema changes or validation fails.

## Daily Command

```powershell
python scripts/run_photo_decoder.py portrait-3 --root "D:\Codex\Condex_Workspace"
```

This validates one JSON, renders one teaching image, and writes one report.

If Codex inspected the image directly, first write compact notes to:

```text
reports/<image_id>-notes.md
```

The runner automatically embeds that file into the final report.

## Required JSON Fields

Top level: `image_id`, `version`, `style_summary`, `shooting_summary`, `light_analysis`, `technical_estimate`, `annotations`, `rendering_rules`.

Each annotation: `id`, `type`, `category`, `label`, `description`, `confidence`, `coordinates`.

## Allowed Values

- `confidence`: `high`, `medium`, `low`
- `type`: `arrow`, `point`, `line`, `rect`, `polygon`, `polyline`, `camera_position`
- common `category`: `light_direction`, `subject_position`, `camera_position`, `composition_line`, `negative_space`, `pose_direction`

## Light And Technical Fields

`light_analysis` is for the text report, not for drawing. It should include:

- `direction`: clear light direction, such as "front right above", "left side backlight", or "window light from camera left".
- `quality`: soft / hard / flash / street light / window light.
- `temperature`: warm / cool / mixed.
- `confidence`: `high`, `medium`, or `low`.
- `evidence`: visible basis, such as shadow direction, catchlight, face brightness, highlight edge, or background light.
- `shooting_adjustment`: how to adjust on set.

`technical_estimate` is also for the text report. Every estimate must include `value`, `confidence`, and `note`.

Recommended keys:

- `focal_length`
- `aperture`
- `shutter_speed`
- `iso`
- `white_balance`

## Coordinates

All coordinates use normalized `0-1` values.

- `arrow`: `from`, `to`
- `rect`: `x`, `y`, `width`, `height`
- `line` / `polygon` / `polyline`: `points`
- `point` / `camera_position`: `x`, `y`
- `camera_position`: optional `target`

## Visual Checklist

```text
visual check: pass / revise
- face overlap: pass / revise
- bottom panel: pass / revise
- labels readable: pass / revise
- arrows understandable: pass / revise
- style summary useful: pass / revise
```

## Output Files

- report: `reports/<image_id>-analysis.md`
- optional notes: `reports/<image_id>-notes.md`
- json: `annotations/<image_id>.json`
- annotated image: `outputs/annotations/<image_id>-annotated.jpg`
