# -*- mode: python ; coding: utf-8 -*-

# This spec file is configured for a one-directory build (--onedir),
# which results in a faster startup time and a smaller main executable.
# Data files are bundled alongside the executable, preserving their directory structure.

block_cipher = None

a = Analysis(
    ['cloud.py'],
    pathex=['h:\Cloude Gemini 6.4 API BM'],
    binaries=[],
    datas=[
        # Bundle data files, preserving their relative paths in the output directory.
        # Syntax: ('source_path_on_disk', 'destination_path_in_dist_folder')
        ('users.json', '.'),
        ('data/accounts.v1.json', 'data'),
        ('data/Bang tra 1.csv', 'data'),
        ('reports/fonts', 'reports/fonts'),
        ('ui/images', 'ui/images'),
        ('ui/js', 'ui/js'),
        ('ui/models', 'ui/models'),
        ('ui/ads_banner.html', 'ui'),
        ('icon.ico', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CloudGemini',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Use False for GUI applications, True for console applications
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CloudGeminiApp'
)
