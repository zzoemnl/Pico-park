import os
import sys
import pygame

# Set headless display
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath("Pico-park-juego"))

import configuracion
import fuentes
import sprites
import main
import menu_niveles
import personajes_menu

pygame.init()
pygame.display.init()
pygame.font.init()

pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()

os.makedirs("scratch/screenshots", exist_ok=True)

idiomas = ["es", "en", "zh"]

# Dummy saves
dummy_partidas = [
    {
        "id": 1,
        "nombre": "Aventurero 1",
        "mundo_max": 2,
        "nivel_max": 3,
        "fecha": "2026-10-31",
        "hora": "14:30",
        "niveles_desbloqueados": {
            1: [True, True, True, True, True],
            2: [True, True, True, False, False],
            3: [False, False, False, False, False],
        },
        "tiene_password": False,
        "color_p1": "Celeste",
        "color_p2": "Violeta",
        "accesorio_p1": "Corona",
        "accesorio_p2": "Sombrero",
    },
    {
        "id": 2,
        "nombre": "Explorador Pro",
        "mundo_max": 3,
        "nivel_max": 5,
        "fecha": "2026-10-31",
        "hora": "18:15",
        "niveles_desbloqueados": {
            1: [True, True, True, True, True],
            2: [True, True, True, True, True],
            3: [True, True, True, True, True],
        },
        "tiene_password": True,
        "color_p1": "Rojo",
        "color_p2": "Amarillo",
        "accesorio_p1": "Gorro",
        "accesorio_p2": "Anteojos",
    }
]

main.cargar_partidas = lambda: dummy_partidas

def get_menu_buttons(idm):
    ANCHO_BOTON, ALTO_BOTON = 380, 78
    x_centro = (1280 - ANCHO_BOTON) // 2
    btn_j = pygame.Rect(x_centro, 240, ANCHO_BOTON, ALTO_BOTON)
    btn_p = pygame.Rect(x_centro, 330, ANCHO_BOTON, ALTO_BOTON)
    btn_c = pygame.Rect(x_centro, 420, ANCHO_BOTON, ALTO_BOTON)
    btn_s = pygame.Rect(x_centro, 510, ANCHO_BOTON, ALTO_BOTON)

    if idm == "es":
        return [
            (btn_j, sprites.cargar_boton_escalado("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON), None),
            (btn_p, sprites.cargar_boton_escalado("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON), None),
            (btn_c, sprites.cargar_boton_escalado("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON), None),
            (btn_s, sprites.cargar_boton_escalado("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON), None),
        ]
    bj = sprites.generar_boton_con_texto("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON, configuracion.t("jugar"), (27, 82, 36), 26, 0, idm)
    bp = sprites.generar_boton_con_texto("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON, configuracion.t("personajes"), (42, 68, 124), 24, 0, idm)
    bc = sprites.generar_boton_con_texto("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON, configuracion.t("opciones"), (115, 67, 16), 26, 0, idm)
    bs = sprites.generar_boton_con_texto("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON, configuracion.t("salir"), (255, 255, 255), 26, 0, idm)
    return [
        (btn_j, bj, None),
        (btn_p, bp, None),
        (btn_c, bc, None),
        (btn_s, bs, None),
    ]

def get_modo_button(tipo, idm):
    w, h = 425, 100
    if idm == "es":
        if tipo == "continuar":
            return sprites.cargar_boton_escalado("Menu/boton-continuar-cargar....png", w, h)
        return sprites.cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", w, h)

    if tipo == "continuar":
        base_path = "Menu/boton-continuar-cargar....png"
        col_bg = (142, 235, 120)
        col_tit = (18, 55, 24)
        col_sub = (25, 75, 30)
        tit = configuracion.t("continuar")
        sub = configuracion.t("sub_continuar")
    else:
        base_path = "mundos/boton-nueva-partida-reiniciar....png"
        col_bg = (255, 138, 142)
        col_tit = (95, 25, 35)
        col_sub = (115, 30, 42)
        tit = configuracion.t("nueva_partida")
        sub = configuracion.t("sub_nueva_partida")

    marco = sprites.generar_marco_boton(base_path, w, h)
    surf = marco.copy()
    rect_int = pygame.Rect(6, 6, w - 12, h - 22)
    pygame.draw.rect(surf, col_bg, rect_int)

    if idm == "zh":
        f_tit = fuentes.obtener_fuente_cjk(30, negrita=True)
        f_sub = fuentes.obtener_fuente_cjk(15, negrita=False)
        t_tit_s = f_tit.render(tit, True, (0, 0, 0))
        t_tit = f_tit.render(tit, True, col_tit)
        t_sub = f_sub.render(sub, True, col_sub)
        r_tit = t_tit.get_rect(center=(w // 2, 38))
        surf.blit(t_tit_s, r_tit.move(1, 1))
        surf.blit(t_tit, r_tit)
        r_sub = t_sub.get_rect(center=(w // 2, 70))
        surf.blit(t_sub, r_sub)
    else:
        f_tit = fuentes.obtener_fuente_titulo(26)
        f_sub = fuentes.obtener_fuente_pequena(16)
        t_tit_s = f_tit.render(tit, False, (0, 0, 0))
        t_tit = f_tit.render(tit, False, col_tit)
        t_sub = f_sub.render(sub, False, col_sub)
        r_tit = t_tit.get_rect(center=(w // 2, 36))
        surf.blit(t_tit_s, r_tit.move(1, 1))
        surf.blit(t_tit, r_tit)
        r_sub = t_sub.get_rect(center=(w // 2, 70))
        surf.blit(t_sub, r_sub)
    return surf

def get_volver_button(idm, w=238, h=70):
    if idm == "es":
        return sprites.cargar_boton_escalado("mundos/boton-volver.png", w, h)
    return sprites.generar_boton_con_texto("mundos/boton-volver.png", w, h, configuracion.t("volver"), (60, 45, 30), 16, 0, idm)

def get_card_sprites(idm):
    if idm == "es":
        return {
            "cargar_normal": sprites.cargar_boton_escalado("mundos/boton-cargar.png", 126, 38),
            "cargar_hover": None,
            "gestionar_normal": sprites.generar_boton_con_texto("mundos/boton-volver.png", 118, 38, "GESTIONAR", (60, 45, 30), 13, 0),
            "gestionar_hover": None,
            "borrar_normal": sprites.generar_boton_con_texto("Menu/salir.png", 96, 38, "BORRAR", (255, 255, 255), 14, 0),
            "borrar_hover": None,
        }
    return {
        "cargar_normal": sprites.generar_boton_con_texto("mundos/boton-cargar.png", 126, 38, configuracion.t("cargar"), (26, 83, 29), 14, 0, idm),
        "cargar_hover": None,
        "gestionar_normal": sprites.generar_boton_con_texto("mundos/boton-volver.png", 118, 38, configuracion.t("gestionar"), (60, 45, 30), 13, 0, idm),
        "gestionar_hover": None,
        "borrar_normal": sprites.generar_boton_con_texto("Menu/salir.png", 96, 38, configuracion.t("borrar"), (255, 255, 255), 14, 0, idm),
        "borrar_hover": None,
    }

for idm in idiomas:
    configuracion.cambiar_idioma(idm)
    print(f"=== Rendering screens for language: {idm} ===")

    # 1. Menú Principal
    pantalla.fill((30, 30, 30))
    gestor_menu = personajes_menu.GestorPersonajesMenu()
    gestor_menu.sincronizar_personalizacion("Celeste", "Ninguno", "Violeta", "Ninguno")
    botones_menu_datos = get_menu_buttons(idm)
    rect_btn_x = pygame.Rect(1280 - 45, 12, 33, 38)
    spr_x = sprites.cargar_boton_escalado("HUD/boton-x.png", 33, 38)
    fuente_titulo = fuentes.obtener_fuente_titulo(fuentes.TAMANO_TITULO)
    gestor_menu.dibujar_menu_completo(
        pantalla,
        botones_menu_datos=botones_menu_datos,
        pos_mouse=(0, 0),
        spr_x=spr_x,
        rect_x=rect_btn_x,
        fuente_titulo=fuente_titulo
    )
    pygame.image.save(pantalla, f"scratch/screenshots/1_menu_principal_{idm}.png")

    # 2. Modo de Juego
    pantalla.blit(main._obtener_fondo_modo_juego(1280, 720), (0, 0))
    w_placa = min(680, 1280 - 40)
    h_placa = 106
    x_placa = (1280 - w_placa) // 2
    y_placa = 45
    surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    pygame.draw.rect(surf_placa, (252, 242, 228, 225), (0, 0, w_placa, h_placa), border_radius=16)
    pygame.draw.rect(surf_placa, (85, 28, 48, 240), (0, 0, w_placa, h_placa), width=3, border_radius=16)
    pantalla.blit(surf_placa, (x_placa, y_placa))

    txt_tit = configuracion.t("modo_juego")
    f_tit_modo = fuentes.obtener_fuente_para_texto(txt_tit, categoria="titulo", tamano=fuentes.TAMANO_TITULO, negrita=True)
    t_somb = f_tit_modo.render(txt_tit, True, (225, 205, 185))
    t_tit = f_tit_modo.render(txt_tit, True, (68, 20, 42))
    rect_tit = t_tit.get_rect(center=(1280 // 2, y_placa + 38))
    pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
    pantalla.blit(t_tit, rect_tit)

    txt_sub = configuracion.t("subtitulo_modo")
    ancho_max_sub = w_placa - 70
    f_sub_modo, _ = fuentes.ajustar_tamano_fuente(txt_sub, categoria="subtitulo", tamano_inicial=fuentes.TAMANO_SUBTITULO, ancho_max=ancho_max_sub, tamano_min=13)
    t_sub_s = f_sub_modo.render(txt_sub, True, (255, 255, 255))
    t_sub = f_sub_modo.render(txt_sub, True, (108, 52, 45))
    rect_sub = t_sub.get_rect(center=(1280 // 2, y_placa + 78))
    pantalla.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
    pantalla.blit(t_sub, rect_sub)

    btn_continuar = pygame.Rect(440, 200, 400, 100)
    btn_nueva = pygame.Rect(440, 330, 400, 100)
    btn_volver = pygame.Rect(530, 520, 220, 52)
    spr_c = get_modo_button("continuar", idm)
    spr_n = get_modo_button("nueva", idm)
    spr_v = get_volver_button(idm, 220, 52)
    pantalla.blit(spr_c, btn_continuar)
    pantalla.blit(spr_n, btn_nueva)
    pantalla.blit(spr_v, btn_volver)
    pygame.image.save(pantalla, f"scratch/screenshots/2_modo_juego_{idm}.png")

    # 3. Partidas Guardadas
    pantalla.blit(main._obtener_fondo_partidas(1280, 720), (0, 0))
    rect_panel, btn_volver_p, btn_nueva_p, _ = main.obtener_geometria_panel_partidas(1280, 720, True)

    txt_tit_lp = configuracion.t("partidas_guardadas")
    f_tit_lp = fuentes.obtener_fuente_para_texto(txt_tit_lp, categoria="titulo", tamano=fuentes.TAMANO_TITULO, negrita=True)
    t_somb = f_tit_lp.render(txt_tit_lp, True, (195, 170, 140))
    t_tit = f_tit_lp.render(txt_tit_lp, True, (58, 38, 24))
    rect_tit = t_tit.get_rect(center=(1280 // 2, 46))
    pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
    pantalla.blit(t_tit, rect_tit)

    txt_sub_lp = configuracion.t("sub_partidas")
    f_sub_lp = fuentes.obtener_fuente_para_texto(txt_sub_lp, categoria="decorativa", tamano=fuentes.TAMANO_DECORATIVA)
    subt = f_sub_lp.render(txt_sub_lp, True, (125, 95, 65))
    pantalla.blit(subt, subt.get_rect(center=(1280 // 2, 78)))

    # Panel
    pygame.draw.rect(pantalla, (252, 246, 235), rect_panel, border_radius=16)
    pygame.draw.rect(pantalla, (190, 160, 125), rect_panel, width=3, border_radius=16)

    # Tarjetas
    fuentes_tarjetas = {
        "titulo_card": fuentes.obtener_fuente_titulo(24),
        "sub_card": fuentes.obtener_fuente_subtitulo(18),
        "btn_card": fuentes.obtener_fuente_boton(16),
        "badge": fuentes.obtener_fuente_boton(16),
        "btn": fuentes.obtener_fuente_boton(16),
        "texto": fuentes.obtener_fuente_texto(16),
        "sub_btn": fuentes.obtener_fuente_boton(14),
    }
    dict_sp = get_card_sprites(idm)
    for idx_slot, p in enumerate(dummy_partidas):
        main.dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel, (0, 0), fuentes_tarjetas, sprites_botones=dict_sp)

    # Botones inferiores
    spr_vp = get_volver_button(idm, 160, 44)
    spr_nd = (
        sprites.cargar_boton_escalado("mundos/boton-nueva-partida.png", 238, 70)
        if idm == "es"
        else sprites.generar_boton_con_texto("mundos/boton-nueva-partida.png", 238, 70, configuracion.t("nueva_partida"), (95, 25, 35), 14, 0, idm)
    )
    pantalla.blit(spr_vp, btn_volver_p)
    pantalla.blit(spr_nd, btn_nueva_p)
    pygame.image.save(pantalla, f"scratch/screenshots/3_partidas_guardadas_{idm}.png")

    # 4. Selección de Nivel
    desbloqueados = {
        1: [True, True, True, True, True],
        2: [True, True, False, False, False],
        3: [False, False, False, False, False],
    }
    menu_niveles.dibujar_menu_niveles(pantalla, 1, desbloqueados, (0, 0))
    pygame.image.save(pantalla, f"scratch/screenshots/4_seleccion_nivel_{idm}.png")

    # 5. Personalización de Personajes
    pantalla.fill((255, 240, 195))
    pygame.draw.rect(pantalla, (225, 110, 80), pygame.Rect(0, 720 - 80, 1280, 80))

    txt_tit_pj = configuracion.t("personalizacion_personajes")
    f_tit_pj = fuentes.obtener_fuente_para_texto(txt_tit_pj, categoria="titulo", tamano=fuentes.TAMANO_TITULO, negrita=True)
    titulo = f_tit_pj.render(txt_tit_pj, True, (60, 45, 35))
    pantalla.blit(titulo, titulo.get_rect(center=(1280 // 2, 46)))

    txt_sub_pj = configuracion.t("sub_personalizacion")
    f_sub_pj = fuentes.obtener_fuente_para_texto(txt_sub_pj, categoria="subtitulo", tamano=fuentes.TAMANO_SUBTITULO)
    subt = f_sub_pj.render(txt_sub_pj, True, (120, 100, 85))
    pantalla.blit(subt, subt.get_rect(center=(1280 // 2, 78)))

    # Tabs
    rect_tab_col = pygame.Rect(418, 106, 210, 44)
    rect_tab_acc = pygame.Rect(652, 106, 210, 44)
    for tab_id, r_tab, es_activa in [("colores", rect_tab_col, True), ("accesorios", rect_tab_acc, False)]:
        col_tab_bg = (246, 215, 153) if es_activa else (238, 226, 210)
        col_tab_borde = (180, 140, 90) if es_activa else (195, 175, 155)
        pygame.draw.rect(pantalla, col_tab_bg, r_tab, border_radius=12)
        pygame.draw.rect(pantalla, col_tab_borde, r_tab, 3 if es_activa else 2, border_radius=12)
        col_txt = (50, 40, 30) if es_activa else (130, 115, 100)
        txt_tab_str = configuracion.t(tab_id).upper()
        f_tab_str = fuentes.obtener_fuente_para_texto(txt_tab_str, categoria="card_btn", tamano=fuentes.TAMANO_CARD, negrita=True)
        txt_tab = f_tab_str.render(txt_tab_str, True, col_txt)
        pantalla.blit(txt_tab, txt_tab.get_rect(center=r_tab.center))

    # Badges
    r_badge_p1 = pygame.Rect(360 - 130, 164, 260, 34)
    pygame.draw.rect(pantalla, (124, 231, 255), r_badge_p1, border_radius=8)
    pygame.draw.rect(pantalla, (60, 45, 35), r_badge_p1, 2, border_radius=8)
    col_p1_trad = configuracion.t("celeste").upper()
    fuentes.dibujar_texto_en_rect(pantalla, f"{configuracion.t('jugador')} 1  ({col_p1_trad})", r_badge_p1, categoria="boton", tamano=fuentes.TAMANO_BADGE, color=(35, 30, 25), padding=6)

    r_badge_p2 = pygame.Rect(920 - 130, 164, 260, 34)
    pygame.draw.rect(pantalla, (161, 123, 255), r_badge_p2, border_radius=8)
    pygame.draw.rect(pantalla, (60, 45, 35), r_badge_p2, 2, border_radius=8)
    col_p2_trad = configuracion.t("violeta").upper()
    fuentes.dibujar_texto_en_rect(pantalla, f"{configuracion.t('jugador')} 2  ({col_p2_trad})", r_badge_p2, categoria="boton", tamano=fuentes.TAMANO_BADGE, color=(35, 30, 25), padding=6)

    # Frames for options
    for cx in (360, 920):
        rf = pygame.Rect(cx - 235, 295, 470, 276)
        pygame.draw.rect(pantalla, (253, 246, 233), rf, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rf, 3, border_radius=16)
        txt_enc = configuracion.t("colores_disponibles")
        f_enc = fuentes.obtener_fuente_para_texto(txt_enc, categoria="texto", tamano=fuentes.TAMANO_TEXTO, negrita=True)
        t_enc = f_enc.render(txt_enc, True, (115, 95, 80))
        pantalla.blit(t_enc, t_enc.get_rect(center=(rf.centerx, rf.top + 20)))

    # Botón Volver al menú
    btn_volver_pj = pygame.Rect(530, 640, 220, 52)
    spr_vpj = get_volver_button(idm, 220, 52)
    pantalla.blit(spr_vpj, btn_volver_pj)
    pygame.image.save(pantalla, f"scratch/screenshots/5_personalizacion_{idm}.png")

    # 6. Modal Guardar y Salir
    pantalla.fill((40, 40, 40))
    rect_card_m = pygame.Rect((1280 - 560) // 2, (720 - 480) // 2, 560, 480)
    pygame.draw.rect(pantalla, (253, 246, 233), rect_card_m, border_radius=18)
    pygame.draw.rect(pantalla, (195, 168, 138), rect_card_m, width=3, border_radius=18)

    fuente_tit_m = fuentes.obtener_fuente_para_texto(configuracion.t("deseas_guardar"), categoria="dialogos", tamano=fuentes.TAMANO_TITULO_MODAL, negrita=True)
    t_tit_m = fuente_tit_m.render(configuracion.t("deseas_guardar"), True, (60, 45, 35))
    pantalla.blit(t_tit_m, t_tit_m.get_rect(center=(rect_card_m.centerx, rect_card_m.top + 36)))

    btn_g = pygame.Rect(rect_card_m.centerx - 136, rect_card_m.top + 140, 272, 80)
    btn_s = pygame.Rect(rect_card_m.centerx - 136, rect_card_m.top + 234, 272, 80)
    btn_c = pygame.Rect(rect_card_m.centerx - 136, rect_card_m.top + 328, 272, 80)

    if idm == "es":
        spr_gm = sprites.cargar_boton_escalado("Ventanas/boton-guardar-y-salir.png", 272, 80)
        spr_sm = sprites.cargar_boton_escalado("Ventanas/boton-salir-sin-guardar.png", 272, 80)
        spr_cm = sprites.cargar_boton_escalado("Menu/boton-cancelar.png", 272, 80)
    else:
        spr_gm = sprites.generar_boton_con_texto("Ventanas/boton-guardar-y-salir.png", 272, 80, configuracion.t("guardar_salir"), (255, 255, 255), fuentes.TAMANO_BOTON_MODAL)
        spr_sm = sprites.generar_boton_con_texto("Ventanas/boton-salir-sin-guardar.png", 272, 80, configuracion.t("salir_sin_guardar"), (255, 255, 255), fuentes.TAMANO_BOTON_MODAL)
        spr_cm = sprites.generar_boton_con_texto("Menu/boton-cancelar.png", 272, 80, configuracion.t("cancelar"), (60, 45, 35), fuentes.TAMANO_BOTON_MODAL)
    pantalla.blit(spr_gm, btn_g)
    pantalla.blit(spr_sm, btn_s)
    pantalla.blit(spr_cm, btn_c)
    pygame.image.save(pantalla, f"scratch/screenshots/6_guardar_salir_modal_{idm}.png")

print("All screenshots generated successfully.")
