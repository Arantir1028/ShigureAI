#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from version import __version__

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

from utils import resource_path
from gift_config_dialog import GiftConfigDialog
from data_models import load_csv_data
from version_manager import VersionManager
from import_manager import ImportManager
from config_manager import ConfigManager
from ui_components import UIComponents

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

        # 初始化各个管理器
        self.version_manager = VersionManager(self)
        self.import_manager = ImportManager(self)
        self.config_manager = ConfigManager(self)
        self.ui_components = UIComponents(self)

        self.init_data()
        self.init_ui()
        self.load_last_config()

    def init_data(self):
        """初始化数据"""
        try:
            self.gifts_data = load_csv_data(resource_path('giftID.csv'))
            print(f"加载了 {len(self.gifts_data)} 个礼物")

            self.levels_data = load_csv_data(resource_path('exp.csv'))
            print(f"加载了 {len(self.levels_data)} 个等级")

            # 预计算等级数据以提高性能
            self._precompute_levels()

            os.makedirs(resource_path("configs", use_exe_dir_for_config=True), exist_ok=True)
            config_file = os.path.join(resource_path("configs", use_exe_dir_for_config=True), "config.json")

            if not os.path.exists(config_file):
                with open(config_file, 'w', encoding='utf-8') as f:
                    import json
                    json.dump({}, f, ensure_ascii=False, indent=2)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据文件失败:\n{str(e)}")
            sys.exit(1)
    
    def _precompute_levels(self):
        """预计算等级数据以提高性能"""
        self.level_exp_cache = {}  # 等级 -> 所需经验的映射
        self.level_list = []  # 按等级排序的列表
        
        for _, level in self.levels_data.iterrows():
            level_num = int(level['当前等级'])
            exp_required = int(level['达到等级累计经验'])
            self.level_exp_cache[level_num] = exp_required
            self.level_list.append((level_num, exp_required))
        
        # 按等级排序
        self.level_list.sort(key=lambda x: x[0])
        print(f"预计算了 {len(self.level_list)} 个等级数据")

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"ShigureAI {__version__}")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setGeometry(100, 100, 1600, 900)

        self.ui_components.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = self.ui_components.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        right_panel = self.ui_components.create_right_panel()
        main_layout.addWidget(right_panel, 3)

    # 版本管理相关方法
    def show_about(self):
        self.version_manager.show_about()

    def show_version(self):
        self.version_manager.show_version()

    def show_help(self):
        self.ui_components.show_help()

    # 配置管理相关方法
    def create_new_config(self):
        self.config_manager.create_new_config()

    def delete_config(self):
        self.config_manager.delete_config()

    def update_config_combo(self):
        self.config_manager.update_config_combo()

    def load_config(self, config_name):
        self.config_manager.load_config(config_name)
        # 清除配置缓存，强制重新计算
        if hasattr(self, '_cached_config_state'):
            self._cached_config_state = None

    def save_config(self):
        self.config_manager.save_config()

    def save_all_configs(self):
        self.config_manager.save_all_configs()

    def load_config_from_file(self):
        self.config_manager.load_config_from_file()

    def load_last_config(self):
        self.config_manager.load_last_config()

    # 导入管理相关方法
    def paste_from_clipboard(self):
        self.import_manager.paste_from_clipboard()

    def import_from_file(self):
        self.import_manager.import_from_file()

    # UI组件相关方法
    def load_gifts(self):
        self.ui_components.load_gifts()

    def update_special_gifts_display(self):
        self.ui_components.update_special_gifts_display()

    # 核心计算逻辑
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
        # 如果有配置，标记为已修改
        if self.current_config:
            self.config_modified = True
        
        # 清除之前的定时器，避免重复计算
        if hasattr(self, '_calculate_timer'):
            self._calculate_timer.stop()
        
        # 延迟计算，避免频繁计算
        self._calculate_timer = QTimer()
        self._calculate_timer.setSingleShot(True)
        self._calculate_timer.timeout.connect(self.calculate_favor)
        self._calculate_timer.start(300)  # 减少延迟时间到300ms

    def calculate_favor(self):
        """计算好感度"""
        if not hasattr(self, 'level_exp_cache') or not self.level_exp_cache:
            return

        # 获取当前等级的累计经验（使用缓存）
        current_cumulative_exp = self.level_exp_cache.get(self.current_level, 0)

        # total_exp = 达到当前等级的总经验 + 当前等级内经验 + 礼物经验
        total_exp = current_cumulative_exp + self.current_exp

        # 计算所有礼物的经验
        for gift_id, gift_info in self.gift_inputs.items():
            spinbox = gift_info['spinbox']
            if spinbox is None or spinbox.value() <= 0:
                continue

            base_favor = gift_info['base_favor']
            actual_favor = self.get_actual_favor(gift_id, base_favor)
            total_exp += actual_favor * spinbox.value()

        # 使用二分查找找到目标等级
        target_level = self._find_target_level_binary(total_exp)

        # 计算结果显示
        result_text = f"当前状态: 等级 {self.current_level}, 经验 {self.current_exp}\n"
        result_text += f"使用礼物后获得经验: {total_exp - current_cumulative_exp - self.current_exp}\n"
        result_text += f"预计达到等级: {target_level}\n"

        # 检查是否还有下一等级
        if target_level < 100:
            next_level_exp = self.level_exp_cache.get(target_level + 1)
            if next_level_exp is not None:
                remaining_exp = next_level_exp - total_exp
                result_text += f"升级到 {target_level + 1} 级还需要经验: {remaining_exp}"
            else:
                result_text += "无下一等级数据"
        else:
            result_text += "已达到最高等级"

        self.result_text.setPlainText(result_text)
    
    def _find_target_level_binary(self, total_exp):
        """使用二分查找找到目标等级"""
        left, right = 0, len(self.level_list) - 1
        target_level = self.current_level
        
        while left <= right:
            mid = (left + right) // 2
            level_num, required_exp = self.level_list[mid]
            
            if required_exp <= total_exp:
                target_level = level_num
                left = mid + 1
            else:
                right = mid - 1
        
        return target_level

    def get_actual_favor(self, gift_id, base_favor):
        """获取礼物的实际好感度"""
        # 缓存当前配置状态，避免重复查找
        if not hasattr(self, '_cached_config_state'):
            self._cached_config_state = None
            self._cached_config = None
            self._cached_is_linked = False
        
        # 检查配置是否发生变化
        if self._cached_config_state != self.current_config:
            self._cached_config_state = self.current_config
            if self.current_config and self.current_config in self.student_configs:
                self._cached_config = self.student_configs[self.current_config]
                self._cached_is_linked = self._cached_config.get('is_linked_student', False)
            else:
                self._cached_config = None
                self._cached_is_linked = False
        if self.is_linked_student_checkbox is not None:
                    self._cached_is_linked = self.is_linked_student_checkbox.isChecked()

        # 联动学生特殊处理
        if self._cached_is_linked:
            return 20 if gift_id == 100008 else base_favor

        # 没有配置时直接返回基础好感度
        if not self._cached_config:
            return base_favor

        # 特殊喜好礼物处理
        if base_favor == 20:
            if gift_id in self._cached_config.get('level60_gifts', set()):
                return 60
            elif gift_id in self._cached_config.get('level40_gifts', set()):
                return 40
        elif base_favor == 120:
            if gift_id in self._cached_config.get('level240_gifts', set()):
                return 240
            elif gift_id in self._cached_config.get('level180_gifts', set()):
                return 180

        return base_favor

    def on_linked_student_toggled(self, state):
        """处理联动学生复选框切换"""
        is_linked = state == Qt.Checked
        # 启用/禁用配置特殊礼物按钮
        self.config_gifts_btn.setEnabled(not is_linked)

        # 如果没有当前配置，仍然需要重新计算
        if not self.current_config or self.current_config not in self.student_configs:
            # 重新计算以反映联动状态变化
            self.calculate_favor()
            return

        config = self.student_configs[self.current_config]

        if is_linked:
            # 保存当前特殊喜好到配置的临时储存，然后清空以实现"全部按基础好感"效果
            config['_previous_special_gifts'] = {
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
            if '_previous_special_gifts' in config:
                config['level40_gifts'] = config['_previous_special_gifts'].get('level40_gifts', set())
                config['level60_gifts'] = config['_previous_special_gifts'].get('level60_gifts', set())
                config['level180_gifts'] = config['_previous_special_gifts'].get('level180_gifts', set())
                config['level240_gifts'] = config['_previous_special_gifts'].get('level240_gifts', set())
                del config['_previous_special_gifts']  # 删除临时储存

        # **关键**：把 is_linked 状态写回当前 config，这样保存/加载时能保持状态一致
        config['is_linked_student'] = is_linked

        # 更新显示与计算
        self.update_special_gifts_display()
        self.calculate_favor()

        # 标记为修改
        self.config_modified = True

    def configure_special_gifts(self):
        """配置特殊喜好礼物"""
        try:
            if not self.current_config:
                QMessageBox.warning(self, "警告", "请先创建或选择一个配置!")
                return

            if self.is_linked_student_checkbox.isChecked():
                QMessageBox.information(self, "提示", "联动学生无法配置特殊喜好礼物。")
                return

            print(f"打开特殊喜好配置对话框，当前配置: {self.current_config}")
            dialog = GiftConfigDialog(self.gifts_data, self.current_config, self)
            print("对话框创建成功")
            
            result = dialog.exec_()
            print(f"对话框返回结果: {result}")
            
            if result == QDialog.Accepted:
                selected_40, selected_60, selected_180, selected_240 = dialog.get_selected_gifts()
                print(f"获取到选择的礼物: 40={len(selected_40)}, 60={len(selected_60)}, 180={len(selected_180)}, 240={len(selected_240)}")

                config = self.student_configs[self.current_config]
                config['level40_gifts'] = selected_40
                config['level60_gifts'] = selected_60
                config['level180_gifts'] = selected_180
                config['level240_gifts'] = selected_240

                self.config_modified = True

                self.update_special_gifts_display()
                self.calculate_favor()
                print("特殊喜好配置完成")
        except Exception as e:
            print(f"配置特殊喜好礼物时发生错误: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"配置特殊喜好礼物时发生错误:\n{str(e)}")

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
