# 🎛️ SpidsZero - Sistema de interfaz embebida en Raspberry Pi Zero 2 W

SpidsZero es una interfaz de usuario embebida desarrollada en Python para Raspberry Pi Zero 2 W, diseñada para funcionar con:

- 📟 Pantalla e-ink Waveshare v4
- 🔋 UPS Hat (Waveshare C)
- 🎧 Audífonos Bluetooth (con control multimedia)
- 🔊 Reproductor de música local (MPD)
- 📶 Wi-Fi y Bluetooth status

---

## 🧰 Características principales

- 🖥️ UI e-ink con módulos rotativos: `Wi-Fi`, `Bluetooth`, `System`, `Reproductor`
- 🔋 Monitoreo de batería usando INA219 (I2C)
- 🔁 Reproducción de música local continua (MPD + repeat)
- 🔊 Soporte para teclas multimedia Bluetooth (play, pause, next, prev)
- 🧠 Notificaciones visuales temporales en pantalla (ASCII UI)
- 🎧 Detección automática del input Bluetooth
- 🔌 Emparejamiento y configuración fácil con audífonos

---

## 🧱 Requisitos

- Raspberry Pi Zero 2 W con Raspberry Pi OS
- Pantalla e-ink Waveshare (versión v4)
- UPS Hat (C) de Waveshare (opcional)
- Python 3.9+ y `pip`
- Internet para instalar dependencias

---

## 🔧 Instalación

### 1. Clonar el proyecto

```bash
git clone git@github.com:4rgs/RPI2WZeroLAB.git
cd RPI2WZeroLAB/spidsZero
```

### 2. Instalar dependencias

```bash
sudo apt update
sudo apt install python3-pip python3-dev python3-pil python3-setuptools \
                 python3-smbus i2c-tools git evtest mpg123 mpd mpc tree
pip3 install -r requirements.txt
```

### 3. Activar interfaces necesarias

```bash
sudo raspi-config
# Activar:
# - I2C
# - SPI
# - Bluetooth
```
### 4. Copiar librería de pantalla e-ink

Si waveshare_epd no se instala correctamente:

```bash
cp -r waveshare_epd /usr/local/lib/python3.9/dist-packages/
```

### ▶️ Ejecució>

Manual

```bash
sudo cp spids-ui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable spids-ui.service
sudo systemctl start spids-ui.service
```

### 🎧 Emparejamiento de audífonos Bluetooth

1. Correr script de Emparejamiento

```bash
./scripts/pair_and_activate_audio.sh
```

Sigue las instrucciones para conectar tu dispositivo.

2. Activar salida de audio Bluetooth

```bash
./scripts/activate_bluetooth_audio.sh
```
Esto configura automáticamente el perfil a2dp-sink y reinicia MPD.

### 🧠 Controles multimedia Bluetooth soportados
	•	▶️ KEY_PLAYPAUSE, KEY_PLAYCD, KEY_PAUSECD
	•	⏭️ KEY_NEXTSONG
	•	⏮️ KEY_PREVIOUSSONG

Las acciones mostrarán una notificación visual temporal en la parte superior de la pantalla.

### 🔁 Reproducción continua

Los archivos .mp3 colocados en assets/ se moverán automáticamente a ~/Music y comenzarán a reproducirse en loop con mpc repeat on.

### 🛠️ Archivos importantes

```bash
main.py                   → Ciclo principal del sistema
media_controls.py         → Escucha botones multimedia
notification.py           → Dibuja notificaciones temporales
data_fetch.py             → Recolecta info del sistema (RAM, CPU, BT)
ui.py                     → Lógica de interfaz visual
display_driver.py         → Controlador de pantalla e-ink
scripts/                  → Scripts para emparejar y activar audio BT
assets/                   → MP3 que se cargarán automáticamente
```

### 📄 Licencia

MIT

Desarrollado por 4rgs – Powered by SpidsZero 🖖
