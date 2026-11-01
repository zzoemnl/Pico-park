import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import personajes_menu
menu_dummy = personajes_menu.GestorPersonajesMenu()
gorro_pixel = menu_dummy._obtener_gorro_navideno_pixel_art(64, inclinacion=-4)

from test_banner_multilingual_exploratory import generar_banner_generico

for sz in [42, 46, 50]:
    f_main = pygame.font.SysFont("Microsoft YaHei", sz, bold=True)
    f_sub = pygame.font.SysFont("Microsoft YaHei", 24, bold=True)
    b = generar_banner_generico(
        "皮科的小冒险",
        "在公园里",
        f_main,
        f_sub,
        ancho_cinta=380,
        alto_cinta=46,
        antialias=False,
        hat_offset_x=-20,
        hat_offset_y=-32,
        espaciado_cinta=-14
    )
    pygame.image.save(b, f"scratch/test_banners_multi/banner_zh_sz{sz}.png")

print("Saved size variants")

