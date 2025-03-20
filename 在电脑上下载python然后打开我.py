import pyautogui
import time
from pywinauto import Application, Desktop
import win32api
import win32con
import win32gui
import pyperclip  # 导入 pyperclip 模块


def switch_to_english_input():
    """切换输入法为英文（美式键盘）"""
    HKL_ENGLISH = 0x04090409
    try:
        hwnd = win32gui.GetForegroundWindow()
        win32api.SendMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, HKL_ENGLISH)
    except Exception as e:
        print(f"切换输入法失败: {e}")
    finally:
        time.sleep(2)  # 增加延迟确保切换完成


def open_notepad_and_paste(text_to_paste):
    try:
        # 打开记事本
        pyautogui.hotkey("win", "r")
        time.sleep(2)
        pyautogui.write("notepad")
        time.sleep(4)
        pyautogui.press("enter")
        time.sleep(4)
        pyautogui.press("enter")
        time.sleep(4)  # 延长等待时间确保记事本启动
    except Exception as e:
        print(f"打开记事本失败: {e}")
        return

    # 使用更通用的窗口匹配方式
    try:
        # 尝试连接到中文系统的记事本窗口
        app = Application().connect(title_re=".*无标题.*", class_name="Notepad")
        notepad_window = app.window(title_re=".*无标题.*")
        notepad_window.set_focus()
    except Exception as e:
        try:
            # 尝试连接到英文系统的记事本窗口
            app = Application().connect(title_re=".*Untitled.*", class_name="Notepad")
            notepad_window = app.window(title_re=".*Untitled.*")
            notepad_window.set_focus()
        except Exception as e:
            print(f"窗口连接失败: {e}")
            # 手动点击记事本窗口中间位置强制激活
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(x=screen_width // 2, y=screen_height // 2)

    # 切换输入法
    try:
        switch_to_english_input()
    except Exception as e:
        print(f"切换输入法失败: {e}")

    # 将文本复制到剪贴板
    pyperclip.copy(text_to_paste)

    # 粘贴文本
    try:
        pyautogui.hotkey('ctrl', 'v')  # 使用快捷键粘贴
    except Exception as e:
        print(f"粘贴文本失败: {e}")

    time.sleep(4)
    pyautogui.press("enter")


if __name__ == "__main__":
    try:
        text_to_paste = "君に限ことではない" # 在这里输入你想要粘贴的文本
        open_notepad_and_paste(text_to_paste)  # 调用修改后的函数
    except Exception as e:
        print(f"主函数执行过程中发生错误: {e}")
    finally:
        input("按 Enter 键退出...")
