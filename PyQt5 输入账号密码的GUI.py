import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit

class AccountPasswordApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('账号密码输入')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # 标签和输入框
        self.label_username = QLabel('用户名:')
        self.lineEdit_username = QLineEdit()
        self.label_password = QLabel('密码:')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)

        # 添加按钮
        self.add_button = QPushButton('添加账号')
        self.add_button.clicked.connect(self.add_account)

        # 显示已添加的账号和密码
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # 输出按钮
        self.output_button = QPushButton('输出所有账号')
        self.output_button.clicked.connect(self.output_accounts)

        # 布局
        layout.addWidget(self.label_username)
        layout.addWidget(self.lineEdit_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.lineEdit_password)
        layout.addWidget(self.add_button)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.output_button)

        self.setLayout(layout)

        # 存储账号和密码的列表
        self.accounts = []

    def add_account(self):
        username = self.lineEdit_username.text().strip()
        password = self.lineEdit_password.text().strip()
        if username and password:
            self.accounts.append((username, password))
            self.text_edit.append(f'用户名: {username}, 密码: {"*" * len(password)}')
            self.lineEdit_username.clear()
            self.lineEdit_password.clear()
        else:
            self.text_edit.append('请输入有效的用户名和密码')

    def output_accounts(self):
        self.text_edit.clear()
        for username, password in self.accounts:
            self.text_edit.append(f'用户名: {username}, 密码: {password}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AccountPasswordApp()
    ex.show()
    sys.exit(app.exec_())


