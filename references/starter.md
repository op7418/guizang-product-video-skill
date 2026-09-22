# 起步工程：最小可运行，不是通用成片模板

初始化后得到 10 秒、3 镜头的**技术样片**，用于证明 React → HTML → 任意时间截图 → MP4 的链路。文案标注技术样片，音频尚未生成；plan 分别列出 BGM 和两个音效事件。正式制作要替换分镜、组件、品牌、样式和声音。

## 运行

需要 Python 3、Node.js、FFmpeg。新环境先按 SKILL.md 做轻量检查，缺项时由模型按入门指引补装；初始化脚本本身不偷偷联网安装，不调用外部账号。

```sh
python3 <skill-dir>/scripts/init_project.py --output <video-dir> --style repo --repo <repo-dir>
cd <video-dir>
python3 <skill-dir>/scripts/check_environment.py --project . --engine browser
# ready:true 跳过安装；缺项时按 references/onboarding.md 补齐后复查。
npm run build
npm run render -- --still 4 --output evidence/frame-04.png
npm run render -- --silent-demo --output renders/technical-demo.mp4
npm run preview
```

依赖是已验证的固定版本，首次安装保留生成的 lockfile。环境已有可复用依赖时也可以使用，无需改动产品 package.json。`preview` 打印本地 URL；在浏览器控制台用 `playFilm()` 播放或 `seek(4)` 定位。它只预览画面，最终声音用播放器检查。

按 [配乐创作与音效查找](audio-sourcing.md) 用代码创作 `assets/music.wav`；音效先找合适素材，缺项才复制内置 WAV。检查动作和音效 cue 后：

```sh
python3 <skill-dir>/scripts/mix_audio.py plan.json
npm run render -- --audio assets/master.wav --output renders/final.mp4
python3 <skill-dir>/scripts/check_delivery.py plan.json --video renders/final.mp4 --mix-report evidence/audio-mix.json
```

导出脚本逐帧截图；正式长片可切换到已有的高效渲染器。`--silent-demo` 用于技术样片；用户指定的正式静音片设 `audioRequired:false` 并记录 `audioExceptionReason`，渲染时省略 `--audio`。

## 接入仓库

1. 改 `src/presentations.jsx`，实际 import 对应功能的原业务组件及组合层，不能只接几个基础按钮后手写剩余界面。按项目需要在 `integration.config.mjs` 设置 alias、解析路径和明确的环境 stub；不要让初始化脚本猜产品架构。
2. 为依赖注入/上下文设置最小展示 adapter，提供无敏感信息的固定 props。必要时多个镜头使用不同 visual，而不是全部复用同一张卡片。
3. 加载/编译原组件实际依赖的产品样式到 `src/product.css`，保留相关主题、字体、图标和状态规则，不自行抄一份精简颜色/圆角作为替代。Tailwind 类要扫描宣传片源码和真实组件源，避免 CSS 丢失。构建器支持普通 CSS 与 CSS Modules；Tailwind 等预处理链按下文先编译。
4. 品牌、字体和公开图标放 `public/` 或 `assets/`，修正原组件绝对路径。`public/` 会复制到网页根，`assets/` 会保留目录层级。
5. 改 `src/film.jsx` 和 `src/timeline.js` 增加与功能相符的镜头动作。起步样片只有入场动作和进度条，不能代表完整动作设计。
6. 实际 import 图在 `evidence/component-imports.json`；对照清单说明哪些是导入、哪些是适配，不能仅列出没有用到的组件路径。逐功能镜头补充 component-usage 清单，结合静帧验证业务组件真正上镜。

`--style default` / `hybrid` 会复制默认样式组件并接入示例视觉；`repo` 不复制。`hybrid` 的外层默认样式与产品组件样式分别配置。起步样片按 1920×1080 布局；改变画幅必须重新排版，不只改 plan 的尺寸。

## plan 字段

- `demo`：技术样片 true，正式内容完成后设为 false。
- `product / width / height / fps / duration / style / audioRequired`：工程规格。
- `typography`：默认 `mode:bilingual`，分别指定 `zhFont / enFont`，`zhStyle:sans-serif`；用户指定单语/其他字体用 `exceptionReason` 记录依据。
- `shots[]`：`id, start, end, type, headlineEn, headline, plainExplanation, description, descriptionAt, claim, source, component, actions`。英文与中文分别由独立 span 和 `--film-font-en / --film-font-zh` 控制；不再用两行中文宋体做默认标题。
- `descriptionAt`：说明相对镜头开始的出现时间，用于阅读时间预警；应与代码一致。
- `claim` 为 true 的镜头必须提供 `source`（数组，路径或版本证据）。品牌开场不需要假造一个功能 source。
- `component` 指实际源码路径或适配器；字卡可为 null。
- `actions`：每个动作有唯一 `id`、相对镜头开始的 `at`、动作描述与 `soundRequired`。视觉动作仍需模型在时间线上实现。
- `audio.music / audio.cues`：音乐路径与独立音效事件；cue 用影片绝对时间 `at`、动作 `actionId`、音效 `file / gain / role:sfx / kind`；有前奏的声音用 `syncOffset` 表示文件内听觉落点，须与动作对齐。可选 `onBeat:true` 与 `beatDivision` 对照实际测得的 `audio.beatGrid`。混音脚本会实际执行这些 cue。正式导出核对 plan 和 master 的哈希；修改分镜或配乐后重新混音。
- `plainExplanation`：先写清楚的事实解释，非空不等于语义通过；按文案参考做试读并记录改写。

正式渲染前更新 plan 和源码，检查两者时长一致。脚本验证覆盖性，人工核对实现和计划是否一致。

旧工程升级时，在原 plan 补齐这些字段，更新标题 span/CSS，并把旧 sound 描述转为带实际音效文件的 audio.cues。不要重新初始化覆盖用户工程。正式模式缺字段会提示补齐，技术样片保留提醒。

本套工具链的所有生成文件（`plan.json`、`presentations.jsx`、`BRIEF.md`、`audio-mix.json`）均统一采用 UTF-8 编码，以确保跨平台（特别是未开启全局 UTF-8 模式的 Windows CP936 环境）读写中文文案与音频路径时一致。若遇早期版本生成的非 UTF-8 `plan.json`，检查与混音脚本会自动识别并平滑升级为 UTF-8；也可手动执行一键转换：

```sh
python -c "from pathlib import Path; p=Path('plan.json'); p.write_text(p.read_text(encoding='locale'), encoding='utf-8')"
```

`audio.ducking` 默认开启；cue 可按语义使用不同压低幅度与恢复时间。输出 `music-ducked.wav` 和 `sfx-stem.wav` 可分别检查，混音记录保存卡点误差。参数详见声音参考。

通用卡片和默认样式组件示例带有 `data-skill-placeholder` 标记；正式模式仍渲染这些占位内容时，build 会失败。应接入实际功能组件，不是只删标记。这个检查只能拦住未替换的样片，真实复用仍要靠逐镜头来源与实际渲染核对。

## 可运行的仓库接入配置

`init_project.py --style default --repo <repo-dir>` 也会在 BRIEF 和 `plan.repo` 保存仓库；default 只决定影片外层样式。先读取目标功能实际组件，然后配置 `integration.config.mjs`：

```js
import path from 'node:path';
const repo = '/absolute/path/to/product';
export default {
  repoDir: repo,
  aliases: {'@': path.join(repo, 'src')},
  external: [],
  loaders: {},
};
```

在 `src/presentations.jsx` 导入已确认的实际组件。以下路径和 props 应换成目标仓库真实接口：

```jsx
import React from 'react';
import {ModelSelector} from '@/components/chat/ModelSelector';
export function FeatureVisual() {
  return <ModelSelector value="demo-model" options={fixtureOptions} onChange={() => {}} />;
}
// fixtureOptions 由实际组件接口定义；provider 也在此展示入口注入。
```

构建器将业务依赖打入 CJS，`nodePaths` 补充产品的 node_modules 搜索路径，React/ReactDOM 由视频工程统一提供。这样仓库里的图标/UI 包不会因被全部标为 external 而在运行时丢失；额外 external 包需能从视频工程实际解析。若产品 React 主版本不同，视频工程选择兼容版本并验证 hook/provider 行为。产品依赖缺失时，仅在视频工程安装必要的固定版本展示依赖，保留其许可证。`nodePaths` 对 pnpm 等严格隔离布局未必足够，应按实际 workspace 映射解析路径。

普通 CSS、CSS Modules 和导入的字体/图片由 esbuild 处理，输出样式与资源一并复制。SVG 默认当文件 URL；若产品使用 SVGR 组件语义，在视频工程配置相同转换插件。`next/image`、router、运行时 IPC 等按组件真实需要配置显示适配器；这些适配器放视频工程。SSR 只提供静态状态；依赖 effects 或受控交互的功能用客户端挂载，并接入 `seek(t)`。

### Next / Tailwind 样式链

Next 本身无需启动即可 SSR 纯展示组件；`'use client'`、next/font、图片优化和应用级 provider 需要逐项判断。Tailwind 源 CSS 需先编译，不能交给普通 CSS loader 期待其自动展开。读产品 package.json，选同一代构建流程并保留主题、插件、字体和 CSS imports。

Tailwind v4 已有 CLI 时，创建视频工程的 `src/product.input.css`，导入产品真实 CSS 入口，并补充扫描路径：

```css
/* 绝对路径换成实际产品路径；其入口应已包含 Tailwind/theme/plugins。 */
@import "/absolute/path/to/product/src/app/globals.css";
@source "/absolute/path/to/product/src";
@source "./";
```

使用该版本 CLI（产品已经安装时可复用其 CLI；缺失则在视频工程安装与产品匹配的 tailwindcss/@tailwindcss/cli）：

```sh
npx @tailwindcss/cli -i src/product.input.css -o src/product.css
npm run build
```

Tailwind v3 使用对应版本 CLI 和视频侧配置，配置继承产品 theme/plugins，`content` 同时包含产品与视频源码，再输出 `src/product.css`。只有项目实际使用的流程需要接入；遇到 alias/import/plugin 解析错误时按该入口修复。来源：[esbuild nodePaths](https://esbuild.github.io/api/#node-paths)、[packages](https://esbuild.github.io/api/#packages)、[Tailwind CLI](https://tailwindcss.com/docs/installation/tailwind-cli)。

### 验证与耗时

先 build，检查 `evidence/component-imports.json` 含原组件及其依赖，再渲染功能静帧，与产品原界面对照。检查文字、状态、主题、图标和 CSS 资源是否齐全。

默认导出每帧单独截图：48 秒 × 30 FPS = 1440 帧。若单帧约 60 ms，截图约 86 秒，另有启动、加载和编码耗时；普通工程可预留约 2–3 分钟，复杂组件/机器可能更慢。先测少量帧估算，正式长片可用已有框架的高效渲染器。

生产检查至少需要一项 `claim:true`；detail/workspace/macro 需要 component。`source` 的文件写法用 `file:docs/release.md`（相对视频工程）或 `repo:src/features/panel.tsx`（相对 `plan.repo`），支持 `:行号` / `#L行号`。旧式裸路径（如 `src/components/Selector.jsx`、`CHANGELOG.md`）先查视频工程，再查 `plan.repo`；两处都有时以视频工程为准，两处都没有时报错。显式 `file:`、`repo:` 以及 `./`、`../` 路径按指定根目录解析，不回退。URL、版本标签和提交引用留给事实核对；文件存在本身不证明卖点。


### CJS 边界与接入回归

含 top-level await 的 ESM 依赖无法直接打进当前 CJS 包；仅标记为 external 仍可能在同步 require 时失败。优先选择依赖提供的兼容同步入口；确需异步初始化时，在视频工程调整为异步 ESM 构建及加载流程，或改用浏览器挂载，再验证依赖解析与实际状态。官方依据：[esbuild top-level await](https://esbuild.github.io/content-types/#javascript)、[Node require 与异步 ESM](https://nodejs.org/api/modules.html#loading-ecmascript-modules-using-require)。

修改构建器、样式作用域或时间线后，除 Python 回归外运行可选集成测试：

```sh
node <skill-dir>/tests/integration.mjs --modules <video-dir>/node_modules
```

需要现有 esbuild、React/ReactDOM、Playwright 及可启动浏览器；不自动安装依赖。测试在临时目录构造产品仓库，验证仅产品内存在的包、alias、CSS/图片资源、带 transition 的 data-enter 容器前后 seek，以及未被时间线接管的子组件动画。运行结束自动清理临时目录；受限环境的浏览器启动遵循其权限机制。
