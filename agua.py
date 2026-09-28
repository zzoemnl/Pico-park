import os
import sys
import pygame
pygame.init()
# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

ANCHO, ALTO = 800, 600
FPS = 60
GRAVEDAD = 0.8
# -------------------------
# AGUA
# -------------------------
AZUL_AGUA = (0, 140, 240, 130)
# El agua comienza en Y = 220

zona_agua = pygame.Rect(0, 220, ANCHO, 380)

# Física dentro del agua
GRAVEDAD_AGUA = 0.15
VELOCIDAD_NADO_VERTICAL = 0.6
FRICCION_AGUA = 0.90

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
# CONFIGURACIÓN DEL FONDO
# ============================================================

NOMBRE_FONDO = "fondo.png"
RUTA_FONDO = os.path.join(DIRECTORIO_ACTUAL, NOMBRE_FONDO)

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

        img_temp = pygame.Surface((ANCHO_PERSONAJE, ALTO_PERSONAJE),pygame.SRCALPHA)
        img_temp.fill((50, 120, 240))
        sprites[estado] = img_temp

    if os.path.exists(ruta_carpeta):
        for estado in estados:
            ruta_archivo = os.path.join(ruta_carpeta,f"{estado}.png")
            if os.path.isfile(ruta_archivo):

                try:
                    img = pygame.image.load(ruta_archivo).convert_alpha()
                    sprites[estado] = pygame.transform.scale(img,(ANCHO_PERSONAJE,ALTO_PERSONAJE))

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
        "hitbox": pygame.Rect(x,y,ANCHO_HITBOX,ALTO_HITBOX),
        "vel_x": 0,
        "vel_y": 0,

        "velocidad_mov": 5,
        "fuerza_salto": -10,

        "en_suelo": False,

        # NUEVO:
        "en_agua": False,

        "sprites": cargar_sprites(color_carpeta),

        "mirando_derecha": True,

        "frame_animacion": 1,
        "contador_anim": 0,

        "empujando": False,
        "direccion_empuje": 0,

        "tiempo_quieto": 0,
        "mostrando_pestañeo": False,
    }


# ============================================================
# REINICIAR JUEGO
# ============================================================

def reiniciar_juego(p1, p2):

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


# ============================================================
# LÓGICA DE ESTADOS Y PESTAÑEO
# ============================================================

def actualizar_temporizadores(p):

    esta_quieto = (p["vel_x"] == 0 and p["en_suelo"])
    if esta_quieto and not p["empujando"]:

        p["tiempo_quieto"] += 1
        frames_15_seg = 15 * FPS
        frames_10_seg = 10 * FPS
        duracion_pestañeo = int(0.5 * FPS)

        if p["tiempo_quieto"] >= frames_15_seg:
            tiempo_post_15 = (p["tiempo_quieto"]- frames_15_seg)
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

    # Mientras está en el aire
    if not p["en_suelo"]:

        if p["empujando"]:
            return "saltar-empujar"

        return "saltar"

    # Empujando
    if p["empujando"]:
        p["contador_anim"] += 1

        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1

            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1

        return f"caminar-empujar-{p['frame_animacion']}"

    # Caminando
    if p["vel_x"] != 0:
        p["contador_anim"] += 1

        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1

            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1

        return f"caminar-{p['frame_animacion']}"

    # Pestañeo
    if p["mostrando_pestañeo"]:
        return "pestañear"

    return "quieto"


# ============================================================
# FÍSICA Y COLISIONES
# ============================================================
def resolver_colisiones(p1,p2,suelo,pantalla_rect,tecla_arriba=False,tecla_abajo=False):
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]
    # --------------------------------------------------------
    # DETECTAR SI ESTÁ EN EL AGUA
    # --------------------------------------------------------
    p1["en_agua"] = zona_agua.colliderect(hb1)
    # -------------------------------------------------------
    # PERSONAJE 2 ENCIMA DEL PERSONAJE 1
    # --------------------------------------------------------
    p2_encima = (abs(hb2.bottom - hb1.top) <= 4 and hb2.right > hb1.left + 10 and hb2.left < hb1.right - 10)
    x_anterior = hb1.x
    y_anterior = hb1.y

    # --------------------------------------------------------
    # MOVIMIENTO HORIZONTAL
    # --------------------------------------------------------
    hb1.x += p1["vel_x"]

    if p2_encima:
        hb2.x += (hb1.x - x_anterior)

    # --------------------------------------------------------
    # REINICIAR EMPUJE
    # --------------------------------------------------------

    p1["empujando"] = False
    p1["direccion_empuje"] = 0

    # --------------------------------------------------------
    # COLISIÓN HORIZONTAL ENTRE JUGADORES
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
    # FÍSICA VERTICAL
    # --------------------------------------------------------

    if p1["en_agua"]:
        # ================================================
        # FÍSICA DEL AGUA
        # ================================================
        p1["vel_y"] += GRAVEDAD_AGUA
        # Nadar hacia arriba
        if tecla_arriba:
            p1["vel_y"] -= VELOCIDAD_NADO_VERTICAL
        # Nadar hacia abajo
        if tecla_abajo:
            p1["vel_y"] += VELOCIDAD_NADO_VERTICAL
        # Fricción del agua
        p1["vel_y"] *= FRICCION_AGUA

    else:
        # ================================================
        # FÍSICA NORMAL
        # ================================================
        p1["vel_y"] += GRAVEDAD
    # --------------------------------------------------------
    # MOVIMIENTO VERTICAL
    # --------------------------------------------------------
    hb1.y += int(p1["vel_y"])
    if p2_encima:
        hb2.y += (hb1.y - y_anterior)

    # --------------------------------------------------------
    # COLISIÓN VERTICAL ENTRE PERSONAJES
    # --------------------------------------------------------

    if not p2_encima and hb1.colliderect(hb2):
        superposicion = (hb1.right > hb2.left + 10 and hb1.left < hb2.right - 10)

        if (p1["vel_y"] >= 0 and hb1.top < hb2.top and superposicion):
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

        elif (p1["vel_y"] < 0 and hb1.bottom > hb2.bottom):
            hb1.top = hb2.bottom
            p1["vel_y"] = 0

    # --------------------------------------------------------
    # COLISIÓN CON EL SUELO
    # --------------------------------------------------------

    if hb1.colliderect(suelo):
        if p1["vel_y"] >= 0:
            hb1.bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

# ============================================================
# RENDERIZADO DEL PERSONAJE
# ============================================================

def dibujar_personaje(pantalla, p):
    actualizar_temporizadores(p)
    estado = obtener_estado(p)
    sprite = p["sprites"].get(estado,p["sprites"]["quieto"])

    if p["vel_x"] > 0:
        p["mirando_derecha"] = True

    elif p["vel_x"] < 0:
        p["mirando_derecha"] = False

    if not p["mirando_derecha"]:
        sprite = pygame.transform.flip(sprite,True,False)
    rect_sprite = sprite.get_rect(center=p["hitbox"].center)

    # Dibujar personaje normalmente
    pantalla.blit(sprite, rect_sprite)

    # ========================================================
    # EFECTO DE AGUA SOBRE LA PARTE SUMERGIDA
    # ========================================================

    if p["en_agua"]:
        # Crear una copia transparente del sprite
        sprite_agua = pygame.Surface(sprite.get_size(),pygame.SRCALPHA)

        # Color azul del agua
        sprite_agua.fill((0, 100, 180, 70))

        # Usar la transparencia original del sprite
        # para que el azul SOLO aparezca sobre el personaje
        sprite_agua.blit(sprite,(0, 0),special_flags=pygame.BLEND_RGBA_MULT)
        # ----------------------------------------------------
        # Guardamos el área de dibujo actual
        # ----------------------------------------------------
        
        clip_anterior = pantalla.get_clip()
        # Solo permitimos dibujar desde la superficie
        # del agua hacia abajo
        pantalla.set_clip(
            pygame.Rect(0,zona_agua.top,ANCHO,ALTO - zona_agua.top))
        # Dibujar la capa azul SOLO sobre el personaje
        pantalla.blit(sprite_agua,rect_sprite)
        # Restaurar el área de dibujo
        pantalla.set_clip(clip_anterior)


# ============================================================
# DIBUJAR AGUA
# ============================================================

def dibujar_agua(pantalla):
    superficie_agua = pygame.Surface((zona_agua.width,zona_agua.height),pygame.SRCALPHA)
    superficie_agua.fill(AZUL_AGUA)
    pantalla.blit(superficie_agua,(zona_agua.x,zona_agua.y))

# ============================================================
# BOTÓN REINICIAR
# ============================================================

def dibujar_boton_reiniciar(pantalla,fuente,btn_rect):
    pygame.draw.rect(pantalla,(180, 40, 40),btn_rect,border_radius=6)
    pygame.draw.rect(pantalla,(255, 255, 255),btn_rect,2,border_radius=6)
    
    texto = fuente.render("Reiniciar (R)",True,(255, 255, 255))
    pantalla.blit(texto,texto.get_rect(center=btn_rect.center))

# ============================================================
# BUCLE PRINCIPAL
# ============================================================

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pantalla_rect = pantalla.get_rect()

    # ========================================================
    # CARGAR FONDO
    # ========================================================

    fondo = None

    if os.path.isfile(RUTA_FONDO):
        try:
            fondo = pygame.image.load(RUTA_FONDO).convert()
            fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))
        except pygame.error:
            fondo = None

    pygame.display.set_caption("Juego con 2 Personajes - Agua")

    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial",14,bold=True)
    btn_reiniciar = pygame.Rect(ANCHO - 130,15,115,32)
    # --------------------------------------------------------
    # CREAR JUGADORES
    # --------------------------------------------------------
    jugador1 = crear_personaje(100,0,COLOR_JUGADOR1)
    jugador2 = crear_personaje(300,0,COLOR_JUGADOR2)
    # --------------------------------------------------------
    # SUELO
    # --------------------------------------------------------
    suelo = pygame.Rect(0,520,ANCHO,80)
    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        # ====================================================
        # EVENTOS
        # ====================================================

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1):
                if btn_reiniciar.collidepoint(evento.pos):
                    reiniciar_juego(jugador1,jugador2)

            if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_r):
                reiniciar_juego(jugador1,jugador2)

        # ====================================================
        # TECLADO
        # ====================================================
        teclas = pygame.key.get_pressed()
        # ====================================================
        # JUGADOR 1
        # Flechas
        # ====================================================
        jugador1["vel_x"] = 0

        if teclas[pygame.K_LEFT]:
            jugador1["vel_x"] = (-jugador1["velocidad_mov"])

        if teclas[pygame.K_RIGHT]:
            jugador1["vel_x"] = (jugador1["velocidad_mov"])

        # Salto solamente fuera del agua
        if (teclas[pygame.K_UP]and jugador1["en_suelo"]and not jugador1["en_agua"]):
            jugador1["vel_y"] = (jugador1["fuerza_salto"])
            jugador1["en_suelo"] = False

        # ====================================================
        # JUGADOR 2
        # WASD
        # ====================================================

        jugador2["vel_x"] = 0

        if teclas[pygame.K_a]:
            jugador2["vel_x"] = (-jugador2["velocidad_mov"])

        if teclas[pygame.K_d]:
            jugador2["vel_x"] = (jugador2["velocidad_mov"])

        # Salto fuera del agua
        if (teclas[pygame.K_w]and jugador2["en_suelo"]and not jugador2["en_agua"]):

            jugador2["vel_y"] = (jugador2["fuerza_salto"])
            jugador2["en_suelo"] = False

        # ====================================================
        # FÍSICA
        # ====================================================

        # Detectar primero si están en agua
        jugador1["en_agua"] = (zona_agua.colliderect(jugador1["hitbox"]))
        jugador2["en_agua"] = (zona_agua.colliderect(jugador2["hitbox"]))
        # ----------------------------------------------------
        # JUGADOR 1
        # ----------------------------------------------------

        resolver_colisiones(
            jugador1,
            jugador2,
            suelo,
            pantalla_rect,
            tecla_arriba=teclas[pygame.K_UP],
            tecla_abajo=teclas[pygame.K_DOWN])

        # ----------------------------------------------------
        # JUGADOR 2
        # ----------------------------------------------------

        resolver_colisiones(
            jugador2,
            jugador1,
            suelo,
            pantalla_rect,
            tecla_arriba=teclas[pygame.K_w],tecla_abajo=teclas[pygame.K_s])

        # ====================================================
        # LIMITAR PERSONAJES A LA PANTALLA
        # ====================================================
        jugador1["hitbox"].clamp_ip(pantalla_rect)
        jugador2["hitbox"].clamp_ip(pantalla_rect)
        # ====================================================
        # DIBUJAR
        # ====================================================
        if fondo is not None:
            pantalla.blit(fondo, (0, 0))
        else:
            pantalla.fill((30, 30, 30))
            pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        dibujar_agua(pantalla)
        dibujar_personaje(pantalla,jugador1)
        dibujar_personaje(pantalla,jugador2)
        # Botón
        dibujar_boton_reiniciar(pantalla,fuente,btn_reiniciar)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ============================================================
# EJECUTAR
# ============================================================
if __name__ == "__main__":
    main()