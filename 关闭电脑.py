import os
import time

# 设置定时时间（单位：秒）
shutdown_time =1 * 60 * 60  # 2小时

print(f"电脑将在{shutdown_time // 3600}小时后强制关闭")

# 等待指定时间
time.sleep(shutdown_time)

# 强制关闭电脑
os.system("shutdown /s /f /t 1")
