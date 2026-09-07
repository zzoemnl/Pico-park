# Importamos las librerías necesarias
import os          # Permite trabajar con carpetas y rutas de archivos
import sys         # Permite cerrar el programa correctamente
import pygame      


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

# Tamaño de la ventana del juego
ANCHO, ALTO = 800, 600

# Cantidad de fotogramas por segundo
FPS = 60

# Fuerza de gravedad que afecta a los personajes
GRAVEDAD = 0.8

# Tamaño de los personajes
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

# Obtenemos la carpeta donde se encuentra este archivo de Python
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))

# Creamos la ruta de la carpeta donde están los personajes
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "Personajes")


# ============================================================
# FUNCIÓN: cargar_sprites()
# ============================================================

def cargar_sprites(nombre_color):
    # Creamos la ruta completa de la carpeta del personaje
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
    # CARGAR LAS IMÁGENES REALES
    # --------------------------------------------------------

    # Verificamos si la carpeta del personaje existe
    if os.path.exists(ruta_carpeta):

        # Recorremos todos los estados del personaje
        for estado in estados:

            # Probamos diferentes extensiones de imagen
            for ext in [".png", ".PNG", ".jpg", ".JPG"]:

                # Creamos la ruta completa del archivo
                ruta_archivo = os.path.join(
                    ruta_carpeta,
                    f"{estado}{ext}"
                )

                # Verificamos si el archivo existe
                if os.path.isfile(ruta_archivo):
                    try:
                        # Cargamos la imagen
                        img = pygame.image.load(
                            ruta_archivo
                        ).convert_alpha()

                        # Cambiamos el tamaño de la imagen
                        sprites[estado] = pygame.transform.scale(
                            img,
                            (ANCHO_PERSONAJE, ALTO_PERSONAJE)
                        )

                        # Salimos del ciclo porque ya encontramos la imagen correspondiente
                        break

                    except pygame.error:
                        pass


    # Devolvemos todas las imágenes cargadas
    return sprites

# ============================================================
# FUNCIÓN: crear_personaje()
# ============================================================

def crear_personaje(x, y, color_carpeta):
       return {
        # Rectángulo que representa la posición y tamaño
        # del personaje
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

        # Velocidad con la que se mueve horizontalmente
        "velocidad_mov": 5,

        # Fuerza inicial del salto
        # Es negativa porque en Pygame subir significa
        # disminuir la coordenada Y
        "fuerza_salto": -15,

        # Indica si el personaje está tocando el suelo
        "en_suelo": False,

        # Cargamos todos los sprites del personaje
        "sprites": cargar_sprites(color_carpeta),

        # Indica hacia qué dirección está mirando
        "mirando_derecha": True,

        # Número del frame de la animación de caminar
        "frame_animacion": 1,

        # Contador utilizado para controlar la velocidad
        # de la animación
        "contador_anim": 0,
        "empujando": False,
    }


# ============================================================
# FUNCIÓN: obtener_estado()
# ============================================================

def obtener_estado(p):

    # Si está en el aire
    if not p["en_suelo"]:
        return "saltar"

    # Si está caminando
    if p["vel_x"] != 0:

        # Si está chocando contra el otro personaje
        if p["empujando"]:
            return "caminar-empujar-2"

        # Animación normal de caminar
        p["contador_anim"] += 1

        # Cada 8 ciclos cambia el sprite
        if p["contador_anim"] >= 8:

            p["contador_anim"] = 0

            # Cambia entre 1, 2 y 3
            p["frame_animacion"] += 1

            if p["frame_animacion"] > 3:
                p["frame_animacion"] = 1

        return f"caminar-{p['frame_animacion']}"

    # Si no se mueve
    return "quieto"

# ============================================================
# FUNCIÓN: resolver_colisiones()
# ============================================================

def resolver_colisiones(p1, p2, suelo):
    """
    Actualiza el movimiento y las colisiones de un personaje.

    Recibe:
        p1 -> personaje que estamos actualizando.
        p2 -> el otro personaje.
        suelo -> rectángulo que representa el suelo.

    Esta función:
        - mueve al personaje horizontalmente.
        - aplica gravedad.
        - mueve al personaje verticalmente.
        - detecta colisiones con el otro personaje.
        - permite subirse encima del otro personaje.
        - permite que el personaje de abajo pueda saltar.
        - hace que el personaje de abajo arrastre al de arriba.
        - detecta la colisión con el suelo.
    """
    # Por defecto, el personaje no está empujando
    p1["empujando"] = False
    p2_encima = (
        # Los pies de p2 están cerca de la parte superior de p1
        abs(
            p2["rect"].bottom - p1["rect"].top
        ) <= 3

        # p2 toca horizontalmente a p1
        and p2["rect"].right > p1["rect"].left

        # p2 también se superpone desde el otro lado
        and p2["rect"].left < p1["rect"].right
    )


    # ========================================================
    # GUARDAR LA POSICIÓN ANTERIOR
    # ========================================================

    # Guardamos la posición anterior de p1.
    # Esto sirve para saber cuánto se movió.
    # Después podemos usar ese movimiento para arrastrar
    # al personaje que está arriba.

    x_anterior = p1["rect"].x
    y_anterior = p1["rect"].y


    # ========================================================
    # 1. MOVIMIENTO HORIZONTAL
    # ========================================================

    # Movemos al personaje horizontalmente
    # según su velocidad.
    p1["rect"].x += p1["vel_x"]


    # --------------------------------------------------------
    # ARRASTRAR AL PERSONAJE QUE ESTÁ ARRIBA
    # --------------------------------------------------------

    if p2_encima:

        # Calculamos cuánto se movió p1 horizontalmente
        movimiento_x = (
            p1["rect"].x - x_anterior
        )

        # Movemos a p2 exactamente la misma distancia.
        #
        # De esta manera, si p1 se mueve y p2 está arriba,
        # p2 es "arrastrado".
        p2["rect"].x += movimiento_x


    # --------------------------------------------------------
    # COLISIÓN HORIZONTAL ENTRE PERSONAJES
    # --------------------------------------------------------

    # Solo hacemos la colisión normal si p2 NO está arriba.
    #
    # Esto es importante porque, si p2 está arriba,
    # no queremos que p1 considere a p2 como un obstáculo.

    if (
        not p2_encima
        and p1["rect"].colliderect(p2["rect"])
    ):

        # Margen utilizado para detectar si un personaje
        # está casi encima del otro.
        margen_cabeza = 12


        # Si p1 está prácticamente encima de p2
        if (
            p1["rect"].bottom
            <= p2["rect"].top + margen_cabeza
        ):

            # Colocamos los pies de p1 sobre la cabeza de p2
            p1["rect"].bottom = p2["rect"].top

            # Detenemos la caída
            p1["vel_y"] = 0

            # Indicamos que p1 está apoyado
            p1["en_suelo"] = True


        # Si no está encima, es una colisión lateral
        else:

            # Si p1 se mueve hacia la derecha
            if p1["vel_x"] > 0:

                # Colocamos el borde derecho de p1
                # contra el borde izquierdo de p2
                p1["rect"].right = p2["rect"].left


            # Si p1 se mueve hacia la izquierda
            elif p1["vel_x"] < 0:

                # Colocamos el borde izquierdo de p1
                # contra el borde derecho de p2
                p1["rect"].left = p2["rect"].right


    # ========================================================
    # 2. MOVIMIENTO VERTICAL Y GRAVEDAD
    # ========================================================

    # Aplicamos gravedad.
    #
    # En cada ciclo, la velocidad vertical aumenta,
    # haciendo que el personaje caiga.
    p1["vel_y"] += GRAVEDAD


    # Movemos al personaje verticalmente.
    #
    # Usamos int() porque la posición del Rect trabaja
    # con números enteros.
    p1["rect"].y += int(p1["vel_y"])


    # --------------------------------------------------------
    # ARRASTRAR VERTICALMENTE AL PERSONAJE DE ARRIBA
    # --------------------------------------------------------

    if p2_encima:

        # Calculamos cuánto se movió p1 verticalmente
        movimiento_y = (
            p1["rect"].y - y_anterior
        )

        # Movemos a p2 la misma cantidad.
        #
        # Esto permite que, si p1 salta teniendo
        # a p2 encima, p2 suba con él.
        p2["rect"].y += movimiento_y


    # ========================================================
    # COLISIÓN VERTICAL ENTRE LOS PERSONAJES
    # ========================================================

    # Si p2 está arriba de p1, NO hacemos una colisión
    # que bloquee a p1.
    #
    # Gracias a esto, el personaje de abajo puede saltar.

    if (
        not p2_encima
        and p1["rect"].colliderect(p2["rect"])
    ):


        # ----------------------------------------------------
        # P1 CAE ENCIMA DE P2
        # ----------------------------------------------------

        # Si p1 está cayendo y viene desde arriba
        if (
            p1["vel_y"] >= 0
            and p1["rect"].top < p2["rect"].top
        ):

            # Colocamos los pies de p1 sobre p2
            p1["rect"].bottom = p2["rect"].top

            # Detenemos la velocidad vertical
            p1["vel_y"] = 0

            # Indicamos que p1 está apoyado
            p1["en_suelo"] = True


        # ----------------------------------------------------
        # P1 SALTA DESDE ABAJO Y GOLPEA A P2
        # ----------------------------------------------------

        elif (
            p1["vel_y"] < 0
            and p1["rect"].bottom > p2["rect"].bottom
        ):

            # Colocamos a p1 debajo de p2
            p1["rect"].top = p2["rect"].bottom

            # Detenemos el salto
            p1["vel_y"] = 0


    # ========================================================
    # 3. COLISIÓN CON EL SUELO
    # ========================================================

    # Verificamos si p1 está chocando con el suelo
    if p1["rect"].colliderect(suelo):

        # Solo hacemos esta corrección si el personaje
        # está cayendo.
        if p1["vel_y"] >= 0:

            # Colocamos al personaje exactamente
            # encima del suelo.
            p1["rect"].bottom = suelo.top

            # Detenemos la caída
            p1["vel_y"] = 0

            # Indicamos que está apoyado
            p1["en_suelo"] = True


# ============================================================
# FUNCIÓN: dibujar_personaje()
# ============================================================

def dibujar_personaje(pantalla, p):
    """
    Dibuja el personaje en la pantalla.

    Recibe:
        pantalla -> superficie donde se dibuja el juego.
        p -> personaje que queremos dibujar.

    Esta función:
        - obtiene el estado actual del personaje.
        - selecciona el sprite correcto.
        - cambia la dirección del personaje.
        - dibuja el sprite en pantalla.
    """


    # Obtenemos el estado actual:
    # quieto, caminar o saltar.
    estado = obtener_estado(p)


    # Obtenemos el sprite correspondiente.
    #
    # Si no existe, usamos el sprite "quieto".
    sprite = p["sprites"].get(
        estado,
        p["sprites"]["quieto"]
    )


    # --------------------------------------------------------
    # DIRECCIÓN DEL PERSONAJE
    # --------------------------------------------------------

    # Si se mueve hacia la derecha
    if p["vel_x"] > 0:

        # Ahora está mirando hacia la derecha
        p["mirando_derecha"] = True


    # Si se mueve hacia la izquierda
    elif p["vel_x"] < 0:

        # Ahora está mirando hacia la izquierda
        p["mirando_derecha"] = False


    # --------------------------------------------------------
    # VOLTEAR EL SPRITE
    # --------------------------------------------------------

    # Si está mirando hacia la izquierda,
    # volteamos horizontalmente la imagen.
    if not p["mirando_derecha"]:

        sprite = pygame.transform.flip(
            sprite,
            True,   # Voltear horizontalmente
            False   # No voltear verticalmente
        )


    # Dibujamos el sprite en la posición del personaje
    pantalla.blit(
        sprite,
        p["rect"]
    )


# ============================================================
# FUNCIÓN PRINCIPAL: main()
# ============================================================

def main():
    """
    Función principal del juego.

    Aquí se:
        - inicia Pygame.
        - crea la ventana.
        - crean los personajes.
        - crea el suelo.
        - detectan las teclas.
        - actualiza la física.
        - dibuja todo en pantalla.
        - mantiene el juego funcionando.
    """


    # ========================================================
    # INICIAR PYGAME
    # ========================================================

    pygame.init()


    # Creamos la ventana del juego
    pantalla = pygame.display.set_mode(
        (ANCHO, ALTO)
    )


    # Cambiamos el título de la ventana
    pygame.display.set_caption(
        "Juego con 2 Personajes - Subir Encima"
    )


    # Creamos un reloj para controlar los FPS
    reloj = pygame.time.Clock()

    jugador1 = crear_personaje(100, 300, "Celeste")
    jugador2 = crear_personaje(300, 300, "Violeta")

    # ========================================================
    # CREAR LOS PERSONAJES
    # ========================================================

    # Jugador 1:
    # posición inicial = (100, 300)
    # carpeta de sprites = "Verde oscuro"
    jugador1 = crear_personaje(
        100,
        300,
        "Verde oscuro"
    )


    # Jugador 2:
    # posición inicial = (300, 300)
    # carpeta de sprites = "Azul"
    jugador2 = crear_personaje(
        300,
        300,
        "Azul"
    )


    # ========================================================
    # CREAR EL SUELO
    # ========================================================

    # pygame.Rect(x, y, ancho, alto)
    suelo = pygame.Rect(
        0,
        520,
        ANCHO,
        80
    )


    # Variable que controla si el juego continúa funcionando
    ejecutando = True


    # ========================================================
    # BUCLE PRINCIPAL DEL JUEGO
    # ========================================================

    while ejecutando:


        # ----------------------------------------------------
        # CONTROLAR LOS FPS
        # ----------------------------------------------------

        # Limitamos el juego a 60 FPS
        reloj.tick(FPS)


        # ----------------------------------------------------
        # DETECTAR EVENTOS
        # ----------------------------------------------------

        for evento in pygame.event.get():

            # Si el usuario cierra la ventana
            if evento.type == pygame.QUIT:

                # Terminamos el juego
                ejecutando = False


        # ====================================================
        # DETECTAR LAS TECLAS PRESIONADAS
        # ====================================================

        teclas = pygame.key.get_pressed()


        # ====================================================
        # CONTROLES DEL JUGADOR 1
        # ====================================================

        # Reiniciamos la velocidad horizontal
        jugador1["vel_x"] = 0


        # Flecha izquierda
        if teclas[pygame.K_LEFT]:

            # El personaje se mueve hacia la izquierda
            jugador1["vel_x"] = (
                -jugador1["velocidad_mov"]
            )


        # Flecha derecha
        if teclas[pygame.K_RIGHT]:

            # El personaje se mueve hacia la derecha
            jugador1["vel_x"] = (
                jugador1["velocidad_mov"]
            )


        # Flecha arriba
        if (
            teclas[pygame.K_UP]
            and jugador1["en_suelo"]
        ):

            # Aplicamos la fuerza del salto
            jugador1["vel_y"] = (
                jugador1["fuerza_salto"]
            )

            # Ya no está apoyado
            jugador1["en_suelo"] = False


        # ====================================================
        # CONTROLES DEL JUGADOR 2
        # ====================================================

        # Reiniciamos la velocidad horizontal
        jugador2["vel_x"] = 0


        # Tecla A
        if teclas[pygame.K_a]:

            # Mover hacia la izquierda
            jugador2["vel_x"] = (
                -jugador2["velocidad_mov"]
            )


        # Tecla D
        if teclas[pygame.K_d]:

            # Mover hacia la derecha
            jugador2["vel_x"] = (
                jugador2["velocidad_mov"]
            )


        # Tecla W
        if (
            teclas[pygame.K_w]
            and jugador2["en_suelo"]
        ):

            # Aplicamos la fuerza del salto
            jugador2["vel_y"] = (
                jugador2["fuerza_salto"]
            )

            # Ya no está apoyado
            jugador2["en_suelo"] = False


        # ====================================================
        # ACTUALIZAR FÍSICA Y COLISIONES
        # ====================================================

        # Actualizamos al jugador 1.
        #
        # Se mueve, recibe gravedad y detecta colisiones.
        resolver_colisiones(
            jugador1,
            jugador2,
            suelo
        )

        # Actualizamos al jugador 2.
        resolver_colisiones(
            jugador2,
            jugador1,
            suelo
        )

        # ====================================================
        # LIMITAR LOS PERSONAJES A LA PANTALLA
        # ====================================================

        # Evita que el jugador 1 salga de la pantalla
        jugador1["rect"].clamp_ip(
            pantalla.get_rect()
        )

        # Evita que el jugador 2 salga de la pantalla
        jugador2["rect"].clamp_ip(
            pantalla.get_rect()
        )


        # ====================================================
        # RENDERIZADO
        # ====================================================
        # Pintamos el fondo de color oscuro
        pantalla.fill(
            (30, 30, 30)
        )
        # Dibujamos el suelo
        pygame.draw.rect(
            pantalla,
            (100, 100, 100),
            suelo
        )
        # Dibujamos el jugador 1
        dibujar_personaje(
            pantalla,
            jugador1
        )
        # Dibujamos el jugador 2
        dibujar_personaje(
            pantalla,
            jugador2
        )
        # Actualizamos la pantalla
        pygame.display.flip()

    # ========================================================
    # CERRAR EL JUEGO
    # ========================================================

    # Cerramos Pygame
    pygame.quit()

    # Cerramos completamente el programa
    sys.exit()

# ============================================================
# EJECUTAR EL PROGRAMA
# ============================================================

# Esta condición verifica si este archivo se está ejecutando
# directamente.
if __name__ == "__main__":

    # Ejecutamos la función principal
    main()

