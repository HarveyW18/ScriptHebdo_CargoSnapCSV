# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['CargoSnap - CsvExtractor.pyw'],
    pathex=['.'],
    binaries=[],
    datas=[('ressources/*', 'ressources')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CargoSnap - CsvExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='ressources/icon.ico',  # Spécifiez l'icône ici
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CargoSnap - CsvExtractor',
)
