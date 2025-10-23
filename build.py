#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "v0.0.1"

import os
import sys
import subprocess
import platform

def build_executable():
    """打包可执行文件"""
    print("开始打包可执行文件...")
    sep = ';' if platform.system() == 'Windows' else ':'

    required_files = ['favor_calculator.py', 'giftID.xlsx', 'exp.xlsx', 'icon.jpg', 'bacv.txt']
    required_dirs = ['pic']

    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 错误: 找不到必要文件 {file}")
            return False

    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 错误: 找不到必要目录 {dir_name}")
            return False

    cmd = [
        'pyinstaller',
        f'--name=ShigureAI_{__version__}',
        '--onefile',
        '--windowed',
        '--icon=icon.jpg',
        f'--add-data=giftID.xlsx{sep}.',
        f'--add-data=exp.xlsx{sep}.',
        f'--add-data=icon.jpg{sep}.',
        f'--add-data=bacv.txt{sep}.',
        f'--add-data=pic;pic',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=openpyxl',
        '--hidden-import=Pillow',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtCore',
        '--exclude-module=tkinter',
        '--exclude-module=turtle',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--clean',
        '--noconfirm',
        'favor_calculator.py'
    ]

    print("执行 PyInstaller 命令：")
    print(' '.join(cmd))

    try:
        subprocess.run(cmd, check=True)
        print("✅ 打包成功！")
        print(f"📦 生成文件: dist/ShigureAI_{__version__}.exe")
        return True
    except subprocess.CalledProcessError:
        print("❌ 打包失败")
        return False

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    try:
        import PyQt5, pandas, openpyxl, PIL
        print("✅ 所有依赖都已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False

if __name__ == "__main__":
    print(f"=== PyInstaller 打包工具 {__version__} ===\n")

    if not check_dependencies():
        print("请先安装必要依赖：")
        print("pip install PyQt5 pandas openpyxl pillow pyinstaller")
        sys.exit(1)

    if build_executable():
        print(f"\n🚀 版本 {__version__} ShigureAI 打包完成！")
        print(f"📦 可执行文件: dist/ShigureAI_{__version__}.exe")
    else:
        sys.exit(1)
