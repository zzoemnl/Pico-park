import os
import sys
import pygame

sys.path.insert(0, os.path.abspath('.'))
import main
import sprites
from personajes_menu import GestorPersonajesMenu
from fuentes import obtener_fuente_matrix

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

src_hat_path = r'..\Sprites\Objetos\gorro_navideno_original.png'
src_hat = pygame.image.load(src_hat_path).convert_alpha()

w, h = src_hat.get_size()
min_x, max_x, min_y, max_y = w, 0, h, 0
for y in range(h):
    for x in range(w):
        if src_hat.get_at((x, y))[3] > 0:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

cropped = src_hat.subsurface((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)).copy()
cw, ch = cropped.get_size()
flipped = pygame.transform.flip(cropped, True, False)

f_main = obtener_fuente_matrix(38)
txt_raw = f_main.render("LAS AVENTURILLAS", False, (255, 255, 255))
tw, th = txt_raw.get_size()
pad_c = 10

os.makedirs("scratch/test_fine", exist_ok=True)

# We will create a clean title banner WITHOUT the old hat on the left
gestor = GestorPersonajesMenu()

# Let's inspect fine variants
# Let's see the coordinates:
# 'S' in LAS AVENTURILLAS ends at tw = 736. The 'S' starts around 736 - 36 = 700.
# The 'A' before it is around 660 to 695.
# Let's test sizes: 48, 52, 56
# Angles: -4, 0, 4
# Y offsets: -26, -24, -22, -20, -18
# X offsets: to place it right over the S

fine_variants = [
    # (name, w, angle, x_from_end, y_offset)
    # x_from_end: pixels from the right end of the text (tw)
    ("size50_a0_y24", 50, 0, 48, -24),
    ("size50_a0_y26", 50, 0, 48, -26),
    ("size50_am4_y24", 50, -4, 48, -24),
    ("size52_a0_y24", 52, 0, 50, -24),
    ("size52_a0_y26", 52, 0, 50, -26),
    ("size52_am4_y24", 52, -4, 50, -24),
    ("size52_am6_y24", 52, -6, 50, -24),
    ("size52_ap4_y24", 52, 4, 50, -24),
    ("size54_a0_y24", 54, 0, 52, -24),
    ("size54_a0_y26", 54, 0, 52, -26),
    ("size54_am4_y24", 54, -4, 52, -24),
    ("size54_am4_y26", 54, -4, 52, -26),
    ("size54_am6_y24", 54, -6, 52, -24),
    ("size56_a0_y26", 56, 0, 54, -26),
    ("size56_am4_y26", 56, -4, 54, -26),
    ("size56_am6_y26", 56, -6, 54, -26),
]

# Set up menu buttons for drawing
ANCHO_BOTON, ALTO_BOTON, ESPACIO = 272, 80, 14
x_centro = (1280 - ANCHO_BOTON) // 2
y_inicio = (720 - ((ALTO_BOTON * 4) + (ESPACIO * 3))) // 2 + 35
btn_jugar = pygame.Rect(x_centro, y_inicio, ANCHO_BOTON, ALTO_BOTON)
btn_personajes = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO), ANCHO_BOTON, ALTO_BOTON)
btn_config = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON)
btn_salir = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON)
spr_j = sprites.cargar_boton_escalado("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON)
spr_p = sprites.cargar_boton_escalado("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON)
spr_o = sprites.cargar_boton_escalado("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON)
spr_s = sprites.cargar_boton_escalado("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON)
spr_x = sprites.cargar_boton_escalado("HUD/boton-x.png", 44, 52)
rect_btn_x = pygame.Rect(1280 - 16 - 44, 16, 44, 52)
botones_menu_datos = [
    (btn_jugar, spr_j, sprites.aclarar_boton(spr_j)),
    (btn_personajes, spr_p, sprites.aclarar_boton(spr_p)),
    (btn_config, spr_o, sprites.aclarar_boton(spr_o)),
    (btn_salir, spr_s, sprites.aclarar_boton(spr_s)),
]
fuente_tit = main.obtener_fuente_titulo(main.TAMANO_TITULO, negrita=True, tamano_fallback=48)

for name, tw_hat, angle, x_from_end, y_off in fine_variants:
    th_hat = int(round(tw_hat * ch / cw))
    scaled_hat = pygame.transform.scale(flipped, (tw_hat, th_hat))
    if angle != 0:
        rot_hat = pygame.transform.rotate(scaled_hat, angle)
    else:
        rot_hat = scaled_hat
        
    # We will generate banner directly by modifying gestor temporarily or blitting
    # First, let's create a banner without the left hat:
    banner = gestor._generar_banner_titulo().copy()
    
    ancho_total = banner.get_width()
    txt_w = tw + pad_c * 2
    x_txt = (ancho_total - txt_w) // 2
    y_txt = 10
    
    # Calculate hat position
    # The rightmost pixel of 'LAS AVENTURILLAS' is at x_txt + pad_c + tw
    hat_x = x_txt + pad_c + tw - x_from_end
    hat_y = y_txt + pad_c + y_off
    
    banner.blit(rot_hat, (hat_x, hat_y))
    
    surf = pygame.Surface((1280, 720))
    gestor.dibujar_menu_completo(surf, botones_menu_datos=botones_menu_datos, pos_mouse=(0, 0), spr_x=spr_x, rect_x=rect_btn_x, fuente_titulo=fuente_tit)
    r_banner = banner.get_rect(centerx=1280 // 2, top=56)
    surf.blit(banner, r_banner)
    
    # Zoom of the upper right of the title (x=800 to 1100, y=35 to 150)
    zoom = surf.subsurface((820, 35, 260, 115)).copy()
    pygame.image.save(zoom, f"scratch/test_fine/{name}_zoom.png")

print("Fine tuning variants generated!")
