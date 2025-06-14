import cv2
import pyautogui
import time
import os
import sys
import ctypes
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import subprocess
from pywinauto import Application
from PIL import Image, ImageTk
import pygetwindow as gw
from pywinauto.application import Application
import psutil  # type: ignore # 用于检查进程是否存在
import switch_account

pyautogui.FAILSAFE = False  # 警告：关闭安全保护，风险自负！

# 常量定义
APP_PATH = r"D:\BaiduNetdiskDownload\March7thAssistant_v2025.4.18_full\March7th Launcher.exe"
SECOND_APP_PATH = r"D:\BetterGI\BetterGI\BetterGI.exe"
IMAGE_PATH_BUTTON = r"C:\Users\38384\Pictures\Screenshots\wzyx.png"
IMAGE_PATH_DONE = r"C:\Users\38384\Pictures\Screenshots\ahcjg.png"
IMAGE_PATH_BUTTON_3 = r"C:\Users\38384\Pictures\Screenshots\ytl.png"
IMAGE_PATH_BUTTON_4 = r"C:\Users\38384\Pictures\Screenshots\ysqd.png"
IMAGE_PATH_DONE_2 = r"C:\Users\38384\Pictures\Screenshots\jrjlylq.png"
WINDOW_TITLE = "March7th Assistant"
SECOND_WINDOW_TITLE = "更好的原神"

# GUI配置
BACKGROUND_IMAGE_PATH = r"C:\Users\38384\Desktop\CEBD96916B71E4B698AC4614B4A9D580.jpg"
ACCOUNT_FILE = "accounts.json"
GAMES = ["原神", "星穹铁道"]
THEME_COLORS = {
    "bg": "#2E2E2E",
    "fg": "#FFFFFF",
    "accent": "#4A90E2",
    "secondary": "#5C5C5C"
}

# ------------------------ 核心功能函数 ------------------------

def start_application(app_path):
    try:
        Application().start(app_path)
    except Exception as e:
        raise RuntimeError(f"启动应用失败：{e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def cv_imread(file_path):
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

def get_xy(img_model_path, threshold=0.7):
    screenshot_dir = "./screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    pyautogui.screenshot().save(screenshot_path)
    
    img = cv_imread(screenshot_path)
    img_terminal = cv2.imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)

    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

def auto_click(var_avg):
    if var_avg:
        pyautogui.click(var_avg[0], var_avg[1], duration=0)

def routine(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path, threshold=0.6)  # 将阈值从默认的 0.7 降低到 0.6
        if avg:
            print(f'正在点击 {name}')
            auto_click(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
        time.sleep(1)

def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")

def is_process_running(process_name):
    """检查指定进程是否正在运行"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

# 移除原有的 switch_account_thread 线程函数

def main_operation(progress_callback):
    progress_callback(0, "正在初始化...")
    print("---------- 开始执行主流程 ----------")
    try:
        # 新增：主流程延迟45秒执行
        progress_callback(10, "主流程将在45秒后启动...")
        progress_callback(30, "45秒等待完成,开始执行主操作...")

        # 原有主流程逻辑保持不变
        image_paths = [
            IMAGE_PATH_BUTTON, IMAGE_PATH_DONE, 
            IMAGE_PATH_BUTTON_3, IMAGE_PATH_BUTTON_3, 
            IMAGE_PATH_DONE_2
        ]
        for path in image_paths:
            check_file_exists(path)

        start_application(APP_PATH)
        time.sleep(5)
        routine(IMAGE_PATH_BUTTON, "完整运行")

        print("等待第一个任务完成...")
        routine(IMAGE_PATH_DONE, "按回车键关")

        subprocess.run(["taskkill","/IM","StarRail.exe","/F","/T"])
        subprocess.run(["taskkill", "/IM", "March7th Launcher.exe", "/F", "/T"], check=True)
        pyautogui.press('enter')
        
        # start_application(SECOND_APP_PATH)
        
        # # 删除了 routine(IMAGE_PATH_BUTTON_2, "启动按钮") 的调用
        # routine(IMAGE_PATH_BUTTON_3, "一条龙")
        # time.sleep(2)
        
        # # 替换点击按钮的图像路径为 IMAGE_PATH_BUTTON_4
        # routine(IMAGE_PATH_BUTTON_4, "原神启动！")
        
        # # 如果 YuanShen.exe 不存在，则不断尝试点击 ysqd 按钮
        # while not is_process_running("YuanShen.exe"):
        #     print("未检测到 YuanShen.exe，尝试点击确认启动按钮...")
        #     if routine(IMAGE_PATH_BUTTON_4, "原神启动", timeout=5):
        #         print("成功点击确认启动按钮")
        #     else:
        #         print("点击失败，继续尝试...")
        #     time.sleep(2)
        
        # print("等待第二个任务完成...")
        # if not routine(IMAGE_PATH_DONE_2, "最终完成标识"):
        #     raise TimeoutError("第二个任务等待超时")
        # subprocess.run(["taskkill","/IM","YuanShen.exe","/F","/T"])
        # subprocess.run(["taskkill","/IM","BetterGI.exe","/F","/T"])

    except Exception as e:
        print(f"操作异常终止：{str(e)}")
    finally:
        print("---------- 主流程执行完成 ----------")

# ------------------------ GUI 功能 ------------------------

class ModernGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("游戏启动助手")
        self.geometry("1200x800")
        self.configure(bg=THEME_COLORS["bg"])
        
        self.current_game = GAMES[0]
        self.progress_window = None
        
        # 初始化样式
        self.init_styles()
        
        # 构建界面
        self.create_main_container()
        self.create_sidebar()
        self.create_main_content()
        
    def init_styles(self):
        style = ttk.Style()
        style.theme_create("modern", parent="alt", settings={
            "TNotebook": {
                "configure": {"background": THEME_COLORS["bg"], "borderwidth": 0}
            },
            "TNotebook.Tab": {
                "configure": {
                    "padding": [15, 5],
                    "background": THEME_COLORS["secondary"],
                    "foreground": THEME_COLORS["fg"],
                    "font": ("微软雅黑", 12)
                },
                "map": {
                    "background": [("selected", THEME_COLORS["accent"])],
                    "expand": [("selected", [1, 1, 1, 1])]
                }
            },
            "TButton": {
                "configure": {
                    "padding": 6,
                    "relief": "flat",
                    "background": THEME_COLORS["accent"],
                    "foreground": THEME_COLORS["fg"],
                    "font": ("微软雅黑", 12)
                },
                "map": {
                    "background": [("active", "#3B7FC4")],
                    "foreground": [("disabled", "#888888")]
                }
            }
        })
        style.theme_use("modern")
        
    def create_main_container(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
    def create_sidebar(self):
        sidebar = ttk.Frame(self.main_container, width=200)
        sidebar.pack(side="left", fill="y")
        
        logo_frame = ttk.Frame(sidebar)
        logo_frame.pack(pady=20)
        
        self.logo = self.load_scaled_image(BACKGROUND_IMAGE_PATH, (160, 160))
        ttk.Label(logo_frame, image=self.logo).pack()
        
        nav_buttons = [
            ("🚀 一键启动", self.show_launch),
            ("👤 账户管理", self.show_accounts),
            ("⚙️ 系统设置", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(sidebar, text=text, command=command)
            btn.pack(fill="x", pady=5)
        
    def create_main_content(self):
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(side="right", expand=True, fill="both")
        
        # 启动界面
        self.launch_frame = ttk.Frame(self.notebook)
        self.create_launch_ui()
        self.notebook.add(self.launch_frame, text="游戏启动")
        
        # 账户管理界面
        self.account_frame = ttk.Frame(self.notebook)
        self.create_account_ui()
        self.notebook.add(self.account_frame, text="账户管理")
        
        # 默认显示启动界面
        self.notebook.select(0)
        
    def create_launch_ui(self):
        container = ttk.Frame(self.launch_frame)
        container.pack(expand=True, fill="both")
        
        # 动态背景图
        self.canvas = tk.Canvas(container, bg=THEME_COLORS["bg"], highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        
        # 启动按钮
        launch_btn = ttk.Button(container, text="开 始 执 行", command=self.start_game)
        launch_btn.place(relx=0.5, rely=0.5, anchor="center")
        
        # 状态标签
        self.status_label = ttk.Label(container, text="准备就绪", foreground="#AAAAAA")
        self.status_label.place(relx=0.5, rely=0.8, anchor="center")
        
    def create_account_ui(self):
        notebook = ttk.Notebook(self.account_frame)
        notebook.pack(expand=True, fill="both")
        
        # 为每个游戏创建账户页
        self.game_frames = {}
        for game in GAMES:
            frame = ttk.Frame(notebook)
            self.create_game_account_ui(frame, game)
            notebook.add(frame, text=game)
            self.game_frames[game] = frame
            
    def create_game_account_ui(self, parent, game):
        container = ttk.Frame(parent)
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # 账户表格
        columns = ("#1", "#2", "#3", "#4")
        tree = ttk.Treeview(container, columns=columns, show="headings", height=5)
        tree.heading("#1", text="账号")
        tree.heading("#2", text="密码")
        tree.heading("#3", text="配置文件")
        tree.heading("#4", text="操作")
        tree.pack(fill="both", expand=True)
        
        # 操作按钮
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="添加账户", command=lambda: self.edit_account(game)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="导入配置", command=lambda: self.import_config(game)).pack(side="left", padx=5)
        
    def load_scaled_image(self, path, size):
        try:
            img = Image.open(path)
            img.thumbnail(size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"图片加载失败：{e}")
            return None
            
    def show_launch(self):
        self.notebook.select(0)
        
    def show_accounts(self):
        self.notebook.select(1)
        
    def show_settings(self):
        messagebox.showinfo("提示", "设置功能开发中")
        
    def start_game(self):
        # 移除线程逻辑，改为同步执行
        self.update_status("正在初始化...", 0)
        try:
            # 定义回调函数（直接同步调用main_operation）
            def main_operation_callback():
                main_operation(lambda p, msg: self.update_status(msg, p))
            
            # 同步调用 switch_account（会阻塞界面，直到完成）
            switch_account.switch_account(main_operation_callback)
            
            self.update_status("所有操作完成", 100)
        except Exception as e:
            self.update_status(f"执行出错：{str(e)}", 100, error=True)

    def update_status(self, message, progress, error=False):
        self.status_label.config(text=message)
        if error:
            messagebox.showerror("错误", message)
            
    def edit_account(self, game):
        # 账户编辑对话框实现
        pass
        
    def import_config(self, game):
        path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON 文件", "*.json")]
        )
        if path:
            try:
                with open(path, 'r') as f:
                    accounts = json.load(f)
                    self.account_mgr.accounts[game] = accounts
                    self.account_mgr.save_accounts()
                    messagebox.showinfo("成功", "配置导入成功")
            except Exception as e:
                messagebox.showerror("错误", f"配置导入失败：{str(e)}")

if __name__ == "__main__":
    try:
        run_as_admin()
        app = ModernGUI()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("致命错误", f"程序崩溃：{str(e)}")


