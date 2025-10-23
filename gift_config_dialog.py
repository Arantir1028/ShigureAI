import pandas as pd
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QListWidget, QTabWidget, QListWidgetItem, QMessageBox, QWidget
from PyQt5.QtCore import Qt
from utils import resource_path, get_gift_icon

class GiftConfigDialog(QDialog):
    def __init__(self, gifts_data, current_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("配置特殊喜好礼物")
        self.setGeometry(200, 200, 800, 600)
        self.gifts_data = gifts_data
        self.current_config = current_config
        self.parent = parent
        self.level40_gifts = set()
        self.level60_gifts = set()
        self.level180_gifts = set()
        self.level240_gifts = set()

        if parent is not None and hasattr(parent, 'student_configs') and current_config in parent.student_configs:
            config = parent.student_configs[current_config]
            self.level40_gifts = set(config.get('level40_gifts', set()))
            self.level60_gifts = set(config.get('level60_gifts', set()))
            self.level180_gifts = set(config.get('level180_gifts', set()))
            self.level240_gifts = set(config.get('level240_gifts', set()))

            conflicts = self.level40_gifts & self.level60_gifts
            if conflicts:
                print(f"解决冲突: {conflicts}")
                self.level60_gifts -= conflicts

            conflicts = self.level180_gifts & self.level240_gifts
            if conflicts:
                print(f"解决冲突: {conflicts}")
                self.level240_gifts -= conflicts

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        gold_tab = QWidget()
        gold_layout = QHBoxLayout(gold_tab)

        group40 = QGroupBox("40好感")
        group40_layout = QVBoxLayout(group40)
        self.list40 = self.create_gift_tab(20, self.level40_gifts)
        group40_layout.addWidget(self.list40)
        gold_layout.addWidget(group40)

        group60 = QGroupBox("60好感")
        group60_layout = QVBoxLayout(group60)
        self.list60 = self.create_gift_tab(20, self.level60_gifts)
        group60_layout.addWidget(self.list60)
        gold_layout.addWidget(group60)
        tabs.addTab(gold_tab, "金礼物")

        purple_tab = QWidget()
        purple_layout = QHBoxLayout(purple_tab)

        group180 = QGroupBox("180好感")
        group180_layout = QVBoxLayout(group180)
        self.list180 = self.create_gift_tab(120, self.level180_gifts)
        group180_layout.addWidget(self.list180)
        purple_layout.addWidget(group180)

        group240 = QGroupBox("240好感")
        group240_layout = QVBoxLayout(group240)
        self.list240 = self.create_gift_tab(120, self.level240_gifts)
        group240_layout.addWidget(self.list240)
        purple_layout.addWidget(group240)
        tabs.addTab(purple_tab, "紫礼物")

        self.list40.itemChanged.connect(self.on_gift_selection_changed)
        self.list60.itemChanged.connect(self.on_gift_selection_changed)
        self.list180.itemChanged.connect(self.on_gift_selection_changed)
        self.list240.itemChanged.connect(self.on_gift_selection_changed)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def create_gift_tab(self, base_favor, selected_set):
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.NoSelection)

        filtered_gifts = self.gifts_data[self.gifts_data['基础经验值'] == base_favor]
        for _, gift in filtered_gifts.iterrows():
            gift_id = int(gift['ID']) if pd.notna(gift['ID']) else None
            gift_name = str(gift['礼物名']) if pd.notna(gift['礼物名']) else "未知礼物"
            if gift_id is None:
                continue

            item = QListWidgetItem(gift_name)
            item.setData(Qt.UserRole, gift_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if gift_id in selected_set else Qt.Unchecked)
            item.setIcon(get_gift_icon(gift_id))
            list_widget.addItem(item)

        return list_widget

    def on_gift_selection_changed(self, item):
        gift_id = item.data(Qt.UserRole)
        if not gift_id:
            return

        sender = self.sender()
        if sender == self.list40:
            if item.checkState() == Qt.Checked:
                self.level40_gifts.add(gift_id)
                for i in range(self.list60.count()):
                    other_item = self.list60.item(i)
                    if other_item.data(Qt.UserRole) == gift_id:
                        other_item.setCheckState(Qt.Unchecked)
                        self.level60_gifts.discard(gift_id)
                        break
            else:
                self.level40_gifts.discard(gift_id)

        elif sender == self.list60:
            if item.checkState() == Qt.Checked:
                self.level60_gifts.add(gift_id)
                for i in range(self.list40.count()):
                    other_item = self.list40.item(i)
                    if other_item.data(Qt.UserRole) == gift_id:
                        other_item.setCheckState(Qt.Unchecked)
                        self.level40_gifts.discard(gift_id)
                        break
            else:
                self.level60_gifts.discard(gift_id)

        elif sender == self.list180:
            if item.checkState() == Qt.Checked:
                self.level180_gifts.add(gift_id)
                for i in range(self.list240.count()):
                    other_item = self.list240.item(i)
                    if other_item.data(Qt.UserRole) == gift_id:
                        other_item.setCheckState(Qt.Unchecked)
                        self.level240_gifts.discard(gift_id)
                        break
            else:
                self.level180_gifts.discard(gift_id)

        elif sender == self.list240:
            if item.checkState() == Qt.Checked:
                self.level240_gifts.add(gift_id)
                for i in range(self.list180.count()):
                    other_item = self.list180.item(i)
                    if other_item.data(Qt.UserRole) == gift_id:
                        other_item.setCheckState(Qt.Unchecked)
                        self.level180_gifts.discard(gift_id)
                        break
            else:
                self.level240_gifts.discard(gift_id)

    def get_selected_gifts(self):
        return self.level40_gifts, self.level60_gifts, self.level180_gifts, self.level240_gifts
