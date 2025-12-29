# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs, collect_data_files

datas = [('src', 'src'), ('assets', 'assets')]
binaries = []
hiddenimports = collect_submodules('PyQt6')

# curl_cffi 지원 추가 (HTTPS 로그인에 필수)
try:
    # curl_cffi의 네이티브 라이브러리 수집 (libcurl dylib 포함)
    binaries += collect_dynamic_libs('curl_cffi')
    hiddenimports += collect_submodules('curl_cffi')

    # curl_cffi의 핵심 모듈들 명시적으로 추가
    hiddenimports += [
        'curl_cffi',
        'curl_cffi.requests',
        'curl_cffi.const',
        '_cffi_backend',
    ]

    print("✓ curl_cffi libraries collected successfully")
except Exception as e:
    print(f"Warning: Could not collect curl_cffi libraries: {e}")
    print("The application will fallback to requests library")

# SSL 인증서 번들 추가 (HTTPS 요청을 위해 필수)
try:
    import certifi
    datas += [(certifi.where(), 'certifi')]
    print(f"Added certifi certificates: {certifi.where()}")
except ImportError:
    print("Warning: certifi not found. HTTPS requests may fail.")

# cryptography 네이티브 라이브러리 추가
try:
    binaries += collect_dynamic_libs('cryptography')
    hiddenimports += collect_submodules('cryptography')
except Exception as e:
    print(f"Warning: Could not collect cryptography libraries: {e}")

# Crypto (pycryptodome) 네이티브 라이브러리 추가
try:
    binaries += collect_dynamic_libs('Crypto')
    hiddenimports += collect_submodules('Crypto')
except Exception as e:
    print(f"Warning: Could not collect Crypto libraries: {e}")

# SQLAlchemy 및 데이터베이스 관련 (v1.1.0 credential storage)
try:
    hiddenimports += collect_submodules('sqlalchemy')
    hiddenimports += [
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.sql',
        'sqlalchemy.dialects.sqlite',
    ]
    print("✓ SQLAlchemy modules collected successfully")
except Exception as e:
    print(f"Warning: Could not collect SQLAlchemy modules: {e}")

# keyring backends for macOS
hiddenimports += [
    'keyring.backends.macOS',
    'keyring.backends.chainer',
    'keyring.backends.fail',
]

# PyQt6 플랫폼 플러그인 추가
hiddenimports += [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KTX-SRT-Macro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/favicon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='KTX-SRT-Macro',
)
app = BUNDLE(
    coll,
    name='KTX-SRT-Macro.app',
    icon='assets/favicon.icns',
    bundle_identifier='com.leegyurak.ktx-srt-macro',
)
