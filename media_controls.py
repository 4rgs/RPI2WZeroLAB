import logging
import time
import threading
from evdev import InputDevice, ecodes, list_devices
from mpd import MPDClient
from notification import set_notification

def connect_mpd():
    mpd = MPDClient()
    try:
        mpd.connect("localhost", 6600)
        logging.info("✅ MPD conectado correctamente")
        return mpd
    except Exception as e:
        logging.warning(f"⚠️ No se pudo conectar a MPD: {e}")
        return None

def find_bluetooth_input(retries=30, delay=5):
    for i in range(retries):
        for path in list_devices():
            try:
                device = InputDevice(path)
                if "bluetooth" in device.name.lower() or "avrcp" in device.name.lower():
                    logging.info(f"🎧 Input encontrado: {device.name} ({path})")
                    return path
            except:
                continue
        logging.info(f"🔁 Esperando input BT ({i+1}/{retries})...")
        time.sleep(delay)
    return None

def listen_for_media_keys(dev_path, mpd):
    try:
        dev = InputDevice(dev_path)
        logging.info(f"🎧 Escuchando eventos de: {dev.name}")
    except Exception as e:
        logging.warning(f"❌ No se pudo abrir {dev_path}: {e}")
        return

    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            code = event.code
            try:
                if code in [ecodes.KEY_PLAYPAUSE, ecodes.KEY_PLAYCD, ecodes.KEY_PAUSECD]:
                    logging.info("⏯️ Play/Pause detectado")
                    if mpd:
                        state = mpd.status().get("state")
                        if state == "play":
                            mpd.pause(1)
                            logging.info("⏸️ Pausado")
                            set_notification("⏸️ Pausado")
                        else:
                            if not mpd.playlist():
                                mpd.clear()
                                mpd.add("/")
                            mpd.play()
                            logging.info("▶️ Reproduciendo")
                            set_notification("▶️ Reproduciendo")

                elif code == ecodes.KEY_NEXTSONG:
                    logging.info("⏭️ Siguiente canción")
                    set_notification("⏭️ Siguiente canción")
                    if mpd and mpd.playlist():
                        mpd.next()

                elif code == ecodes.KEY_PREVIOUSSONG:
                    logging.info("⏮️ Canción anterior")
                    set_notification("⏮️ Canción anterior")
                    if mpd and mpd.playlist():
                        mpd.previous()

            except Exception as e:
                logging.warning(f"❗ Error al controlar MPD: {e}")

def start_media_key_listener():
    dev_path = find_bluetooth_input()
    if not dev_path:
        logging.warning("❌ No se detectó dispositivo Bluetooth de control.")
        return

    mpd = connect_mpd()

    thread = threading.Thread(
        target=listen_for_media_keys,
        args=(dev_path, mpd),
        daemon=True
    )
    thread.start()
