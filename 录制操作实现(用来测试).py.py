import socket
import time
from pathlib import Path  # 新增：用于文件路径处理
from pyminitouch.utils import str2byte

HOST = '127.0.0.1'
PORT = 1090

# 修改：从桌面的mouse_operations.txt读取指令（与录制脚本保存路径一致）
RECORD_FILE = r"C:\Users\38384\Desktop\抹茶巴菲\mouse_operations.txt"
with open(RECORD_FILE, "r", encoding="utf-8") as f:
    content = f.read()  # 读取txt文件内容作为指令

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.sendall(str2byte(content))
time.sleep(0.5)
sock.shutdown(socket.SHUT_WR)

res = ''
while True:
    data = sock.recv(1024)
    if (not data):
        break
    res += data.decode()

print(res)
print('closed')
sock.close()