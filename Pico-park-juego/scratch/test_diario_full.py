import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Pico-park-juego"))

import pygame
from test_diario_bg import generar_fondo_diario
import fuentes

def dibujar_icono_candado(s, cx, cy, abierto=False):
    """Dibuja un candado pixel art vintage de 9x11 px."""
    col_cuerpo = (185, 142, 68)
    col_arco = (115, 85, 52)
    col_ojo = (52, 28, 16)
    # Arco
    if not abierto:
        pygame.draw.rect(s, col_arco, (cx - 3, cy - 5, 7, 5), 1)
    else:
        pygame.draw.line(s, col_arco, (cx - 3, cy - 5), (cx - 3, cy - 1), 1)
        pygame.draw.line(s, col_arco, (cx - 3, cy - 5), (cx + 1, cy - 5), 1)
        pygame.draw.line(s, col_arco, (cx + 1, cy - 5), (cx + 1, cy - 3), 1)
    # Cuerpo
    pygame.draw.rect(s, col_cuerpo, (cx - 4, cy - 1, 9, 7))
    pygame.draw.rect(s, col_arco, (cx - 4, cy - 1, 9, 7), 1)
    # Ojo de la cerradura
    s.set_at((cx, cy + 2), col_ojo)
    s.set_at((cx, cy + 3), col_ojo)

def dibujar_icono_calendario(s, cx, cy):
    """Dibuja un icono de diario / calendario pixel art de 10x10 px."""
    col_hoja = (255, 252, 245)
    col_borde = (135, 95, 65)
    col_rojo = (185, 65, 52)
    # Cuerpo
    pygame.draw.rect(s, col_hoja, (cx - 5, cy - 4, 10, 9))
    pygame.draw.rect(s, col_borde, (cx - 5, cy - 4, 10, 9), 1)
    # Cinta superior roja
    pygame.draw.line(s, col_rojo, (cx - 4, cy - 3), (cx + 3, cy - 3), 2)
    # Anillas
    s.set_at((cx - 3, cy - 5), col_borde)
    s.set_at((cx + 2, cy - 5), col_borde)

def probar_candado_y_fichas():
    pygame.init()
    W, H = 1280, 720
    pantalla = pygame.Surface((W, H))

    fondo = generar_fondo_diario(W, H)
    pantalla.blit(fondo, (0, 0))

    fuente_pixel_titulo = fuentes.obtener_fuente_titulo(36, tamano_fallback=36)
    fuente_subtitulo = fuentes.obtener_fuente_subtitulo(22)
    fuente_pixel_btn = fuentes.obtener_fuente_botones(17, tamano_fallback=17)
    fuente_pixel_card_btn = fuentes.obtener_fuente_botones(14, tamano_fallback=14)
    fuente_card_titulo = fuentes.obtener_fuente_subtitulo(20)
    fuente_card_sub = fuentes.obtener_fuente_pequena(15)
    fuente_badge = fuentes.obtener_fuente_botones(14, tamano_fallback=14)

    # Título
    txt_tit = "PARTIDAS GUARDADAS"
    t_somb = fuente_pixel_titulo.render(txt_tit, True, (225, 205, 180))
    t_tit = fuente_pixel_titulo.render(txt_tit, True, (54, 26, 16))
    rect_tit = t_tit.get_rect(center=(W // 2, 48))
    pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
    pantalla.blit(t_tit, rect_tit)

    txt_sub = "Registro de expediciones y diario de aventuras"
    t_sub = fuente_subtitulo.render(txt_sub, True, (115, 82, 62))
    rect_sub = t_sub.get_rect(center=(W // 2, 84))
    pantalla.blit(t_sub, rect_sub)

    ancho_panel = 920
    alto_panel = 448
    x_panel = (W - ancho_panel) // 2
    y_panel = 106
    rect_panel = pygame.Rect(x_panel, y_panel, ancho_panel, alto_panel)

    col_pagina = (252, 245, 233)
    col_borde_pag = (195, 168, 135)
    col_borde_int = (225, 202, 168)
    pygame.draw.rect(pantalla, col_pagina, rect_panel, border_radius=14)
    pygame.draw.rect(pantalla, col_borde_pag, rect_panel, width=2, border_radius=14)
    pygame.draw.rect(pantalla, col_borde_int, (rect_panel.left + 3, rect_panel.top + 3, rect_panel.width - 6, rect_panel.height - 6), width=1, border_radius=12)

    for y_linea in range(rect_panel.top + 16, rect_panel.bottom - 16, 26):
        pygame.draw.line(pantalla, (240, 230, 214), (rect_panel.left + 24, y_linea), (rect_panel.right - 24, y_linea), 1)

    for cx_d, cy_d in [(rect_panel.left + 10, rect_panel.top + 10), (rect_panel.right - 10, rect_panel.top + 10),
                       (rect_panel.left + 10, rect_panel.bottom - 10), (rect_panel.right - 10, rect_panel.bottom - 10)]:
        pygame.draw.circle(pantalla, (215, 185, 135), (cx_d, cy_d), 3)

    partidas_ejemplo = [
        {"id": 1, "nombre": "Expedición Alfa", "mundo_max": 2, "nivel_max": 3, "fecha": "30/10/2026", "tiene_password": True, "niveles_desbloqueados": {1: [True]*5, 2: [True, True, True, False, False]}},
        {"id": 2, "nombre": "Camino Nevada", "mundo_max": 1, "nivel_max": 5, "fecha": "28/10/2026", "tiene_password": False, "niveles_desbloqueados": {1: [True]*5}},
        {"id": 3, "nombre": "Exploradores del Valle", "mundo_max": 3, "nivel_max": 1, "fecha": "25/10/2026", "tiene_password": False, "niveles_desbloqueados": {1: [True]*5, 2: [True]*5, 3: [True, False, False, False, False]}},
    ]

    alto_card = 82
    gap_cards = 12
    for idx_slot, p in enumerate(partidas_ejemplo):
        r_card = pygame.Rect(
            rect_panel.left + 20,
            rect_panel.top + 18 + idx_slot * (alto_card + gap_cards),
            rect_panel.width - 40,
            alto_card,
        )

        col_card = (255, 252, 245)
        col_borde_card = (205, 180, 150)
        pygame.draw.rect(pantalla, col_card, r_card, border_radius=10)
        pygame.draw.rect(pantalla, col_borde_card, r_card, width=2, border_radius=10)
        pygame.draw.line(pantalla, (225, 175, 95), (r_card.left + 2, r_card.top + 4), (r_card.left + 2, r_card.bottom - 4), 3)

        m_val = p.get("mundo_max", 1)
        w_badge, h_badge = 116, 50
        r_badge = pygame.Rect(r_card.left + 16, r_card.centery - (h_badge // 2), w_badge, h_badge)

        colores_mundo = {
            1: {"fondo": (238, 246, 238), "borde": (72, 142, 85), "texto": (35, 88, 48)},
            2: {"fondo": (255, 246, 235), "borde": (215, 130, 48), "texto": (135, 68, 18)},
            3: {"fondo": (250, 240, 248), "borde": (148, 68, 120), "texto": (88, 32, 72)},
        }
        info_b = colores_mundo.get(m_val, colores_mundo[1])
        pygame.draw.rect(pantalla, info_b["fondo"], r_badge, border_radius=8)
        pygame.draw.rect(pantalla, info_b["borde"], r_badge, width=2, border_radius=8)

        t_badge = fuente_badge.render(f"MUNDO {m_val}", True, info_b["texto"])
        pantalla.blit(t_badge, t_badge.get_rect(center=(r_badge.centerx, r_badge.centery - 8)))

        fuente_sub_badge = fuentes.obtener_fuente_pequena(12)
        t_sub_b = fuente_sub_badge.render("EXPEDICION", True, (135, 105, 85))
        pantalla.blit(t_sub_b, t_sub_b.get_rect(center=(r_badge.centerx, r_badge.centery + 12)))

        x_texto = r_badge.right + 18
        w_borrar, w_gestionar, w_cargar, h_btn = 96, 118, 126, 38
        gap_btns, margin_der = 10, 16

        r_btn_borrar = pygame.Rect(r_card.right - margin_der - w_borrar, r_card.centery - (h_btn // 2), w_borrar, h_btn)
        r_btn_gestionar = pygame.Rect(r_btn_borrar.left - gap_btns - w_gestionar, r_card.centery - (h_btn // 2), w_gestionar, h_btn)
        r_btn_cargar = pygame.Rect(r_btn_gestionar.left - gap_btns - w_cargar, r_card.centery - (h_btn // 2), w_cargar, h_btn)

        sym_x = x_texto + 4
        sym_y = r_card.top + 24
        pygame.draw.polygon(pantalla, (215, 168, 80), [(sym_x, sym_y - 5), (sym_x + 5, sym_y), (sym_x, sym_y + 5), (sym_x - 5, sym_y)])
        pygame.draw.polygon(pantalla, (120, 80, 42), [(sym_x, sym_y - 5), (sym_x + 5, sym_y), (sym_x, sym_y + 5), (sym_x - 5, sym_y)], 1)

        nombre_str = p.get("nombre", f"Partida {p['id']}")
        t_nombre = fuente_card_titulo.render(nombre_str, True, (48, 24, 15))
        pantalla.blit(t_nombre, (x_texto + 14, r_card.top + 14))

        mundo_m = p.get("mundo_max", 1)
        nivel_m = p.get("nivel_max", 1)
        fecha_str = p.get("fecha", "Reciente")
        tiene_pwd = p.get("tiene_password", False)
        total_comp = sum(sum(1 for v in lista if v) for lista in p.get("niveles_desbloqueados", {}).values())

        # Renderizado de línea de datos con iconos pixel art
        y_info = r_card.top + 48
        x_cursor = x_texto + 14

        t_prog = fuente_card_sub.render(f"Nivel {mundo_m}-{nivel_m}  •  {total_comp}/15 compl.  •", True, (118, 92, 75))
        pantalla.blit(t_prog, (x_cursor, y_info))
        x_cursor += t_prog.get_width() + 10

        # Icono candado
        dibujar_icono_candado(pantalla, x_cursor + 4, y_info + 8, abierto=not tiene_pwd)
        txt_pwd = "Con clave" if tiene_pwd else "Sin clave"
        t_pwd = fuente_card_sub.render(txt_pwd, True, (118, 92, 75))
        pantalla.blit(t_pwd, (x_cursor + 14, y_info))
        x_cursor += 14 + t_pwd.get_width() + 10

        # Icono calendario y fecha
        t_sep = fuente_card_sub.render("•", True, (118, 92, 75))
        pantalla.blit(t_sep, (x_cursor, y_info))
        x_cursor += t_sep.get_width() + 10

        dibujar_icono_calendario(pantalla, x_cursor + 5, y_info + 8)
        t_fecha = fuente_card_sub.render(fecha_str, True, (118, 92, 75))
        pantalla.blit(t_fecha, (x_cursor + 14, y_info))

        # Botones
        # CARGAR
        col_c_cara = (68, 138, 80)
        col_c_luz = (118, 185, 128)
        col_c_borde = (28, 62, 35)
        pygame.draw.rect(pantalla, col_c_borde, r_btn_cargar, border_radius=8)
        pygame.draw.rect(pantalla, col_c_cara, (r_btn_cargar.left + 2, r_btn_cargar.top + 2, r_btn_cargar.width - 4, r_btn_cargar.height - 4), border_radius=6)
        pygame.draw.line(pantalla, col_c_luz, (r_btn_cargar.left + 4, r_btn_cargar.top + 3), (r_btn_cargar.right - 5, r_btn_cargar.top + 3), 2)
        t_btn_c = fuente_pixel_card_btn.render("CARGAR", True, (255, 255, 255))
        pantalla.blit(t_btn_c, t_btn_c.get_rect(center=r_btn_cargar.center))

        # GESTIONAR
        col_g_cara = (244, 236, 222)
        col_g_luz = (255, 252, 245)
        col_g_borde = (125, 92, 65)
        pygame.draw.rect(pantalla, col_g_borde, r_btn_gestionar, border_radius=8)
        pygame.draw.rect(pantalla, col_g_cara, (r_btn_gestionar.left + 2, r_btn_gestionar.top + 2, r_btn_gestionar.width - 4, r_btn_gestionar.height - 4), border_radius=6)
        pygame.draw.line(pantalla, col_g_luz, (r_btn_gestionar.left + 4, r_btn_gestionar.top + 3), (r_btn_gestionar.right - 5, r_btn_gestionar.top + 3), 2)
        t_btn_g = fuente_pixel_card_btn.render("GESTIONAR", True, (58, 28, 16))
        pantalla.blit(t_btn_g, t_btn_g.get_rect(center=r_btn_gestionar.center))

        # BORRAR
        col_b_cara = (208, 86, 75)
        col_b_luz = (238, 132, 120)
        col_b_borde = (95, 32, 28)
        pygame.draw.rect(pantalla, col_b_borde, r_btn_borrar, border_radius=8)
        pygame.draw.rect(pantalla, col_b_cara, (r_btn_borrar.left + 2, r_btn_borrar.top + 2, r_btn_borrar.width - 4, r_btn_borrar.height - 4), border_radius=6)
        pygame.draw.line(pantalla, col_b_luz, (r_btn_borrar.left + 4, r_btn_borrar.top + 3), (r_btn_borrar.right - 5, r_btn_borrar.top + 3), 2)
        t_btn_b = fuente_pixel_card_btn.render("BORRAR", True, (255, 255, 255))
        pantalla.blit(t_btn_b, t_btn_b.get_rect(center=r_btn_borrar.center))

    t_pag = fuentes.obtener_fuente_contador(15).render("Página 1 de 1", True, (105, 78, 58))
    pantalla.blit(t_pag, t_pag.get_rect(center=(rect_panel.centerx, rect_panel.bottom - 22)))

    from test_full_ui import crear_boton_pixel_art
    W_VOLVER, H_VOLVER = 238, 68
    total_w = W_VOLVER * 2 + 24
    x_inicio = (W - total_w) // 2
    y_btns = 582

    btn_v = crear_boton_pixel_art(
        W_VOLVER, H_VOLVER, "VOLVER", icono="volver", estilo="crema", estado="normal", fuente_tit=fuente_pixel_btn
    )
    btn_n = crear_boton_pixel_art(
        W_VOLVER, H_VOLVER, "NUEVA PARTIDA", icono="estrella", estilo="ambar", estado="normal", fuente_tit=fuente_pixel_btn
    )

    pantalla.blit(btn_v, (x_inicio, y_btns))
    pantalla.blit(btn_n, (x_inicio + W_VOLVER + 24, y_btns))

    out_file = "scratch/pantalla_diario_completa2.png"
    pygame.image.save(pantalla, out_file)
    print("Guardada en:", out_file)

if __name__ == '__main__':
    probar_candado_y_fichas()
