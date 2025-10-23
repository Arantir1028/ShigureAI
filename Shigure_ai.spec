# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['favor_calculator.py'],
    pathex=[],
    binaries=[],
    datas=[('giftID.xlsx', '.'), ('exp.xlsx', '.'), ('icon.jpg', '.'), ('bacv.txt', '.'), ('pic', 'pic')],
    hiddenimports=['pandas', 'numpy', 'openpyxl', 'Pillow', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PyQt5.QtCore'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'turtle', 'matplotlib', 'scipy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ShigureAI_v0.0.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.jpg'],
)
