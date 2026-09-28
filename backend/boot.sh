#!/bin/bash
# Levanta la API de Flask.
# Uso: ./boot.sh   (desde la carpeta backend, después de ./install.sh)
cd "$(dirname "$0")"

source venv/bin/activate
python3 app.py

# Si da "Permission denied": chmod +x install.sh boot.sh
