import subprocess
import time
import pyautogui
from pywinauto import Application
import ctypes
import sys
import os

# 提取常量
APP_PATH = r"D:\XUNLEI\March7thAssistant_v2024.12.18_full\March7thAssistant_v2024.12.18_full\March7th Launcher.exe"
IMAGE_PATH_BUTTON = "L308, T1004, R700, B1324"
IMAGE_PATH_DONE = r"C:\Users\38384\Desktop\matutiyabafue\btowari.png"
WINDOW_TITLE = "March7th Assistant"


def is_admin():
    """检查当前进程是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """以管理员权限重新启动脚本"""
    if not is_admin():
        # 重新启动脚本并请求管理员权限
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()


def start_application(app_path):
    try:
        app = Application().start(app_path)
        time.sleep(5)
        return app
    except Exception as e:
        print(f"启动应用时出错: {e}")
        raise


def wait_for_image(image_path, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if pyautogui.locateOnScreen(image_path, confidence=0.9):
            print(f"找到图像: {image_path}")
            return True
        time.sleep(2)
    raise TimeoutError("任务超时")


def parse_image_region(image_region):
    """解析图像区域字符串并返回坐标"""
    image_region = image_region.replace('L', '').replace('T', '').replace('R', '').replace('B', '')
    l, t, r, b = map(int, image_region.split(', '))
    return l, t, r, b


def click_button_by_image(image_region, offset_x=100):
    """通过图像识别并点击按钮，并允许指定偏移量"""
    l, t, r, b = parse_image_region(image_region)
    button_center_x = (l + r) // 2 + offset_x  # 向右移动10个像素
    button_center_y = (t + b) // 2
    pyautogui.click(button_center_x, button_center_y)
    print(f"点击按钮: ({button_center_x}, {button_center_y})")


def check_file_exists(file_path):
    """检查文件是否存在"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    print(f"检查文件路径: {file_path}")


def main():
    try:
        # 检查图像文件是否存在
        check_file_exists(IMAGE_PATH_DONE)
        # 打开第一个应用并操作
        app1 = start_application(APP_PATH)
        app1_window = app1.window(title=WINDOW_TITLE)
        print(f"应用窗口: {app1_window}")
        # 点击按钮
        click_button_by_image(IMAGE_PATH_BUTTON, offset_x=10)
        # 等待完成标识
        wait_for_image(IMAGE_PATH_DONE)
    except Exception as e:
        print(f"流程出错: {e}")


if __name__ == "__main__":
    run_as_admin()
    main()
    input("按 Enter 键退出...")
