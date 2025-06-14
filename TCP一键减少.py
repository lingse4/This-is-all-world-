def set_tcp_tuning():
    """设置TCP自动调节级别为restricted"""
    try:
        # 检查管理员权限
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("需要管理员权限，正在请求提权...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "python", f'"{__file__}" --set-tcp', None, 1
            )
            return

        # 执行配置命令
        cmd = "netsh interface tcp set global autotuninglevel=restricted"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # --------------------------
        # 新增验证步骤
        # --------------------------
        check_cmd = "netsh interface tcp show global"
        result = subprocess.run(
            check_cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 解析输出验证结果
        if "autotuninglevel" in result.stdout and "restricted" in result.stdout:
            print("✅ TCP配置验证成功：已设置为restricted模式")
        else:
            print("❌ TCP配置验证失败，请手动检查")
            
    except subprocess.CalledProcessError as e:
        print(f"配置失败: {e.stderr}")
    except Exception as e:
        print(f"未知错误: {str(e)}")