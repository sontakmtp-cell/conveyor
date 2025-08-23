# -*- mode: python ; coding: utf-8 -*-
# ConveyorCalculator.spec - Tối ưu hóa cho build nhẹ

block_cipher = None

a = Analysis(
    ['cloud.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('ui/images', 'ui/images'),
        ('ui/js', 'ui/js'),
        ('ui/models', 'ui/models'),
        ('reports/fonts', 'reports/fonts'),
        ('users.json', '.'),
        ('env_config.txt', '.'),
        ('icon.ico', '.'),
        ('ui/ads_banner.html', 'ui'),
    ],
    hiddenimports=[
        'core.db', 'core.engine', 'core.licensing', 'core.models',
        'core.optimize', 'core.security', 'core.specs', 'core.thread_worker',
        'core.utils', 'core.validators', 'core.ai.chat_service',
        'core.ai.providers.base', 'core.ai.providers.gemini_provider',
        'core.rag.embedder', 'core.rag.index', 'core.rag.pdf_loader',
        'core.rag.schema', 'core.utils.paths', 'core.utils.trough_utils',
        'core.utils.unit_conversion', 'reports.exporter_excel',
        'reports.exporter_pdf', 'reports.templates', 'ui.activation_dialog',
        'ui.ad_banner_widget', 'ui.login_dialog', 'ui.main_window_3d_enhanced',
        'ui.plotting', 'ui.styles', 'ui.tooltips', 'ui.ui_components_3d_enhanced',
        'ui.visualization_3d', 'ui.chat.chat_panel', 'nest_asyncio', 'dotenv',
        'pandas', 'numpy', 'scipy', 'matplotlib', 'plotly', 'openpyxl',
        'faiss', 'sentence_transformers', 'google.generativeai', 'reportlab',
        'PIL', 'cryptography', 'platformdirs', 'argon2', 'PyMuPDF',
    ],
    excludes=['tkinter', 'test', 'unittest', 'email', 'http', 'urllib3',
              'requests', 'certifi', 'charset_normalizer', 'idna',
              'PySide6.QtWebEngineWidgets'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ConveyorCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='ConveyorCalculator',
)
