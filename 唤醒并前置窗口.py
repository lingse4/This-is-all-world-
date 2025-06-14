import time
import pygetwindow as gw

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

# Example usage:
if __name__ == "__main__":
    window_title = "MuMu操作录制"  # 窗口标题
    time.sleep(2)  # 等待2秒钟
    bring_window_to_front(window_title)

    # Uncomment the line below if you want to minimize the window instead
    # minimize_window(window_title)


