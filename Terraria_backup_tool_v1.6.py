import os
import shutil
import time
import threading
import winreg
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime


class TerrariaBackupTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Terraria_backup_tool_v1.6 - 快照架构版")
        self.root.geometry("800x800")

        icon_path = self.resource_path("terraria.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # 核心变量
        self.game_save_dir = tk.StringVar()
        self.backup_dir = tk.StringVar(value=os.path.join(os.getcwd(), "Backups"))
        self.is_backing_up = False
        self.wakeup_event = threading.Event()

        # 备份策略变量 (V1.5 继承)
        self.global_backup_var = tk.BooleanVar(value=True)
        self.selected_world_var = tk.StringVar()
        self.selected_player_var = tk.StringVar()
        self.available_worlds = []
        self.available_players = []

        # 自动删除策略变量 (V1.6 新增)
        self.auto_delete_enabled = tk.BooleanVar(value=False)
        self.delete_mode = tk.StringVar(value="count")  # 'count' or 'time'
        self.keep_count = tk.StringVar(value="10")
        self.keep_time = tk.StringVar(value="60")
        self.keep_time_unit = tk.StringVar(value="分钟")

        self.base_terraria_dir = ""

        # 初始化流程
        self.auto_detect_registry_path()
        self.setup_ui()
        self.scan_saves()
        self.refresh_backup_list()

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

    def scan_saves(self):
        """扫描游戏存档目录下的世界和人物"""
        game_dir = self.game_save_dir.get()
        if not game_dir or not os.path.exists(game_dir): return

        worlds_dir = os.path.join(game_dir, "Worlds")
        players_dir = os.path.join(game_dir, "Players")

        self.available_worlds = [f for f in os.listdir(worlds_dir) if f.endswith(".wld")] if os.path.exists(
            worlds_dir) else []
        self.available_players = [f for f in os.listdir(players_dir) if f.endswith(".plr")] if os.path.exists(
            players_dir) else []

        self.world_combo['values'] = self.available_worlds
        self.player_combo['values'] = self.available_players

        if self.available_worlds: self.selected_world_var.set(self.available_worlds[0])
        if self.available_players: self.selected_player_var.set(self.available_players[0])

    def setup_ui(self):
        main_container = ttk.Notebook(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        tab_main = ttk.Frame(main_container)
        main_container.add(tab_main, text="主控面板")

        # --- 第一部分：路径设置 ---
        path_frame = ttk.LabelFrame(tab_main, text="目录配置 (支持自动识别与手动指定)")
        path_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(path_frame, text="游戏存档:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.game_save_dir, width=60).grid(row=0, column=1)
        ttk.Button(path_frame, text="浏览", command=self.select_game_dir).grid(row=0, column=2, padx=5)

        ttk.Label(path_frame, text="备份位置:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.backup_dir, width=60).grid(row=1, column=1)
        ttk.Button(path_frame, text="浏览", command=self.select_backup_dir).grid(row=1, column=2, padx=5)
        ttk.Button(path_frame, text="📂 打开备份目录", command=self.open_backup_folder).grid(row=1, column=3, padx=5)

        # --- 第二部分：备份目标与定时 ---
        target_frame = ttk.LabelFrame(tab_main, text="备份任务配置")
        target_frame.pack(fill="x", padx=10, pady=5)

        ttk.Checkbutton(target_frame, text="全局备份 (包含所有人物与世界)", variable=self.global_backup_var,
                        command=self.toggle_global_backup).grid(row=0, column=0, columnspan=2, sticky="w", padx=5,
                                                                pady=5)

        ttk.Label(target_frame, text="特定世界:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.world_combo = ttk.Combobox(target_frame, textvariable=self.selected_world_var, state="disabled", width=30)
        self.world_combo.grid(row=1, column=1, sticky="w")

        ttk.Label(target_frame, text="特定人物:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.player_combo = ttk.Combobox(target_frame, textvariable=self.selected_player_var, state="disabled",
                                         width=30)
        self.player_combo.grid(row=2, column=1, sticky="w")

        timer_frame = ttk.Frame(target_frame)
        timer_frame.grid(row=3, column=0, columnspan=4, sticky="w", padx=5, pady=10)
        ttk.Label(timer_frame, text="备份频率: 每").pack(side="left")
        self.interval_val = tk.StringVar(value="5")
        ttk.Combobox(timer_frame, textvariable=self.interval_val, values=["0.5", "1", "2", "3", "5", "10", "30", "60"],
                     width=5).pack(side="left", padx=5)
        self.unit_val = tk.StringVar(value="分钟")
        ttk.Combobox(timer_frame, textvariable=self.unit_val, values=["秒", "分钟"], width=5).pack(side="left")

        self.toggle_btn = ttk.Button(timer_frame, text="▶ 启动自动备份", command=self.toggle_backup)
        self.toggle_btn.pack(side="left", padx=15)
        self.manual_btn = ttk.Button(timer_frame, text="⚡ 立即执行一次备份", command=self.manual_backup)
        self.manual_btn.pack(side="left", padx=5)

        # --- 第三部分：自动删除规则 (垃圾回收) ---
        gc_frame = ttk.LabelFrame(tab_main, text="垃圾回收策略 (自动删除最旧备份)")
        gc_frame.pack(fill="x", padx=10, pady=5)

        ttk.Checkbutton(gc_frame, text="启用自动清理", variable=self.auto_delete_enabled).grid(row=0, column=0, padx=5,
                                                                                               pady=5, sticky="w")

        ttk.Radiobutton(gc_frame, text="按数量保留: 仅保留最近的", variable=self.delete_mode, value="count").grid(row=1,
                                                                                                                  column=0,
                                                                                                                  padx=20,
                                                                                                                  sticky="w")
        ttk.Entry(gc_frame, textvariable=self.keep_count, width=5).grid(row=1, column=1, sticky="w")
        ttk.Label(gc_frame, text="个快照").grid(row=1, column=2, sticky="w")

        ttk.Radiobutton(gc_frame, text="按时间保留: 自动删除距今超过", variable=self.delete_mode, value="time").grid(
            row=2, column=0, padx=20, sticky="w", pady=5)
        ttk.Entry(gc_frame, textvariable=self.keep_time, width=5).grid(row=2, column=1, sticky="w")
        ttk.Combobox(gc_frame, textvariable=self.keep_time_unit, values=["秒", "分钟", "小时", "天"], width=5).grid(
            row=2, column=2, sticky="w", padx=5)
        ttk.Label(gc_frame, text="的快照").grid(row=2, column=3, sticky="w")

        # --- 第四部分：历史快照与高级工具 ---
        list_frame = ttk.LabelFrame(tab_main, text="历史快照库 (Snapshot Library)")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.backup_listbox = tk.Listbox(list_frame, height=8, font=("Consolas", 10))
        self.backup_listbox.pack(fill="both", expand=True, side="left", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(list_frame, command=self.backup_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.backup_listbox.config(yscrollcommand=scrollbar.set)

        tool_frame = ttk.Frame(tab_main)
        tool_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(tool_frame, text="⏪ 一键回档选中快照", command=self.restore_backup).pack(side="left", padx=5)
        ttk.Button(tool_frame, text="刷新列表", command=self.refresh_backup_list).pack(side="left", padx=5)
        ttk.Button(tool_frame, text="📦 导出选中快照为 Zip", command=self.export_zip).pack(side="right", padx=5)
        ttk.Button(tool_frame, text="📥 导入外来 Zip 备份", command=self.import_zip).pack(side="right", padx=5)

        # 状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        self.stats_label = ttk.Label(status_frame, text="当前共有 0 个快照", font=("Arial", 9, "bold"),
                                     foreground="#0055A4")
        self.stats_label.pack(side="left")
        self.status_label = ttk.Label(status_frame, text="就绪", font=("Arial", 9), foreground="green")
        self.status_label.pack(side="right")

    # === 交互与路径逻辑 ===
    def select_game_dir(self):
        path = filedialog.askdirectory(title="选择泰拉瑞亚存档根目录")
        if path:
            self.game_save_dir.set(path)
            self.scan_saves()

    def select_backup_dir(self):
        path = filedialog.askdirectory(title="选择备份存放位置")
        if path:
            self.backup_dir.set(path)
            self.refresh_backup_list()

    def open_backup_folder(self):
        path = self.backup_dir.get()
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)  # 仅限 Windows 平台生效
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")

    def toggle_global_backup(self):
        state = "disabled" if self.global_backup_var.get() else "readonly"
        self.world_combo.config(state=state)
        self.player_combo.config(state=state)

    # === 核心备份与垃圾回收逻辑 ===
    def toggle_backup(self):
        if not self.is_backing_up:
            self.is_backing_up = True
            self.toggle_btn.config(text="⏹ 停止自动备份")
            threading.Thread(target=self.backup_loop, daemon=True).start()
        else:
            self.is_backing_up = False
            self.toggle_btn.config(text="▶ 启动自动备份")
            self.wakeup_event.set()

    def manual_backup(self):
        self.perform_backup()
        self.status_label.config(text=f"手动快照创建成功 ({datetime.now().strftime('%H:%M:%S')})")
        if self.is_backing_up:
            self.wakeup_event.set()

    def backup_loop(self):
        while self.is_backing_up:
            self.perform_backup()
            self.root.after(0, lambda: self.status_label.config(
                text=f"自动快照完成 ({datetime.now().strftime('%H:%M:%S')})"))

            try:
                val = float(self.interval_val.get())
                wait_seconds = val if self.unit_val.get() == "秒" else val * 60
            except ValueError:
                wait_seconds = 300

            self.wakeup_event.wait(wait_seconds)
            self.wakeup_event.clear()

    def get_next_snapshot_id(self):
        """解析备份目录下所有的文件夹，寻找最大的前缀序号"""
        backup_dir = self.backup_dir.get()
        if not os.path.exists(backup_dir): return 1

        max_id = 0
        for item in os.listdir(backup_dir):
            if os.path.isdir(os.path.join(backup_dir, item)):
                parts = item.split("_")
                if parts[0].isdigit():
                    max_id = max(max_id, int(parts[0]))
        return max_id + 1

    def perform_backup(self):
        game_dir = self.game_save_dir.get()
        backup_dir = self.backup_dir.get()
        if not os.path.exists(game_dir): return
        os.makedirs(backup_dir, exist_ok=True)

        # 1. 生成标准的快照文件夹名称：序号_年_月_日_时-分-秒
        next_id = self.get_next_snapshot_id()
        timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
        snapshot_name = f"{next_id:03d}_{timestamp}"
        snapshot_dir = os.path.join(backup_dir, snapshot_name)

        # 在快照文件夹内创建标准游戏结构
        snap_worlds = os.path.join(snapshot_dir, "Worlds")
        snap_players = os.path.join(snapshot_dir, "Players")
        os.makedirs(snap_worlds, exist_ok=True)
        os.makedirs(snap_players, exist_ok=True)

        is_global = self.global_backup_var.get()

        # 2. 复制世界存档
        worlds_to_backup = self.available_worlds if is_global else [self.selected_world_var.get()]
        for wld in worlds_to_backup:
            if not wld: continue
            src = os.path.join(game_dir, "Worlds", wld)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(snap_worlds, wld))

        # 3. 复制人物存档及地图依赖
        players_to_backup = self.available_players if is_global else [self.selected_player_var.get()]
        for plr in players_to_backup:
            if not plr: continue
            src_plr = os.path.join(game_dir, "Players", plr)
            if os.path.exists(src_plr):
                shutil.copy2(src_plr, os.path.join(snap_players, plr))
                # 附带复制同名小地图文件夹
                player_name = plr.replace(".plr", "")
                src_map = os.path.join(game_dir, "Players", player_name)
                if os.path.isdir(src_map):
                    shutil.copytree(src_map, os.path.join(snap_players, player_name))

        # 4. 执行垃圾回收机制
        self.cleanup_old_backups()
        self.root.after(0, self.refresh_backup_list)

    def cleanup_old_backups(self):
        """V1.6 新增：自动化垃圾回收"""
        if not self.auto_delete_enabled.get(): return

        backup_dir = self.backup_dir.get()
        if not os.path.exists(backup_dir): return

        # 获取所有快照文件夹并按修改时间倒序排列 (最新的在前面)
        snapshots = []
        for d in os.listdir(backup_dir):
            path = os.path.join(backup_dir, d)
            if os.path.isdir(path) and d[0].isdigit():  # 过滤掉非快照文件夹
                snapshots.append((path, os.path.getmtime(path)))
        snapshots.sort(key=lambda x: x[1], reverse=True)

        mode = self.delete_mode.get()
        if mode == "count":
            try:
                limit = int(self.keep_count.get())
                # 删掉超过 limit 的所有旧快照
                for path, _ in snapshots[limit:]:
                    shutil.rmtree(path)
            except ValueError:
                pass

        elif mode == "time":
            try:
                time_val = float(self.keep_time.get())
                unit = self.keep_time_unit.get()
                multiplier = {"秒": 1, "分钟": 60, "小时": 3600, "天": 86400}[unit]
                threshold_time = time.time() - (time_val * multiplier)

                for path, mtime in snapshots:
                    if mtime < threshold_time:
                        shutil.rmtree(path)
            except Exception:
                pass

    # === 快照还原与 Zip 管理 ===
    def refresh_backup_list(self):
        self.backup_listbox.delete(0, tk.END)
        backup_dir = self.backup_dir.get()
        if not os.path.exists(backup_dir): return

        # 仅显示具备序号特征的快照文件夹
        snapshots = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d)) and d[0].isdigit()]
        # 按名称降序排列（因为名字包含了序号）
        snapshots.sort(reverse=True)

        for snap in snapshots:
            self.backup_listbox.insert(tk.END, snap)

        self.stats_label.config(text=f"当前共有 {len(snapshots)} 个快照")

    def restore_backup(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个要回档的快照")
            return

        snapshot_name = self.backup_listbox.get(selection[0])
        snap_dir = os.path.join(self.backup_dir.get(), snapshot_name)
        game_dir = self.game_save_dir.get()

        if not messagebox.askyesno("确认回档",
                                   f"确定要将存档恢复到快照：{snapshot_name} 的状态吗？\n当前游戏存档将被覆盖！"):
            return

        try:
            # 完整将快照内的 Worlds 和 Players 覆盖到游戏目录
            for target in ["Worlds", "Players"]:
                src = os.path.join(snap_dir, target)
                dst = os.path.join(game_dir, target)
                if os.path.exists(src):
                    # Python 原生 copytree 在目标存在时会报错(3.8前)或需要特别处理。
                    # 为了稳定覆盖，手动遍历复制
                    for root, dirs, files in os.walk(src):
                        rel_path = os.path.relpath(root, src)
                        dst_path = os.path.join(dst, rel_path) if rel_path != "." else dst
                        os.makedirs(dst_path, exist_ok=True)
                        for file in files:
                            shutil.copy2(os.path.join(root, file), os.path.join(dst_path, file))

            messagebox.showinfo("成功", f"回档成功！游戏状态已回到快照：{snapshot_name}")
            self.scan_saves()
        except Exception as e:
            messagebox.showerror("错误", f"回档失败: {e}\n请确保游戏已完全退出！")

    def export_zip(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个要打包的快照")
            return

        snapshot_name = self.backup_listbox.get(selection[0])
        snap_dir = os.path.join(self.backup_dir.get(), snapshot_name)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile=f"Terraria_Backup_{snapshot_name}.zip",
            title="导出为 Zip 压缩包"
        )
        if save_path:
            try:
                # shutil.make_archive 自动附加后缀，因此先去除用户输入的 .zip
                base_name = save_path[:-4] if save_path.endswith('.zip') else save_path
                shutil.make_archive(base_name, 'zip', snap_dir)
                messagebox.showinfo("成功", "压缩包导出成功！")
            except Exception as e:
                messagebox.showerror("打包失败", str(e))

    def import_zip(self):
        zip_path = filedialog.askopenfilename(title="选择快照压缩包", filetypes=[("Zip 压缩包", "*.zip")])
        if not zip_path: return

        try:
            # 生成一个新的快照ID，保证导入的数据有独立槽位
            next_id = self.get_next_snapshot_id()
            timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
            new_snap_name = f"{next_id:03d}_导入_{timestamp}"
            new_snap_dir = os.path.join(self.backup_dir.get(), new_snap_name)

            os.makedirs(new_snap_dir)
            shutil.unpack_archive(zip_path, new_snap_dir, 'zip')

            self.refresh_backup_list()
            messagebox.showinfo("成功", f"导入成功！已分配快照名：{new_snap_name}")
        except Exception as e:
            messagebox.showerror("导入失败", f"文件可能损坏或格式不正确：{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TerrariaBackupTool(root)
    root.mainloop()