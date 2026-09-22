---
name: guizang-product-video-skill
license: "AGPL-3.0; CodePilot fallback assets: BUSL-1.1 (see README.md)"
description: 制作代码驱动的软件版本更新宣传片（release notes video、changelog promo）。从真实更新提炼卖点，复用产品组件和设计语言，完成分镜、代码原创配乐、动作音效、渲染与验收。
---

# 归藏 product video skill

用真实组件讲清楚软件更新，让画面、文案和声音一起推进。本文使用统一术语：**默认样式**指 `assets/fallback/`；**起步工程**指 `assets/starter/`；其初始产物称**技术样片**；音效事件统一保存在 **`audio.cues`**。

## 流程

1. **确认范围、平台与风格。** 已有工程沿用 brief 和用户决定，只处理本次修改。新片优先补齐产品/仓库、时长与画幅、语言和链接要求，再用一次提问问清**范围与平台**：宣传片覆盖**全量产品介绍、最新一个版本周期，还是用户指定的版本区间**？覆盖**哪些平台面**（桌面端／CLI/TUI／移动端／服务端 API）？仓库记录只能说明「有哪些版本」，说明不了「用户想宣传哪个范围和面」——这一项必须由用户拍板，不要默认替用户决定。答案写入 `plan.json` 的 `scope`（如 `{"versions":"v0.10.12..v0.11.0","platforms":["cli-tui"]}`）并同步进 BRIEF；未纳入的平台面在交付时明确声明，避免观众误以为宣传片覆盖产品全貌。范围与平台尚未确定时问一次；用户已经指定时直接执行。**风格**也在此一并确认：“沿用代码库自己的设计风格（推荐），还是默认的暖白／炭黑风格？” `repo` 使用产品设计；`default` 使用默认样式包装；`hybrid` 保留产品识别并调整外层排版。普通场景可建议横版、45–60 秒、中文。
2. **初始化后检查环境。** 风格确定后，按下方工具入口初始化独立视频目录，再运行环境检查。仅对报告的缺项加载 [依赖安装](references/onboarding.md) 并补装，随后复查；`ready:true` 继续制作。已有工程直接检查，无需再次初始化。Python 本身缺失时先按依赖安装文档补齐 Python。检查每次执行，安装文档按缺项加载；browser 每次重查环境并实际启动浏览器，`cached:true` 仅表示环境指纹匹配上次成功记录；HyperFrames 指纹匹配时可跳过 doctor。
3. **调查更新并接通组件。** 按 [仓库与风格审计](references/repo-and-style.md) 确定日期/版本、发布状态和 3–5 组核心变化。找到对应业务组件、完整样式和所需状态，先接通一个功能镜头。React 项目的依赖解析、CSS/Tailwind 接入见 [起步工程](references/starter.md)，其他挂载路径见 [组件接入](references/component-pipeline.md)。
4. **编排画面与文案。** 按 [分镜与文案](references/story-and-copy.md) 写解释、标题、动作及阅读时间，交替安排字卡、组件特写、工作区和细节。用真实渲染路径输出 3–6 张关键静帧自检；用户要求先看方向时等反馈，否则继续。默认样式可先看 [标题预览](assets/fallback/title-preview.png) 与 [组件预览](assets/fallback/preview.png)。
5. **完成动效与声音。** 用主时间轴控制组件状态和镜头，支持前后 seek。按 [配乐与音效来源](references/audio-sourcing.md) 为当前影片代码原创配乐，先查找适合产品和动作的音效，缺项才用内置 WAV。按 [混音与验收](references/audio-and-qa.md) 对齐 `audio.cues`、压低关键音效期间的音乐并完成混音。
6. **验证并交付。** 检查最终 MP4 的裁切、字体、图片、Logo、阅读时间、声音和用户指定的链接处理。修改后重新导出并复查相关镜头。交付 MP4、可复现工程和少量预览；区分自动检查、实际观看/试听及仍受限部分。遇到历史同类问题可查 [案例复盘](references/case-study.md)。

## 硬约束

- **真实功能。** 正式片至少一项可追溯的更新主张；每项记录发布状态、来源和白话解释。演示数据可固定，功能效果与数字应有证据。范围与平台以 `plan.scope` 为准，交付时声明未覆盖的平台面。
- **原组件。** 功能镜头优先接入实际业务组件、原样式及状态；抽象化用于取景、布局和外层动画。逐镜头核对导入图、来源与静帧。平台确实无法接入时记录阻碍和替代方式，遵从已有授权。
- **清楚排版。** 宣传标题默认有意义的英文与中文各占一个 span、分别指定字体，中文无衬线；中文说明交代对象、动作和结果。原产品内部字体保持其设计；用户指定的语言/字体优先。
- **完整声音。** 默认代码原创音乐与独立动作音效均入轨，关键反馈可闻、音画同步。用户要求静音或省略音效时，记录 `audioExceptionReason`；该字段保存用户依据。
- **隔离工程。** 源码适配、展示依赖和构建配置放视频工程；原产品代码和依赖保持不动。读取产品已安装依赖，必要时在视频工程固定版本补装适配所需包。
- **授权与真实验收。** 使用素材时保留来源和适用许可。默认样式仍受 [BSL 授权](assets/fallback/SOURCE.md) 约束。自动检查证明结构与文件一致性，视觉、语义和听感由实际审阅补充。

## 工具入口

先确认风格，再初始化；三种风格均可传 `--repo`，其中 repo/hybrid 必填：

```sh
python3 <skill-dir>/scripts/init_project.py --output <video-dir> --style repo --repo <repo-dir>
python3 <skill-dir>/scripts/check_environment.py --project <video-dir> --engine browser
# 缺项 → 按 references/onboarding.md 补装 → 使用 --force 复查。
```

HyperFrames 工程使用 `--engine hyperframes`。新工程附 10 秒技术样片，用于验证链路；正式制作按实际产品替换内容。

- [起步工程](references/starter.md)：依赖接入、CSS、编译、静帧和导出耗时。
- [配乐源码](assets/audio/codepilot-score-example.py)：48 秒、120 BPM、48 kHz 示例，复制进工程按本片改编。
- [内置音效](assets/audio/SOURCE.md)：11 个 WAV；需改音色时运行 `scripts/make_sfx.py --output <new-sfx-dir>`。
- `scripts/mix_audio.py <plan.json>`：混音、音乐让位、独立音轨和证据报告。
- `scripts/check_delivery.py <plan.json> [--video <final.mp4>] [--mix-report <audio-mix.json>]`：结构、文件、时间线与媒体验证。
- `python3 -m unittest discover -s <skill-dir>/tests`：维护此 skill 时运行回归测试；日常制片无需读取测试源码。
