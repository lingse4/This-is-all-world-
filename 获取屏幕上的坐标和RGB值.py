import pyautogui as p
from PIL import ImageGrab
import time

def get_mouse_position_and_rgb():
    """
    获取鼠标当前位置的坐标和屏幕上该位置的 RGB 值
    """
    # 获取鼠标当前位置
    x, y = p.position()
    # 获取屏幕上该位置的 RGB 值
    screenshot = ImageGrab.grab()
    rgb = screenshot.getpixel((x, y))
    print(f"鼠标当前位置：({x}, {y})，RGB 值：{rgb}")
    return x, y, rgb

# 主程序
if __name__ == "__main__":
    print("请将鼠标移动到目标位置，2 秒后获取坐标和 RGB 值...")
    time.sleep(2)  # 等待 2 秒
    get_mouse_position_and_rgb() 