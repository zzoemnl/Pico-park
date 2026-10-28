import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
from movimientos import (
    crear_personaje,
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    resolver_colisiones,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    DISTANCIA_SOGA_MAXIMA,
    DISTANCIA_SOGA_REPOSO,
)

p2 = pygame.Rect(420, 410, 220, 24)
p3 = pygame.Rect(120, 355, 220, 24)
p4 = pygame.Rect(360, 300, 220, 24)
todas = [p2, p3, p4]
suelo = pygame.Rect(0, 640, 1300, 80)
mundo_rect = pygame.Rect(0, 0, 1300, 720)
estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

j1 = crear_personaje(p2.left + 5, p2.top - ALTO_HITBOX, "Celeste")
j2 = crear_personaje(p2.left + 30, p2.top - ALTO_HITBOX, "Violeta")
resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=todas)
resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=todas)

print("P2 left:", p2.left, "P3 right:", p3.right, "Gap:", p2.left - p3.right)
print("Init: j1 x:", j1["hitbox"].x, "y:", j1["hitbox"].y)

for f in range(35):
    if f == 0:
        j1["vel_y"] = j1["fuerza_salto"]
        j1["en_suelo"] = False
    j1["vel_x"] = -6
    j2["vel_x"] = 0
    actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, todas, suelo, estado_soga)
    resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=todas)
    resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=todas)
    print(f"f={f:02d}: x={j1['hitbox'].x}, y={j1['hitbox'].y}, bottom={j1['hitbox'].bottom}, vy={j1['vel_y']:.1f}, en_suelo={j1['en_suelo']}")
    if j1["en_suelo"] and p3.collidepoint(j1["hitbox"].centerx, j1["hitbox"].bottom):
        print(f"Landed on P3 at frame {f}!")
        break
