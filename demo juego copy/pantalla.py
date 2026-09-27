import os
import sys
import pygame

from sprites import (
    ANCHO, ALTO, FPS,
    COLOR_JUGADOR1, COLOR_JUGADOR2,
    RUTA_BOTONES,
    dibujar_personaje,
)
from movimientos import (
    DISTANCIA_SOGA,
    crear_personaje,
    crear_caja,
    crear_pinchos,
    reiniciar_juego,
    resolver_colisiones,
    actualizar_caja,
    transportar_personaje_encima,
    aplicar_restriccion_soga,
    comprobar_pinchos,
    actualizar_muerte,
)
from agua import (
    ZONA_AGUA,
    actualizar_estado_agua,
    aplicar_fisica_agua,
    puede_saltar,
    dibujar_agua,
)

COLOR_SOGA = (200, 160, 100)


def dibujar_soga(pantalla, p1, p2):
    pygame.draw.line(
        pantalla,
        COLOR_SOGA,
        p1["hitbox"].center,
        p2["hitbox"].center,
        4,
    )


def dibujar_pinchos(pantalla, pinchos):
    for pincho in pinchos:
        puntos = [
            (pincho.left, pincho.bottom),
            (pincho.centerx, pincho.top),
            (pincho.right, pincho.bottom),
        ]
        pygame.draw.polygon(pantalla, (220, 220, 220), puntos)
        pygame.draw.polygon(pantalla, (80, 80, 80), puntos, 2)


def cargar_boton(nombre):
    ruta = os.path.join(RUTA_BOTONES, nombre)
    try:
        return pygame.image.load(ruta).convert_alpha()
    except (FileNotFoundError, pygame.error):
        return None


def pantalla_muerte(pantalla, reloj):
    fuente_titulo = pygame.font.Font(None, 60)
    fuente_texto = pygame.font.Font(None, 36)

    boton_salir_normal = cargar_boton("boton-salir.png")
    boton_salir_apretado = cargar_boton("boton-salir-apretado.png")
    boton_reiniciar_normal = cargar_boton("boton-reiniciar.png")
    boton_reiniciar_apretado = cargar_boton("boton-reiniciar-apretado.png")

    if any(x is None for x in (
        boton_salir_normal,
        boton_salir_apretado,
        boton_reiniciar_normal,
        boton_reiniciar_apretado,
    )):
        return "salir"

    boton_reiniciar_normal = pygame.transform.scale(boton_reiniciar_normal, (260, 80))
    boton_reiniciar_apretado = pygame.transform.scale(boton_reiniciar_apretado, (260, 80))
    boton_salir_normal = pygame.transform.scale(boton_salir_normal, (260, 80))
    boton_salir_apretado = pygame.transform.scale(boton_salir_apretado, (260, 80))

    boton_reiniciar = boton_reiniciar_normal.get_rect(center=(ANCHO // 2 - 150, 400))
    boton_salir = boton_salir_normal.get_rect(center=(ANCHO // 2 + 150, 400))

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_reiniciar.collidepoint(evento.pos):
                    pantalla.blit(boton_reiniciar_apretado, boton_reiniciar)
                    pygame.display.flip()
                    pygame.time.delay(300)
                    return "reiniciar"

                if boton_salir.collidepoint(evento.pos):
                    pantalla.blit(boton_salir_apretado, boton_salir)
                    pygame.display.flip()
                    pygame.time.delay(300)
                    return "salir"

        pantalla.fill((25, 25, 25))
        titulo = fuente_titulo.render("¡Te moriste!", True, (255, 80, 80))
        texto = fuente_texto.render("¿Querés reiniciar o salir?", True, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 180)))
        pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 250)))
        pantalla.blit(boton_reiniciar_normal, boton_reiniciar)
        pantalla.blit(boton_salir_normal, boton_salir)
        pygame.display.flip()
        reloj.tick(FPS)


def dibujar_boton_salir_mundo(pantalla, boton, imagen_normal):
    if imagen_normal is not None:
        pantalla.blit(imagen_normal, boton)
    else:
        pygame.draw.rect(pantalla, (70, 70, 70), boton, border_radius=8)
        pygame.draw.rect(pantalla, (255, 255, 255), boton, 2, border_radius=8)
        fuente = pygame.font.Font(None, 28)
        texto = fuente.render("SALIR", True, (255, 255, 255))
        pantalla.blit(texto, texto.get_rect(center=boton.center))


def iniciar_mundo(mecanicas=None):
    """
    Inicia un mundo con la estructura común del juego.

    Ejemplos:
        iniciar_mundo(["caja"])
        iniciar_mundo(["soga"])
        iniciar_mundo(["agua"])
        iniciar_mundo(["pinchos"])
        iniciar_mundo(["caja", "soga", "agua"])
    """

    if mecanicas is None:
        mecanicas = []

    usar_caja = "caja" in mecanicas
    usar_soga = "soga" in mecanicas
    usar_agua = "agua" in mecanicas
    usar_pinchos = "pinchos" in mecanicas

    pantalla = pygame.display.get_surface()
    if pantalla is None:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))

    pantalla_rect = pantalla.get_rect()
    reloj = pygame.time.Clock()

    jugador1 = crear_personaje(100, 0, COLOR_JUGADOR1)
    jugador2 = crear_personaje(300, 0, COLOR_JUGADOR2)

    suelo = pygame.Rect(0, 520, ANCHO, 80)
    caja = crear_caja(450, 0) if usar_caja else None
    pinchos = crear_pinchos() if usar_pinchos else []

    # Botón de salida disponible durante TODO el mundo.
    boton_salir_normal = cargar_boton("boton-salir.png")
    boton_salir_apretado = cargar_boton("boton-salir-apretado.png")
    if boton_salir_normal is not None:
        boton_salir_normal = pygame.transform.scale(boton_salir_normal, (150, 50))
    if boton_salir_apretado is not None:
        boton_salir_apretado = pygame.transform.scale(boton_salir_apretado, (150, 50))

    boton_salir = pygame.Rect(ANCHO - 170, 15, 150, 50)

    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                reiniciar_juego(jugador1, jugador2, caja)

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    if boton_salir_apretado is not None:
                        pantalla.blit(boton_salir_apretado, boton_salir)
                        pygame.display.flip()
                        pygame.time.delay(250)
                    return "salir"

        teclas = pygame.key.get_pressed()

        # ====================================================
        # MOVIMIENTO BÁSICO
        # ====================================================

        if not jugador1["muerto"]:
            jugador1["vel_x"] = 0
            jugador1["moviendo"] = False

            if teclas[pygame.K_LEFT]:
                jugador1["vel_x"] = -jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            if teclas[pygame.K_RIGHT]:
                jugador1["vel_x"] = jugador1["velocidad_mov"]
                jugador1["moviendo"] = True

            if teclas[pygame.K_UP]:
                puede_saltar_1 = (
                    puede_saltar(jugador1)
                    if usar_agua
                    else jugador1["en_suelo"] and not jugador1["muerto"]
                )
                if puede_saltar_1:
                    jugador1["vel_y"] = jugador1["fuerza_salto"]
                    jugador1["en_suelo"] = False

        if not jugador2["muerto"]:
            jugador2["vel_x"] = 0
            jugador2["moviendo"] = False

            if teclas[pygame.K_a]:
                jugador2["vel_x"] = -jugador2["velocidad_mov"]
                jugador2["moviendo"] = True
            if teclas[pygame.K_d]:
                jugador2["vel_x"] = jugador2["velocidad_mov"]
                jugador2["moviendo"] = True

            if teclas[pygame.K_w]:
                puede_saltar_2 = (
                    puede_saltar(jugador2)
                    if usar_agua
                    else jugador2["en_suelo"] and not jugador2["muerto"]
                )
                if puede_saltar_2:
                    jugador2["vel_y"] = jugador2["fuerza_salto"]
                    jugador2["en_suelo"] = False

        # ====================================================
        # AGUA
        # ====================================================

        if usar_agua:
            actualizar_estado_agua(jugador1)
            actualizar_estado_agua(jugador2)

            if jugador1["en_agua"]:
                aplicar_fisica_agua(
                    jugador1,
                    teclas[pygame.K_UP],
                    teclas[pygame.K_DOWN],
                )

            if jugador2["en_agua"]:
                aplicar_fisica_agua(
                    jugador2,
                    teclas[pygame.K_w],
                    teclas[pygame.K_s],
                )
        else:
            jugador1["en_agua"] = False
            jugador2["en_agua"] = False

        # ====================================================
        # CAJA
        # ====================================================

        if usar_caja:
            actualizar_caja(caja, suelo, pantalla_rect)

        # ====================================================
        # COLISIONES BÁSICAS
        # ====================================================

        if not jugador1["muerto"]:
            resolver_colisiones(
                jugador1,
                jugador2,
                suelo,
                pantalla_rect,
                caja if usar_caja else None,
            )

        if not jugador2["muerto"]:
            resolver_colisiones(
                jugador2,
                jugador1,
                suelo,
                pantalla_rect,
                caja if usar_caja else None,
            )

        transportar_personaje_encima(jugador1, jugador2)
        transportar_personaje_encima(jugador2, jugador1)

        # ====================================================
        # SOGA
        # ====================================================

        if usar_soga:
            aplicar_restriccion_soga(jugador1, jugador2, DISTANCIA_SOGA)

        # ====================================================
        # PINCHOS
        # ====================================================

        if usar_pinchos:
            comprobar_pinchos(jugador1, pinchos)
            comprobar_pinchos(jugador2, pinchos)

        actualizar_muerte(jugador1)
        actualizar_muerte(jugador2)

        # Los personajes vivos sí respetan los bordes.
        # Los muertos NO se limitan: tienen que poder caer fuera de pantalla.
        if not jugador1["muerto"]:
            jugador1["hitbox"].clamp_ip(pantalla_rect)
        if not jugador2["muerto"]:
            jugador2["hitbox"].clamp_ip(pantalla_rect)

        # ====================================================
        # DIBUJADO
        # ====================================================

        pantalla.fill((30, 30, 30))
        pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        if usar_agua:
            dibujar_agua(pantalla)
        if usar_soga:
            dibujar_soga(pantalla, jugador1, jugador2)
        if usar_caja:
            pantalla.blit(caja["sprite"], caja["rect"])
        if usar_pinchos:
            dibujar_pinchos(pantalla, pinchos)

        dibujar_personaje(
            pantalla,
            jugador1,
            ZONA_AGUA if usar_agua else None,
        )
        dibujar_personaje(
            pantalla,
            jugador2,
            ZONA_AGUA if usar_agua else None,
        )

        dibujar_boton_salir_mundo(pantalla, boton_salir, boton_salir_normal)

        pygame.display.flip()

        if jugador1["muerte_terminada"] or jugador2["muerte_terminada"]:
            resultado = pantalla_muerte(pantalla, reloj)

            if resultado == "salir":
                return "salir"

            if resultado == "reiniciar":
                reiniciar_juego(jugador1, jugador2, caja)

    return "salir"
