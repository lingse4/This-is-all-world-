import logging
import os

# 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建日志记录器
log = logging.getLogger("main_logger")
log.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
log.addHandler(file_handler)
log.addHandler(console_handler)