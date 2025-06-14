# rules.py
import time
import pyautogui as p

def blue_rule(scaled_coords, keys, get_running_state,_):
    """蓝色规则：B通道>200时点按"""
    while True:
        if not get_running_state():
            time.sleep(0.1)
            continue
            
        for key in keys:
            x, y = scaled_coords[key]
            try:
                if p.pixel(x, y)[2] > 200:  # B通道检测
                    p.press(key)
                    time.sleep(0.02)  # 防抖延迟
            except:
                continue

def green_rule(scaled_coords, keys, get_running_state, update_key_state):
    """绿色规则处理"""
    current_key = None
    while True:
        if not get_running_state():
            time.sleep(0.1)
            continue
            
        best_key = None
        max_g_value = 0

        for key in keys:
            x, y = scaled_coords[key]
            try:
                g_value = p.pixel(x, y)[1]
            except:
                continue
                
            if g_value > 200:  # 高优先级绿色
                if not best_key or g_value > max_g_value:
                    best_key = key
                    max_g_value = g_value
            elif g_value > 120 and not best_key:  # 低优先级绿色
                best_key = key
                max_g_value = g_value

        # 安全更新按键状态
        update_key_state(current_key, best_key)
        current_key = best_key
        time.sleep(0.01)

def red_rule(scaled_coords, keys, get_running_state,_):
    """红色规则：R通道>200时滑动"""
    while True:
        if not get_running_state():
            time.sleep(0.1)
            continue
            
        for key in keys:
            x, y = scaled_coords[key]
            try:
                if p.pixel(x, y)[0] > 200:  # R通道检测
                    p.moveTo(x, y)
                    p.dragTo(x, y-100, duration=0.15, button='left')
                    break  # 每次只处理一个滑动
            except:
                continue