from pywinauto.application import Application
import traceback


def print_control_info(control, indent=0):
    """递归地打印给定控件及其子控件的信息"""
    try:
        # 打印当前控件的基本信息
        print(
            ' ' * indent + f'Control: {control.friendly_class_name()} - "{control.window_text()}" (Handle: {control.handle})')
        print(' ' * (indent + 4) + f'Class Name: {control.class_name()}')
        print(' ' * (indent + 4) + f'Window Text: {control.window_text()}')
        print(' ' * (indent + 4) + f'Rect: {control.rectangle()}')

        # 尝试打印其他可能存在的属性
        try:
            print(' ' * (indent + 4) + f'Style: {control.style()}')
        except AttributeError:
            print(' ' * (indent + 4) + 'Style: Not available')

        try:
            print(' ' * (indent + 4) + f'ExStyle: {control.exstyle()}')
        except AttributeError:
            print(' ' * (indent + 4) + 'ExStyle: Not available')

        try:
            print(' ' * (indent + 4) + f'Is Enabled: {control.is_enabled()}')
        except AttributeError:
            print(' ' * (indent + 4) + 'Is Enabled: Not available')

        try:
            print(' ' * (indent + 4) + f'Is Visible: {control.is_visible()}')
        except AttributeError:
            print(' ' * (indent + 4) + 'Is Visible: Not available')

        try:
            print(' ' * (indent + 4) + f'Is Active: {control.is_active()}')
        except AttributeError:
            print(' ' * (indent + 4) + 'Is Active: Not available')

        try:
            print(' ' * (indent + 4) + f'Is Dialog: {control.is_dialog()}')
        except AttributeError:
            print(' ' * (indent + 4) + 'Is Dialog: Not available')

        # 对每个子控件递归调用此函数
        for child in control.children():
            print_control_info(child, indent + 4)
    except Exception as e:
        # 捕捉并报告在处理控件过程中遇到的任何错误
        print(f"{' ' * indent}Error while processing control: {e}")
        traceback.print_exc()


def main():
    backends = ["uia", "win32"]
    for backend in backends:
        try:
            # 尝试通过标题正则表达式连接到目标应用
            app = Application(backend=backend).connect(title_re=".*March7th Assistant.*")
            break  # 如果成功连接，则退出循环
        except Exception as e:
            print(f"Failed to connect to the application using {backend} backend: {e}")
            traceback.print_exc()
    else:
        # 如果所有后端都失败了
        print("Failed to connect to the application with all available backends.")
        return

    try:
        # 获取主窗口
        main_window = app.window(title_re=".*March7th Assistant.*")
        # 打印窗口标题
        print("Main Window Title:", main_window.window_text())
    except Exception as e:
        print(f"Failed to find or interact with the main window: {e}")
        traceback.print_exc()
        return

    # 从主窗口开始递归打印所有控件信息
    print_control_info(main_window)


if __name__ == "__main__":
    main()
