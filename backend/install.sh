#!/bin/bash
# Crea el entorno virtual e instala las dependencias del backend.
# Uso: ./install.sh   (desde la carpeta backend)
cd "$(dirname "$0")"

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Si todavía no existe el archivo .env, se crea a partir del ejemplo
if [ ! -f .env ]; then
    cp .env-example .env
    echo "Se creó .env a partir de .env-example (revisá los valores)."
fi
