import os
import sys
import pygame

sys.path.insert(0, os.path.abspath("."))
os.chdir(os.path.abspath("."))

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from personajes_menu import GestorPersonajesMenu
from fuentes import obtener_fuente_matrix

gestor = GestorPersonajesMenu(1280, 720)
os.makedirs("scratch/test_gorro_shift2", exist_ok=True)

# Generate custom banner with variable off_x
for off in [26, 27, 28]:
    f_main = obtener_fuente_matrix(38)
    f_sub = obtener_fuente_matrix(23)
    texto_principal = "LAS AVENTURILLAS"
    texto_secundario = "DE PICO EN EL PARQUE"

    txt_raw = f_main.render(texto_principal, False, (255, 255, 255))
    tw, th = txt_raw.get_size()

    txt_relleno = pygame.Surface((tw, th), pygame.SRCALPHA)
    for y in range(th):
        ratio = y / max(1, th - 1)
        if ratio < 0.42:
            col = (255, 248, 222)
        elif ratio < 0.54:
            col = (255, 204, 105)
        elif ratio < 0.80:
            col = (248, 126, 34)
        else:
            col = (215, 88, 22)

        for x in range(tw):
            if txt_raw.get_at((x, y))[:3] != (0, 0, 0):
                txt_relleno.set_at((x, y), col)

    pad_c = 10
    txt_con_borde = pygame.Surface((tw + pad_c * 2, th + pad_c * 2), pygame.SRCALPHA)
    c_sombra = (22, 12, 10, 230)
    for dy in range(4, 8):
        for dx in range(-1, 3):
            txt_con_borde.blit(txt_raw, (pad_c + dx, pad_c + dy))
    for x in range(txt_con_borde.get_width()):
        for y in range(txt_con_borde.get_height()):
            if txt_con_borde.get_at((x, y)).a > 0:
                txt_con_borde.set_at((x, y), c_sombra)

    c_borde = (34, 14, 8)
    for ox in range(-3, 4):
        for oy in range(-3, 4):
            if ox * ox + oy * oy <= 9 and (ox != 0 or oy != 0):
                for x in range(tw):
                    for y in range(th):
                        if txt_raw.get_at((x, y))[:3] != (0, 0, 0):
                            txt_con_borde.set_at((pad_c + x + ox, pad_c + y + oy), c_borde)

    txt_con_borde.blit(txt_relleno, (pad_c, pad_c))

    # Nieve acumulada
    c_nieve = (255, 255, 255)
    c_nieve_sombra = (208, 226, 246)
    c_nieve_borde = (165, 190, 218)
    for col_x in range(pad_c + 2, pad_c + tw - 2):
        primer_y = None
        for row_y in range(pad_c, pad_c + th):
            if txt_con_borde.get_at((col_x, row_y)).a > 200:
                primer_y = row_y
                break
        if primer_y is not None and primer_y < pad_c + 12:
            rel_x = col_x - pad_c
            if (rel_x % 44) < 22 and rel_x < tw - 20:
                h_nieve = 2 + ((rel_x % 5) % 2)
                for ny in range(h_nieve):
                    col_p = c_nieve if ny < h_nieve - 1 else c_nieve_sombra
                    txt_con_borde.set_at((col_x, primer_y - ny), col_p)
                    if ny == h_nieve - 1:
                        txt_con_borde.set_at((col_x, primer_y - ny - 1), c_nieve_borde)

    ancho_cinta = 665
    alto_cinta = 46
    cinta_surf = gestor._crear_cinta_roja(ancho_cinta, alto_cinta, texto_secundario, f_sub)

    pad_top_banner = 32
    ancho_total = max(txt_con_borde.get_width() + 100, ancho_cinta + 50)
    alto_total = txt_con_borde.get_height() + cinta_surf.get_height() + pad_top_banner + 6

    banner = pygame.Surface((ancho_total, alto_total), pygame.SRCALPHA)
    x_txt = (ancho_total - txt_con_borde.get_width()) // 2
    y_txt = pad_top_banner
    banner.blit(txt_con_borde, (x_txt, y_txt))

    x_cinta = (ancho_total - cinta_surf.get_width()) // 2
    y_cinta = y_txt + txt_con_borde.get_height() - 14
    banner.blit(cinta_surf, (x_cinta, y_cinta))

    gorro = gestor._obtener_gorro_navideno_pixel_art(52, inclinacion=-4)
    x_gorro = x_txt + pad_c + tw - off
    y_gorro = y_txt + pad_c - 26
    banner.blit(gorro, (x_gorro, y_gorro))

    # Composite on background
    surf = pygame.Surface((1280, 720))
    gestor.dibujar_escenario(surf)
    r_ban = banner.get_rect(centerx=1280 // 2, top=40)
    surf.blit(banner, r_ban)

    crop = surf.subsurface(pygame.Rect(780, 20, 300, 160))
    pygame.image.save(crop, f"scratch/test_gorro_shift2/zoom_off{off}.png")
    print(f"Saved zoom for off={off}")

print("Done comparing!")
