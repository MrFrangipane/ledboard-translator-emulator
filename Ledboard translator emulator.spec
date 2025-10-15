# -*- mode: python ; coding: utf-8 -*-

import pkg_resources
from PyInstaller.utils.hooks import collect_data_files


installed_packages = [dist.key for dist in pkg_resources.working_set]
all_data = []
for package in installed_packages:
    try:
        package_data = collect_data_files(package)
        if package_data:
            all_data.extend(package_data)
            print(f"Added data files from {package}")
    except Exception as e:
        print(f"Error collecting data files from {package}: {e}")


a = Analysis(
    ['ledboardtranslatoremulator\\__main__.py'],
    pathex=[],
    binaries=[],
    datas=all_data + [('ledboardtranslatoremulator\\resources', 'ledboardtranslatoremulator\\resources')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='Ledboard translator emulator',
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
)
