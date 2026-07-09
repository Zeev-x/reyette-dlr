@echo off
py -3.12 -m venv x
call x\Scripts\activate.bat
python -m pip install -r requirements.txt
echo "Instalasi selesai. Jalankan main.py untuk memulai aplikasi."
pause
