
import os
import subprocess

import cv2
import numpy as np

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
        print("截图保存成功: {save_path}")
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
    
adb_tap(1085, 684)  # 示例点击坐标