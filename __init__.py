import os
import sys

# Obtener la ruta base del proyecto dinámicamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Agregar a sys.path si no está
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Asegurar que waveshare_epd esté accesible como módulo
WAVESHARE_PATH = os.path.join(BASE_DIR, "waveshare_epd")
if WAVESHARE_PATH not in sys.path:
    sys.path.insert(0, WAVESHARE_PATH)
