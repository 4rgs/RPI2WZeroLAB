import logging
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

def find_bluetooth_input():
    for path in list_devices():
        try:
            device = InputDevice(path)
            if "Bluetooth" in device.name or "AVRCP" in device.name or "Redmi" in device.name:
                logging.info(f"✅ Input Bluetooth encontrado: {device.name} en {path}")
                return path
        except Exception:
            continue
    logging.warning("⚠️ No se detectó ningún input Bluetooth compatible.")
    return None

def media_key_listener(mpd):
    dev_path = find_bluetooth_input()
    if not dev_path:
        logging.warning("🎧 No se iniciará media listener: no se detectó dispositivo de control.")
        return

    try:
        dev = InputDevice(dev_path)
        logging.info(f"🎧 Escuchando eventos de: {dev.name}")
    except Exception as e:
        logging.warning(f"❌ No se pudo abrir {dev_path}: {e}")
        return

    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            code = event.code

            if code in [ecodes.KEY_PLAYPAUSE, ecodes.KEY_PLAYCD, ecodes.KEY_PAUSECD]:
                logging.info("⏯️  Play/Pause detectado")
                if mpd:
                    try:
                        state = mpd.status().get("state")
                        if state == "play":
                            mpd.pause(1)
                            logging.info("⏸️  Pausado")
                            set_notification("⏸️ Pausado")
                        else:
                            if not mpd.playlist():
                                mpd.clear()
                                mpd.add("/")
                            mpd.play()
                            logging.info("▶️ Reproduciendo")
                            set_notification("▶️ Reproduciendo")
                    except Exception as e:
                        logging.warning(f"❗ Error al controlar reproducción: {e}")

            elif code == ecodes.KEY_NEXTSONG:
                logging.info("⏭️  Siguiente canción")
                set_notification("⏭️ Siguiente canción")
                if mpd and mpd.playlist():
                    try:
                        mpd.next()
                    except Exception as e:
                        logging.warning(f"❗ Error al avanzar canción: {e}")

            elif code == ecodes.KEY_PREVIOUSSONG:
                logging.info("⏮️  Canción anterior")
                set_notification("⏮️ Canción anterior")
                if mpd and mpd.playlist():
                    try:
                        mpd.previous()
                    except Exception as e:
                        logging.warning(f"❗ Error al retroceder canción: {e}")
