from PIL import Image, ImageDraw, ImageFont
import time

WIDTH, HEIGHT = 250, 122
notification_active = False
notification_text = ""
notification_time = 0

font_notify = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)

def set_notification(text):
    global notification_text, notification_active, notification_time
    notification_text = text
    notification_active = True
    notification_time = time.time()

def draw_notification_if_active(epd):
    global notification_active

    if not notification_active:
        return

    # Si pasaron más de 2.5s, desactiva
    if time.time() - notification_time > 2.5:
        notification_active = False
        return

    # Crear imagen transparente encima
    from display_driver import WIDTH, HEIGHT  # por si no lo tienes definido
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    # Fondo rectangular en parte media
    box_height = 20
    y_pos = HEIGHT // 2 - box_height // 2
    draw.rectangle([0, y_pos, WIDTH, y_pos + box_height], fill=255)
    w, h = draw.textsize(notification_text, font=font_notify)
    x = (WIDTH - w) // 2
    y = y_pos + (box_height - h) // 2
    draw.text((x, y), notification_text, font=font_notify, fill=0)

    if hasattr(epd, "displayPartial"):
        epd.displayPartial(epd.getbuffer(image))
    else:
        epd.display(epd.getbuffer(image))
