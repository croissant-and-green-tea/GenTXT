# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Collecter tous les fichiers du package gentxt
gentxt_datas = []
gentxt_path = os.path.join('src', 'gentxt')
for root, dirs, files in os.walk(gentxt_path):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            dest_dir = os.path.dirname(file_path).replace('src' + os.sep, '')
            gentxt_datas.append((file_path, dest_dir))

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=gentxt_datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'gentxt',
        'gentxt.config',
        'gentxt.core',
        'gentxt.dialogs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GenTXT',
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
    icon='src/icons/icons.ico' if sys.platform == 'win32' else None,
)
