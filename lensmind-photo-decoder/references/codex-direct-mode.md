# Codex Direct Mode

Use this mode when Codex can inspect the image attachment or local image file.

User request example:

```text
Use $lensmind-photo-decoder. I added portrait-3.jpg. Please run the full Photo Decoder workflow.
```

Codex should:

1. Locate the image under `samples/*/<image_id>.jpg`.
2. Inspect the image directly.
3. Write a compact note file at `reports/<image_id>-notes.md`:
   - one-sentence style summary
   - why it looks good, 3 bullets
   - how to shoot it, 3-5 bullets
   - light direction, quality, and temperature
   - composition and camera position
   - pose guidance
   - color and post-processing direction
   - parameter guesses only when visible, with confidence
4. Create `annotations/<image_id>.json` using Visual Annotation JSON v0.4.
5. Run `scripts/run_photo_decoder.py <image_id> --root <root>`.
6. Fix obvious JSON schema or coordinate issues.
7. Inspect the rendered image.
8. Report:
   - analysis summary
   - JSON path
   - report path
   - rendered image path
   - whether it should enter the style library

Do not ask the user to run ChatGPT manually unless Codex cannot inspect the image.
