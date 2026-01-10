# -*- mode: python ; coding: utf-8 -*-
"""
CF Proxy Manager PyInstaller 配置文件
使用方法: pyinstaller cf_proxy_manager.spec
"""

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
        'hypothesis',  # 测试库，不需要打包
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
    name='虎哥API反代',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico',  # 应用图标
    uac_admin=True,  # 请求管理员权限
    uac_uiaccess=False,
    manifest='app.manifest',  # 使用自定义清单文件
)
