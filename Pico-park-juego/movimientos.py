import pygame
from sprites import cargar_sprites, cargar_sprite_caja

GRAVEDAD = 0.8
ANCHO_HITBOX = 50
ALTO_HITBOX = 85
TAMANO_CAJA = 60
DISTANCIA_SOGA_REPOSO = 140
DISTANCIA_SOGA_MAXIMA = 210
DISTANCIA_SOGA = DISTANCIA_SOGA_MAXIMA
VELOCIDAD_MUERTE = -17


def crear_personaje(x, y, color_carpeta="Blanco"):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "hitbox": pygame.Rect(x, y, ANCHO_HITBOX, ALTO_HITBOX),
        "vel_x": 0,
        "vel_y": 0,
        "velocidad_mov": 5,
        "fuerza_salto": -15,
        "en_suelo": False,
        "en_agua": False,
        "sprites": cargar_sprites(color_carpeta),
        "color": (255, 255, 255),
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
    hb1.x += p1["vel_x"]

    p1["empujando"] = False
    p1["direccion_empuje"] = 0

    if plataformas:
        for plat in plataformas:
            if hb1.colliderect(plat):
                # Solo colisiona de costado si está claramente a la altura lateral (no parado arriba)
                if hb1.bottom > plat.top + 10 and hb1.top < plat.bottom - 10:
                    if p1["vel_x"] > 0:
                        hb1.right = plat.left
                        p1["empujando"] = True
                        p1["direccion_empuje"] = 1
                    elif p1["vel_x"] < 0:
                        hb1.left = plat.right
                        p1["empujando"] = True
                        p1["direccion_empuje"] = -1

    if pantalla_rect is not None:
        if hb1.left <= pantalla_rect.left:
            hb1.left = pantalla_rect.left
            if p1["vel_x"] < 0:
                p1["empujando"] = True
                p1["direccion_empuje"] = -1
        elif hb1.right >= pantalla_rect.right:
            hb1.right = pantalla_rect.right
            if p1["vel_x"] > 0:
                p1["empujando"] = True
                p1["direccion_empuje"] = 1

    if caja is not None:
        empujar_caja(p1, caja, p2, pantalla_rect, plataformas)

    # Colisión lateral entre personajes (solo si están al mismo nivel lateral, no si uno está encima del otro)
    if hb2 is not None and not p2_encima and hb1.colliderect(hb2):
        if hb1.bottom > hb2.top + 10 and hb1.top < hb2.bottom - 10:
            if p1["vel_x"] > 0:
                hb1.right = hb2.left
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
            elif p1["vel_x"] < 0:
                hb1.left = hb2.right
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
            if hb1.right > plat.left and hb1.left < plat.right:
                if p1["vel_y"] >= 0 and hb1.bottom >= plat.top and y_inicio + hb1.height <= plat.top + max(12, int(p1["vel_y"]) + 10):
                    hb1.bottom = plat.top
                    p1["vel_y"] = 0
                    p1["en_suelo"] = True
                    toco_superficie = True
                elif p1["vel_y"] < 0 and hb1.top <= plat.bottom and y_inicio >= plat.bottom - 10:
                    hb1.top = plat.bottom
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
    }


def actualizar_fisica_soga(p1, p2, estado_soga=None, d_reposo=DISTANCIA_SOGA_REPOSO, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Aplica una física de soga suave, progresiva y con retraso natural:
    - Cuando los personajes están cerca (distancia <= d_reposo), la soga está floja y no genera tensión.
    - Al superar d_reposo, la tensión aparece y crece progresivamente hacia d_max.
    - Incorpora un retraso natural (amortiguamiento suave) para que la soga no reaccione de golpe a cambios instantáneos.
    - Limita progresivamente la velocidad que aleja a los personajes, evitando que se lancen o arrastren violentamente entre sí.
    - Si un personaje camina hacia el otro o ambos caminan juntos, pueden moverse con total normalidad sin tirones.
    """
    if p1.get("muerto", False) or p2.get("muerto", False):
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

    # 1. Cálculo de la tensión objetivo según el estiramiento progresivo
    if distancia <= d_reposo:
        tension_objetivo = 0.0
    else:
        tasa = min(1.0, (distancia - d_reposo) / max(1.0, (d_max - d_reposo)))
        tension_objetivo = tasa * tasa  # Crecimiento cuadrático suave

    if distancia >= d_max:
        tension_objetivo = max(tension_objetivo, min(1.0, 0.90 + (distancia - d_max) * 0.04))

    # 2. Retraso natural y filtrado de tensión
    if estado_soga is not None:
        tension_actual = estado_soga.get("tension", 0.0)
        if tension_objetivo > tension_actual:
            # Retraso progresivo al tensarse (evita tirones abruptos instantáneos)
            factor_retardo = 0.22 if distancia < d_max else 0.50
            tension_actual += (tension_objetivo - tension_actual) * factor_retardo
        else:
            # Relajación rápida al acercarse
            tension_actual += (tension_objetivo - tension_actual) * 0.45
            if tension_actual < 0.001:
                tension_actual = 0.0
        estado_soga["tension"] = max(0.0, min(1.0, tension_actual))
        t = estado_soga["tension"]
    else:
        t = 0.0 if tension_objetivo < 0.001 else max(0.0, min(1.0, tension_objetivo))

    if t <= 0.01:
        return

    # 3. Limitación progresiva de velocidades en la dirección de alejamiento
    vel_1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    vel_2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))

    vel_alejamiento_1 = -vel_1.dot(direccion)  # Positivo si P1 se aleja de P2
    vel_alejamiento_2 = vel_2.dot(direccion)   # Positivo si P2 se aleja de P1

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    # Si P1 se aleja, amortiguar su avance sin jalar a P2
    if vel_alejamiento_1 > 0:
        if p1_suelo and p2_suelo:
            factor_freno_1 = 1.0 if distancia >= d_max - 0.5 else (t * 0.85)
        elif p1_suelo and not p2_suelo:
            # P1 en el suelo puede moverse y rescatar/llevar a P2 en el aire
            factor_freno_1 = min(0.40, t * 0.40)
        else:
            factor_freno_1 = 1.0 if distancia >= d_max - 0.5 else (t * 0.70)

        p1["vel_x"] += direccion.x * (vel_alejamiento_1 * factor_freno_1)

        # Amortiguación vertical para saltos y caídas
        if vel_1.y < 0 and direccion.y > 0.2:
            # Salto vertical alejándose de P2
            p1["vel_y"] += direccion.y * (vel_alejamiento_1 * factor_freno_1 * 0.45)
        elif vel_1.y > 0 and direccion.y < -0.2:
            # Caída alejándose de P2 que está arriba
            factor_caida = 1.0 if distancia >= d_max else (factor_freno_1 * 0.85)
            p1["vel_y"] += direccion.y * (vel_alejamiento_1 * factor_caida)

    # Si P2 se aleja, amortiguar su avance sin jalar a P1
    if vel_alejamiento_2 > 0:
        if p1_suelo and p2_suelo:
            factor_freno_2 = 1.0 if distancia >= d_max - 0.5 else (t * 0.85)
        elif p2_suelo and not p1_suelo:
            # P2 en el suelo puede moverse y rescatar/llevar a P1 en el aire
            factor_freno_2 = min(0.40, t * 0.40)
        else:
            factor_freno_2 = 1.0 if distancia >= d_max - 0.5 else (t * 0.70)

        p2["vel_x"] -= direccion.x * (vel_alejamiento_2 * factor_freno_2)

        # Amortiguación vertical para saltos y caídas
        if vel_2.y < 0 and direccion.y < -0.2:
            # Salto vertical alejándose de P1
            p2["vel_y"] -= direccion.y * (vel_alejamiento_2 * factor_freno_2 * 0.45)
        elif vel_2.y > 0 and direccion.y > 0.2:
            # Caída alejándose de P1 que está arriba
            factor_caida = 1.0 if distancia >= d_max else (factor_freno_2 * 0.85)
            p2["vel_y"] -= direccion.y * (vel_alejamiento_2 * factor_caida)


def aplicar_restriccion_soga(p1, p2, distancia_maxima=DISTANCIA_SOGA_MAXIMA, plataformas=None, suelo=None, estado_soga=None):
    """
    Garantiza el límite absoluto de distancia sin teletransportes ni tirones bruscos:
    - Aplica una estabilización suave únicamente si la distancia supera el límite máximo.
    - Respeta colisiones sólidas con plataformas y suelo.
    - No arrastra al personaje que está quieto en el suelo.
    - Permite al personaje en el suelo moverse cuando el otro cuelga en el aire.
    """
    if p1.get("muerto", False) or p2.get("muerto", False):
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

    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    vel_alejamiento_1 = -v1.dot(direccion)
    vel_alejamiento_2 = v2.dot(direccion)

    # El personaje en el suelo actúa como ancla firme y no es arrastrado
    if p1_suelo and not p2_suelo:
        w1, w2 = 0.0, 1.0
    elif p2_suelo and not p1_suelo:
        w1, w2 = 1.0, 0.0
    elif p1_suelo and p2_suelo:
        # Ambos en el suelo: no mover a quien está quieto (vel_x == 0)
        p1_mov = abs(p1.get("vel_x", 0.0)) > 0.1
        p2_mov = abs(p2.get("vel_x", 0.0)) > 0.1
        if p1_mov and not p2_mov:
            w1, w2 = 1.0, 0.0
        elif p2_mov and not p1_mov:
            w1, w2 = 0.0, 1.0
        else:
            w1, w2 = 0.5, 0.5
    else:
        w1, w2 = 0.5, 0.5

    def _redondear_hacia_afuera(val):
        return int(val + 0.5) if val >= 0 else int(val - 0.5)

    if w1 > 0 and w2 > 0:
        if exceso >= 1.5:
            desp1 = direccion * (exceso * 0.5)
            desp2 = -direccion * (exceso * 0.5)
        else:
            # Exceso residual de 1 px: corregir en el que tenga mayor velocidad de alejamiento
            if vel_alejamiento_1 >= vel_alejamiento_2:
                desp1 = direccion * exceso
                desp2 = pygame.Vector2(0, 0)
            else:
                desp1 = pygame.Vector2(0, 0)
                desp2 = -direccion * exceso
    elif w1 > 0:
        desp1 = direccion * exceso
        desp2 = pygame.Vector2(0, 0)
    elif w2 > 0:
        desp1 = pygame.Vector2(0, 0)
        desp2 = -direccion * exceso
    else:
        desp1 = pygame.Vector2(0, 0)
        desp2 = pygame.Vector2(0, 0)

    def ajustar_posicion_con_solidez(p, desp):
        hb = p["hitbox"]
        dx = _redondear_hacia_afuera(desp.x)
        if dx != 0:
            hb.x += dx
            if plataformas:
                for plat in plataformas:
                    if hb.colliderect(plat) and hb.bottom > plat.top + 8 and hb.top < plat.bottom - 8:
                        if dx > 0:
                            hb.right = plat.left
                        elif dx < 0:
                            hb.left = plat.right

        dy = _redondear_hacia_afuera(desp.y)
        if dy != 0:
            hb.y += dy
            if suelo and hb.bottom > suelo.top:
                hb.bottom = suelo.top
                p["vel_y"] = 0
                p["en_suelo"] = True
            if plataformas:
                for plat in plataformas:
                    if hb.colliderect(plat):
                        if dy > 0 and hb.bottom >= plat.top and hb.top < plat.top:
                            hb.bottom = plat.top
                            p["vel_y"] = 0
                            p["en_suelo"] = True
                        elif dy < 0 and hb.top <= plat.bottom and hb.bottom > plat.bottom:
                            hb.top = plat.bottom
                            p["vel_y"] = 0

    if w1 > 0:
        ajustar_posicion_con_solidez(p1, desp1)
    if w2 > 0:
        ajustar_posicion_con_solidez(p2, desp2)

    # Disipación residual de velocidad de alejamiento
    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_separacion = (v2 - v1).dot(direccion)

    if v_separacion > 0:
        p1["vel_x"] += direccion.x * (v_separacion * w1 * 0.5)
        p2["vel_x"] -= direccion.x * (v_separacion * w2 * 0.5)
        if direccion.y != 0:
            p1["vel_y"] += direccion.y * (v_separacion * w1 * 0.25)
            p2["vel_y"] -= direccion.y * (v_separacion * w2 * 0.25)


def crear_llave(x, y):
    from sprites import cargar_sprite_llave
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
    from sprites import cargar_sprites_puerta
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


def crear_pinchos(y_suelo=640):
    alto, ancho = 28, 45
    return [pygame.Rect(x, y_suelo - alto, ancho, alto) for x in (350, 400, 700, 950, 1000, 1250, 1550, 1600, 1800)]


def comprobar_pinchos(p, pinchos):
    if p["muerto"]:
        return
    for pincho in pinchos:
        if p["hitbox"].colliderect(pincho):
            p["muerto"] = True
            p["vel_y"] = VELOCIDAD_MUERTE
            p["en_suelo"] = False
            break


def actualizar_muerte(p):
    if not p["muerto"]:
        return
    p["tiempo_muerte"] += 1
    p["vel_y"] += GRAVEDAD
    p["hitbox"].y += int(p["vel_y"])
    if p["hitbox"].top > 720:
        p["muerte_terminada"] = True