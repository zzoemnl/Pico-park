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

plat_a = pygame.Rect(180, 465, 220, 24)
plat_b = pygame.Rect(440, 415, 220, 24)
todas = [plat_a, plat_b]
suelo = pygame.Rect(0, 640, 1500, 80)
mundo_rect = pygame.Rect(0, 0, 1500, 720)
estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

# P1 near right edge of plat_a:
p1 = crear_personaje(plat_a.right - 50, plat_a.top - ALTO_HITBOX, "Celeste")
p2 = crear_personaje(plat_a.right - 100, plat_a.top - ALTO_HITBOX, "Violeta")

resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas)
resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas)

print(f"Init: p1 bottom={p1['hitbox'].bottom}, p1 x={p1['hitbox'].x}, en_suelo={p1['en_suelo']}")
print(f"Init: p2 bottom={p2['hitbox'].bottom}, p2 x={p2['hitbox'].x}, en_suelo={p2['en_suelo']}")
print(f"plat_b top={plat_b.top}, left={plat_b.left}, right={plat_b.right}")

for f in range(30):
    if f == 0:
        p1["vel_y"] = p1["fuerza_salto"]
        p1["en_suelo"] = False
    p1["vel_x"] = 6
    p2["vel_x"] = 0

    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, todas, suelo, estado_soga)
    resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas)
    resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas)

    d_soga = estado_soga["distancia"]
    print(f"Frame {f:02d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, bottom={p1['hitbox'].bottom}, vel_y={p1['vel_y']:.1f}, en_suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x} | d_soga={d_soga:.1f}, tirante={estado_soga['tirante']}")
    if p1["en_suelo"] and plat_b.collidepoint(p1["hitbox"].centerx, p1["hitbox"].bottom):
        print(f"--> P1 LLEGÓ A PLAT_B en frame {f}!")
        break

print("\n--- Fase 2: P2 salta a plat_b ---")
p1["vel_x"] = 0
for f in range(35):
    if f == 0:
        p2["vel_y"] = p2["fuerza_salto"]
        p2["en_suelo"] = False
    p2["vel_x"] = 6
    p1["vel_x"] = 0

    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, todas, suelo, estado_soga)
    resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas)
    resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas)

    d_soga = estado_soga["distancia"]
    print(f"Frame {f:02d}: P2 x={p2['hitbox'].x}, bottom={p2['hitbox'].bottom}, vel_y={p2['vel_y']:.1f}, en_suelo={p2['en_suelo']} | d_soga={d_soga:.1f}, tirante={estado_soga['tirante']}")
    if p2["en_suelo"] and plat_b.collidepoint(p2["hitbox"].centerx, p2["hitbox"].bottom):
        print(f"--> P2 LLEGÓ A PLAT_B en frame {f}!")
        break
