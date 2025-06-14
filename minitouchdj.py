import socket
import time
import sys
from pyminitouch.utils import str2byte

# 新增：定义触摸指令发送函数，参数y为纵坐标，x为横坐标
def send_touch_command(x, y):
    HOST = '127.0.0.1'
    PORT = 1090

    # 修改：使用参数动态生成触摸指令，原固定坐标350→y，1100→x
    content = f"d 0 {y} {x} 50\nw 400\nc\nu 0\nc\n"

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