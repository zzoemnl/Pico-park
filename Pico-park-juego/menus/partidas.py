"""
Lista de partidas guardadas: tarjetas, geometría, fondo y acciones (cargar, gestionar, borrar).
"""
import pygame
import copy
import math as _math
import random as _random
from configuracion import (
    obtener_idioma,
    reproducir_musica,
    reproducir_sonido_ui,
    seleccionar_musica_menu_aleatoria,
    t,
)
from fuentes import (
    TAMANO_BADGE,
    TAMANO_BOTONES,
    TAMANO_CONTADOR,
    TAMANO_DECORATIVA,
    TAMANO_SUBTITULO,
    TAMANO_TITULO,
    contiene_caracteres_cjk,
    dibujar_texto_en_rect,
    obtener_fuente_cjk,
    obtener_fuente_para_texto,
    obtener_fuente_pequena,
)
from guardado import TOTAL_NIVELES_ADMIN, TOTAL_NIVELES_NORMALES, calcular_niveles_completados, cargar_partidas, crear_desbloqueados_inicial, eliminar_partida, es_partida_admin, guardar_partida, obtener_nombre_partida_visible
from menus.dialogos import flujo_crear_nueva_partida, modal_administrar_perfil, mostrar_dialogo_confirmar_atuendos, mostrar_dialogo_confirmar_borrado, pedir_password_modal
from menu_niveles import COLORES_TABS
from menus.comunes import (
    ESTADO_MODO_JUEGO,
    ESTADO_SELECCION_NIVEL,
    _dibujar_icono_calendario,
    _dibujar_icono_candado,
    _dibujar_icono_estrella_nivel,
    _dibujar_icono_reloj,
    _dibujar_icono_trofeo,
)
from menus.seleccion_nivel import jugar_niveles_desde
from sprites import animar_pulsacion_boton


_fondo_partidas_cache: "pygame.Surface | None" = None


def _generar_fondo_partidas(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    """
    Fondo pixel art estilo Diario de Aventuras / Registro de Expediciones.
    - Tonos cálidos pergamino: crema, beige, avellana, toques dorados y detalles sutiles de atardecer.
    - Textura de papel envejecido y bordes desgastados.
    - Bocetos discretos de mapa y expedición: montañas en tinta sepia, rosa de los vientos/brújula,
      rutas punteadas, pequeños árboles y estrellas de navegación.
    - Cantoneras de cuero y latón en las esquinas.
    """
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. Base pergamino con gradiente cálido vertical y leve curvatura de tomo abierto
    col_centro = (246, 236, 214)
    col_extremo = (226, 206, 172)
    for y in range(H):
        t_y = y / H
        for x in range(W):
            t_x = abs(x - W / 2) / (W / 2)
            t_diag = (t_x * 0.6 + t_y * 0.4)
            r = int(col_centro[0] * (1 - t_diag) + col_extremo[0] * t_diag)
            g = int(col_centro[1] * (1 - t_diag) + col_extremo[1] * t_diag)
            b = int(col_centro[2] * (1 - t_diag) + col_extremo[2] * t_diag)
            surf.set_at((x, y), (r, g, b))

    # 2. Textura sutil de papel antiguo (grano fino de fibra vegetal)
    rnd_fibra = _random.Random(1842)
    for _ in range(3500):
        fx = rnd_fibra.randint(0, W - 1)
        fy = rnd_fibra.randint(0, H - 1)
        c_orig = surf.get_at((fx, fy))
        delta = rnd_fibra.choice([-7, -4, 4, 6])
        surf.set_at((fx, fy), (
            max(0, min(255, c_orig.r + delta)),
            max(0, min(255, c_orig.g + delta)),
            max(0, min(255, c_orig.b + delta)),
        ))

    # 3. Bordes envejecidos / efecto papel quemado y biselado
    for b in range(12):
        factor_osc = 1.0 - (b / 12.0) * 0.45
        for x in range(b, W - b):
            # Arriba y abajo
            for y_b in (b, H - 1 - b):
                c = surf.get_at((x, y_b))
                surf.set_at((x, y_b), (int(c.r * factor_osc), int(c.g * factor_osc), int(c.b * factor_osc)))
        for y in range(b, H - b):
            # Izquierda y derecha
            for x_b in (b, W - 1 - b):
                c = surf.get_at((x_b, y))
                surf.set_at((x_b, y), (int(c.r * factor_osc), int(c.g * factor_osc), int(c.b * factor_osc)))

    # Línea de encuadre perimetral interior en tinta sepia tenue
    m_int = 14
    col_marco_int = (185, 155, 120)
    col_marco_fino = (215, 192, 160)
    pygame.draw.rect(surf, col_marco_int, (m_int, m_int, W - m_int * 2, H - m_int * 2), width=2)
    pygame.draw.rect(surf, col_marco_fino, (m_int + 3, m_int + 3, W - (m_int + 3) * 2, H - (m_int + 3) * 2), width=1)

    # 4. Líneas guía muy sutiles de cuaderno/diario
    col_pauta = (212, 195, 168)
    for y in range(54, H - 30, 24):
        for x in range(m_int + 8, W - m_int - 8, 4):
            surf.set_at((x, y), col_pauta)

    # 5. Bocetos ilustrados discretos en tinta sepia (Montañas estilo cartografía)
    col_tinta_mont = (150, 115, 80)
    col_tinta_clara = (190, 160, 125)

    def _dibujar_montana_boceto(cx, base_y, ancho, alto):
        mitad = ancho // 2
        for dy in range(alto):
            y_cur = base_y - dy
            prog = dy / max(1, alto)
            w_act = int(mitad * (1.0 - prog))
            x_izq = cx - w_act
            x_der = cx + w_act
            if 0 <= y_cur < H:
                if 0 <= x_izq < W:
                    surf.set_at((x_izq, y_cur), col_tinta_mont)
                if 0 <= x_der < W:
                    surf.set_at((x_der, y_cur), col_tinta_mont)
                # Sombreado rayado en la ladera este
                for sx in range(cx, x_der):
                    if (sx + y_cur) % 3 == 0 and 0 <= sx < W:
                        surf.set_at((sx, y_cur), col_tinta_clara)
        for dy in range(alto):
            y_cur = base_y - dy
            c_offset = int(_math.sin(dy * 0.25) * 2)
            if 0 <= cx + c_offset < W and 0 <= y_cur < H:
                surf.set_at((cx + c_offset, y_cur), col_tinta_mont)

    # Grupo de montañas en el margen izquierdo
    _dibujar_montana_boceto(48, 120, 42, 32)
    _dibujar_montana_boceto(76, 128, 50, 40)
    _dibujar_montana_boceto(108, 134, 38, 28)

    # Pequeño macizo en el margen derecho inferior
    _dibujar_montana_boceto(585, 305, 46, 36)
    _dibujar_montana_boceto(555, 312, 38, 26)

    # 6. Pequeños pinos/árboles en tinta sepia en los márgenes
    def _dibujar_arbolito_tinta(tx, ty):
        if not (0 <= tx < W and 0 <= ty < H - 12):
            return
        for dy in range(4):
            surf.set_at((tx, ty + 8 + dy), col_tinta_mont)
        for r_fila in range(4):
            y_f = ty + r_fila * 2
            ancho_f = r_fila + 1
            for dx in range(-ancho_f, ancho_f + 1):
                if 0 <= tx + dx < W and 0 <= y_f < H:
                    surf.set_at((tx + dx, y_f), col_tinta_mont)

    for ax, ay in [(32, 130), (42, 138), (62, 142), (92, 145), (120, 148), (530, 318), (542, 322), (610, 315)]:
        _dibujar_arbolito_tinta(ax, ay)

    # 7. Brújula / Rosa de los vientos ilustrada en margen superior derecho
    bx, by = 585, 58
    radio_b = 20
    pygame.draw.circle(surf, col_tinta_clara, (bx, by), radio_b, width=1)
    pygame.draw.circle(surf, (218, 172, 70), (bx, by), radio_b - 3, width=1)
    col_aguja_norte = (195, 65, 55)   # Acento coral/terracota aventura
    col_aguja_sur = (75, 95, 125)     # Acento azul expedición
    col_aguja_sepia = col_tinta_mont

    for dy in range(radio_b - 2):
        w_ag = int(3 * (1.0 - dy / (radio_b - 2)))
        for dx in range(-w_ag, w_ag + 1):
            if 0 <= bx + dx < W and 0 <= by - dy < H:
                surf.set_at((bx + dx, by - dy), col_aguja_norte if dx <= 0 else (235, 125, 115))
    for dy in range(radio_b - 2):
        w_ag = int(3 * (1.0 - dy / (radio_b - 2)))
        for dx in range(-w_ag, w_ag + 1):
            if 0 <= bx + dx < W and 0 <= by + dy < H:
                surf.set_at((bx + dx, by + dy), col_aguja_sur if dx <= 0 else (120, 145, 175))
    for dx in range(radio_b - 4):
        w_ag = int(3 * (1.0 - dx / (radio_b - 4)))
        for dy in range(-w_ag, w_ag + 1):
            if 0 <= bx + dx < W and 0 <= by + dy < H:
                surf.set_at((bx + dx, by + dy), col_aguja_sepia)
            if 0 <= bx - dx < W and 0 <= by + dy < H:
                surf.set_at((bx - dx, by + dy), col_aguja_sepia)
    pygame.draw.circle(surf, (235, 195, 80), (bx, by), 3)
    pygame.draw.circle(surf, (110, 65, 30), (bx, by), 3, width=1)

    # 8. Camino de expedición punteado (ruta de viaje en mapa)
    puntos_ruta = [
        (65, 145), (85, 162), (112, 175), (145, 182), (170, 205),
        (190, 240), (200, 280), (215, 315), (240, 335)
    ]
    for i in range(len(puntos_ruta) - 1):
        x1, y1 = puntos_ruta[i]
        x2, y2 = puntos_ruta[i + 1]
        dist = int(_math.hypot(x2 - x1, y2 - y1))
        for step in range(0, dist, 6):
            t = step / max(1, dist)
            px = int(x1 + (x2 - x1) * t)
            py = int(y1 + (y2 - y1) * t)
            if 0 <= px < W and 0 <= py < H:
                surf.set_at((px, py), (175, 110, 65))
                if 0 <= px + 1 < W:
                    surf.set_at((px + 1, py), (175, 110, 65))

    cx_camp, cy_camp = puntos_ruta[4]
    for d_cruz in range(-2, 3):
        if 0 <= cx_camp + d_cruz < W and 0 <= cy_camp + d_cruz < H:
            surf.set_at((cx_camp + d_cruz, cy_camp + d_cruz), (195, 55, 45))
            surf.set_at((cx_camp + d_cruz, cy_camp - d_cruz), (195, 55, 45))

    # 9. Estrellas de orientación tenues en tinta dorada
    estrellas_mapa = [(38, 45), (120, 38), (520, 48), (608, 145), (35, 325), (480, 320)]
    col_estrella = (205, 165, 85)
    for ex, ey in estrellas_mapa:
        if 0 <= ex < W and 0 <= ey < H:
            surf.set_at((ex, ey), col_estrella)
            surf.set_at((ex + 1, ey), col_estrella)
            surf.set_at((ex - 1, ey), col_estrella)
            surf.set_at((ex, ey + 1), col_estrella)
            surf.set_at((ex, ey - 1), col_estrella)

    # 10. Cantoneras de latón / cuero en las 4 esquinas del diario
    tam_cantonera = 22
    col_cant_laton = (195, 155, 65)
    col_cant_sombra = (95, 65, 30)
    col_cant_remache = (245, 215, 115)

    def _dibujar_cantonera(x_origen, y_origen, dir_x, dir_y):
        for dx in range(tam_cantonera):
            for dy in range(tam_cantonera):
                if dx + dy < tam_cantonera:
                    x = x_origen + dx * dir_x
                    y = y_origen + dy * dir_y
                    if 0 <= x < W and 0 <= y < H:
                        if dx + dy == tam_cantonera - 1 or dx == 0 or dy == 0:
                            surf.set_at((x, y), col_cant_sombra)
                        elif dx + dy < tam_cantonera - 3:
                            surf.set_at((x, y), col_cant_laton)
                        else:
                            surf.set_at((x, y), (145, 110, 48))
        rx = x_origen + 7 * dir_x
        ry = y_origen + 7 * dir_y
        if 0 <= rx < W and 0 <= ry < H:
            surf.set_at((rx, ry), col_cant_remache)
            surf.set_at((rx + dir_x, ry), col_cant_sombra)

    _dibujar_cantonera(4, 4, 1, 1)
    _dibujar_cantonera(W - 5, 4, -1, 1)
    _dibujar_cantonera(4, H - 5, 1, -1)
    _dibujar_cantonera(W - 5, H - 5, -1, -1)

    # 11. Escalar a resolución final
    surf_final = pygame.transform.scale(surf, (ancho, alto))
    return surf_final


def _obtener_fondo_partidas(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_partidas_cache
    if _fondo_partidas_cache is None:
        _fondo_partidas_cache = _generar_fondo_partidas(ancho, alto)
    return _fondo_partidas_cache


def obtener_geometria_panel_partidas(ancho_menu, alto_menu, tiene_partidas=True):
    """
    Calcula dinámicamente las dimensiones y posiciones del panel y botones
    de la pantalla de partidas guardadas adaptadas al formato Diario de Aventuras.
    Garantiza que «VOLVER» y «NUEVA PARTIDA» queden perfectamente centrados juntos
    y sin colisión vertical con la paginación ni con las fichas de registro.
    """
    ancho_panel = min(960, max(680, ancho_menu - 80))
    alto_panel = 448
    x_panel = (ancho_menu - ancho_panel) // 2
    y_panel = 96
    rect_panel = pygame.Rect(x_panel, y_panel, ancho_panel, alto_panel)

    y_btns_inf = 620
    w_btn, h_btn = 238, 70
    gap_btns = 24

    if tiene_partidas:
        total_w = w_btn * 2 + gap_btns
        x_inicio = (ancho_menu - total_w) // 2
        btn_volver = pygame.Rect(x_inicio, y_btns_inf, w_btn, h_btn)
        btn_nueva = pygame.Rect(x_inicio + w_btn + gap_btns, y_btns_inf, w_btn, h_btn)
    else:
        btn_volver = pygame.Rect((ancho_menu - w_btn) // 2, y_btns_inf, w_btn, h_btn)
        btn_nueva = pygame.Rect(0, 0, 0, 0)

    btn_iniciar_primera = pygame.Rect(rect_panel.centerx - 136, rect_panel.centery + 35, 272, 80)

    return rect_panel, btn_volver, btn_nueva, btn_iniciar_primera


def obtener_geometria_tarjeta_partida(rect_panel, idx_slot, alto_card=90, gap_cards=6):
    """
    Calcula los rectángulos de cada elemento dentro de la ficha de registro de partida:
    - r_card: rectángulo general de la ficha (papel antiguo, altura optimizada 90 px)
    - r_badge: rectángulo del sello/badge de mundo a la izquierda
    - r_btn_cargar: botón principal «CARGAR» (126x38)
    - r_btn_gestionar: botón de administración «GESTIONAR» (118x38)
    - r_btn_borrar: botón secundario «BORRAR» (96x38)
    - (x_texto, ancho_max_texto): zona exclusiva para los textos y metadatos organizados en 2 líneas
    """
    r_card = pygame.Rect(
        rect_panel.left + 20,
        rect_panel.top + 12 + idx_slot * (alto_card + gap_cards),
        rect_panel.width - 40,
        alto_card,
    )

    # Badge de mundo / expedición a la izquierda
    w_badge, h_badge = 112, 48
    r_badge = pygame.Rect(r_card.left + 16, r_card.centery - (h_badge // 2), w_badge, h_badge)

    # Botones a la derecha
    w_borrar = 96
    w_gestionar = 118
    w_cargar = 126
    h_btn = 38
    gap_btns = 10
    margin_der = 16

    r_btn_borrar = pygame.Rect(r_card.right - margin_der - w_borrar, r_card.centery - (h_btn // 2), w_borrar, h_btn)
    r_btn_gestionar = pygame.Rect(r_btn_borrar.left - gap_btns - w_gestionar, r_card.centery - (h_btn // 2), w_gestionar, h_btn)
    r_btn_cargar = pygame.Rect(r_btn_gestionar.left - gap_btns - w_cargar, r_card.centery - (h_btn // 2), w_cargar, h_btn)

    # Zona disponible para información textual a la izquierda de los botones
    x_texto = r_badge.right + 18
    x_limite_texto = r_btn_cargar.left - 14
    ancho_max_texto = max(80, x_limite_texto - x_texto)

    return r_card, r_badge, r_btn_cargar, r_btn_gestionar, r_btn_borrar, (x_texto, ancho_max_texto)


def dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel, pos_mouse, fuentes, sprites_botones=None):
    """
    Dibuja una ficha de registro dentro del diario antiguo de expediciones.
    - Ficha de papel antiguo con bordes envejecidos y tira de lomo decorativa.
    - Sello heráldico de expedición para el mundo alcanzado.
    - Símbolo de aventura dorado, nombre y detalles con iconos pixel art (candado y diario).
    - Botones de acción integrados a la paleta cálida (verde oliva, pergamino tostado y terracota).
    """
    r_card, r_badge, r_btn_cargar, r_btn_gestionar, r_btn_borrar, (x_texto, ancho_max_texto) = obtener_geometria_tarjeta_partida(rect_panel, idx_slot)

    hov_card = r_card.collidepoint(pos_mouse)
    hov_cargar = r_btn_cargar.collidepoint(pos_mouse)
    hov_gestionar = r_btn_gestionar.collidepoint(pos_mouse)
    hov_borrar = r_btn_borrar.collidepoint(pos_mouse)

    # 1. Base de la ficha: papel antiguo con sutil sombreado y borde cálido
    col_card = (255, 253, 245) if hov_card else (253, 248, 238)
    borde_card = (210, 130, 45) if hov_card else (185, 150, 110)
    pygame.draw.rect(pantalla, col_card, r_card, border_radius=12)
    pygame.draw.rect(pantalla, borde_card, r_card, width=3 if hov_card else 2, border_radius=12)

    # Filete perimetral interior suave estilo documento antiguo
    pygame.draw.rect(pantalla, (235, 220, 195), r_card.inflate(-6, -6), width=1, border_radius=8)

    # Tira de lomo / acento decorativo a la izquierda
    col_tira = (195, 120, 50) if hov_card else (160, 120, 80)
    pygame.draw.rect(pantalla, col_tira, (r_card.left + 3, r_card.top + 8, 4, r_card.height - 16), border_radius=2)

    # 2. Sello / Badge de Mundo y Expedición
    m_val = p.get("mundo_max", 1)
    info_b = COLORES_TABS.get(m_val, COLORES_TABS[1])
    pygame.draw.rect(pantalla, info_b["fondo"], r_badge, border_radius=8)
    pygame.draw.rect(pantalla, info_b["borde"], r_badge, width=2, border_radius=8)
    pygame.draw.rect(pantalla, (245, 235, 220), r_badge.inflate(-4, -4), width=1, border_radius=6)

    fuente_badge = fuentes.get("badge", fuentes.get("btn"))
    txt_badge = f"{t('mundo')} {m_val}"
    f_badge = obtener_fuente_para_texto(txt_badge, categoria="botones", tamano=TAMANO_BADGE)
    t_badge = f_badge.render(txt_badge, True, info_b["texto"])
    pantalla.blit(t_badge, t_badge.get_rect(center=r_badge.center))

    # 3. Metadatos de la aventura
    nombre = obtener_nombre_partida_visible(p)
    es_adm = es_partida_admin(p)
    mundo_max = p.get("mundo_max", 1)
    nivel_max = p.get("nivel_max", 1)
    fecha = p.get("fecha", "")
    cant_comp = calcular_niveles_completados(p.get("niveles_desbloqueados", {}), es_admin=es_adm)
    tiene_pwd = p.get("tiene_password", False)

    # Símbolo decorativo de aventura: diamante / gema dorada pixel art
    diam_cx = x_texto + 4
    diam_cy = r_card.top + 18
    for d_diam in range(-4, 5):
        w_diam = 4 - abs(d_diam)
        for dx in range(-w_diam, w_diam + 1):
            c_d = (245, 215, 110) if (d_diam <= 0 and dx <= 0) else (210, 145, 35)
            pantalla.set_at((diam_cx + dx, diam_cy + d_diam), c_d)

    # Línea 1: Nombre de la partida en sepia profundo con soporte para clave
    cur_x_tit = x_texto + 16
    if tiene_pwd:
        _dibujar_icono_candado(pantalla, cur_x_tit + 3, r_card.top + 18, abierto=False)
        cur_x_tit += 14

    rect_tit_card = pygame.Rect(cur_x_tit, r_card.top + 7, ancho_max_texto - (cur_x_tit - x_texto), 24)
    dibujar_texto_en_rect(pantalla, nombre, rect_tit_card, categoria="subtitulo", tamano=21, color=(55, 42, 30), negrita=True, alineacion="izquierda", padding=0)

    # Metadatos ampliados (+60% a +70%, tamano=28) distribuidos en dos líneas claras sin superposiciones
    partes_f = fecha.strip().split(" ") if fecha else []
    str_fecha = partes_f[0] if len(partes_f) > 0 else ""
    str_hora = partes_f[1] if len(partes_f) > 1 else ""
    tiene_fecha_hora = bool(str_fecha or str_hora)

    # Línea 2: Nivel alcanzado y Progreso de expedición
    y_fila2 = (r_card.top + 35) if tiene_fecha_hora else (r_card.top + 45)
    cur_x2 = x_texto + 4

    # 1. Nivel alcanzado
    _dibujar_icono_estrella_nivel(pantalla, cur_x2 + 5, y_fila2 + 14)
    cur_x2 += 16
    str_niv = f"{t('nivel')} {mundo_max}-{nivel_max}"
    f_niv = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_niv) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
    t_niv = f_niv.render(str_niv, True, (75, 48, 30))
    pantalla.blit(t_niv, (cur_x2, y_fila2))
    cur_x2 += t_niv.get_width() + 14

    # Separador sutil
    pygame.draw.circle(pantalla, (180, 150, 120), (cur_x2, y_fila2 + 14), 2)
    cur_x2 += 10

    # 2. Niveles completados
    _dibujar_icono_trofeo(pantalla, cur_x2 + 6, y_fila2 + 14)
    cur_x2 += 18
    tot_niv = TOTAL_NIVELES_ADMIN if es_adm else TOTAL_NIVELES_NORMALES
    str_comp = f"{cant_comp}/{tot_niv} {t('completados')}"
    f_comp = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_comp) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
    t_comp = f_comp.render(str_comp, True, (90, 65, 45))
    pantalla.blit(t_comp, (cur_x2, y_fila2))

    # Línea 3: Fecha y Hora (perfectamente alineadas debajo, aprovechando el ancho con holgura segura)
    if tiene_fecha_hora:
        y_fila3 = r_card.top + 61
        cur_x3 = x_texto + 4
        

        # 3. Fecha
        if str_fecha:
            _dibujar_icono_calendario(pantalla, cur_x3 + 6, y_fila3 + 14)
            cur_x3 += 16
            f_fec = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_fecha) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
            t_fec = f_fec.render(str_fecha, True, (105, 80, 60))
            pantalla.blit(t_fec, (cur_x3, y_fila3))
            cur_x3 += t_fec.get_width() + 16

        # 4. Hora
        if str_hora:
            _dibujar_icono_reloj(pantalla, cur_x3 + 6, y_fila3 + 14)
            cur_x3 += 16
            f_hor = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_hora) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
            t_hor = f_hor.render(str_hora, True, (105, 80, 60))
            pantalla.blit(t_hor, (cur_x3, y_fila3))

    # 4. Botón «CARGAR» (Verde bosque cálido de expedición - Sprite oficial)
    if sprites_botones and sprites_botones.get("cargar_normal"):
        spr_cn = sprites_botones["cargar_normal"]
        spr_ch = sprites_botones.get("cargar_hover")
        pantalla.blit(spr_ch if (hov_cargar and spr_ch) else spr_cn, r_btn_cargar)
    else:
        col_bc = (78, 155, 82) if hov_cargar else (65, 138, 72)
        borde_bc = (22, 45, 24)
        pygame.draw.rect(pantalla, col_bc, r_btn_cargar, border_radius=8)
        pygame.draw.rect(pantalla, borde_bc, r_btn_cargar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, t("cargar"), r_btn_cargar, categoria="boton", tamano=14, color=(255, 255, 255), padding=4)

    # 5. Botón «GESTIONAR» (Pergamino tostado - Sprite oficial)
    if sprites_botones and sprites_botones.get("gestionar_normal"):
        spr_gn = sprites_botones["gestionar_normal"]
        spr_gh = sprites_botones.get("gestionar_hover")
        pantalla.blit(spr_gh if (hov_gestionar and spr_gh) else spr_gn, r_btn_gestionar)
    else:
        col_bg = (255, 252, 246) if hov_gestionar else (246, 238, 224)
        borde_bg = (150, 115, 80) if hov_gestionar else (185, 155, 120)
        pygame.draw.rect(pantalla, col_bg, r_btn_gestionar, border_radius=8)
        pygame.draw.rect(pantalla, borde_bg, r_btn_gestionar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, t("gestionar"), r_btn_gestionar, categoria="boton", tamano=13, color=(82, 83, 83), padding=4)

    # 6. Botón «BORRAR» (Terracota cálido suave - Sprite oficial) - Oculto y protegido para la partida especial de Administrador
    if not es_adm:
        if sprites_botones and sprites_botones.get("borrar_normal"):
            spr_bn = sprites_botones["borrar_normal"]
            spr_bh = sprites_botones.get("borrar_hover")
            pantalla.blit(spr_bh if (hov_borrar and spr_bh) else spr_bn, r_btn_borrar)
        else:
            col_bb = (235, 95, 85) if hov_borrar else (205, 80, 70)
            borde_bb = (255, 255, 255) if hov_borrar else (150, 50, 45)
            pygame.draw.rect(pantalla, col_bb, r_btn_borrar, border_radius=8)
            pygame.draw.rect(pantalla, borde_bb, r_btn_borrar, width=2, border_radius=8)
            dibujar_texto_en_rect(pantalla, t("borrar"), r_btn_borrar, categoria="boton", tamano=14, color=(125, 48, 17), padding=4)
    else:
        r_btn_borrar = pygame.Rect(0, 0, 0, 0)

    return r_card, r_btn_cargar, r_btn_gestionar, r_btn_borrar


def _eventos_lista_partidas(m, evento):
    """Clic izquierdo en la pantalla «lista_partidas». Devuelve True si hay que cortar el resto de eventos del frame."""
    m.partidas_guardadas = cargar_partidas()
    m.rect_panel_partidas, m.btn_volver_partidas, m.btn_nueva_desde_lista, m.btn_iniciar_primera = (
        obtener_geometria_panel_partidas(m.ANCHO_MENU, m.ALTO_MENU, bool(m.partidas_guardadas))
    )
    m.total_p = len(m.partidas_guardadas)
    m.total_paginas = max(1, (m.total_p + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
    if m.pagina_partidas >= m.total_paginas:
        m.pagina_partidas = max(0, m.total_paginas - 1)

    m.idm_act = obtener_idioma()
    m.dict_sp_act = m._obtener_sprites_tarjeta(m.idm_act)

    if not m.partidas_guardadas:
        if m.btn_iniciar_primera.collidepoint(evento.pos):
            m.pulsado = True
            m.sp_pr_semi = m._obtener_boton_primera_partida("semi", m.idm_act)
            m.sp_pr_apret = m._obtener_boton_primera_partida("apretado", m.idm_act)
            m.sp_pr_norm = m._obtener_boton_primera_partida("normal", m.idm_act)
            if m.sp_pr_semi and m.sp_pr_apret:
                m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_iniciar_primera, m.sp_pr_semi, m.sp_pr_apret, (252, 248, 238), m.sp_pr_norm, tipo_sonido="partida_nueva")
            if m.pulsado:
                m.nueva_p = flujo_crear_nueva_partida(
                    m.pantalla, m.reloj,
                    color_p1=m.color_p1, color_p2=m.color_p2,
                    accesorio_p1=m.accesorio_p1, accesorio_p2=m.accesorio_p2,
                )
                if m.nueva_p is not None:
                    m.personalizacion_modificada_en_menu = False
                    m.niveles_desbloqueados = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                    m.snapshot_guardado = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                    m.partida_actual_id = m.nueva_p["id"]
                    m.partida_actual_nombre = m.nueva_p["nombre"]
                    m.partida_actual_password = m.nueva_p.get("password_plain", "")
                    m.partida_creada_flag = True
                    m.sesion_activa = True
                    m.mundo_seleccionado = 1
                    m.fin_acc, m.mundo_seleccionado = jugar_niveles_desde(
                        1, 0,
                        m.color_p1, m.color_p2,
                        m.niveles_desbloqueados,
                        m.partida_actual_id,
                        m.partida_actual_nombre,
                        m.snapshot_guardado,
                        accesorio_p1=m.accesorio_p1,
                        accesorio_p2=m.accesorio_p2,
                        partida_actual_password=m.partida_actual_password,
                    )
                    if m.fin_acc == "menu":
                        m.estado_actual = ESTADO_SELECCION_NIVEL
                        seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                        reproducir_musica("menu", forzar=True)
                    else:
                        m.ejecutando = False
    else:
        m.inicio_idx = m.pagina_partidas * m.MAX_PARTIDAS_POR_PAGINA
        m.fin_idx = m.inicio_idx + m.MAX_PARTIDAS_POR_PAGINA
        m.partidas_pagina = m.partidas_guardadas[m.inicio_idx:m.fin_idx]

        m.accion_ejecutada = False
        for m.idx_slot, m.p in enumerate(m.partidas_pagina):
            m.r_card, m._, m.r_btn_cargar, m.r_btn_gestionar, m.r_btn_borrar, m._ = obtener_geometria_tarjeta_partida(
                m.rect_panel_partidas, m.idx_slot
            )
            # Clic en botón BORRAR (dispara confirmación previa con advertencia)
            if m.r_btn_borrar.collidepoint(evento.pos):
                m.pulsado = True
                m.spr_b_s = m.dict_sp_act.get("borrar_semi")
                m.spr_b_a = m.dict_sp_act.get("borrar_apretado")
                m.spr_b_n = m.dict_sp_act.get("borrar_normal")
                if m.spr_b_s and m.spr_b_a:
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.r_btn_borrar, m.spr_b_s, m.spr_b_a, (253, 246, 233), m.spr_b_n, tipo_sonido="partida_borrar")
                if m.pulsado:
                    if mostrar_dialogo_confirmar_borrado(m.pantalla, m.reloj, m.p):
                        eliminar_partida(m.p["id"])
                        if m.partida_actual_id == m.p["id"]:
                            m.partida_actual_id = None
                            m.partida_actual_nombre = None
                            m.partida_actual_password = None
                            m.niveles_desbloqueados = crear_desbloqueados_inicial()
                            m.snapshot_guardado = copy.deepcopy(m.niveles_desbloqueados)
                            m.sesion_activa = False
                            m.partida_cargada_flag = False
                            m.partida_creada_flag = False
                        m.nuevas_p = cargar_partidas()
                        m.nuevas_total_pag = max(1, (len(m.nuevas_p) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
                        if m.pagina_partidas >= m.nuevas_total_pag:
                            m.pagina_partidas = max(0, m.nuevas_total_pag - 1)
                m.accion_ejecutada = True
                break

            # Clic en botón GESTIONAR (renombrar, cambiar/quitar clave, borrar)
            elif m.r_btn_gestionar.collidepoint(evento.pos):
                m.pulsado = True
                m.spr_g_s = m.dict_sp_act.get("gestionar_semi")
                m.spr_g_a = m.dict_sp_act.get("gestionar_apretado")
                m.spr_g_n = m.dict_sp_act.get("gestionar_normal")
                if m.spr_g_s and m.spr_g_a:
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.r_btn_gestionar, m.spr_g_s, m.spr_g_a, (253, 246, 233), m.spr_g_n, tipo_sonido="partida_gestionar")
                if m.pulsado:
                    if modal_administrar_perfil(m.pantalla, m.reloj, m.p):
                        m.nuevas_p = cargar_partidas()
                        m.nuevas_total_pag = max(1, (len(m.nuevas_p) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
                        if m.pagina_partidas >= m.nuevas_total_pag:
                            m.pagina_partidas = max(0, m.nuevas_total_pag - 1)
                m.accion_ejecutada = True
                break

            # Clic en botón CARGAR (única y exclusivamente sobre r_btn_cargar)
            elif m.r_btn_cargar.collidepoint(evento.pos):
                m.pulsado = True
                m.spr_c_s = m.dict_sp_act.get("cargar_semi")
                m.spr_c_a = m.dict_sp_act.get("cargar_apretado")
                m.spr_c_n = m.dict_sp_act.get("cargar_normal")
                if m.spr_c_s and m.spr_c_a:
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.r_btn_cargar, m.spr_c_s, m.spr_c_a, (253, 246, 233), m.spr_c_n, tipo_sonido="partida_cargar")
                if m.pulsado:
                    if m.p.get("tiene_password", False):
                        if not pedir_password_modal(m.pantalla, m.reloj, m.p):
                            pygame.event.clear()
                            m.accion_ejecutada = True
                            break
                        pygame.event.clear()

                    m.atuendo_guardado = (
                        m.p.get("color_p1", "Celeste"),
                        m.p.get("color_p2", "Violeta"),
                        m.p.get("accesorio_p1", "Ninguno"),
                        m.p.get("accesorio_p2", "Ninguno"),
                    )
                    m.atuendo_actual = (m.color_p1, m.color_p2, m.accesorio_p1, m.accesorio_p2)
                    m.hay_cambios_pendientes = m.personalizacion_modificada_en_menu and (m.atuendo_actual != m.atuendo_guardado)

                    if m.hay_cambios_pendientes:
                        m.decision = mostrar_dialogo_confirmar_atuendos(
                            m.pantalla, m.reloj, m.p,
                            color_p1_nuevo=m.color_p1,
                            color_p2_nuevo=m.color_p2,
                            acc_p1_nuevo=m.accesorio_p1,
                            acc_p2_nuevo=m.accesorio_p2,
                        )
                        if m.decision == "cancelar":
                            pygame.event.clear()
                            m.accion_ejecutada = True
                            break
                        elif m.decision == "mantener":
                            m.color_p1, m.color_p2, m.accesorio_p1, m.accesorio_p2 = m.atuendo_guardado
                            m.personalizacion_modificada_en_menu = False
                        elif m.decision == "cambiar":
                            m.p_actualizada = guardar_partida(
                                niveles_desbloqueados=m.p["niveles_desbloqueados"],
                                id_partida=m.p["id"],
                                nombre_partida=m.p["nombre"],
                                password_hash=m.p.get("password_hash"),
                                password_salt=m.p.get("password_salt"),
                                color_p1=m.color_p1,
                                color_p2=m.color_p2,
                                accesorio_p1=m.accesorio_p1,
                                accesorio_p2=m.accesorio_p2,
                            )
                            if m.p_actualizada:
                                m.p["color_p1"] = m.color_p1
                                m.p["color_p2"] = m.color_p2
                                m.p["accesorio_p1"] = m.accesorio_p1
                                m.p["accesorio_p2"] = m.accesorio_p2
                            m.personalizacion_modificada_en_menu = False
                    else:
                        m.color_p1, m.color_p2, m.accesorio_p1, m.accesorio_p2 = m.atuendo_guardado
                        m.personalizacion_modificada_en_menu = False

                    m.niveles_desbloqueados = copy.deepcopy(m.p["niveles_desbloqueados"])
                    m.snapshot_guardado = copy.deepcopy(m.p["niveles_desbloqueados"])
                    m.partida_actual_id = m.p["id"]
                    m.partida_actual_nombre = m.p["nombre"]
                    m.partida_actual_password = None
                    m.partida_cargada_flag = True
                    m.sesion_activa = True
                    m.mundo_seleccionado = m.p["mundo_max"]
                    m.estado_actual = ESTADO_SELECCION_NIVEL
                    m.accion_ejecutada = True
                    break

        if not m.accion_ejecutada:
            if m.total_paginas > 1:
                m.btn_pag_ant = pygame.Rect(m.rect_panel_partidas.centerx - 120, 508, 36, 32)
                m.btn_pag_sig = pygame.Rect(m.rect_panel_partidas.centerx + 84, 508, 36, 32)
                if m.btn_pag_ant.collidepoint(evento.pos) and m.pagina_partidas > 0:
                    m.pagina_partidas -= 1
                    reproducir_sonido_ui("pagina")
                elif m.btn_pag_sig.collidepoint(evento.pos) and m.pagina_partidas < m.total_paginas - 1:
                    m.pagina_partidas += 1
                    reproducir_sonido_ui("pagina")

            if m.btn_nueva_desde_lista.collidepoint(evento.pos):
                m.pulsado = True
                m.sp_nl_s = m._obtener_boton_nueva_lista("semi", m.idm_act)
                m.sp_nl_a = m._obtener_boton_nueva_lista("apretado", m.idm_act)
                m.sp_nl_n = m._obtener_boton_nueva_lista("normal", m.idm_act)
                if m.sp_nl_s and m.sp_nl_a:
                    m.f_limp = _obtener_fondo_partidas(m.ANCHO_MENU, m.ALTO_MENU)
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_nueva_desde_lista, m.sp_nl_s, m.sp_nl_a, m.f_limp, m.sp_nl_n, tipo_sonido="partida_nueva")
                if m.pulsado:
                    m.nueva_p = flujo_crear_nueva_partida(
                        m.pantalla, m.reloj,
                        color_p1=m.color_p1, color_p2=m.color_p2,
                        accesorio_p1=m.accesorio_p1, accesorio_p2=m.accesorio_p2,
                    )
                    if m.nueva_p is not None:
                        m.personalizacion_modificada_en_menu = False
                        m.niveles_desbloqueados = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                        m.snapshot_guardado = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                        m.partida_actual_id = m.nueva_p["id"]
                        m.partida_actual_nombre = m.nueva_p["nombre"]
                        m.partida_actual_password = m.nueva_p.get("password_plain", "")
                        m.partida_creada_flag = True
                        m.sesion_activa = True
                        m.mundo_seleccionado = 1
                        m.fin_acc, m.mundo_seleccionado = jugar_niveles_desde(
                            1, 0,
                            m.color_p1, m.color_p2,
                            m.niveles_desbloqueados,
                            m.partida_actual_id,
                            m.partida_actual_nombre,
                            m.snapshot_guardado,
                            accesorio_p1=m.accesorio_p1,
                            accesorio_p2=m.accesorio_p2,
                            partida_actual_password=m.partida_actual_password,
                        )
                        if m.fin_acc == "menu":
                            m.estado_actual = ESTADO_SELECCION_NIVEL
                            seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                            reproducir_musica("menu", forzar=True)
                        else:
                            m.ejecutando = False

    if m.btn_volver_partidas.collidepoint(evento.pos):
        m.pulsado = True
        m.sp_vp_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_vp_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_vp_n = m._obtener_boton_volver("normal", m.idm_act)
        if m.sp_vp_s and m.sp_vp_a:
            m.f_limp = _obtener_fondo_partidas(m.ANCHO_MENU, m.ALTO_MENU)
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_partidas, m.sp_vp_s, m.sp_vp_a, m.f_limp, m.sp_vp_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MODO_JUEGO
    return False


def _dibujar_lista_partidas(m):
    """Dibuja la pantalla «lista_partidas»."""
    m.ANCHO_MENU = m.pantalla.get_width()
    m.ALTO_MENU = m.pantalla.get_height()
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()
    partidas = cargar_partidas()

    # Asegurar recursos pixel art del diario cargados
    m._cargar_recursos_partidas()

    # Fondo pergamino antiguo con bocetos cartográficos y bordes envejecidos
    m.pantalla.blit(_obtener_fondo_partidas(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))

    m.rect_panel_partidas, m.btn_volver_partidas, m.btn_nueva_desde_lista, m.btn_iniciar_primera = (
        obtener_geometria_panel_partidas(m.ANCHO_MENU, m.ALTO_MENU, bool(partidas))
    )

    # Título «PARTIDAS GUARDADAS» en sepia oscuro con relieve y subtítulo de expedición
    txt_tit_lp = t("partidas_guardadas")
    f_tit_lp = obtener_fuente_para_texto(txt_tit_lp, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
    m.t_somb = f_tit_lp.render(txt_tit_lp, True, (195, 170, 140))
    m.t_tit = f_tit_lp.render(txt_tit_lp, True, (58, 38, 24))
    m.rect_tit = m.t_tit.get_rect(center=(m.ANCHO_MENU // 2, 46))
    m.pantalla.blit(m.t_somb, (m.rect_tit.x + 2, m.rect_tit.y + 2))
    m.pantalla.blit(m.t_tit, m.rect_tit)

    txt_sub_lp = t("sub_partidas")
    f_sub_lp = obtener_fuente_para_texto(txt_sub_lp, categoria="decorativa", tamano=TAMANO_DECORATIVA)
    m.subt = f_sub_lp.render(txt_sub_lp, True, (125, 95, 65))
    m.pantalla.blit(m.subt, m.subt.get_rect(center=(m.ANCHO_MENU // 2, 78)))

    # Contenedor de página del diario (folio pergamino con líneas sutiles y remaches)
    col_pagina = (252, 246, 235)
    col_borde_pag = (190, 160, 125)
    col_linea_int = (225, 200, 160)
    pygame.draw.rect(m.pantalla, col_pagina, m.rect_panel_partidas, border_radius=16)
    pygame.draw.rect(m.pantalla, col_borde_pag, m.rect_panel_partidas, width=3, border_radius=16)
    pygame.draw.rect(m.pantalla, col_linea_int, m.rect_panel_partidas.inflate(-8, -8), width=1, border_radius=12)

    # Pauta de cuaderno sutil (líneas horizontales tenues de diario de campo)
    for m.y_linea in range(m.rect_panel_partidas.top + 28, m.rect_panel_partidas.bottom - 20, 22):
        pygame.draw.line(m.pantalla, (238, 230, 216), (m.rect_panel_partidas.left + 14, m.y_linea), (m.rect_panel_partidas.right - 14, m.y_linea), 1)

    # Remaches / clavos metálicos en las esquinas del folio
    for m.rx, m.ry in [
        (m.rect_panel_partidas.left + 12, m.rect_panel_partidas.top + 12),
        (m.rect_panel_partidas.right - 12, m.rect_panel_partidas.top + 12),
        (m.rect_panel_partidas.left + 12, m.rect_panel_partidas.bottom - 12),
        (m.rect_panel_partidas.right - 12, m.rect_panel_partidas.bottom - 12),
    ]:
        pygame.draw.circle(m.pantalla, (205, 175, 105), (m.rx, m.ry), 3)
        pygame.draw.circle(m.pantalla, (100, 70, 40), (m.rx, m.ry), 3, width=1)

    if not partidas:
        m.txt_sin = t("no_partidas")
        m.f_sin = obtener_fuente_para_texto(m.txt_sin, categoria="subtitulo", tamano=TAMANO_SUBTITULO)
        m.t_sin = m.f_sin.render(m.txt_sin, True, (65, 45, 30))
        m.pantalla.blit(m.t_sin, m.t_sin.get_rect(center=(m.rect_panel_partidas.centerx, m.rect_panel_partidas.centery - 40)))

        m.rect_sin2 = pygame.Rect(m.rect_panel_partidas.left + 40, m.rect_panel_partidas.centery - 20, m.rect_panel_partidas.width - 80, 24)
        dibujar_texto_en_rect(m.pantalla, t("comenzar_historia"), m.rect_sin2, categoria="texto", tamano=16, color=(120, 100, 80))

        m.hov_prim = m.btn_iniciar_primera.collidepoint(m.pos_mouse)
        m.spr_prim_norm = m._obtener_boton_primera_partida("normal", m.idm_act)
        m.spr_prim_hov = m._obtener_boton_primera_partida("hover", m.idm_act)
        m.spr_prim = m.spr_prim_hov if (m.hov_prim and m.spr_prim_hov) else m.spr_prim_norm
        if m.spr_prim:
            m.pantalla.blit(m.spr_prim, m.btn_iniciar_primera)
        else:
            m.col_prim = (235, 128, 48) if m.hov_prim else (215, 110, 42)
            pygame.draw.rect(m.pantalla, m.col_prim, m.btn_iniciar_primera, border_radius=12)
            pygame.draw.rect(m.pantalla, (118, 44, 14), m.btn_iniciar_primera, width=2, border_radius=12)
            dibujar_texto_en_rect(m.pantalla, t("comenzar_aventura"), m.btn_iniciar_primera, categoria="boton", tamano=TAMANO_BOTONES, color=(255, 255, 255), padding=6)
    else:
        m.total_paginas = max(1, (len(partidas) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
        if m.pagina_partidas >= m.total_paginas:
            m.pagina_partidas = max(0, m.total_paginas - 1)

        m.inicio_idx = m.pagina_partidas * m.MAX_PARTIDAS_POR_PAGINA
        m.fin_idx = m.inicio_idx + m.MAX_PARTIDAS_POR_PAGINA
        m.partidas_pagina = partidas[m.inicio_idx:m.fin_idx]

        m.fuentes_tarjetas = {
            "titulo_card": m.fuente_card_titulo,
            "sub_card": m.fuente_card_sub,
            "btn_card": m.fuente_pixel_card_btn,
            "badge": m.fuente_pixel_badge,
            "btn": m.fuente_pixel_badge,
            "texto": m.fuente_texto,
            "sub_btn": m.fuente_sub_btn,
        }

        m.dict_sp_partidas = m._obtener_sprites_tarjeta(m.idm_act)
        for m.idx_slot, m.p in enumerate(m.partidas_pagina):
            dibujar_tarjeta_partida(m.pantalla, m.p, m.idx_slot, m.rect_panel_partidas, m.pos_mouse, m.fuentes_tarjetas, sprites_botones=m.dict_sp_partidas)

        # Indicador de paginación si hay más de 1 página (y = 508, dentro del panel inferior sin colisiones)
        if m.total_paginas > 1:
            m.btn_pag_ant = pygame.Rect(m.rect_panel_partidas.centerx - 120, 508, 36, 30)
            m.btn_pag_sig = pygame.Rect(m.rect_panel_partidas.centerx + 84, 508, 36, 30)

            # Botón página anterior
            m.hov_ant = m.btn_pag_ant.collidepoint(m.pos_mouse) and m.pagina_partidas > 0
            m.col_ant = (255, 255, 255) if m.hov_ant else ((253, 246, 233) if m.pagina_partidas > 0 else (240, 230, 215))
            m.borde_ant = (160, 125, 90) if m.hov_ant else (195, 168, 138)
            pygame.draw.rect(m.pantalla, m.col_ant, m.btn_pag_ant, border_radius=6)
            m.col_flecha_ant = (65, 45, 30) if m.pagina_partidas > 0 else (175, 155, 135)
            m.cx_a, m.cy_a = m.btn_pag_ant.center
            for m.dy in range(-4, 5):
                m.ancho_f = 4 - abs(m.dy)
                for m.dx in range(m.ancho_f + 1):
                    m.pantalla.set_at((m.cx_a + 2 - m.dx, m.cy_a + m.dy), m.col_flecha_ant)

            # Contador de página
            m.txt_pag = t("entrada_pagina").format(m.pagina_partidas + 1, m.total_paginas)
            m.f_pag = obtener_fuente_para_texto(m.txt_pag, categoria="contador", tamano=TAMANO_CONTADOR)
            m.t_pag = m.f_pag.render(m.txt_pag, True, (75, 55, 38))
            m.pantalla.blit(m.t_pag, m.t_pag.get_rect(center=(m.rect_panel_partidas.centerx, 523)))

            # Botón página siguiente
            m.hov_sig = m.btn_pag_sig.collidepoint(m.pos_mouse) and m.pagina_partidas < m.total_paginas - 1
            m.col_sig = (255, 255, 255) if m.hov_sig else ((253, 246, 233) if m.pagina_partidas < m.total_paginas - 1 else (240, 230, 215))
            m.borde_sig = (160, 125, 90) if m.hov_sig else (195, 168, 138)
            pygame.draw.rect(m.pantalla, m.col_sig, m.btn_pag_sig, border_radius=6)
            pygame.draw.rect(m.pantalla, m.borde_sig, m.btn_pag_sig, width=2 if m.hov_sig else 1, border_radius=6)
            m.col_flecha_sig = (65, 45, 30) if m.pagina_partidas < m.total_paginas - 1 else (175, 155, 135)
            m.cx_s, m.cy_s = m.btn_pag_sig.center
            for m.dy in range(-4, 5):
                m.ancho_f = 4 - abs(m.dy)
                for m.dx in range(m.ancho_f + 1):
                    m.pantalla.set_at((m.cx_s - 2 + m.dx, m.cy_s + m.dy), m.col_flecha_sig)

    # Botón «VOLVER» centrado al pie de la pantalla en tonos pergamino/crema
    hov_vp = m.btn_volver_partidas.collidepoint(m.pos_mouse)
    spr_vp_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vp_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vp = spr_vp_hov if (hov_vp and spr_vp_hov) else spr_vp_norm
    if spr_vp:
        m.pantalla.blit(spr_vp, m.btn_volver_partidas)
    else:
        m.col_vp = (255, 255, 255) if hov_vp else (253, 246, 233)
        m.borde_vp = (165, 135, 105) if hov_vp else (195, 168, 138)
        pygame.draw.rect(m.pantalla, m.col_vp, m.btn_volver_partidas, border_radius=12)
        pygame.draw.rect(m.pantalla, m.borde_vp, m.btn_volver_partidas, width=2, border_radius=12)
        dibujar_texto_en_rect(m.pantalla, t("volver"), m.btn_volver_partidas, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)

    if partidas:
        # Botón «NUEVA PARTIDA» ubicado al lado de «VOLVER», centrados juntos en ámbar/terracota
        m.hov_nd = m.btn_nueva_desde_lista.collidepoint(m.pos_mouse)
        m.spr_nd_norm = m._obtener_boton_nueva_lista("normal", m.idm_act)
        m.spr_nd_hov = m._obtener_boton_nueva_lista("hover", m.idm_act)
        m.spr_nd = m.spr_nd_hov if (m.hov_nd and m.spr_nd_hov) else m.spr_nd_norm
        if m.spr_nd:
            m.pantalla.blit(m.spr_nd, m.btn_nueva_desde_lista)
        else:
            m.col_nd = (235, 128, 48) if m.hov_nd else (215, 110, 42)
            m.borde_nd = (255, 255, 255) if m.hov_nd else (118, 44, 14)
            pygame.draw.rect(m.pantalla, m.col_nd, m.btn_nueva_desde_lista, border_radius=12)
            pygame.draw.rect(m.pantalla, m.borde_nd, m.btn_nueva_desde_lista, width=2, border_radius=12)
            dibujar_texto_en_rect(m.pantalla, t("nueva_partida"), m.btn_nueva_desde_lista, categoria="boton", tamano=TAMANO_BOTONES, color=(255, 255, 255), padding=6)
