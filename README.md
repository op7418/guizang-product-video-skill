# 归藏 product video skill

**软件更新了，顺手把宣传片也做了。**

[![GitHub stars](https://img.shields.io/github/stars/op7418/guizang-product-video-skill?style=flat-square)](https://github.com/op7418/guizang-product-video-skill/stargazers)
[![License](https://img.shields.io/github/license/op7418/guizang-product-video-skill?style=flat-square)](LICENSE)
![Agent Skill](https://img.shields.io/badge/Agent-Skill-252525?style=flat-square)
![Claude Code](https://img.shields.io/badge/Claude-Code-D97757?style=flat-square)
![Codex](https://img.shields.io/badge/Codex-supported-252525?style=flat-square)

把代码库交给 AI，告诉它这次更新了什么，或者想介绍整个产品，就可以开始做一支宣传片：整理卖点、写文案、接入原组件、做动画、写配乐、配音效，最后导出视频和可继续修改的工程。

我把自己做 CodePilot 宣传片时反复打磨的流程，整理成了这个 skill。重点是三件事：**看起来像你的产品，听得懂你在讲什么，看完不会觉得拖沓。**

![归藏 product video skill：软件更新了，宣传片呢？](assets/readme/hero.jpg)

<!-- 在这里粘贴上传到 GitHub 后的视频附件地址。介绍视频不随 skill 安装包分发。 -->

## 30 秒开始

在终端安装：

```bash
npx skills add https://github.com/op7418/guizang-product-video-skill --skill guizang-product-video-skill
```

然后打开你的产品代码库，对支持 skill 的 AI 编程工具说：

> 用 guizang-product-video-skill，把这个项目最近三周的主要更新做成一支宣传片。横版，45–60 秒，中文。先看看代码库自己的组件和设计风格，给我看几张关键画面，再继续做动画和声音。

也可以直接把仓库地址发给它：

> 帮我安装这个 skill：https://github.com/op7418/guizang-product-video-skill ，然后用它给当前项目做一支版本更新宣传片。

首次使用会检查 Node.js、Python、FFmpeg 和渲染依赖，缺什么再按官方安装方式补什么。安装系统软件时，仍遵循你的工具和系统权限设置。

## 它能帮你做什么？

| 你手里的东西 | 它会怎么处理 |
| --- | --- |
| 最近几周的提交、版本说明 | 找出值得讲的变化，整理成几组观众能理解的卖点 |
| 软件的组件和页面 | 优先直接接入原组件、原样式和演示状态，再用代码驱动动画 |
| 已经有一套不错的设计 | 沿用产品的颜色、字体、圆角、层次和交互语言 |
| 暂时没有成熟的宣传视觉 | 用内置的 CodePilot 暖白／炭黑样式组织外层画面 |
| 几句很技术的更新描述 | 写成完整的白话句子，让人知道改了什么、用起来有什么不同 |
| 一支只有画面的片子 | 为本片用代码写配乐，给操作配独立音效，并在关键音效出现时压低音乐 |

画面由代码渲染，能继续修改。标题、功能特写、完整工作区和细节镜头交替出现，既有大字文案，也留出看清操作的时间。

![真实组件与中英文排版](assets/readme/components.jpg)

## 三种风格，先选适合你的

第一次制作时，AI 会先确认风格。已经说过的选择会沿用，不需要每次重新回答。

| 模式 | 适合什么情况 |
| --- | --- |
| **沿用产品风格 `repo`** · 推荐 | 产品已有完整设计，希望宣传片一眼就像自己的软件 |
| **默认样式 `default`** | 想先用 CodePilot 的暖白、炭黑、卡片层次和中英文排版开始制作 |
| **混合 `hybrid`** | 保留软件内部的真实界面，把外层文案、取景和节奏做得更适合传播 |

三种模式的功能镜头都会优先用原产品组件。默认样式主要负责外层排版和视觉包装；接入受平台或框架限制时，会说明原因和替代方式。

英文标题与中文说明分开指定字体。英文负责节奏和排版，中文把事情说清楚；也可以直接要求全中文或全英文。

## 怎么提需求，比较容易一次做好？

不需要写一份很长的 brief，把**介绍什么、给谁看、发在哪里**说清楚就够了。

**做一支版本更新片**

> 介绍 v2.1 到 v2.4 的主要更新，优先讲多模型切换、文件预览和浏览器操作。发 B 站，横版 50 秒左右。沿用我们的产品设计，文案口语化一点，不要把提交记录逐条念出来。

**给海外用户看**

> 做一支英文版 changelog promo，45 秒，主要面向第一次接触产品的人。先解释这几个更新能解决什么问题，再展示操作。保留产品原组件和字体。

**先看方向再做成片**

> 先整理卖点、分镜和四张真实渲染的关键画面。风格用默认 CodePilot 样式，中文配英文标题，等我确认后再做完整动画。

**修改已经做好的片子**

> 模型选择那一段太慢了，压缩到三秒。通知出现时加一个清楚的叮咚声，音乐让一下。最后去掉官网地址，浏览器里能看出链接的地方也遮掉。

不用一次把所有信息填完；已有上下文会继续使用，影响制作的缺项才会问你。

## 从代码库到成片

1. **先定范围。** 确认产品、更新范围、受众、发布平台、画幅、语言和风格，有参考视频就一起给。
2. **找真实内容。** 查版本与代码，核对功能状态，把真实组件挂载起来，按视频尺度放大上镜。
3. **先定方向。** 拆解参考，提炼产品气质，提出三个差异明显的方向并选定；每个视觉手法都要说得出"因为产品有什么"；把字号、界面倍数、镜头表写成具体数字，再动手。
4. **逐镜头搭建。** GSAP 主时间轴编排动画，Three.js / canvas 做背景层，真实组件用真实点击和输入驱动；每个镜头搭完就出静帧对照。
5. **把声音配好。** 按分镜编曲、按产品气质选音色，音效先用录音素材，实测落点后对齐动作，混音并处理音乐让位。
6. **审片，再导出。** 看联系表、看每个转场、看信息密集的全尺寸帧，改完重新导出。
7. **需要的话做封面。** 3:4、4:3、16:9 三种比例，画面语言沿用这支片子，只用片中真实渲染的画面。

每支片子的手法都从产品本身推导出来，不是套同一个模板：同样的流程，给笔记产品和给开发者工具做出来的片子应该完全不一样。

## 同一套流程，三支不一样的片子

下面三支片子用的是同一套流程，画面和声音却完全不同：每支片子都先回答"这个产品有什么"，再决定"所以画面怎么做"。

| 产品 | 从产品里找到的东西 | 所以这支片子这样做 | 声音 |
| --- | --- | --- | --- |
| **CodePilot**（桌面 AI 编程客户端） | 接入多家模型服务商；深色、有质感的桌面应用 | 暗色舞台和银白光弧；粒子汇成标志；服务商围绕产品旋转；看板飞越 | 120 BPM 电影感电子 |
| **Zed**（多人协作代码编辑器） | 编辑器本身就是主角；队友光标实时出现 | 浅色一镜到底，镜头一直在编辑器里走；标题是敲出来的代码注释；队友光标带路，最后画出标志 | 128 BPM 马林巴打击乐 |
| **T3 Code**（开源的 coding agent 控制台） | 定位是 "control plane"；自带 5 套主题；每个 harness 各有一条登录命令 | 全片是一块 3×3 控制台面板，镜头推进哪张卡片就进入哪一章；每章换一套产品内置主题色；开场五个终端敲五条登录命令，再被吸进面板 | 96 BPM lo-fi 电钢琴 |

同一个工作区连续做片时，也会避开上一支用过的开场、转场和背景手法。

默认起点是 **45–60 秒、横版、中文**。你可以调整时长和画幅；竖版需要重新安排取景和文字，通常不会直接裁掉左右两边。

## 音乐和音效怎么来？

**音乐按顺序选：你给的曲子 → 本机真的能跑的音乐生成模型 → 代码原创合成。** 代码合成时保留编曲源码，按本片的镜头边界排段落、按产品气质选音色。仓库里有两种气质的合成示例（轻快键盘、电影感电子），借的是手法，不是曲子。

**音效先找合适的，再用内置素材补缺。** 先搜索可用素材库并记录来源、许可和适合的动作；没有合适素材的类别，再使用随包提供的 11 个代码合成 WAV，或调整合成参数。

**音乐和音效分开混。** 点击、弹出、切换、完成提醒等动作有独立的音效事件。关键反馈出现时音乐会短暂降低，让叮咚、确认和转场真正听得见。

![配乐、动作音效与音乐让位](assets/readme/audio.jpg)

## 最后会拿到什么？

- 一支可以发布的 **MP4**。
- 一个可以继续修改、重新渲染的 **视频工程**。
- 几张关键画面，方便确认方向或后续做封面。
- 组件来源、素材来源、声音事件和检查记录，方便以后追溯与调整。

自动检查能发现部分结构、文件和时间线问题；文字是否好懂、画面是否舒服、声音是否合适，还需要实际观看和试听。工程会区分已经验证的内容和仍有条件限制的部分。

## 安装与更新

### 用 skills CLI 安装

```bash
npx skills add https://github.com/op7418/guizang-product-video-skill --skill guizang-product-video-skill
```

按提示选择你的 AI 工具和安装范围。需要更新时，可以让 AI 从本仓库检查并更新已安装的 skill；如果本地改过文件，先保留自己的修改。

### 手动安装

**Codex：**

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/op7418/guizang-product-video-skill.git \
  ~/.agents/skills/guizang-product-video-skill
```

**Claude Code：**

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/op7418/guizang-product-video-skill.git \
  ~/.claude/skills/guizang-product-video-skill
```

安装目录可参照 [Codex 官方说明](https://learn.chatgpt.com/docs/customization/overview#skills) 和 [Claude Code 官方说明](https://code.claude.com/docs/en/skills#choose-where-skills-load)。上面的通用安装命令使用 [skills CLI](https://github.com/vercel-labs/skills)。

重新打开会话，让工具读取新安装的 skill。手动 clone 且没有本地修改时，可在安装目录里运行 `git pull --ff-only` 更新。

也可以下载仓库 ZIP，解压后把包含 `SKILL.md` 的文件夹放入对应的 skills 目录，文件夹命名为 `guizang-product-video-skill`。

## 需要什么环境？

内置起步工程使用 React、esbuild 和 Playwright 输出画面，再由 FFmpeg 编码。已有 HyperFrames 工程也可以沿用。

| 依赖 | 用途 |
| --- | --- |
| Node.js ≥ 22、npm | 构建组件、运行浏览器渲染工具 |
| Python ≥ 3.9 | 初始化工程、环境检查、配乐和混音脚本 |
| FFmpeg / ffprobe | 音频处理、视频编码和文件检查 |
| Playwright Chromium | 内置浏览器管线的静帧和逐帧渲染（WebGL 走 SwiftShader） |
| React、GSAP、Three.js | 挂载真实组件、主时间轴动画、背景效果层（装在视频工程里） |
| 产品仓库与其依赖 | 直接接入原组件及样式 |

依赖安装说明按需加载，见 [入门与依赖检查](references/onboarding.md)。无需为了使用内置浏览器管线额外购买视频服务；AI 编程工具本身及你选择的外部服务按各自规则使用。

不同组件框架的接入工作量不同。React 代码库有现成示例；monorepo 的 workspace 包、特殊的 TypeScript 编译选项可以在视频工程的 `integration.config.mjs` 里映射和放宽，不用改产品代码。需要服务端、原生运行环境或复杂上下文的组件，可能还需要展示适配层；实在接不进来的界面按源码忠实重建，并在证据里逐项标明。

## 仓库里有什么？

```text
LICENSE                  GNU AGPL-3.0 主许可证
COMMERCIAL_LICENSING.md   单独商业授权的合作入口
SKILL.md                 工作流、硬约束和工具入口
agents/                  Codex 的展示信息
references/              影片方向、视觉手法词汇、组件接入、分镜文案、音频、审片、封面、依赖与验收方法
scripts/                 初始化、环境检查、音效落点测量、合成音效、混音、交付检查
assets/starter/          可运行的起步工程（技术底座，不带风格）
assets/fx-lab/           可改写的视觉手法样例（流线场、粒子汇聚、字符场、地平线、切片、环绕）
assets/fallback/         CodePilot 默认样式与展示组件
assets/audio/            两种气质的配乐合成示例、11 个内置音效及来源说明
assets/readme/           本页使用的介绍片画面
tests/                   脚本回归测试与组件接入测试
```

维护这个 skill 时，可以运行：

```bash
python3 -m unittest discover -s tests
node tests/integration.mjs --modules <某个视频工程>/node_modules
```

接入与渲染说明见 [起步工程](references/starter.md)，完整制作入口见 [SKILL.md](SKILL.md)。

## 常见问题

**只能给 CodePilot 做视频吗？**

可以用于其他软件。CodePilot 提供的是默认样式和这套流程的实践案例，正常使用优先接入你自己的产品组件。

**是让模型生成一段视频吗？**

这里的主要画面由代码、组件和时间轴渲染，配乐也由代码合成。你可以继续改文字、布局、时长、动画和声音，再重新导出。

**给一个仓库地址就能直接出片吗？**

有时还需要下载仓库、补齐依赖和确认演示状态。它是一套让 AI 逐步完成作品的制作流程，不是忽略项目环境的一键转换器。

**默认样式能随便商用吗？**

默认样式中改编自 CodePilot 的组件与样式保留原有 BSL 授权，使用前请阅读 [来源说明](assets/fallback/SOURCE.md) 和 [LICENSE.CodePilot](assets/fallback/LICENSE.CodePilot)，根据具体用途判断适用条件。这里没有把默认样式重新授权为 MIT。

**能换成自己的音乐、Logo 或参考片吗？**

可以，把素材和要求交给 AI。参考片用于理解节奏和表现方式；引入的素材需要有适用的使用许可，并保留来源。

## 反馈与改进

欢迎在 [Issues](https://github.com/op7418/guizang-product-video-skill/issues) 分享作品、问题和改进建议。反馈时最好带上使用的 AI 工具、产品技术栈、失败阶段，以及脱敏后的日志或画面。

如果你也想让 AI 帮你做图文，可以看看 [归藏社交媒体卡片 skill](https://github.com/op7418/guizang-social-card-skill)。

## License

GNU AGPL-3.0 © 2026 [op7418](https://github.com/op7418)

除下文明确单独授权的内容外，本仓库的工作流、文档、脚本、起步工程和原创音频资产采用 **GNU AGPL-3.0**，完整条款见 [LICENSE](LICENSE)。

- 复制或分发时保留版权、许可证和相关声明；发布修改版时说明修改内容。
- 分发受该许可证约束的修改版或衍生程序时，遵守 AGPL-3.0 对许可和对应源码的要求。
- 修改后的程序支持远程网络交互时，应按第 13 条向与其交互的用户提供免费获取该版本对应源码的方式。
- AGPL-3.0 允许商业使用和收费分发；收费不会免除适用的许可证与源码提供义务。

**单独授权的内容：** [assets/fallback/](assets/fallback/SOURCE.md) 中改编自 CodePilot 的组件和样式继续适用 [Business Source License 1.1](assets/fallback/LICENSE.CodePilot)，包括其中的 Additional Use Grant 和 Change Date。它们不因主许可证的加入而改为 AGPL。使用、修改或分发包含这些组件的工程时，需要同时核对相关条款，不能将混合后的工程整体宣称为仅受 AGPL 约束或可无限制商用。

接入的产品组件、Logo、字体、第三方音乐或音效，依各自适用许可使用。生成的视频也不会仅因使用本工具就自动变为 AGPL 作品；若输出包含受保护的组件、素材或代码，其适用条款仍需保留和遵守。

如需闭源集成、白标、平台内置、上架合作或不适用 AGPL 条件的单独授权，请参阅 [商业授权合作说明](COMMERCIAL_LICENSING.md)。本节是阅读指引，具体权利与义务以适用许可证或双方书面协议为准。
