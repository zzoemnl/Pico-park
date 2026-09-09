import os
import sys
import pygame

# --- CONFIGURACIÓN GLOBAL ---
ANCHO, ALTO = 800, 600
FPS = 60
GRAVEDAD = 0.8

# Tamaño del sprite visual
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

# Tamaño de la Hitbox (Mismo alto, pero menor ancho y centrada)
ANCHO_HITBOX = 45  # Menos ancho que el sprite
ALTO_HITBOX = ALTO_PERSONAJE

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "Personajes")


def cargar_sprites(nombre_color):
    """Carga y escala todos los sprites al nuevo tamaño."""
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

    # Imagen de respaldo escalada
    for estado in estados:
        img_temp = pygame.Surface((ANCHO_PERSONAJE, ALTO_PERSONAJE))
        img_temp.fill((50, 120, 240))
        sprites[estado] = img_temp

    # Carga y reescalado de imágenes reales
    if os.path.exists(ruta_carpeta):
        for estado in estados:
            for ext in [".png", ".PNG", ".jpg", ".JPG"]:
                ruta_archivo = os.path.join(ruta_carpeta, f"{estado}{ext}")
                if os.path.isfile(ruta_archivo):
                    try:
                        img = pygame.image.load(ruta_archivo).convert_alpha()
                        sprites[estado] = pygame.transform.scale(
                            img, (ANCHO_PERSONAJE, ALTO_PERSONAJE)
                        )
                        break
                    except pygame.error:
                        pass

    return sprites


def crear_personaje(x, y, color_carpeta):
    """Inicializa al personaje usando la hitbox para físicas."""
    return {
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
        "tocando_otro": False,
        "tiempo_quieto": 0,  # Contador en frames de cuánto tiempo lleva quieto
        "mostrando_pestañeo": False,
    }


def actualizar_temporizadores(p):
    """Maneja la lógica de los 15 segundos quieto y el pestañeo cada 10 segundos."""
    # Consideramos quieto cuando no tiene velocidad horizontal y está tocando el suelo
    esta_quieto = (p["vel_x"] == 0) and p["en_suelo"]

    if esta_quieto and not p["tocando_otro"]:
        p["tiempo_quieto"] += 1

        # 15 segundos = 15 * FPS frames
        frames_15_seg = 15 * FPS
        frames_10_seg = 10 * FPS
        duracion_pestañeo = int(0.5 * FPS)  # El pestañeo dura 0.5 segundos

        if p["tiempo_quieto"] >= frames_15_seg:
            tiempo_post_15 = p["tiempo_quieto"] - frames_15_seg
            # Cada 10 segundos pestaña
            if (tiempo_post_15 % frames_10_seg) < duracion_pestañeo:
                p["mostrando_pestañeo"] = True
            else:
                p["mostrando_pestañeo"] = False
        else:
            p["mostrando_pestañeo"] = False
    else:
        # Si se mueve o toca al otro personaje, resetea los contadores
        p["tiempo_quieto"] = 0
        p["mostrando_pestañeo"] = False


def obtener_estado(p):
    """Determina la animación/sprite según el estado del personaje."""
    if not p["en_suelo"]:
        return "saltar"

    # Si está quieto y tocando al otro personaje -> empujar
    if p["vel_x"] == 0 and p["tocando_otro"]:
        return "caminar-empujar-2"

    # Si está en movimiento horizontal
    if p["vel_x"] != 0:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] = (p["frame_animacion"] % 3) + 1
        return f"caminar-{p['frame_animacion']}"

    # Si está quieto hace más de 15s y le toca pestañear
    if p["mostrando_pestañeo"]:
        return "pestañear"

    return "quieto"


def resolver_colisiones(p1, p2, suelo):
    """Resuelve las físicas usando las HITBOXES de los personajes."""
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]

    # --- 1. MOVIMIENTO HORIZONTAL ---
    hb1.x += p1["vel_x"]

    # Verificar si están en contacto
    p1["tocando_otro"] = hb1.colliderect(hb2)

    if p1["tocando_otro"]:
        margen_cabeza = 12

        # Si la base de p1 está casi al nivel de la cabeza de p2, sube encima
        if hb1.bottom <= hb2.top + margen_cabeza:
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        else:
            # Bloqueo lateral
            if p1["vel_x"] > 0:
                hb1.right = hb2.left
            elif p1["vel_x"] < 0:
                hb1.left = hb2.right

    # --- 2. MOVIMIENTO VERTICAL Y GRAVEDAD ---
    p1["vel_y"] += GRAVEDAD
    hb1.y += int(p1["vel_y"])

    # Verificación de apoyo sobre el personaje 2
    if hb1.colliderect(hb2):
        # Caída sobre el personaje 2
        if p1["vel_y"] >= 0 and hb1.top < hb2.top:
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

        # Colisión con la cabeza de p2 (saltando desde abajo)
        elif p1["vel_y"] < 0 and hb1.bottom > hb2.bottom:
            hb1.top = hb2.bottom
            p1["vel_y"] = 0

    # --- 3. COLISIÓN CON EL SUELO ---
    if hb1.colliderect(suelo):
        if p1["vel_y"] >= 0:
            hb1.bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True


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

    # El sprite visual se centra respecto a la hitbox para alinearse siempre
    rect_sprite = sprite.get_rect(center=p["hitbox"].center)
    pantalla.blit(sprite, rect_sprite)

    # --- OPCIONAL: Dibujar el cuadrado de la Hitbox (Descomentar para depurar) ---
    # pygame.draw.rect(pantalla, (255, 0, 0), p["hitbox"], 2)


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Juego con 2 Personajes - Hitbox y Animaciones")
    reloj = pygame.time.Clock()

    jugador1 = crear_personaje(100, 300, "Celeste")
    jugador2 = crear_personaje(300, 300, "Violeta")

    suelo = pygame.Rect(0, 520, ANCHO, 80)

    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        teclas = pygame.key.get_pressed()

        # --- CONTROLES JUGADOR 1 (Flechas) ---
        jugador1["vel_x"] = 0
        if teclas[pygame.K_LEFT]:
            jugador1["vel_x"] = -jugador1["velocidad_mov"]
        if teclas[pygame.K_RIGHT]:
            jugador1["vel_x"] = jugador1["velocidad_mov"]
        if teclas[pygame.K_UP] and jugador1["en_suelo"]:
            jugador1["vel_y"] = jugador1["fuerza_salto"]
            jugador1["en_suelo"] = False

        # --- CONTROLES JUGADOR 2 (WASD) ---
        jugador2["vel_x"] = 0
        if teclas[pygame.K_a]:
            jugador2["vel_x"] = -jugador2["velocidad_mov"]
        if teclas[pygame.K_d]:
            jugador2["vel_x"] = jugador2["velocidad_mov"]
        if teclas[pygame.K_w] and jugador2["en_suelo"]:
            jugador2["vel_y"] = jugador2["fuerza_salto"]
            jugador2["en_suelo"] = False

        # Actualizar posiciones y físicas
        resolver_colisiones(jugador1, jugador2, suelo)
        resolver_colisiones(jugador2, jugador1, suelo)

        # Restringir a los bordes de la pantalla (usando la hitbox)
        jugador1["hitbox"].clamp_ip(pantalla.get_rect())
        jugador2["hitbox"].clamp_ip(pantalla.get_rect())

        # Renderizado
        pantalla.fill((30, 30, 30))
        pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        dibujar_personaje(pantalla, jugador1)
        dibujar_personaje(pantalla, jugador2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()