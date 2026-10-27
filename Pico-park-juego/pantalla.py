import os
import sys
import math
import random
import pygame

from fuentes import (
    obtener_fuente,
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_pequena,
    TAMANO_TITULO,
    TAMANO_TITULO_GRANDE,
    TAMANO_SUBTITULO,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO,
    TAMANO_TEXTO_GRANDE,
    TAMANO_BOTON,
    TAMANO_BOTON_GRANDE,
    TAMANO_PEQUENA,
    TAMANO_BADGE,
)
from configuracion import t, mostrar_pestana_configuracion

from sprites import (
    ANCHO, ALTO, FPS,
    COLOR_JUGADOR1, COLOR_JUGADOR2,
    RUTA_BOTONES,
    dibujar_personaje,
    dibujar_agua,
    cargar_boton,
    cargar_boton_escalado,
    animar_pulsacion_boton,
    aclarar_boton,
)
from movimientos import (
    crear_personaje,
    crear_caja,
    crear_pinchos,
    PinchoRect,
    crear_pincho,
    crear_llave,
    crear_puerta,
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
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    ZONA_AGUA,
    actualizar_estado_agua,
    aplicar_fisica_agua,
    actualizar_estado_soga_muerte,
    ALTO_HITBOX,
    ANCHO_HITBOX,
)
from guardado import (
    crear_desbloqueados_inicial,
    mostrar_dialogo_guardar_salir,
    hay_progreso_sin_guardar,
)

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

    boton_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("salir.png", w_btn, h_btn)
    boton_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-preapretado.png", w_btn, h_btn)
    boton_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-apretado.png", w_btn, h_btn)

    boton_reiniciar_normal = cargar_boton_escalado("Ventanas/boton-reiniciar.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar.png", w_btn, h_btn)
    boton_reiniciar_semi = cargar_boton_escalado("Ventanas/boton-reiniciar-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-semiapretado.png", w_btn, h_btn)
    boton_reiniciar_apretado = cargar_boton_escalado("Ventanas/boton-reiniciar-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-apretado.png", w_btn, h_btn)

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

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_reiniciar.collidepoint(evento.pos):
                    if animar_pulsacion_boton(pantalla, boton_reiniciar, boton_reiniciar_semi, boton_reiniciar_apretado, (25, 25, 25), boton_reiniciar_normal):
                        return "reiniciar"

                if boton_menu.collidepoint(evento.pos):
                    if animar_pulsacion_boton(pantalla, boton_menu, boton_menu_semi, boton_menu_apretado, (25, 25, 25), boton_menu_normal):
                        return "salir"

        pantalla.fill((25, 25, 25))
        titulo = fuente_titulo.render(t("te_moriste"), True, (255, 80, 80))
        texto = fuente_texto.render(t("reiniciar_o_salir"), True, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 180)))
        pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 250)))

        spr_r = boton_reiniciar_hover if (hov_reinicio and boton_reiniciar_hover) else boton_reiniciar_normal
        spr_m = boton_menu_hover if (hov_menu and boton_menu_hover) else boton_menu_normal

        pantalla.blit(spr_r, boton_reiniciar)
        pantalla.blit(spr_m, boton_menu)
        pygame.display.flip()
        reloj.tick(FPS)


def obtener_fuente_elegante(tamanio, negrita=True):
    for nombre in ["Microsoft YaHei", "SimHei", "SimSun", "Segoe UI", "Arial Rounded MT Bold", "Arial", "Trebuchet MS", "DejaVu Sans"]:
        try:
            return pygame.font.SysFont(nombre, tamanio, bold=negrita)
        except Exception:
            pass
    return obtener_fuente_subtitulo(tamanio, negrita=negrita, tamano_fallback=int(tamanio * 1.1))


def dibujar_estrella_decorativa(superficie, centro, r_exterior=14, r_interior=6, col_relleno=(255, 222, 90), col_borde=(185, 145, 75)):
    """Dibuja una estrella decorativa de 5 puntas estilo pixel/cartoon."""
    puntos = []
    cx, cy = centro
    for i in range(10):
        r = r_exterior if i % 2 == 0 else r_interior
        ang = i * (math.pi / 5) - math.pi / 2
        puntos.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    pygame.draw.polygon(superficie, col_relleno, puntos)
    pygame.draw.polygon(superficie, col_borde, puntos, 2)


def renderizar_texto_con_sombra(texto, fuente, col_texto, col_sombra=(20, 20, 20), offset=(3, 3)):
    """Crea una superficie SRCALPHA con el texto nítido y su sombra suave."""
    t_sombra = fuente.render(texto, True, col_sombra)
    t_texto = fuente.render(texto, True, col_texto)
    w = max(t_sombra.get_width() + abs(offset[0]), t_texto.get_width() + abs(offset[0])) + 8
    h = max(t_sombra.get_height() + abs(offset[1]), t_texto.get_height() + abs(offset[1])) + 8
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(t_sombra, (max(0, offset[0]) + 4, max(0, offset[1]) + 4))
    surf.blit(t_texto, (4, 4))
    return surf


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
    Animación visual de cierre de la puerta utilizando exclusivamente su sprite original:
    La hoja se despliega desde su estado abierto (ancho 15) hasta cerrarse por completo (ancho 60),
    revelando el pomo dorado original y un sutil destello de sellado sin alterar su diseño.
    """
    if puerta is None or mundo is None:
        return

    rect_p = puerta["rect"]
    ancho_p = rect_p.width
    alto_p = rect_p.height

    sprite_cerrada = puerta["sprites"]["cerrada"]

    frames_cierre = 20
    for f in range(frames_cierre + 1):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        t = f / frames_cierre
        factor = t * t

        # Redibujar fondo original del escenario detrás de la puerta
        pygame.draw.rect(mundo, (255, 240, 195), rect_p)

        # Animar el desplazamiento de la hoja usando directamente el sprite original cerrado
        w_actual = max(15, min(ancho_p, int(15 + (ancho_p - 15) * factor)))
        sub_hoja = sprite_cerrada.subsurface((0, 0, w_actual, alto_p))
        mundo.blit(sub_hoja, rect_p.topleft)

        pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))
        pygame.display.flip()

    # Destello sutil de absorción/cierre aplicado directamente sobre la puerta original cerrada
    frames_brillo = 14
    for fb in range(frames_brillo):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        p_b = fb / frames_brillo
        alpha_b = int(75 * math.sin(p_b * math.pi))

        pygame.draw.rect(mundo, (255, 240, 195), rect_p)
        mundo.blit(sprite_cerrada, rect_p.topleft)

        if alpha_b > 0:
            surf_brillo = pygame.Surface((ancho_p, alto_p), pygame.SRCALPHA)
            surf_brillo.fill((255, 255, 255, alpha_b // 2))
            y_luz = int(alto_p * p_b)
            pygame.draw.line(surf_brillo, (255, 255, 255, alpha_b), (0, y_luz), (ancho_p, y_luz), 2)
            mundo.blit(surf_brillo, rect_p.topleft)

        pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))
        pygame.display.flip()

    # Dejar el escenario en mundo con la puerta cerrada original limpia
    pygame.draw.rect(mundo, (255, 240, 195), rect_p)
    mundo.blit(sprite_cerrada, rect_p.topleft)
    pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))
    pygame.display.flip()

    # Pausa breve (~0.12s) con la puerta cerrada
    for _ in range(7):
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))
        pygame.display.flip()


def animar_salida_franjas(pantalla, reloj, captura_escenario, puerta=None, cam_x=0):
    """
    Transición geométrica multicapa integrada con la puerta original:
    - Capa 1 (Detrás de la puerta): Escenario base y halo de absorción oscura expandiéndose detrás de ella.
    - Capa 2 (La puerta): Sprite original de la puerta conservando diseño, pomo, colores y posición exactos.
    - Capa 3 (Por delante de la puerta): Bandas geométricas que nacen de la puerta y la cruzan por delante
      hacia afuera, junto a las franjas que entran desde los bordes, acelerando hasta cubrir la pantalla (~1.13s).
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()
    franjas = crear_franjas_geometricas(ancho, alto)

    frames_totales = 68
    duracion = 1.13

    sprite_cerrada = puerta["sprites"]["cerrada"] if (puerta and "sprites" in puerta and "cerrada" in puerta["sprites"]) else None
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

        # --- CAPA 1: Escenario base y aura de absorción DETRÁS de la puerta ---
        pantalla.blit(captura_escenario, (0, 0))

        if sprite_cerrada is not None and pos_puerta is not None:
            radio_w = int(door_w // 2 + 180 * (progreso ** 1.6))
            radio_h = int(door_h // 2 + 130 * (progreso ** 1.6))
            alpha_aura = max(0, min(180, int(220 * math.sin(min(1.0, progreso * 1.4) * math.pi))))
            if alpha_aura > 0:
                surf_aura = pygame.Surface((radio_w * 2, radio_h * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(surf_aura, (0, 0, 0, alpha_aura), (0, 0, radio_w * 2, radio_h * 2))
                pantalla.blit(surf_aura, (door_cx - radio_w, door_cy - radio_h))

        # --- CAPA 2: La puerta original del juego ---
        if sprite_cerrada is not None and pos_puerta is not None:
            pantalla.blit(sprite_cerrada, pos_puerta)

        # --- CAPA 3: Efecto de transición visible POR DELANTE de la puerta ---
        # 1. Bandas geométricas negras que nacen de la puerta y se expanden por delante de ella
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

    # Mini bloques decorativos de los personajes en la cabecera
    r_sq1 = pygame.Rect(rect_panel.left + 16, rect_panel.top + 16, 26, 26)
    pygame.draw.rect(superficie, c_p1, r_sq1, border_radius=4)
    pygame.draw.rect(superficie, (45, 45, 50), r_sq1, width=2, border_radius=4)

    r_sq2 = pygame.Rect(rect_panel.right - 42, rect_panel.top + 16, 26, 26)
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

    # Fuentes estilizadas para la pantalla de victoria (tamaños legibles y nítidos)
    fuente_titulo = obtener_fuente_elegante(34, negrita=True)
    fuente_sub = obtener_fuente_elegante(25, negrita=True)
    fuente_badge = obtener_fuente_elegante(20, negrita=True)
    fuente_btn = obtener_fuente_elegante(26, negrita=True)

    w_btn = 272
    h_btn = 80
    btn1_x = cx - w_btn // 2
    btn1_target_y = rect_panel.top + 215
    btn2_x = cx - w_btn // 2
    btn2_target_y = rect_panel.top + 305

    rect_btn1 = pygame.Rect(btn1_x, btn1_target_y, w_btn, h_btn)
    rect_btn2 = pygame.Rect(btn2_x, btn2_target_y, w_btn, h_btn)

    spr_sig_normal = cargar_boton_escalado("Ventanas/boton-siguiente.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente.png", w_btn, h_btn)
    spr_sig_semi = cargar_boton_escalado("Ventanas/boton-siguiente-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-semiapretado.png", w_btn, h_btn)
    spr_sig_apretado = cargar_boton_escalado("Ventanas/boton-siguiente-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-apretado.png", w_btn, h_btn)

    spr_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn)
    spr_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn)
    spr_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn)

    spr_sig_hover = aclarar_boton(spr_sig_normal) if spr_sig_normal else None
    spr_menu_hover = aclarar_boton(spr_menu_normal) if spr_menu_normal else None

    txt_btn1 = t("siguiente") if hay_siguiente else t("finalizar")
    txt_btn2 = t("volver_juego")

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
        t_tit_surf = fuente_titulo.render(t("nivel_completado"), True, (255, 255, 255))
        pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, y_tit)))

        # Subtítulo y cápsula de nivel
        if f >= 8:
            t_sub = fuente_sub.render(t("buen_trabajo"), True, (75, 70, 70))
            pantalla.blit(t_sub, t_sub.get_rect(center=(cx, rect_panel.top + 98)))

            r_badge = pygame.Rect(cx - 150, rect_panel.top + 132, 300, 36)
            pygame.draw.rect(pantalla, (255, 255, 255), r_badge, border_radius=8)
            pygame.draw.rect(pantalla, (210, 195, 160), r_badge, width=2, border_radius=8)
            t_nb = fuente_badge.render(nom_nivel, True, (50, 45, 40))
            pantalla.blit(t_nb, t_nb.get_rect(center=r_badge.center))

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
                tb1 = fuente_btn.render(txt_btn1, True, (255, 255, 255))
                pantalla.blit(tb1, tb1.get_rect(center=r1_anim.center))

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
                tb2 = fuente_btn.render(txt_btn2, True, (50, 50, 55))
                pantalla.blit(tb2, tb2.get_rect(center=r2_anim.center))

        pygame.display.flip()

    # --- FASE 3: Interacción del usuario (hover y selección) ---
    accion_seleccionada = None
    boton_presionado = None
    fondo_limpio_btn1 = None
    fondo_limpio_btn2 = None

    while accion_seleccionada is None:
        reloj.tick(FPS)
        pos_mouse = pygame.mouse.get_pos()
        hover1 = rect_btn1.collidepoint(pos_mouse)
        hover2 = rect_btn2.collidepoint(pos_mouse)

        # Ajuste de cursor al pasar sobre los botones
        try:
            if hover1 or hover2:
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
                if rect_btn1.collidepoint(evento.pos):
                    spr1_norm = spr_sig_normal if hay_siguiente else spr_menu_normal
                    spr1_semi = spr_sig_semi if hay_siguiente else spr_menu_semi
                    spr1_apr = spr_sig_apretado if hay_siguiente else spr_menu_apretado
                    if animar_pulsacion_boton(pantalla, rect_btn1, spr1_semi, spr1_apr, fondo_limpio_btn1, spr1_norm):
                        accion_seleccionada = "siguiente" if hay_siguiente else "menu"
                elif rect_btn2.collidepoint(evento.pos):
                    if animar_pulsacion_boton(pantalla, rect_btn2, spr_menu_semi, spr_menu_apretado, fondo_limpio_btn2, spr_menu_normal):
                        accion_seleccionada = "menu"

        if accion_seleccionada is not None:
            break

        pantalla.fill((0, 0, 0))
        dibujar_panel_victoria_solido(pantalla, rect_panel, color_p1, color_p2)

        # Título
        t_tit_surf = fuente_titulo.render(t("nivel_completado"), True, (255, 255, 255))
        pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, rect_panel.top + 35)))

        # Subtítulo y cápsula
        t_sub = fuente_sub.render(t("buen_trabajo"), True, (75, 70, 70))
        pantalla.blit(t_sub, t_sub.get_rect(center=(cx, rect_panel.top + 98)))

        r_badge = pygame.Rect(cx - 150, rect_panel.top + 132, 300, 36)
        pygame.draw.rect(pantalla, (255, 255, 255), r_badge, border_radius=8)
        pygame.draw.rect(pantalla, (210, 195, 160), r_badge, width=2, border_radius=8)
        t_nb = fuente_badge.render(nom_nivel, True, (50, 45, 40))
        pantalla.blit(t_nb, t_nb.get_rect(center=r_badge.center))

        # Captura de fondos limpios antes de renderizar los botones
        fondo_limpio_btn1 = pantalla.subsurface(rect_btn1).copy()
        fondo_limpio_btn2 = pantalla.subsurface(rect_btn2).copy()

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
                tb1 = fuente_btn.render(txt_btn1, True, (245, 245, 245))
                pantalla.blit(tb1, tb1.get_rect(center=r1_draw.center))
            elif hover1:
                r1_draw = pygame.Rect(rect_btn1.x, rect_btn1.y - 2, rect_btn1.w, rect_btn1.h)
                pygame.draw.rect(pantalla, (160, 50, 35), (r1_draw.x, r1_draw.y + 6, r1_draw.w, r1_draw.h), border_radius=8)
                pygame.draw.rect(pantalla, (240, 125, 95), r1_draw, border_radius=8)
                pygame.draw.rect(pantalla, (180, 60, 45), r1_draw, width=3, border_radius=8)
                tb1 = fuente_btn.render(txt_btn1, True, (255, 255, 255))
                pantalla.blit(tb1, tb1.get_rect(center=r1_draw.center))
            else:
                pygame.draw.rect(pantalla, (160, 50, 35), (rect_btn1.x, rect_btn1.y + 4, rect_btn1.w, rect_btn1.h), border_radius=8)
                pygame.draw.rect(pantalla, (225, 110, 80), rect_btn1, border_radius=8)
                pygame.draw.rect(pantalla, (150, 45, 30), rect_btn1, width=3, border_radius=8)
                tb1 = fuente_btn.render(txt_btn1, True, (255, 255, 255))
                pantalla.blit(tb1, tb1.get_rect(center=rect_btn1.center))

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
                tb2 = fuente_btn.render(txt_btn2, True, (35, 35, 40))
                pantalla.blit(tb2, tb2.get_rect(center=r2_draw.center))
            elif hover2:
                r2_draw = pygame.Rect(rect_btn2.x, rect_btn2.y - 2, rect_btn2.w, rect_btn2.h)
                pygame.draw.rect(pantalla, (195, 185, 165), (r2_draw.x, r2_draw.y + 6, r2_draw.w, r2_draw.h), border_radius=8)
                pygame.draw.rect(pantalla, (255, 248, 232), r2_draw, border_radius=8)
                pygame.draw.rect(pantalla, (40, 40, 45), r2_draw, width=3, border_radius=8)
                tb2 = fuente_btn.render(txt_btn2, True, (40, 40, 45))
                pantalla.blit(tb2, tb2.get_rect(center=r2_draw.center))
            else:
                pygame.draw.rect(pantalla, (195, 185, 165), (rect_btn2.x, rect_btn2.y + 4, rect_btn2.w, rect_btn2.h), border_radius=8)
                pygame.draw.rect(pantalla, (245, 235, 215), rect_btn2, border_radius=8)
                pygame.draw.rect(pantalla, (70, 70, 75), rect_btn2, width=3, border_radius=8)
                tb2 = fuente_btn.render(txt_btn2, True, (50, 50, 55))
                pantalla.blit(tb2, tb2.get_rect(center=rect_btn2.center))

        pygame.display.flip()

    try:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        pass

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
    # 1. Animación de cierre de puerta en el escenario actual
    if puerta is not None and mundo_surface is not None:
        animar_cierre_puerta(pantalla, reloj, mundo_surface, puerta, cam_x, ancho_mundo_nivel)

    # 2. Captura del escenario base detrás de la puerta para el sistema multicapa
    mundo_fondo = mundo_surface.copy()
    if puerta is not None:
        pygame.draw.rect(mundo_fondo, (255, 240, 195), puerta["rect"])
    captura_escenario = pygame.Surface((pantalla.get_width(), pantalla.get_height()))
    captura_escenario.blit(mundo_fondo, (0, 0), pygame.Rect(cam_x, 0, pantalla.get_width(), pantalla.get_height()))

    # 3. Franjas y transición multicapa generada desde la puerta
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
        s_abismo = pygame.Surface((pz["ancho"], pz["alto"]), pygame.SRCALPHA)
        s_abismo.fill((40, 25, 25, 110))
        superficie.blit(s_abismo, (pz["x"], pz["y"]))

    if bloque_peligroso is not None:
        br = bloque_peligroso["rect"] if isinstance(bloque_peligroso, dict) else bloque_peligroso
        pygame.draw.rect(superficie, (220, 50, 50), br, border_radius=4)
        pygame.draw.rect(superficie, (140, 25, 25), br, width=2, border_radius=4)
        for by in range(br.top + 14, br.bottom - 8, 14):
            pygame.draw.line(superficie, (160, 30, 30), (br.left + 4, by), (br.right - 4, by), 2)
        for rx, ry in [(br.left + 6, br.top + 6), (br.right - 6, br.top + 6), (br.left + 6, br.bottom - 6), (br.right - 6, br.bottom - 6)]:
            pygame.draw.circle(superficie, (255, 180, 180), (rx, ry), 2)
            pygame.draw.circle(superficie, (110, 20, 20), (rx, ry), 1)

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
        s_abismo = pygame.Surface((pz["ancho"], pz["alto"]), pygame.SRCALPHA)
        s_abismo.fill((40, 25, 25, 120))
        superficie.blit(s_abismo, (pz["x"], pz["y"]))

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
        s_abismo = pygame.Surface((pz["ancho"], pz["alto"]), pygame.SRCALPHA)
        s_abismo.fill((40, 25, 25, 120))
        superficie.blit(s_abismo, (pz["x"], pz["y"]))

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
    Dibuja la soga que une a ambos personajes con estiramiento progresivo y aspecto visual natural:
    - Cuando los personajes están cerca (<= d_reposo), la soga cuelga formando una curva catenaria/Bézier suave y floja.
    - A medida que se alejan hacia d_max, la comba se reduce progresivamente en consonancia con la tensión física.
    - Durante la secuencia de muerte, permite un margen exclusivo de +10px de estiramiento.
    - Al superar ese límite, se muestra la soga rota en ambos extremos con hilachas y partículas de rotura.
    - Anclada en el torso/cintura para no tapar los rostros ni interferir con los sprites.
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

    # 1. Caso soga rota por muerte en el Mundo 2
    if estado_soga and estado_soga.get("rota", False):
        if dist > 0.001:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x, dir_y = 1.0, 0.0

        len_cabo = 35.0
        # Cabo 1 (desde p1)
        m1 = (p_inicio[0] + dir_x * (len_cabo * 0.5), p_inicio[1] + dir_y * (len_cabo * 0.5) + 6)
        e1 = (p_inicio[0] + dir_x * len_cabo, p_inicio[1] + dir_y * len_cabo + 16)
        pygame.draw.lines(superficie, col_soga_ext, False, [p_inicio, m1, e1], 4)
        pygame.draw.lines(superficie, col_soga_int, False, [p_inicio, m1, e1], 2)
        # Hilachas deshilachadas en la punta
        pygame.draw.line(superficie, col_soga_ext, e1, (e1[0] - 2, e1[1] + 5), 1)
        pygame.draw.line(superficie, col_soga_ext, e1, (e1[0] + 3, e1[1] + 4), 1)
        pygame.draw.circle(superficie, col_soga_ext, p_inicio, 4)
        pygame.draw.circle(superficie, col_soga_int, p_inicio, 2)

        # Cabo 2 (desde p2)
        m2 = (p_fin[0] - dir_x * (len_cabo * 0.5), p_fin[1] - dir_y * (len_cabo * 0.5) + 6)
        e2 = (p_fin[0] - dir_x * len_cabo, p_fin[1] - dir_y * len_cabo + 16)
        pygame.draw.lines(superficie, col_soga_ext, False, [p_fin, m2, e2], 4)
        pygame.draw.lines(superficie, col_soga_int, False, [p_fin, m2, e2], 2)
        # Hilachas deshilachadas en la punta
        pygame.draw.line(superficie, col_soga_ext, e2, (e2[0] - 2, e2[1] + 5), 1)
        pygame.draw.line(superficie, col_soga_ext, e2, (e2[0] + 3, e2[1] + 4), 1)
        pygame.draw.circle(superficie, col_soga_ext, p_fin, 4)
        pygame.draw.circle(superficie, col_soga_int, p_fin, 2)

        # Partículas de rotura
        for part in estado_soga.get("particulas_rotura", []):
            pygame.draw.circle(superficie, col_soga_ext, (int(part["x"]), int(part["y"])), 3)
            pygame.draw.circle(superficie, col_soga_int, (int(part["x"]), int(part["y"])), 2)
        return

    # Si está en secuencia de muerte pero aún no rompió, el límite máximo se estira 10px adicionales
    en_muerte = estado_soga and estado_soga.get("en_muerte", False)
    d_max_efectivo = (d_max + 10.0) if en_muerte else d_max

    if dist < 16:
        pygame.draw.line(superficie, col_soga_ext, p_inicio, p_fin, 4)
        pygame.draw.line(superficie, col_soga_int, p_inicio, p_fin, 2)
        return

    # Grado de tensión visual entre 0.0 (reposo) y 1.0 (máximo estiramiento)
    if dist <= d_reposo:
        tension_visual = 0.0
    else:
        tension_visual = min(1.0, (dist - d_reposo) / max(1.0, d_max_efectivo - d_reposo))

    if tension_visual < 0.96 and dist < d_max_efectivo:
        sag_max = min(52.0, max(10.0, (d_max_efectivo - dist) * 0.42))
        sag = sag_max * (1.0 - (tension_visual ** 1.4))
        ctrl_x = (p_inicio[0] + p_fin[0]) / 2.0
        ctrl_y = (p_inicio[1] + p_fin[1]) / 2.0 + sag

        puntos = []
        pasos = 14
        for i in range(pasos + 1):
            t = i / pasos
            bx = (1 - t) ** 2 * p_inicio[0] + 2 * (1 - t) * t * ctrl_x + t ** 2 * p_fin[0]
            by = (1 - t) ** 2 * p_inicio[1] + 2 * (1 - t) * t * ctrl_y + t ** 2 * p_fin[1]
            puntos.append((bx, by))

        pygame.draw.lines(superficie, col_soga_ext, False, puntos, 4)
        pygame.draw.lines(superficie, col_soga_int, False, puntos, 2)
    else:
        # Soga tensa recta
        pygame.draw.line(superficie, (160, 110, 50), p_inicio, p_fin, 4)
        pygame.draw.line(superficie, (225, 180, 110), p_inicio, p_fin, 2)

    pygame.draw.circle(superficie, col_soga_ext, p_inicio, 4)
    pygame.draw.circle(superficie, col_soga_int, p_inicio, 2)
    pygame.draw.circle(superficie, col_soga_ext, p_fin, 4)
    pygame.draw.circle(superficie, col_soga_int, p_fin, 2)


# ==============================================================================
# ELEMENTOS VISUALES SUBMARINOS — MUNDO 3: EL JARDÍN DE ALGAS
# ==============================================================================

_CACHE_FONDO_MUNDO3 = {}


def dibujar_submarino_fondo_escenario(superficie, ancho_mundo, tick=0):
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

    superficie.blit(_CACHE_FONDO_MUNDO3[ancho_mundo], (0, 0))

    # Rayos de sol volumétricos que filtran desde la superficie
    paso_rayo = 380
    for rx in range(80, ancho_mundo + 200, paso_rayo):
        oscilacion = math.sin((tick * 0.02) + (rx * 0.005)) * 25.0
        x_base = rx + oscilacion
        ancho_rayo = 90
        poly_pts = [
            (x_base, 0),
            (x_base + ancho_rayo, 0),
            (x_base + ancho_rayo - 120, 520),
            (x_base - 140, 520),
        ]
        s_rayo = pygame.Surface((ancho_mundo, 520), pygame.SRCALPHA)
        alpha_rayo = int(20 + 8 * math.sin(tick * 0.03 + rx))
        pygame.draw.polygon(s_rayo, (220, 245, 255, max(10, alpha_rayo)), poly_pts)
        superficie.blit(s_rayo, (0, 0))

    # Ondulación translúcida en la superficie superior del agua (y = 0..25)
    for wx in range(0, ancho_mundo, 24):
        onda_y = int(math.sin((wx + tick * 2.0) * 0.06) * 3)
        pygame.draw.line(superficie, (180, 235, 255), (wx, 10 + onda_y), (wx + 16, 10 + onda_y), 2)


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
        s_burb = pygame.Surface((br * 2 + 2, br * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s_burb, (180, 235, 255, 140), (br + 1, br + 1), br)
        pygame.draw.circle(s_burb, (255, 255, 255, 210), (br + 1, br + 1), br, width=1)
        pygame.draw.circle(s_burb, (255, 255, 255, 240), (br - 1, br - 1), max(1, br // 3))
        superficie.blit(s_burb, (bx - br - 1, by - br - 1))

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
    pedestal_puerta = pygame.Rect(2420, y_suelo - 15, 150, 15)
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


def obtener_superficies_luz_linterna(radio_linterna=145, radio_tenue=34):
    """
    Crea o retorna en caché las superficies circulares de luz para las linternas de Mundo 3 Nivel 4:
    - Haz principal de la linterna: radio 145px con gradiente radial suave.
    - Resplandor personal tenue: radio 34px (cuando la linterna está apagada).
    """
    global _SURF_LUZ_LINTERNA, _SURF_LUZ_TENUE
    if _SURF_LUZ_LINTERNA is not None and _SURF_LUZ_TENUE is not None:
        return _SURF_LUZ_LINTERNA, _SURF_LUZ_TENUE

    diam_linterna = radio_linterna * 2
    s_linterna = pygame.Surface((diam_linterna, diam_linterna), pygame.SRCALPHA)
    for r in range(radio_linterna, 0, -2):
        frac = r / float(radio_linterna)
        alpha = int(255 * (1.0 - frac * frac))
        pygame.draw.circle(s_linterna, (alpha, alpha, alpha, alpha), (radio_linterna, radio_linterna), r)
    _SURF_LUZ_LINTERNA = s_linterna

    diam_tenue = radio_tenue * 2
    s_tenue = pygame.Surface((diam_tenue, diam_tenue), pygame.SRCALPHA)
    for r in range(radio_tenue, 0, -2):
        frac = r / float(radio_tenue)
        alpha = int(210 * (1.0 - frac))
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


def dibujar_oscuridad_laberinto(superficie, jugadores_info, surf_oscuridad, surf_luz, surf_tenue):
    """
    Aplica la capa de oscuridad total sobre el mundo y substrae los haces de luz circulares
    de las linternas activas de cada personaje:
    - jugadores_info: lista de tuplas (jugador, linterna_activa, completado)
    - Ilumina únicamente un círculo alrededor de cada personaje (~145px cuando linterna está ON).
    - Cuando la linterna está OFF, solo queda un resplandor personal tenue (~34px).
    - Los elementos fuera del haz de luz (rocas, trampas, llave, puerta) quedan ocultos en la penumbra.
    """
    for jugador, linterna_on, completado in jugadores_info:
        if not completado and not jugador.get("muerte_terminada", False):
            dibujar_linterna_minero(superficie, jugador, linterna_on and not jugador.get("muerto", False))

    surf_oscuridad.fill((4, 7, 14, 252))

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

    superficie.blit(surf_oscuridad, (0, 0))


def dibujar_linternas_submarinas_m3_n5(superficie, jugadores_info, tick=0):
    """
    Renderiza el sistema de linternas submarinas independientes para Mundo 3 Nivel 5:
    - Cada personaje porta su linterna de buceo montada en la cabeza.
    - Cuando está encendida, emite un haz de luz cónico con degradado suave y partículas
      que acompaña al buceador e ilumina el océano frente a él.
    - El escenario completo permanece 100% visible en todo momento (no se oscurece la pantalla).
    - Cuando está apagada, la linterna frontal permanece apagada sin proyectar haz de luz.
    """
    s_haz_local = pygame.Surface((340, 180), pygame.SRCALPHA)

    for jugador, linterna_on, completado in jugadores_info:
        if completado or jugador.get("muerte_terminada", False):
            continue

        esta_muerto = jugador.get("muerto", False)
        # 1. Dibujar linterna frontal en la cabeza del buceador
        dibujar_linterna_minero(superficie, jugador, linterna_on and not esta_muerto)

        # 2. Si está encendida y vivo, proyectar el haz de luz submarino direccional
        if linterna_on and not esta_muerto:
            hx = jugador["hitbox"].centerx
            hy = jugador["hitbox"].top + 10
            dir_mirar = 1 if jugador.get("mirando_derecha", True) else -1
            lamp_x = hx + dir_mirar * 12
            lamp_y = hy - 2

            s_haz_local.fill((0, 0, 0, 0))

            ox = 60 if dir_mirar > 0 else 280
            oy = 90

            # Aura radial suave alrededor del buceador
            for r_aura, a_aura in [(80, 10), (60, 18), (40, 26)]:
                pygame.draw.circle(s_haz_local, (215, 240, 255, a_aura), (ox - dir_mirar * 12, oy), r_aura)

            # Capas cónicas del haz de luz con degradado suave y leve oscilación marina
            flicker = math.sin(tick * 0.08) * 2.5
            capas_haz = [
                (250, 56, (200, 235, 255, 14)),
                (210, 44, (215, 245, 255, 24)),
                (170, 32, (240, 250, 255, 38)),
                (120, 20, (255, 252, 225, 58)),
                (65, 11, (255, 255, 240, 85)),
            ]
            for largo, apertura, col in capas_haz:
                pts = [
                    (ox, oy - 3),
                    (ox + dir_mirar * largo, int(oy - apertura + flicker)),
                    (ox + dir_mirar * largo, int(oy + apertura + flicker)),
                    (ox, oy + 3),
                ]
                pygame.draw.polygon(s_haz_local, col, pts)

            # Resplandor frontal en la lente
            pygame.draw.circle(s_haz_local, (255, 250, 210, 130), (ox, oy), 14)
            pygame.draw.circle(s_haz_local, (255, 255, 255, 200), (ox, oy), 6)

            # Partículas / motas de luz flotando en suspensión dentro del haz acuático
            for i, (offset_base, y_base_m, r_mota, alpha_base) in enumerate([
                (45, 4, 2, 95), (95, -7, 3, 115), (145, 11, 2, 90), (195, -5, 2, 75)
            ]):
                fase = tick * 0.06 + i * 1.5
                desp_x = ox + dir_mirar * (offset_base + math.sin(fase) * 6)
                desp_y = oy + y_base_m + math.cos(fase * 1.2) * 5
                pygame.draw.circle(s_haz_local, (255, 255, 240, alpha_base), (int(desp_x), int(desp_y)), r_mota)

            superficie.blit(s_haz_local, (lamp_x - ox, lamp_y - oy))


def _dibujar_hud_linternas_m3_n4(pantalla_surf, linterna_p1, linterna_p2, p1_color, p2_color, y_base=22):
    """
    Dibuja un HUD estilizado y claro indicando el estado
    y los controles de las linternas independientes de cada jugador:
    - P1: [E] ON / OFF
    - P2: [L] ON / OFF
    """
    fuente_hud = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)

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
    pedestal_puerta = pygame.Rect(2420, y_suelo - 15, 150, 15)
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

    return {
        "rocas": rocas,
        "barreras": barreras,
        "corales": corales,
        "algas": algas,
        "pinchos": pinchos,
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
    fuente_aire = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 12, bold=True)
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
    fuente_hud = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 12, bold=True)
    fuente_pct = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 11, bold=True)

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


def dibujar_alerta_oxigeno_personaje(superficie, jugador, oxigeno, tick):
    """Muestra un icono flotante de advertencia cuando el personaje está a punto de ahogarse."""
    if jugador.get("muerto", False) or oxigeno >= 22.0:
        return
    if (tick // 12) % 2 == 0:
        hx = jugador["hitbox"].centerx
        hy = jugador["hitbox"].top - 18
        s_alerta = pygame.Surface((38, 16), pygame.SRCALPHA)
        pygame.draw.rect(s_alerta, (230, 40, 50, 220), (0, 0, 38, 16), border_radius=8)
        fuente_aviso = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 10, bold=True)
        lbl = fuente_aviso.render("! O2", True, (255, 255, 255))
        s_alerta.blit(lbl, ((38 - lbl.get_width()) // 2, (16 - lbl.get_height()) // 2))
        superficie.blit(s_alerta, (hx - 19, hy))


def iniciar_mundo(
    mecanicas=None,
    numero_nivel=1,
    color_p1=None,
    color_p2=None,
    mundo=1,
    niveles_desbloqueados=None,
    partida_id=None,
    partida_nombre=None,
    snapshot_guardado=None,
    accesorio_p1=None,
    accesorio_p2=None,
    partida_password=None,
):
    numero_mundo = mundo
    p1_acc = accesorio_p1 if accesorio_p1 else "Ninguno"
    p2_acc = accesorio_p2 if accesorio_p2 else "Ninguno"
    if mecanicas is None:
        mecanicas = []

    if niveles_desbloqueados is None:
        niveles_desbloqueados = crear_desbloqueados_inicial()

    hay_siguiente_nivel = not (numero_mundo >= 3 and numero_nivel >= 5)

    usar_caja = "caja" in mecanicas
    usar_soga = "soga" in mecanicas
    usar_agua = "agua" in mecanicas
    usar_pinchos = "pinchos" in mecanicas
    usar_llave = True

    linterna_p1 = True
    linterna_p2 = True
    surf_oscuridad_m3_n4 = None
    surf_luz_linterna = None
    surf_luz_tenue = None

    oxigeno_p1 = 100.0
    oxigeno_p2 = 100.0
    OXIGENO_MAX = 100.0
    camaras_aire = []
    corrientes_marinas = []

    pantalla = pygame.display.get_surface()
    if pantalla is None:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))

    mundo_rect = pygame.Rect(0, 0, ANCHO_MUNDO, ALTO)
    reloj = pygame.time.Clock()
    fuente_tut = obtener_fuente_texto(TAMANO_TEXTO_GRANDE, tamano_fallback=32)

    W_BOTON_HUD, H_BOTON_HUD = 44, 52
    MARGEN_DER, MARGEN_SUP, ESPACIO_BOTONES = 18, 16, 12

    rect_btn_x = pygame.Rect(pantalla.get_width() - MARGEN_DER - W_BOTON_HUD, MARGEN_SUP, W_BOTON_HUD, H_BOTON_HUD)
    rect_btn_reiniciar = pygame.Rect(rect_btn_x.left - ESPACIO_BOTONES - W_BOTON_HUD, MARGEN_SUP, W_BOTON_HUD, H_BOTON_HUD)
    rect_btn_casa = pygame.Rect(rect_btn_reiniciar.left - ESPACIO_BOTONES - W_BOTON_HUD, MARGEN_SUP, W_BOTON_HUD, H_BOTON_HUD)
    rect_btn_config = pygame.Rect(rect_btn_casa.left - ESPACIO_BOTONES - W_BOTON_HUD, MARGEN_SUP, W_BOTON_HUD, H_BOTON_HUD)

    def _cargar_hud(nombre):
        return cargar_boton_escalado(nombre, W_BOTON_HUD, H_BOTON_HUD)

    spr_x_normal = _cargar_hud("boton-x.png")
    spr_x_semi = _cargar_hud("boton-x-semiapretado.png")
    spr_x_apretado = _cargar_hud("boton-x-apretado.png")
    spr_x_hover = aclarar_boton(spr_x_normal)

    spr_reiniciar_normal = _cargar_hud("boton-reiniciar-icono.png")
    spr_reiniciar_semi = _cargar_hud("boton-reiniciar-icono-semiapretado.png")
    spr_reiniciar_apretado = _cargar_hud("boton-reiniciar-icono-apretado.png")
    spr_reiniciar_hover = aclarar_boton(spr_reiniciar_normal)

    spr_casa_normal = _cargar_hud("boton-casa.png")
    spr_casa_semi = _cargar_hud("boton-casa-semiapretado.png")
    spr_casa_apretado = _cargar_hud("boton-casa-apretado.png")
    spr_casa_hover = aclarar_boton(spr_casa_normal)

    spr_config_normal = _cargar_hud("boton-configuracion.png")
    spr_config_semi = _cargar_hud("boton-configuracion-semiapretado.png")
    spr_config_apretado = _cargar_hud("boton-configuracion-apretado.png")
    spr_config_hover = aclarar_boton(spr_config_normal)

    fondo_btn_config = None
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

        fuente_tecla = obtener_fuente_boton(int(TAM_BTN_TUT * 0.58), negrita=True)
        txt_surf = fuente_tecla.render(str(letra_fallback).upper(), True, color_letra)
        rect_txt = txt_surf.get_rect(center=(TAM_BTN_TUT // 2, TAM_BTN_TUT // 2 - 1))
        surf.blit(txt_surf, rect_txt)
        return surf

    def _crear_etiqueta_jugador(texto, color_nombre):
        color_base = COLORES_PERSONAJES.get(color_nombre, (124, 231, 255))
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
        if not p1_completado and not jugador1["muerto"] and not p1_soplado and alpha_p1 > 0:
            _dibujar_cluster_jugador(
                superficie, jugador1, badge_p1,
                btn_w, btn_a, btn_s, btn_d,
                pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                teclas_actuales, alpha=int(alpha_p1), bottom_override=bottom_p1
            )

        # Dibujar Flechas directamente sobre Jugador 2
        if not p2_completado and not jugador2["muerto"] and not p2_soplado and alpha_p2 > 0:
            _dibujar_cluster_jugador(
                superficie, jugador2, badge_p2,
                btn_arr, btn_izq, btn_aba, btn_der,
                pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT,
                teclas_actuales, alpha=int(alpha_p2), bottom_override=bottom_p2
            )

    def _crear_efecto_soplar(jugador_quieto, es_p1, dir_viento):
        alto_grid = 2 * TAM_BTN_TUT + GAP_BTN_TUT
        badge_ref = badge_p1 if es_p1 else badge_p2
        alto_total = badge_ref.get_height() + 4 + alto_grid
        ancho_grid = 3 * TAM_BTN_TUT + 2 * GAP_BTN_TUT

        left_cluster = jugador_quieto["hitbox"].centerx - ancho_grid // 2
        top_cluster = (jugador_quieto["hitbox"].top - 8) - alto_total

        y_grid_offset = badge_ref.get_height() + 4
        col0_x = 0
        col1_x = TAM_BTN_TUT + GAP_BTN_TUT
        col2_x = 2 * (TAM_BTN_TUT + GAP_BTN_TUT)
        row1_y = TAM_BTN_TUT + GAP_BTN_TUT

        if es_p1:
            badge_surf = badge_p1
            btn_arr_surf = btn_w
            btn_izq_surf = btn_a
            btn_aba_surf = btn_s
            btn_der_surf = btn_d
        else:
            badge_surf = badge_p2
            btn_arr_surf = btn_arr
            btn_izq_surf = btn_izq
            btn_aba_surf = btn_aba
            btn_der_surf = btn_der

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
                "x": float(left_cluster + col1_x + TAM_BTN_TUT // 2),
                "y": float(top_cluster + y_grid_offset + TAM_BTN_TUT // 2),
                "vx": dir_viento * random.uniform(6.0, 8.0),
                "vy": random.uniform(-3.5, -2.0),
                "rot": 0.0,
                "rot_vel": dir_viento * random.uniform(3.0, 5.5),
                "alpha": 255.0,
            },
            # Tecla izquierda
            {
                "surf": btn_izq_surf,
                "x": float(left_cluster + col0_x + TAM_BTN_TUT // 2),
                "y": float(top_cluster + y_grid_offset + row1_y + TAM_BTN_TUT // 2),
                "vx": dir_viento * (random.uniform(8.5, 11.0) if dir_viento < 0 else random.uniform(4.5, 6.5)),
                "vy": random.uniform(-2.5, -1.0),
                "rot": 0.0,
                "rot_vel": dir_viento * random.uniform(3.5, 6.0),
                "alpha": 255.0,
            },
            # Tecla abajo
            {
                "surf": btn_aba_surf,
                "x": float(left_cluster + col1_x + TAM_BTN_TUT // 2),
                "y": float(top_cluster + y_grid_offset + row1_y + TAM_BTN_TUT // 2),
                "vx": dir_viento * random.uniform(5.5, 7.5),
                "vy": random.uniform(-1.0, 0.5),
                "rot": 0.0,
                "rot_vel": dir_viento * random.uniform(2.0, 4.5),
                "alpha": 255.0,
            },
            # Tecla derecha
            {
                "surf": btn_der_surf,
                "x": float(left_cluster + col2_x + TAM_BTN_TUT // 2),
                "y": float(top_cluster + y_grid_offset + row1_y + TAM_BTN_TUT // 2),
                "vx": dir_viento * (random.uniform(8.5, 11.0) if dir_viento > 0 else random.uniform(4.5, 6.5)),
                "vy": random.uniform(-2.5, -1.0),
                "rot": 0.0,
                "rot_vel": dir_viento * random.uniform(3.5, 6.0),
                "alpha": 255.0,
            },
        ]

        for p in piezas:
            teclas_sopladas.append(p)

        # Líneas de viento estilo pixel art
        for _ in range(10):
            lineas_viento.append({
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
            lineas_viento.append({
                "tipo": "particula",
                "x": float(left_cluster + random.randint(-10, ancho_grid + 10)),
                "y": float(top_cluster + random.randint(0, alto_total)),
                "tam": random.choice([2, 3]),
                "vx": dir_viento * random.uniform(7.0, 12.0),
                "vy": random.uniform(-1.5, 0.5),
                "alpha": 240.0,
                "fade": random.uniform(7.0, 10.0),
            })

    def _actualizar_y_dibujar_soplado(superficie):
        # 1. Actualizar y dibujar líneas y partículas de viento
        activas_viento = []
        for elem in lineas_viento:
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
        lineas_viento[:] = activas_viento

        # 2. Actualizar y dibujar teclas sopladas con rotación y desvanecimiento
        activas_teclas = []
        for pieza in teclas_sopladas:
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
        teclas_sopladas[:] = activas_teclas

    boton_nivel = None
    pared_nivel = None
    dintel_superior = None
    laser_nivel = None
    pozo_nivel = None
    paredes_colores = None
    botones_colores = None
    plataformas_base = None
    barrera_l_horiz = None
    barrera_l_vert = None
    boton_compuerta = None
    compuerta = None
    plataforma_movil = None
    bloque_central = None
    bloque_peligroso = None
    plat_elevada = None
    plataformas_derrumbables = None
    plataformas_alternadas = None
    rocas_submarinas = None
    barreras_algas = None
    corales_decorativos = None
    algas_decorativas = None
    burbujas_m3 = None
    tick_m3 = 0
    estado_soga = crear_estado_soga()

    if numero_mundo == 1 and numero_nivel == 1:
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

    elif numero_mundo == 1 and numero_nivel == 2:
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

    elif numero_mundo == 1 and numero_nivel == 3:
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

    elif numero_mundo == 1 and numero_nivel == 4:
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
    elif numero_mundo == 1 and numero_nivel == 5:
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
    elif numero_mundo == 2 and numero_nivel == 1:
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

        # Pozo y pinchos mortales debajo de la zona aérea extendidos de forma continua hasta el final del nivel
        pozo_nivel = {
            "x": 920,
            "y": 570,
            "ancho": ancho_mundo_nivel - 920,
            "alto": 70,
        }
        pinchos = [pygame.Rect(x, suelo.top - 24, 32, 24) for x in range(926, ancho_mundo_nivel - 20, 35)]

        # Llave cerca del final del recorrido sobre la plataforma de destino
        llave = crear_llave(1820, plat_destino.top - 46)

        # Puerta de salida en la plataforma de destino
        puerta = crear_puerta(2040, plat_destino.top - 90)
    elif numero_mundo == 2 and numero_nivel == 2:
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

        # Abismo continuo con pinchos mortales cubriendo todo el recorrido debajo de la plataforma móvil
        pozo_nivel = {
            "x": 360,
            "y": 570,
            "ancho": ancho_mundo_nivel - 360,
            "alto": 70,
        }
        pinchos = [pygame.Rect(x, suelo.top - 24, 32, 24) for x in range(366, ancho_mundo_nivel - 20, 35)]

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
    elif numero_mundo == 2 and numero_nivel == 3:
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

        # 3. Abismo de pinchos mortales continuo y denso en el fondo del pozo (x: 260 a 1430)
        pozo_nivel = {
            "x": 260,
            "y": 570,
            "ancho": 1170,
            "alto": 70,
        }
        # Hilera continua de pinchos más juntos (separación reducida a 22px, sin huecos entre ellos)
        pinchos = [crear_pincho(x, suelo.top - 28, 25, 28, direccion="arriba") for x in range(262, 1420, 22)]

        # Pinchos laterales en las paredes del abismo (aumentan la dificultad si el péndulo se acerca a los extremos)
        pinchos_pared_izq = [crear_pincho(260, y, 22, 26, direccion="derecha") for y in range(390, 600, 32)]
        pinchos_pared_der = [crear_pincho(1380 - 22, y, 22, 26, direccion="izquierda") for y in range(390, 600, 32)]
        pinchos.extend(pinchos_pared_izq + pinchos_pared_der)

        # Lecho elevado de pinchos más cerca de la trayectoria del balanceo (acerca el peligro verticalmente)
        pinchos_elevados = [crear_pincho(x, 520, 24, 26, direccion="arriba") for x in range(560, 800, 24)]
        pinchos.extend(pinchos_elevados)

        # 4. Bloque peligroso rojo y pinchos dobles arriba, abajo y alrededor
        # Ubicado en la zona del abismo como obstáculo central que desafía el balanceo sin bloquearlo
        bx, by, bw, bh = 880, 440, 70, 60
        bloque_peligroso = {
            "rect": pygame.Rect(bx, by, bw, bh),
            "x": bx,
            "y": by,
            "ancho": bw,
            "alto": bh,
        }

        # Pinchos dobles y más cerrados alrededor del bloque rojo
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
            bloque_peligroso["rect"],
            plat_llegada,
            plat_llegada_base,
        ]

        # 6. Llave ubicada en la trayectoria del péndulo más allá del bloque rojo
        llave = crear_llave(1020, 360)

        # 7. Puerta de salida en la plataforma segura de llegada
        puerta = crear_puerta(2050, 360 - 90)
    elif numero_mundo == 2 and numero_nivel == 4:
        # Mundo 2 — Nivel 4: «Las plataformas que se derrumban» (Niveles.pdf, página 8)
        # Objetivo: cruzar un abismo lleno de pinchos, conseguir la llave y llegar a la puerta de salida sin caer.
        # Mecánica principal: Las plataformas son temporales y se derrumban aproximadamente 1 segundo (60 frames) tras ser pisadas.
        # Los personajes están unidos por una soga y deben sincronizar sus saltos rápidamente antes de que caigan.
        # A mitad del recorrido se encuentra la llave, sobre las plataformas suspendidas sobre el abismo.
        # Si un personaje cae al abismo o toca los pinchos, ambos pierden y el nivel se reinicia.
        ancho_mundo_nivel = 2400
        suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
        mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

        usar_caja = False
        usar_soga = True
        usar_agua = False
        usar_pinchos = True
        usar_llave = True

        # Plataforma inicial segura (x: 0..240, y=460)
        plat_inicio = pygame.Rect(0, 460, 240, 26)
        plat_inicio_base = pygame.Rect(0, 486, 240, suelo.top - 486 + 80)

        # Ambos personajes inician unidos por la soga en el lado izquierdo
        jugador1 = crear_personaje(60, 460 - ALTO_HITBOX, p1_color)
        jugador2 = crear_personaje(150, 460 - ALTO_HITBOX, p2_color)

        caja = None

        # Abismo continuo cubierto de pinchos mortales debajo de todas las plataformas (x: 240..1960)
        pozo_nivel = {
            "x": 240,
            "y": 570,
            "ancho": 1720,
            "alto": 70,
        }
        pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(245, 1955, 35)]

        # Plataforma final de llegada con la puerta (x: 1960..2400, y=460)
        plat_llegada = pygame.Rect(1960, 460, 440, 26)
        plat_llegada_base = pygame.Rect(1960, 486, 440, suelo.top - 486 + 80)

        plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]

        # Serie de 8 plataformas pequeñas que se derrumban 1.0 segundo (60 frames) tras pisarlas
        def _crear_p_derrumbable(px, py, pw=120, ph=22):
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
            (310, 460),
            (510, 430),
            (720, 460),
            (930, 420),   # Plataforma central con la llave
            (1140, 450),
            (1350, 410),
            (1560, 440),
            (1770, 460),
        ]
        plataformas_derrumbables = [_crear_p_derrumbable(px, py) for px, py in coords_plats]
        plataformas = list(plataformas_base) + [p["rect"] for p in plataformas_derrumbables]

        # Llave a mitad del recorrido sobre la 4ta plataforma
        llave = crear_llave(975, 420 - 46)

        # Puerta de salida en la plataforma de destino
        puerta = crear_puerta(2220, 460 - 90)
    elif numero_mundo == 2 and numero_nivel == 5:
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
        pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(165, 725, 32)]

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
    elif numero_mundo == 3 and numero_nivel == 1:
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
    elif numero_mundo == 3 and numero_nivel == 2:
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
    elif numero_mundo == 3 and numero_nivel == 3:
        # Nivel 3-3: Las rocas peligrosas (Mundo Submarino)
        # - Pasillos estrechos con estalactitas, estalagmitas y formaciones rocosas marinas.
        # - Pinchos y erizos submarinos mortales sobresaliendo tanto del suelo como del techo y cornisas.
        # - Los personajes se mueven de forma independiente (sin cuerda, según las reglas de Mundo 3) en 4 direcciones.
        # - Maniobras de precisión obligatorias para esquivar los pinchos; si cualquiera toca uno, ambos mueren.
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

        # Formaciones rocosas que definen los pasillos estrechos
        rocas_submarinas = [
            # Zona 1: Entrada y primer estrechamiento (x = 0 .. 440)
            {"rect": pygame.Rect(320, techo_agua.bottom, 130, 95)},
            {"rect": pygame.Rect(320, 520, 130, suelo.top - 520)},

            # Zona 2: Desfiladero serpenteante en S (x = 450 .. 1120)
            {"rect": pygame.Rect(480, techo_agua.bottom, 210, 240)},
            {"rect": pygame.Rect(720, 390, 190, suelo.top - 390)},
            {"rect": pygame.Rect(700, techo_agua.bottom, 230, 90)},
            {"rect": pygame.Rect(940, techo_agua.bottom, 180, 230)},

            # Zona 3: Gran bifurcación y Gruta de la Llave (x = 1140 .. 1720)
            {"rect": pygame.Rect(1140, techo_agua.bottom, 480, 75)},
            {"rect": pygame.Rect(1200, 270, 360, 120), "coral": True, "color_coral": (245, 110, 140)},
            {"rect": pygame.Rect(1350, 220, 80, 20), "coral": True, "color_coral": (255, 180, 80)},
            {"rect": pygame.Rect(1240, 530, 260, suelo.top - 530)},

            # Zona 4: Laberinto de pilares y colmillos de roca (x = 1750 .. 2320)
            {"rect": pygame.Rect(1780, techo_agua.bottom, 85, 300)},
            {"rect": pygame.Rect(1940, 310, 85, suelo.top - 310)},
            {"rect": pygame.Rect(2100, techo_agua.bottom, 85, 290)},
            {"rect": pygame.Rect(2090, 530, 105, suelo.top - 530)},

            # Zona 5: Terraza final de llegada con la puerta (x = 2380 .. 2700)
            {"rect": pygame.Rect(2380, 480, 320, suelo.top - 480), "coral": True, "color_coral": (255, 140, 80)},
        ]

        # Obstáculos mortales: erizos de mar y corales puntiagudos en suelo y techo
        pinchos = [
            # Zona 1: Primer estrechamiento
            crear_pincho(340, techo_agua.bottom + 95, 75, 24, direccion="abajo"),
            crear_pincho(340, 520 - 24, 75, 24, direccion="arriba"),

            # Zona 2: Serpentín en S
            crear_pincho(520, techo_agua.bottom + 240, 130, 24, direccion="abajo"),
            crear_pincho(540, suelo.top - 24, 100, 24, direccion="arriba"),
            crear_pincho(740, 390 - 24, 145, 24, direccion="arriba"),
            crear_pincho(735, techo_agua.bottom + 90, 150, 24, direccion="abajo"),
            crear_pincho(965, techo_agua.bottom + 230, 125, 24, direccion="abajo"),
            crear_pincho(980, suelo.top - 24, 100, 24, direccion="arriba"),

            # Zona 3: La gruta de la llave
            crear_pincho(1200, techo_agua.bottom + 75, 110, 24, direccion="abajo"),
            crear_pincho(1460, techo_agua.bottom + 75, 110, 24, direccion="abajo"),
            crear_pincho(1210, 270 - 24, 100, 24, direccion="arriba"),
            crear_pincho(1465, 270 - 24, 90, 24, direccion="arriba"),
            crear_pincho(1280, 390, 140, 24, direccion="abajo"),
            crear_pincho(1285, 530 - 24, 150, 24, direccion="arriba"),

            # Zona 4: Pilares y desfiladero final
            crear_pincho(1785, techo_agua.bottom + 300, 75, 24, direccion="abajo"),
            crear_pincho(1775, suelo.top - 24, 95, 24, direccion="arriba"),
            crear_pincho(1945, 310 - 24, 75, 24, direccion="arriba"),
            crear_pincho(1940, techo_agua.bottom, 85, 24, direccion="abajo"),
            crear_pincho(2105, techo_agua.bottom + 290, 75, 24, direccion="abajo"),
            crear_pincho(2095, 530 - 24, 95, 24, direccion="arriba"),
        ]

        barreras_algas = [
            {"rect": pygame.Rect(1620, 420, 35, suelo.top - 420)},
        ]

        # Plataformas sólidas combinadas
        plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
        plataformas = list(plataformas_base)

        # La llave sobre la repisa segura en la gruta
        llave = crear_llave(1378, 220 - 46)

        # Puerta de salida en la terraza final
        puerta = crear_puerta(2480, 480 - 90)

        # Corales decorativos temáticos
        corales_decorativos = [
            # Entrada
            {"tipo": "ramificado", "x": 160, "y": suelo.top, "escala": 1.1, "fase": 0.4, "color": (250, 95, 135), "color_sec": (255, 185, 205), "anclaje": "abajo"},
            # Gruta de la llave
            {"tipo": "anemona", "x": 1390, "y": 220, "escala": 1.15, "fase": 1.2, "color": (255, 210, 60), "color_sec": (255, 255, 180), "anclaje": "abajo"},
            {"tipo": "ramificado", "x": 1345, "y": 220, "escala": 0.85, "fase": 0.5, "color": (255, 105, 145), "color_sec": (255, 185, 205), "anclaje": "abajo"},
            {"tipo": "tubular", "x": 1435, "y": 220, "escala": 0.85, "fase": 2.2, "color": (45, 195, 180), "color_sec": (130, 245, 230), "anclaje": "abajo"},
            {"tipo": "cerebro", "x": 1280, "y": 270, "escala": 1.0, "fase": 3.0, "color": (230, 110, 180), "color_sec": (255, 185, 225), "anclaje": "abajo"},
            {"tipo": "abanico", "x": 1500, "y": 270, "escala": 0.95, "fase": 1.8, "color": (175, 95, 220), "color_sec": (225, 170, 255), "anclaje": "abajo"},
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
    elif numero_mundo == 3 and numero_nivel == 4:
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

        plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
        plataformas = list(plataformas_base)

        llave = crear_llave(datos_lab["llave_x"], datos_lab["llave_y"])
        puerta = crear_puerta(datos_lab["puerta_x"], datos_lab["puerta_y"])

        burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)
        tick_m3 = 0

        surf_oscuridad_m3_n4 = pygame.Surface((ancho_mundo_nivel, ALTO), pygame.SRCALPHA)
        surf_luz_linterna, surf_luz_tenue = obtener_superficies_luz_linterna()
    elif numero_mundo == 3 and numero_nivel == 5:
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
            {"rect": pygame.Rect(2180, 220, 240, 320), "fuerza_x": 1.8, "fuerza_y": -1.8, "direccion": "arriba"},
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
            {"rect": pygame.Rect(1400, techo_agua.bottom, 220, 380)},
            {"rect": pygame.Rect(1640, techo_agua.bottom, 340, 240)},
            {"rect": pygame.Rect(1640, 480, 140, suelo.top - 480)},

            # Repisa abisal donde reposa la llave dorada
            {"rect": pygame.Rect(1780, 590, 110, suelo.top - 590), "coral": True, "color_coral": (255, 135, 70)},

            # Sector 5: Pared antes del refugio y terraza
            {"rect": pygame.Rect(1980, 270, 110, suelo.top - 270)},
            {"rect": pygame.Rect(2210, techo_agua.bottom, 180, 200)},
            {"rect": pygame.Rect(2210, 540, 180, suelo.top - 540)},

            # Terraza final de llegada con la puerta
            {"rect": pygame.Rect(2390, 440, 210, suelo.top - 440), "coral": True, "color_coral": (255, 140, 80)},
        ]

        barreras_algas = [
            {"rect": pygame.Rect(1380, 380, 30, suelo.top - 380)},
        ]

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
            crear_pincho(2210, techo_agua.bottom + 200, 100, 24, direccion="abajo"),
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

        burbujas_m3 = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)
        tick_m3 = 0
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
    mostrar_tutorial = (numero_mundo == 1 and numero_nivel == 1)
    contador_tutorial = 0
    frames_tutorial = 300  # Los controles duran 5 segundos antes de despejar la pantalla
    p1_movio = False
    p2_movio = False
    alpha_tut_p1 = 255.0
    alpha_tut_p2 = 255.0
    p1_soplado = False
    p2_soplado = False
    teclas_sopladas = []
    lineas_viento = []

    p1_sobre_p2 = False
    p2_sobre_p1 = False

    # Renderizar el fotograma inicial del escenario con los personajes en sus posiciones iniciales
    mundo_inicio = pygame.Surface((ancho_mundo_nivel, ALTO))

    if numero_mundo == 3:
        dibujar_submarino_fondo_escenario(mundo_inicio, ancho_mundo_nivel, 0)
        dibujar_lecho_marino(mundo_inicio, suelo, ancho_mundo_nivel)
        if algas_decorativas:
            dibujar_algas_decorativas_escenario(mundo_inicio, algas_decorativas, 0, capa="fondo")
        if corrientes_marinas:
            dibujar_corrientes_marinas_escenario(mundo_inicio, corrientes_marinas, 0)
        if camaras_aire:
            dibujar_camaras_aire_escenario(mundo_inicio, camaras_aire, 0)
        if rocas_submarinas:
            dibujar_rocas_submarinas_escenario(mundo_inicio, rocas_submarinas)
        if barreras_algas:
            dibujar_barreras_algas_escenario(mundo_inicio, barreras_algas, 0)
        if corales_decorativos:
            dibujar_corales_escenario(mundo_inicio, corales_decorativos, 0)
        if algas_decorativas:
            dibujar_algas_decorativas_escenario(mundo_inicio, algas_decorativas, 0, capa="frente")
        if pinchos:
            dibujar_peligros_marinos_escenario(mundo_inicio, pinchos)
        if burbujas_m3:
            actualizar_y_dibujar_burbujas_m3(mundo_inicio, burbujas_m3, [jugador1, jugador2], 0)
    else:
        mundo_inicio.fill((255, 240, 195))

        if pozo_nivel is not None:
            pz = pozo_nivel
            pygame.draw.rect(mundo_inicio, (235, 222, 192), (pz["x"], pz["y"], pz["ancho"], pz["alto"]))
            pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (pz["x"], pz["y"]), (pz["x"], pz["y"] + pz["alto"]), 2)
            pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (pz["x"] + pz["ancho"], pz["y"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

        for plat in plataformas:
            if barrera_l_horiz is not None and (plat is barrera_l_horiz or plat is barrera_l_vert):
                continue
            if bloque_central is not None and plat is bloque_central["rect"]:
                continue
            if plataforma_movil is not None and plat is plataforma_movil["rect"]:
                continue
            if compuerta is not None and plat is compuerta["rect"]:
                continue
            if plataformas_derrumbables is not None and any(plat is p_d["rect"] for p_d in plataformas_derrumbables):
                continue
            if plat.bottom >= suelo.top:
                rect_torre = pygame.Rect(plat.x, plat.y, plat.width, plat.height + 4)
                pygame.draw.rect(mundo_inicio, COLOR_PLATAFORMA, rect_torre, border_top_left_radius=4, border_top_right_radius=4)
                pygame.draw.rect(mundo_inicio, COLOR_BORDE_PLATAFORMA, rect_torre, width=2, border_top_left_radius=4, border_top_right_radius=4)
            else:
                pygame.draw.rect(mundo_inicio, COLOR_PLATAFORMA, plat, border_radius=4)
                pygame.draw.rect(mundo_inicio, COLOR_BORDE_PLATAFORMA, plat, width=2, border_radius=4)

        if barrera_l_horiz is not None and barrera_l_vert is not None:
            dibujar_barrera_l_escenario(mundo_inicio, barrera_l_horiz, barrera_l_vert)

        pygame.draw.rect(mundo_inicio, (225, 110, 80), suelo)
        if pozo_nivel is not None:
            pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (pz["x"], pz["y"] + pz["alto"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

        if pinchos:
            dibujar_pinchos_escenario(mundo_inicio, pinchos)
        if numero_mundo == 2 and numero_nivel == 3:
            dibujar_pendulo_escenario(mundo_inicio, plataformas, plat_elevada, pozo_nivel)
        if numero_mundo == 2 and numero_nivel == 4 and plataformas_derrumbables is not None:
            dibujar_plataformas_derrumbables_escenario(mundo_inicio, plataformas_derrumbables, pozo_nivel)
        if numero_mundo == 2 and numero_nivel == 5 and plataformas_alternadas is not None:
            dibujar_plataformas_alternadas_escenario(mundo_inicio, plataformas_alternadas, pozo_nivel)

    if boton_nivel is not None:
        rect_b = boton_nivel["rect"]
        h_actual = 4 if boton_nivel["presionado"] else 12
        y_actual = suelo.top - h_actual
        pygame.draw.rect(mundo_inicio, (90, 70, 60), (rect_b.left - 6, suelo.top - 4, rect_b.width + 12, 10), border_radius=2)
        col_btn = (80, 200, 100) if boton_nivel["presionado"] else (225, 65, 65)
        col_borde_btn = (50, 150, 70) if boton_nivel["presionado"] else (175, 45, 45)
        pygame.draw.rect(mundo_inicio, col_btn, (rect_b.x, y_actual, rect_b.width, h_actual), border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.rect(mundo_inicio, col_borde_btn, (rect_b.x, y_actual, rect_b.width, h_actual), width=2, border_top_left_radius=3, border_top_right_radius=3)

    if pared_nivel is not None:
        pr = pared_nivel["rect"]
        for y_linea in range(pr.top + 30, pr.bottom - 10, 35):
            if 0 <= y_linea <= ALTO:
                pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (pr.left + 4, y_linea), (pr.right - 4, y_linea), 2)

    if laser_nivel is not None:
        dibujar_laser_escenario(mundo_inicio, laser_nivel)

    if paredes_colores is not None:
        dibujar_paredes_colores_escenario(mundo_inicio, paredes_colores)

    if botones_colores is not None:
        dibujar_botones_colores_escenario(mundo_inicio, botones_colores, suelo)

    if boton_compuerta is not None:
        rect_bc = boton_compuerta["rect"]
        h_bc = 4 if boton_compuerta["presionado"] else 12
        y_bc = suelo.top - h_bc
        pygame.draw.rect(mundo_inicio, (90, 70, 60), (rect_bc.left - 6, suelo.top - 4, rect_bc.width + 12, 10), border_radius=2)
        col_bc = (220, 200, 60) if boton_compuerta["presionado"] else (245, 175, 40)
        col_borde_bc = (160, 140, 30) if boton_compuerta["presionado"] else (180, 120, 20)
        pygame.draw.rect(mundo_inicio, col_bc, (rect_bc.x, y_bc, rect_bc.width, h_bc), border_top_left_radius=3, border_top_right_radius=3)
        pygame.draw.rect(mundo_inicio, col_borde_bc, (rect_bc.x, y_bc, rect_bc.width, h_bc), width=2, border_top_left_radius=3, border_top_right_radius=3)

    if compuerta is not None and compuerta["rect"].width > 0:
        cr = compuerta["rect"]
        pygame.draw.rect(mundo_inicio, COLOR_PLATAFORMA, cr, border_radius=3)
        pygame.draw.rect(mundo_inicio, COLOR_BORDE_PLATAFORMA, cr, width=2, border_radius=3)
        for lx in range(cr.left + 12, cr.right - 8, 16):
            pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (lx, cr.top + 3), (lx, cr.bottom - 4), 2)

    if bloque_central is not None:
        br = bloque_central["rect"]
        pygame.draw.line(mundo_inicio, (110, 100, 95), (br.left + 12, 0), (br.left + 12, br.top), 3)
        pygame.draw.line(mundo_inicio, (110, 100, 95), (br.right - 12, 0), (br.right - 12, br.top), 3)
        pygame.draw.circle(mundo_inicio, (70, 65, 60), (br.left + 12, br.top), 4)
        pygame.draw.circle(mundo_inicio, (70, 65, 60), (br.right - 12, br.top), 4)
        pygame.draw.rect(mundo_inicio, (220, 50, 50), br, border_radius=4)
        pygame.draw.rect(mundo_inicio, (140, 25, 25), br, width=2, border_radius=4)
        for by in range(br.top + 16, br.bottom - 8, 16):
            pygame.draw.line(mundo_inicio, (160, 30, 30), (br.left + 4, by), (br.right - 4, by), 2)

    if plataforma_movil is not None:
        pm = plataforma_movil["rect"]
        pygame.draw.rect(mundo_inicio, COLOR_PLATAFORMA, pm, border_radius=4)
        pygame.draw.rect(mundo_inicio, COLOR_BORDE_PLATAFORMA, pm, width=2, border_radius=4)
        for rx in range(pm.left + 15, pm.right - 10, 22):
            pygame.draw.circle(mundo_inicio, (140, 60, 40), (rx, pm.bottom - 5), 3)
        col_ind = (80, 220, 100) if plataforma_movil["moviendo"] else ((240, 180, 40) if plataforma_movil["tiempo_con_peso"] > 0 else (180, 80, 55))
        pygame.draw.circle(mundo_inicio, col_ind, (pm.centerx, pm.centery), 4)

    if usar_agua:
        dibujar_agua(mundo_inicio, ZONA_AGUA)
    if usar_soga and not p1_completado and not p2_completado:
        dibujar_soga_escenario(mundo_inicio, jugador1, jugador2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    if usar_caja:
        mundo_inicio.blit(caja["sprite"], caja["rect"])

    if usar_llave and puerta:
        estado_p = "cerrada"
        mundo_inicio.blit(puerta["sprites"][estado_p], puerta["rect"])
        if llave:
            if numero_mundo == 3:
                halo_surf = pygame.Surface((44, 60), pygame.SRCALPHA)
                pygame.draw.ellipse(halo_surf, (255, 230, 90, 75), (0, 0, 44, 60))
                mundo_inicio.blit(halo_surf, (llave["rect"].centerx - 22, llave["rect"].centery - 30))
            mundo_inicio.blit(llave["sprite"], llave["rect"])

    dibujar_personaje(mundo_inicio, jugador1, ZONA_AGUA if usar_agua else None)
    dibujar_personaje(mundo_inicio, jugador2, ZONA_AGUA if usar_agua else None)

    if numero_mundo == 3 and numero_nivel == 4 and surf_oscuridad_m3_n4 is not None:
        dibujar_oscuridad_laberinto(
            mundo_inicio,
            [(jugador1, linterna_p1, False), (jugador2, linterna_p2, False)],
            surf_oscuridad_m3_n4,
            surf_luz_linterna,
            surf_luz_tenue
        )
    elif numero_mundo == 3 and numero_nivel == 5:
        dibujar_linternas_submarinas_m3_n5(
            mundo_inicio,
            [(jugador1, linterna_p1, False), (jugador2, linterna_p2, False)],
            0
        )

    distancia_ini = abs(jugador1["hitbox"].centerx - jugador2["hitbox"].centerx)
    if distancia_ini <= DISTANCIA_SPLIT:
        centro_ini = (jugador1["hitbox"].centerx + jugador2["hitbox"].centerx) // 2
        cam_ini_x = max(0, min(centro_ini - ANCHO // 2, ancho_mundo_nivel - ANCHO))
        pantalla.blit(mundo_inicio, (0, 0), pygame.Rect(cam_ini_x, 0, ANCHO, ALTO))
    else:
        ancho_m = ANCHO // 2
        p_izq = jugador1 if jugador1["hitbox"].centerx <= jugador2["hitbox"].centerx else jugador2
        p_der = jugador2 if p_izq is jugador1 else jugador1
        cam_izq_x = max(0, min(p_izq["hitbox"].centerx - ancho_m // 2, ancho_mundo_nivel - ancho_m))
        cam_der_x = max(0, min(p_der["hitbox"].centerx - ancho_m // 2, ancho_mundo_nivel - ancho_m))
        pantalla.blit(mundo_inicio, (0, 0), pygame.Rect(cam_izq_x, 0, ancho_m, ALTO))
        pantalla.blit(mundo_inicio, (ancho_m, 0), pygame.Rect(cam_der_x, 0, ancho_m, ALTO))
        pygame.draw.line(pantalla, (0, 0, 0), (ancho_m, 0), (ancho_m, ALTO), 4)

    fondo_btn_config = pantalla.subsurface(rect_btn_config).copy()
    fondo_btn_casa = pantalla.subsurface(rect_btn_casa).copy()
    fondo_btn_reiniciar = pantalla.subsurface(rect_btn_reiniciar).copy()
    fondo_btn_x = pantalla.subsurface(rect_btn_x).copy()

    if spr_config_normal: pantalla.blit(spr_config_normal, rect_btn_config)
    if spr_casa_normal: pantalla.blit(spr_casa_normal, rect_btn_casa)
    if spr_reiniciar_normal: pantalla.blit(spr_reiniciar_normal, rect_btn_reiniciar)
    if spr_x_normal: pantalla.blit(spr_x_normal, rect_btn_x)

    captura_nuevo_nivel = pantalla.copy()
    animar_apertura_franjas(pantalla, reloj, captura_nuevo_nivel)

    jugador1["accesorio"] = p1_acc
    jugador2["accesorio"] = p2_acc

    def _reiniciar_nivel_completo():
        nonlocal p1_completado, p2_completado, mostrar_tutorial, contador_tutorial
        nonlocal p1_movio, p2_movio, alpha_tut_p1, alpha_tut_p2, p1_soplado, p2_soplado, plataformas
        nonlocal rocas_submarinas, barreras_algas, corales_decorativos, algas_decorativas, plataformas_base, llave, pinchos, linterna_p1, linterna_p2
        nonlocal oxigeno_p1, oxigeno_p2, camaras_aire, corrientes_marinas

        reiniciar_juego(jugador1, jugador2, caja, llave, puerta, estado_soga=estado_soga)
        jugador1["accesorio"] = p1_acc
        jugador2["accesorio"] = p2_acc
        if boton_nivel is not None and pared_nivel is not None:
            boton_nivel["presionado"] = False
            pared_nivel["progreso"] = 0.0
            pared_nivel["y"] = pared_nivel["y_cerrada"]
            pared_nivel["rect"].y = int(pared_nivel["y_cerrada"])
        if laser_nivel is not None:
            laser_nivel["bloqueado"] = False
            pared_x = laser_nivel.get("pared_der_x", 1100)
            laser_nivel["x_fin"] = pared_x
            laser_nivel["rect_dano"].x = laser_nivel["emisor_rect"].right
            laser_nivel["rect_dano"].width = max(0, pared_x - laser_nivel["emisor_rect"].right)
        if botones_colores is not None and paredes_colores is not None:
            for btn in botones_colores:
                btn["presionado"] = False
            for pared in paredes_colores:
                pared["progreso"] = 0.0
                pared["rect"].y = int(pared["y_cerrada"])
        if boton_compuerta is not None and compuerta is not None:
            boton_compuerta["presionado"] = False
            compuerta["progreso"] = 0.0
            compuerta["rect"].x = 1700
            compuerta["rect"].width = 140
        if plataforma_movil is not None:
            plataforma_movil["x"] = plataforma_movil["x_inicial"]
            plataforma_movil["rect"].x = int(plataforma_movil["x_inicial"])
            plataforma_movil["tiempo_con_peso"] = 0
            plataforma_movil["tiempo_espera_retorno"] = 0
            plataforma_movil["estado"] = "esperando_inicio"
            plataforma_movil["moviendo"] = False
            plataforma_movil["llegada"] = False

        if plataformas_base is not None:
            plataformas = list(plataformas_base)
            if paredes_colores is not None:
                plataformas.extend([p["rect"] for p in paredes_colores])
            if compuerta is not None and compuerta["rect"].width > 0:
                plataformas.append(compuerta["rect"])
            if plataforma_movil is not None:
                plataformas.append(plataforma_movil["rect"])
            if plataformas_derrumbables is not None:
                plataformas.extend([p_d["rect"] for p_d in plataformas_derrumbables])
            if plataformas_alternadas is not None:
                plataformas.extend(plataformas_alternadas)

        if plataformas_derrumbables is not None:
            for p_d in plataformas_derrumbables:
                p_d["rect"].x = p_d["x_inicial"]
                p_d["rect"].y = p_d["y_inicial"]
                p_d["y"] = float(p_d["y_inicial"])
                p_d["vel_y"] = 0.0
                p_d["estado"] = "intacta"
                p_d["pisada"] = False
                p_d["tiempo_restante"] = 60
                p_d["particulas"].clear()

        p1_completado, p2_completado = False, False
        mostrar_tutorial = (numero_mundo == 1 and numero_nivel == 1)
        contador_tutorial = 0
        p1_movio = False
        p2_movio = False
        alpha_tut_p1 = 255.0
        alpha_tut_p2 = 255.0
        p1_soplado = False
        p2_soplado = False
        teclas_sopladas.clear()
        lineas_viento.clear()

        if numero_mundo == 3 and numero_nivel == 1:
            jugador1["en_agua"] = True
            jugador2["en_agua"] = True
            if burbujas_m3:
                burbujas_m3[:] = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)

        if numero_mundo == 3 and numero_nivel == 2:
            datos_lab = generar_laberinto_coral_m3_n2(ancho_mundo_nivel, ALTO, suelo.top, techo_agua.bottom)
            rocas_submarinas = datos_lab["rocas"]
            barreras_algas = datos_lab["barreras"]
            corales_decorativos = datos_lab["corales"]
            algas_decorativas = datos_lab["algas"]
            plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
            plataformas = list(plataformas_base)
            llave["x_inicial"] = datos_lab["llave_x"]
            llave["y_inicial"] = datos_lab["llave_y"]
            llave["x_float"] = float(datos_lab["llave_x"])
            llave["y_float"] = float(datos_lab["llave_y"])
            llave["rect"].x = datos_lab["llave_x"]
            llave["rect"].y = datos_lab["llave_y"]
            llave["recolectada"] = False
            llave["portador"] = None
            puerta["abierta"] = False
            jugador1["x_inicial"] = datos_lab["p1_x"]
            jugador1["y_inicial"] = datos_lab["p1_y"]
            jugador1["hitbox"].x = datos_lab["p1_x"]
            jugador1["hitbox"].y = datos_lab["p1_y"]
            jugador1["vel_x"] = 0
            jugador1["vel_y"] = 0
            jugador1["en_agua"] = True
            jugador2["x_inicial"] = datos_lab["p2_x"]
            jugador2["y_inicial"] = datos_lab["p2_y"]
            jugador2["hitbox"].x = datos_lab["p2_x"]
            jugador2["hitbox"].y = datos_lab["p2_y"]
            jugador2["vel_x"] = 0
            jugador2["vel_y"] = 0
            jugador2["en_agua"] = True
            if burbujas_m3:
                burbujas_m3[:] = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=50)

        if numero_mundo == 3 and numero_nivel == 3:
            jugador1["en_agua"] = True
            jugador2["en_agua"] = True
            if burbujas_m3:
                burbujas_m3[:] = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)

        if numero_mundo == 3 and numero_nivel == 4:
            linterna_p1 = True
            linterna_p2 = True
            datos_lab = generar_laberinto_oscuro_m3_n4(ancho_mundo_nivel, ALTO, suelo.top, techo_agua.bottom)
            rocas_submarinas = datos_lab["rocas"]
            barreras_algas = datos_lab["barreras"]
            corales_decorativos = datos_lab["corales"]
            algas_decorativas = datos_lab["algas"]
            pinchos = datos_lab["pinchos"]
            plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
            plataformas = list(plataformas_base)
            llave["x_inicial"] = datos_lab["llave_x"]
            llave["y_inicial"] = datos_lab["llave_y"]
            llave["x_float"] = float(datos_lab["llave_x"])
            llave["y_float"] = float(datos_lab["llave_y"])
            llave["rect"].x = datos_lab["llave_x"]
            llave["rect"].y = datos_lab["llave_y"]
            llave["recolectada"] = False
            llave["portador"] = None
            puerta["abierta"] = False
            jugador1["x_inicial"] = datos_lab["p1_x"]
            jugador1["y_inicial"] = datos_lab["p1_y"]
            jugador1["hitbox"].x = datos_lab["p1_x"]
            jugador1["hitbox"].y = datos_lab["p1_y"]
            jugador1["vel_x"] = 0
            jugador1["vel_y"] = 0
            jugador1["en_agua"] = True
            jugador2["x_inicial"] = datos_lab["p2_x"]
            jugador2["y_inicial"] = datos_lab["p2_y"]
            jugador2["hitbox"].x = datos_lab["p2_x"]
            jugador2["hitbox"].y = datos_lab["p2_y"]
            jugador2["vel_x"] = 0
            jugador2["vel_y"] = 0
            jugador2["en_agua"] = True
            if burbujas_m3:
                burbujas_m3[:] = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)

        if numero_mundo == 3 and numero_nivel == 5:
            linterna_p1 = True
            linterna_p2 = True
            oxigeno_p1 = 100.0
            oxigeno_p2 = 100.0
            jugador1["en_agua"] = True
            jugador2["en_agua"] = True
            if burbujas_m3:
                burbujas_m3[:] = crear_sistema_burbujas_m3(ancho_mundo_nivel, cantidad=45)

    mundo = pygame.Surface((ancho_mundo_nivel, ALTO)).convert()
    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                if hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_id):
                    resp = mostrar_dialogo_guardar_salir(
                        pantalla, reloj,
                        niveles_desbloqueados=niveles_desbloqueados,
                        id_partida=partida_id,
                        nombre_partida=partida_nombre,
                        password_partida=partida_password,
                        color_p1=color_p1,
                        color_p2=color_p2,
                        accesorio_p1=p1_acc,
                        accesorio_p2=p2_acc,
                    )
                    if resp in ("guardar_salir", "salir_sin_guardar"):
                        pygame.quit()
                        sys.exit()
                else:
                    pygame.quit()
                    sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    if spr_reiniciar_semi and spr_reiniciar_apretado:
                        f_limpio = fondo_btn_reiniciar if fondo_btn_reiniciar else (255, 240, 195)
                        animar_pulsacion_boton(pantalla, rect_btn_reiniciar, spr_reiniciar_semi, spr_reiniciar_apretado, f_limpio)
                    _reiniciar_nivel_completo()
                elif numero_mundo == 3 and numero_nivel in (4, 5):
                    if evento.key in (pygame.K_e, pygame.K_f, pygame.K_SPACE):
                        if not jugador1.get("muerto", False):
                            linterna_p1 = not linterna_p1
                    elif evento.key in (pygame.K_l, pygame.K_RETURN, pygame.K_RSHIFT, pygame.K_RCTRL):
                        if not jugador2.get("muerto", False):
                            linterna_p2 = not linterna_p2

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    f_limpio = fondo_btn_x if fondo_btn_x else (255, 240, 195)
                    if animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, f_limpio, spr_x_normal):
                        if hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_id):
                            resp = mostrar_dialogo_guardar_salir(
                                pantalla, reloj,
                                niveles_desbloqueados=niveles_desbloqueados,
                                id_partida=partida_id,
                                nombre_partida=partida_nombre,
                                password_partida=partida_password,
                                color_p1=color_p1,
                                color_p2=color_p2,
                                accesorio_p1=p1_acc,
                                accesorio_p2=p2_acc,
                            )
                            if resp in ("guardar_salir", "salir_sin_guardar"):
                                pygame.quit()
                                sys.exit()
                        else:
                            pygame.quit()
                            sys.exit()

                if rect_btn_reiniciar.collidepoint(evento.pos):
                    f_limpio = fondo_btn_reiniciar if fondo_btn_reiniciar else (255, 240, 195)
                    if animar_pulsacion_boton(pantalla, rect_btn_reiniciar, spr_reiniciar_semi, spr_reiniciar_apretado, f_limpio, spr_reiniciar_normal):
                        _reiniciar_nivel_completo()

                if rect_btn_casa.collidepoint(evento.pos):
                    f_limpio = fondo_btn_casa if fondo_btn_casa else (255, 240, 195)
                    if animar_pulsacion_boton(pantalla, rect_btn_casa, spr_casa_semi, spr_casa_apretado, f_limpio, spr_casa_normal):
                        return "menu"

                if rect_btn_config.collidepoint(evento.pos):
                    f_limpio = fondo_btn_config if fondo_btn_config else (255, 240, 195)
                    if animar_pulsacion_boton(pantalla, rect_btn_config, spr_config_semi, spr_config_apretado, f_limpio, spr_config_normal):
                        mostrar_pestana_configuracion(pantalla, reloj)

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

            # Desvanecer los controles de P1 al moverse o soplado
            if p1_soplado:
                alpha_tut_p1 = 0.0
            elif p1_movio:
                alpha_tut_p1 = max(0.0, alpha_tut_p1 - 25.0)

            # Desvanecer los controles de P2 al moverse o soplado
            if p2_soplado:
                alpha_tut_p2 = 0.0
            elif p2_movio:
                alpha_tut_p2 = max(0.0, alpha_tut_p2 - 25.0)

            if alpha_tut_p1 <= 0 and alpha_tut_p2 <= 0 and not teclas_sopladas and not lineas_viento:
                mostrar_tutorial = False

        p1_sobre_p2 = (
            not p1_completado and not p2_completado and not jugador1["muerto"] and not jugador2["muerto"]
            and abs(jugador1["hitbox"].bottom - jugador2["hitbox"].top) <= 8
            and jugador1["hitbox"].right > jugador2["hitbox"].left + 2
            and jugador1["hitbox"].left < jugador2["hitbox"].right - 2
        )
        p2_sobre_p1 = (
            not p1_completado and not p2_completado and not jugador1["muerto"] and not jugador2["muerto"]
            and abs(jugador2["hitbox"].bottom - jugador1["hitbox"].top) <= 8
            and jugador2["hitbox"].right > jugador1["hitbox"].left + 2
            and jugador2["hitbox"].left < jugador1["hitbox"].right - 2
        )

        # Movimiento horizontal Jugador 1 (P1: WASD)
        if not jugador1["muerto"] and not p1_completado:
            mover_izq_p1 = teclas[pygame.K_a]
            mover_der_p1 = teclas[pygame.K_d]

            if mover_izq_p1 and not mover_der_p1:
                if usar_soga and not jugador1["en_suelo"] and jugador2.get("en_suelo", False):
                    # Suspendido en el aire: bombear impulso tangencial al péndulo
                    jugador1["vel_x"] = max(-jugador1["velocidad_mov"], jugador1["vel_x"] - 0.45)
                else:
                    jugador1["vel_x"] = -jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            elif mover_der_p1 and not mover_izq_p1:
                if usar_soga and not jugador1["en_suelo"] and jugador2.get("en_suelo", False):
                    jugador1["vel_x"] = min(jugador1["velocidad_mov"], jugador1["vel_x"] + 0.45)
                else:
                    jugador1["vel_x"] = jugador1["velocidad_mov"]
                jugador1["moviendo"] = True
            else:
                if usar_soga and not jugador1["en_suelo"]:
                    if jugador2.get("en_suelo", False):
                        jugador1["vel_x"] *= 0.995  # Conservación natural de la inercia pendular
                    else:
                        jugador1["vel_x"] *= 0.97
                elif numero_mundo == 3:
                    jugador1["vel_x"] *= 0.82
                    if abs(jugador1["vel_x"]) < 0.15:
                        jugador1["vel_x"] = 0
                else:
                    jugador1["vel_x"] = 0
                if abs(jugador1["vel_x"]) < 0.15 and abs(jugador1.get("vel_y", 0)) < 0.3:
                    jugador1["moviendo"] = False

            if salto_p1_pedido:
                impulso = 0
                if not usar_agua and p1_sobre_p2 and (salto_p2_pedido or jugador2["vel_y"] < 0):
                    impulso = -4.5
                jugador1["vel_y"] = jugador1["fuerza_salto"] + impulso
                jugador1["en_suelo"] = False

        # Movimiento horizontal Jugador 2 (P2: Flechas)
        if not jugador2["muerto"] and not p2_completado:
            mover_izq_p2 = teclas[pygame.K_LEFT]
            mover_der_p2 = teclas[pygame.K_RIGHT]

            if mover_izq_p2 and not mover_der_p2:
                if usar_soga and not jugador2["en_suelo"] and jugador1.get("en_suelo", False):
                    # Suspendido en el aire: bombear impulso tangencial al péndulo
                    jugador2["vel_x"] = max(-jugador2["velocidad_mov"], jugador2["vel_x"] - 0.45)
                else:
                    jugador2["vel_x"] = -jugador2["velocidad_mov"]
                jugador2["moviendo"] = True
            elif mover_der_p2 and not mover_izq_p2:
                if usar_soga and not jugador2["en_suelo"] and jugador1.get("en_suelo", False):
                    jugador2["vel_x"] = min(jugador2["velocidad_mov"], jugador2["vel_x"] + 0.45)
                else:
                    jugador2["vel_x"] = jugador2["velocidad_mov"]
                jugador2["moviendo"] = True
            else:
                if usar_soga and not jugador2["en_suelo"]:
                    if jugador1.get("en_suelo", False):
                        jugador2["vel_x"] *= 0.995  # Conservación natural de la inercia pendular
                    else:
                        jugador2["vel_x"] *= 0.97
                elif numero_mundo == 3:
                    jugador2["vel_x"] *= 0.82
                    if abs(jugador2["vel_x"]) < 0.15:
                        jugador2["vel_x"] = 0
                else:
                    jugador2["vel_x"] = 0
                if abs(jugador2["vel_x"]) < 0.15 and abs(jugador2.get("vel_y", 0)) < 0.3:
                    jugador2["moviendo"] = False

            if salto_p2_pedido:
                impulso = 0
                if not usar_agua and p2_sobre_p1 and (salto_p1_pedido or jugador1["vel_y"] < 0):
                    impulso = -4.5
                jugador2["vel_y"] = jugador2["fuerza_salto"] + impulso
                jugador2["en_suelo"] = False

        if usar_soga and not p1_completado and not p2_completado:
            actualizar_fisica_soga(jugador1, jugador2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)

        if usar_agua:
            if not jugador1["muerto"]:
                actualizar_estado_agua(jugador1, ZONA_AGUA)
                if jugador1["en_agua"]:
                    aplicar_fisica_agua(jugador1, teclas[pygame.K_w], teclas[pygame.K_s], submarino=(numero_mundo == 3))
            if not jugador2["muerto"]:
                actualizar_estado_agua(jugador2, ZONA_AGUA)
                if jugador2["en_agua"]:
                    aplicar_fisica_agua(jugador2, teclas[pygame.K_UP], teclas[pygame.K_DOWN], submarino=(numero_mundo == 3))

        if boton_nivel is not None and pared_nivel is not None:
            caja_sobre_btn = (
                caja is not None
                and caja["rect"].right > boton_nivel["rect"].left + 15
                and caja["rect"].left < boton_nivel["rect"].right - 15
                and abs(caja["rect"].bottom - suelo.top) <= 8
            )
            pj_sobre_btn = any(
                not p["muerto"] and not comp
                and p["hitbox"].right > boton_nivel["rect"].left + 10
                and p["hitbox"].left < boton_nivel["rect"].right - 10
                and abs(p["hitbox"].bottom - suelo.top) <= 8
                for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]
            )
            boton_nivel["presionado"] = caja_sobre_btn or pj_sobre_btn

            vel_pared = 0.04
            if boton_nivel["presionado"]:
                if pared_nivel["progreso"] < 1.0:
                    pared_nivel["progreso"] = min(1.0, pared_nivel["progreso"] + vel_pared)
            else:
                if pared_nivel["progreso"] > 0.0:
                    pared_nivel["progreso"] = max(0.0, pared_nivel["progreso"] - vel_pared)

            pared_nivel["y"] = pared_nivel["y_cerrada"] + (pared_nivel["y_abierta"] - pared_nivel["y_cerrada"]) * pared_nivel["progreso"]
            pared_nivel["rect"].y = int(pared_nivel["y"])

        if botones_colores is not None and paredes_colores is not None:
            # Comprobación continua de presión física: el botón solo está presionado
            # mientras un personaje permanezca físicamente apoyado sobre él.
            for btn in botones_colores:
                rb = btn["rect"]
                pj_sobre = False
                for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                    if not p["muerto"] and not comp:
                        hb = p["hitbox"]
                        if (
                            hb.right > rb.left + 8
                            and hb.left < rb.right - 8
                            and abs(hb.bottom - suelo.top) <= 8
                            and (p["en_suelo"] or abs(p["vel_y"]) <= 1.5)
                        ):
                            pj_sobre = True
                            break
                btn["presionado"] = pj_sobre

            rojo_presionado = any(btn["presionado"] for btn in botones_colores if btn["color"] == "rojo")
            azul_presionado = any(btn["presionado"] for btn in botones_colores if btn["color"] == "azul")

            vel_pared = 0.05
            for pared in paredes_colores:
                abrir = (rojo_presionado if pared["color"] == "rojo" else azul_presionado)
                if abrir:
                    if pared["progreso"] < 1.0:
                        pared["progreso"] = min(1.0, pared["progreso"] + vel_pared)
                else:
                    # Protección anti-aplastamiento: si un personaje está en el espacio que ocupa la pared cerrada,
                    # no reactivar la colisión ni bajar la pared directamente sobre él hasta que el espacio quede libre.
                    rect_espacio_cerrado = pygame.Rect(pared["x"], int(pared["y_cerrada"]), pared["ancho"], pared["alto"])
                    jugador_en_espacio = any(
                        not pj["muerto"] and not comp and pj["hitbox"].colliderect(rect_espacio_cerrado)
                        for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]
                    )
                    if not jugador_en_espacio:
                        if pared["progreso"] > 0.0:
                            pared["progreso"] = max(0.0, pared["progreso"] - vel_pared)

                y_actual = pared["y_cerrada"] + (pared["y_abierta"] - pared["y_cerrada"]) * pared["progreso"]
                pared["rect"].y = int(y_actual)

            paredes_solidas = []
            for p_col in paredes_colores:
                if p_col["progreso"] < 0.75:
                    solapado = any(
                        not pj["muerto"] and not comp and pj["hitbox"].colliderect(p_col["rect"])
                        for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]
                    )
                    if not solapado:
                        paredes_solidas.append(p_col["rect"])
            plataformas = plataformas_base + paredes_solidas

        if boton_compuerta is not None:
            pj_sobre = False
            rb = boton_compuerta["rect"]
            for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                if not comp and not p["muerto"]:
                    hb = p["hitbox"]
                    if (
                        hb.right > rb.left + 6
                        and hb.left < rb.right - 6
                        and abs(hb.bottom - suelo.top) <= 8
                        and (p["en_suelo"] or abs(p["vel_y"]) <= 1.5)
                    ):
                        pj_sobre = True
                        break
            boton_compuerta["presionado"] = pj_sobre

        if compuerta is not None:
            vel_comp = 0.06
            if boton_compuerta is not None and boton_compuerta["presionado"]:
                if compuerta["progreso"] < 1.0:
                    compuerta["progreso"] = min(1.0, compuerta["progreso"] + vel_comp)
            else:
                rect_espacio_hueco = pygame.Rect(1700, 460, 140, 60)
                jugador_en_espacio = any(
                    not pj["muerto"] and not comp and pj["hitbox"].colliderect(rect_espacio_hueco)
                    for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]
                )
                if not jugador_en_espacio:
                    if compuerta["progreso"] > 0.0:
                        compuerta["progreso"] = max(0.0, compuerta["progreso"] - vel_comp)

            comp_x = 1700 + int(140 * compuerta["progreso"])
            compuerta["rect"].x = comp_x
            compuerta["rect"].width = max(0, 1840 - comp_x)

            if compuerta["progreso"] < 0.75:
                solapado_comp = any(
                    not pj["muerto"] and not comp and pj["hitbox"].colliderect(compuerta["rect"])
                    for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]
                )
                if not solapado_comp and compuerta["rect"].width > 0:
                    if compuerta["rect"] not in plataformas:
                        plataformas.append(compuerta["rect"])

        if plataforma_movil is not None:
            pm_rect = plataforma_movil["rect"]
            pjs_sobre = []
            for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                if not comp and not pj["muerto"]:
                    hb = pj["hitbox"]
                    if (
                        hb.right > pm_rect.left + 4
                        and hb.left < pm_rect.right - 4
                        and abs(hb.bottom - pm_rect.top) <= 8
                        and (pj["en_suelo"] or abs(pj["vel_y"]) <= 2.0)
                    ):
                        pjs_sobre.append(pj)

            estado_pm = plataforma_movil.get("estado", "esperando_inicio")

            if estado_pm == "esperando_inicio":
                if len(pjs_sobre) > 0:
                    plataforma_movil["tiempo_con_peso"] += 1
                    if plataforma_movil["tiempo_con_peso"] >= plataforma_movil.get("tiempo_activacion", 120):
                        plataforma_movil["estado"] = "avanzando"
                        plataforma_movil["moviendo"] = True
                else:
                    plataforma_movil["tiempo_con_peso"] = 0

            elif estado_pm == "avanzando":
                vel = plataforma_movil["velocidad"]
                x_fin = plataforma_movil.get("x_fin", 1720.0)
                if plataforma_movil["x"] + vel >= x_fin:
                    plataforma_movil["x"] = x_fin
                    plataforma_movil["estado"] = "esperando_retorno"
                    plataforma_movil["moviendo"] = False
                    plataforma_movil["llegada"] = True
                    plataforma_movil["tiempo_espera_retorno"] = 0
                else:
                    plataforma_movil["x"] += vel
                plataforma_movil["rect"].x = int(plataforma_movil["x"])

            elif estado_pm == "esperando_retorno":
                plataforma_movil["moviendo"] = False
                plataforma_movil["tiempo_espera_retorno"] += 1
                if plataforma_movil["tiempo_espera_retorno"] >= plataforma_movil.get("tiempo_max_espera_retorno", 300):
                    plataforma_movil["estado"] = "regresando"
                    plataforma_movil["moviendo"] = True
                    plataforma_movil["llegada"] = False

            elif estado_pm == "regresando":
                vel = plataforma_movil["velocidad"]
                x_ini = plataforma_movil["x_inicial"]
                if plataforma_movil["x"] - vel <= x_ini:
                    plataforma_movil["x"] = x_ini
                    plataforma_movil["estado"] = "esperando_inicio"
                    plataforma_movil["moviendo"] = False
                    plataforma_movil["tiempo_con_peso"] = 0
                    plataforma_movil["tiempo_espera_retorno"] = 0
                else:
                    plataforma_movil["x"] -= vel
                plataforma_movil["rect"].x = int(plataforma_movil["x"])

            # Los personajes deben tener que moverse para mantenerse sobre la plataforma
            # (No se traslada artificialmente pj["hitbox"].x += dx)

            if plataformas_base is not None:
                plataformas = list(plataformas_base) + [plataforma_movil["rect"]]

        if plataformas_derrumbables is not None:
            for p_d in plataformas_derrumbables:
                # 1. Detectar si un personaje vivo no completado está pisando físicamente la plataforma
                # Cada plataforma gestiona su propio temporizador de forma independiente.
                if not p_d["pisada"]:
                    pjs_pisando = False
                    for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                        if not comp and not pj["muerto"]:
                            hb = pj["hitbox"]
                            # El personaje pisa la plataforma si tiene solapamiento horizontal y sus pies
                            # contactan la cara superior (estando en suelo o aterrizando con vel_y >= 0)
                            if (
                                hb.right > p_d["rect"].left + 2
                                and hb.left < p_d["rect"].right - 2
                                and abs(hb.bottom - p_d["rect"].top) <= 8
                                and (pj["en_suelo"] or pj.get("vel_y", 0) >= 0)
                            ):
                                pjs_pisando = True
                                break
                    if pjs_pisando:
                        p_d["pisada"] = True
                        p_d["tiempo_restante"] = 60  # Exactamente 1.0 segundo a 60 FPS (no se reinicia al permanecer encima)

                # 2. Descontar temporizador
                if p_d["pisada"] and p_d["tiempo_restante"] > 0:
                    p_d["tiempo_restante"] -= 1
                    if p_d["tiempo_restante"] <= 20:
                        p_d["estado"] = "temblando"
                    else:
                        p_d["estado"] = "agrietandose"

                    if p_d["tiempo_restante"] <= 0:
                        p_d["estado"] = "derrumbada"
                        # Dejar de sostener inmediatamente a los personajes sobre esta plataforma
                        for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                            if not comp and not pj["muerto"]:
                                hb = pj["hitbox"]
                                if (
                                    hb.right > p_d["rect"].left + 2
                                    and hb.left < p_d["rect"].right - 2
                                    and abs(hb.bottom - p_d["rect"].top) <= 8
                                ):
                                    pj["en_suelo"] = False
                        for _ in range(14):
                            p_d["particulas"].append({
                                "x": random.uniform(p_d["rect"].left, p_d["rect"].right),
                                "y": random.uniform(p_d["rect"].top, p_d["rect"].bottom),
                                "vx": random.uniform(-2.5, 2.5),
                                "vy": random.uniform(-1.0, 3.0),
                                "tam": random.randint(3, 6),
                                "vida": random.randint(30, 50),
                            })

                # 3. Caída libre de la plataforma si se derrumbó (caída rápida)
                if p_d["estado"] == "derrumbada":
                    p_d["vel_y"] += 1.5
                    p_d["y"] += p_d["vel_y"]
                    p_d["rect"].y = int(p_d["y"])

                # 4. Actualizar partículas existentes
                activas_part = []
                for part in p_d["particulas"]:
                    part["x"] += part["vx"]
                    part["y"] += part["vy"]
                    part["vy"] += 0.25
                    part["vida"] -= 1
                    if part["vida"] > 0:
                        activas_part.append(part)
                p_d["particulas"] = activas_part

            # 5. Las plataformas activas que sostienen a los personajes son las que no se han derrumbado
            if plataformas_base is not None:
                plataformas = list(plataformas_base) + [p_d["rect"] for p_d in plataformas_derrumbables if p_d["estado"] != "derrumbada"]

        if usar_caja:
            actualizar_caja(caja, suelo, mundo_rect, plataformas)
            if numero_mundo == 1 and numero_nivel == 4 and caja is not None:
                if caja["rect"].left < 20:
                    caja["rect"].left = 20

        if not jugador1["muerto"] and not p1_completado:
            resolver_colisiones(jugador1, jugador2 if not p2_completado and not jugador2["muerto"] else None, suelo, mundo_rect, caja if usar_caja else None, jugador1["en_agua"], plataformas)
        if not jugador2["muerto"] and not p2_completado:
            resolver_colisiones(jugador2, jugador1 if not p1_completado and not jugador1["muerto"] else None, suelo, mundo_rect, caja if usar_caja else None, jugador2["en_agua"], plataformas)

        if numero_mundo == 3 and numero_nivel == 5:
            # 1. Empuje de corrientes marinas sobre personajes activos
            for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                if not comp and not p["muerto"]:
                    for corr in corrientes_marinas:
                        if p["hitbox"].colliderect(corr["rect"]):
                            p["hitbox"].x += int(corr["fuerza_x"])
                            p["hitbox"].y += int(corr["fuerza_y"])

            # 2. Gestión del oxígeno de Jugador 1
            if not p1_completado and not jugador1["muerto"]:
                en_camara_p1 = any(cam["rect"].colliderect(jugador1["hitbox"]) for cam in camaras_aire)
                if en_camara_p1:
                    oxigeno_p1 = min(OXIGENO_MAX, oxigeno_p1 + 0.85)
                else:
                    oxigeno_p1 = max(0.0, oxigeno_p1 - 0.082)
                    if oxigeno_p1 <= 0.0:
                        matar_personaje(jugador1)
                        if numero_mundo != 3 and not jugador2["muerto"] and not p2_completado:
                            matar_personaje(jugador2)

            # 3. Gestión del oxígeno de Jugador 2
            if not p2_completado and not jugador2["muerto"]:
                en_camara_p2 = any(cam["rect"].colliderect(jugador2["hitbox"]) for cam in camaras_aire)
                if en_camara_p2:
                    oxigeno_p2 = min(OXIGENO_MAX, oxigeno_p2 + 0.85)
                else:
                    oxigeno_p2 = max(0.0, oxigeno_p2 - 0.086)
                    if oxigeno_p2 <= 0.0:
                        matar_personaje(jugador2)
                        if numero_mundo != 3 and not jugador1["muerto"] and not p1_completado:
                            matar_personaje(jugador1)

        if usar_soga and not p1_completado and not p2_completado:
            aplicar_restriccion_soga(jugador1, jugador2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if usar_llave:
            personajes_activos = [p for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)] if not comp and not p["muerto"]]
            actualizar_llave(llave, personajes_activos, puerta)
        if usar_pinchos:
            p1_toco = False
            p2_toco = False
            if not p1_completado:
                p1_toco = comprobar_pinchos(jugador1, pinchos)
            if not p2_completado:
                p2_toco = comprobar_pinchos(jugador2, pinchos)

            if numero_mundo != 3:
                if p1_toco and not jugador2["muerto"] and not p2_completado:
                    matar_personaje(jugador2)
                elif p2_toco and not jugador1["muerto"] and not p1_completado:
                    matar_personaje(jugador1)

        if laser_nivel is not None:
            em = laser_nivel["emisor_rect"]
            y_r = laser_nivel["y_rayo"]
            pared_x = laser_nivel.get("pared_der_x", 1100)
            x_stop = pared_x
            bloqueado = False
            if caja is not None:
                cr = caja["rect"]
                if cr.right > em.left and cr.left < pared_x and cr.top <= y_r <= cr.bottom:
                    x_stop = max(em.right, cr.left)
                    bloqueado = True

            laser_nivel["bloqueado"] = bloqueado
            laser_nivel["x_fin"] = x_stop
            laser_nivel["rect_dano"].x = em.right
            laser_nivel["rect_dano"].width = max(0, x_stop - em.right)

            for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                if not comp and not p["muerto"]:
                    if laser_nivel["rect_dano"].width > 0 and p["hitbox"].colliderect(laser_nivel["rect_dano"]):
                        matar_personaje(p)
                        if numero_mundo != 3:
                            otro = jugador2 if p is jugador1 else jugador1
                            comp_otro = p2_completado if p is jugador1 else p1_completado
                            if not comp_otro and not otro.get("muerto", False):
                                matar_personaje(otro)

        # Detección continua de muerte cuando un personaje cae o sale completamente de la pantalla o del escenario
        for p, comp, otro, comp_otro in [
            (jugador1, p1_completado, jugador2, p2_completado),
            (jugador2, p2_completado, jugador1, p1_completado),
        ]:
            if not comp and not p.get("muerto", False):
                hb = p["hitbox"]
                # Solo se detecta muerte si sale completamente de los límites (evitando falsos positivos parciales)
                caida_abajo = hb.top >= ALTO
                salida_izq = hb.right <= 0
                salida_der = hb.left >= ancho_mundo_nivel
                salida_arriba = hb.bottom <= -50

                if caida_abajo or salida_izq or salida_der or salida_arriba:
                    if caida_abajo:
                        # Asegurar que inicie el salto de muerte desde el borde para que sea visible en pantalla
                        hb.top = ALTO
                    matar_personaje(p)

                    # Si el personaje que cayó portaba la llave, reubicarla en su posición inicial
                    # para que el sobreviviente pueda continuar sin quedar bloqueado indefinidamente
                    if usar_llave and llave and llave.get("recolectada", False) and llave.get("portador") is p:
                        llave["recolectada"] = False
                        llave["portador"] = None
                        llave["rect"].x = llave["x_inicial"]
                        llave["rect"].y = llave["y_inicial"]
                        llave["x_float"] = float(llave["x_inicial"])
                        llave["y_float"] = float(llave["y_inicial"])

                    # Reglas por mundo:
                    # - Mundos 1 y 2: muerte compartida (si uno muere, mueren ambos)
                    # - Mundo 3: muerte independiente (el otro continúa con vida)
                    if numero_mundo != 3:
                        if not comp_otro and not otro.get("muerto", False):
                            matar_personaje(otro)

        actualizar_muerte(jugador1)
        actualizar_muerte(jugador2)

        # Limitar horizontalmente y techo para personajes vivos, permitiendo caída libre por el fondo
        for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
            if not comp and not p.get("muerto", False):
                hb = p["hitbox"]
                if hb.left < 0:
                    hb.left = 0
                elif hb.right > ancho_mundo_nivel:
                    hb.right = ancho_mundo_nivel
                if hb.top < 0:
                    hb.top = 0

        # Detección de interacción especial en Mundo 1 Nivel 1: soplar indicadores del personaje quieto al saltar sobre él
        if numero_mundo == 1 and numero_nivel == 1:
            ancho_c = 3 * TAM_BTN_TUT + 2 * GAP_BTN_TUT
            h_c1 = badge_p1.get_height() + 4 + (2 * TAM_BTN_TUT + GAP_BTN_TUT)
            h_c2 = badge_p2.get_height() + 4 + (2 * TAM_BTN_TUT + GAP_BTN_TUT)

            # Caso 1: Jugador 1 está quieto, Jugador 2 salta y atraviesa la zona de sus indicadores
            if not p1_movio and not p1_soplado and alpha_tut_p1 > 0 and not jugador1["muerto"] and not p1_completado:
                if not jugador2["muerto"] and not p2_completado and not p2_sobre_p1:
                    if not jugador2["en_suelo"] or abs(jugador2["vel_y"]) > 1.0:
                        rect_c1 = pygame.Rect(jugador1["hitbox"].centerx - ancho_c // 2, (jugador1["hitbox"].top - 8) - h_c1, ancho_c, h_c1)
                        if jugador2["hitbox"].colliderect(rect_c1):
                            pasa_sobre = abs(jugador2["vel_x"]) > 0.3 or (jugador2["hitbox"].right > jugador1["hitbox"].left + 2 and jugador2["hitbox"].left < jugador1["hitbox"].right - 2)
                            if pasa_sobre:
                                p1_soplado = True
                                alpha_tut_p1 = 0.0
                                dir_v = 1.0 if jugador2["vel_x"] > 0.3 else (-1.0 if jugador2["vel_x"] < -0.3 else (1.0 if jugador2["hitbox"].centerx >= jugador1["hitbox"].centerx else -1.0))
                                _crear_efecto_soplar(jugador1, es_p1=True, dir_viento=dir_v)

            # Caso 2: Jugador 2 está quieto, Jugador 1 salta y atraviesa la zona de sus indicadores
            if not p2_movio and not p2_soplado and alpha_tut_p2 > 0 and not jugador2["muerto"] and not p2_completado:
                if not jugador1["muerto"] and not p1_completado and not p1_sobre_p2:
                    if not jugador1["en_suelo"] or abs(jugador1["vel_y"]) > 1.0:
                        rect_c2 = pygame.Rect(jugador2["hitbox"].centerx - ancho_c // 2, (jugador2["hitbox"].top - 8) - h_c2, ancho_c, h_c2)
                        if jugador1["hitbox"].colliderect(rect_c2):
                            pasa_sobre = abs(jugador1["vel_x"]) > 0.3 or (jugador1["hitbox"].right > jugador2["hitbox"].left + 2 and jugador1["hitbox"].left < jugador2["hitbox"].right - 2)
                            if pasa_sobre:
                                p2_soplado = True
                                alpha_tut_p2 = 0.0
                                dir_v = 1.0 if jugador1["vel_x"] > 0.3 else (-1.0 if jugador1["vel_x"] < -0.3 else (1.0 if jugador1["hitbox"].centerx >= jugador2["hitbox"].centerx else -1.0))
                                _crear_efecto_soplar(jugador2, es_p1=False, dir_viento=dir_v)

        if puerta and puerta["abierta"]:
            if not p1_completado and jugador1["hitbox"].colliderect(puerta["rect"]):
                p1_completado = True
                jugador1["hitbox"].x = -9999
            if not p2_completado and jugador2["hitbox"].colliderect(puerta["rect"]):
                p2_completado = True
                jugador2["hitbox"].x = -9999

        if numero_mundo == 3:
            tick_m3 += 1
            dibujar_submarino_fondo_escenario(mundo, ancho_mundo_nivel, tick_m3)
            dibujar_lecho_marino(mundo, suelo, ancho_mundo_nivel)
            if algas_decorativas:
                dibujar_algas_decorativas_escenario(mundo, algas_decorativas, tick_m3, capa="fondo")
            if corrientes_marinas:
                dibujar_corrientes_marinas_escenario(mundo, corrientes_marinas, tick_m3)
            if camaras_aire:
                dibujar_camaras_aire_escenario(mundo, camaras_aire, tick_m3)
            if rocas_submarinas:
                dibujar_rocas_submarinas_escenario(mundo, rocas_submarinas)
            if barreras_algas:
                dibujar_barreras_algas_escenario(mundo, barreras_algas, tick_m3)
            if corales_decorativos:
                dibujar_corales_escenario(mundo, corales_decorativos, tick_m3)
            if algas_decorativas:
                dibujar_algas_decorativas_escenario(mundo, algas_decorativas, tick_m3, capa="frente")
            if pinchos:
                dibujar_peligros_marinos_escenario(mundo, pinchos)
            if burbujas_m3:
                actualizar_y_dibujar_burbujas_m3(mundo, burbujas_m3, [jugador1, jugador2], tick_m3)
        else:
            mundo.fill((255, 240, 195))

            if pozo_nivel is not None:
                pz = pozo_nivel
                pygame.draw.rect(mundo, (235, 222, 192), (pz["x"], pz["y"], pz["ancho"], pz["alto"]))
                pygame.draw.line(mundo, COLOR_BORDE_PLATAFORMA, (pz["x"], pz["y"]), (pz["x"], pz["y"] + pz["alto"]), 2)
                pygame.draw.line(mundo, COLOR_BORDE_PLATAFORMA, (pz["x"] + pz["ancho"], pz["y"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

            plats_dibujar = plataformas_base if (paredes_colores is not None and plataformas_base is not None) else plataformas
            for plat in plats_dibujar:
                if barrera_l_horiz is not None and (plat is barrera_l_horiz or plat is barrera_l_vert):
                    continue
                if compuerta is not None and plat is compuerta["rect"]:
                    continue
                if bloque_central is not None and plat is bloque_central["rect"]:
                    continue
                if bloque_peligroso is not None and plat is bloque_peligroso["rect"]:
                    continue
                if plataforma_movil is not None and plat is plataforma_movil["rect"]:
                    continue
                if plataformas_derrumbables is not None and any(plat is p_d["rect"] for p_d in plataformas_derrumbables):
                    continue
                if plat.bottom >= suelo.top:
                    rect_torre = pygame.Rect(plat.x, plat.y, plat.width, plat.height + 4)
                    pygame.draw.rect(mundo, COLOR_PLATAFORMA, rect_torre, border_top_left_radius=4, border_top_right_radius=4)
                    pygame.draw.rect(mundo, COLOR_BORDE_PLATAFORMA, rect_torre, width=2, border_top_left_radius=4, border_top_right_radius=4)
                else:
                    pygame.draw.rect(mundo, COLOR_PLATAFORMA, plat, border_radius=4)
                    pygame.draw.rect(mundo, COLOR_BORDE_PLATAFORMA, plat, width=2, border_radius=4)

            if barrera_l_horiz is not None and barrera_l_vert is not None:
                dibujar_barrera_l_escenario(mundo, barrera_l_horiz, barrera_l_vert)

            pygame.draw.rect(mundo, (225, 110, 80), suelo)
            if pozo_nivel is not None:
                pygame.draw.line(mundo, COLOR_BORDE_PLATAFORMA, (pz["x"], pz["y"] + pz["alto"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

            if pinchos:
                dibujar_pinchos_escenario(mundo, pinchos)
            if numero_mundo == 2 and numero_nivel == 3:
                dibujar_pendulo_escenario(mundo, plataformas, plat_elevada, pozo_nivel, bloque_peligroso)
            if numero_mundo == 2 and numero_nivel == 4 and plataformas_derrumbables is not None:
                dibujar_plataformas_derrumbables_escenario(mundo, plataformas_derrumbables, pozo_nivel)
            if numero_mundo == 2 and numero_nivel == 5 and plataformas_alternadas is not None:
                dibujar_plataformas_alternadas_escenario(mundo, plataformas_alternadas, pozo_nivel)

        if compuerta is not None and compuerta["rect"].width > 0:
            c_rect = compuerta["rect"]
            pygame.draw.rect(mundo, (180, 85, 60), c_rect, border_radius=3)
            pygame.draw.rect(mundo, (120, 45, 30), c_rect, width=2, border_radius=3)
            for lx in range(c_rect.left + 14, c_rect.right - 6, 18):
                pygame.draw.line(mundo, (130, 55, 35), (lx, c_rect.top + 3), (lx, c_rect.bottom - 4), 2)

        if boton_compuerta is not None:
            rect_bc = boton_compuerta["rect"]
            h_bc = 4 if boton_compuerta["presionado"] else 12
            y_bc = suelo.top - h_bc
            pygame.draw.rect(mundo, (85, 70, 60), (rect_bc.left - 6, suelo.top - 4, rect_bc.width + 12, 10), border_radius=2)
            col_bc = (70, 205, 120) if boton_compuerta["presionado"] else (210, 85, 45)
            col_borde_bc = (40, 150, 80) if boton_compuerta["presionado"] else (150, 45, 25)
            pygame.draw.rect(mundo, col_bc, (rect_bc.x, y_bc, rect_bc.width, h_bc), border_top_left_radius=3, border_top_right_radius=3)
            pygame.draw.rect(mundo, col_borde_bc, (rect_bc.x, y_bc, rect_bc.width, h_bc), width=2, border_top_left_radius=3, border_top_right_radius=3)

        if bloque_central is not None:
            bc = bloque_central["rect"]
            pygame.draw.rect(mundo, (220, 50, 50), bc, border_radius=4)
            pygame.draw.rect(mundo, (140, 25, 25), bc, width=2, border_radius=4)
            for by in range(bc.top + 16, bc.bottom - 8, 16):
                pygame.draw.line(mundo, (160, 30, 30), (bc.left + 4, by), (bc.right - 4, by), 2)

        if plataforma_movil is not None:
            pm = plataforma_movil["rect"]
            pygame.draw.rect(mundo, (215, 105, 75), pm, border_radius=5)
            pygame.draw.rect(mundo, (150, 60, 40), pm, width=2, border_radius=5)
            for rx in range(pm.left + 16, pm.right - 8, 24):
                pygame.draw.circle(mundo, (140, 60, 40), (rx, pm.bottom - 5), 3)

            estado_pm = plataforma_movil.get("estado", "esperando_inicio")
            if estado_pm == "esperando_retorno":
                t_esp = plataforma_movil.get("tiempo_espera_retorno", 0)
                parpadeo = (t_esp // 15) % 2 == 0
                col_luz = (255, 235, 40) if parpadeo else (100, 85, 20)
                col_halo = (255, 245, 120) if parpadeo else (70, 60, 15)
                if parpadeo:
                    pygame.draw.circle(mundo, col_halo, (pm.centerx, pm.centery), 8)
                pygame.draw.circle(mundo, col_luz, (pm.centerx, pm.centery), 5)
                pygame.draw.circle(mundo, (255, 255, 200) if parpadeo else (60, 50, 10), (pm.centerx, pm.centery), 5, width=1)
            elif estado_pm in ("avanzando", "regresando"):
                pygame.draw.circle(mundo, (80, 220, 100), (pm.centerx, pm.centery), 5)
                pygame.draw.circle(mundo, (180, 255, 190), (pm.centerx, pm.centery), 5, width=1)
            else:
                col_ind = (240, 180, 40) if plataforma_movil.get("tiempo_con_peso", 0) > 0 else (180, 80, 55)
                pygame.draw.circle(mundo, col_ind, (pm.centerx, pm.centery), 4)

        if boton_nivel is not None:
            rect_b = boton_nivel["rect"]
            h_actual = 4 if boton_nivel["presionado"] else 12
            y_actual = suelo.top - h_actual
            pygame.draw.rect(mundo, (90, 70, 60), (rect_b.left - 6, suelo.top - 4, rect_b.width + 12, 10), border_radius=2)
            col_btn = (80, 200, 100) if boton_nivel["presionado"] else (225, 65, 65)
            col_borde_btn = (50, 150, 70) if boton_nivel["presionado"] else (175, 45, 45)
            pygame.draw.rect(mundo, col_btn, (rect_b.x, y_actual, rect_b.width, h_actual), border_top_left_radius=3, border_top_right_radius=3)
            pygame.draw.rect(mundo, col_borde_btn, (rect_b.x, y_actual, rect_b.width, h_actual), width=2, border_top_left_radius=3, border_top_right_radius=3)

        if pared_nivel is not None:
            pr = pared_nivel["rect"]
            for y_linea in range(pr.top + 30, pr.bottom - 10, 35):
                if 0 <= y_linea <= ALTO:
                    pygame.draw.line(mundo, COLOR_BORDE_PLATAFORMA, (pr.left + 4, y_linea), (pr.right - 4, y_linea), 2)

        if laser_nivel is not None:
            dibujar_laser_escenario(mundo, laser_nivel)

        if paredes_colores is not None:
            dibujar_paredes_colores_escenario(mundo, paredes_colores)

        if botones_colores is not None:
            dibujar_botones_colores_escenario(mundo, botones_colores, suelo)

        if usar_agua: dibujar_agua(mundo, ZONA_AGUA)
        if usar_soga and not p1_completado and not p2_completado:
            dibujar_soga_escenario(mundo, jugador1, jugador2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        if usar_caja: mundo.blit(caja["sprite"], caja["rect"])

        if usar_llave:
            estado_p = "abierta" if puerta["abierta"] else "cerrada"
            mundo.blit(puerta["sprites"][estado_p], puerta["rect"])
            if llave and not puerta["abierta"]:
                if numero_mundo == 3:
                    halo_surf = pygame.Surface((44, 60), pygame.SRCALPHA)
                    alpha_h = int(60 + 25 * math.sin(tick_m3 * 0.08))
                    pygame.draw.ellipse(halo_surf, (255, 230, 90, alpha_h), (0, 0, 44, 60))
                    mundo.blit(halo_surf, (llave["rect"].centerx - 22, llave["rect"].centery - 30))
                mundo.blit(llave["sprite"], llave["rect"])

        if not p1_completado: dibujar_personaje(mundo, jugador1, ZONA_AGUA if usar_agua else None)
        if not p2_completado: dibujar_personaje(mundo, jugador2, ZONA_AGUA if usar_agua else None)

        if numero_mundo == 3 and numero_nivel == 4 and surf_oscuridad_m3_n4 is not None:
            dibujar_oscuridad_laberinto(
                mundo,
                [(jugador1, linterna_p1, p1_completado), (jugador2, linterna_p2, p2_completado)],
                surf_oscuridad_m3_n4,
                surf_luz_linterna,
                surf_luz_tenue
            )
        elif numero_mundo == 3 and numero_nivel == 5:
            dibujar_linternas_submarinas_m3_n5(
                mundo,
                [(jugador1, linterna_p1, p1_completado), (jugador2, linterna_p2, p2_completado)],
                tick_m3
            )
            if not p1_completado:
                dibujar_alerta_oxigeno_personaje(mundo, jugador1, oxigeno_p1, tick_m3)
            if not p2_completado:
                dibujar_alerta_oxigeno_personaje(mundo, jugador2, oxigeno_p2, tick_m3)

        # Controles tutorial directamente arriba de cada personaje
        if numero_mundo == 1 and numero_nivel == 1 and mostrar_tutorial:
            _dibujar_controles_tutorial(mundo, alpha_p1=alpha_tut_p1, alpha_p2=alpha_tut_p2, teclas_actuales=teclas)

        # Efecto de ráfaga y animación de teclas sopladas
        if numero_mundo == 1 and numero_nivel == 1:
            _actualizar_y_dibujar_soplado(mundo)

        if p1_completado and not p2_completado:
            # Jugador 1 ya pasó por la puerta: cámara completa siguiendo al Jugador 2
            cam_x = max(0, min(jugador2["hitbox"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif p2_completado and not p1_completado:
            # Jugador 2 ya pasó por la puerta: cámara completa siguiendo al Jugador 1
            cam_x = max(0, min(jugador1["hitbox"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif (p1_completado and p2_completado) or (numero_mundo == 3 and ((jugador1["muerto"] and p2_completado) or (jugador2["muerto"] and p1_completado))):
            # Nivel completado: cámara fija centrada en la puerta de salida
            cam_x = max(0, min(puerta["rect"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif numero_mundo == 3 and jugador1["muerto"] and not jugador2["muerto"]:
            # En Mundo 3, P1 murió: la cámara sigue completamente al sobreviviente P2
            cam_x = max(0, min(jugador2["hitbox"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif numero_mundo == 3 and jugador2["muerto"] and not jugador1["muerto"]:
            # En Mundo 3, P2 murió: la cámara sigue completamente al sobreviviente P1
            cam_x = max(0, min(jugador1["hitbox"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
            pantalla.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, ANCHO, ALTO))
        elif numero_mundo == 3 and jugador1["muerto"] and jugador2["muerto"]:
            # Ambos murieron en Mundo 3: mantener la cámara en el centro promedio
            centro = (jugador1["hitbox"].centerx + jugador2["hitbox"].centerx) // 2
            cam_x = max(0, min(centro - ANCHO // 2, ancho_mundo_nivel - ANCHO))
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

        # Botones HUD en la esquina superior derecha solo si el nivel continúa activo
        if not (p1_completado and p2_completado):
            pos_m_hud = pygame.mouse.get_pos()
            spr_cfg_hud = spr_config_hover if (rect_btn_config.collidepoint(pos_m_hud) and spr_config_hover) else spr_config_normal
            spr_c_hud = spr_casa_hover if (rect_btn_casa.collidepoint(pos_m_hud) and spr_casa_hover) else spr_casa_normal
            spr_r_hud = spr_reiniciar_hover if (rect_btn_reiniciar.collidepoint(pos_m_hud) and spr_reiniciar_hover) else spr_reiniciar_normal
            spr_x_hud = spr_x_hover if (rect_btn_x.collidepoint(pos_m_hud) and spr_x_hover) else spr_x_normal

            fondo_btn_config = pantalla.subsurface(rect_btn_config).copy()
            fondo_btn_casa = pantalla.subsurface(rect_btn_casa).copy()
            fondo_btn_reiniciar = pantalla.subsurface(rect_btn_reiniciar).copy()
            fondo_btn_x = pantalla.subsurface(rect_btn_x).copy()

            if spr_cfg_hud: pantalla.blit(spr_cfg_hud, rect_btn_config)
            if spr_c_hud: pantalla.blit(spr_c_hud, rect_btn_casa)
            if spr_r_hud: pantalla.blit(spr_r_hud, rect_btn_reiniciar)
            if spr_x_hud: pantalla.blit(spr_x_hud, rect_btn_x)

        if numero_mundo == 3 and numero_nivel == 4 and not (p1_completado and p2_completado):
            _dibujar_hud_linternas_m3_n4(pantalla, linterna_p1, linterna_p2, p1_color, p2_color)
        if numero_mundo == 3 and numero_nivel == 5 and not (p1_completado and p2_completado):
            _dibujar_hud_oxigeno_m3_n5(pantalla, oxigeno_p1, oxigeno_p2, p1_color, p2_color, tick_m3)
            _dibujar_hud_linternas_m3_n4(pantalla, linterna_p1, linterna_p2, p1_color, p2_color, y_base=60)

        pygame.display.flip()

        # Gestión de pantalla de muerte y reinicio según las reglas de cada mundo
        debe_mostrar_muerte = False
        if numero_mundo == 3:
            if jugador1["muerto"] and jugador2["muerto"]:
                if jugador1["muerte_terminada"] and jugador2["muerte_terminada"]:
                    debe_mostrar_muerte = True
        else:
            muertos = [p for p in (jugador1, jugador2) if p.get("muerto", False)]
            if muertos and all(p.get("muerte_terminada", False) for p in muertos):
                debe_mostrar_muerte = True

        if debe_mostrar_muerte:
            resultado = pantalla_muerte(pantalla, reloj)
            if resultado == "salir": return "salir"
            if resultado == "reiniciar":
                _reiniciar_nivel_completo()

        # Condición de nivel superado
        nivel_superado = False
        if numero_mundo == 3:
            if (p1_completado and p2_completado) or \
               (jugador1["muerto"] and p2_completado) or \
               (jugador2["muerto"] and p1_completado):
                nivel_superado = True
        else:
            if p1_completado and p2_completado:
                nivel_superado = True

        if nivel_superado:
            cam_puerta_x = max(0, min(puerta["rect"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO)) if puerta else 0
            return animar_transicion_nivel_completado(
                pantalla=pantalla,
                reloj=reloj,
                hay_siguiente=hay_siguiente_nivel,
                mundo=numero_mundo,
                numero_nivel=numero_nivel,
                puerta=puerta,
                mundo_surface=mundo,
                cam_x=cam_puerta_x,
                ancho_mundo_nivel=ancho_mundo_nivel,
                color_p1=p1_color,
                color_p2=p2_color,
                niveles_desbloqueados=niveles_desbloqueados,
                partida_id=partida_id,
                partida_nombre=partida_nombre,
                snapshot_guardado=snapshot_guardado,
            )

    return "salir"