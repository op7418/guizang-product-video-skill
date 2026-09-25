# 依赖安装（仅有缺项时读取）

先确认风格并初始化视频目录，再运行 `check_environment.py --project <video-dir>`。Python 不存在时先补 Python。检查脚本只用标准库，缺依赖也可运行并列出需要安装的项目。

## 安装范围与验证

| 路径 | 所需环境 |
| --- | --- |
| 起步工程 | Python ≥3.9、Node ≥22、npm、FFmpeg/FFprobe；项目内 React、ReactDOM、esbuild、GSAP、Three.js、Playwright 及其可启动的 Chromium |
| 代码合成配乐（可选） | 使用 `score-example-cinematic.py` 这类依赖 numpy/scipy/soundfile 的脚本时，在视频工程里建 venv 安装，不装进系统 Python |
| HyperFrames | 对应版本的官方运行要求、FFmpeg/FFprobe、可启动 Chrome；本 skill 音频脚本需要 Python |
| 其他已有框架 | 保留框架与 lockfile，补齐其实际缺项 |

先复用可用环境。下面命令只执行缺项；安装前查询链接中的**当前官方说明**核对系统支持、包名和所需版本。稳定下限用于兼容性判断，新装优先受支持版本。安装后的实际版本、锁文件和运行结果记录进项目；历史验证日期不代表未来兼容承诺。

执行后重跑检查。同一错误在安装后仍出现时，先读错误区分权限、系统库、网络和版本问题，再针对原因处理，避免反复下载。系统权限按当前执行环境的权限机制处理。

## 系统工具

### macOS

已有 Homebrew 时，按缺项选择命令。安装前可用 `brew info <formula>` 核对包信息：

```sh
brew install ffmpeg
brew install node
brew install python
```

来源：[FFmpeg](https://formulae.brew.sh/formula/ffmpeg)、[Node](https://formulae.brew.sh/formula/node)、[Python](https://docs.brew.sh/Homebrew-and-Python)。若需要 Node LTS，按 [Node 下载页](https://nodejs.org/en/download) 与 Homebrew 当前 formula 选择受支持的 LTS；已有可用 Node 保留原版本。版本化 formula 的 PATH 用实际 `brew --prefix <formula>` 和安装输出确定。

没有 Homebrew 时可使用已有工具或 [官方安装器](https://docs.brew.sh/Installation)。需要安装 Homebrew 时，从官方文档取当前命令，查看脚本后执行；不在此冻结安装脚本版本。

### Debian / Ubuntu

```sh
sudo apt-get update
sudo apt-get install -y ffmpeg python3
```

仅缺一项时缩减包列表。Node 可复用现有 nvm：

```sh
nvm install --lts
nvm use --lts
```

nvm 未安装时，按 [nvm 官方安装说明](https://github.com/nvm-sh/nvm#installing-and-updating) 获取当前版本化脚本 URL，下载查看后执行；可用 `PROFILE=/dev/null` 避免修改 shell 配置，再加载安装输出中的实际 `nvm.sh`。其他发行版按其包管理器及 [FFmpeg 下载页](https://ffmpeg.org/download.html) 处理。

### Windows / PowerShell

先查询并核对包身份，再安装实际返回的准确 ID。例如：

```powershell
winget search --name Node.js
winget search --name FFmpeg
winget search --name Python
# 将 package-id 替换成查询结果与官方说明核对后的精确 ID：
winget show --id <package-id> --exact
winget install --id <package-id> --exact
```

来源：[WinGet search](https://learn.microsoft.com/en-us/windows/package-manager/winget/search)、[WinGet install](https://learn.microsoft.com/en-us/windows/package-manager/winget/install)、[Python Windows 安装说明](https://docs.python.org/3/using/windows.html)、[FFmpeg 官方列出的 Windows 构建](https://ffmpeg.org/download.html)。Python 包身份/安装管理器以当时官方说明为准，不冻结 Store ID。安装后刷新会话 PATH，使用实际 `python` / `py -3` 命令验证。

## 项目依赖与浏览器

在视频工程目录内，有 package-lock.json 使用 `npm ci`；首次无锁文件使用 `npm install`。其他管理器沿用现有锁文件。起步工程 package.json 的固定版本是可复现基线；升级时测试后更新，不为每次制片自动升级。

浏览器版本跟随项目 Playwright；仅缺对应浏览器时：

```sh
npx playwright install chromium --only-shell
```

此命令适合起步工程默认 `headless:true`、未指定 channel 的导出。工程需要有头 Chromium 时去掉 `--only-shell`。Linux 缺系统库时可用 `npx playwright install --with-deps chromium`。依据 [Playwright 浏览器文档](https://playwright.dev/docs/browsers)，headless shell 与完整 Chromium 是独立文件，**以真实 launch 成败验收**。沙箱/权限导致 launch 失败时处理执行权限，重新下载浏览器无助于修复。

起步工程的导出脚本带 `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`，让 Three.js/WebGL 在无头模式下用软件渲染；环境检查实际启动浏览器时也带同样参数。

## HyperFrames

沿用已有版本。新工程需要 CLI 时，先核对 [官方 CLI 文档](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-cli/references/doctor-browser.md) 和当前 `--help`，再执行：

```sh
npm install --save-dev --save-exact hyperframes
npx hyperframes doctor --json
# 仅缺 Chrome 时：
npx hyperframes browser ensure
```

锁定实际安装版本。doctor 按实际缺项解释：本地渲染需要 Node、FFmpeg、FFprobe、Chrome；未选择的 TTS、Whisper、MusicGen、Docker 不构成必装依赖。doctor schema 改变时更新检查适配器，而不是反复安装已存在的软件。只有使用 Docker 渲染时才处理其依赖。框架 CLI 与其他 skill 分开安装，按任务实际需要选择。

## 复查

```sh
python3 <skill-dir>/scripts/check_environment.py --project <video-dir> --engine browser --force
```

HyperFrames 改为 `--engine hyperframes`。成功后继续原分镜工作；只有缺项才重新读取对应段落。平台安装语法来自上述官方来源，实机覆盖以验证记录为准。
