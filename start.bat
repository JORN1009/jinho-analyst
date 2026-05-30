@echo off
echo =========================================
echo        JINHO Analyst - Demarrage
echo =========================================

echo [1/2] Backend...
cd backend
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)
start "JINHO Backend" uvicorn app.main:app --reload --port 8000
cd ..

echo [2/2] Frontend...
cd frontend
if not exist node_modules (
    npm install
)
start "JINHO Frontend" npm run dev
cd ..

echo.
echo =========================================
echo   JINHO Analyst est pret!
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000/docs
echo =========================================
pause
