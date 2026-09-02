import os
import sys
import pygame

# --- CONFIGURACIÓN GLOBAL ---
ANCHO, ALTO = 800, 600
FPS = 60
GRAVEDAD = 0.8

# Tamaño del personaje
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

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
    """Inicializa al personaje con las nuevas dimensiones."""
    return {
        "rect": pygame.Rect(x, y, ANCHO_PERSONAJE, ALTO_PERSONAJE),
        "vel_x": 0,
        "vel_y": 0,
        "velocidad_mov": 5,
        "fuerza_salto": -15,
        "en_suelo": False,
        "sprites": cargar_sprites(color_carpeta),
        "mirando_derecha": True,
        "frame_animacion": 1,
        "contador_anim": 0,
    }


def obtener_estado(p):
    if not p["en_suelo"]:
        return "saltar"

    if p["vel_x"] != 0:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] = (p["frame_animacion"] % 3) + 1
        return f"caminar-{p['frame_animacion']}"

    return "quieto"


def actualizar_personaje(p, suelo):
    # Movimiento Horizontal
    p["rect"].x += p["vel_x"]

    # Gravedad y Movimiento Vertical
    p["vel_y"] += GRAVEDAD
    p["rect"].y += int(p["vel_y"])

    # Colisión con el suelo
    if p["rect"].colliderect(suelo):
        if p["vel_y"] > 0:
            p["rect"].bottom = suelo.top
            p["vel_y"] = 0
            p["en_suelo"] = True


def dibujar_personaje(pantalla, p):
    estado = obtener_estado(p)
    sprite = p["sprites"].get(estado, p["sprites"]["quieto"])

    if p["vel_x"] > 0:
        p["mirando_derecha"] = True
    elif p["vel_x"] < 0:
        p["mirando_derecha"] = False

    if not p["mirando_derecha"]:
        sprite = pygame.transform.flip(sprite, True, False)

    pantalla.blit(sprite, p["rect"])


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Juego con 2 Personajes")
    reloj = pygame.time.Clock()

    # Creación de los dos personajes en posiciones y carpetas distintas
    jugador1 = crear_personaje(100, 300, "Verde oscuro")
    jugador2 = crear_personaje(300, 300, "Azul")  # Cambia "Azul" por el nombre de tu otra carpeta

    suelo = pygame.Rect(0, 520, ANCHO, 80)

    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

        teclas = pygame.key.get_pressed()

        # --- CONTROLES JUGADOR 1 (Flechas del teclado) ---
        jugador1["vel_x"] = 0
        if teclas[pygame.K_LEFT]:
            jugador1["vel_x"] = -jugador1["velocidad_mov"]
        if teclas[pygame.K_RIGHT]:
            jugador1["vel_x"] = jugador1["velocidad_mov"]
        if teclas[pygame.K_UP] and jugador1["en_suelo"]:
            jugador1["vel_y"] = jugador1["fuerza_salto"]
            jugador1["en_suelo"] = False

        # --- CONTROLES JUGADOR 2 (Teclas WASD) ---
        jugador2["vel_x"] = 0
        if teclas[pygame.K_a]:
            jugador2["vel_x"] = -jugador2["velocidad_mov"]
        if teclas[pygame.K_d]:
            jugador2["vel_x"] = jugador2["velocidad_mov"]
        if teclas[pygame.K_w] and jugador2["en_suelo"]:
            jugador2["vel_y"] = jugador2["fuerza_salto"]
            jugador2["en_suelo"] = False

        # Actualizar ambos personajes
        actualizar_personaje(jugador1, suelo)
        actualizar_personaje(jugador2, suelo)

        jugador1["rect"].clamp_ip(pantalla.get_rect())
        jugador2["rect"].clamp_ip(pantalla.get_rect())

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