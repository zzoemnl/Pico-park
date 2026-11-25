"""
Camerino: elección de color y accesorio de cada jugador.
"""
import pygame
import random as _random
from configuracion import obtener_idioma, reproducir_sonido_ui, t
from fuentes import (
    TAMANO_BADGE,
    TAMANO_BOTONES,
    TAMANO_SUBTITULO,
    TAMANO_TEXTO,
    TAMANO_TITULO,
    dibujar_texto_en_rect,
    obtener_fuente_para_texto,
)
from menu_niveles import dibujar_mascota_gato
from menus.comunes import (
    ESTADO_MENU_PRINCIPAL,
    FILAS_COLORES_SELECCION,
    PERSONAJES_DISPONIBLES,
    _obtener_nombre_color_visible,
    _obtener_preview_accesorio_tarjeta,
)
from sprites import (
    animar_pulsacion_boton,
    cargar_sprites,
    dibujar_accesorio_en_personaje,
    generar_boton_con_texto,
    obtener_accesorios_disponibles,
)


_fondo_camerino_personajes_cache: "pygame.Surface | None" = None


def _generar_fondo_camerino_personajes(W: int = 1280, H: int = 720) -> "pygame.Surface":
    """
    Genera un fondo pixel art auténtico estilo habitación de vestuario / camerino cálido
    para la pantalla de PERSONALIZACIÓN DE PERSONAJES de Las Aventurillas de Pico en el Parque.
    Paleta: Rosa pastel, durazno, beige cálido, marrón suave, detalles en coral y crema.
    """
    sw, sh = 640, 360
    surf = pygame.Surface((sw, sh))

    # =========================================================================
    # 1. PARED DE HABITACIÓN DE VESTUARIO (y = 0 a 282)
    # =========================================================================
    c_pared_base = (246, 222, 224)
    c_pared_raya = (252, 230, 232)
    c_pared_sombra = (240, 212, 216)

    surf.fill(c_pared_base)

    # Rayas de papel tapiz vertical sutil
    for x in range(sw):
        if x % 10 in (0, 1, 2, 3):
            pygame.draw.line(surf, c_pared_raya, (x, 0), (x, 225))
        elif x % 10 == 9:
            pygame.draw.line(surf, c_pared_sombra, (x, 0), (x, 225))

    # Moldura superior del techo (Cornisa de yeso / madera crema)
    pygame.draw.rect(surf, (253, 248, 242), (0, 0, sw, 3))
    pygame.draw.rect(surf, (242, 230, 218), (0, 3, sw, 3))
    pygame.draw.rect(surf, (218, 196, 180), (0, 6, sw, 2))

    # Moldura intermedia (Chair rail / moldura a y = 222..228)
    pygame.draw.rect(surf, (255, 250, 244), (0, 222, sw, 2))
    pygame.draw.rect(surf, (235, 215, 198), (0, 224, sw, 3))
    pygame.draw.rect(surf, (208, 184, 165), (0, 227, sw, 2))

    # Panel inferior de pared (Wainscoting en crema / durazno suave y = 229..282)
    c_wains_base = (252, 238, 232)
    c_wains_luz = (255, 248, 244)
    c_wains_som = (230, 212, 202)
    pygame.draw.rect(surf, c_wains_base, (0, 229, sw, 53))

    # Paneles moldurados en la parte inferior
    w_pnl = 38
    for px in range(6, sw - 6, w_pnl + 6):
        r_pnl = pygame.Rect(px, 233, w_pnl, 45)
        pygame.draw.rect(surf, c_wains_som, r_pnl, 1)
        pygame.draw.line(surf, c_wains_luz, (r_pnl.left + 1, r_pnl.top + 1), (r_pnl.right - 1, r_pnl.top + 1))
        pygame.draw.line(surf, c_wains_luz, (r_pnl.left + 1, r_pnl.top + 1), (r_pnl.left + 1, r_pnl.bottom - 1))

    # =========================================================================
    # 2. ZÓCALO Y SUELO DE MADERA EN TONOS CÁLIDOS (y = 282 a 360)
    # =========================================================================
    # Zócalo de madera cálida
    pygame.draw.rect(surf, (232, 188, 142), (0, 282, sw, 2)) # Bisel superior de luz
    pygame.draw.rect(surf, (168, 116, 75), (0, 284, sw, 4))  # Madera base
    pygame.draw.rect(surf, (115, 75, 45), (0, 288, sw, 2))   # Sombra de contacto

    # Suelo de madera: tablones de parquet cálidos
    col_tablones = [
        (198, 144, 96),
        (184, 130, 82),
        (206, 152, 104),
        (190, 136, 88),
        (178, 124, 76),
        (200, 146, 98),
        (186, 132, 84),
    ]
    h_tab = 10
    rnd_wood = _random.Random(789)

    for i, c_tab in enumerate(col_tablones):
        y_tab = 290 + i * h_tab
        h_act = min(h_tab, sh - y_tab)
        pygame.draw.rect(surf, c_tab, (0, y_tab, sw, h_act))
        # Vetas de madera
        for vy in range(y_tab + 2, y_tab + h_act - 2, 3):
            c_veta = (max(0, c_tab[0] - 14), max(0, c_tab[1] - 12), max(0, c_tab[2] - 10))
            for vx in range(0, sw, rnd_wood.randint(10, 24)):
                pygame.draw.line(surf, c_veta, (vx, vy), (min(sw, vx + rnd_wood.randint(8, 20)), vy))
        # Línea de unión horizontal oscura
        pygame.draw.line(surf, (115, 75, 45), (0, y_tab + h_act - 1), (sw, y_tab + h_act - 1))
        # Juntas verticales escalonadas
        offset_junta = (i * 41) % 70
        for jx in range(offset_junta, sw, 70):
            pygame.draw.line(surf, (110, 70, 40), (jx, y_tab), (jx, y_tab + h_act - 1))
            surf.set_at((jx + 2, y_tab + 3), (85, 52, 28))
            surf.set_at((jx - 3, y_tab + h_act - 4), (85, 52, 28))

    # =========================================================================
    # 3. ALFOMBRA OVALADA GRANDE Y DISCRETA (debajo de la interfaz)
    # =========================================================================
    cx_alf, cy_alf = 320, 324
    rx_alf, ry_alf = 276, 33

    s_alf = pygame.Surface((sw, sh), pygame.SRCALPHA)

    c_fringe_ext = (226, 132, 114, 255)
    c_fringe_int = (242, 162, 146, 255)
    c_alf_borde = (252, 214, 198, 255)
    c_alf_cuerpo = (254, 248, 240, 255)
    c_alf_textura = (246, 238, 226, 255)

    pygame.draw.ellipse(s_alf, c_fringe_ext, (cx_alf - rx_alf, cy_alf - ry_alf, rx_alf * 2, ry_alf * 2))
    pygame.draw.ellipse(s_alf, c_fringe_int, (cx_alf - rx_alf + 2, cy_alf - ry_alf + 2, (rx_alf - 2) * 2, (ry_alf - 2) * 2))
    pygame.draw.ellipse(s_alf, c_alf_borde, (cx_alf - rx_alf + 5, cy_alf - ry_alf + 4, (rx_alf - 5) * 2, (ry_alf - 4) * 2))
    pygame.draw.ellipse(s_alf, c_alf_cuerpo, (cx_alf - rx_alf + 10, cy_alf - ry_alf + 7, (rx_alf - 10) * 2, (ry_alf - 7) * 2))

    # Textura tejida suave
    for y in range(cy_alf - ry_alf + 8, cy_alf + ry_alf - 7, 2):
        for x in range(cx_alf - rx_alf + 12, cx_alf + rx_alf - 12, 4):
            dx = (x - cx_alf) / float(rx_alf - 12)
            dy = (y - cy_alf) / float(ry_alf - 9)
            if dx * dx + dy * dy < 0.95:
                if (x + y) % 4 == 0:
                    s_alf.set_at((x, y), c_alf_textura)

    # Ribete decorativo interno
    rx_rib, ry_rib = rx_alf - 22, ry_alf - 12
    pygame.draw.ellipse(s_alf, (240, 180, 168, 180), (cx_alf - rx_rib, cy_alf - ry_rib, rx_rib * 2, ry_rib * 2), 1)

    surf.blit(s_alf, (0, 0))

    # =========================================================================
    # 4. ELEMENTOS DECORATIVOS: PARTE SUPERIOR (Guirnalda de luces y plantas)
    # =========================================================================
    # Guirnalda de luces cálidas pegada al techo (y entre 7 y 14) para no tocar el título
    pts_guirnalda = []
    tramos = [
        (0, 105, 7, 14),
        (105, 210, 7, 13),
        (210, 315, 7, 12),
        (315, 420, 7, 12),
        (420, 525, 7, 13),
        (525, 640, 7, 14),
    ]
    for x0, x1, y_top, y_dip in tramos:
        mid = (x0 + x1) / 2.0
        w_t = (x1 - x0) / 2.0
        for x in range(x0, x1 + 1):
            norm = (x - mid) / w_t
            y = int(y_dip - (y_dip - y_top) * (1 - norm * norm))
            pts_guirnalda.append((x, y))

    for i in range(len(pts_guirnalda) - 1):
        pygame.draw.line(surf, (95, 80, 65), pts_guirnalda[i], pts_guirnalda[i+1], 1)

    c_halo = (255, 235, 175, 75)
    s_halo = pygame.Surface((sw, sh), pygame.SRCALPHA)

    for i in range(10, len(pts_guirnalda) - 10, 22):
        bx, by = pts_guirnalda[i]
        by += 1
        surf.set_at((bx, by), (115, 95, 75))
        surf.set_at((bx, by + 1), (255, 255, 235))
        surf.set_at((bx - 1, by + 2), (255, 225, 130))
        surf.set_at((bx, by + 2), (255, 255, 245))
        surf.set_at((bx + 1, by + 2), (255, 225, 130))
        surf.set_at((bx, by + 3), (255, 190, 105))
        pygame.draw.circle(s_halo, c_halo, (bx, by + 2), 5)
        pygame.draw.circle(s_halo, (255, 245, 205, 130), (bx, by + 2), 2)

    surf.blit(s_halo, (0, 0))

    # Plantas colgantes en las esquinas superiores
    def dibujar_maceta_colgante(s, cx, cy, flip=False):
        col_cuerda = (235, 220, 205)
        pygame.draw.line(s, col_cuerda, (cx - 6, 0), (cx - 4, cy - 3))
        pygame.draw.line(s, col_cuerda, (cx + 6, 0), (cx + 4, cy - 3))
        pygame.draw.line(s, col_cuerda, (cx, 0), (cx, cy - 3))

        r_pot = pygame.Rect(cx - 6, cy - 3, 13, 8)
        pygame.draw.rect(s, (225, 125, 95), r_pot, border_radius=2)
        pygame.draw.rect(s, (248, 165, 138), (r_pot.left + 1, r_pot.top + 1, r_pot.width - 2, 2))
        pygame.draw.rect(s, (165, 80, 55), r_pot, 1, border_radius=2)

        col_v1 = (72, 142, 68)
        col_v2 = (110, 182, 95)
        col_v3 = (46, 102, 45)
        hojas = [
            (cx - 4, cy + 5, 5, 8, col_v1),
            (cx + 2, cy + 6, 6, 12, col_v2),
            (cx - 2, cy + 10, 5, 15, col_v1),
            (cx + 4, cy + 14, 4, 10, col_v3),
            (cx - 5, cy + 18, 5, 8, col_v2),
            (cx, cy + 24, 4, 12, col_v1),
            (cx + 1, cy + 34, 3, 6, col_v2),
        ]
        if flip:
            hojas = [(cx - (hx - cx), hy, w, h, c) for hx, hy, w, h, c in hojas]
        for hx, hy, hw, hh, hc in hojas:
            pygame.draw.ellipse(s, hc, (hx - hw//2, hy, hw, hh))
            s.set_at((hx, hy + 2), col_v2)
            pygame.draw.line(s, col_v3, (cx, cy + 2), (hx, hy), 1)

    dibujar_maceta_colgante(surf, 18, 11, flip=False)
    dibujar_maceta_colgante(surf, sw - 18, 11, flip=True)

    # =========================================================================
    # 5. ELEMENTOS DECORATIVOS: LADO IZQUIERDO
    # =========================================================================
    # a) Cuadrito pixel art en la pared (x = 12..44, y = 46..76)
    r_cuadro = pygame.Rect(12, 46, 33, 29)
    pygame.draw.rect(surf, (165, 110, 60), r_cuadro, border_radius=2)
    pygame.draw.rect(surf, (220, 175, 105), (r_cuadro.left + 1, r_cuadro.top + 1, r_cuadro.width - 2, r_cuadro.height - 2), 1)
    pygame.draw.rect(surf, (110, 68, 35), r_cuadro, 1, border_radius=2)

    r_lienzo = pygame.Rect(r_cuadro.left + 3, r_cuadro.top + 3, r_cuadro.width - 6, r_cuadro.height - 6)
    pygame.draw.rect(surf, (253, 248, 238), r_lienzo)
    pygame.draw.rect(surf, (255, 185, 160), (r_lienzo.left, r_lienzo.top, r_lienzo.width, 9))
    pygame.draw.rect(surf, (255, 218, 175), (r_lienzo.left, r_lienzo.top + 9, r_lienzo.width, 6))
    surf.set_at((r_lienzo.right - 7, r_lienzo.top + 4), (255, 245, 210))
    pts_colina = [(r_lienzo.left, r_lienzo.bottom), (r_lienzo.left + 9, r_lienzo.top + 11), (r_lienzo.right, r_lienzo.bottom)]
    pygame.draw.polygon(surf, (105, 165, 95), pts_colina)
    gx, gy = r_lienzo.left + 7, r_lienzo.bottom - 6
    pygame.draw.rect(surf, (55, 45, 40), (gx, gy, 4, 4))
    surf.set_at((gx, gy - 1), (55, 45, 40))
    surf.set_at((gx + 2, gy - 1), (55, 45, 40))
    surf.set_at((gx + 4, gy + 2), (55, 45, 40))
    pygame.draw.line(surf, (140, 100, 65), (r_cuadro.centerx, r_cuadro.top - 5), (r_cuadro.left + 5, r_cuadro.top), 1)
    pygame.draw.line(surf, (140, 100, 65), (r_cuadro.centerx, r_cuadro.top - 5), (r_cuadro.right - 6, r_cuadro.top), 1)
    surf.set_at((r_cuadro.centerx, r_cuadro.top - 6), (110, 75, 45))

    # b) Repisa de madera en la pared izquierda (x = 8..48, y = 94..98)
    r_rep1 = pygame.Rect(8, 94, 41, 5)
    pygame.draw.rect(surf, (175, 120, 72), r_rep1, border_radius=1)
    pygame.draw.rect(surf, (215, 165, 115), (r_rep1.left, r_rep1.top, r_rep1.width, 2))
    pygame.draw.rect(surf, (115, 75, 40), r_rep1, 1)
    pygame.draw.polygon(surf, (135, 85, 50), [(12, 99), (16, 99), (12, 106)])
    pygame.draw.polygon(surf, (135, 85, 50), [(42, 99), (46, 99), (46, 106)])

    # Perfume vintage
    r_perf = pygame.Rect(30, 82, 8, 12)
    pygame.draw.rect(surf, (250, 175, 195), r_perf, border_radius=2)
    pygame.draw.rect(surf, (255, 220, 232), (r_perf.left + 1, r_perf.top + 2, 2, 8))
    surf.set_at((33, 80), (225, 180, 75))
    surf.set_at((34, 80), (225, 180, 75))
    pygame.draw.line(surf, (170, 130, 50), (35, 81), (39, 84))
    pygame.draw.circle(surf, (225, 175, 80), (40, 85), 2)

    # Maceta con enredadera / suculenta
    r_pot_rep = pygame.Rect(11, 85, 11, 9)
    pygame.draw.rect(surf, (230, 135, 100), r_pot_rep, border_radius=2)
    pygame.draw.rect(surf, (155, 80, 55), r_pot_rep, 1)
    surf.set_at((13, 83), (105, 175, 90))
    surf.set_at((15, 82), (72, 142, 68))
    surf.set_at((17, 83), (115, 185, 98))
    surf.set_at((19, 84), (72, 142, 68))
    pts_enredadera = [(12, 94), (10, 101), (13, 108), (9, 116), (12, 124), (10, 131)]
    for i in range(len(pts_enredadera) - 1):
        pygame.draw.line(surf, (60, 120, 55), pts_enredadera[i], pts_enredadera[i+1], 1)
    for px, py in [(9, 98), (14, 105), (8, 113), (14, 120), (9, 128)]:
        pygame.draw.circle(surf, (95, 168, 85), (px, py), 2)
        surf.set_at((px, py), (140, 205, 125))

    # c) Perchero de madera de pie con prendas colgadas (x = 6..44, y = 142..288)
    cx_perch = 24
    pygame.draw.circle(surf, (205, 150, 95), (cx_perch, 144), 3)
    surf.set_at((cx_perch, 143), (240, 190, 140))
    pygame.draw.line(surf, (165, 112, 68), (cx_perch, 147), (cx_perch, 280), 2)
    pygame.draw.line(surf, (205, 155, 105), (cx_perch - 1, 147), (cx_perch - 1, 280), 1)
    pygame.draw.line(surf, (115, 75, 42), (cx_perch + 1, 147), (cx_perch + 1, 280), 1)

    pygame.draw.line(surf, (155, 105, 62), (cx_perch, 154), (cx_perch - 11, 149), 2)
    pygame.draw.circle(surf, (195, 145, 95), (cx_perch - 11, 149), 2)
    pygame.draw.line(surf, (155, 105, 62), (cx_perch, 154), (cx_perch + 11, 149), 2)
    pygame.draw.circle(surf, (195, 145, 95), (cx_perch + 11, 149), 2)

    # Prendas colgadas:
    # 1. Chaqueta coral
    pts_tapado = [
        (cx_perch - 11, 151), (cx_perch - 1, 155), (cx_perch, 205),
        (cx_perch - 7, 208), (cx_perch - 17, 204), (cx_perch - 19, 172)
    ]
    pygame.draw.polygon(surf, (230, 115, 98), pts_tapado)
    pygame.draw.polygon(surf, (175, 78, 65), pts_tapado, 1)
    pygame.draw.line(surf, (248, 155, 138), (cx_perch - 6, 155), (cx_perch - 6, 205), 1)
    for by in [165, 175, 185]:
        surf.set_at((cx_perch - 8, by), (255, 235, 160))

    # 2. Bufanda celeste abrigada
    pts_bufanda = [
        (cx_perch - 5, 162), (cx_perch + 7, 160), (cx_perch + 10, 192),
        (cx_perch + 5, 195), (cx_perch + 2, 170), (cx_perch - 4, 168)
    ]
    pygame.draw.polygon(surf, (125, 188, 218), pts_bufanda)
    pygame.draw.polygon(surf, (85, 140, 168), pts_bufanda, 1)
    for fx in range(cx_perch + 5, cx_perch + 11, 2):
        surf.set_at((fx, 196), (125, 188, 218))

    # 3. Suéter mostaza
    pts_sueter = [
        (cx_perch + 2, 152), (cx_perch + 12, 151), (cx_perch + 14, 180),
        (cx_perch + 9, 182), (cx_perch + 3, 172)
    ]
    pygame.draw.polygon(surf, (242, 195, 88), pts_sueter)
    pygame.draw.polygon(surf, (180, 138, 52), pts_sueter, 1)

    # Patas de madera
    pygame.draw.line(surf, (140, 92, 55), (cx_perch, 276), (cx_perch - 13, 287), 2)
    pygame.draw.line(surf, (140, 92, 55), (cx_perch, 276), (cx_perch + 13, 287), 2)
    pygame.draw.line(surf, (110, 70, 40), (cx_perch, 276), (cx_perch, 289), 2)

    # =========================================================================
    # 6. ELEMENTOS DECORATIVOS: LADO DERECHO
    # =========================================================================
    # a) Repisa de madera en la pared derecha (x = 590..634, y = 88..92)
    r_rep2 = pygame.Rect(590, 88, 42, 5)
    pygame.draw.rect(surf, (175, 120, 72), r_rep2, border_radius=1)
    pygame.draw.rect(surf, (215, 165, 115), (r_rep2.left, r_rep2.top, r_rep2.width, 2))
    pygame.draw.rect(surf, (115, 75, 40), r_rep2, 1)
    pygame.draw.polygon(surf, (135, 85, 50), [(595, 93), (599, 93), (595, 100)])
    pygame.draw.polygon(surf, (135, 85, 50), [(625, 93), (629, 93), (629, 100)])

    # Cajas sombrereras
    r_box1 = pygame.Rect(594, 71, 22, 17)
    pygame.draw.rect(surf, (244, 182, 190), r_box1, border_radius=3)
    pygame.draw.rect(surf, (255, 238, 240), (r_box1.left, r_box1.top, r_box1.width, 4), border_radius=2)
    pygame.draw.rect(surf, (185, 120, 130), r_box1, 1, border_radius=3)
    pygame.draw.rect(surf, (230, 110, 95), (r_box1.centerx - 2, r_box1.top, 4, r_box1.height))

    r_box2 = pygame.Rect(597, 56, 16, 15)
    pygame.draw.rect(surf, (252, 212, 185), r_box2, border_radius=3)
    pygame.draw.rect(surf, (255, 246, 235), (r_box2.left, r_box2.top, r_box2.width, 4), border_radius=2)
    pygame.draw.rect(surf, (195, 145, 120), r_box2, 1, border_radius=3)
    pygame.draw.rect(surf, (235, 185, 75), (r_box2.centerx - 1, r_box2.top, 3, r_box2.height))
    surf.set_at((r_box2.centerx - 2, r_box2.top - 1), (235, 185, 75))
    surf.set_at((r_box2.centerx + 2, r_box2.top - 1), (235, 185, 75))
    surf.set_at((r_box2.centerx, r_box2.top - 1), (255, 220, 110))

    # Florerito decorativo
    r_vaso = pygame.Rect(620, 74, 9, 14)
    pygame.draw.rect(surf, (175, 215, 230), r_vaso, border_radius=3)
    pygame.draw.rect(surf, (230, 245, 252), (r_vaso.left + 1, r_vaso.top + 2, 2, 10))
    pygame.draw.rect(surf, (120, 160, 175), r_vaso, 1, border_radius=3)
    pygame.draw.line(surf, (140, 100, 65), (624, 74), (622, 65))
    pygame.draw.line(surf, (140, 100, 65), (625, 74), (627, 63))
    pygame.draw.circle(surf, (248, 165, 165), (622, 64), 2)
    pygame.draw.circle(surf, (252, 210, 140), (627, 62), 2)

    # b) Soporte / maniquí con sombrero (posicionado a x = 556..580, y = 100..144)
    cx_man = 566
    pygame.draw.ellipse(surf, (165, 112, 68), (cx_man - 7, 141, 15, 5))
    pygame.draw.ellipse(surf, (205, 155, 105), (cx_man - 6, 142, 13, 2))
    pygame.draw.line(surf, (155, 105, 65), (cx_man, 126), (cx_man, 142), 2)
    pygame.draw.circle(surf, (225, 185, 145), (cx_man, 122), 6)

    pygame.draw.ellipse(surf, (185, 75, 70), (cx_man - 14, 117, 28, 8))
    pygame.draw.ellipse(surf, (215, 105, 100), (cx_man - 13, 118, 26, 5))
    r_copa = pygame.Rect(cx_man - 7, 108, 15, 10)
    pygame.draw.rect(surf, (185, 75, 70), r_copa, border_radius=4)
    pygame.draw.rect(surf, (220, 110, 105), (r_copa.left + 2, r_copa.top + 1, r_copa.width - 4, 3))
    pygame.draw.rect(surf, (255, 245, 230), (r_copa.left, r_copa.bottom - 3, r_copa.width, 3))
    surf.set_at((r_copa.right + 1, r_copa.top + 2), (255, 220, 120))

    # c) Espejo grande de cuerpo entero con marco de madera (x = 590..630, y = 138..288)
    cx_esp = 610
    w_esp = 38
    h_esp = 142
    r_esp_marco = pygame.Rect(cx_esp - w_esp // 2, 138, w_esp, h_esp)

    pygame.draw.line(surf, (135, 88, 50), (r_esp_marco.left + 2, r_esp_marco.bottom - 10), (r_esp_marco.left - 5, r_esp_marco.bottom + 6), 3)
    pygame.draw.line(surf, (135, 88, 50), (r_esp_marco.right - 2, r_esp_marco.bottom - 10), (r_esp_marco.right + 5, r_esp_marco.bottom + 6), 3)

    pygame.draw.rect(surf, (165, 112, 68), r_esp_marco, border_radius=8)
    pygame.draw.circle(surf, (195, 145, 95), (cx_esp, r_esp_marco.top + 2), 4)
    surf.set_at((cx_esp, r_esp_marco.top + 1), (240, 190, 135))
    pygame.draw.rect(surf, (115, 75, 42), r_esp_marco, 1, border_radius=8)
    pygame.draw.rect(surf, (215, 165, 115), (r_esp_marco.left + 1, r_esp_marco.top + 1, r_esp_marco.width - 2, r_esp_marco.height - 2), 1, border_radius=7)

    r_vidrio = pygame.Rect(r_esp_marco.left + 3, r_esp_marco.top + 6, r_esp_marco.width - 6, r_esp_marco.height - 10)
    pygame.draw.rect(surf, (218, 234, 244), r_vidrio, border_radius=5)
    pygame.draw.rect(surf, (235, 222, 224), (r_vidrio.left, r_vidrio.top + 20, r_vidrio.width, r_vidrio.height - 35))

    for d in range(12):
        surf.set_at((r_vidrio.left + 5 + d, r_vidrio.top + 8 + d * 2), (255, 255, 255))
        surf.set_at((r_vidrio.left + 6 + d, r_vidrio.top + 8 + d * 2), (255, 255, 255))
        if d < 18:
            surf.set_at((r_vidrio.left + 4 + d, r_vidrio.top + 45 + d * 2), (255, 255, 255))
            surf.set_at((r_vidrio.left + 5 + d, r_vidrio.top + 45 + d * 2), (255, 255, 255))

    pygame.draw.circle(surf, (210, 160, 100), (r_esp_marco.left - 1, r_esp_marco.top + 60), 3)
    pygame.draw.circle(surf, (210, 160, 100), (r_esp_marco.right + 1, r_esp_marco.top + 60), 3)

    return pygame.transform.scale(surf, (W, H))


def _obtener_fondo_personajes(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_camerino_personajes_cache
    if _fondo_camerino_personajes_cache is None:
        _fondo_camerino_personajes_cache = _generar_fondo_camerino_personajes(ancho, alto)
    return _fondo_camerino_personajes_cache


def _eventos_personajes(m, evento):
    """Clic izquierdo en la pantalla «personajes». Devuelve True si hay que cortar el resto de eventos del frame."""
    if m.btn_volver_personajes.collidepoint(evento.pos) or m.btn_guardar.collidepoint(evento.pos):
        m.pulsado = True
        m.idm_act = obtener_idioma()
        m.sp_vp_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_vp_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_vp_n = m._obtener_boton_volver("normal", m.idm_act)
        if m.sp_vp_s and m.sp_vp_a and m.btn_volver_personajes.collidepoint(evento.pos):
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_personajes, m.sp_vp_s, m.sp_vp_a, _obtener_fondo_personajes(m.ANCHO_MENU, m.ALTO_MENU), m.sp_vp_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MENU_PRINCIPAL
            return True

    # Pestañas [ COLORES ] y [ ACCESORIOS ]
    m.rect_tab_col = pygame.Rect(388, 83, 240, 67)
    m.rect_tab_acc = pygame.Rect(652, 83, 240, 67)

    if m.rect_tab_col.collidepoint(evento.pos):
        if m.tab_personajes_actual != "colores":
            m.tab_personajes_actual = "colores"
            reproducir_sonido_ui("tab")
    elif m.rect_tab_acc.collidepoint(evento.pos):
        if m.tab_personajes_actual != "accesorios":
            m.tab_personajes_actual = "accesorios"
            reproducir_sonido_ui("tab")
        m.acc_list_tab = obtener_accesorios_disponibles()
        for m._ia, m._acc in enumerate(m.acc_list_tab):
            if m._acc["id"] == m.accesorio_p1:
                m.pagina_acc_p1 = m._ia // 6
            if m._acc["id"] == m.accesorio_p2:
                m.pagina_acc_p2 = m._ia // 6

    # Marcos de selección (Jugador 1: izquierda=125, Jugador 2: izquierda=685)
    m.rect_f1_ev = pygame.Rect(125, 295, 470, 276)
    m.rect_f2_ev = pygame.Rect(685, 295, 470, 276)

    if m.tab_personajes_actual == "colores":
        m.w_sw, m.h_sw = 80, 45
        m.y_start_sw = 338
        m.h_paso_y = 77
        for m.r_idx, m.fila in enumerate(FILAS_COLORES_SELECCION):
            m.n = len(m.fila)
            m.gap_x = 10 if m.n == 5 else 24
            m.row_w = m.n * m.w_sw + (m.n - 1) * m.gap_x
            m.x_start_rel = (m.rect_f1_ev.width - m.row_w) // 2
            m.y_sw = m.y_start_sw + m.r_idx * m.h_paso_y
            for m.c_idx, m.color_idx in enumerate(m.fila):
                m.p_info = PERSONAJES_DISPONIBLES[m.color_idx]
                m.x_sw_rel = m.x_start_rel + m.c_idx * (m.w_sw + m.gap_x)
                m.r1 = pygame.Rect(m.rect_f1_ev.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw + 28)
                m.r2 = pygame.Rect(m.rect_f2_ev.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw + 28)

                if m.r1.collidepoint(evento.pos):
                    if m.color_p1 != m.p_info["nombre"]:
                        m.color_p1 = m.p_info["nombre"]
                        m.personalizacion_modificada_en_menu = True
                        reproducir_sonido_ui("select")
                        # Respetar accesorios exclusivos: si el equipado no le pertenece, desequipar
                        m.permitidos_p1 = [a["id"] for a in obtener_accesorios_disponibles(m.color_p1)]
                        if m.accesorio_p1 not in m.permitidos_p1:
                            m.accesorio_p1 = "Ninguno"
                if m.r2.collidepoint(evento.pos):
                    if m.color_p2 != m.p_info["nombre"]:
                        m.color_p2 = m.p_info["nombre"]
                        m.personalizacion_modificada_en_menu = True
                        reproducir_sonido_ui("select")
                        # Respetar accesorios exclusivos: si el equipado no le pertenece, desequipar
                        m.permitidos_p2 = [a["id"] for a in obtener_accesorios_disponibles(m.color_p2)]
                        if m.accesorio_p2 not in m.permitidos_p2:
                            m.accesorio_p2 = "Ninguno"

    elif m.tab_personajes_actual == "accesorios":
        m.accesorios_p1_disp = obtener_accesorios_disponibles(m.color_p1)
        m.accesorios_p2_disp = obtener_accesorios_disponibles(m.color_p2)
        m.items_por_pag = 6
        m.total_pags_p1 = max(1, (len(m.accesorios_p1_disp) + m.items_por_pag - 1) // m.items_por_pag)
        m.total_pags_p2 = max(1, (len(m.accesorios_p2_disp) + m.items_por_pag - 1) // m.items_por_pag)

        # Flechas de paginación para Jugador 1
        m.btn_prev_p1 = pygame.Rect(m.rect_f1_ev.centerx - 72, m.rect_f1_ev.top + 234, 34, 26)
        m.btn_next_p1 = pygame.Rect(m.rect_f1_ev.centerx + 38, m.rect_f1_ev.top + 234, 34, 26)
        if m.btn_prev_p1.collidepoint(evento.pos):
            m.pagina_acc_p1 = (m.pagina_acc_p1 - 1) % m.total_pags_p1
            reproducir_sonido_ui("pagina")
        elif m.btn_next_p1.collidepoint(evento.pos):
            m.pagina_acc_p1 = (m.pagina_acc_p1 + 1) % m.total_pags_p1
            reproducir_sonido_ui("pagina")

        # Flechas de paginación para Jugador 2
        m.btn_prev_p2 = pygame.Rect(m.rect_f2_ev.centerx - 72, m.rect_f2_ev.top + 234, 34, 26)
        m.btn_next_p2 = pygame.Rect(m.rect_f2_ev.centerx + 38, m.rect_f2_ev.top + 234, 34, 26)
        if m.btn_prev_p2.collidepoint(evento.pos):
            m.pagina_acc_p2 = (m.pagina_acc_p2 - 1) % m.total_pags_p2
            reproducir_sonido_ui("pagina")
        elif m.btn_next_p2.collidepoint(evento.pos):
            m.pagina_acc_p2 = (m.pagina_acc_p2 + 1) % m.total_pags_p2
            reproducir_sonido_ui("pagina")

        m.w_acc, m.h_acc, m.gap_acc_x, m.gap_acc_y = 126, 82, 16, 10
        m.ancho_fila_acc = 3 * m.w_acc + 2 * m.gap_acc_x
        m.x_offset_acc = (m.rect_f1_ev.width - m.ancho_fila_acc) // 2

        # Selección de accesorios en marco de Jugador 1
        m.inicio_p1 = m.pagina_acc_p1 * m.items_por_pag
        for m.idx_rel, m.acc in enumerate(m.accesorios_p1_disp[m.inicio_p1:m.inicio_p1 + m.items_por_pag]):
            m.r = m.idx_rel // 3
            m.c = m.idx_rel % 3
            m.x_offset_rel = m.x_offset_acc + m.c * (m.w_acc + m.gap_acc_x)
            m.y_card_a = m.rect_f1_ev.top + 42 + m.r * (m.h_acc + m.gap_acc_y)
            m.ra1 = pygame.Rect(m.rect_f1_ev.left + m.x_offset_rel, m.y_card_a, m.w_acc, m.h_acc)
            if m.ra1.collidepoint(evento.pos):
                if m.accesorio_p1 != m.acc["id"]:
                    m.accesorio_p1 = m.acc["id"]
                    m.personalizacion_modificada_en_menu = True
                    reproducir_sonido_ui("select")

        # Selección de accesorios en marco de Jugador 2
        m.inicio_p2 = m.pagina_acc_p2 * m.items_por_pag
        for m.idx_rel, m.acc in enumerate(m.accesorios_p2_disp[m.inicio_p2:m.inicio_p2 + m.items_por_pag]):
            m.r = m.idx_rel // 3
            m.c = m.idx_rel % 3
            m.x_offset_rel = m.x_offset_acc + m.c * (m.w_acc + m.gap_acc_x)
            m.y_card_a = m.rect_f2_ev.top + 42 + m.r * (m.h_acc + m.gap_acc_y)
            m.ra2 = pygame.Rect(m.rect_f2_ev.left + m.x_offset_rel, m.y_card_a, m.w_acc, m.h_acc)
            if m.ra2.collidepoint(evento.pos):
                if m.accesorio_p2 != m.acc["id"]:
                    m.accesorio_p2 = m.acc["id"]
                    m.personalizacion_modificada_en_menu = True
                    reproducir_sonido_ui("select")
    return False


def _dibujar_personajes(m):
    """Dibuja la pantalla «personajes»."""
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()

    # 1. Fondo de habitación de vestuario / camerino pixel art
    m.pantalla.blit(_obtener_fondo_personajes(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))

    # 2. Título y subtítulo centrados
    txt_tit_pj = t("personalizacion_personajes")
    f_tit_pj = obtener_fuente_para_texto(txt_tit_pj, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
    m.titulo = f_tit_pj.render(txt_tit_pj, True, (60, 45, 35))
    m.pantalla.blit(m.titulo, m.titulo.get_rect(center=(m.ANCHO_MENU // 2, 46)))

    txt_sub_pj = t("sub_personalizacion")
    f_sub_pj = obtener_fuente_para_texto(txt_sub_pj, categoria="subtitulo", tamano=TAMANO_SUBTITULO)
    m.subt = f_sub_pj.render(txt_sub_pj, True, (120, 100, 85))
    m.pantalla.blit(m.subt, m.subt.get_rect(center=(m.ANCHO_MENU // 2, 78)))

    # 3. Pestañas visuales [ COLORES ] y [ ACCESORIOS ] con sprites oficiales
    w_tab_pj = 240
    h_tab_pj = round(w_tab_pj * 264 / 950)  # 67 px
    y_tab_pj = 150 - h_tab_pj               # 83 px
    m.rect_tab_col = pygame.Rect(388, y_tab_pj, w_tab_pj, h_tab_pj)
    m.rect_tab_acc = pygame.Rect(652, y_tab_pj, w_tab_pj, h_tab_pj)

    hov_tab_col = m.rect_tab_col.collidepoint(m.pos_mouse)
    hov_tab_acc = m.rect_tab_acc.collidepoint(m.pos_mouse)

    # Dibujar primero la pestaña inactiva y luego la seleccionada para mantener profundidad correcta
    tabs_orden = [
        ("accesorios", m.rect_tab_acc, hov_tab_acc),
        ("colores", m.rect_tab_col, hov_tab_col),
    ] if m.tab_personajes_actual == "colores" else [
        ("colores", m.rect_tab_col, hov_tab_col),
        ("accesorios", m.rect_tab_acc, hov_tab_acc),
    ]

    for m.tab_id, m.r_tab, m.hov in tabs_orden:
        m.es_activa = (m.tab_personajes_actual == m.tab_id)
        m.nom_spr = f"{m.tab_id}-seleccionado.png" if m.es_activa else f"{m.tab_id}.png"
        m.col_txt_tab = (116, 78, 45) if m.es_activa else (157, 131, 100)
        m.spr_tab = generar_boton_con_texto(
            m.nom_spr, w_tab_pj, h_tab_pj,
            texto=t(m.tab_id).upper(),
            color_texto=m.col_txt_tab,
            tamano_fuente=16,
            offset_y=0,
        )
        if m.spr_tab:
            m.pantalla.blit(m.spr_tab, (m.r_tab.left, m.r_tab.top))
            if not m.es_activa and m.hov:
                m.glow = m.spr_tab.copy()
                m.bright = pygame.Surface(m.spr_tab.get_size(), pygame.SRCALPHA)
                m.bright.fill((35, 35, 35, 0))
                m.glow.blit(m.bright, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                m.pantalla.blit(m.glow, (m.r_tab.left, m.r_tab.top))
        else:
            m.r_fb = pygame.Rect(m.r_tab.left, 100, w_tab_pj, 50)
            m.col_tab_bg = (246, 215, 153) if m.es_activa else ((248, 242, 232) if m.hov else (238, 226, 210))
            m.col_tab_borde = (175, 130, 80) if m.es_activa else (195, 175, 155)
            m.ancho_b = 3 if m.es_activa else 2
            pygame.draw.rect(m.pantalla, m.col_tab_bg, m.r_fb, border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_tab_borde, m.r_fb, m.ancho_b, border_radius=12)

            m.col_txt = (50, 40, 30) if m.es_activa else (130, 115, 100)
            m.txt_tab_str = t(m.tab_id).upper()
            dibujar_texto_en_rect(m.pantalla, m.txt_tab_str, m.r_fb, categoria="boton", tamano=18, color=m.col_txt, negrita=True, padding=8)

            if m.es_activa:
                dibujar_mascota_gato(m.pantalla, m.r_fb.left + 16, m.r_fb.top - 18, size=28, color=(246, 215, 153))

    # 4. Columnas simétricas de Jugador 1 y Jugador 2
    cx_p1 = 360
    cx_p2 = 920

    colores_dict = {p["nombre"]: p["color"] for p in PERSONAJES_DISPONIBLES}
    c_p1_val = colores_dict.get(m.color_p1, (124, 231, 255))
    c_p2_val = colores_dict.get(m.color_p2, (161, 123, 255))

    # Badges de encabezado de jugador con ajuste automático para nombres extensos de color
    r_badge_p1 = pygame.Rect(cx_p1 - 130, 150, 260, 32)
    pygame.draw.rect(m.pantalla, c_p1_val, r_badge_p1, border_radius=8)
    pygame.draw.rect(m.pantalla, (60, 45, 35), r_badge_p1, 2, border_radius=8)
    col_p1_trad = _obtener_nombre_color_visible(m.color_p1, m.idm_act).upper()
    dibujar_texto_en_rect(m.pantalla, f"{t('jugador')} 1  ({col_p1_trad})", r_badge_p1, categoria="boton", tamano=TAMANO_BADGE, color=(35, 30, 25), padding=4)

    r_badge_p2 = pygame.Rect(cx_p2 - 130, 150, 260, 32)
    pygame.draw.rect(m.pantalla, c_p2_val, r_badge_p2, border_radius=8)
    pygame.draw.rect(m.pantalla, (60, 45, 35), r_badge_p2, 2, border_radius=8)
    col_p2_trad = _obtener_nombre_color_visible(m.color_p2, m.idm_act).upper()
    dibujar_texto_en_rect(m.pantalla, f"{t('jugador')} 2  ({col_p2_trad})", r_badge_p2, categoria="boton", tamano=TAMANO_BADGE, color=(35, 30, 25), padding=4)

    # Previews de personajes con pedestal y accesorios
    for m.cx, m.col_pj, m.acc_pj in [
        (cx_p1, m.color_p1, m.accesorio_p1),
        (cx_p2, m.color_p2, m.accesorio_p2),
    ]:
        pygame.draw.ellipse(m.pantalla, (230, 210, 175), (m.cx - 50, 276, 100, 16))

        m.sp_pj = cargar_sprites(m.col_pj)
        m.img_pj = m.sp_pj.get("quieto", list(m.sp_pj.values())[0])
        m.rect_pj = m.img_pj.get_rect(center=(m.cx, 240))
        m.pantalla.blit(m.img_pj, m.rect_pj)

        if m.acc_pj and m.acc_pj != "Ninguno":
            dibujar_accesorio_en_personaje(m.pantalla, m.acc_pj, sprite_personaje=m.img_pj, rect_personaje=m.rect_pj, mirando_derecha=True)

    # 5. Marcos rectangulares contenedores de opciones
    w_frame, h_frame = 470, 276
    y_frame = 295
    rect_f1 = pygame.Rect(cx_p1 - w_frame // 2, y_frame, w_frame, h_frame)
    rect_f2 = pygame.Rect(cx_p2 - w_frame // 2, y_frame, w_frame, h_frame)

    for m.rf in (rect_f1, rect_f2):
        pygame.draw.rect(m.pantalla, (253, 246, 233), m.rf, border_radius=16)
        pygame.draw.rect(m.pantalla, (195, 168, 138), m.rf, 3, border_radius=16)

        m.txt_encabezado = t("colores_disponibles") if m.tab_personajes_actual == "colores" else t("accesorios_disponibles")
        m.f_enc = obtener_fuente_para_texto(m.txt_encabezado, categoria="texto", tamano=TAMANO_TEXTO, negrita=True)
        m.t_enc = m.f_enc.render(m.txt_encabezado, True, (115, 95, 80))
        m.pantalla.blit(m.t_enc, m.t_enc.get_rect(center=(m.rf.centerx, m.rf.top + 20)))
        pygame.draw.line(m.pantalla, (235, 215, 195), (m.rf.left + 24, m.rf.top + 34), (m.rf.right - 24, m.rf.top + 34), 2)

    # 6. Opciones dentro del marco según la pestaña activa
    if m.tab_personajes_actual == "colores":
        m.w_sw, m.h_sw = 80, 45
        m.y_start_sw = 338
        m.h_paso_y = 77
        for m.r_idx, m.fila in enumerate(FILAS_COLORES_SELECCION):
            m.n = len(m.fila)
            m.gap_x = 10 if m.n == 5 else 24
            m.row_w = m.n * m.w_sw + (m.n - 1) * m.gap_x
            m.x_start_rel = (rect_f1.width - m.row_w) // 2
            m.y_sw = m.y_start_sw + m.r_idx * m.h_paso_y

            for m.c_idx, m.color_idx in enumerate(m.fila):
                m.p_info = PERSONAJES_DISPONIBLES[m.color_idx]
                m.x_sw_rel = m.x_start_rel + m.c_idx * (m.w_sw + m.gap_x)
                m.r1 = pygame.Rect(rect_f1.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw)
                m.r2 = pygame.Rect(rect_f2.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw)
                m.nom_col = _obtener_nombre_color_visible(m.p_info["nombre"], m.idm_act)
                m.f_nom = obtener_fuente_para_texto(m.nom_col, categoria="dialogos", tamano=22, negrita=True)

                # P1 swatch
                m.sel1 = (m.p_info["nombre"] == m.color_p1)
                m.hov1 = m.r1.collidepoint(m.pos_mouse)
                pygame.draw.rect(m.pantalla, m.p_info["color"], m.r1, border_radius=8)
                if m.sel1:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r1, 3, border_radius=8)
                    pygame.draw.rect(m.pantalla, (40, 30, 25), m.r1, 1, border_radius=8)
                    m.cx_k, m.cy_k = m.r1.center
                    m.pts_chk = [(m.cx_k - 7, m.cy_k), (m.cx_k - 2, m.cy_k + 5), (m.cx_k + 7, m.cy_k - 5)]
                    m.pts_shadow = [(x + 1, y + 1) for x, y in m.pts_chk]
                    pygame.draw.lines(m.pantalla, (40, 30, 25), False, m.pts_shadow, 4)
                    pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_chk, 3)
                elif m.hov1:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r1, 2, border_radius=8)
                else:
                    pygame.draw.rect(m.pantalla, (180, 160, 140), m.r1, 1, border_radius=8)

                m.col_t1 = (25, 15, 8) if m.sel1 else (50, 34, 22)
                m.ts1 = m.f_nom.render(m.nom_col, True, m.col_t1)
                m.tx1 = m.r1.centerx - m.ts1.get_width() // 2
                m.ty1 = m.r1.bottom + 4
                m.pantalla.blit(m.ts1, (m.tx1, m.ty1))
                m.pantalla.blit(m.ts1, (m.tx1 + 1, m.ty1))

                # P2 swatch
                m.sel2 = (m.p_info["nombre"] == m.color_p2)
                m.hov2 = m.r2.collidepoint(m.pos_mouse)
                pygame.draw.rect(m.pantalla, m.p_info["color"], m.r2, border_radius=8)
                if m.sel2:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r2, 3, border_radius=8)
                    pygame.draw.rect(m.pantalla, (40, 30, 25), m.r2, 1, border_radius=8)
                    m.cx_k2, m.cy_k2 = m.r2.center
                    m.pts_chk2 = [(m.cx_k2 - 7, m.cy_k2), (m.cx_k2 - 2, m.cy_k2 + 5), (m.cx_k2 + 7, m.cy_k2 - 5)]
                    m.pts_shadow2 = [(x + 1, y + 1) for x, y in m.pts_chk2]
                    pygame.draw.lines(m.pantalla, (40, 30, 25), False, m.pts_shadow2, 4)
                    pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_chk2, 3)
                elif m.hov2:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r2, 2, border_radius=8)
                else:
                    pygame.draw.rect(m.pantalla, (180, 160, 140), m.r2, 1, border_radius=8)

                m.col_t2 = (25, 15, 8) if m.sel2 else (50, 34, 22)
                m.ts2 = m.f_nom.render(m.nom_col, True, m.col_t2)
                m.tx2 = m.r2.centerx - m.ts2.get_width() // 2
                m.ty2 = m.r2.bottom + 4
                m.pantalla.blit(m.ts2, (m.tx2, m.ty2))
                m.pantalla.blit(m.ts2, (m.tx2 + 1, m.ty2))

    elif m.tab_personajes_actual == "accesorios":
        m.items_por_pag = 6
        m.w_acc, m.h_acc, m.gap_acc_x, m.gap_acc_y = 126, 82, 16, 10
        m.ancho_fila_acc = 3 * m.w_acc + 2 * m.gap_acc_x
        m.x_offset_acc = (w_frame - m.ancho_fila_acc) // 2

        for m.rf, m.acc_actual, m.pag_num, m.color_pj_actual in [
            (rect_f1, m.accesorio_p1, m.pagina_acc_p1, m.color_p1),
            (rect_f2, m.accesorio_p2, m.pagina_acc_p2, m.color_p2),
        ]:
            m.accesorios_disp = obtener_accesorios_disponibles(m.color_pj_actual)
            m.total_pags = max(1, (len(m.accesorios_disp) + m.items_por_pag - 1) // m.items_por_pag)
            m.pag_num = min(m.pag_num, m.total_pags - 1)
            # 1. Controles inferiores de paginación
            m.btn_prev = pygame.Rect(m.rf.centerx - 72, m.rf.top + 234, 34, 26)
            m.btn_next = pygame.Rect(m.rf.centerx + 38, m.rf.top + 234, 34, 26)

            for m.b_rect, m.es_izq in [(m.btn_prev, True), (m.btn_next, False)]:
                m.hov_b = m.b_rect.collidepoint(m.pos_mouse)
                m.col_bg_b = (255, 252, 245) if m.hov_b else (244, 236, 224)
                m.col_brd_b = (220, 180, 120) if m.hov_b else (195, 168, 138)
                pygame.draw.rect(m.pantalla, m.col_bg_b, m.b_rect, border_radius=6)
                pygame.draw.rect(m.pantalla, m.col_brd_b, m.b_rect, 2, border_radius=6)

                m.col_arr = (80, 60, 45) if m.hov_b else (120, 100, 85)
                m.cx_b, m.cy_b = m.b_rect.center
                if m.es_izq:
                    for m.dy in range(-5, 6):
                        m.ancho_f = 5 - abs(m.dy)
                        for m.dx in range(m.ancho_f + 1):
                            m.pantalla.set_at((m.cx_b + 2 - m.dx, m.cy_b + m.dy), m.col_arr)
                else:
                    for m.dy in range(-5, 6):
                        m.ancho_f = 5 - abs(m.dy)
                        for m.dx in range(m.ancho_f + 1):
                            m.pantalla.set_at((m.cx_b - 2 + m.dx, m.cy_b + m.dy), m.col_arr)

            m.txt_pag = f"{m.pag_num + 1} / {m.total_pags}"
            m.f_pag = obtener_fuente_para_texto(m.txt_pag, categoria="texto", tamano=TAMANO_BADGE, negrita=True)
            m.t_pag = m.f_pag.render(m.txt_pag, True, (115, 95, 80))
            m.pantalla.blit(m.t_pag, m.t_pag.get_rect(center=(m.rf.centerx, m.rf.top + 247)))

            # 2. Tarjetas de accesorios de la página activa con fondo crema claro de alto contraste
            m.inicio = m.pag_num * m.items_por_pag
            for m.idx_rel, m.acc in enumerate(m.accesorios_disp[m.inicio:m.inicio + m.items_por_pag]):
                m.r = m.idx_rel // 3
                m.c = m.idx_rel % 3
                m.x_offset_rel = m.x_offset_acc + m.c * (m.w_acc + m.gap_acc_x)
                m.y_card_a = m.rf.top + 42 + m.r * (m.h_acc + m.gap_acc_y)
                m.r_card_a = pygame.Rect(m.rf.left + m.x_offset_rel, m.y_card_a, m.w_acc, m.h_acc)

                m.sel = (m.acc["id"] == m.acc_actual or m.acc["id"].lower() == str(m.acc_actual).lower())
                m.hov = m.r_card_a.collidepoint(m.pos_mouse)

                m.col_bg_a = (242, 252, 244) if m.sel else ((255, 252, 246) if m.hov else (248, 242, 232))
                m.col_brd_a = (45, 165, 85) if m.sel else ((180, 145, 110) if m.hov else (195, 168, 138))
                pygame.draw.rect(m.pantalla, m.col_bg_a, m.r_card_a, border_radius=10)
                pygame.draw.rect(m.pantalla, m.col_brd_a, m.r_card_a, 3 if m.sel else 2, border_radius=10)

                if m.sel:
                    m.cx_ca = m.r_card_a.right - 14
                    m.cy_ca = m.r_card_a.top + 14
                    pygame.draw.circle(m.pantalla, (45, 165, 85), (m.cx_ca, m.cy_ca), 9)
                    m.pts_ca = [(m.cx_ca - 4, m.cy_ca), (m.cx_ca - 1, m.cy_ca + 3), (m.cx_ca + 4, m.cy_ca - 3)]
                    pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_ca, 2)

                if m.acc["id"] == "Ninguno":
                    m.cx_ic, m.cy_ic = m.r_card_a.centerx, m.r_card_a.top + 25
                    pygame.draw.circle(m.pantalla, (220, 80, 75), (m.cx_ic, m.cy_ic), 13, width=2)
                    pygame.draw.line(m.pantalla, (220, 80, 75), (m.cx_ic - 8, m.cy_ic - 8), (m.cx_ic + 8, m.cy_ic + 8), 2)
                else:
                    m.surf_icon = _obtener_preview_accesorio_tarjeta(m.acc["id"])
                    if m.surf_icon:
                        m.r_mini = m.surf_icon.get_rect(center=(m.r_card_a.centerx, m.r_card_a.top + 25))
                        m.pantalla.blit(m.surf_icon, m.r_mini)

                m.col_nom = (25, 75, 35) if m.sel else ((45, 30, 18) if m.hov else (55, 38, 25))
                m.rect_nom_acc = pygame.Rect(m.r_card_a.left + 2, m.r_card_a.bottom - 32, m.r_card_a.width - 4, 30)
                m.nom_acc_trad = t(m.acc["id"].lower())
                dibujar_texto_en_rect(m.pantalla, m.nom_acc_trad, m.rect_nom_acc, categoria="boton", tamano=13, color=m.col_nom, negrita=True, multiline=True, alineacion="centro", padding=0, interlineado=1)

    # 7. Botón Volver al Menú
    hov_vpj = m.btn_volver_personajes.collidepoint(m.pos_mouse)
    spr_vpj_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vpj_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vpj = spr_vpj_hov if (hov_vpj and spr_vpj_hov) else spr_vpj_norm
    if spr_vpj:
        m.pantalla.blit(spr_vpj, m.btn_volver_personajes)
    else:
        m.col_v = (255, 255, 255) if hov_vpj else (242, 234, 222)
        pygame.draw.rect(m.pantalla, m.col_v, m.btn_volver_personajes, border_radius=10)
        pygame.draw.rect(m.pantalla, (185, 155, 125), m.btn_volver_personajes, width=2, border_radius=10)
        dibujar_texto_en_rect(m.pantalla, t("volver_al_menu"), m.btn_volver_personajes, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)
