#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QGridLayout, QScrollArea, QGroupBox, QTextEdit, QComboBox, QSpinBox, 
                             QCheckBox, QMenuBar, QMenu, QAction, QDialog, QWidget)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt
from utils import resource_path, get_gift_icon
from data_models import notna

class UIComponents:
    def __init__(self, parent):
        self.parent = parent

    def create_menu_bar(self):
        menubar = self.parent.menuBar()

        about_action = QAction('关于', self.parent)
        about_action.triggered.connect(self.parent.show_about)
        menubar.addAction(about_action)

        version_action = QAction('版本信息', self.parent)
        version_action.triggered.connect(self.parent.show_version)
        menubar.addAction(version_action)

        help_action = QAction('帮助', self.parent)
        help_action.triggered.connect(self.parent.show_help)
        menubar.addAction(help_action)

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
        self.parent.config_combo = QComboBox()
        self.parent.config_combo.setMinimumWidth(150)
        self.parent.config_combo.currentTextChanged.connect(self.parent.load_config)
        config_select_layout.addWidget(self.parent.config_combo)

        new_config_btn = QPushButton("新建")
        new_config_btn.clicked.connect(self.parent.create_new_config)
        config_select_layout.addWidget(new_config_btn)

        delete_config_btn = QPushButton("删除")
        delete_config_btn.clicked.connect(self.parent.delete_config)
        config_select_layout.addWidget(delete_config_btn)

        config_layout.addLayout(config_select_layout)

        start_group = QGroupBox("起始状态")
        start_layout = QVBoxLayout(start_group)

        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("当前等级:"))
        self.parent.level_input = QSpinBox()
        self.parent.level_input.setRange(1, 100)
        self.parent.level_input.setValue(1)
        self.parent.level_input.valueChanged.connect(self.parent.update_level)
        level_layout.addWidget(self.parent.level_input)

        level_layout.addWidget(QLabel("当前经验:"))
        self.parent.exp_input = QSpinBox()
        self.parent.exp_input.setRange(0, 999999)
        self.parent.exp_input.setValue(0)
        self.parent.exp_input.valueChanged.connect(self.parent.update_exp)
        level_layout.addWidget(self.parent.exp_input)

        start_layout.addLayout(level_layout)

        config_layout.addWidget(start_group)

        self.parent.is_linked_student_checkbox = QCheckBox("联动学生")
        self.parent.is_linked_student_checkbox.stateChanged.connect(self.parent.on_linked_student_toggled)
        config_layout.addWidget(self.parent.is_linked_student_checkbox)

        special_group = QGroupBox("特殊喜好礼物")
        special_layout = QVBoxLayout(special_group)

        self.parent.config_gifts_btn = QPushButton("配置特殊喜好礼物")
        self.parent.config_gifts_btn.clicked.connect(self.parent.configure_special_gifts)
        special_layout.addWidget(self.parent.config_gifts_btn)

        self.parent.special_gifts_layout = QVBoxLayout()
        special_layout.addLayout(self.parent.special_gifts_layout)

        special_layout.addStretch()
        config_layout.addWidget(special_group)

        layout.addWidget(config_group)

        button_group = QGroupBox("操作")
        button_layout = QVBoxLayout(button_group)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.parent.save_config)
        button_layout.addWidget(save_btn)

        load_btn = QPushButton("导入配置")
        load_btn.clicked.connect(self.parent.load_config_from_file)
        button_layout.addWidget(load_btn)

        import_group = QGroupBox("导入bacv文本（from Alice）")
        import_layout = QVBoxLayout(import_group)

        paste_btn = QPushButton("粘贴字符串")
        paste_btn.clicked.connect(self.parent.paste_from_clipboard)
        import_layout.addWidget(paste_btn)

        import_file_btn = QPushButton("导入文件")
        import_file_btn.clicked.connect(self.parent.import_from_file)
        import_layout.addWidget(import_file_btn)

        button_layout.addWidget(import_group)
        layout.addWidget(button_group)

        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)

        self.parent.result_text = QTextEdit()
        self.parent.result_text.setReadOnly(True)
        result_layout.addWidget(self.parent.result_text)

        layout.addWidget(result_group)

        return panel

    def create_right_panel(self):
        """创建右侧礼物面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 礼物网格
        gifts_widget = QWidget()
        self.parent.gifts_layout = QGridLayout(gifts_widget)
        self.parent.gifts_layout.setSpacing(10)

        # 加载礼物
        self.parent.load_gifts()

        scroll_area.setWidget(gifts_widget)

        layout = QVBoxLayout(panel)
        layout.addWidget(scroll_area)

        # 计算按钮
        calculate_btn = QPushButton("计算好感度")
        calculate_btn.clicked.connect(self.parent.calculate_favor)
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
        if self.parent.gifts_data is None:
            return

        # 清除现有布局
        while self.parent.gifts_layout.count():
            item = self.parent.gifts_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        self.parent.gift_inputs = {}
        row = 0
        col = 0

        for idx, gift in self.parent.gifts_data.iterrows():
            gift_frame = self.create_gift_item(gift)
            self.parent.gifts_layout.addWidget(gift_frame, row, col)

            col += 1
            if col >= 5:
                col = 0
                row += 1

    def create_gift_item(self, gift):
        """创建单个礼物项"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setFixedSize(200, 150)

        layout = QVBoxLayout(frame)

        try:
            gift_id = int(gift['ID']) if notna(gift['ID']) else 0
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

        gift_name = str(gift['礼物名']) if notna(gift['礼物名']) else "未知礼物"
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
        spin_box.valueChanged.connect(self.parent.on_gift_quantity_changed)

        input_layout.addWidget(spin_box)

        layout.addLayout(input_layout)

        try:
            gift_id = int(gift['ID']) if notna(gift['ID']) else None
            if gift_id is not None:
                self.parent.gift_inputs[gift_id] = {
                    'spinbox': spin_box,
                    'base_favor': int(gift.get('基础经验值', 0)) if notna(gift.get('基础经验值')) else 0,
                    'name': str(gift.get('礼物名', '')) if notna(gift.get('礼物名')) else '未知礼物'
                }
        except (ValueError, TypeError):
            pass

        return frame

    def update_special_gifts_display(self):
        """更新特殊礼物显示"""
        # 清除动态内容
        for i in reversed(range(self.parent.special_gifts_layout.count())):
            widget = self.parent.special_gifts_layout.itemAt(i).widget()
            if widget and isinstance(widget, (QGroupBox, QLabel)):
                widget.deleteLater()

        if not self.parent.current_config or self.parent.current_config not in self.parent.student_configs:
            return

        config = self.parent.student_configs[self.parent.current_config]

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

            self.parent.special_gifts_layout.addWidget(level20_group)

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

            self.parent.special_gifts_layout.addWidget(level120_group)

    def show_help(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("帮助")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>功能</h2>
        <ul>
        <li>配置学生特殊喜好礼物</li>
        <li>输入礼物数量并计算好感度升级</li>
        <li>支持联动学生模式</li>
        <li>支持通过bacv格式字符串导入库存，Alice用户可粘贴"ba导出bacv"得到的字符串一键导入库存</li>
        <li>保存/加载配置</li>
        </ul>
        
        <h2>使用</h2>
        <ul>
        <li>创建或加载配置</li>
        <li>配置特殊喜好（金/紫礼物）</li>
        <li>输入礼物数量</li>
        <li>点击计算查看结果</li>
        </ul>
        """)
        
        layout.addWidget(help_text)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()
