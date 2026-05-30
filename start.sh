#!/bin/bash
echo "========================================="
echo "       JINHO Analyst - Demarrage"
echo "========================================="

# Backend
echo "[1/2] Demarrage du backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "  -> Creation de l'environnement virtuel..."
    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
else
    source venv/Scripts/activate
fi

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "  -> Backend demarre sur http://localhost:8000"
cd ..

# Frontend
echo "[2/2] Demarrage du frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "  -> Installation des dependances..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
echo "  -> Frontend demarre sur http://localhost:3000"
cd ..

echo ""
echo "========================================="
echo "  JINHO Analyst est pret!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000/docs"
echo "========================================="

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
