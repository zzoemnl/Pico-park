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


def resolver_colisiones(p1, p2, suelo):
    """Resuelve la física entre personajes y plataformas permitiendo subirse encima."""
    
    # --- 1. MOVIMIENTO HORIZONTAL ---
    p1["rect"].x += p1["vel_x"]
    
    if p1["rect"].colliderect(p2["rect"]):
        margen_cabeza = 12 
        
        # Si la base de p1 está casi al nivel de la cabeza de p2, sube directamente
        if p1["rect"].bottom <= p2["rect"].top + margen_cabeza:
            p1["rect"].bottom = p2["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        else:
            # Bloqueo lateral si no está en la cima
            if p1["vel_x"] > 0:
                p1["rect"].right = p2["rect"].left
            elif p1["vel_x"] < 0:
                p1["rect"].left = p2["rect"].right

    # --- 2. MOVIMIENTO VERTICAL Y GRAVEDAD ---
    p1["vel_y"] += GRAVEDAD
    p1["rect"].y += int(p1["vel_y"])

    # Verificación de apoyo sobre el personaje 2
    if p1["rect"].colliderect(p2["rect"]):
        # Caída sobre el personaje 2
        if p1["vel_y"] >= 0 and p1["rect"].top < p2["rect"].top:
            p1["rect"].bottom = p2["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        
        # Colisión con la cabeza de p2 estando por debajo (saltando desde abajo)
        elif p1["vel_y"] < 0 and p1["rect"].bottom > p2["rect"].bottom:
            p1["rect"].top = p2["rect"].bottom
            p1["vel_y"] = 0

    # --- 3. COLISIÓN CON EL SUELO ---
    if p1["rect"].colliderect(suelo):
        if p1["vel_y"] >= 0:
            p1["rect"].bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True


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
    pygame.display.set_caption("Juego con 2 Personajes - Subir Encima")
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

        # Actualizar posiciones y físicas en una sola llamada por jugador
        resolver_colisiones(jugador1, jugador2, suelo)
        resolver_colisiones(jugador2, jugador1, suelo)

        # Restringir a los bordes de la pantalla
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