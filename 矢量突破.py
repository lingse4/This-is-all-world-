# -------------------- 1. 初始化ADB连接 --------------------
import os
import subprocess
import time
import cv2
import numpy as np
import pygetwindow as gw
import pyautogui

SCREENSHOT_DIR = r"C:\Users\38384\Pictures\Screenshots"
SCREENSHOT_MAIN = os.path.join(SCREENSHOT_DIR, "main_screenshot.png")

def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16384"  # 指定目标设备
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
    device_serial = "127.0.0.1:16384"
    
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

# -------------------- 5. ADB点击函数 --------------------

def adb_tap(x, y):
    """使用ADB命令在指定坐标点击,修复重复执行和编码问题"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16384"  # 指定目标设备
    
    # 构建完整的 ADB 命令
    command = f'"{adb_path}" -s {device_serial} shell input tap {x} {y}'
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",  # 强制使用 UTF-8 解码
            errors="ignore",    # 忽略无法解码的字符
            check=True          # 检查命令执行状态，失败时抛出异常
        )
        print(f"ADB点击完成: ({x}, {y})")
    except subprocess.CalledProcessError as e:
        print(f"ADB点击失败,退出码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
    except Exception as e:
        print(f"ADB未知异常: {str(e)}")

def cv_imread(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在！")
        return None
    try:
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None
    
def get_xy(img_model_path, SCREENSHOT_MAIN, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param SCREENSHOT_MAIN: 截图保存路径
    :param threshold: 匹配阈值，默认为0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果没有匹配则返回None
    """
    while True:
        screenshot_dir = "./Pictures/Screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        adb_screenshot(SCREENSHOT_MAIN)
        time.sleep(1)  # 等待截图保存完成
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
                        adb_tap(center_x, center_y)
                        time.sleep(1)  # 等待点击效果生效
            else:
                return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...")
time.sleep(1)

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

            adb_tap(center_x, center_y)
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
                        adb_tap(center_x, center_y)
                        time.sleep(1)  # 等待点击效果生效
            else:
                return True
        else:
            print(f"未匹配到目标: {template_path}，继续检测...")
time.sleep(1)


while True:
    # 检查ADB连接
    check_adb_connection()
    
    # 截图并保存
    adb_screenshot(SCREENSHOT_MAIN)
    
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\sltp1.png",
        SCREENSHOT_MAIN,
        None,  # 无需验证事件
        )   
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\sltp2.png",
        SCREENSHOT_MAIN,
        None,  # 无需验证事件
        )  

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
    minimize_window("b服")  # 最小化窗口
    minimize_window("MuMu操作录制")  # 最小化窗口  

    print("检测并点击 '1倍速'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\1bs.png",
        SCREENSHOT_MAIN,
        r"C:\Users\38384\Pictures\Screenshots\2bs.png"
    )

    match_and_click_with_retry(
    r"C:\Users\38384\Pictures\Screenshots\sltp31.png",
    SCREENSHOT_MAIN,
    r"C:\Users\38384\Pictures\Screenshots\sltp1.png",  # 无需验证事件
    )  
