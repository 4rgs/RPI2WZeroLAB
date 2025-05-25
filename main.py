import time
import threading
import logging
import os
import shutil
from pathlib import Path
from display_driver import init_display, display_image
from data_fetch import get_system_info
from ui import render_ui
from media_controls import media_key_listener, connect_mpd
from notification import draw_notification_if_active

def move_mp3_assets():
    source_dir = Path(__file__).parent / "assets"
    music_dir  = Path("/home/4rgs/Music") 
    music_dir.mkdir(parents=True, exist_ok=True)

    for mp3_file in source_dir.glob("*.mp3"):
        dest = music_dir / mp3_file.name
        if not dest.exists():
            shutil.move(str(mp3_file), str(dest))
            logging.info(f"🎵 MP3 movido: {mp3_file.name}")

    # 🟢 Asegurar actualización y reproducción en loop
    os.system("mpc update")
    os.system("mpc clear && mpc add / && mpc play")
    os.system("mpc repeat on")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    move_mp3_assets()
    epd = init_display()
    mpd = connect_mpd()

    # 🟢 Listener de teclas multimedia (BT)
    threading.Thread(target=media_key_listener, args=(mpd,), daemon=True).start()

    mode = 0
    while True:
        try:
            info = get_system_info()
            img = render_ui(info, mode)
            draw_notification_if_active(img)
            display_image(epd, img)
            mode = (mode + 1) % 4
            time.sleep(5)
        except Exception as e:
            logging.error(f"❌ Error en UI loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
