#!/bin/bash

set -e

echo "🔍 Buscando dispositivo Bluetooth..."

# 1. Detectar el card Bluetooth
CARD=$(pactl list short cards | awk '/bluez_card/ {print $1}' | head -n1)

if [ -z "$CARD" ]; then
  echo "❌ No se detectó ningún dispositivo Bluetooth conectado."
  exit 1
fi

echo "🎧 Card detectado: $CARD"

# 2. Forzar perfil A2DP
echo "⚙️  Activando perfil A2DP..."
pactl set-card-profile "$CARD" a2dp-sink || {
  echo "❌ Falló el cambio de perfil a a2dp-sink."
  exit 1
}

sleep 1

# 3. Detectar el sink Bluetooth
SINK=$(pactl list short sinks | awk '/bluez_output/ {print $1}' | head -n1)

if [ -z "$SINK" ]; then
  echo "❌ Sink Bluetooth no encontrado. ¿El perfil A2DP está activo?"
  exit 1
fi

echo "🔊 Sink detectado: $SINK"

# 4. Establecer como predeterminado
echo "✅ Estableciendo como sink predeterminado..."
pactl set-default-sink "$SINK"

# 5. Reiniciar MPD (user-level)
echo "🔄 Reiniciando MPD..."
systemctl --user restart mpd

echo "✅ Configuración completada."
