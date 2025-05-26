import subprocess
import time
import threading
import logging

bluetooth_status = "Buscando..."

def attempt_reconnection():
    global bluetooth_status

    try:
        paired_output = subprocess.check_output(["bluetoothctl", "paired-devices"], text=True)
        devices = [line.split()[1] for line in paired_output.strip().splitlines() if "Device" in line]
    except Exception:
        bluetooth_status = "Error: No dispositivos emparejados"
        return

    if not devices:
        bluetooth_status = "Error: No emparejados"
        return

    target_mac = devices[0]  # usar el primero

    success = False
    for i in range(20):  # 15s * 20 = 5 minutos
        logging.info(f"🔁 Intentando reconectar a {target_mac} (intento {i+1}/20)")
        try:
            out = subprocess.check_output(["bluetoothctl", "connect", target_mac], text=True)
            if "Connection successful" in out:
                bluetooth_status = "Conectado"
                logging.info("✅ Conexión BT exitosa")
                success = True
                break
        except Exception as e:
            logging.warning(f"❗ Error al conectar: {e}")

        bluetooth_status = f"Buscando... ({i+1}/20)"
        time.sleep(15)

    if not success:
        bluetooth_status = "Error: No se encontró"

def start_reconnection_thread():
    thread = threading.Thread(target=attempt_reconnection, daemon=True)
    thread.start()
