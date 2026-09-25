# 音频示例与内置音效来源

- `score-example-keys.py`：CodePilot 早期 48 秒宣传片的配乐部分（D 大调，和弦铺底、短音旋律、轻鼓），只依赖 Python 标准库和 FFmpeg。
- `score-example-cinematic.py`：CodePilot 50 秒影片的配乐（F 小调，supersaw 铺底、pluck 琶音、侧链鼓组、上升音、冲击和卷积混响），依赖 numpy/scipy/soundfile。
- 两个示例都由波形、噪声、包络和音符编排生成，没有外部采样、没有生成模型调用。它们是两种不同气质的改编参考，不是每个产品的固定配乐：借用合成与编曲手法，调性、速度、配器和段落时间按新片重新推导。
- `sfx/*.wav`：由本 skill 的 `scripts/make_sfx.py` 生成，48 kHz、单声道、16-bit PCM。包含 click、click-alt、pop、toggle、typing、ding-dong、success、error、resolve、whoosh、sweep，共 11 种；各文件时长与 SHA-256 见 `manifest.json`。没有第三方录音或参考视频采样。
- 这些原创音效按用户要求随 skill 提供，供宣传片在未找到合适素材时使用和调整；不是原片使用的 Pixabay 录音。它们的来源说明不扩展到外部下载素材，也不改变 `assets/fallback/` 中组件所附的许可证。
- 本目录不包含 Pixabay 原始录音，也不包含混入这些录音的原片 master。原录音来源与查找方法见 [配乐创作与音效查找](../../references/audio-sourcing.md)。

使用时先按画面职责找合适音效，只复制缺项；要改变音色可在新目录重新生成。素材与音乐组合后仍须试听、调整 gain、对齐动作，并在音效出现时平滑压低音乐。
