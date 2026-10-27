import os
import sys
import math
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
    GRAVEDAD,
)

def simular_salto_dos_jugadores(plat_a, plat_b, todas_plataformas, dir_x):
    """
    Simula que dos jugadores unidos por la soga viajan de plat_a a plat_b.
    Retorna True si ambos logran llegar y quedar en suelo firme sobre plat_b sin morir ni caer.
    """
    suelo = pygame.Rect(0, 640, 1500, 80)
    mundo_rect = pygame.Rect(0, 0, 1500, 720)
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

    # Ambos jugadores inician sobre plat_a
    # P1 cerca del borde en dirección del salto, P2 detrás a distancia segura
    if dir_x > 0:
        p1_x = plat_a.right - ANCHO_HITBOX - 10
        p2_x = p1_x - 50
    else:
        p1_x = plat_a.left + 10
        p2_x = p1_x + 50

    p1 = crear_personaje(p1_x, plat_a.top - ALTO_HITBOX, "Celeste")
    p2 = crear_personaje(p2_x, plat_a.top - ALTO_HITBOX, "Violeta")

    # Asegurar que inician en el suelo
    resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas_plataformas)
    resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas_plataformas)

    if not p1["en_suelo"] or not p2["en_suelo"]:
        return False, "No inician en suelo sobre plat_a"

    # Fase 1: P1 salta hacia plat_b mientras P2 espera en el borde de plat_a
    p1_llego = False
    for frame in range(60):
        # Input P1
        saltar = (frame == 0)
        if saltar and p1["en_suelo"]:
            p1["vel_y"] = p1["fuerza_salto"]
            p1["en_suelo"] = False
        p1["vel_x"] = dir_x * p1["velocidad_mov"]

        # P2 se queda quieto en plat_a pero puede dar pequeños pasos de soporte
        p2["vel_x"] = 0

        # Física de soga
        actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, todas_plataformas, suelo, estado_soga)

        # Colisiones
        resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas_plataformas)
        resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas_plataformas)

        # Verificar si P1 aterrizó en plat_b
        if p1["en_suelo"] and plat_b.collidepoint(p1["hitbox"].centerx, p1["hitbox"].bottom):
            p1_llego = True
            break

        # Si alguien cae por debajo de plat_a + 100, fallo
        if p1["hitbox"].top > max(plat_a.bottom, plat_b.bottom) + 120 or p2["hitbox"].top > plat_a.bottom + 50:
            return False, f"P1 o P2 cayeron durante el salto de P1 en frame {frame}"

    if not p1_llego:
        return False, "P1 no alcanzó plat_b en 60 frames"

    # Fase 2: P1 espera en plat_b y P2 salta hacia plat_b para reunirse
    p2_llego = False
    for frame in range(60):
        saltar = (frame == 0)
        if saltar and p2["en_suelo"]:
            p2["vel_y"] = p2["fuerza_salto"]
            p2["en_suelo"] = False
        p2["vel_x"] = dir_x * p2["velocidad_mov"]

        # P1 espera en plat_b
        p1["vel_x"] = 0

        actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, todas_plataformas, suelo, estado_soga)

        resolver_colisiones(p1, None, suelo, mundo_rect, plataformas=todas_plataformas)
        resolver_colisiones(p2, None, suelo, mundo_rect, plataformas=todas_plataformas)

        if p2["en_suelo"] and plat_b.collidepoint(p2["hitbox"].centerx, p2["hitbox"].bottom):
            p2_llego = True
            break

        if p2["hitbox"].top > max(plat_a.bottom, plat_b.bottom) + 120 or p1["hitbox"].top > plat_b.bottom + 50:
            return False, f"P2 cayó durante el salto en frame {frame}"

    if not p2_llego:
        return False, "P2 no alcanzó plat_b en 60 frames"

    return True, "Ambos llegaron exitosamente a plat_b!"

# Probar las posiciones anteriores (antiguas)
plat_inicio_old = pygame.Rect(0, 520, 200, 26)
p1_old = pygame.Rect(240, 440, 220, 24)
p2_old = pygame.Rect(500, 365, 220, 24)
p3_old = pygame.Rect(180, 290, 230, 24)
p4_old = pygame.Rect(540, 215, 220, 24)
plat_llegada_old = pygame.Rect(840, 480, 460, 26)

todas_old = [plat_inicio_old, p1_old, p2_old, p3_old, p4_old, plat_llegada_old]

print("--- Probando posiciones antiguas ---")
res, msg = simular_salto_dos_jugadores(plat_inicio_old, p1_old, todas_old, dir_x=1)
print(f"Inicio -> P1: {res} ({msg})")

res, msg = simular_salto_dos_jugadores(p1_old, p2_old, todas_old, dir_x=1)
print(f"P1 -> P2: {res} ({msg})")

res, msg = simular_salto_dos_jugadores(p2_old, p3_old, todas_old, dir_x=-1)
print(f"P2 -> P3: {res} ({msg})")

res, msg = simular_salto_dos_jugadores(p3_old, p4_old, todas_old, dir_x=1)
print(f"P3 -> P4: {res} ({msg})")

res, msg = simular_salto_dos_jugadores(p4_old, plat_llegada_old, todas_old, dir_x=1)
print(f"P4 -> Salida: {res} ({msg})")

print("\n--- Probando ZIGZAG DINÁMICO ESCALONADO ---")
plat_inicio_cand = pygame.Rect(0, 520, 180, 26)
p1_cand = pygame.Rect(130, 465, 200, 20)  # P1: Izquierda (centro 230, y=465)
p2_cand = pygame.Rect(280, 410, 200, 20)  # P2: Derecha   (centro 380, y=410)
p3_cand = pygame.Rect(200, 355, 200, 20)  # P3: Izquierda (centro 300, y=355)
p4_cand = pygame.Rect(350, 300, 200, 20)  # P4: Derecha   (centro 450, y=300)
plat_llegada_cand = pygame.Rect(490, 250, 600, 26) # Salida (centro 790, y=250)

todas_cand = [plat_inicio_cand, p1_cand, p2_cand, p3_cand, p4_cand, plat_llegada_cand]

res1, msg1 = simular_salto_dos_jugadores(plat_inicio_cand, p1_cand, todas_cand, dir_x=1)
print(f"Inicio -> P1 (Izq): {res1} ({msg1})")

res2, msg2 = simular_salto_dos_jugadores(p1_cand, p2_cand, todas_cand, dir_x=1)
print(f"P1 (Izq) -> P2 (Der): {res2} ({msg2})")

res3, msg3 = simular_salto_dos_jugadores(p2_cand, p3_cand, todas_cand, dir_x=-1)
print(f"P2 (Der) -> P3 (Izq): {res3} ({msg3})")

res4, msg4 = simular_salto_dos_jugadores(p3_cand, p4_cand, todas_cand, dir_x=1)
print(f"P3 (Izq) -> P4 (Der): {res4} ({msg4})")

res5, msg5 = simular_salto_dos_jugadores(p4_cand, plat_llegada_cand, todas_cand, dir_x=1)
print(f"P4 (Der) -> Salida: {res5} ({msg5})")
