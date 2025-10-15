# -*- mode: python ; coding: utf-8 -*-

import pyside6helpers

a = Analysis(
    ['ledboardtranslatoremulator\\__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ledboardtranslatoremulator\\resources', 'resources'),
        (pyside6helpers.__path__[0] + "\\resources", 'pyside6helpers\\resources')
    ],
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
