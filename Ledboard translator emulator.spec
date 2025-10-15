# -*- mode: python ; coding: utf-8 -*-

import os.path

import pyside6helpers

a = Analysis(
    [os.path.join('ledboardtranslatoremulator', '__main__.py')],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join('ledboardtranslatoremulator', 'resources'), 'resources'),
        (os.path.join(pyside6helpers.__path__[0], "resources"), os.path.join('pyside6helpers', 'resources'))
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
