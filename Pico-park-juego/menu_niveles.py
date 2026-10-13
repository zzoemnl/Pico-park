import math
import pygame

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
            return ["caja", "pinchos"]
        elif nivel == 4:
            return ["pinchos"]
        elif nivel == 5:
            return ["caja"]
    elif mundo == 2:
        return ["soga"]
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


from miniaturas import obtener_miniaturas


def obtener_thumbnails():
    """Retorna las 15 miniaturas oficiales de los niveles generadas en miniaturas.py."""
    return obtener_miniaturas()


def obtener_geometria_menu(ancho_pantalla, alto_pantalla):
    """
    Calcula dinámicamente los rectángulos interactivos del menú
    adaptados a la resolución actual del juego.
    """
    w_panel = min(1140, int(ancho_pantalla * 0.90))
    h_panel = min(330, int(alto_pantalla * 0.49))
    x_panel = (ancho_pantalla - w_panel) // 2
    y_panel = (alto_pantalla - h_panel) // 2 + 35

    # Pestañas
    w_tab = min(230, int((w_panel - 80) / 3))
    h_tab_activa = 58
    h_tab_inactiva = 48
    gap_tab = 10
    x_tabs_start = x_panel + 35

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

    # Tarjetas de nivel (5 columnas en una sola fila)
    pad_x = 20
    pad_y = 20
    gap_cards = 16
    w_card = (w_panel - 2 * pad_x - 4 * gap_cards) // 5
    h_card = h_panel - 2 * pad_y

    rects_cards = []
    for i in range(5):
        x_c = x_panel + pad_x + i * (w_card + gap_cards)
        y_c = y_panel + pad_y
        rects_cards.append(pygame.Rect(x_c, y_c, w_card, h_card))

    rect_panel = pygame.Rect(x_panel, y_panel, w_panel, h_panel)
    return rect_panel, rects_tabs, rects_cards


def dibujar_menu_niveles(pantalla, mundo_actual, niveles_desbloqueados, pos_mouse, fuentes):
    """
    Dibuja la pantalla completa de selección de niveles con estética pixel art Pico Park:
    - Fondo de paisaje pastel con nubes y cactus.
    - Pestañas superiores estilizadas para cada mundo con mascota de gato.
    - Panel contenedor con 5 tarjetas horizontales, miniaturas, nombres y estrellas.
    """
    ancho, alto = pantalla.get_size()
    rect_panel, tabs_info, rects_cards = obtener_geometria_menu(ancho, alto)
    thumbs = obtener_thumbnails()

    fuente_titulo = fuentes.get("titulo")
    fuente_tab = fuentes.get("tab")
    fuente_card = fuentes.get("card")

    # 1. FONDO DE PAISAJE PASTEL
    pantalla.fill(COL_CIELO)

    # Nubes decorativas
    for cx, cy, cw in [(100, 60, 95), (ancho // 2 - 40, 48, 115), (ancho - 160, 75, 90)]:
        pygame.draw.ellipse(pantalla, (255, 255, 255), (cx, cy, cw, 28))
        pygame.draw.ellipse(pantalla, (255, 255, 255), (cx + 16, cy - 8, cw - 32, 28))

    # Suelo con pasto y cactus
    y_pasto = alto - 55
    pygame.draw.rect(pantalla, COL_TIERRA, (0, y_pasto + 10, ancho, 45))
    pygame.draw.rect(pantalla, COL_PASTO, (0, y_pasto, ancho, 12))
    for kx in [35, 65, ancho - 75, ancho - 45]:
        pygame.draw.rect(pantalla, (85, 150, 70), (kx, y_pasto - 22, 10, 24), border_radius=3)
        pygame.draw.rect(pantalla, (85, 150, 70), (kx - 4, y_pasto - 16, 6, 8), border_radius=2)
        pygame.draw.rect(pantalla, (85, 150, 70), (kx + 8, y_pasto - 12, 6, 8), border_radius=2)

    # Título principal
    if fuente_titulo:
        txt_tit = fuente_titulo.render("SELECCIÓN DE NIVEL", True, (60, 45, 35))
        pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, 70)))

    # 2. PESTAÑAS (MUNDO 1, MUNDO 2, MUNDO 3)
    # Dibujamos primero las inactivas y al final la activa para que la activa quede al frente
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
            txt_tab = fuente_tab.render(f"MUNDO {m}", True, color_txt)
            rect_txt_tab = txt_tab.get_rect(center=(x_t + w_t // 2, y_t + h_t // 2 - 2))
            pantalla.blit(txt_tab, rect_txt_tab)

        # Mascota de gatito Pico Park en la pestaña activa
        if es_activa:
            dibujar_mascota_gato(pantalla, x_t + 16, y_t - 28, size=34, color=info_col["fondo"])

    # 3. PANEL CONTENEDOR PRINCIPAL
    pygame.draw.rect(pantalla, COL_PANEL, rect_panel, border_radius=18)
    pygame.draw.rect(pantalla, COL_BORDE_PANEL, rect_panel, 3, border_radius=18)

    # Líneas divisorias sutiles entre tarjetas
    for i in range(1, 5):
        c_left = rects_cards[i - 1].right
        c_right = rects_cards[i].left
        x_div = (c_left + c_right) // 2
        pygame.draw.line(pantalla, COL_DIVISOR, (x_div, rect_panel.top + 20), (x_div, rect_panel.bottom - 20), 2)

    # 4. TARJETAS DE NIVEL (5 EN FILA)
    for idx, r_card in enumerate(rects_cards):
        nivel_num = idx + 1
        desbloqueado = niveles_desbloqueados[mundo_actual][idx]
        mouse_encima = r_card.collidepoint(pos_mouse)

        # Fondo individual de la tarjeta al hacer hover
        if mouse_encima:
            card_highlight = pygame.Surface((r_card.width, r_card.height), pygame.SRCALPHA)
            card_highlight.fill((255, 255, 255, 140))
            pantalla.blit(card_highlight, r_card)
            pygame.draw.rect(pantalla, (235, 195, 140), r_card, 2, border_radius=12)

        # Miniatura del escenario
        thumb_img = thumbs[mundo_actual][nivel_num]
        w_th, h_th = thumb_img.get_size()
        x_th = r_card.centerx - w_th // 2
        y_th = r_card.top + 14
        r_th = pygame.Rect(x_th, y_th, w_th, h_th)

        # Si el mouse está encima, elevar la miniatura 2 píxeles
        y_draw_th = y_th - (2 if mouse_encima and desbloqueado else 0)
        pantalla.blit(thumb_img, (x_th, y_draw_th))

        # Overlay de bloqueo si está bloqueado
        if not desbloqueado:
            lock_mask = pygame.Surface((w_th, h_th), pygame.SRCALPHA)
            lock_mask.fill((30, 20, 20, 160))
            pantalla.blit(lock_mask, (x_th, y_draw_th))
            # Icono de candado
            cx, cy = x_th + w_th // 2, y_draw_th + h_th // 2
            pygame.draw.rect(pantalla, (230, 210, 170), (cx - 10, cy - 4, 20, 16), border_radius=3)
            pygame.draw.arc(pantalla, (230, 210, 170), (cx - 7, cy - 14, 14, 16), 0, 3.14, 3)

        # Texto "NIVEL X"
        if fuente_card:
            col_texto_n = (55, 45, 35) if desbloqueado else (150, 140, 130)
            txt_n = fuente_card.render(f"NIVEL {nivel_num}", True, col_texto_n)
            rect_txt_n = txt_n.get_rect(center=(r_card.centerx, r_th.bottom + 26))
            pantalla.blit(txt_n, rect_txt_n)

        # Estrella decorativa debajo
        y_star = r_th.bottom + 58
        if desbloqueado:
            dibujar_estrella(pantalla, (r_card.centerx, y_star), r_exterior=14, r_interior=6)
        else:
            # Estrella gris vacía si está bloqueado
            dibujar_estrella(
                pantalla,
                (r_card.centerx, y_star),
                r_exterior=14,
                r_interior=6,
                col_relleno=(235, 230, 222),
                col_borde=(180, 170, 160),
            )
