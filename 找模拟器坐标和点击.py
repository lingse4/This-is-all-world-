import os
import subprocess
import cv2
import numpy as np
import pyautogui
import time

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

def cv_imread(file_path):
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在！")
        return None
    try:
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

def get_xy(img_model_path, threshold=0.8):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path: 用来检测的模板图片的路径
    :param threshold: 匹配阈值，默认为 0.8
    :return: 以元组形式返回检测到的区域的中心坐标，如果未匹配则返回 None
    """
    # 将屏幕截图保存
    screenshot_path = adb_screenshot("./Pictures/Screenshots/screenshot.png")
    # 载入截图
    img = cv2.imread("./Pictures/Screenshots/screenshot.png")
    # 载入模板
    img_terminal = cv2.imread(img_model_path)
    if img is None or img_terminal is None:
        print("无法加载截图或模板图片")
        return None

    # 获取模板的宽度和高度
    height, width, channel = img_terminal.shape
    # 进行模板匹配
    result = cv2.matchTemplate(img, img_terminal, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 检查匹配值是否达到阈值
    if max_val >= threshold:
        # 解析出匹配区域的左上角坐标
        upper_left = max_loc
        # 计算匹配区域右下角的坐标
        lower_right = (upper_left[0] + width, upper_left[1] + height)
        # 计算中心区域的坐标并且返回
        avg = (int((upper_left[0] + lower_right[0]) / 2), int((upper_left[1] + lower_right[1]) / 2))
        return avg
    else:
        print(f"匹配值 {max_val} 未达到阈值 {threshold}")
        return None

def auto_click(var_avg):
    """
    接受一个元组参数，自动点击
    :param var_avg: 坐标范围
    :return: None
    """
    if var_avg:
        adb_tap(var_avg[0], var_avg[1], button='left')
        time.sleep(2)
    else:
        print("未检测到目标，无法点击")

def routine(img_model_path, name, threshold=0.8):
    while True:
        avg = get_xy(img_model_path, threshold)
        if avg:
            print(f'正在点击 {name}，坐标：{avg}')
            adb_tap(avg[0], avg[1])
            return avg
        else:
            print(f"未检测到 {name}，继续检测...")
            time.sleep(1)

#adb_tap(1085,500)
avg = routine(r"C:\Users\38384\Pictures\Screenshots\cs.png", "开始剧情", threshold=0.8)
print(f"点击完成,坐标：{avg}")