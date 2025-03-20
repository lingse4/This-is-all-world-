import pygetwindow as gw

# 获取所有窗口
windows = gw.getAllTitles()

# 打印每个窗口的标题
for window in windows:
    print(window)
# 您的代码...

# 在脚本最后添加以下行
input("按 Enter 键退出...")
