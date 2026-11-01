import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
import sprites
import fuentes

W, H = 272, 80

def get_menu_btn(base_img, text, text_color, sz=22, idioma="zh"):
    if idioma == "es":
        return sprites.cargar_boton_escalado(base_img, W, H)
    return sprites.generar_boton_con_texto(base_img, W, H, text, text_color, sz, 0, idioma)

os.makedirs("scratch/test_menu_btns", exist_ok=True)

for idm, texts in [
    ("en", ["PLAY", "CHARACTERS", "SETTINGS", "QUIT"]),
    ("zh", ["开始游戏", "角色设置", "设置", "退出游戏"])
]:
    b1 = get_menu_btn("Menu/jugar.png", texts[0], (26, 83, 29), 24, idm)
    b2 = get_menu_btn("Menu/personajes.png", texts[1], (45, 30, 80), 22, idm)
    b3 = get_menu_btn("Menu/opciones.png", texts[2], (80, 45, 20), 24, idm)
    b4 = get_menu_btn("Menu/salir.png", texts[3], (255, 255, 255), 24, idm)
    
    strip = pygame.Surface((W, H * 4 + 30), pygame.SRCALPHA)
    for i, b in enumerate([b1, b2, b3, b4]):
        if b:
            strip.blit(b, (0, i * (H + 10)))
    pygame.image.save(strip, f"scratch/test_menu_btns/strip_{idm}.png")

print("Saved menu button strips")

