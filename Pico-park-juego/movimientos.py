import pygame
from sprites import cargar_sprites, cargar_sprite_caja

GRAVEDAD = 0.8
ANCHO_HITBOX = 45
ALTO_HITBOX = 85
TAMANO_CAJA = 60
DISTANCIA_SOGA = 200
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


def reiniciar_juego(p1, p2, caja=None, llave=None, puerta=None):
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
        and hb2.right > hb1.left + 5
        and hb2.left < hb1.right - 5
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
    if hb2 is not None and not p2_encima and hb1.right > hb2.left + 5 and hb1.left < hb2.right - 5:
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


def aplicar_restriccion_soga(p1, p2, distancia_maxima=DISTANCIA_SOGA, plataformas=None, suelo=None):
    c1 = pygame.Vector2(p1["hitbox"].center)
    c2 = pygame.Vector2(p2["hitbox"].center)
    v = c2 - c1
    distancia = v.length()

    if distancia <= distancia_maxima or distancia == 0:
        return

    direccion = v / distancia
    exceso = distancia - distancia_maxima

    p1["hitbox"].centerx = round(c1.x + direccion.x * (exceso / 2))
    p2["hitbox"].centerx = round(c2.x - direccion.x * (exceso / 2))


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