# -*- mode: python ; coding: utf-8 -*-
"""
CF Proxy Manager PyInstaller 配置文件
使用方法: pyinstaller cf_proxy_manager.spec
"""
import re

# 从 __init__.py 读取版本号
def get_version():
    with open('cf_proxy_manager/__init__.py', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else '1.0.0'

APP_VERSION = get_version()
APP_NAME = f'虎哥API反代-v{APP_VERSION}'

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cf_proxy_manager',
        'cf_proxy_manager.gui',
        'cf_proxy_manager.models',
        'cf_proxy_manager.config_manager',
        'cf_proxy_manager.parsers',
        'cf_proxy_manager.hosts_manager',
        'cf_proxy_manager.speed_tester',
        'cf_proxy_manager.ios_widgets',
        'cf_proxy_manager.hosts_viewer',
        'cf_proxy_manager.admin_helper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'hypothesis',
        'pytest',
    ],
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
    name=APP_NAME,
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
    icon='resources/icon.ico',
    uac_admin=True,
    uac_uiaccess=False,
    manifest='app.manifest',
)
