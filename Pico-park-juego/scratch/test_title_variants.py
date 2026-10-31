import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Pico-park-juego"))

import pygame
from test_landscape import generar_fondo_atardecer
import fuentes

def comparar_variantes():
    pygame.init()
    W, H = 1280, 720
    
    # Variante A: Placa pergamino crema/dorado cálido con texto en BORDÓ / VIOLETA PROFUNDO
    pA = pygame.Surface((W, H))
    fondoA = generar_fondo_atardecer(W, H)
    pA.blit(fondoA, (0, 0))

    fuente_pixel_titulo = fuentes.obtener_fuente_titulo(36, tamano_fallback=36)
    fuente_subtitulo = fuentes.obtener_fuente_subtitulo(24)

    w_placa, h_placa = 720, 108
    x_placa = (W - w_placa) // 2
    y_placa = 42

    surf_placaA = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    # Fondo pergamino suave semitransparente
    pygame.draw.rect(surf_placaA, (252, 242, 228, 225), (0, 0, w_placa, h_placa), border_radius=16)
    # Borde bordó / coral cálido escalonado
    pygame.draw.rect(surf_placaA, (85, 28, 48, 240), (0, 0, w_placa, h_placa), width=3, border_radius=16)
    pygame.draw.rect(surf_placaA, (235, 142, 72, 180), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)
    # Gemas esquinas
    for cx_d, cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
        pygame.draw.circle(surf_placaA, (215, 110, 42), (cx_d, cy_d), 4)
        pygame.draw.circle(surf_placaA, (255, 240, 200), (cx_d, cy_d), 2)

    pA.blit(surf_placaA, (x_placa, y_placa))

    # Título en BORDÓ / VIOLETA PROFUNDO
    txt_tit = "MODO DE JUEGO"
    t_somb = fuente_pixel_titulo.render(txt_tit, True, (225, 205, 185))
    t_tit = fuente_pixel_titulo.render(txt_tit, True, (68, 20, 42))  # Bordó / violeta profundo
    rect_tit = t_tit.get_rect(center=(W // 2, y_placa + 40))
    pA.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
    pA.blit(t_tit, rect_tit)

    # Subtítulo en marrón cálido
    txt_sub = "Selecciona cómo deseas comenzar tu aventura"
    t_sub_s = fuente_subtitulo.render(txt_sub, True, (255, 255, 255))
    t_sub = fuente_subtitulo.render(txt_sub, True, (108, 52, 45))
    rect_sub = t_sub.get_rect(center=(W // 2, y_placa + 80))
    pA.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
    pA.blit(t_sub, rect_sub)

    pygame.image.save(pA, "scratch/variante_A_crema_bordo.png")

    # Variante B: Placa ciruela oscura con texto bordó iluminado con contorno dorado
    pB = pygame.Surface((W, H))
    fondoB = generar_fondo_atardecer(W, H)
    pB.blit(fondoB, (0, 0))

    surf_placaB = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    pygame.draw.rect(surf_placaB, (42, 16, 32, 190), (0, 0, w_placa, h_placa), border_radius=16)
    pygame.draw.rect(surf_placaB, (238, 148, 75, 230), (0, 0, w_placa, h_placa), width=3, border_radius=16)
    pygame.draw.rect(surf_placaB, (255, 220, 140, 140), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)
    pB.blit(surf_placaB, (x_placa, y_placa))

    # Título bordó con resplandor dorado
    t_glow = fuente_pixel_titulo.render(txt_tit, True, (255, 215, 140))
    t_bordo = fuente_pixel_titulo.render(txt_tit, True, (138, 38, 62)) # Bordó intenso
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1)]:
        pB.blit(t_glow, (rect_tit.x + dx, rect_tit.y + dy))
    pB.blit(t_bordo, rect_tit)

    t_sub_b = fuente_subtitulo.render(txt_sub, True, (255, 218, 180))
    pB.blit(t_sub_b, rect_sub)

    pygame.image.save(pB, "scratch/variante_B_bordo_glow.png")
    print("Variantes guardadas")

if __name__ == '__main__':
    comparar_variantes()
