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

p1 = movimientos.crear_personaje(280, 480 - 85, "Celeste")
p1["en_suelo"] = True
# P2 cuelga 160px abajo
p2 = movimientos.crear_personaje(280, 480 - 85 + 160, "Violeta")
p2["en_suelo"] = False
estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

print("=== P1 INTENTA SALTAR CON P2 COLGANDO ===")
# P1 presiona salto
p1["vel_y"] = p1["fuerza_salto"] # -15.0
p1["en_suelo"] = False

for f in range(15):
    # En pantalla.py:
    # 1. Inputs: P1 vel_x = 0
    p1["vel_x"] = 0
    p2["vel_x"] = 0

    # 2. actualizar_fisica_soga
    movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
    vy_despues_soga = p1["vel_y"]

    # 3. resolver_colisiones
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    vy_despues_col = p1["vel_y"]

    # 4. aplicar_restriccion_soga
    movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
    vy_despues_restriccion = p1["vel_y"]

    print(f"Frame {f:2d}: P1 y={p1['hitbox'].y}, vy_soga={vy_despues_soga:.2f}, vy_col={vy_despues_col:.2f}, vy_final={vy_despues_restriccion:.2f}, en_suelo={p1['en_suelo']}")
