# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

SPEC_DIR = Path(SPECPATH).resolve()

# Complete list of data files - automatically include the whole data directory
data_files = [
    ('data', 'data'),
    ('web-app/templates', 'web-app/templates'),
    ('web-app/static', 'web-app/static'),
]

# PyInstaller already adds the active environment. Adding site-packages to
# pathex explicitly can mix interpreters and is rejected by PyInstaller 7.
search_paths = [str(SPEC_DIR)]

hidden_imports = [
    'webview',
    'server',
    'core',
    'core.crypto',
    'core.parser',
    'core.editor',
    'core.environment',
    'core.instances',
    'http.server',
    'urllib.parse',
    'json',
    'base64',
    'socket',
    'threading',
]
if sys.platform == 'darwin':
    hidden_imports.append('webview.platforms.cocoa')
elif sys.platform == 'win32':
    hidden_imports.append('webview.platforms.edgechromium')

a = Analysis(
    ['main.py'],
    pathex=search_paths,
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == 'darwin':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Change of Heart',
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
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name='Change of Heart',
    )
    app = BUNDLE(
        coll,
        name='Change of Heart.app',
        icon=str(SPEC_DIR / 'change_of_heart.icns'),
        bundle_identifier='com.j0nnydigital.changeofheart',
        info_plist={
            'CFBundleDisplayName': 'Change of Heart',
            'CFBundleName': 'Change of Heart',
            'CFBundleShortVersionString': '1.1.1',
            'CFBundleVersion': '1',
            'LSMinimumSystemVersion': '12.0',
            'NSHighResolutionCapable': True,
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='P5R_Save_Editor',
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
