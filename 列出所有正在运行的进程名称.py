import psutil

def list_specific_processes(process_names):
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in process_names:
                processes.append((proc.info['pid'], proc.info['name']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

if __name__ == "__main__":
    specific_process_names = ["chrome.exe", "firefox.exe", "Code.exe"]  # 替换为你想要查找的进程名称列表
    running_processes = list_specific_processes(specific_process_names)
    print("特定类型的正在运行的进程:")
    for pid, name in running_processes:
        print(f"PID: {pid}, Name: {name}")


