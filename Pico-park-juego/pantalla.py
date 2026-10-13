import os
import sys
import pygame

from sprites import (
    ANCHO, ALTO, FPS,
    COLOR_JUGADOR1, COLOR_JUGADOR2,
    RUTA_BOTONES, DIRECTORIO_ACTUAL,
    dibujar_personaje,
)
from movimientos import (
    ALTO_HITBOX,
    ANCHO_HITBOX,
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
    def _cargar(ruta_archivo):
        try:
            img = pygame.image.load(ruta_archivo)
            try:
                return img.convert_alpha()
            except pygame.error:
                return img
        except (FileNotFoundError, pygame.error):
            return None

    ruta = os.path.join(RUTA_BOTONES, nombre)
    if os.path.isfile(ruta):
        res = _cargar(ruta)
        if res:
            return res

    for raiz, _, archivos in os.walk(RUTA_BOTONES):
        if nombre in archivos:
            res = _cargar(os.path.join(raiz, nombre))
            if res:
                return res

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

    boton_salir_normal = cargar_boton("salir.png") or cargar_boton("boton-salir.png")
    boton_salir_semi = cargar_boton("salir-preapretado.png")
    boton_salir_apretado = cargar_boton("salir-apretado.png") or cargar_boton("boton-salir-apretado.png")
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
    if boton_salir_semi:
        boton_salir_semi = pygame.transform.scale(boton_salir_semi, (260, 80))
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
                    if boton_salir_semi and boton_salir_apretado:
                        fondo_m = pygame.Surface(boton_salir.size)
                        fondo_m.fill((25, 25, 25))
                        animar_pulsacion_boton(pantalla, boton_salir, boton_salir_semi, boton_salir_apretado, fondo_m)
                    else:
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
            "img_normal": _cargar_img_btn("salir.png") or _cargar_img_btn("boton-salir.png"),
            "img_semi": _cargar_img_btn("salir-preapretado.png"),
            "img_apretado": _cargar_img_btn("salir-apretado.png") or _cargar_img_btn("boton-salir-apretado.png"),
        },
    ]

    overlay = pygame.Surface((ancho_m, alto_m), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    def _dibujar_menu(boton_presionado=None, estado_anim=None):
        pantalla.blit(overlay, (0, 0))
        txt_win = fuente_t.render("¡NIVEL COMPLETADO!", True, (255, 220, 100))
        pantalla.blit(txt_win, txt_win.get_rect(center=(ancho_m // 2, y_base - 50)))

        for b in botones_info:
            r = b["rect"]
            es_presionado = (boton_presionado == b["accion"])
            if es_presionado and estado_anim == "semi" and b.get("img_semi"):
                img = b["img_semi"]
            elif es_presionado and b.get("img_apretado"):
                img = b["img_apretado"]
            else:
                img = b["img_normal"]

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
                        if b.get("img_semi") and b.get("img_apretado"):
                            _dibujar_menu(boton_presionado=b["accion"], estado_anim="semi")
                            pygame.display.flip()
                            pygame.event.pump()
                            pygame.time.delay(80)
                            _dibujar_menu(boton_presionado=b["accion"], estado_anim="apretado")
                            pygame.display.flip()
                            pygame.event.pump()
                            pygame.time.delay(120)
                        else:
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

    # Configuración de botones e indicadores para Tutorial (Nivel 1)
    TAM_BTN_TUT = 32
    GAP_BTN_TUT = 3

    COLORES_PERSONAJES = {
        "Blanco": (232, 232, 232),
        "Gris": (154, 154, 154),
        "Negro": (95, 95, 95),
        "Marron": (206, 136, 111),
        "Rojo": (255, 137, 134),
        "Rosa": (255, 150, 240),
        "Naranja": (255, 160, 100),
        "Amarillo": (255, 244, 123),
        "Verde": (157, 255, 124),
        "Verde oscuro": (105, 205, 75),
        "Celeste": (124, 231, 255),
        "Azul": (36, 166, 247),
        "Violeta": (161, 123, 255),
    }

    def _cargar_o_crear_boton(nombres_posibles, letra_fallback):
        img = None
        for nombre in nombres_posibles:
            img = cargar_boton(nombre)
            if img is not None:
                break

        if img is not None:
            try:
                mask = pygame.mask.from_surface(img)
                rects = mask.get_bounding_rects()
                if rects:
                    img = img.subsurface(rects[0])
            except Exception:
                pass
            return pygame.transform.smoothscale(img, (TAM_BTN_TUT, TAM_BTN_TUT))

        # Botón procedimental si no encuentra la imagen (mismo diseño de tecla roja)
        surf = pygame.Surface((TAM_BTN_TUT, TAM_BTN_TUT), pygame.SRCALPHA)
        color_fondo = (237, 112, 109)
        color_borde = (94, 4, 4)
        color_sombra = (237, 86, 83)
        color_letra = (94, 4, 4)

        pygame.draw.rect(surf, color_fondo, (0, 0, TAM_BTN_TUT, TAM_BTN_TUT), border_radius=6)
        pygame.draw.rect(surf, color_sombra, (2, TAM_BTN_TUT - 5, TAM_BTN_TUT - 4, 3), border_bottom_left_radius=4, border_bottom_right_radius=4)
        pygame.draw.rect(surf, color_borde, (0, 0, TAM_BTN_TUT, TAM_BTN_TUT), width=2, border_radius=6)

        fuente_tecla = pygame.font.SysFont("Arial", int(TAM_BTN_TUT * 0.58), bold=True)
        txt_surf = fuente_tecla.render(str(letra_fallback).upper(), True, color_letra)
        rect_txt = txt_surf.get_rect(center=(TAM_BTN_TUT // 2, TAM_BTN_TUT // 2 - 1))
        surf.blit(txt_surf, rect_txt)
        return surf

    def _crear_etiqueta_jugador(texto, color_nombre):
        color_base = COLORES_PERSONAJES.get(color_nombre, (124, 231, 255))
        color_borde = (max(0, color_base[0] - 65), max(0, color_base[1] - 65), max(0, color_base[2] - 65))
        fuente = pygame.font.SysFont("Arial", 16, bold=True)
        t_base = fuente.render(texto, True, (25, 35, 45))
        w, h = t_base.get_size()
        ancho_cartel = max(w + 14, 40)
        alto_cartel = h + 4
        surf = pygame.Surface((ancho_cartel, alto_cartel), pygame.SRCALPHA)
        pygame.draw.rect(surf, color_base, (0, 0, ancho_cartel, alto_cartel), border_radius=6)
        pygame.draw.rect(surf, color_borde, (0, 0, ancho_cartel, alto_cartel), width=2, border_radius=6)
        rect_txt = t_base.get_rect(center=(ancho_cartel // 2, alto_cartel // 2))
        surf.blit(t_base, rect_txt)
        return surf

    # Cargar botones WASD para Jugador 1 (P1: W arriba, A izquierda, S abajo, D derecha)
    btn_w = _cargar_o_crear_boton(["boton-w.png", "boton-W.png", "w.png", "W.png"], "W")
    btn_s = _cargar_o_crear_boton(["boton-s.png", "boton-S.png", "s.png", "S.png"], "S")
    btn_a = _cargar_o_crear_boton(["boton-a.png", "boton-A.png", "a.png", "A.png"], "A")
    btn_d = _cargar_o_crear_boton(["boton-d.png", "boton-D.png", "d.png", "D.png"], "D")
    badge_p1 = _crear_etiqueta_jugador("P1", p1_color)

    # Cargar botones Flechas para Jugador 2 (P2: Flecha arriba, flecha izquierda, flecha abajo, flecha derecha)
    btn_arr = _cargar_o_crear_boton(["boton-arriba.png", "arriba.png"], "↑")
    btn_aba = _cargar_o_crear_boton(["boton-abajo.png", "abajo.png"], "↓")
    btn_izq = _cargar_o_crear_boton(["boton-izquierda.png", "izquierda.png"], "←")
    btn_der = _cargar_o_crear_boton(["boton-derecha.png", "derecha.png"], "→")
    badge_p2 = _crear_etiqueta_jugador("P2", p2_color)

    def _dibujar_cluster_jugador(superficie, jugador, badge, btn_arriba, btn_izq, btn_abajo, btn_der, k_arriba, k_izq, k_abajo, k_der, teclas_presionadas, alpha=255, bottom_override=None):
        if jugador.get("muerto", False):
            return 0

        ancho_grid = 3 * TAM_BTN_TUT + 2 * GAP_BTN_TUT
        alto_grid = 2 * TAM_BTN_TUT + GAP_BTN_TUT
        alto_total = badge.get_height() + 4 + alto_grid

        surf_total = pygame.Surface((ancho_grid, alto_total), pygame.SRCALPHA)

        # 1. Badge centrado arriba
        badge_x = (ancho_grid - badge.get_width()) // 2
        surf_total.blit(badge, (badge_x, 0))

        # 2. Teclas abajo del badge
        y_grid_offset = badge.get_height() + 4
        col0_x = 0
        col1_x = TAM_BTN_TUT + GAP_BTN_TUT
        col2_x = 2 * (TAM_BTN_TUT + GAP_BTN_TUT)
        row1_y = TAM_BTN_TUT + GAP_BTN_TUT

        press_arriba = teclas_presionadas[k_arriba] if teclas_presionadas else False
        press_izq = teclas_presionadas[k_izq] if teclas_presionadas else False
        press_abajo = teclas_presionadas[k_abajo] if teclas_presionadas else False
        press_der = teclas_presionadas[k_der] if teclas_presionadas else False

        surf_total.blit(btn_arriba, (col1_x, y_grid_offset + (2 if press_arriba else 0)))
        surf_total.blit(btn_izq, (col0_x, y_grid_offset + row1_y + (2 if press_izq else 0)))
        surf_total.blit(btn_abajo, (col1_x, y_grid_offset + row1_y + (2 if press_abajo else 0)))
        surf_total.blit(btn_der, (col2_x, y_grid_offset + row1_y + (2 if press_der else 0)))

        if alpha < 255:
            surf_total.set_alpha(alpha)

        bottom_y = bottom_override if bottom_override is not None else (jugador["hitbox"].top - 8)
        dest_rect = surf_total.get_rect(centerx=jugador["hitbox"].centerx, bottom=bottom_y)
        superficie.blit(surf_total, dest_rect)
        return alto_total

    def _dibujar_controles_tutorial(superficie, alpha_p1=255, alpha_p2=255, teclas_actuales=None):
        if teclas_actuales is None:
            teclas_actuales = pygame.key.get_pressed()

        # Determinar posición vertical si uno está parado sobre el otro
        bottom_p1 = jugador1["hitbox"].top - 8
        bottom_p2 = jugador2["hitbox"].top - 8

        if p1_sobre_p2:
            h_p1 = badge_p1.get_height() + 4 + (2 * TAM_BTN_TUT + GAP_BTN_TUT)
            bottom_p2 = bottom_p1 - h_p1 - 6
        elif p2_sobre_p1:
            h_p2 = badge_p2.get_height() + 4 + (2 * TAM_BTN_TUT + GAP_BTN_TUT)
            bottom_p1 = bottom_p2 - h_p2 - 6

        # Dibujar WASD directamente sobre Jugador 1
        if not p1_completado and not jugador1["muerto"] and alpha_p1 > 0:
            _dibujar_cluster_jugador(
                superficie, jugador1, badge_p1,
                btn_w, btn_a, btn_s, btn_d,
                pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                teclas_actuales, alpha=int(alpha_p1), bottom_override=bottom_p1
            )

        # Dibujar Flechas directamente sobre Jugador 2
        if not p2_completado and not jugador2["muerto"] and alpha_p2 > 0:
            _dibujar_cluster_jugador(
                superficie, jugador2, badge_p2,
                btn_arr, btn_izq, btn_aba, btn_der,
                pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT,
                teclas_actuales, alpha=int(alpha_p2), bottom_override=bottom_p2
            )

    if numero_nivel == 1:
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
        # Ambos personajes inician sobre el suelo principal
        jugador1 = crear_personaje(120, suelo.top - ALTO_HITBOX, p1_color)
        jugador2 = crear_personaje(240, suelo.top - ALTO_HITBOX, p2_color)

        caja = None
        pinchos = []

        # Segunda zona: plataformas bajas y pequeñas para practicar saltos
        plataformas = [
            # Obstáculo bajo en el suelo (45px de altura, para saltar por encima o subirse)
            pygame.Rect(540, suelo.top - 45, 80, 45),
            # Plataforma flotante baja (a 70px de altura para saltar y aterrizar encima)
            pygame.Rect(710, suelo.top - 70, 120, 24),
            # Secuencia de plataformas bajas a alturas cómodas y con espacio amplio
            pygame.Rect(890, suelo.top - 60, 110, 24),
            pygame.Rect(1070, suelo.top - 95, 120, 24),
            # Tercera zona: plataforma baja donde se ubica la llave accesible
            pygame.Rect(1300, suelo.top - 60, 90, 24),
        ]

        # Tercera zona: llave visible accesible sobre la plataforma
        llave = crear_llave(1332, suelo.top - 60 - 46)
        # Cuarta zona: puerta de salida al final del recorrido
        puerta = crear_puerta(1750, suelo.top - 90)
    else:
        ancho_mundo_nivel = ANCHO_MUNDO
        suelo = pygame.Rect(0, ALTO - 80, ANCHO_MUNDO, 80)
        mundo_rect = pygame.Rect(0, 0, ANCHO_MUNDO, ALTO)

        jugador1 = crear_personaje(100, 0, p1_color)
        jugador2 = crear_personaje(300, 0, p2_color)

        caja = crear_caja(450, 0) if usar_caja else None
        pinchos = crear_pinchos(suelo.top) if usar_pinchos else []
        llave = crear_llave(1400, suelo.top - 46) if usar_llave else None
        puerta = crear_puerta(1900, suelo.top - 90) if usar_llave else None

        plataformas = []
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
    mostrar_tutorial = (numero_nivel == 1)
    contador_tutorial = 0
    frames_tutorial = 300  # Los controles duran 5 segundos antes de despejar la pantalla
    p1_movio = False
    p2_movio = False
    alpha_tut_p1 = 255.0
    alpha_tut_p2 = 255.0

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
                    mostrar_tutorial = (numero_nivel == 1)
                    contador_tutorial = 0
                    p1_movio = False
                    p2_movio = False
                    alpha_tut_p1 = 255.0
                    alpha_tut_p2 = 255.0

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
                    mostrar_tutorial = (numero_nivel == 1)
                    contador_tutorial = 0
                    p1_movio = False
                    p2_movio = False
                    alpha_tut_p1 = 255.0
                    alpha_tut_p2 = 255.0

                if rect_btn_casa.collidepoint(evento.pos):
                    if spr_casa_semi and spr_casa_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_casa, spr_casa_semi, spr_casa_apretado, fondo_btn_casa)
                    return "menu"

        teclas = pygame.key.get_pressed()

        salto_p1_pedido = teclas[pygame.K_w] and (puede_saltar(jugador1) if usar_agua else jugador1["en_suelo"])
        salto_p2_pedido = teclas[pygame.K_UP] and (puede_saltar(jugador2) if usar_agua else jugador2["en_suelo"])

        if mostrar_tutorial:
            contador_tutorial += 1

            # Detectar si Jugador 1 se mueve (WASD o salto)
            if not p1_movio and not p1_completado and not jugador1["muerto"]:
                if (
                    teclas[pygame.K_a] or teclas[pygame.K_d] or salto_p1_pedido
                    or (usar_agua and (teclas[pygame.K_w] or teclas[pygame.K_s]))
                    or jugador1["moviendo"]
                ):
                    p1_movio = True

            # Detectar si Jugador 2 se mueve (Flechas o salto)
            if not p2_movio and not p2_completado and not jugador2["muerto"]:
                if (
                    teclas[pygame.K_LEFT] or teclas[pygame.K_RIGHT] or salto_p2_pedido
                    or (usar_agua and (teclas[pygame.K_UP] or teclas[pygame.K_DOWN]))
                    or jugador2["moviendo"]
                ):
                    p2_movio = True

            # Desvanecer los controles de P1 al moverse
            if p1_movio:
                alpha_tut_p1 = max(0.0, alpha_tut_p1 - 25.0)
            elif contador_tutorial > 240:
                alpha_tut_p1 = max(0.0, 255.0 * (1.0 - (contador_tutorial - 240) / 60.0))

            # Desvanecer los controles de P2 al moverse
            if p2_movio:
                alpha_tut_p2 = max(0.0, alpha_tut_p2 - 25.0)
            elif contador_tutorial > 240:
                alpha_tut_p2 = max(0.0, 255.0 * (1.0 - (contador_tutorial - 240) / 60.0))

            if alpha_tut_p1 <= 0 and alpha_tut_p2 <= 0:
                mostrar_tutorial = False

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

        # Movimiento horizontal Jugador 1 (P1: WASD)
        if not jugador1["muerto"] and not p1_completado:
            jugador1["vel_x"] = 0
            jugador1["moviendo"] = False
            if teclas[pygame.K_a]:
                jugador1["vel_x"] = -jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            if teclas[pygame.K_d]:
                jugador1["vel_x"] = jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            if salto_p1_pedido:
                impulso = 0
                if not usar_agua and p1_sobre_p2 and (salto_p2_pedido or jugador2["vel_y"] < 0):
                    impulso = -4.5
                jugador1["vel_y"] = jugador1["fuerza_salto"] + impulso
                jugador1["en_suelo"] = False

        # Movimiento horizontal Jugador 2 (P2: Flechas)
        if not jugador2["muerto"] and not p2_completado:
            jugador2["vel_x"] = 0
            jugador2["moviendo"] = False
            if teclas[pygame.K_LEFT]:
                jugador2["vel_x"] = -jugador2["velocidad_mov"]
                jugador2["moviendo"] = True
            if teclas[pygame.K_RIGHT]:
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
            if jugador1["en_agua"]: aplicar_fisica_agua(jugador1, teclas[pygame.K_w], teclas[pygame.K_s])
            if jugador2["en_agua"]: aplicar_fisica_agua(jugador2, teclas[pygame.K_UP], teclas[pygame.K_DOWN])

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

        mundo = pygame.Surface((ancho_mundo_nivel, ALTO))
        mundo.fill((255, 240, 195))
        pygame.draw.rect(mundo, (225, 110, 80), suelo)

        for plat in plataformas:
            pygame.draw.rect(mundo, (110, 110, 115), plat, border_radius=4)
            pygame.draw.rect(mundo, (75, 75, 80), plat, width=2, border_radius=4)

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

        # Controles tutorial directamente arriba de cada personaje
        if numero_nivel == 1 and mostrar_tutorial:
            _dibujar_controles_tutorial(mundo, alpha_p1=alpha_tut_p1, alpha_p2=alpha_tut_p2, teclas_actuales=teclas)

        if p1_completado and not p2_completado:
            # Jugador 1 ya pasó por la puerta: cámara completa siguiendo al Jugador 2
            cam_x = max(0, min(jugador2["hitbox"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif p2_completado and not p1_completado:
            # Jugador 2 ya pasó por la puerta: cámara completa siguiendo al Jugador 1
            cam_x = max(0, min(jugador1["hitbox"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        else:
            # Ambos personajes están en juego
            distancia = abs(jugador1["hitbox"].centerx - jugador2["hitbox"].centerx)
            if distancia <= DISTANCIA_SPLIT:
                centro = (jugador1["hitbox"].centerx + jugador2["hitbox"].centerx) // 2
                cam_x = max(0, min(centro - ANCHO // 2, ancho_mundo_nivel - ANCHO))
                pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
            else:
                ancho_m = ANCHO // 2
                if jugador1["hitbox"].centerx <= jugador2["hitbox"].centerx:
                    p_izq, p_der = jugador1, jugador2
                else:
                    p_izq, p_der = jugador2, jugador1

                cam_izq_x = max(0, min(p_izq["hitbox"].centerx - ancho_m // 2, ancho_mundo_nivel - ancho_m))
                cam_der_x = max(0, min(p_der["hitbox"].centerx - ancho_m // 2, ancho_mundo_nivel - ancho_m))

                pantalla.blit(mundo, (0, 0), pygame.Rect(cam_izq_x, 0, ancho_m, ALTO))
                pantalla.blit(mundo, (ancho_m, 0), pygame.Rect(cam_der_x, 0, ancho_m, ALTO))
                pygame.draw.line(pantalla, (0, 0, 0), (ancho_m, 0), (ancho_m, ALTO), 4)

        # Botones HUD en la esquina superior derecha
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
                mostrar_tutorial = (numero_nivel == 1)
                contador_tutorial = 0
                p1_movio = False
                p2_movio = False
                alpha_tut_p1 = 255.0
                alpha_tut_p2 = 255.0

        if p1_completado and p2_completado:
            return mostrar_menu_victoria(pantalla)

    return "salir"