#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "v0.0.3"

import os
import sys
import io
import subprocess
import platform
import shutil
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def build_executable():
    print("开始使用 Nuitka 打包可执行文件...")
    
    required_files = ['favor_calculator.py', 'giftID.csv', 'exp.csv', 'icon.ico', 'bacv.txt']
    required_dirs = ['pic']
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 错误: 找不到必要文件 {file}")
            return False
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 错误: 找不到必要目录 {dir_name}")
            return False
    
    print("Cleaning previous build files...")
    cleanup_paths = ["build", "dist", "ShigureAI_v0.0.3.exe", "ShigureAI_v0.0.3.dist"]
    for path in cleanup_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Deleted directory: {path}")
            else:
                os.remove(path)
                print(f"Deleted file: {path}")
        else:
            print(f"Path not found: {path}")
    
    cmd = [
        'python', '-m', 'nuitka',
        '--onefile',
        '--enable-plugin=pyqt5',
        '--disable-console',
        '--show-scons',
        '--disable-dll-dependency-cache',
        '--noinclude-default-mode=error',
        '--windows-icon-from-ico=icon.ico',
        '--output-filename=ShigureAI_v0.0.3.exe',
        '--include-data-files=giftID.csv=giftID.csv',
        '--include-data-files=exp.csv=exp.csv',
        '--include-data-files=icon.ico=icon.ico',
        '--include-data-files=bacv.txt=bacv.txt',
        '--include-data-dir=pic=pic',
        '--assume-yes-for-downloads',
        '--remove-output',
        '--no-pyi-file',
        '--jobs=2',  # 限制并行任务数量
        '--low-memory',  # 低内存模式
        '--plugin-no-detection',  # 禁用插件检测
        '--lto=yes',  # 启用链接时优化
        '--noinclude-setuptools-mode=nofollow',
        '--noinclude-pytest-mode=nofollow',
        '--noinclude-unittest-mode=nofollow',
        '--noinclude-IPython-mode=nofollow',
        '--noinclude-pydoc-mode=nofollow',
        '--nofollow-import-to=PyQt5.QtWebEngineWidgets',
        '--nofollow-import-to=PyQt5.QtWebEngine',
        '--nofollow-import-to=PyQt5.QtMultimedia',
        '--nofollow-import-to=PyQt5.QtMultimediaWidgets',
        '--nofollow-import-to=PyQt5.QtNetwork',
        '--nofollow-import-to=PyQt5.QtQml',
        '--nofollow-import-to=PyQt5.QtQuick',
        '--nofollow-import-to=PyQt5.QtQuickWidgets',
        '--nofollow-import-to=PyQt5.QtSql',
        '--nofollow-import-to=PyQt5.QtSvg',
        '--nofollow-import-to=PyQt5.QtTest',
        '--nofollow-import-to=PyQt5.QtXml',
        '--nofollow-import-to=PyQt5.QtBluetooth',
        '--nofollow-import-to=PyQt5.QtPositioning',
        '--nofollow-import-to=PyQt5.QtLocation',
        '--nofollow-import-to=PyQt5.QtSensors',
        '--nofollow-import-to=PyQt5.QtSerialPort',
        '--nofollow-import-to=PyQt5.QtWebKit',
        '--nofollow-import-to=PyQt5.QtWebKitWidgets',
        '--nofollow-import-to=PyQt5.QtDesigner',
        '--nofollow-import-to=PyQt5.QtHelp',
        '--nofollow-import-to=PyQt5.QtOpenGL',
        '--nofollow-import-to=PyQt5.QtPrintSupport',
        '--nofollow-import-to=PyQt5.QtScript',
        '--nofollow-import-to=PyQt5.QtScriptTools',
        '--nofollow-import-to=PyQt5.QtUiTools',
        '--nofollow-import-to=matplotlib',
        '--nofollow-import-to=numpy',
        '--nofollow-import-to=scipy',
        '--nofollow-import-to=pandas',
        '--nofollow-import-to=openpyxl',
        '--nofollow-import-to=xlrd',
        '--nofollow-import-to=xlsxwriter',
        '--nofollow-import-to=IPython',
        '--nofollow-import-to=jupyter',
        '--nofollow-import-to=notebook',
        '--nofollow-import-to=tkinter',
        '--nofollow-import-to=wx',
        '--nofollow-import-to=PySide2',
        '--nofollow-import-to=PySide6',
        '--no-prefer-source-code',
        '--no-progressbar',
        '--no-pyi-file',
        '--python-flag=-OO',
        'favor_calculator.py'
    ]
    
    print("执行 Nuitka 命令：")
    print(' '.join(cmd))
    print()
    print("注意：Nuitka 编译可能需要较长时间，请耐心等待...")
    print("首次运行会下载必要的编译器组件...")
    
    try:
        print("开始执行 Nuitka 命令...")
        start_time = time.time()
        
        result = subprocess.run(cmd, check=True, text=True, timeout=3600)  # 60分钟超时
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("✅ Nuitka 打包成功！")
        print(f"📦 生成文件: ShigureAI_v0.0.3.exe")
        print(f"⏱️ 编译时间: {duration/60:.1f} 分钟")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Nuitka 打包超时（60分钟）")
        return False
    except subprocess.CalledProcessError as e:
        print("❌ Nuitka 打包失败")
        print(f"返回码: {e.returncode}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"错误输出: {e.stderr}")
        return False

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    try:
        import PyQt5, PIL, nuitka
        print("✅ 所有依赖都已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False


if __name__ == "__main__":
    print(f"=== Nuitka 打包工具 {__version__} ===\n")
    
    if not check_dependencies():
        print("请先安装必要依赖：")
        print("pip install PyQt5 pillow nuitka")
        sys.exit(1)
    
    if build_executable():
        print(f"\n🚀 版本 {__version__} ShigureAI Nuitka 打包完成！")
        print(f"📦 可执行文件: ShigureAI_v0.0.3.exe")
        
    else:
        sys.exit(1)
