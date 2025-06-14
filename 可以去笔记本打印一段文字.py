import win32gui
import win32api
import win32con
import time
import pyautogui
from pywinauto.application import Application
import subprocess


def switch_to_english_input(max_retries=3):
    """通过模拟按键切换系统输入法，按下 Shift 键切换"""
    retries = 0

    while retries < max_retries:
        try:
            # 模拟按下 Shift 键切换输入法
            pyautogui.press("shift")
            time.sleep(1)  # 增加延迟确保切换完成

            # 检查是否切换成功
            if is_english_input_active():
                print("系统输入法切换成功")
                return
            else:
                print(f"系统输入法切换失败，重试中...（第 {retries + 1} 次）")
        except Exception as e:
            print(f"切换系统输入法时发生错误: {e}")

        retries += 1

    print("多次尝试后系统输入法仍未切换为英文，请手动切换")


def is_english_input_active():
    """检查当前输入法是否为英文"""
    try:
        current_hkl = win32api.GetKeyboardLayout(0)  # 获取当前线程的输入法句柄
        return current_hkl == 0x04090409  # 检查是否为英文（美式键盘）
    except Exception as e:
        print(f"检查输入法时发生错误: {e}")
        return False


def switch_to_english_halfwidth():
    """通过模拟按键切换到英文半角模式"""
    try:
        # 模拟按下 Shift 键切换到英文半角模式
        pyautogui.press("shift")
        time.sleep(1)  # 增加延迟确保切换完成
        print("已尝试切换到英文半角模式")
    except Exception as e:
        print(f"切换到英文半角模式时发生错误: {e}")


def open_notepad_and_type():
    try:
        # 打开记事本
        pyautogui.hotkey("win", "r")
        time.sleep(2)
        pyautogui.write("notepad")
        time.sleep(2)
        pyautogui.press("enter")
        pyautogui.press("enter")
        time.sleep(2)  # 延长等待时间确保记事本启动

        # 尝试连接到记事本窗口
        for _ in range(4):  # 最多尝试4次
            try:
                app = Application().connect(title_re=".*Notepad.*", class_name="Notepad")
                app.window().set_focus()
                break
            except Exception as e:
                print(f"尝试连接失败: {e}")
                time.sleep(1)
        else:
            print("多次尝试后仍无法连接到记事本窗口")
            screen_width, screen_height = pyautogui.size()
            click_x, click_y = screen_width // 2, screen_height // 2
            pyautogui.click(x=click_x, y=click_y)

        # 切换到英文半角模式
        print("切换到英文半角模式")
        switch_to_english_halfwidth()

        # 显式降低输入速度并输入完整字符串
        print("开始输入文字")
        pyautogui.write("423", interval=0.1)
    except Exception as e:
        print(f"打开记事本并输入文本时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        open_notepad_and_type()
    except Exception as e:
        print(f"主程序执行时发生错误: {e}")
    subprocess.run(["pause"], shell=True)
    input("按 Enter 键退出...")