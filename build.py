import os
import shutil

env_path = "Reyette_Roxylious_Atelier"
url_1 = "https://zeev-x.github.io/reyette-dlr/main.py"
url_2 = "https://zeev-x.github.io/reyette-dlr/downloaderapp.kv"
url_3 = "https://zeev-x.github.io/reyette-dlr/icon/icon_circle.ico"

data = []

cmd = [
    "@echo off",
    f"curl -o main.py {url_1}",
    f"curl -o downloaderapp.kv {url_2}",
    f"mkdir icon && curl -o icon/icon.ico {url_3}",
    f"py -3.12 -m venv {env_path}",
    f"call {env_path}\\Scripts\\activate",
    f"{env_path}\\Scripts\\python.exe -m pip install --upgrade kivy yt-dlp pyinstaller pillow",
    f"{env_path}\\Scripts\\pyinstaller.exe main.spec",
    f"{env_path}\\Scripts\\deactivate",
]

def create_spec_file(app_name):
    main_spec = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('downloaderapp.kv', '.'),
        ('icon/*.ico', 'icon'),
    ],
    hiddenimports=[
        'kivy',
        'kivy.core.text',
        'kivy.core.window',
        'kivy.core.image',
        'kivy.core.audio',
        'kivy.core.video',
        'kivy.modules',
        'yt_dlp',
        'yt_dlp.utils',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,\n'''
    main_spec += f"    name='{app_name}',\n"
    main_spec += '''    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],\n'''
    main_spec +=f"    name='{app_name}'\n"
    main_spec += ")"

    file_location = os.path.join(os.getcwd(), 'main.spec')
    print(f"Creating main.spec at {file_location}")
    try:
        with open(file_location, 'w') as file:
            file.write(main_spec)
        print(f"Successfully wrote to {file_location}")
    except Exception as e:
        print(f"Error writing to {file_location}: {e}")

def run_cmd():
    try:
        for x in cmd:
            print(f"Runing command: {x}")
            os.system(x)
    except Exception as e:
        print(e)

def after_build(app_name):
    src = os.path.join("dist", app_name)
    dst = os.path.join(os.getcwd(), app_name)

    dir_temp = [f"{env_path}", "icon", "build", "dist"]
    file_temp = ["downloaderapp.kv", "main.spec", "main.py"]

    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")

    for x in dir_temp:
        if os.path.exists(x):
            print(f"Deleting {x}")
            shutil.rmtree(x)

    for y in file_temp:
        if os.path.exists(y):
            print(f"Deleting {y}")
            os.remove(y)
    
    os.system("pause")

def main():
    name_of_app = input("Nama aplikasi EXE: ")
    create_spec_file(name_of_app)
    run_cmd()
    after_build(name_of_app)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Closing by user")
