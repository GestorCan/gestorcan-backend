@echo off
cd C:\Users\cualq\gestorcan-backend\app

call venv\Scripts\activate
uvicorn main:app --reload

pause