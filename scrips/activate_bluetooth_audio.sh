#!/bin/bash
set -e

echo "🎧 Buscando dispositivo Bluetooth con perfil A2DP..."

# Intenta detectar la última card Bluetooth
CARD=$(pactl list short cards | grep bluez_card | awk '{print $1}' | tail -n1)

if [ -z "$CARD" ]; then
    echo "❌ No se detectó ningún dispositivo Bluetooth como card."
    pactl list short cards
    exit 1
fi

echo "🔊 Card detectada: $CARD"
echo "⚙️ Activando perfil A2DP..."
pactl set-card-profile "$CARD" a2dp-sink || {
    echo "❌ No se pudo cambiar a perfil a2dp-sink."
    exit 1
}

sleep 2

SINK=$(pactl list short sinks | grep bluez_output | awk '{print $1}' | tail -n1)

if [ -z "$SINK" ]; then
    echo "❌ No se detectó un sink de salida."
    pactl list short sinks
    exit 1
fi

echo "✅ Sink detectado: $SINK"
pactl set-default-sink "$SINK"

echo "🔁 Reiniciando MPD..."
systemctl --user restart mpd

echo "🎉 Audio Bluetooth activo y funcional."
