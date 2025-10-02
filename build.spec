# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 플랫폼에 따라 출력 디렉토리 및 아이콘 결정
if sys.platform == 'darwin':
    dist_dir = 'build/mac'
    app_name = 'KTX-SRT-Macro'
    icon_file = 'assets/favicon.icns'
    target_arch = None  # macOS는 자동 감지
elif sys.platform == 'win32':
    dist_dir = 'build/windows'
    app_name = 'KTX-SRT-Macro'
    icon_file = 'assets/favicon.ico'
    target_arch = 'x86_64'  # Windows는 amd64로 빌드
else:
    dist_dir = 'build/linux'
    app_name = 'KTX-SRT-Macro'
    icon_file = 'assets/favicon.ico'
    target_arch = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/favicon.ico', 'assets'),
        ('assets/favicon.icns', 'assets'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
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
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=target_arch,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# macOS용 앱 번들
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='KTX-SRT-Macro.app',
        icon='assets/favicon.icns',
        bundle_identifier='com.ktxsrt.macro',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleShortVersionString': '1.0.0',
        },
    )
