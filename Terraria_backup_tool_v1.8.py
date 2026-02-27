import os
import shutil
import time
import threading
import winreg
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime


class TerrariaBackupTool:
    """
    泰拉瑞亚存档备份工具 V1.8 - 持久化生命周期版
    """

    I18N = {
        "zh": {
            "title": "泰拉瑞亚存档备份工具 V1.8",
            "tab_main": "主控面板",
            "path_frame": "目录配置 (支持自动识别与手动指定)",
            "game_dir_label": "游戏存档:",
            "browse": "浏览",
            "backup_dir_label": "备份位置:",
            "open_backup": "📂 打开备份目录",
            "target_frame": "备份任务配置",
            "global_backup": "全局备份 (包含所有人物与世界)",
            "tmod_mode": "开启 tModLoader 模式 (模组存档)",
            "spec_world": "特定世界:",
            "spec_player": "特定人物:",
            "freq_label": "备份频率: 每",
            "unit_sec": "秒",
            "unit_min": "分钟",
            "unit_hour": "小时",
            "unit_day": "天",
            "start_auto": "▶ 启动自动备份",
            "stop_auto": "⏹ 停止自动备份",
            "manual_btn": "⚡ 立即执行一次",
            "gc_frame": "垃圾回收策略 (自动删除最旧快照)",
            "enable_gc": "启用自动清理",
            "keep_count_radio": "按数量保留: 仅保留最近的",
            "keep_count_label": "个快照",
            "keep_time_radio": "按时间保留: 删除距今超过",
            "keep_time_label": "的快照",
            "lib_frame": "历史快照库 (Snapshot Library)",
            "restore_btn": "⏪ 一键回档选中快照",
            "undo_btn": "↩ 撤回上一次回档",
            "refresh_btn": "刷新列表",
            "export_zip": "📦 导出选中快照为 Zip",
            "import_zip": "📥 导入外来 Zip 备份",
            "stats_format": "当前共有 {} 个快照",
            "status_ready": "就绪",
            "status_manual_ok": "手动快照创建成功 ({})",
            "status_auto_ok": "自动快照完成 ({})",
            "msg_select_restore": "请先选择一个要回档的快照",
            "msg_confirm_restore": "确定要将存档恢复到快照：\n{}\n的状态吗？当前游戏存档将被覆盖！\n(系统会自动保存当前状态，可随时撤销)",
            "msg_restore_ok": "回档成功！游戏状态已回到快照：{}",
            "msg_restore_fail": "回档失败: {}\n请确保游戏已完全退出！",
            "msg_undo_none": "没有找到可撤销的回档记录。",
            "msg_confirm_undo": "确定要撤回上一次回档操作吗？这会将游戏存档恢复到上次回档前的状态。",
            "msg_undo_ok": "撤回成功！已安全恢复到回档前的游戏状态。",
            "msg_undo_fail": "撤回失败: {}",
            "msg_select_zip": "请先选择一个要打包的快照",
            "msg_zip_ok": "压缩包导出成功！",
            "msg_import_ok": "导入成功！已分配快照名：{}",
            "msg_import_fail": "导入失败，文件可能损坏或格式不正确：{}"
        },
        # (此处为了版面精简，英文和日文字典内容与V1.7完全一致，如需完整可直接粘贴回原本的英文和日文字典)
        "en": {
            "title": "Terraria Backup Tool V1.8", "tab_main": "Main Panel", "path_frame": "Directory Config",
            "game_dir_label": "Game Save:", "browse": "Browse", "backup_dir_label": "Backup Loc:",
            "open_backup": "📂 Open Folder", "target_frame": "Backup Task Config", "global_backup": "Global Backup",
            "tmod_mode": "Enable tModLoader Mode", "spec_world": "Specific World:", "spec_player": "Specific Player:",
            "freq_label": "Frequency: Every", "unit_sec": "Sec", "unit_min": "Min", "unit_hour": "Hour",
            "unit_day": "Day", "start_auto": "▶ Start Auto Backup", "stop_auto": "⏹ Stop Auto Backup",
            "manual_btn": "⚡ Run Manual", "gc_frame": "Garbage Collection", "enable_gc": "Enable Auto Cleanup",
            "keep_count_radio": "By Count: Keep latest", "keep_count_label": "snapshots",
            "keep_time_radio": "By Time: Delete older than", "keep_time_label": "snapshots",
            "lib_frame": "Snapshot Library", "restore_btn": "⏪ Restore Selected", "undo_btn": "↩ Undo Last Restore",
            "refresh_btn": "Refresh List", "export_zip": "📦 Export to Zip", "import_zip": "📥 Import Zip",
            "stats_format": "Total {} snapshots", "status_ready": "Ready",
            "status_manual_ok": "Manual snapshot created ({})", "status_auto_ok": "Auto snapshot finished ({})",
            "msg_select_restore": "Please select a snapshot to restore",
            "msg_confirm_restore": "Restore to:\n{}?\nCurrent game saves will be OVERWRITTEN!",
            "msg_restore_ok": "Restore successful! Reverted to: {}",
            "msg_restore_fail": "Restore failed: {}\nMake sure the game is fully closed!",
            "msg_undo_none": "No undo record found.", "msg_confirm_undo": "Undo the last restore?",
            "msg_undo_ok": "Undo successful!", "msg_undo_fail": "Undo failed: {}",
            "msg_select_zip": "Please select a snapshot to export", "msg_zip_ok": "Zip export successful!",
            "msg_import_ok": "Import successful! Assigned snapshot: {}", "msg_import_fail": "Import failed: {}"
        },
        "ja": {
            "title": "テラリアバックアップ V1.8", "tab_main": "メインパネル", "path_frame": "ディレクトリ設定",
            "game_dir_label": "セーブ元:", "browse": "参照", "backup_dir_label": "保存先:",
            "open_backup": "📂 フォルダを開く", "target_frame": "バックアップ設定",
            "global_backup": "グローバルバックアップ", "tmod_mode": "tModLoaderモード", "spec_world": "特定のワールド:",
            "spec_player": "特定のキャラ:", "freq_label": "頻度: 毎", "unit_sec": "秒", "unit_min": "分",
            "unit_hour": "時間", "unit_day": "日", "start_auto": "▶ 自動バックアップ開始", "stop_auto": "⏹ 自動停止",
            "manual_btn": "⚡ 今すぐ実行", "gc_frame": "ガベージコレクション", "enable_gc": "自動クリーンアップ",
            "keep_count_radio": "数量で保持: 最新の", "keep_count_label": "個を保持",
            "keep_time_radio": "時間で保持: 経過", "keep_time_label": "のデータを削除",
            "lib_frame": "スナップショットライブラリ", "restore_btn": "⏪ 選択項目を復元",
            "undo_btn": "↩ 直前の復元を取り消す", "refresh_btn": "更新", "export_zip": "📦 Zipで書き出し",
            "import_zip": "📥 Zipを読み込み", "stats_format": "現在 {} 個のスナップショット", "status_ready": "待機中",
            "status_manual_ok": "手動作成成功 ({})", "status_auto_ok": "自動バックアップ完了 ({})",
            "msg_select_restore": "復元するスナップショットを選択してください",
            "msg_confirm_restore": "次のスナップショットに復元しますか？\n{}\n現在のセーブデータは上書きされます！",
            "msg_restore_ok": "復元成功！対象: {}", "msg_restore_fail": "復元失敗: {}",
            "msg_undo_none": "取り消し可能な記録が見つかりません。", "msg_confirm_undo": "直前の復元を取り消しますか？",
            "msg_undo_ok": "取り消し成功！", "msg_undo_fail": "取り消し失敗: {}",
            "msg_select_zip": "書き出すスナップショットを選択してください",
            "msg_zip_ok": "Zipの書き出しに成功しました！", "msg_import_ok": "読み込み成功！割り当て名: {}",
            "msg_import_fail": "読み込み失敗: {}"
        }
    }

    def __init__(self, root):
        self.root = root
        # 拦截原生的窗口关闭按钮事件 (右上角的红叉)，转交给我们自定义的函数处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_closing)

        icon_path = self.resource_path("terraria.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # 确定配置文件真正的安全物理路径（与打包后的 EXE 文件同级）
        self.config_file = os.path.join(self.get_real_executable_dir(), "terraria_backup_config.json")

        # === 核心变量定义 (此时先赋予默认值) ===
        self.current_lang = "zh"
        self.game_save_dir = tk.StringVar()
        self.backup_dir = tk.StringVar(value=os.path.join(os.getcwd(), "Backups"))
        self.is_backing_up = False
        self.wakeup_event = threading.Event()

        self.global_backup_var = tk.BooleanVar(value=True)
        self.tmod_mode_var = tk.BooleanVar(value=False)
        self.selected_world_var = tk.StringVar()
        self.selected_player_var = tk.StringVar()
        self.available_worlds = []
        self.available_players = []

        self.auto_delete_enabled = tk.BooleanVar(value=False)
        self.delete_mode = tk.StringVar(value="count")
        self.keep_count = tk.StringVar(value="10")
        self.keep_time = tk.StringVar(value="60")
        self.unit_val = tk.StringVar()
        self.keep_time_unit = tk.StringVar()
        self.interval_val = tk.StringVar(value="5")

        self.base_terraria_dir = ""

        # === 系统初始化生命周期 ===
        # 1. 自动寻找默认原版路径打底
        self.auto_detect_registry_path()
        # 2. 从 JSON 配置文件中读取并覆盖用户的历史设定
        self.load_config()
        # 3. 基于内存中现有的变量构建 UI 骨架
        self.setup_ui()
        # 4. 根据当前设定的语言热重载文字 (会顺带设置好下拉框里的单位)
        self.apply_language(self.current_lang)
        # 5. 扫描硬盘实际情况 (这一步会自动校验并剔除配置文件里已经不存在的人物/世界)
        self.scan_saves()
        # 6. 刷新历史列表
        self.refresh_backup_list()

    def get_real_executable_dir(self):
        """核心原理：破解 PyInstaller 的临时目录陷阱，定位真正双击的 .exe 所在目录"""
        if getattr(sys, 'frozen', False):
            # 如果是打包好的 exe 运行
            return os.path.dirname(sys.executable)
        else:
            # 如果是 py 脚本直接运行
            return os.path.dirname(os.path.abspath(__file__))

    def load_config(self):
        """V1.8 新增：安全反序列化配置文件"""
        if not os.path.exists(self.config_file):
            return  # 没有配置文件则保持默认设定

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 提取并注入设定 (使用字典的 .get() 保证如果新增了字段也不会报错)
            self.current_lang = config.get("lang", "zh")

            # 如果配置文件里存了自定义路径，就覆盖掉刚才自动识别的路径
            if config.get("game_save_dir"):
                self.game_save_dir.set(config.get("game_save_dir"))
            if config.get("backup_dir"):
                self.backup_dir.set(config.get("backup_dir"))

            self.global_backup_var.set(config.get("global_backup", True))
            self.tmod_mode_var.set(config.get("tmod_mode", False))

            # 这里的特定选择只是“预期值”，实际是否生效要等 scan_saves 校验
            self.selected_world_var.set(config.get("selected_world", ""))
            self.selected_player_var.set(config.get("selected_player", ""))

            self.interval_val.set(config.get("interval_val", "5"))
            # 单位字符串因为受多语言影响，所以先直接赋值，稍后由 apply_language 进行二次对齐
            self.unit_val.set(config.get("unit_val", "分钟"))

            self.auto_delete_enabled.set(config.get("auto_delete", False))
            self.delete_mode.set(config.get("delete_mode", "count"))
            self.keep_count.set(config.get("keep_count", "10"))
            self.keep_time.set(config.get("keep_time", "60"))
            self.keep_time_unit.set(config.get("keep_time_unit", "分钟"))

        except Exception as e:
            print(f"配置文件读取失败或损坏，将使用默认设置: {e}")

    def save_config(self):
        """V1.8 新增：将当前程序的一切设定序列化并写入磁盘"""
        config = {
            "lang": self.current_lang,
            "game_save_dir": self.game_save_dir.get(),
            "backup_dir": self.backup_dir.get(),
            "global_backup": self.global_backup_var.get(),
            "tmod_mode": self.tmod_mode_var.get(),
            "selected_world": self.selected_world_var.get(),
            "selected_player": self.selected_player_var.get(),
            "interval_val": self.interval_val.get(),
            "unit_val": self.unit_val.get(),
            "auto_delete": self.auto_delete_enabled.get(),
            "delete_mode": self.delete_mode.get(),
            "keep_count": self.keep_count.get(),
            "keep_time": self.keep_time.get(),
            "keep_time_unit": self.keep_time_unit.get()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"配置文件保存失败: {e}")

    def on_window_closing(self):
        """V1.8 新增：拦截窗口关闭事件，完美接管生命周期"""
        # 1. 停止一切可能还在进行的后台备份循环
        self.is_backing_up = False
        self.wakeup_event.set()

        # 2. 执行核心状态落地写入
        self.save_config()

        # 3. 优雅销毁 UI 进程
        self.root.destroy()

    def _T(self, key):
        return self.I18N[self.current_lang].get(key, key)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def auto_detect_registry_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            val, _ = winreg.QueryValueEx(key, "Personal")
            docs_path = os.path.expandvars(val)
            terraria_path = os.path.join(docs_path, "My Games", "Terraria")
            if os.path.exists(terraria_path):
                self.base_terraria_dir = terraria_path
                self.game_save_dir.set(terraria_path)
        except Exception as e:
            print(f"读取注册表失败: {e}")

    def setup_ui(self):
        self.root.geometry("860x820")
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill="x", side="top", padx=10, pady=5)

        self.lang_btn = ttk.Menubutton(top_bar, text="🌐 语言Language", style="Toolbutton")
        self.lang_btn.pack(side="right")
        self.lang_menu = tk.Menu(self.lang_btn, tearoff=0)
        self.lang_menu.add_command(label="中文 (简体)", command=lambda: self.apply_language("zh"))
        self.lang_menu.add_command(label="English", command=lambda: self.apply_language("en"))
        self.lang_menu.add_command(label="日本語", command=lambda: self.apply_language("ja"))
        self.lang_btn["menu"] = self.lang_menu

        self.main_container = ttk.Notebook(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.tab_main = ttk.Frame(self.main_container)
        self.main_container.add(self.tab_main, text="")

        # 路径配置区
        self.path_frame = ttk.LabelFrame(self.tab_main, text="")
        self.path_frame.pack(fill="x", padx=10, pady=5)
        self.lbl_game_dir = ttk.Label(self.path_frame, text="")
        self.lbl_game_dir.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self.path_frame, textvariable=self.game_save_dir, width=60).grid(row=0, column=1)
        self.btn_browse_game = ttk.Button(self.path_frame, command=self.select_game_dir)
        self.btn_browse_game.grid(row=0, column=2, padx=5)

        self.lbl_backup_dir = ttk.Label(self.path_frame, text="")
        self.lbl_backup_dir.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self.path_frame, textvariable=self.backup_dir, width=60).grid(row=1, column=1)
        self.btn_browse_backup = ttk.Button(self.path_frame, command=self.select_backup_dir)
        self.btn_browse_backup.grid(row=1, column=2, padx=5)
        self.btn_open_backup = ttk.Button(self.path_frame, command=self.open_backup_folder)
        self.btn_open_backup.grid(row=1, column=3, padx=5)

        # 任务配置区
        self.target_frame = ttk.LabelFrame(self.tab_main, text="")
        self.target_frame.pack(fill="x", padx=10, pady=5)

        self.chk_global = ttk.Checkbutton(self.target_frame, variable=self.global_backup_var,
                                          command=self.toggle_global_backup)
        self.chk_global.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.chk_tmod = ttk.Checkbutton(self.target_frame, variable=self.tmod_mode_var, command=self.scan_saves)
        self.chk_tmod.grid(row=0, column=2, columnspan=2, sticky="w", padx=5, pady=5)

        self.lbl_spec_world = ttk.Label(self.target_frame, text="")
        self.lbl_spec_world.grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.world_combo = ttk.Combobox(self.target_frame, textvariable=self.selected_world_var, state="readonly",
                                        width=30)
        self.world_combo.grid(row=1, column=1, sticky="w")

        self.lbl_spec_player = ttk.Label(self.target_frame, text="")
        self.lbl_spec_player.grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.player_combo = ttk.Combobox(self.target_frame, textvariable=self.selected_player_var, state="readonly",
                                         width=30)
        self.player_combo.grid(row=2, column=1, sticky="w")
        self.toggle_global_backup()  # 初始化全局备份开关引起的状态禁用

        timer_frame = ttk.Frame(self.target_frame)
        timer_frame.grid(row=3, column=0, columnspan=4, sticky="w", padx=5, pady=10)
        self.lbl_freq = ttk.Label(timer_frame, text="")
        self.lbl_freq.pack(side="left")
        ttk.Combobox(timer_frame, textvariable=self.interval_val, values=["0.5", "1", "2", "3", "5", "10", "30", "60"],
                     width=5).pack(side="left", padx=5)

        self.unit_combo = ttk.Combobox(timer_frame, textvariable=self.unit_val, width=5, state="readonly")
        self.unit_combo.pack(side="left")

        self.btn_toggle = ttk.Button(timer_frame, command=self.toggle_backup)
        self.btn_toggle.pack(side="left", padx=15)
        self.btn_manual = ttk.Button(timer_frame, command=self.manual_backup)
        self.btn_manual.pack(side="left", padx=5)

        # 垃圾回收策略区 (GC)
        self.gc_frame = ttk.LabelFrame(self.tab_main, text="")
        self.gc_frame.pack(fill="x", padx=10, pady=5)
        self.chk_gc = ttk.Checkbutton(self.gc_frame, variable=self.auto_delete_enabled)
        self.chk_gc.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.radio_count = ttk.Radiobutton(self.gc_frame, variable=self.delete_mode, value="count")
        self.radio_count.grid(row=1, column=0, padx=20, sticky="w")
        ttk.Entry(self.gc_frame, textvariable=self.keep_count, width=5).grid(row=1, column=1, sticky="w")
        self.lbl_keep_count = ttk.Label(self.gc_frame, text="")
        self.lbl_keep_count.grid(row=1, column=2, sticky="w")

        self.radio_time = ttk.Radiobutton(self.gc_frame, variable=self.delete_mode, value="time")
        self.radio_time.grid(row=2, column=0, padx=20, sticky="w", pady=5)
        ttk.Entry(self.gc_frame, textvariable=self.keep_time, width=5).grid(row=2, column=1, sticky="w")

        self.keep_time_combo = ttk.Combobox(self.gc_frame, textvariable=self.keep_time_unit, width=5, state="readonly")
        self.keep_time_combo.grid(row=2, column=2, sticky="w", padx=5)
        self.lbl_keep_time = ttk.Label(self.gc_frame, text="")
        self.lbl_keep_time.grid(row=2, column=3, sticky="w")

        # 历史快照库
        self.lib_frame = ttk.LabelFrame(self.tab_main, text="")
        self.lib_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.backup_listbox = tk.Listbox(self.lib_frame, height=8, font=("Consolas", 10))
        self.backup_listbox.pack(fill="both", expand=True, side="left", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.lib_frame, command=self.backup_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.backup_listbox.config(yscrollcommand=scrollbar.set)

        tool_frame = ttk.Frame(self.tab_main)
        tool_frame.pack(fill="x", padx=10, pady=5)
        self.btn_restore = ttk.Button(tool_frame, command=self.restore_backup)
        self.btn_restore.pack(side="left", padx=5)
        self.btn_undo = ttk.Button(tool_frame, command=self.undo_restore)
        self.btn_undo.pack(side="left", padx=5)

        self.btn_refresh = ttk.Button(tool_frame, command=self.refresh_backup_list)
        self.btn_refresh.pack(side="left", padx=5)
        self.btn_export = ttk.Button(tool_frame, command=self.export_zip)
        self.btn_export.pack(side="right", padx=5)
        self.btn_import = ttk.Button(tool_frame, command=self.import_zip)
        self.btn_import.pack(side="right", padx=5)

        # 状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        self.stats_label = ttk.Label(status_frame, text="", font=("Arial", 9, "bold"), foreground="#0055A4")
        self.stats_label.pack(side="left")
        self.status_label = ttk.Label(status_frame, text="", font=("Arial", 9), foreground="green")
        self.status_label.pack(side="right")

    def apply_language(self, lang):
        self.current_lang = lang
        self.root.title(self._T("title"))
        self.main_container.tab(0, text=self._T("tab_main"))
        self.path_frame.config(text=self._T("path_frame"))
        self.lbl_game_dir.config(text=self._T("game_dir_label"))
        self.btn_browse_game.config(text=self._T("browse"))
        self.lbl_backup_dir.config(text=self._T("backup_dir_label"))
        self.btn_browse_backup.config(text=self._T("browse"))
        self.btn_open_backup.config(text=self._T("open_backup"))

        self.target_frame.config(text=self._T("target_frame"))
        self.chk_global.config(text=self._T("global_backup"))
        self.chk_tmod.config(text=self._T("tmod_mode"))
        self.lbl_spec_world.config(text=self._T("spec_world"))
        self.lbl_spec_player.config(text=self._T("spec_player"))
        self.lbl_freq.config(text=self._T("freq_label"))

        units = [self._T("unit_sec"), self._T("unit_min"), self._T("unit_hour"), self._T("unit_day")]

        # 智能匹配单位 (防止语言切换导致的非法值越界)
        target_val = self.unit_val.get()
        if target_val not in units and target_val in self.unit_combo['values']:
            idx = self.unit_combo['values'].index(target_val)
            self.unit_val.set(units[idx])
        elif target_val not in units:
            self.unit_val.set(units[1])  # 默认分钟
        self.unit_combo['values'] = units[:2]

        gc_target_val = self.keep_time_unit.get()
        if gc_target_val not in units and gc_target_val in self.keep_time_combo['values']:
            idx = self.keep_time_combo['values'].index(gc_target_val)
            self.keep_time_unit.set(units[idx])
        elif gc_target_val not in units:
            self.keep_time_unit.set(units[1])  # 默认分钟
        self.keep_time_combo['values'] = units

        self.btn_toggle.config(text=self._T("stop_auto") if self.is_backing_up else self._T("start_auto"))
        self.btn_manual.config(text=self._T("manual_btn"))

        self.gc_frame.config(text=self._T("gc_frame"))
        self.chk_gc.config(text=self._T("enable_gc"))
        self.radio_count.config(text=self._T("keep_count_radio"))
        self.lbl_keep_count.config(text=self._T("keep_count_label"))
        self.radio_time.config(text=self._T("keep_time_radio"))
        self.lbl_keep_time.config(text=self._T("keep_time_label"))

        self.lib_frame.config(text=self._T("lib_frame"))
        self.btn_restore.config(text=self._T("restore_btn"))
        self.btn_undo.config(text=self._T("undo_btn"))
        self.btn_refresh.config(text=self._T("refresh_btn"))
        self.btn_export.config(text=self._T("export_zip"))
        self.btn_import.config(text=self._T("import_zip"))
        self.status_label.config(text=self._T("status_ready"))
        self.refresh_backup_list()

    def get_unit_multiplier(self, val_str):
        if val_str == self._T("unit_sec"): return 1
        if val_str == self._T("unit_min"): return 60
        if val_str == self._T("unit_hour"): return 3600
        if val_str == self._T("unit_day"): return 86400
        return 60

    def scan_saves(self):
        """扫描硬盘物理存档，并验证配置文件中的历史设定是否依然合法"""
        game_dir = self.game_save_dir.get()
        if not game_dir or not os.path.exists(game_dir): return

        base_dir = os.path.join(game_dir, "tModLoader") if self.tmod_mode_var.get() else game_dir
        worlds_dir = os.path.join(base_dir, "Worlds")
        players_dir = os.path.join(base_dir, "Players")

        if os.path.exists(worlds_dir):
            self.available_worlds = list({f.rsplit('.', 1)[0] for f in os.listdir(worlds_dir) if f.endswith(".wld")})
        else:
            self.available_worlds = []

        if os.path.exists(players_dir):
            self.available_players = list({f.rsplit('.', 1)[0] for f in os.listdir(players_dir) if f.endswith(".plr")})
        else:
            self.available_players = []

        self.world_combo['values'] = self.available_worlds
        self.player_combo['values'] = self.available_players

        # 核心校验逻辑：如果用户配置文件里存的那个存档名称，现在硬盘上已经被删了，必须强制重置下拉框，防止崩溃
        current_wld = self.selected_world_var.get()
        if self.available_worlds and current_wld not in self.available_worlds:
            self.selected_world_var.set(self.available_worlds[0])

        current_plr = self.selected_player_var.get()
        if self.available_players and current_plr not in self.available_players:
            self.selected_player_var.set(self.available_players[0])

    def select_game_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.game_save_dir.set(path)
            self.scan_saves()

    def select_backup_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.backup_dir.set(path)
            self.refresh_backup_list()

    def open_backup_folder(self):
        path = self.backup_dir.get()
        if not os.path.exists(path): os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)
        except Exception:
            pass

    def toggle_global_backup(self):
        state = "disabled" if self.global_backup_var.get() else "readonly"
        self.world_combo.config(state=state)
        self.player_combo.config(state=state)

    def toggle_backup(self):
        if not self.is_backing_up:
            self.is_backing_up = True
            self.btn_toggle.config(text=self._T("stop_auto"))
            threading.Thread(target=self.backup_loop, daemon=True).start()
        else:
            self.is_backing_up = False
            self.btn_toggle.config(text=self._T("start_auto"))
            self.wakeup_event.set()

    def manual_backup(self):
        self.perform_backup()
        self.status_label.config(text=self._T("status_manual_ok").format(datetime.now().strftime('%H:%M:%S')))
        if self.is_backing_up: self.wakeup_event.set()

    def backup_loop(self):
        while self.is_backing_up:
            self.perform_backup()
            self.root.after(0, lambda: self.status_label.config(
                text=self._T("status_auto_ok").format(datetime.now().strftime('%H:%M:%S'))))
            try:
                val = float(self.interval_val.get())
                wait_seconds = val * self.get_unit_multiplier(self.unit_val.get())
            except ValueError:
                wait_seconds = 300
            self.wakeup_event.wait(wait_seconds)
            self.wakeup_event.clear()

    def get_next_snapshot_id(self):
        backup_dir = self.backup_dir.get()
        if not os.path.exists(backup_dir): return 1
        max_id = 0
        for item in os.listdir(backup_dir):
            if os.path.isdir(os.path.join(backup_dir, item)):
                parts = item.split("_")
                if parts[0].isdigit(): max_id = max(max_id, int(parts[0]))
        return max_id + 1

    def _copy_specific_entity(self, src_dir, dest_dir, entity_base_name):
        if not os.path.exists(src_dir): return
        os.makedirs(dest_dir, exist_ok=True)
        for item in os.listdir(src_dir):
            item_path = os.path.join(src_dir, item)
            if os.path.isfile(item_path) and item.startswith(entity_base_name + "."):
                shutil.copy2(item_path, dest_dir)
            elif os.path.isdir(item_path) and item == entity_base_name:
                shutil.copytree(item_path, os.path.join(dest_dir, item), dirs_exist_ok=True)

    def perform_backup(self):
        game_dir = self.game_save_dir.get()
        backup_dir = self.backup_dir.get()
        if not os.path.exists(game_dir): return
        os.makedirs(backup_dir, exist_ok=True)

        is_tmod = self.tmod_mode_var.get()
        mode_str = "tML" if is_tmod else "Vanilla"
        src_base = os.path.join(game_dir, "tModLoader") if is_tmod else game_dir

        next_id = self.get_next_snapshot_id()
        timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
        snapshot_name = f"{next_id:03d}_{mode_str}_{timestamp}"
        snap_dir = os.path.join(backup_dir, snapshot_name)

        is_global = self.global_backup_var.get()
        if is_global:
            for target in ["Worlds", "Players"]:
                src = os.path.join(src_base, target)
                dst = os.path.join(snap_dir, target)
                if os.path.exists(src): shutil.copytree(src, dst, ignore=shutil.ignore_patterns('Backups'))
        else:
            wld = self.selected_world_var.get()
            if wld: self._copy_specific_entity(os.path.join(src_base, "Worlds"), os.path.join(snap_dir, "Worlds"), wld)
            plr = self.selected_player_var.get()
            if plr: self._copy_specific_entity(os.path.join(src_base, "Players"), os.path.join(snap_dir, "Players"),
                                               plr)

        self.cleanup_old_backups()
        self.root.after(0, self.refresh_backup_list)

    def cleanup_old_backups(self):
        if not self.auto_delete_enabled.get(): return
        backup_dir = self.backup_dir.get()
        if not os.path.exists(backup_dir): return
        snapshots = [(os.path.join(backup_dir, d), os.path.getmtime(os.path.join(backup_dir, d))) for d in
                     os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d)) and d[0].isdigit()]
        snapshots.sort(key=lambda x: x[1], reverse=True)
        mode = self.delete_mode.get()
        if mode == "count":
            try:
                limit = int(self.keep_count.get())
                for path, _ in snapshots[limit:]: shutil.rmtree(path)
            except ValueError:
                pass
        elif mode == "time":
            try:
                time_val = float(self.keep_time.get())
                multiplier = self.get_unit_multiplier(self.keep_time_unit.get())
                threshold_time = time.time() - (time_val * multiplier)
                for path, mtime in snapshots:
                    if mtime < threshold_time: shutil.rmtree(path)
            except Exception:
                pass

    def refresh_backup_list(self):
        self.backup_listbox.delete(0, tk.END)
        backup_dir = self.backup_dir.get()
        if not os.path.exists(backup_dir): return
        snapshots = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d)) and d[0].isdigit()]
        snapshots.sort(reverse=True)
        for snap in snapshots: self.backup_listbox.insert(tk.END, snap)
        self.stats_label.config(text=self._T("stats_format").format(len(snapshots)))

    def restore_backup(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showinfo("INFO", self._T("msg_select_restore"))
            return
        snapshot_name = self.backup_listbox.get(selection[0])
        snap_dir = os.path.join(self.backup_dir.get(), snapshot_name)
        game_dir = self.game_save_dir.get()

        if not messagebox.askyesno("Confirm", self._T("msg_confirm_restore").format(snapshot_name)): return

        is_tml_snapshot = "_tML_" in snapshot_name
        target_live_base = os.path.join(game_dir, "tModLoader") if is_tml_snapshot else game_dir

        try:
            prerestore_dir = os.path.join(self.backup_dir.get(), "PreRestore_Backup")
            if os.path.exists(prerestore_dir): shutil.rmtree(prerestore_dir)
            os.makedirs(prerestore_dir)
            with open(os.path.join(prerestore_dir, "restore_mode.txt"), "w") as f:
                f.write("tML" if is_tml_snapshot else "Vanilla")

            for target in ["Worlds", "Players"]:
                live_path = os.path.join(target_live_base, target)
                if os.path.exists(live_path): shutil.copytree(live_path, os.path.join(prerestore_dir, target))

            for target in ["Worlds", "Players"]:
                src = os.path.join(snap_dir, target)
                dst = os.path.join(target_live_base, target)
                if os.path.exists(src):
                    for root, dirs, files in os.walk(src):
                        rel_path = os.path.relpath(root, src)
                        dst_path = os.path.join(dst, rel_path) if rel_path != "." else dst
                        os.makedirs(dst_path, exist_ok=True)
                        for file in files: shutil.copy2(os.path.join(root, file), os.path.join(dst_path, file))

            messagebox.showinfo("OK", self._T("msg_restore_ok").format(snapshot_name))
            self.scan_saves()
        except Exception as e:
            messagebox.showerror("Error", self._T("msg_restore_fail").format(e))

    def undo_restore(self):
        prerestore_dir = os.path.join(self.backup_dir.get(), "PreRestore_Backup")
        if not os.path.exists(prerestore_dir):
            messagebox.showinfo("INFO", self._T("msg_undo_none"))
            return
        if not messagebox.askyesno("Confirm", self._T("msg_confirm_undo")): return

        try:
            mode_file = os.path.join(prerestore_dir, "restore_mode.txt")
            mode_str = "Vanilla"
            if os.path.exists(mode_file):
                with open(mode_file, "r") as f: mode_str = f.read().strip()
            game_dir = self.game_save_dir.get()
            target_live_base = os.path.join(game_dir, "tModLoader") if mode_str == "tML" else game_dir

            for target in ["Worlds", "Players"]:
                src = os.path.join(prerestore_dir, target)
                dst = os.path.join(target_live_base, target)
                if os.path.exists(src):
                    for root, dirs, files in os.walk(src):
                        rel_path = os.path.relpath(root, src)
                        dst_path = os.path.join(dst, rel_path) if rel_path != "." else dst
                        os.makedirs(dst_path, exist_ok=True)
                        for file in files: shutil.copy2(os.path.join(root, file), os.path.join(dst_path, file))
            messagebox.showinfo("OK", self._T("msg_undo_ok"))
            self.scan_saves()
        except Exception as e:
            messagebox.showerror("Error", self._T("msg_undo_fail").format(e))

    def export_zip(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showinfo("INFO", self._T("msg_select_zip"))
            return
        snapshot_name = self.backup_listbox.get(selection[0])
        snap_dir = os.path.join(self.backup_dir.get(), snapshot_name)
        save_path = filedialog.asksaveasfilename(defaultextension=".zip",
                                                 initialfile=f"Terraria_Backup_{snapshot_name}.zip")
        if save_path:
            try:
                base_name = save_path[:-4] if save_path.endswith('.zip') else save_path
                shutil.make_archive(base_name, 'zip', snap_dir)
                messagebox.showinfo("OK", self._T("msg_zip_ok"))
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def import_zip(self):
        zip_path = filedialog.askopenfilename(filetypes=[("Zip", "*.zip")])
        if not zip_path: return
        try:
            next_id = self.get_next_snapshot_id()
            timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
            new_snap_name = f"{next_id:03d}_Imported_{timestamp}"
            new_snap_dir = os.path.join(self.backup_dir.get(), new_snap_name)
            os.makedirs(new_snap_dir)
            shutil.unpack_archive(zip_path, new_snap_dir, 'zip')
            self.refresh_backup_list()
            messagebox.showinfo("OK", self._T("msg_import_ok").format(new_snap_name))
        except Exception as e:
            messagebox.showerror("Error", self._T("msg_import_fail").format(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TerrariaBackupTool(root)
    root.mainloop()