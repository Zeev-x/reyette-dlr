@echo off
python -m venv x
call x\Scripts\activate.bat
pip install -r requirements.txt
echo "Instalasi selesai. Jalankan main.py untuk memulai aplikasi."
pause