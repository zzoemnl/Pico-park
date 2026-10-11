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
    crear_llave,
    crear_puerta,
    actualizar_llave,
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
COLOR_BOTON_SALIR = (150, 45, 45)
ANCHO_MUNDO = 3000
DISTANCIA_SPLIT = 850


def cargar_boton(nombre):
    ruta = os.path.join(RUTA_BOTONES, nombre)
    try:
        return pygame.image.load(ruta).convert_alpha()
    except (FileNotFoundError, pygame.error):
        return None


def animar_pulsacion_boton(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None):
    if fondo_limpio is None:
        try:
            fondo_limpio = pantalla.subsurface(rect).copy()
        except Exception:
            fondo_limpio = None

    if fondo_limpio:
        pantalla.blit(fondo_limpio, rect)
    if spr_semi:
        pantalla.blit(spr_semi, rect)
    pygame.display.flip()
    pygame.event.pump()
    pygame.time.delay(80)

    if fondo_limpio:
        pantalla.blit(fondo_limpio, rect)
    if spr_apretado:
        pantalla.blit(spr_apretado, rect)
    pygame.display.flip()
    pygame.event.pump()
    pygame.time.delay(120)


def pantalla_muerte(pantalla, reloj):
    fuente_titulo = pygame.font.Font(None, 60)
    fuente_texto = pygame.font.Font(None, 36)

    boton_salir_normal = cargar_boton("boton-salir.png")
    boton_salir_apretado = cargar_boton("boton-salir-apretado.png")
    boton_reiniciar_normal = cargar_boton("boton-reiniciar.png")
    boton_reiniciar_apretado = cargar_boton("boton-reiniciar-apretado.png")

    if any(x is None for x in (
        boton_salir_normal, boton_salir_apretado,
        boton_reiniciar_normal, boton_reiniciar_apretado
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


def mostrar_menu_victoria(pantalla):
    fuente_t = pygame.font.Font(None, 55)
    fuente_b = pygame.font.Font(None, 32)

    ancho_m, alto_m = pantalla.get_width(), pantalla.get_height()

    w_btn, h_btn = 260, 75
    espacio = 15
    total_h = 4 * h_btn + 3 * espacio
    y_base = (alto_m - total_h) // 2 + 35
    x_c = (ancho_m - w_btn) // 2

    def _cargar_img_btn(nombre):
        img = cargar_boton(nombre)
        if img is not None:
            return pygame.transform.scale(img, (w_btn, h_btn))
        return None

    botones_info = [
        {
            "rect": pygame.Rect(x_c, y_base, w_btn, h_btn),
            "texto": "Siguiente Nivel",
            "accion": "siguiente",
            "img_normal": _cargar_img_btn("boton-siguiente.png"),
            "img_apretado": _cargar_img_btn("boton-siguiente-apretado.png"),
        },
        {
            "rect": pygame.Rect(x_c, y_base + (h_btn + espacio), w_btn, h_btn),
            "texto": "Reiniciar",
            "accion": "reiniciar",
            "img_normal": _cargar_img_btn("boton-reiniciar.png"),
            "img_apretado": _cargar_img_btn("boton-reiniciar-apretado.png"),
        },
        {
            "rect": pygame.Rect(x_c, y_base + (h_btn + espacio) * 2, w_btn, h_btn),
            "texto": "Menú Principal",
            "accion": "menu",
            "img_normal": _cargar_img_btn("boton-menu.png"),
            "img_apretado": _cargar_img_btn("boton-menu-apretado.png"),
        },
        {
            "rect": pygame.Rect(x_c, y_base + (h_btn + espacio) * 3, w_btn, h_btn),
            "texto": "Salir del Juego",
            "accion": "salir",
            "img_normal": _cargar_img_btn("boton-salir.png"),
            "img_apretado": _cargar_img_btn("boton-salir-apretado.png"),
        },
    ]

    overlay = pygame.Surface((ancho_m, alto_m), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    def _dibujar_menu(boton_presionado=None):
        pantalla.blit(overlay, (0, 0))
        txt_win = fuente_t.render("¡NIVEL COMPLETADO!", True, (255, 220, 100))
        pantalla.blit(txt_win, txt_win.get_rect(center=(ancho_m // 2, y_base - 50)))

        for b in botones_info:
            r = b["rect"]
            es_presionado = (boton_presionado == b["accion"])
            img = b["img_apretado"] if (es_presionado and b["img_apretado"]) else b["img_normal"]

            if img is not None:
                pantalla.blit(img, r)
            else:
                color_fondo = (100, 100, 100) if es_presionado else (60, 60, 60)
                pygame.draw.rect(pantalla, color_fondo, r, border_radius=8)
                pygame.draw.rect(pantalla, (255, 255, 255), r, 2, border_radius=8)
                t = fuente_b.render(b["texto"], True, (255, 255, 255))
                pantalla.blit(t, t.get_rect(center=r.center))

    _dibujar_menu()
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for b in botones_info:
                    if b["rect"].collidepoint(evento.pos):
                        _dibujar_menu(boton_presionado=b["accion"])
                        pygame.display.flip()
                        pygame.time.delay(220)
                        return b["accion"]


def iniciar_mundo(mecanicas=None, numero_nivel=1, color_p1=None, color_p2=None):
    if mecanicas is None:
        mecanicas = []

    usar_caja = "caja" in mecanicas
    usar_soga = "soga" in mecanicas
    usar_agua = "agua" in mecanicas
    usar_pinchos = "pinchos" in mecanicas
    usar_llave = True

    pantalla = pygame.display.get_surface()
    if pantalla is None:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)

    mundo_rect = pygame.Rect(0, 0, ANCHO_MUNDO, ALTO)
    reloj = pygame.time.Clock()
    fuente_tut = pygame.font.Font(None, 32)

    TAM_BOTON_HUD = 92
    MARGEN_DER, MARGEN_SUP, ESPACIO_BOTONES = 25, 20, 16

    rect_btn_x = pygame.Rect(pantalla.get_width() - MARGEN_DER - TAM_BOTON_HUD, MARGEN_SUP, TAM_BOTON_HUD, TAM_BOTON_HUD)
    rect_btn_reiniciar = pygame.Rect(rect_btn_x.left - ESPACIO_BOTONES - TAM_BOTON_HUD, MARGEN_SUP, TAM_BOTON_HUD, TAM_BOTON_HUD)
    rect_btn_casa = pygame.Rect(rect_btn_reiniciar.left - ESPACIO_BOTONES - TAM_BOTON_HUD, MARGEN_SUP, TAM_BOTON_HUD, TAM_BOTON_HUD)

    def _cargar_hud(nombre):
        img = cargar_boton(nombre)
        return pygame.transform.scale(img, (TAM_BOTON_HUD, TAM_BOTON_HUD)) if img else None

    spr_x_normal = _cargar_hud("boton-x.png")
    spr_x_semi = _cargar_hud("boton-x-semiapretado.png")
    spr_x_apretado = _cargar_hud("boton-x-apretado.png")
    spr_reiniciar_normal = _cargar_hud("boton-reiniciar-icono.png")
    spr_reiniciar_semi = _cargar_hud("boton-reiniciar-icono-semiapretado.png")
    spr_reiniciar_apretado = _cargar_hud("boton-reiniciar-icono-apretado.png")
    spr_casa_normal = _cargar_hud("boton-casa.png")
    spr_casa_semi = _cargar_hud("boton-casa-semiapretado.png")
    spr_casa_apretado = _cargar_hud("boton-casa-apretado.png")

    fondo_btn_casa = None
    fondo_btn_reiniciar = None
    fondo_btn_x = None

    p1_color = color_p1 if color_p1 else COLOR_JUGADOR1
    p2_color = color_p2 if color_p2 else COLOR_JUGADOR2

    jugador1 = crear_personaje(100, 0, p1_color)
    jugador2 = crear_personaje(300, 0, p2_color)

    suelo = pygame.Rect(0, ALTO - 80, ANCHO_MUNDO, 80)
    caja = crear_caja(450, 0) if usar_caja else None
    pinchos = crear_pinchos(suelo.top) if usar_pinchos else []
    llave = crear_llave(1400, suelo.top - 46) if usar_llave else None
    puerta = crear_puerta(1900, suelo.top - 90) if usar_llave else None

    plataformas = []
    if numero_nivel == 1:
        plataformas.append(pygame.Rect(600, suelo.top - 170, 40, 170))

    if usar_soga:
        plataformas.extend([
            pygame.Rect(420, 530, 90, 30),
            pygame.Rect(530, 440, 90, 30),
            pygame.Rect(640, 350, 340, 35),
        ])

    if usar_agua:
        ZONA_AGUA.x, ZONA_AGUA.y = 0, 220
        ZONA_AGUA.width, ZONA_AGUA.height = ANCHO_MUNDO, suelo.top - 220

    p1_completado = False
    p2_completado = False

    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    if spr_reiniciar_semi and spr_reiniciar_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_reiniciar, spr_reiniciar_semi, spr_reiniciar_apretado, fondo_btn_reiniciar)
                    reiniciar_juego(jugador1, jugador2, caja, llave, puerta)
                    p1_completado, p2_completado = False, False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    if spr_x_semi and spr_x_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, fondo_btn_x)
                    pygame.quit()
                    sys.exit()

                if rect_btn_reiniciar.collidepoint(evento.pos):
                    if spr_reiniciar_semi and spr_reiniciar_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_reiniciar, spr_reiniciar_semi, spr_reiniciar_apretado, fondo_btn_reiniciar)
                    reiniciar_juego(jugador1, jugador2, caja, llave, puerta)
                    p1_completado, p2_completado = False, False

                if rect_btn_casa.collidepoint(evento.pos):
                    if spr_casa_semi and spr_casa_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_casa, spr_casa_semi, spr_casa_apretado, fondo_btn_casa)
                    return "menu"

        teclas = pygame.key.get_pressed()

        salto_p1_pedido = teclas[pygame.K_UP] and (puede_saltar(jugador1) if usar_agua else jugador1["en_suelo"])
        salto_p2_pedido = teclas[pygame.K_w] and (puede_saltar(jugador2) if usar_agua else jugador2["en_suelo"])

        p1_sobre_p2 = (
            not p1_completado and not p2_completado
            and abs(jugador1["hitbox"].bottom - jugador2["hitbox"].top) <= 8
            and jugador1["hitbox"].right > jugador2["hitbox"].left + 5
            and jugador1["hitbox"].left < jugador2["hitbox"].right - 5
        )
        p2_sobre_p1 = (
            not p1_completado and not p2_completado
            and abs(jugador2["hitbox"].bottom - jugador1["hitbox"].top) <= 8
            and jugador2["hitbox"].right > jugador1["hitbox"].left + 5
            and jugador2["hitbox"].left < jugador1["hitbox"].right - 5
        )

        if not jugador1["muerto"] and not p1_completado:
            jugador1["vel_x"] = 0
            jugador1["moviendo"] = False
            if teclas[pygame.K_LEFT]:
                jugador1["vel_x"] = -jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            if teclas[pygame.K_RIGHT]:
                jugador1["vel_x"] = jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            if salto_p1_pedido:
                impulso = 0
                if not usar_agua and p1_sobre_p2 and (salto_p2_pedido or jugador2["vel_y"] < 0):
                    impulso = -4.5
                jugador1["vel_y"] = jugador1["fuerza_salto"] + impulso
                jugador1["en_suelo"] = False

        if not jugador2["muerto"] and not p2_completado:
            jugador2["vel_x"] = 0
            jugador2["moviendo"] = False
            if teclas[pygame.K_a]:
                jugador2["vel_x"] = -jugador2["velocidad_mov"]
                jugador2["moviendo"] = True
            if teclas[pygame.K_d]:
                jugador2["vel_x"] = jugador2["velocidad_mov"]
                jugador2["moviendo"] = True
            if salto_p2_pedido:
                impulso = 0
                if not usar_agua and p2_sobre_p1 and (salto_p1_pedido or jugador1["vel_y"] < 0):
                    impulso = -4.5
                jugador2["vel_y"] = jugador2["fuerza_salto"] + impulso
                jugador2["en_suelo"] = False

        if usar_agua:
            actualizar_estado_agua(jugador1)
            actualizar_estado_agua(jugador2)
            if jugador1["en_agua"]: aplicar_fisica_agua(jugador1, teclas[pygame.K_UP], teclas[pygame.K_DOWN])
            if jugador2["en_agua"]: aplicar_fisica_agua(jugador2, teclas[pygame.K_w], teclas[pygame.K_s])

        if usar_caja: actualizar_caja(caja, suelo, mundo_rect, plataformas)

        if not jugador1["muerto"] and not p1_completado:
            resolver_colisiones(jugador1, jugador2 if not p2_completado else None, suelo, mundo_rect, caja if usar_caja else None, jugador1["en_agua"], plataformas)
        if not jugador2["muerto"] and not p2_completado:
            resolver_colisiones(jugador2, jugador1 if not p1_completado else None, suelo, mundo_rect, caja if usar_caja else None, jugador2["en_agua"], plataformas)

        if usar_soga and not p1_completado and not p2_completado:
            aplicar_restriccion_soga(jugador1, jugador2, DISTANCIA_SOGA, plataformas, suelo)
        if usar_llave:
            personajes_activos = [p for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)] if not comp]
            actualizar_llave(llave, personajes_activos, puerta)
        if usar_pinchos:
            if not p1_completado: comprobar_pinchos(jugador1, pinchos)
            if not p2_completado: comprobar_pinchos(jugador2, pinchos)

        actualizar_muerte(jugador1)
        actualizar_muerte(jugador2)

        if not jugador1["muerto"] and not p1_completado: jugador1["hitbox"].clamp_ip(mundo_rect)
        if not jugador2["muerto"] and not p2_completado: jugador2["hitbox"].clamp_ip(mundo_rect)

        if puerta and puerta["abierta"]:
            if not p1_completado and jugador1["hitbox"].colliderect(puerta["rect"]):
                p1_completado = True
                jugador1["hitbox"].x = -9999
            if not p2_completado and jugador2["hitbox"].colliderect(puerta["rect"]):
                p2_completado = True
                jugador2["hitbox"].x = -9999

        mundo = pygame.Surface((ANCHO_MUNDO, ALTO))
        mundo.fill((255, 240, 195))
        pygame.draw.rect(mundo, (225, 110, 80), suelo)

        for plat in plataformas:
            pygame.draw.rect(mundo, (110, 110, 115), plat, border_radius=4)

        if usar_agua: dibujar_agua(mundo)
        if usar_soga:
            pygame.draw.line(mundo, COLOR_SOGA, jugador1["hitbox"].center, jugador2["hitbox"].center, 4)
        if usar_caja: mundo.blit(caja["sprite"], caja["rect"])

        if usar_llave:
            estado_p = "abierta" if puerta["abierta"] else "cerrada"
            mundo.blit(puerta["sprites"][estado_p], puerta["rect"])
            if llave and not puerta["abierta"]:
                mundo.blit(llave["sprite"], llave["rect"])

        if not p1_completado: dibujar_personaje(mundo, jugador1, ZONA_AGUA if usar_agua else None)
        if not p2_completado: dibujar_personaje(mundo, jugador2, ZONA_AGUA if usar_agua else None)

        if p1_completado and not p2_completado:
            # Jugador 1 ya pasó por la puerta: cámara completa siguiendo al Jugador 2
            cam_x = max(0, min(jugador2["hitbox"].centerx - ANCHO // 2, ANCHO_MUNDO - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif p2_completado and not p1_completado:
            # Jugador 2 ya pasó por la puerta: cámara completa siguiendo al Jugador 1
            cam_x = max(0, min(jugador1["hitbox"].centerx - ANCHO // 2, ANCHO_MUNDO - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        else:
            # Ambos personajes están en juego
            distancia = abs(jugador1["hitbox"].centerx - jugador2["hitbox"].centerx)
            if distancia <= DISTANCIA_SPLIT:
                centro = (jugador1["hitbox"].centerx + jugador2["hitbox"].centerx) // 2
                cam_x = max(0, min(centro - ANCHO // 2, ANCHO_MUNDO - ANCHO))
                pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
            else:
                ancho_m = ANCHO // 2
                if jugador1["hitbox"].centerx <= jugador2["hitbox"].centerx:
                    p_izq, p_der = jugador1, jugador2
                else:
                    p_izq, p_der = jugador2, jugador1

                cam_izq_x = max(0, min(p_izq["hitbox"].centerx - ancho_m // 2, ANCHO_MUNDO - ancho_m))
                cam_der_x = max(0, min(p_der["hitbox"].centerx - ancho_m // 2, ANCHO_MUNDO - ancho_m))

                pantalla.blit(mundo, (0, 0), pygame.Rect(cam_izq_x, 0, ancho_m, ALTO))
                pantalla.blit(mundo, (ancho_m, 0), pygame.Rect(cam_der_x, 0, ancho_m, ALTO))
                pygame.draw.line(pantalla, (0, 0, 0), (ancho_m, 0), (ancho_m, ALTO), 4)

        if numero_nivel == 1:
            txt1 = fuente_tut.render("P1: Flechas (Mover / Saltar)", True, (20, 20, 20))
            txt2 = fuente_tut.render("P2: W A S D (Mover / Saltar)", True, (20, 20, 20))
            pantalla.blit(txt1, (40, 100))
            pantalla.blit(txt2, (40, 135))

        try:
            fondo_btn_casa = pantalla.subsurface(rect_btn_casa).copy()
            fondo_btn_reiniciar = pantalla.subsurface(rect_btn_reiniciar).copy()
            fondo_btn_x = pantalla.subsurface(rect_btn_x).copy()
        except Exception:
            pass

        if spr_casa_normal: pantalla.blit(spr_casa_normal, rect_btn_casa)
        if spr_reiniciar_normal: pantalla.blit(spr_reiniciar_normal, rect_btn_reiniciar)
        if spr_x_normal: pantalla.blit(spr_x_normal, rect_btn_x)

        pygame.display.flip()

        if jugador1["muerte_terminada"] or jugador2["muerte_terminada"]:
            resultado = pantalla_muerte(pantalla, reloj)
            if resultado == "salir": return "salir"
            if resultado == "reiniciar":
                reiniciar_juego(jugador1, jugador2, caja, llave, puerta)
                p1_completado, p2_completado = False, False

        if p1_completado and p2_completado:
            return mostrar_menu_victoria(pantalla)

    return "salir"