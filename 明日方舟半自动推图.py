from asyncio import Queue
import ctypes
from ctypes import wintypes
import pyautogui
import time
import easyocr
from PIL import Image
import cv2
import numpy as np
from pynput import keyboard
from torch.utils.data import DataLoader, dataset
import win32gui
import os
import threading
from pynput.keyboard import Controller
import subprocess

# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16384"  # 指定目标设备
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接！请确认设备 {device_serial} 已开启USB调试模式")

# 初始化 EasyOCR 读取器
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # 支持中文和英文

# 初始化键盘控制器
keyboard_controller = Controller()

# -------------------- 2. ADB截图函数 --------------------
def adb_screenshot(save_path="screen.png"):
    """截取模拟器屏幕并保存为文件"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16384"  # 指定目标设备
    subprocess.run(f"{adb_path} -s {device_serial} shell screencap -p /sdcard/screen.png", shell=True, check=True)
    subprocess.run(f"{adb_path} -s {device_serial} pull /sdcard/screen.png {save_path}", shell=True, check=True)
    return save_path  # 返回图像路径

# -------------------- 5. ADB点击函数 --------------------
def adb_tap(x, y):
    """使用ADB命令在指定坐标点击"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16384"  # 指定目标设备
    subprocess.run(f"{adb_path} -s {device_serial} shell input tap {x} {y}", shell=True, check=True)


# 定义 BITMAP 结构
class BITMAP(ctypes.Structure):
    _fields_ = [
        ("bmType", wintypes.LONG),
        ("bmWidth", wintypes.LONG),
        ("bmHeight", wintypes.LONG),
        ("bmWidthBytes", wintypes.LONG),
        ("bmPlanes", wintypes.WORD),
        ("bmBitsPixel", wintypes.WORD),
        ("bmBits", ctypes.c_void_p),
    ]

def maximize_window(hwnd):
    """
    将指定窗口最大化
    :param hwnd: 窗口句柄
    """
    ctypes.windll.user32.ShowWindow(hwnd, SW_MAXIMIZE)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    print("窗口已最大化")

def restore_window(hwnd):
    """
    恢复窗口到原始大小
    :param hwnd: 窗口句柄
    """
    ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    print("窗口已恢复到原始大小")

def center_window(hwnd, width=1800, height=900):
    """
    将指定窗口居中
    :param hwnd: 窗口句柄
    :param width: 窗口宽度
    :param height: 窗口高度
    """
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    ctypes.windll.user32.MoveWindow(hwnd, x, y, width, height, True)
    print(f"窗口已居中到 ({x}, {y})，分辨率设置为 {width}x{height}")

def capture_window_screenshot(hwnd, output_path):
    """
    截取指定窗口的内容并保存为图片
    :param hwnd: 窗口句柄
    :param output_path: 截图保存路径
    """
    rect = win32gui.GetWindowRect(hwnd)
    x, y, w, h = rect
    width = w - x
    height = h - y

    # 获取窗口设备上下文
    hdesktop = ctypes.windll.user32.GetDC(hwnd)
    hdc = ctypes.windll.gdi32.CreateCompatibleDC(hdesktop)
    hbmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdesktop, width, height)
    ctypes.windll.gdi32.SelectObject(hdc, hbmp)

    # 执行 BitBlt 截图
    ctypes.windll.gdi32.BitBlt(hdc, 0, 0, width, height, hdesktop, 0, 0, 0x00CC0020)

    # 保存位图为图片
    bmpinfo = BITMAP()
    ctypes.windll.gdi32.GetObjectW(hbmp, ctypes.sizeof(bmpinfo), ctypes.byref(bmpinfo))
    bmpstr = ctypes.create_string_buffer(bmpinfo.bmWidthBytes * bmpinfo.bmHeight)
    ctypes.windll.gdi32.GetBitmapBits(hbmp, len(bmpstr), bmpstr)

    # 使用 PIL 保存图片
    image = Image.frombuffer('RGB', (bmpinfo.bmWidth, bmpinfo.bmHeight), bmpstr, 'raw', 'BGRX', 0, 1)
    image.save(output_path)

    # 释放资源
    ctypes.windll.gdi32.DeleteObject(hbmp)
    ctypes.windll.gdi32.DeleteDC(hdc)
    ctypes.windll.user32.ReleaseDC(hwnd, hdesktop)
    print(f"窗口截图已保存至 {output_path}")

def cv_imread(file_path):
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

def get_xy(img_model_path, screenshot_path, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param screenshot_path: 截图保存路径
    :param threshold: 匹配阈值，默认为0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果没有匹配则返回None
    """
    screenshot_dir = "./Pictures/Screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    pyautogui.screenshot().save(screenshot_path)
    
    img = cv_imread(screenshot_path)
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)
    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

def auto_click(var_avg):
    """
    接受一个元组参数，自动点击
    :param var_avg: 坐标范围
    :return: None
    """
    if var_avg:
        pyautogui.click(var_avg[0], var_avg[1], button='left')
        time.sleep(2)

def routine(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path)
        if avg:
            print(f'正在点击 {name}')
            auto_click(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
        time.sleep(1)

def capture_screenshot_with_bitblt(output_path):
    """
    使用 BitBlt 截取屏幕并保存为图片
    :param output_path: 截图保存路径
    """
    hdesktop = ctypes.windll.user32.GetDC(0)
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    hdc = ctypes.windll.gdi32.CreateCompatibleDC(hdesktop)
    hbmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdesktop, width, height)
    ctypes.windll.gdi32.SelectObject(hdc, hbmp)
    ctypes.windll.gdi32.BitBlt(hdc, 0, 0, width, height, hdesktop, 0, 0, 0x00CC0020)
    bmpinfo = ctypes.windll.gdi32.GetObjectW(hbmp, ctypes.sizeof(wintypes.BITMAP))
    bmpinfo = wintypes.BITMAP()
    ctypes.windll.gdi32.GetObjectW(hbmp, ctypes.sizeof(bmpinfo), ctypes.byref(bmpinfo))
    bmpstr = ctypes.create_string_buffer(bmpinfo.bmWidthBytes * bmpinfo.bmHeight)
    ctypes.windll.gdi32.GetBitmapBits(hbmp, len(bmpstr), bmpstr)
    image = Image.frombuffer('RGB', (bmpinfo.bmWidth, bmpinfo.bmHeight), bmpstr, 'raw', 'BGRX', 0, 1)
    image.save(output_path)
    ctypes.windll.gdi32.DeleteObject(hbmp)
    ctypes.windll.gdi32.DeleteDC(hdc)
    ctypes.windll.user32.ReleaseDC(0, hdesktop)
    print(f"截图已保存至 {output_path}")

def capture_screenshot(output_path):
    """
    使用 BitBlt 截取屏幕并保存为图片
    :param output_path: 截图保存路径
    """
    capture_screenshot_with_bitblt(output_path)

def preprocess_image(image_path):
    """
    预处理图片以提高 OCR 识别率
    :param image_path: 图片路径
    :return: 图片路径（直接返回原路径，因为不再保存新的截图）
    """
    return image_path  # 直接返回原路径

def get_window_position():
    """
    获取当前活动窗口的位置
    :return: 窗口的左上角坐标 (x, y)
    """
    hwnd = win32gui.GetForegroundWindow()  # 获取当前活动窗口句柄
    rect = win32gui.GetWindowRect(hwnd)  # 获取窗口位置
    return rect[0], rect[1]  # 返回窗口左上角的 x 和 y 坐标

def find_and_click_text(screenshot_path, target_text):
    """
    截屏并检测目标文字，识别到后点击
    :param screenshot_path: 截图保存路径
    :param target_text: 目标文字
    :return: 点击的坐标 (x, y)，如果未找到则返回 None
    """
    capture_screenshot(screenshot_path)
    processed_path = preprocess_image(screenshot_path)
    time.sleep(1)  # 等待截图保存完成
    results = reader.readtext(processed_path, detail=1)  # 获取详细信息，包括坐标
    for (bbox, text, prob) in results:
        if target_text in text:
            print(f"找到目标文字 '{target_text}'，坐标: {bbox}")
            # 计算文字区域的中心点
            (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
            center_x = int((x_min + x_max) / 2)
            center_y = int((y_min + y_max) / 2)

            # 获取窗口位置并修正坐标
            window_x, window_y = get_window_position()
            corrected_x = center_x + window_x
            corrected_y = center_y + window_y

            print(f"点击坐标: ({corrected_x}, {corrected_y})")
            pyautogui.click(corrected_x, corrected_y)  # 点击中心点
            print(f"已点击目标文字 '{target_text}'")
            return corrected_x, corrected_y
    print(f"未找到目标文字 '{target_text}'")
    return None

def find_and_click_text_in_window(hwnd, target_text, screenshot_path):
    """
    持续检测窗口内容并点击目标文字
    :param hwnd: 窗口句柄
    :param target_text: 目标文字
    :param screenshot_path: 截图保存路径
    """
    while True:
        capture_window_screenshot(hwnd, screenshot_path)
        results = reader.readtext(screenshot_path, detail=1)  # 获取详细信息，包括坐标
        for (bbox, text, prob) in results:
            if target_text in text:
                # 计算文字区域的中心点
                (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
                center_x = int((x_min + x_max) / 2)
                center_y = int((y_min + y_max) / 2)

                # 获取窗口位置并修正坐标
                rect = win32gui.GetWindowRect(hwnd)
                corrected_x = center_x + rect[0]
                corrected_y = center_y + rect[1]

                print(f"找到目标文字 '{target_text}'，点击坐标: ({corrected_x}, {corrected_y})")
                pyautogui.click(corrected_x, corrected_y)  # 点击中心点
                return True
        print(f"未找到目标文字 '{target_text}'，继续检测...")
        time.sleep(0.5)  # 等待 0.5 秒后继续检测

def capture_fullscreen_screenshot(output_path):
    """
    截取全屏并保存为图片
    :param output_path: 截图保存路径
    """
    hdesktop = ctypes.windll.user32.GetDC(0)
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    hdc = ctypes.windll.gdi32.CreateCompatibleDC(hdesktop)
    hbmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdesktop, width, height)
    ctypes.windll.gdi32.SelectObject(hdc, hbmp)

    # 执行 BitBlt 截图
    ctypes.windll.gdi32.BitBlt(hdc, 0, 0, width, height, hdesktop, 0, 0, 0x00CC0020)

    # 保存位图为图片
    bmpinfo = BITMAP()
    ctypes.windll.gdi32.GetObjectW(hbmp, ctypes.sizeof(bmpinfo), ctypes.byref(bmpinfo))
    bmpstr = ctypes.create_string_buffer(bmpinfo.bmWidthBytes * bmpinfo.bmHeight)
    ctypes.windll.gdi32.GetBitmapBits(hbmp, len(bmpstr), bmpstr)

    # 使用 PIL 保存图片
    image = Image.frombuffer('RGB', (bmpinfo.bmWidth, bmpinfo.bmHeight), bmpstr, 'raw', 'BGRX', 0, 1)
    image.save(output_path)

    # 释放资源
    ctypes.windll.gdi32.DeleteObject(hbmp)
    ctypes.windll.gdi32.DeleteDC(hdc)
    ctypes.windll.user32.ReleaseDC(0, hdesktop)
    print(f"全屏截图已保存至 {output_path}")

def find_and_text_fullscreen(screenshot_path, target_text):
    """
    截取全屏内容并检测目标文字
    """
    capture_fullscreen_screenshot(screenshot_path)
    for _ in range(3):  # 尝试最多 3 次
        try:
            results = reader.readtext(screenshot_path, detail=1)  # 获取详细信息，包括坐标
            for (bbox, text, prob) in results:
                if target_text in text:
                    (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
                    center_x = int((x_min + x_max) / 2)
                    center_y = int((y_min + y_max) / 2)

                    print(f"找到目标文字 '{target_text}")
                    return center_x, center_y  # 返回点击的坐标
            print(f"未找到目标文字 '{target_text}'")
            return None
        except OSError as e:
            print(f"读取图片失败: {e}，重试中...")
            time.sleep(0.5)
    raise OSError(f"无法读取图片文件: {screenshot_path}")

def match_and_click(template_path, screenshot_path, threshold=0.8):
    """
    使用 OpenCV 模板匹配检测目标并点击
    :param template_path: 模板图片路径
    :param screenshot_path: 截图保存路径
    :param threshold: 匹配阈值
    """
    while True:
        capture_fullscreen_screenshot(screenshot_path)
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {screenshot_path} 或 {template_path}")
            return False

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:  # 如果截图是 4 通道（带透明通道）
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)  # 转为 3 通道
        if template.shape[2] == 4:  # 如果模板是 4 通道（带透明通道）
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)  # 转为 3 通道

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 计算模板中心点
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2

            print(f"匹配成功，点击坐标: ({center_x}, {center_y})")
            pyautogui.click(center_x, center_y)
            return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...")
            time.sleep(0.5)

def wait_for_image(template_path, screenshot_path, threshold=0.8):
    """
    循环检测目标图片是否出现，不点击
    :param template_path: 模板图片路径
    :param screenshot_path: 截图保存路径
    :param threshold: 匹配阈值
    :return: 是否检测到目标
    """
    while True:
        capture_fullscreen_screenshot(screenshot_path)
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {screenshot_path} 或 {template_path}")
            return False

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:  # 如果截图是 4 通道（带透明通道）
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)  # 转为 3 通道
        if template.shape[2] == 4:  # 如果模板是 4 通道（带透明通道）
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)  # 转为 3 通道

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            print(f"检测到目标图片: {template_path}")
            return True
        else:
            print(f"未检测到目标图片: {template_path}，继续检测...")
            time.sleep(0.5)

def match_and_click_with_retry(template_path, screenshot_path, event_template_path, threshold=0.8, click_once=False, wait_before_click=0):
    """
    使用 OpenCV 模板匹配检测目标并点击，点击后验证是否成功
    :param template_path: 模板图片路径
    :param screenshot_path: 截图保存路径
    :param event_template_path: 点击后验证的事件图片路径
    :param threshold: 匹配阈值
    :param click_once: 是否只点击一次
    :param wait_before_click: 点击前等待的时间（秒）
    """
    clicked_once = False
    while True:
        # 截取全屏并匹配目标
        capture_fullscreen_screenshot(screenshot_path)
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {screenshot_path} 或 {template_path}")
            return False

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

        # 执行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 计算模板中心点
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2

            print(f"匹配成功，点击坐标: ({center_x}, {center_y})")

            # 如果设置了只点击一次且已经点击过，则直接返回
            if click_once and clicked_once:
                print(f"目标 {template_path} 已点击一次，不再重复点击")
                return True

            # 等待指定时间后点击
            if wait_before_click > 0:
                print(f"等待 {wait_before_click} 秒后点击...")
                time.sleep(wait_before_click)

            pyautogui.click(center_x, center_y)
            clicked_once = True
            time.sleep(1)  # 等待点击效果生效

            # 验证点击是否成功
            if event_template_path:
                while True:
                    capture_fullscreen_screenshot(screenshot_path)
                    event_screenshot = cv2.imread(screenshot_path, cv2.IMREAD_UNCHANGED)
                    event_template = cv2.imread(event_template_path, cv2.IMREAD_UNCHANGED)

                    if event_screenshot is None or event_template is None:
                        print(f"无法加载事件图片: {screenshot_path} 或 {event_template_path}")
                        return False

                    # 确保事件图片和截图的通道一致
                    if event_screenshot.shape[2] == 4:
                        event_screenshot = cv2.cvtColor(event_screenshot, cv2.COLOR_BGRA2BGR)
                    if event_template.shape[2] == 4:
                        event_template = cv2.cvtColor(event_template, cv2.COLOR_BGRA2BGR)

                    # 执行事件图片匹配
                    event_result = cv2.matchTemplate(event_screenshot, event_template, cv2.TM_CCOEFF_NORMED)
                    _, event_max_val, _, _ = cv2.minMaxLoc(event_result)

                    if event_max_val >= threshold:
                        print(f"点击事件成功触发: {event_template_path}")
                        return True
                    else:
                        print(f"点击后未检测到事件图片: {event_template_path}，再次点击...")
                        pyautogui.click(center_x, center_y)
                        time.sleep(1)  # 等待点击效果生效
            else:
                return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...")
            time.sleep(0.5)

# 创建队列用于线程间通信
screenshot_queue = Queue()

def capture_and_enqueue_screenshot(output_path):
    """
    截取全屏并将截图路径放入队列
    """
    capture_fullscreen_screenshot(output_path)
    screenshot_queue.put(output_path)

SCREENSHOT_PATH_THREAD = r"C:\Users\38384\Pictures\Screenshots\thread_screenshot.png"
SCREENSHOT_PATH_MAIN = r"C:\Users\38384\Pictures\Screenshots\main_screenshot.png"

def detect_and_click_tg_and_s():
    """
    持续检测并点击 tg.png 和 s.png
    """
    print("开始循环检测并点击 'tg.png' 和 's.png'")
    while True:
        tg_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\tg.png", SCREENSHOT_PATH_THREAD)
        if tg_coords:
            print("检测到 'tg.png'，点击...")
            auto_click(tg_coords)

        s_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s.png", SCREENSHOT_PATH_THREAD)
        if s_coords:
            print("检测到 's.png'，点击...")
            auto_click(s_coords)

        time.sleep(2)

# 主线程中定期生成截图
def main():
    while True:
        capture_and_enqueue_screenshot(screenshot_path)
        time.sleep(1)

def main_process():
    """
    主流程逻辑
    """
    print("开始主流程...")

        # 检查ADB连接
    check_adb_connection()
    
    # 截取屏幕
    screen_path = adb_screenshot()
    
    # 读取图像文件为numpy数组
    img = cv2.imread(screen_path)
    
    # 调试信息：打印图像尺寸
    print(f"截取的图像尺寸: {img.shape}")
    
    # 初始化EasyOCR阅读器（英文）
    reader_en = easyocr.Reader(['en'])
    
    # 使用EasyOCR进行OCR识别（英文）
    result_en = reader_en.readtext(img)
    print("英文识别结果:")
    
    # 过滤包含 '-' 的识别结果
    filtered_results = [detection for detection in result_en if '-' in detection[1]]
    
    # 找到最右边的文本
    rightmost_detection = None
    max_x = -1
    for detection in filtered_results:
        bbox, text, confidence = detection
        x_center = sum([point[0] for point in bbox]) / len(bbox)
        if x_center > max_x:
            max_x = x_center
            rightmost_detection = detection
    
    if rightmost_detection is not None:
        bbox, text, confidence = rightmost_detection
        x_center = int(sum([point[0] for point in bbox]) / len(bbox))
        y_center = int(sum([point[1] for point in bbox]) / len(bbox))
        
        print(f"最右边的文本: {text} (置信度: {confidence:.2f})")
        print(f"中心点坐标: ({x_center}, {y_center})")
        
        # 使用ADB点击最右边文本的中心点
        adb_tap(x_center, y_center)
    else:
        print("没有找到包含 '-' 的文本。")

    while True:
        coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\yx.png", screenshot_path)
        if coords:  # 如果成功找到目标图片
            print(f"开始半自动推图")
            break
        else:
            print("未检测到目标图片，继续检测...")
            time.sleep(1)  # 等待 1 秒后重试


    txms_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\txms.png", screenshot_path)
    if txms_coords:
        print(f"切换为突袭模式,坐标：{txms_coords}")
        auto_click(txms_coords)  # 点击 txms.png 的位置
    else:
        print("原来只是普通关卡")

    start_coords = (1161,738)

    pyautogui.click(start_coords[0], start_coords[1])  # 使用第一步的点击坐标

    #start_coords = None
    #while not start_coords:
        #start_coords = find_and_text_fullscreen(screenshot_path, "开始")
        #if start_coords:
            #print(f"找到 '开始' 按钮，坐标: {start_coords[0]}, {start_coords[1]}")
            #pyautogui.click(start_coords[0], start_coords[1])  # 点击 '开始' 按钮
        #else:
            #print("未找到 '开始' 按钮，继续检测...")
            #time.sleep(1)  # 等待 1 秒后重试


    ks1_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\ks1.png", screenshot_path)
    if ks1_coords:
        auto_click(start_coords[0], start_coords[1])  # 修复：确保 ks1_coords 已赋值
        print("磨难模式启动！")
    else:
        print("还没有到磨难模式")


    # 第三步：全屏截图并匹配 s2.png
    capture_fullscreen_screenshot(screenshot_path)  # 全屏截图
    s2_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s2.png", screenshot_path)  # 匹配 s2.png
    if s2_coords:
        print("吃个药药")
        pyautogui.click(s2_coords[0], s2_coords[1])  
        time.sleep(2)  # 等待 1 秒
        pyautogui.click(start_coords[0], start_coords[1])  # 使用 ks1_coords 的点击坐标
    else:
        print("启动！")

    # 后续步骤：使用 OpenCV 模板匹配检测并点击，验证点击事件
    print("检测并点击 '助战干员'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\zz.png",
        screenshot_path,
        r"C:\Users\38384\Pictures\Screenshots\jr.png"
    )

    pyautogui.click(start_coords[0] - 1094, start_coords[1] - 462)  # 使用第一步的点击坐标

    yh_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\jr.png", screenshot_path, threshold=0.6)
    yh2_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\yh2.png", screenshot_path, threshold=0.6)
    jr_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\jr.png", screenshot_path, threshold=0.6)
    while True:
        capture_fullscreen_screenshot(screenshot_path)
        if yh_coords:
            print("点击银灰")
            pyautogui.click(yh_coords[0], yh_coords[1])
            break
        elif yh2_coords:
            print("点击银灰2")
            pyautogui.click(yh2_coords[0], yh2_coords[1])
            break
        elif jr_coords:
            pyautogui.click(jr_coords[0],jr_coords[1])  # 使用第一步的点击坐标
        else:
            print("银灰不在，继续")
            keyboard_controller.press('0')  # 按下键 '0'
            keyboard_controller.release('0')  # 松开键 '0'
    time.sleep(1)  # 等待 1 秒

    print("检测并点击 '招募助战'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\zm.png",
        screenshot_path,
        None,  # 无需验证事件
        click_once=True  # 只点击一次
    )

    pyautogui.click(start_coords[0] - 30, start_coords[1] - 30)  # 使用第一步的点击坐标

    # 第四步：全屏截图并匹配 s1.png
    capture_fullscreen_screenshot(screenshot_path)  # 全屏截图
    s1_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s1.png", screenshot_path)  # 匹配 s1.png
    if s1_coords:
        print(f"确认ban位")
        auto_click(s1_coords)  # 点击 s1.png 的位置
    else:
        print("下一步")

    # 第五步：检测并点击 "1倍速"
    print("检测并点击 '1倍速'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\1bs.png",
        screenshot_path,
        r"C:\Users\38384\Pictures\Screenshots\2bs.png"
    )

    # 第六步：等待 "2倍速" 出现
    print("等待 '2倍速' 出现")
    wait_for_image(r"C:\Users\38384\Pictures\Screenshots\2bs.png", screenshot_path)

    # 第七步：检测并点击 "暂停"
    print("检测并点击 '部署干员'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\bsgy.png",
        screenshot_path,
        None,  # 无需验证事件
        click_once=True  # 只点击一次
    )

    # 第八步：检测并点击 "行动结束"
    print("检测并点击 '行动结束'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\xd.png",
        screenshot_path,
        None,  # 最后一步无需验证事件
        click_once=True,  # 点击一次
        wait_before_click=2  # 点击前等待 200 秒
    )

if __name__ == "__main__":
    # 截图保存路径
    screenshot_path = r"C:\Users\38384\Pictures\Screenshots\screenshot.png"

    # 启动独立线程进行循环检测
    detection_thread = threading.Thread(target=detect_and_click_tg_and_s, daemon=True)
    detection_thread.start()

    # 主流程循环
    while True:
        print("开始新一轮主流程...")
        main_process()
        print("主流程完成，等待 5 秒后重新开始...")
        time.sleep(5)  # 等待 5 秒后重新开始

DataLoader(dataset, batch_size=32, shuffle=True, pin_memory=False)


