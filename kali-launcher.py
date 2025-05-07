import os
import json
import subprocess
import sys
import uuid
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRegularExpression
from PyQt6.QtGui import QAction, QFont, QIcon, QDesktopServices, QRegularExpressionValidator, QGuiApplication
import functools


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

        self.button.setStyleSheet(self.get_card_style())
        self.button.clicked.connect(self.execute)
        layout.addWidget(self.button)

    def get_card_style(self):
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4e54c8, stop:1 #8f94fb);
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
                color: white;
                border: none;
                text-align: left;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8f94fb, stop:1 #4e54c8);
            }
            QPushButton:menu-indicator {
                image: none;
            }
        """

    def execute(self):
        try:
            if self.open_terminal:
                # 退出虚拟环境并切换到用户主目录
                full_command = f"deactivate 2>/dev/null; cd ~; {self.command}; exec bash"
                try:
                    # 尝试使用 x-terminal-emulator 来执行命令
                    subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c '{full_command}'"])
                except FileNotFoundError:
                    print("错误: 找不到 x-terminal-emulator，请确保已安装。")
            else:
                subprocess.Popen(self.command, shell=True)
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
        self.command_input = QLineEdit()
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
            lbl.setStyleSheet("font-weight: bold;")
            hbox.addWidget(lbl)
            hbox.addWidget(widget)
            self.layout().addLayout(hbox)

        self.layout().addWidget(self.open_terminal_checkbox)

        regex = QRegularExpression(r'[a-zA-Z0-9_\- ]{1,30}')
        self.name_input.setValidator(QRegularExpressionValidator(regex))

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

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
        if original_name:
            self.name_input.setText(original_name)
        regex = QRegularExpression(r'[a-zA-Z0-9_\- ]{1,20}')
        self.name_input.setValidator(QRegularExpressionValidator(regex))

        self.layout().addWidget(QLabel("组名:"))
        self.layout().addWidget(self.name_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout().addWidget(self.button_box)

    def get_name(self):
        return self.name_input.text().strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 数据配置初始化
        self.default_category = "工作区"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(current_dir, ".kali_launcher.json")
        self.data = self.load_data()

        # 界面元数据
        self.setWindowTitle("Kali 启动器")
        self.resize(1000, 700)
        self.setStyleSheet(self.get_window_style())

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
        self.category_list = QListWidget()
        self.category_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.category_list.customContextMenuRequested.connect(self.show_category_context)
        self.category_list.itemClicked.connect(self.show_category)
        self.refresh_categories()
        self.category_list.setMinimumWidth(200)  # 设置左侧菜单栏最小宽度

        # 右键菜单绑定
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_global_context)

        # 添加列表与样式
        category_box.addWidget(self.category_list)
        main_layout.addLayout(category_box, stretch=1)

        # 内容区初始化
        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setStyleSheet(self.get_content_style())

        main_layout.addWidget(self.scroll_area, stretch=999)

    def get_content_style(self):
        return """
            QScrollArea {
                border: none;
                background: #2a2a3c;
                border-radius: 12px;
                margin: 20px;
            }
            QScrollArea > QWidget {
                border: 1px dashed #444;
            }
        """

    def load_data(self):
        if not os.path.exists(self.config_path):
            return {
                "categories": [self.default_category],
                "items": []
            }

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print("配置解析失败:", e)
            return {
                "categories": [self.default_category],
                "items": []
            }

    def save_data(self):
        try:
            with open(self.config_path, "w") as f:
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

        # 清空原有面板，同时删除子部件
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        row, col = 0, 0
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
                self.content_layout.addWidget(item, row, col)

                col += 1
                if col > 3:
                    col = 0
                    row += 1

        # 右上角添加logo
        if not self.data["items"]:
            self.content_layout.addWidget(QLabel("OPEN\nKALI\nLAUNCHER"), 0, 3)

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
            menu.setStyleSheet(self.get_menu_style())
            global_pos = item.button.mapToGlobal(position)
            menu.exec(global_pos)  # 调整菜单弹出位置
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
            reply = QMessageBox.question(
                self,
                "移除确认",
                f"确定要移除 '{item.name}' 吗？"
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.data["items"] = [p for p in self.data.get("items", []) if p["id"] != item.item_id]
                self.save_data()

                # 清空原有面板，同时删除子部件
                while self.content_layout.count():
                    child = self.content_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                self.show_category(self.category_list.currentItem())
                self.content_widget.updateGeometry()
        except Exception as e:
            print(f"删除启动项时出错: {e}")

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
            menu.setStyleSheet(self.get_menu_style())
            global_pos = self.mapToGlobal(pos)
            menu.exec(global_pos)  # 调整菜单弹出位置
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
            menu.addAction(QIcon.fromTheme("list-add"), "添加启动项", lambda: self.add_launcher_item(clicked_item.text()))
            if clicked_item and clicked_item.text() != self.default_category:
                menu.addAction(QIcon.fromTheme("edit-delete"), "删除组", lambda: self.remove_category(clicked_item))

            menu.addSeparator()
            menu.addAction(QIcon.fromTheme("list-add"), "新建组", self.add_new_category)
            menu.addAction(QIcon.fromTheme("application-exit"), "退出", self.close)
            menu.setStyleSheet(self.get_menu_style())

            if clicked_item:
                menu.exec(self.category_list.mapToGlobal(position))
            else:
                menu.exec(self.mapToGlobal(position))
        except Exception as e:
            print(f"显示分类右键菜单时出错: {e}")

    def rename_category(self, item):
        try:
            if not item or item.text() in [self.default_category, ""]:
                return

            old_name = item.text()
            dialog = CategoryDialog(self, old_name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_name = dialog.get_name()
                if new_name and new_name != old_name and new_name not in self.data["categories"]:
                    # 三步骤更新策略 🔁
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
            print(f"重命名分类时出错: {e}")

    def add_launcher_item(self, category):
        try:
            dialog = ItemEditDialog(self, {
                "name": "",
                "command": "",
                "category": category or self.default_category,
                "open_terminal": True
            })

            if dialog.exec() == QDialog.DialogCode.Accepted:
                item_data = dialog.get_data()
                new_item = {
                    "id": str(uuid.uuid4()),
                    "name": item_data['name'],
                    "command": item_data['command'],
                    "category": item_data['category'] or self.default_category,
                    "open_terminal": item_data["open_terminal"]
                }

                # 存入并展示
                self.data["items"].append(new_item)
                self.save_data()
                self.show_category(self.category_list.currentItem())
        except Exception as e:
            print(f"添加启动项时出错: {e}")

    def add_new_category(self):
        try:
            dialog = CategoryDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                category_name = dialog.get_name()

                if not category_name or category_name in self.data.get("categories", []):
                    return
                self.data["categories"].append(category_name)

                self.save_data()
                self.refresh_categories()
        except Exception as e:
            print(f"添加新分类时出错: {e}")

    def remove_category(self, item):
        try:
            if not item or item.text() == self.default_category:
                return

            reply = QMessageBox.question(
                self,
                "组删除",
                f"删除组 '{item.text()}' 同时会清空所有相关项目，确定继续？"
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.data["categories"].remove(item.text())
                self.data["items"] = [p for p in self.data.get("items", [])
                                      if p["category"] != item.text()]

                self.save_data()
                self.refresh_categories()

                default_item = self.category_list.findItems(
                    self.default_category, Qt.MatchFlag.MatchFixedString)
                if default_item:
                    self.category_list.setCurrentItem(default_item[0])
                    self.show_category(default_item[0])
        except Exception as e:
            print(f"删除分类时出错: {e}")


def main():
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
    
