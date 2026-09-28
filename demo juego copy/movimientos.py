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


def reiniciar_juego(p1, p2, caja=None):
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


def resolver_colisiones(p1, p2, suelo, pantalla_rect, caja=None):
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]

    p2_encima = (
        abs(hb2.bottom - hb1.top) <= 4
        and hb2.right > hb1.left + 10
        and hb2.left < hb1.right - 10
    )

    x_anterior = hb1.x
    y_anterior = hb1.y

    # Movimiento horizontal
    hb1.x += p1["vel_x"]

    if p2_encima:
        hb2.x += hb1.x - x_anterior

    p1["empujando"] = False
    p1["direccion_empuje"] = 0

    # Caja: solo puede empujarse desde un lateral externo.
    if caja is not None:
        empujada = empujar_caja(p1, p2, caja, x_anterior, pantalla_rect)

        # Si el personaje intentó atravesar la caja sin estar en un lateral
        # externo válido, la caja se comporta como un cuerpo sólido y lo frena.
        if not empujada and hb1.colliderect(caja["rect"]):
            if hb1.centerx < caja["rect"].centerx:
                hb1.right = caja["rect"].left
            else:
                hb1.left = caja["rect"].right
            p1["vel_x"] = 0

    # Colisión horizontal entre jugadores
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

    # Física vertical. En agua, el movimiento vertical ya lo controla agua.py.
    if not p1["en_agua"]:
        p1["vel_y"] += GRAVEDAD

    hb1.y += int(p1["vel_y"])

    if p2_encima:
        hb2.y += hb1.y - y_anterior

    # Colisión vertical con caja.
    if caja is not None and hb1.colliderect(caja["rect"]):
        if p1["vel_y"] >= 0 and hb1.bottom - p1["vel_y"] <= caja["rect"].top + 12:
            hb1.bottom = caja["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        elif p1["vel_y"] < 0 and hb1.top < caja["rect"].bottom:
            hb1.top = caja["rect"].bottom
            p1["vel_y"] = 0

    # Colisión vertical entre jugadores
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

    # Suelo
    if hb1.colliderect(suelo) and p1["vel_y"] >= 0:
        hb1.bottom = suelo.top
        p1["vel_y"] = 0
        p1["en_suelo"] = True


# ============================================================
# TRANSPORTAR PERSONAJE ENCIMA
# ============================================================

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


def empujar_caja(p, otro, caja, x_anterior, pantalla_rect):
    jugador = p["hitbox"]
    caja_rect = caja["rect"]
    otro_rect = otro["hitbox"]
    velocidad = p["vel_x"]

    # Solo contacto EXTERNO con un lateral, nunca desde arriba o desde dentro.
    if velocidad == 0 or jugador.bottom <= caja_rect.top + 10 or jugador.top >= caja_rect.bottom:
        return False

    desde_izquierda = (
        velocidad > 0
        and x_anterior + jugador.width <= caja_rect.left
        and jugador.right >= caja_rect.left
    )
    desde_derecha = (
        velocidad < 0
        and x_anterior >= caja_rect.right
        and jugador.left <= caja_rect.right
    )
    if not (desde_izquierda or desde_derecha):
        return False

    destino = caja_rect.move(velocidad, 0)
    destino.clamp_ip(pantalla_rect)

    # IMPORTANTE: probar la CAJA EN SU FUTURA POSICIÓN contra el otro
    # personaje, no la hitbox del personaje que está empujando.
    # Si hay contacto lateral, la caja se queda quieta; no mueve al otro.
    otro_en_lateral = (
        not otro["muerto"]
        and otro_rect.bottom > caja_rect.top + 10
        and otro_rect.top < caja_rect.bottom
    )
    if otro_en_lateral:
        if desde_izquierda and destino.right > otro_rect.left and caja_rect.left < otro_rect.left:
            destino.x = min(destino.x, otro_rect.left - caja_rect.width)
        elif desde_derecha and destino.left < otro_rect.right and caja_rect.right > otro_rect.right:
            destino.x = max(destino.x, otro_rect.right)

    # No permitir que el empuje cree superposición con el otro jugador.
    if otro_en_lateral and destino.colliderect(otro_rect):
        destino.x = caja_rect.x

    caja_rect.x = destino.x
    if desde_izquierda:
        jugador.right = caja_rect.left
        p["direccion_empuje"] = 1
    else:
        jugador.left = caja_rect.right
        p["direccion_empuje"] = -1
    p["empujando"] = True
    return True


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

    direccion_x = dx / distancia

    # Si están separados horizontalmente, bloqueamos solo el movimiento
    # que aumenta la distancia. NO movemos ni arrastramos al otro.
    movimiento_aleja_p1 = p1["vel_x"] * (-direccion_x)
    movimiento_aleja_p2 = p2["vel_x"] * direccion_x

    if movimiento_aleja_p1 > 0:
        # Deshacemos solamente el movimiento de p1 que habría aumentado
        # la distancia. No tocamos la posición ni la velocidad de p2.
        p1["hitbox"].x -= int(p1["vel_x"])
        p1["vel_x"] = 0

    if movimiento_aleja_p2 > 0:
        # Lo mismo para p2: no arrastra ni mueve a p1.
        p2["hitbox"].x -= int(p2["vel_x"])
        p2["vel_x"] = 0


# ============================================================
# PINCHOS - FÍSICA / MUERTE
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

    # No hay clamp durante la muerte. El personaje puede caer infinitamente
    # hasta salir completamente de la pantalla.
    if p["hitbox"].top > 600:
        p["muerte_terminada"] = True
