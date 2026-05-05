@echo off
cd /d %~dp0

REM Chạy Flask app bằng Python trong virtual environment
start "" venv-project-width-line\Scripts\python.exe run.py

REM Giữ cửa sổ cmd mở để xem log
pause