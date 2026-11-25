"""
Definición de los 15 niveles del juego, una función por nivel.

Cada función recibe los colores de los jugadores (y la lista compartida de bloques
peligrosos) y devuelve un diccionario con las variables del nivel: suelo, plataformas,
jugadores, llave, puerta, mecánicas, etc. iniciar_mundo (pantalla.py) toma de ese
diccionario lo que necesita; las variables que un nivel no define conservan su valor
por defecto. El cuerpo de cada función es el bloque original de pantalla.py, sin cambios.

Para agregar un nivel: escribir nivel_M_N(...) con el mismo patrón y registrarlo en NIVELES.
"""
import pygame

from pantalla import (
    ALTO,
    ALTO_HITBOX,
    TAMANO_CAJA,
    ZONA_AGUA,
    crear_bloque_con_pinchos,
    crear_caja,
    crear_llave,
    crear_personaje,
    crear_pincho,
    crear_puerta,
    crear_sistema_burbujas_m3,
    generar_laberinto_coral_m3_n2,
    generar_laberinto_oscuro_m3_n4,
    obtener_superficies_luz_linterna,
)


def nivel_1_1(p1_color, p2_color, bloques_peligrosos):
    # Nivel 1: Tutorial horizontal, corto, sencillo y progresivo
    ancho_mundo_nivel = 2100
    usar_caja = False
    usar_soga = False
    usar_agua = False
    usar_pinchos = False
    usar_llave = True

    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    # Primera zona: suelo libre para aprender a caminar
    # Ambos personajes aparecen en la parte superior y caen por gravedad
    jugador1 = crear_personaje(120, 0, p1_color)
    jugador2 = crear_personaje(240, 0, p2_color)

    caja = None
    pinchos = []

    # Segunda zona: estructuras verticales altas (columnas/torres) que llegan hasta el suelo
    plataformas = [
        # Estructura 1: columna de 45px de altura hasta el suelo
        pygame.Rect(540, suelo.top - 45, 80, 45),
        # Estructura 2: columna/torre de 70px de altura hasta el suelo
        pygame.Rect(710, suelo.top - 70, 120, 70),
        # Estructura 3: columna de 60px de altura hasta el suelo
        pygame.Rect(890, suelo.top - 60, 110, 60),
        # Estructura 4: torre alta de 95px de altura hasta el suelo
        pygame.Rect(1070, suelo.top - 95, 120, 95),
        # Estructura 5: columna de 60px de altura hasta el suelo donde se ubica la llave accesible
        pygame.Rect(1300, suelo.top - 60, 90, 60),
    ]

    # Tercera zona: llave visible accesible sobre la plataforma
    llave = crear_llave(1332, suelo.top - 60 - 46)
    # Cuarta zona: puerta de salida al final del recorrido
    puerta = crear_puerta(1750, suelo.top - 90)
    return locals()


def nivel_1_2(p1_color, p2_color, bloques_peligrosos):
    # Nivel 1-2: «La torre humana»
    # Escenario con suelo continuo en la parte inferior y una plataforma elevada flotante en la zona central.
    # - Suelo continuo: no hay paredes ni obstáculos que bloqueen el paso por debajo.
    # - Plataforma flotante central: fija en el aire (top = suelo.top - 160 = 480, espesor 35px).
    #   Deja 125px de espacio libre hasta el suelo (más que los 85px de altura de los personajes).
    #   Inalcanzable con un salto individual normal desde el suelo (altura máx ~138px < 160px).
    #   Alcanzable formando una torre humana (el personaje superior salta desde la cabeza de su compañero).
    # - Llave: ubicada sobre la parte superior de la plataforma flotante (x=995, y=suelo.top - 160 - 46).
    # - Zona posterior y salida: el personaje con la llave baja saltando o cayendo al suelo continuo;
    #   ambos avanzan libremente hacia la puerta de salida al final del recorrido (x=1750).
    ancho_mundo_nivel = 2100
    usar_caja = False
    usar_soga = False
    usar_agua = False
    usar_pinchos = False
    usar_llave = True

    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    # 1. Zona inicial: ambos personajes inician arriba a la izquierda y caen por gravedad
    jugador1 = crear_personaje(140, 0, p1_color)
    jugador2 = crear_personaje(260, 0, p2_color)

    caja = None
    pinchos = []

    # 2. Plataforma elevada flotante en la zona central:
    # Separada del suelo (espacio inferior libre de 125px). Sin paredes ni columnas.
    # Anchura de 320px: suficiente para que el personaje superior aterrice, camine y recoja la llave.
    plataformas = [
        pygame.Rect(850, suelo.top - 160, 320, 35),
    ]

    # 3. Llave sobre la superficie superior de la plataforma flotante
    llave = crear_llave(995, suelo.top - 160 - 46)

    # 4. Puerta de salida al final del recorrido en el suelo firme
    puerta = crear_puerta(1750, suelo.top - 90)
    return locals()


def nivel_1_3(p1_color, p2_color, bloques_peligrosos):
    # Nivel 1-3: «La caja y el botón»
    # Escenario horizontal continuo seguro (sin pinchos ni zonas mortales).
    # - Recorrido directo de izquierda a derecha.
    # - Personajes inician a salvo a la izquierda (x=140, x=240).
    # - Caja empujable física sobre el suelo en x=520.
    # - Botón sobre el suelo en x=840.
    # - Pared vertical sólida en x=1140 que bloquea el camino hacia la llave.
    # - Al mantener la caja sobre el botón, este se presiona y la pared se eleva dejando el paso libre.
    # - Llave al otro lado de la pared en x=1500.
    # - Puerta de salida situada en el extremo derecho del escenario en x=1850.
    ancho_mundo_nivel = 2100
    usar_caja = True
    usar_soga = False
    usar_agua = False
    usar_pinchos = False
    usar_llave = True

    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    # 1. Zona inicial segura a la izquierda (caen desde la parte superior)
    jugador1 = crear_personaje(140, 0, p1_color)
    jugador2 = crear_personaje(240, 0, p2_color)

    # 2. Caja empujable física sobre el suelo
    caja = crear_caja(520, suelo.top - TAMANO_CAJA)
    pinchos = []

    # 3. Botón físico sobre el suelo
    boton_nivel = {
        "rect": pygame.Rect(840, suelo.top - 12, 80, 12),
        "presionado": False,
    }

    # 4. Pared vertical móvil y dintel superior fijo
    pared_nivel = {
        "x": 1140,
        "y": 140.0,
        "y_cerrada": 140.0,
        "y_abierta": -340.0,
        "ancho": 36,
        "alto": 500,
        "rect": pygame.Rect(1140, 140, 36, 500),
        "progreso": 0.0,
    }

    dintel_superior = pygame.Rect(1120, 0, 76, 140)

    plataformas = [
        dintel_superior,
        pared_nivel["rect"],
    ]

    # 5. Llave al otro lado de la pared
    llave = crear_llave(1500, suelo.top - 46)

    # 6. Puerta de salida en el extremo derecho del escenario
    puerta = crear_puerta(1850, suelo.top - 90)
    return locals()


def nivel_1_4(p1_color, p2_color, bloques_peligrosos):
    # Nivel 1-4: «El láser y la caja»
    # - Zona inicial a la izquierda: plataforma segura (x=0..540, y=480).
    # - Puerta de salida en el extremo derecho del escenario (x=1900) para completar el nivel hacia adelante.
    # - Personajes inician a salvo a la izquierda (x=140, x=220).
    # - Caja cerca del borde (x=340) sobre la plataforma izquierda.
    # - Único pozo central de profundidad moderada (x=540..1100, y=480..560, profundidad=80px).
    # - Pinchos mortales ÚNICAMENTE en el fondo del pozo (x=630..1085, y=544..560).
    # - Emisor de láser (x=524..540, y=509) montado en la pared interna izquierda, apuntando horizontalmente a la derecha (y_rayo=520).
    # - El láser termina estrictamente en la pared interna derecha sólida (x=1100) si no hay obstáculos.
    # - Al empujar la caja hacia el pozo frente al emisor (x=540..600), cae al fondo y bloquea el rayo y su zona mortal.
    # - Plataformas intermedias de cruce sobre el hueco (x=680, y=528; x=890, y=524) bajadas a una altura coherente.
    # - Plataforma de destino a la derecha (x=1100..ancho_mundo, y=480) continua hasta el fin del escenario (sin segundo pozo).
    # - Plataforma elevada con la llave (x=1550, y=425, llave en x=1600).
    # - Tras cruzar el hueco y tomar la llave, ambos avanzan hacia la derecha hasta la puerta de salida.
    ancho_mundo_nivel = 2100
    usar_caja = True
    usar_soga = False
    usar_agua = False
    usar_pinchos = True
    usar_llave = True

    suelo = pygame.Rect(0, 560, ancho_mundo_nivel, ALTO - 560)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    # 1. Plataforma inicial a la izquierda
    plat_izq = pygame.Rect(0, 480, 540, ALTO - 480)
    # 2. Plataformas intermedias de cruce sobre el hueco (bajadas respecto a la posición del láser)
    plat_paso1 = pygame.Rect(680, 528, 110, 16)
    plat_paso2 = pygame.Rect(890, 524, 110, 16)
    # 3. Plataforma de destino a la derecha continua hasta el final del mundo (sin segundo pozo)
    plat_der = pygame.Rect(1100, 480, ancho_mundo_nivel - 1100, ALTO - 480)
    # 4. Plataforma elevada para la llave
    plat_llave = pygame.Rect(1550, 425, 140, 25)

    plataformas = [plat_izq, plat_paso1, plat_paso2, plat_der, plat_llave]

    # Hueco único central de profundidad moderada (80px)
    pozo_nivel = {
        "x": 540,
        "y": 480,
        "ancho": 560,
        "alto": 80,
    }

    # Pinchos mortales únicamente en el fondo del pozo (debajo de las plataformas)
    pinchos = [pygame.Rect(x, suelo.top - 16, 32, 16) for x in range(630, 1085, 34)]

    # Puerta de salida en el extremo derecho del escenario
    puerta = crear_puerta(1900, plat_der.top - 90)

    # Personajes caen desde la parte superior sobre la plataforma izquierda
    jugador1 = crear_personaje(140, 0, p1_color)
    jugador2 = crear_personaje(220, 0, p2_color)

    # Caja empujable en la plataforma izquierda
    caja = crear_caja(340, plat_izq.top - TAMANO_CAJA)

    # Llave sobre la plataforma elevada en la zona derecha
    llave = crear_llave(1600, plat_llave.top - 46)

    # Láser horizontal mortal en la pared interna izquierda (x=540) que termina en la pared derecha (x=1100)
    emisor_laser = pygame.Rect(524, 509, 16, 22)
    laser_nivel = {
        "emisor_rect": emisor_laser,
        "y_rayo": 520,
        "bloqueado": False,
        "x_fin": 1100,
        "pared_der_x": 1100,
        "rect_dano": pygame.Rect(emisor_laser.right, 516, 1100 - emisor_laser.right, 8),
    }
    return locals()


def nivel_1_5(p1_color, p2_color, bloques_peligrosos):
    # Nivel 1-5: «Las cuatro paredes de colores»
    # - Recorrido horizontal con suelo inferior continuo (suelo.top = 640).
    # - Plataforma elevada superior (top=480, espesor=24, bottom=504), dejando 136px de espacio libre hasta el suelo.
    # - Altura inalcanzable de un salto individual desde el suelo (160px > 138px), requiriendo una torre humana:
    #   el personaje superior salta desde la cabeza de su compañero para aterrizar sobre la plataforma elevada.
    # - Cuatro paredes verticales que bloquean el camino superior en secuencia obligatoria:
    #   1. ROJA (x=620) -> 2. AZUL (x=920) -> 3. ROJA (x=1220) -> 4. AZUL (x=1520).
    # - Cuatro botones correspondientes en el suelo para el personaje inferior:
    #   1. ROJO (x=550) -> 2. AZUL (x=850) -> 3. ROJO (x=1150) -> 4. AZUL (x=1450).
    # - Al activar un botón rojo, se desactivan todas las paredes rojas y las azules permanecen activas.
    # - Al activar un botón azul, se desactivan todas las paredes azules y las rojas permanecen activas.
    # - Llave ubicada al final del recorrido superior (x=1630, y=plat_superior.top - 46).
    # - La plataforma superior finaliza en x=1700, permitiendo que el personaje superior baje al suelo derecho mediante un hueco amplio de 140px.
    # - Puerta de salida al final del nivel en el suelo derecho (x=1880, y=suelo.top - 90).
    ancho_mundo_nivel = 2100
    usar_caja = False
    usar_soga = False
    usar_agua = False
    usar_pinchos = False
    usar_llave = True

    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    # Personajes inician arriba a la izquierda y caen por gravedad
    jugador1 = crear_personaje(120, 0, p1_color)
    jugador2 = crear_personaje(220, 0, p2_color)

    caja = None
    pinchos = []

    # Plataforma superior (superficie en y=480, espesor 24px)
    # Termina en x=1700 para dejar una abertura amplia y fluida de descenso (140px) hasta el inicio de la barrera en x=1840.
    plat_superior = pygame.Rect(340, 480, 1360, 24)
    # Techo/riel superior decorativo (y=170, altura 26px)
    techo_superior = pygame.Rect(320, 170, 1440, 26)

    # Barrera sólida en forma de L invertida para cubrir la zona de la puerta y delimitar el final del nivel:
    # - Tramo horizontal ubicado por encima de la puerta (top=480, espesor 24px, x=1840 a 2100)
    # - Tramo vertical conectado en su extremo derecho que baja hasta el suelo (x=2076 a 2100, y=480 a suelo.top=640)
    # - Sellada contra el límite derecho del mundo para evitar trampas o caídas a zonas muertas sin salida.
    barrera_l_horiz = pygame.Rect(1840, 480, 260, 24)
    barrera_l_vert = pygame.Rect(2076, 480, 24, suelo.top - 480)

    plataformas_base = [plat_superior, techo_superior, barrera_l_horiz, barrera_l_vert]
    plataformas = list(plataformas_base)

    # Cuatro paredes verticales en la secuencia: ROJA -> AZUL -> ROJA -> AZUL
    paredes_colores = [
        {
            "id": 1,
            "color": "rojo",
            "col_fill": (230, 50, 50),
            "col_borde": (140, 20, 20),
            "col_luz": (255, 130, 130),
            "x": 620,
            "ancho": 28,
            "alto": 284,
            "y_cerrada": 196.0,
            "y_abierta": -88.0,
            "progreso": 0.0,
            "rect": pygame.Rect(620, 196, 28, 284),
        },
        {
            "id": 2,
            "color": "azul",
            "col_fill": (45, 120, 240),
            "col_borde": (20, 60, 150),
            "col_luz": (130, 190, 255),
            "x": 920,
            "ancho": 28,
            "alto": 284,
            "y_cerrada": 196.0,
            "y_abierta": -88.0,
            "progreso": 0.0,
            "rect": pygame.Rect(920, 196, 28, 284),
        },
        {
            "id": 3,
            "color": "rojo",
            "col_fill": (230, 50, 50),
            "col_borde": (140, 20, 20),
            "col_luz": (255, 130, 130),
            "x": 1220,
            "ancho": 28,
            "alto": 284,
            "y_cerrada": 196.0,
            "y_abierta": -88.0,
            "progreso": 0.0,
            "rect": pygame.Rect(1220, 196, 28, 284),
        },
        {
            "id": 4,
            "color": "azul",
            "col_fill": (45, 120, 240),
            "col_borde": (20, 60, 150),
            "col_luz": (130, 190, 255),
            "x": 1520,
            "ancho": 28,
            "alto": 284,
            "y_cerrada": 196.0,
            "y_abierta": -88.0,
            "progreso": 0.0,
            "rect": pygame.Rect(1520, 196, 28, 284),
        },
    ]

    # Dos botones sobre el suelo debajo del recorrido: exactamente uno rojo y uno azul
    botones_colores = [
        {
            "id": 1,
            "color": "rojo",
            "col_fill": (235, 55, 55),
            "col_borde": (150, 25, 25),
            "col_luz": (255, 140, 140),
            "rect": pygame.Rect(680, suelo.top - 12, 70, 12),
            "presionado": False,
        },
        {
            "id": 2,
            "color": "azul",
            "col_fill": (45, 125, 245),
            "col_borde": (20, 65, 160),
            "col_luz": (140, 200, 255),
            "rect": pygame.Rect(1100, suelo.top - 12, 70, 12),
            "presionado": False,
        },
    ]

    # Llave sobre la plataforma superior en la zona final tras la 4ta pared y antes del descenso
    llave = crear_llave(1630, plat_superior.top - 46)

    # Puerta de salida en el suelo bajo el tramo horizontal de la barrera en L
    puerta = crear_puerta(1880, suelo.top - 90)

    # Botón inferior para la compuerta del hueco de descenso (junto al hueco, a la izquierda de x=1700)
    boton_compuerta = {
        "rect": pygame.Rect(1620, suelo.top - 12, 70, 12),
        "presionado": False,
    }

    # Compuerta mecánica que cierra la abertura por la que el personaje superior podría descender directamente (x=1700..1840)
    compuerta = {
        "rect": pygame.Rect(1700, 480, 140, 24),
        "progreso": 0.0,
    }

    # La compuerta inicia completamente cerrada y sólida
    plataformas = list(plataformas_base) + [p["rect"] for p in paredes_colores] + [compuerta["rect"]]
    return locals()


def nivel_2_1(p1_color, p2_color, bloques_peligrosos):
    # Mundo 2 - Nivel 1: Introducción a la Soga (El arrastre cooperativo)
    # Nivel introductorio centrado en aprender a moverse y coordinar saltos unidos por la soga
    ancho_mundo_nivel = 2200
    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = True
    usar_agua = False
    usar_pinchos = True
    usar_llave = True

    # Zona inicial: ambos personajes caen desde la parte superior unidos por la soga
    jugador1 = crear_personaje(120, 0, p1_color)
    jugador2 = crear_personaje(210, 0, p2_color)

    caja = None

    # 1. Primer obstáculo: escalones amplios para subir y caminar juntos
    escalon_1 = pygame.Rect(440, 580, 230, 60)
    escalon_2 = pygame.Rect(670, 520, 250, 120)

    # 2. Zona de saltos coordinados entre plataformas a distintas alturas
    plat_salto_1 = pygame.Rect(990, 460, 220, 26)
    plat_salto_2 = pygame.Rect(1280, 400, 220, 26)

    # 3. Brecha de separación que exige coordinar el avance y uso de la soga
    # 4. Plataforma de destino amplia con llave y puerta
    plat_destino = pygame.Rect(1620, 430, 520, 26)

    # Las plataformas transitables son las elevadas (sin plataforma de retorno segura)
    plataformas = [escalon_1, escalon_2, plat_salto_1, plat_salto_2, plat_destino]

    # Pozo y pinchos mortales debajo de la zona aérea extendidos de forma continua dentro de la abertura
    pozo_nivel = {
        "x": 920,
        "y": 570,
        "ancho": ancho_mundo_nivel - 920,
        "alto": 70,
    }
    pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(926, ancho_mundo_nivel - 32, 35)]

    # Llave cerca del final del recorrido sobre la plataforma de destino
    llave = crear_llave(1820, plat_destino.top - 46)

    # Puerta de salida en la plataforma de destino
    puerta = crear_puerta(2040, plat_destino.top - 90)
    return locals()


def nivel_2_2(p1_color, p2_color, bloques_peligrosos):
    # Mundo 2 - Nivel 2: «La plataforma móvil»
    # El objetivo es conseguir la llave y llegar a la puerta de salida sin caer en el abismo lleno de pinchos.
    ancho_mundo_nivel = 2200
    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = True
    usar_agua = False
    usar_pinchos = True
    usar_llave = True

    # Plataforma inicial fija donde inician los personajes (superficie en y=460)
    plat_inicio = pygame.Rect(0, 460, 360, 26)
    plat_inicio_base = pygame.Rect(0, 486, 360, suelo.top - 486 + 80)

    # Ambos personajes inician unidos por la soga sobre la plataforma inicial
    jugador1 = crear_personaje(80, 460 - ALTO_HITBOX, p1_color)
    jugador2 = crear_personaje(180, 460 - ALTO_HITBOX, p2_color)

    caja = None

    # Abismo continuo con pinchos mortales cubriendo exactamente el espacio de la abertura (x: 360..1940)
    pozo_nivel = {
        "x": 360,
        "y": 570,
        "ancho": 1940 - 360,
        "alto": 70,
    }
    # Pinchos delimitados exactamente a la abertura del pozo sin superponerse con las paredes
    pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(366, 1940 - 32, 35)]

    # Plataforma móvil para cruzar el abismo
    plataforma_movil = {
        "rect": pygame.Rect(370, 460, 220, 24),
        "x": 370.0,
        "y": 460.0,
        "x_inicial": 370.0,
        "y_inicial": 460.0,
        "ancho": 220,
        "alto": 24,
        "x_fin": 1720.0,
        "velocidad": 1.8,
        "tiempo_con_peso": 0,
        "tiempo_activacion": 120,  # ~2 segundos a 60 FPS
        "tiempo_espera_retorno": 0,
        "tiempo_max_espera_retorno": 300,  # ~5 segundos a 60 FPS
        "estado": "esperando_inicio",  # "esperando_inicio", "avanzando", "esperando_retorno", "regresando"
        "moviendo": False,
        "llegada": False,
    }

    # Bloque central sólido en el recorrido de la plataforma que exige coordinar el salto con la soga
    bloque_central = {
        "rect": pygame.Rect(1060, 390, 54, 66),
        "x": 1060,
        "y": 390,
        "ancho": 54,
        "alto": 66,
    }

    # Plataforma de destino al final del abismo (superficie en y=460)
    plat_llegada = pygame.Rect(1940, 460, 260, 26)
    plat_llegada_base = pygame.Rect(1940, 486, 260, suelo.top - 486 + 80)

    plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base, bloque_central["rect"]]
    plataformas = list(plataformas_base) + [plataforma_movil["rect"]]

    # Llave accesible tras superar el bloque central
    llave = crear_llave(1420, 460 - 46)

    # Puerta de salida en la plataforma de destino
    puerta = crear_puerta(2050, 460 - 90)
    return locals()


def nivel_2_3(p1_color, p2_color, bloques_peligrosos):
    # Mundo 2 — Nivel 3: «El péndulo» (Niveles.pdf, página 8)
    # Objetivo: conseguir la llave que está debajo de la plataforma y llegar juntos a la puerta de salida sin caer en los pinchos.
    # Mecánica principal: La soga se utiliza para balancear a uno de los personajes como un péndulo.
    # Uno sube a la plataforma elevada mientras el otro cuelga sobre el abismo lleno de pinchos.
    # El jugador superior se mueve para generar impulso de balanceo y alcanzar la llave en la zona inferior.
    # El balanceo transmite tensión y puede arrastrar al jugador de arriba hacia el borde si no controla el equilibrio.
    # Los pinchos y el bloque peligroso son mortales: tocar los pinchos reinicia el nivel.
    ancho_mundo_nivel = 2200
    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = True
    usar_agua = False
    usar_pinchos = True
    usar_llave = True

    # 1. Plataforma inicial fija protegida (y=360)
    # Ambos personajes inician juntos en una zona segura unidos por la soga
    plat_inicio = pygame.Rect(0, 360, 260, 26)
    plat_inicio_base = pygame.Rect(0, 386, 260, suelo.top - 386 + 80)

    jugador1 = crear_personaje(70, 360 - ALTO_HITBOX, p1_color)
    jugador2 = crear_personaje(160, 360 - ALTO_HITBOX, p2_color)

    caja = None

    # 2. Gran plataforma elevada (el puente de balanceo a y=250)
    # Accesible limpiamente de un salto desde plat_inicio (diferencia de 110 px, salto normal alcanza 141 px)
    plat_elevada = pygame.Rect(310, 250, 1080, 26)

    # 3. Abismo de pinchos mortales continuo y denso en el fondo del pozo (x: 260 a 1380)
    pozo_nivel = {
        "x": 260,
        "y": 570,
        "ancho": 1380 - 260,
        "alto": 70,
    }
    # Hilera continua de pinchos en el fondo de la abertura (terminando exactamente antes de la pared derecha)
    pinchos = [crear_pincho(x, suelo.top - 28, 25, 28, direccion="arriba") for x in range(264, 1380 - 25, 22)]
    pinchos = [p for p in pinchos if p.right <= 1380]

    # Pinchos laterales en las paredes del abismo (aumentan la dificultad si el péndulo se acerca a los extremos)
    # Se despeja la parte superior de la pared izquierda (quitando el par de pinchos más altos) y de la pared derecha para facilitar el salto y el paso de ambos personajes
    pinchos_pared_izq = [crear_pincho(260, y, 22, 26, direccion="derecha") for y in range(454, 600, 32)]
    pinchos_pared_der = [crear_pincho(1380 - 22, y, 22, 26, direccion="izquierda") for y in range(518, 600, 32)]
    pinchos.extend(pinchos_pared_izq + pinchos_pared_der)

    # Pinchos en el borde inferior de la plataforma elevada (zona de la viga roja)
    # El personaje suspendido que oscila en el péndulo debe controlar el balanceo con precisión
    # para no tocar estos pinchos por arriba
    pinchos_techo_pendulo = [crear_pincho(x, plat_elevada.bottom, 28, 20, direccion="abajo") for x in range(400, 1260, 32)]
    pinchos.extend(pinchos_techo_pendulo)

    # 4. Secuencia de bloques cuadrados con pinchos para aumentar la dificultad del péndulo
    # Se conserva el obstáculo original (880, 440) y se agrega un par de obstáculos seguidos (660, 440 y 770, 440)
    # formando una secuencia horizontal que los personajes deben superar con coordinación
    b_pel_0, s_pel_0 = crear_bloque_con_pinchos(660, 440, 60, 60)
    b_pel_1, s_pel_1 = crear_bloque_con_pinchos(770, 440, 60, 60)
    bloques_peligrosos.extend([b_pel_0, b_pel_1])
    pinchos.extend(s_pel_0 + s_pel_1)

    bx, by, bw, bh = 880, 440, 70, 60
    bloque_peligroso = {
        "rect": pygame.Rect(bx, by, bw, bh),
        "x": bx,
        "y": by,
        "ancho": bw,
        "alto": bh,
    }
    bloques_peligrosos.append(bloque_peligroso)

    # Pinchos dobles y más cerrados alrededor del bloque rojo original
    pinchos.extend([
        crear_pincho(bx + 4, by - 22, 30, 22, direccion="arriba"),
        crear_pincho(bx + 36, by - 22, 30, 22, direccion="arriba"),
        crear_pincho(bx + 4, by + bh, 30, 22, direccion="abajo"),
        crear_pincho(bx + 36, by + bh, 30, 22, direccion="abajo"),
        crear_pincho(bx - 22, by + 4, 22, 24, direccion="izquierda"),
        crear_pincho(bx - 22, by + 32, 22, 24, direccion="izquierda"),
        crear_pincho(bx + bw, by + 4, 22, 24, direccion="derecha"),
        crear_pincho(bx + bw, by + 32, 22, 24, direccion="derecha"),
    ])

    # 5. Plataforma de llegada segura (y=360) tras superar el abismo
    plat_llegada = pygame.Rect(1380, 360, 820, 26)
    plat_llegada_base = pygame.Rect(1380, 386, 820, suelo.top - 386 + 80)

    plataformas = [
        plat_inicio,
        plat_inicio_base,
        plat_elevada,
        b_pel_0["rect"],
        b_pel_1["rect"],
        bloque_peligroso["rect"],
        plat_llegada,
        plat_llegada_base,
    ]

    # 6. Llave ubicada en la trayectoria del péndulo más allá del bloque rojo
    llave = crear_llave(1020, 360)

    # 7. Puerta de salida en la plataforma segura de llegada
    puerta = crear_puerta(2050, 360 - 90)
    return locals()


def nivel_2_4(p1_color, p2_color, bloques_peligrosos):
    # Mundo 2 — Nivel 4: «Las plataformas que se derrumban» (Niveles.pdf, página 8)
    # Objetivo: cruzar un abismo lleno de pinchos, conseguir la llave y llegar a la puerta de salida sin caer.
    # Mecánica principal: Las plataformas son temporales y se derrumban aproximadamente 1 segundo (60 frames) tras ser pisadas.
    # Los personajes están unidos por una soga y deben sincronizar sus saltos rápidamente antes de que caigan.
    # Separación horizontal calibrada (gaps de 120-125px) con riesgo real de caer al abismo si no se salta con precisión.
    # A mitad del recorrido se encuentra la llave, sobre las plataformas suspendidas sobre el abismo.
    # Si un personaje cae al abismo o toca los pinchos, ambos pierden y el nivel se reinicia.
    ancho_mundo_nivel = 2600
    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = True
    usar_agua = False
    usar_pinchos = True
    usar_llave = True

    # Plataforma inicial segura (x: 0..200, y=460)
    plat_inicio = pygame.Rect(0, 460, 200, 26)
    plat_inicio_base = pygame.Rect(0, 486, 200, suelo.top - 486 + 80)

    # Ambos personajes inician unidos por la soga en el lado izquierdo
    jugador1 = crear_personaje(50, 460 - ALTO_HITBOX, p1_color)
    jugador2 = crear_personaje(120, 460 - ALTO_HITBOX, p2_color)

    caja = None

    # Abismo continuo cubierto de pinchos mortales debajo de todas las plataformas (x: 200..2190)
    pozo_nivel = {
        "x": 200,
        "y": 570,
        "ancho": 1990,
        "alto": 70,
    }
    # Pinchos ajustados para que no atraviesen ni sobresalgan de la pared derecha
    pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 2190 - 32, 35)]

    # Plataforma final de llegada con la puerta (x: 2190..2600, y=460)
    plat_llegada = pygame.Rect(2190, 460, 410, 26)
    plat_llegada_base = pygame.Rect(2190, 486, 410, suelo.top - 486 + 80)

    plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]

    # Serie de 8 plataformas pequeñas que se derrumban 1.0 segundo (60 frames) tras pisarlas
    # Separación horizontal moderada (gaps de 120-125px) para exigir saltos reales y coordinación
    def _crear_p_derrumbable(px, py, pw=110, ph=22):
        return {
            "rect": pygame.Rect(px, py, pw, ph),
            "x_inicial": px,
            "y_inicial": py,
            "y": float(py),
            "vel_y": 0.0,
            "ancho": pw,
            "alto": ph,
            "estado": "intacta",  # "intacta", "agrietandose", "temblando", "derrumbada"
            "tiempo_restante": 60,  # 1.0 segundo a 60 FPS
            "pisada": False,
            "particulas": [],
        }

    coords_plats = [
        (320, 460),   # Gap desde inicio (200): 120px
        (550, 430),   # Gap desde P1 (430): 120px, dy = -30px
        (785, 460),   # Gap desde P2 (660): 125px, dy = +30px
        (1020, 420),  # Gap desde P3 (895): 125px, dy = -40px (Plataforma con la llave)
        (1255, 450),  # Gap desde P4 (1130): 125px, dy = +30px
        (1490, 420),  # Gap desde P5 (1365): 125px, dy = -30px
        (1725, 450),  # Gap desde P6 (1600): 125px, dy = +30px
        (1960, 460),  # Gap desde P7 (1835): 125px, dy = +10px
    ]
    plataformas_derrumbables = [_crear_p_derrumbable(px, py) for px, py in coords_plats]
    plataformas = list(plataformas_base) + [p["rect"] for p in plataformas_derrumbables]

    # Llave a mitad del recorrido sobre la 4ta plataforma
    llave = crear_llave(1075, 420 - 46)

    # Puerta de salida en la plataforma de destino
    puerta = crear_puerta(2380, 460 - 90)
    return locals()


def nivel_2_5(p1_color, p2_color, bloques_peligrosos):
    # Mundo 2 — Nivel 5: «Las plataformas alternadas» (Niveles.pdf, página 9)
    # Objetivo: llegar hasta la puerta saltando de plataforma en plataforma sin caer al abismo.
    # Mecánica principal: Saltos entre plataformas a diferentes alturas, coordinación entre los dos personajes
    # unidos por la soga y riesgo de caer al abismo.
    # Reglas:
    # - Las plataformas forman una escalera que asciende claramente desde abajo a la izquierda hasta arriba a la derecha.
    # - Cada plataforma siguiente está más alta que la anterior y desplazada hacia la derecha (ascenso vertical progresivo).
    # - La soga une a ambos personajes y transmite tensión con límite estricto de estiramiento (+20px).
    # - El nivel es compacto horizontalmente (1400px) y aprovecha la altura vertical del escenario.
    # - Debajo de toda la escalera hay un abismo continuo con pinchos mortales.
    # - La llave se encuentra en el escalón superior antes de la cima; la puerta está arriba de todo en la plataforma final.
    # - Ambos personajes deben recoger la llave y llegar juntos a la puerta en la cima para terminar el nivel.
    ancho_mundo_nivel = 1400
    suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = True
    usar_agua = False
    usar_pinchos = True
    usar_llave = True

    # Plataforma inicial segura en la base izquierda (x: 0..160, y=560)
    plat_inicio = pygame.Rect(0, 560, 160, 26)
    plat_inicio_base = pygame.Rect(0, 586, 160, suelo.top - 586 + 80)

    # Ambos personajes inician juntos abajo a la izquierda unidos por la soga
    jugador1 = crear_personaje(40, 560 - ALTO_HITBOX, p1_color)
    jugador2 = crear_personaje(100, 560 - ALTO_HITBOX, p2_color)

    caja = None

    # Abismo continuo cubierto de pinchos mortales bajo todas las plataformas alternadas (x: 160..730)
    pozo_nivel = {
        "x": 160,
        "y": 570,
        "ancho": 570,
        "alto": 70,
    }
    # Pinchos ajustados exactamente dentro de la abertura sin penetrar en la pared de llegada
    pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(165, 730 - 32, 32)]

    # Plataforma de llegada segura a la derecha en la cima con la puerta de salida (x: 730..1400, y=130)
    plat_llegada = pygame.Rect(730, 130, 670, 26)
    plat_llegada_base = pygame.Rect(730, 156, 670, suelo.top - 156 + 80)

    plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]

    # Plataformas en ZIGZAG lateral con amplio despeje vertical (headroom > 70px) para saltar libremente:
    # P1: Izquierda (x: 180..410, y: 480) - Centro 295
    # P2: Derecha   (x: 430..660, y: 390) - Centro 545 (dx = +250 hacia la derecha)
    # P3: Izquierda (x: 130..360, y: 300) - Centro 245 (dx = -300 hacia la izquierda, 180px vertical sobre P1)
    # P4: Derecha   (x: 480..710, y: 210) - Centro 595 (dx = +350 hacia la derecha, 180px vertical sobre P2, con Llave)
    # Recorrido cooperativo: INICIO (y=560) -> P1 (y=480) -> P2 (y=390) -> P3 (y=300) -> P4 (y=210, Llave) -> SALIDA (y=130, Puerta)
    plataformas_alternadas = [
        pygame.Rect(180, 480, 230, 24),  # P1: Izquierda (y=480)
        pygame.Rect(430, 390, 230, 24),  # P2: Derecha   (y=390)
        pygame.Rect(130, 300, 230, 24),  # P3: Izquierda (y=300)
        pygame.Rect(480, 210, 230, 24),  # P4: Derecha   (y=210, cumbre con pedestal y llave)
    ]
    plataformas = list(plataformas_base) + list(plataformas_alternadas)

    # Llave dorada en el pedestal de la cumbre derecha (P4, centro 595, y=210)
    llave = crear_llave(595 - 12, 210 - 46)

    # Puerta de salida en la plataforma final de llegada en la cima (x=810, y=130)
    puerta = crear_puerta(810, 130 - 90)
    return locals()


def nivel_3_1(p1_color, p2_color, bloques_peligrosos):
    # Mundo 3 — Nivel 1: «El jardín de algas» (Niveles.pdf, páginas 10 y 13)
    # Objetivo: explorar el escenario submarino, encontrar la llave y llegar a la puerta de salida.
    # Mecánicas principales:
    # - Movimiento submarino: los personajes pueden desplazarse en cuatro direcciones y controlar su altura.
    # - Personajes independientes: no hay soga ni tirones entre ellos.
    # - Obstáculos naturales: rocas, corales y algunas algas bloquean determinados caminos.
    # - Algas decorativas que ondean con la corriente marina y se atraviesan sin colisión.
    # - Obstáculos mortales: erizos de mar y corales espinosos (si cualquiera los toca, ambos mueren y se reinicia).
    # - La llave se encuentra entre unas rocas en una gruta submarina.
    # - Ambos personajes deben llegar a la puerta para completar el nivel.
    ancho_mundo_nivel = 2600
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = False
    usar_agua = True
    usar_pinchos = True
    usar_llave = True

    # Escenario completamente submarino
    ZONA_AGUA.x = 0
    ZONA_AGUA.y = 0
    ZONA_AGUA.width = ancho_mundo_nivel
    ZONA_AGUA.height = ALTO

    # Personajes inician en la zona abierta izquierda flotando en el agua
    jugador1 = crear_personaje(120, 340, p1_color)
    jugador2 = crear_personaje(230, 340, p2_color)
    jugador1["en_agua"] = True
    jugador2["en_agua"] = True

    caja = None

    # Techo superficial del agua
    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 25)

    # Formaciones rocosas sólidas
    rocas_submarinas = [
        # Zona 1: Entrada y arrecife inicial
        {"rect": pygame.Rect(0, 0, 480, 35)},
        {"rect": pygame.Rect(300, 35, 90, 75)},
        {"rect": pygame.Rect(0, 585, 340, 60)},

        # Zona 2: Gran bifurcación (Arrecife central que divide en ruta superior e inferior)
        {"rect": pygame.Rect(520, 240, 210, 160), "coral": True, "color_coral": (245, 110, 135)},
        {"rect": pygame.Rect(760, 25, 130, 95)},
        {"rect": pygame.Rect(600, 520, 180, 125)},

        # Zona 3: Caverna intermedia y gruta de la llave
        {"rect": pygame.Rect(1020, 25, 320, 75)},
        {"rect": pygame.Rect(1140, 260, 230, 45)},
        {"rect": pygame.Rect(1370, 260, 40, 190)},
        {"rect": pygame.Rect(1100, 510, 220, 135)},
        # Nicho de rocas que custodia la llave
        {"rect": pygame.Rect(1470, 450, 190, 50)},
        {"rect": pygame.Rect(1470, 290, 150, 40)},

        # Zona 4: Columnas y pilares marinos
        {"rect": pygame.Rect(1820, 140, 65, 260)},
        {"rect": pygame.Rect(1980, 25, 160, 85)},
        {"rect": pygame.Rect(2020, 320, 65, 240)},

        # Zona 5: Terraza final de llegada con la puerta
        {"rect": pygame.Rect(2300, 480, 300, 165), "coral": True, "color_coral": (255, 150, 85)},
    ]

    # Algas barrera sólidas que bloquean caminos específicos obligando a buscar rutas alternativas
    # Ancladas al lecho marino (suelo.top) sin quedar suspendidas en el agua
    barreras_algas = [
        {"rect": pygame.Rect(840, 400, 35, suelo.top - 400)},   # Bloquea salida inferior directa en zona 2 (apoyada en el piso)
        {"rect": pygame.Rect(1660, 320, 35, suelo.top - 320)},  # Bloquea salida trasera de la gruta de la llave (apoyada en el piso)
        {"rect": pygame.Rect(1835, 400, 35, suelo.top - 400)},  # Bloquea paso inferior bajo el pilar 1 en zona 4 (apoyada en el piso)
    ]

    # Algas decorativas que ondean con la corriente (sin colisión física)
    # Todas emergen desde el lecho marino (suelo.top) para que ninguna quede flotando en el agua
    algas_decorativas = [
        # Capa fondo
        {"x": 60, "y": suelo.top, "alto": 120, "amplitud": 16, "fase": 0.0, "capa": "fondo"},
        {"x": 200, "y": suelo.top, "alto": 150, "amplitud": 20, "fase": 1.2, "capa": "fondo"},
        {"x": 420, "y": suelo.top, "alto": 130, "amplitud": 18, "fase": 2.5, "capa": "fondo"},
        {"x": 750, "y": suelo.top, "alto": 140, "amplitud": 16, "fase": 0.8, "capa": "fondo"},
        {"x": 980, "y": suelo.top, "alto": 160, "amplitud": 22, "fase": 3.1, "capa": "fondo"},
        {"x": 1280, "y": suelo.top, "alto": 135, "amplitud": 17, "fase": 1.7, "capa": "fondo"},
        {"x": 1540, "y": suelo.top, "alto": 125, "amplitud": 15, "fase": 4.2, "capa": "fondo"},
        {"x": 1740, "y": suelo.top, "alto": 140, "amplitud": 19, "fase": 2.1, "capa": "fondo"},
        {"x": 1940, "y": suelo.top, "alto": 130, "amplitud": 17, "fase": 0.5, "capa": "fondo"},
        {"x": 2160, "y": suelo.top, "alto": 150, "amplitud": 21, "fase": 3.8, "capa": "fondo"},
        {"x": 2480, "y": suelo.top, "alto": 130, "amplitud": 16, "fase": 1.4, "capa": "fondo"},
        # Capa frente
        {"x": 130, "y": suelo.top, "alto": 95, "amplitud": 14, "fase": 2.0, "capa": "frente"},
        {"x": 370, "y": suelo.top, "alto": 110, "amplitud": 15, "fase": 0.3, "capa": "frente"},
        {"x": 670, "y": suelo.top, "alto": 120, "amplitud": 16, "fase": 1.5, "capa": "frente"},
        {"x": 1050, "y": suelo.top, "alto": 115, "amplitud": 18, "fase": 2.9, "capa": "frente"},
        {"x": 1420, "y": suelo.top, "alto": 100, "amplitud": 16, "fase": 0.9, "capa": "frente"},
        {"x": 1890, "y": suelo.top, "alto": 110, "amplitud": 17, "fase": 3.4, "capa": "frente"},
        {"x": 2240, "y": suelo.top, "alto": 120, "amplitud": 18, "fase": 1.1, "capa": "frente"},
    ]

    # Obstáculos mortales: erizos de mar y corales puntiagudos
    pinchos = [
        crear_pincho(795, 120, 60, 24, direccion="abajo"),
        crear_pincho(640, 496, 60, 24, direccion="arriba"),
        crear_pincho(1200, 305, 55, 24, direccion="abajo"),
        crear_pincho(1380, suelo.top - 24, 75, 24, direccion="arriba"),
        crear_pincho(2020, 296, 65, 24, direccion="arriba"),
    ]

    # Plataformas sólidas combinadas
    plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
    plataformas = list(plataformas_base)

    # La llave entre las rocas en la gruta submarina
    llave = crear_llave(1540, 395)

    # Puerta de salida en la terraza final
    puerta = crear_puerta(2410, 480 - 90)

    # Sistema de burbujas flotantes
    burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)
    tick_m3 = 0
    return locals()


def nivel_3_2(p1_color, p2_color, bloques_peligrosos):
    # Nivel 3-2: El laberinto de coral (Mundo Submarino)
    # - Laberinto generado proceduralmente en cada partida y reinicio con 100% de resolubilidad garantizada.
    # - Muros de roca submarina ancestral, arrecifes de coral y densas barreras de quelpo entrelazado.
    # - Múltiples bifurcaciones, rutas alternativas y callejones sin salida para exploración.
    # - Llave oculta en las profundidades de un callejón sin salida del laberinto.
    # - Ambos personajes nadan de forma independiente (sin cuerda, movimiento libre en 4 direcciones).
    # - Algas y corales luminiscentes decoran los pasajes y callejones.
    # - Puerta de salida en la terraza final tras encontrar la llave.
    ancho_mundo_nivel = 2600
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = False
    usar_agua = True
    usar_pinchos = False
    usar_llave = True

    ZONA_AGUA.x = 0
    ZONA_AGUA.y = 0
    ZONA_AGUA.width = ancho_mundo_nivel
    ZONA_AGUA.height = ALTO

    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 25)

    datos_lab = generar_laberinto_coral_m3_n2(ancho_mundo_nivel, ALTO, suelo.top, techo_agua.bottom)
    rocas_submarinas = datos_lab["rocas"]
    barreras_algas = datos_lab["barreras"]
    corales_decorativos = datos_lab["corales"]
    algas_decorativas = datos_lab["algas"]

    jugador1 = crear_personaje(datos_lab["p1_x"], datos_lab["p1_y"], p1_color)
    jugador2 = crear_personaje(datos_lab["p2_x"], datos_lab["p2_y"], p2_color)
    jugador1["en_agua"] = True
    jugador2["en_agua"] = True

    caja = None
    pinchos = []

    plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
    plataformas = list(plataformas_base)

    llave = crear_llave(datos_lab["llave_x"], datos_lab["llave_y"])
    puerta = crear_puerta(datos_lab["puerta_x"], datos_lab["puerta_y"])

    burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=50)
    tick_m3 = 0
    return locals()


def nivel_3_3(p1_color, p2_color, bloques_peligrosos):
    # Nivel 3-3: Las rocas peligrosas (Mundo Submarino)
    # - Pasillos con estalactitas, estalagmitas y formaciones rocosas marinas.
    # - Pasadizos calibrados y moderadamente ampliados para permitir maniobrar cómodamente.
    # - Distancias seguras entre pinchos enfrentados (margen vertical >= 45-75px, chimeneas de 80-125px).
    # - Pinchos y erizos submarinos mortales sobresaliendo tanto del suelo como del techo y cornisas.
    # - Los personajes se mueven de forma independiente (sin cuerda, según las reglas de Mundo 3) en 4 direcciones.
    # - Maniobras de precisión pero justas y superables jugando bien; si cualquiera toca uno, ambos mueren.
    # - Llave oculta en una gruta peligrosa protegida por rocas y pinchos.
    # - Puerta de salida ubicada al otro lado del desfiladero, sobre una terraza marina de coral.
    ancho_mundo_nivel = 2700
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = False
    usar_agua = True
    usar_pinchos = True
    usar_llave = True

    ZONA_AGUA.x = 0
    ZONA_AGUA.y = 0
    ZONA_AGUA.width = ancho_mundo_nivel
    ZONA_AGUA.height = ALTO

    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 30)

    # Personajes inician en la zona segura inicial antes del estrecho
    jugador1 = crear_personaje(110, 330, p1_color)
    jugador2 = crear_personaje(210, 330, p2_color)
    jugador1["en_agua"] = True
    jugador2["en_agua"] = True

    caja = None

    # Formaciones rocosas moderadamente ampliadas para permitir maniobrar
    rocas_submarinas = [
        # Zona 1: Entrada y primer estrechamiento (x = 0 .. 440)
        {"rect": pygame.Rect(320, techo_agua.bottom, 120, 85)},
        {"rect": pygame.Rect(320, 530, 120, suelo.top - 530)},

        # Zona 2: Desfiladero serpenteante en S con chimeneas amplias (x = 450 .. 1120)
        {"rect": pygame.Rect(480, techo_agua.bottom, 160, 210)},
        {"rect": pygame.Rect(720, 420, 180, suelo.top - 420)},
        {"rect": pygame.Rect(720, techo_agua.bottom, 180, 85)},
        {"rect": pygame.Rect(980, techo_agua.bottom, 140, 210)},

        # Zona 3: Gran bifurcación y Gruta de la Llave con pasajes holgados (x = 1140 .. 1720)
        {"rect": pygame.Rect(1140, techo_agua.bottom, 480, 50)},
        {"rect": pygame.Rect(1200, 280, 360, 90), "coral": True, "color_coral": (245, 110, 140)},
        {"rect": pygame.Rect(1350, 230, 80, 18), "coral": True, "color_coral": (255, 180, 80)},
        {"rect": pygame.Rect(1240, 555, 260, suelo.top - 555)},

        # Zona 4: Laberinto de pilares con espacio para maniobrar (x = 1750 .. 2320)
        {"rect": pygame.Rect(1760, techo_agua.bottom, 75, 270)},
        {"rect": pygame.Rect(1960, 340, 75, suelo.top - 340)},
        {"rect": pygame.Rect(2160, techo_agua.bottom, 75, 260)},
        {"rect": pygame.Rect(2150, 560, 95, suelo.top - 560)},

        # Zona 5: Terraza final de llegada con la puerta (x = 2380 .. 2700)
        {"rect": pygame.Rect(2380, 480, 320, suelo.top - 480), "coral": True, "color_coral": (255, 140, 80)},
    ]

    # Obstáculos mortales: erizos de mar y corales puntiagudos en suelo y techo
    pinchos = [
        # Zona 1: Primer estrechamiento
        crear_pincho(340, techo_agua.bottom + 85, 75, 20, direccion="abajo"),
        crear_pincho(340, 530 - 20, 75, 20, direccion="arriba"),

        # Zona 2: Serpentín en S
        crear_pincho(500, techo_agua.bottom + 210, 120, 20, direccion="abajo"),
        crear_pincho(510, suelo.top - 20, 110, 20, direccion="arriba"),
        crear_pincho(740, 420 - 20, 140, 20, direccion="arriba"),
        crear_pincho(740, techo_agua.bottom + 85, 140, 20, direccion="abajo"),
        crear_pincho(1000, techo_agua.bottom + 210, 100, 20, direccion="abajo"),
        crear_pincho(1000, suelo.top - 20, 100, 20, direccion="arriba"),

        # Zona 3: La gruta de la llave
        crear_pincho(1200, techo_agua.bottom + 50, 100, 20, direccion="abajo"),
        crear_pincho(1460, techo_agua.bottom + 50, 100, 20, direccion="abajo"),
        crear_pincho(1210, 280 - 20, 90, 20, direccion="arriba"),
        crear_pincho(1465, 280 - 20, 90, 20, direccion="arriba"),
        crear_pincho(1280, 370, 130, 20, direccion="abajo"),
        crear_pincho(1285, 555 - 20, 140, 20, direccion="arriba"),

        # Zona 4: Pilares y desfiladero final
        crear_pincho(1765, techo_agua.bottom + 270, 65, 20, direccion="abajo"),
        crear_pincho(1755, suelo.top - 20, 85, 20, direccion="arriba"),
        crear_pincho(1965, 340 - 20, 65, 20, direccion="arriba"),
        crear_pincho(1960, techo_agua.bottom, 75, 20, direccion="abajo"),
        crear_pincho(2165, techo_agua.bottom + 260, 65, 20, direccion="abajo"),
        crear_pincho(2155, 560 - 20, 85, 20, direccion="arriba"),
    ]

    barreras_algas = [
        {"rect": pygame.Rect(1620, 420, 35, suelo.top - 420)},
    ]

    # Plataformas sólidas combinadas
    plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
    plataformas = list(plataformas_base)

    # La llave sobre la repisa segura en la gruta
    llave = crear_llave(1378, 230 - 46)

    # Puerta de salida en la terraza final
    puerta = crear_puerta(2480, 480 - 90)

    # Corales decorativos temáticos
    corales_decorativos = [
        # Entrada
        {"tipo": "ramificado", "x": 160, "y": suelo.top, "escala": 1.1, "fase": 0.4, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"},
        # Gruta de la llave
        {"tipo": "anemona", "x": 1390, "y": 230, "escala": 1.15, "fase": 1.2, "color": (255, 210, 60), "color_sec": (255, 255, 180), "anclaje": "abajo"},
        {"tipo": "ramificado", "x": 1345, "y": 230, "escala": 0.85, "fase": 0.5, "color": (255, 105, 145), "color_sec": (255, 185, 205), "anclaje": "abajo"},
        {"tipo": "tubular", "x": 1435, "y": 230, "escala": 0.85, "fase": 2.2, "color": (45, 195, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"},
        {"tipo": "cerebro", "x": 1280, "y": 280, "escala": 1.0, "fase": 3.0, "color": (230, 110, 180), "color_sec": (255, 185, 225), "anclaje": "abajo"},
        {"tipo": "abanico", "x": 1500, "y": 280, "escala": 0.95, "fase": 1.8, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"},
        # Terraza de salida
        {"tipo": "ramificado", "x": 2420, "y": 480, "escala": 1.25, "fase": 0.8, "color": (255, 130, 70), "color_sec": (255, 200, 140), "anclaje": "abajo"},
        {"tipo": "abanico", "x": 2560, "y": 480, "escala": 1.15, "fase": 2.5, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"},
        {"tipo": "tubular", "x": 2390, "y": 480, "escala": 1.05, "fase": 1.2, "color": (45, 195, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"},
    ]

    # Algas marinas decorativas ondeando con la marea
    algas_decorativas = [
        {"x": 80, "y": suelo.top, "alto": 120, "amplitud": 16, "fase": 0.0, "capa": "fondo"},
        {"x": 260, "y": suelo.top, "alto": 140, "amplitud": 18, "fase": 1.3, "capa": "fondo"},
        {"x": 670, "y": suelo.top, "alto": 115, "amplitud": 15, "fase": 2.7, "capa": "fondo"},
        {"x": 1120, "y": suelo.top, "alto": 130, "amplitud": 17, "fase": 0.8, "capa": "fondo"},
        {"x": 1700, "y": suelo.top, "alto": 145, "amplitud": 19, "fase": 3.2, "capa": "fondo"},
        {"x": 2040, "y": suelo.top, "alto": 125, "amplitud": 16, "fase": 1.9, "capa": "fondo"},
        {"x": 2320, "y": suelo.top, "alto": 135, "amplitud": 18, "fase": 0.5, "capa": "fondo"},
        {"x": 2630, "y": suelo.top, "alto": 140, "amplitud": 17, "fase": 2.1, "capa": "fondo"},
        {"x": 140, "y": suelo.top, "alto": 95, "amplitud": 14, "fase": 2.2, "capa": "frente"},
        {"x": 880, "y": suelo.top, "alto": 105, "amplitud": 15, "fase": 0.6, "capa": "frente"},
        {"x": 1660, "y": suelo.top, "alto": 110, "amplitud": 16, "fase": 3.4, "capa": "frente"},
        {"x": 2260, "y": suelo.top, "alto": 100, "amplitud": 15, "fase": 1.2, "capa": "frente"},
    ]

    burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)
    tick_m3 = 0
    return locals()


def nivel_3_4(p1_color, p2_color, bloques_peligrosos):
    # Mundo 3 Nivel 4: "El laberinto oscuro" (Página 13 del PDF)
    # Objetivo: Encontrar la llave y llegar a la puerta de salida atravesando un laberinto submarino oscuro.
    # - Exploración con linternas independientes (P1: E/F/Espacio, P2: L/Enter/RShift/RCtrl).
    # - Haz de luz circular limitado (~145px) alrededor de cada personaje; brillo tenue personal cuando está apagada.
    # - Laberinto generado proceduralmente en cada partida o reinicio con 100% resolubilidad.
    # - Callejones sin salida y trampas mortales (erizos de mar) en cul-de-sacs secundarios.
    # - Llave y puerta completamente ocultas en la oscuridad hasta ser iluminadas por la linterna.
    # - Natación libre en 4 direcciones sin gravedad ni corrientes molestas.
    ancho_mundo_nivel = 2600
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = False
    usar_agua = True
    usar_pinchos = True
    usar_llave = True

    ZONA_AGUA.x = 0
    ZONA_AGUA.y = 0
    ZONA_AGUA.width = ancho_mundo_nivel
    ZONA_AGUA.height = ALTO

    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 25)

    linterna_p1 = True
    linterna_p2 = True

    datos_lab = generar_laberinto_oscuro_m3_n4(ancho_mundo_nivel, ALTO, suelo.top, techo_agua.bottom)

    jugador1 = crear_personaje(datos_lab["p1_x"], datos_lab["p1_y"], p1_color)
    jugador2 = crear_personaje(datos_lab["p2_x"], datos_lab["p2_y"], p2_color)
    jugador1["en_agua"] = True
    jugador2["en_agua"] = True

    caja = None
    rocas_submarinas = datos_lab["rocas"]
    barreras_algas = datos_lab["barreras"]
    corales_decorativos = datos_lab["corales"]
    algas_decorativas = datos_lab["algas"]
    pinchos = datos_lab["pinchos"]
    flechas_indicadoras = datos_lab.get("flechas", [])

    plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
    plataformas = list(plataformas_base)

    llave = crear_llave(datos_lab["llave_x"], datos_lab["llave_y"])
    puerta = crear_puerta(datos_lab["puerta_x"], datos_lab["puerta_y"])

    burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)
    tick_m3 = 0

    surf_oscuridad_m3 = pygame.Surface((ancho_mundo_nivel, ALTO), pygame.SRCALPHA)
    surf_oscuridad_m3_n4 = surf_oscuridad_m3
    surf_luz_linterna, surf_luz_tenue = obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45)
    return locals()


def nivel_3_5(p1_color, p2_color, bloques_peligrosos):
    # Mundo 3 — Nivel 5: «El abismo submarino» (Niveles.pdf, páginas 13 y 14)
    # Último nivel del Mundo 3:
    # Objetivo: conseguir la llave y llegar a la puerta atravesando una zona submarina peligrosa,
    # esquivando obstáculos, resistiendo las corrientes marinas y administrando el oxígeno.
    #
    # Mecánicas principales:
    # 1. Movimiento submarino libre en 4 direcciones y neutral buoyancy (sin soga).
    # 2. Corrientes de agua que empujan a los personajes (lateral, ascendente, descendente).
    # 3. Gestión de Oxígeno: cada personaje tiene una barra de oxígeno visible. Disminuye bajo el agua (~20s).
    # 4. Cámaras de aire / Zonas seguras: distribuidas estratégicamente para recargar oxígeno.
    # 5. Riesgo de ahogamiento: si el oxígeno llega a cero, el personaje muere y el nivel se reinicia.
    # 6. Obstáculos mortales: erizos marinos y corales puntiagudos en suelo, paredes y techo.
    ancho_mundo_nivel = 2600
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

    usar_caja = False
    usar_soga = False
    usar_agua = True
    usar_pinchos = True
    usar_llave = True

    ZONA_AGUA.x = 0
    ZONA_AGUA.y = 0
    ZONA_AGUA.width = ancho_mundo_nivel
    ZONA_AGUA.height = ALTO

    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 25)

    oxigeno_p1 = 100.0
    oxigeno_p2 = 100.0
    linterna_p1 = True
    linterna_p2 = True

    # Personajes inician dentro del primer refugio de aire (Cámara 1)
    jugador1 = crear_personaje(80, 280, p1_color)
    jugador2 = crear_personaje(150, 280, p2_color)
    jugador1["en_agua"] = True
    jugador2["en_agua"] = True

    caja = None

    # 1. Cámaras de aire (Zonas seguras de respiración y recarga de O2)
    camaras_aire = [
        {"rect": pygame.Rect(40, 160, 200, 260), "nombre": "Cámara 1: Refugio Inicial"},
        {"rect": pygame.Rect(860, 50, 190, 200), "nombre": "Cámara 2: Gruta Superior"},
        {"rect": pygame.Rect(1440, 420, 190, 225), "nombre": "Cámara 3: Fosa de la Llave"},
        {"rect": pygame.Rect(2020, 60, 190, 210), "nombre": "Cámara 4: Refugio Final"},
    ]

    # 2. Corrientes marinas dinámicas
    corrientes_marinas = [
        {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
        {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
        {"rect": pygame.Rect(1140, 140, 260, 380), "fuerza_x": 1.4, "fuerza_y": 2.4, "direccion": "abajo"},
        {"rect": pygame.Rect(1620, 360, 360, 280), "fuerza_x": -2.6, "fuerza_y": 0.0, "direccion": "izquierda"},
        {"rect": pygame.Rect(2180, 220, 240, 320), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
    ]

    # 3. Formaciones rocosas que definen el gran abismo submarino
    rocas_submarinas = [
        # Sector 1: Entrada y cámara inicial
        {"rect": pygame.Rect(260, techo_agua.bottom, 90, 260)},
        {"rect": pygame.Rect(260, 560, 90, suelo.top - 560)},

        # Sector 2: Estrecho de la corriente rápida
        {"rect": pygame.Rect(460, techo_agua.bottom, 180, 180)},
        {"rect": pygame.Rect(480, 560, 220, suelo.top - 560)},

        # Sector 2/3: Pilar del Geiser ascendente
        {"rect": pygame.Rect(720, 280, 70, suelo.top - 280)},
        {"rect": pygame.Rect(890, 250, 150, 260)},

        # Sector 3: Meseta central y desfiladero
        {"rect": pygame.Rect(1040, techo_agua.bottom, 120, 280)},
        {"rect": pygame.Rect(1180, 520, 220, suelo.top - 520)},

        # Sector 4: Techo de la Fosa de la Llave
        {"rect": pygame.Rect(1400, techo_agua.bottom, 220, 260)},
        {"rect": pygame.Rect(1640, techo_agua.bottom, 240, 230)},
        {"rect": pygame.Rect(1640, 480, 140, suelo.top - 480)},

        # Repisa abisal donde reposa la llave dorada
        {"rect": pygame.Rect(1780, 590, 110, suelo.top - 590), "coral": True, "color_coral": (255, 135, 70)},

        # Sector 5: Pared antes del refugio y terraza
        {"rect": pygame.Rect(1980, 270, 110, suelo.top - 270)},
        {"rect": pygame.Rect(2210, techo_agua.bottom, 180, 170)},
        {"rect": pygame.Rect(2210, 540, 180, suelo.top - 540)},

        # Terraza final de llegada con la puerta
        {"rect": pygame.Rect(2390, 440, 210, suelo.top - 440), "coral": True, "color_coral": (255, 140, 80)},
    ]

    barreras_algas = []

    # 4. Obstáculos mortales: erizos de mar puntiagudos
    pinchos = [
        # Sector 1/2: Corredor de la corriente
        crear_pincho(350, techo_agua.bottom, 110, 24, direccion="abajo"),
        crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),

        # Sector 2/3: Techo del geiser
        crear_pincho(780, techo_agua.bottom, 110, 24, direccion="abajo"),

        # Sector 3: Pared y lecho abisal
        crear_pincho(950, suelo.top - 24, 120, 24, direccion="arriba"),
        crear_pincho(1200, 520 - 24, 140, 24, direccion="arriba"),

        # Sector 4: Alrededores de la llave
        crear_pincho(1640, 480 - 24, 100, 24, direccion="arriba"),
        crear_pincho(1890, suelo.top - 24, 90, 24, direccion="arriba"),

        # Sector 5: Desfiladero final hacia la terraza
        crear_pincho(2180, 540 - 24, 120, 24, direccion="arriba"),
        crear_pincho(2210, techo_agua.bottom + 170, 100, 24, direccion="abajo"),
    ]

    plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
    plataformas = list(plataformas_base)

    # Llave escondida en la profunda repisa abisal
    llave = crear_llave(1820, 590 - 46)

    # Puerta de salida en la terraza final
    puerta = crear_puerta(2460, 440 - 90)

    # Corales decorativos en cámaras y terrazas
    corales_decorativos = [
        # Cámara 1
        {"tipo": "ramificado", "x": 120, "y": 420, "escala": 1.1, "fase": 0.5, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"},
        # Cámara 2
        {"tipo": "anemona", "x": 920, "y": 250, "escala": 1.2, "fase": 1.2, "color": (255, 210, 60), "color_sec": (255, 255, 180), "anclaje": "abajo"},
        {"tipo": "abanico", "x": 980, "y": 250, "escala": 1.0, "fase": 2.1, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"},
        # Cámara 3
        {"tipo": "cerebro", "x": 1500, "y": suelo.top, "escala": 1.15, "fase": 3.0, "color": (230, 110, 180), "color_sec": (255, 185, 225), "anclaje": "abajo"},
        {"tipo": "tubular", "x": 1560, "y": suelo.top, "escala": 1.05, "fase": 1.4, "color": (45, 195, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"},
        # Repisa de la llave
        {"tipo": "anemona", "x": 1845, "y": 590, "escala": 1.15, "fase": 1.8, "color": (255, 220, 70), "color_sec": (255, 255, 190), "anclaje": "abajo"},
        # Terraza de salida
        {"tipo": "ramificado", "x": 2420, "y": 440, "escala": 1.25, "fase": 0.8, "color": (255, 130, 70), "color_sec": (255, 200, 140), "anclaje": "abajo"},
        {"tipo": "abanico", "x": 2550, "y": 440, "escala": 1.15, "fase": 2.5, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"},
    ]

    algas_decorativas = [
        {"x": 60, "y": suelo.top, "alto": 120, "amplitud": 16, "fase": 0.0, "capa": "fondo"},
        {"x": 210, "y": suelo.top, "alto": 135, "amplitud": 18, "fase": 1.1, "capa": "fondo"},
        {"x": 680, "y": suelo.top, "alto": 110, "amplitud": 15, "fase": 2.5, "capa": "fondo"},
        {"x": 1340, "y": suelo.top, "alto": 130, "amplitud": 17, "fase": 0.9, "capa": "fondo"},
        {"x": 1720, "y": suelo.top, "alto": 140, "amplitud": 19, "fase": 3.1, "capa": "fondo"},
        {"x": 2080, "y": suelo.top, "alto": 125, "amplitud": 16, "fase": 1.8, "capa": "fondo"},
        {"x": 2350, "y": suelo.top, "alto": 135, "amplitud": 18, "fase": 0.6, "capa": "fondo"},
        {"x": 140, "y": suelo.top, "alto": 95, "amplitud": 14, "fase": 2.2, "capa": "frente"},
        {"x": 890, "y": suelo.top, "alto": 105, "amplitud": 15, "fase": 0.6, "capa": "frente"},
        {"x": 1600, "y": suelo.top, "alto": 110, "amplitud": 16, "fase": 3.4, "capa": "frente"},
        {"x": 2480, "y": suelo.top, "alto": 100, "amplitud": 15, "fase": 1.2, "capa": "frente"},
    ]

    # 5. Flechas indicadoras de navegación en paredes y superficies clave
    flechas_indicadoras = [
        # Sector 1: Salida de Cámara 1 hacia la corriente rápida
        {"x": 200, "y": 320, "direccion": "derecha", "tipo": "ruta"},
        # Sector 2: Impulso por la corriente marina
        {"x": 540, "y": 380, "direccion": "derecha", "tipo": "ruta"},
        # Sector 2/3: Ascenso del géiser hacia Cámara 2 (O2)
        {"x": 810, "y": 480, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 820, "y": 240, "direccion": "arriba", "tipo": "oxigeno"},
        # Sector 3: Salida de Cámara 2 y avance hacia la fosa
        {"x": 850, "y": 200, "direccion": "abajo", "tipo": "ruta"},
        {"x": 850, "y": 520, "direccion": "derecha", "tipo": "ruta"},
        # Sector 3: Descenso vertical por la corriente de la fosa
        {"x": 1110, "y": 350, "direccion": "abajo", "tipo": "ruta"},
        # Sector 4: Desvío hacia Cámara 3 (O2)
        {"x": 1360, "y": 480, "direccion": "derecha", "tipo": "oxigeno"},
        # Sector 4: Hacia la profunda repisa de la Llave
        {"x": 1660, "y": 430, "direccion": "derecha", "tipo": "llave"},
        {"x": 1810, "y": 500, "direccion": "abajo", "tipo": "llave"},
        # Sector 5: Chimenea vertical hacia Cámara 4 (Refugio Final O2)
        {"x": 1910, "y": 500, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 1940, "y": 230, "direccion": "derecha", "tipo": "oxigeno"},
        # Sector 5: Salida de Cámara 4 hacia la puerta
        {"x": 2180, "y": 250, "direccion": "derecha", "tipo": "salida"},
        # Terraza final: Conducción directa hacia la puerta de salida
        {"x": 2320, "y": 340, "direccion": "derecha", "tipo": "salida"},
        {"x": 2430, "y": 310, "direccion": "derecha", "tipo": "salida"},
    ]

    burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)
    tick_m3 = 0

    surf_oscuridad_m3 = pygame.Surface((ancho_mundo_nivel, ALTO), pygame.SRCALPHA)
    surf_luz_linterna, surf_luz_tenue = obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45)
    return locals()


NIVELES = {
    (1, 1): nivel_1_1,
    (1, 2): nivel_1_2,
    (1, 3): nivel_1_3,
    (1, 4): nivel_1_4,
    (1, 5): nivel_1_5,
    (2, 1): nivel_2_1,
    (2, 2): nivel_2_2,
    (2, 3): nivel_2_3,
    (2, 4): nivel_2_4,
    (2, 5): nivel_2_5,
    (3, 1): nivel_3_1,
    (3, 2): nivel_3_2,
    (3, 3): nivel_3_3,
    (3, 4): nivel_3_4,
    (3, 5): nivel_3_5,
}


def definir_nivel(numero_mundo, numero_nivel, p1_color, p2_color, bloques_peligrosos):
    """Devuelve el diccionario de variables del nivel, o None si el nivel no existe."""
    fn = NIVELES.get((numero_mundo, numero_nivel))
    if fn is None:
        return None
    return fn(p1_color, p2_color, bloques_peligrosos)
