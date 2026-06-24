@echo off

cd /d C:\Users\cualq\gestorcan-backend

call venv\Scripts\activate

python -m uvicorn app.main:app --reload

pause