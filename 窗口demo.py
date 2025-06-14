from qfluentwidgets import NavigationBarPushButton, NavigationItemPosition, setThemeColor, setTheme, Theme, MSFluentWindow, toggleTheme  # Add this import if using qfluentwidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton  # Add this import
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, QTimer  # 新增QTimer导入
from qfluentwidgets import SplashScreen  # Add this import
from contextlib import redirect_stdout
with redirect_stdout(None):
    from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, setThemeColor, NavigationBarPushButton, toggleTheme, setTheme, Theme
    from qfluentwidgets import FluentIcon as FIF
    from qfluentwidgets import InfoBar, InfoBarPosition

class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

        self.initInterface()
        self.initNavigation()

    def initWindow(self):
        self.setMicaEffectEnabled(False)
        setThemeColor('#f18cb9', lazy=True)
        setTheme(Theme.AUTO, lazy=True)

        # 禁用最大化
        self.titleBar.maxBtn.setHidden(True)
        self.titleBar.maxBtn.setDisabled(True)
        self.titleBar.setDoubleClickEnabled(False)
        self.setResizeEnabled(False)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        self.resize(1920, 1280)
        self.setWindowIcon(QIcon("D:\桌面\dazhaohu.jpg"))
        self.setWindowTitle("March7th Assistant")

        # 创建启动画面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(1920, 1080))
        self.splashScreen.titleBar.maxBtn.setHidden(True)
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.show()
        QApplication.processEvents()

    def initInterface(self):
        # 辅助函数：生成包含按钮的临时界面（新增设置objectName逻辑）
        def create_temp_interface(title: str, parent):
            widget = QWidget(parent)
            widget.setObjectName(title)  # 关键修改：设置对象名称为标题（避免空字符串）
            layout = QVBoxLayout(widget)
            btn = QPushButton(f"临时界面：{title}", widget)
            btn.setMinimumSize(200, 200)
            layout.addWidget(btn, 0, Qt.AlignCenter)
            widget.setLayout(layout)
            return widget

        # 替换为临时界面（原界面对象改为临时按钮界面）
        self.homeInterface = create_temp_interface("主页", self)
        self.helpInterface = create_temp_interface("帮助", self)
        # self.changelogInterface = create_temp_interface("更新日志", self)  # 可选：取消注释启用
        self.warpInterface = create_temp_interface("抽卡记录", self)
        self.toolsInterface = create_temp_interface("工具箱", self)
        self.settingInterface = create_temp_interface("设置", self)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('主页'))
        self.addSubInterface(self.helpInterface, FIF.BOOK_SHELF, self.tr('帮助'))
        # self.addSubInterface(self.changelogInterface, FIF.UPDATE, self.tr('更新日志'))
        self.addSubInterface(self.warpInterface, FIF.SHARE, self.tr('抽卡记录'))
        self.addSubInterface(self.toolsInterface, FIF.DEVELOPER_TOOLS, self.tr('工具箱'))

        #self.navigationInterface.addWidget(
            #'startGameButton',
            #NavigationBarPushButton(FIF.PLAY, '启动游戏', isSelectable=False),
            #self.startGame,
            #NavigationItemPosition.BOTTOM)

        self.navigationInterface.addWidget(
            'themeButton',
            NavigationBarPushButton(FIF.BRUSH, '主题', isSelectable=False),
            lambda: toggleTheme(lazy=True),
            NavigationItemPosition.BOTTOM)

        #self.navigationInterface.addWidget(
            #'avatar',
            #NavigationBarPushButton(FIF.HEART, '赞赏', isSelectable=False),
            #lambda: MessageBoxSupport(
                #'支持作者🥰',
                #'此程序为免费开源项目，如果你付了钱请立刻退款\n如果喜欢本项目，可以微信赞赏送作者一杯咖啡☕\n您的支持就是作者开发和维护项目的动力🚀',
                #'./assets/app/images/sponsor.jpg',
                #self
            #).exec(),
            #NavigationItemPosition.BOTTOM
        #)

        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('设置'), position=NavigationItemPosition.BOTTOM)

        # 原self.splashScreen.finish()修改为延迟2秒关闭
        QTimer.singleShot(2000, self.splashScreen.finish)  # 2000毫秒=2秒


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)  # 创建Qt应用程序实例
    window = MainWindow()         # 创建主窗口实例               
     # 显示窗口（虽然initWindow里已经调用过，这里可以保留冗余）
    sys.exit(app.exec_())         # 启动事件循环并等待退出