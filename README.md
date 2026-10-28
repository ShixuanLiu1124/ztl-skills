# ztl-skills

个人自定义 Codex skills。

## Skills

| Skill | 用途 |
| --- | --- |
| `photography-shoot-planner` | 按固定中文模板撰写摄影策划，覆盖地点、时间、妆造、道具与五类景别的镜头方案。 |
| `lensmind-photo-decoder` | 分析摄影样片，生成摄影分析报告、视觉标注数据、教学标注图与拍摄计划草稿。 |

每个目录的 `SKILL.md` 为入口，其余参考文件与脚本应随目录一起保留。

## 本机目录

- 仓库位置：`E:\Program\ztl-skills`
- 当前调用副本：`C:\Users\Shixuanliu\.codex\skills`

仓库中的两个 skill 从当前调用副本完整复制并逐文件校验。现有调用副本保留不变；两处是独立副本，不会自动同步。更新仓库后，如需使用新版本，应将对应 skill 目录同步至实际的 Codex skills 目录。配置了 `CODEX_HOME` 时，使用其下的 `skills` 目录。

`lensmind-photo-decoder` 中保留原有项目路径配置，使用前请按其说明确认项目位置和运行环境。

本仓库只收录自定义 skills，不包含系统内置技能、插件缓存或第三方 `anatomy` 仓库。
