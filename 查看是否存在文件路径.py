# -*- coding: utf-8 -*-
import os

# 请先确认以下路径是否与你的实际路径完全一致
exe_path = r"D:\XUNLEI\March7thAssistant_v2024.12.18_full\March7thAssistant_v2024.12.18_full\March7th Launcher.exe"
image_path = r"C:\Users\38384\Desktop\抹茶塔菲.py\崩铁运行.png"

# 自动检查路径有效性
print("="*40)
print("EXE文件存在:", os.path.exists(exe_path))
print("图片文件存在:", os.path.exists(image_path))
print("="*40)

# 结果解读
if not os.path.exists(exe_path):
    print("\n错误: EXE路径无效，请检查：")
    print(f"1. 确认文件夹 'XUNLEI' 是否拼写正确（不是XUNLET）")
    print(f"2. 检查文件名是否包含空格：'March7th Launcher.exe'（必须有空格）")

if not os.path.exists(image_path):
    print("\n错误: 图片路径无效，请检查：")
    print(f"1. 确认文件夹名 '抹茶塔菲' 是否与实际一致（不是抹茶酱非）")
    print(f"2. 图片名称必须完全匹配：'崩铁结束.png'（不是谢铁结束）")

# 暂停查看结果（仅限Windows）
os.system("pause")