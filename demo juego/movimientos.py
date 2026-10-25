import pygame
from sprites import (
    ANCHO_HITBOX,
    ALTO_HITBOX,
    GRAVEDAD,
    cargar_sprites
)

# ============================================================
# CONSTRUCCIÓN DE ENTIDADES
# ============================================================

def crear_personaje(x, y, color_carpeta):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "hitbox": pygame.Rect(x, y, ANCHO_HITBOX, ALTO_HITBOX),
        "vel_x": 0,
        "vel_y": 0,
        "velocidad_mov": 5,
        "fuerza_salto": -15,
        "en_suelo": False,
        "sprites": cargar_sprites(color_carpeta),
        "mirando_derecha": True,
        "frame_animacion": 1,
        "contador_anim": 0,
        "empujando": False,
        "direccion_empuje": 0,
        "tiempo_quieto": 0,
        "mostrando_pestañeo": False,
    }


def reiniciar_juego(p1, p2):
    for p in (p1, p2):
        p["hitbox"].x = p["x_inicial"]
        p["hitbox"].y = p["y_inicial"]
        p["vel_x"] = 0
        p["vel_y"] = 0
        p["en_suelo"] = False
        p["empujando"] = False
        p["direccion_empuje"] = 0
        p["tiempo_quieto"] = 0
        p["mostrando_pestañeo"] = False


# ============================================================
# FÍSICA Y COLISIONES
# ============================================================

def resolver_colisiones(p1, p2, suelo, pantalla_rect):
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]

    p2_encima = (
        abs(hb2.bottom - hb1.top) <= 4
        and hb2.right > hb1.left + 10
        and hb2.left < hb1.right - 10
    )

    x_anterior = hb1.x
    y_anterior = hb1.y

    # Movimiento Horizontal
    hb1.x += p1["vel_x"]

    if p2_encima:
        hb2.x += (hb1.x - x_anterior)

    # Reiniciar estado de empuje por defecto
    p1["empujando"] = False
    p1["direccion_empuje"] = 0

    # Colisión Horizontal entre Jugadores
    if not p2_encima and hb1.colliderect(hb2):
        margen_cabeza = 12
        if hb1.bottom <= hb2.top + margen_cabeza:
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        else:
            if p1["vel_x"] > 0:
                hb1.right = hb2.left
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
            elif p1["vel_x"] < 0:
                hb1.left = hb2.right
                p1["empujando"] = True
                p1["direccion_empuje"] = -1

    # Movimiento Vertical
    p1["vel_y"] += GRAVEDAD
    hb1.y += int(p1["vel_y"])

    if p2_encima:
        hb2.y += (hb1.y - y_anterior)

    # Colisión Vertical entre Personajes
    if not p2_encima and hb1.colliderect(hb2):
        superposicion = (
            hb1.right > hb2.left + 10
            and hb1.left < hb2.right - 10
        )

        if p1["vel_y"] >= 0 and hb1.top < hb2.top and superposicion:
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        elif p1["vel_y"] < 0 and hb1.bottom > hb2.bottom:
            hb1.top = hb2.bottom
            p1["vel_y"] = 0

    # Colisión Suelo
    if hb1.colliderect(suelo):
        if p1["vel_y"] >= 0:
            hb1.bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True