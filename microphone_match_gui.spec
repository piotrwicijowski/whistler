# -*- mode: python -*-

block_cipher = None


a = Analysis(['microphone_match_gui.py'],
             pathex=['C:\\Users\\pwici\\Desktop\\audfprint'],
             binaries=[('ffmpeg.exe','.'),
             ('fpdbase.pklz','.')],
             datas=[],
             hiddenimports=[],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='microphone_match_gui',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='microphone_match_gui')
