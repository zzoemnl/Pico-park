import os
import sys
import pygame


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

ANCHO, ALTO = 1500, 800
FPS = 10
GRAVEDAD = 0.8


# Tamaño del personaje
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85


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
        return "caminar-empujar-4"


    # --------------------------------------------------------
    # SI ESTÁ CAMINANDO
    # --------------------------------------------------------

    if p["vel_x"] != 0:

        # Aumentamos el contador
        p["contador_anim"] += 1


        # Cada 8 ciclos cambiamos el frame
        if p["contador_anim"] % 8 == 0:

            p["frame_animacion"] = (
                p["frame_animacion"] % 8
            ) + 1


        return f"caminar-{p['frame_animacion']}"


    # --------------------------------------------------------
    # SI ESTÁ QUIETO
    # --------------------------------------------------------

    return "quieto"


# ============================================================
# FUNCIÓN PARA RESOLVER COLISIONES
# ============================================================

def resolver_colisiones(p1, p2, suelo):
    """
    Maneja:

    - Movimiento horizontal.
    - Movimiento vertical.
    - Gravedad.
    - Colisiones.
    - Subirse encima del otro personaje.
    - Arrastrar al personaje de arriba.
    - Animación de empujar.
    """


    # ========================================================
    # DETECTAR SI P2 ESTÁ ARRIBA DE P1
    # ========================================================

    p2_encima = (

        # Los pies de P2 están cerca de la cabeza de P1
        abs(
            p2["rect"].bottom - p1["rect"].top
        ) <= 3

        # Se superponen horizontalmente
        and p2["rect"].right > p1["rect"].left

        and p2["rect"].left < p1["rect"].right
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

        # P2 se mueve junto con P1
        p2["rect"].x += movimiento_x


    # ========================================================
    # COLISIÓN HORIZONTAL
    # ========================================================

    if (
        not p2_encima
        and p1["rect"].colliderect(p2["rect"])
    ):

        margen_cabeza = 12


        # ----------------------------------------------------
        # SI P1 ESTÁ ENCIMA DE P2
        # ----------------------------------------------------

        if (
            p1["rect"].bottom
            <= p2["rect"].top + margen_cabeza
        ):

            p1["rect"].bottom = p2["rect"].top

            p1["vel_y"] = 0

            p1["en_suelo"] = True


        # ----------------------------------------------------
        # COLISIÓN LATERAL
        # ----------------------------------------------------

        else:

            # ------------------------------------------------
            # P1 CHOCA HACIA LA DERECHA
            # ------------------------------------------------

            if p1["vel_x"] > 0:

                # P1 es quien chocó
                p1["empujando"] = True

                # Guardamos la dirección
                p1["direccion_empuje"] = 1

                # Evitamos que atraviese a P2
                p1["rect"].right = p2["rect"].left


            # ------------------------------------------------
            # P1 CHOCA HACIA LA IZQUIERDA
            # ------------------------------------------------

            elif p1["vel_x"] < 0:

                # P1 es quien chocó
                p1["empujando"] = True

                # Guardamos la dirección
                p1["direccion_empuje"] = -1

                # Evitamos que atraviese a P2
                p1["rect"].left = p2["rect"].right


    # ========================================================
    # GRAVEDAD
    # ========================================================

    p1["vel_y"] += GRAVEDAD


    # ========================================================
    # MOVIMIENTO VERTICAL
    # ========================================================

    p1["rect"].y += int(p1["vel_y"])


    # ========================================================
    # ARRASTRAR VERTICALMENTE AL PERSONAJE DE ARRIBA
    # ========================================================

    if p2_encima:

        movimiento_y = (
            p1["rect"].y - y_anterior
        )

        # Si P1 salta o cae,
        # P2 se mueve con él
        p2["rect"].y += movimiento_y


    # ========================================================
    # COLISIÓN VERTICAL ENTRE PERSONAJES
    # ========================================================

    if (
        not p2_encima
        and p1["rect"].colliderect(p2["rect"])
    ):


        # ----------------------------------------------------
        # P1 CAE ENCIMA DE P2
        # ----------------------------------------------------

        if (

            p1["vel_y"] >= 0

            and p1["rect"].top
            < p2["rect"].top
        ):

            # P1 queda arriba de P2
            p1["rect"].bottom = p2["rect"].top

            # Detenemos la caída
            p1["vel_y"] = 0

            # Ahora está apoyado
            p1["en_suelo"] = True


        # ----------------------------------------------------
        # P1 SALTA DESDE ABAJO
        # ----------------------------------------------------

        elif (

            p1["vel_y"] < 0

            and p1["rect"].bottom
            > p2["rect"].bottom
        ):

            # P1 queda debajo de P2
            p1["rect"].top = p2["rect"].bottom

            # Detenemos el salto
            p1["vel_y"] = 0


    # ========================================================
    # COLISIÓN CON EL SUELO
    # ========================================================

    if p1["rect"].colliderect(suelo):

        if p1["vel_y"] >= 0:

            # Colocamos al personaje sobre el suelo
            p1["rect"].bottom = suelo.top

            # Detenemos la caída
            p1["vel_y"] = 0

            # Está apoyado
            p1["en_suelo"] = True


    # ========================================================
    # COMPROBAR SI SIGUE PEGADO
    # ========================================================

    # Esta parte sirve para que SOLO el personaje
    # que chocó mantenga la animación de empujar.


    # Verificamos si ambos personajes están
    # a la misma altura verticalmente

    superpuestos_verticalmente = (

        p1["rect"].bottom > p2["rect"].top

        and

        p1["rect"].top < p2["rect"].bottom
    )


    # --------------------------------------------------------
    # SI ESTABA EMPUJANDO HACIA LA DERECHA
    # --------------------------------------------------------

    if p1["direccion_empuje"] == 1:

        pegado = (

            # El lado derecho de P1 toca
            # el lado izquierdo de P2

            abs(
                p1["rect"].right
                - p2["rect"].left
            ) <= 2

            and

            superpuestos_verticalmente
        )


    # --------------------------------------------------------
    # SI ESTABA EMPUJANDO HACIA LA IZQUIERDA
    # --------------------------------------------------------

    elif p1["direccion_empuje"] == -1:

        pegado = (

            # El lado izquierdo de P1 toca
            # el lado derecho de P2

            abs(
                p1["rect"].left
                - p2["rect"].right
            ) <= 2

            and

            superpuestos_verticalmente
        )


    # --------------------------------------------------------
    # SI NUNCA ESTUVO EMPUJANDO
    # --------------------------------------------------------

    else:

        pegado = False


    # ========================================================
    # SI YA NO ESTÁ PEGADO
    # ========================================================

    if not pegado:

        # Deja de hacer la animación
        p1["empujando"] = False

        # Reiniciamos la dirección
        p1["direccion_empuje"] = 0


# ============================================================
# FUNCIÓN PARA DIBUJAR EL PERSONAJE
# ============================================================

def dibujar_personaje(pantalla, p):
    """
    Dibuja el personaje usando el sprite correspondiente.
    """

    # Obtenemos el estado
    estado = obtener_estado(p)


    # Obtenemos el sprite
    sprite = p["sprites"].get(
        estado,
        p["sprites"]["quieto"]
    )


    # ========================================================
    # DIRECCIÓN DEL PERSONAJE
    # ========================================================

    if p["vel_x"] > 0:

        p["mirando_derecha"] = True


    elif p["vel_x"] < 0:

        p["mirando_derecha"] = False


    # ========================================================
    # VOLTEAR EL SPRITE
    # ========================================================

    if not p["mirando_derecha"]:

        sprite = pygame.transform.flip(
            sprite,
            True,
            False
        )


    # ========================================================
    # DIBUJAR
    # ========================================================

    pantalla.blit(
        sprite,
        p["rect"]
    )


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():

    # ========================================================
    # INICIAR PYGAME
    # ========================================================

    pygame.init()


    # Creamos la ventana
    pantalla = pygame.display.set_mode(
        (ANCHO, ALTO)
    )


    # Título de la ventana
    pygame.display.set_caption(
        "Juego con 2 Personajes - Subir Encima"
    )


    # Control de FPS
    reloj = pygame.time.Clock()


    # ========================================================
    # CREAR PERSONAJES
    # ========================================================

    jugador1 = crear_personaje(
        100,
        300,
        "Amarillo"
    )


    jugador2 = crear_personaje(
        300,
        300,
        "Amarillo"
    )


    # ========================================================
    # CREAR EL SUELO
    # ========================================================

    suelo = pygame.Rect(
        0,
        520,
        ANCHO,
        80
    )


    # ========================================================
    # BUCLE PRINCIPAL
    # ========================================================

    ejecutando = True


    while ejecutando:


        # ----------------------------------------------------
        # CONTROLAR LOS FPS
        # ----------------------------------------------------

        reloj.tick(FPS)


        # ----------------------------------------------------
        # DETECTAR EVENTOS
        # ----------------------------------------------------

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                ejecutando = False


        # ----------------------------------------------------
        # DETECTAR TECLAS
        # ----------------------------------------------------

        teclas = pygame.key.get_pressed()


        # ====================================================
        # CONTROLES DEL JUGADOR 1
        # ====================================================

        jugador1["vel_x"] = 0


        # Mover hacia la izquierda
        if teclas[pygame.K_LEFT]:

            jugador1["vel_x"] = (
                -jugador1["velocidad_mov"]
            )


        # Mover hacia la derecha
        if teclas[pygame.K_RIGHT]:

            jugador1["vel_x"] = (
                jugador1["velocidad_mov"]
            )


        # Saltar
        if (

            teclas[pygame.K_UP]

            and jugador1["en_suelo"]
        ):

            jugador1["vel_y"] = (
                jugador1["fuerza_salto"]
            )

            jugador1["en_suelo"] = False


        # ====================================================
        # CONTROLES DEL JUGADOR 2
        # ====================================================

        jugador2["vel_x"] = 0


        # Mover hacia la izquierda
        if teclas[pygame.K_a]:

            jugador2["vel_x"] = (
                -jugador2["velocidad_mov"]
            )


        # Mover hacia la derecha
        if teclas[pygame.K_d]:

            jugador2["vel_x"] = (
                jugador2["velocidad_mov"]
            )


        # Saltar
        if (

            teclas[pygame.K_w]

            and jugador2["en_suelo"]
        ):

            jugador2["vel_y"] = (
                jugador2["fuerza_salto"]
            )

            jugador2["en_suelo"] = False


        # ====================================================
        # ACTUALIZAR COLISIONES
        # ====================================================

        resolver_colisiones(
            jugador1,
            jugador2,
            suelo
        )


        resolver_colisiones(
            jugador2,
            jugador1,
            suelo
        )


        # ====================================================
        # LIMITAR A LOS BORDES DE LA PANTALLA
        # ====================================================

        jugador1["rect"].clamp_ip(
            pantalla.get_rect()
        )

        jugador2["rect"].clamp_ip(
            pantalla.get_rect()
        )


        # ====================================================
        # DIBUJAR EL FONDO
        # ====================================================

        pantalla.fill(
            (30, 30, 30)
        )


        # ====================================================
        # DIBUJAR EL SUELO
        # ====================================================

        pygame.draw.rect(
            pantalla,
            (100, 100, 100),
            suelo
        )


        # ====================================================
        # DIBUJAR LOS PERSONAJES
        # ====================================================

        dibujar_personaje(
            pantalla,
            jugador1
        )

        dibujar_personaje(
            pantalla,
            jugador2
        )


        # ====================================================
        # ACTUALIZAR LA PANTALLA
        # ====================================================

        pygame.display.flip()


    # ========================================================
    # CERRAR EL JUEGO
    # ========================================================

    pygame.quit()

    sys.exit()


# ============================================================
# EJECUTAR EL PROGRAMA
# ============================================================

if __name__ == "__main__":

    main()