#!/bin/bash

# Ruta base del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Activando entorno virtual..."
source "$PROJECT_DIR/spids-env/bin/activate"

echo "📦 Instalando dependencias desde requirements.txt..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "✅ Instalación completada correctamente."
