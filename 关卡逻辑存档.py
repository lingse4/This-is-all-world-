start_coords = (1245,661)
        coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\yx.png", screenshot_path)
        coords1 = get_xy(r"C:\Users\38384\Pictures\Screenshots\ys.png", screenshot_path)
        txms_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\txms.png", screenshot_path, threshold=0.7)
        coords2 = get_xy(r"C:\Users\38384\Pictures\Screenshots\ksjq.png", screenshot_path)
        coords3 = get_xy(r"C:\Users\38384\Pictures\Screenshots\jzyx.png", screenshot_path, threshold=0.7)
        coords4 = get_xy(r"C:\Users\38384\Pictures\Screenshots\ys1.png", screenshot_path, threshold=0.6)

        if coords:  # 如果成功找到目标图片
            print(f"找到一个关卡")
            if coords1:
                print(f"没有打")
                time.sleep(0.5)  # 等待 1 秒
                adb_tap(start_coords[0], start_coords[1])  # 使用第一步的点击坐标
                print("进入关卡")
                Clear_levels("这个关卡")
                break
            elif txms_coords:
                print(f"切换为突袭模式,坐标：{txms_coords}")
                auto_click(*txms_coords)
                if coords1:
                    print(f"没有打")
                    time.sleep(0.5)
                    adb_tap(start_coords[0], start_coords[1])
                    print("进入关卡")
                    Clear_levels("这个关卡")
                    break
            else:
                print(f"不是普通关卡")
        elif coords2:  # 如果成功找到目标图片
            print("剧情关卡")
            adb_tap(977, 368)  # 使用第一步的点击坐标
            print("进入关卡")
            time.sleep(5)  # 等待 5 秒
            adb_tap(640,360)  # 使用第一步的点击坐标
            if coords4:
                print("领源石")
                adb_tap(640,360)
                time.sleep(1)
            break
        elif coords3:  # 如果成功找到目标图片
            print("演习关卡")
            adb_tap(1245,661)
            time.sleep(1)
            adb_tap(1085,500)
            print("进入关卡")
            match1_and_click_with_retry(
                r"C:\Users\38384\Pictures\Screenshots\bsgy.png",
                screenshot_path,
                r"C:\Users\38384\Pictures\Screenshots\xd.png"
            )
            time.sleep(2)
            adb_tap(208, 217)
            break