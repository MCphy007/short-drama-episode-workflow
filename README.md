# 短剧单集制作技能

用 `$short-drama-episode-workflow` 从单集剧本制作成片。首集、续集及已有剪辑工程都可以使用。默认横屏 16:9、480p，每集成片最多 90 秒，项目可以逐项覆盖。交付前须记录最终版本、审核结果和已修复问题，全部适用项目通过后才交付。

对白场景默认优先双人同框与连续交流，减少机械的逐句单人正反打；在重要信息、决定或情绪转折处保留有作用的近景。分镜、起始图、视频提示词与剪辑共同落实，创作者另有要求时按其要求执行。

在 Codex 连接官方 LibTV 插件并授权后，可读取 LibTV 定稿、复用画布资产、按实时积分投产，并将本地验收版同步回本集画布。续作沿用项目渠道。详见 [LibTV 画布制作](./short-drama-episode-workflow/references/libtv-production.md)。

## 在另一台电脑安装

1. 使用有权限的 GitHub 账号[下载整个仓库 ZIP](https://github.com/MCphy007/short-drama-episode-workflow/archive/refs/heads/main.zip)，完整解压。
2. 打开解压目录里的 `portable-download.html`。它会在本机从 `portable-parts` 还原安装包并验证 SHA-256。显示“校验通过”后，点击“保存便携安装包 ZIP”。
3. 完整解压刚保存的 `short-drama-episode-workflow-portable.zip`，进入其中的同名技能目录。**Windows** 双击 `Install-Windows.cmd`，默认安装到 `D:\Codex\skills`。**macOS 或 Linux** 运行 `sh ./install.sh`。
4. 打开 Codex，输入“用 `$short-drama-episode-workflow` 制作这个项目的指定集”。包内包含总控与 17 个依赖技能，包括泡漫 Seedance、HyperFrames、Remotion 和 video-use。

## 源码与校验

[浏览总控 SKILL.md](./short-drama-episode-workflow/SKILL.md)。安装包内还有完整的可编辑源码、交付审核标准、安装器源码和六种系统及架构组合的安装器。

当前便携 ZIP 为 11,043,695 字节，SHA-256 为 `e1126aee56482be274c4fd49448d33b3160bc609f7e5f27a5f5704209c6939fa`。
