from PIL import ImageDraw, ImageFont
from datetime import datetime, timedelta

_notification = None
_notification_expire = None

def set_notification(message, duration=2.5):
    global _notification, _notification_expire
    _notification = message
    _notification_expire = datetime.now() + timedelta(seconds=duration)

def draw_notification_if_active(img):
    global _notification, _notification_expire
    if _notification and datetime.now() < _notification_expire:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), _notification, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (img.width - w) // 2
        y = 5

        draw.rectangle((0, 0, img.width, h + 10), fill=255)
        draw.rectangle((2, 2, img.width - 2, h + 8), outline=0)
        draw.text((x, y), _notification, font=font, fill=0)
    elif _notification:
        _notification = None
        _notification_expire = None
