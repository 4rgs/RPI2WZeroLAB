from PIL import Image, ImageDraw, ImageFont
import psutil, socket, datetime, os, glob

# ——— Configuración general ——————————————————————
FONT_PATH   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WIDTH, HEIGHT = 250, 122
MARGIN_X    = 2   # margen izquierdo para el marco
INDENT_TEXT = 4   # indentado interno en px

# Fuentes
font_small = ImageFont.truetype(FONT_PATH, 12)  # barra superior
font_mod   = ImageFont.truetype(FONT_PATH, 12)  # módulos

# Precarga iconos de batería
battery_imgs = sorted(
    glob.glob("assets/battery_*.bmp"),
    key=lambda p: int(os.path.splitext(os.path.basename(p))[0].split("_")[1])
)

def battery_level(voltage):
    try:
        v = float(voltage)
        pct = (v - 3.3) / (4.2 - 3.3) * 100 if v <= 5 else v
        return max(0, min(100, pct))
    except:
        return 0

def draw_top_bar(draw, info, image):
    """
    Dibuja:
      • Icono de batería en la esquina superior izquierda
      • Hostname centrado
      • Hora (HH:MM) en la esquina superior derecha
    """
    # --- Datos básicos ---
    hostname = socket.gethostname()
    time_str = datetime.datetime.now().strftime("%H:%M")

    # --- Icono de batería ---
    pct = battery_level(info.get("battery", 0))
    idx = int(pct / 100 * (len(battery_imgs) - 1))
    try:
        batt = Image.open(battery_imgs[idx]).convert("1")
    except:
        batt = Image.new("1", (24, 12), 1)
    image.paste(batt, (5, 2))

    # --- Hostname centrado ---
    host_txt = hostname
    bx = draw.textbbox((0, 0), host_txt, font=font_small)
    x_host = (WIDTH - (bx[2] - bx[0])) // 2
    draw.text((x_host, 0), host_txt, font=font_small, fill=0)

    # --- Hora en esquina superior derecha ---
    bx2 = draw.textbbox((0, 0), time_str, font=font_small)
    x_time = WIDTH - (bx2[2] - bx2[0]) - 5
    draw.text((x_time, 0), time_str, font=font_small, fill=0)

def draw_static_frame(draw):
    # Altura de la barra superior
    header_h = draw.textbbox((0,0), "Ay", font=font_small)[3] + 2
    y0 = header_h
    y1 = HEIGHT - 1

    # Medimos un ancho de carácter monoespaciado
    cw = draw.textbbox((0,0), "A", font=font_mod)[2]

    # Cuántos caracteres caben entre los márgenes
    total_chars = (WIDTH - 2*MARGIN_X) // cw
    if total_chars < 2:
        total_chars = 2
    interior = total_chars + 4

    # Construimos las líneas de borde
    top_border    = "┌" + "─" * interior + "┐"
    bottom_border = "└" + "─" * interior + "┘"

    # Coordenadas X de los bordes verticales
    x_left  = MARGIN_X
    x_right = MARGIN_X + (total_chars - 1) * cw

    # Altura de línea de módulo
    th = draw.textbbox((0,0), "Ay", font=font_mod)[3]

    # Dibuja borde superior e inferior
    draw.text((x_left,       y0),       top_border,    font=font_mod, fill=0)
    draw.text((x_left,       y1 - th + 1), bottom_border, font=font_mod, fill=0)

    # Dibuja las barras laterales a lo largo del espacio
    for y in range(y0 + th, y1 - th + 1, th):
        draw.text((x_left,  y), "│", font=font_mod, fill=0)
        draw.text((x_right, y), "│", font=font_mod, fill=0)

# ——— Dibuja el contenido de un módulo con indentado ——————
def draw_module_content(draw, lines):
    # Límites verticales
    header_h = draw.textbbox((0,0),"Ay", font=font_small)[3] + 2
    y0 = header_h
    y1 = HEIGHT - 1

    # Ancho de esquina para calcular indent
    cw_corner = draw.textbbox((0,0),"┌",font=font_mod)[2]
    indent_x = MARGIN_X + cw_corner + INDENT_TEXT

    # Altura de línea
    th = draw.textbbox((0,0),"Ay", font=font_mod)[3]
    n  = len(lines)

    # Dibuja cada línea repartida verticalmente
    for i, line in enumerate(lines):
        y_line = y0 + int((i+1)*(y1-y0)/(n+1)) - th//2
        draw.text((indent_x, y_line), line, font=font_mod, fill=0)

# ——— Módulos de contenido ————————————————————————
def draw_wifi_info(draw, info):
    lines = [
        f"SSID: {info.get('ssid','N/A')}",
        f"IP  : {info.get('ip','N/A')}",
        f"Sig : {info.get('signal','N/A')} dBm"
    ]
    draw_module_content(draw, lines)

def draw_bt_info(draw, info):
    lines = [
        f"State  : {info.get('bt_status', 'N/A')}",
        f"OwnMAC : {info.get('bt_own_mac', 'N/A')}",
        f"Peer   : {info.get('bt_peer_mac', 'N/A')}",
        f"Name   : {info.get('bt_peer_name', 'N/A')}",
        f"Disc   : {info.get('bt_discoverable', 'no')}",
    ]
    draw_module_content(draw, lines)

def draw_system_info(draw, info):
    # 1) Calculamos los anchos necesarios
    # Ancho de la esquina '┌'
    cw_corner = draw.textbbox((0,0), "┌", font=font_mod)[2]
    # Ancho de un guión '─'
    cw_line   = draw.textbbox((0,0), "─", font=font_mod)[2]

    # 2) Preparamos las líneas a mostrar
    core = [
        f"CPU: {info['cpu']}%",
        f"RAM: {info['ram']}%"
    ]
    procs = info.get("top_processes", [])
    # Cantidad de guiones que caben entre los márgenes
    dash_count = (WIDTH - 2*MARGIN_X - 2*cw_corner) // cw_line
    separator = "─" * dash_count

    proc_lines = [f"{p['name'][:10].ljust(10)} {p['cpu']}%" for p in procs]
    lines = core + [separator] + proc_lines

    # 3) Dibujamos el contenido dentro del marco
    draw_module_content(draw, lines)

def draw_audio_info(draw, info):
    lines = [
        f"Estado : {info.get('mpd_status', 'N/A')}",
        f"Track  : {info.get('mpd_song', '')}",
        f"Artista: {info.get('mpd_artist', '')}",
        f"Tiempo : {info.get('mpd_time', '')}",
        f"Volumen: {info.get('mpd_volume', '')}"
    ]
    draw_module_content(draw, lines)

# ——— Render final con rotación ——————————————————
def render_ui(info, mode):
    image = Image.new('1', (WIDTH, HEIGHT), 255)
    draw  = ImageDraw.Draw(image)

    draw_top_bar(draw, info, image)
    draw_static_frame(draw)

    if mode == 0:
        draw_wifi_info(draw, info)
    elif mode == 1:
        draw_bt_info(draw, info)
    elif mode == 2:
        draw_system_info(draw, info)
    else:
        draw_audio_info(draw, info)

    return image
