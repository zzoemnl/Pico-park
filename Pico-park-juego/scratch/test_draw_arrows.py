import os
import sys
import pygame
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")

def dibujar_flecha_indicadora(superficie, x, y, direccion, tipo="ruta", tick=0):
    """
    Dibuja un cartel submarino de navegación con flecha direccional e icono temático:
    - tipo: 'llave' (dorado con llave), 'oxigeno' (cian con O2), 'salida' (esmeralda con puerta), 'ruta' (celeste)
    - direccion: 'derecha', 'izquierda', 'arriba', 'abajo'
    """
    es_horiz = direccion in ("derecha", "izquierda")
    w_placa = 52 if es_horiz else 34
    h_placa = 34 if es_horiz else 52
    
    rx = x - w_placa // 2
    ry = y - h_placa // 2
    
    # Placa base de piedra marina oscura con remaches
    pygame.draw.rect(superficie, (12, 22, 34), (rx, ry, w_placa, h_placa), border_radius=6)
    pygame.draw.rect(superficie, (35, 60, 85), (rx, ry, w_placa, h_placa), width=2, border_radius=6)
    
    # Remaches en las esquinas
    for px, py in [(rx + 4, ry + 4), (rx + w_placa - 4, ry + 4), (rx + 4, ry + h_placa - 4), (rx + w_placa - 4, ry + h_placa - 4)]:
        pygame.draw.circle(superficie, (65, 95, 125), (px, py), 1)
        
    # Colores según el tipo
    pulso = int(25 * math.sin(tick * 0.09 + x * 0.02))
    if tipo == "llave":
        col_main = (min(255, 245 + pulso), min(255, 195 + pulso), 40)
        col_light = (255, 250, 180)
    elif tipo == "oxigeno":
        col_main = (50, min(255, 225 + pulso), min(255, 245 + pulso))
        col_light = (205, 255, 255)
    elif tipo == "salida":
        col_main = (min(255, 80 + pulso), min(255, 235 + pulso), 130)
        col_light = (215, 255, 225)
    else: # ruta
        col_main = (60, min(255, 205 + pulso), min(255, 235 + pulso))
        col_light = (210, 250, 255)
        
    cx, cy = x, y
    
    # Coordenadas de la flecha según la dirección
    if direccion == "derecha":
        # Flecha apuntando a la derecha
        pts = [(cx - 10, cy - 8), (cx + 2, cy - 8), (cx + 2, cy - 12), (cx + 14, cy), (cx + 2, cy + 12), (cx + 2, cy + 8), (cx - 10, cy + 8)]
        core = [(cx - 8, cy - 4), (cx + 1, cy - 4), (cx + 1, cy - 7), (cx + 9, cy), (cx + 1, cy + 7), (cx + 1, cy + 4), (cx - 8, cy + 4)]
    elif direccion == "izquierda":
        pts = [(cx + 10, cy - 8), (cx - 2, cy - 8), (cx - 2, cy - 12), (cx - 14, cy), (cx - 2, cy + 12), (cx - 2, cy + 8), (cx + 10, cy + 8)]
        core = [(cx + 8, cy - 4), (cx - 1, cy - 4), (cx - 1, cy - 7), (cx - 9, cy), (cx - 1, cy + 7), (cx - 1, cy + 4), (cx + 8, cy + 4)]
    elif direccion == "arriba":
        pts = [(cx - 8, cy + 10), (cx - 8, cy - 2), (cx - 12, cy - 2), (cx, cy - 14), (cx + 12, cy - 2), (cx + 8, cy - 2), (cx + 8, cy + 10)]
        core = [(cx - 4, cy + 8), (cx - 4, cy - 1), (cx - 7, cy - 1), (cx, cy - 9), (cx + 7, cy - 1), (cx + 4, cy - 1), (cx + 4, cy + 8)]
    else: # abajo
        pts = [(cx - 8, cy - 10), (cx - 8, cy + 2), (cx - 12, cy + 2), (cx, cy + 14), (cx + 12, cy + 2), (cx + 8, cy + 2), (cx + 8, cy - 10)]
        core = [(cx - 4, cy - 8), (cx - 4, cy + 1), (cx - 7, cy + 1), (cx, cy + 9), (cx + 7, cy + 1), (cx + 4, cy + 1), (cx + 4, cy - 8)]
        
    pygame.draw.polygon(superficie, col_main, pts)
    pygame.draw.polygon(superficie, col_light, core)
    
    # Pequeño detalle distintivo según el tipo
    if tipo == "oxigeno":
        # Pequeña burbuja O2 al lado
        b_x = rx + 8 if direccion == "derecha" else (rx + w_placa - 8 if direccion == "izquierda" else cx)
        b_y = ry + 8 if direccion == "abajo" else (ry + h_placa - 8 if direccion == "arriba" else cy)
        pygame.draw.circle(superficie, (180, 250, 255), (b_x, b_y), 3, 1)
    elif tipo == "llave":
        # Pequeño destello dorado
        d_x = rx + 8 if direccion == "derecha" else (rx + w_placa - 8 if direccion == "izquierda" else cx)
        d_y = ry + 8 if direccion == "abajo" else (ry + h_placa - 8 if direccion == "arriba" else cy)
        pygame.draw.circle(superficie, (255, 240, 120), (d_x, d_y), 2)

surf_test = pygame.Surface((300, 200))
surf_test.fill((15, 30, 50))
dibujar_flecha_indicadora(surf_test, 50, 50, "derecha", tipo="llave")
dibujar_flecha_indicadora(surf_test, 130, 50, "arriba", tipo="oxigeno")
dibujar_flecha_indicadora(surf_test, 210, 50, "izquierda", tipo="salida")
dibujar_flecha_indicadora(surf_test, 50, 130, "abajo", tipo="ruta")

out_test = r"C:\Users\Malena\.gemini\antigravity-ide\brain\effb8b14-e88d-402a-8aae-c082111f922f\test_arrows.png"
pygame.image.save(surf_test, out_test)
print("Saved test arrows image to:", out_test)
