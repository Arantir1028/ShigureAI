#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "v0.0.1"

import sys
import os
import json
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea,
                             QFrame, QGroupBox, QTextEdit, QFileDialog, QMessageBox,
                             QInputDialog, QComboBox, QSpinBox, QDialog, QCheckBox,
                             QTabWidget, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QTimer
import re

from utils import resource_path, get_gift_icon
from gift_config_dialog import GiftConfigDialog

class FavorCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gifts_data = None
        self.levels_data = None
        self.student_configs = {}
        self.current_config = None
        self.gift_inputs = {}
        self.current_level = 1
        self.current_exp = 0
        self.config_modified = False  # 跟踪配置是否被修改
        self.is_linked_student_checkbox = None
        self.previous_special_gifts = {}

        self.init_data()
        self.init_ui()
        self.load_last_config()

    def init_data(self):
        """初始化数据"""
        try:
            # 读取礼物数据
            self.gifts_data = pd.read_excel(resource_path('giftID.xlsx'))
            print(f"加载了 {len(self.gifts_data)} 个礼物")

            # 读取好感等级数据
            self.levels_data = pd.read_excel(resource_path('exp.xlsx'))
            print(f"加载了 {len(self.levels_data)} 个等级")

            # 确保 configs 目录存在（在exe目录下）
            os.makedirs(resource_path("configs", use_exe_dir_for_config=True), exist_ok=True)
            config_file = os.path.join(resource_path("configs", use_exe_dir_for_config=True), "config.json")

            if not os.path.exists(config_file):
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据文件失败:\n{str(e)}")
            sys.exit(1)

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"ShigureAI {__version__}")
        self.setWindowIcon(QIcon(resource_path("icon.jpg")))
        self.setGeometry(100, 100, 1200, 800)

        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)

    def create_menu_bar(self):
        """创建菜单栏"""
        from PyQt5.QtWidgets import QMenuBar, QMenu, QAction

        # 创建菜单栏
        menubar = self.menuBar()

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        # 关于动作
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 版本动作
        version_action = QAction('版本信息', self)
        version_action.triggered.connect(self.show_version)
        help_menu.addAction(version_action)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于",
                         f"<h2>ShigureAI</h2>"
                         f"<p><strong>版本:</strong> {__version__}</p>"
                         f"<p>这是一个用于计算《蔚蓝档案》游戏中学生好感度的工具。</p>"
                         f"<p>支持特殊喜好礼物配置、批量导入和计算预计等级。</p>"
                         f"<p><strong>作者:</strong> 学识 @ <a href='https://space.bilibili.com/127207268?spm_id_from=333.1007.0.0'>Arantir_</a></p>"
                         f"<p><strong>许可证:</strong> GPL-3.0</p>")

    def show_version(self):
        """显示版本信息"""
        QMessageBox.information(self, "版本信息",
                               f"当前版本: {__version__}\n\n"
                               f"这是ShigureAI {__version__}，包含以下功能：\n"
                               f"• 支持学生特殊喜好礼物配置\n"
                               f"• 支持批量导入和计算好感度升级\n"
                               f"• 支持保存/加载配置\n")

    def create_left_panel(self):
        """创建左侧配置面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(panel)

        config_group = QGroupBox()
        config_layout = QVBoxLayout(config_group)

        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("学生特殊喜好配置")
        title_label.setFont(QFont("Arial", 10))
        title_bar.addWidget(title_label)

        title_bar.addStretch()

        author_label = QLabel('学识 @ <a href="https://space.bilibili.com/127207268?spm_id_from=333.1007.0.0">Arantir_</a>')
        author_label.setOpenExternalLinks(True)
        author_label.setTextFormat(Qt.RichText)
        author_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        author_label.setStyleSheet("color: gray; font-size: 12px;")
        title_bar.addWidget(author_label, alignment=Qt.AlignRight)

        config_layout.addLayout(title_bar)

        config_select_layout = QHBoxLayout()
        config_select_layout.addWidget(QLabel("配置:"))
        self.config_combo = QComboBox()
        self.config_combo.setMinimumWidth(150)
        self.config_combo.currentTextChanged.connect(self.load_config)
        config_select_layout.addWidget(self.config_combo)

        new_config_btn = QPushButton("新建")
        new_config_btn.clicked.connect(self.create_new_config)
        config_select_layout.addWidget(new_config_btn)

        delete_config_btn = QPushButton("删除")
        delete_config_btn.clicked.connect(self.delete_config)
        config_select_layout.addWidget(delete_config_btn)

        config_layout.addLayout(config_select_layout)

        start_group = QGroupBox("起始状态")
        start_layout = QVBoxLayout(start_group)

        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("当前等级:"))
        self.level_input = QSpinBox()
        self.level_input.setRange(1, 100)
        self.level_input.setValue(1)
        self.level_input.valueChanged.connect(self.update_level)
        level_layout.addWidget(self.level_input)

        level_layout.addWidget(QLabel("当前经验:"))
        self.exp_input = QSpinBox()
        self.exp_input.setRange(0, 999999)
        self.exp_input.setValue(0)
        self.exp_input.valueChanged.connect(self.update_exp)
        level_layout.addWidget(self.exp_input)

        start_layout.addLayout(level_layout)

        config_layout.addWidget(start_group)

        self.is_linked_student_checkbox = QCheckBox("联动学生")
        self.is_linked_student_checkbox.stateChanged.connect(self.on_linked_student_toggled)
        config_layout.addWidget(self.is_linked_student_checkbox)

        special_group = QGroupBox("特殊喜好礼物")
        special_layout = QVBoxLayout(special_group)

        self.config_gifts_btn = QPushButton("配置特殊喜好礼物")
        self.config_gifts_btn.clicked.connect(self.configure_special_gifts)
        special_layout.addWidget(self.config_gifts_btn)

        self.special_gifts_layout = QVBoxLayout()
        special_layout.addLayout(self.special_gifts_layout)

        special_layout.addStretch()
        config_layout.addWidget(special_group)

        layout.addWidget(config_group)

        button_group = QGroupBox("操作")
        button_layout = QVBoxLayout(button_group)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        load_btn = QPushButton("导入配置")
        load_btn.clicked.connect(self.load_config_from_file)
        button_layout.addWidget(load_btn)

        import_group = QGroupBox("导入bacv文本（from Alice）")
        import_layout = QVBoxLayout(import_group)

        paste_btn = QPushButton("粘贴字符串")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        import_layout.addWidget(paste_btn)

        import_file_btn = QPushButton("导入文件")
        import_file_btn.clicked.connect(self.import_from_file)
        import_layout.addWidget(import_file_btn)

        button_layout.addWidget(import_group)
        layout.addWidget(button_group)

        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        layout.addWidget(result_group)

        return panel

    def create_right_panel(self):
        """创建右侧礼物面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 礼物网格布局
        gifts_widget = QWidget()
        self.gifts_layout = QGridLayout(gifts_widget)
        self.gifts_layout.setSpacing(10)

        # 加载礼物
        self.load_gifts()

        scroll_area.setWidget(gifts_widget)

        layout = QVBoxLayout(panel)
        layout.addWidget(scroll_area)

        # 计算按钮
        calculate_btn = QPushButton("计算好感度")
        calculate_btn.clicked.connect(self.calculate_favor)
        layout.addWidget(calculate_btn)

        return panel

    def create_gift_image_label(self, gift_id):
        """创建礼物图片标签"""
        image_path = resource_path(os.path.join("pic", f"{gift_id}.jpg"))
        label = QLabel()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
        else:
            label.setText(str(gift_id))
            label.setStyleSheet("color: gray;")
        label.setFixedSize(24, 24)
        return label

    def load_gifts(self):
        """加载礼物显示"""
        if self.gifts_data is None:
            return

        # 清除现有布局（使用标准的清理方式）
        while self.gifts_layout.count():
            item = self.gifts_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        self.gift_inputs = {}
        row = 0
        col = 0

        for idx, gift in self.gifts_data.iterrows():
            gift_frame = self.create_gift_item(gift)
            self.gifts_layout.addWidget(gift_frame, row, col)

            col += 1
            if col >= 4:  # 每行4个礼物
                col = 0
                row += 1

    def create_gift_item(self, gift):
        """创建单个礼物项"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setFixedSize(200, 150)

        layout = QVBoxLayout(frame)

        try:
            gift_id = int(gift['ID']) if pd.notna(gift['ID']) else 0
            image_path = resource_path(os.path.join("pic", f"{gift_id}.jpg"))
            print(f"主界面加载图片: {gift_id}, 路径: {image_path}, 存在: {os.path.exists(image_path)}")
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                print(f"主界面Pixmap创建成功: {not pixmap.isNull()}, 大小: {pixmap.size()}")
                pixmap = pixmap.scaled(120, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(image_label)
            else:
                placeholder_label = QLabel("无图片")
                placeholder_label.setAlignment(Qt.AlignCenter)
                placeholder_label.setStyleSheet("color: gray; font-size: 12px;")
                layout.addWidget(placeholder_label)
        except (ValueError, TypeError) as e:
            print(f"主界面加载图片错误 {gift_id}: {e}")
            placeholder_label = QLabel("无效ID")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("color: gray; font-size: 12px;")
            layout.addWidget(placeholder_label)

        gift_name = str(gift['礼物名']) if pd.notna(gift['礼物名']) else "未知礼物"
        name_label = QLabel(gift_name)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setMaximumHeight(30)
        layout.addWidget(name_label)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("数量:"))

        spin_box = QSpinBox()
        spin_box.setRange(0, 999999)
        spin_box.setValue(0)
        spin_box.setFocusPolicy(Qt.StrongFocus)  # 禁用鼠标滚轮
        spin_box.wheelEvent = lambda event: None  # 禁用滚轮事件
        spin_box.valueChanged.connect(self.on_gift_quantity_changed)

        input_layout.addWidget(spin_box)

        layout.addLayout(input_layout)

        try:
            gift_id = int(gift['ID']) if pd.notna(gift['ID']) else None
            if gift_id is not None:
                self.gift_inputs[gift_id] = {
                    'spinbox': spin_box,
                    'base_favor': int(gift.get('基础经验值', 0)) if pd.notna(gift.get('基础经验值')) else 0,
                    'name': str(gift.get('礼物名', '')) if pd.notna(gift.get('礼物名')) else '未知礼物'
                }
        except (ValueError, TypeError):
            pass

        return frame

    def create_new_config(self):
        """创建新配置"""
        # 如果有当前配置且有未保存的更改，询问是否保存
        if self.current_config and self.config_modified:
            reply = QMessageBox.question(
                self,
                "确认新建配置",
                f"当前配置 '{self.current_config}' 有未保存的更改。\n\n是否在新建配置前保存当前配置？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_config()

        # 创建自定义对话框以支持占位符文本
        dialog = QDialog(self)
        dialog.setWindowTitle("新建配置")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        label = QLabel("请输入配置名称:")
        layout.addWidget(label)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("建议使用学生姓名")
        layout.addWidget(line_edit)

        button_layout = QHBoxLayout()

        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            name = line_edit.text()
            ok = True
        else:
            name = ""
            ok = False
        if ok and name:
            if name in self.student_configs:
                QMessageBox.warning(self, "警告", "配置名称已存在!")
                return

            self.current_config = name
            self.student_configs[name] = {
                'level20_gifts': set(),
                'level40_gifts': set(),
                'level60_gifts': set(),
                'level120_gifts': set(),
                'level180_gifts': set(),
                'level240_gifts': set(),
                'gift_quantities': {},
                'is_linked_student': False # 新增联动学生状态
            }

            # 重置等级和经验为1级0经验
            self.current_level = 1
            self.current_exp = 0
            self.level_input.blockSignals(True)
            self.exp_input.blockSignals(True)
            self.level_input.setValue(1)
            self.exp_input.setValue(0)
            self.level_input.blockSignals(False)
            self.exp_input.blockSignals(False)

            self.update_config_combo()
            # 确保下拉框显示新创建的配置
            self.config_combo.setCurrentText(name)
            self.update_special_gifts_display()
            self.config_modified = False  # 新配置创建完成，标记为未修改

    def delete_config(self):
        """删除配置"""
        if not self.current_config:
            return

        reply = QMessageBox.question(self, "确认删除",
                                   f"确定要删除配置 '{self.current_config}' 吗?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.student_configs[self.current_config]
            self.current_config = None
            self.update_config_combo()
            self.update_special_gifts_display()

            self.save_config()

    def update_config_combo(self):
        """更新配置下拉框"""
        self.config_combo.clear()
        for name in self.student_configs.keys():
            self.config_combo.addItem(name)

        if self.current_config and self.current_config in self.student_configs:
            self.config_combo.setCurrentText(self.current_config)

    def load_config(self, config_name):
        """加载配置"""
        if not config_name or config_name not in self.student_configs:
            return

        self.current_config = config_name
        config = self.student_configs[config_name]

        if 'gift_quantities' in config:
            for gift_id_str, qty in config['gift_quantities'].items():
                gift_id = int(gift_id_str)  # 将字符串转回整数
                if gift_id in self.gift_inputs:
                    self.gift_inputs[gift_id]['spinbox'].blockSignals(True)
                    self.gift_inputs[gift_id]['spinbox'].setValue(qty)
                    self.gift_inputs[gift_id]['spinbox'].blockSignals(False)

        if 'start_level' in config:
            self.level_input.setValue(config['start_level'])
        if 'start_exp' in config:
            self.exp_input.setValue(config['start_exp'])

        is_linked = config.get('is_linked_student', False)
        self.is_linked_student_checkbox.setChecked(is_linked)
        self.on_linked_student_toggled(Qt.Checked if is_linked else Qt.Unchecked)

        self.update_special_gifts_display()
        self.config_modified = False  # 配置已加载，标记为未修改

    def update_special_gifts_display(self):
        """更新特殊礼物显示"""
        # 清除现有动态内容（只删除QGroupBox和QLabel，不删除按钮）
        for i in reversed(range(self.special_gifts_layout.count())):
            widget = self.special_gifts_layout.itemAt(i).widget()
            if widget and isinstance(widget, (QGroupBox, QLabel)):
                widget.deleteLater()

        if not self.current_config or self.current_config not in self.student_configs:
            return

        config = self.student_configs[self.current_config]

        # 金礼物
        if config['level20_gifts'] or config['level40_gifts'] or config['level60_gifts']:
            level20_group = QGroupBox("金礼物")
            level20_layout = QVBoxLayout(level20_group)

            # 40经验礼物
            if config['level40_gifts']:
                level40_hbox = QHBoxLayout()
                level40_hbox.addWidget(QLabel("40经验礼物:"))
                for gift_id in config['level40_gifts']:
                    level40_hbox.addWidget(self.create_gift_image_label(gift_id))
                level40_hbox.addStretch()
                level20_layout.addLayout(level40_hbox)

            # 60经验礼物
            if config['level60_gifts']:
                level60_hbox = QHBoxLayout()
                level60_hbox.addWidget(QLabel("60经验礼物:"))
                for gift_id in config['level60_gifts']:
                    level60_hbox.addWidget(self.create_gift_image_label(gift_id))
                level60_hbox.addStretch()
                level20_layout.addLayout(level60_hbox)

            self.special_gifts_layout.addWidget(level20_group)

        # 紫礼物
        if config['level120_gifts'] or config['level180_gifts'] or config['level240_gifts']:
            level120_group = QGroupBox("紫礼物")
            level120_layout = QVBoxLayout(level120_group)

            # 180经验礼物
            if config['level180_gifts']:
                level180_hbox = QHBoxLayout()
                level180_hbox.addWidget(QLabel("180经验礼物:"))
                for gift_id in config['level180_gifts']:
                    level180_hbox.addWidget(self.create_gift_image_label(gift_id))
                level180_hbox.addStretch()
                level120_layout.addLayout(level180_hbox)

            # 240经验礼物
            if config['level240_gifts']:
                level240_hbox = QHBoxLayout()
                level240_hbox.addWidget(QLabel("240经验礼物:"))
                for gift_id in config['level240_gifts']:
                    level240_hbox.addWidget(self.create_gift_image_label(gift_id))
                level240_hbox.addStretch()
                level120_layout.addLayout(level240_hbox)

            self.special_gifts_layout.addWidget(level120_group)

    def update_level(self, level):
        """更新等级"""
        self.current_level = level
        self.current_exp = 0
        self.exp_input.setValue(0)
        self.config_modified = True  # 标记配置已修改
        self.calculate_favor()

    def update_exp(self, exp):
        """更新经验"""
        self.current_exp = exp
        self.config_modified = True  # 标记配置已修改
        self.calculate_favor()

    def on_gift_quantity_changed(self):
        """礼物数量改变时自动计算"""
        self.config_modified = True  # 标记配置已修改
        QTimer.singleShot(500, self.calculate_favor)  # 延迟500ms计算，避免频繁计算

    def calculate_favor(self):
        """计算好感度"""
        if self.levels_data is None or self.gifts_data is None:
            return

        # 获取当前等级的累计经验（从1级到当前等级的总经验）
        current_level_row = self.levels_data.loc[self.levels_data['当前等级'] == self.current_level]
        if not current_level_row.empty:
            # 达到当前等级所需的总经验
            current_cumulative_exp = current_level_row.iloc[0]['达到等级累计经验']
        else:
            current_cumulative_exp = 0

        # total_exp = 达到当前等级的总经验 + 当前等级内经验 + 礼物经验
        total_exp = current_cumulative_exp + self.current_exp

        # 计算所有礼物的经验
        for gift_id, gift_info in self.gift_inputs.items():
            spinbox = gift_info['spinbox']
            if spinbox is None:
                continue
            quantity = spinbox.value()
            if quantity <= 0:
                continue

            base_favor = gift_info['base_favor']
            actual_favor = self.get_actual_favor(gift_id, base_favor)
            total_exp += actual_favor * quantity

        # 计算能达到的等级
        target_level = self.current_level

        # 从当前等级开始向上查找能达到的最高等级
        for level in range(self.current_level, 101):  # 从当前等级到100级
            level_row = self.levels_data.loc[self.levels_data['当前等级'] == level]
            if not level_row.empty:
                if total_exp >= level_row.iloc[0]['达到等级累计经验']:
                    target_level = level
                else:
                    break
            else:
                break

        # 计算结果显示
        result_text = f"当前状态: 等级 {self.current_level}, 经验 {self.current_exp}\n"
        result_text += f"使用礼物后获得经验: {total_exp - current_cumulative_exp - self.current_exp}\n"
        result_text += f"预计达到等级: {target_level}\n"

        # 检查是否还有下一等级
        if target_level < 100:
            next_level_rows = self.levels_data.loc[self.levels_data['当前等级'] == target_level + 1, '达到等级累计经验']
            if not next_level_rows.empty:
                next_level_exp = next_level_rows.iloc[0]
                remaining_exp = next_level_exp - total_exp
                result_text += f"升级到 {target_level + 1} 级还需要经验: {remaining_exp}"
            else:
                result_text += "无下一等级数据"
        else:
            result_text += "已达到最高等级"

        self.result_text.setPlainText(result_text)

    def get_actual_favor(self, gift_id, base_favor):
        """获取礼物的实际好感度"""
        is_linked = False
        if self.is_linked_student_checkbox is not None:
            is_linked = self.is_linked_student_checkbox.isChecked()
        if self.current_config not in self.student_configs:
            print(f"get_actual_favor: no current_config -> gift_id={gift_id}, base_favor={base_favor}, is_linked={is_linked}")
            if is_linked and gift_id == 100008:
                return 20
            return base_favor

        config = self.student_configs[self.current_config]
        cfg_is_linked = config.get('is_linked_student', False)
        print(f"get_actual_favor: gift_id={gift_id}, base_favor={base_favor}, checkbox_is_linked={is_linked}, config_is_linked={cfg_is_linked}")

        if is_linked:
            if gift_id == 100008:
                return 20
            return base_favor

        if base_favor == 20:
            if gift_id in config.get('level60_gifts', set()):
                return 60
            elif gift_id in config.get('level40_gifts', set()):
                return 40
        elif base_favor == 120:
            if gift_id in config.get('level240_gifts', set()):
                return 240
            elif gift_id in config.get('level180_gifts', set()):
                return 180

        return base_favor

    def on_linked_student_toggled(self, state):
        """处理联动学生复选框切换"""
        is_linked = state == Qt.Checked
        # 启用/禁用配置特殊礼物按钮
        self.config_gifts_btn.setEnabled(not is_linked)

        # 如果没有当前配置，只更新 UI 状态
        if not self.current_config or self.current_config not in self.student_configs:
            # 仍然保存状态到 checkbox（已由系统做），不再其他处理
            return

        config = self.student_configs[self.current_config]

        if is_linked:
            # 保存当前特殊喜好到临时储存，然后清空以实现“全部按基础好感”效果
            self.previous_special_gifts = {
                'level40_gifts': config.get('level40_gifts', set()).copy(),
                'level60_gifts': config.get('level60_gifts', set()).copy(),
                'level180_gifts': config.get('level180_gifts', set()).copy(),
                'level240_gifts': config.get('level240_gifts', set()).copy()
            }
            config['level40_gifts'] = set()
            config['level60_gifts'] = set()
            config['level180_gifts'] = set()
            config['level240_gifts'] = set()
        else:
            # 恢复之前保存的特殊喜好（如果有）
            if self.previous_special_gifts:
                config['level40_gifts'] = self.previous_special_gifts.get('level40_gifts', set())
                config['level60_gifts'] = self.previous_special_gifts.get('level60_gifts', set())
                config['level180_gifts'] = self.previous_special_gifts.get('level180_gifts', set())
                config['level240_gifts'] = self.previous_special_gifts.get('level240_gifts', set())
                self.previous_special_gifts = {}

        # **关键**：把 is_linked 状态写回当前 config，这样保存/加载时能保持状态一致
        config['is_linked_student'] = is_linked

        # 更新显示与计算
        self.update_special_gifts_display()
        self.calculate_favor()

        # 标记为修改
        self.config_modified = True

    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            QMessageBox.warning(self, "警告", "剪贴板为空!")
            return

        self.parse_import_data(text)

    def import_from_file(self):
        """从文件导入"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择导入文件", "", "Text Files (*.txt);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.parse_import_data(content)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"读取文件失败:\n{str(e)}")

    def parse_import_data(self, content):
        """解析导入数据"""
        try:
            data = json.loads(content)
            if isinstance(data, list) and len(data) > 0 and 'item' in data[0]:
                items = data[0]['item']
                self.import_gift_quantities(items)
            else:
                self.parse_with_regex(content)
        except:
            self.parse_with_regex(content)

    def parse_with_regex(self, content):
        """使用正则表达式解析"""
        # 查找类似 "id": 1234, "number": 5 的模式（支持单双引号，更宽松的格式）
        pattern = r"""['"]?id['"]?\s*:\s*([0-9]+).*?['"]?number['"]?\s*:\s*([0-9]+)"""
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

        if matches:
            items = [{'id': int(id_str), 'number': int(num_str)} for id_str, num_str in matches]
            self.import_gift_quantities(items)
        else:
            QMessageBox.warning(self, "警告", "无法解析数据格式!")

    def import_gift_quantities(self, items):
        """导入礼物数量"""
        imported_count = 0

        for item in items:
            gift_id = item['id']
            quantity = item['number']

            if gift_id in self.gift_inputs:
                self.gift_inputs[gift_id]['spinbox'].setValue(quantity)
                imported_count += 1

        QMessageBox.information(self, "导入完成", f"成功导入 {imported_count} 个礼物的数量")

        # 自动计算
        self.calculate_favor()

    def save_config(self):
        """保存当前配置"""
        if not self.current_config:
            QMessageBox.warning(self, "警告", "请先创建或选择一个配置!")
            return

        config_name = self.current_config.strip()
        if not config_name:
            QMessageBox.warning(self, "警告", "配置名称不能为空!")
            return

        config = self.student_configs[self.current_config]
        config['gift_quantities'] = {
            gift_id: self.gift_inputs[gift_id]['spinbox'].value()
            for gift_id in self.gift_inputs
            if self.gift_inputs[gift_id]['spinbox'].value() > 0
        }

        config['start_level'] = self.level_input.value()
        config['start_exp'] = self.exp_input.value()
        config['is_linked_student'] = self.is_linked_student_checkbox.isChecked()

        config_dir = resource_path("configs", use_exe_dir_for_config=True)
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, "config.json")

        def convert_sets(d):
            return {k: list(v) if isinstance(v, set) else v for k, v in d.items()}

        try:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
            except Exception:
                all_configs = {}

            all_configs[self.current_config] = convert_sets(config)

            all_configs['_last_config'] = self.current_config

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "成功", f"配置 '{self.current_config}' 已保存！")
            self.config_modified = False  # 配置已保存，标记为未修改
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{e}")

    def load_config_from_file(self):
        """从文件导入配置"""
        # 默认打开路径是exe所在目录的configs文件夹
        config_dir = resource_path("configs", use_exe_dir_for_config=True)
        os.makedirs(config_dir, exist_ok=True)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择配置文件",
            config_dir,
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)

                # 检查文件是否包含多个配置（键值对形式）
                if isinstance(file_data, dict) and len(file_data) > 0:
                    # 文件包含多个配置
                    configs_loaded = 0
                    for config_name, config_data in file_data.items():
                        if config_name not in self.student_configs and isinstance(config_data, dict):
                            # 转换集合格式（列表转回集合）
                            converted_config = {
                                'level20_gifts': set(config_data.get('level20_gifts', [])),
                                'level40_gifts': set(config_data.get('level40_gifts', [])),
                                'level60_gifts': set(config_data.get('level60_gifts', [])),
                                'level120_gifts': set(config_data.get('level120_gifts', [])),
                                'level180_gifts': set(config_data.get('level180_gifts', [])),
                                'level240_gifts': set(config_data.get('level240_gifts', [])),
                                'gift_quantities': config_data.get('gift_quantities', {}),
                                'is_linked_student': config_data.get('is_linked_student', False) # 加载联动学生状态
                            }
                            self.student_configs[config_name] = converted_config
                            configs_loaded += 1

                    # 更新UI
                    self.update_config_combo()

                    # 设置第一个新加载的配置为当前配置
                    if configs_loaded > 0:
                        first_new_config = list(file_data.keys())[0]
                        self.current_config = first_new_config
                        self.config_combo.setCurrentText(self.current_config)
                        self.load_config(self.current_config)

                        # 更新上次使用的配置记录
                        last_config_path = resource_path(os.path.join("configs", "last_config.json"), use_exe_dir_for_config=True)
                        with open(last_config_path, "w", encoding="utf-8") as f:
                            json.dump({'last_config': self.current_config}, f, ensure_ascii=False, indent=2)

                    QMessageBox.information(self, "成功", f"已加载 {configs_loaded} 个新配置！")

                else:
                    QMessageBox.warning(self, "警告", "配置文件格式错误或为空！")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置文件失败:\n{str(e)}")

    def configure_special_gifts(self):
        """配置特殊喜好礼物"""
        if not self.current_config:
            QMessageBox.warning(self, "警告", "请先创建或选择一个配置!")
            return

        if self.is_linked_student_checkbox.isChecked():
            QMessageBox.information(self, "提示", "联动学生无法配置特殊喜好礼物。")
            return

        dialog = GiftConfigDialog(self.gifts_data, self.current_config, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_40, selected_60, selected_180, selected_240 = dialog.get_selected_gifts()

            config = self.student_configs[self.current_config]
            config['level40_gifts'] = selected_40
            config['level60_gifts'] = selected_60
            config['level180_gifts'] = selected_180
            config['level240_gifts'] = selected_240

            self.config_modified = True  # 标记配置已修改

            self.update_special_gifts_display()
            self.calculate_favor()

    def load_last_config(self):
        """启动时加载已有配置"""
        try:
            config_file = resource_path(os.path.join("configs", "config.json"), use_exe_dir_for_config=True)
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                            data = json.load(f)

                # 检查是否有last_config信息
                last_config = data.get('_last_config')
                if last_config and last_config in data:
                    # 排除_last_config键，只加载学生配置
                    student_configs_data = {k: v for k, v in data.items() if k != '_last_config'}

                    # 把 list 转回 set
                    self.student_configs = {
                        name: {
                            k: set(v) if isinstance(v, list) else v
                            for k, v in conf.items()
                        }
                        for name, conf in student_configs_data.items()
                    }

                    if self.student_configs:
                        self.current_config = last_config
                        self.update_config_combo()
                        self.update_special_gifts_display()
                        print(f"加载上次配置: {last_config}，共 {len(self.student_configs)} 个配置")
                else:
                    # 如果没有last_config信息，加载所有配置
                    self.student_configs = {
                        name: {
                            k: set(v) if isinstance(v, list) else v
                            for k, v in conf.items()
                        }
                        for name, conf in data.items()
                    }
                    if self.student_configs:
                        self.current_config = list(self.student_configs.keys())[0]
                        self.update_config_combo()
                        self.update_special_gifts_display()
                        print(f"加载配置文件，共 {len(self.student_configs)} 个配置")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置失败：{e}")

def main():
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式

    window = FavorCalculator()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
