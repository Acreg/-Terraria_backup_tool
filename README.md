# -Terraria_backup_tool
使用gemini3.1pro整的泰拉瑞亚存档自动备份工具，随缘分享，个人自用，可能不会再更新

Terraria Save Auto-Backup Tool, built with Gemini 3.1 Pro. Shared casually, for personal use only and may not receive further updates.

本工具是一个基于“时间点快照（Snapshot）”架构的泰拉瑞亚存档自动备份程序。它摒弃了容易导致数据错位的散装文件备份法，将人物存档（包含 .map 小地图探索数据）与世界存档在同一时刻打包隔离。这种设计从根本上杜绝了回档时可能产生的“人物与世界状态不同步（例如利用时间差刷物品的 Bug）”问题。支持定时自动备份、历史快照库管理、自动垃圾回收（清理旧存档）以及标准的 ZIP 压缩包导入导出。

This tool is an automatic Terraria save backup program built on the Point-in-Time Snapshot architecture. It discards the loose file backup method, which often causes data misalignment, and packages player saves (including .map minimap exploration data) together with world saves at the exact same moment for isolation.
This design fundamentally prevents desync issues between player and world states during rollbacks (such as item duplication glitches caused by time discrepancies). It supports scheduled automatic backups, historical snapshot library management, automatic garbage collection (cleaning up old saves), and standard ZIP archive import/export.

功能特色:
1.自动备份，解放双手。（也可手动备份）自定义备份间隔（分钟/秒）
2.快照式备份包含单次备份任务的人物、地图存档，备份包含.map 小地图探索数据，备份之后的存档回档后不黑图
3.中英日多语言支持
4.通过注册表自动定位文档位置，智能识别游戏存档位置。游戏存档位置和备份存取位置自由可更改
5.垃圾自动回收机制，自动删除过时快照，时间可自定义
6.v1.7版本后支持tModLoader存档备份，需要打开开关生效，与原版备份功能互不干扰

 Features
1. Automatic backup** for a hands-free experience (manual backup also supported). Customizable backup intervals (minutes/seconds).
2. Snapshot-style backups** include player and world saves from one single backup task, with full `.map` minimap exploration data retained — no unexplored fog on the minimap after restoring from a backup.
3. Multilingual support: Chinese, English, and Japanese.
4. Automatically locates the Documents folder via the Windows Registry and smartly detects the game save path. Both the game save location and backup storage directory are fully customizable.
5. Automatic garbage collection**: automatically deletes outdated snapshots, with a customizable retention period.
6. Added support for **tModLoader** save backups in v1.7 (requires enabling the toggle); works independently from vanilla game backups with no interference.
