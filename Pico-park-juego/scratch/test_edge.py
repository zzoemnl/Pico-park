import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos

plat = pygame.Rect(180, 480, 230, 24) # x de 180 a 410
plataformas = [plat]
suelo = pygame.Rect(0, 640, 1400, 80)
mundo_rect = pygame.Rect(0, 0, 1400, 720)

p1 = movimientos.crear_personaje(370, 480 - 85, "Celeste")
p1["en_suelo"] = True
# P2 cuelga fuera de la plataforma
p2 = movimientos.crear_personaje(430, 480 + 70, "Violeta")
p2["en_suelo"] = False
estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

print("P1 inicia en x=370 (borde derecho en 410, ancho=40)")
for f in range(30):
    p1["vel_x"] = 0
    movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
    print(f"Frame {f:2d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, en_suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x}, y={p2['hitbox'].y}")
