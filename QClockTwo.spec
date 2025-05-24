a = Analysis(
    ['qclocktwo.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pytz', 'tzlocal'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pillow', 'geopy', 'timezonefinder', 'ttkwidgets', 'cffi', 'pycparser', 'geographiclib', 'h3'],
    noarchive=False
)
a.datas += [
    ('tcl8.6', '/System/Library/Frameworks/Tcl.framework/Versions/8.6/Resources/tcl8.6', 'DATA'),
    ('tk8.6', '/System/Library/Frameworks/Tk.framework/Versions/8.6/Resources/tk8.6', 'DATA'),
]
a.datas = [(d[0], d[1], d[2]) for d in a.datas if not ('tcl8.6' in d[0] and ('demos' in d[0] or 'msgs' in d[0] or 'encoding' in d[0]))]
a.datas = [(d[0], d[1], d[2]) for d in a.datas if not ('tk8.6' in d[0] and ('images' in d[0] or 'demos' in d[0]))]
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QClockTwo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['libtcl*.dylib', 'libtk*.dylib'],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
app = BUNDLE(
    exe,
    name='QClockTwo.app',
    icon=None,
    bundle_identifier=None
)