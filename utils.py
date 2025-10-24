#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

def resource_path(relative_path, use_exe_dir_for_config=False):
    """
    获取资源路径：
    - 普通资源：兼容打包与非打包
    - 配置文件：始终放在 exe 同目录下
    """
    if use_exe_dir_for_config:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.join(base_path, relative_path)

def get_gift_icon(gift_id):
    """获取礼物图标"""
    try:
        image_path = resource_path(os.path.join("pic", f"{int(gift_id)}.jpg"))
        print(f"加载礼物图标: {gift_id}, 路径: {image_path}, 存在: {os.path.exists(image_path)}")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            print(f"Pixmap 创建成功: {not pixmap.isNull()}, 大小: {pixmap.size()}")
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return QIcon(pixmap)
        else:
            print(f"警告：找不到图片文件 {image_path}")
    except (ValueError, TypeError, OSError) as e:
        print(f"错误加载图片 {gift_id}: {e}")
    return QIcon()

