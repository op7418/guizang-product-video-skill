# 声音与成片检查

## 配乐与音效

先按 [配乐创作与音效查找](audio-sourcing.md) 完成选材：音乐默认用代码原创，音效先找与产品/动作相符的录音素材，缺哪一项才用内置音效补哪一项。先确定音乐气质、节拍和收束位置，再安排动作。原案例使用 120 BPM；其他产品按实际分镜选择速度、旋律和配器，不要求同一首曲子。

建立与 `plan.json` 一致的 `audio.cues`：`at / actionId / file / gain / role`。`at` 是影片绝对秒数；动作的 `at` 是相对镜头开始的秒数，cue 对应 `shot.start + action.at`。音效落在动作发生点，而非机械地加在每个镜头开头。选中用轻 click/pop，结构变化才用 whoosh，通知用能被识别的提示音，结尾给一次收束。

许可要区分“能用于成片”和“能随模板重新分发原音频”。这个 skill 不捆绑原案例的 Pixabay 录音，也不携带商业字体。将音频下载进当前视频项目时记录来源及许可，不把项目许可自动视为 skill 的再分发许可。

## 从“写了音效”到“真的听得见”

每个核心功能组选一个最有反馈感的状态变化（选中、打开、完成、通知），将对应 action 标为 `soundRequired: true`。不是每个字入场都加声，但不能只在最后放个音就跳过中间所有关键动作。完成/通知使用可辨认的双音叮咚或确认音；不要只有 whoosh。

声音检查分三步：先单独听 `sfx-stem.wav`，确认关键事件有音效；再听 master，确认没有被配乐淹没；最后听编码后的 MP4，确认剪辑/导出没有漏掉。只检查文件存在或音轨数量都不够。有能力试听时按动作逐项检查；无法试听要准确标明，不假装已通过听感验收。

找不到合适音效时，直接从 [内置音效目录](../assets/audio/sfx/) 复制所缺的 click/click-alt、pop、toggle、typing、ding-dong、success、error、resolve、whoosh 或 sweep。这些是现成的原创 WAV，不需要先运行生成器；需要调整音色时才改 `make_sfx.py`，输出到新目录。

**增益要按实测电平设。** 内置音效峰值约 −20 dBFS，录音素材接近 0 dBFS；同样的 gain，前者会被配乐盖住。用 `scripts/sfx_landmarks.py` 查每个文件的峰值电平和落点。混音后可以逐个 cue 比较音效轨与压低后音乐在出现那一刻的峰值：音效不应明显低于音乐。

```sh
# 将代码原创配乐输出到 assets/music.wav。
# 按 audio-sourcing.md 查找音效，缺项复制内置 WAV；再修改 plan 的动作和 cue。
python3 <skill-dir>/scripts/mix_audio.py plan.json
```

`mix_audio.py` 输出 `assets/sfx-stem.wav`、`assets/music-ducked.wav`、`assets/master.wav` 和 `evidence/audio-mix.json`，对混音做双遍响度处理。配乐太响时应调低音乐 gain，音效太轻应调整对应 cue。现有 HyperFrames/Remotion 混音器也可以使用，但保留等价的素材、音效事件、混音来源与最终输出证据。

配置结构（示意；时间应来自实际镜头）：

```json
{
  "audioRequired": true,
  "sfxRequired": true,
  "audio": {
    "music": {"file": "assets/music.wav", "gain": 0.65},
    "cues": [{"at": 12.2, "actionId": "task-finished", "file": "assets/sfx/ding-dong.wav", "gain": 0.7, "role": "sfx"}]
  }
}
```

对应动作例如：镜头从 12 秒开始，`actions` 中有 `{"id":"task-finished","at":0.2,"action":"任务完成通知出现","soundRequired":true}`。cue 应与该动作对齐，听觉落点与动作通常控制在 1 帧内，检查上限为 2 帧。用户明确要无音效时记录 `sfxRequired:false` 和 `audioExceptionReason`；全静音设 `audioRequired:false`。这类例外遵从用户，不由模型自行决定。

## 音效响时给它让位置

默认开启 `audio.ducking`。原来只有固定音乐 gain，重要提示仍可能被盖住；现在按 cue 预先降低音乐，音效结束后再平滑恢复。不是整首曲子一律变小，也不是突然静音。

下表是本 skill 的试听起点，**不是官方音频标准**；根据音乐密度和音效音色调整：

| 声音职责 | 配乐压低 | 起音前压低 / 主要保持 / 恢复 |
| --- | --- | --- |
| 点击、切换、轻弹出 | 约 3–3.5 dB | 40ms / 100–120ms / 200–240ms |
| 输入细节 | 约 2.5 dB | 40ms / 350ms / 250ms |
| 转场 | 约 4 dB | 40ms / 160–200ms / 300–350ms |
| 完成、通知、重要确认 | 约 5–6 dB | 40ms / 350–450ms / 350–400ms |
| 品牌收尾 | 约 5 dB | 40ms / 550ms / 450ms |

混音脚本使用确定的音量包络；多个音效重叠时取当前最深的压低，不把衰减层层相乘。逐项可调：

```json
{"audio":{"ducking":{"enabled":true}},"cueExample":{"kind":"ding-dong","duck":{"db":6,"attack":0.04,"hold":0.45,"release":0.4}}}
```

`cueExample` 是字段示意，实际放在 `audio.cues[]`。全局设置会覆盖类型预设，cue 的 `duck` 再覆盖全局；没有理由不要给所有声音同样强度。听到音乐不断抽动时减少不必要的 cue、减小压低或延长恢复。音效仍被掩盖时先检查音色冲突、调整 BGM 与 SFX 相对音量，再看局部压低，不只提高最终 master 音量。

若改用实时侧链，FFmpeg `sidechaincompress` 用第二路信号控制第一路的压缩，需调 threshold/ratio/attack/release；本工具选择已知 cue 的音量自动化，更容易预先让位和重复验证。滤镜语法依据 [FFmpeg volume](https://ffmpeg.org/ffmpeg-filters.html#volume) 与 [sidechaincompress](https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress)，延迟依据 [adelay](https://ffmpeg.org/ffmpeg-filters.html#adelay)。

## 卡点和声音的变化

1. 听/分析实际音乐，确定 BPM 与第一拍时间；节奏不固定时记下实际拍点，不编一个 120 BPM。主要转场可对重拍，轻操作不必全对重拍。
2. 图像和声音一起调整时间。`cue.at` 是文件开始，`syncOffset` 是文件内部的听觉落点，因此 `cue.at + syncOffset = shot.start + action.at`。落点用 `scripts/sfx_landmarks.py` 实测：点击类取起音点，whoosh/冲击取峰值（它们要比画面先开始）。
3. 使用节拍网格时填 `audio.beatGrid:{bpm,offset}`；需要对拍的 cue 标 `onBeat:true`，可用 `beatDivision:1|2|4` 对四分/八分/十六分音符。混音记录会报告与动作、最近拍点相差多少帧；只报告，不悄悄挪动音效造成音画错位。
4. 30–60 秒影片一般选 4–6 种职责：选择/确认、弹出/切换、键入、空间转场、完成/通知、收尾。类别服务画面，不为满足数量虚构异常或通知。短片可更少。
5. 连续点击可用 click/click-alt 做轻微音色变化，输入声是有节奏的短簇，转场音只留给画面结构变化，叮咚保留给值得注意的状态。不要所有字出现都“叮”一下。
6. 最后分别听音乐轨、音效轨、完整混音及最终 MP4；检查提示声的第一下是否被盖住、拖尾是否被切断、节奏是否拥挤。

## 混音

音乐应听得见但不疲劳；无配音短片可把最终混音约 -16 LUFS、true peak 不高于 -1 至 -1.5 dBTP 当起点，并依据平台要求和听感调整。不同平台/题材不强制同一数值。有配音时给人声留空间，根据听感做 ducking。

需要标准化时可用 FFmpeg loudnorm 双遍处理：先测量，读取 measured_I/TP/LRA/thresh/offset，再把测量结果带入第二遍；不要仅靠峰值归一化判断听感。最终 AAC 编码后重新测 true peak，因为编码可能产生新峰值。报告 `normalization.normalization_type` 保存第二遍 loudnorm 实际采用的 linear/dynamic 模式。音乐超过片长 1 秒时脚本输出警告并写入报告；自动截断和淡出后需要确认结尾，必要时重新编曲。

核对音乐与画面同长度、片头不突响、片尾自然结束、音效不削波、不突然静音。用播放器试听最终文件；若环境只能测量，明确未完成试听，不能称为“已经听过”。

## 自动检查

```sh
python3 <skill-dir>/scripts/check_delivery.py plan.json --video renders/final.mp4 --mix-report evidence/audio-mix.json > evidence/delivery-check.json
ffmpeg -i renders/final.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json -f null -
```

正式模式（`demo:false`）中，脚本还会拒绝缺中英标题、缺字体分工、关键动作没有 cue、仅有 BGM、混音记录过期或素材哈希变化。脚本不能从 MP4 中自动分离并判断音效听感；内置导出器会核对传入 master 与混音记录的哈希，其他导出器需自行验证轨道接线。

脚本发现时间缺口/重叠、错误规格、缺少音轨、卖点无来源会失败；阅读时长和类型过于单一发出提醒。不能据此宣布卖点真实、视觉无裁切或音乐好听。

`--video` 还会给出 `pacing`（静止帧比例、最长静止段、硬切次数），只用来定位该回看的片段。大面积纯色背景、小区域运动容易被算成静止；不要为了数字加入无意义动画。画面审阅方法见 [审片](review.md)。

## 最终人工检查

| 检查对象 | 具体看什么 |
| --- | --- |
| 叙事 | 第一次看能说出有哪些更新、对自己有什么用 |
| 阅读 | 中文单独读也知道操作对象、动作、结果；没有泛泛口号；说明出现够早 |
| 标题 | 英文有实际语义且处于标题层级；中文统一无衬线；两种语言的字体分别加载 |
| 画面 | 首帧/中间/末帧、所有转场前后；没有误空屏、裁切、跳动、裂图 |
| 品牌 | 正确产品名、正式完整 Logo、与仓库一致的视觉识别 |
| 事实 | 功能状态有证据；示例不冒充客户成果或跑分 |
| 组件 | 原业务组件及样式实际上镜；构建图、状态驱动、来源清单与静帧一致；没有以基础控件或 tokens 复刻冒充整项功能复用 |
| 音频 | BGM 与关键动作 SFX 都可闻；完成/通知反馈清楚；动作对齐；不刺耳、不爆音、结尾完整 |
| 链接 | 按用户要求隐藏 URL/CTA，遮挡在缩放移动中不泄漏 |
| 一致性 | 预览和 MP4 都检查，最终修改确实进入导出文件 |

用最终 MP4 抽取关键帧，而不仅复用导出前截图。交付时附正确文件路径与清楚的成片状态，不把技术样片、未混音版、早期版本误当最终版。
