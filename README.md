# 短剧单集制作技能

用 `$short-drama-episode-workflow` 从单集剧本制作并复核成片。便携包包含可编辑源码、安装器及 17 个配套技能，包括支持参考音频的泡漫 Seedance、HyperFrames、Remotion 与 video-use。

## 下载和安装

1. [下载便携安装包](./short-drama-episode-workflow-portable.zip?raw=true)，完整解压后打开 `short-drama-episode-workflow` 文件夹。
2. Windows 双击 `Install-Windows.cmd`，默认安装在 `D:\Codex\skills`。macOS / Linux 在该文件夹运行 `sh ./install.sh`。
3. 在 Codex 中说“用 `$short-drama-episode-workflow` 制作这个项目的指定集”。缺少的配套技能会自动补装。

默认 16:9 横屏、480p、每集最多 90 秒。项目可逐项覆盖。所有适用审核通过、已发现的问题修复并复核后才正式交付。

源码入口是解压目录中的 `SKILL.md`，安装器源码是 `scripts/install_portable.go`。

便携包 SHA-256 为 `985fe9013ebb58303c305daba3d7ea48f9b4feeea3874c034c073864e70c2735`。
