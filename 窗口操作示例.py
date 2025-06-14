import time
import pygetwindow as gw

def bring_window_to_front(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.activate()
        print(f"Window '{window_title}' brought to front.")
    except IndexError:
        print(f"No window found with title: {window_title}")

def minimize_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.minimize()
        print(f"Window '{window_title}' minimized.")
    except IndexError:
        print(f"No window found with title: {window_title}")

# Example usage:
if __name__ == "__main__":
    window_title = "MuMu操作录制"  # 窗口标题
    time.sleep(2)  # 等待2秒钟
    bring_window_to_front(window_title)
    bring_window_to_front(window_title)
    # Uncomment the line below if you want to minimize the window instead
    # minimize_window(window_title)


