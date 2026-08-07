import os
import shutil

env_path = "Reyette_Roxylious_Atelier"
url_1 = "https://raw.githubusercontent.com/Zeev-x/reyette-dlr/main/main.py"
url_2 = "https://raw.githubusercontent.com/Zeev-x/reyette-dlr/main/downloaderapp.kv"
url_icon = "https://raw.githubusercontent.com/Zeev-x/reyette-dlr/refs/heads/main/logo/app_icon_square.ico"

data = []

def run_cmd(name_of_app):
    cmd = [
        "@echo off",
        f"curl -o main.py {url_1}",
        f"curl -o downloaderapp.kv {url_2}",
        f"mkdir icon && curl -o icon/icon.ico {url_icon}",
        f"py -3.12 -m venv {env_path}",
        f"{env_path}\\Scripts\\python.exe -m pip install --upgrade yt-dlp kivy pyinstaller",
        f'{env_path}\\Scripts\\pyinstaller.exe main.py --onefile --icon=icon/icon.ico --name="{name_of_app}" --windowed --add-data "downloaderapp.kv;." --add-data "icon/icon.ico;icon"',
    ]
    try:
        for x in cmd:
            print(f"Running command: {x}")
            os.system(x)
    except Exception as e:
        print(e)

def after_build(app_name):
    src = os.path.join("dist", f"{app_name}.exe")
    dst = os.path.join(os.getcwd(), f"{app_name}.exe")

    dir_temp = [f"{env_path}", "icon", "build", "dist"]
    file_temp = ["main.py", "builder.py", "downloaderapp.kv", f"{app_name}.spec"]

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
    

def main():
    name_of_app = input("Nama aplikasi EXE: ")
    run_cmd(name_of_app)
    after_build(name_of_app)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Closing by user")
    finally:
        os.system("pause")
