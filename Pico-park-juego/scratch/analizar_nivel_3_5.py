import sys
import os
import pygame
from collections import deque

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos

def test_map(shorten_rock4=False, remove_alga=False, fix_camara4_exit=False, adjust_door=False):
    ancho_mundo_nivel = 2600
    ALTO = 720
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 25)

    w_rock4 = 240 if shorten_rock4 else 340 # 1640 + 240 = 1880, leaving 100px opening before 1980

    # Formaciones rocosas
    rocas_submarinas = [
        # Sector 1
        pygame.Rect(260, techo_agua.bottom, 90, 260),
        pygame.Rect(260, 560, 90, suelo.top - 560),

        # Sector 2
        pygame.Rect(460, techo_agua.bottom, 180, 180),
        pygame.Rect(480, 560, 220, suelo.top - 560),

        # Sector 2/3
        pygame.Rect(720, 280, 70, suelo.top - 280),
        pygame.Rect(890, 250, 150, 260),

        # Sector 3
        pygame.Rect(1040, techo_agua.bottom, 120, 280),
        pygame.Rect(1180, 520, 220, suelo.top - 520),

        # Sector 4: Techo de la Fosa de la Llave
        pygame.Rect(1400, techo_agua.bottom, 220, 260),
        pygame.Rect(1640, techo_agua.bottom, w_rock4, 230),
        pygame.Rect(1640, 480, 140, suelo.top - 480),

        # Repisa abisal donde reposa la llave dorada
        pygame.Rect(1780, 590, 110, suelo.top - 590),

        # Sector 5: Pared antes del refugio y terraza
        pygame.Rect(1980, 270, 110, suelo.top - 270),
        # Techo en sector 5: si se ajusta para que la salida de camara 4 no choque
        pygame.Rect(2210, techo_agua.bottom, 180, 160 if fix_camara4_exit else 200),
        pygame.Rect(2210, 540, 180, suelo.top - 540),

        # Terraza final de llegada con la puerta
        pygame.Rect(2390, 440, 210, suelo.top - 440),
    ]

    barreras_algas = [] if remove_alga else [
        pygame.Rect(1380, 380, 30, suelo.top - 380),
    ]

    pinchos = [
        movimientos.crear_pincho(350, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(780, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(950, suelo.top - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(1200, 520 - 24, 140, 24, direccion="arriba"),
        movimientos.crear_pincho(1640, 480 - 24, 100, 24, direccion="arriba"),
        movimientos.crear_pincho(1890, suelo.top - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(2180, 540 - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(2210, techo_agua.bottom + (160 if fix_camara4_exit else 200), 100, 24, direccion="abajo"),
    ]

    obstaculos = [techo_agua, suelo] + rocas_submarinas + barreras_algas

    llave = pygame.Rect(1820, 590 - 46, 30, 46)
    puerta = pygame.Rect(2460, 440 - 90, 60, 90)

    grid_w, grid_h = 2600 // 10, 720 // 10
    grid = [[True for _ in range(grid_h)] for _ in range(grid_w)]

    pj_w, pj_h = 50, 85

    for gx in range(grid_w):
        for gy in range(grid_h):
            r = pygame.Rect(gx * 10, gy * 10, pj_w, pj_h)
            if any(r.colliderect(obs) for obs in obstaculos) or any(r.colliderect(p) for p in pinchos):
                grid[gx][gy] = False

    # BFS desde inicio (80, 280)
    start_gx = 80 // 10
    start_gy = 280 // 10
    q = deque([(start_gx, start_gy)])
    visitados = set([(start_gx, start_gy)])

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < grid_w and 0 <= ny < grid_h:
                if (nx, ny) not in visitados and grid[nx][ny]:
                    visitados.add((nx, ny))
                    q.append((nx, ny))

    # Verificar si el personaje puede tocar la llave
    puede_llave = any(
        pygame.Rect(gx * 10, gy * 10, pj_w, pj_h).colliderect(llave)
        for (gx, gy) in visitados
    )

    # Si puede tocar la llave, BFS desde la llave hasta la puerta
    # (o verificar si la puerta ya está en visitados)
    puede_puerta = any(
        pygame.Rect(gx * 10, gy * 10, pj_w, pj_h).colliderect(puerta)
        for (gx, gy) in visitados
    )

    max_x = max(gx * 10 for (gx, gy) in visitados) if visitados else 0
    print(f"Config(shorten_rock4={shorten_rock4}, remove_alga={remove_alga}, fix_camara4_exit={fix_camara4_exit}):")
    print(f"  Max X: {max_x} | Puede llave: {puede_llave} | Puede puerta: {puede_puerta}")
    return puede_llave and puede_puerta

print("--- Test 1: Original ---")
test_map(shorten_rock4=False, remove_alga=False, fix_camara4_exit=False)

print("\n--- Test 2: Solo remover alga en 1380 ---")
test_map(shorten_rock4=False, remove_alga=True, fix_camara4_exit=False)

print("\n--- Test 3: Remover alga + acortar roca 4 para abrir chimenea a Camara 4 ---")
test_map(shorten_rock4=True, remove_alga=True, fix_camara4_exit=False)

print("\n--- Test 4: Remover alga + acortar roca 4 + ajustar salida Camara 4 ---")
test_map(shorten_rock4=True, remove_alga=True, fix_camara4_exit=True)
