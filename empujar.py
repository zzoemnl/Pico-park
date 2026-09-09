import os
import sys
import pygame

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

ANCHO, ALTO = 800, 600
FPS = 60
GRAVEDAD = 0.8

# Dimensión del sprite (visual)
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

# Dimensión de la Hitbox (física centrada)
ANCHO_HITBOX = 45
ALTO_HITBOX = ALTO_PERSONAJE

# Tamaño de la caja
TAMANO_CAJA = 60

# Rutas
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "Personajes")


# ============================================================
# FUNCIÓN PARA CARGAR SPRITES
# ============================================================

def cargar_sprites(nombre_color):
    ruta_carpeta = os.path.join(RUTA_BASE, nombre_color)
    sprites = {}

    estados = [
        "quieto",
        "muerto",
        "caminar-1",
        "caminar-2",
        "caminar-3",
        "saltar",
        "caminar-empujar-1",
        "caminar-empujar-2",
        "caminar-empujar-3",
        "saltar-empujar",
        "pestañear",
    ]

    for estado in estados:
        img_temp = pygame.Surface((ANCHO_PERSONAJE, ALTO_PERSONAJE))
        img_temp.fill((50, 120, 240))
        sprites[estado] = img_temp

    if os.path.exists(ruta_carpeta):
        for estado in estados:
            ruta_archivo = os.path.join(ruta_carpeta, f"{estado}.png")
            if os.path.isfile(ruta_archivo):
                try:
                    img = pygame.image.load(ruta_archivo).convert_alpha()
                    sprites[estado] = pygame.transform.scale(
                        img, (ANCHO_PERSONAJE, ALTO_PERSONAJE)
                    )
                except pygame.error:
                    pass

    return sprites


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


def crear_caja(x, y):
    ruta_caja = os.path.join(DIRECTORIO_ACTUAL, "caja.png")
    sprite_caja = None

    if os.path.isfile(ruta_caja):
        try:
            img = pygame.image.load(ruta_caja).convert_alpha()
            sprite_caja = pygame.transform.scale(img, (TAMANO_CAJA, TAMANO_CAJA))
        except pygame.error:
            pass

    if sprite_caja is None:
        sprite_caja = pygame.Surface((TAMANO_CAJA, TAMANO_CAJA))
        sprite_caja.fill((139, 69, 19))

    return {
        "x_inicial": x,
        "y_inicial": y,
        "rect": pygame.Rect(x, y, TAMANO_CAJA, TAMANO_CAJA),
        "vel_y": 0,
        "en_suelo": False,
        "sprite": sprite_caja,
    }


def reiniciar_juego(p1, p2, caja):
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

    caja["rect"].x = caja["x_inicial"]
    caja["rect"].y = caja["y_inicial"]
    caja["vel_y"] = 0


# ============================================================
# LÓGICA DE ESTADOS Y PESTAÑEO
# ============================================================

def actualizar_temporizadores(p):
    esta_quieto = (p["vel_x"] == 0) and p["en_suelo"]

    if esta_quieto and not p["empujando"]:
        p["tiempo_quieto"] += 1
        frames_15_seg = 15 * FPS
        frames_10_seg = 10 * FPS
        duracion_pestañeo = int(0.5 * FPS)

        if p["tiempo_quieto"] >= frames_15_seg:
            tiempo_post_15 = p["tiempo_quieto"] - frames_15_seg
            if (tiempo_post_15 % frames_10_seg) < duracion_pestañeo:
                p["mostrando_pestañeo"] = True
            else:
                p["mostrando_pestañeo"] = False
        else:
            p["mostrando_pestañeo"] = False
    else:
        p["tiempo_quieto"] = 0
        p["mostrando_pestañeo"] = False


def obtener_estado(p):
    if not p["en_suelo"]:
        return "saltar"

    if p["empujando"]:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] = (p["frame_animacion"] % 3) + 1
        return f"caminar-empujar-{p['frame_animacion']}"

    if p["vel_x"] != 0:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] = (p["frame_animacion"] % 3) + 1
        return f"caminar-{p['frame_animacion']}"

    if p["mostrando_pestañeo"]:
        return "pestañear"

    return "quieto"


# ============================================================
# FÍSICA Y COLISIONES
# ============================================================

def actualizar_caja(caja, suelo, pantalla_rect):
    caja["vel_y"] += GRAVEDAD
    caja["rect"].y += int(caja["vel_y"])

    if caja["rect"].colliderect(suelo):
        if caja["vel_y"] >= 0:
            caja["rect"].bottom = suelo.top
            caja["vel_y"] = 0
            caja["en_suelo"] = True

    caja["rect"].clamp_ip(pantalla_rect)


def resolver_colisiones(p1, p2, caja, suelo, pantalla_rect):
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

    # Colisión Horizontal con Caja
    if hb1.colliderect(caja["rect"]):
        if hb1.bottom > caja["rect"].top + 10:
            if p1["vel_x"] > 0:
                caja["rect"].x += p1["vel_x"]
                hb1.right = caja["rect"].left
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
            elif p1["vel_x"] < 0:
                caja["rect"].x += p1["vel_x"]
                hb1.left = caja["rect"].right
                p1["empujando"] = True
                p1["direccion_empuje"] = -1

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

    # Colisión Vertical con Caja
    if hb1.colliderect(caja["rect"]):
        if p1["vel_y"] >= 0 and hb1.bottom - p1["vel_y"] <= caja["rect"].top + 12:
            hb1.bottom = caja["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        elif p1["vel_y"] < 0 and hb1.top < caja["rect"].bottom:
            hb1.top = caja["rect"].bottom
            p1["vel_y"] = 0

    # Colisión Vertical entre Personajes
    if not p2_encima and hb1.colliderect(hb2):
        superposicion = (hb1.right > hb2.left + 10 and hb1.left < hb2.right - 10)
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


# ============================================================
# RENDERIZADO
# ============================================================

def dibujar_personaje(pantalla, p):
    actualizar_temporizadores(p)
    estado = obtener_estado(p)
    sprite = p["sprites"].get(estado, p["sprites"]["quieto"])

    if p["vel_x"] > 0:
        p["mirando_derecha"] = True
    elif p["vel_x"] < 0:
        p["mirando_derecha"] = False

    if not p["mirando_derecha"]:
        sprite = pygame.transform.flip(sprite, True, False)

    rect_sprite = sprite.get_rect(center=p["hitbox"].center)
    pantalla.blit(sprite, rect_sprite)


def dibujar_boton_reiniciar(pantalla, fuente, btn_rect):
    pygame.draw.rect(pantalla, (180, 40, 40), btn_rect, border_radius=6)
    pygame.draw.rect(pantalla, (255, 255, 255), btn_rect, 2, border_radius=6)
    texto = fuente.render("Reiniciar (R)", True, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(center=btn_rect.center))


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pantalla_rect = pantalla.get_rect()
    pygame.display.set_caption("Juego con 2 Personajes - Hitbox Centrada")

    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial", 14, bold=True)

    btn_reiniciar = pygame.Rect(ANCHO - 130, 15, 115, 32)

    jugador1 = crear_personaje(100, 0, "Verde oscuro")
    jugador2 = crear_personaje(300, 0, "Azul")
    caja = crear_caja(450, 0)
    suelo = pygame.Rect(0, 520, ANCHO, 80)

    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_reiniciar.collidepoint(evento.pos):
                    reiniciar_juego(jugador1, jugador2, caja)
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                reiniciar_juego(jugador1, jugador2, caja)

        teclas = pygame.key.get_pressed()

        # Controles Jugador 1
        jugador1["vel_x"] = 0
        if teclas[pygame.K_LEFT]:
            jugador1["vel_x"] = -jugador1["velocidad_mov"]
        if teclas[pygame.K_RIGHT]:
            jugador1["vel_x"] = jugador1["velocidad_mov"]
        if teclas[pygame.K_UP] and jugador1["en_suelo"]:
            jugador1["vel_y"] = jugador1["fuerza_salto"]
            jugador1["en_suelo"] = False

        # Controles Jugador 2
        jugador2["vel_x"] = 0
        if teclas[pygame.K_a]:
            jugador2["vel_x"] = -jugador2["velocidad_mov"]
        if teclas[pygame.K_d]:
            jugador2["vel_x"] = jugador2["velocidad_mov"]
        if teclas[pygame.K_w] and jugador2["en_suelo"]:
            jugador2["vel_y"] = jugador2["fuerza_salto"]
            jugador2["en_suelo"] = False

        # Actualizar Física
        actualizar_caja(caja, suelo, pantalla_rect)
        resolver_colisiones(jugador1, jugador2, caja, suelo, pantalla_rect)
        resolver_colisiones(jugador2, jugador1, caja, suelo, pantalla_rect)

        jugador1["hitbox"].clamp_ip(pantalla_rect)
        jugador2["hitbox"].clamp_ip(pantalla_rect)

        # Dibujado
        pantalla.fill((30, 30, 30))
        pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        pantalla.blit(caja["sprite"], caja["rect"])

        dibujar_personaje(pantalla, jugador1)
        dibujar_personaje(pantalla, jugador2)

        dibujar_boton_reiniciar(pantalla, fuente, btn_reiniciar)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()