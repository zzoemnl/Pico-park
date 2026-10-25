import os
import sys
import math
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

# Dimensiones de la llave
ANCHO_LLAVE = 25
ALTO_LLAVE = 46

# Rutas
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_PERSONAJES = os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Personajes")
RUTA_OBJETOS = os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Objetos")


# ============================================================
# FUNCIÓN PARA CARGAR SPRITES DE PERSONAJES
# ============================================================

def cargar_sprites(nombre_color):
    ruta_carpeta = os.path.join(RUTA_PERSONAJES, nombre_color)
    sprites = {}

    estados = [
        "quieto", "muerto",
        "caminar-1", "caminar-2", "caminar-3", "caminar-4",
        "caminar-5", "caminar-6", "caminar-7", "caminar-8",
        "saltar",
        "caminar-empujar-1", "caminar-empujar-2", "caminar-empujar-3", "caminar-empujar-4",
        "caminar-empujar-5", "caminar-empujar-6", "caminar-empujar-7", "caminar-empujar-8",
        "saltar-empujar", "pestañear",
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
# CARGA Y CREACIÓN DE SPRITES PARA LLAVE Y PUERTA
# ============================================================

def cargar_sprite_llave():
    ruta_llave = os.path.join(RUTA_OBJETOS, "llave.png")
    
    if os.path.isfile(ruta_llave):
        try:
            img = pygame.image.load(ruta_llave).convert_alpha()
            return pygame.transform.scale(img, (ANCHO_LLAVE, ALTO_LLAVE))
        except pygame.error:
            pass
    
    # Placeholder si no existe llave.png
    surface = pygame.Surface((ANCHO_LLAVE, ALTO_LLAVE), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 215, 0), (12, 12), 10)
    pygame.draw.rect(surface, (255, 215, 0), (10, 12, 5, 30))
    pygame.draw.rect(surface, (255, 215, 0), (15, 32, 6, 4))
    pygame.draw.rect(surface, (255, 215, 0), (15, 38, 6, 4))
    return surface


def cargar_sprites_puerta():
    ruta_puerta_cerrada = os.path.join(RUTA_OBJETOS, "Puerta", "puerta_cerrada.png")
    ruta_puerta_abierta = os.path.join(RUTA_OBJETOS, "Puerta", "puerta_abierta.png")
    
    if not os.path.exists(ruta_puerta_cerrada):
        ruta_puerta_cerrada = os.path.join(RUTA_OBJETOS, "puerta.png")

    sprites = {}

    if os.path.isfile(ruta_puerta_cerrada):
        try:
            img = pygame.image.load(ruta_puerta_cerrada).convert_alpha()
            sprites["cerrada"] = pygame.transform.scale(img, (60, 90))
        except pygame.error:
            sprites["cerrada"] = None
    else:
        sprites["cerrada"] = None

    if os.path.isfile(ruta_puerta_abierta):
        try:
            img = pygame.image.load(ruta_puerta_abierta).convert_alpha()
            sprites["abierta"] = pygame.transform.scale(img, (60, 90))
        except pygame.error:
            sprites["abierta"] = None
    else:
        sprites["abierta"] = None

    if sprites["cerrada"] is None:
        p_cerrada = pygame.Surface((60, 90))
        p_cerrada.fill((139, 69, 19))
        pygame.draw.circle(p_cerrada, (255, 215, 0), (50, 45), 5)
        sprites["cerrada"] = p_cerrada

    if sprites["abierta"] is None:
        p_abierta = pygame.Surface((60, 90))
        p_abierta.fill((50, 50, 50))
        pygame.draw.rect(p_abierta, (139, 69, 19), (0, 0, 15, 90))
        sprites["abierta"] = p_abierta

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


def crear_llave(x, y):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "x_float": float(x),
        "y_float": float(y),
        "rect": pygame.Rect(x, y, ANCHO_LLAVE, ALTO_LLAVE),
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


def reiniciar_juego(p1, p2, llave, puerta):
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

    llave["x_float"] = float(llave["x_inicial"])
    llave["y_float"] = float(llave["y_inicial"])
    llave["rect"].x = llave["x_inicial"]
    llave["rect"].y = llave["y_inicial"]
    llave["recolectada"] = False
    llave["portador"] = None

    puerta["abierta"] = False


# ============================================================
# LÓGICA DE LA LLAVE Y LA PUERTA
# ============================================================

def actualizar_llave(llave, personajes, puerta):
    if not llave["recolectada"]:
        for p in personajes:
            if llave["rect"].colliderect(p["hitbox"]):
                llave["recolectada"] = True
                llave["portador"] = p
                break
    else:
        if llave["portador"] and not puerta["abierta"]:
            p = llave["portador"]
            
            # Separación horizontal en píxeles
            distancia_separacion = 25
            
            if p["mirando_derecha"]:
                objetivo_x = p["hitbox"].left - llave["rect"].width - distancia_separacion
            else:
                objetivo_x = p["hitbox"].right + distancia_separacion
            
            objetivo_y = p["hitbox"].centery - (llave["rect"].height // 2)

            dx = objetivo_x - llave["x_float"]
            dy = objetivo_y - llave["y_float"]
            distancia = math.hypot(dx, dy)

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
        if llave["portador"]["hitbox"].colliderect(puerta["rect"]):
            puerta["abierta"] = True
            llave["portador"] = None


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


# ============================================================
# FÍSICA Y COLISIONES
# ============================================================

def resolver_colisiones(p1, p2, suelo, pantalla_rect):
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

    p1["empujando"] = False
    p1["direccion_empuje"] = 0

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


def dibujar_puerta(pantalla, puerta):
    estado = "abierta" if puerta["abierta"] else "cerrada"
    pantalla.blit(puerta["sprites"][estado], puerta["rect"])


def dibujar_llave(pantalla, llave, puerta):
    if not puerta["abierta"]:
        pantalla.blit(llave["sprite"], llave["rect"])


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
    pygame.display.set_caption("Juego con Llave y Puerta")

    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial", 14, bold=True)

    btn_reiniciar = pygame.Rect(ANCHO - 130, 15, 115, 32)
    suelo = pygame.Rect(0, 520, ANCHO, 80)

    jugador1 = crear_personaje(100, 0, COLOR_JUGADOR1)
    jugador2 = crear_personaje(200, 0, COLOR_JUGADOR2)

    llave = crear_llave(500, suelo.top - ALTO_LLAVE)
    puerta = crear_puerta(710, suelo.top - 90)

    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_reiniciar.collidepoint(evento.pos):
                    reiniciar_juego(jugador1, jugador2, llave, puerta)

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                reiniciar_juego(jugador1, jugador2, llave, puerta)

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
        resolver_colisiones(jugador1, jugador2, suelo, pantalla_rect)
        resolver_colisiones(jugador2, jugador1, suelo, pantalla_rect)

        jugador1["hitbox"].clamp_ip(pantalla_rect)
        jugador2["hitbox"].clamp_ip(pantalla_rect)

        # Actualizar dirección de mirada según velocidad
        for p in (jugador1, jugador2):
            if p["vel_x"] > 0:
                p["mirando_derecha"] = True
            elif p["vel_x"] < 0:
                p["mirando_derecha"] = False

        # Actualizar Mecánica de Llave y Puerta
        actualizar_llave(llave, [jugador1, jugador2], puerta)

        # Dibujado
        pantalla.fill((30, 30, 30))
        pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        # Dibujar Objetos y Entidades
        dibujar_puerta(pantalla, puerta)
        dibujar_llave(pantalla, llave, puerta)
        dibujar_personaje(pantalla, jugador1)
        dibujar_personaje(pantalla, jugador2)

        dibujar_boton_reiniciar(pantalla, fuente, btn_reiniciar)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()