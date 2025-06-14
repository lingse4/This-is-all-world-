class Clearlevels:

    ks1_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\ks1.png", screenshot_path)
    if ks1_coords:
        adb_click(start_coords[0], start_coords[1])  # 修复：确保 ks1_coords 已赋值
        print("磨难模式启动！")
    else:
        print("还没有到磨难模式")


    # 第三步：全屏截图并匹配 s2.png
    adb_screenshot(screenshot_path)  # 全屏截图
    s2_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s2.png", screenshot_path)  # 匹配 s2.png
    if s2_coords:
        print("吃个药药")
        adb_tap(s2_coords[0], s2_coords[1])  
        time.sleep(2)  # 等待 1 秒
        adb_tap(start_coords[0], start_coords[1])  # 使用 ks1_coords 的点击坐标
    else:
        print("启动！")

    # 后续步骤：使用 OpenCV 模板匹配检测并点击，验证点击事件
    print("检测并点击 '助战干员'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\zz.png",
        screenshot_path,
        r"C:\Users\38384\Pictures\Screenshots\jr.png"
    )

    adb_tap(135,205)  # 使用第一步的点击坐标

    yh_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\jr.png", screenshot_path, threshold=0.6)
    yh2_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\yh2.png", screenshot_path, threshold=0.6)
    jr_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\jr.png", screenshot_path, threshold=0.6)
    while True:
        adb_screenshot(screenshot_path)
        if yh_coords:
            print("点击银灰")
            adb_tap(yh_coords[0], yh_coords[1])
            break
        elif yh2_coords:
            print("点击银灰2")
            adb_tap(yh2_coords[0], yh2_coords[1])
            break
        elif jr_coords:
            adb_tap(jr_coords[0],jr_coords[1])  # 使用第一步的点击坐标
        else:
            print("银灰不在，继续")
            keyboard.Controller().press('0')  # 按下键 '0'
            keyboard.Controller().release('0')  # 松开键 '0'
    time.sleep(1)  # 等待 1 秒

    print("检测并点击 '招募助战'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\zm.png",
        screenshot_path,
        None,  # 无需验证事件
        click_once=True  # 只点击一次
    )

    start_coords = (1085,500)
    time.sleep(5)  # 等待 1 秒
    adb_tap(start_coords[0], start_coords[1])  # 使用第一步的点击坐标
    print(f"点击坐标: {start_coords}")

    # 第四步：全屏截图并匹配 s1.png
    adb_screenshot(screenshot_path)  # 全屏截图
    s1_coords = get_xy(r"C:\Users\38384\Pictures\Screenshots\s1.png", screenshot_path)  # 匹配 s1.png
    if s1_coords:
        print(f"确认ban位")
        auto_click(s1_coords)  # 点击 s1.png 的位置
    else:
        print("下一步")

    # 第五步：检测并点击 "1倍速"
    print("检测并点击 '1倍速'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\1bs.png",
        screenshot_path,
        r"C:\Users\38384\Pictures\Screenshots\2bs.png"
    )

    # 第六步：等待 "2倍速" 出现
    print("等待 '2倍速' 出现")
    wait_for_image(r"C:\Users\38384\Pictures\Screenshots\2bs.png", screenshot_path)

    # 第七步：检测并点击 "暂停"
    print("检测并点击 '部署干员'")
    match1_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\bsgy.png",
        screenshot_path,
        None,  # 无需验证事件
        click_once=True  # 只点击一次
    )

    # 第八步：检测并点击 "行动结束"
    print("检测并点击 '行动结束'")
    match_and_click_with_retry(
        r"C:\Users\38384\Pictures\Screenshots\xd.png",
        screenshot_path,
        None,  # 最后一步无需验证事件
        click_once=True,  # 点击一次
        wait_before_click=2  # 点击前等待 2 秒
    )
