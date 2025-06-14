from pynput import mouse, keyboard  # 新增：导入键盘监听模块
from pynput.keyboard import Key    # 新增：用于识别功能键
import time
from pathlib import Path
import pygetwindow as gw  # 新增：用于获取窗口信息（需安装：pip install pygetwindow）

# 新增：模拟器配置（根据实际情况修改）
EMU_WINDOW_TITLE = "官服"  # 模拟器窗口标题（需匹配实际窗口名称）
EMU_RESOLUTION = (1280,720)   # 模拟器内部分辨率（如1920x1080）

# 桌面路径（Windows通用）
DESKTOP_PATH = Path.home() / "Desktop" / "抹茶巴菲"
RECORD_FILE = DESKTOP_PATH / "mouse_operations.txt"

# 记录变量初始化（新增last_time记录上一次事件时间）
start_time = None
last_time = None  # 新增：用于计算时间间隔
record = []
recording = True  # 新增：录制状态标志

# 新增：获取模拟器窗口信息函数
def get_emu_window_info():
    try:
        emu_window = gw.getWindowsWithTitle(EMU_WINDOW_TITLE)[0]
        # 窗口在屏幕上的位置（左上角坐标）和尺寸
        return {
            "x": emu_window.left*(2560/1280),    # 窗口左边缘x坐标
            "y": emu_window.top*(1600/720),     # 窗口上边缘y坐标
            "width": emu_window.width,  # 窗口宽度（含边框）
            "height": emu_window.height  # 窗口高度（含标题栏）
        }
     
    except IndexError:
        raise RuntimeError(f"未找到标题为 '{EMU_WINDOW_TITLE}' 的模拟器窗口")

# 新增：坐标转换函数（电脑屏幕坐标 → 模拟器内部坐标）
def screen_to_emu_coords(screen_x, screen_y):
    window_info = get_emu_window_info()
    # 转换公式（按比例映射到模拟器分辨率）
    print(f"窗口信息：{window_info}")  # 调试输出窗口信息
    print(f"屏幕坐标：({screen_x}, {screen_y})")  # 调试输出屏幕坐标
    emu_x = int(screen_x - window_info["x"])
    emu_y = int(740-(screen_y - window_info["y"]))
    print(f"转换后坐标：({emu_x}, {emu_y})")  # 调试输出转换后的坐标
    return emu_x, emu_y

# 新增：拖动状态标记（在全局变量初始化部分添加）
is_dragging = False  # 初始未拖动

def on_click(x, y, button, pressed):
    global start_time, last_time, is_dragging  # 新增is_first_event
    if not start_time:
        start_time = time.time()
        last_time = start_time  # 初始化首次时间

    current_time = time.time()
    interval = int((current_time - last_time) * 1000)
    last_time = current_time  # 更新上次时间

    is_dragging = pressed  # 按下时为True，抬起时为False
    emu_x, emu_y = screen_to_emu_coords(x, y)

    if pressed:
        record.append(f"w {interval}\nc\nd 0 {emu_y} {emu_x} 50\nc")  # 正常添加w间隔
    else:
        record.append(f"w {interval}\nc\nu 0\nc")  # 正常添加w间隔

def on_move(x, y):
    global last_time, is_dragging  # 新增is_dragging
    if not start_time or not is_dragging:  # 未开始录制 或 未处于拖动状态时跳过
        return
    
    # 计算与上一次事件的时间间隔（毫秒级）
    current_time = time.time()
    interval = int((current_time - last_time) * 1000)
    last_time = current_time  # 更新上次时间

    # 修改：转换为模拟器坐标
    emu_x, emu_y = screen_to_emu_coords(x, y)
    record.append(f"w {interval}\nc\nm 0 {emu_y} {emu_x} 50\nc")  # 使用模拟器坐标

# 新增：键盘监听回调（按F1停止录制）
def on_press(key):
    global recording
    if key == Key.f1:  # 设置F1键为停止键
        recording = False
        print("检测到F1键，停止录制...")
        return False  # 返回False会停止键盘监听

def start_recording():
    global recording  # 新增：声明使用全局变量
    print("开始录制鼠标操作（按F1键或Ctrl+C停止）...")  # 更新提示信息
    
    # 同时启动鼠标和键盘监听
    mouse_listener = mouse.Listener(
        on_click=on_click,
        on_move=on_move)
    keyboard_listener = keyboard.Listener(
        on_press=on_press)
    
    # 启动监听器
    mouse_listener.start()
    keyboard_listener.start()
    
    # 等待录制停止（添加异常处理）
    while recording:
        try:
            time.sleep(1)  # 降低CPU占用
        except KeyboardInterrupt:  # 捕获Ctrl+C中断
            print("检测到Ctrl+C，停止录制...")
            recording = False  # 触发退出循环
    
    # 停止监听器（原有逻辑不变）
    mouse_listener.stop()
    keyboard_listener.stop()
    
    # 保存记录（原有逻辑不变）
    if record:
        record[-1] = record[-1].rsplit("\n", 1)[0]
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(record))
        f.write("\n" + "c")
    print(f"操作已保存到：{RECORD_FILE}")

if __name__ == "__main__":
    start_recording()