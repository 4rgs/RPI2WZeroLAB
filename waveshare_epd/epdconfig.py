import spidev
import RPi.GPIO as GPIO
import time

# Pines BCM usados por la pantalla Waveshare e-Paper 2.13 V4
RST_PIN  = 17
DC_PIN   = 25
CS_PIN   = 8
BUSY_PIN = 24
PWR_PIN  = 18
MOSI_PIN = 10
SCLK_PIN = 11

class RaspberryPi:
    def __init__(self):
        self.RST_PIN  = RST_PIN
        self.DC_PIN   = DC_PIN
        self.CS_PIN   = CS_PIN
        self.BUSY_PIN = BUSY_PIN
        self.PWR_PIN  = PWR_PIN
        self.MOSI_PIN = MOSI_PIN
        self.SCLK_PIN = SCLK_PIN

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.PWR_PIN, GPIO.OUT)
        GPIO.setup(self.BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0b00

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, milliseconds):
        time.sleep(milliseconds / 1000.0)

    def spi_writebyte(self, data):
        self.spi.writebytes(data)

    def module_exit(self):
        self.spi.close()
        GPIO.cleanup()

# Instancia global requerida
implementation = RaspberryPi()

# === Compatibilidad con drivers que llaman funciones globales ===
digital_write   = implementation.digital_write
digital_read    = implementation.digital_read
delay_ms        = implementation.delay_ms
spi_writebyte   = implementation.spi_writebyte
module_init     = lambda: 0
module_exit     = implementation.module_exit

# Pines globales requeridos
RST_PIN  = implementation.RST_PIN
DC_PIN   = implementation.DC_PIN
CS_PIN   = implementation.CS_PIN
BUSY_PIN = implementation.BUSY_PIN

# Soporte para spi_writebyte2
try:
    implementation.spi_writebyte2 = lambda data: implementation.spi.xfer2(data)
except AttributeError:
    implementation.spi_writebyte2 = lambda data: implementation.spi.writebytes(data)

spi_writebyte2 = implementation.spi_writebyte2
