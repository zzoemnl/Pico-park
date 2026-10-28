import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos

plat = pygame.Rect(180, 480, 230, 24)
plataformas = [plat]
suelo = pygame.Rect(0, 640, 1400, 80)
mundo_rect = pygame.Rect(0, 0, 1400, 720)

print("=== IMPACTO DE P2 COLGANDO SOBRE P1 EN CADA FRAME ===")
print("\n=== SIMULACIÓN CONTINUA DE P2 COLGANDO (60 FRAMES) ===")
p1 = movimientos.crear_personaje(280, 480 - 85, "Celeste")
p1["en_suelo"] = True
p2 = movimientos.crear_personaje(360, 480 + 80, "Violeta")
p2["en_suelo"] = False
estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

for f in range(60):
    p1["vel_x"] = 0
    movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
    if f % 5 == 0:
        print(f"Frame {f:2d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, vx={p1['vel_x']:.2f}, vy={p1['vel_y']:.2f}, en_suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x}, y={p2['hitbox'].y}, vy={p2['vel_y']:.2f}")

print(f"\nPosición final P1: x={p1['hitbox'].x}, y={p1['hitbox'].y}")
