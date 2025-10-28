#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from utils import resource_path

class ConfigManager:
    def __init__(self, parent):
        self.parent = parent

    def create_new_config(self):
        """创建新配置"""
        # 如果有当前配置且有未保存的更改，询问是否保存
        if self.parent.current_config and self.parent.config_modified:
            reply = QMessageBox.question(
                self.parent,
                "确认新建配置",
                f"当前配置 '{self.parent.current_config}' 有未保存的更改。\n\n是否在新建配置前保存当前配置？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_config()

        # 创建自定义对话框以支持占位符文本
        dialog = QDialog(self.parent)
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
            if name in self.parent.student_configs:
                QMessageBox.warning(self.parent, "警告", "配置名称已存在!")
                return

            self.parent.current_config = name
            self.parent.student_configs[name] = {
                'level20_gifts': set(),
                'level40_gifts': set(),
                'level60_gifts': set(),
                'level120_gifts': set(),
                'level180_gifts': set(),
                'level240_gifts': set(),
                'gift_quantities': {},
                'is_linked_student': False # 新增联动学生状态
            }

            # 保存当前的礼物数量到新配置
            current_gift_quantities = {}
            for gift_id, gift_info in self.parent.gift_inputs.items():
                spinbox = gift_info['spinbox']
                if spinbox is not None:
                    current_gift_quantities[gift_id] = spinbox.value()
            
            self.parent.student_configs[name]['gift_quantities'] = current_gift_quantities
            
            # 重置等级和经验为1级0经验
            self.parent.current_level = 1
            self.parent.current_exp = 0
            self.parent.level_input.blockSignals(True)
            self.parent.exp_input.blockSignals(True)
            self.parent.level_input.setValue(1)
            self.parent.exp_input.setValue(0)
            self.parent.level_input.blockSignals(False)
            self.parent.exp_input.blockSignals(False)

            self.parent.update_config_combo()
            # 确保下拉框显示新创建的配置
            self.parent.config_combo.setCurrentText(name)
            self.parent.update_special_gifts_display()
            self.parent.config_modified = False  # 新配置创建完成，标记为未修改

    def delete_config(self):
        if not self.parent.current_config:
            return

        reply = QMessageBox.question(self.parent, "确认删除",
                                   f"确定要删除配置 '{self.parent.current_config}' 吗?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.parent.student_configs[self.parent.current_config]
            self.parent.current_config = None
            self.parent.update_config_combo()
            self.parent.update_special_gifts_display()
            self.save_all_configs()

    def update_config_combo(self):
        """更新配置下拉框"""
        self.parent.config_combo.clear()
        for name in self.parent.student_configs.keys():
            self.parent.config_combo.addItem(name)

        if self.parent.current_config and self.parent.current_config in self.parent.student_configs:
            self.parent.config_combo.setCurrentText(self.parent.current_config)

    def load_config(self, config_name):
        """加载配置"""
        if not config_name or config_name not in self.parent.student_configs:
            return

        self.parent.current_config = config_name
        config = self.parent.student_configs[config_name]

        if 'gift_quantities' in config:
            for gift_id_str, qty in config['gift_quantities'].items():
                gift_id = int(gift_id_str)  # 将字符串转回整数
                if gift_id in self.parent.gift_inputs:
                    self.parent.gift_inputs[gift_id]['spinbox'].blockSignals(True)
                    self.parent.gift_inputs[gift_id]['spinbox'].setValue(qty)
                    self.parent.gift_inputs[gift_id]['spinbox'].blockSignals(False)

        if 'start_level' in config:
            self.parent.level_input.setValue(config['start_level'])
        if 'start_exp' in config:
            self.parent.exp_input.setValue(config['start_exp'])

        is_linked = config.get('is_linked_student', False)
        self.parent.is_linked_student_checkbox.setChecked(is_linked)
        self.parent.on_linked_student_toggled(Qt.Checked if is_linked else Qt.Unchecked)

        self.parent.update_special_gifts_display()
        self.parent.config_modified = False  # 配置已加载，标记为未修改

    def save_config(self):
        """保存当前配置"""
        if not self.parent.current_config:
            QMessageBox.warning(self.parent, "警告", "请先创建或选择一个配置!")
            return

        config_name = self.parent.current_config.strip()
        if not config_name:
            QMessageBox.warning(self.parent, "警告", "配置名称不能为空!")
            return

        config = self.parent.student_configs[self.parent.current_config]
        config['gift_quantities'] = {
            gift_id: self.parent.gift_inputs[gift_id]['spinbox'].value()
            for gift_id in self.parent.gift_inputs
            if self.parent.gift_inputs[gift_id]['spinbox'].value() > 0
        }

        config['start_level'] = self.parent.level_input.value()
        config['start_exp'] = self.parent.exp_input.value()
        config['is_linked_student'] = self.parent.is_linked_student_checkbox.isChecked()

        config_dir = resource_path("configs", use_exe_dir_for_config=True)
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, "config.json")

        def convert_sets(d):
            return {k: list(v) if isinstance(v, set) else v for k, v in d.items() if not k.startswith('_')}

        try:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
            except Exception:
                all_configs = {}

            all_configs[self.parent.current_config] = convert_sets(config)

            all_configs['_last_config'] = self.parent.current_config

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self.parent, "成功", f"配置 '{self.parent.current_config}' 已保存！")
            self.parent.config_modified = False  # 配置已保存，标记为未修改
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"保存配置失败:\n{e}")

    def save_all_configs(self):
        config_dir = resource_path("configs", use_exe_dir_for_config=True)
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "config.json")

        def convert_sets(d):
            return {k: list(v) if isinstance(v, set) else v for k, v in d.items() if not k.startswith('_')}

        try:
            all_configs = {}
            for config_name, config in self.parent.student_configs.items():
                all_configs[config_name] = convert_sets(config)
            
            if self.parent.current_config:
                all_configs['_last_config'] = self.parent.current_config

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"保存配置失败:\n{e}")

    def load_config_from_file(self):
        """从文件导入配置"""
        # 默认打开路径是exe所在目录的configs文件夹
        config_dir = resource_path("configs", use_exe_dir_for_config=True)
        os.makedirs(config_dir, exist_ok=True)

        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
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
                        if config_name not in self.parent.student_configs and isinstance(config_data, dict):
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
                            self.parent.student_configs[config_name] = converted_config
                            configs_loaded += 1

                        # 更新UI
                        self.parent.update_config_combo()

                    # 设置第一个新加载的配置为当前配置
                    if configs_loaded > 0:
                        first_new_config = list(file_data.keys())[0]
                        self.parent.current_config = first_new_config
                        self.parent.config_combo.setCurrentText(self.parent.current_config)
                        self.load_config(self.parent.current_config)

                        # 更新上次使用的配置记录
                        last_config_path = resource_path(os.path.join("configs", "last_config.json"), use_exe_dir_for_config=True)
                        with open(last_config_path, "w", encoding="utf-8") as f:
                            json.dump({'last_config': self.parent.current_config}, f, ensure_ascii=False, indent=2)

                    QMessageBox.information(self.parent, "成功", f"已加载 {configs_loaded} 个新配置！")

                else:
                    QMessageBox.warning(self.parent, "警告", "配置文件格式错误或为空！")

            except Exception as e:
                QMessageBox.critical(self.parent, "错误", f"加载配置文件失败:\n{str(e)}")

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
                    self.parent.student_configs = {
                        name: {
                            k: set(v) if isinstance(v, list) else v
                            for k, v in conf.items()
                        }
                        for name, conf in student_configs_data.items()
                    }

                    if self.parent.student_configs:
                        self.parent.current_config = last_config
                        self.parent.update_config_combo()
                        self.parent.update_special_gifts_display()
                        print(f"加载上次配置: {last_config}，共 {len(self.parent.student_configs)} 个配置")
                else:
                    # 如果没有last_config信息，加载所有配置
                    self.parent.student_configs = {
                        name: {
                            k: set(v) if isinstance(v, list) else v
                            for k, v in conf.items()
                        }
                        for name, conf in data.items()
                    }
                    if self.parent.student_configs:
                        self.parent.current_config = list(self.parent.student_configs.keys())[0]
                        self.parent.update_config_combo()
                        self.parent.update_special_gifts_display()
                        print(f"加载配置文件，共 {len(self.parent.student_configs)} 个配置")
        except Exception as e:
            QMessageBox.warning(self.parent, "警告", f"加载配置失败：{e}")
