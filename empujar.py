import os
import sys
import pygame


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

ANCHO, ALTO = 800, 600
FPS = 60
GRAVEDAD = 0.8


# Tamaño del personaje
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

# Tamaño de la caja
TAMANO_CAJA = 60


# Ruta de las carpetas de personajes
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "Personajes")


# ============================================================
# FUNCIÓN PARA CARGAR LOS SPRITES
# ============================================================

def cargar_sprites(nombre_color):
    """
    Carga todos los sprites de un personaje.
    """

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

    # --------------------------------------------------------
    # IMÁGENES DE RESPALDO
    # --------------------------------------------------------

    for estado in estados:

        img_temp = pygame.Surface(
            (ANCHO_PERSONAJE, ALTO_PERSONAJE)
        )

        img_temp.fill((50, 120, 240))

        sprites[estado] = img_temp


    # --------------------------------------------------------
    # CARGAR LAS IMÁGENES REALES
    # --------------------------------------------------------

    if os.path.exists(ruta_carpeta):

        for estado in estados:

            for ext in [".png", ".PNG", ".jpg", ".JPG"]:

                ruta_archivo = os.path.join(
                    ruta_carpeta,
                    f"{estado}{ext}"
                )

                if os.path.isfile(ruta_archivo):

                    try:

                        img = pygame.image.load(
                            ruta_archivo
                        ).convert_alpha()

                        sprites[estado] = pygame.transform.scale(
                            img,
                            (
                                ANCHO_PERSONAJE,
                                ALTO_PERSONAJE
                            )
                        )

                        break

                    except pygame.error:
                        pass


    return sprites


# ============================================================
# FUNCIÓN PARA CREAR UN PERSONAJE
# ============================================================

def crear_personaje(x, y, color_carpeta):
    """
    Crea un personaje con todas sus propiedades.
    """

    return {

        # Posición inicial guardada para reiniciar
        "x_inicial": x,
        "y_inicial": y,

        # Posición y tamaño
        "rect": pygame.Rect(
            x,
            y,
            ANCHO_PERSONAJE,
            ALTO_PERSONAJE
        ),

        # Velocidad horizontal
        "vel_x": 0,

        # Velocidad vertical
        "vel_y": 0,

        # Velocidad de movimiento
        "velocidad_mov": 5,

        # Fuerza del salto
        "fuerza_salto": -15,

        # Indica si está apoyado
        "en_suelo": False,

        # Sprites
        "sprites": cargar_sprites(color_carpeta),

        # Dirección
        "mirando_derecha": True,

        # Animación de caminar
        "frame_animacion": 1,
        "contador_anim": 0,

        # ----------------------------------------------------
        # VARIABLES PARA LA ANIMACIÓN DE EMPUJAR
        # ----------------------------------------------------

        # Indica si este personaje es el que chocó
        "empujando": False,

        # 1 = está empujando hacia la derecha
        # -1 = está empujando hacia la izquierda
        # 0 = no está empujando
        "direccion_empuje": 0,
    }


# ============================================================
# FUNCIÓN PARA CREAR LA CAJA
# ============================================================

def crear_caja(x, y):
    return {
        "x_inicial": x,
        "y_inicial": y,
        "rect": pygame.Rect(x, y, TAMANO_CAJA, TAMANO_CAJA),
        "vel_y": 0,
        "en_suelo": False
    }


# ============================================================
# FUNCIÓN PARA REINICIAR POSICIONES
# ============================================================

def reiniciar_juego(p1, p2, caja):
    p1["rect"].x = p1["x_inicial"]
    p1["rect"].y = p1["y_inicial"]
    p1["vel_x"] = 0
    p1["vel_y"] = 0
    p1["en_suelo"] = False
    p1["empujando"] = False

    p2["rect"].x = p2["x_inicial"]
    p2["rect"].y = p2["y_inicial"]
    p2["vel_x"] = 0
    p2["vel_y"] = 0
    p2["en_suelo"] = False
    p2["empujando"] = False

    caja["rect"].x = caja["x_inicial"]
    caja["rect"].y = caja["y_inicial"]
    caja["vel_y"] = 0


# ============================================================
# FUNCIÓN PARA OBTENER EL ESTADO DEL PERSONAJE
# ============================================================

def obtener_estado(p):
    """
    Determina qué sprite debe mostrar el personaje.
    """

    # --------------------------------------------------------
    # SI ESTÁ EN EL AIRE
    # --------------------------------------------------------

    if not p["en_suelo"]:
        return "saltar"


    # --------------------------------------------------------
    # SI ESTÁ EMPUJANDO
    # --------------------------------------------------------

    # Solo el personaje que chocó tendrá esta variable en True
    if p["empujando"]:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] = (p["frame_animacion"] % 3) + 1
        return f"caminar-empujar-{p['frame_animacion']}"


    # --------------------------------------------------------
    # SI ESTÁ CAMINANDO
    # --------------------------------------------------------

    if p["vel_x"] != 0:

        # Aumentamos el contador
        p["contador_anim"] += 1


        # Cada 8 ciclos cambiamos el frame
        if p["contador_anim"] % 8 == 0:

            p["frame_animacion"] = (
                p["frame_animacion"] % 3
            ) + 1


        return f"caminar-{p['frame_animacion']}"


    # --------------------------------------------------------
    # SI ESTÁ QUIETO
    # --------------------------------------------------------

    return "quieto"


# ============================================================
# FÍSICA Y COLISIONES CORREGIDAS
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
    """
    Maneja el movimiento, la gravedad y las colisiones sin permitir
    que los personajes se queden flotando fuera de los bordes.
    """

    # ========================================================
    # DETECTAR SI P2 ESTÁ ARRIBA DE P1 (LÍMITES ESTRICTOS)
    # ========================================================

    # Exigimos que haya un traslape horizontal real (más estricto que solo rozar el borde)
    p2_encima = (
        abs(p2["rect"].bottom - p1["rect"].top) <= 4
        and p2["rect"].right > p1["rect"].left + 15
        and p2["rect"].left < p1["rect"].right - 15
    )


    # ========================================================
    # GUARDAR POSICIÓN ANTERIOR
    # ========================================================

    x_anterior = p1["rect"].x
    y_anterior = p1["rect"].y


    # ========================================================
    # MOVIMIENTO HORIZONTAL
    # ========================================================

    p1["rect"].x += p1["vel_x"]


    # ========================================================
    # ARRASTRAR AL PERSONAJE DE ARRIBA
    # ========================================================

    if p2_encima:

        movimiento_x = (
            p1["rect"].x - x_anterior
        )

        p2["rect"].x += movimiento_x


    # ========================================================
    # COLISIÓN HORIZONTAL CON LA CAJA
    # ========================================================

    if p1["rect"].colliderect(caja["rect"]):
        if p1["rect"].bottom > caja["rect"].top + 10:
            if p1["vel_x"] > 0:
                rect_prueba_caja = caja["rect"].copy()
                rect_prueba_caja.left = p1["rect"].right

                bloqueado_pantalla = rect_prueba_caja.right > pantalla_rect.right
                bloqueado_p2 = rect_prueba_caja.colliderect(p2["rect"])

                if bloqueado_pantalla or bloqueado_p2:
                    p1["rect"].right = caja["rect"].left
                else:
                    caja["rect"].left = p1["rect"].right
                    p1["empujando"] = True
                    p1["direccion_empuje"] = 1

            elif p1["vel_x"] < 0:
                rect_prueba_caja = caja["rect"].copy()
                rect_prueba_caja.right = p1["rect"].left

                bloqueado_pantalla = rect_prueba_caja.left < pantalla_rect.left
                bloqueado_p2 = rect_prueba_caja.colliderect(p2["rect"])

                if bloqueado_pantalla or bloqueado_p2:
                    p1["rect"].left = caja["rect"].right
                else:
                    caja["rect"].right = p1["rect"].left
                    p1["empujando"] = True
                    p1["direccion_empuje"] = -1


    # ========================================================
    # COLISIÓN HORIZONTAL ENTRE JUGADORES
    # ========================================================

    if not p2_encima and p1["rect"].colliderect(p2["rect"]):

        margen_cabeza = 12

        if p1["rect"].bottom <= p2["rect"].top + margen_cabeza:
            p1["rect"].bottom = p2["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

        else:
            if p1["vel_x"] > 0:
                p1["empujando"] = True
                p1["direccion_empuje"] = 1
                p1["rect"].right = p2["rect"].left

            elif p1["vel_x"] < 0:
                p1["empujando"] = True
                p1["direccion_empuje"] = -1
                p1["rect"].left = p2["rect"].right


    # ========================================================
    # GRAVEDAD Y MOVIMIENTO VERTICAL
    # ========================================================

    p1["vel_y"] += GRAVEDAD
    p1["rect"].y += int(p1["vel_y"])


    # ========================================================
    # ARRASTRAR VERTICALMENTE AL PERSONAJE DE ARRIBA
    # ========================================================

    if p2_encima:
        movimiento_y = p1["rect"].y - y_anterior
        p2["rect"].y += movimiento_y


    # ========================================================
    # COLISIÓN VERTICAL CON LA CAJA
    # ========================================================

    if p1["rect"].colliderect(caja["rect"]):
        if p1["vel_y"] >= 0 and p1["rect"].bottom - p1["vel_y"] <= caja["rect"].top + 12:
            p1["rect"].bottom = caja["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True
        elif p1["vel_y"] < 0 and p1["rect"].top < caja["rect"].bottom:
            p1["rect"].top = caja["rect"].bottom
            p1["vel_y"] = 0


    # ========================================================
    # COLISIÓN VERTICAL ENTRE PERSONAJES (CORREGIDA)
    # ========================================================

    if not p2_encima and p1["rect"].colliderect(p2["rect"]):

        # Solo permite apoyarse si el personaje p1 se superpone horizontalmente de manera suficiente sobre p2
        superposicion_suficiente = (
            p1["rect"].right > p2["rect"].left + 15
            and p1["rect"].left < p2["rect"].right - 15
        )

        if p1["vel_y"] >= 0 and p1["rect"].top < p2["rect"].top and superposicion_suficiente:
            p1["rect"].bottom = p2["rect"].top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

        elif p1["vel_y"] < 0 and p1["rect"].bottom > p2["rect"].bottom:
            p1["rect"].top = p2["rect"].bottom
            p1["vel_y"] = 0


    # ========================================================
    # COLISIÓN CON EL SUELO
    # ========================================================

    if p1["rect"].colliderect(suelo):
        if p1["vel_y"] >= 0:
            p1["rect"].bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True


    # ========================================================
    # COMPROBAR SI SIGUE PEGADO PARA ANIMACIÓN
    # ========================================================

    superpuestos_verticalmente = (
        p1["rect"].bottom > p2["rect"].top
        and p1["rect"].top < p2["rect"].bottom
    )

    toca_caja_vert = (
        p1["rect"].bottom > caja["rect"].top
        and p1["rect"].top < caja["rect"].bottom
    )

    if p1["direccion_empuje"] == 1:
        pegado_p2 = (abs(p1["rect"].right - p2["rect"].left) <= 2 and superpuestos_verticalmente)
        pegado_caja = (abs(p1["rect"].right - caja["rect"].left) <= 2 and toca_caja_vert)
        pegado = pegado_p2 or pegado_caja

    elif p1["direccion_empuje"] == -1:
        pegado_p2 = (abs(p1["rect"].left - p2["rect"].right) <= 2 and superpuestos_verticalmente)
        pegado_caja = (abs(p1["rect"].left - caja["rect"].right) <= 2 and toca_caja_vert)
        pegado = pegado_p2 or pegado_caja

    else:
        pegado = False

    if not pegado:
        p1["empujando"] = False
        p1["direccion_empuje"] = 0


# ============================================================
# FUNCIÓN PARA DIBUJAR EL PERSONAJE
# ============================================================

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


def dibujar_boton_reiniciar(pantalla, fuente, btn_rect):
    pygame.draw.rect(pantalla, (180, 40, 40), btn_rect, border_radius=6)
    pygame.draw.rect(pantalla, (255, 255, 255), btn_rect, 2, border_radius=6)
    texto = fuente.render("Reiniciar (R)", True, (255, 255, 255))
    texto_rect = texto.get_rect(center=btn_rect.center)
    pantalla.blit(texto, texto_rect)


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pantalla_rect = pantalla.get_rect()
    pygame.display.set_caption("Juego con 2 Personajes - Subir Encima")

    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial", 14, bold=True)

    btn_reiniciar = pygame.Rect(ANCHO - 130, 15, 115, 32)

    # Personajes iniciales arriba (Y = 0)
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

        # CONTROLES JUGADOR 1
        jugador1["vel_x"] = 0
        if teclas[pygame.K_LEFT]:
            jugador1["vel_x"] = -jugador1["velocidad_mov"]
        if teclas[pygame.K_RIGHT]:
            jugador1["vel_x"] = jugador1["velocidad_mov"]
        if teclas[pygame.K_UP] and jugador1["en_suelo"]:
            jugador1["vel_y"] = jugador1["fuerza_salto"]
            jugador1["en_suelo"] = False

        # CONTROLES JUGADOR 2
        jugador2["vel_x"] = 0
        if teclas[pygame.K_a]:
            jugador2["vel_x"] = -jugador2["velocidad_mov"]
        if teclas[pygame.K_d]:
            jugador2["vel_x"] = jugador2["velocidad_mov"]
        if teclas[pygame.K_w] and jugador2["en_suelo"]:
            jugador2["vel_y"] = jugador2["fuerza_salto"]
            jugador2["en_suelo"] = False

        # ACTUALIZAR FÍSICA
        actualizar_caja(caja, suelo, pantalla_rect)

        resolver_colisiones(jugador1, jugador2, caja, suelo, pantalla_rect)
        resolver_colisiones(jugador2, jugador1, caja, suelo, pantalla_rect)

        jugador1["rect"].clamp_ip(pantalla_rect)
        jugador2["rect"].clamp_ip(pantalla_rect)

        # RENDERIZAR
        pantalla.fill((30, 30, 30))
        pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        # Caja
        pygame.draw.rect(pantalla, (139, 69, 19), caja["rect"])
        pygame.draw.rect(pantalla, (100, 40, 10), caja["rect"], 3)

        # Personajes
        dibujar_personaje(pantalla, jugador1)
        dibujar_personaje(pantalla, jugador2)

        # Botón
        dibujar_boton_reiniciar(pantalla, fuente, btn_reiniciar)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()