import os
import sys
import pygame
sys.path.insert(0, os.path.abspath('.'))
from personajes_menu import GestorPersonajesMenu
from fuentes import obtener_fuente_matrix

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

src_hat_path = r'..\Sprites\Objetos\gorro_navideno_original.png'
src_hat = pygame.image.load(src_hat_path).convert_alpha()

# Crop to bounding box
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
print(f"BBox cropped size: {cw}x{ch}")

# Invert horizontally (mirror left-to-right)
flipped = pygame.transform.flip(cropped, True, False)

# Let's inspect where the letters of LAS AVENTURILLAS are
f_main = obtener_fuente_matrix(38)
txt_raw = f_main.render("LAS AVENTURILLAS", False, (255, 255, 255))
tw, th = txt_raw.get_size()
pad_c = 10

# Let's test a few combinations of (target_w, rotation_deg, x_offset, y_offset)
os.makedirs("scratch/test_gorro_variants", exist_ok=True)

# Build a base title banner without any hat
gestor = GestorPersonajesMenu()

# Variations to test:
# target_w around 54, 58, 62, 66
# angle: 0, 4, 8, 12, -4, -8
# We want the hat to rest naturally on the upper-right letters:
# The rightmost letter is S (ends at tw = 736).
# The upper-right of the title is x around x_txt + pad_c + tw - target_w + offset
# In personajes_menu:
# tw is 736. txt_con_borde width is tw + pad_c * 2 = 756.
# x_txt = (ancho_total - 756) // 2.
# So the rightmost letters 'AS' are around x_txt + pad_c + tw - 55 to x_txt + pad_c + tw.

test_configs = [
    # (name, target_w, angle, rel_x_from_right, y_offset)
    ("w54_a0", 54, 0, 18, -20),
    ("w54_a_minus6", 54, -6, 18, -20),
    ("w54_a_plus6", 54, 6, 18, -20),
    ("w58_a0", 58, 0, 16, -22),
    ("w58_a_minus8", 58, -8, 16, -22),
    ("w58_a_plus6", 58, 6, 16, -22),
    ("w62_a0", 62, 0, 14, -24),
    ("w62_a_minus6", 62, -6, 14, -24),
    ("w62_a_minus10", 62, -10, 14, -24),
    ("w62_a_plus6", 62, 6, 14, -24),
    ("w66_a0", 66, 0, 12, -26),
    ("w66_a_minus8", 66, -8, 12, -26),
]

for name, tw_hat, angle, right_offset, y_off in test_configs:
    th_hat = int(round(tw_hat * ch / cw))
    scaled_hat = pygame.transform.scale(flipped, (tw_hat, th_hat))
    if angle != 0:
        rot_hat = pygame.transform.rotate(scaled_hat, angle)
    else:
        rot_hat = scaled_hat
    
    # Render on top of menu
    gestor._banner_titulo = None # Force regenerate
    banner = gestor._banner_titulo or gestor._generar_banner_titulo()
    # We want to replace or place this hat
    banner_copy = banner.copy()
    
    # Calculate pos
    ancho_total = banner_copy.get_width()
    txt_w = tw + pad_c * 2
    x_txt = (ancho_total - txt_w) // 2
    y_txt = 10
    
    # Right edge of letters is x_txt + pad_c + tw
    # Place hat so it sits on 'AS'
    hat_x = x_txt + pad_c + tw - tw_hat + right_offset
    hat_y = y_txt + pad_c + y_off
    
    banner_copy.blit(rot_hat, (hat_x, hat_y))
    
    import main, sprites
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
    surf = pygame.Surface((1280, 720))
    gestor.dibujar_menu_completo(surf, botones_menu_datos=botones_menu_datos, pos_mouse=(0, 0), spr_x=spr_x, rect_x=rect_btn_x, fuente_titulo=fuente_tit)
    # Overwrite banner area on surf
    r_banner = banner_copy.get_rect(centerx=1280 // 2, top=56)
    surf.blit(banner_copy, r_banner)
    
    # Save zoomed crop of the title area (from x=600 to 1100, y=30 to 180)
    zoom = surf.subsurface((650, 40, 450, 130)).copy()
    pygame.image.save(zoom, f"scratch/test_gorro_variants/{name}_zoom.png")
    pygame.image.save(surf, f"scratch/test_gorro_variants/{name}_full.png")

print("Saved all test variants!")
