import os
import sys
import math
import random
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
from guardado import (
    crear_desbloqueados_inicial,
    mostrar_dialogo_guardar_salir,
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

    w_btn = min(360, w_panel - 80)
    h_btn = 56
    btn1_x = cx - w_btn // 2
    btn1_target_y = rect_panel.top + 225
    btn2_x = cx - w_btn // 2
    btn2_target_y = rect_panel.top + 295

    rect_btn1 = pygame.Rect(btn1_x, btn1_target_y, w_btn, h_btn)
    rect_btn2 = pygame.Rect(btn2_x, btn2_target_y, w_btn, h_btn)

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

            pygame.draw.rect(pantalla, (195, 185, 165), (r2_anim.x, r2_anim.y + 4, r2_anim.w, r2_anim.h), border_radius=8)
            pygame.draw.rect(pantalla, (245, 235, 215), r2_anim, border_radius=8)
            pygame.draw.rect(pantalla, (70, 70, 75), r2_anim, width=3, border_radius=8)
            tb2 = fuente_btn.render(txt_btn2, True, (50, 50, 55))
            pantalla.blit(tb2, tb2.get_rect(center=r2_anim.center))

        pygame.display.flip()

    # --- FASE 3: Interacción del usuario (hover y selección) ---
    accion_seleccionada = None
    boton_presionado = None

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
                    accion_seleccionada = "siguiente" if hay_siguiente else "menu"
                elif boton_presionado == 2 and rect_btn2.collidepoint(evento.pos):
                    accion_seleccionada = "menu"
                boton_presionado = None

        if accion_seleccionada is not None:
            # Animación breve de pulsación/selección confirmada
            for _ in range(8):
                reloj.tick(FPS)
                pygame.event.pump()
                pantalla.fill((0, 0, 0))
                dibujar_panel_victoria_solido(pantalla, rect_panel, color_p1, color_p2)
                t_tit_surf = fuente_titulo.render("¡NIVEL COMPLETADO!", True, (255, 255, 255))
                pantalla.blit(t_tit_surf, t_tit_surf.get_rect(center=(cx, rect_panel.top + 35)))
                t_sub = fuente_sub.render("¡Buen trabajo!", True, (75, 70, 70))
                pantalla.blit(t_sub, t_sub.get_rect(center=(cx, rect_panel.top + 98)))
                r_badge = pygame.Rect(cx - 150, rect_panel.top + 132, 300, 36)
                pygame.draw.rect(pantalla, (255, 255, 255), r_badge, border_radius=8)
                pygame.draw.rect(pantalla, (210, 195, 160), r_badge, width=2, border_radius=8)
                t_nb = fuente_badge.render(nom_nivel, True, (50, 45, 40))
                pantalla.blit(t_nb, t_nb.get_rect(center=r_badge.center))

                # Dibujar botón seleccionado presionado
                if accion_seleccionada == "siguiente" or (not hay_siguiente and accion_seleccionada == "menu"):
                    r1_draw = pygame.Rect(rect_btn1.x, rect_btn1.y + 3, rect_btn1.w, rect_btn1.h)
                    pygame.draw.rect(pantalla, (190, 80, 55), r1_draw, border_radius=8)
                    pygame.draw.rect(pantalla, (130, 40, 25), r1_draw, width=3, border_radius=8)
                    tb1 = fuente_btn.render(txt_btn1, True, (240, 240, 240))
                    pantalla.blit(tb1, tb1.get_rect(center=r1_draw.center))

                    pygame.draw.rect(pantalla, (195, 185, 165), (rect_btn2.x, rect_btn2.y + 4, rect_btn2.w, rect_btn2.h), border_radius=8)
                    pygame.draw.rect(pantalla, (245, 235, 215), rect_btn2, border_radius=8)
                    pygame.draw.rect(pantalla, (70, 70, 75), rect_btn2, width=3, border_radius=8)
                    tb2 = fuente_btn.render(txt_btn2, True, (50, 50, 55))
                    pantalla.blit(tb2, tb2.get_rect(center=rect_btn2.center))
                else:
                    pygame.draw.rect(pantalla, (160, 50, 35), (rect_btn1.x, rect_btn1.y + 4, rect_btn1.w, rect_btn1.h), border_radius=8)
                    pygame.draw.rect(pantalla, (225, 110, 80), rect_btn1, border_radius=8)
                    pygame.draw.rect(pantalla, (150, 45, 30), rect_btn1, width=3, border_radius=8)
                    tb1 = fuente_btn.render(txt_btn1, True, (255, 255, 255))
                    pantalla.blit(tb1, tb1.get_rect(center=rect_btn1.center))

                    r2_draw = pygame.Rect(rect_btn2.x, rect_btn2.y + 3, rect_btn2.w, rect_btn2.h)
                    pygame.draw.rect(pantalla, (220, 210, 190), r2_draw, border_radius=8)
                    pygame.draw.rect(pantalla, (35, 35, 40), r2_draw, width=3, border_radius=8)
                    tb2 = fuente_btn.render(txt_btn2, True, (35, 35, 40))
                    pantalla.blit(tb2, tb2.get_rect(center=r2_draw.center))
                pygame.display.flip()
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

        # Renderizado interactivo Botón 1 («SIGUIENTE NIVEL →»)
        press1 = (boton_presionado == 1 and hover1)
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
    p1_soplado = False
    p2_soplado = False
    teclas_sopladas = []
    lineas_viento = []

    p1_sobre_p2 = False
    p2_sobre_p1 = False

    # Renderizar el fotograma inicial del escenario con los personajes en sus posiciones iniciales
    mundo_inicio = pygame.Surface((ancho_mundo_nivel, ALTO))
    mundo_inicio.fill((255, 240, 195))
    pygame.draw.rect(mundo_inicio, (225, 110, 80), suelo)

    for plat in plataformas:
        if numero_nivel == 1:
            pygame.draw.rect(mundo_inicio, (110, 110, 115), plat, border_top_left_radius=4, border_top_right_radius=4)
            pygame.draw.rect(mundo_inicio, (75, 75, 80), plat, width=2, border_top_left_radius=4, border_top_right_radius=4)
        else:
            pygame.draw.rect(mundo_inicio, (110, 110, 115), plat, border_radius=4)
            pygame.draw.rect(mundo_inicio, (75, 75, 80), plat, width=2, border_radius=4)

    if usar_agua:
        dibujar_agua(mundo_inicio)
    if usar_soga:
        pygame.draw.line(mundo_inicio, COLOR_SOGA, jugador1["hitbox"].center, jugador2["hitbox"].center, 4)
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
                    reiniciar_juego(jugador1, jugador2, caja, llave, puerta)
                    p1_completado, p2_completado = False, False
                    mostrar_tutorial = (numero_nivel == 1)
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
                    reiniciar_juego(jugador1, jugador2, caja, llave, puerta)
                    p1_completado, p2_completado = False, False
                    mostrar_tutorial = (numero_nivel == 1)
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

        # Detección de interacción especial en Mundo 1: soplar indicadores del personaje quieto al saltar sobre él
        if numero_nivel == 1:
            ancho_c = 3 * TAM_BTN_TUT + 2 * GAP_BTN_TUT
            h_c1 = badge_p1.get_height() + 4 + (2 * TAM_BTN_TUT + GAP_BTN_TUT)
            h_c2 = badge_p2.get_height() + 4 + (2 * TAM_BTN_TUT + GAP_BTN_TUT)

            # Caso 1: Jugador 1 está quieto, Jugador 2 salta y atraviesa la zona de sus indicadores
            if not p1_movio and not p1_soplado and alpha_tut_p1 > 0 and not jugador1["muerto"] and not p1_completado:
                if not jugador2["muerto"] and not p2_completado and not p2_sobre_p1:
                    if not jugador2["en_suelo"] or abs(jugador2["vel_y"]) > 1.0:
                        rect_c1 = pygame.Rect(jugador1["hitbox"].centerx - ancho_c // 2, (jugador1["hitbox"].top - 8) - h_c1, ancho_c, h_c1)
                        if jugador2["hitbox"].colliderect(rect_c1):
                            pasa_sobre = abs(jugador2["vel_x"]) > 0.3 or (jugador2["hitbox"].right > jugador1["hitbox"].left + 5 and jugador2["hitbox"].left < jugador1["hitbox"].right - 5)
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
                            pasa_sobre = abs(jugador1["vel_x"]) > 0.3 or (jugador1["hitbox"].right > jugador2["hitbox"].left + 5 and jugador1["hitbox"].left < jugador2["hitbox"].right - 5)
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
        pygame.draw.rect(mundo, (225, 110, 80), suelo)

        for plat in plataformas:
            if numero_nivel == 1:
                pygame.draw.rect(mundo, (110, 110, 115), plat, border_top_left_radius=4, border_top_right_radius=4)
                pygame.draw.rect(mundo, (75, 75, 80), plat, width=2, border_top_left_radius=4, border_top_right_radius=4)
            else:
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

        # Efecto de ráfaga y animación de teclas sopladas
        if numero_nivel == 1:
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