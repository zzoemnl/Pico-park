import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
import sprites
import fuentes

pygame.init()

def generar_boton_modo_traducido(sprite_base, w, h, tit, sub, col_tit, col_sub, col_bg, idioma):
    marco = sprites.generar_marco_boton(sprite_base, w, h)
    surf = marco.copy()
    
    # Rellenar el centro con el color interior del botón (dejando bordes y bisel inferior)
    # Borde: 6px arriba/izq/der, 14px abajo (bisel)
    rect_interior = pygame.Rect(6, 6, w - 12, h - 22)
    pygame.draw.rect(surf, col_bg, rect_interior)
    
    # Línea decorativa clara inferior que separa el bisel
    # (reconstruir si quedó tapada o dejarla)
    
    if idioma == "zh":
        f_tit = pygame.font.SysFont("Microsoft YaHei", 30, bold=True)
        f_sub = pygame.font.SysFont("Microsoft YaHei", 15, bold=False)
        t_tit_s = f_tit.render(tit, True, (0, 0, 0))
        t_tit = f_tit.render(tit, True, col_tit)
        t_sub = f_sub.render(sub, True, col_sub)
        
        r_tit = t_tit.get_rect(center=(w // 2, 38))
        surf.blit(t_tit_s, r_tit.move(1, 1))
        surf.blit(t_tit, r_tit)
        
        r_sub = t_sub.get_rect(center=(w // 2, 70))
        surf.blit(t_sub, r_sub)
    elif idioma == "en":
        f_tit = fuentes.obtener_fuente_titulo(26)
        f_sub = fuentes.obtener_fuente_texto_pequeno(16)
        t_tit_s = f_tit.render(tit, False, (0, 0, 0))
        t_tit = f_tit.render(tit, False, col_tit)
        t_sub = f_sub.render(sub, False, col_sub)
        
        r_tit = t_tit.get_rect(center=(w // 2, 36))
        surf.blit(t_tit_s, r_tit.move(1, 1))
        surf.blit(t_tit, r_tit)
        
        r_sub = t_sub.get_rect(center=(w // 2, 70))
        surf.blit(t_sub, r_sub)
        
    return surf

b_c_zh = generar_boton_modo_traducido(
    "Menu/boton-continuar-cargar....png", 425, 100,
    "继续游戏", "加载保存的存档并查看关卡进度",
    (18, 55, 24), (25, 75, 30), (142, 235, 120), "zh"
)
pygame.image.save(b_c_zh, "scratch/test_btn_continuar_zh.png")

b_n_zh = generar_boton_modo_traducido(
    "mundos/boton-nueva-partida-reiniciar....png", 425, 100,
    "新建游戏", "重新开始，从世界 1 - 关卡 1 开始",
    (95, 25, 35), (115, 30, 42), (255, 138, 142), "zh"
)
pygame.image.save(b_n_zh, "scratch/test_btn_nueva_zh.png")

print("Generated translated mode buttons!")

