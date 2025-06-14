import pyautogui
import time
import subprocess
import pyperclip
import win32gui
import win32con
from PIL import Image
import cv2
import numpy as np

def close_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print(f"已关闭窗口 (句柄: {hwnd})")
        return True
    except Exception as e:
        print(f"关闭失败 (句柄: {hwnd}): {str(e)}")
        return False

def screenshot_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"未找到窗口：{window_title}")
        return None
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    screenshot = pyautogui.screenshot()
    crop = screenshot.crop((left, top, right, bottom))
    return cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)

def routine(template_path, target_name, threshold=0.85):
    """
    基于pyautogui截图的图像匹配点击
    """
    hwnd = win32gui.FindWindow(None, "QQ")
    if not hwnd:
        print(f"错误：未找到{target_name}窗口")
        return False

    screenshot = screenshot_window("QQ")
    if screenshot is None or screenshot.size == 0:
        print(f"错误：{target_name}截图失败")
        return False

    template = cv2.imread(template_path)
    if template is None:
        print(f"错误：模板图片{template_path}不存在")
        return False

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        window_left, window_top, _, _ = win32gui.GetWindowRect(hwnd)
        click_x = window_left + max_loc[0] + w // 2
        click_y = window_top + max_loc[1] + h // 2
        pyautogui.click(click_x, click_y)
        print(f"成功点击{target_name}（相似度：{max_val:.2f}）")
        return True
    else:
        print(f"{target_name}匹配失败（相似度：{max_val:.2f} < {threshold}）")
        return False

# 1. 打开QQ群快捷方式 (替换为你的快捷方式路径)
shortcut_path = r"C:\Users\38384\Desktop\QQ群.lnk"
subprocess.Popen(f'cmd /c start "" "{shortcut_path}"', shell=True)


while not (
    routine(r"C:\Users\38384\Pictures\Screenshots\fxx.png", "发消息", threshold=0.6)
    and
    routine(r"C:\Users\38384\Pictures\Screenshots\fs.png", "发消息", threshold=0.6)
):
    time.sleep(0.5)

pyperclip.copy("买甜点")
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.5)
pyautogui.hotkey('ctrl', 'enter')  # QQ默认发送快捷键
print("消息已发送!")



# 4. 关闭QQ主窗口
close_window("QQ")
close_window("QQ群")