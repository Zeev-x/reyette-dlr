@echo off
py -3.12 -m venv x
call x\Scripts\activate.bat
x\Scripts\python.exe -m pip install -r requirements.txt
echo "Instalasi selesai. Jalankan main.py untuk memulai aplikasi."
pause
