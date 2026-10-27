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

plat_inicio = pygame.Rect(0, 520, 180, 26)

# Configuration to test:
# P1: Izquierda (x: 180..400, y: 470, center: 290)
# P2: Derecha   (x: 420..640, y: 410, center: 530)
# P3: Izquierda (x: 120..340, y: 350, center: 230)
# P4: Derecha   (x: 380..600, y: 290, center: 490)
# Salida:       (x: 630..1300, y: 230, center: 965)
p1 = pygame.Rect(180, 470, 220, 24)
p2 = pygame.Rect(420, 410, 220, 24)
p3 = pygame.Rect(120, 350, 220, 24)
p4 = pygame.Rect(380, 290, 220, 24)
salida = pygame.Rect(630, 230, 670, 26)

plataformas = [plat_inicio, p1, p2, p3, p4, salida]
suelo = pygame.Rect(0, 640, 1300, 80)
mundo_rect = pygame.Rect(0, 0, 1300, 720)

print("Checking clearances and staggering:")
print(f"P1 vs P3 center diff: {p1.centerx} vs {p3.centerx} = {abs(p1.centerx - p3.centerx)}px")
print(f"P2 vs P4 center diff: {p2.centerx} vs {p4.centerx} = {abs(p2.centerx - p4.centerx)}px")
print(f"P1 to P2 gap: {p2.left - p1.right}px")
print(f"P2 to P3 gap: {p2.left - p3.right}px")
print(f"P3 to P4 gap: {p4.left - p3.right}px")
print(f"P4 to Salida gap: {salida.left - p4.right}px")

transiciones = [
    (plat_inicio, p1, 1, "Inicio -> P1 (Izq)"),
    (p1, p2, 1, "P1 (Izq) -> P2 (Der)"),
    (p2, p3, -1, "P2 (Der) -> P3 (Izq)"),
    (p3, p4, 1, "P3 (Izq) -> P4 (Der)"),
    (p4, salida, 1, "P4 (Der) -> Salida"),
]

for pa, pb, dir_x, name in transiciones:
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}
    if dir_x > 0:
        j1_x = pa.right - ANCHO_HITBOX - 10
        j2_x = pa.right - ANCHO_HITBOX - 40
    else:
        j1_x = pa.left + 10
        j2_x = pa.left + 40

    j1 = crear_personaje(j1_x, pa.top - ALTO_HITBOX, "Celeste")
    j2 = crear_personaje(j2_x, pa.top - ALTO_HITBOX, "Violeta")

    resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
    resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)

    print(f"\n--- {name} ---")
    print(f"  Init: J1 bottom={j1['hitbox'].bottom} (target {pa.top}), ground={j1['en_suelo']}")
    print(f"  Init: J2 bottom={j2['hitbox'].bottom} (target {pa.top}), ground={j2['en_suelo']}")

    # Phase 1: J1 jumps
    j1_ok = False
    max_d1 = 0
    for f in range(45):
        if f == 0:
            j1["vel_y"] = j1["fuerza_salto"]
            j1["en_suelo"] = False
        j1["vel_x"] = dir_x * 6
        j2["vel_x"] = 0

        actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)

        max_d1 = max(max_d1, estado_soga["distancia"])
        if j1["en_suelo"] and pb.collidepoint(j1["hitbox"].centerx, j1["hitbox"].bottom):
            j1_ok = True
            print(f"  J1 landed at frame {f}, soga={estado_soga['distancia']:.1f}")
            break

    if not j1_ok:
        print(f"  FAILED: J1 did not land on {pb}! Final: pos=({j1['hitbox'].x}, {j1['hitbox'].y}), vel_y={j1['vel_y']}")
        continue

    # Phase 2: J2 jumps
    j2_ok = False
    max_d2 = 0
    for f in range(45):
        if f == 0:
            j2["vel_y"] = j2["fuerza_salto"]
            j2["en_suelo"] = False
        j2["vel_x"] = dir_x * 6
        j1["vel_x"] = 0

        actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)

        max_d2 = max(max_d2, estado_soga["distancia"])
        if j2["en_suelo"] and pb.collidepoint(j2["hitbox"].centerx, j2["hitbox"].bottom):
            j2_ok = True
            print(f"  J2 landed at frame {f}, soga={estado_soga['distancia']:.1f}")
            break

    if not j2_ok:
        print(f"  FAILED: J2 did not land on {pb}! Final: pos=({j2['hitbox'].x}, {j2['hitbox'].y}), vel_y={j2['vel_y']}")
        continue

    print(f"  SUCCESS! Max soga tension distance = {max(max_d1, max_d2):.1f}px")
