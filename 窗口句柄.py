from pywinauto import Desktop

def find_window_by_title(target_title):
    # 遍历所有顶层窗口
    for window in Desktop(backend="win32").windows():
        # 获取窗口标题
        window_title = window.texts()[0] if window.texts() else ""
        # 比较窗口标题
        if window_title == target_title:
            # 返回窗口句柄
            return window.handle
    # 如果没有找到匹配的窗口，返回 None
    return None

# 示例用法
if __name__ == "__main__":
    target_window_title = "MuMu模拟器12"  # 替换为目标窗口的实际标题
    hwnd = find_window_by_title(target_window_title)
    if hwnd:
        print(f"找到窗口，句柄为：{hwnd}")
    else:
        print("未找到匹配的窗口")