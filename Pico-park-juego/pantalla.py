import os
import sys
import math
import random
import pygame

from sprites import (
    ANCHO, ALTO, FPS,
    COLOR_JUGADOR1, COLOR_JUGADOR2,
    RUTA_BOTONES,
    dibujar_personaje,
    dibujar_agua,
    cargar_boton,
    animar_pulsacion_boton,
    aclarar_boton,
)
from movimientos import (
    crear_personaje,
    crear_caja,
    crear_pinchos,
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
)
from guardado import (
    crear_desbloqueados_inicial,
    mostrar_dialogo_guardar_salir,
)

COLOR_SOGA = (200, 160, 100)
COLOR_BOTON_SALIR = (150, 45, 45)
COLOR_PLATAFORMA = (225, 110, 80)
COLOR_BORDE_PLATAFORMA = (185, 80, 55)
ANCHO_MUNDO = 3000
DISTANCIA_SPLIT = 850


def pantalla_muerte(pantalla, reloj):
    fuente_titulo = pygame.font.Font(None, 60)
    fuente_texto = pygame.font.Font(None, 36)

    w_btn, h_btn = 260, 76

    boton_menu_normal = cargar_boton("Ventanas/boton-menu.png") or cargar_boton("boton-menu.png") or cargar_boton("salir.png")
    boton_menu_semi = cargar_boton("Ventanas/boton-menu-semiapretado.png") or cargar_boton("boton-menu-semiapretado.png") or cargar_boton("salir-preapretado.png")
    boton_menu_apretado = cargar_boton("Ventanas/boton-menu-apretado.png") or cargar_boton("boton-menu-apretado.png") or cargar_boton("salir-apretado.png")

    boton_reiniciar_normal = cargar_boton("Ventanas/boton-reiniciar.png") or cargar_boton("boton-reiniciar.png")
    boton_reiniciar_semi = cargar_boton("Ventanas/boton-reiniciar-semiapretado.png") or cargar_boton("boton-reiniciar-semiapretado.png")
    boton_reiniciar_apretado = cargar_boton("Ventanas/boton-reiniciar-apretado.png") or cargar_boton("boton-reiniciar-apretado.png")

    if any(x is None for x in (
        boton_menu_normal, boton_menu_apretado,
        boton_reiniciar_normal, boton_reiniciar_apretado
    )):
        return "salir"

    boton_reiniciar_normal = pygame.transform.smoothscale(boton_reiniciar_normal, (w_btn, h_btn))
    if boton_reiniciar_semi:
        boton_reiniciar_semi = pygame.transform.smoothscale(boton_reiniciar_semi, (w_btn, h_btn))
    boton_reiniciar_apretado = pygame.transform.smoothscale(boton_reiniciar_apretado, (w_btn, h_btn))

    boton_menu_normal = pygame.transform.smoothscale(boton_menu_normal, (w_btn, h_btn))
    if boton_menu_semi:
        boton_menu_semi = pygame.transform.smoothscale(boton_menu_semi, (w_btn, h_btn))
    boton_menu_apretado = pygame.transform.smoothscale(boton_menu_apretado, (w_btn, h_btn))

    boton_reiniciar = boton_reiniciar_normal.get_rect(center=(ANCHO // 2 - 150, 400))
    boton_menu = boton_menu_normal.get_rect(center=(ANCHO // 2 + 150, 400))

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
                    animar_pulsacion_boton(pantalla, boton_reiniciar, boton_reiniciar_semi, boton_reiniciar_apretado, (25, 25, 25))
                    return "reiniciar"

                if boton_menu.collidepoint(evento.pos):
                    animar_pulsacion_boton(pantalla, boton_menu, boton_menu_semi, boton_menu_apretado, (25, 25, 25))
                    return "salir"

        pantalla.fill((25, 25, 25))
        titulo = fuente_titulo.render("¡Te moriste!", True, (255, 80, 80))
        texto = fuente_texto.render("¿Querés reiniciar o salir?", True, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 180)))
        pantalla.blit(texto, texto.get_rect(center=(ANCHO // 2, 250)))

        spr_r = boton_reiniciar_hover if (hov_reinicio and boton_reiniciar_hover) else boton_reiniciar_normal
        spr_m = boton_menu_hover if (hov_menu and boton_menu_hover) else boton_menu_normal

        pantalla.blit(spr_r, boton_reiniciar)
        pantalla.blit(spr_m, boton_menu)
        pygame.display.flip()
        reloj.tick(FPS)


def obtener_fuente_elegante(tamanio, negrita=True):
    for nombre in ["Segoe UI", "Arial Rounded MT Bold", "Arial", "Trebuchet MS"]:
        try:
            return pygame.font.SysFont(nombre, tamanio, bold=negrita)
        except Exception:
            pass
    return pygame.font.Font(None, int(tamanio * 1.1))


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

    frames_totales = 68
    duracion = 1.13

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


def mostrar_pantalla_victoria(pantalla, reloj, mundo=1, numero_nivel=1, hay_siguiente=True, color_p1=None, color_p2=None):
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

    # --- FASE 1: Ensamblaje de bloques (54 fotogramas ~ 0.9s) ---
    frames_ensamble = 54
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

    # Fuentes estilizadas
    fuente_titulo = obtener_fuente_elegante(40, negrita=True)
    fuente_sub = obtener_fuente_elegante(25, negrita=True)
    fuente_badge = obtener_fuente_elegante(21, negrita=True)
    fuente_btn = obtener_fuente_elegante(27, negrita=True)

    w_btn = 272
    h_btn = 80
    btn1_x = cx - w_btn // 2
    btn1_target_y = rect_panel.top + 215
    btn2_x = cx - w_btn // 2
    btn2_target_y = rect_panel.top + 305

    rect_btn1 = pygame.Rect(btn1_x, btn1_target_y, w_btn, h_btn)
    rect_btn2 = pygame.Rect(btn2_x, btn2_target_y, w_btn, h_btn)

    spr_sig_normal = cargar_boton("Ventanas/boton-siguiente.png") or cargar_boton("boton-siguiente.png")
    spr_sig_semi = cargar_boton("Ventanas/boton-siguiente-semiapretado.png") or cargar_boton("boton-siguiente-semiapretado.png")
    spr_sig_apretado = cargar_boton("Ventanas/boton-siguiente-apretado.png") or cargar_boton("boton-siguiente-apretado.png")

    spr_menu_normal = cargar_boton("Ventanas/boton-menu.png") or cargar_boton("boton-menu.png")
    spr_menu_semi = cargar_boton("Ventanas/boton-menu-semiapretado.png") or cargar_boton("boton-menu-semiapretado.png")
    spr_menu_apretado = cargar_boton("Ventanas/boton-menu-apretado.png") or cargar_boton("boton-menu-apretado.png")

    if spr_sig_normal: spr_sig_normal = pygame.transform.smoothscale(spr_sig_normal, (w_btn, h_btn))
    if spr_sig_semi: spr_sig_semi = pygame.transform.smoothscale(spr_sig_semi, (w_btn, h_btn))
    if spr_sig_apretado: spr_sig_apretado = pygame.transform.smoothscale(spr_sig_apretado, (w_btn, h_btn))

    if spr_menu_normal: spr_menu_normal = pygame.transform.smoothscale(spr_menu_normal, (w_btn, h_btn))
    if spr_menu_semi: spr_menu_semi = pygame.transform.smoothscale(spr_menu_semi, (w_btn, h_btn))
    if spr_menu_apretado: spr_menu_apretado = pygame.transform.smoothscale(spr_menu_apretado, (w_btn, h_btn))

    spr_sig_hover = aclarar_boton(spr_sig_normal) if spr_sig_normal else None
    spr_menu_hover = aclarar_boton(spr_menu_normal) if spr_menu_normal else None

    txt_btn1 = "SIGUIENTE NIVEL →" if hay_siguiente else "¡JUEGO COMPLETADO!"
    txt_btn2 = "VOLVER AL MENÚ"

    nom_nivel = f"MUNDO {mundo} — NIVEL {numero_nivel}"

    # --- FASE 2: Entrada secuencial del título y botones con rebote (38 fotogramas ~ 0.63s) ---
    frames_intro = 38
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
        t_tit_surf = fuente_titulo.render("¡NIVEL COMPLETADO!", True, (255, 255, 255))
        pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, y_tit)))

        # Subtítulo y cápsula de nivel
        if f >= 8:
            t_sub = fuente_sub.render("¡Buen trabajo!", True, (75, 70, 70))
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
                return "salir"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn1.collidepoint(evento.pos):
                    boton_presionado = 1
                elif rect_btn2.collidepoint(evento.pos):
                    boton_presionado = 2

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if boton_presionado == 1 and rect_btn1.collidepoint(evento.pos):
                    if spr_sig_semi and spr_sig_apretado and hay_siguiente:
                        animar_pulsacion_boton(pantalla, rect_btn1, spr_sig_semi, spr_sig_apretado, fondo_limpio_btn1)
                    elif spr_menu_semi and spr_menu_apretado and not hay_siguiente:
                        animar_pulsacion_boton(pantalla, rect_btn1, spr_menu_semi, spr_menu_apretado, fondo_limpio_btn1)
                    accion_seleccionada = "siguiente" if hay_siguiente else "menu"
                elif boton_presionado == 2 and rect_btn2.collidepoint(evento.pos):
                    if spr_menu_semi and spr_menu_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn2, spr_menu_semi, spr_menu_apretado, fondo_limpio_btn2)
                    accion_seleccionada = "menu"
                boton_presionado = None

        if accion_seleccionada is not None:
            break

        pantalla.fill((0, 0, 0))
        dibujar_panel_victoria_solido(pantalla, rect_panel, color_p1, color_p2)

        # Título
        t_tit_surf = fuente_titulo.render("¡NIVEL COMPLETADO!", True, (255, 255, 255))
        pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, rect_panel.top + 35)))

        # Subtítulo y cápsula
        t_sub = fuente_sub.render("¡Buen trabajo!", True, (75, 70, 70))
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
    )


def dibujar_pinchos_escenario(superficie, pinchos):
    col_cuerpo = (235, 235, 240)
    col_borde = (110, 110, 115)
    for p in pinchos:
        if p.width < p.height:
            # Pincho en pared interna izquierda apuntando horizontalmente hacia la derecha
            puntos = [(p.left, p.top), (p.right, p.centery), (p.left, p.bottom)]
        else:
            # Pincho en suelo horizontal apuntando hacia arriba
            puntos = [(p.left, p.bottom), (p.centerx, p.top), (p.right, p.bottom)]
        pygame.draw.polygon(superficie, col_cuerpo, puntos)
        pygame.draw.polygon(superficie, col_borde, puntos, 2)


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
    - Cuando alcanza el límite máximo, la soga se tensa recta con acabado estilizado.
    - Anclada en el torso/cintura para no tapar los rostros ni interferir con los sprites.
    """
    if p1 is None or p2 is None:
        return
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]
    p_inicio = (hb1.centerx, hb1.centery + 6)
    p_fin = (hb2.centerx, hb2.centery + 6)

    dx = p_fin[0] - p_inicio[0]
    dy = p_fin[1] - p_inicio[1]
    dist = math.hypot(dx, dy)

    col_soga_ext = (175, 125, 65)
    col_soga_int = (215, 170, 105)

    if dist < 16:
        pygame.draw.line(superficie, col_soga_ext, p_inicio, p_fin, 4)
        pygame.draw.line(superficie, col_soga_int, p_inicio, p_fin, 2)
        return

    # Grado de tensión visual entre 0.0 (reposo) y 1.0 (máximo estiramiento)
    if dist <= d_reposo:
        tension_visual = 0.0
    else:
        tension_visual = min(1.0, (dist - d_reposo) / max(1.0, d_max - d_reposo))

    if tension_visual < 0.96 and dist < d_max:
        sag_max = min(52.0, max(10.0, (d_max - dist) * 0.42))
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


def iniciar_mundo(mecanicas=None, numero_nivel=1, color_p1=None, color_p2=None, mundo=1, niveles_desbloqueados=None, partida_id=None, partida_nombre=None):
    numero_mundo = mundo
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
    spr_x_hover = aclarar_boton(spr_x_normal)

    spr_reiniciar_normal = _cargar_hud("boton-reiniciar-icono.png")
    spr_reiniciar_semi = _cargar_hud("boton-reiniciar-icono-semiapretado.png")
    spr_reiniciar_apretado = _cargar_hud("boton-reiniciar-icono-apretado.png")
    spr_reiniciar_hover = aclarar_boton(spr_reiniciar_normal)

    spr_casa_normal = _cargar_hud("boton-casa.png")
    spr_casa_semi = _cargar_hud("boton-casa-semiapretado.png")
    spr_casa_apretado = _cargar_hud("boton-casa-apretado.png")
    spr_casa_hover = aclarar_boton(spr_casa_normal)

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
        # - Llave ubicada al final del recorrido superior (x=1680, y=plat_superior.top - 46).
        # - La plataforma superior finaliza en x=1760, permitiendo que el personaje superior baje al suelo derecho.
        # - Puerta de salida al final del nivel en el suelo derecho (x=1920, y=suelo.top - 90).
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
        # Termina en x=1730 para dejar un espacio de descenso hasta el inicio de la barrera en x=1790.
        plat_superior = pygame.Rect(340, 480, 1390, 24)
        # Techo/riel superior decorativo (y=170, altura 26px)
        techo_superior = pygame.Rect(320, 170, 1440, 26)

        # Barrera sólida en forma de L invertida para impedir que los personajes hagan trampas:
        # - Tramo horizontal ubicado por encima de la puerta y del área inferior (top=480, espesor 24px, x=1790 a 2030)
        # - Tramo vertical conectado en su extremo derecho que baja hasta el suelo (x=2006 a 2030, y=480 a suelo.top=640)
        # - Colisión sólida real y continua; sin huecos con el suelo ni entre ambos tramos.
        barrera_l_horiz = pygame.Rect(1790, 480, 240, 24)
        barrera_l_vert = pygame.Rect(2006, 480, 24, suelo.top - 480)

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

        # Llave sobre la plataforma superior en la zona final antes del descenso
        llave = crear_llave(1650, plat_superior.top - 46)

        # Puerta de salida en el suelo bajo el tramo horizontal de la barrera en L
        puerta = crear_puerta(1880, suelo.top - 90)
    elif numero_mundo == 2 and numero_nivel == 1:
        # Mundo 2 - Nivel 1: Introducción a la Soga (El arrastre cooperativo)
        # Nivel introductorio centrado en aprender a moverse y coordinar saltos unidos por la soga
        ancho_mundo_nivel = 2200
        suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
        mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

        usar_caja = False
        usar_soga = True
        usar_agua = False
        usar_pinchos = False
        usar_llave = True

        # Zona inicial: ambos personajes caen desde la parte superior unidos por la soga
        jugador1 = crear_personaje(120, 0, p1_color)
        jugador2 = crear_personaje(210, 0, p2_color)

        caja = None
        pinchos = []

        # 1. Primer obstáculo: escalones amplios para subir y caminar juntos
        escalon_1 = pygame.Rect(440, 580, 230, 60)
        escalon_2 = pygame.Rect(670, 520, 250, 120)

        # 2. Zona de saltos coordinados entre plataformas a distintas alturas
        plat_salto_1 = pygame.Rect(990, 460, 220, 26)
        plat_salto_2 = pygame.Rect(1280, 400, 220, 26)

        # Plataforma de retorno en la zona baja por si un jugador cae
        plat_retorno = pygame.Rect(990, 580, 510, 60)

        # 3. Brecha de separación que exige coordinar el avance y uso de la soga
        # 4. Plataforma de destino amplia con llave y puerta
        plat_destino = pygame.Rect(1620, 430, 520, 26)

        plataformas = [escalon_1, escalon_2, plat_salto_1, plat_salto_2, plat_retorno, plat_destino]

        # Llave cerca del final del recorrido sobre la plataforma de destino
        llave = crear_llave(1820, plat_destino.top - 46)

        # Puerta de salida en la plataforma de destino
        puerta = crear_puerta(2040, plat_destino.top - 90)
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
    mundo_inicio.fill((255, 240, 195))

    if pozo_nivel is not None:
        pz = pozo_nivel
        pygame.draw.rect(mundo_inicio, (235, 222, 192), (pz["x"], pz["y"], pz["ancho"], pz["alto"]))
        pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (pz["x"], pz["y"]), (pz["x"], pz["y"] + pz["alto"]), 2)
        pygame.draw.line(mundo_inicio, COLOR_BORDE_PLATAFORMA, (pz["x"] + pz["ancho"], pz["y"]), (pz["x"] + pz["ancho"], pz["y"] + pz["alto"]), 2)

    for plat in plataformas:
        if barrera_l_horiz is not None and (plat is barrera_l_horiz or plat is barrera_l_vert):
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

    if usar_agua:
        dibujar_agua(mundo_inicio)
    if usar_soga and not p1_completado and not p2_completado:
        dibujar_soga_escenario(mundo_inicio, jugador1, jugador2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    if usar_caja:
        mundo_inicio.blit(caja["sprite"], caja["rect"])

    if usar_llave and puerta:
        estado_p = "cerrada"
        mundo_inicio.blit(puerta["sprites"][estado_p], puerta["rect"])
        if llave:
            mundo_inicio.blit(llave["sprite"], llave["rect"])

    dibujar_personaje(mundo_inicio, jugador1, ZONA_AGUA if usar_agua else None)
    dibujar_personaje(mundo_inicio, jugador2, ZONA_AGUA if usar_agua else None)

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

    if spr_casa_normal: pantalla.blit(spr_casa_normal, rect_btn_casa)
    if spr_reiniciar_normal: pantalla.blit(spr_reiniciar_normal, rect_btn_reiniciar)
    if spr_x_normal: pantalla.blit(spr_x_normal, rect_btn_x)

    captura_nuevo_nivel = pantalla.copy()
    animar_apertura_franjas(pantalla, reloj, captura_nuevo_nivel)

    ejecutando = True
    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                resp = mostrar_dialogo_guardar_salir(
                    pantalla, reloj,
                    niveles_desbloqueados=niveles_desbloqueados,
                    id_partida=partida_id,
                    nombre_partida=partida_nombre,
                )
                if resp != "cancelar":
                    pygame.quit()
                    sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    if spr_reiniciar_semi and spr_reiniciar_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_reiniciar, spr_reiniciar_semi, spr_reiniciar_apretado, fondo_btn_reiniciar)
                    reiniciar_juego(jugador1, jugador2, caja, llave, puerta, estado_soga=estado_soga)
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
                        if plataformas_base is not None:
                            plataformas = list(plataformas_base) + [p["rect"] for p in paredes_colores]
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

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    if spr_x_semi and spr_x_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, fondo_btn_x)
                    resp = mostrar_dialogo_guardar_salir(
                        pantalla, reloj,
                        niveles_desbloqueados=niveles_desbloqueados,
                        id_partida=partida_id,
                        nombre_partida=partida_nombre,
                    )
                    if resp != "cancelar":
                        pygame.quit()
                        sys.exit()

                if rect_btn_reiniciar.collidepoint(evento.pos):
                    if spr_reiniciar_semi and spr_reiniciar_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_reiniciar, spr_reiniciar_semi, spr_reiniciar_apretado, fondo_btn_reiniciar)
                    reiniciar_juego(jugador1, jugador2, caja, llave, puerta, estado_soga=estado_soga)
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
                        if plataformas_base is not None:
                            plataformas = list(plataformas_base) + [p["rect"] for p in paredes_colores]
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
            not p1_completado and not p2_completado
            and abs(jugador1["hitbox"].bottom - jugador2["hitbox"].top) <= 8
            and jugador1["hitbox"].right > jugador2["hitbox"].left + 2
            and jugador1["hitbox"].left < jugador2["hitbox"].right - 2
        )
        p2_sobre_p1 = (
            not p1_completado and not p2_completado
            and abs(jugador2["hitbox"].bottom - jugador1["hitbox"].top) <= 8
            and jugador2["hitbox"].right > jugador1["hitbox"].left + 2
            and jugador2["hitbox"].left < jugador1["hitbox"].right - 2
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

        if usar_soga and not p1_completado and not p2_completado:
            actualizar_fisica_soga(jugador1, jugador2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)

        if usar_agua:
            actualizar_estado_agua(jugador1)
            actualizar_estado_agua(jugador2)
            if jugador1["en_agua"]: aplicar_fisica_agua(jugador1, teclas[pygame.K_w], teclas[pygame.K_s])
            if jugador2["en_agua"]: aplicar_fisica_agua(jugador2, teclas[pygame.K_UP], teclas[pygame.K_DOWN])

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

        if usar_caja:
            actualizar_caja(caja, suelo, mundo_rect, plataformas)
            if numero_mundo == 1 and numero_nivel == 4 and caja is not None:
                if caja["rect"].left < 20:
                    caja["rect"].left = 20

        if not jugador1["muerto"] and not p1_completado:
            resolver_colisiones(jugador1, jugador2 if not p2_completado else None, suelo, mundo_rect, caja if usar_caja else None, jugador1["en_agua"], plataformas)
        if not jugador2["muerto"] and not p2_completado:
            resolver_colisiones(jugador2, jugador1 if not p1_completado else None, suelo, mundo_rect, caja if usar_caja else None, jugador2["en_agua"], plataformas)

        if usar_soga and not p1_completado and not p2_completado:
            aplicar_restriccion_soga(jugador1, jugador2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if usar_llave:
            personajes_activos = [p for p, comp in [(jugador1, p1_completado), (jugador2, p2_completado)] if not comp]
            actualizar_llave(llave, personajes_activos, puerta)
        if usar_pinchos:
            if not p1_completado: comprobar_pinchos(jugador1, pinchos)
            if not p2_completado: comprobar_pinchos(jugador2, pinchos)

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

        actualizar_muerte(jugador1)
        actualizar_muerte(jugador2)

        if not jugador1["muerto"] and not p1_completado: jugador1["hitbox"].clamp_ip(mundo_rect)
        if not jugador2["muerto"] and not p2_completado: jugador2["hitbox"].clamp_ip(mundo_rect)

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

        mundo = pygame.Surface((ancho_mundo_nivel, ALTO))
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

        if usar_agua: dibujar_agua(mundo)
        if usar_soga and not p1_completado and not p2_completado:
            dibujar_soga_escenario(mundo, jugador1, jugador2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        if usar_caja: mundo.blit(caja["sprite"], caja["rect"])

        if usar_llave:
            estado_p = "abierta" if puerta["abierta"] else "cerrada"
            mundo.blit(puerta["sprites"][estado_p], puerta["rect"])
            if llave and not puerta["abierta"]:
                mundo.blit(llave["sprite"], llave["rect"])

        if not p1_completado: dibujar_personaje(mundo, jugador1, ZONA_AGUA if usar_agua else None)
        if not p2_completado: dibujar_personaje(mundo, jugador2, ZONA_AGUA if usar_agua else None)

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
        elif p1_completado and p2_completado:
            # Ambos personajes completaron el nivel: cámara fija centrada en la puerta de salida
            cam_x = max(0, min(puerta["rect"].centerx - ANCHO // 2, ancho_mundo_nivel - ANCHO))
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
            try:
                fondo_btn_casa = pantalla.subsurface(rect_btn_casa).copy()
                fondo_btn_reiniciar = pantalla.subsurface(rect_btn_reiniciar).copy()
                fondo_btn_x = pantalla.subsurface(rect_btn_x).copy()
            except Exception:
                pass

            pos_m_hud = pygame.mouse.get_pos()
            spr_c_hud = spr_casa_hover if (rect_btn_casa.collidepoint(pos_m_hud) and spr_casa_hover) else spr_casa_normal
            spr_r_hud = spr_reiniciar_hover if (rect_btn_reiniciar.collidepoint(pos_m_hud) and spr_reiniciar_hover) else spr_reiniciar_normal
            spr_x_hud = spr_x_hover if (rect_btn_x.collidepoint(pos_m_hud) and spr_x_hover) else spr_x_normal

            if spr_c_hud: pantalla.blit(spr_c_hud, rect_btn_casa)
            if spr_r_hud: pantalla.blit(spr_r_hud, rect_btn_reiniciar)
            if spr_x_hud: pantalla.blit(spr_x_hud, rect_btn_x)

        pygame.display.flip()

        if jugador1["muerte_terminada"] or jugador2["muerte_terminada"]:
            resultado = pantalla_muerte(pantalla, reloj)
            if resultado == "salir": return "salir"
            if resultado == "reiniciar":
                reiniciar_juego(jugador1, jugador2, caja, llave, puerta, estado_soga=estado_soga)
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
                    if plataformas_base is not None:
                        plataformas = list(plataformas_base) + [p["rect"] for p in paredes_colores]
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

        if p1_completado and p2_completado:
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
            )

    return "salir"