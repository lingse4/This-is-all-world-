import cv2
import subprocess
import numpy as np
from paddleocr import PaddleOCR

# -------------------- 1. 初始化ADB连接 --------------------
def check_adb_connection():
    """检查ADB设备是否已连接"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16480"  # 指定目标设备
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接！请确认设备 {device_serial} 已开启USB调试模式")

# -------------------- 2. ADB截图函数 --------------------
def adb_screenshot(save_path="screen.png"):
    """截取模拟器屏幕并返回OpenCV图像"""
    adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
    device_serial = "127.0.0.1:16480"  # 指定目标设备
    subprocess.run(f"{adb_path} -s {device_serial} shell screencap -p /sdcard/screen.png", shell=True, check=True)
    subprocess.run(f"{adb_path} -s {device_serial} pull /sdcard/screen.png {save_path}", shell=True, check=True)
    
    # 读取图像
    img = cv2.imread(save_path, cv2.IMREAD_GRAYSCALE)  # 读取为灰度图
    # 自动检测背景颜色并反转
    mean_pixel = np.mean(img)
    if mean_pixel > 127:  # 如果背景是白色
        img = cv2.bitwise_not(img)  # 反转为黑背景白字
    cv2.imwrite(save_path, img)  # 保存处理后的图像
    return save_path  # 返回图像路径

# -------------------- 3. 主程序 --------------------
if __name__ == "__main__":
    # 初始化OCR（使用默认字符集）
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="en",  # 使用英文模型
        show_log=False
    )
    
    # 检查ADB连接
    check_adb_connection()
    
    # 截取屏幕
    screen = adb_screenshot()
    
    # OCR识别
    result = ocr.ocr(screen, cls=True)
    
    # 提取并打印所有识别结果
    for line in result:
        if line:
            # 打印检测框坐标
            print(f"检测框坐标: {line[0]}")
            
            # 提取文本和置信度
            text, confidence = line[1]  # 解包元组，分别获取文本和置信度
            if isinstance(confidence, (float, int)):  # 确保置信度是数值类型
                print(f"识别到内容: {text} (置信度: {confidence:.2f})")
            else:
                print(f"识别到内容: {text} (置信度: {confidence})")  # 如果置信度不是数值，直接打印

    # 假设 img 是原始图像
    img = cv2.imread(screen)
    box = [[1055.0, 392.0], [1113.0, 392.0], [1113.0, 417.0], [1055.0, 417.0]]
    box = np.array(box, dtype=np.int32)
    cv2.polylines(img, [box], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.imshow("Detected Box", img)
    cv2.waitKey(0)