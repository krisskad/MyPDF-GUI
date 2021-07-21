# -*- mode: python -*-

import os, platform
from kivy_deps import sdl2, glew, angle


if platform.system().lower() == 'windows':
    os.environ['KIVY_GL_BACKEND'] = "angle_sdl2"

spec_root = os.path.abspath("E:\final_year_project\GITHUB\Demo")
block_cipher = None
app_name = 'MyPDF'


a = Analysis(['main.py'],
             pathex=[spec_root],
             datas=[('logo/*.png', '.'), ('logo/*.gif', 'logo')],
             hiddenimports=['win32timezone', 'plyer.platforms.win.filechooser'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=app_name,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True,)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=False,
               name=app_name)