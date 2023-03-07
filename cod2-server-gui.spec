# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
import subprocess
import datetime

# Get the current date and time
now = datetime.datetime.now()


# SET YOUR VERSION HERE
VERSION = '0.0.3'
BUILD_DATE = now.strftime("%Y-%m-%d %H:%M:%S")

# Write the version information to a version.py file
with open(os.path.join(os.getcwd(),'src',"version.py"), "w") as f:
    f.write(f"VERSION = '{VERSION}'\n")
    f.write(f"BUILD_DATE = '{BUILD_DATE}'\n")


# Import version.py file
with open(os.path.join(os.getcwd(),'src',"version.py")) as f:
    exec(f.read())

# Define the base directory of the application
base_dir = os.path.join(os.getcwd(), 'src')


# Define the paths to the configuration directories
mods_dir = os.path.join(base_dir, 'mods')
profiles_dir = os.path.join(base_dir, 'profiles')
server_config_dir = os.path.join(base_dir, 'server_config')
icon_dir = os.path.join(base_dir, 'icons')
img_dir = os.path.join(base_dir, 'img')

block_cipher = None


a = Analysis(
    ['./src/main.py'],
    pathex=[],
    binaries=[],
    datas=[(mods_dir, 'mods'), (profiles_dir, 'profiles'), (server_config_dir, 'server_config'), (icon_dir,'icons'), (img_dir, 'img')],
    hiddenimports=[],
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

# VERSION

a.version = VERSION


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'COD2-SERVER-GUI-{VERSION}',
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
    icon=os.path.join(icon_dir,'Call-of-Duty-2.ico'),
    version_file=os.path.join(os.getcwd(),'src','version.py')
)
