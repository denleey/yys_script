# -*- mode: python -*-

block_cipher = None

SETUP_DIR = 'F:\\gitee\\knowledge\\yys_script\\test\\match_im\\'

a = Analysis(['match_widget.py', 'matchwin.py'],
             pathex=['F:\\gitee\\knowledge\\yys_script\\test\\match_im'],
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
          name='matchwin',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
