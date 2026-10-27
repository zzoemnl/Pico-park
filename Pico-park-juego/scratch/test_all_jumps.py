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

def probar_salto(plat_a, plat_b, dir_x, todas, nombre_transicion):
    suelo = pygame.Rect(0, 640, 1500, 80)
    mundo_rect = pygame.Rect(0, 0, 1500, 720)
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

    # Posicionar P1 en el área de salto de plat_a (lejos de chocar con la pared de plat_b)
    if dir_x > 0:
        # Salto a la derecha
        # P1 debe estar a la izquierda de plat_b.left para no chocar con la pared lateral de plat_b
        p1_x = min(plat_a.right - 50, plat_b.left - 45) if plat_b.left < plat_a.right else (plat_a.right - 50)
        p2_x = p1_x - 45
    else:
        # Salto a la izquierda
        # P1 debe estar a la derecha de plat_b.right para no chocar con la pared lateral de plat_b
        p1_x = max(plat_a.left + 10, plat_b.right + 5) if plat_b.right > plat_a.left else (plat_a.left + 10)
        p2_x = p1_x + 45

    p1 = crear_personaje(p1_x, plat_a.top - ALTO_HITBOX, "Celeste")
    p2 = crear_personaje(p2_x, plat_a.top - ALTO_HITBOX, "Violeta")

    resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas)
    resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas)

    # Fase 1: P1 salta a plat_b
    p1_llego = False
    for f in range(40):
        if f == 0:
            p1["vel_y"] = p1["fuerza_salto"]
            p1["en_suelo"] = False
        p1["vel_x"] = dir_x * 6
        p2["vel_x"] = 0

        actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, todas, suelo, estado_soga)
        resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas)
        resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas)

        if p1["en_suelo"] and plat_b.collidepoint(p1["hitbox"].centerx, p1["hitbox"].bottom):
            p1_llego = True
            break

    if not p1_llego:
        return False, f"P1 no llegó en {nombre_transicion} (x={p1['hitbox'].x}, y={p1['hitbox'].y})"

    # Fase 2: P2 salta a plat_b
    p2_llego = False
    for f in range(40):
        if f == 0:
            p2["vel_y"] = p2["fuerza_salto"]
            p2["en_suelo"] = False
        p2["vel_x"] = dir_x * 6
        p1["vel_x"] = 0

        actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, todas, suelo, estado_soga)
        resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas)
        resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas)

        if p2["en_suelo"] and plat_b.collidepoint(p2["hitbox"].centerx, p2["hitbox"].bottom):
            p2_llego = True
            break

    if not p2_llego:
        return False, f"P2 no llegó en {nombre_transicion} (x={p2['hitbox'].x}, y={p2['hitbox'].y})"

    return True, f"{nombre_transicion}: Ambos llegaron con éxito!"

# Definición de plataformas para probar
plat_inicio = pygame.Rect(0, 520, 180, 26)
p1 = pygame.Rect(130, 465, 200, 20)  # P1: Izquierda (centro 230)
p2 = pygame.Rect(280, 410, 200, 20)  # P2: Derecha   (centro 380)
p3 = pygame.Rect(130, 355, 200, 20)  # P3: Izquierda (centro 230)
p4 = pygame.Rect(280, 300, 200, 20)  # P4: Derecha   (centro 380)
plat_llegada = pygame.Rect(440, 250, 400, 26) # Salida (centro 640)

todas = [plat_inicio, p1, p2, p3, p4, plat_llegada]

for p_from, p_to, d_x, name in [
    (plat_inicio, p1, 1, "Inicio -> P1 (Izq)"),
    (p1, p2, 1, "P1 (Izq) -> P2 (Der)"),
    (p2, p3, -1, "P2 (Der) -> P3 (Izq)"),
    (p3, p4, 1, "P3 (Izq) -> P4 (Der)"),
    (p4, plat_llegada, 1, "P4 (Der) -> Salida"),
]:
    ok, msg = probar_salto(p_from, p_to, d_x, todas, name)
    print(f"{name}: {ok} | {msg}")
