import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
import personajes_menu
import configuracion

g = personajes_menu.GestorPersonajesMenu()
os.makedirs("scratch/banners_real", exist_ok=True)

for idm in ["es", "en", "zh"]:
    b = g._generar_banner_titulo(idm)
    pygame.image.save(b, f"scratch/banners_real/banner_{idm}.png")
    print(f"Banner {idm}: size {b.get_size()}")

print("Saved all real banners!")

