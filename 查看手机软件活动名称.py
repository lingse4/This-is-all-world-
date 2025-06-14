# -------------------- 1. 初始化ADB连接 --------------------
import subprocess

adb_path = r"D:\BaiduNetdiskDownload\platform-tools-latest-windows\platform-tools\adb"  # ADB 的完整路径
device_serial = "emulator-5558" \
""  # 指定目标设备
def check_adb_connection():
    """检查ADB设备是否已连接"""
   
    result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
    if device_serial not in result.stdout:
        subprocess.run(f"{adb_path} connect {device_serial}", shell=True)
        result = subprocess.run(f"{adb_path} devices", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
        if device_serial not in result.stdout:
            raise ConnectionError(f"ADB设备未连接!请确认设备 {device_serial} 已开启USB调试模式")

check_adb_connection()
subprocess.run(f"{adb_path} -s {device_serial} shell monkey -p com.hypergryph.arknights -v -v -v 1", shell=True)