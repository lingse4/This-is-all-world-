import win32gui
import win32api
import win32con
import time
import pyautogui
from pywinauto.application import Application


def switch_to_english_input():
    """切换输入法为英文（美式键盘）"""
    HKL_ENGLISH = 0x04090409
    hwnd = win32gui.GetForegroundWindow()
    try:
        result = win32api.SendMessage(
            hwnd,
            win32con.WM_INPUTLANGCHANGEREQUEST,
            0,
            HKL_ENGLISH
        )
        if result == 0:
            print("输入法切换成功")
        else:
            print("输入法切换失败")
    except Exception as e:
        print(f"输入法切换时发生错误: {e}")
    time.sleep(1)  # 增加延迟确保切换完成


def is_english_input_active():
    """检查当前输入法是否为英文"""
    hwnd = win32gui.GetForegroundWindow()
    try:
        current_hkl = win32api.SendMessage(hwnd, win32con.WM_GETCURRENTINPUTLANGUAGE, 0, 0)
        return current_hkl == 0x04090409
    except Exception as e:
        print(f"检查输入法时发生错误: {e}")
        return False


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

        # 切换输入法
        switch_to_english_input()
        if not is_english_input_active():
            print("输入法未切换为英文，请手动切换")
            return

        # 显式降低输入速度并输入完整字符串
        pyautogui.write("𰻝𰻝面", interval=0.1)
    except Exception as e:
        print(f"打开记事本并输入文本时发生错误: {e}")


if __name__ == "__main__":
    try:
        open_notepad_and_type()
    except Exception as e:
        print(f"主程序执行时发生错误: {e}")
    subprocess.run(["pause"], shell=True)
    input("按 Enter 键退出...")