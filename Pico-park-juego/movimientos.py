import os
import sys
import math
import random
import pygame

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from sprites import (
    ANCHO,
    ALTO,
    cargar_sprites,
    cargar_sprite_caja,
    cargar_sprite_llave,
    cargar_sprites_puerta,
)

GRAVEDAD = 0.85
ANCHO_HITBOX = 50
ALTO_HITBOX = 85
TAMANO_CAJA = 60
DISTANCIA_SOGA_REPOSO = 140
DISTANCIA_SOGA_MAXIMA = 160
DISTANCIA_SOGA = DISTANCIA_SOGA_MAXIMA
VELOCIDAD_MUERTE = -17


def crear_personaje(x, y, color_carpeta="Blanco", accesorio="Ninguno"):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "hitbox": pygame.Rect(x, y, ANCHO_HITBOX, ALTO_HITBOX),
        "vel_x": 0,
        "vel_y": 0,
        "velocidad_mov": 6,
        "fuerza_salto": -15.5,
        "en_suelo": False,
        "en_agua": False,
        "sprites": cargar_sprites(color_carpeta),
        "color": (255, 255, 255),
        "accesorio": accesorio or "Ninguno",
        "mirando_derecha": True,
        "frame_animacion": 1,
        "contador_anim": 0,
        "empujando": False,
        "direccion_empuje": 0,
        "tiempo_quieto": 0,
        "mostrando_pestañeo": False,
        "moviendo": False,
        "muerto": False,
        "muerte_terminada": False,
        "tiempo_muerte": 0,
    }


def reiniciar_juego(p1, p2, caja=None, llave=None, puerta=None, estado_soga=None):
    if estado_soga is not None:
        estado_soga["tension"] = 0.0
        estado_soga["dano_acumulado"] = 0.0
        estado_soga["nivel_estres"] = 0.0
        estado_soga["rota"] = False
        estado_soga["en_muerte"] = False
        estado_soga["particulas_rotura"] = []
        estado_soga["tiempo_rotura"] = 0

    for p in (p1, p2):
        p["hitbox"].x = p["x_inicial"]
        p["hitbox"].y = p["y_inicial"]
        p["vel_x"] = 0
        p["vel_y"] = 0
        p["en_suelo"] = False
        p["en_agua"] = False
        p["empujando"] = False
        p["direccion_empuje"] = 0
        p["tiempo_quieto"] = 0
        p["mostrando_pestañeo"] = False
        p["moviendo"] = False
        p["muerto"] = False
        p["muerte_terminada"] = False
        p["tiempo_muerte"] = 0

    if caja is not None:
        caja["rect"].x = caja["x_inicial"]
        caja["rect"].y = caja["y_inicial"]
        caja["vel_y"] = 0
        caja["en_suelo"] = False

    if llave is not None:
        llave["x_float"] = float(llave["x_inicial"])
        llave["y_float"] = float(llave["y_inicial"])
        llave["rect"].x = llave["x_inicial"]
        llave["rect"].y = llave["y_inicial"]
        llave["recolectada"] = False
        llave["portador"] = None

    if puerta is not None:
        puerta["abierta"] = False
        puerta["fase_candado"] = 0
        puerta["tick_candado"] = 0
        puerta["desbloqueando"] = False


def coordinar_movimiento_soga(p1, p2, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Coordinación y recorte pre-desplazamiento para garantizar que la soga NUNCA
    supere su longitud máxima (distancia <= d_max) en ninguna actualización física.
    - Recorta únicamente la componente del desplazamiento que provocaría exceso.
    - Si un personaje camina y el otro está quieto, el que camina se detiene firmemente al llegar a d_max.
    - Si ambos caminan en direcciones opuestas, ambos se detienen al llegar al límite.
    - El movimiento de acercamiento o perpendicular es 100% libre sin ninguna resistencia.
    - Si uno cuelga en el aire y el otro camina en una plataforma, el del suelo arrastra al suspendido suavemente.
    - No aplica teletransportes ni retrocesos bruscos.
    """
    if p1 is None or p2 is None or p1.get("muerto", False) or p2.get("muerto", False):
        return

    c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
    c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
    v = c2 - c1
    d = v.length()


    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)
    dy = c2.y - c1.y
    if abs(dy) >= d_max:
        x_max = 0.0
    else:
        x_max = math.sqrt(max(0.0, d_max * d_max - dy * dy))

    v1_x = p1.get("vel_x", 0.0)
    v2_x = p2.get("vel_x", 0.0)
    dx1 = int(round(v1_x))
    dx2 = int(round(v2_x))

    # Arrastre horizontal cuando uno cuelga en el aire y el otro camina en plataforma
    if p1_suelo and not p2_suelo and dy > 15:
        if dx1 != 0 and abs(dx2) <= 1:
            dx2 = dx1
            p2["vel_x"] = float(dx2)
    elif p2_suelo and not p1_suelo and -dy > 15:
        if dx2 != 0 and abs(dx1) <= 1:
            dx1 = dx2
            p1["vel_x"] = float(dx1)

    new_rel_x = (c2.x + dx2) - (c1.x + dx1)
    if new_rel_x > x_max:
        excess = new_rel_x - x_max
        if dx1 > 0 and dx2 > 0:
            dx2 = max(0, dx1)
            p2["vel_x"] = float(dx2)
        elif dx1 < 0 and dx2 < 0:
            dx1 = min(0, dx2)
            p1["vel_x"] = float(dx1)
        else:
            s1 = max(0, -dx1)
            s2 = max(0, dx2)
            s_tot = s1 + s2
            reduce = int(math.ceil(excess))
            if s1 > 0 and s2 == 0:
                dx1 += reduce
                p1["vel_x"] = float(dx1)
            elif s2 > 0 and s1 == 0:
                dx2 -= reduce
                p2["vel_x"] = float(dx2)
            elif s_tot > 0:
                r1 = int(round(reduce * (s1 / s_tot)))
                r2 = reduce - r1
                dx1 += r1
                dx2 -= r2
                p1["vel_x"] = float(dx1)
                p2["vel_x"] = float(dx2)

    elif new_rel_x < -x_max:
        excess = -x_max - new_rel_x
        if dx1 > 0 and dx2 > 0:
            dx1 = max(0, dx2)
            p1["vel_x"] = float(dx1)
        elif dx1 < 0 and dx2 < 0:
            dx2 = min(0, dx1)
            p2["vel_x"] = float(dx2)
        else:
            s1 = max(0, dx1)
            s2 = max(0, -dx2)
            s_tot = s1 + s2
            reduce = int(math.ceil(excess))
            if s1 > 0 and s2 == 0:
                dx1 -= reduce
                p1["vel_x"] = float(dx1)
            elif s2 > 0 and s1 == 0:
                dx2 += reduce
                p2["vel_x"] = float(dx2)
            elif s_tot > 0:
                r1 = int(round(reduce * (s1 / s_tot)))
                r2 = reduce - r1
                dx1 -= r1
                dx2 -= r2
                p1["vel_x"] = float(dx1)
                p2["vel_x"] = float(dx2)


def resolver_colisiones(p1, p2, suelo, pantalla_rect, caja=None, en_agua=False, plataformas=None, usar_soga=False, d_max=DISTANCIA_SOGA_MAXIMA):
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"] if p2 is not None else None

    # Detectar si p2 está parado encima de p1
    p2_encima = (
        hb2 is not None
        and abs(hb2.bottom - hb1.top) <= 6
        and hb2.right > hb1.left + 2
        and hb2.left < hb1.right - 2
    )

    x_inicio = hb1.x
    y_inicio = hb1.y

    # Movimiento horizontal de p1 con límite físico estricto de soga
    dx = int(round(p1["vel_x"]))
    if usar_soga and hb2 is not None and not p1.get("muerto", False) and not p2.get("muerto", False):
        c1_y = hb1.centery + 4
        c2_y = hb2.centery + 4
        dy = c2_y - c1_y
        if abs(dy) >= d_max:
            x_max = 0.0
        else:
            x_max = math.sqrt(max(0.0, d_max * d_max - dy * dy))

        c1_x = hb1.centerx
        c2_x = hb2.centerx
        c1_x_prop = c1_x + dx

        rel_x = c2_x - c1_x_prop
        if rel_x > x_max:
            max_c1_x = c2_x - x_max
            dx = int(math.ceil(max_c1_x - c1_x))
            p1["vel_x"] = float(dx)
        elif rel_x < -x_max:
            min_c1_x = c2_x + x_max
            dx = int(math.floor(min_c1_x - c1_x))
            p1["vel_x"] = float(dx)

    hb1.x += dx

    p1["empujando"] = False
    p1["direccion_empuje"] = 0

    if plataformas:
        for plat in plataformas:
            if hb1.colliderect(plat):
                # Colisión lateral sólida con la plataforma u obstáculo
                if hb1.bottom > plat.top + 2 and hb1.top < plat.bottom - 2:
                    if x_inicio + hb1.width <= plat.left + max(8, abs(int(p1["vel_x"])) + 2) or hb1.centerx < plat.centerx:
                        hb1.right = plat.left
                        if p1["vel_x"] > 0:
                            p1["vel_x"] = 0
                        p1["empujando"] = True
                        p1["direccion_empuje"] = 1
                    else:
                        hb1.left = plat.right
                        if p1["vel_x"] < 0:
                            p1["vel_x"] = 0
                        p1["empujando"] = True
                        p1["direccion_empuje"] = -1

    if pantalla_rect is not None:
        if hb1.left <= pantalla_rect.left:
            hb1.left = pantalla_rect.left
            if p1["vel_x"] < 0:
                p1["vel_x"] = 0
                p1["empujando"] = True
                p1["direccion_empuje"] = -1
        elif hb1.right >= pantalla_rect.right:
            hb1.right = pantalla_rect.right
            if p1["vel_x"] > 0:
                p1["vel_x"] = 0
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
        if hb1.top <= pantalla_rect.top:
            hb1.top = pantalla_rect.top
            if p1["vel_y"] < 0:
                p1["vel_y"] = 0

    if caja is not None:
        empujar_caja(p1, caja, p2, pantalla_rect, plataformas)
        # Si la caja actúa como obstáculo sólido y el personaje no la empuja, evitar penetración lateral
        caja_rect = caja["rect"]
        if hb1.colliderect(caja_rect) and hb1.bottom > caja_rect.top + 10 and hb1.top < caja_rect.bottom - 10:
            if x_inicio + hb1.width <= caja_rect.left + max(8, abs(int(p1["vel_x"])) + 2) or hb1.centerx < caja_rect.centerx:
                hb1.right = caja_rect.left
                if p1["vel_x"] > 0:
                    p1["vel_x"] = 0
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
            else:
                hb1.left = caja_rect.right
                if p1["vel_x"] < 0:
                    p1["vel_x"] = 0
                p1["empujando"] = True
                p1["direccion_empuje"] = -1

    # Empuje y colisión lateral entre personajes (solo si están al mismo nivel lateral, no si uno está encima del otro)
    if hb2 is not None and not p2_encima and hb1.colliderect(hb2):
        if hb1.bottom > hb2.top + 10 and hb1.top < hb2.bottom - 10:
            # Determinación direccional estricta para evitar intercambio anómalo de posiciones (teletransporte)
            p1_a_la_izq = (x_inicio + hb1.width <= hb2.left + max(8, abs(dx) + 2)) or (hb1.centerx < hb2.centerx)

            if p1_a_la_izq:
                # P1 está a la izquierda de P2
                if p1["vel_x"] > 0:
                    penetracion = hb1.right - hb2.left
                    p2_resiste = (p2.get("vel_x", 0) < 0 and p2.get("moviendo", False)) or (p2.get("empujando", False) and p2.get("direccion_empuje", 0) == -1)
                    if p2_resiste:
                        hb1.right = hb2.left
                        p1["vel_x"] = 0
                        p1["empujando"] = True
                        p1["direccion_empuje"] = 1
                    else:
                        max_desp = penetracion
                        if plataformas:
                            for plat in plataformas:
                                if hb2.bottom > plat.top + 2 and hb2.top < plat.bottom - 2 and plat.left >= hb2.left:
                                    max_desp = min(max_desp, max(0, plat.left - hb2.right))
                        if pantalla_rect:
                            max_desp = min(max_desp, max(0, pantalla_rect.right - hb2.right))
                        if caja is not None:
                            caja_rect = caja["rect"]
                            if hb2.bottom > caja_rect.top + 10 and hb2.top < caja_rect.bottom - 10 and caja_rect.left >= hb2.left:
                                max_desp = min(max_desp, max(0, caja_rect.left - hb2.right))

                        if max_desp > 0:
                            hb2.x += max_desp
                            hb1.right = hb2.left
                            p1["empujando"] = True
                            p1["direccion_empuje"] = 1
                            p2["moviendo"] = True
                            p2["mirando_derecha"] = True
                        else:
                            if caja is not None and hb2.bottom > caja_rect.top + 10 and hb2.top < caja_rect.bottom - 10 and caja_rect.left >= hb2.left:
                                hb2.right = min(hb2.right, caja_rect.left)
                            hb1.right = hb2.left
                            p1["vel_x"] = 0
                            p1["empujando"] = True
                            p1["direccion_empuje"] = 1
                else:
                    # P1 está a la izquierda pero no avanza sobre P2: mantener separación limpia
                    hb1.right = hb2.left
            else:
                # P1 está a la derecha de P2
                if p1["vel_x"] < 0:
                    penetracion = hb2.right - hb1.left
                    p2_resiste = (p2.get("vel_x", 0) > 0 and p2.get("moviendo", False)) or (p2.get("empujando", False) and p2.get("direccion_empuje", 0) == 1)
                    if p2_resiste:
                        hb1.left = hb2.right
                        p1["vel_x"] = 0
                        p1["empujando"] = True
                        p1["direccion_empuje"] = -1
                    else:
                        max_desp = penetracion
                        if plataformas:
                            for plat in plataformas:
                                if hb2.bottom > plat.top + 2 and hb2.top < plat.bottom - 2 and plat.right <= hb2.right:
                                    max_desp = min(max_desp, max(0, hb2.left - plat.right))
                        if pantalla_rect:
                            max_desp = min(max_desp, max(0, hb2.left - pantalla_rect.left))
                        if caja is not None:
                            caja_rect = caja["rect"]
                            if hb2.bottom > caja_rect.top + 10 and hb2.top < caja_rect.bottom - 10 and caja_rect.right <= hb2.right:
                                max_desp = min(max_desp, max(0, hb2.left - caja_rect.right))

                        if max_desp > 0:
                            hb2.x -= max_desp
                            hb1.left = hb2.right
                            p1["empujando"] = True
                            p1["direccion_empuje"] = -1
                            p2["moviendo"] = True
                            p2["mirando_derecha"] = False
                        else:
                            if caja is not None and hb2.bottom > caja_rect.top + 10 and hb2.top < caja_rect.bottom - 10 and caja_rect.right <= hb2.right:
                                hb2.left = max(hb2.left, caja_rect.right)
                            hb1.left = hb2.right
                            p1["vel_x"] = 0
                            p1["empujando"] = True
                            p1["direccion_empuje"] = -1
                else:
                    # P1 está a la derecha y se mueve alejándose (o quieto): mantener separación limpia
                    hb1.left = hb2.right

    # Si p2 estaba encima de p1, trasladar a p2 el desplazamiento horizontal real de p1
    if p2_encima and hb2 is not None:
        hb2.x += hb1.x - x_inicio

    # Movimiento vertical de p1
    if not en_agua:
        p1["vel_y"] += GRAVEDAD

    dy = int(p1["vel_y"])
    if usar_soga and hb2 is not None and not p1.get("muerto", False) and not p2.get("muerto", False):
        c1_x = hb1.centerx
        c2_x = hb2.centerx
        dx_cur = c2_x - c1_x
        if abs(dx_cur) >= d_max:
            y_max = 0.0
        else:
            y_max = math.sqrt(max(0.0, d_max * d_max - dx_cur * dx_cur))

        c1_y = hb1.centery + 4
        c2_y = hb2.centery + 4
        c1_y_prop = c1_y + dy
        rel_y = c2_y - c1_y_prop
        if rel_y > y_max:
            max_c1_y = c2_y - y_max
            dy = int(math.ceil(max_c1_y - c1_y))
            p1["vel_y"] = float(dy)
        elif rel_y < -y_max:
            min_c1_y = c2_y + y_max
            dy = int(math.floor(min_c1_y - c1_y))
            p1["vel_y"] = float(dy)

    hb1.y += dy

    toco_superficie = False
    if plataformas:
        for plat in plataformas:
            if hb1.right > plat.left + 2 and hb1.left < plat.right - 2:
                # 1. Aterrizaje sobre la cara superior de la plataforma
                if p1["vel_y"] >= 0 and hb1.bottom >= plat.top and y_inicio + hb1.height <= plat.top + max(14, int(p1["vel_y"]) + 10):
                    hb1.bottom = plat.top
                    p1["vel_y"] = 0
                    p1["en_suelo"] = True
                    toco_superficie = True
                # 2. Choque contra el techo / cara inferior de la plataforma
                elif hb1.top <= plat.bottom and y_inicio >= plat.bottom - max(12, abs(int(p1["vel_y"])) + 4):
                    hb1.top = plat.bottom
                    if p1["vel_y"] < 0:
                        p1["vel_y"] = 0

    if caja is not None:
        caja_rect = caja["rect"]
        if hb1.right > caja_rect.left and hb1.left < caja_rect.right:
            if p1["vel_y"] >= 0 and hb1.bottom >= caja_rect.top and y_inicio + hb1.height <= caja_rect.top + max(12, int(p1["vel_y"]) + 10):
                hb1.bottom = caja_rect.top
                p1["vel_y"] = 0
                p1["en_suelo"] = True
                toco_superficie = True
            elif p1["vel_y"] < 0 and hb1.top <= caja_rect.bottom and y_inicio >= caja_rect.bottom - 10:
                hb1.top = caja_rect.bottom
                p1["vel_y"] = 0

    # Colisión vertical cuando p1 aterriza sobre la cabeza de p2
    if hb2 is not None and not p2_encima and hb1.right > hb2.left + 2 and hb1.left < hb2.right - 2:
        if p1["vel_y"] >= 0 and hb1.bottom >= hb2.top and y_inicio + hb1.height <= hb2.top + max(12, int(p1["vel_y"]) + 10):
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
            toco_superficie = True
        elif p1["vel_y"] < 0 and hb1.top <= hb2.bottom and y_inicio >= hb2.bottom - 10:
            hb1.top = hb2.bottom
            p1["vel_y"] = 0

    if suelo is not None and hb1.right > suelo.left and hb1.left < suelo.right:
        if hb1.bottom >= suelo.top and p1["vel_y"] >= 0:
            hb1.bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
            toco_superficie = True

    if not toco_superficie and not p2_encima:
        p1["en_suelo"] = False

    # Si p2 estaba encima de p1, mantener a p2 firmemente sobre la cabeza de p1
    if p2_encima and hb2 is not None:
        if p2 is not None and p2["vel_y"] >= 0:
            hb2.bottom = hb1.top
            p2["vel_y"] = 0
            p2["en_suelo"] = True


def crear_caja(x, y):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "rect": pygame.Rect(x, y, TAMANO_CAJA, TAMANO_CAJA),
        "vel_y": 0,
        "en_suelo": False,
        "sprite": cargar_sprite_caja(TAMANO_CAJA),
    }


def actualizar_caja(caja, suelo, pantalla_rect, plataformas=None):
    caja["vel_y"] += GRAVEDAD
    caja["rect"].y += int(caja["vel_y"])

    if caja["rect"].colliderect(suelo) and caja["vel_y"] >= 0:
        caja["rect"].bottom = suelo.top
        caja["vel_y"] = 0
        caja["en_suelo"] = True
    else:
        caja["en_suelo"] = False

    if plataformas:
        for plat in plataformas:
            if caja["rect"].colliderect(plat):
                if caja["vel_y"] >= 0 and caja["rect"].bottom - int(caja["vel_y"]) <= plat.top + 8:
                    caja["rect"].bottom = plat.top
                    caja["vel_y"] = 0
                    caja["en_suelo"] = True

    caja["rect"].clamp_ip(pantalla_rect)


def empujar_caja(p, caja, otro=None, pantalla_rect=None, plataformas=None):
    jugador = p["hitbox"]
    caja_rect = caja["rect"]

    # No empuja lateralmente si el jugador está parado arriba o abajo de la caja
    if jugador.bottom <= caja_rect.top + 10 or jugador.top >= caja_rect.bottom - 10:
        return False

    hb_otro = otro["hitbox"] if (otro is not None and not otro.get("muerto", False)) else None
    otro_encima_caja = (
        hb_otro is not None
        and abs(hb_otro.bottom - caja_rect.top) <= 8
        and hb_otro.right > caja_rect.left
        and hb_otro.left < caja_rect.right
    )
    otro_obstaculo_lateral = (
        hb_otro is not None
        and not otro_encima_caja
        and hb_otro.bottom > caja_rect.top + 10
        and hb_otro.top < caja_rect.bottom - 10
    )

    if p["vel_x"] > 0:
        # Solo hay colisión si el jugador penetra/toca el lado izquierdo de la caja
        if jugador.right > caja_rect.left and jugador.left < caja_rect.left:
            desplazamiento = jugador.right - caja_rect.left
            caja_x_ant = caja_rect.x
            rect_futuro = caja_rect.move(desplazamiento, 0)
            bloqueado = False

            # 1. Plataforma como obstáculo lateral
            if plataformas:
                for plat in plataformas:
                    if rect_futuro.colliderect(plat) and (caja_rect.bottom > plat.top + 8 and caja_rect.top < plat.bottom - 8):
                        caja_rect.right = plat.left
                        jugador.right = caja_rect.left
                        if p["vel_x"] > 0:
                            p["vel_x"] = 0
                        bloqueado = True
                        break

            # 2. Otro personaje como obstáculo sólido
            if not bloqueado and otro_obstaculo_lateral and rect_futuro.colliderect(hb_otro) and hb_otro.left >= caja_rect.left:
                caja_rect.right = hb_otro.left
                jugador.right = caja_rect.left
                if p["vel_x"] > 0:
                    p["vel_x"] = 0
                bloqueado = True

            # 3. Límite de pantalla
            if not bloqueado and pantalla_rect and rect_futuro.right > pantalla_rect.right:
                caja_rect.right = pantalla_rect.right
                jugador.right = caja_rect.left
                if p["vel_x"] > 0:
                    p["vel_x"] = 0
                bloqueado = True

            if not bloqueado:
                caja_rect.x += desplazamiento
                jugador.right = caja_rect.left

            p["empujando"] = True
            p["direccion_empuje"] = 1

            dx = caja_rect.x - caja_x_ant
            if otro_encima_caja and dx != 0:
                hb_otro.x += dx
            return True

    elif p["vel_x"] < 0:
        # Solo hay colisión si el jugador penetra/toca el lado derecho de la caja
        if jugador.left < caja_rect.right and jugador.right > caja_rect.right:
            desplazamiento = caja_rect.right - jugador.left
            caja_x_ant = caja_rect.x
            rect_futuro = caja_rect.move(-desplazamiento, 0)
            bloqueado = False

            # 1. Plataforma como obstáculo lateral
            if plataformas:
                for plat in plataformas:
                    if rect_futuro.colliderect(plat) and (caja_rect.bottom > plat.top + 8 and caja_rect.top < plat.bottom - 8):
                        caja_rect.left = plat.right
                        jugador.left = caja_rect.right
                        if p["vel_x"] < 0:
                            p["vel_x"] = 0
                        bloqueado = True
                        break

            # 2. Otro personaje como obstáculo sólido
            if not bloqueado and otro_obstaculo_lateral and rect_futuro.colliderect(hb_otro) and hb_otro.right <= caja_rect.right:
                caja_rect.left = hb_otro.right
                jugador.left = caja_rect.right
                if p["vel_x"] < 0:
                    p["vel_x"] = 0
                bloqueado = True

            # 3. Límite de pantalla
            if not bloqueado and pantalla_rect and rect_futuro.left < pantalla_rect.left:
                caja_rect.left = pantalla_rect.left
                jugador.left = caja_rect.right
                if p["vel_x"] < 0:
                    p["vel_x"] = 0
                bloqueado = True

            if not bloqueado:
                caja_rect.x -= desplazamiento
                jugador.left = caja_rect.right

            p["empujando"] = True
            p["direccion_empuje"] = -1

            dx = caja_rect.x - caja_x_ant
            if otro_encima_caja and dx != 0:
                hb_otro.x += dx
            return True

    return False


def crear_estado_soga():
    return {
        "tension": 0.0,
        "dano_acumulado": 0.0,
        "nivel_estres": 0.0,
        "rota": False,
        "en_muerte": False,
        "particulas_rotura": [],
        "tiempo_rotura": 0,
    }


def actualizar_estado_soga_muerte(p1, p2, estado_soga=None, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Gestiona el comportamiento de la soga cuando uno de los personajes muere en el Mundo 2:
    - Permite un estiramiento adicional exclusivo de 10 px por encima de d_max (hasta d_max + 10 = 170).
    - Al superar ese límite adicional, la soga se rompe de forma visible y limpia en el centro.
    - Deja de ejercer fuerza física tras romperse.
    - El personaje muerto continúa cayendo libremente sin interferencias ni tirones.
    - Cada personaje conserva su cabo limpio colgando sin partículas ni hilachas sueltas.
    """
    if estado_soga is None:
        return

    en_muerte = p1.get("muerto", False) or p2.get("muerto", False)
    if not en_muerte:
        return

    if not estado_soga.get("en_muerte", False):
        estado_soga["en_muerte"] = True

    if not estado_soga.get("rota", False):
        c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
        c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
        distancia = (c2 - c1).length()
        limite_muerte = d_max + 10.0  # 160 + 10 = 170

        if distancia >= limite_muerte:
            estado_soga["rota"] = True
            estado_soga["tension"] = 0.0
            estado_soga["tiempo_rotura"] = 0
            estado_soga["particulas_rotura"] = []
    else:
        estado_soga["tension"] = 0.0
        estado_soga["tiempo_rotura"] = estado_soga.get("tiempo_rotura", 0) + 1


def actualizar_fisica_soga(p1, p2, estado_soga=None, d_reposo=DISTANCIA_SOGA_REPOSO, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Aplica una física de soga suave, continua y natural con desgaste acumulativo y límite estricto de estiramiento:
    - Cuando los personajes están dentro de la distancia de reposo (distancia <= d_reposo = 140px),
      la soga está floja (zona segura) y recupera progresivamente el desgaste acumulado.
    - Al superar d_reposo, la tensión elástica aparece progresivamente hasta d_max (160px).
    - Al alcanzar d_max con tensión/tirón activo, acumula daño en la zona central.
    - Si los personajes se quedan quietos, el daño acumulado PERMANECE en el nivel alcanzado (no se borra).
    - La recuperación solamente ocurre cuando los personajes se acercan lo suficiente entre sí (distancia <= 140px).
    - Si el daño acumulado llega al 100% (1.0), la cuerda se rompe limpiamente en el centro.
    - Remolque a velocidad natural completa sin frenos artificiales ni pérdidas de control.
    """
    if p1.get("muerto", False) or p2.get("muerto", False) or (estado_soga is not None and estado_soga.get("rota", False)):
        actualizar_estado_soga_muerte(p1, p2, estado_soga, d_max)
        if estado_soga is not None:
            estado_soga["tension"] = 0.0
        return

    c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
    c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
    v = c2 - c1
    distancia = v.length()

    if distancia < 0.001:
        if estado_soga is not None:
            estado_soga["tension"] = 0.0
        return

    direccion = v / distancia

    # 1. Cálculo de tensión elástica progresiva instantánea [0.0, 1.0]
    if distancia <= d_reposo:
        tension_objetivo = 0.0
    else:
        estiramiento = distancia - d_reposo
        rango = max(1.0, d_max - d_reposo)
        tasa = min(1.0, estiramiento / rango)
        tension_objetivo = tasa * tasa  # Crecimiento suave cuadrático
        if distancia >= d_max:
            tension_objetivo = 1.0

    if estado_soga is not None:
        tension_actual = estado_soga.get("tension", 0.0)
        factor = 0.40 if tension_objetivo > tension_actual else 0.50
        tension_actual += (tension_objetivo - tension_actual) * factor
        estado_soga["tension"] = max(0.0, min(1.0, tension_actual))
        t = estado_soga["tension"]
    else:
        t = tension_objetivo

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_rel = v2 - v1
    v_separacion = v_rel.dot(direccion)

    # 2. Mecánica de Daño Acumulativo (Desgaste en el centro)
    if estado_soga is not None:
        ux = direccion.x
        v1_away_h = -p1.get("vel_x", 0.0) * ux
        v2_away_h = p2.get("vel_x", 0.0) * ux
        dano_act = estado_soga.get("dano_acumulado", 0.0)

        # A. Acumulación de daño: ocurre cuando la cuerda supera su límite de tensión y hay esfuerzo de separación
        if distancia >= (d_max - 2.5):
            tasa_dano = 0.0
            if v1_away_h > 0.1 and v2_away_h > 0.1:
                # Tirón activo en direcciones opuestas (tug-of-war): máxima tensión
                tasa_dano = 0.0055  # ~180 frames (3 segundos continuos) de 0% a 100%
            elif v1_away_h > 0.1:
                p2_bloq = p2.get("empujando", False) or abs(p2.get("vel_x", 0.0)) < 0.1
                if p2_bloq:
                    tasa_dano = 0.0045
            elif v2_away_h > 0.1:
                p1_bloq = p1.get("empujando", False) or abs(p1.get("vel_x", 0.0)) < 0.1
                if p1_bloq:
                    tasa_dano = 0.0045
            elif not p1_suelo and not p2_suelo and v_separacion > 0.05:
                tasa_dano = 0.0045

            if tasa_dano > 0.0:
                dano_act = min(1.0, dano_act + tasa_dano)
                estado_soga["dano_acumulado"] = dano_act

        # B. Recuperación de daño: SOLAMENTE cuando los personajes se acercan a la zona segura (distancia <= d_reposo)
        elif distancia <= d_reposo:
            if dano_act > 0.0:
                tasa_recuperacion = 0.006  # Recuperación progresiva suave (~2.7s para volver a 0%)
                dano_act = max(0.0, dano_act - tasa_recuperacion)
                estado_soga["dano_acumulado"] = dano_act

        # C. Si los personajes se quedan quietos o están a distancia intermedia (140 < dist < 157):
        # El daño acumulado PERMANECE en el nivel exacto que alcanzó sin recuperarse automáticamente.

        estado_soga["nivel_estres"] = dano_act

        # D. Rotura por desgaste máximo (100% de daño acumulado)
        if dano_act >= 1.0:
            estado_soga["rota"] = True
            estado_soga["tension"] = 0.0
            estado_soga["tiempo_rotura"] = 0
            estado_soga["particulas_rotura"] = []
            matar_personaje(p1)
            matar_personaje(p2)
            return

    # Si la tensión física es despreciable y no hay restricción por distancia máxima
    if t <= 0.005 and distancia < d_max:
        return

    # 3. Situación A: Ambos personajes en el suelo
    if p1_suelo and p2_suelo:
        ux = direccion.x
        v1_x = p1.get("vel_x", 0.0)
        v2_x = p2.get("vel_x", 0.0)

        v1_away = -v1_x * ux
        v2_away = v2_x * ux

        p2_bloqueado_hacia_p1 = (
            p2.get("empujando", False) and (
                (-ux < -0.1 and p2.get("direccion_empuje", 0) == -1) or
                (-ux > 0.1 and p2.get("direccion_empuje", 0) == 1)
            )
        )
        p1_bloqueado_hacia_p2 = (
            p1.get("empujando", False) and (
                (ux < -0.1 and p1.get("direccion_empuje", 0) == -1) or
                (ux > 0.1 and p1.get("direccion_empuje", 0) == 1)
            )
        )

        p1_bloqueado = p1.get("empujando", False)
        p2_bloqueado = p2.get("empujando", False)

        if v1_away > 0.1 and v2_away > 0.1:
            # Tirón en direcciones opuestas (Tug of war)
            if distancia >= d_max:
                p1["vel_x"] = 0.0
                p2["vel_x"] = 0.0
            else:
                p1["vel_x"] *= max(0.0, 1.0 - t * 0.70)
                p2["vel_x"] *= max(0.0, 1.0 - t * 0.70)

        elif v1_away > 0.1 and v2_away <= 0.1:
            # P1 camina alejándose, tirando progresivamente de P2 (arrastre cooperativo)
            drag_dir = -ux  # Dirección hacia P1
            p2_bloqueado_hacia_p1 = p2_bloqueado and ((drag_dir > 0 and p2.get("direccion_empuje", 0) == 1) or (drag_dir < 0 and p2.get("direccion_empuje", 0) == -1))
            if p2_bloqueado_hacia_p1:
                if distancia >= d_max:
                    if ux > 0:
                        p1["vel_x"] = max(0.0, p1.get("vel_x", 0.0))
                    else:
                        p1["vel_x"] = min(0.0, p1.get("vel_x", 0.0))
                    p2["vel_x"] = 0.0
                else:
                    p1["vel_x"] *= max(0.0, 1.0 - t * 0.70)
            else:
                if distancia >= d_max:
                    v_shared = v1_x * 0.75
                    p1["vel_x"] = v_shared
                    p2["vel_x"] = v_shared
                    p2["moviendo"] = True
                    p2["mirando_derecha"] = (v_shared > 0)
                else:
                    target_v2 = v1_x * 0.75
                    p2["vel_x"] += (target_v2 - p2["vel_x"]) * (t * 0.40)
                    p1["vel_x"] -= v1_x * (t * 0.20)
                    if abs(p2["vel_x"]) > 0.2:
                        p2["moviendo"] = True
                        p2["mirando_derecha"] = (p2["vel_x"] > 0)

        elif v2_away > 0.1 and v1_away <= 0.1:
            # P2 camina alejándose, tirando progresivamente de P1 (arrastre cooperativo)
            drag_dir = ux  # Dirección hacia P2
            p1_bloqueado_hacia_p2 = p1_bloqueado and ((drag_dir > 0 and p1.get("direccion_empuje", 0) == 1) or (drag_dir < 0 and p1.get("direccion_empuje", 0) == -1))
            if p1_bloqueado_hacia_p2:
                if distancia >= d_max:
                    if ux > 0:
                        p2["vel_x"] = min(0.0, p2.get("vel_x", 0.0))
                    else:
                        p2["vel_x"] = max(0.0, p2.get("vel_x", 0.0))
                    p1["vel_x"] = 0.0
                else:
                    p2["vel_x"] *= max(0.0, 1.0 - t * 0.70)
            else:
                if distancia >= d_max:
                    v_shared = v2_x * 0.75
                    p2["vel_x"] = v_shared
                    p1["vel_x"] = v_shared
                    p1["moviendo"] = True
                    p1["mirando_derecha"] = (v_shared > 0)
                else:
                    target_v1 = v2_x * 0.75
                    p1["vel_x"] += (target_v1 - p1["vel_x"]) * (t * 0.40)
                    p2["vel_x"] -= v2_x * (t * 0.20)
                    if abs(p1["vel_x"]) > 0.2:
                        p1["moviendo"] = True
                        p1["mirando_derecha"] = (p1["vel_x"] > 0)

        # Garantizar que ninguna velocidad residual aumente la distancia por encima de d_max
        v1_post = p1.get("vel_x", 0.0)
        v2_post = p2.get("vel_x", 0.0)
        v_sep_post = (v2_post - v1_post) * ux
        if distancia >= d_max and v_sep_post > 0:
            if ux > 0:
                p1["vel_x"] = max(0.0, p1["vel_x"])
                p2["vel_x"] = min(0.0, p2["vel_x"])
            else:
                p1["vel_x"] = min(0.0, p1["vel_x"])
                p2["vel_x"] = max(0.0, p2["vel_x"])
        return

    # 4. Situación B: P1 en suelo, P2 en el aire
    if p1_suelo and not p2_suelo:
        if direccion.y > 0.05:
            # P2 cuelga por debajo de P1: Péndulo continuo
            p2["vel_y"] -= t * GRAVEDAD * (direccion.y * direccion.y)
            p2["vel_x"] -= t * GRAVEDAD * (direccion.y * direccion.x)

            v_tan = v_rel - v_separacion * direccion
            v_tan_mag = v_tan.length()
            a_c = min(3.5, (v_tan_mag * v_tan_mag) / max(1.0, distancia))
            p2["vel_x"] -= t * a_c * direccion.x
            p2["vel_y"] -= t * a_c * direccion.y

            if v_separacion > 0:
                sep_max = max(0.0, d_max - distancia)
                exc = max(0.0, v_separacion - sep_max)
                if exc > 0:
                    p2["vel_x"] -= direccion.x * exc
                    p2["vel_y"] -= direccion.y * exc
                else:
                    damp = v_separacion * (0.45 + 0.35 * t)
                    p2["vel_x"] -= direccion.x * damp
                    p2["vel_y"] -= direccion.y * damp

            if not p1.get("moviendo", False):
                p1["vel_x"] = 0.0
            else:
                if distancia >= d_max and v1.dot(direccion) < 0:
                    p1["vel_x"] *= 0.88
                    p2["vel_x"] += (p1["vel_x"] - p2["vel_x"]) * (0.35 * t)
        else:
            # P2 está por encima o a nivel (salto / gap)
            fuerza_tiron = t * 1.3
            if direccion.y < -0.15:
                p2["vel_y"] -= direccion.y * (t * 0.6)
            p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.6)
            if v_separacion > 0:
                sep_max = max(0.0, d_max - distancia)
                exc = max(0.0, v_separacion - sep_max)
                if exc > 0:
                    p2["vel_x"] -= direccion.x * exc
                    p2["vel_y"] -= direccion.y * (exc * 0.5)
                else:
                    damp = v_separacion * 0.5
                    p2["vel_x"] -= direccion.x * damp
        return

    # 5. Situación C: P2 en suelo, P1 en el aire (completamente simétrico a Situación B)
    if p2_suelo and not p1_suelo:
        dir_p1 = -direccion
        v_rel_p1 = v1 - v2
        v_sep_p1 = v_rel_p1.dot(dir_p1)

        if dir_p1.y > 0.05:
            p1["vel_y"] -= t * GRAVEDAD * (dir_p1.y * dir_p1.y)
            p1["vel_x"] -= t * GRAVEDAD * (dir_p1.y * dir_p1.x)

            v_tan = v_rel_p1 - v_sep_p1 * dir_p1
            v_tan_mag = v_tan.length()
            a_c = min(3.5, (v_tan_mag * v_tan_mag) / max(1.0, distancia))
            p1["vel_x"] -= t * a_c * dir_p1.x
            p1["vel_y"] -= t * a_c * dir_p1.y

            if v_sep_p1 > 0:
                sep_max = max(0.0, d_max - distancia)
                exc = max(0.0, v_sep_p1 - sep_max)
                if exc > 0:
                    p1["vel_x"] -= dir_p1.x * exc
                    p1["vel_y"] -= dir_p1.y * exc
                else:
                    damp = v_sep_p1 * (0.45 + 0.35 * t)
                    p1["vel_x"] -= dir_p1.x * damp
                    p1["vel_y"] -= dir_p1.y * damp

            if not p2.get("moviendo", False):
                p2["vel_x"] = 0.0
            else:
                if distancia >= d_max and v2.dot(dir_p1) < 0:
                    p2["vel_x"] *= 0.88
                    p1["vel_x"] += (p2["vel_x"] - p1["vel_x"]) * (0.35 * t)
        else:
            fuerza_tiron = t * 1.3
            if dir_p1.y < -0.15:
                p1["vel_y"] -= dir_p1.y * (t * 0.6)
            p1["vel_x"] -= dir_p1.x * (fuerza_tiron * 0.6)
            if v_sep_p1 > 0:
                sep_max = max(0.0, d_max - distancia)
                exc = max(0.0, v_sep_p1 - sep_max)
                if exc > 0:
                    p1["vel_x"] -= dir_p1.x * exc
                    p1["vel_y"] -= dir_p1.y * (exc * 0.5)
                else:
                    damp = v_sep_p1 * 0.5
                    p1["vel_x"] -= dir_p1.x * damp
        return

    # 6. Situación D: Ambos personajes en el aire
    fuerza_tiron = t * 1.0
    p1["vel_x"] += direccion.x * (fuerza_tiron * 0.5)
    p1["vel_y"] += direccion.y * (fuerza_tiron * 0.5)
    p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.5)
    p2["vel_y"] -= direccion.y * (fuerza_tiron * 0.5)

    if v_separacion > 0:
        sep_max = max(0.0, d_max - distancia)
        exc = max(0.0, v_separacion - sep_max)
        if exc > 0:
            p1["vel_x"] += direccion.x * (exc * 0.5)
            p1["vel_y"] += direccion.y * (exc * 0.5)
            p2["vel_x"] -= direccion.x * (exc * 0.5)
            p2["vel_y"] -= direccion.y * (exc * 0.5)

        # Elevación asistida: Si uno salta hacia arriba y el otro cuelga, lo eleva suavemente
        if p1["vel_y"] < -2.0 and direccion.y > 0.15:
            p2["vel_y"] = min(p2["vel_y"], p1["vel_y"] * 0.65)
        elif p2["vel_y"] < -2.0 and direccion.y < -0.15:
            p1["vel_y"] = min(p1["vel_y"], p2["vel_y"] * 0.65)


def aplicar_restriccion_soga(p1, p2, distancia_maxima=DISTANCIA_SOGA_MAXIMA, plataformas=None, suelo=None, estado_soga=None):
    """
    Garantiza el límite absoluto de distancia sin teletransportes ni tirones bruscos:
    - Aplica una estabilización suave únicamente si la distancia supera el límite máximo.
    - Con histéresis sub-píxel (<0.5px) para evitar jitter o vibración numérica.
    - Respeta colisiones sólidas con plataformas y suelo impidiendo atravesar techos o suelos.
    - Cuando un personaje está en el suelo y el otro cuelga, el del suelo actúa como ancla firme (w=0, w=1).
    - Anula cualquier velocidad residual que causó el exceso sin inyectar rebotes ni fuerzas opuestas.
    - Mantiene la trayectoria continua y natural del balanceo pendular.
    """
    if p1.get("muerto", False) or p2.get("muerto", False) or (estado_soga is not None and estado_soga.get("rota", False)):
        return

    c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
    c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
    v = c2 - c1
    distancia = v.length()

    if distancia <= distancia_maxima or distancia < 0.001:
        return

    exceso = distancia - distancia_maxima
    if exceso <= 0.001:
        return

    direccion = v / distancia

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    # Distribución equilibrada de la corrección posicional
    if p1_suelo and not p2_suelo:
        w1, w2 = 0.0, 1.0
    elif p2_suelo and not p1_suelo:
        w1, w2 = 1.0, 0.0
    elif p1_suelo and p2_suelo:
        p1_emp = p1.get("empujando", False)
        p2_emp = p2.get("empujando", False)
        if p1_emp and not p2_emp:
            w1, w2 = 0.0, 1.0
        elif p2_emp and not p1_emp:
            w1, w2 = 1.0, 0.0
        else:
            w1, w2 = 0.50, 0.50
    else:
        w1, w2 = 0.50, 0.50

    desp1 = direccion * (exceso * w1)
    desp2 = -direccion * (exceso * w2)

    def ajustar_posicion_con_solidez(p, desp):
        hb = p["hitbox"]
        x_prev = hb.x
        y_prev = hb.y

        dx = int(math.ceil(desp.x)) if desp.x > 0 else int(math.floor(desp.x))
        if dx != 0:
            hb.x += dx
            if plataformas:
                for plat in plataformas:
                    if hb.colliderect(plat) and hb.bottom > plat.top + 2 and hb.top < plat.bottom - 2:
                        if dx > 0 and x_prev + hb.width <= plat.left + 4:
                            hb.right = plat.left
                            if p.get("vel_x", 0) > 0:
                                p["vel_x"] = 0
                        elif dx < 0 and x_prev >= plat.right - 4:
                            hb.left = plat.right
                            if p.get("vel_x", 0) < 0:
                                p["vel_x"] = 0

        dy = int(math.ceil(desp.y)) if desp.y > 0 else int(math.floor(desp.y))
        if dy != 0:
            hb.y += dy
            if suelo is not None and hb.right > suelo.left and hb.left < suelo.right and hb.bottom > suelo.top:
                hb.bottom = suelo.top
                if p.get("vel_y", 0) > 0:
                    p["vel_y"] = 0
                p["en_suelo"] = True

            if plataformas:
                for plat in plataformas:
                    if hb.colliderect(plat):
                        # Aterrizaje sobre cara superior viniendo desde arriba
                        if dy > 0 and y_prev + hb.height <= plat.top + 6:
                            hb.bottom = plat.top
                            if p.get("vel_y", 0) > 0:
                                p["vel_y"] = 0
                            p["en_suelo"] = True
                        # Toque contra el techo / cara inferior viniendo desde abajo
                        elif dy < 0 and y_prev >= plat.bottom - 6:
                            hb.top = plat.bottom
                            if p.get("vel_y", 0) < 0:
                                p["vel_y"] = 0
                        # Bloqueo impenetrable si el personaje ya estaba abajo: NUNCA permitir atravesar hacia arriba
                        elif y_prev >= plat.bottom:
                            hb.top = plat.bottom
                            if p.get("vel_y", 0) < 0:
                                p["vel_y"] = 0

    if w1 > 0:
        ajustar_posicion_con_solidez(p1, desp1)
    if w2 > 0:
        ajustar_posicion_con_solidez(p2, desp2)

    # Anular cualquier velocidad residual de separación
    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_sep = (v2 - v1).dot(direccion)
    if v_sep > 0:
        p1["vel_x"] += direccion.x * (v_sep * w1)
        p1["vel_y"] += direccion.y * (v_sep * w1)
        p2["vel_x"] -= direccion.x * (v_sep * w2)
        p2["vel_y"] -= direccion.y * (v_sep * w2)


def crear_llave(x, y):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "x_float": float(x),
        "y_float": float(y),
        "rect": pygame.Rect(x, y, 25, 46),
        "sprite": cargar_sprite_llave(),
        "recolectada": False,
        "portador": None,
        "velocidad": 6.0,
    }


ANCHO_PORTAL = 146
ALTO_PORTAL = 180


def crear_puerta(x, y, w=ANCHO_PORTAL, h=ALTO_PORTAL):
    sprites = cargar_sprites_puerta((w, h))
    # Mantener el portal apoyado sobre el suelo y centrado en su posición actual:
    # La coordenada y histórica correspondía a (suelo.top - 90), y x al borde izquierdo de 60 px.
    # El centro x original era (x + 30) y el suelo base era (y + 90).
    centro_x = x + 30
    suelo_y = y + 90
    rect_x = centro_x - w // 2
    # El sprite del portal (146x180) posee 4 filas transparentes en su base inferior (y=176..179).
    # Desplazamos rect_y 4 px hacia abajo para que el umbral de piedra apoye directamente sobre la superficie del suelo sin ningún hueco visible.
    rect_y = suelo_y - h + 4
    rect = pygame.Rect(rect_x, rect_y, w, h)
    # Zona de entrada al núcleo de energía verde para que los personajes entren visualmente al portal
    rect_entrada = pygame.Rect(centro_x - 30, rect_y + 20, 60, h - 20)
    return {
        "rect": rect,
        "rect_entrada": rect_entrada,
        "sprites": sprites,
        "abierta": False,
        "tick_portal": 0,
        "frame_portal": 0,
        "fase_candado": 0,      # 0: cerrado, 1: roto, 2: cayendo, 3: particula, 4: desaparecido
        "tick_candado": 0,
        "desbloqueando": False,
    }


def actualizar_puerta(puerta):
    """
    Actualiza la animación en bucle continuo de la energía verde del portal
    y la secuencia fluida de desbloqueo del candado (roto -> cayendo -> partícula -> desaparecer).
    Actualiza automáticamente 'cerrada' y 'abierta' en puerta['sprites'] para que cualquier
    llamada a blit(puerta['sprites'][estado], puerta['rect']) renderice la animación completa.
    """
    if puerta is None or "sprites" not in puerta:
        return

    # 1. Animación fluida en bucle de la energía verde del portal (Sprite 1 -> 2 -> 3 -> 1...)
    # 15 frames por sprite a 60 FPS (~4 FPS de rotación suave, gradual y natural de la energía mística)
    puerta["tick_portal"] = puerta.get("tick_portal", 0) + 1
    if puerta["tick_portal"] >= 15:
        puerta["tick_portal"] = 0
        puerta["frame_portal"] = (puerta.get("frame_portal", 0) + 1) % 3

    idx_p = puerta.get("frame_portal", 0)
    sp_portal_actual = puerta["sprites"]["portal"][idx_p]

    # 2. Secuencia de desbloqueo del candado
    fase = puerta.get("fase_candado", 0)
    tick_c = puerta.get("tick_candado", 0)
    candados = puerta["sprites"]["candado"]

    surf_candado_actual = None
    alpha_candado = 255
    offset_candado_y = 0

    if fase == 0:
        # Candado cerrado: permanece estático sobre el portal mientras esté bloqueado
        surf_candado_actual = candados[0]
    elif fase == 1:
        # Candado roto: al entrar en contacto con la llave (~14 frames / 0.23 s)
        surf_candado_actual = candados[1]
        puerta["tick_candado"] = tick_c + 1
        if puerta["tick_candado"] >= 14:
            puerta["fase_candado"] = 2
            puerta["tick_candado"] = 0
    elif fase == 2:
        # Candado cayendo: cae hacia abajo mientras se desvanece progresivamente (~24 frames / 0.40 s)
        surf_candado_actual = candados[2]
        puerta["tick_candado"] = tick_c + 1
        alpha_candado = max(30, int(255 * (1.0 - (puerta["tick_candado"] / 24.0))))
        offset_candado_y = int(puerta["tick_candado"] * 0.3)
        if puerta["tick_candado"] >= 24:
            puerta["fase_candado"] = 3
            puerta["tick_candado"] = 0
    elif fase == 3:
        # Última partícula: pequeña partícula en el suelo terminando de desaparecer (~18 frames / 0.30 s)
        surf_candado_actual = candados[3]
        puerta["tick_candado"] = tick_c + 1
        alpha_candado = max(0, int(255 * (1.0 - (puerta["tick_candado"] / 18.0))))
        if puerta["tick_candado"] >= 18:
            puerta["fase_candado"] = 4
            puerta["tick_candado"] = 0
    # fase == 4: Candado desaparecido por completo (no vuelve a aparecer jamás)

    # 3. Componer la superficie actual del portal + candado
    # Superficie limpia del portal sin candado
    puerta["sprites"]["abierta"] = sp_portal_actual

    # Si hay candado visible en pantalla
    if surf_candado_actual is not None and alpha_candado > 0:
        surf_comp = sp_portal_actual.copy()
        if alpha_candado < 255:
            s_alpha = surf_candado_actual.copy()
            s_alpha.set_alpha(alpha_candado)
            surf_comp.blit(s_alpha, (0, offset_candado_y))
        else:
            surf_comp.blit(surf_candado_actual, (0, offset_candado_y))

        # Durante el desbloqueo (fases 1, 2, 3), mostramos la transición activa
        if fase > 0:
            puerta["sprites"]["abierta"] = surf_comp
        puerta["sprites"]["cerrada"] = surf_comp
    else:
        puerta["sprites"]["cerrada"] = sp_portal_actual


def actualizar_llave(llave, personajes, puerta):
    if llave is None or puerta is None:
        return

    if not llave["recolectada"]:
        for p in personajes:
            if not p["muerto"] and llave["rect"].colliderect(p["hitbox"]):
                llave["recolectada"] = True
                llave["portador"] = p
                break
    else:
        if llave["portador"] is not None and not puerta["abierta"]:
            p = llave["portador"]
            if p.get("muerto", False):
                # Si el portador muere, suelta la llave en su posición actual para que el compañero pueda recogerla
                llave["portador"] = None
                llave["recolectada"] = False
                return
            distancia_separacion = 25
            objetivo_x = p["hitbox"].left - llave["rect"].width - distancia_separacion if p["mirando_derecha"] else p["hitbox"].right + distancia_separacion
            objetivo_y = p["hitbox"].centery - (llave["rect"].height // 2)

            dx = objetivo_x - llave["x_float"]
            dy = objetivo_y - llave["y_float"]
            distancia = (dx ** 2 + dy ** 2) ** 0.5

            if distancia > 0:
                vel = llave["velocidad"]
                if distancia <= vel:
                    llave["x_float"] = float(objetivo_x)
                    llave["y_float"] = float(objetivo_y)
                else:
                    llave["x_float"] += (dx / distancia) * vel
                    llave["y_float"] += (dy / distancia) * vel

            llave["rect"].x = int(llave["x_float"])
            llave["rect"].y = int(llave["y_float"])

    if llave["recolectada"] and not puerta["abierta"]:
        portador = llave["portador"]
        if portador is not None and portador["hitbox"].colliderect(puerta["rect"]):
            puerta["abierta"] = True
            puerta["desbloqueando"] = True
            puerta["fase_candado"] = 1  # Inicia desbloqueo: candado roto
            puerta["tick_candado"] = 0
            llave["portador"] = None


class PinchoRect(pygame.Rect):
    """
    Rectángulo para pincho con soporte de dirección (arriba, abajo, izquierda, derecha)
    para dibujo y cálculo geométrico adecuado.
    """
    def __init__(self, *args, direccion="arriba"):
        super().__init__(*args)
        self.direccion = direccion


def crear_pincho(x, y, ancho=32, alto=22, direccion="arriba"):
    """Crea una instancia de PinchoRect orientada."""
    return PinchoRect(x, y, ancho, alto, direccion=direccion)


def crear_pinchos(y_suelo=640):
    alto, ancho = 28, 45
    return [pygame.Rect(x, y_suelo - alto, ancho, alto) for x in (350, 400, 700, 950, 1000, 1250, 1550, 1600, 1800)]


def matar_personaje(p):
    """
    Aplica el estado de muerte al personaje con el impulso vertical característico.
    Si ya está muerto, no se vuelve a activar ni se reinicia el impulso.
    Desvincula inmediatamente al personaje de cualquier velocidad residual o física de agua.
    Conserva la posición horizontal exacta donde se produjo la muerte sin desplazamientos.
    En escenarios acuáticos (Mundo 3), aplica una reacción vertical suave (-3.5) para que
    el personaje comience la animación de caída exactamente donde perdió la vida sin atravesar techos.
    """
    if p.get("muerto", False):
        return
    p["muerto"] = True
    es_acuatico = p.get("equipo_buceo", False) or p.get("en_agua", False)
    if es_acuatico:
        p["vel_y"] = -3.5
    else:
        p["vel_y"] = VELOCIDAD_MUERTE
    p["vel_x"] = 0
    p["moviendo"] = False
    p["en_agua"] = False
    p["en_suelo"] = False
    p["tiempo_muerte"] = 0
    p["muerte_terminada"] = False


def comprobar_pinchos(p, pinchos):
    if p["muerto"]:
        return False
    hb = p.get("hitbox", p.get("rect"))
    if hb is None:
        return False
    vy = p.get("vel_y", 0)
    vx = p.get("vel_x", 0)

    for pincho in pinchos:
        # Colisión directa adaptada al tipo de obstáculo
        # En entornos acuáticos o con pinchos laterales (izq/der), se evalúa colisión precisa completa
        es_acuatico = p.get("equipo_buceo", False) or p.get("en_agua", False)
        dir_p = getattr(pincho, "direccion", "arriba")
        if es_acuatico or dir_p in ("izquierda", "derecha"):
            c_rect = pincho
        else:
            c_rect = pincho.inflate(-4, -2) if (pincho.width > 12 and pincho.height > 6) else pincho

        if hb.colliderect(c_rect):
            matar_personaje(p)
            return True

        # Detección continua anti-túnel cuando el personaje cae a gran velocidad
        if vy > 0:
            if hb.right > pincho.left + 2 and hb.left < pincho.right - 2:
                y_prev_bottom = hb.bottom - int(vy)
                if y_prev_bottom <= pincho.top + 4 and hb.bottom >= pincho.top:
                    matar_personaje(p)
                    return True
        elif vy < 0:
            # Detección continua anti-túnel cuando el personaje salta hacia pinchos en el techo
            if hb.right > pincho.left + 2 and hb.left < pincho.right - 2:
                y_prev_top = hb.top - int(vy)
                if y_prev_top >= pincho.bottom - 4 and hb.top <= pincho.bottom:
                    matar_personaje(p)
                    return True

        # Detección continua anti-túnel horizontal (desplazamiento en nado o corrientes)
        if vx > 0:
            if hb.bottom > pincho.top + 2 and hb.top < pincho.bottom - 2:
                x_prev_right = hb.right - int(vx)
                if x_prev_right <= pincho.left + 4 and hb.right >= pincho.left:
                    matar_personaje(p)
                    return True
        elif vx < 0:
            if hb.bottom > pincho.top + 2 and hb.top < pincho.bottom - 2:
                x_prev_left = hb.left - int(vx)
                if x_prev_left >= pincho.right - 4 and hb.left <= pincho.right:
                    matar_personaje(p)
                    return True
    return False


def actualizar_muerte(p, duracion_max=None, limites_mundo=None):
    if not p["muerto"]:
        return
    p["tiempo_muerte"] += 1
    p["vel_y"] += GRAVEDAD
    p["hitbox"].y += int(p["vel_y"])

    # Mantener al personaje en animación de muerte dentro de los límites físicos del escenario
    if limites_mundo is not None:
        y_min = limites_mundo.top if hasattr(limites_mundo, "top") else 0
        if p["hitbox"].top < y_min:
            p["hitbox"].top = y_min
            p["vel_y"] = max(0.0, p["vel_y"])
        x_min = limites_mundo.left if hasattr(limites_mundo, "left") else 0
        x_max = limites_mundo.right if hasattr(limites_mundo, "right") else 3000
        if p["hitbox"].left < x_min:
            p["hitbox"].left = x_min
        elif p["hitbox"].right > x_max:
            p["hitbox"].right = x_max
    elif p["hitbox"].top < 0 and (p.get("equipo_buceo", False) or p.get("en_agua", False)):
        p["hitbox"].top = 0
        p["vel_y"] = max(0.0, p["vel_y"])

    d_max = duracion_max if duracion_max is not None else p.get("duracion_muerte_max", None)
    if p["hitbox"].top > 720 or (d_max is not None and p["tiempo_muerte"] >= d_max):
        p["muerte_terminada"] = True


# ============================================================
# FÍSICA Y MECÁNICAS ACUÁTICAS (MUNDO 3)
# ============================================================

ZONA_AGUA = pygame.Rect(0, 220, ANCHO, ALTO - 80 - 220)
GRAVEDAD_AGUA = 0.10
VELOCIDAD_NADO_VERTICAL = 0.85
FRICCION_AGUA = 0.86


def actualizar_estado_agua(p, zona_agua=ZONA_AGUA):
    """
    Detecta si el personaje está dentro del agua.
    - Recibe: diccionario del personaje 'p' y el rectángulo de agua 'zona_agua'.
    - Modifica: p["en_agua"] = True/False según colisión con la hitbox.
    - Devuelve: booleano indicando si está sumergido.
    """
    if p.get("muerto", False):
        p["en_agua"] = False
        return False
    p["en_agua"] = zona_agua.colliderect(p["hitbox"])
    return p["en_agua"]


def aplicar_fisica_agua(p, tecla_arriba=False, tecla_abajo=False, submarino=False):
    """
    Aplica la flotabilidad, nado y fricción viscosa del agua (Mundo 3).
    - Recibe: personaje 'p', estados de las teclas arriba/abajo para nadar, y modo 'submarino'.
    - Si submarino=True: control libre en 4 direcciones sin caída gravitacional. Los personajes
      pueden flotar en suspensión a cualquier altura y controlar su desplazamiento vertical y horizontal.
    - Si submarino=False: física acuática estándar con flotabilidad parcial.
    - Si el personaje está muerto, no se aplica amortiguación ni restricción acuática para
      conservar la velocidad y aceleración de caída natural de la animación de muerte.
    """
    if p.get("muerto", False):
        return
    if submarino:
        vel_nado = 4.5
        acel = 1.2
        if tecla_arriba and not tecla_abajo:
            if p["vel_y"] > 0:
                p["vel_y"] = -2.5
            else:
                p["vel_y"] = max(-vel_nado, p["vel_y"] - acel)
            p["moviendo"] = True
            p["en_suelo"] = False
        elif tecla_abajo and not tecla_arriba:
            if p["vel_y"] < 0:
                p["vel_y"] = 2.5
            else:
                p["vel_y"] = min(vel_nado, p["vel_y"] + acel)
            p["moviendo"] = True
        else:
            p["vel_y"] *= 0.82
            if abs(p["vel_y"]) < 0.15:
                p["vel_y"] = 0.0

        p["vel_y"] = max(-vel_nado, min(vel_nado, p["vel_y"]))
        return

    p["vel_y"] += GRAVEDAD_AGUA

    if tecla_arriba:
        p["vel_y"] -= VELOCIDAD_NADO_VERTICAL

    if tecla_abajo:
        p["vel_y"] += VELOCIDAD_NADO_VERTICAL

    p["vel_y"] *= FRICCION_AGUA
    p["vel_y"] = max(-6, min(6, p["vel_y"]))


def puede_saltar(p):
    """
    Verifica si el personaje tiene permitido saltar.
    - Regla: debe estar en el suelo firme, no sumergido en agua y no estar muerto.
    """
    return p["en_suelo"] and not p["en_agua"] and not p["muerto"]
