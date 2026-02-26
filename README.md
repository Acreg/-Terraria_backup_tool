# -Terraria_backup_tool
使用gemini3.1pro整的泰拉瑞亚存档自动备份工具，随缘分享，个人自用，可能不会再更新

Terraria Save Auto-Backup Tool, built with Gemini 3.1 Pro. Shared casually, for personal use only and may not receive further updates.

本工具是一个基于“时间点快照（Snapshot）”架构的泰拉瑞亚存档自动备份程序。它摒弃了容易导致数据错位的散装文件备份法，将人物存档（包含 .map 小地图探索数据）与世界存档在同一时刻打包隔离。这种设计从根本上杜绝了回档时可能产生的“人物与世界状态不同步（例如利用时间差刷物品的 Bug）”问题。支持定时自动备份、历史快照库管理、自动垃圾回收（清理旧存档）以及标准的 ZIP 压缩包导入导出。

功能特色:
1系统交互：底层穿透与动态多语言
2数据流转：跨设备的归档与导入
3目标控制：全局与局部的自由切换
4自动化任务：无人值守的备份与清理
5底层架构：时间点快照（强一致性保证）

<img width="822" height="852" alt="image" src="https://github.com/user-attachments/assets/1aa67725-3c4b-417d-9652-c9c4364517e2" />
<img width="822" height="852" alt="image" src="https://github.com/user-attachments/assets/f83d9495-1531-47ea-acfe-72b7fe2a8242" />
<img width="822" height="852" alt="image" src="https://github.com/user-attachments/assets/47db4859-67a5-4355-8713-449defcadb5d" />
