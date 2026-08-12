@echo off

:: 1. Явно переходимо на потрібний диск
C:

:: 2. Переходимо в папку проекту, використовуючи лапки
cd "C:\Scripts\automatizationAD"

:: 3. Запускаємо uvicorn, вказуючи повний шлях до нього, також у лапках
"C:\Scripts\automatizationAD\.venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8080