---
name: guizang-product-video-skill
license: "AGPL-3.0; CodePilot fallback assets: BUSL-1.1 (see README.md)"
description: 制作代码驱动的软件产品宣传片和版本更新片（product promo、release notes video、changelog promo）。从真实功能和产品设计出发定方向，用真实组件、GSAP/Three.js 动效、原创配乐和动作音效完成影片，每支片子的视觉手法都从产品本身推导，不套模板。
---

# 归藏 product video skill

用真实组件讲清楚一个软件产品或一次更新，让画面、文案和声音一起推进。本文术语：**默认样式**指 `assets/fallback/`；**起步工程**指 `assets/starter/`，初始产物称**技术样片**；**方向文件**指视频工程里的 `DIRECTION.md`；音效事件统一保存在 `audio.cues`。

## 流程

1. **确认范围、平台与风格。** 已有工程沿用 brief 和用户决定，只处理本次修改。新片补齐：产品/仓库、发布渠道、时长与画幅、语言、是否允许链接，以及用户有没有参考视频。**范围与产品平台面必须由用户拍板**，仓库只能说明有哪些版本，说明不了用户想宣传什么：覆盖全量产品、最新一个版本周期，还是指定版本区间？覆盖哪些平台面（桌面端／CLI·TUI／移动端／服务端 API）？没指定时问一次，答案写入 `plan.json` 的 `scope`（如 `{"versions":"v0.10.12..v0.11.0","platforms":["cli-tui"]}`）并同步进 BRIEF。风格没定时问一次："沿用代码库自己的设计风格（推荐），还是默认的暖白／炭黑风格？"`repo` 用产品设计；`default` 用默认样式包装；`hybrid` 保留产品识别、调整外层排版。常见起点：横版、45–60 秒、中文。
2. **初始化并检查环境。** 按下方工具入口初始化独立视频目录，再运行环境检查；只对报告的缺项加载 [依赖安装](references/onboarding.md)，装完复查。已有工程直接检查，不重新初始化。
3. **调查产品，接通组件。** 按 [仓库与风格审计](references/repo-and-style.md) 确定功能、发布状态和证据，记下设计语言、暗色主题和可做母题的产品元素。在浏览器里挂载真实业务组件：补 provider，接口用 fixture，交互用真实点击和输入，放大到视频尺度（[起步工程](references/starter.md)、[组件接入](references/component-pipeline.md)）。先接通一个功能镜头并出静帧。
4. **定方向，写 `DIRECTION.md`。** 按 [影片方向](references/direction.md)：拆解参考，提炼产品气质，沿不同的轴提出三个方向，选一个并写出理由；列出 3–5 个"因为产品有 X、所以用 Y"的专属手法，并避开本工作区上一支片子的手法；把画面规范写成具体数字；写到每一秒的镜头表。用户想先看方向时，给三个方向和 3–6 张关键静帧，等反馈；否则继续。
5. **逐镜头搭建。** 每个镜头 = 视图组件 + builder（GSAP 主时间轴、`onRender` 画布层、`onDrive` 真实交互），时间只从 `plan.json` 读。手法从 [视觉手法词汇](references/visual-vocabulary.md) 里选能从产品推导的，`assets/fx-lab/` 的样例改写后再用。每搭完一个镜头就出静帧，对照镜头表（[审片](references/review.md)）。
6. **配乐与音效。** 按 [配乐与音效](references/audio-sourcing.md) 选音乐来源（用户提供 → 本机可用的生成模型 → 代码合成），编曲从镜头边界推出来，音色从产品气质推出来；音效先用录音素材，缺项再用内置 WAV。用 `sfx_landmarks.py` 实测落点和电平，按 [混音与验收](references/audio-and-qa.md) 对位、让位、混音。
7. **审片并交付。** 导出全片，看 2 fps 联系表、每个转场的 10 fps 条带和信息密集镜头的全尺寸帧，按 [审片](references/review.md) 修改后重新导出。运行 `check_delivery.py`（`pacing` 只提示该去看哪一段）。交付 MP4、可复现工程和少量预览；说清哪些是自动检查、哪些实际看过/听过、哪些仍未验证。要发布时按 [封面](references/cover.md) 做 3:4 / 4:3 / 16:9 封面，用户没提就用一句话问一下。历史问题查 [案例复盘](references/case-study.md)。

## 硬约束

- **真实功能。** 正式片至少一项可追溯的主张；每项记录发布状态、来源和白话解释。演示数据可以固定，功能效果与数字要有证据。范围与平台以 `plan.scope` 为准，交付时声明没有覆盖的平台面，避免观众以为片子讲的是产品全貌。
- **原组件，视频尺度。** 功能镜头接入实际业务组件、原样式及状态，界面正文在成片里 ≥ 22px（1080p）。抽象化只用于取景、布局和外层动画。平台确实无法接入时，记录阻碍和替代方式，遵从已有授权。
- **先有方向，再写代码。** 正式片必须有 `DIRECTION.md`：选定的方向和理由、从产品推导的专属手法、画面规范、镜头表。
- **不套模板。** 每个视觉手法都要能说出它对应产品的哪一点。案例和 fx-lab 是推导示范，不是风格包；同一工作区连续做片，不原样复用上一支的开场、章节和背景手法。片内也要避免所有元素同一种入场、同一种转场。
- **清楚排版。** 宣传标题默认英文、中文各一个 span，分别指定字体，中文无衬线；中文说明交代对象、动作和结果。产品内部字体保持原设计；用户指定的语言/字体优先。
- **完整声音。** 默认音乐与独立动作音效都进音轨，关键反馈听得见、音画同步。用户要求静音或省略音效时，记录 `audioExceptionReason`。
- **隔离工程。** 源码适配、展示依赖和构建配置放在视频工程；原产品代码和依赖不动。
- **授权与真实验收。** 素材保留来源和许可。默认样式受 [BSL 授权](assets/fallback/SOURCE.md) 约束。自动检查只证明结构与文件一致；视觉、语义和听感靠实际审阅，没有试听就如实说明。

## 工具入口

先确认风格，再初始化；三种风格都可以传 `--repo`，其中 repo/hybrid 必填：

```sh
python3 <skill-dir>/scripts/init_project.py --output <video-dir> --style repo --repo <repo-dir>
python3 <skill-dir>/scripts/check_environment.py --project <video-dir> --engine browser
# 缺项 → 按 references/onboarding.md 补装 → 使用 --force 复查。
```

HyperFrames 工程使用 `--engine hyperframes`。新工程附 10 秒技术样片（刻意没有风格，只验证链路）和一份只有问题的 `DIRECTION.md`。

- [影片方向](references/direction.md)：参考拆解、产品气质、三个方向与差异轴、专属手法推导、反重复、画面规范、镜头表。
- [视觉手法词汇](references/visual-vocabulary.md)：按作用分组的手法，写明表达什么、从哪里推导、怎么实现、何时不用。
- [起步工程](references/starter.md)：运行时结构（seek、GSAP 主时间轴、onRender、onDrive）、接入仓库、样式链、plan 字段。
- [审片](references/review.md)：三个审片节点、联系表与转场条带、常见问题对照表。
- [封面](references/cover.md)：3:4 / 4:3 / 16:9 三种比例的布局思路、选图、文案和导出（起步工程的 `cover.mjs`）。
- `assets/fx-lab/`：流线场、粒子汇聚、字符场、发光地平线、切片、环绕的可改写样例。
- `assets/audio/score-example-keys.py`、`score-example-cinematic.py`：两种气质的代码合成配乐示例，借手法，不照搬曲子。
- [内置音效](assets/audio/SOURCE.md)：11 个原创 WAV；需要改音色时运行 `scripts/make_sfx.py --output <new-sfx-dir>`。
- `scripts/sfx_landmarks.py <files>`：实测音效的起音点、峰值时间和峰值电平。
- `scripts/mix_audio.py <plan.json>`：混音、音乐让位、独立音轨和证据报告。
- `scripts/check_delivery.py <plan.json> [--video <final.mp4>] [--mix-report <audio-mix.json>]`：结构、文件、时间线、方向文件、媒体与画面节奏提示。
- `python3 -m unittest discover -s <skill-dir>/tests` 与 `node <skill-dir>/tests/integration.mjs --modules <video-dir>/node_modules`：维护此 skill 时运行；日常制片不需要读测试源码。
