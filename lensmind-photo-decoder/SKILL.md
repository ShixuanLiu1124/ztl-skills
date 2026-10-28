---
name: lensmind-photo-decoder
description: Analyze photography samples for LensMind and turn them into plain-language photo analysis reports, Visual Annotation JSON, rendered teaching annotation images, approved sample-library entries, and Shoot Planner drafts. Use when the user mentions LensMind, Photo Decoder, sample photo analysis, photography sample workflows, annotation JSON, teaching annotation images, or converting a photo analysis into a shoot plan.
---

# LensMind Photo Decoder

Use this skill to run the LensMind sample workflow:

```text
sample photo -> short report -> Visual Annotation JSON v0.4 -> validation -> teaching annotation image
```

Keep outputs practical for ordinary users and beginner photographers. Do not evaluate appearance. Do not encourage copying a photographer's work; extract reusable methods.

## Modes

Use Codex direct mode when the image is attached or readable from the local workspace. Inspect the image directly, write the short analysis, create `annotations/<image_id>.json`, validate it, render the teaching image, and report paths.

Use ChatGPT manual mode only when Codex cannot inspect the image. Ask the user to use `references/photo-analysis-workflow.md` and `references/visual-annotation-json-v0.4.md`, then save the returned JSON.

## Workspace Layout

Assume a project root with:

```text
samples/<type>/<image_id>.jpg
annotations/<image_id>.json
reports/<image_id>-analysis.md
outputs/annotations/<image_id>-annotated.jpg
```

Current LensMind root:

```text
D:\Codex\Condex_Workspace
```

## Daily Workflow

1. Read `references/quick-rules.md` for routine runs. Read full references only when schema changes or validation fails.
2. Put one image in `samples/<type>/<image_id>.jpg`.
3. If inspecting the image directly, write compact analysis notes to `reports/<image_id>-notes.md`.
4. Generate or update `annotations/<image_id>.json`. Use `annotations/_template.json` as the skeleton when helpful.
5. Run one sample only:

```powershell
python scripts/run_photo_decoder.py <image_id> --root "D:\Codex\Condex_Workspace"
```

6. If needed, run separate commands:

```powershell
python scripts/validate_annotations.py --root "D:\Codex\Condex_Workspace" --image-id <image_id>
python scripts/render_annotations.py --root "D:\Codex\Condex_Workspace" --image-id <image_id>
```

7. Inspect the rendered image with this checklist:

```text
visual check: pass / revise
- face overlap: pass / revise
- bottom panel: pass / revise
- labels readable: pass / revise
- arrows understandable: pass / revise
- style summary useful: pass / revise
```

8. If it passes, update `docs/approved-sample-library.md`.

## JSON Rules

Use Visual Annotation JSON v0.4.

Required top-level fields: `image_id`, `version`, `style_summary`, `shooting_summary`, `light_analysis`, `technical_estimate`, `annotations`, `rendering_rules`.

Annotation rules:

- At most 6 annotations.
- Use normalized `0-1` coordinates.
- Use `confidence`: `high`, `medium`, or `low`.
- Use short, plain labels on the image.
- Put longer explanation in `description`.
- Avoid arrows, labels, and boxes crossing eyes, nose, and mouth.
- Prefer labels like `视线方向`, `看向方向`, `身体方向`, `主光`, `侧前光`, `机位`, `留白`, `人物主体`.
- Avoid labels like `视觉动线` unless the user specifically wants professional wording.

Report-only fields:

- `light_analysis`: clear light direction, confidence, visible evidence, and on-set adjustment.
- `technical_estimate`: focal length, aperture, shutter, ISO, and white balance guesses. Every item must include `value`, `confidence`, and `note`.

## Scripts

- `scripts/run_photo_decoder.py <image_id> --root <root>`: validate one sample, render one image, and write one report.
- `reports/<image_id>-notes.md`: optional compact direct-image analysis that is embedded into the final report.
- `scripts/validate_annotations.py --root <root> --image-id <image_id>`: validate one JSON.
- `scripts/render_annotations.py --root <root> --image-id <image_id>`: render one annotated image.

## References

- `references/quick-rules.md`: daily low-token rules.
- `references/codex-direct-mode.md`: direct image inspection workflow.
- `references/photo-analysis-workflow.md`: full ChatGPT text-analysis prompts.
- `references/visual-annotation-json-v0.4.md`: full JSON prompt and schema.
- `references/shoot-planner-from-photo-analysis.md`: convert a passed analysis into a Shoot Planner.

## Acceptance Criteria

A sample passes when:

- The image and JSON filenames match the `image_id`.
- Validation passes.
- `reports/<image_id>-analysis.md` exists.
- `outputs/annotations/<image_id>-annotated.jpg` exists.
- Labels do not seriously obscure the face.
- The bottom panel is complete and does not cover the original image.
- The sample can be explained as a reusable shooting method.
