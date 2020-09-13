# -*- mode: python -*-

block_cipher = None

SETUP_DIR = 'F:\\gitee\\knowledge\\yys_script\\'

a = Analysis(['src\\main.py',
              'src/autogui.py',
              'src/screenshot.py',
              'src/config.py',
              'src/mainwin.py',
              'src/yuhun.py',
              'src/chi.py',
              'src/yuling.py',
              'src/chapter.py',
              'src/yysbreak.py',
              'src/ui/main_widget.py'],
             pathex=['F:\\gitee\\knowledge\\yys_script'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='yys_script',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
