#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

def resource_path(relative_path, use_exe_dir_for_config=False):
    """
    自动识别当前运行环境（脚本 / PyInstaller / Nuitka Onefile），返回正确资源路径。
    """
    # ✅ 优先使用配置文件存放目录（例如用户配置）
    if use_exe_dir_for_config:
        return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), relative_path)

    # ✅ Nuitka onefile 模式
    if getattr(sys, "frozen", False):
        # Nuitka 在 onefile 模式下会设置这个
        base_path = os.environ.get("NUITKA_ONEFILE_TEMP", None)
        if base_path and os.path.exists(base_path):
            return os.path.join(base_path, relative_path)
        else:
            # 如果环境变量未设，退回 exe 同目录
            return os.path.join(os.path.dirname(sys.executable), relative_path)

    # ✅ 普通 Python 运行模式
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def get_gift_icon(gift_id):
    try:
        print(f"[DEBUG] 当前工作目录: {os.getcwd()}")
        print(f"[DEBUG] NUITKA_ONEFILE_TEMP: {os.environ.get('NUITKA_ONEFILE_TEMP')}")
        print(f"[DEBUG] sys.argv[0]: {sys.argv[0]}")
        
        image_path = resource_path(os.path.join("pic", f"{int(gift_id)}.jpg"))
        print(f"[DEBUG] 最终图片路径: {image_path}")
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

