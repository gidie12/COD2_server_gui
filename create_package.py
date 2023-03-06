# Define the PyInstaller executable
import sys
from pathlib import Path

pyi_bin = str(Path(sys.executable).parent / 'pyinstaller.exe')

# Define the PyInstaller options
opts = ['cod2-server-gui.spec']

# Run PyInstaller
import subprocess
subprocess.run([pyi_bin] + opts)