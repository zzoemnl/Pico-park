import math
import random
import pygame
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
        estado_soga["rota"] = False
        estado_soga["en_muerte"] = False
        estado_soga["particulas_rotura"] = []

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


def resolver_colisiones(p1, p2, suelo, pantalla_rect, caja=None, en_agua=False, plataformas=None):
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

    # Movimiento horizontal de p1
    hb1.x += int(round(p1["vel_x"]))

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

    # Colisión lateral entre personajes (solo si están al mismo nivel lateral, no si uno está encima del otro)
    if hb2 is not None and not p2_encima and hb1.colliderect(hb2):
        if hb1.bottom > hb2.top + 10 and hb1.top < hb2.bottom - 10:
            if p1["vel_x"] > 0:
                hb1.right = hb2.left
                p1["vel_x"] = 0
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
            elif p1["vel_x"] < 0:
                hb1.left = hb2.right
                p1["vel_x"] = 0
                p1["empujando"] = True
                p1["direccion_empuje"] = -1

    # Si p2 estaba encima de p1, trasladar a p2 el desplazamiento horizontal real de p1
    if p2_encima and hb2 is not None:
        hb2.x += hb1.x - x_inicio

    # Movimiento vertical de p1
    if not en_agua:
        p1["vel_y"] += GRAVEDAD

    hb1.y += int(p1["vel_y"])

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


def transportar_personaje_encima(p_arriba, p_abajo):
    pass


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
                        bloqueado = True
                        break

            # 2. Otro personaje como obstáculo sólido
            if not bloqueado and otro_obstaculo_lateral and rect_futuro.colliderect(hb_otro):
                caja_rect.right = hb_otro.left
                jugador.right = caja_rect.left
                bloqueado = True

            # 3. Límite de pantalla
            if not bloqueado and pantalla_rect and rect_futuro.right > pantalla_rect.right:
                caja_rect.right = pantalla_rect.right
                jugador.right = caja_rect.left
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
                        bloqueado = True
                        break

            # 2. Otro personaje como obstáculo sólido
            if not bloqueado and otro_obstaculo_lateral and rect_futuro.colliderect(hb_otro):
                caja_rect.left = hb_otro.right
                jugador.left = caja_rect.right
                bloqueado = True

            # 3. Límite de pantalla
            if not bloqueado and pantalla_rect and rect_futuro.left < pantalla_rect.left:
                caja_rect.left = pantalla_rect.left
                jugador.left = caja_rect.right
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
        "rota": False,
        "en_muerte": False,
        "particulas_rotura": [],
    }


def actualizar_estado_soga_muerte(p1, p2, estado_soga=None, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Gestiona el comportamiento de la soga cuando uno de los personajes muere en el Mundo 2:
    - Permite un estiramiento adicional exclusivo de 10 px por encima de d_max (hasta d_max + 10).
    - Al superar ese límite adicional, la soga se rompe de forma visible.
    - Deja de ejercer fuerza física tras romperse.
    - El personaje muerto continúa cayendo libremente sin interferencias ni tirones.
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

            # Generar partículas de rotura en el punto de ruptura
            mid = (c1 + c2) * 0.5
            particulas = []
            for i in range(8):
                ang = i * (math.pi / 4.0) + random.uniform(-0.2, 0.2)
                spd = random.uniform(1.5, 3.5)
                particulas.append({
                    "x": mid.x + random.uniform(-3, 3),
                    "y": mid.y + random.uniform(-3, 3),
                    "vx": math.cos(ang) * spd,
                    "vy": math.sin(ang) * spd - 1.0,
                    "vida": random.randint(20, 35),
                })
            estado_soga["particulas_rotura"] = particulas
    else:
        estado_soga["tension"] = 0.0

    # Actualizar partículas existentes
    particulas_activas = []
    for part in estado_soga.get("particulas_rotura", []):
        part["x"] += part["vx"]
        part["y"] += part["vy"]
        part["vy"] += 0.25
        part["vida"] -= 1
        if part["vida"] > 0:
            particulas_activas.append(part)
    estado_soga["particulas_rotura"] = particulas_activas


def actualizar_fisica_soga(p1, p2, estado_soga=None, d_reposo=DISTANCIA_SOGA_REPOSO, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Aplica una física de soga suave, continua y natural con límite estricto de estiramiento:
    - Cuando los personajes están dentro de la distancia de reposo (distancia <= d_reposo = 140px),
      la soga está floja y no genera tensión ni fuerzas (libertad total de movimiento).
    - Al superar d_reposo, la tensión elástica aparece progresivamente hasta d_max (~20 px de estiramiento = 160px).
    - Al alcanzar d_max, transmite tensión y limita la separación afectando la velocidad de los personajes,
      impidiendo que la cuerda se estire más de lo permitido.
    - Conserva de manera fidedigna la inercia tangencial pendular y la trayectoria continua del péndulo.
    - Distingue adecuadamente entre personajes en el suelo y en el aire sin aceleraciones exageradas ni tirones bruscos.
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

    # 1. Cálculo del estiramiento elástico y tensión progresiva
    if distancia <= d_reposo:
        if estado_soga is not None:
            estado_soga["tension"] = 0.0
        return

    estiramiento = distancia - d_reposo
    rango = max(1.0, d_max - d_reposo)
    tasa = min(1.0, estiramiento / rango)
    tension_objetivo = tasa * tasa  # Crecimiento suave cuadrático

    if distancia >= d_max:
        tension_objetivo = 1.0

    if estado_soga is not None:
        tension_actual = estado_soga.get("tension", 0.0)
        if tension_objetivo > tension_actual:
            factor_retardo = 0.35 if distancia < d_max else 0.85
            tension_actual += (tension_objetivo - tension_actual) * factor_retardo
        else:
            tension_actual += (tension_objetivo - tension_actual) * 0.50
            if tension_actual < 0.001:
                tension_actual = 0.0
        estado_soga["tension"] = max(0.0, min(1.0, tension_actual))
        t = estado_soga["tension"]
    else:
        t = tension_objetivo

    if t <= 0.01:
        return

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_rel = v2 - v1
    v_separacion = v_rel.dot(direccion)

    # 2. Situación A: Ambos personajes en el suelo
    # Límite estricto a d_max (~20px adicionales = 160px). Ninguno puede alejarse más allá del límite.
    if p1_suelo and p2_suelo:
        if v_separacion > 0:
            sep_max_permitida = max(0.0, d_max - distancia)
            exceso_vel = max(0.0, v_separacion - sep_max_permitida)
            if exceso_vel > 0:
                p1_away = max(0.0, -v1.dot(direccion))
                p2_away = max(0.0, v2.dot(direccion))
                tot = p1_away + p2_away
                if tot > 0.001:
                    p1["vel_x"] += direccion.x * (exceso_vel * (p1_away / tot))
                    p2["vel_x"] -= direccion.x * (exceso_vel * (p2_away / tot))
            else:
                factor_freno = t * 0.60
                if v1.dot(direccion) < 0:
                    p1["vel_x"] += direccion.x * (v_separacion * factor_freno * 0.5)
                if v2.dot(direccion) > 0:
                    p2["vel_x"] -= direccion.x * (v_separacion * factor_freno * 0.5)
        return

    # 3. Situación B: P1 en el suelo, P2 en el aire
    # P1 actúa como ancla sobre la plataforma. P2 cuelga y se balancea como un péndulo continuo.
    if p1_suelo and not p2_suelo:
        fuerza_tiron = t * 1.3

        if direccion.y > 0.05:
            # P2 cuelga por debajo de P1: física de péndulo real
            # 1. Soporte radial contra la gravedad
            p2["vel_y"] -= t * GRAVEDAD * (direccion.y * direccion.y)
            p2["vel_x"] -= t * GRAVEDAD * (direccion.y * direccion.x)

            # 2. Aceleración centrípeta a lo largo del arco de oscilación
            v_tan = v_rel - v_separacion * direccion
            v_tan_mag = v_tan.length()
            a_c = min(3.5, (v_tan_mag * v_tan_mag) / max(1.0, distancia))
            p2["vel_x"] -= t * a_c * direccion.x
            p2["vel_y"] -= t * a_c * direccion.y

            # 3. Control de velocidad de separación
            if v_separacion > 0:
                sep_max_permitida = max(0.0, d_max - distancia)
                exceso_vel = max(0.0, v_separacion - sep_max_permitida)
                if exceso_vel > 0:
                    # Al límite máximo, P1 no puede seguir alejándose libremente
                    v1_away = max(0.0, -v1.dot(direccion))
                    if v1_away > 0:
                        p1["vel_x"] += direccion.x * min(v1_away, exceso_vel)
                    p2["vel_x"] -= direccion.x * (exceso_vel * 0.5)
                    p2["vel_y"] -= direccion.y * (exceso_vel * 0.5)
                else:
                    damp = v_separacion * (0.45 + 0.35 * t)
                    p2["vel_x"] -= direccion.x * damp
                    p2["vel_y"] -= direccion.y * damp

            # 4. Tracción transmitida al personaje ancla en el suelo (P1)
            tension_total = t * (GRAVEDAD * direccion.y + a_c + max(0.0, v_separacion) * 0.5)
            pull_x = tension_total * direccion.x
            if distancia >= d_max:
                v1_away = max(0.0, -v1.dot(direccion))
                if v1_away > 0:
                    p1["vel_x"] += direccion.x * v1_away
                else:
                    p1["vel_x"] += pull_x * 0.25
            else:
                if p1.get("moviendo", False):
                    p1["vel_x"] += pull_x * 0.15
                else:
                    p1["vel_x"] += pull_x * 0.40
        else:
            # P2 está por encima o al mismo nivel de P1 (salto estándar)
            if direccion.y < -0.15:
                p2["vel_y"] -= direccion.y * (t * 0.6)
            p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.6)
            p1["vel_x"] += direccion.x * (fuerza_tiron * 0.5)
            if v_separacion > 0:
                sep_max_permitida = max(0.0, d_max - distancia)
                exceso_vel = max(0.0, v_separacion - sep_max_permitida)
                if exceso_vel > 0:
                    p1["vel_x"] += direccion.x * (exceso_vel * 0.5)
                    p2["vel_x"] -= direccion.x * (exceso_vel * 0.5)
                else:
                    damp = v_separacion * (0.35 + 0.45 * t)
                    p2["vel_x"] -= direccion.x * (damp * 0.6)
                    p1["vel_x"] += direccion.x * (damp * 0.4)
        return

    # 4. Situación C: P2 en el suelo, P1 en el aire (completamente simétrico a Situación B)
    if p2_suelo and not p1_suelo:
        fuerza_tiron = t * 1.3
        if direccion.y < -0.05:
            dir_hacia_p1 = -direccion
            v_rel_p1 = v1 - v2
            v_sep_p1 = v_rel_p1.dot(dir_hacia_p1)

            p1["vel_y"] -= t * GRAVEDAD * (dir_hacia_p1.y * dir_hacia_p1.y)
            p1["vel_x"] -= t * GRAVEDAD * (dir_hacia_p1.y * dir_hacia_p1.x)

            v_tan = v_rel_p1 - v_sep_p1 * dir_hacia_p1
            v_tan_mag = v_tan.length()
            a_c = min(3.5, (v_tan_mag * v_tan_mag) / max(1.0, distancia))
            p1["vel_x"] -= t * a_c * dir_hacia_p1.x
            p1["vel_y"] -= t * a_c * dir_hacia_p1.y

            if v_sep_p1 > 0:
                sep_max_permitida = max(0.0, d_max - distancia)
                exceso_vel = max(0.0, v_sep_p1 - sep_max_permitida)
                if exceso_vel > 0:
                    v2_away = max(0.0, -v2.dot(dir_hacia_p1))
                    if v2_away > 0:
                        p2["vel_x"] += dir_hacia_p1.x * min(v2_away, exceso_vel)
                    p1["vel_x"] -= dir_hacia_p1.x * (exceso_vel * 0.5)
                    p1["vel_y"] -= dir_hacia_p1.y * (exceso_vel * 0.5)
                else:
                    damp = v_sep_p1 * (0.45 + 0.35 * t)
                    p1["vel_x"] -= dir_hacia_p1.x * damp
                    p1["vel_y"] -= dir_hacia_p1.y * damp

            tension_total = t * (GRAVEDAD * dir_hacia_p1.y + a_c + max(0.0, v_sep_p1) * 0.5)
            pull_x = tension_total * dir_hacia_p1.x
            if distancia >= d_max:
                v2_away = max(0.0, -v2.dot(dir_hacia_p1))
                if v2_away > 0:
                    p2["vel_x"] += dir_hacia_p1.x * v2_away
                else:
                    p2["vel_x"] += pull_x * 0.25
            else:
                if p2.get("moviendo", False):
                    p2["vel_x"] += pull_x * 0.15
                else:
                    p2["vel_x"] += pull_x * 0.40
        else:
            if direccion.y > 0.15:
                p1["vel_y"] += direccion.y * (t * 0.6)
            p1["vel_x"] += direccion.x * (fuerza_tiron * 0.6)
            p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.5)
            if v_separacion > 0:
                sep_max_permitida = max(0.0, d_max - distancia)
                exceso_vel = max(0.0, v_separacion - sep_max_permitida)
                if exceso_vel > 0:
                    p1["vel_x"] += direccion.x * (exceso_vel * 0.5)
                    p2["vel_x"] -= direccion.x * (exceso_vel * 0.5)
                else:
                    damp = v_separacion * (0.35 + 0.45 * t)
                    p1["vel_x"] += direccion.x * (damp * 0.6)
                    p2["vel_x"] -= direccion.x * (damp * 0.4)
        return

    # 5. Situación D: Ambos personajes en el aire
    fuerza_tiron = t * 1.0
    p1["vel_x"] += direccion.x * (fuerza_tiron * 0.5)
    p1["vel_y"] += direccion.y * (fuerza_tiron * 0.5)
    p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.5)
    p2["vel_y"] -= direccion.y * (fuerza_tiron * 0.5)

    if v_separacion > 0:
        sep_max_permitida = max(0.0, d_max - distancia)
        exceso_vel = max(0.0, v_separacion - sep_max_permitida)
        if exceso_vel > 0:
            p1["vel_x"] += direccion.x * (exceso_vel * 0.5)
            p1["vel_y"] += direccion.y * (exceso_vel * 0.5)
            p2["vel_x"] -= direccion.x * (exceso_vel * 0.5)
            p2["vel_y"] -= direccion.y * (exceso_vel * 0.5)
        else:
            damp = v_separacion * (0.40 + 0.35 * t)
            p1["vel_x"] += direccion.x * (damp * 0.5)
            p1["vel_y"] += direccion.y * (damp * 0.5)
            p2["vel_x"] -= direccion.x * (damp * 0.5)
            p2["vel_y"] -= direccion.y * (damp * 0.5)


def aplicar_restriccion_soga(p1, p2, distancia_maxima=DISTANCIA_SOGA_MAXIMA, plataformas=None, suelo=None, estado_soga=None):
    """
    Garantiza el límite absoluto de distancia sin teletransportes ni tirones bruscos:
    - Aplica una estabilización suave únicamente si la distancia supera el límite máximo.
    - Respeta colisiones sólidas con plataformas y suelo impidiendo atravesar techos o suelos.
    - Distribuye la corrección equilibradamente para no desplazar instantáneamente a personajes colgados.
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

    direccion = v / distancia
    exceso = distancia - distancia_maxima

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    # Distribución equilibrada de la corrección posicional
    if p1_suelo and not p2_suelo:
        w1, w2 = 0.40, 0.60
    elif p2_suelo and not p1_suelo:
        w1, w2 = 0.60, 0.40
    elif p1_suelo and p2_suelo:
        w1, w2 = 0.50, 0.50
    else:
        w1, w2 = 0.50, 0.50

    # Cancelar residualmente velocidad de separación a lo largo de la cuerda
    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_separacion = (v2 - v1).dot(direccion)

    if v_separacion > 0:
        p1["vel_x"] += direccion.x * (v_separacion * w1)
        p1["vel_y"] += direccion.y * (v_separacion * w1)
        p2["vel_x"] -= direccion.x * (v_separacion * w2)
        p2["vel_y"] -= direccion.y * (v_separacion * w2)

    desp1 = direccion * (exceso * w1)
    desp2 = -direccion * (exceso * w2)

    def ajustar_posicion_con_solidez(p, desp):
        hb = p["hitbox"]
        x_prev = hb.x
        y_prev = hb.y

        dx = int(round(desp.x))
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

        dy = int(round(desp.y))
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


def crear_puerta(x, y):
    return {
        "rect": pygame.Rect(x, y, 60, 90),
        "sprites": cargar_sprites_puerta(),
        "abierta": False,
    }


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
    """
    if p.get("muerto", False):
        return
    p["muerto"] = True
    p["vel_y"] = VELOCIDAD_MUERTE
    p["en_suelo"] = False


def comprobar_pinchos(p, pinchos):
    if p["muerto"]:
        return False
    hb = p.get("hitbox", p.get("rect"))
    if hb is None:
        return False
    vy = p.get("vel_y", 0)

    for pincho in pinchos:
        # Colisión directa de bounding box
        if hb.colliderect(pincho):
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
    return False


def actualizar_muerte(p):
    if not p["muerto"]:
        return
    p["tiempo_muerte"] += 1
    p["vel_y"] += GRAVEDAD
    p["hitbox"].y += int(p["vel_y"])
    if p["hitbox"].top > 720:
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