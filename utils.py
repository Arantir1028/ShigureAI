#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

def resource_path(relative_path, use_exe_dir_for_config=False):
    """返回资源路径，适配脚本与打包环境"""
    # 配置类文件使用可执行文件目录
    if use_exe_dir_for_config:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), relative_path)

    # 打包运行
    if getattr(sys, "frozen", False):
        base_path = os.environ.get("NUITKA_ONEFILE_TEMP", None)
        if base_path and os.path.exists(base_path):
            return os.path.join(base_path, relative_path)
        else:
            # 退回到 exe 同目录
            return os.path.join(os.path.dirname(sys.executable), relative_path)

    # 脚本运行
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_gift_icon(gift_id):
    try:
        image_path = resource_path(os.path.join("pic", f"{int(gift_id)}.jpg"))
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return QIcon(pixmap)
        else:
            pass
    except (ValueError, TypeError, OSError) as e:
        pass
    return QIcon()

