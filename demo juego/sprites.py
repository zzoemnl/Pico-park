import os
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
COLOR_JUGADOR1 = "Celeste"
COLOR_JUGADOR2 = "Violeta"

# Rutas
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Personajes")


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
        "caminar-4",
        "caminar-5",
        "caminar-6",
        "caminar-7",
        "caminar-8",
        "saltar",
        "caminar-empujar-1",
        "caminar-empujar-2",
        "caminar-empujar-3",
        "caminar-empujar-4",
        "caminar-empujar-5",
        "caminar-empujar-6",
        "caminar-empujar-7",
        "caminar-empujar-8",
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
        if p["empujando"]:
            return "saltar-empujar"
        return "saltar"

    if p["empujando"]:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1
            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1
        return f"caminar-empujar-{p['frame_animacion']}"

    if p["vel_x"] != 0:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1
            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1
        return f"caminar-{p['frame_animacion']}"

    if p["mostrando_pestañeo"]:
        return "pestañear"
    return "quieto"


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