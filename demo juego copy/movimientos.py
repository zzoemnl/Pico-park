import pygame

from sprites import cargar_sprites, cargar_sprite_caja

# ============================================================
# CONFIGURACIÓN GLOBAL DE MOVIMIENTO
# ============================================================

GRAVEDAD = 0.8
ANCHO_HITBOX = 45
ALTO_HITBOX = 85

# ============================================================
# CAJA
# ============================================================

TAMANO_CAJA = 60

# ============================================================
# SOGA
# ============================================================

DISTANCIA_SOGA = 200

# ============================================================
# MUERTE / PINCHOS
# ============================================================

VELOCIDAD_MUERTE = -17


# ============================================================
# MOVIMIENTO BÁSICO
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
        "en_agua": False,
        "sprites": cargar_sprites(color_carpeta),
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


# ============================================================
# MOVIMIENTO Y COLISIONES
# ============================================================

def resolver_colisiones(
    p1, p2, suelo, pantalla_rect, caja=None, en_agua=False
):
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]

    p2_encima = (
        abs(hb2.bottom - hb1.top) <= 4
        and hb2.right > hb1.left + 10
        and hb2.left < hb1.right - 10
    )

    x_anterior = hb1.x
    y_anterior = hb1.y

    # --------------------------------------------------------
    # Movimiento horizontal
    # --------------------------------------------------------
    hb1.x += p1["vel_x"]

    if p2_encima:
        hb2.x += hb1.x - x_anterior

    p1["empujando"] = False
    p1["direccion_empuje"] = 0

    # --------------------------------------------------------
    # Caja: contacto físico lateral, sin atravesarla
    # --------------------------------------------------------
    if caja is not None:
        empujar_caja(p1, caja, p2, pantalla_rect)

    # --------------------------------------------------------
    # Colisión horizontal entre jugadores
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Movimiento vertical
    # En agua la física vertical ya fue calculada por agua.py.
    # --------------------------------------------------------
    if not en_agua:
        p1["vel_y"] += GRAVEDAD

    hb1.y += int(p1["vel_y"])

    if p2_encima:
        hb2.y += hb1.y - y_anterior

    # --------------------------------------------------------
    # Colisión vertical con caja
    # --------------------------------------------------------
    if caja is not None and hb1.colliderect(caja["rect"]):
        if p1["vel_y"] >= 0 and hb1.bottom - p1["vel_y"] <= caja["rect"].top + 12:
            hb1.bottom = caja["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        elif p1["vel_y"] < 0 and hb1.top < caja["rect"].bottom:
            hb1.top = caja["rect"].bottom
            p1["vel_y"] = 0

    # --------------------------------------------------------
    # Colisión vertical entre jugadores
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Suelo
    # --------------------------------------------------------
    if hb1.colliderect(suelo) and p1["vel_y"] >= 0:
        hb1.bottom = suelo.top
        p1["vel_y"] = 0
        p1["en_suelo"] = True


def transportar_personaje_encima(p_arriba, p_abajo):
    if p_arriba["muerto"] or p_abajo["muerto"]:
        return

    hb_arriba = p_arriba["hitbox"]
    hb_abajo = p_abajo["hitbox"]
    margen = 4

    esta_encima = (
        abs(hb_arriba.bottom - hb_abajo.top) <= margen
        and hb_arriba.right > hb_abajo.left
        and hb_arriba.left < hb_abajo.right
    )

    if esta_encima:
        hb_arriba.x += p_abajo["vel_x"]
        hb_arriba.bottom = hb_abajo.top
        p_arriba["vel_y"] = 0
        p_arriba["en_suelo"] = True


# ============================================================
# CAJA - FÍSICA
# ============================================================

def crear_caja(x, y):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "rect": pygame.Rect(x, y, TAMANO_CAJA, TAMANO_CAJA),
        "vel_y": 0,
        "en_suelo": False,
        "sprite": cargar_sprite_caja(TAMANO_CAJA),
    }


def actualizar_caja(caja, suelo, pantalla_rect):
    caja["vel_y"] += GRAVEDAD
    caja["rect"].y += int(caja["vel_y"])

    if caja["rect"].colliderect(suelo) and caja["vel_y"] >= 0:
        caja["rect"].bottom = suelo.top
        caja["vel_y"] = 0
        caja["en_suelo"] = True
    else:
        caja["en_suelo"] = False

    caja["rect"].clamp_ip(pantalla_rect)


def empujar_caja(p, caja, otro=None, pantalla_rect=None):
    jugador = p["hitbox"]
    caja_rect = caja["rect"]

    # Tiene que existir contacto vertical con el lateral.
    if jugador.bottom <= caja_rect.top or jugador.top >= caja_rect.bottom:
        return False

    # --------------------------------------------------------
    # Empujar hacia la derecha
    # --------------------------------------------------------
    if p["vel_x"] > 0:
        contacto_externo = (
            jugador.right >= caja_rect.left - 5
            and jugador.right <= caja_rect.left + 5
            and jugador.left < caja_rect.left
        )

        if not contacto_externo:
            return False

        # Si hay otro personaje delante, la caja no avanza.
        if otro is not None:
            otro_rect = otro["hitbox"]
            caja_futura = caja_rect.move(p["vel_x"], 0)

            if caja_futura.colliderect(otro_rect):
                jugador.right = caja_rect.left
                p["empujando"] = True
                p["direccion_empuje"] = 1
                return True

        # ----------------------------------------------------
        # LÍMITE DERECHO DEL MUNDO
        # ----------------------------------------------------
        nueva_x = caja_rect.x + p["vel_x"]

        if pantalla_rect is not None:
            nueva_x = min(
                nueva_x,
                pantalla_rect.right - caja_rect.width
            )

        # Mover la caja solamente hasta donde puede llegar.
        caja_rect.x = nueva_x

        # El jugador siempre queda detrás de la caja.
        jugador.right = caja_rect.left

        p["empujando"] = True
        p["direccion_empuje"] = 1
        return True

    # --------------------------------------------------------
    # Empujar hacia la izquierda
    # --------------------------------------------------------
    if p["vel_x"] < 0:
        contacto_externo = (jugador.left <= caja_rect.right + 5 
                            and jugador.left >= caja_rect.right - 5 
                            and jugador.right > caja_rect.right)

        if not contacto_externo:
            return False

        # Si hay otro personaje delante, la caja no avanza.
        if otro is not None:
            otro_rect = otro["hitbox"]
            caja_futura = caja_rect.move(p["vel_x"], 0)

            if caja_futura.colliderect(otro_rect):
                jugador.left = caja_rect.right
                p["empujando"] = True
                p["direccion_empuje"] = -1
                return True
        # ----------------------------------------------------
        # LÍMITE IZQUIERDO DEL MUNDO
        # ----------------------------------------------------
        nueva_x = caja_rect.x + p["vel_x"]

        if pantalla_rect is not None:
            nueva_x = max(nueva_x,pantalla_rect.left)

        # Mover la caja solamente hasta donde puede llegar.
        caja_rect.x = nueva_x

        # El jugador siempre queda detrás de la caja.
        jugador.left = caja_rect.right
        p["empujando"] = True
        p["direccion_empuje"] = -1
        return True
    return False

    # --------------------------------------------------------
    # Empujar hacia la izquierda.
    # El personaje tiene que estar AFUERA, a la derecha.
    # --------------------------------------------------------
    if p["vel_x"] < 0:
        contacto_externo = (
            jugador.left <= caja_rect.right + 5
            and jugador.left >= caja_rect.right - 5
            and jugador.right > caja_rect.right
        )

        if not contacto_externo:
            return False

        if otro is not None:
            otro_rect = otro["hitbox"]
            caja_futura = caja_rect.move(p["vel_x"], 0)
            if caja_futura.colliderect(otro_rect):
                # La caja queda EXACTAMENTE en su posición.
                jugador.left = caja_rect.right
                p["empujando"] = True
                p["direccion_empuje"] = -1
                return True

        caja_rect.x += p["vel_x"]
        jugador.left = caja_rect.right
        p["empujando"] = True
        p["direccion_empuje"] = -1
        return True

    return False


# ============================================================
# SOGA - FÍSICA
# ============================================================

def aplicar_restriccion_soga(p1, p2, distancia_maxima=DISTANCIA_SOGA):
    centro1 = p1["hitbox"].center
    centro2 = p2["hitbox"].center

    dx = centro2[0] - centro1[0]
    dy = centro2[1] - centro1[1]
    distancia = (dx ** 2 + dy ** 2) ** 0.5

    if distancia <= distancia_maxima or distancia == 0:
        return

    # Bloqueamos solamente el movimiento que aumenta la distancia.
    direccion_x = dx / distancia
    movimiento_aleja_p1 = p1["vel_x"] * (-direccion_x)
    movimiento_aleja_p2 = p2["vel_x"] * direccion_x

    if movimiento_aleja_p1 > 0:
        p1["vel_x"] = 0
        p1["moviendo"] = True

    if movimiento_aleja_p2 > 0:
        p2["vel_x"] = 0
        p2["moviendo"] = True


# ============================================================
# LLAVE Y PUERTA
# ============================================================

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

            if p["mirando_derecha"]:
                objetivo_x = p["hitbox"].left - llave["rect"].width - distancia_separacion
            else:
                objetivo_x = p["hitbox"].right + distancia_separacion

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


def dibujar_llave_activa(llave, puerta):
    return llave is not None and puerta is not None and not puerta["abierta"]


# ============================================================
# PINCHOS / MUERTE
# ============================================================

def crear_pinchos():
    return [pygame.Rect(x, 500, 50, 20) for x in (220, 400, 580)]


def comprobar_pinchos(p, pinchos):
    if p["muerto"]:
        return

    for pincho in pinchos:
        if p["hitbox"].colliderect(pincho):
            p["muerto"] = True
            p["tiempo_muerte"] = 0
            p["vel_y"] = VELOCIDAD_MUERTE
            p["vel_x"] = 0
            p["en_suelo"] = False
            break


def actualizar_muerte(p):
    if not p["muerto"]:
        return

    p["tiempo_muerte"] += 1
    p["vel_y"] += GRAVEDAD
    p["hitbox"].y += int(p["vel_y"])

    # No se limita el personaje al borde inferior.
    # Sigue cayendo hasta salir completamente de la pantalla.
    if p["hitbox"].top > 600:
        p["muerte_terminada"] = True
