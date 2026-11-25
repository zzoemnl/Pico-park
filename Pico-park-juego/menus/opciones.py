"""
Configuración: volumen, idioma, música y controles.
"""
import pygame
import math as _math
import random as _random
from configuracion import (
    cambiar_idioma,
    cambiar_volumen,
    fijar_modo_musica_menu,
    fijar_volumen,
    obtener_idioma,
    obtener_modo_musica_menu,
    obtener_volumen,
    reproducir_beep_volumen,
    reproducir_sonido_ui,
    t,
)
from fuentes import (
    TAMANO_BOTONES,
    TAMANO_SUBTITULO,
    TAMANO_TITULO,
    contiene_caracteres_cjk,
    dibujar_texto_en_rect,
    obtener_fuente_para_texto,
)
from menus.comunes import ESTADO_MENU_PRINCIPAL, _dibujar_icono_tecla, _obtener_icono_instruccion
from sprites import (
    animar_pulsacion_boton,
    cargar_sprites,
    dibujar_accesorio_en_personaje,
    escalar_cacheado,
    renderizar_texto_pixamuse,
)


_fondo_opciones_cache: "pygame.Surface | None" = None


_copos_opciones: list[dict] = []


def _generar_fondo_opciones(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    """
    Paisaje invernal pixel art con montañas nevadas, árboles de invierno y cielo nocturno
    estrellado con luna suave para la pantalla completa de «OPCIONES».
    """
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. Cielo nocturno invernal profundo
    bandas = [
        (0,   60,  (12, 16, 32)),   # Azul medianoche oscuro
        (60,  130, (20, 28, 54)),   # Azul zafiro profundo
        (130, 200, (32, 45, 78)),   # Azul frío
        (200, 255, (48, 64, 102)),  # Azul noche boreal tenue
        (255, 300, (68, 86, 124)),  # Brillo frío sobre montañas
    ]
    for y1, y2, col in bandas:
        pygame.draw.rect(surf, col, (0, y1, W, y2 - y1))

    for i in range(len(bandas) - 1):
        yt = bandas[i][1]
        c1, c2 = bandas[i][2], bandas[i+1][2]
        for dy in range(-3, 4):
            y = yt + dy
            if 0 <= y < H:
                for x in range(W):
                    if dy == -3 and (x % 4 == 0 and y % 4 == 0): surf.set_at((x, y), c2)
                    elif dy == -2 and (x + y) % 4 == 0: surf.set_at((x, y), c2)
                    elif dy == -1 and (x % 2 == 0 and y % 2 == 0): surf.set_at((x, y), c2)
                    elif dy == 0 and (x + y) % 2 == 0: surf.set_at((x, y), c2)
                    elif dy == 1 and (x % 2 == 0 and y % 2 == 0): surf.set_at((x, y), c1)
                    elif dy == 2 and (x + y) % 4 == 0: surf.set_at((x, y), c1)
                    elif dy == 3 and (x % 4 == 0 and y % 4 == 0): surf.set_at((x, y), c1)

    # 2. Estrellas nocturnas
    rnd = _random.Random(4242)
    for _ in range(65):
        sx = rnd.randint(10, W - 10)
        sy = rnd.randint(6, 190)
        alpha = rnd.choice([(255, 255, 255), (200, 220, 255), (230, 240, 255), (170, 190, 230)])
        surf.set_at((sx, sy), alpha)
        if rnd.random() < 0.15:
            surf.set_at((sx + 1, sy), (180, 205, 240))
            surf.set_at((sx - 1, sy), (180, 205, 240))
            surf.set_at((sx, sy + 1), (180, 205, 240))
            surf.set_at((sx, sy - 1), (180, 205, 240))

    # Luna invernal suave
    mx, my, mr = 540, 55, 20
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            d2 = dx * dx + dy * dy
            if d2 <= mr * mr:
                surf.set_at((mx + dx, my + dy), (245, 248, 255))
            elif d2 <= (mr + 3) * (mr + 3):
                surf.set_at((mx + dx, my + dy), (120, 150, 200))

    # 3. Montañas lejanas nevadas
    def mnt(x, seed, h_base, amp):
        return h_base - int(amp * _math.sin(x * 0.008 + seed) + amp * 0.5 * _math.sin(x * 0.021 + seed * 2))

    for x in range(W):
        y_m1 = mnt(x, 12, 225, 45)
        for y in range(y_m1, 280):
            surf.set_at((x, y), (195, 215, 240) if y < y_m1 + 18 else (55, 70, 105))

    for x in range(W):
        y_m2 = mnt(x, 77, 245, 38)
        for y in range(y_m2, 310):
            surf.set_at((x, y), (225, 238, 255) if y < y_m2 + 15 else (38, 52, 85))

    # 4. Colinas nevadas en primer plano
    for x in range(W):
        y_col = 285 + int(12 * _math.sin(x * 0.015))
        for y in range(y_col, H):
            prog = (y - y_col) / max(1, H - y_col)
            if prog < 0.2:
                col = (235, 242, 255)
            elif prog < 0.6:
                col = (210, 225, 248) if (x + y) % 2 == 0 else (185, 205, 235)
            else:
                col = (160, 182, 215)
            surf.set_at((x, y), col)

    # 5. Pinos nevados en los laterales
    def pino_nevado(cx, by, alt, anc):
        for y in range(by - alt, by):
            prog = (y - (by - alt)) / alt
            w_act = int(anc * prog)
            for dx in range(-w_act // 2, w_act // 2 + 1):
                px = cx + dx
                if 0 <= px < W and 0 <= y < H:
                    if dx == -w_act // 2 or dx == w_act // 2 or (y % 6 in (0, 1)):
                        surf.set_at((px, y), (230, 240, 255))
                    else:
                        surf.set_at((px, y), (24, 48, 42))

    pino_nevado(30, 310, 85, 32)
    pino_nevado(65, 320, 95, 38)
    pino_nevado(100, 335, 75, 30)
    pino_nevado(610, 310, 85, 32)
    pino_nevado(575, 320, 95, 38)
    pino_nevado(540, 335, 75, 30)

    return pygame.transform.scale(surf, (ancho, alto))


def _obtener_fondo_opciones(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_opciones_cache
    if _fondo_opciones_cache is None:
        _fondo_opciones_cache = _generar_fondo_opciones(ancho, alto)
    return _fondo_opciones_cache


def _init_copos_opciones(ancho: int = 1280, alto: int = 720) -> None:
    global _copos_opciones
    rnd = _random.Random(1337)
    _copos_opciones = [
        {
            "x": rnd.uniform(0, ancho),
            "y": rnd.uniform(0, alto),
            "vy": rnd.uniform(0.5, 1.4),
            "vx": rnd.uniform(-0.3, 0.3),
            "r": rnd.choice([1, 2, 2, 3]),
            "alpha": rnd.randint(120, 210),
        }
        for _ in range(45)
    ]


def _dibujar_copos_opciones(pantalla: "pygame.Surface") -> None:
    global _copos_opciones
    if not _copos_opciones:
        _init_copos_opciones(pantalla.get_width(), pantalla.get_height())
    w, h = pantalla.get_size()
    for c in _copos_opciones:
        c["x"] += c["vx"]
        c["y"] += c["vy"]
        if c["y"] > h:
            c["y"] = -4
            c["x"] = _random.uniform(0, w)
        if c["x"] < 0:
            c["x"] = w
        elif c["x"] > w:
            c["x"] = 0
        r = c["r"]
        surf_c = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf_c, (235, 245, 255, c["alpha"]), (r, r), r)
        pantalla.blit(surf_c, (int(c["x"]) - r, int(c["y"]) - r))


def _eventos_configuracion(m, evento):
    """Clic izquierdo en la pantalla «configuracion». Devuelve True si hay que cortar el resto de eventos del frame."""
    m.idm_act = obtener_idioma()
    if m.btn_volver_config.collidepoint(evento.pos):
        m.sp_v_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_v_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_v_n = m._obtener_boton_volver("normal", m.idm_act)
        m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_config, m.sp_v_s, m.sp_v_a, _obtener_fondo_opciones(m.ANCHO_MENU, m.ALTO_MENU), m.sp_v_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MENU_PRINCIPAL
    elif m.rect_btn_sec_cfg.collidepoint(evento.pos):
        if m.seccion_opciones_actual != "configuracion":
            reproducir_sonido_ui("tab")
        m.seccion_opciones_actual = "configuracion"
    elif m.rect_btn_sec_ctrl.collidepoint(evento.pos):
        if m.seccion_opciones_actual != "controles":
            reproducir_sonido_ui("tab")
        m.seccion_opciones_actual = "controles"
    elif m.rect_btn_sec_inst.collidepoint(evento.pos):
        if m.seccion_opciones_actual != "instrucciones":
            reproducir_sonido_ui("tab")
        m.seccion_opciones_actual = "instrucciones"
    elif m.seccion_opciones_actual == "configuracion":
        m.rect_panel_ev = pygame.Rect(340, 115, 875, 495)
        m.y_vol_ev = m.rect_panel_ev.top + 60
        m.r_card_vol_ev = pygame.Rect(m.rect_panel_ev.left + 45, m.y_vol_ev + 24, m.rect_panel_ev.width - 90, 72)
        m.cy_v_ev = m.r_card_vol_ev.centery
        m.r_menos_ev = pygame.Rect(m.r_card_vol_ev.left + 25, m.cy_v_ev - 22, 50, 44)
        m.r_barra_bg_ev = pygame.Rect(m.r_menos_ev.right + 20, m.cy_v_ev - 18, 460, 36)
        m.r_mas_ev = pygame.Rect(m.r_barra_bg_ev.right + 20, m.cy_v_ev - 22, 50, 44)

        m.y_idioma_ev = m.r_card_vol_ev.bottom + 12
        m.r_card_idm_ev = pygame.Rect(m.rect_panel_ev.left + 45, m.y_idioma_ev + 24, m.rect_panel_ev.width - 90, 94)
        m.w_btn_l_ev = (m.r_card_idm_ev.width - 60) // 3
        m.r_bl_es = pygame.Rect(m.r_card_idm_ev.left + 20, m.r_card_idm_ev.top + 11, m.w_btn_l_ev, 72)
        m.r_bl_en = pygame.Rect(m.r_card_idm_ev.left + 20 + (m.w_btn_l_ev + 10), m.r_card_idm_ev.top + 11, m.w_btn_l_ev, 72)
        m.r_bl_zh = pygame.Rect(m.r_card_idm_ev.left + 20 + 2 * (m.w_btn_l_ev + 10), m.r_card_idm_ev.top + 11, m.w_btn_l_ev, 72)

        m.y_musica_ev = m.r_card_idm_ev.bottom + 12
        m.r_card_mus_ev = pygame.Rect(m.rect_panel_ev.left + 45, m.y_musica_ev + 24, m.rect_panel_ev.width - 90, 102)
        m.w_btn_m_ev = (m.r_card_mus_ev.width - 60) // 3
        m.r_bm_rnd = pygame.Rect(m.r_card_mus_ev.left + 20, m.r_card_mus_ev.top + 10, m.w_btn_m_ev, 82)
        m.r_bm_cai = pygame.Rect(m.r_card_mus_ev.left + 20 + (m.w_btn_m_ev + 10), m.r_card_mus_ev.top + 10, m.w_btn_m_ev, 82)
        m.r_bm_chr = pygame.Rect(m.r_card_mus_ev.left + 20 + 2 * (m.w_btn_m_ev + 10), m.r_card_mus_ev.top + 10, m.w_btn_m_ev, 82)

        if m.r_menos_ev.collidepoint(evento.pos):
            cambiar_volumen(-10)
            reproducir_beep_volumen()
        elif m.r_mas_ev.collidepoint(evento.pos):
            cambiar_volumen(+10)
            reproducir_beep_volumen()
        elif m.r_barra_bg_ev.collidepoint(evento.pos):
            m.frac = max(0.0, min(1.0, (evento.pos[0] - (m.r_barra_bg_ev.left + 4)) / float(max(1, m.r_barra_bg_ev.width - 8))))
            m.nuevo_vol = int(round(m.frac * 10)) * 10
            fijar_volumen(m.nuevo_vol)
            reproducir_beep_volumen()
        elif m.r_bl_es.collidepoint(evento.pos):
            cambiar_idioma("es")
            reproducir_sonido_ui("select")
        elif m.r_bl_en.collidepoint(evento.pos):
            cambiar_idioma("en")
            reproducir_sonido_ui("select")
        elif m.r_bl_zh.collidepoint(evento.pos):
            cambiar_idioma("zh")
            reproducir_sonido_ui("select")
        elif m.r_bm_rnd.collidepoint(evento.pos):
            fijar_modo_musica_menu("aleatorio")
            reproducir_sonido_ui("select")
        elif m.r_bm_cai.collidepoint(evento.pos):
            fijar_modo_musica_menu("caillou")
            reproducir_sonido_ui("select")
        elif m.r_bm_chr.collidepoint(evento.pos):
            fijar_modo_musica_menu("christmas")
            reproducir_sonido_ui("select")
    return False


def _dibujar_configuracion(m):
    """Dibuja la pantalla «configuracion»."""
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()

    # 1. Fondo de paisaje invernal pixel art con copos de nieve cayendo
    m.pantalla.blit(_obtener_fondo_opciones(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))
    _dibujar_copos_opciones(m.pantalla)

    # 2. Título y Subtítulo
    m.txt_tit = t("opciones").upper()
    m.f_tit = obtener_fuente_para_texto(m.txt_tit, categoria="titulo", tamano=TAMANO_TITULO + 2, negrita=True)
    m.t_tit = m.f_tit.render(m.txt_tit, True, (255, 240, 195))
    t_tit_s = m.f_tit.render(m.txt_tit, True, (15, 20, 35))
    rc_tit = m.t_tit.get_rect(center=(m.ANCHO_MENU // 2, 44))
    m.pantalla.blit(t_tit_s, (rc_tit.x + 2, rc_tit.y + 2))
    m.pantalla.blit(m.t_tit, rc_tit)

    m.txt_sub = t("sub_opciones")
    m.f_sub = obtener_fuente_para_texto(m.txt_sub, categoria="subtitulo", tamano=TAMANO_SUBTITULO - 2)
    m.t_sub = m.f_sub.render(m.txt_sub, True, (215, 230, 255))
    m.pantalla.blit(m.t_sub, m.t_sub.get_rect(center=(m.ANCHO_MENU // 2, 78)))

    # 3. Barra lateral izquierda (3 botones de secciones)
    botones_sec = [
        ("configuracion", t("configuracion").upper(), m.rect_btn_sec_cfg),
        ("controles", t("controles").upper(), m.rect_btn_sec_ctrl),
        ("instrucciones", t("instrucciones").upper(), m.rect_btn_sec_inst),
    ]

    for m.sec_id, m.sec_nom, m.r_b in botones_sec:
        m.es_activa = (m.seccion_opciones_actual == m.sec_id)
        m.hov_b = m.r_b.collidepoint(m.pos_mouse)

        if m.es_activa:
            m.col_bg = (250, 225, 165)
            m.col_brd = (185, 110, 60)
            m.col_txt = (45, 30, 15)
            pygame.draw.rect(m.pantalla, (140, 80, 40), (m.r_b.left, m.r_b.top + 4, m.r_b.width, m.r_b.height), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_bg, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_brd, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), 3, border_radius=12)
            # Indicador rombo / gema
            m.cy_g = m.r_b.centery - 1
            m.pts_gema = [(m.r_b.left + 16, m.cy_g), (m.r_b.left + 22, m.cy_g - 6), (m.r_b.left + 28, m.cy_g), (m.r_b.left + 22, m.cy_g + 6)]
            pygame.draw.polygon(m.pantalla, (225, 110, 80), m.pts_gema)
            pygame.draw.polygon(m.pantalla, (150, 60, 30), m.pts_gema, 1)
        else:
            m.col_bg = (38, 52, 82) if m.hov_b else (28, 38, 62)
            m.col_brd = (110, 140, 185) if m.hov_b else (85, 110, 150)
            m.col_txt = (255, 255, 255) if m.hov_b else (220, 230, 245)
            pygame.draw.rect(m.pantalla, (15, 22, 38), (m.r_b.left, m.r_b.top + 4, m.r_b.width, m.r_b.height), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_bg, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_brd, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), 2, border_radius=12)

        m.r_txt_b = pygame.Rect(m.r_b.left + (36 if m.es_activa else 12), m.r_b.top, m.r_b.width - (44 if m.es_activa else 24), m.r_b.height - 2)
        dibujar_texto_en_rect(m.pantalla, m.sec_nom, m.r_txt_b, categoria="boton", tamano=15, color=m.col_txt, negrita=True, alineacion="centro")

    # Personajes decorativos en la barra lateral izquierda
    cx_dec, cy_dec = 190, 430
    pygame.draw.ellipse(m.pantalla, (220, 235, 255), (cx_dec - 80, cy_dec + 45, 160, 24))
    sp_p1_d = cargar_sprites(m.color_p1).get("quieto")
    sp_p2_d = cargar_sprites(m.color_p2).get("quieto")
    r_mini_p1 = pygame.Rect(cx_dec - 55, cy_dec, 50, 62)
    r_mini_p2 = pygame.Rect(cx_dec + 5, cy_dec, 50, 62)
    if sp_p1_d:
        m.pantalla.blit(escalar_cacheado(sp_p1_d, (50, 62)), r_mini_p1)
        if m.accesorio_p1:
            dibujar_accesorio_en_personaje(m.pantalla, m.accesorio_p1, sprite_personaje=sp_p1_d, rect_personaje=r_mini_p1, mirando_derecha=True)
    if sp_p2_d:
        m.pantalla.blit(escalar_cacheado(sp_p2_d, (50, 62)), r_mini_p2)
        if m.accesorio_p2:
            dibujar_accesorio_en_personaje(m.pantalla, m.accesorio_p2, sprite_personaje=sp_p2_d, rect_personaje=r_mini_p2, mirando_derecha=True)

    # 4. Panel central grande de color crema
    m.rect_panel = pygame.Rect(340, 115, 875, 495)
    # Sombra del panel
    pygame.draw.rect(m.pantalla, (15, 20, 35), (m.rect_panel.left + 5, m.rect_panel.top + 5, m.rect_panel.width, m.rect_panel.height), border_radius=18)
    # Fondo crema
    pygame.draw.rect(m.pantalla, (253, 248, 238), m.rect_panel, border_radius=18)
    # Borde exterior marrón
    pygame.draw.rect(m.pantalla, (115, 75, 48), m.rect_panel, 4, border_radius=18)
    # Borde interior coral
    rect_in = pygame.Rect(m.rect_panel.left + 6, m.rect_panel.top + 6, m.rect_panel.width - 12, m.rect_panel.height - 12)
    pygame.draw.rect(m.pantalla, (225, 115, 85), rect_in, 2, border_radius=14)

    # Cabecera dentro del panel
    nom_seccion = {
        "configuracion": t("ajustes_generales"),
        "controles": t("controles_teclado"),
        "instrucciones": t("guia_juego"),
    }.get(m.seccion_opciones_actual, t("opciones"))

    f_p_tit = obtener_fuente_para_texto(nom_seccion, categoria="titulo", tamano=19, negrita=True)
    t_p_tit = f_p_tit.render(nom_seccion, True, (60, 42, 30))
    m.pantalla.blit(t_p_tit, t_p_tit.get_rect(center=(m.rect_panel.centerx, m.rect_panel.top + 28)))
    # Línea divisoria decorativa
    pygame.draw.line(m.pantalla, (225, 115, 85), (m.rect_panel.left + 35, m.rect_panel.top + 48), (m.rect_panel.right - 35, m.rect_panel.top + 48), 2)
    pygame.draw.circle(m.pantalla, (180, 90, 55), (m.rect_panel.centerx, m.rect_panel.top + 48), 4)

    # =========================================================================
    # SECCIÓN: CONFIGURACIÓN
    # =========================================================================
    if m.seccion_opciones_actual == "configuracion":
        # Bloque A: Volumen
        m.y_vol = m.rect_panel.top + 60
        m.txt_vol_b = t("volumen_musica_y_sonido")
        m.f_bloq = obtener_fuente_para_texto(m.txt_vol_b, categoria="texto", tamano=15, negrita=True)
        m.pantalla.blit(m.f_bloq.render(m.txt_vol_b, True, (65, 45, 32)), (m.rect_panel.left + 45, m.y_vol))

        # Tarjeta contenedora de volumen
        m.r_card_vol = pygame.Rect(m.rect_panel.left + 45, m.y_vol + 24, m.rect_panel.width - 90, 72)
        pygame.draw.rect(m.pantalla, (244, 236, 222), m.r_card_vol, border_radius=12)
        pygame.draw.rect(m.pantalla, (200, 175, 145), m.r_card_vol, 2, border_radius=12)

        m.vol_actual = obtener_volumen()
        m.cy_v = m.r_card_vol.centery

        # Botón [-]
        m.r_menos = pygame.Rect(m.r_card_vol.left + 25, m.cy_v - 22, 50, 44)
        m.hov_m = m.r_menos.collidepoint(m.pos_mouse)
        m.col_bm = (235, 115, 85) if m.hov_m else (215, 105, 75)
        pygame.draw.rect(m.pantalla, m.col_bm, m.r_menos, border_radius=8)
        pygame.draw.rect(m.pantalla, (140, 60, 40), m.r_menos, 2, border_radius=8)
        m.f_btn_v = obtener_fuente_para_texto("-", categoria="boton", tamano=22, negrita=True)
        m.pantalla.blit(m.f_btn_v.render("-", True, (255, 255, 255)), m.f_btn_v.render("-", True, (255, 255, 255)).get_rect(center=m.r_menos.center))

        # Barra de volumen
        m.r_barra_bg = pygame.Rect(m.r_menos.right + 20, m.cy_v - 18, 460, 36)
        pygame.draw.rect(m.pantalla, (40, 46, 62), m.r_barra_bg, border_radius=8)
        pygame.draw.rect(m.pantalla, (150, 160, 185), m.r_barra_bg, 2, border_radius=8)

        # Relleno de la barra (por bloques de 10%)
        m.bloques = m.vol_actual // 10
        m.ancho_bloque = (m.r_barra_bg.width - 8) / 10.0
        for m.b in range(m.bloques):
            m.bx = m.r_barra_bg.left + 4 + int(m.b * m.ancho_bloque)
            m.bw = int(m.ancho_bloque) - 3
            m.col_b = (255, 150, 70) if m.b < 4 else ((255, 195, 65) if m.b < 8 else (255, 225, 95))
            pygame.draw.rect(m.pantalla, m.col_b, (m.bx, m.r_barra_bg.top + 4, m.bw, m.r_barra_bg.height - 8), border_radius=4)

        # Botón [+]
        m.r_mas = pygame.Rect(m.r_barra_bg.right + 20, m.cy_v - 22, 50, 44)
        m.hov_p = m.r_mas.collidepoint(m.pos_mouse)
        m.col_bp = (95, 200, 120) if m.hov_p else (85, 180, 110)
        pygame.draw.rect(m.pantalla, m.col_bp, m.r_mas, border_radius=8)
        pygame.draw.rect(m.pantalla, (45, 120, 65), m.r_mas, 2, border_radius=8)
        m.f_btn_mas = obtener_fuente_para_texto("+", categoria="boton", tamano=20, negrita=True)
        m.pantalla.blit(m.f_btn_mas.render("+", True, (255, 255, 255)), m.f_btn_mas.render("+", True, (255, 255, 255)).get_rect(center=m.r_mas.center))

        # Porcentaje numérico badge
        m.r_pct = pygame.Rect(m.r_mas.right + 20, m.cy_v - 22, 85, 44)
        pygame.draw.rect(m.pantalla, (255, 255, 255), m.r_pct, border_radius=8)
        pygame.draw.rect(m.pantalla, (180, 155, 125), m.r_pct, 2, border_radius=8)
        m.str_pct = f"{m.vol_actual}%"
        m.f_pct = obtener_fuente_para_texto(m.str_pct, categoria="boton", tamano=16, negrita=True)
        m.pantalla.blit(m.f_pct.render(m.str_pct, True, (45, 35, 25)), m.f_pct.render(m.str_pct, True, (45, 35, 25)).get_rect(center=m.r_pct.center))

        # Bloque B: Idioma
        m.y_idioma = m.r_card_vol.bottom + 12
        m.txt_idm_b = t("seleccion_idioma")
        m.pantalla.blit(m.f_bloq.render(m.txt_idm_b, True, (65, 45, 32)), (m.rect_panel.left + 45, m.y_idioma))

        m.r_card_idm = pygame.Rect(m.rect_panel.left + 45, m.y_idioma + 24, m.rect_panel.width - 90, 94)
        pygame.draw.rect(m.pantalla, (244, 236, 222), m.r_card_idm, border_radius=12)
        pygame.draw.rect(m.pantalla, (200, 175, 145), m.r_card_idm, 2, border_radius=12)

        m.langs = [
            ("es", "ESPAÑOL", "Español (Latinoamérica / España)"),
            ("en", "ENGLISH", "English (United States / UK)"),
            ("zh", "中文 (CHINO)", "简体中文 (Simplified Chinese)"),
        ]
        m.w_btn_l = (m.r_card_idm.width - 60) // 3
        for m.l_idx, (m.l_code, m.l_tit, m.l_sub) in enumerate(m.langs):
            m.rx_l = m.r_card_idm.left + 20 + m.l_idx * (m.w_btn_l + 10)
            m.r_bl = pygame.Rect(m.rx_l, m.r_card_idm.top + 11, m.w_btn_l, 72)
            m.es_sel = (m.idm_act == m.l_code)
            m.hov_l = m.r_bl.collidepoint(m.pos_mouse)

            m.col_l_bg = (255, 250, 235) if m.es_sel else ((248, 240, 228) if m.hov_l else (238, 228, 212))
            m.col_l_brd = (225, 110, 80) if m.es_sel else ((205, 180, 150) if m.hov_l else (185, 160, 130))
            pygame.draw.rect(m.pantalla, m.col_l_bg, m.r_bl, border_radius=10)
            pygame.draw.rect(m.pantalla, m.col_l_brd, m.r_bl, 3 if m.es_sel else 2, border_radius=10)

            if m.es_sel:
                m.cx_ck, m.cy_ck = m.r_bl.right - 13, m.r_bl.top + 13
                pygame.draw.circle(m.pantalla, (80, 185, 105), (m.cx_ck, m.cy_ck), 8)
                m.pts_ck = [(m.cx_ck - 4, m.cy_ck), (m.cx_ck - 1, m.cy_ck + 3), (m.cx_ck + 4, m.cy_ck - 3)]
                pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_ck, 2)

            m.col_lt = (45, 30, 20) if m.es_sel else (95, 75, 60)
            if contiene_caracteres_cjk(m.l_tit):
                m.f_lt = obtener_fuente_para_texto(m.l_tit, categoria="boton", tamano=16, negrita=True)
                m.t_lt = m.f_lt.render(m.l_tit, True, m.col_lt)
            else:
                m._, m.t_lt = renderizar_texto_pixamuse(m.l_tit, 15, m.col_lt, max_w=m.r_bl.width - 28)
            m.pantalla.blit(m.t_lt, m.t_lt.get_rect(center=(m.r_bl.centerx, m.r_bl.top + 23)))

            dibujar_texto_en_rect(m.pantalla, m.l_sub, pygame.Rect(m.r_bl.left + 6, m.r_bl.top + 36, m.r_bl.width - 12, 32), categoria="texto", tamano=12, color=(80, 60, 45), alineacion="centro", multiline=True, interlineado=1)

        # Bloque C: Música del Menú
        m.y_musica = m.r_card_idm.bottom + 12
        m.txt_mus_b = t("musica_menu_titulo")
        m.pantalla.blit(m.f_bloq.render(m.txt_mus_b, True, (65, 45, 32)), (m.rect_panel.left + 45, m.y_musica))

        m.r_card_musica = pygame.Rect(m.rect_panel.left + 45, m.y_musica + 24, m.rect_panel.width - 90, 102)
        pygame.draw.rect(m.pantalla, (244, 236, 222), m.r_card_musica, border_radius=12)
        pygame.draw.rect(m.pantalla, (200, 175, 145), m.r_card_musica, 2, border_radius=12)

        m.modo_musica_act = obtener_modo_musica_menu()
        m.opciones_musica = [
            ("aleatorio", t("modo_aleatorio"), t("desc_aleatorio")),
            ("caillou", t("modo_caillou"), t("desc_caillou")),
            ("christmas", t("modo_christmas"), t("desc_christmas")),
        ]
        m.w_btn_m = (m.r_card_musica.width - 60) // 3
        for m.m_idx, (m.m_code, m.m_tit, m.m_sub) in enumerate(m.opciones_musica):
            m.rx_m = m.r_card_musica.left + 20 + m.m_idx * (m.w_btn_m + 10)
            m.r_bm = pygame.Rect(m.rx_m, m.r_card_musica.top + 10, m.w_btn_m, 82)
            m.es_sel_m = (m.modo_musica_act == m.m_code)
            m.hov_m = m.r_bm.collidepoint(m.pos_mouse)

            m.col_m_bg = (255, 250, 235) if m.es_sel_m else ((248, 240, 228) if m.hov_m else (238, 228, 212))
            m.col_m_brd = (225, 110, 80) if m.es_sel_m else ((205, 180, 150) if m.hov_m else (185, 160, 130))
            pygame.draw.rect(m.pantalla, m.col_m_bg, m.r_bm, border_radius=10)
            pygame.draw.rect(m.pantalla, m.col_m_brd, m.r_bm, 3 if m.es_sel_m else 2, border_radius=10)

            if m.es_sel_m:
                m.cx_ck, m.cy_ck = m.r_bm.right - 13, m.r_bm.top + 13
                pygame.draw.circle(m.pantalla, (80, 185, 105), (m.cx_ck, m.cy_ck), 8)
                m.pts_ck = [(m.cx_ck - 4, m.cy_ck), (m.cx_ck - 1, m.cy_ck + 3), (m.cx_ck + 4, m.cy_ck - 3)]
                pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_ck, 2)

            m.col_mt = (45, 30, 20) if m.es_sel_m else (95, 75, 60)
            if contiene_caracteres_cjk(m.m_tit):
                m.f_mt = obtener_fuente_para_texto(m.m_tit, categoria="boton", tamano=16, negrita=True)
                m.t_mt = m.f_mt.render(m.m_tit, True, m.col_mt)
            else:
                m._, m.t_mt = renderizar_texto_pixamuse(m.m_tit, 15, m.col_mt, max_w=m.r_bm.width - 28)
            m.pantalla.blit(m.t_mt, m.t_mt.get_rect(center=(m.r_bm.centerx, m.r_bm.top + 20)))

            m.r_sub_m = pygame.Rect(m.r_bm.left + 4, m.r_bm.top + 34, m.r_bm.width - 8, 44)
            dibujar_texto_en_rect(m.pantalla, m.m_sub, m.r_sub_m, categoria="texto", tamano=15, color=(80, 60, 45), alineacion="centro", multiline=True, interlineado=2, padding=1)

        # Nota al pie de ajustes (agrandada y más legible con sombra suave)
        m.txt_not = t("cambios_guardados_auto")
        m.f_not = obtener_fuente_para_texto(m.txt_not, categoria="texto", tamano=14, negrita=True)
        m.pantalla.blit(m.f_not.render(m.txt_not, True, (245, 235, 220)), (m.rect_panel.left + 51, m.rect_panel.bottom - 32))
        m.pantalla.blit(m.f_not.render(m.txt_not, True, (55, 38, 25)), (m.rect_panel.left + 50, m.rect_panel.bottom - 33))

    # =========================================================================
    # SECCIÓN: CONTROLES
    # =========================================================================
    elif m.seccion_opciones_actual == "controles":
        m.w_pj_card = (m.rect_panel.width - 60) // 2
        m.h_pj_card = 356
        m.y_pj_top = m.rect_panel.top + 60

        # --- TARJETA JUGADOR 1 ---
        m.r_card_p1 = pygame.Rect(m.rect_panel.left + 22, m.y_pj_top, m.w_pj_card, m.h_pj_card)
        pygame.draw.rect(m.pantalla, (244, 238, 226), m.r_card_p1, border_radius=14)
        pygame.draw.rect(m.pantalla, (124, 210, 240), m.r_card_p1, 3, border_radius=14)

        m.r_head_p1 = pygame.Rect(m.r_card_p1.left + 14, m.r_card_p1.top + 10, m.r_card_p1.width - 28, 34)
        pygame.draw.rect(m.pantalla, (124, 231, 255), m.r_head_p1, border_radius=8)
        pygame.draw.rect(m.pantalla, (50, 40, 30), m.r_head_p1, 2, border_radius=8)
        m.tit_head_p1 = f"{t('jugador_1').upper()}  (WASD)"
        dibujar_texto_en_rect(m.pantalla, m.tit_head_p1, m.r_head_p1, categoria="boton", tamano=16, color=(35, 30, 25), negrita=True, padding=2)

        m.filas_p1 = [
            (t("accion_moverse"), ["A", "D"], t("desc_moverse")),
            (t("accion_saltar"), ["W"], t("desc_saltar")),
            (t("accion_nadar"), ["W", "S"], t("desc_nadar_p1")),
            (t("accion_empujar"), ["A", "D"], t("desc_empujar")),
            (t("accion_linterna"), ["E", "F", "ESP"], t("desc_linterna")),
        ]
        for m.f_idx, (m.accion, m.teclas, m.desc) in enumerate(m.filas_p1):
            m.yf = m.r_card_p1.top + 52 + m.f_idx * 58
            # Línea 1: Nombre de la acción a la izquierda y teclas alineadas a la derecha
            m.f_act = obtener_fuente_para_texto(m.accion, categoria="boton", tamano=15, negrita=True)
            m.pantalla.blit(m.f_act.render(m.accion, True, (45, 32, 20)), (m.r_card_p1.left + 16, m.yf + 3))

            m.xk = m.r_card_p1.right - 14
            for m.tk in reversed(m.teclas):
                m.kw = 56 if len(m.tk) > 2 else 38
                m.xk -= m.kw
                m.rk = pygame.Rect(m.xk, m.yf, m.kw, 30)
                _dibujar_icono_tecla(m.pantalla, m.tk, m.rk, activo=True, tamano_fuente=15)
                m.xk -= 6

            # Línea 2: Texto descriptivo amplio y claro (completamente separado sin superposición)
            m.f_dsc = obtener_fuente_para_texto(m.desc, categoria="texto", tamano=14, negrita=False)
            m.pantalla.blit(m.f_dsc.render(f"• {m.desc}", True, (80, 60, 45)), (m.r_card_p1.left + 16, m.yf + 33))

            if m.f_idx < len(m.filas_p1) - 1:
                pygame.draw.line(m.pantalla, (230, 218, 200), (m.r_card_p1.left + 14, m.yf + 54), (m.r_card_p1.right - 14, m.yf + 54), 1)

        # --- TARJETA JUGADOR 2 ---
        m.r_card_p2 = pygame.Rect(m.r_card_p1.right + 16, m.y_pj_top, m.w_pj_card, m.h_pj_card)
        pygame.draw.rect(m.pantalla, (244, 238, 226), m.r_card_p2, border_radius=14)
        pygame.draw.rect(m.pantalla, (180, 140, 255), m.r_card_p2, 3, border_radius=14)

        m.r_head_p2 = pygame.Rect(m.r_card_p2.left + 14, m.r_card_p2.top + 10, m.r_card_p2.width - 28, 34)
        pygame.draw.rect(m.pantalla, (180, 140, 255), m.r_head_p2, border_radius=8)
        pygame.draw.rect(m.pantalla, (50, 40, 30), m.r_head_p2, 2, border_radius=8)
        m.tit_head_p2 = f"{t('jugador_2').upper()}  ({t('flechas_direccion')})"
        dibujar_texto_en_rect(m.pantalla, m.tit_head_p2, m.r_head_p2, categoria="boton", tamano=16, color=(35, 30, 25), negrita=True, padding=2)

        m.filas_p2 = [
            (t("accion_moverse"), ["←", "→"], t("desc_moverse")),
            (t("accion_saltar"), ["↑"], t("desc_saltar")),
            (t("accion_nadar"), ["↑", "↓"], t("desc_nadar_p2")),
            (t("accion_empujar"), ["←", "→"], t("desc_empujar")),
            (t("accion_linterna"), ["L", "ENT"], t("desc_linterna")),
        ]
        for m.f_idx, (m.accion, m.teclas, m.desc) in enumerate(m.filas_p2):
            m.yf = m.r_card_p2.top + 52 + m.f_idx * 58
            m.f_act = obtener_fuente_para_texto(m.accion, categoria="boton", tamano=15, negrita=True)
            m.pantalla.blit(m.f_act.render(m.accion, True, (45, 32, 20)), (m.r_card_p2.left + 16, m.yf + 3))

            m.xk = m.r_card_p2.right - 14
            for m.tk in reversed(m.teclas):
                m.kw = 56 if len(m.tk) > 2 else 38
                m.xk -= m.kw
                m.rk = pygame.Rect(m.xk, m.yf, m.kw, 30)
                _dibujar_icono_tecla(m.pantalla, m.tk, m.rk, activo=True, tamano_fuente=15)
                m.xk -= 6

            m.f_dsc = obtener_fuente_para_texto(m.desc, categoria="texto", tamano=14, negrita=False)
            m.pantalla.blit(m.f_dsc.render(f"• {m.desc}", True, (80, 60, 45)), (m.r_card_p2.left + 16, m.yf + 33))

            if m.f_idx < len(m.filas_p2) - 1:
                pygame.draw.line(m.pantalla, (230, 218, 200), (m.r_card_p2.left + 14, m.yf + 54), (m.r_card_p2.right - 14, m.yf + 54), 1)

        # Fila inferior: Tecla R y Menú ESC (Agrandadas y legibles)
        m.r_inf_ctrl = pygame.Rect(m.rect_panel.left + 22, m.r_card_p1.bottom + 10, m.rect_panel.width - 44, 52)
        pygame.draw.rect(m.pantalla, (238, 230, 215), m.r_inf_ctrl, border_radius=10)
        pygame.draw.rect(m.pantalla, (195, 170, 140), m.r_inf_ctrl, 2, border_radius=10)

        m.rk_r = pygame.Rect(m.r_inf_ctrl.left + 18, m.r_inf_ctrl.top + 9, 42, 34)
        _dibujar_icono_tecla(m.pantalla, "R", m.rk_r, activo=False, tamano_fuente=16)
        m.txt_r = t("reiniciar_nivel_act")
        m.f_r = obtener_fuente_para_texto(m.txt_r, categoria="texto", tamano=15, negrita=True)
        m.pantalla.blit(m.f_r.render(m.txt_r, True, (55, 40, 30)), (m.rk_r.right + 12, m.r_inf_ctrl.top + 16))

        m.rk_esc = pygame.Rect(m.r_inf_ctrl.centerx + 20, m.r_inf_ctrl.top + 9, 58, 34)
        _dibujar_icono_tecla(m.pantalla, "ESC", m.rk_esc, activo=False, tamano_fuente=16)
        m.txt_esc = t("pausa_volver_menu")
        m.f_esc = obtener_fuente_para_texto(m.txt_esc, categoria="texto", tamano=15, negrita=True)
        m.pantalla.blit(m.f_esc.render(m.txt_esc, True, (55, 40, 30)), (m.rk_esc.right + 12, m.r_inf_ctrl.top + 16))

    # =========================================================================
    # SECCIÓN: INSTRUCCIONES
    # =========================================================================
    elif m.seccion_opciones_actual == "instrucciones":
        m.w_c = (m.rect_panel.width - 60) // 2
        m.h_c = 202

        m.tarjetas_inst = [
            (
                t("inst_tit_1"),
                [
                    t("inst_1_1"),
                    t("inst_1_2"),
                    t("inst_1_3"),
                    t("inst_1_4"),
                ],
                "llave_puerta"
            ),
            (
                t("inst_tit_2"),
                [
                    t("inst_2_1"),
                    t("inst_2_2"),
                    t("inst_2_3"),
                    t("inst_2_4"),
                ],
                "caja_boton"
            ),
            (
                t("inst_tit_3"),
                [
                    t("inst_3_1"),
                    t("inst_3_2"),
                    t("inst_3_3"),
                    t("inst_3_4"),
                ],
                "soga_salto"
            ),
            (
                t("inst_tit_4"),
                [
                    t("inst_4_1"),
                    t("inst_4_2"),
                    t("inst_4_3"),
                    t("inst_4_4"),
                ],
                "submarino"
            ),
        ]

        for m.idx_t, (m.tit_t, m.lines_t, m.tipo_ico) in enumerate(m.tarjetas_inst):
            m.col_idx = m.idx_t % 2
            m.row_idx = m.idx_t // 2
            m.x_tc = m.rect_panel.left + 20 + m.col_idx * (m.w_c + 20)
            m.y_tc = m.rect_panel.top + 58 + m.row_idx * (m.h_c + 12)
            m.rtc = pygame.Rect(m.x_tc, m.y_tc, m.w_c, m.h_c)

            pygame.draw.rect(m.pantalla, (246, 240, 228), m.rtc, border_radius=12)
            pygame.draw.rect(m.pantalla, (215, 175, 140), m.rtc, 2, border_radius=12)

            # Encabezado con título centrado y multilínea para que nunca se desborde
            m.r_head_t = pygame.Rect(m.rtc.left + 8, m.rtc.top + 8, m.rtc.width - 16, 36)
            pygame.draw.rect(m.pantalla, (235, 218, 195), m.r_head_t, border_radius=6)
            dibujar_texto_en_rect(m.pantalla, m.tit_t, m.r_head_t, categoria="boton", tamano=13, color=(55, 38, 25), negrita=True, multiline=True, padding=2, alineacion="centro")

            # Recuadro de ilustración con los sprites reales del juego
            m.r_box_ico = pygame.Rect(m.rtc.right - 56, m.rtc.top + 46, 48, 48)
            pygame.draw.rect(m.pantalla, (232, 222, 205), m.r_box_ico, border_radius=8)
            pygame.draw.rect(m.pantalla, (180, 150, 120), m.r_box_ico, 1, border_radius=8)

            m.cx_i, m.cy_i = m.r_box_ico.center
            if m.tipo_ico == "llave_puerta":
                m.spr_ico = _obtener_icono_instruccion("llave", 40, 44)
                if m.spr_ico:
                    m.pantalla.blit(m.spr_ico, m.spr_ico.get_rect(center=m.r_box_ico.center))
            elif m.tipo_ico == "caja_boton":
                m.spr_ico = _obtener_icono_instruccion("caja", 44, 42)
                if m.spr_ico:
                    m.pantalla.blit(m.spr_ico, m.spr_ico.get_rect(center=m.r_box_ico.center))
            elif m.tipo_ico == "soga_salto":
                m.pts_soga = [(m.cx_i - 15, m.cy_i - 8), (m.cx_i - 5, m.cy_i + 8), (m.cx_i + 5, m.cy_i - 6), (m.cx_i + 15, m.cy_i + 8)]
                pygame.draw.lines(m.pantalla, (160, 110, 60), False, m.pts_soga, 3)
                pygame.draw.circle(m.pantalla, (124, 231, 255), (m.cx_i - 13, m.cy_i - 8), 5)
                pygame.draw.circle(m.pantalla, (180, 140, 255), (m.cx_i + 13, m.cy_i + 8), 5)
            elif m.tipo_ico == "submarino":
                m.spr_ico = _obtener_icono_instruccion("buceo", 44, 40)
                if m.spr_ico:
                    m.pantalla.blit(m.spr_ico, m.spr_ico.get_rect(center=m.r_box_ico.center))

            for m.l_num, m.line_txt in enumerate(m.lines_t):
                m.yf_l = m.rtc.top + 50 + m.l_num * 36
                m.bx = m.rtc.left + 14
                m.by = m.yf_l + 6
                pygame.draw.rect(m.pantalla, (215, 175, 140), (m.bx + 1, m.by + 1, 4, 4))
                pygame.draw.rect(m.pantalla, (65, 45, 30), (m.bx, m.by, 4, 4))

                m.clean_txt = m.line_txt.lstrip("•- \t")
                m.f_lin = obtener_fuente_para_texto(m.clean_txt, categoria="dialogos", tamano=18, negrita=True)
                m.ts_lin = m.f_lin.render(m.clean_txt, True, (45, 32, 20))
                m.pantalla.blit(m.ts_lin, (m.rtc.left + 24, m.yf_l))
                m.pantalla.blit(m.ts_lin, (m.rtc.left + 25, m.yf_l))

    # 5. Botón Volver al Menú (mundos/boton-volver)
    hov_vcfg = m.btn_volver_config.collidepoint(m.pos_mouse)
    spr_vcfg_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vcfg_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vcfg = spr_vcfg_hov if (hov_vcfg and spr_vcfg_hov) else spr_vcfg_norm
    if spr_vcfg:
        m.pantalla.blit(spr_vcfg, m.btn_volver_config)
    else:
        m.col_v = (255, 255, 255) if hov_vcfg else (242, 234, 222)
        pygame.draw.rect(m.pantalla, m.col_v, m.btn_volver_config, border_radius=10)
        pygame.draw.rect(m.pantalla, (185, 155, 125), m.btn_volver_config, width=2, border_radius=10)
        dibujar_texto_en_rect(m.pantalla, t("volver_al_menu"), m.btn_volver_config, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)
