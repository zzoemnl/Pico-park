import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def simular_casos_jugador_arriba():
    # Setup de plataformas exactamente como Nivel 2-5
    # P1: (180, 480, 230, 24)
    # P2: (430, 390, 230, 24)
    # P3: (130, 300, 230, 24)
    # P4: (480, 210, 230, 24)
    p_inicio = pygame.Rect(0, 560, 160, 26)
    p_inicio_b = pygame.Rect(0, 586, 160, 640 - 586 + 80)
    p_llegada = pygame.Rect(730, 130, 670, 26)
    p_llegada_b = pygame.Rect(730, 156, 670, 640 - 156 + 80)
    plataformas_base = [p_inicio, p_inicio_b, p_llegada, p_llegada_b]
    plataformas_alternadas = [
        pygame.Rect(180, 480, 230, 24),
        pygame.Rect(430, 390, 230, 24),
        pygame.Rect(130, 300, 230, 24),
        pygame.Rect(480, 210, 230, 24),
    ]
    plataformas = plataformas_base + plataformas_alternadas
    suelo = pygame.Rect(0, 640, 1400, 80)
    mundo_rect = pygame.Rect(0, 0, 1400, 720)

    print("======================================================================")
    print("CASO 1: P1 está sobre P2 (x=500, y=390), P2 cae por el borde derecho")
    print("======================================================================")
    p1 = movimientos.crear_personaje(500, 390 - 85, "Celeste")
    p1["en_suelo"] = True
    p2 = movimientos.crear_personaje(670, 420, "Violeta")
    p2["en_suelo"] = False
    p2["vel_y"] = 6.0
    p2["vel_x"] = 2.0
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

    for f in range(60):
        # P1 está quieto (no presiona teclas)
        p1["vel_x"] = 0
        movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

        c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
        c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
        dist = (c2 - c1).length()
        if f % 5 == 0:
            print(f"F{f:2d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, vx={p1['vel_x']:.2f}, vy={p1['vel_y']:.2f}, suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x}, y={p2['hitbox'].y}, vy={p2['vel_y']:.2f} | dist={dist:.1f}, tens={estado_soga['tension']:.2f}")

    print("\n======================================================================")
    print("CASO 2: P1 intenta caminar (hacia izquierda) mientras P2 cuelga")
    print("======================================================================")
    p1_x_inicial = p1["hitbox"].x
    for f in range(30):
        # P1 presiona izquierda
        p1["vel_x"] = -p1["velocidad_mov"]
        p1["moviendo"] = True
        movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if f % 5 == 0:
            print(f"F{f:2d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, vx={p1['vel_x']:.2f}, vy={p1['vel_y']:.2f}, suelo={p1['en_suelo']}")
    print(f"Avance de P1 en 30 frames: {p1_x_inicial - p1['hitbox'].x} px (esperado ~180px a 6px/f)")

    print("\n======================================================================")
    print("CASO 3: P1 intenta saltar mientras P2 cuelga")
    print("======================================================================")
    p1["vel_y"] = p1["fuerza_salto"]
    p1["en_suelo"] = False
    p1_y_inicio_salto = p1["hitbox"].y
    alturas = []
    for f in range(30):
        p1["vel_x"] = 0
        movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        alturas.append(p1["hitbox"].y)
        if f % 5 == 0:
            print(f"F{f:2d}: P1 y={p1['hitbox'].y}, vy={p1['vel_y']:.2f}, suelo={p1['en_suelo']}")
    max_salto = p1_y_inicio_salto - min(alturas)
    print(f"Altura alcanzada por P1: {max_salto} px (esperado normal ~130px)")

if __name__ == "__main__":
    simular_casos_jugador_arriba()
