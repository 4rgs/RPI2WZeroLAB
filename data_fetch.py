import psutil
import subprocess
import re
from datetime import datetime
from mpd import MPDClient
from bluetooth_manager import bluetooth_status

# Batería desde INA219
try:
    import board
    import busio
    from adafruit_ina219 import INA219

    i2c = busio.I2C(board.SCL, board.SDA)
    ina = INA219(i2c, addr=0x43)
    ina_sensor_available = True
except Exception:
    ina_sensor_available = False

def get_wifi_info():
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
        iwconfig_output = subprocess.check_output(["iwconfig"]).decode()
        signal_line = next((line for line in iwconfig_output.splitlines() if "Signal level" in line), "")
        signal = signal_line.split("Signal level=")[-1].split(" ")[0]
        ip = subprocess.check_output(["hostname", "-I"]).decode().strip().split()[0]
        return ssid, ip, signal
    except:
        return "N/A", "N/A", "N/A"

def setup_bluetooth_audio():
    try:
        result = subprocess.run(
            ["/home/4rgs/RPI2WZeroLAB/scripts/setup_bluetooth_audio.sh"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error al configurar BT: {e}"

def get_bluetooth_info():
    try:
        # Obtener la MAC del dispositivo actualmente conectado
        output = subprocess.check_output(["bt-device", "--list"], text=True)
        match = re.search(r'([0-9A-F:]{17})\s+\((.*?)\)', output)
        if not match:
            raise ValueError("No conectado")

        mac, name = match.groups()

        # Confirmar que está conectado
        info_output = subprocess.check_output(["bt-device", "-i", mac], text=True)
        if "Connected: 1" not in info_output:
            raise ValueError("No conectado activamente")

        discoverable = get_discoverable_state()
        own_mac = get_own_mac()

        return {
            "bt_status": "Conectado",
            "bt_peer_mac": mac,
            "bt_name": name,
            "bt_discoverable": discoverable,
            "bt_own_mac": own_mac
        }

    except Exception:
        return {
            "bt_status": bluetooth_status,
            "bt_peer_mac": "N/A",
            "bt_name": "Ninguno",
            "bt_discoverable": get_discoverable_state(),
            "bt_own_mac": get_own_mac()
        }

def get_discoverable_state():
    try:
        output = subprocess.check_output(["bluetoothctl", "show"], text=True)
        match = re.search(r"Discoverable:\s+(yes|no)", output)
        return match.group(1) if match else "N/A"
    except:
        return "N/A"

def get_own_mac():
    try:
        out = subprocess.check_output(["hciconfig"], text=True)
        match = re.search(r"hci0.*?\n\s*BD Address:\s*([0-9A-F:]{17})", out, re.DOTALL)
        return match.group(1) if match else "N/A"
    except:
        return "N/A"

def get_top_processes():
    procs = []
    for p in psutil.process_iter(['name', 'cpu_percent']):
        try:
            procs.append({
                "name": p.info['name'][:15],
                "cpu": round(p.info['cpu_percent'], 1)
            })
        except:
            continue
    return sorted(procs, key=lambda x: x['cpu'], reverse=True)[:3]

def get_mpd_info():
    try:
        client = MPDClient()
        client.connect("localhost", 6600)
        status = client.status()
        song = client.currentsong()
        client.close()
        client.disconnect()

        return {
            "mpd_status": status.get("state", "N/A"),
            "mpd_song": song.get("title", "N/A"),
            "mpd_artist": song.get("artist", "N/A"),
            "mpd_time": status.get("time", "N/A"),
            "mpd_volume": status.get("volume", "N/A")
        }
    except Exception:
        return {
            "mpd_status": "N/A",
            "mpd_song": "N/A",
            "mpd_artist": "N/A",
            "mpd_time": "N/A",
            "mpd_volume": "N/A"
        }

def get_system_info():
    ssid, ip, signal = get_wifi_info()
    bt = get_bluetooth_info()
    mpd_info = get_mpd_info()

    voltage = current = "N/A"
    if ina_sensor_available:
        try:
            voltage = round(ina.bus_voltage, 2)
            current = round(ina.current / 1000, 2)
        except:
            pass

    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "battery": voltage,
        "ssid": ssid,
        "ip": ip,
        "signal": signal,
        "bt_status": bt.get("bt_status", "N/A"),
        "bt_peer_mac": bt.get("bt_peer_mac", "N/A"),
        "bt_discoverable": bt.get("bt_discoverable", "N/A"),
        "bt_name": bt.get("bt_name", "N/A"),
        "bt_own_mac": bt.get("bt_own_mac", "N/A"),
        "top_processes": get_top_processes(),
        **mpd_info
    }
