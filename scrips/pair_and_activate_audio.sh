#!/bin/bash
set -e

echo "🔍 Iniciando escaneo Bluetooth..."
bluetoothctl <<EOF
power on
agent on
default-agent
scan on
EOF

echo "🕵️  Busca el dispositivo en consola y copia su MAC (ej: 4C:A7:6C:FD:04:05)"
read -p "🎧 Ingrese MAC del dispositivo a emparejar: " MAC

echo "🔗 Emparejando con $MAC..."
bluetoothctl <<EOF
scan off
pair $MAC
trust $MAC
connect $MAC
EOF

echo "⏳ Esperando a que el sistema registre el dispositivo..."
sleep 5  # da tiempo a BlueZ + PipeWire para crear card/sink

CARD=$(pactl list short cards | grep "$MAC" | awk '{print $1}' | head -n1)
SINK=$(pactl list short sinks | grep "$MAC" | awk '{print $1}' | head -n1)

if [ -z "$CARD" ]; then
    echo "❌ No se encontró la tarjeta de audio para el dispositivo $MAC"
    pactl list short cards
    exit 1
fi

echo "🔊 Card detectada: $CARD"

# Intentar activar A2DP
echo "⚙️ Forzando perfil A2DP..."
if ! pactl set-card-profile "$CARD" a2dp-sink; then
    echo "❌ Error al cambiar a a2dp-sink. ¿Tu dispositivo soporta A2DP?"
    exit 1
fi

sleep 2

SINK=$(pactl list short sinks | grep "$MAC" | awk '{print $1}' | head -n1)

if [ -z "$SINK" ]; then
    echo "❌ No se detectó el sink de salida. ¿Está conectado el perfil A2DP?"
    pactl list short sinks
    exit 1
fi

echo "🔈 Sink detectado: $SINK"

echo "✅ Estableciendo sink predeterminado..."
pactl set-default-sink "$SINK"

echo "🔄 Reiniciando MPD..."
systemctl --user restart mpd

echo "🎉 Listo. Reproducción por Bluetooth activada."
