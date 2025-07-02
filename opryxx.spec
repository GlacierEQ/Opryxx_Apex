# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['opryxx_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include configuration files
        ('config/*.yaml', 'config'),
        ('config/*.json', 'config'),
        
        # Include web assets if any
        ('ai_workbench/api/static', 'ai_workbench/api/static'),
        ('ai_workbench/api/templates', 'ai_workbench/api/templates'),
        
        # Include any other data files
        ('docs', 'docs'),
        ('scripts', 'scripts'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'sqlalchemy',
        'psutil',
        'pyyaml',
        'python-multipart',
        'aiofiles',
        'jinja2',
        'prometheus_client',
        'opryxx',
        'ai_workbench',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add any additional files that need to be included
# a.datas += Tree('path/to/additional/files', prefix='destination/folder')

# Add any DLLs that might be needed on Windows
if sys.platform == 'win32':
    from PyInstaller.utils.win32.versioninfo import (
        VSVersionInfo,
        FixedFileInfo,
        SetVersion,
        StringFileInfo,
        StringTable,
        StringStruct,
        VarFileInfo,
        VarStruct,
    )
    
    # Version information for the executable
    version = '1.0.0.0'
    
    # Create version info for the executable
    version_info = VersionInfo(
        vs=FixedFileInfo(
            filevers=(1, 0, 0, 0),
            prodvers=(1, 0, 0, 0),
            mask=0x3f,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0)
        ),
        kids=[
            StringFileInfo(
                [
                    StringTable(
                        '040904B0',
                        [
                            StringStruct('CompanyName', 'OPRYXX'),
                            StringStruct('FileDescription', 'OPRYXX Unified System'),
                            StringStruct('FileVersion', version),
                            StringStruct('InternalName', 'OPRYXX'),
                            StringStruct('LegalCopyright', 'Copyright © 2025 OPRYXX. All rights reserved.'),
                            StringStruct('OriginalFilename', 'OPRYXX.exe'),
                            StringStruct('ProductName', 'OPRYXX'),
                            StringStruct('ProductVersion', version),
                        ]
                    )
                ]
            ),
            VarFileInfo([VarStruct('Translation', [1033, 1200])])
        ]
    )
    
    # Set the version info
    a.version = version_info

# Create the executable
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OPRYXX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False if you don't want a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/opryxx.ico',  # Optional: path to an icon file
)

# Create a one-file executable
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OPRYXX',
)
