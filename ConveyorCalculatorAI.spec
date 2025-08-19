# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cloud.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data'), ('ui', 'ui'), ('reports', 'reports'), ('ui/ads_banner.html', '.'), ('ui/images', 'ui/images'), ('ui/models', 'ui/models'), ('ui/js', 'ui/js')],
    hiddenimports=['argon2', 'argon2.low_level', 'platformdirs', 'cryptography', 'google.generativeai', 'faiss', 'sentence_transformers', 'PySide6.QtWebEngineWidgets'],
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
    [],
    exclude_binaries=True,
    name='ConveyorCalculatorAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['H:\\Cloude Gemini 6.4 API BM\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ConveyorCalculatorAI',
)
