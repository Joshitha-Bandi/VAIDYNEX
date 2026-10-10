#!/bin/bash
set -e

echo "=========================================================="
echo "  🏥 MEDIKIOSK LOCAL PROTOTYPE SUITE (PS 26047)"
echo "=========================================================="

# 1. Start FastAPI Backend Gateway on Port 8000
echo "▶️  [1/3] Starting FastAPI Clinical Gateway on http://localhost:8000 ..."
PYTHONPATH=. /opt/homebrew/bin/python3.14 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 2

# 2. Start Unified MediKiosk Web Suite on Port 3000
echo "▶️  [2/2] Starting MediKiosk Unified Web Portals on http://localhost:3000 ..."
/opt/homebrew/bin/python3.14 -m http.server 3000 --directory public &
WEB_PID=$!

echo ""
echo "✨ ALL SERVICES ACTIVE & SYNCED:"
echo "   1. 📱 Patient Intake Kiosk:     http://localhost:3000"
echo "   2. 🩺 Doctor Consultation:      http://localhost:3000/doctor"
echo "   3. 🌿 AYUSH Dashavidha Hub:     http://localhost:3000/ayush"
echo "   4. 🚨 Emergency Triage:         http://localhost:3000/triage"
echo "   5. 📊 Admin & ABDM Console:     http://localhost:3000/admin"
echo "   6. ⚡ FastAPI Gateway & Docs:   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."

cleanup() {
    echo "Stopping all services..."
    kill $BACKEND_PID $WEB_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM
wait
