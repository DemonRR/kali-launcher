# -*- coding: utf-8 -*-

import os
import json
import subprocess
import sys
import uuid
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRegularExpression, QRect
from PyQt6.QtGui import QAction, QFont, QIcon, QDesktopServices, QRegularExpressionValidator, QGuiApplication
import functools


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def doLayout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        for item in self.item_list:
            wid = item.widget()
            space_x = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal
            )
            space_y = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical
            )
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


# 定义日志文件路径
LOG_DIR = os.path.join(os.path.expanduser("~"), ".config", "kali_launcher")
LOG_FILE = os.path.join(LOG_DIR, "error.log")

# 创建日志目录
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def log_error(error_message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{error_message}\n")
    except Exception as e:
        print(f"记录日志时出错: {e}")

class LauncherItem(QWidget):
    def __init__(self, item_id, name, command, category, open_terminal, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.name = name
        self.command = command
        self.category = category
        self.open_terminal = open_terminal

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton()
        self.button.setText(self.name)
        self.button.setMinimumSize(QSize(180, 60))
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)

        if QIcon.hasThemeIcon('utilities-terminal'):
            self.button.setIcon(QIcon.fromTheme('utilities-terminal'))
            self.button.setIconSize(QSize(24, 24))
            self.button.setText(f"  {self.name}")

        self.button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4e54c8, stop:1 #8f94fb);
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
                color: white;
                border: none;
                text-align: left;
                font-family: 'Segoe UI', sans-serif;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8f94fb, stop:1 #4e54c8);
                transform: scale(1.05);
            }
            QPushButton:menu-indicator {
                image: none;
            }
        """)
        self.button.clicked.connect(self.execute)
        layout.addWidget(self.button)
        # 添加背景样式，与右侧区域一致
        self.setStyleSheet("""
            QWidget {
                background: #2a2a3c;
            }
        """)

    def execute(self):
        try:
            if self.open_terminal:
                # 简化命令字符串，去掉 deactivate
                full_command = f"cd ~; {self.command}; exec bash"
                terminal_emulators = ["x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal"]
                for emulator in terminal_emulators:
                    try:
                        print(f"尝试使用 {emulator} 执行命令: {full_command}")
                        if emulator == "x-terminal-emulator":
                            process = subprocess.Popen([emulator, '-e', 'bash', '-c', full_command],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)
                        elif emulator == "gnome-terminal":
                            process = subprocess.Popen([emulator, '--', 'bash', '-c', full_command],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)
                        elif emulator == "konsole":
                            process = subprocess.Popen([emulator, '-e', 'bash', '-c', full_command],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)
                        elif emulator == "xfce4-terminal":
                            process = subprocess.Popen([emulator, '--command', f"bash -c '{full_command}'"],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate()
                        if process.returncode == 0:
                            print(f"成功使用 {emulator} 执行命令。")
                            return
                        else:
                            print(f"使用 {emulator} 执行命令失败，返回码: {process.returncode}")
                            print(f"标准输出: {stdout.decode('utf-8')}")
                            print(f"标准错误: {stderr.decode('utf-8')}")
                    except FileNotFoundError:
                        print(f"{emulator} 不可用，尝试下一个终端模拟器。")
                print("没有可用的终端模拟器。")
            else:
                try:
                    print(f"尝试执行命令: {self.command}")
                    process = subprocess.Popen(self.command, shell=True,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        print("命令执行成功。")
                    else:
                        print(f"命令执行失败，返回码: {process.returncode}")
                        print(f"标准输出: {stdout.decode('utf-8')}")
                        print(f"标准错误: {stderr.decode('utf-8')}")
                except Exception as e:
                    print(f"执行命令时发生未知错误: {e}")
        except Exception as e:
            print(f"执行命令错误: {e}")


class ItemEditDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle("编辑快速入口")
        self.setLayout(QVBoxLayout())
        self.setMinimumWidth(400)
        self.item_data = item_data

        category_list = parent.data.get("categories", [])

        self.name_input = QLineEdit()
        # 修改为 PyQt6 支持的输入法提示
        self.name_input.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)

        self.command_input = QLineEdit()
        # 修改为 PyQt6 支持的输入法提示
        self.command_input.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)

        self.category_combo = QComboBox()
        self.category_combo.addItems(category_list)
        self.open_terminal_checkbox = QCheckBox("打开终端界面")

        if item_data:
            self.name_input.setText(item_data.get('name', ''))
            self.command_input.setText(item_data.get('command', ''))
            if item_data.get('category', '') in category_list:
                self.category_combo.setCurrentText(item_data.get('category', ''))
            self.open_terminal_checkbox.setChecked(item_data.get('open_terminal', True))

        for label, widget in [
            ("名称:", self.name_input),
            ("分组:", self.category_combo),
            ("命令:", self.command_input)
        ]:
            hbox = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setMinimumWidth(80)
            lbl.setStyleSheet("font-weight: bold; color: #e0e0e0;")  # 修改标签颜色
            hbox.addWidget(lbl)
            hbox.addWidget(widget)
            self.layout().addLayout(hbox)

        self.layout().addWidget(self.open_terminal_checkbox)

        regex = QRegularExpression(r'^[\p{L}0-9_\- ]{1,30}$', QRegularExpression.PatternOption.UseUnicodePropertiesOption)
        self.name_input.setValidator(QRegularExpressionValidator(regex))

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

        self.setStyleSheet("""
            QDialog {
                background-color: #2a2a3c;
                color: #e0e0e0;  # 修改整体颜色
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit, QComboBox {
                background-color: #3a3a4c;
                color: #e0e0e0;  # 修改输入框颜色
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #4e54c8;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #8f94fb;
            }
        """)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "command": self.command_input.text(),
            "category": self.category_combo.currentText(),
            "open_terminal": self.open_terminal_checkbox.isChecked()
        }


class CategoryDialog(QDialog):
    def __init__(self, parent=None, original_name=""):
        super().__init__(parent)
        self.setWindowTitle("管理应用组")
        self.setLayout(QVBoxLayout())
        self.setMinimumWidth(300)

        self.name_input = QLineEdit()
        # 修改为 PyQt6 支持的输入法提示
        self.name_input.setInputMethodHints(Qt.InputMethodHint.ImhNoAutoUppercase)

        if original_name:
            self.name_input.setText(original_name)
        regex = QRegularExpression(r'^[\p{L}0-9_\- ]{1,20}$', QRegularExpression.PatternOption.UseUnicodePropertiesOption)
        self.name_input.setValidator(QRegularExpressionValidator(regex))

        self.layout().addWidget(QLabel("组名:", styleSheet="font-weight: bold; color: #e0e0e0;"))  # 修改标签颜色
        self.layout().addWidget(self.name_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

        self.setStyleSheet("""
            QDialog {
                background-color: #2a2a3c;
                color: #e0e0e0;  # 修改整体颜色
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background-color: #3a3a4c;
                color: #e0e0e0;  # 修改输入框颜色
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #4e54c8;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #8f94fb;
            }
        """)

    def get_name(self):
        return self.name_input.text().strip()


# 定义配置和日志文件路径
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "kali_launcher")
CONFIG_FILE = os.path.join(CONFIG_DIR, ".kali_launcher.json")
LOG_FILE = os.path.join(CONFIG_DIR, "error.log")

# 创建配置目录
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


def log_error(error_message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{error_message}\n")
    except Exception as e:
        print(f"记录日志时出错: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 数据配置初始化
        self.default_category = "工作区"
        self.config_path = CONFIG_FILE

        # 检查配置文件是否存在，不存在则创建默认配置
        if not os.path.exists(self.config_path):
            default_data = {
                "categories": [],
                "items": []
            }
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
            except Exception as e:
                print("创建默认配置文件时出错:", e)
                log_error(f"创建默认配置文件时出错: {e}")

        self.data = self.load_data()

        # 界面元数据
        self.setWindowTitle("Kali 启动器")
        # 再次增大窗口初始宽度
        self.resize(1100, 700)
        self.setStyleSheet("""
                    QWidget {
                        background: #1e1e2f;
                        color: #ffffff;
                        font-family: 'Segoe UI', sans-serif;
                    }
                    QListWidget::item:selected {
                        background: qlineargradient(x1:1, y1:1, x2:0, y2:0, stop:0 #3a47d5, stop:1 #7080f5);
                    }
                """)

        # 计算窗口最小宽度，确保能容纳一行 4 个启动器
        launcher_min_width = 180
        spacing = 20
        # 再次增大最小宽度
        min_width = 200 + 2 * spacing + 4 * launcher_min_width + 3 * spacing + 50
        self.setMinimumWidth(min_width)

        # 将窗口移动到屏幕中心
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # UI 组件部署
        self.init_ui()

    def get_window_style(self):
        return """
            QWidget {
                background: #1e1e2f;
                color: #ffffff;
                font-family: Segoe UI;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:1, y1:1, x2:0, y2:0, stop:0 #3a47d5, stop:1 #7080f5);
            }
        """

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧面板布局
        category_box = QVBoxLayout()

        # 创建一个容器来包含标题和列表，设置背景样式
        left_container = QWidget()
        left_container.setStyleSheet("""
            background-color: #2a2a3c;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
        """)
        left_layout = QVBoxLayout(left_container)

        # 添加左侧菜单栏标题
        left_title = QLabel("菜单栏")
        left_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 15px;
            text-align: center;
        """)
        left_layout.addWidget(left_title)

        self.category_list = QListWidget()
        self.category_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_list.customContextMenuRequested.connect(self.show_category_context)
        self.category_list.itemClicked.connect(self.show_category)
        self.refresh_categories()
        self.category_list.setMinimumWidth(200)  # 设置左侧菜单栏最小宽度
        self.category_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                color: #ffffff;
                font-size: 16px;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:1, y1:1, x2:0, y2:0, stop:0 #3a47d5, stop:1 #7080f5);
            }
            QListWidget::item:focus {
                outline: none;
            }
        """)
        left_layout.addWidget(self.category_list)

        category_box.addWidget(left_container)
        main_layout.addLayout(category_box, stretch=1)

        # 右键菜单绑定
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_global_context)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #444; margin: 0 10px;")
        main_layout.addWidget(separator)

        # 内容区初始化
        launcher_box = QVBoxLayout()

        # 创建一个容器来包含标题和滚动区域，设置背景样式
        right_container = QWidget()
        right_container.setStyleSheet("background-color: #2a2a3c; border-radius: 12px;")
        right_layout = QVBoxLayout(right_container)

        # 添加右侧动态标题
        self.right_title = QLabel()
        self.right_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            margin: 10px;
        """)
        right_layout.addWidget(self.right_title)

        self.content_widget = QWidget()
        self.content_layout = FlowLayout()
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setAutoFillBackground(True)
        self.content_widget.setStyleSheet("background: #2a2a3c;")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #2a2a3c;
                border-radius: 12px;
                margin: 0;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }
            QScrollArea > QWidget {
                border: none;
                background: #2a2a3c;
                border-radius: 12px;
            }
            QScrollBar:vertical {
                background: #3a3a4c;
                width: 12px;
                margin: 12px 0 12px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4e54c8;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        right_layout.addWidget(self.scroll_area)
        launcher_box.addWidget(right_container)
        main_layout.addLayout(launcher_box, stretch=999)

        # 初始化时自动显示第一个分类的启动器
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.show_category(self.category_list.currentItem())

    def get_content_style(self):
        return """
            QScrollArea {
                border: none;
                background: #2a2a3c;
                border-radius: 12px;
                margin: 20px;
            }
            QScrollArea > QWidget {
                border: none;
            }
        """

    def load_data(self):
        if not os.path.exists(self.config_path):
            return {
                "categories": [],
                "items": []
            }

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("配置解析失败:", e)
            log_error(f"配置解析失败: {e}")
            return {
                "categories": [],
                "items": []
            }

    def save_data(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print("配置保存失败:", e)

    def refresh_categories(self):
        self.category_list.clear()
        for cat in self.data.get("categories", []):
            item = QListWidgetItem(cat)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            self.category_list.addItem(item)

    def show_category(self, item):
        self.selected_category = item.text()

        # 更新右侧动态标题
        self.right_title.setText(self.selected_category)

        # 清空原有面板，同时删除子部件
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for project in self.data["items"]:
            if project["category"] == self.selected_category:
                item = LauncherItem(
                    item_id=project['id'],
                    name=project['name'],
                    command=project['command'],
                    category=project['category'],
                    open_terminal=project.get('open_terminal', True)
                )
                item.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                item.customContextMenuRequested.connect(lambda pos, i=item: self.show_item_context(i, pos))
                self.content_layout.addWidget(item)

        # 右上角添加logo
        if not self.data["items"]:
            self.content_layout.addWidget(QLabel("OPEN\nKALI\nLAUNCHER"))

        self.content_widget.updateGeometry()

    def show_item_context(self, item, position):
        try:
            menu = QMenu(self)
            menu.addAction("编辑", lambda: self.edit_launcher_item(item))
            move_to = menu.addMenu("移动到..")

            for category in sorted(self.data.get("categories", []), key=lambda x: x != item.category):
                if category == item.category:
                    continue
                action = move_to.addAction(category)
                action.triggered.connect(functools.partial(self.move_to_category, item, category))

            menu.addSeparator()
            menu.addAction("删除", lambda: self.delete_launcher_item(item))
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2a2a3c;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
                }
                QMenu::item:selected {
                    background: #3a47d5;
                    color: white;
                }
                QMenu::icon {
                    margin-right: 10px;
                }
            """)
            global_pos = item.mapToGlobal(position)
            menu.exec(global_pos)
        except Exception as e:
            print(f"显示项目右键菜单时出错: {e}")

    def move_to_category(self, item, target_category):
        try:
            for project in self.data["items"]:
                if project["id"] == item.item_id:
                    project["category"] = target_category
                    break
            self.save_data()
            self.show_category(self.category_list.currentItem())
        except Exception as e:
            print(f"移动到分类时出错: {e}")

    def edit_launcher_item(self, item):
        try:
            target_item = None
            for project in self.data["items"]:
                if project["id"] == item.item_id:
                    target_item = project
                    break

            dialog = ItemEditDialog(self, {
                "name": target_item["name"],
                "command": target_item["command"],
                "category": target_item["category"],
                "open_terminal": target_item.get('open_terminal', True)
            })

            if dialog.exec() == QDialog.DialogCode.Accepted:
                target_data = dialog.get_data()
                target_item.update({
                    "name": target_data["name"],
                    "command": target_data["command"],
                    "category": target_data["category"] or self.default_category,
                    "open_terminal": target_data["open_terminal"]
                })

                self.save_data()
                self.show_category(self.category_list.currentItem())
        except Exception as e:
            print(f"编辑启动项时出错: {e}")

    def delete_launcher_item(self, item):
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("移除确认")
            msg_box.setText(f"确定要移除 '{item.name}' 吗？")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2a2a3c;
                    color: #ffffff;
                    font-family: 'Segoe UI', sans-serif;
                }
                QPushButton {
                    background-color: #4e54c8;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #8f94fb;
                }
            """)

            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                self.data["items"] = [p for p in self.data.get("items", []) if p["id"] != item.item_id]
                self.save_data()

                while self.content_layout.count():
                    child = self.content_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                self.show_category(self.category_list.currentItem())
                self.content_widget.updateGeometry()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除启动项时出错: {str(e)}")

    def show_global_context(self, pos):
        try:
            menu = QMenu(self)

            # 当前所有组
            if "categories" in self.data:
                switch_menu = menu.addMenu(QIcon.fromTheme("go-jump"), "切换组")
                for cat in sorted(self.data["categories"], key=lambda x: x == self.default_category):
                    if cat == self.default_category:
                        continue
                    switch_menu.addAction(cat, lambda c=cat: self.switch_to_category(c))

            # 更多功能
            menu.addSeparator()
            menu.addAction(QIcon.fromTheme("list-add"), "新建启动器", lambda: self.add_launcher_item(None))
            menu.addAction(QIcon.fromTheme("list-add"), "新建组", self.add_new_category)
            menu.addAction(QIcon.fromTheme("application-exit"), "退出", self.close)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2a2a3c;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
                }
                QMenu::item:selected {
                    background: #3a47d5;
                    color: white;
                }
                QMenu::icon {
                    margin-right: 10px;
                }
            """)
            global_pos = self.mapToGlobal(pos)
            menu.exec(global_pos)
        except Exception as e:
            print(f"显示全局右键菜单时出错: {e}")

    def get_menu_style(self):
        return """
            QMenu {
                background-color: #2a2a3c;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QMenu::item:selected {
                background: #3a47d5;
                color: white;
            }
            QMenu::icon {
                margin-right: 10px;
            }
        """

    def switch_to_category(self, category):
        item = self.category_list.findItems(category, Qt.MatchFlag.MatchFixedString)
        if item:
            self.category_list.setCurrentItem(item[0])
            self.show_category(item[0])

    def show_category_context(self, position):
        try:
            clicked_item = self.category_list.itemAt(position)
            menu = QMenu(self)

            menu.addAction(QIcon.fromTheme("edit-rename"), "重命名组", lambda: self.rename_category(clicked_item))
            menu.addAction(QIcon.fromTheme("list-add"), "添加启动项",
                           lambda: self.add_launcher_item(clicked_item.text()))
            if clicked_item and clicked_item.text() != self.default_category:
                menu.addAction(QIcon.fromTheme("edit-delete"), "删除组", lambda: self.remove_category(clicked_item))

            menu.addSeparator()
            menu.addAction(QIcon.fromTheme("list-add"), "新建组", self.add_new_category)
            menu.addAction(QIcon.fromTheme("application-exit"), "退出", self.close)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2a2a3c;
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
                }
                QMenu::item:selected {
                    background: #3a47d5;
                    color: white;
                }
                QMenu::icon {
                    margin-right: 10px;
                }
            """)

            if clicked_item:
                menu.exec(self.category_list.mapToGlobal(position))
            else:
                menu.exec(self.mapToGlobal(position))
        except Exception as e:
            print(f"显示分类右键菜单时出错: {e}")

    def rename_category(self, item):
        try:
            if not item or item.text() in [self.default_category, ""]:
                QMessageBox.warning(self, "提示", "不能重命名默认分类或空分类")
                return

            old_name = item.text()
            dialog = CategoryDialog(self, old_name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_name = dialog.get_name()
                if new_name and new_name != old_name and new_name not in self.data["categories"]:
                    self.data["categories"].remove(old_name)
                    self.data["categories"].append(new_name)

                    for project in self.data["items"]:
                        if project["category"] == old_name:
                            project["category"] = new_name

                    self.save_data()
                    self.refresh_categories()

                    new_item = self.category_list.findItems(new_name, Qt.MatchFlag.MatchFixedString)
                    if new_item:
                        self.category_list.setCurrentItem(new_item[0])
                        self.show_category(new_item[0])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名分类时出错: {str(e)}")

    def add_launcher_item(self, category):
        if not self.data.get("categories"):
            QMessageBox.warning(self, "提示", "当前没有可用的分类，请先创建分类。")
            return

        try:
            dialog = ItemEditDialog(self, {
                "name": "",
                "command": "",
                "category": category or self.default_category,
                "open_terminal": True
            })

            if dialog.exec() == QDialog.DialogCode.Accepted:
                item_data = dialog.get_data()
                if not item_data['command'].strip():
                    QMessageBox.warning(self, "提示", "命令不能为空，请输入有效的命令。")
                    return

                existing_names = [item["name"] for item in self.data["items"]]
                if item_data["name"] in existing_names:
                    QMessageBox.warning(self, "提示", "该启动器名称已存在，请使用其他名称。")
                    return

                new_item = {
                    "id": str(uuid.uuid4()),
                    "name": item_data['name'],
                    "command": item_data['command'],
                    "category": item_data['category'] or self.default_category,
                    "open_terminal": item_data["open_terminal"]
                }

                self.data["items"].append(new_item)
                self.save_data()
                self.show_category(self.category_list.currentItem())
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加启动项时出错: {str(e)}")

    def add_new_category(self):
        try:
            dialog = CategoryDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                category_name = dialog.get_name()

                if not category_name or category_name in self.data.get("categories", []):
                    QMessageBox.warning(self, "提示", "分类名称不能为空或已存在，请输入其他名称")
                    return

                self.data["categories"].append(category_name)
                self.save_data()
                self.refresh_categories()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加新分类时出错: {str(e)}")

    def remove_category(self, item):
        try:
            if not item or item.text() == self.default_category:
                QMessageBox.warning(self, "提示", "不能删除默认分类")
                return

            msg_box = QMessageBox()
            msg_box.setWindowTitle("删除确认")
            msg_box.setText(f"确定要删除分类 '{item.text()}' 吗？此操作将删除该分类下的所有启动项。")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            # 正确将样式表应用到 QMessageBox
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2a2a3c;
                    color: #ffffff;
                    font-family: 'Segoe UI', sans-serif;
                }
                QPushButton {
                    background-color: #4e54c8;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #8f94fb;
                }
            """)

            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                category_to_remove = item.text()
                # 移除该分类下的所有启动项
                self.data["items"] = [p for p in self.data.get("items", []) if p["category"] != category_to_remove]
                # 移除分类
                if category_to_remove in self.data["categories"]:
                    self.data["categories"].remove(category_to_remove)

                self.save_data()
                self.refresh_categories()

                # 清空当前显示的启动器
                while self.content_layout.count():
                    child = self.content_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                # 如果还有其他分类，显示第一个分类的内容
                if self.category_list.count() > 0:
                    self.category_list.setCurrentRow(0)
                    self.show_category(self.category_list.currentItem())
                else:
                    # 如果没有分类了，显示提示信息
                    self.right_title.setText("无分类")
                    self.content_layout.addWidget(QLabel("暂无分类，请添加新分类。"))

        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除分类时出错: {str(e)}")


def main():
    # 设置输入法模块
    os.environ["QT_IM_MODULE"] = "fcitx"

    # 设置高 DPI 支持（PyQt6.5+ 推荐方案）
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        # 兼容旧版 PyQt6.4 或 PySide6
        QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    else:
        # PyQt6.5+ 需要使用此方案
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    # 强制启用高分辨率支持
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Kali 启动器")
    app.setApplicationVersion("2.1")

    app.setStyle("fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open('last_crash.log', 'a') as f:
            import traceback
            f.write(traceback.format_exc())