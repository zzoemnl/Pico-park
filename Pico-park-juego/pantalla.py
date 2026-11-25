import os
import sys
import math
import random
import pygame

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from fuentes import (
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_botones,
    obtener_fuente_pequena,
    obtener_fuente_contador,
    TAMANO_TITULO_GRANDE,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO_GRANDE,
    TAMANO_BOTON_GRANDE,
    TAMANO_BADGE,
    dibujar_texto_en_rect,
)
from configuracion import (
    t,
    mostrar_pestana_configuracion,
    reproducir_musica,
    obtener_idioma,
    reproducir_sonido_ahogamiento,
    detener_sonido_ahogamiento,
    reproducir_sonido_ui,
)

from sprites import (
    ANCHO, ALTO, FPS,
    COLOR_JUGADOR1, COLOR_JUGADOR2,
    dibujar_personaje,
    dibujar_agua,
    cargar_boton,
    cargar_boton_escalado,
    animar_pulsacion_boton,
    aclarar_boton,
    generar_boton_con_texto,
)
from movimientos import (
    crear_personaje,
    crear_caja,
    crear_pinchos,
    crear_pincho,
    crear_llave,
    crear_puerta,
    actualizar_puerta,
    reiniciar_juego,
    matar_personaje,
    resolver_colisiones,
    actualizar_caja,
    actualizar_llave,
    comprobar_pinchos,
    actualizar_muerte,
    puede_saltar,
    TAMANO_CAJA,
    DISTANCIA_SOGA_REPOSO,
    DISTANCIA_SOGA_MAXIMA,
    crear_estado_soga,
    coordinar_movimiento_soga,
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    ZONA_AGUA,
    actualizar_estado_agua,
    aplicar_fisica_agua,
    ALTO_HITBOX,
)
from guardado import crear_desbloqueados_inicial, hay_progreso_sin_guardar, es_partida_admin
from menus.dialogos import mostrar_dialogo_guardar_salir

COLOR_SOGA = (200, 160, 100)
COLOR_BOTON_SALIR = (150, 45, 45)
COLOR_PLATAFORMA = (225, 110, 80)
COLOR_BORDE_PLATAFORMA = (185, 80, 55)
ANCHO_MUNDO = 3000
DISTANCIA_SPLIT = 850


def pantalla_muerte(pantalla, reloj):
    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_GRANDE, tamano_fallback=60)
    fuente_texto = obtener_fuente_texto(TAMANO_SUBTITULO_GRANDE, tamano_fallback=36)

    w_btn, h_btn = 272, 80

    idm_muerte = obtener_idioma()
    if idm_muerte == "es":
        boton_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("salir.png", w_btn, h_btn)
        boton_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-preapretado.png", w_btn, h_btn)
        boton_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-apretado.png", w_btn, h_btn)

        boton_reiniciar_normal = cargar_boton_escalado("Ventanas/boton-reiniciar.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar.png", w_btn, h_btn)
        boton_reiniciar_semi = cargar_boton_escalado("Ventanas/boton-reiniciar-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-semiapretado.png", w_btn, h_btn)
        boton_reiniciar_apretado = cargar_boton_escalado("Ventanas/boton-reiniciar-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-apretado.png", w_btn, h_btn)
    else:
        col_btn_muerte = (45, 30, 20)
        boton_menu_normal = generar_boton_con_texto("Ventanas/boton-menu.png", w_btn, h_btn, t("menu"), col_btn_muerte, 24, 0, idm_muerte)
        boton_menu_semi = generar_boton_con_texto("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn, t("menu"), col_btn_muerte, 24, 1, idm_muerte)
        boton_menu_apretado = generar_boton_con_texto("Ventanas/boton-menu-apretado.png", w_btn, h_btn, t("menu"), col_btn_muerte, 24, 2, idm_muerte)

        boton_reiniciar_normal = generar_boton_con_texto("Ventanas/boton-reiniciar.png", w_btn, h_btn, t("reiniciar"), col_btn_muerte, 24, 0, idm_muerte)
        boton_reiniciar_semi = generar_boton_con_texto("Ventanas/boton-reiniciar-semiapretado.png", w_btn, h_btn, t("reiniciar"), col_btn_muerte, 24, 1, idm_muerte)
        boton_reiniciar_apretado = generar_boton_con_texto("Ventanas/boton-reiniciar-apretado.png", w_btn, h_btn, t("reiniciar"), col_btn_muerte, 24, 2, idm_muerte)

    # Botón X pixel art para salir completamente del juego
    w_x, h_x = 44, 52
    rect_btn_x = pygame.Rect(ANCHO - 18 - w_x, 16, w_x, h_x)
    boton_x_normal = cargar_boton_escalado("HUD/boton-x.png", w_x, h_x) or cargar_boton_escalado("boton-x.png", w_x, h_x)
    boton_x_semi = cargar_boton_escalado("HUD/boton-x-semiapretado.png", w_x, h_x) or cargar_boton_escalado("boton-x-semiapretado.png", w_x, h_x)
    boton_x_apretado = cargar_boton_escalado("HUD/boton-x-apretado.png", w_x, h_x) or cargar_boton_escalado("boton-x-apretado.png", w_x, h_x)
    boton_x_hover = aclarar_boton(boton_x_normal) if boton_x_normal else None

    if any(x is None for x in (
        boton_menu_normal, boton_menu_apretado,
        boton_reiniciar_normal, boton_reiniciar_apretado
    )):
        return "salir"

    boton_reiniciar = boton_reiniciar_normal.get_rect(center=(ANCHO // 2 - 160, 400))
    boton_menu = boton_menu_normal.get_rect(center=(ANCHO // 2 + 160, 400))

    boton_reiniciar_hover = aclarar_boton(boton_reiniciar_normal)
    boton_menu_hover = aclarar_boton(boton_menu_normal)

    while True:
        pos_mouse = pygame.mouse.get_pos()
        hov_reinicio = boton_reiniciar.collidepoint(pos_mouse)
        hov_menu = boton_menu.collidepoint(pos_mouse)
        hov_x = rect_btn_x.collidepoint(pos_mouse)

        try:
            if hov_reinicio or hov_menu or hov_x:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                try:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                except Exception:
                    pass
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    try:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    except Exception:
                        pass
                    if animar_pulsacion_boton(pantalla, rect_btn_x, boton_x_semi, boton_x_apretado, (25, 25, 25), boton_x_normal, tipo_sonido="ventana_cancelar"):
                        return "salir"

                elif boton_reiniciar.collidepoint(evento.pos):
                    try:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    except Exception:
                        pass
                    if animar_pulsacion_boton(pantalla, boton_reiniciar, boton_reiniciar_semi, boton_reiniciar_apretado, (25, 25, 25), boton_reiniciar_normal, tipo_sonido="ventana_reiniciar"):
                        return "reiniciar"

                elif boton_menu.collidepoint(evento.pos):
                    try:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    except Exception:
                        pass
                    if animar_pulsacion_boton(pantalla, boton_menu, boton_menu_semi, boton_menu_apretado, (25, 25, 25), boton_menu_normal, tipo_sonido="ventana_volver"):
                        return "menu"

        pantalla.fill((25, 25, 25))
        rect_tit = pygame.Rect(ANCHO // 2 - 300, 155, 600, 50)
        dibujar_texto_en_rect(pantalla, t("te_moriste"), rect_tit, categoria="titulo", tamano=TAMANO_TITULO_GRANDE, color=(255, 80, 80), padding=4)
        rect_sub = pygame.Rect(ANCHO // 2 - 350, 230, 700, 42)
        dibujar_texto_en_rect(pantalla, t("reiniciar_o_salir"), rect_sub, categoria="texto", tamano=TAMANO_SUBTITULO_GRANDE, color=(255, 255, 255), padding=4)

        spr_r = boton_reiniciar_hover if (hov_reinicio and boton_reiniciar_hover) else boton_reiniciar_normal
        spr_m = boton_menu_hover if (hov_menu and boton_menu_hover) else boton_menu_normal
        spr_x = boton_x_hover if (hov_x and boton_x_hover) else boton_x_normal

        pantalla.blit(spr_r, boton_reiniciar)
        pantalla.blit(spr_m, boton_menu)
        if spr_x:
            pantalla.blit(spr_x, rect_btn_x)
        pygame.display.flip()
        reloj.tick(FPS)


def crear_franjas_geometricas(ancho, alto):
    """
    Genera las franjas rectangulares negras que entran desde los 4 bordes:
    - Franjas horizontales desde izquierda y derecha con desfases.
    - Franjas verticales desde arriba y abajo con desfases.
    Se cruzan e intercalan para una sensación geométrica contundente.
    """
    franjas = []

    # 1. Franjas Horizontales (6 franjas alternadas)
    num_h = 6
    band_h = math.ceil(alto / num_h)
    for r in range(num_h):
        y = r * (alto // num_h)
        h = band_h + 3  # Ligero solapamiento para evitar líneas residuales
        desde_izq = (r % 2 == 0)

        # Desfase temporal orgánico desde los bordes hacia el centro
        dist_centro = abs(r - (num_h - 1) / 2) / ((num_h - 1) / 2)
        delay = (1.0 - dist_centro) * 0.12 + (0.05 if r % 2 == 1 else 0.0)

        franjas.append({
            "tipo": "horizontal",
            "direccion": "izq" if desde_izq else "der",
            "y": y,
            "h": h,
            "delay": delay,
        })

    # 2. Franjas Verticales (8 columnas alternadas)
    num_v = 8
    col_w = math.ceil(ancho / num_v)
    for c in range(num_v):
        x = c * (ancho // num_v)
        w = col_w + 3
        desde_arriba = (c % 2 == 0)

        dist_centro = abs(c - (num_v - 1) / 2) / ((num_v - 1) / 2)
        delay = dist_centro * 0.14 + (0.04 if c % 2 == 0 else 0.02)

        franjas.append({
            "tipo": "vertical",
            "direccion": "arriba" if desde_arriba else "abajo",
            "x": x,
            "w": w,
            "delay": delay,
        })

    return franjas


def obtener_rect_franja_cierre(franja, t_sec, duracion, ancho, alto):
    delay = franja["delay"]
    dur_efectiva = max(0.01, duracion - delay)
    if t_sec <= delay:
        factor = 0.0
    elif t_sec >= duracion:
        factor = 1.0
    else:
        p = (t_sec - delay) / dur_efectiva
        factor = p ** 2.4  # Empieza lento y se acelera contundentemente

    if factor <= 0.0:
        return None

    if franja["tipo"] == "horizontal":
        y = franja["y"]
        h = franja["h"]
        w_actual = int((ancho + 12) * factor)
        if franja["direccion"] == "izq":
            return pygame.Rect(0, y, w_actual, h)
        else:
            return pygame.Rect(ancho - w_actual, y, w_actual + 12, h)
    else:
        x = franja["x"]
        w = franja["w"]
        h_actual = int((alto + 12) * factor)
        if franja["direccion"] == "arriba":
            return pygame.Rect(x, 0, w, h_actual)
        else:
            return pygame.Rect(x, alto - h_actual, w, h_actual + 12)


def obtener_rect_franja_apertura(franja, t_sec, duracion, ancho, alto):
    delay = franja["delay"]
    dur_efectiva = max(0.01, duracion - delay)
    if t_sec <= delay:
        p = 0.0
    elif t_sec >= duracion:
        p = 1.0
    else:
        p = (t_sec - delay) / dur_efectiva

    # Se retiran progresivamente hacia los bordes
    factor = max(0.0, 1.0 - (p ** 2.2))
    if factor <= 0.001:
        return None

    if franja["tipo"] == "horizontal":
        y = franja["y"]
        h = franja["h"]
        w_actual = int((ancho + 12) * factor)
        if franja["direccion"] == "izq":
            return pygame.Rect(0, y, w_actual, h)
        else:
            return pygame.Rect(ancho - w_actual, y, w_actual + 12, h)
    else:
        x = franja["x"]
        w = franja["w"]
        h_actual = int((alto + 12) * factor)
        if franja["direccion"] == "arriba":
            return pygame.Rect(x, 0, w, h_actual)
        else:
            return pygame.Rect(x, alto - h_actual, w, h_actual + 12)


def animar_cierre_puerta(pantalla, reloj, mundo, puerta, cam_x, ancho_mundo_nivel):
    """
    Pausa limpia y fluida tras ingresar al portal antes de iniciar la transición
    geométrica de franjas, manteniendo intacto el escenario y el portal sin recuadros ni destellos blancos.
    """
    if puerta is None or mundo is None:
        return

    # Pausa breve (~0.2s / 14 frames) para apreciar la entrada al portal limpiamente
    for _ in range(14):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))
        pygame.display.flip()


def animar_salida_franjas(pantalla, reloj, captura_escenario, puerta=None, cam_x=0):
    """
    Transición geométrica limpia de franjas negras:
    - Capa 1: Escenario base capturado de forma limpia e intacta, con el portal en su posición natural.
    - Capa 2: Bandas geométricas negras que nacen del centro del portal y se expanden hacia afuera,
      junto a las franjas rectangulares que entran desde los bordes hasta cubrir la pantalla en negro absoluto (~1.13s).
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()
    franjas = crear_franjas_geometricas(ancho, alto)

    frames_totales = 68
    duracion = 1.13

    rect_p = puerta["rect"] if puerta else None
    pos_puerta = (rect_p.x - cam_x, rect_p.y) if rect_p else None

    door_cx = (pos_puerta[0] + rect_p.width // 2) if (pos_puerta and rect_p) else ancho // 2
    door_cy = (pos_puerta[1] + rect_p.height // 2) if (pos_puerta and rect_p) else alto // 2
    door_w = rect_p.width if rect_p else 60
    door_h = rect_p.height if rect_p else 90

    for f in range(frames_totales + 1):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        t_sec = (f / frames_totales) * duracion
        progreso = f / frames_totales

        # --- CAPA 1: Escenario base capturado limpio (con el portal ya integrado naturalmente) ---
        pantalla.blit(captura_escenario, (0, 0))

        # --- CAPA 2: Bandas geométricas negras que nacen de la puerta y se expanden ---
        if pos_puerta is not None:
            factor_door = (progreso ** 2.2)
            w_exp = int(ancho * factor_door)
            h_exp = int(alto * factor_door)

            if w_exp > 0:
                h_b = door_h + 12
                y_b = pos_puerta[1] - 6
                r_h_izq = pygame.Rect(door_cx - w_exp, y_b, w_exp, h_b)
                r_h_der = pygame.Rect(door_cx, y_b, w_exp, h_b)
                pygame.draw.rect(pantalla, (0, 0, 0), r_h_izq)
                pygame.draw.rect(pantalla, (0, 0, 0), r_h_der)

            if h_exp > 0:
                w_b = door_w + 12
                x_b = pos_puerta[0] - 6
                r_v_arr = pygame.Rect(x_b, door_cy - h_exp, w_b, h_exp)
                r_v_aba = pygame.Rect(x_b, door_cy, w_b, h_exp)
                pygame.draw.rect(pantalla, (0, 0, 0), r_v_arr)
                pygame.draw.rect(pantalla, (0, 0, 0), r_v_aba)

        # 2. Franjas rectangulares geométricas desde los bordes de la pantalla
        for franja in franjas:
            r = obtener_rect_franja_cierre(franja, t_sec, duracion, ancho, alto)
            if r is not None:
                pygame.draw.rect(pantalla, (0, 0, 0), r)

        pygame.display.flip()

    pantalla.fill((0, 0, 0))
    pygame.display.flip()


def animar_apertura_franjas(pantalla, reloj, captura_nuevo_nivel):
    """
    Transición de apertura al nuevo nivel:
    Las franjas negras se retiran en sentido contrario hacia los bordes,
    revelando el escenario y los personajes en sus posiciones iniciales (~1.13s).
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()
    franjas = crear_franjas_geometricas(ancho, alto)

    frames_totales = 24
    duracion = 0.40

    for f in range(frames_totales + 1):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        t_sec = (f / frames_totales) * duracion
        pantalla.blit(captura_nuevo_nivel, (0, 0))

        for franja in franjas:
            r = obtener_rect_franja_apertura(franja, t_sec, duracion, ancho, alto)
            if r is not None:
                pygame.draw.rect(pantalla, (0, 0, 0), r)

        pygame.display.flip()

    pantalla.blit(captura_nuevo_nivel, (0, 0))
    pygame.display.flip()


def crear_bloques_panel(rect_panel, ancho_pantalla, alto_pantalla):
    """
    Descompone el panel rectangular en pequeños bloques de color crema y rojo
    provenientes de diferentes direcciones fuera de la pantalla.
    """
    cols, rows = 8, 6
    bloques = []

    px, py = rect_panel.x, rect_panel.y
    pw, ph = rect_panel.width, rect_panel.height
    cx, cy = ancho_pantalla / 2, alto_pantalla / 2

    COL_CREMA = (255, 240, 195)
    COL_CREMA_CLARO = (255, 246, 218)
    COL_ROJO = (225, 110, 80)
    COL_ROJO_OSCURO = (195, 85, 60)

    for r in range(rows):
        for c in range(cols):
            x1 = px + int(c * pw / cols)
            y1 = py + int(r * ph / rows)
            x2 = px + int((c + 1) * pw / cols)
            y2 = py + int((r + 1) * ph / rows)
            bw, bh = x2 - x1, y2 - y1

            if r == 0 or r == rows - 1:
                color = COL_ROJO if (c + r) % 2 == 0 else COL_ROJO_OSCURO
                color_borde = (140, 45, 30)
            else:
                color = COL_CREMA if (c + r) % 2 == 0 else COL_CREMA_CLARO
                color_borde = (215, 198, 162)

            ang = math.atan2(y1 + bh / 2 - cy, x1 + bw / 2 - cx)
            ang += (((c * 7 + r * 13) % 9) - 4) * 0.18
            dist = max(ancho_pantalla, alto_pantalla) * 0.75 + ((c * 3 + r * 5) % 6) * 70

            sx = cx + math.cos(ang) * dist
            sy = cy + math.sin(ang) * dist
            delay = ((c * 3 + r * 2) % 7) * 0.038 + (c + r) * 0.015

            bloques.append({
                "c": c, "r": r,
                "tx": x1, "ty": y1,
                "w": bw, "h": bh,
                "color": color,
                "color_borde": color_borde,
                "sx": sx, "sy": sy,
                "delay": delay,
                "ang": ang,
            })

    return bloques


def dibujar_panel_victoria_solido(superficie, rect_panel, color_p1=None, color_p2=None):
    """
    Dibuja el panel rectangular ensamblado con la estética limpia y original de Pico Park.
    """
    col_dict = {
        "Blanco": (232, 232, 232), "Gris": (154, 154, 154), "Negro": (95, 95, 95),
        "Marron": (206, 136, 111), "Rojo": (255, 137, 134), "Rosa": (255, 150, 240),
        "Naranja": (255, 160, 100), "Amarillo": (255, 244, 123), "Verde": (157, 255, 124),
        "Verde oscuro": (105, 205, 75), "Celeste": (124, 231, 255), "Azul": (36, 166, 247),
        "Violeta": (161, 123, 255),
    }
    c_p1 = col_dict.get(color_p1, (124, 231, 255))
    c_p2 = col_dict.get(color_p2, (161, 123, 255))

    # Cuerpo principal color crema
    pygame.draw.rect(superficie, (255, 240, 195), rect_panel, border_radius=8)

    # Franja superior roja (cabecera)
    h_top = int(rect_panel.height / 6)
    r_top = pygame.Rect(rect_panel.x, rect_panel.y, rect_panel.width, h_top)
    pygame.draw.rect(superficie, (225, 110, 80), r_top, border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(superficie, (180, 75, 55), (rect_panel.left, rect_panel.top + h_top), (rect_panel.right, rect_panel.top + h_top), 2)

    # Franja inferior roja (base estilo suelo)
    h_bot = int(rect_panel.height / 6)
    r_bot = pygame.Rect(rect_panel.x, rect_panel.bottom - h_bot, rect_panel.width, h_bot)
    pygame.draw.rect(superficie, (225, 110, 80), r_bot, border_bottom_left_radius=8, border_bottom_right_radius=8)
    pygame.draw.line(superficie, (180, 75, 55), (rect_panel.left, rect_panel.bottom - h_bot), (rect_panel.right, rect_panel.bottom - h_bot), 2)

    # Borde exterior contundente
    pygame.draw.rect(superficie, (45, 45, 50), rect_panel, width=4, border_radius=8)

    # Mini bloques decorativos de los personajes en la franja naranja inferior
    y_sq = r_bot.centery - 13
    r_sq1 = pygame.Rect(rect_panel.left + 24, y_sq, 26, 26)
    pygame.draw.rect(superficie, c_p1, r_sq1, border_radius=4)
    pygame.draw.rect(superficie, (45, 45, 50), r_sq1, width=2, border_radius=4)

    r_sq2 = pygame.Rect(rect_panel.right - 50, y_sq, 26, 26)
    pygame.draw.rect(superficie, c_p2, r_sq2, border_radius=4)
    pygame.draw.rect(superficie, (45, 45, 50), r_sq2, width=2, border_radius=4)


def mostrar_pantalla_victoria(
    pantalla,
    reloj,
    mundo=1,
    numero_nivel=1,
    hay_siguiente=True,
    color_p1=None,
    color_p2=None,
    niveles_desbloqueados=None,
    partida_id=None,
    partida_nombre=None,
    snapshot_guardado=None,
):
    """
    Pantalla de victoria completa con:
    - Ensamblaje en bloques de crema y rojo (~0.9s).
    - Título animado con rebote: «¡NIVEL COMPLETADO!».
    - «¡Buen trabajo!» y número/nombre del nivel.
    - Botones secuenciales con desplazamiento y rebote («SIGUIENTE NIVEL →» y «VOLVER AL MENÚ»).
    - Interacción con hover y animación de selección.
    - Desarmado en bloques al avanzar al siguiente nivel.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()
    cx = ancho // 2
    cy = alto // 2

    # Pausa de inicio en negro (~0.18s)
    for _ in range(11):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pantalla.fill((0, 0, 0))
        pygame.display.flip()

    w_panel = min(560, ancho - 80)
    h_panel = min(420, alto - 80)
    rect_panel = pygame.Rect(cx - w_panel // 2, cy - h_panel // 2, w_panel, h_panel)
    bloques = crear_bloques_panel(rect_panel, ancho, alto)

    # --- FASE 1: Ensamblaje de bloques (24 fotogramas ~ 0.4s) ---
    frames_ensamble = 24
    for f in range(frames_ensamble + 1):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        t_sec = (f / frames_ensamble) * 0.90
        pantalla.fill((0, 0, 0))

        for b in bloques:
            p = (t_sec - b["delay"]) / 0.52
            if p <= 0.0:
                cur_x, cur_y = b["sx"], b["sy"]
            elif p >= 1.0:
                cur_x, cur_y = b["tx"], b["ty"]
            else:
                p_back = p - 1.0
                c1 = 1.35
                c3 = c1 + 1.0
                f_back = 1.0 + c3 * (p_back ** 3) + c1 * (p_back ** 2)
                cur_x = b["sx"] + (b["tx"] - b["sx"]) * f_back
                cur_y = b["sy"] + (b["ty"] - b["sy"]) * f_back

            r_bl = pygame.Rect(int(cur_x), int(cur_y), b["w"], b["h"])
            pygame.draw.rect(pantalla, b["color"], r_bl)
            pygame.draw.rect(pantalla, b["color_borde"], r_bl, 1)

        pygame.display.flip()

    # Botón X pixel art DENTRO del encabezado en la esquina superior derecha
    w_x, h_x = 36, 42
    h_top = int(rect_panel.height / 6)
    rect_btn_x = pygame.Rect(rect_panel.right - 14 - w_x, rect_panel.top + (h_top - h_x) // 2, w_x, h_x)
    spr_x_normal = cargar_boton_escalado("HUD/boton-x.png", w_x, h_x) or cargar_boton_escalado("boton-x.png", w_x, h_x)
    spr_x_semi = cargar_boton_escalado("HUD/boton-x-semiapretado.png", w_x, h_x) or cargar_boton_escalado("boton-x-semiapretado.png", w_x, h_x)
    spr_x_apretado = cargar_boton_escalado("HUD/boton-x-apretado.png", w_x, h_x) or cargar_boton_escalado("boton-x-apretado.png", w_x, h_x)
    spr_x_hover = aclarar_boton(spr_x_normal) if spr_x_normal else None

    # Título dinámico para evitar desbordes y no tapar el botón X
    txt_titulo = t("nivel_completado")
    max_w_tit = (rect_btn_x.left - cx - 20) * 2
    sz_tit = 22
    fuente_titulo = obtener_fuente_titulo(sz_tit)
    while sz_tit > 16 and fuente_titulo.size(txt_titulo)[0] > max_w_tit:
        sz_tit -= 1
        fuente_titulo = obtener_fuente_titulo(sz_tit)

    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE, negrita=True)
    fuente_badge = obtener_fuente_contador(20, negrita=True)
    fuente_btn = obtener_fuente_botones(26, negrita=True)

    w_btn = 272
    h_btn = 80
    btn1_x = cx - w_btn // 2
    btn1_target_y = rect_panel.top + 215
    btn2_x = cx - w_btn // 2
    btn2_target_y = rect_panel.top + 305

    rect_btn1 = pygame.Rect(btn1_x, btn1_target_y, w_btn, h_btn)
    rect_btn2 = pygame.Rect(btn2_x, btn2_target_y, w_btn, h_btn)

    txt_btn1 = t("siguiente") if hay_siguiente else t("finalizar")
    txt_btn2 = t("volver_juego")

    idm_vic = obtener_idioma()
    if idm_vic == "es":
        spr_sig_normal = cargar_boton_escalado("Ventanas/boton-siguiente.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente.png", w_btn, h_btn)
        spr_sig_semi = cargar_boton_escalado("Ventanas/boton-siguiente-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-semiapretado.png", w_btn, h_btn)
        spr_sig_apretado = cargar_boton_escalado("Ventanas/boton-siguiente-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-apretado.png", w_btn, h_btn)

        spr_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn)
        spr_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn)
        spr_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn)
    else:
        col_btn_vic = (45, 30, 20)
        spr_sig_normal = generar_boton_con_texto("Ventanas/boton-siguiente.png", w_btn, h_btn, txt_btn1, col_btn_vic, 24, 0, idm_vic)
        spr_sig_semi = generar_boton_con_texto("Ventanas/boton-siguiente-semiapretado.png", w_btn, h_btn, txt_btn1, col_btn_vic, 24, 1, idm_vic)
        spr_sig_apretado = generar_boton_con_texto("Ventanas/boton-siguiente-apretado.png", w_btn, h_btn, txt_btn1, col_btn_vic, 24, 2, idm_vic)

        spr_menu_normal = generar_boton_con_texto("Ventanas/boton-menu.png", w_btn, h_btn, txt_btn2, col_btn_vic, 20 if idm_vic == "en" else 22, 0, idm_vic)
        spr_menu_semi = generar_boton_con_texto("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn, txt_btn2, col_btn_vic, 20 if idm_vic == "en" else 22, 1, idm_vic)
        spr_menu_apretado = generar_boton_con_texto("Ventanas/boton-menu-apretado.png", w_btn, h_btn, txt_btn2, col_btn_vic, 20 if idm_vic == "en" else 22, 2, idm_vic)

    spr_sig_hover = aclarar_boton(spr_sig_normal) if spr_sig_normal else None
    spr_menu_hover = aclarar_boton(spr_menu_normal) if spr_menu_normal else None


    nom_nivel = f"{t('mundo')} {mundo} — {t('nivel')} {numero_nivel}"

    # --- FASE 2: Entrada secuencial del título y botones con rebote (18 fotogramas ~ 0.3s) ---
    frames_intro = 18
    for f in range(frames_intro + 1):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pantalla.fill((0, 0, 0))
        dibujar_panel_victoria_solido(pantalla, rect_panel, color_p1, color_p2)

        # 1. Título con rebote (empieza en f=0)
        t_tit = min(1.0, f / 18.0)
        bounce_tit = math.sin(t_tit * math.pi * 2.5) * (1.0 - t_tit) if t_tit < 1.0 else 0.0
        y_tit = rect_panel.top + 35 + int(-28 * bounce_tit)
        t_tit_surf = fuente_titulo.render(txt_titulo, True, (255, 255, 255))
        pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, y_tit)))

        # Subtítulo y cápsula de nivel
        if f >= 8:
            t_sub = fuente_sub.render(t("buen_trabajo"), True, (75, 70, 70))
            pantalla.blit(t_sub, t_sub.get_rect(center=(cx, rect_panel.top + 98)))

            r_badge = pygame.Rect(cx - 195, rect_panel.top + 130, 390, 42)
            pygame.draw.rect(pantalla, (255, 255, 255), r_badge, border_radius=8)
            pygame.draw.rect(pantalla, (180, 75, 55), r_badge, width=2, border_radius=8)
            dibujar_texto_en_rect(pantalla, nom_nivel, r_badge, categoria="boton", tamano=21, color=(25, 25, 30), padding=4)

        # Botón X animado en la esquina superior derecha
        if f >= 12 and spr_x_normal:
            pantalla.blit(spr_x_normal, rect_btn_x)

        # 2. Botón 1 con desplazamiento y rebote (empieza en f=12)
        if f >= 12:
            t_b1 = min(1.0, (f - 12) / 16.0)
            bounce_b1 = math.sin(t_b1 * math.pi * 2.5) * (1.0 - t_b1) if t_b1 < 1.0 else 0.0
            cur_y1 = btn1_target_y + int(35 * (1.0 - t_b1) + 12 * bounce_b1)
            r1_anim = pygame.Rect(btn1_x, cur_y1, w_btn, h_btn)

            if spr_sig_normal and hay_siguiente:
                pantalla.blit(spr_sig_normal, r1_anim)
            elif spr_menu_normal and not hay_siguiente:
                pantalla.blit(spr_menu_normal, r1_anim)
            else:
                pygame.draw.rect(pantalla, (160, 50, 35), (r1_anim.x, r1_anim.y + 4, r1_anim.w, r1_anim.h), border_radius=8)
                pygame.draw.rect(pantalla, (225, 110, 80), r1_anim, border_radius=8)
                pygame.draw.rect(pantalla, (150, 45, 30), r1_anim, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn1, r1_anim, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(255, 255, 255), padding=6)

        # 3. Botón 2 con desplazamiento y rebote (empieza en f=20)
        if f >= 20:
            t_b2 = min(1.0, (f - 20) / 16.0)
            bounce_b2 = math.sin(t_b2 * math.pi * 2.5) * (1.0 - t_b2) if t_b2 < 1.0 else 0.0
            cur_y2 = btn2_target_y + int(35 * (1.0 - t_b2) + 12 * bounce_b2)
            r2_anim = pygame.Rect(btn2_x, cur_y2, w_btn, h_btn)

            if spr_menu_normal:
                pantalla.blit(spr_menu_normal, r2_anim)
            else:
                pygame.draw.rect(pantalla, (195, 185, 165), (r2_anim.x, r2_anim.y + 4, r2_anim.w, r2_anim.h), border_radius=8)
                pygame.draw.rect(pantalla, (245, 235, 215), r2_anim, border_radius=8)
                pygame.draw.rect(pantalla, (70, 70, 75), r2_anim, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn2, r2_anim, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(50, 50, 55), padding=6)

        pygame.display.flip()

    # --- FASE 3: Interacción del usuario (hover y selección) ---
    accion_seleccionada = None
    boton_presionado = None
    fondo_limpio_btn1 = None
    fondo_limpio_btn2 = None
    fondo_limpio_btn_x = None

    while accion_seleccionada is None:
        reloj.tick(FPS)
        pos_mouse = pygame.mouse.get_pos()
        hover1 = rect_btn1.collidepoint(pos_mouse)
        hover2 = rect_btn2.collidepoint(pos_mouse)
        hover_x = rect_btn_x.collidepoint(pos_mouse)

        # Ajuste de cursor al pasar sobre los botones
        try:
            if hover1 or hover2 or hover_x:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                try: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                except Exception: pass
                if hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_id):
                    resp = mostrar_dialogo_guardar_salir(
                        pantalla, reloj,
                        niveles_desbloqueados=niveles_desbloqueados,
                        id_partida=partida_id,
                        nombre_partida=partida_nombre,
                        color_p1=color_p1,
                        color_p2=color_p2,
                    )
                    if resp in ("guardar_salir", "salir_sin_guardar"):
                        pygame.quit()
                        sys.exit()
                else:
                    pygame.quit()
                    sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    try:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    except Exception:
                        pass
                    if animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, fondo_limpio_btn_x or (0, 0, 0), spr_x_normal, tipo_sonido="ventana_cancelar"):
                        accion_seleccionada = "salir"
                elif rect_btn1.collidepoint(evento.pos):
                    spr1_norm = spr_sig_normal if hay_siguiente else spr_menu_normal
                    spr1_semi = spr_sig_semi if hay_siguiente else spr_menu_semi
                    spr1_apr = spr_sig_apretado if hay_siguiente else spr_menu_apretado
                    if animar_pulsacion_boton(pantalla, rect_btn1, spr1_semi, spr1_apr, fondo_limpio_btn1, spr1_norm, tipo_sonido="ventana_aceptar"):
                        accion_seleccionada = "siguiente" if hay_siguiente else "menu"
                elif rect_btn2.collidepoint(evento.pos):
                    if animar_pulsacion_boton(pantalla, rect_btn2, spr_menu_semi, spr_menu_apretado, fondo_limpio_btn2, spr_menu_normal, tipo_sonido="ventana_volver"):
                        accion_seleccionada = "menu"

        if accion_seleccionada is not None:
            break

        pantalla.fill((0, 0, 0))
        dibujar_panel_victoria_solido(pantalla, rect_panel, color_p1, color_p2)

        # Título
        t_tit_surf = fuente_titulo.render(txt_titulo, True, (255, 255, 255))
        pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, rect_panel.top + 35)))

        # Subtítulo y cápsula
        t_sub = fuente_sub.render(t("buen_trabajo"), True, (75, 70, 70))
        pantalla.blit(t_sub, t_sub.get_rect(center=(cx, rect_panel.top + 98)))

        r_badge = pygame.Rect(cx - 195, rect_panel.top + 130, 390, 42)
        pygame.draw.rect(pantalla, (255, 255, 255), r_badge, border_radius=8)
        pygame.draw.rect(pantalla, (180, 75, 55), r_badge, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, nom_nivel, r_badge, categoria="boton", tamano=21, color=(25, 25, 30), padding=4)

        # Captura de fondos limpios antes de renderizar los botones
        fondo_limpio_btn1 = pantalla.subsurface(rect_btn1).copy()
        fondo_limpio_btn2 = pantalla.subsurface(rect_btn2).copy()
        fondo_limpio_btn_x = pantalla.subsurface(rect_btn_x).copy()

        # Renderizado interactivo Botón X
        if spr_x_normal:
            spr_x_dib = spr_x_apretado if (boton_presionado == 3 and hover_x) else (spr_x_hover if (hover_x and spr_x_hover) else spr_x_normal)
            pantalla.blit(spr_x_dib, rect_btn_x)

        # Renderizado interactivo Botón 1 («SIGUIENTE NIVEL →»)
        press1 = (boton_presionado == 1 and hover1)
        if spr_sig_normal and hay_siguiente:
            spr_b1 = spr_sig_apretado if press1 else (spr_sig_hover if (hover1 and spr_sig_hover) else spr_sig_normal)
            pantalla.blit(spr_b1, rect_btn1)
        elif spr_menu_normal and not hay_siguiente:
            spr_b1 = spr_menu_apretado if press1 else (spr_menu_hover if (hover1 and spr_menu_hover) else spr_menu_normal)
            pantalla.blit(spr_b1, rect_btn1)
        else:
            if press1:
                r1_draw = pygame.Rect(rect_btn1.x, rect_btn1.y + 3, rect_btn1.w, rect_btn1.h)
                pygame.draw.rect(pantalla, (200, 85, 60), r1_draw, border_radius=8)
                pygame.draw.rect(pantalla, (130, 40, 25), r1_draw, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn1, r1_draw, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(245, 245, 245), padding=6)
            elif hover1:
                r1_draw = pygame.Rect(rect_btn1.x, rect_btn1.y - 2, rect_btn1.w, rect_btn1.h)
                pygame.draw.rect(pantalla, (160, 50, 35), (r1_draw.x, r1_draw.y + 6, r1_draw.w, r1_draw.h), border_radius=8)
                pygame.draw.rect(pantalla, (240, 125, 95), r1_draw, border_radius=8)
                pygame.draw.rect(pantalla, (180, 60, 45), r1_draw, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn1, r1_draw, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(255, 255, 255), padding=6)
            else:
                pygame.draw.rect(pantalla, (160, 50, 35), (rect_btn1.x, rect_btn1.y + 4, rect_btn1.w, rect_btn1.h), border_radius=8)
                pygame.draw.rect(pantalla, (225, 110, 80), rect_btn1, border_radius=8)
                pygame.draw.rect(pantalla, (150, 45, 30), rect_btn1, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn1, rect_btn1, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(255, 255, 255), padding=6)

        # Renderizado interactivo Botón 2 («VOLVER AL MENÚ»)
        press2 = (boton_presionado == 2 and hover2)
        if spr_menu_normal:
            spr_b2 = spr_menu_apretado if press2 else (spr_menu_hover if (hover2 and spr_menu_hover) else spr_menu_normal)
            pantalla.blit(spr_b2, rect_btn2)
        else:
            if press2:
                r2_draw = pygame.Rect(rect_btn2.x, rect_btn2.y + 3, rect_btn2.w, rect_btn2.h)
                pygame.draw.rect(pantalla, (225, 215, 195), r2_draw, border_radius=8)
                pygame.draw.rect(pantalla, (35, 35, 40), r2_draw, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn2, r2_draw, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(35, 35, 40), padding=6)
            elif hover2:
                r2_draw = pygame.Rect(rect_btn2.x, rect_btn2.y - 2, rect_btn2.w, rect_btn2.h)
                pygame.draw.rect(pantalla, (195, 185, 165), (r2_draw.x, r2_draw.y + 6, r2_draw.w, r2_draw.h), border_radius=8)
                pygame.draw.rect(pantalla, (255, 248, 232), r2_draw, border_radius=8)
                pygame.draw.rect(pantalla, (40, 40, 45), r2_draw, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn2, r2_draw, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(40, 40, 45), padding=6)
            else:
                pygame.draw.rect(pantalla, (195, 185, 165), (rect_btn2.x, rect_btn2.y + 4, rect_btn2.w, rect_btn2.h), border_radius=8)
                pygame.draw.rect(pantalla, (245, 235, 215), rect_btn2, border_radius=8)
                pygame.draw.rect(pantalla, (70, 70, 75), rect_btn2, width=3, border_radius=8)
                dibujar_texto_en_rect(pantalla, txt_btn2, rect_btn2, categoria="boton", tamano=TAMANO_BOTON_GRANDE, color=(50, 50, 55), padding=6)

        pygame.display.flip()

    try:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        pass

    if accion_seleccionada == "salir":
        return "salir"

    # --- FASE 4: Desarmado del panel en bloques rectangulares que se dispersan (~0.4s) ---
    frames_desarme = 24
    for f in range(frames_desarme + 1):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        t_out = (f / frames_desarme) ** 2.2
        pantalla.fill((0, 0, 0))

        for b in bloques:
            cur_x = b["tx"] + math.cos(b["ang"]) * t_out * 1250
            cur_y = b["ty"] + math.sin(b["ang"]) * t_out * 1250
            r_bl = pygame.Rect(int(cur_x), int(cur_y), b["w"], b["h"])
            pygame.draw.rect(pantalla, b["color"], r_bl)
            pygame.draw.rect(pantalla, b["color_borde"], r_bl, 1)

        pygame.display.flip()

    pantalla.fill((0, 0, 0))
    pygame.display.flip()

    return accion_seleccionada


def animar_transicion_nivel_completado(
    pantalla,
    reloj,
    hay_siguiente=True,
    mundo=1,
    numero_nivel=1,
    puerta=None,
    mundo_surface=None,
    cam_x=0,
    ancho_mundo_nivel=None,
    color_p1=None,
    color_p2=None,
    niveles_desbloqueados=None,
    partida_id=None,
    partida_nombre=None,
    snapshot_guardado=None,
):
    """
    Secuencia maestra completa de fin de nivel:
    1. Animación de cierre de la puerta.
    2. Transición geométrica de salida con franjas rectangulares negras acelerándose.
    3. Construcción interactiva del panel de victoria en bloques y menú de selección.
    4. Desarmado y retorno de la acción elegida («siguiente», «menu» o «salir»).
    """
    # 1. Animación y pausa limpia en el escenario actual
    if puerta is not None and mundo_surface is not None:
        animar_cierre_puerta(pantalla, reloj, mundo_surface, puerta, cam_x, ancho_mundo_nivel)

    # 2. Captura limpia del escenario base para la transición geométrica (sin recuadros ni bordes artificiales)
    captura_escenario = pygame.Surface((pantalla.get_width(), pantalla.get_height()))
    if mundo_surface is not None:
        captura_escenario.blit(mundo_surface, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))
    else:
        captura_escenario.blit(pantalla, (0, 0))

    # 3. Franjas y transición geométrica generada desde el portal
    animar_salida_franjas(pantalla, reloj, captura_escenario, puerta=puerta, cam_x=cam_x)

    # 4. Pantalla de victoria con ensamblaje, interacción y desarmado
    return mostrar_pantalla_victoria(
        pantalla=pantalla,
        reloj=reloj,
        mundo=mundo,
        numero_nivel=numero_nivel,
        hay_siguiente=hay_siguiente,
        color_p1=color_p1,
        color_p2=color_p2,
        niveles_desbloqueados=niveles_desbloqueados,
        partida_id=partida_id,
        partida_nombre=partida_nombre,
        snapshot_guardado=snapshot_guardado,
    )


def dibujar_pinchos_escenario(superficie, pinchos):
    col_cuerpo = (235, 235, 240)
    col_sombra = (195, 195, 205)
    col_borde = (100, 95, 100)
    for p in pinchos:
        dir_p = getattr(p, "direccion", None)
        if dir_p == "abajo":
            # Pincho saliendo del techo apuntando hacia abajo
            puntos = [(p.left, p.top), (p.centerx, p.bottom), (p.right, p.top)]
            puntos_sombra = [(p.centerx, p.bottom), (p.right, p.top), (p.centerx, p.top)]
        elif dir_p == "izquierda":
            # Pincho en pared saliendo hacia la izquierda
            puntos = [(p.right, p.top), (p.left, p.centery), (p.right, p.bottom)]
            puntos_sombra = [(p.left, p.centery), (p.right, p.bottom), (p.right, p.centery)]
        elif dir_p == "derecha" or (dir_p is None and p.width < p.height):
            # Pincho en pared saliendo hacia la derecha
            puntos = [(p.left, p.top), (p.right, p.centery), (p.left, p.bottom)]
            puntos_sombra = [(p.right, p.centery), (p.left, p.bottom), (p.left, p.centery)]
        else:
            # Pincho en suelo horizontal apuntando hacia arriba
            puntos = [(p.left, p.bottom), (p.centerx, p.top), (p.right, p.bottom)]
            puntos_sombra = [(p.centerx, p.top), (p.right, p.bottom), (p.centerx, p.bottom)]

        pygame.draw.polygon(superficie, col_cuerpo, puntos)
        if len(puntos_sombra) >= 3:
            pygame.draw.polygon(superficie, col_sombra, puntos_sombra)
        pygame.draw.polygon(superficie, col_borde, puntos, 2)


def dibujar_bloque_peligroso(superficie, bloque_peligroso):
    """Dibuja un bloque peligroso rojo con textura metálica de alerta, remaches y ranuras."""
    if bloque_peligroso is None:
        return
    br = bloque_peligroso["rect"] if isinstance(bloque_peligroso, dict) else bloque_peligroso
    pygame.draw.rect(superficie, (220, 50, 50), br, border_radius=4)
    pygame.draw.rect(superficie, (140, 25, 25), br, width=2, border_radius=4)
    for by in range(br.top + 14, br.bottom - 8, 14):
        pygame.draw.line(superficie, (160, 30, 30), (br.left + 4, by), (br.right - 4, by), 2)
    for rx, ry in [(br.left + 6, br.top + 6), (br.right - 6, br.top + 6), (br.left + 6, br.bottom - 6), (br.right - 6, br.bottom - 6)]:
        pygame.draw.circle(superficie, (255, 180, 180), (rx, ry), 2)
        pygame.draw.circle(superficie, (110, 20, 20), (rx, ry), 1)


def crear_bloque_con_pinchos(bx, by, bw=60, bh=60):
    """
    Crea un bloque cuadrado peligroso con puntas triangulares sobresaliendo por sus 4 lados (arriba, abajo, izq, der).
    Reutiliza exactamente el modelo y proporciones de Nivel 3.
    """
    bloque = {
        "rect": pygame.Rect(bx, by, bw, bh),
        "x": bx,
        "y": by,
        "ancho": bw,
        "alto": bh,
    }
    w_top = (bw - 10) // 2
    h_side = (bh - 10) // 2
    spikes = [
        crear_pincho(bx + 4, by - 22, w_top, 22, direccion="arriba"),
        crear_pincho(bx + w_top + 6, by - 22, w_top, 22, direccion="arriba"),
        crear_pincho(bx + 4, by + bh, w_top, 22, direccion="abajo"),
        crear_pincho(bx + w_top + 6, by + bh, w_top, 22, direccion="abajo"),
        crear_pincho(bx - 22, by + 4, 22, h_side, direccion="izquierda"),
        crear_pincho(bx - 22, by + h_side + 6, 22, h_side, direccion="izquierda"),
        crear_pincho(bx + bw, by + 4, 22, h_side, direccion="derecha"),
        crear_pincho(bx + bw, by + h_side + 6, 22, h_side, direccion="derecha"),
    ]
    return bloque, spikes


def dibujar_pendulo_escenario(superficie, plataformas, plat_elevada=None, pozo_info=None, bloque_peligroso=None):
    """
    Dibuja los elementos visuales específicos de «Mundo 2 — Nivel 3: El péndulo»:
    - Estructura metálica/industrial y vigas de soporte de la plataforma elevada.
    - Señales de advertencia en los bordes y abismo cavernoso de pinchos.
    - Bloque peligroso rojo central con textura metálica de alerta y remaches.
    """
    col_viga = (185, 80, 55)
    col_viga_borde = (130, 45, 30)
    col_remache = (255, 205, 150)
    col_aviso_1 = (245, 200, 60)
    col_aviso_2 = (45, 40, 35)

    if plat_elevada is not None:
        p_el = plat_elevada
        # Franja de vigas con remaches en la parte inferior de la plataforma elevada
        h_viga = 8
        y_viga = p_el.bottom - h_viga
        pygame.draw.rect(superficie, col_viga_borde, (p_el.x, y_viga, p_el.width, h_viga))
        for rx in range(p_el.left + 16, p_el.right - 10, 32):
            pygame.draw.circle(superficie, col_remache, (rx, y_viga + 4), 2)
            pygame.draw.circle(superficie, (90, 30, 20), (rx, y_viga + 4), 1)

        # Franjas de precaución en los bordes izquierdo y derecho de la plataforma
        for borde_x in (p_el.left, p_el.right - 24):
            rect_aviso = pygame.Rect(borde_x, p_el.top, 24, p_el.height)
            pygame.draw.rect(superficie, col_aviso_1, rect_aviso)
            for s in range(0, 24, 8):
                pygame.draw.line(superficie, col_aviso_2, (borde_x + s, p_el.bottom), (borde_x + s + 6, p_el.top), 2)

        # Tirantes de anclaje diagonales en los extremos del puente suspendido
        pygame.draw.line(superficie, col_viga_borde, (p_el.left, p_el.bottom), (p_el.left - 40, p_el.bottom + 50), 3)
        pygame.draw.line(superficie, col_viga_borde, (p_el.right, p_el.bottom), (p_el.right + 40, p_el.bottom + 50), 3)

    if pozo_info is not None:
        pz = pozo_info
        # Fondo sombreado de profundidad peligrosa sobre el abismo de pinchos
        if "_surf_abismo" not in pz:
            s_abismo = pygame.Surface((pz["ancho"], pz["alto"]), pygame.SRCALPHA)
            s_abismo.fill((40, 25, 25, 110))
            pz["_surf_abismo"] = s_abismo
        superficie.blit(pz["_surf_abismo"], (pz["x"], pz["y"]))

    if bloque_peligroso is not None:
        dibujar_bloque_peligroso(superficie, bloque_peligroso)

    # Detalles rocosos en formaciones intermedias
    col_fisura = (150, 65, 45)
    for plat in plataformas:
        if plat.width < 200 and plat.height > 40:
            for fx in range(plat.left + 15, plat.right - 10, 35):
                pygame.draw.line(superficie, col_fisura, (fx, plat.top + 6), (fx + 6, plat.top + 26), 2)
                pygame.draw.line(superficie, col_fisura, (fx + 6, plat.top + 26), (fx + 2, min(plat.bottom - 4, plat.top + 40)), 2)


def dibujar_plataformas_derrumbables_escenario(superficie, plataformas_derrumbables, pozo_info=None):
    """
    Dibuja los elementos visuales de «Mundo 2 — Nivel 4: Las plataformas que se derrumban»:
    - Fondo de profundidad peligrosa del abismo de pinchos.
    - Plataformas con textura pétrea y grietas progresivas según el tiempo restante.
    - Efecto de temblor/vibración en los últimos segundos antes del colapso.
    - Desmoronamiento y caída física con partículas de roca y polvo.
    """
    if pozo_info is not None:
        pz = pozo_info
        if "_surf_abismo_derr" not in pz:
            s_abismo = pygame.Surface((pz["ancho"], pz["alto"]), pygame.SRCALPHA)
            s_abismo.fill((40, 25, 25, 120))
            pz["_surf_abismo_derr"] = s_abismo
        superficie.blit(pz["_surf_abismo_derr"], (pz["x"], pz["y"]))

    if plataformas_derrumbables is None:
        return

    col_bloque = (185, 120, 85)
    col_borde = (130, 65, 40)
    col_grieta = (60, 30, 20)
    col_alerta_grieta = (255, 160, 100)

    for p_d in plataformas_derrumbables:
        r = p_d["rect"]
        if r.top > ALTO + 50:
            continue

        estado = p_d["estado"]
        tiempo = p_d["tiempo_restante"]

        dx_shake = 0
        dy_shake = 0
        if estado == "temblando":
            dx_shake = random.choice([-2, -1, 0, 1, 2])
            dy_shake = random.choice([0, 1])

        rect_draw = pygame.Rect(r.x + dx_shake, r.y + dy_shake, r.width, r.height)

        if estado == "derrumbada":
            col_caida = (150, 90, 65)
            rect_part1 = pygame.Rect(rect_draw.x, rect_draw.y, rect_draw.width // 2 - 2, rect_draw.height)
            rect_part2 = pygame.Rect(rect_draw.x + rect_draw.width // 2 + 2, rect_draw.y + 4, rect_draw.width // 2 - 2, rect_draw.height)
            pygame.draw.rect(superficie, col_caida, rect_part1, border_radius=2)
            pygame.draw.rect(superficie, col_borde, rect_part1, width=1, border_radius=2)
            pygame.draw.rect(superficie, col_caida, rect_part2, border_radius=2)
            pygame.draw.rect(superficie, col_borde, rect_part2, width=1, border_radius=2)
        else:
            pygame.draw.rect(superficie, col_bloque, rect_draw, border_radius=3)
            pygame.draw.rect(superficie, col_borde, rect_draw, width=2, border_radius=3)

            if estado == "intacta":
                pygame.draw.line(superficie, col_grieta, (rect_draw.x + 24, rect_draw.top + 2), (rect_draw.x + 30, rect_draw.top + 8), 1)
                pygame.draw.line(superficie, col_grieta, (rect_draw.x + 85, rect_draw.top + 2), (rect_draw.x + 80, rect_draw.top + 9), 1)
            elif estado in ("agrietandose", "temblando"):
                progreso_grieta = min(1.0, max(0.0, (60.0 - tiempo) / 60.0))
                prof = int(rect_draw.height * progreso_grieta)
                c_x = rect_draw.x + rect_draw.width // 2
                pts_grieta = [
                    (c_x - 10, rect_draw.top + 1),
                    (c_x - 3, rect_draw.top + prof // 2),
                    (c_x + 6, rect_draw.top + prof),
                ]
                pygame.draw.lines(superficie, col_grieta, False, pts_grieta, 2)
                pygame.draw.line(superficie, col_grieta, (rect_draw.x + 20, rect_draw.top + 1), (rect_draw.x + 28, rect_draw.top + prof), 2)
                pygame.draw.line(superficie, col_grieta, (rect_draw.right - 25, rect_draw.top + 1), (rect_draw.right - 35, rect_draw.top + prof), 2)

                if estado == "temblando":
                    pygame.draw.lines(superficie, col_alerta_grieta, False, pts_grieta, 1)

        for part in p_d.get("particulas", []):
            tam = max(2, part.get("tam", 3))
            c_part = (165, 105, 75) if part["vida"] > 20 else (120, 65, 45)
            pygame.draw.rect(superficie, c_part, (int(part["x"]), int(part["y"]), tam, tam), border_radius=1)
def dibujar_plataformas_alternadas_escenario(superficie, plataformas_alternadas, pozo_info=None):
    """
    Dibuja los elementos visuales de «Mundo 2 — Nivel 5: Las plataformas alternadas»:
    - Atmósfera de profundidad en el abismo sobre los pinchos mortales.
    - Cables tensores industriales suspendidos desde el techo hasta cada plataforma flotante.
    - Remaches y marcos metálicos estructurales en cada plataforma alternada.
    - Pedestal dorado con halo brillante en la cumbre central donde descansa la llave.
    """
    if pozo_info is not None:
        pz = pozo_info
        if "_surf_abismo_derr" not in pz:
            s_abismo = pygame.Surface((pz["ancho"], pz["alto"]), pygame.SRCALPHA)
            s_abismo.fill((40, 25, 25, 120))
            pz["_surf_abismo_derr"] = s_abismo
        superficie.blit(pz["_surf_abismo_derr"], (pz["x"], pz["y"]))

    if not plataformas_alternadas:
        return

    col_cable = (145, 130, 115)
    col_cable_sombra = (95, 80, 68)
    col_anclaje = (80, 70, 62)
    col_remache = (150, 75, 45)
    col_brillo_cumbre = (255, 215, 90, 40)

    for idx, p in enumerate(plataformas_alternadas):
        # 1. Cables tensores suspendidos desde la parte superior del escenario
        for offset_x in (14, p.width - 14):
            cx = p.left + offset_x
            pygame.draw.line(superficie, col_cable_sombra, (cx + 1, 0), (cx + 1, p.top), 2)
            pygame.draw.line(superficie, col_cable, (cx, 0), (cx, p.top), 1)
            # Anclaje con perno circular
            pygame.draw.circle(superficie, col_anclaje, (cx, p.top - 2), 3)

        # 2. Detalles de remaches metálicos y molduras
        pygame.draw.circle(superficie, col_remache, (p.left + 14, p.centery), 2)
        pygame.draw.circle(superficie, col_remache, (p.right - 14, p.centery), 2)

        # 3. Plataforma superior con la llave (último escalón suspendido previo a la cima)
        if idx == len(plataformas_alternadas) - 1:
            s_halo = pygame.Surface((p.width + 36, 75), pygame.SRCALPHA)
            pygame.draw.ellipse(s_halo, col_brillo_cumbre, (0, 8, p.width + 36, 56))
            superficie.blit(s_halo, (p.left - 18, p.top - 58))
            # Pedestal bajo la llave
            pedestal_rect = pygame.Rect(p.centerx - 18, p.top - 6, 36, 6)
            pygame.draw.rect(superficie, (240, 190, 80), pedestal_rect, border_radius=2)
            pygame.draw.rect(superficie, (175, 130, 40), pedestal_rect, width=1, border_radius=2)


def dibujar_laser_escenario(superficie, laser_info):
    if laser_info is None:
        return
    em = laser_info["emisor_rect"]
    y_rayo = laser_info["y_rayo"]
    x_fin = laser_info["x_fin"]
    bloqueado = laser_info["bloqueado"]

    # 1. Base / Soporte del emisor montado en la plataforma
    pygame.draw.rect(superficie, (65, 60, 70), (em.x - 4, em.y - 4, em.width + 8, em.height + 8), border_radius=4)
    pygame.draw.rect(superficie, (40, 35, 45), (em.x - 4, em.y - 4, em.width + 8, em.height + 8), width=2, border_radius=4)
    pygame.draw.rect(superficie, (110, 105, 120), em, border_radius=3)
    # Lente / núcleo emisor
    pygame.draw.circle(superficie, (255, 60, 60), (em.right - 4, y_rayo), 5)
    pygame.draw.circle(superficie, (255, 220, 220), (em.right - 4, y_rayo), 2)

    # 2. Rayo láser si hay distancia hasta x_fin
    if x_fin > em.right:
        # Resplandor exterior suave
        surf_glow = pygame.Surface((x_fin - em.right, 14), pygame.SRCALPHA)
        surf_glow.fill((255, 30, 30, 75))
        superficie.blit(surf_glow, (em.right, y_rayo - 7))

        # Rayo exterior rojo vivo
        pygame.draw.line(superficie, (255, 45, 45), (em.right, y_rayo), (x_fin, y_rayo), 6)
        # Rayo interior blanco incandescente
        pygame.draw.line(superficie, (255, 235, 235), (em.right, y_rayo), (x_fin, y_rayo), 2)

        # Destellos en el punto de impacto
        if bloqueado:
            pygame.draw.circle(superficie, (255, 220, 80), (x_fin, y_rayo), 6)
            pygame.draw.circle(superficie, (255, 255, 255), (x_fin, y_rayo), 3)
            pygame.draw.circle(superficie, (255, 140, 40), (x_fin - 3, y_rayo - 4), 2)
            pygame.draw.circle(superficie, (255, 140, 40), (x_fin - 3, y_rayo + 4), 2)
        else:
            pygame.draw.circle(superficie, (255, 100, 80), (x_fin, y_rayo), 5)
            pygame.draw.circle(superficie, (255, 230, 200), (x_fin, y_rayo), 2)


def dibujar_paredes_colores_escenario(superficie, paredes_colores):
    if not paredes_colores:
        return
    for p in paredes_colores:
        rect = p["rect"]
        col_cuerpo = p["col_fill"]
        col_borde = p["col_borde"]
        col_luz = p["col_luz"]

        # Riel superior / soporte tecnológico en el dintel
        x_soporte = p["x"] - 4
        w_soporte = p["ancho"] + 8
        pygame.draw.rect(superficie, (65, 60, 70), (x_soporte, 162, w_soporte, 40), border_radius=3)
        pygame.draw.rect(superficie, (40, 35, 45), (x_soporte, 162, w_soporte, 40), width=2, border_radius=3)

        # La pared asoma por debajo del riel (y > 195)
        y_corte = 196
        if rect.bottom > y_corte:
            y_top_vis = max(y_corte, rect.top)
            h_vis = rect.bottom - y_top_vis
            if h_vis > 0:
                rect_vis = pygame.Rect(rect.x, y_top_vis, rect.width, h_vis)

                # Cuerpo de la pared
                pygame.draw.rect(superficie, col_cuerpo, rect_vis, border_bottom_left_radius=4, border_bottom_right_radius=4)
                pygame.draw.rect(superficie, col_borde, rect_vis, width=2, border_bottom_left_radius=4, border_bottom_right_radius=4)

                # Núcleo interior brillante estilo compuerta Pico Park
                w_core = max(4, p["ancho"] - 14)
                r_core = pygame.Rect(rect_vis.centerx - w_core // 2, rect_vis.top + 6, w_core, max(0, rect_vis.height - 14))
                if r_core.height > 2:
                    pygame.draw.rect(superficie, col_luz, r_core, border_radius=2)

                # Ranuras horizontales decorativas
                for y_g in range(235, rect_vis.bottom - 15, 38):
                    if y_corte <= y_g <= ALTO:
                        pygame.draw.line(superficie, col_borde, (rect_vis.left + 3, y_g), (rect_vis.right - 3, y_g), 2)

                # Indicador de gema circular en la base de la pared
                if rect_vis.height > 26:
                    pygame.draw.circle(superficie, (255, 255, 255), (rect_vis.centerx, rect_vis.bottom - 14), 5)
                    pygame.draw.circle(superficie, col_cuerpo, (rect_vis.centerx, rect_vis.bottom - 14), 3)


def dibujar_botones_colores_escenario(superficie, botones_colores, suelo):
    if not botones_colores:
        return
    for btn in botones_colores:
        rect = btn["rect"]
        col_cuerpo = btn["col_fill"]
        col_borde = btn["col_borde"]
        col_luz = btn["col_luz"]
        presionado = btn["presionado"]

        h_btn = 4 if presionado else 12
        y_btn = suelo.top - h_btn

        # Base mecánica fija en el suelo
        pygame.draw.rect(superficie, (75, 65, 60), (rect.left - 6, suelo.top - 4, rect.width + 12, 10), border_radius=3)
        pygame.draw.rect(superficie, (45, 38, 35), (rect.left - 6, suelo.top - 4, rect.width + 12, 10), width=2, border_radius=3)

        # Cabezal del botón móvil
        r_cab = pygame.Rect(rect.x, y_btn, rect.width, h_btn)
        pygame.draw.rect(superficie, col_cuerpo, r_cab, border_top_left_radius=4, border_top_right_radius=4)
        pygame.draw.rect(superficie, col_borde, r_cab, width=2, border_top_left_radius=4, border_top_right_radius=4)

        if not presionado and h_btn > 6:
            pygame.draw.line(superficie, col_luz, (rect.left + 6, y_btn + 2), (rect.right - 6, y_btn + 2), 2)
            pygame.draw.circle(superficie, col_luz, (rect.centerx, y_btn + h_btn // 2), 3)
        else:
            pygame.draw.line(superficie, (255, 255, 255), (rect.left + 6, y_btn + 1), (rect.right - 6, y_btn + 1), 1)


def dibujar_barrera_l_escenario(superficie, barrera_horiz, barrera_vert):
    if barrera_horiz is None or barrera_vert is None:
        return
    rect_h = barrera_horiz
    rect_v = pygame.Rect(barrera_vert.x, barrera_vert.y, barrera_vert.width, barrera_vert.height + 4)

    # Relleno del tramo horizontal y vertical como una única estructura de plataforma
    pygame.draw.rect(superficie, COLOR_PLATAFORMA, rect_h, border_top_left_radius=4)
    pygame.draw.rect(superficie, COLOR_PLATAFORMA, rect_v, border_top_right_radius=4)

    # Contorno unificado en forma de L invertida
    # 1. Borde superior completo (desde el extremo izquierdo del tramo horizontal hasta la esquina derecha)
    pygame.draw.line(superficie, COLOR_BORDE_PLATAFORMA, (rect_h.left, rect_h.top), (rect_v.right, rect_h.top), 2)
    # 2. Extremo izquierdo del tramo horizontal
    pygame.draw.line(superficie, COLOR_BORDE_PLATAFORMA, (rect_h.left, rect_h.top), (rect_h.left, rect_h.bottom), 2)
    # 3. Techo interior sobre la zona de la puerta (línea inferior del tramo horizontal)
    pygame.draw.line(superficie, COLOR_BORDE_PLATAFORMA, (rect_h.left, rect_h.bottom), (rect_v.left, rect_h.bottom), 2)
    # 4. Pared lateral exterior derecha (baja hasta el suelo)
    pygame.draw.line(superficie, COLOR_BORDE_PLATAFORMA, (rect_v.right, rect_h.top), (rect_v.right, rect_v.bottom), 2)
    # 5. Pared lateral interior izquierda (baja hasta el suelo detrás de la puerta)
    pygame.draw.line(superficie, COLOR_BORDE_PLATAFORMA, (rect_v.left, rect_h.bottom), (rect_v.left, rect_v.bottom), 2)


def dibujar_soga_escenario(superficie, p1, p2, estado_soga=None, d_reposo=DISTANCIA_SOGA_REPOSO, d_max=DISTANCIA_SOGA_MAXIMA):
    """
    Dibuja la soga que une a ambos personajes con desgaste acumulativo en la parte central:
    - Los extremos conectados a los personajes mantienen SIEMPRE su grosor original (4px exterior, 2px interior).
    - Los círculos de anclaje en la cintura conservan su tamaño original (radio 4 / 2).
    - El desgaste acumulado se concentra en la zona central y se extiende progresivamente hacia los costados.
    - Pequeñas irregularidades pixeladas en las fibras de la zona central según el nivel de daño.
    - Cuando está muy dañada (>82%), el centro es un hilo de 1px con sutil temblor armónico.
    - Si se rompe, muestra una animación limpia de rotura en el centro con los cabos colgando naturalmente.
    """
    if p1 is None or p2 is None:
        return
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]
    p_inicio = (hb1.centerx, hb1.centery + 4)
    p_fin = (hb2.centerx, hb2.centery + 4)

    dx = p_fin[0] - p_inicio[0]
    dy = p_fin[1] - p_inicio[1]
    dist = math.hypot(dx, dy)

    col_soga_ext = (175, 125, 65)
    col_soga_int = (215, 170, 105)
    col_soga_mid = (185, 135, 75)
    col_fibra_clara = (230, 185, 120)
    col_fibra_oscura = (145, 95, 40)

    # 1. Caso soga rota (animación de rotura en la parte central)
    if estado_soga and estado_soga.get("rota", False):
        if dist > 0.001:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x, dir_y = 1.0, 0.0

        t_rot = estado_soga.get("tiempo_rotura", 0)
        recoil = min(1.0, t_rot / 18.0)
        y_caida = min(36.0, t_rot * 1.6)

        len_cabo = max(26.0, 36.0 - recoil * 6.0)

        # Cabo 1 (desde P1): anclaje intacto, se afina hacia la punta rota
        m1 = (p_inicio[0] + dir_x * (len_cabo * 0.4), p_inicio[1] + (y_caida * 0.4) + 6.0)
        e1 = (p_inicio[0] + dir_x * (len_cabo * 0.8), p_inicio[1] + y_caida + 14.0)
        pygame.draw.lines(superficie, col_soga_ext, False, [p_inicio, m1], 4)
        pygame.draw.lines(superficie, col_soga_int, False, [p_inicio, m1], 2)
        pygame.draw.line(superficie, col_soga_mid, m1, e1, 2)
        pygame.draw.circle(superficie, col_soga_ext, (int(e1[0]), int(e1[1])), 1)
        pygame.draw.circle(superficie, col_soga_ext, p_inicio, 4)
        pygame.draw.circle(superficie, col_soga_int, p_inicio, 2)

        # Cabo 2 (desde P2): anclaje intacto, se afina hacia la punta rota
        m2 = (p_fin[0] - dir_x * (len_cabo * 0.4), p_fin[1] + (y_caida * 0.4) + 6.0)
        e2 = (p_fin[0] - dir_x * (len_cabo * 0.8), p_fin[1] + y_caida + 14.0)
        pygame.draw.lines(superficie, col_soga_ext, False, [p_fin, m2], 4)
        pygame.draw.lines(superficie, col_soga_int, False, [p_fin, m2], 2)
        pygame.draw.line(superficie, col_soga_mid, m2, e2, 2)
        pygame.draw.circle(superficie, col_soga_ext, (int(e2[0]), int(e2[1])), 1)
        pygame.draw.circle(superficie, col_soga_ext, p_fin, 4)
        pygame.draw.circle(superficie, col_soga_int, p_fin, 2)
        return

    en_muerte = estado_soga and estado_soga.get("en_muerte", False)
    d_max_efectivo = (d_max + 10.0) if en_muerte else d_max

    if dist < 16:
        pygame.draw.line(superficie, col_soga_ext, p_inicio, p_fin, 4)
        pygame.draw.line(superficie, col_soga_int, p_inicio, p_fin, 2)
        pygame.draw.circle(superficie, col_soga_ext, p_inicio, 4)
        pygame.draw.circle(superficie, col_soga_int, p_inicio, 2)
        pygame.draw.circle(superficie, col_soga_ext, p_fin, 4)
        pygame.draw.circle(superficie, col_soga_int, p_fin, 2)
        return

    # Tensión instantánea geométrica
    if dist <= d_reposo:
        tension_geom = 0.0
    else:
        tension_geom = min(1.0, (dist - d_reposo) / max(1.0, d_max_efectivo - d_reposo))

    dano = estado_soga.get("dano_acumulado", 0.0) if estado_soga else 0.0
    tension_act = estado_soga.get("tension", 0.0) if estado_soga else 0.0

    # Determinar comba catenaria o recta tensa
    comba = (tension_geom < 0.95 and dist < (d_max_efectivo - 2.0))
    if comba:
        sag_max = min(52.0, max(10.0, (d_max_efectivo - dist) * 0.42))
        sag = sag_max * (1.0 - (tension_geom ** 1.4))
        ctrl_x = (p_inicio[0] + p_fin[0]) / 2.0
        ctrl_y = (p_inicio[1] + p_fin[1]) / 2.0 + sag
    else:
        ctrl_x, ctrl_y = 0.0, 0.0

    # Vector normal perpendicular a la cuerda
    if dist > 0.001:
        nx = -dy / dist
        ny = dx / dist
    else:
        nx, ny = 0.0, 1.0

    # Número de pasos para renderizado suave de la cuerda
    pasos = 28
    puntos = []
    for i in range(pasos + 1):
        fr = i / pasos
        if comba:
            bx = (1 - fr) ** 2 * p_inicio[0] + 2 * (1 - fr) * fr * ctrl_x + fr ** 2 * p_fin[0]
            by = (1 - fr) ** 2 * p_inicio[1] + 2 * (1 - fr) * fr * ctrl_y + fr ** 2 * p_fin[1]
        else:
            bx = p_inicio[0] + fr * dx
            by = p_inicio[1] + fr * dy
        puntos.append((bx, by))

    ticks = pygame.time.get_ticks()

    # Si no hay daño acumulado, renderizado uniforme clásico de grosor original
    if dano <= 0.01:
        pygame.draw.lines(superficie, col_soga_ext, False, puntos, 4)
        pygame.draw.lines(superficie, col_soga_int, False, puntos, 2)
    else:
        # El efecto aparece ÚNICAMENTE en la parte central:
        # Los extremos mantienen grosor original (4px / 2px).
        # El centro se hace progresivamente más fino y se extiende hacia los costados.
        ancho_zona_desgaste = 0.08 + 0.16 * dano  # Entre 16% y 48% de la longitud total centrada en s=0.5

        for i in range(pasos):
            p_a = puntos[i]
            p_b = puntos[i + 1]
            s_mid = (i + 0.5) / pasos
            dist_centro = abs(s_mid - 0.5)

            if dist_centro >= ancho_zona_desgaste:
                # Fuera de la zona central desgastada: grosor original completo (4px exterior, 2px interior)
                pygame.draw.line(superficie, col_soga_ext, p_a, p_b, 4)
                pygame.draw.line(superficie, col_soga_int, p_a, p_b, 2)
            else:
                # Dentro de la zona central desgastada:
                # Intensidad local del desgaste (1.0 en el centro exacto s=0.5, 0.0 en el borde)
                factor_centro = 1.0 - (dist_centro / ancho_zona_desgaste)
                desgaste_local = dano * (factor_centro ** 1.3)

                if desgaste_local < 0.22:
                    # Inicio de afinamiento en el centro (3px exterior, 1px interior)
                    pygame.draw.line(superficie, col_soga_ext, p_a, p_b, 3)
                    pygame.draw.line(superficie, col_soga_int, p_a, p_b, 1)
                elif desgaste_local < 0.55:
                    # Zona central notablemente más fina (2px sólido con tono dorado medio)
                    pygame.draw.line(superficie, col_soga_mid, p_a, p_b, 2)
                    pygame.draw.line(superficie, col_fibra_clara, p_a, p_b, 1)
                elif desgaste_local < 0.82:
                    # Zona central fina (1px) con irregularidades pixeladas de fibras cediendo
                    pygame.draw.line(superficie, col_soga_mid, p_a, p_b, 1)
                    # Pequeña irregularidad pixelada alterna simulando hebras de fibra cediendo
                    if i % 2 == 1:
                        offset_x = nx * (1.0 if (i % 4 == 1) else -1.0)
                        offset_y = ny * (1.0 if (i % 4 == 1) else -1.0)
                        p_irr_a = (p_a[0] + offset_x, p_a[1] + offset_y)
                        p_irr_b = (p_b[0] + offset_x, p_b[1] + offset_y)
                        pygame.draw.line(superficie, col_fibra_oscura, p_irr_a, p_irr_b, 1)
                else:
                    # Daño crítico (>82%): la parte central parece a punto de cortarse (1px nítido + temblor sutil)
                    vibr_px = 0.0
                    if tension_act > 0.35:
                        vibr_px = math.sin(ticks * 0.14 + i * 0.8) * 1.0

                    p_v_a = (p_a[0] + nx * vibr_px, p_a[1] + ny * vibr_px)
                    p_v_b = (p_b[0] + nx * vibr_px, p_b[1] + ny * vibr_px)
                    pygame.draw.line(superficie, col_soga_mid, p_v_a, p_v_b, 1)

                    # Micro-irregularidad pixelada de fibra estirada al límite
                    if i % 2 == 0:
                        irr_px = 1.0 if (i % 4 == 0) else -1.0
                        pygame.draw.line(superficie, col_fibra_clara,
                                         (p_v_a[0] + nx * irr_px, p_v_a[1] + ny * irr_px),
                                         (p_v_b[0] + nx * irr_px, p_v_b[1] + ny * irr_px), 1)

    # Anclajes en la cintura de los personajes: SIEMPRE conservan su tamaño y grosor original
    pygame.draw.circle(superficie, col_soga_ext, p_inicio, 4)
    pygame.draw.circle(superficie, col_soga_int, p_inicio, 2)
    pygame.draw.circle(superficie, col_soga_ext, p_fin, 4)
    pygame.draw.circle(superficie, col_soga_int, p_fin, 2)


# ==============================================================================
# ELEMENTOS VISUALES INVERNALES Y NAVIDEÑOS — MUNDO 1: BOSQUE NEVADO
# ==============================================================================

_CACHE_FONDO_MUNDO1 = {}
_PARTICULAS_NIEVE_M1 = None


def generar_fondo_mundo1(ancho_mundo, alto=ALTO):
    """
    Genera y cachea el fondo invernal y navideño pixel art para Mundo 1:
    cielo crepuscular frío, estrellas sutiles, luna llena y cordillera
    de montañas nevadas facetadas con treeline de pinos.
    """
    if ancho_mundo in _CACHE_FONDO_MUNDO1:
        return _CACHE_FONDO_MUNDO1[ancho_mundo]

    w_low = ancho_mundo // 2
    h_low = alto // 2
    surf_low = pygame.Surface((w_low, h_low))

    # 1. Cielo crepuscular invernal frío
    bandas = [
        (0,   65,  (14, 20, 42)),   # Azul medianoche invernal
        (65,  130, (22, 34, 65)),   # Azul zafiro frío
        (130, 195, (38, 56, 92)),   # Azul crepúsculo
        (195, 255, (58, 82, 125)),  # Azul frío suave
        (255, 360, (92, 120, 164)), # Resplandor helado sobre montañas
    ]
    for y1, y2, col in bandas:
        pygame.draw.rect(surf_low, col, (0, y1, w_low, y2 - y1))

    # Difuminado dither suave entre bandas del cielo
    for i in range(len(bandas) - 1):
        yt = bandas[i][1]
        c1, c2 = bandas[i][2], bandas[i + 1][2]
        for dy in range(-2, 3):
            y = yt + dy
            if 0 <= y < h_low:
                for x in range(w_low):
                    if dy == -2 and (x + y) % 4 == 0: surf_low.set_at((x, y), c2)
                    elif dy == -1 and (x % 2 == 0 and y % 2 == 0): surf_low.set_at((x, y), c2)
                    elif dy == 0 and (x + y) % 2 == 0: surf_low.set_at((x, y), c2)
                    elif dy == 1 and (x % 2 == 0 and y % 2 == 0): surf_low.set_at((x, y), c1)
                    elif dy == 2 and (x + y) % 4 == 0: surf_low.set_at((x, y), c1)

    # 2. Estrellas nocturnas discretas
    rnd_est = random.Random(2025)
    for _ in range(w_low // 9):
        sx = rnd_est.randint(5, w_low - 5)
        sy = rnd_est.randint(4, 175)
        c_star = rnd_est.choice([(255, 255, 255), (210, 235, 255), (240, 245, 255), (180, 210, 250)])
        surf_low.set_at((sx, sy), c_star)
        if rnd_est.random() < 0.12:
            surf_low.set_at((sx + 1, sy), (170, 200, 245))
            surf_low.set_at((sx, sy + 1), (170, 200, 245))

    # Luna llena invernal
    lx, ly, lr = w_low - 110, 46, 16
    for dy in range(-lr, lr + 1):
        for dx in range(-lr, lr + 1):
            d2 = dx * dx + dy * dy
            if d2 <= lr * lr:
                surf_low.set_at((lx + dx, ly + dy), (250, 252, 255))
            elif d2 <= (lr + 2) * (lr + 2):
                surf_low.set_at((lx + dx, ly + dy), (100, 130, 175))

    # 3. Cordillera de montañas nevadas facetadas estilo pixel art
    y_base = 275
    rnd_p = random.Random(888)
    paso_pico = 110
    for px in range(-60, w_low + 120, paso_pico):
        py = rnd_p.randint(95, 140)
        wm = rnd_p.randint(160, 220)
        h_snow = int((y_base - py) * 0.32)
        for y in range(py, y_base):
            prog = (y - py) / float(y_base - py)
            half = int((wm // 2) * prog)
            for x in range(px - half, px):
                if 0 <= x < w_low:
                    es_nieve = (y - py < h_snow + (x % 3))
                    col = (252, 254, 255) if es_nieve else (72, 92, 130)
                    surf_low.set_at((x, y), col)
            for x in range(px, px + half + 1):
                if 0 <= x < w_low:
                    es_nieve = (y - py < h_snow + ((x + 1) % 3))
                    col = (205, 224, 248) if es_nieve else (48, 64, 96)
                    surf_low.set_at((x, y), col)

    # 4. Colinas nevadas intermedias
    for x in range(w_low):
        y_hill = 238 + int(14 * math.sin(x * 0.015 + 0.8))
        for y in range(y_hill, h_low):
            surf_low.set_at((x, y), (185, 208, 238) if y < y_hill + 8 else (132, 158, 196))

    # Siluetas de pinos en la colina nevada lejana
    for x_tree in range(12, w_low - 10, 18):
        y_tree = 238 + int(14 * math.sin(x_tree * 0.015 + 0.8))
        h_t = 11 + (x_tree % 6)
        pygame.draw.polygon(surf_low, (22, 48, 38), [(x_tree, y_tree - h_t), (x_tree - 4, y_tree), (x_tree + 4, y_tree)])
        surf_low.set_at((x_tree, y_tree - h_t), (250, 252, 255))

    surf_final = pygame.transform.scale(surf_low, (ancho_mundo, alto))
    _CACHE_FONDO_MUNDO1[ancho_mundo] = surf_final
    return surf_final


def dibujar_fondo_mundo1_invierno(superficie, ancho_mundo):
    superficie.blit(generar_fondo_mundo1(ancho_mundo, superficie.get_height()), (0, 0))


def dibujar_escenario_mundo1(superficie, suelo, plataformas, pozo_nivel=None):
    """
    Dibuja el suelo y las plataformas con manto de nieve y relieve invernal.
    """
    col_tierra = (65, 80, 105)
    col_nieve_sombra = (210, 230, 250)
    col_nieve_pura = (252, 254, 255)
    col_plat_cuerpo = (82, 105, 134)
    col_plat_borde = (52, 68, 90)

    if pozo_nivel is not None:
        pz = pozo_nivel
        pygame.draw.rect(superficie, (38, 50, 72), (pz["x"], pz["y"], pz["ancho"], pz["alto"]))
        pygame.draw.line(superficie, col_plat_borde, (pz["x"], pz["y"]), (pz["x"], pz["y"] + pz["alto"]), 2)
        pygame.draw.line(superficie, col_plat_borde, (pz["x"] + pz["ancho"], pz["y"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

    for plat in plataformas:
        if plat.bottom >= suelo.top:
            rect_torre = pygame.Rect(plat.x, plat.y, plat.width, plat.height + 4)
            pygame.draw.rect(superficie, col_plat_cuerpo, rect_torre, border_top_left_radius=4, border_top_right_radius=4)
            pygame.draw.rect(superficie, col_plat_borde, rect_torre, width=2, border_top_left_radius=4, border_top_right_radius=4)
        else:
            pygame.draw.rect(superficie, col_plat_cuerpo, plat, border_radius=4)
            pygame.draw.rect(superficie, col_plat_borde, plat, width=2, border_radius=4)

        # Capa fina de nieve en la parte superior (sin alterar colisiones ni hitboxes)
        h_nieve = min(6, max(3, plat.height // 3))
        r_nieve = pygame.Rect(plat.x + 2, plat.y + 1, plat.width - 4, h_nieve)
        pygame.draw.rect(superficie, col_nieve_pura, r_nieve, border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.line(superficie, col_nieve_sombra, (plat.x + 3, plat.y + h_nieve), (plat.right - 4, plat.y + h_nieve), 1)

        # Si es una plataforma flotante en el aire, pequeños carámbanos de hielo abajo
        if plat.bottom < suelo.top - 20 and plat.width >= 30:
            paso_hielo = 22
            for ix in range(plat.x + 8, plat.right - 8, paso_hielo):
                len_h = 4 + (ix % 5)
                pts_hielo = [(ix, plat.bottom - 1), (ix + 2, plat.bottom + len_h), (ix + 4, plat.bottom - 1)]
                pygame.draw.polygon(superficie, (215, 240, 255), pts_hielo)

    # Suelo principal con manto de nieve
    pygame.draw.rect(superficie, col_tierra, suelo)
    pygame.draw.rect(superficie, col_nieve_sombra, (suelo.x, suelo.y, suelo.width, 14))
    pygame.draw.rect(superficie, col_nieve_pura, (suelo.x, suelo.y, suelo.width, 8))
    for sx in range(0, suelo.width, 32):
        pygame.draw.circle(superficie, col_nieve_pura, (sx + 16, suelo.y), 4)

    if pozo_nivel is not None:
        pygame.draw.line(superficie, col_plat_borde, (pz["x"], pz["y"] + pz["alto"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)


def dibujar_decoraciones_mundo1(superficie, suelo, ancho_mundo, tick=0):
    """
    Dibuja árboles de Navidad decorados con luces titilantes y paquetes de regalos.
    """
    col_luces = [(255, 60, 60), (255, 220, 50), (60, 210, 255), (80, 240, 90)]
    py = suelo.top

    # Pinos navideños decorados
    for px in range(280, ancho_mundo - 160, 360):
        pygame.draw.rect(superficie, (52, 36, 24), (px + 18, py - 32, 8, 32))
        capas = [(48, 38, py - 62), (38, 34, py - 92), (28, 28, py - 116)]
        for w_p, h_p, y_p in capas:
            pts_pino = [(px + 22 - w_p // 2, y_p + h_p), (px + 22, y_p), (px + 22 + w_p // 2, y_p + h_p)]
            pygame.draw.polygon(superficie, (22, 68, 38), pts_pino)
            pygame.draw.line(superficie, (248, 252, 255), (px + 22 - w_p // 2, y_p + h_p), (px + 22 - w_p // 4, y_p + h_p - 3), 3)
            pygame.draw.line(superficie, (248, 252, 255), (px + 22 + w_p // 2, y_p + h_p), (px + 22 + w_p // 4, y_p + h_p - 3), 3)

        # Estrella dorada en la cima
        pygame.draw.circle(superficie, (255, 225, 60), (px + 22, py - 120), 5)
        pygame.draw.circle(superficie, (255, 245, 160), (px + 22, py - 120), 2)

        # Luces festivas titilantes
        offsets_luces = [(-10, -50), (8, -55), (-6, -75), (10, -80), (0, -100)]
        for i_l, (lx_off, ly_off) in enumerate(offsets_luces):
            fase = (tick // 15 + i_l) % len(col_luces)
            pygame.draw.circle(superficie, col_luces[fase], (px + 22 + lx_off, py + ly_off), 2)

    # Pequeños regalos decorativos sin obstaculizar
    for gx in range(410, ancho_mundo - 120, 480):
        gy = py - 16
        c_box = (220, 45, 45) if (gx % 2 == 0) else (38, 142, 64)
        c_ribbon = (255, 215, 60) if (gx % 2 == 0) else (235, 55, 55)
        pygame.draw.rect(superficie, c_box, (gx, gy, 14, 16), border_radius=2)
        pygame.draw.line(superficie, c_ribbon, (gx + 7, gy), (gx + 7, gy + 15), 2)
        pygame.draw.line(superficie, c_ribbon, (gx, gy + 8), (gx + 13, gy + 8), 2)
        pygame.draw.circle(superficie, c_ribbon, (gx + 7, gy - 1), 3)


def actualizar_y_dibujar_nieve_mundo1(superficie, ancho_mundo, tick=0):
    """
    Simula partículas de nieve animada cayendo suavemente en Mundo 1.
    """
    global _PARTICULAS_NIEVE_M1
    alto = superficie.get_height()
    if _PARTICULAS_NIEVE_M1 is None:
        rnd = random.Random(101)
        _PARTICULAS_NIEVE_M1 = [
            {
                'x': rnd.uniform(0, ancho_mundo),
                'y': rnd.uniform(0, alto),
                'vy': rnd.uniform(1.0, 1.8),
                'tam': rnd.choice([2, 2, 3]),
                'seed': rnd.uniform(0, 10)
            }
            for _ in range(50)
        ]
    for c in _PARTICULAS_NIEVE_M1:
        c['y'] += c['vy']
        c['x'] += math.sin(tick * 0.03 + c['seed']) * 0.45
        if c['y'] > alto - 10:
            c['y'] = -5
            c['x'] = (c['x'] + random.uniform(-20, 20)) % ancho_mundo
        col = (255, 255, 255) if c['tam'] > 2 else (220, 240, 255)
        pygame.draw.rect(superficie, col, (int(c['x']), int(c['y']), c['tam'], c['tam']))


# ==============================================================================
# ELEMENTOS VISUALES RUINAS ANTIGUAS Y TEMPLO ABANDONADO — MUNDO 2
# ==============================================================================

_CACHE_FONDO_MUNDO2 = {}
_PARTICULAS_POLVO_M2 = None


def generar_fondo_mundo2(ancho_mundo, alto=ALTO):
    """
    Genera y cachea el fondo de ruinas antiguas y templo abandonado para Mundo 2:
    cielo crepuscular de desierto cálido, sol abrasador suave, siluetas de pirámides
    escalonadas ancestrales (zigurats), obeliscos y muro de cantería con hornacinas.
    """
    if ancho_mundo in _CACHE_FONDO_MUNDO2:
        return _CACHE_FONDO_MUNDO2[ancho_mundo]

    w_low = ancho_mundo // 2
    h_low = alto // 2
    surf_low = pygame.Surface((w_low, h_low))

    # 1. Cielo crepuscular cálido de desierto
    bandas = [
        (0,   60,  (145, 105, 68)),   # Ámbar oscuro ancestral
        (60,  125, (175, 132, 92)),   # Ocre cálido
        (125, 195, (205, 165, 122)),  # Arena dorada
        (195, 255, (226, 192, 150)),  # Resplandor crepuscular cálido
        (255, 360, (238, 212, 175)),  # Horizonte dorado
    ]
    for y1, y2, col in bandas:
        pygame.draw.rect(surf_low, col, (0, y1, w_low, y2 - y1))

    # Dither suave entre bandas del cielo
    for i in range(len(bandas) - 1):
        yt = bandas[i][1]
        c1, c2 = bandas[i][2], bandas[i + 1][2]
        for dy in range(-2, 3):
            y = yt + dy
            if 0 <= y < h_low:
                for x in range(w_low):
                    if dy == -2 and (x + y) % 4 == 0: surf_low.set_at((x, y), c2)
                    elif dy == -1 and (x % 2 == 0 and y % 2 == 0): surf_low.set_at((x, y), c2)
                    elif dy == 0 and (x + y) % 2 == 0: surf_low.set_at((x, y), c2)
                    elif dy == 1 and (x % 2 == 0 and y % 2 == 0): surf_low.set_at((x, y), c1)
                    elif dy == 2 and (x + y) % 4 == 0: surf_low.set_at((x, y), c1)

    # Sol suave en la lejanía
    sx, sy, sr = 120, 55, 16
    for dy in range(-sr, sr + 1):
        for dx in range(-sr, sr + 1):
            d2 = dx * dx + dy * dy
            if d2 <= sr * sr:
                surf_low.set_at((sx + dx, sy + dy), (255, 248, 220))
            elif d2 <= (sr + 2) * (sr + 2):
                surf_low.set_at((sx + dx, sy + dy), (235, 195, 135))

    # 2. Siluetas de pirámides escalonadas ancestrales (zigurats) y obeliscos
    col_pyr_luz = (158, 118, 85)
    col_pyr_sombra = (128, 92, 62)
    col_obelisco = (142, 104, 74)

    paso_zigurat = 320
    for cx in range(160, w_low + 200, paso_zigurat):
        top_y = 135
        n_steps = 6
        for stp in range(n_steps):
            sy_cur = top_y + stp * 13
            sw = 18 + stp * 22
            pygame.draw.rect(surf_low, col_pyr_luz, (cx - sw, sy_cur, sw, 13))
            pygame.draw.rect(surf_low, col_pyr_sombra, (cx, sy_cur, sw, 13))
            if stp == 0:
                pygame.draw.rect(surf_low, col_pyr_luz, (cx - 10, sy_cur - 10, 10, 10))
                pygame.draw.rect(surf_low, col_pyr_sombra, (cx, sy_cur - 10, 10, 10))

    # Obeliscos entre los templos
    for ox in range(60, w_low + 100, 260):
        oy, oh = 175, 42
        pts_ob_luz = [(ox - 4, oy + oh), (ox - 3, oy + 8), (ox, oy), (ox, oy + oh)]
        pts_ob_sombra = [(ox, oy), (ox + 3, oy + 8), (ox + 4, oy + oh), (ox, oy + oh)]
        pygame.draw.polygon(surf_low, col_obelisco, pts_ob_luz)
        pygame.draw.polygon(surf_low, col_pyr_sombra, pts_ob_sombra)

    # 3. Muro / terraza de cantería de piedra en el plano medio
    y_mesa = 228
    col_mesa_top = (198, 164, 124)
    col_mesa_face = (168, 132, 94)
    col_mortero_bg = (135, 100, 68)

    pygame.draw.rect(surf_low, col_mesa_face, (0, y_mesa, w_low, h_low - y_mesa))
    pygame.draw.rect(surf_low, col_mesa_top, (0, y_mesa, w_low, 6))

    # Bloques de cantería de piedra del templo antiguo
    for bx in range(0, w_low, 48):
        for by in range(y_mesa + 6, h_low, 22):
            off = 24 if ((by // 22) % 2 == 1) else 0
            x_line = bx + off
            pygame.draw.line(surf_low, col_mortero_bg, (0, by), (w_low, by), 1)
            pygame.draw.line(surf_low, col_mortero_bg, (x_line, by), (x_line, by + 22), 1)

    # Hornacinas y arcos en el muro de fondo
    for ax in range(40, w_low, 110):
        ay = y_mesa + 12
        pygame.draw.rect(surf_low, (110, 78, 52), (ax, ay, 20, 32), border_top_left_radius=10, border_top_right_radius=10)

    surf_final = pygame.transform.scale(surf_low, (ancho_mundo, alto))
    _CACHE_FONDO_MUNDO2[ancho_mundo] = surf_final
    return surf_final


def dibujar_fondo_mundo2_ruinas(superficie, ancho_mundo):
    superficie.blit(generar_fondo_mundo2(ancho_mundo, superficie.get_height()), (0, 0))


def dibujar_escenario_mundo2(superficie, suelo, plataformas, pozo_nivel=None):
    """
    Dibuja el suelo y las plataformas con apariencia de bloques de templo esculpidos y lajas de arenisca.
    """
    col_base_suelo = (142, 112, 78)
    col_laja_arenisca = (188, 158, 118)
    col_mortero = (115, 88, 58)
    col_musgo = (55, 95, 45)

    if pozo_nivel is not None:
        pz = pozo_nivel
        pygame.draw.rect(superficie, (75, 54, 38), (pz["x"], pz["y"], pz["ancho"], pz["alto"]))
        pygame.draw.line(superficie, col_mortero, (pz["x"], pz["y"]), (pz["x"], pz["y"] + pz["alto"]), 2)
        pygame.draw.line(superficie, col_mortero, (pz["x"] + pz["ancho"], pz["y"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

    for plat in plataformas:
        if plat.bottom >= suelo.top:
            rect_torre = pygame.Rect(plat.x, plat.y, plat.width, plat.height + 4)
            pygame.draw.rect(superficie, col_laja_arenisca, rect_torre, border_top_left_radius=4, border_top_right_radius=4)
            pygame.draw.rect(superficie, col_mortero, rect_torre, width=2, border_top_left_radius=4, border_top_right_radius=4)
        else:
            pygame.draw.rect(superficie, col_laja_arenisca, plat, border_radius=4)
            pygame.draw.rect(superficie, col_mortero, plat, width=2, border_radius=4)

        # División en bloques de cantería
        paso_bloque = 60
        for bx in range(plat.x + paso_bloque, plat.right - 10, paso_bloque):
            pygame.draw.line(superficie, col_mortero, (bx, plat.y + 2), (bx, plat.bottom - 2), 2)

        # Grieta sutil decorativa en plataformas anchas
        if plat.width >= 100:
            gx = plat.x + 35
            gy = plat.y + 6
            pygame.draw.line(superficie, col_mortero, (gx, gy), (gx + 6, gy + 8), 1)
            pygame.draw.line(superficie, col_mortero, (gx + 6, gy + 8), (gx + 12, gy + 14), 1)

        # Detalles de musgo en esquinas
        pygame.draw.rect(superficie, col_musgo, (plat.x + 2, plat.bottom - 6, 12, 4), border_radius=2)
        pygame.draw.rect(superficie, col_musgo, (plat.right - 14, plat.y + 2, 10, 4), border_radius=2)

    # Suelo principal de grandes lajas de arenisca antigua tallada
    pygame.draw.rect(superficie, col_base_suelo, suelo)
    pygame.draw.rect(superficie, col_laja_arenisca, (suelo.x, suelo.y, suelo.width, 24))
    for lx in range(suelo.x, suelo.right, 80):
        pygame.draw.line(superficie, col_mortero, (lx, suelo.y), (lx, suelo.y + 24), 2)
        if (lx // 80) % 2 == 0:
            pygame.draw.rect(superficie, col_musgo, (lx - 6, suelo.y + 1, 12, 4), border_radius=2)

    if pozo_nivel is not None:
        pygame.draw.line(superficie, col_mortero, (pz["x"], pz["y"] + pz["alto"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)


def dibujar_decoraciones_mundo2(superficie, suelo, ancho_mundo, tick=0, pozo_nivel=None):
    """
    Dibuja columnas de piedra antiguas (enteras y rotas) con enredaderas y antorchas con llamas animadas.
    """
    col_columna = (175, 145, 108)
    col_columna_sombra = (130, 100, 70)
    col_musgo = (48, 88, 40)
    cy_base = suelo.top

    # Columnas de piedra
    for cx in range(260, ancho_mundo - 120, 320):
        if pozo_nivel and (pozo_nivel["x"] - 20 <= cx <= pozo_nivel["x"] + pozo_nivel["ancho"] + 20):
            continue

        entera = ((cx // 320) % 2 == 0)
        w_col = 32
        h_col = 220 if entera else 130

        pygame.draw.rect(superficie, col_columna_sombra, (cx - 4, cy_base - 14, w_col + 8, 14))
        pygame.draw.rect(superficie, col_columna, (cx - 2, cy_base - 12, w_col + 4, 10))

        pygame.draw.rect(superficie, col_columna, (cx, cy_base - h_col, w_col, h_col - 14))
        pygame.draw.line(superficie, col_columna_sombra, (cx + 8, cy_base - h_col), (cx + 8, cy_base - 14), 2)
        pygame.draw.line(superficie, col_columna_sombra, (cx + 22, cy_base - h_col), (cx + 22, cy_base - 14), 2)

        if entera:
            pygame.draw.rect(superficie, col_columna_sombra, (cx - 6, cy_base - h_col - 12, w_col + 12, 12))
            pygame.draw.rect(superficie, col_columna, (cx - 4, cy_base - h_col - 10, w_col + 8, 8))
        else:
            pygame.draw.polygon(superficie, (200, 170, 130), [
                (cx, cy_base - h_col), (cx + 8, cy_base - h_col + 8),
                (cx + 18, cy_base - h_col - 4), (cx + w_col, cy_base - h_col + 10),
                (cx + w_col, cy_base - h_col),
            ])

        for vy in range(cy_base - 20, cy_base - h_col + 20, -25):
            pygame.draw.circle(superficie, col_musgo, (cx + 2, vy), 4)
            pygame.draw.circle(superficie, (65, 110, 50), (cx + 6, vy + 4), 3)

    # Antorchas con llamas animadas sutiles en la pared
    frame_fuego = (tick // 10) % 3
    col_llama_ext = (245, 130, 30)
    col_llama_int = (255, 220, 70)

    for tx in range(180, ancho_mundo - 80, 380):
        ty = cy_base - 140
        pygame.draw.rect(superficie, (85, 60, 42), (tx - 3, ty, 6, 18))
        pygame.draw.rect(superficie, (110, 80, 55), (tx - 5, ty - 4, 10, 5))

        s_glow = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(s_glow, (255, 180, 50, 22), (22, 22), 20)
        superficie.blit(s_glow, (tx - 22, ty - 22))

        off_fuego = [(0, -10), (1, -12), (-1, -11)][frame_fuego]
        pygame.draw.polygon(superficie, col_llama_ext, [
            (tx - 4, ty - 4), (tx, ty + off_fuego[1]), (tx + 4, ty - 4)
        ])
        pygame.draw.circle(superficie, col_llama_int, (tx + off_fuego[0], ty - 6), 3)


def actualizar_y_dibujar_polvo_mundo2(superficie, ancho_mundo, tick=0):
    """
    Simula partículas sutiles de polvo dorado flotando en las ruinas de Mundo 2.
    """
    global _PARTICULAS_POLVO_M2
    alto = superficie.get_height()
    if _PARTICULAS_POLVO_M2 is None:
        rnd = random.Random(202)
        _PARTICULAS_POLVO_M2 = [
            {
                'x': rnd.uniform(0, ancho_mundo),
                'y': rnd.uniform(200, alto - 90),
                'vy': rnd.uniform(-0.4, -0.9),
                'seed': rnd.uniform(0, 10)
            }
            for _ in range(30)
        ]
    for p in _PARTICULAS_POLVO_M2:
        p['y'] += p['vy']
        p['x'] += math.sin(tick * 0.02 + p['seed']) * 0.35
        if p['y'] < 190:
            p['y'] = alto - 90
            p['x'] = (p['x'] + random.uniform(-30, 30)) % ancho_mundo
        pygame.draw.rect(superficie, (235, 195, 120), (int(p['x']), int(p['y']), 2, 2))


# ==============================================================================
# ELEMENTOS VISUALES SUBMARINOS — MUNDO 3: EL JARDÍN DE ALGAS
# ==============================================================================

_CACHE_FONDO_MUNDO3 = {}
_SURF_RAYOS_SOL = None
_CACHE_BURBUJAS_M3 = {}


def dibujar_submarino_fondo_escenario(superficie, ancho_mundo, tick=0, rangos=None):
    """
    Renderiza el fondo marino completo con gradiente oceánico profundo,
    rayos de sol volumétricos y siluetas subacuáticas distantes.
    """
    alto = superficie.get_height()
    if ancho_mundo not in _CACHE_FONDO_MUNDO3:
        surf_fondo = pygame.Surface((ancho_mundo, alto))
        pasos = 32
        h_paso = alto / float(pasos)
        for i in range(pasos):
            ratio = i / float(pasos - 1)
            # De azul turquesa claro superficial a azul marino abisal
            r = int(22 * (1.0 - ratio) + 9 * ratio)
            g = int(135 * (1.0 - ratio) + 45 * ratio)
            b = int(195 * (1.0 - ratio) + 88 * ratio)
            y_i = int(i * h_paso)
            h_i = int(h_paso) + 2
            pygame.draw.rect(surf_fondo, (r, g, b), (0, y_i, ancho_mundo, h_i))

        # Siluetas lejanas de arrecifes de fondo
        col_silueta = (14, 60, 105)
        for sx in range(0, ancho_mundo, 220):
            puntos_silueta = [
                (sx, alto - 80),
                (sx + 50, alto - 170),
                (sx + 110, alto - 190),
                (sx + 160, alto - 150),
                (sx + 220, alto - 80),
            ]
            pygame.draw.polygon(surf_fondo, col_silueta, puntos_silueta)

        _CACHE_FONDO_MUNDO3[ancho_mundo] = surf_fondo

    # El mundo mide hasta 2600 px pero la cámara muestra 1280: con `rangos` solo se pintan
    # los tramos que se van a ver este frame (el resultado visible es idéntico).
    if rangos is None:
        rangos = [(0, ancho_mundo)]
    for x0, x1 in rangos:
        superficie.blit(_CACHE_FONDO_MUNDO3[ancho_mundo], (x0, 0), pygame.Rect(x0, 0, x1 - x0, alto))

    # Rayos de sol volumétricos que filtran desde la superficie (reutiliza superficie para evitar sobrecarga de memoria)
    global _SURF_RAYOS_SOL
    if _SURF_RAYOS_SOL is None or _SURF_RAYOS_SOL.get_width() != ancho_mundo:
        _SURF_RAYOS_SOL = pygame.Surface((ancho_mundo, 520), pygame.SRCALPHA)
    else:
        for x0, x1 in rangos:
            _SURF_RAYOS_SOL.fill((0, 0, 0, 0), pygame.Rect(x0, 0, x1 - x0, 520))

    paso_rayo = 380
    for rx in range(80, ancho_mundo + 200, paso_rayo):
        oscilacion = math.sin((tick * 0.02) + (rx * 0.005)) * 25.0
        x_base = rx + oscilacion
        ancho_rayo = 90
        if not any(x_base - 140 < x1 and x_base + ancho_rayo > x0 for x0, x1 in rangos):
            continue
        poly_pts = [
            (x_base, 0),
            (x_base + ancho_rayo, 0),
            (x_base + ancho_rayo - 120, 520),
            (x_base - 140, 520),
        ]
        alpha_rayo = int(20 + 8 * math.sin(tick * 0.03 + rx))
        pygame.draw.polygon(_SURF_RAYOS_SOL, (220, 245, 255, max(10, alpha_rayo)), poly_pts)

    for x0, x1 in rangos:
        superficie.blit(_SURF_RAYOS_SOL, (x0, 0), pygame.Rect(x0, 0, x1 - x0, 520))

    # Ondulación translúcida en la superficie superior del agua (y = 0..25)
    for wx in range(0, ancho_mundo, 24):
        if not any(wx + 16 >= x0 and wx <= x1 for x0, x1 in rangos):
            continue
        onda_y = int(math.sin((wx + tick * 2.0) * 0.06) * 3)
        pygame.draw.line(superficie, (180, 235, 255), (wx, 10 + onda_y), (wx + 16, 10 + onda_y), 2)


# ------------------------------------------------------------------------------
# Capas estáticas del mundo 3 (lecho, rocas, erizos): se dibujan una sola vez por nivel
# en una superficie con alfa y después solo se copia el tramo visible. Son ~700 llamadas
# a pygame.draw por frame que no cambian nunca. Las funciones de dibujo originales se
# siguen usando para generar la capa, así que el resultado es píxel a píxel el mismo.
# ------------------------------------------------------------------------------
_CAPAS_ESTATICAS_M3 = {}
_MAX_CAPAS_ESTATICAS_M3 = 6
_COLOR_LLAVE_CAPAS = (1, 1, 2)   # color que no usa ninguna de estas funciones de dibujo


def obtener_capa_estatica_m3(nombre, origen, ancho_mundo, alto, dibujar):
    """
    Devuelve la capa cacheada para `origen` (la lista/rect que define el dibujo). La clave
    guarda una referencia a `origen` para no confundir objetos distintos que reutilicen el
    mismo id; al reiniciar un laberinto aleatorio se genera una capa nueva y la más vieja
    se descarta.
    """
    clave = (nombre, id(origen), ancho_mundo)
    entrada = _CAPAS_ESTATICAS_M3.get(clave)
    if entrada is None or entrada[0] is not origen:
        # Superficie opaca con color llave en vez de canal alfa: todo lo que dibujan estas
        # funciones es opaco, y el blit con color llave (RLE) es varias veces más rápido
        # que una mezcla alfa de 1280x720 por capa y por frame.
        capa = pygame.Surface((ancho_mundo, alto)).convert()
        capa.fill(_COLOR_LLAVE_CAPAS)
        dibujar(capa)
        capa.set_colorkey(_COLOR_LLAVE_CAPAS, pygame.RLEACCEL)
        if len(_CAPAS_ESTATICAS_M3) >= _MAX_CAPAS_ESTATICAS_M3:
            del _CAPAS_ESTATICAS_M3[next(iter(_CAPAS_ESTATICAS_M3))]
        entrada = (origen, capa)
        _CAPAS_ESTATICAS_M3[clave] = entrada
    return entrada[1]


def blit_capa_en_rangos(superficie, capa, rangos):
    alto = capa.get_height()
    for x0, x1 in rangos:
        superficie.blit(capa, (x0, 0), pygame.Rect(x0, 0, x1 - x0, alto))


def dibujar_lecho_marino(superficie, suelo_rect, ancho_mundo):
    """
    Dibuja el lecho marino con arena oceánica texturizada, conchillas y relieve.
    """
    col_arena = (52, 98, 138)
    col_borde_arena = (82, 148, 188)
    col_sombra = (36, 68, 100)

    pygame.draw.rect(superficie, col_arena, suelo_rect)
    pygame.draw.line(superficie, col_borde_arena, (0, suelo_rect.top), (ancho_mundo, suelo_rect.top), 4)
    pygame.draw.line(superficie, col_sombra, (0, suelo_rect.top + 5), (ancho_mundo, suelo_rect.top + 5), 2)

    # Guijarros y pequeñas conchillas esparcidas por la arena
    for px in range(35, ancho_mundo, 85):
        h_mod = (px % 7) - 3
        pygame.draw.circle(superficie, (115, 175, 215), (px, suelo_rect.top + 14 + h_mod), 3)
        pygame.draw.circle(superficie, (230, 220, 195), (px + 18, suelo_rect.top + 8), 2)


def dibujar_rocas_submarinas_escenario(superficie, rocas_info):
    """
    Dibuja formaciones rocosas marinas naturales, arcos y salientes con texturas
    oceánicas de piedra y crecimiento de musgo/coral.
    """
    col_roca = (54, 82, 112)
    col_luz = (86, 128, 168)
    col_crevice = (34, 52, 74)
    col_alga_musgo = (46, 148, 98)

    for r_item in rocas_info:
        rect = r_item["rect"] if isinstance(r_item, dict) else r_item
        pygame.draw.rect(superficie, col_roca, rect, border_radius=6)
        pygame.draw.rect(superficie, col_crevice, rect, width=2, border_radius=6)
        pygame.draw.line(superficie, col_luz, (rect.left + 4, rect.top + 2), (rect.right - 4, rect.top + 2), 3)

        if rect.width >= 30:
            pygame.draw.line(superficie, col_alga_musgo, (rect.left + 3, rect.top + 1), (rect.right - 3, rect.top + 1), 2)

        for fx in range(rect.left + 22, rect.right - 15, 42):
            h_f = min(rect.height - 8, 28)
            if h_f > 8:
                pygame.draw.line(superficie, col_crevice, (fx, rect.top + 6), (fx + 5, rect.top + h_f), 2)
                pygame.draw.line(superficie, col_luz, (fx + 6, rect.top + 7), (fx + 7, rect.top + h_f), 1)

        if isinstance(r_item, dict) and r_item.get("coral"):
            cx, cy = rect.centerx, rect.top - 6
            color_c = r_item.get("color_coral", (245, 115, 140))
            pygame.draw.circle(superficie, color_c, (cx, cy), 6)
            pygame.draw.circle(superficie, (255, 235, 180), (cx, cy), 3)


def dibujar_barreras_algas_escenario(superficie, barreras_algas, tick=0):
    """
    Dibuja las algas que funcionan como barreras sólidas que bloquean el camino
    y obligan a buscar rutas alternativas.
    Diseño: gruesos tallos entrelazados de quelpo verde oscuro, hojas densas y esporas brillantes.
    """
    col_tallo_osc = (18, 76, 42)
    col_tallo_claro = (28, 115, 65)
    col_hoja = (40, 160, 90)
    col_hoja_borde = (16, 68, 36)

    for b in barreras_algas:
        rect = b["rect"] if isinstance(b, dict) else b
        s_barrera = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s_barrera.fill((16, 70, 38, 220))
        superficie.blit(s_barrera, (rect.x, rect.y))

        num_tallos = max(2, rect.width // 14)
        espacio = rect.width / float(num_tallos)
        for i in range(num_tallos):
            x_tallo = rect.left + int(i * espacio + espacio * 0.5)
            puntos = []
            pasos = max(4, rect.height // 25)
            for j in range(pasos + 1):
                y_j = rect.top + int(j * (rect.height / pasos))
                ondulacion = math.sin(tick * 0.04 + i + j * 0.6) * 3.5
                puntos.append((x_tallo + ondulacion, y_j))
            if len(puntos) >= 2:
                pygame.draw.lines(superficie, col_tallo_osc, False, puntos, 5)
                pygame.draw.lines(superficie, col_tallo_claro, False, puntos, 3)

            for j in range(1, pasos):
                y_nodo = rect.top + int(j * (rect.height / pasos))
                lado = 1 if (i + j) % 2 == 0 else -1
                h_x = x_tallo + lado * 10
                pygame.draw.ellipse(superficie, col_hoja, (min(x_tallo, h_x), y_nodo - 4, 12, 8))
                pygame.draw.ellipse(superficie, col_hoja_borde, (min(x_tallo, h_x), y_nodo - 4, 12, 8), 1)

        pygame.draw.rect(superficie, col_tallo_osc, rect, width=2, border_radius=4)

        for sy in range(rect.top + 16, rect.bottom - 12, 34):
            glow_x = rect.centerx + int(math.sin(tick * 0.05 + sy) * 4)
            pulso = 0.5 + 0.5 * math.sin(tick * 0.08 + sy * 0.2)
            tam_e = 3 if pulso > 0.6 else 2
            pygame.draw.circle(superficie, (110, 245, 165), (glow_x, sy), tam_e + 2)
            pygame.draw.circle(superficie, (255, 255, 255), (glow_x, sy), tam_e)


def dibujar_algas_decorativas_escenario(superficie, algas_decorativas, tick=0, capa="frente"):
    """
    Dibuja algas marinas decorativas ondeando suavemente con las corrientes marinas.
    Permiten el paso libre de los personajes sin colisión física.
    """
    for a in algas_decorativas:
        if a.get("capa", "frente") != capa:
            continue
        xb = a["x"]
        yb = a["y"]
        alto = a["alto"]
        amp = a.get("amplitud", 14.0)
        seed = a.get("fase", 0.0)
        col_tallo = a.get("color_tallo", (34, 155, 80))
        col_hoja = a.get("color_hoja", (48, 195, 105))

        pasos = 6
        puntos = []
        for i in range(pasos + 1):
            t = i / float(pasos)
            curva = (t ** 1.4)
            dx = math.sin((tick * 0.035) + seed + i * 0.45) * (amp * curva)
            y_i = yb - int(t * alto)
            x_i = xb + int(dx)
            puntos.append((x_i, y_i))

        if len(puntos) >= 2:
            pygame.draw.lines(superficie, (20, 95, 50), False, puntos, 4)
            pygame.draw.lines(superficie, col_tallo, False, puntos, 2)

        for i in range(1, pasos):
            px, py = puntos[i]
            lado = 1 if i % 2 == 0 else -1
            w_h, h_h = 14, 7
            rect_h = pygame.Rect(px - (w_h if lado < 0 else 0), py - h_h // 2, w_h, h_h)
            pygame.draw.ellipse(superficie, col_hoja, rect_h)
            pygame.draw.ellipse(superficie, (20, 95, 50), rect_h, 1)


def dibujar_peligros_marinos_escenario(superficie, pinchos):
    """
    Dibuja los obstáculos mortales submarinos (erizos de mar puntiagudos y corales de fuego).
    Si un personaje los toca, ambos mueren y el nivel se reinicia.
    Soporta orientación hacia arriba, abajo, izquierda y derecha con erizos alineados.
    """
    for p in pinchos:
        dir_p = getattr(p, "direccion", "arriba")
        if dir_p in ("arriba", "abajo"):
            paso_erizo = 42
            num_erizos = max(1, p.width // paso_erizo)
            w_seg = p.width / float(num_erizos)
            for e_idx in range(num_erizos):
                cx = int(p.left + (e_idx + 0.5) * w_seg)
                cy = p.centery
                r_cuerpo = min(int(w_seg * 0.4), p.height // 2)
                num_puas = 7
                for i in range(num_puas):
                    if dir_p == "arriba":
                        ang = math.pi + (i / float(num_puas - 1)) * math.pi
                    else:
                        ang = (i / float(num_puas - 1)) * math.pi
                    px = cx + math.cos(ang) * (w_seg * 0.55)
                    py = cy + math.sin(ang) * (p.height * 0.75)
                    pygame.draw.line(superficie, (180, 30, 60), (cx, cy), (int(px), int(py)), 3)
                    pygame.draw.line(superficie, (255, 220, 230), (int(px - math.cos(ang) * 4), int(py - math.sin(ang) * 4)), (int(px), int(py)), 2)

                pygame.draw.circle(superficie, (45, 18, 50), (cx, cy), r_cuerpo)
                pygame.draw.circle(superficie, (190, 45, 75), (cx, cy), r_cuerpo, width=2)
                pygame.draw.circle(superficie, (255, 70, 95), (cx, cy), max(2, r_cuerpo // 2))
        elif dir_p in ("izquierda", "derecha"):
            paso_erizo = 42
            num_erizos = max(1, p.height // paso_erizo)
            h_seg = p.height / float(num_erizos)
            for e_idx in range(num_erizos):
                cx = p.centerx
                cy = int(p.top + (e_idx + 0.5) * h_seg)
                r_cuerpo = min(int(h_seg * 0.4), p.width // 2)
                num_puas = 7
                for i in range(num_puas):
                    if dir_p == "izquierda":
                        ang = 0.5 * math.pi + (i / float(num_puas - 1)) * math.pi
                    else:
                        ang = -0.5 * math.pi + (i / float(num_puas - 1)) * math.pi
                    px = cx + math.cos(ang) * (p.width * 0.75)
                    py = cy + math.sin(ang) * (h_seg * 0.55)
                    pygame.draw.line(superficie, (180, 30, 60), (cx, cy), (int(px), int(py)), 3)
                    pygame.draw.line(superficie, (255, 220, 230), (int(px - math.cos(ang) * 4), int(py - math.sin(ang) * 4)), (int(px), int(py)), 2)

                pygame.draw.circle(superficie, (45, 18, 50), (cx, cy), r_cuerpo)
                pygame.draw.circle(superficie, (190, 45, 75), (cx, cy), r_cuerpo, width=2)
                pygame.draw.circle(superficie, (255, 70, 95), (cx, cy), max(2, r_cuerpo // 2))
        else:
            pygame.draw.rect(superficie, (180, 30, 60), p, border_radius=3)
            pygame.draw.rect(superficie, (255, 210, 220), p, width=2, border_radius=3)


def crear_sistema_burbujas_m3(ancho_mundo, cantidad=40):
    """Inicializa la lista de partículas de burbujas flotantes."""
    burbujas = []
    for _ in range(cantidad):
        burbujas.append({
            "x": random.uniform(0, ancho_mundo),
            "y": random.uniform(40, ALTO - 80),
            "vy": random.uniform(0.9, 2.2),
            "radio": random.randint(3, 7),
            "fase": random.uniform(0, 6.28),
        })
    return burbujas


def actualizar_y_dibujar_burbujas_m3(superficie, burbujas, jugadores, tick=0):
    """
    Actualiza el movimiento ascendente de burbujas y las dibuja con reflejos cristalinos.
    También emite burbujas de nado al desplazarse los personajes.
    """
    ancho_mundo = superficie.get_width()
    for b in burbujas:
        b["y"] -= b["vy"]
        b["x"] += math.sin(tick * 0.05 + b["fase"]) * 0.65
        if b["y"] <= 25:
            b["y"] = random.uniform(ALTO - 110, ALTO - 80)
            b["x"] = random.uniform(20, ancho_mundo - 20)
            b["vy"] = random.uniform(0.9, 2.2)

        bx, by, br = int(b["x"]), int(b["y"]), b["radio"]
        if br not in _CACHE_BURBUJAS_M3:
            s_burb = pygame.Surface((br * 2 + 2, br * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s_burb, (180, 235, 255, 140), (br + 1, br + 1), br)
            pygame.draw.circle(s_burb, (255, 255, 255, 210), (br + 1, br + 1), br, width=1)
            pygame.draw.circle(s_burb, (255, 255, 255, 240), (br - 1, br - 1), max(1, br // 3))
            _CACHE_BURBUJAS_M3[br] = s_burb
        superficie.blit(_CACHE_BURBUJAS_M3[br], (bx - br - 1, by - br - 1))

    for p in jugadores:
        if not p.get("muerto", False) and p.get("moviendo", False) and random.random() < 0.25:
            burbujas.append({
                "x": float(p["hitbox"].centerx + random.uniform(-10, 10)),
                "y": float(p["hitbox"].bottom - 8),
                "vy": random.uniform(1.2, 2.5),
                "radio": random.randint(2, 4),
                "fase": random.uniform(0, 6.28),
            })
            if len(burbujas) > 65:
                burbujas.pop(0)


def dibujar_corales_escenario(superficie, corales_info, tick=0):
    """
    Dibuja corales marinos vivos de alta fidelidad estética inspirados en arrecifes de coral:
    - Ramificados (staghorn / asta de ciervo) con puntas luminiscentes que ondean con la marea.
    - Cerebro (dome / estriado) con circunvoluciones y texturas rugosas.
    - Abanico de mar (sea fans) con mallas translúcidas y filamentos radiantes.
    - Tubulares (esponjas / chimeneas) con orificios superiores sombreados.
    - Anémonas bioluminiscentes con tentáculos ondulantes.
    """
    if not corales_info:
        return

    for c in corales_info:
        tipo = c.get("tipo", "ramificado")
        cx = int(c["x"])
        cy = int(c["y"])
        escala = float(c.get("escala", 1.0))
        fase = float(c.get("fase", 0.0))
        col_base = c.get("color", (245, 105, 140))
        col_sec = c.get("color_sec", (255, 190, 210))
        anclaje = c.get("anclaje", "abajo")

        dir_y = -1 if anclaje == "abajo" else (1 if anclaje == "arriba" else 0)
        dir_x = 1 if anclaje == "izq" else (-1 if anclaje == "der" else 0)

        ondulacion = math.sin(tick * 0.04 + fase)

        if tipo == "ramificado":
            h_tronco = int(24 * escala)
            w_tronco = max(3, int(6 * escala))
            top_x = cx + int(ondulacion * 2.5)
            top_y = cy + dir_y * h_tronco if dir_y != 0 else cy
            if dir_x != 0:
                top_x = cx + dir_x * h_tronco
                top_y = cy + int(ondulacion * 2.5)

            pygame.draw.line(superficie, col_base, (cx, cy), (top_x, top_y), w_tronco)

            ramas = [
                (-16 * escala, dir_y * 18 * escala, -0.6),
                (16 * escala, dir_y * 20 * escala, 0.6),
                (-8 * escala, dir_y * 26 * escala, -0.2),
                (10 * escala, dir_y * 28 * escala, 0.3),
            ]
            for rx, ry, r_factor in ramas:
                sway = math.sin(tick * 0.045 + fase + r_factor) * 3.5 * escala
                punta_x = top_x + int(rx + sway)
                punta_y = top_y + int(ry)
                w_rama = max(2, int(4 * escala))
                pygame.draw.line(superficie, col_base, (top_x, top_y), (punta_x, punta_y), w_rama)
                r_punta = max(2, int(3.5 * escala))
                pygame.draw.circle(superficie, col_sec, (punta_x, punta_y), r_punta)
                pygame.draw.circle(superficie, (255, 255, 255), (punta_x - 1, punta_y - 1), max(1, r_punta // 2))

        elif tipo == "cerebro":
            r_ancho = int(18 * escala)
            r_alto = int(13 * escala)
            rect_base = pygame.Rect(cx - r_ancho, cy + (dir_y * r_alto if dir_y < 0 else -r_alto // 2), r_ancho * 2, r_alto * 2)
            pygame.draw.ellipse(superficie, col_base, rect_base)
            pygame.draw.ellipse(superficie, (max(0, col_base[0] - 50), max(0, col_base[1] - 50), max(0, col_base[2] - 50)), rect_base, 2)
            for i in range(1, 4):
                factor = 1.0 - (i * 0.25)
                w_e = int(r_ancho * 2 * factor)
                h_e = int(r_alto * 2 * factor)
                x_e = rect_base.centerx - w_e // 2
                y_e = rect_base.centery - h_e // 2
                pygame.draw.arc(superficie, col_sec, (x_e, y_e, w_e, h_e), 0.2, math.pi - 0.2, max(1, int(2 * escala)))

        elif tipo == "abanico":
            h_fan = int(32 * escala)
            w_fan = int(30 * escala)
            stem_y = cy + dir_y * (h_fan // 3) if dir_y != 0 else cy
            stem_x = cx + dir_x * (h_fan // 3) if dir_x != 0 else cx
            pygame.draw.line(superficie, (max(0, col_base[0] - 40), max(0, col_base[1] - 40), max(0, col_base[2] - 40)), (cx, cy), (stem_x, stem_y), max(2, int(4 * escala)))

            num_costillas = 7
            puntos_borde = []
            for i in range(num_costillas):
                t = i / float(num_costillas - 1)
                ang = (-math.pi * 0.85) + t * (math.pi * 0.7) if dir_y <= 0 else (math.pi * 0.15 + t * (math.pi * 0.7))
                sway = math.sin(tick * 0.035 + fase + i * 0.3) * (4.0 * escala)
                px = stem_x + math.cos(ang) * (w_fan * 0.9) + sway
                py = stem_y + math.sin(ang) * (h_fan * 0.9)
                puntos_borde.append((int(px), int(py)))
                pygame.draw.line(superficie, col_base, (stem_x, stem_y), (int(px), int(py)), max(1, int(2 * escala)))

            if len(puntos_borde) >= 2:
                pygame.draw.lines(superficie, col_sec, False, puntos_borde, max(2, int(3 * escala)))
                for bx, by in puntos_borde:
                    pygame.draw.circle(superficie, (255, 240, 210), (bx, by), max(1, int(2 * escala)))

        elif tipo == "tubular":
            num_tubos = 3
            anchos = [int(10 * escala), int(8 * escala), int(9 * escala)]
            altos = [int(28 * escala), int(22 * escala), int(25 * escala)]
            offsets_x = [-int(9 * escala), int(1 * escala), int(10 * escala)]

            for i in range(num_tubos):
                tx = cx + offsets_x[i]
                th = altos[i]
                tw = anchos[i]
                ty = cy - th if dir_y <= 0 else cy
                rect_tubo = pygame.Rect(tx - tw // 2, ty, tw, th)
                pygame.draw.rect(superficie, col_base, rect_tubo, border_radius=max(2, int(3 * escala)))
                pygame.draw.rect(superficie, (max(0, col_base[0] - 40), max(0, col_base[1] - 40), max(0, col_base[2] - 40)), rect_tubo, 1, border_radius=max(2, int(3 * escala)))
                boca_y = rect_tubo.top if dir_y <= 0 else rect_tubo.bottom - int(5 * escala)
                rect_boca = pygame.Rect(rect_tubo.left, boca_y, tw, int(6 * escala))
                pygame.draw.ellipse(superficie, (max(0, col_base[0] - 60), max(0, col_base[1] - 60), max(0, col_base[2] - 60)), rect_boca)
                pygame.draw.ellipse(superficie, col_sec, rect_boca, 1)

        elif tipo == "anemona":
            r_cuerpo = int(8 * escala)
            pygame.draw.circle(superficie, col_base, (cx, cy), r_cuerpo)
            num_tentaculos = 8
            for i in range(num_tentaculos):
                ang = -math.pi + (i / float(num_tentaculos - 1)) * math.pi if dir_y <= 0 else (i / float(num_tentaculos - 1)) * math.pi
                largo = (14 + (i % 3) * 4) * escala
                sway = math.sin(tick * 0.05 + fase + i * 0.7) * (3.5 * escala)
                tip_x = cx + int(math.cos(ang) * largo + sway)
                tip_y = cy + int(math.sin(ang) * largo)
                pygame.draw.line(superficie, col_base, (cx, cy), (tip_x, tip_y), max(1, int(2.5 * escala)))
                pygame.draw.circle(superficie, col_sec, (tip_x, tip_y), max(2, int(3 * escala)))
                pygame.draw.circle(superficie, (255, 255, 255), (tip_x, tip_y), 1)


def generar_laberinto_coral_m3_n2(ancho_mundo, alto_mundo, y_suelo, y_techo, rng_seed=None):
    """
    Genera proceduralmente el laberinto de coral para Mundo 3 Nivel 2:
    - Laberinto submarino navegable en 4 direcciones (natación libre sin gravedad terrestre).
    - Formado por rocas marinas milenarias, arrecifes de coral y barreras de quelpo sólido.
    - Garantiza 100% resolubilidad matemática (árbol de expansión DFS con atajos selectivos).
    - Asegura la existencia de múltiples callejones sin salida genuinos para exploración y desorientación.
    - Ubica la llave oculta en el fondo de un callejón sin salida distante.
    - Puerta de salida ubicada en una terraza marina en la cámara final.
    - Distribución procedural aleatoria única en cada nueva partida o reinicio del nivel.
    """
    rng = random.Random(rng_seed)

    x_offset = 220
    x_final = 2380
    w_total_lab = x_final - x_offset  # 2160
    NUM_COLS = 9
    w_cell = w_total_lab // NUM_COLS  # 240

    h_total_lab = y_suelo - y_techo   # 620
    NUM_FILAS = 4
    h_cell = h_total_lab // NUM_FILAS # 155
    grosor_muro = 24

    # Generar árbol de expansión garantizando callejones sin salida
    while True:
        row_inicio = rng.choice([1, 2])
        row_salida = rng.choice([1, 2])

        v_walls = {(c, r): True for c in range(NUM_COLS - 1) for r in range(NUM_FILAS)}
        h_walls = {(c, r): True for c in range(NUM_COLS) for r in range(NUM_FILAS - 1)}

        visited = set([(0, row_inicio)])
        stack = [(0, row_inicio)]

        while stack:
            curr_c, curr_r = stack[-1]
            unvisited_neighbors = []

            if curr_r > 0 and (curr_c, curr_r - 1) not in visited:
                unvisited_neighbors.append((curr_c, curr_r - 1, 'h', (curr_c, curr_r - 1)))
            if curr_r < NUM_FILAS - 1 and (curr_c, curr_r + 1) not in visited:
                unvisited_neighbors.append((curr_c, curr_r + 1, 'h', (curr_c, curr_r)))
            if curr_c > 0 and (curr_c - 1, curr_r) not in visited:
                unvisited_neighbors.append((curr_c - 1, curr_r, 'v', (curr_c - 1, curr_r)))
            if curr_c < NUM_COLS - 1 and (curr_c + 1, curr_r) not in visited:
                unvisited_neighbors.append((curr_c + 1, curr_r, 'v', (curr_c, curr_r)))

            if unvisited_neighbors:
                next_c, next_r, w_type, w_pos = rng.choice(unvisited_neighbors)
                if w_type == 'h':
                    h_walls[w_pos] = False
                else:
                    v_walls[w_pos] = False
                visited.add((next_c, next_r))
                stack.append((next_c, next_r))
            else:
                stack.pop()

        adj = {(c, r): [] for c in range(NUM_COLS) for r in range(NUM_FILAS)}
        for c in range(NUM_COLS):
            for r in range(NUM_FILAS):
                if r > 0 and not h_walls[(c, r - 1)]:
                    adj[(c, r)].append((c, r - 1))
                if r < NUM_FILAS - 1 and not h_walls[(c, r)]:
                    adj[(c, r)].append((c, r + 1))
                if c > 0 and not v_walls[(c - 1, r)]:
                    adj[(c, r)].append((c - 1, r))
                if c < NUM_COLS - 1 and not v_walls[(c, r)]:
                    adj[(c, r)].append((c + 1, r))

        start_node = (0, row_inicio)
        exit_node = (NUM_COLS - 1, row_salida)
        dead_ends = [cell for cell in adj if len(adj[cell]) == 1 and cell != start_node and cell != exit_node]
        if len(dead_ends) >= 5:
            break

    # Remover selectivamente algunos muros interiores SOLO entre celdas con grado >= 2
    candidatos_remover = []
    for (c, r), v in v_walls.items():
        if v and len(adj[(c, r)]) >= 2 and len(adj[(c + 1, r)]) >= 2:
            candidatos_remover.append(('v', (c, r)))
    for (c, r), v in h_walls.items():
        if v and len(adj[(c, r)]) >= 2 and len(adj[(c, r + 1)]) >= 2:
            candidatos_remover.append(('h', (c, r)))

    num_remover = min(len(candidatos_remover), 3)
    if candidatos_remover and num_remover > 0:
        for w_type, k in rng.sample(candidatos_remover, num_remover):
            if w_type == 'v':
                v_walls[k] = False
                adj[(k[0], k[1])].append((k[0] + 1, k[1]))
                adj[(k[0] + 1, k[1])].append((k[0], k[1]))
            else:
                h_walls[k] = False
                adj[(k[0], k[1])].append((k[0], k[1] + 1))
                adj[(k[0], k[1] + 1)].append((k[0], k[1]))

    # Distancias BFS desde el inicio
    dist = {start_node: 0}
    q = [start_node]
    while q:
        curr = q.pop(0)
        for nxt in adj[curr]:
            if nxt not in dist:
                dist[nxt] = dist[curr] + 1
                q.append(nxt)

    dead_ends = [cell for cell in adj if len(adj[cell]) == 1 and cell != start_node and cell != exit_node]
    candidatos_llave = [c for c in dead_ends if dist[c] >= 4 and c[0] != NUM_COLS - 1]
    if not candidatos_llave:
        candidatos_llave = [c for c in dead_ends if c != exit_node]
    if not candidatos_llave:
        candidatos_llave = [max(adj.keys(), key=lambda x: dist[x] if x != exit_node else -1)]

    key_cell = rng.choice(candidatos_llave)

    rocas = []
    barreras = []
    corales = []
    algas = []

    # Muros de contorno izquierdo (entrada)
    x_muro_izq = x_offset - grosor_muro // 2
    for r in range(NUM_FILAS):
        if r != row_inicio:
            rocas.append({"rect": pygame.Rect(x_muro_izq, y_techo + r * h_cell, grosor_muro, h_cell)})

    # Muros de contorno derecho (salida)
    x_muro_der = x_final - grosor_muro // 2
    for r in range(NUM_FILAS):
        if r != row_salida:
            rocas.append({"rect": pygame.Rect(x_muro_der, y_techo + r * h_cell, grosor_muro, h_cell)})

    colores_coral = [
        ((250, 95, 135), (255, 185, 205)),   # Magenta / rosa arrecife
        ((255, 135, 70), (255, 205, 140)),   # Coral anaranjado
        ((255, 195, 50), (255, 240, 160)),   # Dorado ámbar
        ((45, 200, 180), (130, 245, 230)),   # Turquesa marino
        ((175, 95, 220), (225, 170, 255)),   # Violeta profundo
    ]

    # Muros verticales interiores
    for (c, r), v in v_walls.items():
        if v:
            xw = x_offset + (c + 1) * w_cell - grosor_muro // 2
            yw = y_techo + r * h_cell
            rect = pygame.Rect(xw, yw, grosor_muro, h_cell)
            if (c * 3 + r) % 5 == 1:
                barreras.append({"rect": rect})
            elif (c + r) % 6 == 4:
                col_c, col_s = rng.choice(colores_coral)
                rocas.append({"rect": rect, "coral": True, "color_coral": col_c})
            else:
                rocas.append({"rect": rect})

    # Muros horizontales interiores
    for (c, r), v in h_walls.items():
        if v:
            xw = x_offset + c * w_cell
            yw = y_techo + (r + 1) * h_cell - grosor_muro // 2
            rect = pygame.Rect(xw, yw, w_cell, grosor_muro)
            if (c + r * 2) % 5 == 2:
                barreras.append({"rect": rect})
            elif (c * 2 + r) % 7 == 3:
                col_c, col_s = rng.choice(colores_coral)
                rocas.append({"rect": rect, "coral": True, "color_coral": col_c})
            else:
                rocas.append({"rect": rect})

            if rng.random() < 0.45:
                pos_x = xw + rng.randint(30, w_cell - 30)
                algas.append({
                    "x": pos_x, "y": yw, "alto": rng.randint(45, 75),
                    "amplitud": rng.uniform(10, 15), "fase": rng.uniform(0, 6.28),
                    "capa": rng.choice(["fondo", "frente"])
                })
            elif rng.random() < 0.40:
                pos_x = xw + rng.randint(25, w_cell - 25)
                tipo_c = rng.choice(["ramificado", "cerebro", "abanico", "tubular"])
                col_c, col_s = rng.choice(colores_coral)
                corales.append({
                    "tipo": tipo_c, "x": pos_x, "y": yw,
                    "escala": rng.uniform(0.75, 1.05), "fase": rng.uniform(0, 6.28),
                    "color": col_c, "color_sec": col_s, "anclaje": "abajo"
                })

    # Postes de esquina y cruces
    for c in range(1, NUM_COLS):
        for r in range(1, NUM_FILAS):
            tiene_muro = (
                v_walls.get((c - 1, r - 1), False) or v_walls.get((c - 1, r), False) or
                h_walls.get((c - 1, r - 1), False) or h_walls.get((c, r - 1), False)
            )
            if tiene_muro:
                rocas.append({"rect": pygame.Rect(x_offset + c * w_cell - grosor_muro // 2, y_techo + r * h_cell - grosor_muro // 2, grosor_muro, grosor_muro)})

    p_center_y = y_techo + row_inicio * h_cell + (h_cell - 65) // 2
    p1_x = 75
    p1_y = p_center_y
    p2_x = 145
    p2_y = p_center_y

    puerta_x = 2460
    puerta_y = y_suelo - 90
    pedestal_puerta = pygame.Rect(2405, y_suelo - 15, 170, 15)
    rocas.append({"rect": pedestal_puerta, "coral": True, "color_coral": (255, 135, 70)})

    corales.append({"tipo": "ramificado", "x": 2430, "y": y_suelo, "escala": 1.25, "fase": 0.5, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"})
    corales.append({"tipo": "abanico", "x": 2540, "y": y_suelo, "escala": 1.2, "fase": 2.1, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"})
    corales.append({"tipo": "tubular", "x": 2405, "y": y_suelo, "escala": 1.1, "fase": 1.2, "color": (45, 200, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"})
    corales.append({"tipo": "cerebro", "x": 2565, "y": y_suelo, "escala": 1.15, "fase": 3.4, "color": (255, 135, 70), "color_sec": (255, 205, 140), "anclaje": "abajo"})

    llave_x = x_offset + key_cell[0] * w_cell + (w_cell - 25) // 2
    llave_y = y_techo + key_cell[1] * h_cell + (h_cell - 46) // 2

    corales.append({"tipo": "anemona", "x": llave_x + 12, "y": llave_y + 46, "escala": 1.2, "fase": 1.0, "color": (255, 210, 60), "color_sec": (255, 255, 180), "anclaje": "abajo"})
    corales.append({"tipo": "ramificado", "x": llave_x - 38, "y": llave_y + 46, "escala": 0.95, "fase": 2.5, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"})
    corales.append({"tipo": "tubular", "x": llave_x + 55, "y": llave_y + 46, "escala": 0.9, "fase": 0.8, "color": (45, 200, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"})

    for dead_c, dead_r in dead_ends:
        if (dead_c, dead_r) == key_cell:
            continue
        cx = x_offset + dead_c * w_cell + w_cell // 2
        cy = y_techo + dead_r * h_cell + h_cell - 4
        tipo_c = rng.choice(["ramificado", "cerebro", "abanico", "tubular", "anemona"])
        col_c, col_s = rng.choice(colores_coral)
        corales.append({
            "tipo": tipo_c, "x": cx + rng.randint(-30, 30), "y": cy,
            "escala": rng.uniform(0.85, 1.15), "fase": rng.uniform(0, 6.28),
            "color": col_c, "color_sec": col_s, "anclaje": "abajo"
        })

    for px in range(40, ancho_mundo - 50, 95):
        if rng.random() < 0.65:
            algas.append({
                "x": px + rng.randint(-15, 15),
                "y": y_suelo,
                "alto": rng.randint(85, 145),
                "amplitud": rng.uniform(14, 20),
                "fase": rng.uniform(0, 6.28),
                "capa": rng.choice(["fondo", "frente"])
            })

    return {
        "rocas": rocas,
        "barreras": barreras,
        "corales": corales,
        "algas": algas,
        "p1_x": p1_x, "p1_y": p1_y,
        "p2_x": p2_x, "p2_y": p2_y,
        "llave_x": llave_x, "llave_y": llave_y,
        "puerta_x": puerta_x, "puerta_y": puerta_y,
        "key_cell": key_cell,
        "exit_cell": exit_node,
        "distancia_llave": dist[key_cell],
        "distancia_salida": dist[exit_node],
        "num_callejones": len(dead_ends),
    }


_SURF_LUZ_LINTERNA = None
_SURF_LUZ_TENUE = None


def obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45):
    """
    Crea o retorna en caché las superficies circulares de luz para las linternas de Mundo 3 Niveles 4 y 5:
    - Haz principal de la linterna: radio 165px con núcleo transparente y gradiente suave.
    - Resplandor personal tenue: radio 45px (cuando la linterna está apagada).
    """
    global _SURF_LUZ_LINTERNA, _SURF_LUZ_TENUE
    if _SURF_LUZ_LINTERNA is not None and _SURF_LUZ_TENUE is not None:
        return _SURF_LUZ_LINTERNA, _SURF_LUZ_TENUE

    diam_linterna = radio_linterna * 2
    s_linterna = pygame.Surface((diam_linterna, diam_linterna), pygame.SRCALPHA)
    for r in range(radio_linterna, 0, -2):
        frac = r / float(radio_linterna)
        if frac <= 0.45:
            alpha = 255
        else:
            t = (frac - 0.45) / 0.55
            alpha = int(255 * (1.0 - t * t))
        pygame.draw.circle(s_linterna, (alpha, alpha, alpha, alpha), (radio_linterna, radio_linterna), r)
    _SURF_LUZ_LINTERNA = s_linterna

    diam_tenue = radio_tenue * 2
    s_tenue = pygame.Surface((diam_tenue, diam_tenue), pygame.SRCALPHA)
    for r in range(radio_tenue, 0, -2):
        frac = r / float(radio_tenue)
        if frac <= 0.35:
            alpha = 255
        else:
            t = (frac - 0.35) / 0.65
            alpha = int(255 * (1.0 - t * t))
        pygame.draw.circle(s_tenue, (alpha, alpha, alpha, alpha), (radio_tenue, radio_tenue), r)
    _SURF_LUZ_TENUE = s_tenue

    return _SURF_LUZ_LINTERNA, _SURF_LUZ_TENUE


def dibujar_linterna_minero(superficie, jugador, encendida):
    """Dibuja una linterna de buceo submarino montada en la cabeza del personaje."""
    if jugador.get("muerto", False) and jugador.get("muerte_terminada", False):
        return
    hx = jugador["hitbox"].centerx
    hy = jugador["hitbox"].top + 10
    dir_mirar = 1 if jugador.get("mirando_derecha", True) else -1
    lamp_x = hx + dir_mirar * 12
    lamp_y = hy - 2

    # Correa elástica de sujeción sobre la frente
    pygame.draw.line(superficie, (30, 42, 54), (hx - 15, lamp_y), (hx + 15, lamp_y), 3)

    # Carcasa y lente de la linterna
    pygame.draw.circle(superficie, (35, 45, 55), (lamp_x, lamp_y), 6)
    if encendida and not jugador.get("muerto", False):
        pygame.draw.circle(superficie, (255, 240, 140), (lamp_x, lamp_y), 4)
        pygame.draw.circle(superficie, (255, 255, 255), (lamp_x, lamp_y), 2)
        foco_x = lamp_x + dir_mirar * 5
        pygame.draw.circle(superficie, (255, 250, 180), (foco_x, lamp_y), 3)
    else:
        pygame.draw.circle(superficie, (75, 80, 90), (lamp_x, lamp_y), 4)


def calcular_vistas_camara(jugador1, jugador2, p1_completado, p2_completado, numero_mundo, puerta, ancho_mundo):
    """
    Decide qué tramos del mundo se muestran este frame. Devuelve una lista de
    (x_destino_en_pantalla, cam_x, ancho): una vista normal o dos en pantalla dividida.
    La usan tanto el dibujo (para no pintar lo que no se ve) como el blit final a pantalla.
    """
    if p1_completado and not p2_completado:
        # Jugador 1 ya pasó por la puerta: cámara completa siguiendo al Jugador 2
        return [(0, max(0, min(jugador2["hitbox"].centerx - ANCHO // 2, ancho_mundo - ANCHO)), ANCHO)]
    if p2_completado and not p1_completado:
        # Jugador 2 ya pasó por la puerta: cámara completa siguiendo al Jugador 1
        return [(0, max(0, min(jugador1["hitbox"].centerx - ANCHO // 2, ancho_mundo - ANCHO)), ANCHO)]
    if (p1_completado and p2_completado) or (numero_mundo == 3 and ((jugador1["muerto"] and p2_completado) or (jugador2["muerto"] and p1_completado))):
        # Nivel completado: cámara fija centrada en la puerta de salida
        return [(0, max(0, min(puerta["rect"].centerx - ANCHO // 2, ancho_mundo - ANCHO)), ANCHO)]
    # Ambos personajes están en juego
    distancia = abs(jugador1["hitbox"].centerx - jugador2["hitbox"].centerx)
    if distancia <= DISTANCIA_SPLIT:
        centro = (jugador1["hitbox"].centerx + jugador2["hitbox"].centerx) // 2
        return [(0, max(0, min(centro - ANCHO // 2, ancho_mundo - ANCHO)), ANCHO)]
    ancho_m = ANCHO // 2
    if jugador1["hitbox"].centerx <= jugador2["hitbox"].centerx:
        p_izq, p_der = jugador1, jugador2
    else:
        p_izq, p_der = jugador2, jugador1
    cam_izq_x = max(0, min(p_izq["hitbox"].centerx - ancho_m // 2, ancho_mundo - ancho_m))
    cam_der_x = max(0, min(p_der["hitbox"].centerx - ancho_m // 2, ancho_mundo - ancho_m))
    return [(0, cam_izq_x, ancho_m), (ancho_m, cam_der_x, ancho_m)]


def rangos_visibles_de_vistas(vistas):
    """Convierte las vistas de cámara en tramos [x0, x1) del mundo, fusionando los que se solapan."""
    tramos = sorted((cam_x, cam_x + ancho) for _, cam_x, ancho in vistas)
    res = []
    for x0, x1 in tramos:
        if res and x0 <= res[-1][1]:
            res[-1] = (res[-1][0], max(res[-1][1], x1))
        else:
            res.append((x0, x1))
    return res


def aplicar_oscuridad_submarina(superficie, jugadores_info, surf_oscuridad, surf_luz, surf_tenue, rangos=None):
    """
    Aplica la capa de oscuridad total sobre el mundo y substrae los haces de luz circulares
    de las linternas activas de cada personaje:
    - jugadores_info: lista de tuplas (jugador, linterna_activa, completado)
    - Ilumina un área circular amplia (~165px) alrededor de cada personaje cuando su linterna está ON.
    - Cuando la linterna está OFF, solo deja una silueta de tenue presencia (~45px).
    - Si dos linternas iluminan zonas cercanas, sus áreas de luz se combinan de manera natural en surf_oscuridad.
    - Los elementos fuera del haz de luz (rocas, pinchos, corrientes, llave, puerta, flechas) quedan ocultos en la penumbra.
    """
    if rangos is None:
        rangos = [(0, surf_oscuridad.get_width())]
    for x0, x1 in rangos:
        surf_oscuridad.fill((3, 7, 15, 252), pygame.Rect(x0, 0, x1 - x0, surf_oscuridad.get_height()))

    w_luz, h_luz = surf_luz.get_size()
    rad_luz = w_luz // 2
    w_tenue, h_tenue = surf_tenue.get_size()
    rad_tenue = w_tenue // 2

    for jugador, linterna_on, completado in jugadores_info:
        if completado or jugador.get("muerte_terminada", False):
            continue
        cx = jugador["hitbox"].centerx
        cy = jugador["hitbox"].centery
        if linterna_on and not jugador.get("muerto", False):
            surf_oscuridad.blit(surf_luz, (cx - rad_luz, cy - rad_luz), special_flags=pygame.BLEND_RGBA_SUB)
        else:
            surf_oscuridad.blit(surf_tenue, (cx - rad_tenue, cy - rad_tenue), special_flags=pygame.BLEND_RGBA_SUB)

    for x0, x1 in rangos:
        superficie.blit(surf_oscuridad, (x0, 0), pygame.Rect(x0, 0, x1 - x0, surf_oscuridad.get_height()))


# Alias para compatibilidad con código existente
dibujar_oscuridad_laberinto = aplicar_oscuridad_submarina


def dibujar_flechas_indicadoras_escenario(superficie, flechas, tick=0):
    """
    Dibuja carteles submarinos de navegación con flechas direccionales e iconos temáticos:
    - Se dibujan sobre las paredes/fondos y quedan ocultos en la oscuridad hasta que
      la linterna de un personaje los ilumina.
    - tipo: 'llave' (dorado con llave), 'oxigeno' (cian con O2), 'salida' (esmeralda con puerta), 'ruta' (celeste)
    - direccion: 'derecha', 'izquierda', 'arriba', 'abajo'
    """
    for f in flechas:
        x = f["x"]
        y = f["y"]
        direccion = f["direccion"]
        tipo = f.get("tipo", "ruta")

        es_horiz = direccion in ("derecha", "izquierda")
        w_placa = 52 if es_horiz else 34
        h_placa = 34 if es_horiz else 52

        rx = x - w_placa // 2
        ry = y - h_placa // 2

        # Placa base de piedra marina oscura con remaches
        pygame.draw.rect(superficie, (12, 22, 34), (rx, ry, w_placa, h_placa), border_radius=6)
        pygame.draw.rect(superficie, (35, 60, 85), (rx, ry, w_placa, h_placa), width=2, border_radius=6)

        # Remaches en las esquinas
        for px, py in [(rx + 4, ry + 4), (rx + w_placa - 4, ry + 4), (rx + 4, ry + h_placa - 4), (rx + w_placa - 4, ry + h_placa - 4)]:
            pygame.draw.circle(superficie, (65, 95, 125), (px, py), 1)

        # Colores según el tipo con sutil pulso
        pulso = int(20 * math.sin(tick * 0.09 + x * 0.02))
        if tipo == "llave":
            col_main = (min(255, 245 + pulso), min(255, 195 + pulso), 40)
            col_light = (255, 250, 180)
        elif tipo == "oxigeno":
            col_main = (50, min(255, 225 + pulso), min(255, 245 + pulso))
            col_light = (205, 255, 255)
        elif tipo == "salida":
            col_main = (min(255, 80 + pulso), min(255, 235 + pulso), 130)
            col_light = (215, 255, 225)
        else: # ruta
            col_main = (60, min(255, 205 + pulso), min(255, 235 + pulso))
            col_light = (210, 250, 255)

        cx, cy = x, y

        # Polígono de flecha según la dirección
        if direccion == "derecha":
            pts = [(cx - 10, cy - 8), (cx + 2, cy - 8), (cx + 2, cy - 12), (cx + 14, cy), (cx + 2, cy + 12), (cx + 2, cy + 8), (cx - 10, cy + 8)]
            core = [(cx - 8, cy - 4), (cx + 1, cy - 4), (cx + 1, cy - 7), (cx + 9, cy), (cx + 1, cy + 7), (cx + 1, cy + 4), (cx - 8, cy + 4)]
        elif direccion == "izquierda":
            pts = [(cx + 10, cy - 8), (cx - 2, cy - 8), (cx - 2, cy - 12), (cx - 14, cy), (cx - 2, cy + 12), (cx - 2, cy + 8), (cx + 10, cy + 8)]
            core = [(cx + 8, cy - 4), (cx - 1, cy - 4), (cx - 1, cy - 7), (cx - 9, cy), (cx - 1, cy + 7), (cx - 1, cy + 4), (cx + 8, cy + 4)]
        elif direccion == "arriba":
            pts = [(cx - 8, cy + 10), (cx - 8, cy - 2), (cx - 12, cy - 2), (cx, cy - 14), (cx + 12, cy - 2), (cx + 8, cy - 2), (cx + 8, cy + 10)]
            core = [(cx - 4, cy + 8), (cx - 4, cy - 1), (cx - 7, cy - 1), (cx, cy - 9), (cx + 7, cy - 1), (cx + 4, cy - 1), (cx + 4, cy + 8)]
        else: # abajo
            pts = [(cx - 8, cy - 10), (cx - 8, cy + 2), (cx - 12, cy + 2), (cx, cy + 14), (cx + 12, cy + 2), (cx + 8, cy + 2), (cx + 8, cy - 10)]
            core = [(cx - 4, cy - 8), (cx - 4, cy + 1), (cx - 7, cy + 1), (cx, cy + 9), (cx + 7, cy + 1), (cx + 4, cy + 1), (cx + 4, cy - 8)]

        pygame.draw.polygon(superficie, col_main, pts)
        pygame.draw.polygon(superficie, col_light, core)

        # Detalle distintivo según el tipo
        if tipo == "oxigeno":
            b_x = rx + 8 if direccion == "derecha" else (rx + w_placa - 8 if direccion == "izquierda" else cx)
            b_y = ry + 8 if direccion == "abajo" else (ry + h_placa - 8 if direccion == "arriba" else cy)
            pygame.draw.circle(superficie, (180, 250, 255), (b_x, b_y), 3, 1)
        elif tipo == "llave":
            d_x = rx + 8 if direccion == "derecha" else (rx + w_placa - 8 if direccion == "izquierda" else cx)
            d_y = ry + 8 if direccion == "abajo" else (ry + h_placa - 8 if direccion == "arriba" else cy)
            pygame.draw.circle(superficie, (255, 240, 120), (d_x, d_y), 2)


def _dibujar_hud_linternas_m3_n4(pantalla_surf, linterna_p1, linterna_p2, p1_color, p2_color, y_base=22):
    """
    Dibuja un HUD estilizado y claro indicando el estado
    y los controles de las linternas independientes de cada jugador:
    - P1: [E] ON / OFF
    - P2: [L] ON / OFF
    """
    fuente_hud = obtener_fuente_pequena(13, negrita=True)

    x1, y1 = 28, y_base
    w_badge = 195 if y_base > 30 else 190
    h_badge = 30 if y_base > 30 else 32

    # Badge Jugador 1
    s_p1 = pygame.Surface((w_badge, h_badge), pygame.SRCALPHA)
    pygame.draw.rect(s_p1, (12, 22, 36, 220), (0, 0, w_badge, h_badge), border_radius=15)
    borde_p1 = (80, 210, 255) if linterna_p1 else (70, 85, 105)
    pygame.draw.rect(s_p1, borde_p1, (0, 0, w_badge, h_badge), width=2, border_radius=15)

    col_luz_p1 = (255, 240, 110) if linterna_p1 else (65, 75, 90)
    pygame.draw.circle(s_p1, col_luz_p1, (18, h_badge // 2), 6)
    if linterna_p1:
        pygame.draw.circle(s_p1, (255, 255, 220), (18, h_badge // 2), 3)

    txt_estado_p1 = "LINTERNA ON" if linterna_p1 else "LINTERNA OFF"
    col_txt_p1 = (255, 250, 190) if linterna_p1 else (140, 155, 175)
    t1_surf = fuente_hud.render(f"P1 [E]: {txt_estado_p1}", True, col_txt_p1)
    s_p1.blit(t1_surf, (32, (h_badge - t1_surf.get_height()) // 2))
    pantalla_surf.blit(s_p1, (x1, y1))

    # Badge Jugador 2
    x2 = 235 if y_base > 30 else (x1 + w_badge + 12)
    s_p2 = pygame.Surface((w_badge, h_badge), pygame.SRCALPHA)
    pygame.draw.rect(s_p2, (12, 22, 36, 220), (0, 0, w_badge, h_badge), border_radius=15)
    borde_p2 = (220, 140, 255) if linterna_p2 else (70, 85, 105)
    pygame.draw.rect(s_p2, borde_p2, (0, 0, w_badge, h_badge), width=2, border_radius=15)

    col_luz_p2 = (255, 240, 110) if linterna_p2 else (65, 75, 90)
    pygame.draw.circle(s_p2, col_luz_p2, (18, h_badge // 2), 6)
    if linterna_p2:
        pygame.draw.circle(s_p2, (255, 255, 220), (18, h_badge // 2), 3)

    txt_estado_p2 = "LINTERNA ON" if linterna_p2 else "LINTERNA OFF"
    col_txt_p2 = (255, 250, 190) if linterna_p2 else (140, 155, 175)
    t2_surf = fuente_hud.render(f"P2 [L]: {txt_estado_p2}", True, col_txt_p2)
    s_p2.blit(t2_surf, (32, (h_badge - t2_surf.get_height()) // 2))
    pantalla_surf.blit(s_p2, (x2, y1))


def generar_laberinto_oscuro_m3_n4(ancho_mundo, alto_mundo, y_suelo, y_techo, rng_seed=None):
    """
    Genera proceduralmente el laberinto oscuro para Mundo 3 Nivel 4:
    - Laberinto submarino oscuro navegable en 4 direcciones (natación libre).
    - Formado por rocas marinas ancestrales, arrecifes de coral y barreras de quelpo.
    - Garantiza 100% resolubilidad matemática (árbol de expansión DFS con atajos selectivos).
    - Incluye callejones sin salida genuinos y trampas mortales (erizos de mar) en cul-de-sacs secundarios.
    - Ubica la llave oculta en un callejón seguro distante.
    - Puerta de salida ubicada en la terraza marina final.
    - Tanto la llave como la puerta y los peligros permanecen ocultos en la oscuridad hasta ser iluminados por las linternas.
    """
    rng = random.Random(rng_seed)

    x_offset = 220
    x_final = 2380
    w_total_lab = x_final - x_offset  # 2160
    NUM_COLS = 9
    w_cell = w_total_lab // NUM_COLS  # 240

    h_total_lab = y_suelo - y_techo   # 620
    NUM_FILAS = 4
    h_cell = h_total_lab // NUM_FILAS # 155
    grosor_muro = 24

    # Generar árbol de expansión garantizando callejones sin salida
    while True:
        row_inicio = rng.choice([1, 2])
        row_salida = rng.choice([1, 2])

        v_walls = {(c, r): True for c in range(NUM_COLS - 1) for r in range(NUM_FILAS)}
        h_walls = {(c, r): True for c in range(NUM_COLS) for r in range(NUM_FILAS - 1)}

        visited = set([(0, row_inicio)])
        stack = [(0, row_inicio)]

        while stack:
            curr_c, curr_r = stack[-1]
            unvisited_neighbors = []

            if curr_r > 0 and (curr_c, curr_r - 1) not in visited:
                unvisited_neighbors.append((curr_c, curr_r - 1, 'h', (curr_c, curr_r - 1)))
            if curr_r < NUM_FILAS - 1 and (curr_c, curr_r + 1) not in visited:
                unvisited_neighbors.append((curr_c, curr_r + 1, 'h', (curr_c, curr_r)))
            if curr_c > 0 and (curr_c - 1, curr_r) not in visited:
                unvisited_neighbors.append((curr_c - 1, curr_r, 'v', (curr_c - 1, curr_r)))
            if curr_c < NUM_COLS - 1 and (curr_c + 1, curr_r) not in visited:
                unvisited_neighbors.append((curr_c + 1, curr_r, 'v', (curr_c, curr_r)))

            if unvisited_neighbors:
                next_c, next_r, w_type, w_pos = rng.choice(unvisited_neighbors)
                if w_type == 'h':
                    h_walls[w_pos] = False
                else:
                    v_walls[w_pos] = False
                visited.add((next_c, next_r))
                stack.append((next_c, next_r))
            else:
                stack.pop()

        adj = {(c, r): [] for c in range(NUM_COLS) for r in range(NUM_FILAS)}
        for c in range(NUM_COLS):
            for r in range(NUM_FILAS):
                if r > 0 and not h_walls[(c, r - 1)]:
                    adj[(c, r)].append((c, r - 1))
                if r < NUM_FILAS - 1 and not h_walls[(c, r)]:
                    adj[(c, r)].append((c, r + 1))
                if c > 0 and not v_walls[(c - 1, r)]:
                    adj[(c, r)].append((c - 1, r))
                if c < NUM_COLS - 1 and not v_walls[(c, r)]:
                    adj[(c, r)].append((c + 1, r))

        start_node = (0, row_inicio)
        exit_node = (NUM_COLS - 1, row_salida)
        dead_ends = [cell for cell in adj if len(adj[cell]) == 1 and cell != start_node and cell != exit_node]
        if len(dead_ends) >= 5:
            break

    # Remover selectivamente algunos muros interiores SOLO entre celdas con grado >= 2
    candidatos_remover = []
    for (c, r), v in v_walls.items():
        if v and len(adj[(c, r)]) >= 2 and len(adj[(c + 1, r)]) >= 2:
            candidatos_remover.append(('v', (c, r)))
    for (c, r), v in h_walls.items():
        if v and len(adj[(c, r)]) >= 2 and len(adj[(c, r + 1)]) >= 2:
            candidatos_remover.append(('h', (c, r)))

    num_remover = min(len(candidatos_remover), 3)
    if candidatos_remover and num_remover > 0:
        for w_type, k in rng.sample(candidatos_remover, num_remover):
            if w_type == 'v':
                v_walls[k] = False
                adj[(k[0], k[1])].append((k[0] + 1, k[1]))
                adj[(k[0] + 1, k[1])].append((k[0], k[1]))
            else:
                h_walls[k] = False
                adj[(k[0], k[1])].append((k[0], k[1] + 1))
                adj[(k[0], k[1] + 1)].append((k[0], k[1]))

    # Distancias BFS desde el inicio
    dist = {start_node: 0}
    q = [start_node]
    while q:
        curr = q.pop(0)
        for nxt in adj[curr]:
            if nxt not in dist:
                dist[nxt] = dist[curr] + 1
                q.append(nxt)

    dead_ends = [cell for cell in adj if len(adj[cell]) == 1 and cell != start_node and cell != exit_node]
    candidatos_llave = [c for c in dead_ends if dist[c] >= 4 and c[0] != NUM_COLS - 1]
    if not candidatos_llave:
        candidatos_llave = [c for c in dead_ends if c != exit_node]
    if not candidatos_llave:
        candidatos_llave = [max(adj.keys(), key=lambda x: dist[x] if x != exit_node else -1)]

    key_cell = rng.choice(candidatos_llave)

    # Seleccionar callejones para trampas mortales (que NO sean la llave ni la entrada)
    callejones_trampa = [c for c in dead_ends if c != key_cell and c[0] > 0]
    num_trampas = min(len(callejones_trampa), rng.randint(2, 3))
    trap_cells = rng.sample(callejones_trampa, num_trampas) if callejones_trampa else []

    rocas = []
    barreras = []
    corales = []
    algas = []
    pinchos = []

    # Muros de contorno izquierdo (entrada)
    x_muro_izq = x_offset - grosor_muro // 2
    for r in range(NUM_FILAS):
        if r != row_inicio:
            rocas.append({"rect": pygame.Rect(x_muro_izq, y_techo + r * h_cell, grosor_muro, h_cell)})

    # Muros de contorno derecho (salida)
    x_muro_der = x_final - grosor_muro // 2
    for r in range(NUM_FILAS):
        if r != row_salida:
            rocas.append({"rect": pygame.Rect(x_muro_der, y_techo + r * h_cell, grosor_muro, h_cell)})

    colores_coral = [
        ((250, 95, 135), (255, 185, 205)),
        ((255, 135, 70), (255, 205, 140)),
        ((255, 195, 50), (255, 240, 160)),
        ((45, 200, 180), (130, 245, 230)),
        ((175, 95, 220), (225, 170, 255)),
    ]

    # Muros verticales interiores
    for (c, r), v in v_walls.items():
        if v:
            xw = x_offset + (c + 1) * w_cell - grosor_muro // 2
            yw = y_techo + r * h_cell
            rect = pygame.Rect(xw, yw, grosor_muro, h_cell)
            if (c * 3 + r) % 5 == 1:
                barreras.append({"rect": rect})
            elif (c + r) % 6 == 4:
                col_c, col_s = rng.choice(colores_coral)
                rocas.append({"rect": rect, "coral": True, "color_coral": col_c})
            else:
                rocas.append({"rect": rect})

    # Muros horizontales interiores
    for (c, r), v in h_walls.items():
        if v:
            xw = x_offset + c * w_cell
            yw = y_techo + (r + 1) * h_cell - grosor_muro // 2
            rect = pygame.Rect(xw, yw, w_cell, grosor_muro)
            if (c + r * 2) % 5 == 2:
                barreras.append({"rect": rect})
            elif (c * 2 + r) % 7 == 3:
                col_c, col_s = rng.choice(colores_coral)
                rocas.append({"rect": rect, "coral": True, "color_coral": col_c})
            else:
                rocas.append({"rect": rect})

            if rng.random() < 0.40:
                pos_x = xw + rng.randint(30, w_cell - 30)
                algas.append({
                    "x": pos_x, "y": yw, "alto": rng.randint(45, 75),
                    "amplitud": rng.uniform(10, 15), "fase": rng.uniform(0, 6.28),
                    "capa": rng.choice(["fondo", "frente"])
                })
            elif rng.random() < 0.35:
                pos_x = xw + rng.randint(25, w_cell - 25)
                tipo_c = rng.choice(["ramificado", "cerebro", "abanico", "tubular"])
                col_c, col_s = rng.choice(colores_coral)
                corales.append({
                    "tipo": tipo_c, "x": pos_x, "y": yw,
                    "escala": rng.uniform(0.75, 1.05), "fase": rng.uniform(0, 6.28),
                    "color": col_c, "color_sec": col_s, "anclaje": "abajo"
                })

    # Postes de esquina y cruces
    for c in range(1, NUM_COLS):
        for r in range(1, NUM_FILAS):
            tiene_muro = (
                v_walls.get((c - 1, r - 1), False) or v_walls.get((c - 1, r), False) or
                h_walls.get((c - 1, r - 1), False) or h_walls.get((c, r - 1), False)
            )
            if tiene_muro:
                rocas.append({"rect": pygame.Rect(x_offset + c * w_cell - grosor_muro // 2, y_techo + r * h_cell - grosor_muro // 2, grosor_muro, grosor_muro)})

    p_center_y = y_techo + row_inicio * h_cell + (h_cell - 65) // 2
    p1_x = 75
    p1_y = p_center_y
    p2_x = 145
    p2_y = p_center_y

    puerta_x = 2460
    puerta_y = y_suelo - 90
    pedestal_puerta = pygame.Rect(2405, y_suelo - 15, 170, 15)
    rocas.append({"rect": pedestal_puerta, "coral": True, "color_coral": (255, 135, 70)})

    corales.append({"tipo": "ramificado", "x": 2430, "y": y_suelo, "escala": 1.25, "fase": 0.5, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"})
    corales.append({"tipo": "abanico", "x": 2540, "y": y_suelo, "escala": 1.2, "fase": 2.1, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"})
    corales.append({"tipo": "tubular", "x": 2405, "y": y_suelo, "escala": 1.1, "fase": 1.2, "color": (45, 200, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"})

    llave_x = x_offset + key_cell[0] * w_cell + (w_cell - 25) // 2
    llave_y = y_techo + key_cell[1] * h_cell + (h_cell - 46) // 2

    corales.append({"tipo": "anemona", "x": llave_x + 12, "y": llave_y + 46, "escala": 1.2, "fase": 1.0, "color": (255, 210, 60), "color_sec": (255, 255, 180), "anclaje": "abajo"})
    corales.append({"tipo": "ramificado", "x": llave_x - 38, "y": llave_y + 46, "escala": 0.95, "fase": 2.5, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"})

    # Trampas mortales en los callejones sin salida seleccionados
    for tc, tr in trap_cells:
        cell_x = x_offset + tc * w_cell
        cell_y = y_techo + tr * h_cell
        vecinos = adj[(tc, tr)]
        if vecinos:
            vc, vr = vecinos[0]
            if vc < tc:
                p_rect = crear_pincho(cell_x + w_cell - 45, cell_y + 35, 24, 85, direccion="izquierda")
            elif vc > tc:
                p_rect = crear_pincho(cell_x + 20, cell_y + 35, 24, 85, direccion="derecha")
            elif vr < tr:
                p_rect = crear_pincho(cell_x + 60, cell_y + h_cell - 28, 110, 24, direccion="arriba")
            else:
                p_rect = crear_pincho(cell_x + 60, cell_y + 4, 110, 24, direccion="abajo")
            pinchos.append(p_rect)

    for dead_c, dead_r in dead_ends:
        if (dead_c, dead_r) == key_cell or (dead_c, dead_r) in trap_cells:
            continue
        cx = x_offset + dead_c * w_cell + w_cell // 2
        cy = y_techo + dead_r * h_cell + h_cell - 4
        tipo_c = rng.choice(["ramificado", "cerebro", "abanico", "tubular", "anemona"])
        col_c, col_s = rng.choice(colores_coral)
        corales.append({
            "tipo": tipo_c, "x": cx + rng.randint(-30, 30), "y": cy,
            "escala": rng.uniform(0.85, 1.15), "fase": rng.uniform(0, 6.28),
            "color": col_c, "color_sec": col_s, "anclaje": "abajo"
        })

    for px in range(40, ancho_mundo - 50, 95):
        if rng.random() < 0.65:
            algas.append({
                "x": px + rng.randint(-15, 15),
                "y": y_suelo,
                "alto": rng.randint(85, 145),
                "amplitud": rng.uniform(14, 20),
                "fase": rng.uniform(0, 6.28),
                "capa": rng.choice(["fondo", "frente"])
            })

    # Generar flechas indicadoras dinámicas a lo largo de los caminos óptimos (Llave y Salida)
    def _encontrar_camino_bfs(origen, destino):
        if origen == destino:
            return [origen]
        cola = [[origen]]
        visitados = set([origen])
        while cola:
            camino = cola.pop(0)
            nodo = camino[-1]
            for vecino in adj.get(nodo, []):
                if vecino == destino:
                    return camino + [vecino]
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(camino + [vecino])
        return [origen, destino]

    camino_llave = _encontrar_camino_bfs(start_node, key_cell)
    camino_salida = _encontrar_camino_bfs(key_cell, exit_node)

    flechas = []
    posiciones_usadas = set()

    # 1. Flechas guiando hacia la llave
    dir_anterior = None
    for i in range(len(camino_llave) - 1):
        curr = camino_llave[i]
        nxt = camino_llave[i + 1]

        if nxt[0] > curr[0]: dir_nombre = "derecha"
        elif nxt[0] < curr[0]: dir_nombre = "izquierda"
        elif nxt[1] > curr[1]: dir_nombre = "abajo"
        else: dir_nombre = "arriba"

        es_inicio = (i == 0)
        es_giro = (dir_nombre != dir_anterior)
        es_interseccion = len(adj.get(curr, [])) >= 3

        if es_inicio or es_giro or es_interseccion or (i % 2 == 0):
            cx_min = x_offset + curr[0] * w_cell
            cx_max = x_offset + (curr[0] + 1) * w_cell
            cy_min = y_techo + curr[1] * h_cell
            cy_max = y_techo + (curr[1] + 1) * h_cell
            centro_x = cx_min + w_cell // 2
            centro_y = cy_min + h_cell // 2

            if dir_nombre == "derecha":
                fx, fy = cx_max - 50, centro_y
            elif dir_nombre == "izquierda":
                fx, fy = cx_min + 50, centro_y
            elif dir_nombre == "abajo":
                fx, fy = centro_x, cy_max - 40
            else:
                fx, fy = centro_x, cy_min + 40

            k_pos = (fx // 25, fy // 25)
            if k_pos not in posiciones_usadas:
                posiciones_usadas.add(k_pos)
                flechas.append({
                    "x": fx, "y": fy,
                    "direccion": dir_nombre,
                    "tipo": "llave"
                })
        dir_anterior = dir_nombre

    # 2. Flechas guiando desde la llave hacia la salida
    dir_anterior = None
    for i in range(len(camino_salida) - 1):
        curr = camino_salida[i]
        nxt = camino_salida[i + 1]

        if nxt[0] > curr[0]: dir_nombre = "derecha"
        elif nxt[0] < curr[0]: dir_nombre = "izquierda"
        elif nxt[1] > curr[1]: dir_nombre = "abajo"
        else: dir_nombre = "arriba"

        es_inicio = (i == 0)
        es_giro = (dir_nombre != dir_anterior)
        es_interseccion = len(adj.get(curr, [])) >= 3

        if es_inicio or es_giro or es_interseccion or (i % 2 == 0):
            cx_min = x_offset + curr[0] * w_cell
            cx_max = x_offset + (curr[0] + 1) * w_cell
            cy_min = y_techo + curr[1] * h_cell
            cy_max = y_techo + (curr[1] + 1) * h_cell
            centro_x = cx_min + w_cell // 2
            centro_y = cy_min + h_cell // 2

            if dir_nombre == "derecha":
                fx, fy = cx_max - 50, centro_y
            elif dir_nombre == "izquierda":
                fx, fy = cx_min + 50, centro_y
            elif dir_nombre == "abajo":
                fx, fy = centro_x, cy_max - 40
            else:
                fx, fy = centro_x, cy_min + 40

            k_pos = (fx // 25, fy // 25)
            if k_pos not in posiciones_usadas:
                posiciones_usadas.add(k_pos)
                flechas.append({
                    "x": fx, "y": fy,
                    "direccion": dir_nombre,
                    "tipo": "salida"
                })
        dir_anterior = dir_nombre

    return {
        "rocas": rocas,
        "barreras": barreras,
        "corales": corales,
        "algas": algas,
        "pinchos": pinchos,
        "flechas": flechas,
        "p1_x": p1_x, "p1_y": p1_y,
        "p2_x": p2_x, "p2_y": p2_y,
        "llave_x": llave_x, "llave_y": llave_y,
        "puerta_x": puerta_x, "puerta_y": puerta_y,
        "key_cell": key_cell,
        "exit_cell": exit_node,
        "distancia_llave": dist[key_cell],
        "distancia_salida": dist[exit_node],
        "num_callejones": len(dead_ends),
        "num_trampas": len(pinchos),
    }


def dibujar_camaras_aire_escenario(superficie, camaras_aire, tick):
    """
    Dibuja las cámaras de aire y zonas seguras para respirar en Mundo 3 Nivel 5:
    - Bóveda de aire translúcida con brillo cian y borde burbujeante.
    - Superficie líquida ondulante que separa el agua del aire.
    - Microburbujas de oxígeno ascendentes que invitan al jugador a recargar.
    - Rótulo resplandeciente 'AIRE / O2' indicando claramente la zona segura.
    """
    fuente_aire = obtener_fuente_pequena(12, negrita=True)
    for cam in camaras_aire:
        r = cam["rect"]

        # 1. Bóveda de aire translúcida
        s_aire = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        pulso_alfa = int(40 + 12 * math.sin(tick * 0.05 + r.x * 0.01))
        pygame.draw.rect(s_aire, (180, 240, 255, pulso_alfa), (0, 0, r.width, r.height), border_radius=14)
        pygame.draw.rect(s_aire, (140, 230, 255, 140), (0, 0, r.width, r.height), width=2, border_radius=14)

        # 2. Microburbujas de oxígeno flotando hacia arriba dentro de la cámara
        for b_idx in range(6):
            bx = (r.x * 7 + b_idx * 31 + tick * 0.6) % (r.width - 20) + 10
            by = (r.height - 10) - ((tick * 1.2 + b_idx * 27) % (r.height - 20))
            r_burbuja = 2 if b_idx % 2 == 0 else 3
            pygame.draw.circle(s_aire, (225, 250, 255, 180), (int(bx), int(by)), r_burbuja)
            pygame.draw.circle(s_aire, (255, 255, 255, 240), (int(bx), int(by)), 1)

        superficie.blit(s_aire, (r.x, r.y))

        # 3. Ondulación superficial en la entrada inferior/abierta
        for ox in range(r.left, r.right, 6):
            oy = r.bottom - 4 + int(math.sin(tick * 0.12 + ox * 0.08) * 3)
            pygame.draw.circle(superficie, (200, 245, 255), (ox, oy), 2)

        # 4. Cartel o insignia 'AIRE O2'
        ancho_tag, alto_tag = 76, 20
        tag_x = r.centerx - ancho_tag // 2
        tag_y = r.top + 8
        s_tag = pygame.Surface((ancho_tag, alto_tag), pygame.SRCALPHA)
        pygame.draw.rect(s_tag, (15, 30, 48, 200), (0, 0, ancho_tag, alto_tag), border_radius=10)
        pygame.draw.rect(s_tag, (100, 225, 255, 220), (0, 0, ancho_tag, alto_tag), width=1, border_radius=10)
        lbl_surf = fuente_aire.render("AIRE  O2", True, (220, 250, 255))
        s_tag.blit(lbl_surf, ((ancho_tag - lbl_surf.get_width()) // 2, (alto_tag - lbl_surf.get_height()) // 2))
        superficie.blit(s_tag, (tag_x, tag_y))


def dibujar_corrientes_marinas_escenario(superficie, corrientes_marinas, tick):
    """
    Dibuja las corrientes marinas y sus vectores de fuerza en Mundo 3 Nivel 5:
    - Ondas de flujo translúcidas dinámicas en la dirección del empuje.
    - Flechas chevrons de corriente submarina mostrando la trayectoria.
    - Partículas y estelas de burbujas arrastradas a alta velocidad.
    """
    for corr in corrientes_marinas:
        r = corr["rect"]
        fx = corr["fuerza_x"]
        fy = corr["fuerza_y"]
        direccion = corr.get("direccion", "derecha")

        s_corr = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        pygame.draw.rect(s_corr, (110, 215, 255, 28), (0, 0, r.width, r.height), border_radius=8)

        if direccion in ("derecha", "izquierda"):
            vel_signo = 1 if fx > 0 else -1
            num_lineas = max(2, r.height // 35)
            for li in range(num_lineas):
                ly = int((li + 0.5) * (r.height / float(num_lineas)))
                offset_x = int((tick * (abs(fx) * 1.8) * vel_signo) % 60)
                for lx in range(-60, r.width + 60, 60):
                    x_start = lx + offset_x
                    x_end = x_start + int(36 * (1 if fx > 0 else -1))
                    if 0 <= x_start <= r.width or 0 <= x_end <= r.width:
                        pygame.draw.line(s_corr, (160, 235, 255, 75), (max(0, min(r.width, x_start)), ly), (max(0, min(r.width, x_end)), ly), 2)
                        arrow_tip_x = x_end
                        if 5 <= arrow_tip_x <= r.width - 5:
                            if fx > 0:
                                pygame.draw.lines(s_corr, (210, 245, 255, 120), False, [(arrow_tip_x - 7, ly - 5), (arrow_tip_x, ly), (arrow_tip_x - 7, ly + 5)], 2)
                            else:
                                pygame.draw.lines(s_corr, (210, 245, 255, 120), False, [(arrow_tip_x + 7, ly - 5), (arrow_tip_x, ly), (arrow_tip_x + 7, ly + 5)], 2)
        elif direccion in ("arriba", "abajo"):
            vel_signo = 1 if fy > 0 else -1
            num_lineas = max(2, r.width // 35)
            for li in range(num_lineas):
                lx = int((li + 0.5) * (r.width / float(num_lineas)))
                offset_y = int((tick * (abs(fy) * 1.8) * vel_signo) % 60)
                for ly in range(-60, r.height + 60, 60):
                    y_start = ly + offset_y
                    y_end = y_start + int(36 * (1 if fy > 0 else -1))
                    if 0 <= y_start <= r.height or 0 <= y_end <= r.height:
                        pygame.draw.line(s_corr, (160, 235, 255, 75), (lx, max(0, min(r.height, y_start))), (lx, max(0, min(r.height, y_end))), 2)
                        arrow_tip_y = y_end
                        if 5 <= arrow_tip_y <= r.height - 5:
                            if fy > 0:
                                pygame.draw.lines(s_corr, (210, 245, 255, 120), False, [(lx - 5, arrow_tip_y - 7), (lx, arrow_tip_y), (lx + 5, arrow_tip_y - 7)], 2)
                            else:
                                pygame.draw.lines(s_corr, (210, 245, 255, 120), False, [(lx - 5, arrow_tip_y + 7), (lx, arrow_tip_y), (lx + 5, arrow_tip_y + 7)], 2)

        superficie.blit(s_corr, (r.x, r.y))


def _dibujar_hud_oxigeno_m3_n5(pantalla_surf, oxigeno_p1, oxigeno_p2, p1_color, p2_color, tick):
    """
    Dibuja los medidores de oxígeno de ambos jugadores en la esquina superior izquierda de la pantalla:
    - Barra de oxígeno fluida con color cian/verde cuando está llena, ámbar en nivel medio, y rojo palpitante en peligro.
    - Porcentaje numérico exacto de reserva de aire.
    - Alerta visual destacada cuando el oxígeno cae por debajo del 25%.
    """
    fuente_hud = obtener_fuente_pequena(12, negrita=True)
    fuente_pct = obtener_fuente_contador(11, negrita=True)

    w_badge, h_badge = 195, 34
    x_base, y_base = 28, 22

    datos_p = [
        (oxigeno_p1, "P1", p1_color, x_base, y_base),
        (oxigeno_p2, "P2", p2_color, x_base + w_badge + 12, y_base),
    ]

    for o2, tag_p, col_p, bx, by in datos_p:
        s_hud = pygame.Surface((w_badge, h_badge), pygame.SRCALPHA)
        pct = max(0.0, min(100.0, o2))
        es_critico = pct < 25.0

        col_fondo = (20, 10, 15, 230) if (es_critico and (tick // 15) % 2 == 0) else (12, 22, 36, 225)
        pygame.draw.rect(s_hud, col_fondo, (0, 0, w_badge, h_badge), border_radius=17)

        if es_critico:
            borde_col = (255, 60, 75) if (tick // 10) % 2 == 0 else (180, 40, 50)
        elif pct < 50.0:
            borde_col = (255, 205, 50)
        else:
            borde_col = (75, 210, 245)
        pygame.draw.rect(s_hud, borde_col, (0, 0, w_badge, h_badge), width=2, border_radius=17)

        cx_ico, cy_ico = 16, h_badge // 2
        col_ico = (255, 70, 80) if es_critico else (100, 235, 255)
        pygame.draw.circle(s_hud, col_ico, (cx_ico, cy_ico), 7)
        pygame.draw.circle(s_hud, (255, 255, 255), (cx_ico - 2, cy_ico - 2), 2)

        t_jug = fuente_hud.render(f"O2 {tag_p}", True, (255, 255, 255))
        s_hud.blit(t_jug, (28, 4))

        t_pct = fuente_pct.render(f"{int(pct)}%", True, (255, 240, 200) if not es_critico else (255, 100, 110))
        s_hud.blit(t_pct, (w_badge - t_pct.get_width() - 10, 4))

        bar_x, bar_y = 28, 20
        bar_w, bar_h = w_badge - 38, 9
        pygame.draw.rect(s_hud, (25, 35, 48), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        w_llenado = int(bar_w * (pct / 100.0))
        if w_llenado > 0:
            if es_critico:
                col_bar = (255, 55, 75)
            elif pct < 50.0:
                col_bar = (255, 205, 45)
            else:
                col_bar = (45, 220, 185)
            pygame.draw.rect(s_hud, col_bar, (bar_x, bar_y, w_llenado, bar_h), border_radius=4)
            if bar_h > 3:
                pygame.draw.rect(s_hud, (255, 255, 255, 120), (bar_x, bar_y, w_llenado, 2), border_radius=2)

        pantalla_surf.blit(s_hud, (bx, by))


_SURF_ALERTA_O2 = None


def dibujar_alerta_oxigeno_personaje(superficie, jugador, oxigeno, tick):
    """Muestra un icono flotante de advertencia cuando el personaje está a punto de ahogarse."""
    global _SURF_ALERTA_O2
    if jugador.get("muerto", False) or oxigeno >= 22.0:
        return
    if (tick // 12) % 2 == 0:
        hx = jugador["hitbox"].centerx
        hy = jugador["hitbox"].top - 18
        if _SURF_ALERTA_O2 is None:
            s_alerta = pygame.Surface((38, 16), pygame.SRCALPHA)
            pygame.draw.rect(s_alerta, (230, 40, 50, 220), (0, 0, 38, 16), border_radius=8)
            fuente_aviso = obtener_fuente_pequena(10, negrita=True)
            lbl = fuente_aviso.render("! O2", True, (255, 255, 255))
            s_alerta.blit(lbl, ((38 - lbl.get_width()) // 2, (16 - lbl.get_height()) // 2))
            _SURF_ALERTA_O2 = s_alerta
        superficie.blit(_SURF_ALERTA_O2, (hx - 19, hy))


class EstadoNivel:
    """
    Estado de un nivel en curso: jugadores, objetos, mecánicas, cámara y HUD (antes eran las
    variables locales de iniciar_mundo). __init__ hace toda la preparación: carga el nivel desde
    niveles.py, crea los sprites y el HUD, dibuja el primer cuadro y corre la animación de apertura.
    Cada fase del frame es una función _fase(n) que trabaja sobre este objeto.
    """

    def __init__(self, mecanicas=None, numero_nivel=1, color_p1=None, color_p2=None, mundo=1, niveles_desbloqueados=None, partida_id=None, partida_nombre=None, snapshot_guardado=None, accesorio_p1=None, accesorio_p2=None, partida_password=None):
        self.mecanicas = mecanicas
        self.numero_nivel = numero_nivel
        self.color_p1 = color_p1
        self.color_p2 = color_p2
        self.mundo = mundo
        self.niveles_desbloqueados = niveles_desbloqueados
        self.partida_id = partida_id
        self.partida_nombre = partida_nombre
        self.snapshot_guardado = snapshot_guardado
        self.accesorio_p1 = accesorio_p1
        self.accesorio_p2 = accesorio_p2
        self.partida_password = partida_password
        self.numero_mundo = self.mundo
        self.p1_acc = self.accesorio_p1 if self.accesorio_p1 else "Ninguno"
        self.p2_acc = self.accesorio_p2 if self.accesorio_p2 else "Ninguno"
        if self.mecanicas is None:
            self.mecanicas = []

        if self.niveles_desbloqueados is None:
            self.niveles_desbloqueados = crear_desbloqueados_inicial()

        # Reproducción centralizada de música del mundo correspondiente (sin reiniciar dentro del mismo mundo)
        reproducir_musica(f"mundo_{self.numero_mundo}")

        self.es_admin = es_partida_admin(self.partida_nombre, self.partida_id)
        if self.es_admin:
            self.hay_siguiente_nivel = not (self.numero_mundo >= 3 and self.numero_nivel >= 6)
        else:
            self.hay_siguiente_nivel = not (self.numero_mundo >= 3 and self.numero_nivel >= 5)

        self.usar_caja = "caja" in self.mecanicas
        self.usar_soga = "soga" in self.mecanicas
        self.usar_agua = "agua" in self.mecanicas
        self.usar_pinchos = "pinchos" in self.mecanicas
        self.usar_llave = True

        self.linterna_p1 = True
        self.linterna_p2 = True
        self.surf_oscuridad_m3 = None
        self.surf_oscuridad_m3_n4 = None
        self.surf_luz_linterna = None
        self.surf_luz_tenue = None
        self.flechas_indicadoras = []

        self.oxigeno_p1 = 100.0
        self.oxigeno_p2 = 100.0
        self.OXIGENO_MAX = 100.0
        self.camaras_aire = []
        self.corrientes_marinas = []

        self.pantalla = pygame.display.get_surface()
        if self.pantalla is None:
            from ventana import crear_ventana
            self.pantalla = crear_ventana()

        self.mundo_rect = pygame.Rect(0, 0, ANCHO_MUNDO, ALTO)
        self.reloj = pygame.time.Clock()
        self.fuente_tut = obtener_fuente_texto(TAMANO_TEXTO_GRANDE, tamano_fallback=32)

        self.W_BOTON_HUD, self.H_BOTON_HUD = 44, 52
        self.MARGEN_DER, self.MARGEN_SUP, self.ESPACIO_BOTONES = 18, 16, 12

        self.rect_btn_x = pygame.Rect(self.pantalla.get_width() - self.MARGEN_DER - self.W_BOTON_HUD, self.MARGEN_SUP, self.W_BOTON_HUD, self.H_BOTON_HUD)
        self.rect_btn_reiniciar = pygame.Rect(self.rect_btn_x.left - self.ESPACIO_BOTONES - self.W_BOTON_HUD, self.MARGEN_SUP, self.W_BOTON_HUD, self.H_BOTON_HUD)
        self.rect_btn_casa = pygame.Rect(self.rect_btn_reiniciar.left - self.ESPACIO_BOTONES - self.W_BOTON_HUD, self.MARGEN_SUP, self.W_BOTON_HUD, self.H_BOTON_HUD)
        self.rect_btn_config = pygame.Rect(self.rect_btn_casa.left - self.ESPACIO_BOTONES - self.W_BOTON_HUD, self.MARGEN_SUP, self.W_BOTON_HUD, self.H_BOTON_HUD)

        def _cargar_hud(nombre):
            return cargar_boton_escalado(nombre, self.W_BOTON_HUD, self.H_BOTON_HUD)
        self._cargar_hud = _cargar_hud

        self.spr_x_normal = self._cargar_hud("boton-x.png")
        self.spr_x_semi = self._cargar_hud("boton-x-semiapretado.png")
        self.spr_x_apretado = self._cargar_hud("boton-x-apretado.png")
        self.spr_x_hover = aclarar_boton(self.spr_x_normal)

        self.spr_reiniciar_normal = self._cargar_hud("boton-reiniciar-icono.png")
        self.spr_reiniciar_semi = self._cargar_hud("boton-reiniciar-icono-semiapretado.png")
        self.spr_reiniciar_apretado = self._cargar_hud("boton-reiniciar-icono-apretado.png")
        self.spr_reiniciar_hover = aclarar_boton(self.spr_reiniciar_normal)

        self.spr_casa_normal = self._cargar_hud("boton-casa.png")
        self.spr_casa_semi = self._cargar_hud("boton-casa-semiapretado.png")
        self.spr_casa_apretado = self._cargar_hud("boton-casa-apretado.png")
        self.spr_casa_hover = aclarar_boton(self.spr_casa_normal)

        self.spr_config_normal = self._cargar_hud("boton-configuracion.png")
        self.spr_config_semi = self._cargar_hud("boton-configuracion-semiapretado.png")
        self.spr_config_apretado = self._cargar_hud("boton-configuracion-apretado.png")
        self.spr_config_hover = aclarar_boton(self.spr_config_normal)

        self.fondo_btn_config = None
        self.fondo_btn_casa = None
        self.fondo_btn_reiniciar = None
        self.fondo_btn_x = None

        self.p1_color = self.color_p1 if self.color_p1 else COLOR_JUGADOR1
        self.p2_color = self.color_p2 if self.color_p2 else COLOR_JUGADOR2

        # Configuración de botones e indicadores para Tutorial (Nivel 1)
        self.TAM_BTN_TUT = 32
        self.GAP_BTN_TUT = 3

        self.COLORES_PERSONAJES = {
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
                return pygame.transform.smoothscale(img, (self.TAM_BTN_TUT, self.TAM_BTN_TUT))

            # Botón procedimental si no encuentra la imagen (mismo diseño de tecla roja)
            surf = pygame.Surface((self.TAM_BTN_TUT, self.TAM_BTN_TUT), pygame.SRCALPHA)
            color_fondo = (237, 112, 109)
            color_borde = (94, 4, 4)
            color_sombra = (237, 86, 83)
            color_letra = (94, 4, 4)

            pygame.draw.rect(surf, color_fondo, (0, 0, self.TAM_BTN_TUT, self.TAM_BTN_TUT), border_radius=6)
            pygame.draw.rect(surf, color_sombra, (2, self.TAM_BTN_TUT - 5, self.TAM_BTN_TUT - 4, 3), border_bottom_left_radius=4, border_bottom_right_radius=4)
            pygame.draw.rect(surf, color_borde, (0, 0, self.TAM_BTN_TUT, self.TAM_BTN_TUT), width=2, border_radius=6)

            fuente_tecla = obtener_fuente_boton(int(self.TAM_BTN_TUT * 0.58), negrita=True)
            txt_surf = fuente_tecla.render(str(letra_fallback).upper(), True, color_letra)
            rect_txt = txt_surf.get_rect(center=(self.TAM_BTN_TUT // 2, self.TAM_BTN_TUT // 2 - 1))
            surf.blit(txt_surf, rect_txt)
            return surf
        self._cargar_o_crear_boton = _cargar_o_crear_boton

        def _crear_etiqueta_jugador(texto, color_nombre):
            color_base = self.COLORES_PERSONAJES.get(color_nombre, (124, 231, 255))
            color_borde = (max(0, color_base[0] - 65), max(0, color_base[1] - 65), max(0, color_base[2] - 65))
            fuente = obtener_fuente_pequena(16, negrita=True)
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
        self._crear_etiqueta_jugador = _crear_etiqueta_jugador

        # Cargar botones WASD para Jugador 1 (P1: W arriba, A izquierda, S abajo, D derecha)
        self.btn_w = self._cargar_o_crear_boton(["boton-w.png", "boton-W.png", "w.png", "W.png"], "W")
        self.btn_s = self._cargar_o_crear_boton(["boton-s.png", "boton-S.png", "s.png", "S.png"], "S")
        self.btn_a = self._cargar_o_crear_boton(["boton-a.png", "boton-A.png", "a.png", "A.png"], "A")
        self.btn_d = self._cargar_o_crear_boton(["boton-d.png", "boton-D.png", "d.png", "D.png"], "D")
        self.badge_p1 = self._crear_etiqueta_jugador("P1", self.p1_color)

        # Cargar botones Flechas para Jugador 2 (P2: Flecha arriba, flecha izquierda, flecha abajo, flecha derecha)
        self.btn_arr = self._cargar_o_crear_boton(["boton-arriba.png", "arriba.png"], "↑")
        self.btn_aba = self._cargar_o_crear_boton(["boton-abajo.png", "abajo.png"], "↓")
        self.btn_izq = self._cargar_o_crear_boton(["boton-izquierda.png", "izquierda.png"], "←")
        self.btn_der = self._cargar_o_crear_boton(["boton-derecha.png", "derecha.png"], "→")
        self.badge_p2 = self._crear_etiqueta_jugador("P2", self.p2_color)

        def _dibujar_cluster_jugador(superficie, jugador, badge, btn_arriba, btn_izq, btn_abajo, btn_der, k_arriba, k_izq, k_abajo, k_der, teclas_presionadas, alpha=255, bottom_override=None):
            if jugador.get("muerto", False):
                return 0

            ancho_grid = 3 * self.TAM_BTN_TUT + 2 * self.GAP_BTN_TUT
            alto_grid = 2 * self.TAM_BTN_TUT + self.GAP_BTN_TUT
            alto_total = badge.get_height() + 4 + alto_grid

            surf_total = pygame.Surface((ancho_grid, alto_total), pygame.SRCALPHA)

            # 1. Badge centrado arriba
            badge_x = (ancho_grid - badge.get_width()) // 2
            surf_total.blit(badge, (badge_x, 0))

            # 2. Teclas abajo del badge
            y_grid_offset = badge.get_height() + 4
            col0_x = 0
            col1_x = self.TAM_BTN_TUT + self.GAP_BTN_TUT
            col2_x = 2 * (self.TAM_BTN_TUT + self.GAP_BTN_TUT)
            row1_y = self.TAM_BTN_TUT + self.GAP_BTN_TUT

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
        self._dibujar_cluster_jugador = _dibujar_cluster_jugador

        def _dibujar_controles_tutorial(superficie, alpha_p1=255, alpha_p2=255, teclas_actuales=None):
            if teclas_actuales is None:
                teclas_actuales = pygame.key.get_pressed()

            # Determinar posición vertical si uno está parado sobre el otro
            bottom_p1 = self.jugador1["hitbox"].top - 8
            bottom_p2 = self.jugador2["hitbox"].top - 8

            if self.p1_sobre_p2:
                h_p1 = self.badge_p1.get_height() + 4 + (2 * self.TAM_BTN_TUT + self.GAP_BTN_TUT)
                bottom_p2 = bottom_p1 - h_p1 - 6
            elif self.p2_sobre_p1:
                h_p2 = self.badge_p2.get_height() + 4 + (2 * self.TAM_BTN_TUT + self.GAP_BTN_TUT)
                bottom_p1 = bottom_p2 - h_p2 - 6

            # Dibujar WASD directamente sobre Jugador 1
            if not self.p1_completado and not self.jugador1["muerto"] and not self.p1_soplado and alpha_p1 > 0:
                self._dibujar_cluster_jugador(
                    superficie, self.jugador1, self.badge_p1,
                    self.btn_w, self.btn_a, self.btn_s, self.btn_d,
                    pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                    teclas_actuales, alpha=int(alpha_p1), bottom_override=bottom_p1
                )

            # Dibujar Flechas directamente sobre Jugador 2
            if not self.p2_completado and not self.jugador2["muerto"] and not self.p2_soplado and alpha_p2 > 0:
                self._dibujar_cluster_jugador(
                    superficie, self.jugador2, self.badge_p2,
                    self.btn_arr, self.btn_izq, self.btn_aba, self.btn_der,
                    pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT,
                    teclas_actuales, alpha=int(alpha_p2), bottom_override=bottom_p2
                )
        self._dibujar_controles_tutorial = _dibujar_controles_tutorial

        def _crear_efecto_soplar(jugador_quieto, es_p1, dir_viento):
            alto_grid = 2 * self.TAM_BTN_TUT + self.GAP_BTN_TUT
            badge_ref = self.badge_p1 if es_p1 else self.badge_p2
            alto_total = badge_ref.get_height() + 4 + alto_grid
            ancho_grid = 3 * self.TAM_BTN_TUT + 2 * self.GAP_BTN_TUT

            left_cluster = jugador_quieto["hitbox"].centerx - ancho_grid // 2
            top_cluster = (jugador_quieto["hitbox"].top - 8) - alto_total

            y_grid_offset = badge_ref.get_height() + 4
            col0_x = 0
            col1_x = self.TAM_BTN_TUT + self.GAP_BTN_TUT
            col2_x = 2 * (self.TAM_BTN_TUT + self.GAP_BTN_TUT)
            row1_y = self.TAM_BTN_TUT + self.GAP_BTN_TUT

            if es_p1:
                badge_surf = self.badge_p1
                btn_arr_surf = self.btn_w
                btn_izq_surf = self.btn_a
                btn_aba_surf = self.btn_s
                btn_der_surf = self.btn_d
            else:
                badge_surf = self.badge_p2
                btn_arr_surf = self.btn_arr
                btn_izq_surf = self.btn_izq
                btn_aba_surf = self.btn_aba
                btn_der_surf = self.btn_der

            piezas = [
                # Badge centrado arriba
                {
                    "surf": badge_surf,
                    "x": float(left_cluster + ancho_grid // 2),
                    "y": float(top_cluster + badge_surf.get_height() // 2),
                    "vx": dir_viento * random.uniform(6.5, 8.5),
                    "vy": random.uniform(-4.5, -3.0),
                    "rot": 0.0,
                    "rot_vel": dir_viento * random.uniform(2.5, 4.5),
                    "alpha": 255.0,
                },
                # Tecla arriba
                {
                    "surf": btn_arr_surf,
                    "x": float(left_cluster + col1_x + self.TAM_BTN_TUT // 2),
                    "y": float(top_cluster + y_grid_offset + self.TAM_BTN_TUT // 2),
                    "vx": dir_viento * random.uniform(6.0, 8.0),
                    "vy": random.uniform(-3.5, -2.0),
                    "rot": 0.0,
                    "rot_vel": dir_viento * random.uniform(3.0, 5.5),
                    "alpha": 255.0,
                },
                # Tecla izquierda
                {
                    "surf": btn_izq_surf,
                    "x": float(left_cluster + col0_x + self.TAM_BTN_TUT // 2),
                    "y": float(top_cluster + y_grid_offset + row1_y + self.TAM_BTN_TUT // 2),
                    "vx": dir_viento * (random.uniform(8.5, 11.0) if dir_viento < 0 else random.uniform(4.5, 6.5)),
                    "vy": random.uniform(-2.5, -1.0),
                    "rot": 0.0,
                    "rot_vel": dir_viento * random.uniform(3.5, 6.0),
                    "alpha": 255.0,
                },
                # Tecla abajo
                {
                    "surf": btn_aba_surf,
                    "x": float(left_cluster + col1_x + self.TAM_BTN_TUT // 2),
                    "y": float(top_cluster + y_grid_offset + row1_y + self.TAM_BTN_TUT // 2),
                    "vx": dir_viento * random.uniform(5.5, 7.5),
                    "vy": random.uniform(-1.0, 0.5),
                    "rot": 0.0,
                    "rot_vel": dir_viento * random.uniform(2.0, 4.5),
                    "alpha": 255.0,
                },
                # Tecla derecha
                {
                    "surf": btn_der_surf,
                    "x": float(left_cluster + col2_x + self.TAM_BTN_TUT // 2),
                    "y": float(top_cluster + y_grid_offset + row1_y + self.TAM_BTN_TUT // 2),
                    "vx": dir_viento * (random.uniform(8.5, 11.0) if dir_viento > 0 else random.uniform(4.5, 6.5)),
                    "vy": random.uniform(-2.5, -1.0),
                    "rot": 0.0,
                    "rot_vel": dir_viento * random.uniform(3.5, 6.0),
                    "alpha": 255.0,
                },
            ]

            for p in piezas:
                self.teclas_sopladas.append(p)

            # Líneas de viento estilo pixel art
            for _ in range(10):
                self.lineas_viento.append({
                    "tipo": "linea",
                    "x": float(left_cluster + random.randint(-15, ancho_grid + 15)),
                    "y": float(top_cluster + random.randint(0, alto_total)),
                    "longitud": random.randint(14, 28),
                    "grosor": random.choice([1, 2]),
                    "vx": dir_viento * random.uniform(11.0, 16.0),
                    "vy": random.uniform(-0.8, 0.5),
                    "alpha": 220.0,
                    "fade": random.uniform(10.0, 14.0),
                })

            # Partículas discretas de aire pixel art
            for _ in range(8):
                self.lineas_viento.append({
                    "tipo": "particula",
                    "x": float(left_cluster + random.randint(-10, ancho_grid + 10)),
                    "y": float(top_cluster + random.randint(0, alto_total)),
                    "tam": random.choice([2, 3]),
                    "vx": dir_viento * random.uniform(7.0, 12.0),
                    "vy": random.uniform(-1.5, 0.5),
                    "alpha": 240.0,
                    "fade": random.uniform(7.0, 10.0),
                })
        self._crear_efecto_soplar = _crear_efecto_soplar

        def _actualizar_y_dibujar_soplado(superficie):
            # 1. Actualizar y dibujar líneas y partículas de viento
            activas_viento = []
            for elem in self.lineas_viento:
                elem["x"] += elem["vx"]
                elem["y"] += elem["vy"]
                elem["alpha"] -= elem["fade"]
                if elem["alpha"] > 0:
                    activas_viento.append(elem)
                    alpha_int = max(0, min(255, int(elem["alpha"])))
                    if elem["tipo"] == "linea":
                        surf_lin = pygame.Surface((elem["longitud"], elem["grosor"] + 2), pygame.SRCALPHA)
                        pygame.draw.line(surf_lin, (255, 255, 255, alpha_int), (0, 1), (elem["longitud"], 1), elem["grosor"])
                        superficie.blit(surf_lin, (int(elem["x"]), int(elem["y"])))
                    elif elem["tipo"] == "particula":
                        tam = elem["tam"]
                        surf_pt = pygame.Surface((tam, tam), pygame.SRCALPHA)
                        surf_pt.fill((255, 255, 255, alpha_int))
                        superficie.blit(surf_pt, (int(elem["x"]), int(elem["y"])))
            self.lineas_viento[:] = activas_viento

            # 2. Actualizar y dibujar teclas sopladas con rotación y desvanecimiento
            activas_teclas = []
            for pieza in self.teclas_sopladas:
                pieza["x"] += pieza["vx"]
                pieza["y"] += pieza["vy"]
                pieza["vy"] += 0.12  # Suave aceleración gravitacional
                pieza["rot"] += pieza["rot_vel"]
                pieza["alpha"] = max(0.0, pieza["alpha"] - 5.5)

                if pieza["alpha"] > 0:
                    activas_teclas.append(pieza)
                    surf_rot = pygame.transform.rotate(pieza["surf"], pieza["rot"])
                    surf_rot.set_alpha(int(pieza["alpha"]))
                    rect_rot = surf_rot.get_rect(center=(int(pieza["x"]), int(pieza["y"])))
                    superficie.blit(surf_rot, rect_rot)
            self.teclas_sopladas[:] = activas_teclas
        self._actualizar_y_dibujar_soplado = _actualizar_y_dibujar_soplado

        self.boton_nivel = None
        self.pared_nivel = None
        self.dintel_superior = None
        self.laser_nivel = None
        self.pozo_nivel = None
        self.paredes_colores = None
        self.botones_colores = None
        self.plataformas_base = None
        self.barrera_l_horiz = None
        self.barrera_l_vert = None
        self.boton_compuerta = None
        self.compuerta = None
        self.plataforma_movil = None
        self.bloque_central = None
        self.bloque_peligroso = None
        self.bloques_peligrosos = []
        self.plat_elevada = None
        self.plataformas_derrumbables = None
        self.plataformas_alternadas = None
        self.rocas_submarinas = None
        self.barreras_algas = None
        self.corales_decorativos = None
        self.algas_decorativas = None
        self.burbujas_m3 = None
        self.tick_m3 = 0
        self.tick_m1 = 0
        self.tick_m2 = 0
        self.estado_soga = crear_estado_soga()

        # Los niveles viven en niveles.py (una función por nivel). Se importa acá y no al inicio
        # del módulo porque niveles.py usa funciones de pantalla.py (evita el import circular).
        from niveles import definir_nivel
        self.definicion_nivel = definir_nivel(self.numero_mundo, self.numero_nivel, self.p1_color, self.p2_color, self.bloques_peligrosos)
        if self.definicion_nivel is not None:
            if "algas_decorativas" in self.definicion_nivel: self.algas_decorativas = self.definicion_nivel["algas_decorativas"]
            if "ancho_mundo_nivel" in self.definicion_nivel: self.ancho_mundo_nivel = self.definicion_nivel["ancho_mundo_nivel"]
            if "b" in self.definicion_nivel: self.b = self.definicion_nivel["b"]
            if "barrera_l_horiz" in self.definicion_nivel: self.barrera_l_horiz = self.definicion_nivel["barrera_l_horiz"]
            if "barrera_l_vert" in self.definicion_nivel: self.barrera_l_vert = self.definicion_nivel["barrera_l_vert"]
            if "barreras_algas" in self.definicion_nivel: self.barreras_algas = self.definicion_nivel["barreras_algas"]
            if "bloque_central" in self.definicion_nivel: self.bloque_central = self.definicion_nivel["bloque_central"]
            if "bloque_peligroso" in self.definicion_nivel: self.bloque_peligroso = self.definicion_nivel["bloque_peligroso"]
            if "boton_compuerta" in self.definicion_nivel: self.boton_compuerta = self.definicion_nivel["boton_compuerta"]
            if "boton_nivel" in self.definicion_nivel: self.boton_nivel = self.definicion_nivel["boton_nivel"]
            if "botones_colores" in self.definicion_nivel: self.botones_colores = self.definicion_nivel["botones_colores"]
            if "burbujas_m3" in self.definicion_nivel: self.burbujas_m3 = self.definicion_nivel["burbujas_m3"]
            if "by" in self.definicion_nivel: self.by = self.definicion_nivel["by"]
            if "caja" in self.definicion_nivel: self.caja = self.definicion_nivel["caja"]
            if "camaras_aire" in self.definicion_nivel: self.camaras_aire = self.definicion_nivel["camaras_aire"]
            if "compuerta" in self.definicion_nivel: self.compuerta = self.definicion_nivel["compuerta"]
            if "corales_decorativos" in self.definicion_nivel: self.corales_decorativos = self.definicion_nivel["corales_decorativos"]
            if "corrientes_marinas" in self.definicion_nivel: self.corrientes_marinas = self.definicion_nivel["corrientes_marinas"]
            if "datos_lab" in self.definicion_nivel: self.datos_lab = self.definicion_nivel["datos_lab"]
            if "flechas_indicadoras" in self.definicion_nivel: self.flechas_indicadoras = self.definicion_nivel["flechas_indicadoras"]
            if "jugador1" in self.definicion_nivel: self.jugador1 = self.definicion_nivel["jugador1"]
            if "jugador2" in self.definicion_nivel: self.jugador2 = self.definicion_nivel["jugador2"]
            if "laser_nivel" in self.definicion_nivel: self.laser_nivel = self.definicion_nivel["laser_nivel"]
            if "linterna_p1" in self.definicion_nivel: self.linterna_p1 = self.definicion_nivel["linterna_p1"]
            if "linterna_p2" in self.definicion_nivel: self.linterna_p2 = self.definicion_nivel["linterna_p2"]
            if "llave" in self.definicion_nivel: self.llave = self.definicion_nivel["llave"]
            if "mundo_rect" in self.definicion_nivel: self.mundo_rect = self.definicion_nivel["mundo_rect"]
            if "oxigeno_p1" in self.definicion_nivel: self.oxigeno_p1 = self.definicion_nivel["oxigeno_p1"]
            if "oxigeno_p2" in self.definicion_nivel: self.oxigeno_p2 = self.definicion_nivel["oxigeno_p2"]
            if "p" in self.definicion_nivel: self.p = self.definicion_nivel["p"]
            if "pared_nivel" in self.definicion_nivel: self.pared_nivel = self.definicion_nivel["pared_nivel"]
            if "paredes_colores" in self.definicion_nivel: self.paredes_colores = self.definicion_nivel["paredes_colores"]
            if "pinchos" in self.definicion_nivel: self.pinchos = self.definicion_nivel["pinchos"]
            if "plat_elevada" in self.definicion_nivel: self.plat_elevada = self.definicion_nivel["plat_elevada"]
            if "plataforma_movil" in self.definicion_nivel: self.plataforma_movil = self.definicion_nivel["plataforma_movil"]
            if "plataformas" in self.definicion_nivel: self.plataformas = self.definicion_nivel["plataformas"]
            if "plataformas_alternadas" in self.definicion_nivel: self.plataformas_alternadas = self.definicion_nivel["plataformas_alternadas"]
            if "plataformas_base" in self.definicion_nivel: self.plataformas_base = self.definicion_nivel["plataformas_base"]
            if "plataformas_derrumbables" in self.definicion_nivel: self.plataformas_derrumbables = self.definicion_nivel["plataformas_derrumbables"]
            if "pozo_nivel" in self.definicion_nivel: self.pozo_nivel = self.definicion_nivel["pozo_nivel"]
            if "puerta" in self.definicion_nivel: self.puerta = self.definicion_nivel["puerta"]
            if "r" in self.definicion_nivel: self.r = self.definicion_nivel["r"]
            if "rocas_submarinas" in self.definicion_nivel: self.rocas_submarinas = self.definicion_nivel["rocas_submarinas"]
            if "suelo" in self.definicion_nivel: self.suelo = self.definicion_nivel["suelo"]
            if "surf_luz_linterna" in self.definicion_nivel: self.surf_luz_linterna = self.definicion_nivel["surf_luz_linterna"]
            if "surf_luz_tenue" in self.definicion_nivel: self.surf_luz_tenue = self.definicion_nivel["surf_luz_tenue"]
            if "surf_oscuridad_m3" in self.definicion_nivel: self.surf_oscuridad_m3 = self.definicion_nivel["surf_oscuridad_m3"]
            if "techo_agua" in self.definicion_nivel: self.techo_agua = self.definicion_nivel["techo_agua"]
            if "tick_m3" in self.definicion_nivel: self.tick_m3 = self.definicion_nivel["tick_m3"]
            if "usar_agua" in self.definicion_nivel: self.usar_agua = self.definicion_nivel["usar_agua"]
            if "usar_caja" in self.definicion_nivel: self.usar_caja = self.definicion_nivel["usar_caja"]
            if "usar_llave" in self.definicion_nivel: self.usar_llave = self.definicion_nivel["usar_llave"]
            if "usar_pinchos" in self.definicion_nivel: self.usar_pinchos = self.definicion_nivel["usar_pinchos"]
            if "usar_soga" in self.definicion_nivel: self.usar_soga = self.definicion_nivel["usar_soga"]
        else:
            self.ancho_mundo_nivel = ANCHO_MUNDO
            self.suelo = pygame.Rect(0, ALTO - 80, ANCHO_MUNDO, 80)
            self.mundo_rect = pygame.Rect(0, 0, ANCHO_MUNDO, ALTO)

            self.jugador1 = crear_personaje(100, 0, self.p1_color)
            self.jugador2 = crear_personaje(300, 0, self.p2_color)

            self.caja = crear_caja(450, 0) if self.usar_caja else None
            self.pinchos = crear_pinchos(self.suelo.top) if self.usar_pinchos else []
            self.llave = crear_llave(1400, self.suelo.top - 46) if self.usar_llave else None
            self.puerta = crear_puerta(1900, self.suelo.top - 90) if self.usar_llave else None

            self.plataformas = []
            if self.usar_soga:
                self.plataformas.extend([
                    pygame.Rect(420, 530, 90, 30),
                    pygame.Rect(530, 440, 90, 30),
                    pygame.Rect(640, 350, 340, 35),
                ])

            if self.usar_agua:
                ZONA_AGUA.x, ZONA_AGUA.y = 0, 220
                ZONA_AGUA.width, ZONA_AGUA.height = ANCHO_MUNDO, self.suelo.top - 220

        self.p1_completado = False
        self.p2_completado = False
        self.mostrar_tutorial = (self.numero_mundo == 1 and self.numero_nivel == 1)
        self.contador_tutorial = 0
        self.frames_tutorial = 300  # Los controles duran 5 segundos antes de despejar la pantalla
        self.p1_movio = False
        self.p2_movio = False
        self.alpha_tut_p1 = 255.0
        self.alpha_tut_p2 = 255.0
        self.p1_soplado = False
        self.p2_soplado = False
        self.teclas_sopladas = []
        self.lineas_viento = []

        self.p1_sobre_p2 = False
        self.p2_sobre_p1 = False

        # Renderizar el fotograma inicial del escenario con los personajes en sus posiciones iniciales
        self.mundo_inicio = pygame.Surface((self.ancho_mundo_nivel, ALTO))

        if self.numero_mundo == 3:
            dibujar_submarino_fondo_escenario(self.mundo_inicio, self.ancho_mundo_nivel, 0)
            dibujar_lecho_marino(self.mundo_inicio, self.suelo, self.ancho_mundo_nivel)
            if self.algas_decorativas:
                dibujar_algas_decorativas_escenario(self.mundo_inicio, self.algas_decorativas, 0, capa="fondo")
            if self.corrientes_marinas:
                dibujar_corrientes_marinas_escenario(self.mundo_inicio, self.corrientes_marinas, 0)
            if self.camaras_aire:
                dibujar_camaras_aire_escenario(self.mundo_inicio, self.camaras_aire, 0)
            if self.rocas_submarinas:
                dibujar_rocas_submarinas_escenario(self.mundo_inicio, self.rocas_submarinas)
            if self.barreras_algas:
                dibujar_barreras_algas_escenario(self.mundo_inicio, self.barreras_algas, 0)
            if self.flechas_indicadoras:
                dibujar_flechas_indicadoras_escenario(self.mundo_inicio, self.flechas_indicadoras, 0)
            if self.corales_decorativos:
                dibujar_corales_escenario(self.mundo_inicio, self.corales_decorativos, 0)
            if self.algas_decorativas:
                dibujar_algas_decorativas_escenario(self.mundo_inicio, self.algas_decorativas, 0, capa="frente")
            if self.pinchos:
                dibujar_peligros_marinos_escenario(self.mundo_inicio, self.pinchos)
            if self.burbujas_m3:
                actualizar_y_dibujar_burbujas_m3(self.mundo_inicio, self.burbujas_m3, [self.jugador1, self.jugador2], 0)
        elif self.numero_mundo == 1:
            dibujar_fondo_mundo1_invierno(self.mundo_inicio, self.ancho_mundo_nivel)
            dibujar_decoraciones_mundo1(self.mundo_inicio, self.suelo, self.ancho_mundo_nivel, 0)
            self.plats_dibujar_ini = self.plataformas_base if (self.paredes_colores is not None and self.plataformas_base is not None) else self.plataformas
            self.plats_estaticas_ini = [p for p in self.plats_dibujar_ini if not (
                (self.barrera_l_horiz is not None and (p is self.barrera_l_horiz or p is self.barrera_l_vert)) or
                (self.bloque_central is not None and p is self.bloque_central["rect"]) or
                (self.plataforma_movil is not None and p is self.plataforma_movil["rect"]) or
                (self.compuerta is not None and p is self.compuerta["rect"]) or
                (self.plataformas_derrumbables is not None and any(p is p_d["rect"] for p_d in self.plataformas_derrumbables))
            )]
            dibujar_escenario_mundo1(self.mundo_inicio, self.suelo, self.plats_estaticas_ini, self.pozo_nivel)
            if self.barrera_l_horiz is not None and self.barrera_l_vert is not None:
                dibujar_barrera_l_escenario(self.mundo_inicio, self.barrera_l_horiz, self.barrera_l_vert)
            if self.pinchos:
                dibujar_pinchos_escenario(self.mundo_inicio, self.pinchos)
            actualizar_y_dibujar_nieve_mundo1(self.mundo_inicio, self.ancho_mundo_nivel, 0)
        elif self.numero_mundo == 2:
            dibujar_fondo_mundo2_ruinas(self.mundo_inicio, self.ancho_mundo_nivel)
            dibujar_decoraciones_mundo2(self.mundo_inicio, self.suelo, self.ancho_mundo_nivel, 0, self.pozo_nivel)
            self.plats_dibujar_ini = self.plataformas_base if (self.paredes_colores is not None and self.plataformas_base is not None) else self.plataformas
            self.plats_estaticas_ini = [p for p in self.plats_dibujar_ini if not (
                (self.barrera_l_horiz is not None and (p is self.barrera_l_horiz or p is self.barrera_l_vert)) or
                (self.bloque_central is not None and p is self.bloque_central["rect"]) or
                (self.plataforma_movil is not None and p is self.plataforma_movil["rect"]) or
                (self.compuerta is not None and p is self.compuerta["rect"]) or
                (self.plataformas_derrumbables is not None and any(p is p_d["rect"] for p_d in self.plataformas_derrumbables))
            )]
            dibujar_escenario_mundo2(self.mundo_inicio, self.suelo, self.plats_estaticas_ini, self.pozo_nivel)
            if self.barrera_l_horiz is not None and self.barrera_l_vert is not None:
                dibujar_barrera_l_escenario(self.mundo_inicio, self.barrera_l_horiz, self.barrera_l_vert)
            if self.pinchos:
                dibujar_pinchos_escenario(self.mundo_inicio, self.pinchos)
            if self.numero_nivel == 3:
                dibujar_pendulo_escenario(self.mundo_inicio, self.plataformas, self.plat_elevada, self.pozo_nivel)
            if self.numero_nivel == 4 and self.plataformas_derrumbables is not None:
                dibujar_plataformas_derrumbables_escenario(self.mundo_inicio, self.plataformas_derrumbables, self.pozo_nivel)
            if self.numero_nivel == 5 and self.plataformas_alternadas is not None:
                dibujar_plataformas_alternadas_escenario(self.mundo_inicio, self.plataformas_alternadas, self.pozo_nivel)
            actualizar_y_dibujar_polvo_mundo2(self.mundo_inicio, self.ancho_mundo_nivel, 0)
        else:
            self.mundo_inicio.fill((255, 240, 195))

            if self.pozo_nivel is not None:
                self.pz = self.pozo_nivel
                pygame.draw.rect(self.mundo_inicio, (235, 222, 192), (self.pz["x"], self.pz["y"], self.pz["ancho"], self.pz["alto"]))
                pygame.draw.line(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, (self.pz["x"], self.pz["y"]), (self.pz["x"], self.pz["y"] + self.pz["alto"]), 2)
                pygame.draw.line(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, (self.pz["x"] + self.pz["ancho"], self.pz["y"]), (self.pz["x"] + self.pz["ancho"], self.pz["y"] + self.pz["alto"]), 2)

            for self.plat in self.plataformas:
                if self.barrera_l_horiz is not None and (self.plat is self.barrera_l_horiz or self.plat is self.barrera_l_vert):
                    continue
                if self.bloque_central is not None and self.plat is self.bloque_central["rect"]:
                    continue
                if self.plataforma_movil is not None and self.plat is self.plataforma_movil["rect"]:
                    continue
                if self.compuerta is not None and self.plat is self.compuerta["rect"]:
                    continue
                if self.plataformas_derrumbables is not None and any(self.plat is p_d["rect"] for p_d in self.plataformas_derrumbables):
                    continue
                if self.plat.bottom >= self.suelo.top:
                    self.rect_torre = pygame.Rect(self.plat.x, self.plat.y, self.plat.width, self.plat.height + 4)
                    pygame.draw.rect(self.mundo_inicio, COLOR_PLATAFORMA, self.rect_torre, border_top_left_radius=4, border_top_right_radius=4)
                    pygame.draw.rect(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, self.rect_torre, width=2, border_top_left_radius=4, border_top_right_radius=4)
                else:
                    pygame.draw.rect(self.mundo_inicio, COLOR_PLATAFORMA, self.plat, border_radius=4)
                    pygame.draw.rect(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, self.plat, width=2, border_radius=4)

            if self.barrera_l_horiz is not None and self.barrera_l_vert is not None:
                dibujar_barrera_l_escenario(self.mundo_inicio, self.barrera_l_horiz, self.barrera_l_vert)

            pygame.draw.rect(self.mundo_inicio, (225, 110, 80), self.suelo)
            if self.pozo_nivel is not None:
                pygame.draw.line(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, (self.pz["x"], self.pz["y"] + self.pz["alto"]), (self.pz["x"] + self.pz["ancho"], self.pz["y"] + self.pz["alto"]), 2)

            if self.pinchos:
                dibujar_pinchos_escenario(self.mundo_inicio, self.pinchos)
            if self.numero_mundo == 2 and self.numero_nivel == 3:
                dibujar_pendulo_escenario(self.mundo_inicio, self.plataformas, self.plat_elevada, self.pozo_nivel)
            if self.numero_mundo == 2 and self.numero_nivel == 4 and self.plataformas_derrumbables is not None:
                dibujar_plataformas_derrumbables_escenario(self.mundo_inicio, self.plataformas_derrumbables, self.pozo_nivel)
            if self.numero_mundo == 2 and self.numero_nivel == 5 and self.plataformas_alternadas is not None:
                dibujar_plataformas_alternadas_escenario(self.mundo_inicio, self.plataformas_alternadas, self.pozo_nivel)

        if self.boton_nivel is not None:
            self.rect_b = self.boton_nivel["rect"]
            self.h_actual = 4 if self.boton_nivel["presionado"] else 12
            self.y_actual = self.suelo.top - self.h_actual
            pygame.draw.rect(self.mundo_inicio, (90, 70, 60), (self.rect_b.left - 6, self.suelo.top - 4, self.rect_b.width + 12, 10), border_radius=2)
            self.col_btn = (80, 200, 100) if self.boton_nivel["presionado"] else (225, 65, 65)
            self.col_borde_btn = (50, 150, 70) if self.boton_nivel["presionado"] else (175, 45, 45)
            pygame.draw.rect(self.mundo_inicio, self.col_btn, (self.rect_b.x, self.y_actual, self.rect_b.width, self.h_actual), border_top_left_radius=3, border_top_right_radius=3)
            pygame.draw.rect(self.mundo_inicio, self.col_borde_btn, (self.rect_b.x, self.y_actual, self.rect_b.width, self.h_actual), width=2, border_top_left_radius=3, border_top_right_radius=3)

        if self.pared_nivel is not None:
            self.pr = self.pared_nivel["rect"]
            for self.y_linea in range(self.pr.top + 30, self.pr.bottom - 10, 35):
                if 0 <= self.y_linea <= ALTO:
                    pygame.draw.line(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, (self.pr.left + 4, self.y_linea), (self.pr.right - 4, self.y_linea), 2)

        if self.laser_nivel is not None:
            dibujar_laser_escenario(self.mundo_inicio, self.laser_nivel)

        if self.paredes_colores is not None:
            dibujar_paredes_colores_escenario(self.mundo_inicio, self.paredes_colores)

        if self.botones_colores is not None:
            dibujar_botones_colores_escenario(self.mundo_inicio, self.botones_colores, self.suelo)

        if self.boton_compuerta is not None:
            self.rect_bc = self.boton_compuerta["rect"]
            self.h_bc = 4 if self.boton_compuerta["presionado"] else 12
            self.y_bc = self.suelo.top - self.h_bc
            pygame.draw.rect(self.mundo_inicio, (90, 70, 60), (self.rect_bc.left - 6, self.suelo.top - 4, self.rect_bc.width + 12, 10), border_radius=2)
            self.col_bc = (220, 200, 60) if self.boton_compuerta["presionado"] else (245, 175, 40)
            self.col_borde_bc = (160, 140, 30) if self.boton_compuerta["presionado"] else (180, 120, 20)
            pygame.draw.rect(self.mundo_inicio, self.col_bc, (self.rect_bc.x, self.y_bc, self.rect_bc.width, self.h_bc), border_top_left_radius=3, border_top_right_radius=3)
            pygame.draw.rect(self.mundo_inicio, self.col_borde_bc, (self.rect_bc.x, self.y_bc, self.rect_bc.width, self.h_bc), width=2, border_top_left_radius=3, border_top_right_radius=3)

        if self.compuerta is not None and self.compuerta["rect"].width > 0:
            self.cr = self.compuerta["rect"]
            pygame.draw.rect(self.mundo_inicio, COLOR_PLATAFORMA, self.cr, border_radius=3)
            pygame.draw.rect(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, self.cr, width=2, border_radius=3)
            for self.lx in range(self.cr.left + 12, self.cr.right - 8, 16):
                pygame.draw.line(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, (self.lx, self.cr.top + 3), (self.lx, self.cr.bottom - 4), 2)

        if self.bloque_central is not None:
            self.br = self.bloque_central["rect"]
            pygame.draw.line(self.mundo_inicio, (110, 100, 95), (self.br.left + 12, 0), (self.br.left + 12, self.br.top), 3)
            pygame.draw.line(self.mundo_inicio, (110, 100, 95), (self.br.right - 12, 0), (self.br.right - 12, self.br.top), 3)
            pygame.draw.circle(self.mundo_inicio, (70, 65, 60), (self.br.left + 12, self.br.top), 4)
            pygame.draw.circle(self.mundo_inicio, (70, 65, 60), (self.br.right - 12, self.br.top), 4)
            pygame.draw.rect(self.mundo_inicio, (220, 50, 50), self.br, border_radius=4)
            pygame.draw.rect(self.mundo_inicio, (140, 25, 25), self.br, width=2, border_radius=4)
            for self.by in range(self.br.top + 16, self.br.bottom - 8, 16):
                pygame.draw.line(self.mundo_inicio, (160, 30, 30), (self.br.left + 4, self.by), (self.br.right - 4, self.by), 2)

        if self.plataforma_movil is not None:
            self.pm = self.plataforma_movil["rect"]
            pygame.draw.rect(self.mundo_inicio, COLOR_PLATAFORMA, self.pm, border_radius=4)
            pygame.draw.rect(self.mundo_inicio, COLOR_BORDE_PLATAFORMA, self.pm, width=2, border_radius=4)
            for self.rx in range(self.pm.left + 15, self.pm.right - 10, 22):
                pygame.draw.circle(self.mundo_inicio, (140, 60, 40), (self.rx, self.pm.bottom - 5), 3)
            self.col_ind = (80, 220, 100) if self.plataforma_movil["moviendo"] else ((240, 180, 40) if self.plataforma_movil["tiempo_con_peso"] > 0 else (180, 80, 55))
            pygame.draw.circle(self.mundo_inicio, self.col_ind, (self.pm.centerx, self.pm.centery), 4)

        if self.usar_agua:
            dibujar_agua(self.mundo_inicio, ZONA_AGUA)
        if self.usar_soga and not self.p1_completado and not self.p2_completado:
            dibujar_soga_escenario(self.mundo_inicio, self.jugador1, self.jugador2, self.estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        if self.usar_caja:
            self.mundo_inicio.blit(self.caja["sprite"], self.caja["rect"])

        if self.usar_llave and self.puerta:
            actualizar_puerta(self.puerta)
            self.estado_p = "cerrada"
            self.mundo_inicio.blit(self.puerta["sprites"][self.estado_p], self.puerta["rect"])
            if self.llave:
                if self.numero_mundo == 3:
                    self.halo_surf = pygame.Surface((44, 60), pygame.SRCALPHA)
                    pygame.draw.ellipse(self.halo_surf, (255, 230, 90, 75), (0, 0, 44, 60))
                    self.mundo_inicio.blit(self.halo_surf, (self.llave["rect"].centerx - 22, self.llave["rect"].centery - 30))
                self.mundo_inicio.blit(self.llave["sprite"], self.llave["rect"])

        if self.numero_mundo == 3 and self.numero_nivel in (4, 5) and self.surf_oscuridad_m3 is not None:
            aplicar_oscuridad_submarina(
                self.mundo_inicio,
                [(self.jugador1, self.linterna_p1, False), (self.jugador2, self.linterna_p2, False)],
                self.surf_oscuridad_m3,
                self.surf_luz_linterna,
                self.surf_luz_tenue
            )
            dibujar_personaje(self.mundo_inicio, self.jugador1, ZONA_AGUA if self.usar_agua else None)
            dibujar_linterna_minero(self.mundo_inicio, self.jugador1, self.linterna_p1)
            dibujar_personaje(self.mundo_inicio, self.jugador2, ZONA_AGUA if self.usar_agua else None)
            dibujar_linterna_minero(self.mundo_inicio, self.jugador2, self.linterna_p2)
        else:
            dibujar_personaje(self.mundo_inicio, self.jugador1, ZONA_AGUA if self.usar_agua else None)
            dibujar_personaje(self.mundo_inicio, self.jugador2, ZONA_AGUA if self.usar_agua else None)

        self.distancia_ini = abs(self.jugador1["hitbox"].centerx - self.jugador2["hitbox"].centerx)
        if self.distancia_ini <= DISTANCIA_SPLIT:
            self.centro_ini = (self.jugador1["hitbox"].centerx + self.jugador2["hitbox"].centerx) // 2
            self.cam_ini_x = max(0, min(self.centro_ini - ANCHO // 2, self.ancho_mundo_nivel - ANCHO))
            self.pantalla.blit(self.mundo_inicio, (0, 0), pygame.Rect(self.cam_ini_x, 0, ANCHO, ALTO))
        else:
            self.ancho_m = ANCHO // 2
            self.p_izq = self.jugador1 if self.jugador1["hitbox"].centerx <= self.jugador2["hitbox"].centerx else self.jugador2
            self.p_der = self.jugador2 if self.p_izq is self.jugador1 else self.jugador1
            self.cam_izq_x = max(0, min(self.p_izq["hitbox"].centerx - self.ancho_m // 2, self.ancho_mundo_nivel - self.ancho_m))
            self.cam_der_x = max(0, min(self.p_der["hitbox"].centerx - self.ancho_m // 2, self.ancho_mundo_nivel - self.ancho_m))
            self.pantalla.blit(self.mundo_inicio, (0, 0), pygame.Rect(self.cam_izq_x, 0, self.ancho_m, ALTO))
            self.pantalla.blit(self.mundo_inicio, (self.ancho_m, 0), pygame.Rect(self.cam_der_x, 0, self.ancho_m, ALTO))
            pygame.draw.line(self.pantalla, (0, 0, 0), (self.ancho_m, 0), (self.ancho_m, ALTO), 4)

        self.fondo_btn_config = self.pantalla.subsurface(self.rect_btn_config).copy()
        self.fondo_btn_casa = self.pantalla.subsurface(self.rect_btn_casa).copy()
        self.fondo_btn_reiniciar = self.pantalla.subsurface(self.rect_btn_reiniciar).copy()
        self.fondo_btn_x = self.pantalla.subsurface(self.rect_btn_x).copy()

        if self.spr_config_normal: self.pantalla.blit(self.spr_config_normal, self.rect_btn_config)
        if self.spr_casa_normal: self.pantalla.blit(self.spr_casa_normal, self.rect_btn_casa)
        if self.spr_reiniciar_normal: self.pantalla.blit(self.spr_reiniciar_normal, self.rect_btn_reiniciar)
        if self.spr_x_normal: self.pantalla.blit(self.spr_x_normal, self.rect_btn_x)

        self.captura_nuevo_nivel = self.pantalla.copy()
        animar_apertura_franjas(self.pantalla, self.reloj, self.captura_nuevo_nivel)

        self.jugador1["accesorio"] = self.p1_acc
        self.jugador2["accesorio"] = self.p2_acc
        self.jugador1["equipo_buceo"] = (self.numero_mundo == 3)
        self.jugador2["equipo_buceo"] = (self.numero_mundo == 3)

        def _reiniciar_nivel_completo():
            pass  # (antes: nonlocal; ahora son atributos del estado del nivel)
            pass  # (antes: nonlocal; ahora son atributos del estado del nivel)
            pass  # (antes: nonlocal; ahora son atributos del estado del nivel)
            pass  # (antes: nonlocal; ahora son atributos del estado del nivel)

            reiniciar_juego(self.jugador1, self.jugador2, self.caja, self.llave, self.puerta, estado_soga=self.estado_soga)
            self.jugador1["accesorio"] = self.p1_acc
            self.jugador2["accesorio"] = self.p2_acc
            self.jugador1["equipo_buceo"] = (self.numero_mundo == 3)
            self.jugador2["equipo_buceo"] = (self.numero_mundo == 3)
            if self.boton_nivel is not None and self.pared_nivel is not None:
                self.boton_nivel["presionado"] = False
                self.pared_nivel["progreso"] = 0.0
                self.pared_nivel["y"] = self.pared_nivel["y_cerrada"]
                self.pared_nivel["rect"].y = int(self.pared_nivel["y_cerrada"])
            if self.laser_nivel is not None:
                self.laser_nivel["bloqueado"] = False
                pared_x = self.laser_nivel.get("pared_der_x", 1100)
                self.laser_nivel["x_fin"] = pared_x
                self.laser_nivel["rect_dano"].x = self.laser_nivel["emisor_rect"].right
                self.laser_nivel["rect_dano"].width = max(0, pared_x - self.laser_nivel["emisor_rect"].right)
            if self.botones_colores is not None and self.paredes_colores is not None:
                for btn in self.botones_colores:
                    btn["presionado"] = False
                for pared in self.paredes_colores:
                    pared["progreso"] = 0.0
                    pared["rect"].y = int(pared["y_cerrada"])
            if self.boton_compuerta is not None and self.compuerta is not None:
                self.boton_compuerta["presionado"] = False
                self.compuerta["progreso"] = 0.0
                self.compuerta["rect"].x = 1700
                self.compuerta["rect"].width = 140
            if self.plataforma_movil is not None:
                self.plataforma_movil["x"] = self.plataforma_movil["x_inicial"]
                self.plataforma_movil["rect"].x = int(self.plataforma_movil["x_inicial"])
                self.plataforma_movil["tiempo_con_peso"] = 0
                self.plataforma_movil["tiempo_espera_retorno"] = 0
                self.plataforma_movil["estado"] = "esperando_inicio"
                self.plataforma_movil["moviendo"] = False
                self.plataforma_movil["llegada"] = False

            if self.plataformas_base is not None:
                self.plataformas = list(self.plataformas_base)
                if self.paredes_colores is not None:
                    self.plataformas.extend([p["rect"] for p in self.paredes_colores])
                if self.compuerta is not None and self.compuerta["rect"].width > 0:
                    self.plataformas.append(self.compuerta["rect"])
                if self.plataforma_movil is not None:
                    self.plataformas.append(self.plataforma_movil["rect"])
                if self.plataformas_derrumbables is not None:
                    self.plataformas.extend([p_d["rect"] for p_d in self.plataformas_derrumbables])
                if self.plataformas_alternadas is not None:
                    self.plataformas.extend(self.plataformas_alternadas)

            if self.plataformas_derrumbables is not None:
                for p_d in self.plataformas_derrumbables:
                    p_d["rect"].x = p_d["x_inicial"]
                    p_d["rect"].y = p_d["y_inicial"]
                    p_d["y"] = float(p_d["y_inicial"])
                    p_d["vel_y"] = 0.0
                    p_d["estado"] = "intacta"
                    p_d["pisada"] = False
                    p_d["tiempo_restante"] = 60
                    p_d["particulas"].clear()

            self.p1_completado, self.p2_completado = False, False
            self.mostrar_tutorial = (self.numero_mundo == 1 and self.numero_nivel == 1)
            self.contador_tutorial = 0
            self.p1_movio = False
            self.p2_movio = False
            self.alpha_tut_p1 = 255.0
            self.alpha_tut_p2 = 255.0
            self.p1_soplado = False
            self.p2_soplado = False
            self.teclas_sopladas.clear()
            self.lineas_viento.clear()

            if self.numero_mundo == 3 and self.numero_nivel == 1:
                self.jugador1["en_agua"] = True
                self.jugador2["en_agua"] = True
                if self.burbujas_m3:
                    self.burbujas_m3[:] = crear_sistema_burbujas_m3(self.ancho_mundo_nivel, cantidad=45)

            if self.numero_mundo == 3 and self.numero_nivel == 2:
                datos_lab = generar_laberinto_coral_m3_n2(self.ancho_mundo_nivel, ALTO, self.suelo.top, self.techo_agua.bottom)
                self.rocas_submarinas = datos_lab["rocas"]
                self.barreras_algas = datos_lab["barreras"]
                self.corales_decorativos = datos_lab["corales"]
                self.algas_decorativas = datos_lab["algas"]
                self.plataformas_base = [self.techo_agua] + [r["rect"] for r in self.rocas_submarinas] + [b["rect"] for b in self.barreras_algas]
                self.plataformas = list(self.plataformas_base)
                self.llave["x_inicial"] = datos_lab["llave_x"]
                self.llave["y_inicial"] = datos_lab["llave_y"]
                self.llave["x_float"] = float(datos_lab["llave_x"])
                self.llave["y_float"] = float(datos_lab["llave_y"])
                self.llave["rect"].x = datos_lab["llave_x"]
                self.llave["rect"].y = datos_lab["llave_y"]
                self.llave["recolectada"] = False
                self.llave["portador"] = None
                self.puerta["abierta"] = False
                self.jugador1["x_inicial"] = datos_lab["p1_x"]
                self.jugador1["y_inicial"] = datos_lab["p1_y"]
                self.jugador1["hitbox"].x = datos_lab["p1_x"]
                self.jugador1["hitbox"].y = datos_lab["p1_y"]
                self.jugador1["vel_x"] = 0
                self.jugador1["vel_y"] = 0
                self.jugador1["en_agua"] = True
                self.jugador2["x_inicial"] = datos_lab["p2_x"]
                self.jugador2["y_inicial"] = datos_lab["p2_y"]
                self.jugador2["hitbox"].x = datos_lab["p2_x"]
                self.jugador2["hitbox"].y = datos_lab["p2_y"]
                self.jugador2["vel_x"] = 0
                self.jugador2["vel_y"] = 0
                self.jugador2["en_agua"] = True
                if self.burbujas_m3:
                    self.burbujas_m3[:] = crear_sistema_burbujas_m3(self.ancho_mundo_nivel, cantidad=50)

            if self.numero_mundo == 3 and self.numero_nivel == 3:
                self.jugador1["en_agua"] = True
                self.jugador2["en_agua"] = True
                if self.burbujas_m3:
                    self.burbujas_m3[:] = crear_sistema_burbujas_m3(self.ancho_mundo_nivel, cantidad=45)

            if self.numero_mundo == 3 and self.numero_nivel == 4:
                self.linterna_p1 = True
                self.linterna_p2 = True
                datos_lab = generar_laberinto_oscuro_m3_n4(self.ancho_mundo_nivel, ALTO, self.suelo.top, self.techo_agua.bottom)
                self.rocas_submarinas = datos_lab["rocas"]
                self.barreras_algas = datos_lab["barreras"]
                self.corales_decorativos = datos_lab["corales"]
                self.algas_decorativas = datos_lab["algas"]
                self.pinchos = datos_lab["pinchos"]
                self.flechas_indicadoras = datos_lab.get("flechas", [])
                self.plataformas_base = [self.techo_agua] + [r["rect"] for r in self.rocas_submarinas] + [b["rect"] for b in self.barreras_algas]
                self.plataformas = list(self.plataformas_base)
                self.llave["x_inicial"] = datos_lab["llave_x"]
                self.llave["y_inicial"] = datos_lab["llave_y"]
                self.llave["x_float"] = float(datos_lab["llave_x"])
                self.llave["y_float"] = float(datos_lab["llave_y"])
                self.llave["rect"].x = datos_lab["llave_x"]
                self.llave["rect"].y = datos_lab["llave_y"]
                self.llave["recolectada"] = False
                self.llave["portador"] = None
                self.puerta["abierta"] = False
                self.jugador1["x_inicial"] = datos_lab["p1_x"]
                self.jugador1["y_inicial"] = datos_lab["p1_y"]
                self.jugador1["hitbox"].x = datos_lab["p1_x"]
                self.jugador1["hitbox"].y = datos_lab["p1_y"]
                self.jugador1["vel_x"] = 0
                self.jugador1["vel_y"] = 0
                self.jugador1["en_agua"] = True
                self.jugador2["x_inicial"] = datos_lab["p2_x"]
                self.jugador2["y_inicial"] = datos_lab["p2_y"]
                self.jugador2["hitbox"].x = datos_lab["p2_x"]
                self.jugador2["hitbox"].y = datos_lab["p2_y"]
                self.jugador2["vel_x"] = 0
                self.jugador2["vel_y"] = 0
                self.jugador2["en_agua"] = True
                if self.burbujas_m3:
                    self.burbujas_m3[:] = crear_sistema_burbujas_m3(self.ancho_mundo_nivel, cantidad=45)

            if self.numero_mundo == 3 and self.numero_nivel in (5, 6):
                self.linterna_p1 = True
                self.linterna_p2 = True
                self.oxigeno_p1 = 100.0
                self.oxigeno_p2 = 100.0
                self.jugador1["en_agua"] = True
                self.jugador2["en_agua"] = True
                detener_sonido_ahogamiento()
                if self.burbujas_m3:
                    self.burbujas_m3[:] = crear_sistema_burbujas_m3(self.ancho_mundo_nivel, cantidad=45)
        self._reiniciar_nivel_completo = _reiniciar_nivel_completo

        self.mundo = pygame.Surface((self.ancho_mundo_nivel, ALTO)).convert()
        self.ejecutando = True



def _procesar_eventos(n):
    """Eventos de teclado y botones del HUD. Devuelve un resultado ('menu', 'salir') para terminar el nivel, o None."""
    for n.evento in pygame.event.get():
        if n.evento.type == pygame.QUIT:
            if hay_progreso_sin_guardar(n.niveles_desbloqueados, n.snapshot_guardado, id_partida=n.partida_id):
                n.resp = mostrar_dialogo_guardar_salir(
                    n.pantalla, n.reloj,
                    niveles_desbloqueados=n.niveles_desbloqueados,
                    id_partida=n.partida_id,
                    nombre_partida=n.partida_nombre,
                    password_partida=n.partida_password,
                    color_p1=n.color_p1,
                    color_p2=n.color_p2,
                    accesorio_p1=n.p1_acc,
                    accesorio_p2=n.p2_acc,
                )
                if n.resp in ("guardar_salir", "salir_sin_guardar"):
                    pygame.quit()
                    sys.exit()
            else:
                pygame.quit()
                sys.exit()

        if n.evento.type == pygame.KEYDOWN:
            if n.evento.key == pygame.K_r:
                if n.spr_reiniciar_semi and n.spr_reiniciar_apretado:
                    n.f_limpio = n.fondo_btn_reiniciar if n.fondo_btn_reiniciar else (255, 240, 195)
                    animar_pulsacion_boton(n.pantalla, n.rect_btn_reiniciar, n.spr_reiniciar_semi, n.spr_reiniciar_apretado, n.f_limpio, tipo_sonido="ventana_reiniciar")
                n._reiniciar_nivel_completo()
            elif n.numero_mundo == 3 and n.numero_nivel in (4, 5):
                if n.evento.key in (pygame.K_e, pygame.K_f, pygame.K_SPACE):
                    if not n.jugador1.get("muerto", False):
                        n.linterna_p1 = not n.linterna_p1
                elif n.evento.key in (pygame.K_l, pygame.K_RETURN, pygame.K_RSHIFT, pygame.K_RCTRL):
                    if not n.jugador2.get("muerto", False):
                        n.linterna_p2 = not n.linterna_p2

        if n.evento.type == pygame.MOUSEBUTTONDOWN and n.evento.button == 1:
            if n.rect_btn_x.collidepoint(n.evento.pos):
                n.f_limpio = n.fondo_btn_x if n.fondo_btn_x else (255, 240, 195)
                if animar_pulsacion_boton(n.pantalla, n.rect_btn_x, n.spr_x_semi, n.spr_x_apretado, n.f_limpio, n.spr_x_normal, tipo_sonido="ventana_cancelar"):
                    if hay_progreso_sin_guardar(n.niveles_desbloqueados, n.snapshot_guardado, id_partida=n.partida_id):
                        n.resp = mostrar_dialogo_guardar_salir(
                            n.pantalla, n.reloj,
                            niveles_desbloqueados=n.niveles_desbloqueados,
                            id_partida=n.partida_id,
                            nombre_partida=n.partida_nombre,
                            password_partida=n.partida_password,
                            color_p1=n.color_p1,
                            color_p2=n.color_p2,
                            accesorio_p1=n.p1_acc,
                            accesorio_p2=n.p2_acc,
                        )
                        if n.resp in ("guardar_salir", "salir_sin_guardar"):
                            pygame.quit()
                            sys.exit()
                    else:
                        pygame.quit()
                        sys.exit()

            if n.rect_btn_reiniciar.collidepoint(n.evento.pos):
                n.f_limpio = n.fondo_btn_reiniciar if n.fondo_btn_reiniciar else (255, 240, 195)
                if animar_pulsacion_boton(n.pantalla, n.rect_btn_reiniciar, n.spr_reiniciar_semi, n.spr_reiniciar_apretado, n.f_limpio, n.spr_reiniciar_normal, tipo_sonido="ventana_reiniciar"):
                    n._reiniciar_nivel_completo()

            if n.rect_btn_casa.collidepoint(n.evento.pos):
                n.f_limpio = n.fondo_btn_casa if n.fondo_btn_casa else (255, 240, 195)
                if animar_pulsacion_boton(n.pantalla, n.rect_btn_casa, n.spr_casa_semi, n.spr_casa_apretado, n.f_limpio, n.spr_casa_normal, tipo_sonido="ventana_volver"):
                    return "menu"

            if n.rect_btn_config.collidepoint(n.evento.pos):
                n.f_limpio = n.fondo_btn_config if n.fondo_btn_config else (255, 240, 195)
                if animar_pulsacion_boton(n.pantalla, n.rect_btn_config, n.spr_config_semi, n.spr_config_apretado, n.f_limpio, n.spr_config_normal, tipo_sonido="menu"):
                    mostrar_pestana_configuracion(n.pantalla, n.reloj)


def _actualizar_jugadores(n):
    """Entrada de los jugadores, tutorial, movimiento, soga y agua."""
    n.teclas = pygame.key.get_pressed()

    salto_p1_pedido = n.teclas[pygame.K_w] and (puede_saltar(n.jugador1) if n.usar_agua else n.jugador1["en_suelo"])
    salto_p2_pedido = n.teclas[pygame.K_UP] and (puede_saltar(n.jugador2) if n.usar_agua else n.jugador2["en_suelo"])

    if n.mostrar_tutorial:
        n.contador_tutorial += 1

        # Detectar si Jugador 1 se mueve (WASD o salto)
        if not n.p1_movio and not n.p1_completado and not n.jugador1["muerto"]:
            if (
                n.teclas[pygame.K_a] or n.teclas[pygame.K_d] or salto_p1_pedido
                or (n.usar_agua and (n.teclas[pygame.K_w] or n.teclas[pygame.K_s]))
                or n.jugador1["moviendo"]
            ):
                n.p1_movio = True

        # Detectar si Jugador 2 se mueve (Flechas o salto)
        if not n.p2_movio and not n.p2_completado and not n.jugador2["muerto"]:
            if (
                n.teclas[pygame.K_LEFT] or n.teclas[pygame.K_RIGHT] or salto_p2_pedido
                or (n.usar_agua and (n.teclas[pygame.K_UP] or n.teclas[pygame.K_DOWN]))
                or n.jugador2["moviendo"]
            ):
                n.p2_movio = True

        # Desvanecer los controles de P1 al moverse o soplado
        if n.p1_soplado:
            n.alpha_tut_p1 = 0.0
        elif n.p1_movio:
            n.alpha_tut_p1 = max(0.0, n.alpha_tut_p1 - 25.0)

        # Desvanecer los controles de P2 al moverse o soplado
        if n.p2_soplado:
            n.alpha_tut_p2 = 0.0
        elif n.p2_movio:
            n.alpha_tut_p2 = max(0.0, n.alpha_tut_p2 - 25.0)

        if n.alpha_tut_p1 <= 0 and n.alpha_tut_p2 <= 0 and not n.teclas_sopladas and not n.lineas_viento:
            n.mostrar_tutorial = False

    n.p1_sobre_p2 = (
        not n.p1_completado and not n.p2_completado and not n.jugador1["muerto"] and not n.jugador2["muerto"]
        and abs(n.jugador1["hitbox"].bottom - n.jugador2["hitbox"].top) <= 8
        and n.jugador1["hitbox"].right > n.jugador2["hitbox"].left + 2
        and n.jugador1["hitbox"].left < n.jugador2["hitbox"].right - 2
    )
    n.p2_sobre_p1 = (
        not n.p1_completado and not n.p2_completado and not n.jugador1["muerto"] and not n.jugador2["muerto"]
        and abs(n.jugador2["hitbox"].bottom - n.jugador1["hitbox"].top) <= 8
        and n.jugador2["hitbox"].right > n.jugador1["hitbox"].left + 2
        and n.jugador2["hitbox"].left < n.jugador1["hitbox"].right - 2
    )

    # Movimiento horizontal Jugador 1 (P1: WASD)
    if not n.jugador1["muerto"] and not n.p1_completado:
        n.mover_izq_p1 = n.teclas[pygame.K_a]
        n.mover_der_p1 = n.teclas[pygame.K_d]

        if n.mover_izq_p1 and not n.mover_der_p1:
            if n.usar_soga and not n.jugador1["en_suelo"] and n.jugador2.get("en_suelo", False):
                # Suspendido en el aire: bombear impulso tangencial al péndulo
                n.jugador1["vel_x"] = max(-n.jugador1["velocidad_mov"], n.jugador1["vel_x"] - 0.45)
            else:
                n.jugador1["vel_x"] = -n.jugador1["velocidad_mov"]
            n.jugador1["moviendo"] = True
        elif n.mover_der_p1 and not n.mover_izq_p1:
            if n.usar_soga and not n.jugador1["en_suelo"] and n.jugador2.get("en_suelo", False):
                n.jugador1["vel_x"] = min(n.jugador1["velocidad_mov"], n.jugador1["vel_x"] + 0.45)
            else:
                n.jugador1["vel_x"] = n.jugador1["velocidad_mov"]
            n.jugador1["moviendo"] = True
        else:
            if n.usar_soga and not n.jugador1["en_suelo"]:
                if n.jugador2.get("en_suelo", False):
                    n.jugador1["vel_x"] *= 0.995  # Conservación natural de la inercia pendular
                else:
                    n.jugador1["vel_x"] *= 0.97
            elif n.numero_mundo == 3:
                n.jugador1["vel_x"] *= 0.82
                if abs(n.jugador1["vel_x"]) < 0.15:
                    n.jugador1["vel_x"] = 0
            else:
                n.jugador1["vel_x"] = 0
            if abs(n.jugador1["vel_x"]) < 0.15 and abs(n.jugador1.get("vel_y", 0)) < 0.3:
                n.jugador1["moviendo"] = False

        if salto_p1_pedido:
            n.impulso = 0
            if not n.usar_agua and n.p1_sobre_p2 and (salto_p2_pedido or n.jugador2["vel_y"] < 0):
                n.impulso = -4.5
            n.jugador1["vel_y"] = n.jugador1["fuerza_salto"] + n.impulso
            n.jugador1["en_suelo"] = False

    # Movimiento horizontal Jugador 2 (P2: Flechas)
    if not n.jugador2["muerto"] and not n.p2_completado:
        n.mover_izq_p2 = n.teclas[pygame.K_LEFT]
        n.mover_der_p2 = n.teclas[pygame.K_RIGHT]

        if n.mover_izq_p2 and not n.mover_der_p2:
            if n.usar_soga and not n.jugador2["en_suelo"] and n.jugador1.get("en_suelo", False):
                # Suspendido en el aire: bombear impulso tangencial al péndulo
                n.jugador2["vel_x"] = max(-n.jugador2["velocidad_mov"], n.jugador2["vel_x"] - 0.45)
            else:
                n.jugador2["vel_x"] = -n.jugador2["velocidad_mov"]
            n.jugador2["moviendo"] = True
        elif n.mover_der_p2 and not n.mover_izq_p2:
            if n.usar_soga and not n.jugador2["en_suelo"] and n.jugador1.get("en_suelo", False):
                n.jugador2["vel_x"] = min(n.jugador2["velocidad_mov"], n.jugador2["vel_x"] + 0.45)
            else:
                n.jugador2["vel_x"] = n.jugador2["velocidad_mov"]
            n.jugador2["moviendo"] = True
        else:
            if n.usar_soga and not n.jugador2["en_suelo"]:
                if n.jugador1.get("en_suelo", False):
                    n.jugador2["vel_x"] *= 0.995  # Conservación natural de la inercia pendular
                else:
                    n.jugador2["vel_x"] *= 0.97
            elif n.numero_mundo == 3:
                n.jugador2["vel_x"] *= 0.82
                if abs(n.jugador2["vel_x"]) < 0.15:
                    n.jugador2["vel_x"] = 0
            else:
                n.jugador2["vel_x"] = 0
            if abs(n.jugador2["vel_x"]) < 0.15 and abs(n.jugador2.get("vel_y", 0)) < 0.3:
                n.jugador2["moviendo"] = False

        if salto_p2_pedido:
            n.impulso = 0
            if not n.usar_agua and n.p2_sobre_p1 and (salto_p1_pedido or n.jugador1["vel_y"] < 0):
                n.impulso = -4.5
            n.jugador2["vel_y"] = n.jugador2["fuerza_salto"] + n.impulso
            n.jugador2["en_suelo"] = False

    if n.usar_soga and not n.p1_completado and not n.p2_completado:
        actualizar_fisica_soga(n.jugador1, n.jugador2, n.estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)

    if n.usar_agua:
        if not n.jugador1["muerto"]:
            actualizar_estado_agua(n.jugador1, ZONA_AGUA)
            if n.jugador1["en_agua"]:
                aplicar_fisica_agua(n.jugador1, n.teclas[pygame.K_w], n.teclas[pygame.K_s], submarino=(n.numero_mundo == 3))
        if not n.jugador2["muerto"]:
            actualizar_estado_agua(n.jugador2, ZONA_AGUA)
            if n.jugador2["en_agua"]:
                aplicar_fisica_agua(n.jugador2, n.teclas[pygame.K_UP], n.teclas[pygame.K_DOWN], submarino=(n.numero_mundo == 3))


def _actualizar_mecanicas(n):
    """Botones, paredes, compuerta, plataformas móviles y derrumbables, caja."""
    if n.boton_nivel is not None and n.pared_nivel is not None:
        n.caja_sobre_btn = (
            n.caja is not None
            and n.caja["rect"].right > n.boton_nivel["rect"].left + 15
            and n.caja["rect"].left < n.boton_nivel["rect"].right - 15
            and abs(n.caja["rect"].bottom - n.suelo.top) <= 8
        )
        n.pj_sobre_btn = any(
            not p["muerto"] and not comp
            and p["hitbox"].right > n.boton_nivel["rect"].left + 10
            and p["hitbox"].left < n.boton_nivel["rect"].right - 10
            and abs(p["hitbox"].bottom - n.suelo.top) <= 8
            for p, comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]
        )
        n.nuevo_pres_btn = (n.caja_sobre_btn or n.pj_sobre_btn)
        if n.nuevo_pres_btn and not n.boton_nivel.get("presionado", False):
            reproducir_sonido_ui("nivel_boton")
        n.boton_nivel["presionado"] = n.nuevo_pres_btn

        n.vel_pared = 0.04
        if n.boton_nivel["presionado"]:
            if n.pared_nivel["progreso"] < 1.0:
                n.pared_nivel["progreso"] = min(1.0, n.pared_nivel["progreso"] + n.vel_pared)
        else:
            if n.pared_nivel["progreso"] > 0.0:
                n.pared_nivel["progreso"] = max(0.0, n.pared_nivel["progreso"] - n.vel_pared)

        n.pared_nivel["y"] = n.pared_nivel["y_cerrada"] + (n.pared_nivel["y_abierta"] - n.pared_nivel["y_cerrada"]) * n.pared_nivel["progreso"]
        n.pared_nivel["rect"].y = int(n.pared_nivel["y"])

    if n.botones_colores is not None and n.paredes_colores is not None:
        # Comprobación continua de presión física: el botón solo está presionado
        # mientras un personaje permanezca físicamente apoyado sobre él.
        for n.btn in n.botones_colores:
            n.rb = n.btn["rect"]
            n.pj_sobre = False
            for n.p, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
                if not n.p["muerto"] and not n.comp:
                    n.hb = n.p["hitbox"]
                    if (
                        n.hb.right > n.rb.left + 8
                        and n.hb.left < n.rb.right - 8
                        and abs(n.hb.bottom - n.suelo.top) <= 8
                        and (n.p["en_suelo"] or abs(n.p["vel_y"]) <= 1.5)
                    ):
                        n.pj_sobre = True
                        break
            if n.pj_sobre and not n.btn.get("presionado", False):
                reproducir_sonido_ui("nivel_boton")
            n.btn["presionado"] = n.pj_sobre

        n.rojo_presionado = any(btn["presionado"] for btn in n.botones_colores if btn["color"] == "rojo")
        n.azul_presionado = any(btn["presionado"] for btn in n.botones_colores if btn["color"] == "azul")

        n.vel_pared = 0.05
        for n.pared in n.paredes_colores:
            n.abrir = (n.rojo_presionado if n.pared["color"] == "rojo" else n.azul_presionado)
            if n.abrir:
                if n.pared["progreso"] < 1.0:
                    n.pared["progreso"] = min(1.0, n.pared["progreso"] + n.vel_pared)
            else:
                # Protección anti-aplastamiento: si un personaje está en el espacio que ocupa la pared cerrada,
                # no reactivar la colisión ni bajar la pared directamente sobre él hasta que el espacio quede libre.
                n.rect_espacio_cerrado = pygame.Rect(n.pared["x"], int(n.pared["y_cerrada"]), n.pared["ancho"], n.pared["alto"])
                n.jugador_en_espacio = any(
                    not pj["muerto"] and not comp and pj["hitbox"].colliderect(n.rect_espacio_cerrado)
                    for pj, comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]
                )
                if not n.jugador_en_espacio:
                    if n.pared["progreso"] > 0.0:
                        n.pared["progreso"] = max(0.0, n.pared["progreso"] - n.vel_pared)

            n.y_actual = n.pared["y_cerrada"] + (n.pared["y_abierta"] - n.pared["y_cerrada"]) * n.pared["progreso"]
            n.pared["rect"].y = int(n.y_actual)

        n.paredes_solidas = []
        for n.p_col in n.paredes_colores:
            if n.p_col["progreso"] < 0.75:
                n.solapado = any(
                    not pj["muerto"] and not comp and pj["hitbox"].colliderect(n.p_col["rect"])
                    for pj, comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]
                )
                if not n.solapado:
                    n.paredes_solidas.append(n.p_col["rect"])
        n.plataformas = n.plataformas_base + n.paredes_solidas

    if n.boton_compuerta is not None:
        n.pj_sobre = False
        n.rb = n.boton_compuerta["rect"]
        for n.p, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
            if not n.comp and not n.p["muerto"]:
                n.hb = n.p["hitbox"]
                if (
                    n.hb.right > n.rb.left + 6
                    and n.hb.left < n.rb.right - 6
                    and abs(n.hb.bottom - n.suelo.top) <= 8
                    and (n.p["en_suelo"] or abs(n.p["vel_y"]) <= 1.5)
                ):
                    n.pj_sobre = True
                    break
        if n.pj_sobre and not n.boton_compuerta.get("presionado", False):
            reproducir_sonido_ui("nivel_boton")
        n.boton_compuerta["presionado"] = n.pj_sobre

    if n.compuerta is not None:
        n.vel_comp = 0.06
        if n.boton_compuerta is not None and n.boton_compuerta["presionado"]:
            if n.compuerta["progreso"] < 1.0:
                n.compuerta["progreso"] = min(1.0, n.compuerta["progreso"] + n.vel_comp)
        else:
            n.rect_espacio_hueco = pygame.Rect(1700, 460, 140, 60)
            n.jugador_en_espacio = any(
                not pj["muerto"] and not comp and pj["hitbox"].colliderect(n.rect_espacio_hueco)
                for pj, comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]
            )
            if not n.jugador_en_espacio:
                if n.compuerta["progreso"] > 0.0:
                    n.compuerta["progreso"] = max(0.0, n.compuerta["progreso"] - n.vel_comp)

        n.comp_x = 1700 + int(140 * n.compuerta["progreso"])
        n.compuerta["rect"].x = n.comp_x
        n.compuerta["rect"].width = max(0, 1840 - n.comp_x)

        if n.compuerta["progreso"] < 0.75:
            n.solapado_comp = any(
                not pj["muerto"] and not comp and pj["hitbox"].colliderect(n.compuerta["rect"])
                for pj, comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]
            )
            if not n.solapado_comp and n.compuerta["rect"].width > 0:
                if n.compuerta["rect"] not in n.plataformas:
                    n.plataformas.append(n.compuerta["rect"])

    if n.plataforma_movil is not None:
        n.pm_rect = n.plataforma_movil["rect"]
        n.pjs_sobre = []
        for n.pj, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
            if not n.comp and not n.pj["muerto"]:
                n.hb = n.pj["hitbox"]
                if (
                    n.hb.right > n.pm_rect.left + 4
                    and n.hb.left < n.pm_rect.right - 4
                    and abs(n.hb.bottom - n.pm_rect.top) <= 8
                    and (n.pj["en_suelo"] or abs(n.pj["vel_y"]) <= 2.0)
                ):
                    n.pjs_sobre.append(n.pj)

        n.estado_pm = n.plataforma_movil.get("estado", "esperando_inicio")

        if n.estado_pm == "esperando_inicio":
            if len(n.pjs_sobre) > 0:
                n.plataforma_movil["tiempo_con_peso"] += 1
                if n.plataforma_movil["tiempo_con_peso"] >= n.plataforma_movil.get("tiempo_activacion", 120):
                    n.plataforma_movil["estado"] = "avanzando"
                    n.plataforma_movil["moviendo"] = True
            else:
                n.plataforma_movil["tiempo_con_peso"] = 0

        elif n.estado_pm == "avanzando":
            n.vel = n.plataforma_movil["velocidad"]
            n.x_fin = n.plataforma_movil.get("x_fin", 1720.0)
            if n.plataforma_movil["x"] + n.vel >= n.x_fin:
                n.plataforma_movil["x"] = n.x_fin
                n.plataforma_movil["estado"] = "esperando_retorno"
                n.plataforma_movil["moviendo"] = False
                n.plataforma_movil["llegada"] = True
                n.plataforma_movil["tiempo_espera_retorno"] = 0
            else:
                n.plataforma_movil["x"] += n.vel
            n.plataforma_movil["rect"].x = int(n.plataforma_movil["x"])

        elif n.estado_pm == "esperando_retorno":
            n.plataforma_movil["moviendo"] = False
            n.plataforma_movil["tiempo_espera_retorno"] += 1
            if n.plataforma_movil["tiempo_espera_retorno"] >= n.plataforma_movil.get("tiempo_max_espera_retorno", 300):
                n.plataforma_movil["estado"] = "regresando"
                n.plataforma_movil["moviendo"] = True
                n.plataforma_movil["llegada"] = False

        elif n.estado_pm == "regresando":
            n.vel = n.plataforma_movil["velocidad"]
            n.x_ini = n.plataforma_movil["x_inicial"]
            if n.plataforma_movil["x"] - n.vel <= n.x_ini:
                n.plataforma_movil["x"] = n.x_ini
                n.plataforma_movil["estado"] = "esperando_inicio"
                n.plataforma_movil["moviendo"] = False
                n.plataforma_movil["tiempo_con_peso"] = 0
                n.plataforma_movil["tiempo_espera_retorno"] = 0
            else:
                n.plataforma_movil["x"] -= n.vel
            n.plataforma_movil["rect"].x = int(n.plataforma_movil["x"])

        # Los personajes deben tener que moverse para mantenerse sobre la plataforma
        # (No se traslada artificialmente pj["hitbox"].x += dx)

        if n.plataformas_base is not None:
            n.plataformas = list(n.plataformas_base) + [n.plataforma_movil["rect"]]

    if n.plataformas_derrumbables is not None:
        for n.p_d in n.plataformas_derrumbables:
            # 1. Detectar si un personaje vivo no completado está pisando físicamente la plataforma
            # Cada plataforma gestiona su propio temporizador de forma independiente.
            if not n.p_d["pisada"]:
                n.pjs_pisando = False
                for n.pj, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
                    if not n.comp and not n.pj["muerto"]:
                        n.hb = n.pj["hitbox"]
                        # El personaje pisa la plataforma si tiene solapamiento horizontal y sus pies
                        # contactan la cara superior (estando en suelo o aterrizando con vel_y >= 0)
                        if (
                            n.hb.right > n.p_d["rect"].left + 2
                            and n.hb.left < n.p_d["rect"].right - 2
                            and abs(n.hb.bottom - n.p_d["rect"].top) <= 8
                            and (n.pj["en_suelo"] or n.pj.get("vel_y", 0) >= 0)
                        ):
                            n.pjs_pisando = True
                            break
                if n.pjs_pisando:
                    n.p_d["pisada"] = True
                    n.p_d["tiempo_restante"] = 60  # Exactamente 1.0 segundo a 60 FPS (no se reinicia al permanecer encima)

            # 2. Descontar temporizador
            if n.p_d["pisada"] and n.p_d["tiempo_restante"] > 0:
                n.p_d["tiempo_restante"] -= 1
                if n.p_d["tiempo_restante"] <= 20:
                    n.p_d["estado"] = "temblando"
                else:
                    n.p_d["estado"] = "agrietandose"

                if n.p_d["tiempo_restante"] <= 0:
                    n.p_d["estado"] = "derrumbada"
                    # Dejar de sostener inmediatamente a los personajes sobre esta plataforma
                    for n.pj, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
                        if not n.comp and not n.pj["muerto"]:
                            n.hb = n.pj["hitbox"]
                            if (
                                n.hb.right > n.p_d["rect"].left + 2
                                and n.hb.left < n.p_d["rect"].right - 2
                                and abs(n.hb.bottom - n.p_d["rect"].top) <= 8
                            ):
                                n.pj["en_suelo"] = False
                    for n._ in range(14):
                        n.p_d["particulas"].append({
                            "x": random.uniform(n.p_d["rect"].left, n.p_d["rect"].right),
                            "y": random.uniform(n.p_d["rect"].top, n.p_d["rect"].bottom),
                            "vx": random.uniform(-2.5, 2.5),
                            "vy": random.uniform(-1.0, 3.0),
                            "tam": random.randint(3, 6),
                            "vida": random.randint(30, 50),
                        })

            # 3. Caída libre de la plataforma si se derrumbó (caída rápida)
            if n.p_d["estado"] == "derrumbada":
                n.p_d["vel_y"] += 1.5
                n.p_d["y"] += n.p_d["vel_y"]
                n.p_d["rect"].y = int(n.p_d["y"])

            # 4. Actualizar partículas existentes
            n.activas_part = []
            for n.part in n.p_d["particulas"]:
                n.part["x"] += n.part["vx"]
                n.part["y"] += n.part["vy"]
                n.part["vy"] += 0.25
                n.part["vida"] -= 1
                if n.part["vida"] > 0:
                    n.activas_part.append(n.part)
            n.p_d["particulas"] = n.activas_part

        # 5. Las plataformas activas que sostienen a los personajes son las que no se han derrumbado
        if n.plataformas_base is not None:
            n.plataformas = list(n.plataformas_base) + [p_d["rect"] for p_d in n.plataformas_derrumbables if p_d["estado"] != "derrumbada"]

    if n.usar_caja:
        actualizar_caja(n.caja, n.suelo, n.mundo_rect, n.plataformas)
        if n.numero_mundo == 1 and n.numero_nivel == 4 and n.caja is not None:
            if n.caja["rect"].left < 20:
                n.caja["rect"].left = 20


def _resolver_interacciones(n):
    """Colisiones, oxígeno, llave y puerta, pinchos, láser, caídas, muerte y entrada a la puerta."""
    if n.usar_soga and not n.p1_completado and not n.p2_completado:
        coordinar_movimiento_soga(n.jugador1, n.jugador2, DISTANCIA_SOGA_MAXIMA)

    if not n.jugador1["muerto"] and not n.p1_completado:
        resolver_colisiones(n.jugador1, n.jugador2 if not n.p2_completado and not n.jugador2["muerto"] else None, n.suelo, n.mundo_rect, n.caja if n.usar_caja else None, n.jugador1["en_agua"], n.plataformas, usar_soga=n.usar_soga, d_max=DISTANCIA_SOGA_MAXIMA)
    if not n.jugador2["muerto"] and not n.p2_completado:
        resolver_colisiones(n.jugador2, n.jugador1 if not n.p1_completado and not n.jugador1["muerto"] else None, n.suelo, n.mundo_rect, n.caja if n.usar_caja else None, n.jugador2["en_agua"], n.plataformas, usar_soga=n.usar_soga, d_max=DISTANCIA_SOGA_MAXIMA)

    if n.numero_mundo == 3 and n.numero_nivel in (5, 6):
        # 1. Empuje de corrientes marinas sobre personajes activos
        for n.p, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
            if not n.comp and not n.p["muerto"]:
                for n.corr in n.corrientes_marinas:
                    if n.p["hitbox"].colliderect(n.corr["rect"]):
                        n.p["hitbox"].x += int(n.corr["fuerza_x"])
                        n.p["hitbox"].y += int(n.corr["fuerza_y"])

        # 2. Gestión del oxígeno de Jugador 1
        if not n.p1_completado and not n.jugador1["muerto"]:
            n.en_camara_p1 = any(cam["rect"].colliderect(n.jugador1["hitbox"]) for cam in n.camaras_aire)
            if n.en_camara_p1:
                n.oxigeno_p1 = min(n.OXIGENO_MAX, n.oxigeno_p1 + 0.85)
            else:
                n.oxigeno_p1 = max(0.0, n.oxigeno_p1 - 0.082)
                if n.oxigeno_p1 <= 0.0:
                    matar_personaje(n.jugador1)
                    if n.numero_mundo != 3 and not n.jugador2["muerto"] and not n.p2_completado:
                        matar_personaje(n.jugador2)

        # 3. Gestión del oxígeno de Jugador 2
        if not n.p2_completado and not n.jugador2["muerto"]:
            n.en_camara_p2 = any(cam["rect"].colliderect(n.jugador2["hitbox"]) for cam in n.camaras_aire)
            if n.en_camara_p2:
                n.oxigeno_p2 = min(n.OXIGENO_MAX, n.oxigeno_p2 + 0.85)
            else:
                n.oxigeno_p2 = max(0.0, n.oxigeno_p2 - 0.086)
                if n.oxigeno_p2 <= 0.0:
                    matar_personaje(n.jugador2)
                    if n.numero_mundo != 3 and not n.jugador1["muerto"] and not n.p1_completado:
                        matar_personaje(n.jugador1)

        # 4. Gestión del sonido de ahogamiento (se activa cuando la barra de oxígeno entra en rojo < 25%)
        n.p1_ahogandose = (not n.p1_completado and not n.jugador1["muerto"] and n.oxigeno_p1 < 25.0)
        n.p2_ahogandose = (not n.p2_completado and not n.jugador2["muerto"] and n.oxigeno_p2 < 25.0)

        if n.p1_ahogandose or n.p2_ahogandose:
            reproducir_sonido_ahogamiento()
        else:
            detener_sonido_ahogamiento()

    if n.usar_soga and not n.p1_completado and not n.p2_completado:
        aplicar_restriccion_soga(n.jugador1, n.jugador2, DISTANCIA_SOGA_MAXIMA, n.plataformas, n.suelo, n.estado_soga)
    if n.usar_llave:
        n.personajes_activos = [p for p, comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)] if not comp and not p["muerto"]]
        actualizar_llave(n.llave, n.personajes_activos, n.puerta)
    if n.usar_pinchos:
        n.p1_toco = False
        n.p2_toco = False
        if not n.p1_completado:
            n.p1_toco = comprobar_pinchos(n.jugador1, n.pinchos)
        if not n.p2_completado:
            n.p2_toco = comprobar_pinchos(n.jugador2, n.pinchos)

        if n.numero_mundo != 3:
            if n.p1_toco and not n.jugador2["muerto"] and not n.p2_completado:
                matar_personaje(n.jugador2)
            elif n.p2_toco and not n.jugador1["muerto"] and not n.p1_completado:
                matar_personaje(n.jugador1)

    if n.laser_nivel is not None:
        n.em = n.laser_nivel["emisor_rect"]
        n.y_r = n.laser_nivel["y_rayo"]
        n.pared_x = n.laser_nivel.get("pared_der_x", 1100)
        n.x_stop = n.pared_x
        n.bloqueado = False
        if n.caja is not None:
            n.cr = n.caja["rect"]
            if n.cr.right > n.em.left and n.cr.left < n.pared_x and n.cr.top <= n.y_r <= n.cr.bottom:
                n.x_stop = max(n.em.right, n.cr.left)
                n.bloqueado = True

        n.laser_nivel["bloqueado"] = n.bloqueado
        n.laser_nivel["x_fin"] = n.x_stop
        n.laser_nivel["rect_dano"].x = n.em.right
        n.laser_nivel["rect_dano"].width = max(0, n.x_stop - n.em.right)

        for n.p, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
            if not n.comp and not n.p["muerto"]:
                if n.laser_nivel["rect_dano"].width > 0 and n.p["hitbox"].colliderect(n.laser_nivel["rect_dano"]):
                    matar_personaje(n.p)
                    if n.numero_mundo != 3:
                        n.otro = n.jugador2 if n.p is n.jugador1 else n.jugador1
                        n.comp_otro = n.p2_completado if n.p is n.jugador1 else n.p1_completado
                        if not n.comp_otro and not n.otro.get("muerto", False):
                            matar_personaje(n.otro)

    # Detección continua de muerte cuando un personaje cae o sale completamente de la pantalla o del escenario
    for n.p, n.comp, n.otro, n.comp_otro in [
        (n.jugador1, n.p1_completado, n.jugador2, n.p2_completado),
        (n.jugador2, n.p2_completado, n.jugador1, n.p1_completado),
    ]:
        if not n.comp and not n.p.get("muerto", False):
            n.hb = n.p["hitbox"]
            if n.numero_mundo == 3:
                # En Mundo 3 todos los bordes (izquierdo x=0, derecho x=ancho, techo y=0, suelo marino)
                # son límites físicos sólidos infranqueables, no zonas mortales ni abismos.
                # Tocarlos nunca causa daño ni muerte a los personajes.
                n.caida_abajo = False
                n.salida_izq = False
                n.salida_der = False
                n.salida_arriba = False
            else:
                n.caida_abajo = (n.hb.top >= ALTO)
                n.salida_izq = (n.hb.right <= 0)
                n.salida_der = (n.hb.left >= n.ancho_mundo_nivel)
                n.salida_arriba = (n.hb.bottom <= -50)

            if n.caida_abajo or n.salida_izq or n.salida_der or n.salida_arriba:
                if n.caida_abajo and n.numero_mundo != 3:
                    # Asegurar que inicie el salto de muerte desde el borde para que sea visible en pantalla
                    n.hb.top = ALTO
                matar_personaje(n.p)

                # Si el personaje que cayó portaba la llave, reubicarla en su posición inicial
                # para que el sobreviviente pueda continuar sin quedar bloqueado indefinidamente
                if n.usar_llave and n.llave and n.llave.get("recolectada", False) and n.llave.get("portador") is n.p:
                    n.llave["recolectada"] = False
                    n.llave["portador"] = None
                    n.llave["rect"].x = n.llave["x_inicial"]
                    n.llave["rect"].y = n.llave["y_inicial"]
                    n.llave["x_float"] = float(n.llave["x_inicial"])
                    n.llave["y_float"] = float(n.llave["y_inicial"])

                # Reglas por mundo:
                # - Mundos 1 y 2: muerte compartida (si uno muere, mueren ambos)
                # - Mundo 3: muerte independiente (el otro continúa con vida)
                if n.numero_mundo != 3:
                    if not n.comp_otro and not n.otro.get("muerto", False):
                        matar_personaje(n.otro)

    dur_max_muerte = 36 if n.numero_mundo == 3 else None
    actualizar_muerte(n.jugador1, duracion_max=dur_max_muerte, limites_mundo=n.mundo_rect if n.numero_mundo == 3 else None)
    actualizar_muerte(n.jugador2, duracion_max=dur_max_muerte, limites_mundo=n.mundo_rect if n.numero_mundo == 3 else None)

    # Limitar horizontalmente y techo para personajes vivos, permitiendo caída libre por el fondo
    for n.p, n.comp in [(n.jugador1, n.p1_completado), (n.jugador2, n.p2_completado)]:
        if not n.comp and not n.p.get("muerto", False):
            n.hb = n.p["hitbox"]
            if n.hb.left < 0:
                n.hb.left = 0
            elif n.hb.right > n.ancho_mundo_nivel:
                n.hb.right = n.ancho_mundo_nivel
            if n.hb.top < 0:
                n.hb.top = 0

    # Detección de interacción especial en Mundo 1 Nivel 1: soplar indicadores del personaje quieto al saltar sobre él
    if n.numero_mundo == 1 and n.numero_nivel == 1:
        n.ancho_c = 3 * n.TAM_BTN_TUT + 2 * n.GAP_BTN_TUT
        n.h_c1 = n.badge_p1.get_height() + 4 + (2 * n.TAM_BTN_TUT + n.GAP_BTN_TUT)
        n.h_c2 = n.badge_p2.get_height() + 4 + (2 * n.TAM_BTN_TUT + n.GAP_BTN_TUT)

        # Caso 1: Jugador 1 está quieto, Jugador 2 salta y atraviesa la zona de sus indicadores
        if not n.p1_movio and not n.p1_soplado and n.alpha_tut_p1 > 0 and not n.jugador1["muerto"] and not n.p1_completado:
            if not n.jugador2["muerto"] and not n.p2_completado and not n.p2_sobre_p1:
                if not n.jugador2["en_suelo"] or abs(n.jugador2["vel_y"]) > 1.0:
                    n.rect_c1 = pygame.Rect(n.jugador1["hitbox"].centerx - n.ancho_c // 2, (n.jugador1["hitbox"].top - 8) - n.h_c1, n.ancho_c, n.h_c1)
                    if n.jugador2["hitbox"].colliderect(n.rect_c1):
                        n.pasa_sobre = abs(n.jugador2["vel_x"]) > 0.3 or (n.jugador2["hitbox"].right > n.jugador1["hitbox"].left + 2 and n.jugador2["hitbox"].left < n.jugador1["hitbox"].right - 2)
                        if n.pasa_sobre:
                            n.p1_soplado = True
                            n.alpha_tut_p1 = 0.0
                            n.dir_v = 1.0 if n.jugador2["vel_x"] > 0.3 else (-1.0 if n.jugador2["vel_x"] < -0.3 else (1.0 if n.jugador2["hitbox"].centerx >= n.jugador1["hitbox"].centerx else -1.0))
                            n._crear_efecto_soplar(n.jugador1, es_p1=True, dir_viento=n.dir_v)

        # Caso 2: Jugador 2 está quieto, Jugador 1 salta y atraviesa la zona de sus indicadores
        if not n.p2_movio and not n.p2_soplado and n.alpha_tut_p2 > 0 and not n.jugador2["muerto"] and not n.p2_completado:
            if not n.jugador1["muerto"] and not n.p1_completado and not n.p1_sobre_p2:
                if not n.jugador1["en_suelo"] or abs(n.jugador1["vel_y"]) > 1.0:
                    n.rect_c2 = pygame.Rect(n.jugador2["hitbox"].centerx - n.ancho_c // 2, (n.jugador2["hitbox"].top - 8) - n.h_c2, n.ancho_c, n.h_c2)
                    if n.jugador1["hitbox"].colliderect(n.rect_c2):
                        n.pasa_sobre = abs(n.jugador1["vel_x"]) > 0.3 or (n.jugador1["hitbox"].right > n.jugador2["hitbox"].left + 2 and n.jugador1["hitbox"].left < n.jugador2["hitbox"].right - 2)
                        if n.pasa_sobre:
                            n.p2_soplado = True
                            n.alpha_tut_p2 = 0.0
                            n.dir_v = 1.0 if n.jugador1["vel_x"] > 0.3 else (-1.0 if n.jugador1["vel_x"] < -0.3 else (1.0 if n.jugador1["hitbox"].centerx >= n.jugador2["hitbox"].centerx else -1.0))
                            n._crear_efecto_soplar(n.jugador2, es_p1=False, dir_viento=n.dir_v)

    if n.puerta and n.puerta["abierta"]:
        n.rect_ent = n.puerta.get("rect_entrada", n.puerta["rect"])
        if not n.p1_completado and n.jugador1["hitbox"].colliderect(n.rect_ent):
            n.p1_completado = True
            n.jugador1["hitbox"].x = -9999
        if not n.p2_completado and n.jugador2["hitbox"].colliderect(n.rect_ent):
            n.p2_completado = True
            n.jugador2["hitbox"].x = -9999


def _dibujar_frame(n):
    """Cámara, dibujo del mundo, objetos, personajes, oscuridad y HUD; termina con el flip."""
    vistas_camara = calcular_vistas_camara(n.jugador1, n.jugador2, n.p1_completado, n.p2_completado, n.numero_mundo, n.puerta, n.ancho_mundo_nivel)
    rangos_visibles = rangos_visibles_de_vistas(vistas_camara)

    if n.numero_mundo == 3:
        n.tick_m3 += 1
        dibujar_submarino_fondo_escenario(n.mundo, n.ancho_mundo_nivel, n.tick_m3, rangos=rangos_visibles)
        blit_capa_en_rangos(n.mundo, obtener_capa_estatica_m3(
            "lecho", n.suelo, n.ancho_mundo_nivel, ALTO,
            lambda capa: dibujar_lecho_marino(capa, n.suelo, n.ancho_mundo_nivel)), rangos_visibles)
        if n.algas_decorativas:
            dibujar_algas_decorativas_escenario(n.mundo, n.algas_decorativas, n.tick_m3, capa="fondo")
        if n.corrientes_marinas:
            dibujar_corrientes_marinas_escenario(n.mundo, n.corrientes_marinas, n.tick_m3)
        if n.camaras_aire:
            dibujar_camaras_aire_escenario(n.mundo, n.camaras_aire, n.tick_m3)
        if n.rocas_submarinas:
            blit_capa_en_rangos(n.mundo, obtener_capa_estatica_m3(
                "rocas", n.rocas_submarinas, n.ancho_mundo_nivel, ALTO,
                lambda capa: dibujar_rocas_submarinas_escenario(capa, n.rocas_submarinas)), rangos_visibles)
        if n.barreras_algas:
            dibujar_barreras_algas_escenario(n.mundo, n.barreras_algas, n.tick_m3)
        if n.flechas_indicadoras:
            dibujar_flechas_indicadoras_escenario(n.mundo, n.flechas_indicadoras, n.tick_m3)
        if n.corales_decorativos:
            dibujar_corales_escenario(n.mundo, n.corales_decorativos, n.tick_m3)
        if n.algas_decorativas:
            dibujar_algas_decorativas_escenario(n.mundo, n.algas_decorativas, n.tick_m3, capa="frente")
        if n.pinchos:
            blit_capa_en_rangos(n.mundo, obtener_capa_estatica_m3(
                "erizos", n.pinchos, n.ancho_mundo_nivel, ALTO,
                lambda capa: dibujar_peligros_marinos_escenario(capa, n.pinchos)), rangos_visibles)
        if n.burbujas_m3:
            actualizar_y_dibujar_burbujas_m3(n.mundo, n.burbujas_m3, [n.jugador1, n.jugador2], n.tick_m3)
    elif n.numero_mundo == 1:
        n.tick_m1 += 1
        dibujar_fondo_mundo1_invierno(n.mundo, n.ancho_mundo_nivel)
        dibujar_decoraciones_mundo1(n.mundo, n.suelo, n.ancho_mundo_nivel, n.tick_m1)
        n.plats_dibujar = n.plataformas_base if (n.paredes_colores is not None and n.plataformas_base is not None) else n.plataformas
        n.plats_estaticas = [p for p in n.plats_dibujar if not (
            (n.barrera_l_horiz is not None and (p is n.barrera_l_horiz or p is n.barrera_l_vert)) or
            (n.compuerta is not None and p is n.compuerta["rect"]) or
            (n.bloque_central is not None and p is n.bloque_central["rect"]) or
            (n.bloque_peligroso is not None and p is n.bloque_peligroso["rect"]) or
            (n.plataforma_movil is not None and p is n.plataforma_movil["rect"]) or
            (n.plataformas_derrumbables is not None and any(p is p_d["rect"] for p_d in n.plataformas_derrumbables))
        )]
        dibujar_escenario_mundo1(n.mundo, n.suelo, n.plats_estaticas, n.pozo_nivel)
        if n.barrera_l_horiz is not None and n.barrera_l_vert is not None:
            dibujar_barrera_l_escenario(n.mundo, n.barrera_l_horiz, n.barrera_l_vert)
        if n.pinchos:
            dibujar_pinchos_escenario(n.mundo, n.pinchos)
        actualizar_y_dibujar_nieve_mundo1(n.mundo, n.ancho_mundo_nivel, n.tick_m1)
    elif n.numero_mundo == 2:
        n.tick_m2 += 1
        dibujar_fondo_mundo2_ruinas(n.mundo, n.ancho_mundo_nivel)
        dibujar_decoraciones_mundo2(n.mundo, n.suelo, n.ancho_mundo_nivel, n.tick_m2, n.pozo_nivel)
        n.plats_dibujar = n.plataformas_base if (n.paredes_colores is not None and n.plataformas_base is not None) else n.plataformas
        n.plats_estaticas = [p for p in n.plats_dibujar if not (
            (n.barrera_l_horiz is not None and (p is n.barrera_l_horiz or p is n.barrera_l_vert)) or
            (n.compuerta is not None and p is n.compuerta["rect"]) or
            (n.bloque_central is not None and p is n.bloque_central["rect"]) or
            (n.bloque_peligroso is not None and p is n.bloque_peligroso["rect"]) or
            (n.bloques_peligrosos and any(p is bp["rect"] for bp in n.bloques_peligrosos)) or
            (n.plataforma_movil is not None and p is n.plataforma_movil["rect"]) or
            (n.plataformas_derrumbables is not None and any(p is p_d["rect"] for p_d in n.plataformas_derrumbables))
        )]
        dibujar_escenario_mundo2(n.mundo, n.suelo, n.plats_estaticas, n.pozo_nivel)
        if n.barrera_l_horiz is not None and n.barrera_l_vert is not None:
            dibujar_barrera_l_escenario(n.mundo, n.barrera_l_horiz, n.barrera_l_vert)
        if n.numero_nivel == 3:
            dibujar_pendulo_escenario(n.mundo, n.plataformas, n.plat_elevada, n.pozo_nivel, n.bloque_peligroso)
        if n.pinchos:
            dibujar_pinchos_escenario(n.mundo, n.pinchos)
        for n.bp in n.bloques_peligrosos:
            if n.bp is not n.bloque_peligroso:
                dibujar_bloque_peligroso(n.mundo, n.bp)
        if n.numero_nivel == 4 and n.plataformas_derrumbables is not None:
            dibujar_plataformas_derrumbables_escenario(n.mundo, n.plataformas_derrumbables, n.pozo_nivel)
        if n.numero_nivel == 5 and n.plataformas_alternadas is not None:
            dibujar_plataformas_alternadas_escenario(n.mundo, n.plataformas_alternadas, n.pozo_nivel)
        actualizar_y_dibujar_polvo_mundo2(n.mundo, n.ancho_mundo_nivel, n.tick_m2)
    else:
        n.mundo.fill((255, 240, 195))

        if n.pozo_nivel is not None:
            n.pz = n.pozo_nivel
            pygame.draw.rect(n.mundo, (235, 222, 192), (n.pz["x"], n.pz["y"], n.pz["ancho"], n.pz["alto"]))
            pygame.draw.line(n.mundo, COLOR_BORDE_PLATAFORMA, (n.pz["x"], n.pz["y"]), (n.pz["x"], n.pz["y"] + n.pz["alto"]), 2)
            pygame.draw.line(n.mundo, COLOR_BORDE_PLATAFORMA, (n.pz["x"] + n.pz["ancho"], n.pz["y"]), (n.pz["x"] + n.pz["ancho"], n.pz["y"] + n.pz["alto"]), 2)

        n.plats_dibujar = n.plataformas_base if (n.paredes_colores is not None and n.plataformas_base is not None) else n.plataformas
        for n.plat in n.plats_dibujar:
            if n.barrera_l_horiz is not None and (n.plat is n.barrera_l_horiz or n.plat is n.barrera_l_vert):
                continue
            if n.compuerta is not None and n.plat is n.compuerta["rect"]:
                continue
            if n.bloque_central is not None and n.plat is n.bloque_central["rect"]:
                continue
            if n.bloque_peligroso is not None and n.plat is n.bloque_peligroso["rect"]:
                continue
            if n.plataforma_movil is not None and n.plat is n.plataforma_movil["rect"]:
                continue
            if n.plataformas_derrumbables is not None and any(n.plat is p_d["rect"] for p_d in n.plataformas_derrumbables):
                continue
            if n.plat.bottom >= n.suelo.top:
                n.rect_torre = pygame.Rect(n.plat.x, n.plat.y, n.plat.width, n.plat.height + 4)
                pygame.draw.rect(n.mundo, COLOR_PLATAFORMA, n.rect_torre, border_top_left_radius=4, border_top_right_radius=4)
                pygame.draw.rect(n.mundo, COLOR_BORDE_PLATAFORMA, n.rect_torre, width=2, border_top_left_radius=4, border_top_right_radius=4)
            else:
                pygame.draw.rect(n.mundo, COLOR_PLATAFORMA, n.plat, border_radius=4)
                pygame.draw.rect(n.mundo, COLOR_BORDE_PLATAFORMA, n.plat, width=2, border_radius=4)

        if n.barrera_l_horiz is not None and n.barrera_l_vert is not None:
            dibujar_barrera_l_escenario(n.mundo, n.barrera_l_horiz, n.barrera_l_vert)

        pygame.draw.rect(n.mundo, (225, 110, 80), n.suelo)
        if n.pozo_nivel is not None:
            pygame.draw.line(n.mundo, COLOR_BORDE_PLATAFORMA, (n.pz["x"], n.pz["y"] + n.pz["alto"]), (n.pz["x"] + n.pz["ancho"], n.pz["y"] + n.pz["alto"]), 2)

        if n.pinchos:
            dibujar_pinchos_escenario(n.mundo, n.pinchos)
        if n.numero_mundo == 2 and n.numero_nivel == 3:
            dibujar_pendulo_escenario(n.mundo, n.plataformas, n.plat_elevada, n.pozo_nivel, n.bloque_peligroso)
        for n.bp in n.bloques_peligrosos:
            if n.bp is not n.bloque_peligroso:
                dibujar_bloque_peligroso(n.mundo, n.bp)
        if n.numero_mundo == 2 and n.numero_nivel == 4 and n.plataformas_derrumbables is not None:
            dibujar_plataformas_derrumbables_escenario(n.mundo, n.plataformas_derrumbables, n.pozo_nivel)
        if n.numero_mundo == 2 and n.numero_nivel == 5 and n.plataformas_alternadas is not None:
            dibujar_plataformas_alternadas_escenario(n.mundo, n.plataformas_alternadas, n.pozo_nivel)

    if n.compuerta is not None and n.compuerta["rect"].width > 0:
        n.c_rect = n.compuerta["rect"]
        pygame.draw.rect(n.mundo, (180, 85, 60), n.c_rect, border_radius=3)
        pygame.draw.rect(n.mundo, (120, 45, 30), n.c_rect, width=2, border_radius=3)
        for n.lx in range(n.c_rect.left + 14, n.c_rect.right - 6, 18):
            pygame.draw.line(n.mundo, (130, 55, 35), (n.lx, n.c_rect.top + 3), (n.lx, n.c_rect.bottom - 4), 2)

    if n.boton_compuerta is not None:
        n.rect_bc = n.boton_compuerta["rect"]
        n.h_bc = 4 if n.boton_compuerta["presionado"] else 12
        n.y_bc = n.suelo.top - n.h_bc
        pygame.draw.rect(n.mundo, (85, 70, 60), (n.rect_bc.left - 6, n.suelo.top - 4, n.rect_bc.width + 12, 10), border_radius=2)
        n.col_bc = (70, 205, 120) if n.boton_compuerta["presionado"] else (210, 85, 45)
        n.col_borde_bc = (40, 150, 80) if n.boton_compuerta["presionado"] else (150, 45, 25)
        pygame.draw.rect(n.mundo, n.col_bc, (n.rect_bc.x, n.y_bc, n.rect_bc.width, n.h_bc), border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.rect(n.mundo, n.col_borde_bc, (n.rect_bc.x, n.y_bc, n.rect_bc.width, n.h_bc), width=2, border_top_left_radius=3, border_top_right_radius=3)

    if n.bloque_central is not None:
        n.bc = n.bloque_central["rect"]
        pygame.draw.rect(n.mundo, (220, 50, 50), n.bc, border_radius=4)
        pygame.draw.rect(n.mundo, (140, 25, 25), n.bc, width=2, border_radius=4)
        for n.by in range(n.bc.top + 16, n.bc.bottom - 8, 16):
            pygame.draw.line(n.mundo, (160, 30, 30), (n.bc.left + 4, n.by), (n.bc.right - 4, n.by), 2)

    if n.plataforma_movil is not None:
        n.pm = n.plataforma_movil["rect"]
        pygame.draw.rect(n.mundo, (215, 105, 75), n.pm, border_radius=5)
        pygame.draw.rect(n.mundo, (150, 60, 40), n.pm, width=2, border_radius=5)
        for n.rx in range(n.pm.left + 16, n.pm.right - 8, 24):
            pygame.draw.circle(n.mundo, (140, 60, 40), (n.rx, n.pm.bottom - 5), 3)

        n.estado_pm = n.plataforma_movil.get("estado", "esperando_inicio")
        if n.estado_pm == "esperando_retorno":
            n.t_esp = n.plataforma_movil.get("tiempo_espera_retorno", 0)
            n.parpadeo = (n.t_esp // 15) % 2 == 0
            n.col_luz = (255, 235, 40) if n.parpadeo else (100, 85, 20)
            n.col_halo = (255, 245, 120) if n.parpadeo else (70, 60, 15)
            if n.parpadeo:
                pygame.draw.circle(n.mundo, n.col_halo, (n.pm.centerx, n.pm.centery), 8)
            pygame.draw.circle(n.mundo, n.col_luz, (n.pm.centerx, n.pm.centery), 5)
            pygame.draw.circle(n.mundo, (255, 255, 200) if n.parpadeo else (60, 50, 10), (n.pm.centerx, n.pm.centery), 5, width=1)
        elif n.estado_pm in ("avanzando", "regresando"):
            pygame.draw.circle(n.mundo, (80, 220, 100), (n.pm.centerx, n.pm.centery), 5)
            pygame.draw.circle(n.mundo, (180, 255, 190), (n.pm.centerx, n.pm.centery), 5, width=1)
        else:
            n.col_ind = (240, 180, 40) if n.plataforma_movil.get("tiempo_con_peso", 0) > 0 else (180, 80, 55)
            pygame.draw.circle(n.mundo, n.col_ind, (n.pm.centerx, n.pm.centery), 4)

    if n.boton_nivel is not None:
        n.rect_b = n.boton_nivel["rect"]
        n.h_actual = 4 if n.boton_nivel["presionado"] else 12
        n.y_actual = n.suelo.top - n.h_actual
        pygame.draw.rect(n.mundo, (90, 70, 60), (n.rect_b.left - 6, n.suelo.top - 4, n.rect_b.width + 12, 10), border_radius=2)
        n.col_btn = (80, 200, 100) if n.boton_nivel["presionado"] else (225, 65, 65)
        n.col_borde_btn = (50, 150, 70) if n.boton_nivel["presionado"] else (175, 45, 45)
        pygame.draw.rect(n.mundo, n.col_btn, (n.rect_b.x, n.y_actual, n.rect_b.width, n.h_actual), border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.rect(n.mundo, n.col_borde_btn, (n.rect_b.x, n.y_actual, n.rect_b.width, n.h_actual), width=2, border_top_left_radius=3, border_top_right_radius=3)

    if n.pared_nivel is not None:
        n.pr = n.pared_nivel["rect"]
        for n.y_linea in range(n.pr.top + 30, n.pr.bottom - 10, 35):
            if 0 <= n.y_linea <= ALTO:
                pygame.draw.line(n.mundo, COLOR_BORDE_PLATAFORMA, (n.pr.left + 4, n.y_linea), (n.pr.right - 4, n.y_linea), 2)

    if n.laser_nivel is not None:
        dibujar_laser_escenario(n.mundo, n.laser_nivel)

    if n.paredes_colores is not None:
        dibujar_paredes_colores_escenario(n.mundo, n.paredes_colores)

    if n.botones_colores is not None:
        dibujar_botones_colores_escenario(n.mundo, n.botones_colores, n.suelo)

    if n.usar_agua: dibujar_agua(n.mundo, ZONA_AGUA, rangos=rangos_visibles)
    if n.usar_soga and not n.p1_completado and not n.p2_completado:
        dibujar_soga_escenario(n.mundo, n.jugador1, n.jugador2, n.estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    if n.usar_caja: n.mundo.blit(n.caja["sprite"], n.caja["rect"])

    if n.usar_llave and n.puerta:
        actualizar_puerta(n.puerta)
        n.estado_p = "abierta" if n.puerta["abierta"] else "cerrada"
        n.mundo.blit(n.puerta["sprites"][n.estado_p], n.puerta["rect"])
        if n.llave and not n.puerta["abierta"]:
            if n.numero_mundo == 3:
                n.halo_surf = pygame.Surface((44, 60), pygame.SRCALPHA)
                n.alpha_h = int(60 + 25 * math.sin(n.tick_m3 * 0.08))
                pygame.draw.ellipse(n.halo_surf, (255, 230, 90, n.alpha_h), (0, 0, 44, 60))
                n.mundo.blit(n.halo_surf, (n.llave["rect"].centerx - 22, n.llave["rect"].centery - 30))
            n.mundo.blit(n.llave["sprite"], n.llave["rect"])

    if n.numero_mundo == 3 and n.numero_nivel in (4, 5) and n.surf_oscuridad_m3 is not None:
        aplicar_oscuridad_submarina(
            n.mundo,
            [(n.jugador1, n.linterna_p1, n.p1_completado), (n.jugador2, n.linterna_p2, n.p2_completado)],
            n.surf_oscuridad_m3,
            n.surf_luz_linterna,
            n.surf_luz_tenue,
            rangos=rangos_visibles,
        )
        if not n.p1_completado:
            dibujar_personaje(n.mundo, n.jugador1, ZONA_AGUA if n.usar_agua else None)
            dibujar_linterna_minero(n.mundo, n.jugador1, n.linterna_p1 and not n.jugador1.get("muerto", False))
            if n.numero_nivel in (5, 6):
                dibujar_alerta_oxigeno_personaje(n.mundo, n.jugador1, n.oxigeno_p1, n.tick_m3)
        if not n.p2_completado:
            dibujar_personaje(n.mundo, n.jugador2, ZONA_AGUA if n.usar_agua else None)
            dibujar_linterna_minero(n.mundo, n.jugador2, n.linterna_p2 and not n.jugador2.get("muerto", False))
            if n.numero_nivel in (5, 6):
                dibujar_alerta_oxigeno_personaje(n.mundo, n.jugador2, n.oxigeno_p2, n.tick_m3)
    else:
        if not n.p1_completado: dibujar_personaje(n.mundo, n.jugador1, ZONA_AGUA if n.usar_agua else None)
        if not n.p2_completado: dibujar_personaje(n.mundo, n.jugador2, ZONA_AGUA if n.usar_agua else None)

    # Controles tutorial directamente arriba de cada personaje
    if n.numero_mundo == 1 and n.numero_nivel == 1 and n.mostrar_tutorial:
        n._dibujar_controles_tutorial(n.mundo, alpha_p1=n.alpha_tut_p1, alpha_p2=n.alpha_tut_p2, teclas_actuales=n.teclas)

    # Efecto de ráfaga y animación de teclas sopladas
    if n.numero_mundo == 1 and n.numero_nivel == 1:
        n._actualizar_y_dibujar_soplado(n.mundo)

    # Las vistas se calcularon antes de dibujar (calcular_vistas_camara), con este mismo estado
    for n.x_dest, n.cam_x, n.ancho_vista in vistas_camara:
        n.pantalla.blit(n.mundo, (n.x_dest, 0), pygame.Rect(n.cam_x, 0, n.ancho_vista, ALTO))
    if len(vistas_camara) > 1:
        pygame.draw.line(n.pantalla, (0, 0, 0), (ANCHO // 2, 0), (ANCHO // 2, ALTO), 4)

    # Botones HUD en la esquina superior derecha solo si el nivel continúa activo
    if not (n.p1_completado and n.p2_completado):
        n.pos_m_hud = pygame.mouse.get_pos()
        n.spr_cfg_hud = n.spr_config_hover if (n.rect_btn_config.collidepoint(n.pos_m_hud) and n.spr_config_hover) else n.spr_config_normal
        n.spr_c_hud = n.spr_casa_hover if (n.rect_btn_casa.collidepoint(n.pos_m_hud) and n.spr_casa_hover) else n.spr_casa_normal
        n.spr_r_hud = n.spr_reiniciar_hover if (n.rect_btn_reiniciar.collidepoint(n.pos_m_hud) and n.spr_reiniciar_hover) else n.spr_reiniciar_normal
        n.spr_x_hud = n.spr_x_hover if (n.rect_btn_x.collidepoint(n.pos_m_hud) and n.spr_x_hover) else n.spr_x_normal

        # El fondo detrás de cada botón solo se usa para animar el clic; se copia únicamente
        # cuando el mouse está cerca del HUD en vez de hacer 4 copias en cada frame.
        if n.rect_btn_config.unionall([n.rect_btn_casa, n.rect_btn_reiniciar, n.rect_btn_x]).inflate(80, 80).collidepoint(n.pos_m_hud):
            n.fondo_btn_config = n.pantalla.subsurface(n.rect_btn_config).copy()
            n.fondo_btn_casa = n.pantalla.subsurface(n.rect_btn_casa).copy()
            n.fondo_btn_reiniciar = n.pantalla.subsurface(n.rect_btn_reiniciar).copy()
            n.fondo_btn_x = n.pantalla.subsurface(n.rect_btn_x).copy()

        if n.spr_cfg_hud: n.pantalla.blit(n.spr_cfg_hud, n.rect_btn_config)
        if n.spr_c_hud: n.pantalla.blit(n.spr_c_hud, n.rect_btn_casa)
        if n.spr_r_hud: n.pantalla.blit(n.spr_r_hud, n.rect_btn_reiniciar)
        if n.spr_x_hud: n.pantalla.blit(n.spr_x_hud, n.rect_btn_x)

    if n.numero_mundo == 3 and n.numero_nivel == 4 and not (n.p1_completado and n.p2_completado):
        _dibujar_hud_linternas_m3_n4(n.pantalla, n.linterna_p1, n.linterna_p2, n.p1_color, n.p2_color)
    if n.numero_mundo == 3 and n.numero_nivel in (5, 6) and not (n.p1_completado and n.p2_completado):
        _dibujar_hud_oxigeno_m3_n5(n.pantalla, n.oxigeno_p1, n.oxigeno_p2, n.p1_color, n.p2_color, n.tick_m3)
        if n.numero_nivel == 5:
            _dibujar_hud_linternas_m3_n4(n.pantalla, n.linterna_p1, n.linterna_p2, n.p1_color, n.p2_color, y_base=60)

    pygame.display.flip()


def _comprobar_fin_de_nivel(n):
    """Pantalla de muerte o transición de victoria. Devuelve el resultado del nivel o None para seguir."""
    # Gestión de pantalla de muerte y reinicio según las reglas de cada mundo
    debe_mostrar_muerte = False
    muertos = [p for p in (n.jugador1, n.jugador2) if p.get("muerto", False)]
    if n.numero_mundo == 3:
        # En Mundo 3 la muerte es individual: si uno muere, el otro permanece vivo.
        # En cuanto cualquier personaje que haya muerto completa su breve animación de muerte,
        # se gestiona la derrota de inmediato sin quedarse esperando indefinidamente a que el otro personaje muera.
        if muertos and any(p.get("muerte_terminada", False) for p in muertos):
            debe_mostrar_muerte = True
    else:
        if muertos and all(p.get("muerte_terminada", False) for p in muertos):
            debe_mostrar_muerte = True

    if debe_mostrar_muerte:
        detener_sonido_ahogamiento()
        n.resultado = pantalla_muerte(n.pantalla, n.reloj)
        if n.resultado == "salir": return "salir"
        if n.resultado == "menu": return "menu"
        if n.resultado == "reiniciar":
            n._reiniciar_nivel_completo()

    # Condición de nivel superado
    nivel_superado = False
    if n.numero_mundo == 3:
        if (n.p1_completado and n.p2_completado) or \
           (n.jugador1["muerto"] and n.p2_completado) or \
           (n.jugador2["muerto"] and n.p1_completado):
            nivel_superado = True
    else:
        if n.p1_completado and n.p2_completado:
            nivel_superado = True

    if nivel_superado:
        detener_sonido_ahogamiento()
        n.cam_puerta_x = max(0, min(n.puerta["rect"].centerx - ANCHO // 2, n.ancho_mundo_nivel - ANCHO)) if n.puerta else 0
        return animar_transicion_nivel_completado(
            pantalla=n.pantalla,
            reloj=n.reloj,
            hay_siguiente=n.hay_siguiente_nivel,
            mundo=n.numero_mundo,
            numero_nivel=n.numero_nivel,
            puerta=n.puerta,
            mundo_surface=n.mundo,
            cam_x=n.cam_puerta_x,
            ancho_mundo_nivel=n.ancho_mundo_nivel,
            color_p1=n.p1_color,
            color_p2=n.p2_color,
            niveles_desbloqueados=n.niveles_desbloqueados,
            partida_id=n.partida_id,
            partida_nombre=n.partida_nombre,
            snapshot_guardado=n.snapshot_guardado,
        )


def iniciar_mundo(mecanicas=None, numero_nivel=1, color_p1=None, color_p2=None, mundo=1, niveles_desbloqueados=None, partida_id=None, partida_nombre=None, snapshot_guardado=None, accesorio_p1=None, accesorio_p2=None, partida_password=None):
    """Corre un nivel completo y devuelve "siguiente", "menu" o "salir"."""
    n = EstadoNivel(mecanicas, numero_nivel, color_p1, color_p2, mundo, niveles_desbloqueados, partida_id, partida_nombre, snapshot_guardado, accesorio_p1, accesorio_p2, partida_password)
    while n.ejecutando:
        n.reloj.tick(FPS)
        resultado = _procesar_eventos(n)
        if resultado is not None:
            return resultado
        _actualizar_jugadores(n)
        _actualizar_mecanicas(n)
        _resolver_interacciones(n)
        _dibujar_frame(n)
        resultado = _comprobar_fin_de_nivel(n)
        if resultado is not None:
            return resultado
    detener_sonido_ahogamiento()
    return "salir"