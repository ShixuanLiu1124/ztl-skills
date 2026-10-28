# Photo Analysis Workflow

Use these prompts in order when testing one sample photo in ChatGPT.

## Step 1: Summary

```text
请分析这张摄影样片。

我的目标：
- 理解它为什么好看。
- 学习怎么拍出属于自己的类似照片。
- 不复制原图，只学习摄影方法。

请只输出 Summary，不要展开成长篇。

输出格式：
1. 一句话总结，30 字以内。
2. 为什么好看的 3 个原因，用普通人语言。
3. 如果我想拍，最重要的 3 个动作。
4. 是否值得继续展开：普通人解释 / 专业分析 / 教学标注图 / Shoot Planner 模板。

要求：
- 先说人话，不要一上来讲专业术语。
- 简洁一点，是什么就是什么，不要绕弯。
- 不评价人物长相、身材、年龄、吸引力。
- 不要说绝对的相机参数。
- 不鼓励直接复制原作品。
```

## Step 2: Plain-Language Explanation

```text
请继续展开，用普通人语言解释。

不要写太长，不要堆摄影术语。重点回答“我明天怎么拍”。

请告诉我：
1. 这张图为什么好看。
2. 适合什么时间拍。
3. 人物应该站哪里。
4. 摄影师应该站哪里。
5. 画面应该框到哪里，比如从人物哪里到哪里。
6. 光大概从哪边来，落在脸上大约几分之几。
7. 如果画面里有风感，请推测风从哪边来，以及它怎么影响头发、衣服或氛围。
8. 怎么引导人物，具体到肩膀、脸、眼神、手。
9. 如果光太强，出现阴阳脸，应该怎么调整。
```

## Step 3: Professional Analysis

```text
请展开专业摄影分析。

所有参数、光位、灯位、焦段、后期判断都只能推测，必须写置信度：低 / 中 / 高。

请包括：
1. 光线方向与光质。
2. 构图与机位。
3. 摄影师站位推测。
4. 画面取景边界：从人物哪里框到哪里。
5. 焦段 / 光圈 / 快门 / ISO 推测，并说明对画面的影响。
6. 色彩分析：主色、辅助色、点缀色、色彩关系。
7. 前期参数和后期调色如何配合。
8. 如果是夜景、CCD 或闪光灯照片，请具体分析补光灯 / 闪光灯方向、色温、亮度和环境光关系。
9. Pose 与互动关系，具体到肩膀、脸、眼神、手。
10. 服装造型建议。
11. 适合什么类型的约拍。
12. 是否适合转化成 Shoot Planner 模板。
```

## Step 4: Visual Annotation JSON

Use `references/visual-annotation-json-v0.4.md`.

Replace only this placeholder before sending it to ChatGPT:

```text
image_id 使用：你的真实图片编号
```

Save only the JSON object from `{` to `}` as:

```text
annotations/<image_id>.json
```

Do not save the ```json fence.

## Step 5: Local Validation And Rendering

Run:

```powershell
python skills/lensmind-photo-decoder/scripts/validate_annotations.py --root "D:\Codex\Condex_Workspace"
python skills/lensmind-photo-decoder/scripts/render_annotations.py --root "D:\Codex\Condex_Workspace"
```

Expected output:

```text
PASS <image_id>.json
outputs/annotations/<image_id>-annotated.jpg
```

## Future Testing Shortcut

When the workflow is stable, the user only needs to add:

```text
samples/<type>/<image_id>.jpg
annotations/<image_id>.json
```

Then Codex should:

1. Validate the JSON.
2. Fix small schema or coordinate issues when obvious.
3. Render the teaching annotation image.
4. Inspect whether labels avoid the face and whether the bottom panel is readable.
5. Update `docs/approved-sample-library.md` only after the output passes.
