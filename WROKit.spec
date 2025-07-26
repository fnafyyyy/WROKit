# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('WROKit.ico', '.'), ('config.json', '.'), ('instalki\\\\jre-8u331-windows-x64.exe', 'instalki'), ('instalki\\\\VC_redist.x64.exe', 'instalki'), ('instalki\\\\PROTECT_Installer_x64_en_US-2.exe', 'instalki'), ('instalki\\\\tightvnc-2.8.81-gpl-setup-64bit.msi', 'instalki'), ('instalki\\\\haos_1.9.8.zip', 'instalki'), ('instalki\\\\anyconnect-win-4.8.03052-predeploy-k9.zip', 'instalki')],
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
    name='WROKit',
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
    uac_admin=True,
    icon=['WROKit.ico'],
)
