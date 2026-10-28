# Visual Annotation JSON v0.4

Use this prompt to ask ChatGPT to produce annotation JSON.

```text
请基于前面的图片分析，生成 LensMind Visual Annotation JSON v0.4。

用途：
这个 JSON 后续会交给前端 / Canva / 画布工具，把原图渲染成教学标注图。

请只输出格式化后的 JSON，并放在 json 代码块中。
不要压缩成一行。
不要输出 JSON 以外的解释文字。

image_id 使用：[填写真实图片编号，例如 cafe-1]

必须包含：
- image_id
- version
- style_summary
- shooting_summary
- light_analysis
- technical_estimate
- annotations
- rendering_rules

基础规则：
1. image_id 必须使用我提供的真实图片编号，不要使用 sample_001。
2. version 固定为 "LensMind Visual Annotation JSON v0.4"。
3. annotations 最多 6 个。
4. 坐标必须使用 0-1 的相对比例。
5. 坐标、文字、箭头、框线尽量避开人物脸部，尤其不要穿过眼睛、鼻子、嘴巴。
6. confidence 只能使用英文枚举：high / medium / low。

style_summary 必须包含：
- label：短标题，例如“冷蓝夜景电影感”。
- description：一句话说明整体色彩和氛围。
- palette：3-4 个主要颜色，每个颜色包含 name 和 hex。
- shooting_hint：一句普通人能理解的拍摄提示。

shooting_summary 必须包含：
- camera_angle：拍摄角度，例如平视、俯拍、仰拍、略低机位。
- framing：取景范围，例如半身、全身环境人像、近景。
- camera_distance：拍摄距离感。
- light_temperature：光的冷暖，例如偏暖、冷白、冷蓝。
- light_quality：光质，例如柔光、硬光、闪光、路灯、侧前光。
- lens_feel：镜头观感，例如中焦人像感、广角近距离感。

light_analysis 用于文字报告，不算入 6 个图上标注，必须包含：
- direction：明确写光从哪里来，例如画面左前方、右后方逆光、窗户从摄影师左侧来。
- quality：光质，例如柔光、硬光、闪光、路灯、窗光。
- temperature：光的冷暖，例如偏暖、冷白、冷蓝、冷暖混合。
- confidence：high / medium / low。
- evidence：判断依据，例如脸部哪边更亮、阴影方向、眼神光、高光边缘、背景灯位置。
- shooting_adjustment：如果复刻，现场怎么调整光。

technical_estimate 用于文字报告，不算入 6 个图上标注。每项都必须包含 value、confidence、note。
建议包含：
- focal_length
- aperture
- shutter_speed
- iso
- white_balance

注意：参数只能推测，必须写 confidence，不能说绝对正确。

annotations 最多输出 6 个主要标注，优先标注：
- 光线方向
- 人物位置
- 摄影师站位
- 构图线 / 视线方向 / 引导线
- 留白区域
- 身体方向 / Pose 方向

每个 annotation 必须包含：
- id
- type
- category
- label
- description
- confidence
- coordinates

type 使用绘图类型，只能从这些里面选：
- arrow
- point
- line
- rect
- polygon
- polyline
- camera_position

category 使用语义类型，例如：
- light_direction
- subject_position
- camera_position
- composition_line
- negative_space
- pose_direction

label 要短，适合直接显示在图上，尽量 2-6 个字。
label 要通俗直观，避免使用“视觉动线”这类偏专业词。
可以优先用：
- 主光
- 侧前光
- 人物主体
- 机位
- 引导线
- 视线方向
- 看向方向
- 身体方向
- 留白

description 写更完整的解释，用于悬停或详情，不直接显示在图上。

坐标规则：
- arrow 使用 from 和 to
- rect 使用 x、y、width、height
- line / polygon / polyline 使用 points
- point / camera_position 使用 x、y
- camera_position 可以额外加 target

rendering_rules 必须包含：
{
  "coordinate_system": "normalized_0_1",
  "max_annotations": 6,
  "avoid_face_overlap": true,
  "confidence_enum": ["high", "medium", "low"],
  "show_label_on_image": true,
  "show_description_on_hover": true
}

生成前请自检：
- 是否是合法 JSON。
- 是否不超过 6 个 annotations。
- 是否每个 annotation 都有必填字段。
- confidence 是否全部为 high / medium / low。
- 坐标是否都在 0-1 之间。
- 箭头、线条、标签是否尽量避开人物五官。
- style_summary 是否包含色彩和色调。
- shooting_summary 是否包含机位、取景、距离、光的冷暖、光质、镜头感。

自检不要输出，只输出最终 JSON。
```
