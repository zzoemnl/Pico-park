import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
import sprites

W, H = 272, 80

buttons_cfg = [
    ("Menu/jugar.png", "开始游戏", (27, 82, 36), (155, 255, 124), 26),
    ("Menu/personajes.png", "角色设置", (42, 68, 124), (122, 230, 255), 26),
    ("Menu/opciones.png", "设置", (115, 67, 16), (255, 243, 123), 28),
    ("Menu/salir.png", "退出游戏", (255, 255, 255), (255, 159, 99), 26),
]

strip = pygame.Surface((W, H * 4 + 30), pygame.SRCALPHA)

for i, (path, text, col_txt, bg_color, sz) in enumerate(buttons_cfg):
    base_img = sprites.cargar_boton_escalado(path, W, H)
    surf = base_img.copy()
    
    # Fill interior
    rect_int = pygame.Rect(8, 8, W - 16, H - 24)
    pygame.draw.rect(surf, bg_color, rect_int)
    
    f = pygame.font.SysFont("Microsoft YaHei", sz, bold=True)
    
    # Sombra para salir si es blanco
    if col_txt == (255, 255, 255):
        ts = f.render(text, True, (127, 49, 19))
        rs = ts.get_rect(center=(W // 2 + 1, (H - 8) // 2 + 1))
        surf.blit(ts, rs)
        
    t = f.render(text, True, col_txt)
    r = t.get_rect(center=(W // 2, (H - 8) // 2))
    surf.blit(t, r)
    
    strip.blit(surf, (0, i * (H + 10)))

pygame.image.save(strip, "scratch/test_menu_btns/strip_zh_fixed.png")
print("Saved strip_zh_fixed.png")
