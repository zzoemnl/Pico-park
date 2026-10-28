import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def simular_p1_arriba_p2_colgando():
    plat = pygame.Rect(180, 480, 230, 24)
    plataformas = [plat]
    suelo = pygame.Rect(0, 720 - 80, 1400, 80)
    mundo_rect = pygame.Rect(0, 0, 1400, 720)

    p1 = movimientos.crear_personaje(280, 480 - 85, "Celeste")
    p1["en_suelo"] = True

    # P2 cuelga por debajo de P1 a la derecha
    p2 = movimientos.crear_personaje(330, 580, "Violeta")
    p2["en_suelo"] = False

    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

    print("--- Estado Inicial ---")
    print(f"P1: pos=({p1['hitbox'].x}, {p1['hitbox'].y}), vel=({p1['vel_x']}, {p1['vel_y']}), en_suelo={p1['en_suelo']}")
    print(f"P2: pos=({p2['hitbox'].x}, {p2['hitbox'].y}), vel=({p2['vel_x']}, {p2['vel_y']}), en_suelo={p2['en_suelo']}")

    # Test 1: P2 oscila como péndulo
    print("\n==============================================")
    print("TEST 1: P2 oscila como péndulo colgado de P1")
    print("==============================================")
    p1 = movimientos.crear_personaje(280, 480 - 85, "Celeste")
    p1["en_suelo"] = True
    p2 = movimientos.crear_personaje(380, 520, "Violeta")
    p2["vel_x"] = 3.0
    p2["vel_y"] = 0.0
    p2["en_suelo"] = False
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

    for frame in range(120):
        # P1 no toca controles
        p1["vel_x"] = 0
        movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if frame % 15 == 0:
            print(f"Frame {frame:3d}: P1 x={p1['hitbox'].x:6.1f}, y={p1['hitbox'].y:6.1f}, vx={p1['vel_x']:6.2f}, vy={p1['vel_y']:6.2f}, en_suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x:6.1f}, y={p2['hitbox'].y:6.1f}, vx={p2['vel_x']:6.2f}, vy={p2['vel_y']:6.2f}")

    print(f"P1 posición final tras oscilación: x={p1['hitbox'].x}, y={p1['hitbox'].y}")

    # Test 2: P1 intenta caminar hacia la izquierda (alejándose de P2 o acercándose al centro)
    print("\n==============================================")
    print("TEST 2: P1 intenta caminar hacia la izquierda")
    print("==============================================")
    for frame in range(40):
        # P1 presiona izquierda
        p1["vel_x"] = -p1["velocidad_mov"]
        p1["moviendo"] = True
        movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if frame % 10 == 0:
            print(f"Frame {frame:2d}: P1 x={p1['hitbox'].x:6.1f}, y={p1['hitbox'].y:6.1f}, vx={p1['vel_x']:6.2f}, vy={p1['vel_y']:6.2f}, en_suelo={p1['en_suelo']}")

    # Test 3: P1 intenta saltar
    print("\n==============================================")
    print("TEST 3: P1 intenta saltar estando en el suelo")
    print("==============================================")
    p1["vel_y"] = p1["fuerza_salto"]
    p1["en_suelo"] = False
    for frame in range(30):
        p1["vel_x"] = 0
        movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if frame % 5 == 0:
            print(f"Frame {frame:2d}: P1 x={p1['hitbox'].x:6.1f}, y={p1['hitbox'].y:6.1f}, vx={p1['vel_x']:6.2f}, vy={p1['vel_y']:6.2f}, en_suelo={p1['en_suelo']}")

if __name__ == "__main__":
    simular_p1_arriba_p2_colgando()
