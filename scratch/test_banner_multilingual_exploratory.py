import os
import sys
import pygame

sys.path.insert(0, "Pico-park-juego")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import fuentes
from fuentes import obtener_fuente_matrix

os.makedirs("scratch/test_banners_multi", exist_ok=True)

# Helper function to obtain the Christmas hat from personajes_menu
import personajes_menu
menu_dummy = personajes_menu.GestorPersonajesMenu()
gorro_pixel = menu_dummy._obtener_gorro_navideno_pixel_art(64, inclinacion=-4)

def crear_cinta_roja(ancho_total, alto, texto, fuente_sub, antialias=False):
    surf = pygame.Surface((ancho_total, alto + 12), pygame.SRCALPHA)
    w_cola = 42
    h_cinta = alto
    y_cinta = 4
    w_cuerpo = ancho_total - 2 * w_cola
    x_cuerpo = w_cola

    c_borde = (38, 10, 16)
    c_fondo = (205, 30, 40)
    c_luz = (242, 74, 84)
    c_sombra = (135, 18, 25)
    c_doblez = (95, 12, 18)
    c_oro = (255, 215, 75)

    y_cola = y_cinta + 5

    # Cola izquierda (muesca en V)
    pts_izq = [
        (0, y_cola),
        (w_cola + 4, y_cola),
        (w_cola + 4, y_cola + h_cinta),
        (0, y_cola + h_cinta),
        (12, y_cola + h_cinta // 2),
    ]
    pygame.draw.polygon(surf, c_borde, pts_izq)
    pts_izq_in = [
        (2, y_cola + 2),
        (w_cola + 2, y_cola + 2),
        (w_cola + 2, y_cola + h_cinta - 2),
        (2, y_cola + h_cinta - 2),
        (13, y_cola + h_cinta // 2),
    ]
    pygame.draw.polygon(surf, c_sombra, pts_izq_in)

    # Cola derecha (muesca en V)
    x_cola_der = ancho_total - w_cola
    pts_der = [
        (x_cola_der - 4, y_cola),
        (ancho_total, y_cola),
        (ancho_total - 12, y_cola + h_cinta // 2),
        (ancho_total, y_cola + h_cinta),
        (x_cola_der - 4, y_cola + h_cinta),
    ]
    pygame.draw.polygon(surf, c_borde, pts_der)
    pts_der_in = [
        (x_cola_der - 2, y_cola + 2),
        (ancho_total - 2, y_cola + 2),
        (ancho_total - 13, y_cola + h_cinta // 2),
        (ancho_total - 2, y_cola + h_cinta - 2),
        (x_cola_der - 2, y_cola + h_cinta - 2),
    ]
    pygame.draw.polygon(surf, c_sombra, pts_der_in)

    # Pliegues de doblez hacia atrás
    pygame.draw.polygon(surf, c_doblez, [(x_cuerpo, y_cola), (x_cuerpo + 6, y_cinta + h_cinta), (x_cuerpo, y_cinta + h_cinta)])
    pygame.draw.polygon(surf, c_doblez, [(x_cuerpo + w_cuerpo, y_cola), (x_cuerpo + w_cuerpo - 6, y_cinta + h_cinta), (x_cuerpo + w_cuerpo, y_cinta + h_cinta)])

    # Sombra del cuerpo central
    pygame.draw.rect(surf, (20, 8, 12, 160), (x_cuerpo, y_cinta + 3, w_cuerpo, h_cinta), border_radius=4)

    # Cuerpo central de la cinta
    pygame.draw.rect(surf, c_borde, (x_cuerpo - 1, y_cinta - 1, w_cuerpo + 2, h_cinta + 2), border_radius=4)
    pygame.draw.rect(surf, c_fondo, (x_cuerpo, y_cinta, w_cuerpo, h_cinta), border_radius=3)

    # Luces y sombras biseladas
    pygame.draw.line(surf, c_luz, (x_cuerpo + 2, y_cinta + 1), (x_cuerpo + w_cuerpo - 3, y_cinta + 1), 2)
    pygame.draw.line(surf, c_sombra, (x_cuerpo + 2, y_cinta + h_cinta - 2), (x_cuerpo + w_cuerpo - 3, y_cinta + h_cinta - 2), 2)

    # Detalles dorados finos
    pygame.draw.line(surf, c_oro, (x_cuerpo + 6, y_cinta + 3), (x_cuerpo + 6, y_cinta + h_cinta - 4), 2)
    pygame.draw.line(surf, c_oro, (x_cuerpo + w_cuerpo - 7, y_cinta + 3), (x_cuerpo + w_cuerpo - 7, y_cinta + h_cinta - 4), 2)

    # Texto centrado en color crema con sombra
    col_txt = (255, 248, 228)
    col_sombra_txt = (60, 10, 16)
    txt_s = fuente_sub.render(texto, antialias, col_sombra_txt)
    txt_f = fuente_sub.render(texto, antialias, col_txt)
    r_txt = txt_f.get_rect(center=(ancho_total // 2, y_cinta + h_cinta // 2))
    surf.blit(txt_s, r_txt.move(1, 1))
    surf.blit(txt_f, r_txt)

    return surf

def generar_banner_generico(
    texto_principal,
    texto_secundario,
    f_main,
    f_sub,
    ancho_cinta,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-29,
    hat_offset_y=-32,
    espaciado_cinta=-14
):
    txt_raw = f_main.render(texto_principal, antialias, (255, 255, 255))
    tw, th = txt_raw.get_size()

    # Relleno de letras en crema y naranja cálido
    txt_relleno = pygame.Surface((tw, th), pygame.SRCALPHA)
    for y in range(th):
        ratio = y / max(1, th - 1)
        if ratio < 0.42:
            col = (255, 248, 222)   # Crema
        elif ratio < 0.54:
            col = (255, 204, 105)   # Transición dorada
        elif ratio < 0.80:
            col = (248, 126, 34)    # Naranja cálido
        else:
            col = (215, 88, 22)     # Sombra naranja profunda

        for x in range(tw):
            if txt_raw.get_at((x, y))[:3] != (0, 0, 0):
                txt_relleno.set_at((x, y), (*col, 255))

    pad_c = 10
    txt_con_borde = pygame.Surface((tw + pad_c * 2, th + pad_c * 2 + 6), pygame.SRCALPHA)
    c_borde = (38, 16, 12)

    # 1. Sombra desplazada (+4, +5)
    for dx in range(2, 6):
        for dy in range(3, 7):
            txt_con_borde.blit(f_main.render(texto_principal, antialias, (18, 10, 15)), (pad_c + dx, pad_c + dy))

    # 2. Contorno grueso de 2-3 píxeles
    desplazamientos_borde = [
        (-2, 0), (2, 0), (0, -2), (0, 2),
        (-2, -1), (-2, 1), (2, -1), (2, 1),
        (-1, -2), (1, -2), (-1, 2), (1, 2),
        (-1, -1), (1, -1), (-1, 1), (1, 1),
        (-2, -2), (2, -2), (-2, 2), (2, 2),
    ]
    for dx, dy in desplazamientos_borde:
        txt_con_borde.blit(f_main.render(texto_principal, antialias, c_borde), (pad_c + dx, pad_c + dy))

    # 3. Relleno dos tonos
    txt_con_borde.blit(txt_relleno, (pad_c, pad_c))

    # 4. Parches de nieve acumulada en letras clave
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

    # 5. Cinta roja
    cinta_surf = crear_cinta_roja(ancho_cinta, alto_cinta, texto_secundario, f_sub, antialias=antialias)

    # 6. Composición del banner
    pad_top_banner = 38
    ancho_total = max(txt_con_borde.get_width() + 100, ancho_cinta + 50)
    alto_total = txt_con_borde.get_height() + cinta_surf.get_height() + pad_top_banner + 6

    banner = pygame.Surface((ancho_total, alto_total), pygame.SRCALPHA)

    x_txt = (ancho_total - txt_con_borde.get_width()) // 2
    y_txt = pad_top_banner
    banner.blit(txt_con_borde, (x_txt, y_txt))

    x_cinta = (ancho_total - cinta_surf.get_width()) // 2
    y_cinta = y_txt + txt_con_borde.get_height() + espaciado_cinta
    banner.blit(cinta_surf, (x_cinta, y_cinta))

    # 7. Gorrito
    gorro = gorro_pixel
    x_gorro = x_txt + pad_c + tw + hat_offset_x
    y_gorro = y_txt + pad_c + hat_offset_y
    banner.blit(gorro, (x_gorro, y_gorro))

    # 8. Estrellitas doradas navideñas
    def _estrella(cx, cy):
        if 0 <= cx < banner.get_width() and 0 <= cy < banner.get_height():
            banner.set_at((cx, cy), (255, 255, 230))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                if 0 <= cx + dx < banner.get_width() and 0 <= cy + dy < banner.get_height():
                    banner.set_at((cx + dx, cy + dy), (255, 218, 60))

    _estrella(x_txt + pad_c + 12, y_txt + 4)
    _estrella(x_gorro + 68, y_gorro + 16)
    _estrella(x_cinta + 16, y_cinta + 32)
    _estrella(x_cinta + ancho_cinta - 16, y_cinta + 32)

    return banner

# --- CASOS DE PRUEBA ---
# 1. ESPAÑOL
b_es = generar_banner_generico(
    "LAS AVENTURILLAS",
    "DE PICO EN EL PARQUE",
    obtener_fuente_matrix(38),
    obtener_fuente_matrix(23),
    ancho_cinta=665,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-29,
    hat_offset_y=-32,
    espaciado_cinta=-14
)
pygame.image.save(b_es, "scratch/test_banners_multi/banner_es.png")

# 2. INGLÉS - Opción A: "PICO'S LITTLE ADVENTURES" / "IN THE PARK"
b_en_a = generar_banner_generico(
    "PICO'S LITTLE ADVENTURES",
    "IN THE PARK",
    obtener_fuente_matrix(30),
    obtener_fuente_matrix(23),
    ancho_cinta=460,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-26,
    hat_offset_y=-30,
    espaciado_cinta=-14
)
pygame.image.save(b_en_a, "scratch/test_banners_multi/banner_en_a.png")

# 3. INGLÉS - Opción B: "PICO'S" / "LITTLE ADVENTURES IN THE PARK"
b_en_b = generar_banner_generico(
    "PICO'S",
    "LITTLE ADVENTURES IN THE PARK",
    obtener_fuente_matrix(42),
    obtener_fuente_matrix(20),
    ancho_cinta=680,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-24,
    hat_offset_y=-34,
    espaciado_cinta=-14
)
pygame.image.save(b_en_b, "scratch/test_banners_multi/banner_en_b.png")

# 4. CHINO - Opción A: "皮科的小冒险" / "在公园里"
f_zh_main_yahei = pygame.font.SysFont("Microsoft YaHei", 42, bold=True)
f_zh_sub_yahei = pygame.font.SysFont("Microsoft YaHei", 24, bold=True)
b_zh_a = generar_banner_generico(
    "皮科的小冒险",
    "在公园里",
    f_zh_main_yahei,
    f_zh_sub_yahei,
    ancho_cinta=360,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-20,
    hat_offset_y=-32,
    espaciado_cinta=-14
)
pygame.image.save(b_zh_a, "scratch/test_banners_multi/banner_zh_a.png")

# 5. CHINO - Opción B: "皮科在公园里" / "的小冒险"
b_zh_b = generar_banner_generico(
    "皮科在公园里",
    "的小冒险",
    f_zh_main_yahei,
    f_zh_sub_yahei,
    ancho_cinta=360,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-20,
    hat_offset_y=-32,
    espaciado_cinta=-14
)
pygame.image.save(b_zh_b, "scratch/test_banners_multi/banner_zh_b.png")

# 6. CHINO - Opción C: "皮科在公园里的小冒险" (todo arriba)
# O qué tal "皮科" / "在公园里的小冒险"
b_zh_c = generar_banner_generico(
    "皮科",
    "在公园里的小冒险",
    pygame.font.SysFont("Microsoft YaHei", 52, bold=True),
    pygame.font.SysFont("Microsoft YaHei", 22, bold=True),
    ancho_cinta=460,
    alto_cinta=46,
    antialias=False,
    hat_offset_x=-20,
    hat_offset_y=-38,
    espaciado_cinta=-14
)
pygame.image.save(b_zh_c, "scratch/test_banners_multi/banner_zh_c.png")

print("All exploratory banners generated successfully!")
