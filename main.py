import time
import threading
import logging
import os
import shutil
from pathlib import Path
from display_driver import init_display
from data_fetch import get_system_info
from ui import render_ui
from media_controls import start_media_key_listener
from notification import draw_notification_if_active
from bluetooth_manager import start_reconnection_thread

# Iniciar reconexión BT automática
start_reconnection_thread()

def move_mp3_assets():
    source_dir = Path(__file__).parent / "assets"
    music_dir  = Path("/home/4rgs/Music") 
    music_dir.mkdir(parents=True, exist_ok=True)

    for mp3_file in source_dir.glob("*.mp3"):
        dest = music_dir / mp3_file.name
        if not dest.exists():
            shutil.move(str(mp3_file), str(dest))
            logging.info(f"🎵 MP3 movido: {mp3_file.name}")

    os.system("mpc update")
    os.system("mpc clear && mpc add / && mpc play")
    os.system("mpc repeat on")

def main():
    logging.basicConfig(level=logging.INFO)

    # Cargar música
    move_mp3_assets()

    # Iniciar pantalla e-ink
    epd = init_display()

    # Iniciar listener multimedia en segundo plano
    start_media_key_listener()

    # Lógica de rotación y refresco
    module_index = 0
    last_module_change = time.time()
    last_refresh = 0

    while True:
        current_time = time.time()

        # Rotar módulo cada 5 segundos
        if current_time - last_module_change >= 5:
            module_index = (module_index + 1) % 4
            last_module_change = current_time

        # Refrescar UI cada segundo
        if current_time - last_refresh >= 1:
            info = get_system_info()
            render_ui(epd, info, module_index)
            draw_notification_if_active(epd)
            last_refresh = current_time

        time.sleep(0.1)

if __name__ == "__main__":
    main()
