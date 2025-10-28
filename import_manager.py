#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import QTimer

class ImportManager:
    def __init__(self, parent):
        self.parent = parent

    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            QMessageBox.warning(self.parent, "警告", "剪贴板为空!")
            return

        self.parse_import_data(text)

    def import_from_file(self):
        """从文件导入"""
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "选择导入文件", "", "Text Files (*.txt);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.parse_import_data(content)
            except Exception as e:
                QMessageBox.critical(self.parent, "错误", f"读取文件失败:\n{str(e)}")

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
        """正则解析导入文本"""
        # 查找类似 "id": 1234, "number": 5 的模式（支持单双引号，更宽松的格式）
        pattern = r"""['"]?id['"]?\s*:\s*([0-9]+).*?['"]?number['"]?\s*:\s*([0-9]+)"""
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

        if matches:
            items = [{'id': int(id_str), 'number': int(num_str)} for id_str, num_str in matches]
            self.import_gift_quantities(items)
        else:
            QMessageBox.warning(self.parent, "警告", "无法解析数据格式!")

    def import_gift_quantities(self, items):
        """导入礼物数量"""
        imported_count = 0

        for item in items:
            gift_id = item['id']
            quantity = item['number']

            if gift_id in self.parent.gift_inputs:
                self.parent.gift_inputs[gift_id]['spinbox'].setValue(quantity)
                imported_count += 1

        QMessageBox.information(self.parent, "导入完成", f"成功导入 {imported_count} 个礼物的数量")

        # 自动计算
        self.parent.calculate_favor()
