import os, platform, subprocess, shutil

url_win = "https://raw.githubusercontent.com/Zeev-x/reyette-dlr/main/reyette.py"
url_nonwin = "https://raw.githubusercontent.com/Zeev-x/reyette-dlr/main/main_noui.py"
name_file = "reyette.py"
path_venv = ".reyette"

def os_detector():
    return platform.system()

def os_system_cmd():
    if os_detector() == "Windows":
        return [
            f"curl -o {name_file} {url_win}",
            "cls",
            f"python {name_file}",
        ]
    else:
        return [
            f"curl -o {name_file} {url_nonwin}",
            f"python -m venv {path_venv}",
            f"./{path_venv}/bin/python -m pip install yt-dlp",
            "clear",
            f"./{path_venv}/bin/python {name_file}",
        ]

def worker():
    cmd = os_system_cmd()
    if os_detector() == "Windows":
        try:
            for x in cmd:
                print(f"Running > {x}")
                subprocess.run(x, shell=True, check=True)
        except Exception as e:
            print("Error:", e)
    else:
        try:
            for x in cmd:
                print(f"Running > {x}")
                os.system(x)
        except Exception as e:
            print("Error:", e)


def after_work():
    try:
        if os.path.exists(name_file):
            print(f"Deleting file > {name_file}")
            os.remove(name_file)
        if os_detector() != "Windows" and os.path.exists(path_venv):
            print(f"Deleting venv > {path_venv}")
            shutil.rmtree(path_venv)
    except Exception as e:
        print("Cleanup error:", e)

def main():
    try:
        print(f"Detected OS: {os_detector()}")
        worker()
    except KeyboardInterrupt:
        print("Exiting by user")
    finally:
        after_work()
        print("All Good")

if __name__ == "__main__":
    main()
