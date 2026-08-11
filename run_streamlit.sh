#!/bin/bash
# Lancer l'application Streamlit

VENV_PATH="./venv/bin"
PORT=${1:-8501}

echo "🚀 Lancement du dashboard Streamlit..."
echo "📍 Accès : http://localhost:${PORT}"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

$VENV_PATH/python -m streamlit run streamlit_app.py --server.port $PORT
