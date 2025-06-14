import ctypes
import os
import sys
import time
import cv2
import json  # 新增：用于读取JSON文件
import numpy as np
import pyautogui
import pyperclip
from pywinauto import Application
# 新增：从account_manager导入必要变量和函数
from account_manager import data_dir, xor_decrypt_from_base64  # 确保account_manager.py在当前目录或Python路径中

def start_application(app_path):
    try:
        Application().start(app_path)
    except Exception as e:
        raise RuntimeError(f"启动应用失败：{e}")

def routine(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy(img_model_path, threshold=0.6)  # 将阈值从默认的 0.7 降低到 0.6
        if avg:
            print(f'正在点击 {name}')
            auto_click(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
        time.sleep(1)

def routine1(img_model_path, name, timeout=None):
    start_time = time.time()
    while True:
        avg = get_xy1(img_model_path, threshold=0.6)  # 将阈值从默认的 0.7 降低到 0.6
        if avg:
            print(f'正在点击 {name}')
            auto_click(avg)
            return True
        if timeout and time.time() - start_time > timeout:
            return False
        time.sleep(1)

def get_xy1(img_model_path, threshold=0.7):
    screenshot_dir = "./screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    
    img = cv_imread(screenshot_path)
    img_terminal = cv2.imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)

    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

def get_xy(img_model_path, threshold=0.7):
    screenshot_dir = "./screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    pyautogui.screenshot().save(screenshot_path)
    
    img = cv_imread(screenshot_path)
    img_terminal = cv2.imread(img_model_path)
    if img is None or img_terminal is None:
        return None

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(img_terminal, cv2.COLOR_BGR2GRAY)

    
    h, w = template_gray.shape
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    return (max_loc[0] + w//2, max_loc[1] + h//2) if max_val >= threshold else None

def auto_click(var_avg):
    if var_avg:
        pyautogui.click(var_avg[0], var_avg[1], duration=0)

def cv_imread(file_path):
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

def load_accounts_from_manager():
    """从account_manager的账号目录读取并解密所有账号"""
    accounts = []
    # 遍历account_manager的账号存储目录下的所有JSON文件
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 提取加密的凭证（格式：账号名,密码）
                encrypted_creds = data.get("encrypted_credentials")
                if not encrypted_creds:
                    continue  # 跳过无密码的账号
                
                # 解密凭证
                decrypted_creds = xor_decrypt_from_base64(encrypted_creds)
                account_name, account_pass = decrypted_creds.split(",", 1)  # 分割为账号名和密码
                
                # 构造账号信息（可根据需要添加其他字段如account_id）
                accounts.append({
                    "id": data["account_name"],  # 从JSON获取账号ID（如UID）
                    "name": account_name,      # 解密后的账号名
                    "code": account_pass       # 解密后的密码
                })
    return accounts

def switch_account(main_operation_callback):  # 新增回调参数（默认None）
    """切换账号逻辑"""
    
    try:

        # 从account_manager的账号目录加载并解密所有账号
        accounts = load_accounts_from_manager()

        for account in accounts:
            print(f"正在处理账号：{account['name']}(ID:{account['id']})")
            start_application(r"D:\miHoYo Launcher\games\Star Rail Game\StarRail - 快捷方式.lnk")
            # 执行账号切换前置操作（登出、退出等）
            routine(r"C:\Users\38384\Pictures\Screenshots\dc.png", "登出")
            routine(r"C:\Users\38384\Pictures\Screenshots\tc.png", "退出")
            routine(r"C:\Users\38384\Pictures\Screenshots\drqtyxzh.png", "登求其他账号")
            
            # 输入当前账号信息（使用解密后的name和code）
            routine(r"C:\Users\38384\Pictures\Screenshots\zhmm.png", "账号密码")
            pyperclip.copy(account['name'])  # 改为使用解密后的账号名
            pyautogui.hotkey('ctrl', 'v')
            
            routine(r"C:\Users\38384\Pictures\Screenshots\srmm.png", "输入密码")
            pyperclip.copy(account['code'])  # 使用解密后的密码
            pyautogui.hotkey('ctrl', 'v')
            
            # 完成登录
            routine(r"C:\Users\38384\Pictures\Screenshots\yuan.png", "我超,⚪！")
            routine(r"C:\Users\38384\Pictures\Screenshots\jryx.png", "进入游戏")
            
                
            # 每个账号切换完成后调用主操作
            main_operation_callback()
    except Exception as e:
            print(f"账号切换出错: {str(e)}")

