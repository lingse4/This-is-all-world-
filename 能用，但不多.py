import cv2
import pyautogui
import time
import os
import sys
import ctypes
from pywinauto import Application, Desktop
import numpy as np
import subprocess

# 常量定义
APP_PATH = r"D:\XUNLEI\March7thAssistant_v2024.12.18_full\March7thAssistant_v2024.12.18_full\March7th Launcher.exe"
SECOND_APP_PATH = r"D:\BetterGI\BetterGI\BetterGI.exe"
IMAGE_PATH_BUTTON = r"C:\Users\38384\Pictures\Screenshots\wzyx.png"
IMAGE_PATH_DONE = r"C:\Users\38384\Pictures\Screenshots\dhkjzht.png"
IMAGE_PATH_BUTTON_2 = r"C:\Users\38384\Pictures\Screenshots\qd.png"
IMAGE_PATH_BUTTON_3 = r"C:\Users\38384\Pictures\Screenshots\ytl.png"
IMAGE_PATH_BUTTON_4 = r"C:\Users\38384\Pictures\Screenshots\ysqd.png"
IMAGE_PATH_DONE_2 = r"C:\Users\38384\Pictures\Screenshots\mrwtjl.png"
WINDOW_TITLE = "March7th Assistant"
SECOND_WINDOW_TITLE = "更好的原神"

def cv_imread(file_path):
    """解决OpenCV中文路径问题"""
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

def bring_window_to_front(window_title):
    """强制将指定窗口置顶"""
    hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
    if hwnd != 0:
        # 恢复最小化窗口
        if ctypes.windll.user32.IsIconic(hwnd):
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
        # 置顶窗口
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        time.sleep(1)  # 等待窗口激活
    else:
        print(f"警告：未找到窗口 '{window_title}'")

def auto_click(var_avg, window_title):
    """修改后的点击函数"""
    if var_avg:
        bring_window_to_front(window_title)
        pyautogui.click(var_avg[0], var_avg[1], duration=0.25)
        minimize_window(window_title)  # 点击后最小化
        time.sleep(1)

def get_xy(img_model_path, interval=10, threshold=0.1):
    """获取图像坐标（带窗口激活检测）"""
    # 截图保存路径
    screenshot_dir = "./Pictures/Screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # 截图并保存
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    pyautogui.screenshot().save(screenshot_path)
    
    # 读取图像
    img = cv_imread(screenshot_path)
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        print("图像读取失败")
        return None

    # 转换灰度图
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)
    
    # 获取模板尺寸
    h, w = template_gray.shape
    
    # 模板匹配
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_SQDIFF_NORMED)
    min_val, _, min_loc, _ = cv2.minMaxLoc(res)
    
    # 阈值验证
    if min_val > threshold:
        print(f"匹配失败：当前阈值 {min_val:.3f} > 设定阈值 {threshold}")
        return None
    
    # 计算中心坐标
    x_center = min_loc[0] + w // 2
    y_center = min_loc[1] + h // 2
    return (x_center, y_center)

def auto_click(var_avg, window_title):
    """带窗口激活的点击操作"""
    if var_avg:
        bring_window_to_front(window_title)
        pyautogui.click(var_avg[0], var_avg[1], duration=0.25)
        time.sleep(1)

def routine(img_model_path, name, window_title):
    """自动化流程"""
    avg = get_xy(img_model_path)
    if avg:
        print(f'正在点击 {name}')
        auto_click(avg, window_title)
    else:
        print(f'未找到 {name}')

def check_file_exists(file_path):
    """文件存在性检查"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")
    print(f"已确认文件存在：{file_path}")

def start_application(app_path):
    """启动应用程序"""
    try:
        Application().start(app_path)
        time.sleep(5)
    except Exception as e:
        print(f"启动应用失败：{e}")
        raise

def is_admin():
    """管理员权限检查"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """请求管理员权限"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def main_operation():
    """主业务流程"""
    try:
        # 检查所有图像路径
        image_paths = [
            IMAGE_PATH_BUTTON, IMAGE_PATH_DONE,
            IMAGE_PATH_BUTTON_2, IMAGE_PATH_BUTTON_3,
            IMAGE_PATH_BUTTON_4, IMAGE_PATH_DONE_2
        ]
        for path in image_paths:
            check_file_exists(path)

        # 启动第一个应用
        start_application(APP_PATH)
        bring_window_to_front(WINDOW_TITLE)

        # 第一个应用操作流程
        routine(IMAGE_PATH_BUTTON, "完整运行", WINDOW_TITLE)

        # 等待任务完成
        print("等待第一个任务完成...")
        timeout = 999999  # 99999分钟超时
        start_time = time.time()
        while time.time() - start_time < timeout:
            if get_xy(IMAGE_PATH_DONE, threshold=0.01):
                print("检测到完成标识")
                break
            time.sleep(10)
        else:
            raise TimeoutError("第一个任务等待超时")

        subptocess.run(["ttaskkill /IM StarRail.exe /F"],shell=True)

        # 启动第二个应用
        start_application(SECOND_APP_PATH)
        bring_window_to_front(SECOND_WINDOW_TITLE)

        # 第二个应用操作流程
        routine(IMAGE_PATH_BUTTON_2, "启动按钮", SECOND_WINDOW_TITLE)
        routine(IMAGE_PATH_BUTTON_3, "一条龙", SECOND_WINDOW_TITLE)
        routine(IMAGE_PATH_BUTTON_4, "原始启动", SECOND_WINDOW_TITLE)

        # 等待第二个任务完成
        print("等待第二个任务完成...")
        timeout = 999999  # 10分钟超时
        start_time = time.time()
        while time.time() - start_time < timeout:
            if get_xy(IMAGE_PATH_DONE_2, threshold=0.01):
                print("检测到最终完成标识")
                break
            time.sleep(10)
        else:
            raise TimeoutError("第二个任务等待超时")

    except Exception as e:
        print(f"操作异常终止：{str(e)}")
        sys.exit(1)

    subprocess.run(["ttaskkill /IM YuanShen.exe /F"],shell=Turn)

if __name__ == "__main__":
    run_as_admin()
    main_operation()
    input("操作完成，按回车键退出...")