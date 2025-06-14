import pygetwindow as gw
import pyautogui

def get_genshin_impact_position(window_title='崩坏：星穹铁道'):
    # 查找所有窗口标题中包含特定字符串的窗口
    windows = gw.getWindowsWithTitle(window_title)
    
    if not windows:
        print(f"没有找到标题包含 '{window_title}' 的窗口")
        return None
    
    # 假设第一个匹配的窗口就是我们要找的目标窗口
    window = windows[0]
    
    # 获取窗口的位置信息 (left, top, width, height)
    left, top, width, height = window.left, window.top, window.width, window.height
    
    # 返回窗口左上角的绝对坐标
    return (left, top, width, height)

# 使用函数获取《崩坏：星穹铁道》窗口的位置
position = get_genshin_impact_position('崩坏：星穹铁道')
if position:
    print(f"《崩坏：星穹铁道》窗口的绝对位置: 左上角 ({position[0]}, {position[1]}), 宽度 {position[2]}, 高度 {position[3]})")
else:
    print("无法找到《崩坏：星穹铁道》窗口")


