from pywinauto import Desktop

def find_windows_by_title(target_title):
    # 存储匹配窗口句柄的列表
    matching_handles = []
    
    # 遍历所有顶层窗口
    for window in Desktop(backend="win32").windows():
        # 获取窗口标题
        window_title = window.texts()[0] if window.texts() else ""
        # 比较窗口标题
        if window_title == target_title:
            # 添加窗口句柄到列表中
            matching_handles.append(window.handle)
    
    # 返回匹配窗口句柄列表
    return matching_handles

# 示例用法
if __name__ == "__main__":
    target_window_title = "MuMu模拟器12"  # 替换为目标窗口的实际标题
    hwnd_list = find_windows_by_title(target_window_title)
    if hwnd_list:
        print(f"找到 {len(hwnd_list)} 个窗口，句柄为：{hwnd_list}")
    else:
        print("未找到匹配的窗口")


