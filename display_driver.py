from waveshare_epd import epd2in13_V4
from PIL import Image

WIDTH, HEIGHT = 250, 122

def init_display():
    epd = epd2in13_V4.EPD()
    epd.init()
    # epd.init_partial()  # ← usa esto si tu controlador lo tiene
    return epd

def display_image(epd, image):
    # Usa actualización parcial
    epd.displayPartial(epd.getbuffer(image))

def clear_display(epd):
    epd.Clear(0xFF)
