from asyncio import Queue
from csv import reader
import ctypes
import os
import re
import socket
import subprocess
import sys
import time
import easyocr
import cv2
import numpy as np
import threading
import pyautogui
from pyminitouch.utils import str2byte
from pynput import keyboard
from paddleocr import PaddleOCR
import pygetwindow as gw
from minitouchdj import send_touch_command as dj

SCREENSHOT_DIR = r"C:\Users\38384\Pictures\Screenshots"
SCREENSHOT_MAIN = os.path.join(SCREENSHOT_DIR, "main_screenshot.png")
SCREENSHOT_THREAD = os.path.join(SCREENSHOT_DIR, "thread_screenshot.png")
processed_texts = []
device_serial = "127.0.0.1:16384"  # 指定目标设备
PORT = 1090         # minitouch服务端口

# 初始化 EasyOCR 读取器
ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch")

# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接!请确认设备 {device_serial} 已开启USB调试模式")

# -------------------- 2. ADB截图函数 --------------------
def adb_screenshot(save_path=SCREENSHOT_MAIN):
    """截取模拟器屏幕并保存为文件"""
    """通过 ADB 直接获取截图二进制流，避免文件传输损坏"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"

    
    command = f'"{adb_path}" -s {device_serial} exec-out screencap -p'

    try:
        # 直接捕获二进制数据
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        # 将二进制数据写入文件
        with open(save_path, "wb") as f:
            f.write(result.stdout)
        print(f"截图保存成功: {save_path}")
        return save_path
    except subprocess.CalledProcessError as e:
        print(f"截图失败: {e.stderr.decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"截图异常: {str(e)}")
        return False

def cv_imread(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在！")
        return None
    try:
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None
    
# -------------------- 3. ADB点击函数 --------------------
def adb_tap(x, y):
    """
    使用ADB命令模拟点击屏幕坐标 (x, y)
    """
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    x = int(x)
    y = int(y)
    command = f'"{adb_path}" -s {device_serial} shell input tap {x} {y}'
    print(f"执行的命令: {command}")
    os.system(command)

# -------------------- 6. adb返回键命令函数 --------------------
def adb_back():
    """使用ADB命令模拟返回键"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    command = f'"{adb_path}" -s {device_serial} shell input keyevent KEYCODE_ESCAPE'
    print(f"执行的命令: {command}")
    os.system(command)

def get_xy(img_model_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值，默认为0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果没有匹配则返回None
    """
    screenshot_dir = "./Pictures/Screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    adb_screenshot(SCREENSHOT_MAIN)
    img = cv_imread(SCREENSHOT_MAIN)
    img_terminal = cv_imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)
    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

    
    # -------------------- 5. 基于socket的minitouch点击函数 --------------------
def dj(x, y):
    """使用socket发送minitouch触摸指令(替换原ADB点击)"""
    HOST = '127.0.0.1'  # minitouch服务地址
    x = int(x)
    y = int(y)

    # 构造触摸指令（d:按下, w:等待, c:提交, u:抬起）
    # 注意：坐标顺序为y在前，x在后（根据你的模板调整）
    content = f"d 0 {720-y} {x} 50\nw 400\nc\nu 0\nc\n"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(str2byte(content))
    time.sleep(0.5)
    sock.shutdown(socket.SHUT_WR)

    res = ''
    while True:
        data = sock.recv(1024)
        if (not data):
            break
        res += data.decode()

    print(res)
    print('closed')
    sock.close()

def routine(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path, SCREENSHOT_MAIN)
        if avg:
            print(f'正在点击 {name}')
            dj(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
time.sleep(1)

def bring_window_to_front(window_title):
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            print(f"No window found with title: {window_title}")
            return
        
        window = windows[0]
        
        # 如果窗口是最小化的，则还原它
        if window.isMinimized:
            window.restore()
            print(f"Window '{window_title}' restored from minimized state.")
        
        # 将窗口置于前台
        window.activate()
        print(f"Window '{window_title}' brought to front.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def minimize_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.minimize()
        print(f"Window '{window_title}' minimized.")
    except IndexError:
        print(f"No window found with title: {window_title}")

def find_and_click_text(SCREENSHOT_MAIN, target_text):
    """
    截屏并检测目标文字，识别到后点击
    :param SCREENSHOT_MAIN: 截图保存路径
    :param target_text: 目标文字
    :return: 点击的坐标 (x, y)，如果未找到则返回 None
    """
    adb_screenshot(SCREENSHOT_MAIN)
    processed_path = preprocess_image(SCREENSHOT_MAIN)
    time.sleep(1)  # 等待截图保存完成
    results = reader.readtext(processed_path, detail=1)  # 获取详细信息，包括坐标
    for (bbox, text, prob) in results:
        if target_text in text:
            print(f"找到目标文字 '{target_text}'，坐标: {bbox}")
            # 计算文字区域的中心点
            (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
            center_x = int((x_min + x_max) / 2)
            center_y = int((y_min + y_max) / 2)

            print(f"点击坐标: ({center_x}, {center_y})")
            dj(center_x, center_y)  # 点击中心点
            print(f"已点击目标文字 '{target_text}'")
            return center_x, center_y
    print(f"未找到目标文字 '{target_text}'")
    return None

def preprocess_image(image_path):
    """
    预处理图片以提高 OCR 识别率
    :param image_path: 图片路径
    :return: 图片路径（直接返回原路径，因为不再保存新的截图）
    """
    return image_path  # 直接返回原路径

def match_and_click(template_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    使用 OpenCV 模板匹配检测目标并点击
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值
    """
    while True:
        adb_screenshot(SCREENSHOT_MAIN)
        time.sleep(1)
        screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {SCREENSHOT_MAIN} 或 {template_path}")
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
            dj(center_x, center_y)
            return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...") 

def wait_for_image(template_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    循环检测目标图片是否出现，不点击
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值
    :return: 是否检测到目标
    """
    while True:
        adb_screenshot(SCREENSHOT_MAIN)
        time.sleep(1)
        screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

        if screenshot is None or template is None:
            print(f"无法加载图片: {SCREENSHOT_MAIN} 或 {template_path}")
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
        time.sleep(1)

def match1_and_click_with_retry(template_path, SCREENSHOT_MAIN, event_template_path, threshold=0.8, click_once=False, wait_before_click=0):
    """
    使用 OpenCV 模板匹配检测目标并点击，点击后验证是否成功
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param event_template_path: 点击后验证的事件图片路径
    :param threshold: 匹配阈值
    :param click_once: 是否只点击一次
    :param wait_before_click: 点击前等待的时间（秒）
    """
    clicked_once = False
    while True:
        # 截取全屏并匹配目标
        bring_window_to_front("MuMu操作录制")
        minimize_window("官服")  # 最小化窗口
        pyautogui.screenshot(SCREENSHOT_MAIN)
        time.sleep(1)
        max_retries = 3
        retry_delay = 2  # 重试间隔时间（秒）
        for attempt in range(max_retries):
            # 尝试读取图像
            screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

            # 检查图片是否成功读取
            if screenshot is not None and template is not None:
                break
            else:
                print(f"第 {attempt + 1} 次尝试：无法读取图片: {SCREENSHOT_MAIN} 或 {template_path}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)

        # 确保模板和截图的通道一致
        if screenshot.shape[2] == 4:
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
        
        if event_template_path:
            event_screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
            event_template = cv2.imread(event_template_path, cv2.IMREAD_UNCHANGED)
            if event_screenshot is not None and event_template is not None:
                if event_screenshot.shape[2] == 4:
                    event_screenshot = cv2.cvtColor(event_screenshot, cv2.COLOR_BGRA2BGR)
                if event_template.shape[2] == 4:
                    event_template = cv2.cvtColor(event_template, cv2.COLOR_BGRA2BGR)
                event_result = cv2.matchTemplate(event_screenshot, event_template, cv2.TM_CCOEFF_NORMED)
                _, event_max_val, _, _ = cv2.minMaxLoc(event_result)
                if event_max_val >= threshold:
                    print(f"点击前事件图片已出现: {event_template_path}")
                    return True

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
            time.sleep(20)  # 等待点击效果生效

            # 验证点击是否成功
            pyautogui.screenshot(SCREENSHOT_MAIN)
            event_screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
            event_template = cv2.imread(event_template_path, cv2.IMREAD_UNCHANGED)

            if event_screenshot is None or event_template is None:
                print(f"无法加载事件图片: {SCREENSHOT_MAIN} 或 {event_template_path}")
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
        time.sleep(10)  # 等待一秒后再次尝试匹配

def match_and_click_with_retry(template_path, SCREENSHOT_MAIN, event_template_path, threshold=0.8, click_once=False, wait_before_click=0):
    """
    使用 OpenCV 模板匹配检测目标并点击，点击后验证是否成功
    :param template_path: 模板图片路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param event_template_path: 点击后验证的事件图片路径
    :param threshold: 匹配阈值
    :param click_once: 是否只点击一次
    :param wait_before_click: 点击前等待的时间（秒）
    """
    clicked_once = False
    while True:
        # 截取全屏并匹配目标
        adb_screenshot(SCREENSHOT_MAIN)
        time.sleep(1)
        max_retries = 4
        retry_delay = 5  # 重试间隔时间（秒）
        for attempt in range(max_retries):
            # 尝试读取图像
            screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

            # 检查图片是否成功读取
            if screenshot is not None and template is not None:
                break
            else:
                print(f"第 {attempt + 1} 次尝试：无法读取图片: {SCREENSHOT_MAIN} 或 {template_path}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)

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

            dj(center_x, center_y)
            clicked_once = True
            time.sleep(1)  # 等待点击效果生效

            # 验证点击是否成功
            if event_template_path:
                while True:
                    adb_screenshot(SCREENSHOT_MAIN)
                    event_screenshot = cv2.imread(SCREENSHOT_MAIN, cv2.IMREAD_UNCHANGED)
                    event_template = cv2.imread(event_template_path, cv2.IMREAD_UNCHANGED)

                    if event_screenshot is None or event_template is None:
                        print(f"无法加载事件图片: {SCREENSHOT_MAIN} 或 {event_template_path}")
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
                        dj(center_x, center_y)
                        time.sleep(1)  # 等待点击效果生效
            else:
                return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...")
time.sleep(1)

def detect_and_click_tg_and_s():
    """ 
    持续检测并点击 tg.png 和 s.png
    """
    print("开始循环检测并点击 'tg.png' 和 's.png'")
    while True:
        # 你可以在这里加点击或其它逻辑
        jq_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\tg.png", SCREENSHOT_THREAD, threshold=0.6)
        zcys_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\zcys.png", SCREENSHOT_THREAD, threshold=0.6)
        adb_screenshot(save_path=SCREENSHOT_THREAD)  # 使用全局常量路径
        if jq_coords:
            print("跳过剧情")
            dj(1183, 52)
            time.sleep(1)
            dj(796, 462)
        if zcys_coords:
            print("至纯源石")
            dj(640,100)
        time.sleep(5)  # 每秒检测一次
    


def Clear_levels(name):
    time.sleep(1)
    start_coords = (1245,661)
    ks1_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\ks1.png", SCREENSHOT_MAIN)
    if ks1_coords:
        dj(start_coords[0], start_coords[1])  # 修复：确保 ks1_coords 已赋值
        print("磨难模式启动！")
    else:
        print("还没有到磨难模式")


    # 第三步：全屏截图并匹配 s2.png
    adb_screenshot(SCREENSHOT_MAIN)  # 全屏截图
    start_coords = (1245,661)
    s2_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s2.png", SCREENSHOT_MAIN)  # 匹配 s2.png
    if s2_coords:
        print("吃个药药")
        dj(s2_coords[0], s2_coords[1])  
        time.sleep(2)  # 等待 1 秒
        dj(start_coords[0], start_coords[1])
    else:
        print("启动！")

    # 后续步骤：使用 OpenCV 模板匹配检测并点击，验证点击事件
    print("检测并点击 '助战干员'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\zz.png",
        SCREENSHOT_MAIN,
        r"C:\Users\38384\Pictures\Screenshots\jr.png"
    )

    dj(135,205)  # 使用第一步的点击坐标

    yh_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\jr.png", SCREENSHOT_MAIN, threshold=0.6)
    yh2_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\yh2.png", SCREENSHOT_MAIN, threshold=0.6)
    jr_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\jr.png", SCREENSHOT_MAIN, threshold=0.6)
    while True:
        adb_screenshot(SCREENSHOT_MAIN)
        if yh_coords:
            print("点击银灰")
            dj(yh_coords[0], yh_coords[1])
            break
        elif yh2_coords:
            print("点击银灰2")
            dj(yh2_coords[0], yh2_coords[1])
            break
        elif jr_coords:
            dj(jr_coords[0],jr_coords[1])  # 使用第一步的点击坐标
        else:
            print("银灰不在，继续")
            keyboard.Controller().press('0')  # 按下键 '0'
            keyboard.Controller().release('0')  # 松开键 '0'
    time.sleep(1)  # 等待 1 秒

    print("检测并点击 '招募助战'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\zm.png",
        SCREENSHOT_MAIN,
        None,  # 无需验证事件
        click_once=True  # 只点击一次
    )

    time.sleep(3)  # 等待 1 秒
    dj(1099, 505)  # 使用第一步的点击坐标
    print("点击坐标: (1099, 505)")

    # 第四步：全屏截图并匹配 s1.png
    adb_screenshot(SCREENSHOT_MAIN)  # 全屏截图
    s1_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s1.png", SCREENSHOT_MAIN)  # 匹配 s1.png
    if s1_coords:
        print(f"确认ban位")
        dj(s1_coords)  # 点击 s1.png 的位置
    else:
        print("下一步")

    
        # 第七步：检测并点击 "暂停"
    print("检测并点击 '部署干员'")
    bring_window_to_front("MuMu操作录制")  # 确保窗口在最前面
    while True:
        onebs_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\1bs.png", SCREENSHOT_MAIN)    
        if onebs_coords:
            match1_and_click_with_retry(
            r"C:\Users\38384\Pictures\Screenshots\bsgy.png",
            SCREENSHOT_MAIN,
            None,  # 无需验证事件
            click_once=True  # 只点击一次
            )
            break
    time.sleep(25)  # 等待 1 秒    
    minimize_window("官服")  # 最小化窗口
    minimize_window("MuMu操作录制")  # 最小化窗口    
    # 第五步：检测并点击 "1倍速"
    print("检测并点击 '1倍速'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\1bs.png",
        SCREENSHOT_MAIN,
        r"C:\Users\38384\Pictures\Screenshots\2bs.png"
    )

    # 第六步：等待 "2倍速" 出现
    print("等待 '2倍速' 出现")
    wait_for_image(r"C:\Users\38384\Pictures\Screenshots\2bs.png", SCREENSHOT_MAIN)

    # 第八步：检测并点击 "行动结束"
    print("检测并点击 '行动结束'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\xd.png",
        SCREENSHOT_MAIN,
        None,  # 最后一步无需验证事件
        click_once=True,  # 点击一次
        wait_before_click=2  # 点击前等待 2 秒
    )
    print(f"{name} 结束")
    return False

def process_stage(SCREENSHOT_MAIN, max_retries):
    """rightmost_entry
    处理游戏关卡流程的主函数
    :param SCREENSHOT_MAIN: 截图存储路径
    :param max_retries: 最大重试次数
    :return: True表示流程成功完成，False表示失败
    """
    # 关键坐标定义
    START_COORDS = (1245, 661)
    COMMON_TAP_POINTS = {
        'story': (977, 368),      # 剧情关卡坐标
        'confirm': (640, 360),    # 通用确认坐标
        'exercise': (1085, 500),  # 演习确认坐标
        'close': (208, 217)       # 关闭按钮坐标
    }
    
    # 图像模板路径配置
    TEMPLATE_PATHS = {
        'level': r"C:\Users\38384\Pictures\Screenshots\yx.png",
        'unplayed': r"C:\Users\38384\Pictures\Screenshots\ys.png",
        'sudden_attack': r"C:\Users\38384\Pictures\Screenshots\txms.png",
        'story_level': r"C:\Users\38384\Pictures\Screenshots\ksjq.png",
        'exercise_level': r"C:\Users\38384\Pictures\Screenshots\jzyx.png",
        'stone': r"C:\Users\38384\Pictures\Screenshots\ys1.png",
        'strategy': r"C:\Users\38384\Pictures\Screenshots\bsgy.png",
        'operation': r"C:\Users\38384\Pictures\Screenshots\xd.png"
    }

    for attempt in range(max_retries):
        try:
            # 图像匹配检测
            coords = get_xy(TEMPLATE_PATHS['level'], SCREENSHOT_MAIN, threshold=0.7)
            coords1 = get_xy(TEMPLATE_PATHS['unplayed'], SCREENSHOT_MAIN)
            txms_coords = get_xy(TEMPLATE_PATHS['sudden_attack'], SCREENSHOT_MAIN, threshold=0.7)
            coords2 = get_xy(TEMPLATE_PATHS['story_level'], SCREENSHOT_MAIN)
            coords3 = get_xy(TEMPLATE_PATHS['exercise_level'], SCREENSHOT_MAIN, threshold=0.7)
            coords4 = get_xy(TEMPLATE_PATHS['stone'], SCREENSHOT_MAIN, threshold=0.6)
            coords5 = get_xy(TEMPLATE_PATHS['operation'], SCREENSHOT_MAIN, threshold=0.7)


            # 普通关卡处理流程
            if coords:
                print("[流程] 检测到普通关卡")
                if coords1:
                    print("[状态] 未通关关卡")
                    time.sleep(0.5)
                    dj(*START_COORDS)
                    print("[操作] 进入普通关卡")
                    if not Clear_levels("普通关卡"):
                        return False
                elif txms_coords:
                    print(f"[切换] 突袭模式坐标：{txms_coords}")
                    dj(*txms_coords)
                    if coords1:
                        time.sleep(0.5)
                        dj(*START_COORDS)
                        print("[操作] 进入突袭关卡")
                        if not Clear_levels("突袭关卡"):
                            return False

                else:
                    print("[警告] 非常规关卡类型")

            # 剧情关卡处理流程
            if coords2:
                print("[流程] 检测到剧情关卡")
                dj(*COMMON_TAP_POINTS['story'])
                print("[操作] 进入剧情关卡")
                time.sleep(5)
                dj(*COMMON_TAP_POINTS['confirm'])
                time.sleep(20)
                dj(*COMMON_TAP_POINTS['confirm'])
                time.sleep(2)
                dj(640,100)
                return "特殊关卡"

            # 演习关卡处理流程
            if coords3:
                print("[流程] 检测到演习关卡")
                dj(*START_COORDS)
                time.sleep(1)
                dj(*COMMON_TAP_POINTS['exercise'])
                print("[操作] 进入演习关卡")
                match1_and_click_with_retry(
                    TEMPLATE_PATHS['strategy'],
                    SCREENSHOT_MAIN,
                    TEMPLATE_PATHS['operation']
                    )
                time.sleep(2)
                dj(*COMMON_TAP_POINTS['close'])
                return "特殊关卡"
            # 未匹配到任何有效关卡
            if attempt == max_retries - 1:
                print("[错误] 已达到最大重试次数")
                return True

            print(f"[重试] 第 {attempt+1} 次重试...")
            time.sleep(2)

        except Exception as e:
            print(f"[异常] 流程执行出错: {str(e)}")
            if attempt == max_retries - 1:
                return True
            time.sleep(2)

def main_process():
    """
    主流程逻辑
    """
    print("开始主流程...")

    # 检查ADB连接
    check_adb_connection()

    adb_screenshot(save_path=SCREENSHOT_MAIN)
    
    img = cv2.imread(SCREENSHOT_MAIN)
        
# 合并匹配规则：同时匹配 13-14 和 TR-15 格式
    pattern = r'^(\d+|[A-Za-z]{2,})(-[A-Za-z]{1,2})?-\d+$' # 前段允许数字/字母，后段必须数字
    
    # 执行OCR并过滤
    filtered = []
    result = ocr_engine.ocr(img, cls=True)

    for line in result:
        for line1 in line:
            if isinstance(line1, (list, tuple)) and len(line1) >= 2:
                boxes = line1[0]
                text = str(line1[1][0]).strip()
                confidence = line1[1][1]
                if re.match(pattern, text):
                    filtered.append(line1)
    # 按小到大排序文本
    filtered.sort(key=lambda x: x[0][0], reverse=True)

    while filtered:
        
        item = filtered[0]
        text = item[1][0]

        processed_texts.append(text)
        filtered = [item for item in filtered if item[1][0] not in processed_texts]

        new_img = adb_screenshot()

        new_results = ocr_engine.ocr(new_img)
        
        for item1 in new_results:

            item1.sort(key=lambda x: x[0][0], reverse=False)

            match = next((r for r in item1 if r[1][0] == text), None)
            if match is None:
                print(f"未找到与 {text} 匹配的bbox,跳过。")
                continue
            new_bbox = match[0]

            # 计算 x 坐标的平均值
            x_sum = sum(point[0] for point in new_bbox)
            x_center = x_sum / len(new_bbox)
            # 计算 y 坐标的平均值
            y_sum = sum(point[1] for point in new_bbox)
            y_center = y_sum / len(new_bbox)

            print(f"识别到文本: {text} (置信度: {confidence:.2f}) 坐标: ({x_center}, {y_center})")
            print(item1)
            dj(x_center, y_center)
            print(f"执行点击")
            
            result = process_stage(SCREENSHOT_MAIN, max_retries=2)
            if result == "特殊关卡":
                print(f"√ {text} 验证成功")
                time.sleep(2)
                continue
            elif result:
                print(f"√ {text} 验证成功")
                print("点击 '返回' 按钮")
                adb_back()
                time.sleep(2)
                continue
            else:
                print("再来一次！")
                # 重新获取坐标
                time.sleep(5)
                dj(x_center, y_center)
                process_stage(SCREENSHOT_MAIN, max_retries=2)
                continue

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QLineEdit, QPushButton, 
                             QLabel, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal

class AutoPushThread(QThread):
    """推图任务线程（避免界面卡顿）"""
    progress_signal = pyqtSignal(str)  # 状态更新信号

    def __init__(self, level_type, level_param):
        super().__init__()
        self.level_type = level_type  # 'main'或'side'
        self.level_param = level_param  # 主线章节号或插曲代号

    def run(self):
        self.progress_signal.emit("开始导航到目标关卡...")
        # 这里调用你的导航逻辑（需要你自行实现）
        # navigate_to_level(self.level_type, self.level_param)
        
        self.progress_signal.emit("启动推图流程...")
        # 这里调用你的推图主函数（示例调用）
        # process_stage(SCREENSHOT_MAIN, max_retries=2)
        
        self.progress_signal.emit("推图完成！")

class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.thread = None  # 保存线程引用

    def init_ui(self):
        self.setWindowTitle("明日方舟全自动推图")
        self.setGeometry(100, 100, 400, 200)

        # 中心容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 主线章节选择
        main_chapter_layout = QHBoxLayout()
        main_chapter_layout.addWidget(QLabel("主线章节："))
        self.main_combobox = QComboBox()
        self.main_combobox.addItems([f"{i}-X" for i in range(0, 15)])  # 0-14章
        main_chapter_layout.addWidget(self.main_combobox)
        main_layout.addLayout(main_chapter_layout)

        # 插曲别传输入
        side_story_layout = QHBoxLayout()
        side_story_layout.addWidget(QLabel("插曲代号："))
        self.side_input = QLineEdit()
        self.side_input.setPlaceholderText("例如：TR-15 / CB-EX8")
        side_story_layout.addWidget(self.side_input)
        main_layout.addLayout(side_story_layout)

        # 启动按钮
        self.start_btn = QPushButton("启动推图")
        self.start_btn.clicked.connect(self.start_push)
        main_layout.addWidget(self.start_btn)

        # 状态提示
        self.status_label = QLabel("状态：等待启动")
        main_layout.addWidget(self.status_label)

    def start_push(self):
        """启动按钮点击处理"""
        main_chapter = self.main_combobox.currentText()
        side_code = self.side_input.text().strip()

        # 验证输入
        if not main_chapter and not side_code:
            QMessageBox.warning(self, "错误", "请选择主线章节或输入插曲代号")
            return

        # 确定关卡类型
        level_type = 'main' if main_chapter else 'side'
        level_param = main_chapter if level_type == 'main' else side_code

        # 启动线程
        self.thread = AutoPushThread(level_type, level_param)
        self.thread.progress_signal.connect(self.update_status)
        self.thread.finished.connect(lambda: self.start_btn.setEnabled(True))
        self.start_btn.setEnabled(False)  # 禁用按钮防止重复点击
        self.thread.start()

    def update_status(self, msg):
        """更新状态提示"""
        self.status_label.setText(f"状态：{msg}")

def run_gui():
    """启动图形界面"""
    app = QApplication(sys.argv)
    window = MainInterface()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # 启动独立线程进行循环检测
    detection_thread = threading.Thread(target=detect_and_click_tg_and_s, daemon=True)
    detection_thread.start()

    # 主流程循环
    while True:
        print("开始新一轮主流程...")
        main_process()
        print("主流程完成，等待 5 秒后重新开始...")
        time.sleep(5)  # 等待 5 秒后重新开始


