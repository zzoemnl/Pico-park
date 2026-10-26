import os
import math
import pygame

from fuentes import (
    obtener_fuente_titulo,
    obtener_fuente_boton,
    TAMANO_TITULO,
    TAMANO_TITULO_MODAL,
    TAMANO_CARD,
)
from configuracion import t

# Paletas de colores del menú
COL_CIELO = (244, 238, 226)
COL_PANEL = (253, 246, 233)
COL_BORDE_PANEL = (195, 168, 138)
COL_DIVISOR = (235, 215, 195)
COL_TIERRA = (188, 140, 102)
COL_PASTO = (130, 190, 100)

COLORES_TABS = {
    1: {"fondo": (246, 215, 153), "borde": (180, 140, 90), "texto": (50, 40, 30)},
    2: {"fondo": (203, 195, 227), "borde": (140, 120, 180), "texto": (45, 35, 45)},
    3: {"fondo": (185, 222, 253), "borde": (100, 150, 200), "texto": (30, 45, 55)},
}


def obtener_mecanicas_nivel(mundo, nivel):
    """
    Retorna las mecánicas asignadas a cada nivel según los requerimientos:
    - Mundo 1: niveles con cajas y otros niveles sin cajas.
    - Mundo 2: soga que une a los personajes.
    - Mundo 3: niveles acuáticos.
    """
    if mundo == 1:
        if nivel == 1:
            return []
        elif nivel == 2:
            return []
        elif nivel == 3:
            return ["caja"]
        elif nivel == 4:
            return ["caja"]
        elif nivel == 5:
            return []
    elif mundo == 2:
        return ["soga", "pinchos"]
    elif mundo == 3:
        return ["agua"]
    return []


def dibujar_estrella(superficie, centro, r_exterior=14, r_interior=6, col_relleno=(255, 222, 90), col_borde=(185, 145, 75)):
    """Dibuja una estrella decorativa de 5 puntas estilo pixel art."""
    puntos = []
    cx, cy = centro
    for i in range(10):
        r = r_exterior if i % 2 == 0 else r_interior
        ang = i * (math.pi / 5) - math.pi / 2
        puntos.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    pygame.draw.polygon(superficie, col_relleno, puntos)
    pygame.draw.polygon(superficie, col_borde, puntos, 2)


def dibujar_mascota_gato(surf, x, y, size=34, color=(246, 215, 153)):
    """Dibuja la simpática cabeza de gato estilo Pico Park sobre la pestaña activa."""
    cat = pygame.Surface((size, size), pygame.SRCALPHA)
    ear_h = size // 4
    # Orejas
    pygame.draw.polygon(cat, color, [(3, ear_h + 2), (size // 4, 1), (size // 2 - 2, ear_h + 2)])
    pygame.draw.polygon(cat, (60, 45, 30), [(3, ear_h + 2), (size // 4, 1), (size // 2 - 2, ear_h + 2)], 2)
    pygame.draw.polygon(cat, color, [(size // 2 + 2, ear_h + 2), (3 * size // 4, 1), (size - 3, ear_h + 2)])
    pygame.draw.polygon(cat, (60, 45, 30), [(size // 2 + 2, ear_h + 2), (3 * size // 4, 1), (size - 3, ear_h + 2)], 2)
    # Cabeza
    body_r = pygame.Rect(2, ear_h, size - 4, size - ear_h - 2)
    pygame.draw.rect(cat, color, body_r, border_radius=5)
    pygame.draw.rect(cat, (60, 45, 30), body_r, 2, border_radius=5)
    # Ojos
    eye_s = max(3, size // 8)
    pygame.draw.rect(cat, (30, 20, 15), (size // 4, ear_h + size // 4 + 1, eye_s, eye_s))
    pygame.draw.rect(cat, (30, 20, 15), (3 * size // 4 - eye_s, ear_h + size // 4 + 1, eye_s, eye_s))
    # Hocico
    pygame.draw.rect(cat, (60, 45, 30), (size // 2 - 1, ear_h + size // 2 + 2, 2, 2))
    surf.blit(cat, (x, y))




def obtener_thumbnails():
    """Retorna las 15 miniaturas oficiales de los niveles generadas en miniaturas.py."""
    return obtener_miniaturas()


_CACHE_THUMBS_SCALED = {}


def _obtener_thumb_escalada(mundo, nivel, thumb_orig, w_target=196, h_target=125):
    """Retorna la miniatura escalada y cacheada para las tarjetas de nivel ampliadas."""
    clave = (mundo, nivel, w_target, h_target)
    if clave in _CACHE_THUMBS_SCALED:
        return _CACHE_THUMBS_SCALED[clave]
    try:
        surf = pygame.transform.smoothscale(thumb_orig, (w_target, h_target))
    except Exception:
        surf = pygame.transform.scale(thumb_orig, (w_target, h_target))
    _CACHE_THUMBS_SCALED[clave] = surf
    return surf


def obtener_geometria_menu(ancho_pantalla, alto_pantalla):
    """
    Calcula dinámicamente los rectángulos interactivos del menú
    adaptados a la resolución actual del juego con botones grandes y cómodos.
    """
    w_panel = min(1200, int(ancho_pantalla * 0.94))
    h_panel = min(425, int(alto_pantalla * 0.60))
    x_panel = (ancho_pantalla - w_panel) // 2
    y_panel = 175

    # Pestañas
    w_tab = min(240, int((w_panel - 80) / 3))
    h_tab_activa = 58
    h_tab_inactiva = 48
    gap_tab = 12
    x_tabs_start = x_panel + 40

    rects_tabs = {}
    for m in (1, 2, 3):
        x_t = x_tabs_start + (m - 1) * (w_tab + gap_tab)
        rects_tabs[m] = {
            "rect_click": pygame.Rect(x_t, y_panel - h_tab_activa, w_tab, h_tab_activa + 5),
            "x": x_t,
            "y_base": y_panel,
            "w": w_tab,
            "h_activa": h_tab_activa,
            "h_inactiva": h_tab_inactiva,
        }

    # Tarjetas de nivel (5 columnas en una sola fila con proporciones amplias)
    pad_x = 20
    pad_y = 18
    gap_cards = 15
    w_card = (w_panel - 2 * pad_x - 4 * gap_cards) // 5  # 220 px a 1200px de panel
    h_card = h_panel - 2 * pad_y                         # 389 px

    rects_cards = []
    for i in range(5):
        x_c = x_panel + pad_x + i * (w_card + gap_cards)
        y_c = y_panel + pad_y
        rects_cards.append(pygame.Rect(x_c, y_c, w_card, h_card))

    rect_panel = pygame.Rect(x_panel, y_panel, w_panel, h_panel)
    return rect_panel, rects_tabs, rects_cards


def dibujar_menu_niveles(pantalla, mundo_actual, niveles_desbloqueados, pos_mouse, fuentes=None):
    """
    Dibuja la pantalla completa de selección de niveles con estética pixel art Pico Park:
    - Fondo de paisaje pastel con nubes y cactus.
    - Pestañas superiores estilizadas para cada mundo con mascota de gato.
    - Panel contenedor con 5 botones/tarjetas grandes, miniaturas ampliadas, nombres, estrellas y botón de acción.
    """
    ancho, alto = pantalla.get_size()
    rect_panel, tabs_info, rects_cards = obtener_geometria_menu(ancho, alto)
    thumbs = obtener_thumbnails()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO, tamano_fallback=55)
    fuente_tab = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=34)
    fuente_card = obtener_fuente_boton(TAMANO_CARD, tamano_fallback=28)
    fuente_btn_card = obtener_fuente_boton(TAMANO_CARD, tamano_fallback=28)

    # 1. FONDO Y SUELO ORIGINALES DEL JUEGO (idénticos al escenario de los niveles)
    pantalla.fill((255, 240, 195))
    pygame.draw.rect(pantalla, (225, 110, 80), pygame.Rect(0, alto - 80, ancho, 80))

    # Título principal
    if fuente_titulo:
        txt_tit = fuente_titulo.render(t("seleccion_nivel"), True, (60, 45, 35))
        pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, 65)))

    # 2. PESTAÑAS (MUNDO 1, MUNDO 2, MUNDO 3)
    mundos_orden = [m for m in (1, 2, 3) if m != mundo_actual] + [mundo_actual]

    for m in mundos_orden:
        t_data = tabs_info[m]
        es_activa = (m == mundo_actual)
        info_col = COLORES_TABS[m]

        h_t = t_data["h_activa"] if es_activa else t_data["h_inactiva"]
        y_t = t_data["y_base"] - h_t + (3 if es_activa else 0)
        w_t = t_data["w"]
        x_t = t_data["x"]

        # Rectángulo de pestaña con borde superior redondeado
        r_dibujo = pygame.Rect(x_t, y_t, w_t, h_t + 10)
        pygame.draw.rect(pantalla, info_col["fondo"], r_dibujo, border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.rect(pantalla, info_col["borde"], r_dibujo, 3, border_top_left_radius=16, border_top_right_radius=16)

        # Si el mouse está sobre la pestaña inactiva, iluminar levemente
        if not es_activa and t_data["rect_click"].collidepoint(pos_mouse):
            glow = pygame.Surface((w_t, h_t), pygame.SRCALPHA)
            glow.fill((255, 255, 255, 50))
            pantalla.blit(glow, (x_t, y_t))

        # Texto de la pestaña
        if fuente_tab:
            color_txt = info_col["texto"] if es_activa else (110, 100, 95)
            txt_tab = fuente_tab.render(f"{t('mundo')} {m}", True, color_txt)
            rect_txt_tab = txt_tab.get_rect(center=(x_t + w_t // 2, y_t + h_t // 2 - 2))
            pantalla.blit(txt_tab, rect_txt_tab)

        # Mascota de gatito Pico Park en la pestaña activa
        if es_activa:
            dibujar_mascota_gato(pantalla, x_t + 16, y_t - 28, size=34, color=info_col["fondo"])

    # 3. PANEL CONTENEDOR PRINCIPAL
    pygame.draw.rect(pantalla, COL_PANEL, rect_panel, border_radius=18)
    pygame.draw.rect(pantalla, COL_BORDE_PANEL, rect_panel, 3, border_radius=18)

    # 4. TARJETAS DE NIVEL (5 BOTONES EN FILA)
    for idx, r_card in enumerate(rects_cards):
        nivel_num = idx + 1
        desbloqueado = niveles_desbloqueados[mundo_actual][idx]
        mouse_encima = r_card.collidepoint(pos_mouse)

        # Fondo individual de la tarjeta botón
        if desbloqueado:
            col_fondo_card = (255, 255, 255) if mouse_encima else (255, 252, 246)
            col_borde_card = (235, 165, 60) if mouse_encima else (210, 185, 155)
            ancho_borde = 3 if mouse_encima else 2
        else:
            col_fondo_card = (248, 244, 236) if mouse_encima else (244, 237, 226)
            col_borde_card = (195, 180, 165)
            ancho_borde = 2

        pygame.draw.rect(pantalla, col_fondo_card, r_card, border_radius=14)
        pygame.draw.rect(pantalla, col_borde_card, r_card, ancho_borde, border_radius=14)

        # Sombra sutil en la base de la tarjeta para efecto botón
        if desbloqueado and not mouse_encima:
            pygame.draw.rect(
                pantalla,
                (230, 210, 185),
                (r_card.left + 6, r_card.bottom - 4, r_card.width - 12, 4),
                border_bottom_left_radius=10,
                border_bottom_right_radius=10,
            )

        # Miniatura ampliada del escenario (196x125 para encajar perfectamente con 12px de margen)
        thumb_orig = thumbs[mundo_actual][nivel_num]
        w_th, h_th = 196, 125
        thumb_img = _obtener_thumb_escalada(mundo_actual, nivel_num, thumb_orig, w_th, h_th)
        x_th = r_card.centerx - w_th // 2
        y_th = r_card.top + 16
        r_th = pygame.Rect(x_th, y_th, w_th, h_th)

        # Elevación al hacer hover si el nivel está desbloqueado
        y_draw_th = y_th - (3 if mouse_encima and desbloqueado else 0)
        pantalla.blit(thumb_img, (x_th, y_draw_th))

        # Borde decorativo de la miniatura
        pygame.draw.rect(pantalla, (165, 140, 115), (x_th, y_draw_th, w_th, h_th), 2, border_radius=6)

        # Overlay de bloqueo si está bloqueado
        if not desbloqueado:
            lock_mask = pygame.Surface((w_th, h_th), pygame.SRCALPHA)
            lock_mask.fill((30, 20, 20, 160))
            pantalla.blit(lock_mask, (x_th, y_draw_th))
            cx, cy = x_th + w_th // 2, y_draw_th + h_th // 2
            pygame.draw.rect(pantalla, (230, 210, 170), (cx - 12, cy - 4, 24, 18), border_radius=4)
            pygame.draw.arc(pantalla, (230, 210, 170), (cx - 8, cy - 16, 16, 18), 0, 3.14, 3)

        # Texto "NIVEL X"
        if fuente_card:
            col_texto_n = (55, 45, 35) if desbloqueado else (150, 140, 130)
            txt_n = fuente_card.render(f"{t('nivel')} {nivel_num}", True, col_texto_n)
            rect_txt_n = txt_n.get_rect(center=(r_card.centerx, r_th.bottom + 26))
            pantalla.blit(txt_n, rect_txt_n)

        # Estrella decorativa debajo
        y_star = r_th.bottom + 66
        if desbloqueado:
            dibujar_estrella(pantalla, (r_card.centerx, y_star), r_exterior=16, r_interior=7)
        else:
            dibujar_estrella(
                pantalla,
                (r_card.centerx, y_star),
                r_exterior=16,
                r_interior=7,
                col_relleno=(235, 230, 222),
                col_borde=(180, 170, 160),
            )

        # Botón / Badge de estado inferior ("JUGAR" o "BLOQUEADO")
        r_btn_status = pygame.Rect(r_card.centerx - 70, r_card.bottom - 44, 140, 32)
        if desbloqueado:
            col_pill = (96, 212, 130) if mouse_encima else (82, 194, 114)
            borde_pill = (45, 130, 70)
            txt_pill_col = (255, 255, 255)
            texto_pill = f"{t('jugar')} ▶"
        else:
            col_pill = (220, 212, 204)
            borde_pill = (180, 170, 160)
            txt_pill_col = (140, 130, 120)
            texto_pill = t("bloqueado")

        pygame.draw.rect(pantalla, col_pill, r_btn_status, border_radius=8)
        pygame.draw.rect(pantalla, borde_pill, r_btn_status, 2, border_radius=8)
        if fuente_btn_card:
            t_pill = fuente_btn_card.render(texto_pill, True, txt_pill_col)
            pantalla.blit(t_pill, t_pill.get_rect(center=r_btn_status.center))


# ==============================================================================
# GENERACIÓN Y GESTIÓN DE MINIATURAS (PREVIEWS DE NIVELES)
# ==============================================================================

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_SPRITES = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites")
RUTA_PERSONAJES = os.path.join(RUTA_SPRITES, "Personajes")
RUTA_OBJETOS = os.path.join(RUTA_SPRITES, "Objetos")
RUTA_MINIATURAS = os.path.join(RUTA_SPRITES, "Miniaturas")

# Constantes de colores originales del juego
COL_FONDO_M1 = (255, 240, 195)
COL_SUELO_M1 = (225, 110, 80)
COL_PLATAFORMA_M1 = (225, 110, 80)
COL_BORDE_PLAT = (185, 80, 55)
COLOR_SOGA = (200, 160, 100)

ANCHO_MINI = 176
ALTO_MINI = 112

_CACHE_MINIATURAS = None


def _cargar_recurso_original(ruta, tamano):
    """Carga una imagen y la escala al tamaño requerido manteniendo transparencia."""
    if os.path.isfile(ruta):
        try:
            img = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(img, tamano)
        except Exception:
            pass
    # Fallback si el display aún no se inicializó
    if os.path.isfile(ruta):
        try:
            img = pygame.image.load(ruta)
            return pygame.transform.scale(img, tamano)
        except Exception:
            pass
    return None


def _cargar_personaje(color_nombre="Celeste", tamano=(16, 20), tinte_agua=False):
    """Carga el sprite en reposo del personaje original."""
    ruta = os.path.join(RUTA_PERSONAJES, color_nombre, "quieto.png")
    sp = _cargar_recurso_original(ruta, tamano)
    if sp is None:
        sp = pygame.Surface(tamano, pygame.SRCALPHA)
        color = (124, 231, 255) if color_nombre == "Celeste" else (161, 123, 255)
        pygame.draw.rect(sp, color, (0, 0, *tamano), border_radius=4)

    if tinte_agua:
        sp_agua = sp.copy()
        filtro = pygame.Surface(tamano, pygame.SRCALPHA)
        filtro.fill((0, 100, 180, 80))
        sp_agua.blit(filtro, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return sp_agua
    return sp


def _cargar_caja(tamano=(18, 18)):
    """Carga la caja original del juego."""
    ruta = os.path.join(RUTA_OBJETOS, "caja.png")
    sp = _cargar_recurso_original(ruta, tamano)
    if sp is None:
        sp = pygame.Surface(tamano, pygame.SRCALPHA)
        pygame.draw.rect(sp, (185, 130, 75), (0, 0, *tamano))
        pygame.draw.rect(sp, (90, 55, 25), (0, 0, *tamano), 2)
        pygame.draw.line(sp, (90, 55, 25), (0, 0), (tamano[0], tamano[1]), 2)
        pygame.draw.line(sp, (90, 55, 25), (tamano[0], 0), (0, tamano[1]), 2)
    return sp


def _cargar_llave(tamano=(10, 18)):
    """Carga la llave original del juego."""
    ruta = os.path.join(RUTA_OBJETOS, "llave.png")
    sp = _cargar_recurso_original(ruta, tamano)
    if sp is None:
        sp = pygame.Surface(tamano, pygame.SRCALPHA)
        pygame.draw.circle(sp, (255, 215, 0), (tamano[0] // 2, 5), 4)
        pygame.draw.rect(sp, (255, 215, 0), (tamano[0] // 2 - 1, 5, 2, tamano[1] - 5))
        pygame.draw.rect(sp, (255, 215, 0), (tamano[0] // 2 + 1, tamano[1] - 6, 3, 2))
    return sp


def _crear_puerta_original(tamano=(16, 26)):
    """Representación fiel en pixel art de la puerta de madera con marco y pomo dorado."""
    p = pygame.Surface(tamano, pygame.SRCALPHA)
    w, h = tamano
    # Marco exterior
    pygame.draw.rect(p, (90, 45, 15), (0, 0, w, h), border_radius=2)
    # Hoja de madera
    pygame.draw.rect(p, (139, 69, 19), (2, 2, w - 4, h - 2), border_radius=2)
    # Tablones decorativos sutiles
    pygame.draw.line(p, (115, 55, 15), (w // 2, 3), (w // 2, h - 2), 1)
    # Pomo dorado
    pygame.draw.circle(p, (255, 215, 0), (w - 4, h // 2 + 2), 2)
    return p


def _dibujar_pinchos(surf, x_inicio, x_fin, y_base, hacia_arriba=True, w_p=10, h_p=10):
    """Dibuja una hilera de pinchos triangulares clásicos."""
    col_cuerpo = (235, 235, 240)
    col_borde = (110, 110, 115)
    x = x_inicio
    while x + w_p <= x_fin:
        if hacia_arriba:
            puntos = [(x, y_base), (x + w_p // 2, y_base - h_p), (x + w_p, y_base)]
        else:
            puntos = [(x, y_base), (x + w_p // 2, y_base + h_p), (x + w_p, y_base)]
        pygame.draw.polygon(surf, col_cuerpo, puntos)
        pygame.draw.polygon(surf, col_borde, puntos, 1)
        x += w_p


def _dibujar_soga(surf, p1, p2):
    """Traza la soga entre dos coordenadas de personaje."""
    pygame.draw.line(surf, COLOR_SOGA, p1, p2, 2)


# ==============================================================================
# MUNDO 1: BÁSICO (Fondo cálido original, sin soga)
# ==============================================================================

def _crear_m1_n1():
    """1-1: Tutorial (Suelo continuo con torres/columnas, 2 personajes, llave y puerta)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 88

    # Torres del tutorial integradas al suelo
    torre1 = pygame.Rect(70, y_suelo - 7, 14, 10)
    torre2 = pygame.Rect(92, y_suelo - 14, 20, 17)
    for t in (torre1, torre2):
        pygame.draw.rect(s, COL_PLATAFORMA_M1, t, border_top_left_radius=2, border_top_right_radius=2)
        pygame.draw.rect(s, COL_BORDE_PLAT, t, width=1, border_top_left_radius=2, border_top_right_radius=2)

    # Suelo continuo
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (20, y_suelo - 20))
    s.blit(pj2, (42, y_suelo - 20))
    # Llave sobre la torre del tutorial
    s.blit(llave, (97, y_suelo - 14 - 18))
    s.blit(puerta, (142, y_suelo - 26))
    return s


def _crear_m1_n2():
    """1-2: La torre humana (Plataforma flotante central, torre humana, llave arriba y puerta al suelo)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 88
    # Suelo continuo inferior
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))

    # Plataforma flotante central (separada del suelo, espacio libre por debajo)
    rect_plat = pygame.Rect(70, 52, 46, 8)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, rect_plat, border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, rect_plat, width=1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Torre humana antes de la plataforma: Celeste abajo, Violeta arriba
    s.blit(pj1, (36, y_suelo - 20))
    s.blit(pj2, (36, y_suelo - 38))

    # Llave sobre la plataforma flotante
    s.blit(llave, (88, 52 - 18))

    # Puerta de salida en el suelo al final del recorrido
    s.blit(puerta, (142, y_suelo - 26))
    return s


def _crear_m1_n3():
    """1-3: La caja y el botón (Personajes a la izquierda, caja sobre botón, pared levantada, llave y puerta a la derecha)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 88
    # Suelo continuo
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))

    # Personajes en la zona izquierda
    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    s.blit(pj1, (20, y_suelo - 20))
    s.blit(pj2, (38, y_suelo - 20))

    # Botón en el suelo presionado
    pygame.draw.rect(s, (80, 200, 100), (66, y_suelo - 2, 20, 3), border_radius=1)

    # Caja sobre el botón
    caja = _cargar_caja()
    s.blit(caja, (67, y_suelo - 20))

    # Pared vertical levantada
    rect_pared = pygame.Rect(102, 12, 7, y_suelo - 46)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, rect_pared, border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, rect_pared, 1, border_radius=2)

    # Llave al otro lado de la pared
    llave = _cargar_llave()
    s.blit(llave, (126, y_suelo - 20))

    # Puerta de salida en el extremo derecho
    puerta = _crear_puerta_original()
    s.blit(puerta, (148, y_suelo - 26))
    return s


def _crear_m1_n4():
    """1-4: El láser y la caja (Puerta a la izquierda, caja bloqueando láser en el borde, plataformas sobre pozo, llave a la derecha)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_plat = 68

    # Plataforma izquierda con puerta
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_plat, 48, ALTO_MINI - y_plat))
    pygame.draw.line(s, (245, 140, 110), (0, y_plat), (48, y_plat), 1)
    pygame.draw.line(s, (180, 80, 50), (48, y_plat), (48, ALTO_MINI), 1)

    # Puerta de salida al inicio en la plataforma izquierda
    puerta = _crear_puerta_original((15, 25))
    s.blit(puerta, (6, y_plat - 25))

    # Pozo de profundidad moderada con pinchos en el fondo
    h_pozo = 14
    y_fondo = y_plat + h_pozo
    pygame.draw.rect(s, (230, 215, 185), (48, y_plat, 62, h_pozo))
    pygame.draw.rect(s, COL_SUELO_M1, (48, y_fondo, 62, ALTO_MINI - y_fondo))
    pygame.draw.line(s, (180, 80, 50), (48, y_fondo), (110, y_fondo), 1)

    # Pinchos horizontales en el fondo del pozo
    _dibujar_pinchos(s, 64, 108, y_fondo, hacia_arriba=True, w_p=6, h_p=5)

    # Plataforma de paso intermedia en el pozo (bajadas a la altura del láser)
    rect_paso = pygame.Rect(72, y_plat + 5, 14, 4)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, rect_paso, border_radius=1)
    pygame.draw.rect(s, COL_BORDE_PLAT, rect_paso, 1, border_radius=1)

    # Plataforma derecha
    pygame.draw.rect(s, COL_SUELO_M1, (110, y_plat, ANCHO_MINI - 110, ALTO_MINI - y_plat))
    pygame.draw.line(s, (245, 140, 110), (110, y_plat), (ANCHO_MINI, y_plat), 1)
    pygame.draw.line(s, (180, 80, 50), (110, y_plat), (110, ALTO_MINI), 1)

    # Plataforma elevada para la llave en la zona derecha
    rect_llave_plat = pygame.Rect(140, 48, 22, 5)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, rect_llave_plat, border_radius=1)
    pygame.draw.rect(s, COL_BORDE_PLAT, rect_llave_plat, 1, border_radius=1)
    llave = _cargar_llave((9, 16))
    s.blit(llave, (146, 48 - 16))

    # Emisor de láser en la pared interna izquierda
    pygame.draw.rect(s, (65, 60, 70), (44, y_plat + 4, 4, 6), border_radius=1)
    pygame.draw.circle(s, (255, 60, 60), (48, y_plat + 7), 2)

    # Caja en el pozo bloqueando el láser
    caja = _cargar_caja((14, 14))
    s.blit(caja, (50, y_fondo - 14))

    # Rayo láser interceptado por la caja
    pygame.draw.line(s, (255, 45, 45), (48, y_plat + 7), (50, y_plat + 7), 2)
    pygame.draw.circle(s, (255, 220, 80), (50, y_plat + 7), 2)

    # Personajes
    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    s.blit(pj1, (20, y_plat - 20))
    s.blit(pj2, (50, y_fondo - 14 - 20))

    # Puerta de salida en el extremo derecho
    puerta = _crear_puerta_original()
    s.blit(puerta, (156, y_plat - 26))

    return s


def _crear_m1_n5():
    """1-5: Las cuatro paredes de colores (Recorrido superior: paredes roja, azul, roja, azul. Recorrido inferior: botones correspondientes)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_techo = 10
    y_div = 52
    y_suelo = 94

    # Techo superior
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (0, 0, ANCHO_MINI, y_techo))
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, 0, ANCHO_MINI, y_techo), 1)

    # Plataforma divisoria central entre ambos recorridos (con caída al final)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (0, y_div, 138, 6))
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, y_div, 138, 6), 1)

    # Barrera en L invertida sobre la puerta y bajando al suelo
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (144, y_div, 30, 6))
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (170, y_div, 4, y_suelo - y_div))
    pygame.draw.rect(s, COL_BORDE_PLAT, (144, y_div, 30, 6), 1)
    pygame.draw.rect(s, COL_BORDE_PLAT, (170, y_div, 4, y_suelo - y_div), 1)

    # Suelo del recorrido inferior
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))
    pygame.draw.line(s, (245, 140, 110), (0, y_suelo), (ANCHO_MINI, y_suelo), 1)
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo), 1)

    # RECORRIDO SUPERIOR: 4 paredes verticales en orden ROJO, AZUL, ROJO, AZUL
    colores_pared = [
        (225, 45, 45),   # 1. Roja
        (45, 110, 225),  # 2. Azul
        (225, 45, 45),   # 3. Roja
        (45, 110, 225),  # 4. Azul
    ]
    xs_pared = [46, 72, 98, 122]
    for col, xp in zip(colores_pared, xs_pared):
        r_p = pygame.Rect(xp, y_techo, 6, y_div - y_techo)
        pygame.draw.rect(s, col, r_p)
        pygame.draw.rect(s, (30, 30, 30), r_p, 1)

    # RECORRIDO INFERIOR: Exactamente 2 botones en el suelo (uno Rojo y uno Azul)
    colores_boton = [
        (225, 45, 45),   # 1. Rojo
        (45, 110, 225),  # 2. Azul
    ]
    xs_boton = [54, 88]
    for i, (col, xb) in enumerate(zip(colores_boton, xs_boton)):
        pygame.draw.rect(s, (70, 60, 55), (xb - 2, y_suelo - 1, 16, 2))
        if i == 0:
            # Botón Rojo presionado por Violeta
            pygame.draw.rect(s, col, (xb, y_suelo - 2, 12, 2), border_radius=1)
        else:
            # Botón Azul sin presionar
            pygame.draw.rect(s, col, (xb, y_suelo - 4, 12, 4), border_radius=1)

    # Compuerta mecánica en la abertura de descenso
    pygame.draw.rect(s, (180, 85, 60), (138, y_div, 6, 6))
    pygame.draw.rect(s, (120, 45, 30), (138, y_div, 6, 6), 1)

    # Botón inferior para la compuerta junto al hueco
    pygame.draw.rect(s, (70, 60, 55), (130, y_suelo - 1, 14, 2))
    pygame.draw.rect(s, (210, 85, 45), (132, y_suelo - 4, 10, 4), border_radius=1)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Celeste arriba en el recorrido superior frente a las paredes
    s.blit(pj1, (20, y_div - 20))
    # Violeta abajo en el recorrido inferior colaborando al presionar el botón rojo
    s.blit(pj2, (52, y_suelo - 20))

    # Llave al final del recorrido superior y puerta de salida al final en el suelo bajo la L
    s.blit(llave, (130, y_div - 18))
    s.blit(puerta, (148, y_suelo - 26))

    return s


def _crear_m2_n1():
    """2-1: El arrastre básico (Introducción a la soga: personajes unidos, escalones, plataformas de salto, abismo con pinchos extendidos hasta el final, llave y puerta)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 94

    # Suelo seguro inicial y abismo continuo con pinchos hasta el final
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, 76, ALTO_MINI - y_suelo))
    pygame.draw.line(s, (245, 140, 110), (0, y_suelo), (76, y_suelo), 1)
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, y_suelo, 76, ALTO_MINI - y_suelo), 1)

    pygame.draw.rect(s, (45, 35, 35), (76, 96, ANCHO_MINI - 76, ALTO_MINI - 96))
    _dibujar_pinchos(s, 76, ANCHO_MINI, 96, hacia_arriba=True)

    # 1. Escalones para subir juntos
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (36, 84, 18, 10), border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, (36, 84, 18, 10), 1, border_radius=2)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (54, 74, 22, 20), border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, (54, 74, 22, 20), 1, border_radius=2)

    # 2. Plataformas de salto coordinado
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (82, 62, 22, 5), border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, (82, 62, 22, 5), 1, border_radius=2)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (110, 52, 22, 5), border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, (110, 52, 22, 5), 1, border_radius=2)

    # 3. Plataforma de destino con llave y puerta
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (138, 58, 38, 5), border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, (138, 58, 38, 5), 1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Personajes en las plataformas de salto unidos por la soga
    pos_v = (84, 62 - 20)
    pos_c = (112, 52 - 20)
    _dibujar_soga(s, (pos_v[0] + 12, pos_v[1] + 14), (pos_c[0] + 6, pos_c[1] + 14))

    s.blit(pj2, pos_v)
    s.blit(pj1, pos_c)

    # Llave en la plataforma de destino
    s.blit(llave, (144, 58 - 18))

    # Puerta de salida al final
    s.blit(puerta, (156, 58 - 26))

    return s


def _crear_m2_n2():
    """2-2: La plataforma móvil (Plataforma sobre abismo con pinchos, bloque obstáculo, llave y puerta)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Bordes de suelo
    pygame.draw.rect(s, COL_SUELO_M1, (0, 78, 25, ALTO_MINI - 78))
    pygame.draw.rect(s, COL_SUELO_M1, (151, 78, 25, ALTO_MINI - 78))

    # Abismo con pinchos en el fondo
    pygame.draw.rect(s, (45, 35, 35), (25, 96, 126, ALTO_MINI - 96))
    _dibujar_pinchos(s, 25, 151, 96, hacia_arriba=True)

    # Plataforma móvil suspendida sobre el abismo
    plat_movil = pygame.Rect(42, 66, 68, 8)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_movil, border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_movil, 1, border_radius=2)

    # Bloque en medio del trayecto de la plataforma
    bloque = pygame.Rect(72, 46, 14, 20)
    pygame.draw.rect(s, (95, 75, 65), bloque)
    pygame.draw.rect(s, (45, 30, 20), bloque, 1)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    pos1 = (46, 66 - 20)
    pos2 = (90, 66 - 20)
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 10), (pos2[0] + 8, pos2[1] + 10))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)
    s.blit(llave, (126, 52))
    s.blit(puerta, (154, 78 - 26))
    return s


def _crear_m2_n3():
    """2-3: El péndulo (Plataforma elevada sobre abismo de pinchos, personaje balanceándose con la soga como péndulo para agarrar la llave)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Plataforma de inicio izquierda (y=60)
    plat_ini = pygame.Rect(0, 60, 26, 52)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_ini)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_ini, 1)

    # Plataforma de llegada derecha (y=60)
    plat_lleg = pygame.Rect(144, 60, 32, 52)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_lleg)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_lleg, 1)

    # Abismo con pinchos mortales continuo
    pygame.draw.rect(s, (45, 35, 35), (26, 94, 118, 18))
    _dibujar_pinchos(s, 26, 144, 94, hacia_arriba=True, w_p=7, h_p=7)

    # Plataforma elevada central (el puente de balanceo)
    plat_el = pygame.Rect(32, 34, 108, 8)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_el, border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_el, 1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    pos1 = (62, 34 - 18)
    pos2 = (82, 56)

    # Personajes unidos por la soga: uno en la plataforma y el otro colgando como péndulo
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 12), (pos2[0] + 8, pos2[1] + 8))
    s.blit(pj1, pos1)
    s.blit(pj2, pos2)

    # Bloque peligroso rojo central con pinchos en el abismo
    bloque_rojo = pygame.Rect(86, 70, 10, 8)
    pygame.draw.rect(s, (220, 50, 50), bloque_rojo, border_radius=1)
    pygame.draw.rect(s, (140, 25, 25), bloque_rojo, 1, border_radius=1)
    _dibujar_pinchos(s, 86, 96, 70, hacia_arriba=True, w_p=4, h_p=3)

    # Llave en la parte inferior del recorrido debajo de la plataforma
    s.blit(llave, (98, 60))
    # Puerta en la plataforma segura de llegada
    s.blit(puerta, (148, 60 - 26))
    return s


def _crear_m2_n4():
    """2-4: Las plataformas que se derrumban (Abismo con pinchos, plataformas pequeñas que caen a los 1,5 segundos, llave central, puerta)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Plataforma de inicio izquierda (y=66)
    plat_ini = pygame.Rect(0, 66, 22, 46)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_ini)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_ini, 1)

    # Plataforma de llegada derecha (y=66)
    plat_lleg = pygame.Rect(150, 66, 26, 46)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_lleg)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_lleg, 1)

    # Abismo de pinchos en el fondo
    pygame.draw.rect(s, (45, 35, 35), (22, 94, 128, 18))
    _dibujar_pinchos(s, 22, 150, 94, hacia_arriba=True, w_p=7, h_p=7)

    # Serie de plataformas pequeñas agrietadas
    plats = [
        pygame.Rect(28, 66, 24, 7),
        pygame.Rect(58, 60, 24, 7),
        pygame.Rect(88, 56, 24, 7),
        pygame.Rect(118, 62, 24, 7),
    ]
    for idx, p in enumerate(plats):
        pygame.draw.rect(s, (185, 120, 85), p, border_radius=1)
        pygame.draw.rect(s, (140, 75, 45), p, 1, border_radius=1)
        # Fisuras de derrumbe
        pygame.draw.line(s, (65, 35, 25), (p.x + 6, p.y + 1), (p.x + 11, p.y + 6), 1)
        pygame.draw.line(s, (65, 35, 25), (p.x + 16, p.y + 1), (p.x + 13, p.y + 6), 1)
        # Partículas de desmoronamiento cayendo de la plataforma activa
        if idx == 1:
            pygame.draw.rect(s, (140, 75, 45), (p.x + 8, p.bottom + 2, 2, 2))
            pygame.draw.rect(s, (185, 120, 85), (p.x + 14, p.bottom + 4, 2, 2))

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    pos1 = (58, 60 - 20)
    pos2 = (88, 56 - 20)
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 10), (pos2[0] + 8, pos2[1] + 10))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)
    s.blit(llave, (96, 40))
    s.blit(puerta, (152, 66 - 26))
    return s


def _crear_m2_n5():
    """2-5: Las plataformas alternadas (Escalera ascendente continua de plataformas, soga, cables, llave y puerta en la cima)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Abismo inferior con pinchos mortales
    pygame.draw.rect(s, (45, 35, 35), (0, 104, ANCHO_MINI, ALTO_MINI - 104))
    _dibujar_pinchos(s, 0, ANCHO_MINI, 104, hacia_arriba=True, w_p=7, h_p=7)

    # Plataformas formando una escalera claramente ascendente de abajo-izquierda a arriba-derecha
    plats = [
        pygame.Rect(4, 96, 26, 6),    # Inicio abajo izquierda
        pygame.Rect(34, 82, 22, 6),   # Escalón 1
        pygame.Rect(62, 68, 22, 6),   # Escalón 2
        pygame.Rect(90, 54, 22, 6),   # Escalón 3
        pygame.Rect(118, 40, 24, 6),  # Escalón 4 (superior con llave)
        pygame.Rect(148, 28, 28, 6),  # Cima llegada (superior con puerta)
    ]
    for p in plats[1:5]:
        # Cables tensores desde el techo
        pygame.draw.line(s, (160, 145, 130), (p.left + 4, 0), (p.left + 4, p.top), 1)
        pygame.draw.line(s, (160, 145, 130), (p.right - 4, 0), (p.right - 4, p.top), 1)

    for p in plats:
        pygame.draw.rect(s, COL_PLATAFORMA_M1, p, border_radius=2)
        pygame.draw.rect(s, COL_BORDE_PLAT, p, 1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    pos1 = (36, 82 - 20)
    pos2 = (8, 96 - 20)
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 10), (pos2[0] + 8, pos2[1] + 10))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)
    s.blit(llave, (124, 40 - 18))
    s.blit(puerta, (150, 28 - 25))
    return s


# ==============================================================================
# MUNDO 3: SUBMARINO (Agua, rocas, corales, algas, tinte azul, sin soga)
# ==============================================================================

def _dibujar_alga(surf, x, y_base, alto=28, color=(40, 160, 80)):
    """Dibuja un tallo de alga marina ondeante pixel art."""
    puntos = [
        (x, y_base),
        (x + 3, y_base - alto // 3),
        (x - 3, y_base - 2 * alto // 3),
        (x + 1, y_base - alto)
    ]
    pygame.draw.lines(surf, color, False, puntos, 3)


def _dibujar_coral(surf, x, y_base, color=(235, 105, 130)):
    """Dibuja una ramificación de coral marino."""
    pygame.draw.line(surf, color, (x, y_base), (x, y_base - 14), 3)
    pygame.draw.line(surf, color, (x, y_base - 8), (x - 6, y_base - 16), 2)
    pygame.draw.line(surf, color, (x, y_base - 8), (x + 6, y_base - 16), 2)


def _crear_fondo_submarino():
    """Fondo base acuático con superficie y burbujas."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill((25, 115, 195))

    # Olas en la superficie superior
    for i in range(11):
        wx = i * 16
        pygame.draw.arc(s, (140, 220, 255), (wx, 0, 18, 10), 0, 3.14, 2)

    # Burbujas flotantes
    burbujas = [(25, 30, 2), (65, 45, 3), (115, 25, 2), (145, 55, 3), (85, 80, 2)]
    for bx, by, br in burbujas:
        pygame.draw.circle(s, (190, 240, 255), (bx, by), br, 1)

    return s


def _crear_m3_n1():
    """3-1: El jardín de algas (Zona abierta submarina, algas, rocas, corales, llave entre rocas, puerta)."""
    s = _crear_fondo_submarino()

    # Lecho marino rocoso
    y_lecho = 90
    pygame.draw.rect(s, (45, 75, 105), (0, y_lecho, ANCHO_MINI, ALTO_MINI - y_lecho))

    # Formaciones rocosas
    pygame.draw.ellipse(s, (65, 95, 125), (75, y_lecho - 14, 35, 24))
    pygame.draw.ellipse(s, (55, 85, 115), (95, y_lecho - 18, 28, 28))

    # Algas y corales
    _dibujar_alga(s, 15, y_lecho, alto=32)
    _dibujar_alga(s, 22, y_lecho, alto=40)
    _dibujar_alga(s, 65, y_lecho, alto=35)
    _dibujar_coral(s, 45, y_lecho, (240, 110, 130))
    _dibujar_coral(s, 128, y_lecho, (245, 160, 90))

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (30, 48))
    s.blit(pj2, (50, 38))
    # Llave entre rocas
    s.blit(llave, (88, y_lecho - 22))
    # Puerta al final
    s.blit(puerta, (146, y_lecho - 26))
    return s


def _crear_m3_n2():
    """3-2: El laberinto de coral (Paredes de roca marina, corales, caminos y callejones, llave escondida)."""
    s = _crear_fondo_submarino()

    col_roca = (55, 85, 115)
    col_borde_roca = (35, 60, 85)

    # Estructura del laberinto submarino (muros y callejones)
    paredes_laberinto = [
        pygame.Rect(0, 0, ANCHO_MINI, 8),                  # Techo
        pygame.Rect(0, 104, ANCHO_MINI, 8),                # Suelo
        pygame.Rect(40, 8, 12, 60),                       # Muro 1 bajando
        pygame.Rect(40, 68, 45, 10),                      # Conector 1
        pygame.Rect(85, 35, 12, 69),                      # Muro 2 subiendo
        pygame.Rect(125, 8, 12, 65),                      # Muro 3 bajando
        pygame.Rect(125, 73, 35, 10),                     # Callejón sin salida
    ]
    for p in paredes_laberinto:
        pygame.draw.rect(s, col_roca, p)
        pygame.draw.rect(s, col_borde_roca, p, 1)

    # Corales y algas decorando las esquinas del laberinto
    _dibujar_coral(s, 35, 68, (230, 95, 120))
    _dibujar_coral(s, 105, 104, (245, 150, 80))
    _dibujar_alga(s, 15, 104, alto=28)
    _dibujar_alga(s, 120, 104, alto=24)

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()

    s.blit(pj1, (16, 35))
    s.blit(pj2, (58, 40))
    # Llave escondida en la sección interior del laberinto
    s.blit(llave, (102, 22))
    return s


def _crear_m3_n3():
    """3-3: Las rocas peligrosas (Pasillos estrechos, rocas y pinchos en suelo y techo, llave en zona peligrosa)."""
    s = _crear_fondo_submarino()

    col_roca = (55, 80, 105)

    # Techo y suelo rocosos
    pygame.draw.rect(s, col_roca, (0, 0, ANCHO_MINI, 18))
    pygame.draw.rect(s, col_roca, (0, 94, ANCHO_MINI, 18))

    # Pinchos saliendo del techo hacia abajo
    _dibujar_pinchos(s, 35, 125, 18, hacia_arriba=False, w_p=10, h_p=12)
    # Pinchos saliendo del suelo hacia arriba
    _dibujar_pinchos(s, 55, 135, 94, hacia_arriba=True, w_p=10, h_p=12)

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Personajes maniobrando en el pasillo estrecho
    s.blit(pj1, (14, 46))
    s.blit(pj2, (34, 46))

    # Llave detrás de la zona peligrosa
    s.blit(llave, (98, 46))
    # Puerta al otro lado
    s.blit(puerta, (146, 94 - 26))
    return s


def _crear_m3_n4():
    """3-4: El laberinto oscuro (Zona oscura, círculos de luz de linternas alrededor de personajes)."""
    # Fondo de oscuridad abisal profunda
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill((12, 18, 30))

    # Paredes oscuras del laberinto
    paredes = [
        pygame.Rect(35, 0, 10, 50),
        pygame.Rect(75, 45, 10, 67),
        pygame.Rect(115, 0, 10, 60),
    ]
    for p in paredes:
        pygame.draw.rect(s, (25, 35, 50), p)

    # Capa de linternas con luz cálida/cian translúcida
    pos_pj1 = (52, 50)
    pos_pj2 = (95, 42)

    luz_surf = pygame.Surface((ANCHO_MINI, ALTO_MINI), pygame.SRCALPHA)
    # Haz de luz de Celeste
    pygame.draw.circle(luz_surf, (220, 245, 255, 110), (pos_pj1[0] + 8, pos_pj1[1] + 10), 32)
    pygame.draw.circle(luz_surf, (255, 255, 255, 170), (pos_pj1[0] + 8, pos_pj1[1] + 10), 18)
    # Haz de luz de Violeta
    pygame.draw.circle(luz_surf, (220, 245, 255, 110), (pos_pj2[0] + 8, pos_pj2[1] + 10), 30)
    pygame.draw.circle(luz_surf, (255, 255, 255, 170), (pos_pj2[0] + 8, pos_pj2[1] + 10), 16)
    s.blit(luz_surf, (0, 0))

    # Corales visibles sólo donde alumbra la luz
    _dibujar_coral(s, 68, 90, (190, 80, 100))
    _dibujar_alga(s, 48, 112, alto=24, color=(35, 110, 65))

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, pos_pj1)
    s.blit(pj2, pos_pj2)

    # Llave y puerta emergiendo en la penumbra
    s.blit(llave, (132, 28))
    s.blit(puerta, (148, 70))
    return s


def _crear_m3_n5():
    """3-5: El abismo submarino (Gran abismo, pasillos estrechos, pinchos, corrientes de agua con flechas)."""
    s = _crear_fondo_submarino()

    col_roca = (45, 75, 105)

    # Plataforma rocosa izquierda elevada
    pygame.draw.rect(s, col_roca, (0, 48, 45, ALTO_MINI - 48))
    # Gran abismo central profundo
    pygame.draw.rect(s, (20, 45, 70), (45, 96, 75, ALTO_MINI - 96))
    _dibujar_pinchos(s, 45, 120, 96, hacia_arriba=True, w_p=10, h_p=10)
    # Saliente superior derecho
    pygame.draw.rect(s, col_roca, (120, 40, 56, ALTO_MINI - 40))

    # Pinchos en el techo saliente
    _dibujar_pinchos(s, 50, 95, 0, hacia_arriba=False, w_p=10, h_p=10)

    # Corrientes de agua marinas representadas con líneas y flechas cian translúcidas
    for cy in [26, 68]:
        pygame.draw.line(s, (180, 245, 255), (55, cy), (105, cy), 2)
        # Flecha de corriente
        pygame.draw.polygon(s, (180, 245, 255), [(105, cy - 4), (112, cy), (105, cy + 4)])

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (16, 28))
    s.blit(pj2, (28, 28))

    # Llave en cavidad profunda del abismo
    s.blit(llave, (78, 74))
    # Puerta en la cima derecha
    s.blit(puerta, (146, 40 - 26))
    return s


# ==============================================================================
# DICCIONARIO Y GENERADOR PRINCIPAL
# ==============================================================================

CREADORES_MINIATURAS = {
    1: {
        1: _crear_m1_n1,
        2: _crear_m1_n2,
        3: _crear_m1_n3,
        4: _crear_m1_n4,
        5: _crear_m1_n5,
    },
    2: {
        1: _crear_m2_n1,
        2: _crear_m2_n2,
        3: _crear_m2_n3,
        4: _crear_m2_n4,
        5: _crear_m2_n5,
    },
    3: {
        1: _crear_m3_n1,
        2: _crear_m3_n2,
        3: _crear_m3_n3,
        4: _crear_m3_n4,
        5: _crear_m3_n5,
    },
}


def generar_todas_las_miniaturas(guardar_en_disco=True):
    """
    Genera las 15 miniaturas temáticas y opcionalmente las guarda como PNGs
    en la carpeta Sprites/Miniaturas/ (nivel_{mundo}_{nivel}.png).
    Retorna un diccionario {mundo: {nivel: Surface}}.
    """
    if guardar_en_disco:
        os.makedirs(RUTA_MINIATURAS, exist_ok=True)

    resultado = {}
    for mundo in (1, 2, 3):
        resultado[mundo] = {}
        for nivel in range(1, 6):
            creador = CREADORES_MINIATURAS[mundo][nivel]
            surf = creador()

            # Añadir borde pixel art sutil para tarjeta
            pygame.draw.rect(surf, (165, 140, 115), (0, 0, ANCHO_MINI, ALTO_MINI), 2, border_radius=6)

            resultado[mundo][nivel] = surf

            if guardar_en_disco:
                ruta_archivo = os.path.join(RUTA_MINIATURAS, f"nivel_{mundo}_{nivel}.png")
                try:
                    pygame.image.save(surf, ruta_archivo)
                except Exception:
                    pass

    return resultado


def obtener_miniaturas():
    """
    Retorna el diccionario de las 15 miniaturas en memoria (con caché).
    Si los archivos PNG ya existen en disco, los carga para máxima velocidad.
    """
    global _CACHE_MINIATURAS
    if _CACHE_MINIATURAS is not None:
        return _CACHE_MINIATURAS

    _CACHE_MINIATURAS = {}
    archivos_completos = True

    for mundo in (1, 2, 3):
        _CACHE_MINIATURAS[mundo] = {}
        for nivel in range(1, 6):
            ruta_img = os.path.join(RUTA_MINIATURAS, f"nivel_{mundo}_{nivel}.png")
            if os.path.isfile(ruta_img):
                try:
                    _CACHE_MINIATURAS[mundo][nivel] = pygame.image.load(ruta_img).convert_alpha()
                except Exception:
                    archivos_completos = False
            else:
                archivos_completos = False

    if not archivos_completos:
        _CACHE_MINIATURAS = generar_todas_las_miniaturas(guardar_en_disco=True)

    return _CACHE_MINIATURAS


def obtener_miniatura(mundo, nivel):
    """Retorna la miniatura específica de un mundo y nivel."""
    todos = obtener_miniaturas()
    return todos.get(mundo, {}).get(nivel)


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1, 1))
    mins = generar_todas_las_miniaturas(guardar_en_disco=True)
    print(f"¡Las 15 miniaturas fueron creadas y guardadas exitosamente en {RUTA_MINIATURAS}!")
