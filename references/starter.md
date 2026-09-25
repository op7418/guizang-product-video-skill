# 起步工程：技术底座，不是成片模板

初始化后得到 10 秒、3 镜头的**技术样片**，只证明"真实组件挂载 → 时间轴 → 任意时刻截图 → MP4"这条链路能走通。它刻意没有视觉风格：正式片的画面规范、镜头和手法都按 `DIRECTION.md` 为这个产品重新写。

## 运行

需要 Python 3、Node.js、FFmpeg。先按 SKILL.md 做环境检查，缺项按 [依赖安装](onboarding.md) 补装。

```sh
python3 <skill-dir>/scripts/init_project.py --output <video-dir> --style repo --repo <repo-dir>
cd <video-dir>
python3 <skill-dir>/scripts/check_environment.py --project . --engine browser
npm run build
node stills.mjs evidence/stills 1.5 5 8.5          # 一次会话批量出静帧，并打印页面错误和 API 请求
node render.mjs --from 4 --to 7 --output renders/draft.mp4   # 局部草稿，不需要音频
node render.mjs --silent-demo --output renders/technical-demo.mp4
npm run preview                                     # 浏览器控制台：await seek(4) 或 playFilm()
node cover.mjs                                      # 从 cover/cover.html 导出 3:4 / 4:3 / 16:9 封面（见 references/cover.md）
```

正式导出：

```sh
python3 <skill-dir>/scripts/mix_audio.py plan.json
node render.mjs --audio assets/master.wav --output renders/final.mp4
python3 <skill-dir>/scripts/check_delivery.py plan.json --video renders/final.mp4 --mix-report evidence/audio-mix.json
```

导出逐帧截图（JPEG 中间帧，x264 编码）。50 秒片子、含 WebGL 和模糊滤镜，一般 2–4 分钟；先渲染几秒估算。`--silent-demo` 只用于技术样片；用户要求的正式静音片设 `audioRequired:false` 并记录 `audioExceptionReason`。

## 运行时结构

```
src/client.jsx        挂载 <Film>，等字体和假数据就绪后运行各镜头的 builder，暴露 window.seek / __filmReady
src/engine.js         seek(t)：React 时钟 → 交互驱动 → GSAP 主时间轴 → 镜头显隐 → onRender 画布
src/film-store.js     useShotState(select)：组件按镜头内时间取离散状态（第几步、打了几个字）
src/fake-api.js       固定时钟、固定随机种子、按路径返回 fixture 的 fetch，静默 EventSource/WebSocket
src/fixtures/api.js   接口 fixture；尽量从产品自己的常量/目录派生，保证名字、图标是真的
src/product-context.jsx  产品外壳本该提供的 provider（i18n、主题、tooltip、路由/面板上下文）
src/kit/              Split + reveal（文字拆分入场）、Cursor + paintCursor、offsetCenter / screenCenterAt、setFieldValue / typed / ensureOpen
src/shots/index.js    plan.json 每个镜头 id → 视图组件 + builder
src/film.css          本片的画面规范（字号阶梯、布局），加上逐帧渲染必需的机制
src/adapters/         next/image、next/navigation 等框架运行时的静态替身，按需 alias
```

`seek(t)` 是 t 的纯函数，前后跳转、单帧渲染结果一致：

1. `flushSync` 把时间推给 React。组件用 `useShotState(l => stageAt(l, [...]))` 只在离散状态变化时重渲染，例如工具步骤出现、回复多了几个字。
2. 运行 `onDrive(id, fn)` 注册的驱动，也就是**真实交互**：往真实输入框里打字（`setFieldValue` + `typed`）、点真实按钮打开真实弹层（`ensureOpen`）。驱动要幂等：先按时间算出应有状态，DOM 不同时才动手。需要等弹层定位时返回 Promise，`render.mjs` 会等它。
3. `master.seek(t)`：所有 GSAP 动画都挂在这一条暂停的主时间轴上，用影片绝对时间摆放。
4. 按时间显示/隐藏镜头（前后各留 0.8 秒给转场重叠）。
5. 调用 `onRender(id, fn)` 注册的每帧绘制：Three.js、2D canvas、依赖时间的样式计算。

### 写一个镜头

```jsx
// src/shots/agent.jsx（示意，名字、结构按本片需要来）
export function AgentView() { /* 真实组件 + 本片的排版；GSAP 目标用稳定的包裹层 */ }
export const buildAgent = tl => {
  const s = shot('agent');
  // 1. 先测量（布局已存在）：offsetCenter(el, root)，或 screenCenterAt(tl, t, el) 取 3D 变换后的屏幕位置
  // 2. 再往 tl 上摆动画：tl.fromTo(el, from, to, s.start + 0.4)
  // 3. 注册每帧工作：onDrive('agent', local => ...)、onRender('agent', local => ...)
};
```

- 镜头的起止时间只写在 `plan.json`，代码通过 `shot(id)` 读，时间只有一处来源。
- GSAP 的 `fromTo` 在搭建时就写入起始值，所以测量要放在摆动画之前。
- GSAP 时间轴是 thenable：`await tl` 要等时间轴播完，暂停的主时间轴永远不会结束。builder 可以是 async 函数，但不要 await 时间轴本身。
- React 会重新渲染或条件渲染的节点，不要直接当 GSAP 目标：套一层稳定的包裹层来动。
- 产品里的微动画（motion/framer-motion、CSS transition）会和影片时钟抢状态：`film.css` 已冻结 CSS 动画；用 motion 库的产品在 `client.jsx` 里打开 `MotionGlobalConfig.skipAnimations`。旋转的加载图标这类需要动的，在 `onRender` 里按时间设 transform。
- 背景效果可以参考 `assets/fx-lab/` 改写，见 [视觉手法词汇](visual-vocabulary.md)。

## 接入仓库

1. 在镜头视图里直接 import 该功能的原业务组件和组合层。不要只接几个基础按钮，再手写剩下的界面。
2. 读产品的根布局和 App 外壳，把组件依赖的 provider 写进 `product-context.jsx`，全部用静态值。缺哪个 provider，运行时会直接报错（`xxx must be used within yyy`），按报错逐个补。
3. 组件在 effect 里请求数据的，在 `fixtures/api.js` 按路径给 fixture。`stills.mjs` 输出的 `api` 列表就是实际请求过的路径，用来查漏。
4. 编译产品真实样式到 `src/product.css`（下文），保留主题、字体、图标和状态规则。产品有暗色主题时，`ProductContext dark` 直接启用。
5. 品牌、字体、公开图标放 `public/`（会复制到网页根），修正组件里的根路径引用（如 `/provider-icons/...`）。
6. 构建会写出 `evidence/component-imports.json`；逐镜头记录复用证据，见 [组件接入](component-pipeline.md)。

`--style default` / `hybrid` 会复制默认样式组件；`repo` 不复制。起步样片按 1920×1080 布局，改画幅必须重新排版。

### 解析配置

```js
// integration.config.mjs
import path from 'node:path';
const repo = '/absolute/path/to/product', video = path.resolve('.');
export default {
  repoDir: repo,
  aliases: {
    '@': path.join(repo, 'src'),
    'next/image': path.join(video, 'src/adapters/next-image.jsx'),     // 组件真的用到才加
  },
  external: [], loaders: {}, define: {},
  esbuild: {},   // 其他 esbuild 选项，例如 tsconfigRaw
};
```

构建器打出浏览器 IIFE 包：先从产品的 `node_modules` 解析依赖，React/ReactDOM 统一指向视频工程的那一份（两份 React 会导致 `Cannot read properties of null (reading 'useContext')`）。产品依赖缺失时，只在视频工程安装固定版本的展示依赖。pnpm 等严格隔离的布局按实际 workspace 映射解析路径。含 top-level await 的依赖不能打进 IIFE：换用它的同步入口，或把构建改成 ESM。

monorepo 里直接导出 TS 源码的 workspace 包：把包名 alias 到它的 `src`；带子路径 `exports` 的包，读它的 `package.json` 生成一张子路径 → 源文件的 alias 表。产品开了 `verbatimModuleSyntax` 时，类型导入会被原样保留，可能把服务端运行时拖进浏览器包；用 `esbuild: {tsconfigRaw: {compilerOptions: {verbatimModuleSyntax: false}}}` 只放宽这次展示构建。

暗色 token 挂在 `:root` 的 `dark` 变体上时，`dark` class 必须加在 `<html>` 上（`client.jsx` 挂载前执行 `document.documentElement.classList.add('dark')`），加在某个 div 上不生效。同一画面要同时出现几套主题时，先确认 Tailwind 工具类直接引用 `var(--token)`，再把主题色写成元素级 CSS 变量。

某个 alias 需要"换掉一个模块里的一个导出、其余照旧"时（例如让弹层的 portal 挂进镜头里），adapter 可以先 `export * from '<真实文件绝对路径>'`，再单独导出同名的替身。

### Next / Tailwind 样式链

Tailwind 源 CSS 要先编译。Tailwind v4：创建 `src/product.input.css`，导入产品真实的 CSS 入口，并扫描产品源码和视频源码：

```css
@import "/absolute/path/to/product/src/app/globals.css";
@source "/absolute/path/to/product/src";
@source "./";
```

```sh
npx @tailwindcss/cli -i src/product.input.css -o src/product.css   # 版本与产品一致
npm run build
```

镜头代码里新写了 Tailwind 类，要重新编译。Tailwind v3 用对应版本的 CLI 和继承产品 theme/plugins 的配置，`content` 同时包含产品与视频源码。产品 CSS 里的 `url(...)` 字体/图片要能在 `dist/` 里找到。来源：[esbuild nodePaths](https://esbuild.github.io/api/#node-paths)、[Tailwind CLI](https://tailwindcss.com/docs/installation/tailwind-cli)。

## plan 字段

- `demo`：技术样片 true，正式内容完成后设为 false。
- `product / width / height / fps / duration / style / audioRequired`：工程规格。
- `typography`：默认 `mode:bilingual`，分别指定 `zhFont / enFont`，`zhStyle:sans-serif`；用户指定单语或其他字体时，用 `exceptionReason` 记录依据。
- `shots[]`：`id, start, end, type, headlineEn, headline, plainExplanation, description, descriptionAt, claim, source, component, actions`。镜头在代码里的实现以 `DIRECTION.md` 的镜头表为准，plan 记录时间、事实与声音，两者要一致。
- `claim` 为 true 的镜头必须给 `source`。写法：`file:docs/release.md`（相对视频工程）或 `repo:src/features/panel.tsx`（相对 `plan.repo`），支持 `:行号` / `#L行号`；裸路径先查视频工程再查 `plan.repo`；URL、版本标签、提交引用留给事实核对。品牌开场不需要假造 source。
- `component`：实际源码路径或适配器；字卡可为 null。
- `actions`：唯一 `id`、相对镜头开始的 `at`、动作描述、`soundRequired`。
- `audio.music / audio.cues`：cue 的 `at` 是文件开始的影片绝对时间，`syncOffset` 是文件内听觉落点，满足 `at + syncOffset = 动作时间`。落点用 `scripts/sfx_landmarks.py` 测，不要猜。可选 `onBeat` / `beatDivision` 对照 `audio.beatGrid`。
- `descriptionAt`：说明文字相对镜头开始的出现时间，用于阅读时间提示。

改了分镜或配乐就重新混音；正式导出会核对 plan 与 master 的哈希。通用占位组件带 `data-skill-placeholder`，正式模式下 build 会拒绝仍在画面上的占位内容。

## 接入回归

修改构建器、引擎或 kit 后运行：

```sh
python3 -m unittest discover -s <skill-dir>/tests
node <skill-dir>/tests/integration.mjs --modules <video-dir>/node_modules
```

集成测试在临时目录构造一个产品仓库，验证：只存在于产品里的依赖和 alias 能解析、CSS 资源能复制、组件 effect 通过 fixture API 拿到数据、前后跳转时 GSAP 状态正确、WebGL 能在无头导出里渲染。它不会自动安装依赖。
