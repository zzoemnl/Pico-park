import sys
import copy
import pygame

from sprites import ANCHO, ALTO, FPS, cargar_sprites, cargar_boton, animar_pulsacion_boton, aclarar_boton
from pantalla import iniciar_mundo
from menu_niveles import (
    dibujar_menu_niveles,
    obtener_geometria_menu,
    obtener_mecanicas_nivel,
    COLORES_TABS,
    COL_PANEL,
    COL_BORDE_PANEL,
)
from guardado import (
    crear_desbloqueados_inicial,
    cargar_partidas,
    guardar_partida,
    eliminar_partida,
    mostrar_dialogo_guardar_salir,
    mostrar_dialogo_confirmar_borrado,
    cargar_fuente_pixel,
)

# Estados de la máquina de navegación de menús
ESTADO_MENU_PRINCIPAL = "principal"
ESTADO_MODO_JUEGO = "modo_juego"
ESTADO_LISTA_PARTIDAS = "lista_partidas"
ESTADO_CONFIGURACION = "configuracion"
ESTADO_CREDITOS = "creditos"
ESTADO_PERSONAJES = "personajes"
ESTADO_SELECCION_MUNDO = "seleccion_mundo"
ESTADO_SELECCION_NIVEL = "seleccion_nivel"

PERSONAJES_DISPONIBLES = [
    # Tonos Neutros y Tierra
    {"nombre": "Blanco", "color": (232, 232, 232)},
    {"nombre": "Gris", "color": (154, 154, 154)},
    {"nombre": "Negro", "color": (89, 89, 89)},
    {"nombre": "Marron", "color": (206, 136, 111)},
    # Tonos Cálidos
    {"nombre": "Rojo", "color": (255, 137, 134)},
    {"nombre": "Rosa", "color": (255, 150, 240)},
    {"nombre": "Naranja", "color": (255, 160, 100)},
    {"nombre": "Amarillo", "color": (255, 244, 123)},
    # Tonos Verdes
    {"nombre": "Verde", "color": (157, 255, 124)},
    {"nombre": "Verde oscuro", "color": (105, 205, 75)},
    # Tonos Fríos / Azules / Violetas
    {"nombre": "Celeste", "color": (124, 231, 255)},
    {"nombre": "Azul", "color": (36, 166, 247)},
    {"nombre": "Violeta", "color": (161, 123, 255)},
]


def truncar_texto(texto, fuente, ancho_max):
    """Acorta el texto con puntos suspensivos si supera el ancho máximo disponible."""
    if fuente.size(texto)[0] <= ancho_max:
        return texto
    ellipsis = "..."
    ancho_ell = fuente.size(ellipsis)[0]
    if ancho_ell >= ancho_max:
        return ""
    recortado = texto
    while recortado and fuente.size(recortado + ellipsis)[0] > ancho_max:
        recortado = recortado[:-1]
    return recortado + ellipsis


def obtener_geometria_panel_partidas(ancho_menu, alto_menu, tiene_partidas=True):
    """
    Calcula dinámicamente las dimensiones y posiciones del panel y botones
    de la pantalla de partidas guardadas adaptadas a la resolución actual.
    Garantiza que «VOLVER» y «NUEVA PARTIDA» queden perfectamente centrados juntos.
    """
    ancho_panel = min(960, max(680, ancho_menu - 80))
    alto_panel = min(490, max(360, alto_menu - 190))
    x_panel = (ancho_menu - ancho_panel) // 2
    y_panel = 105
    rect_panel = pygame.Rect(x_panel, y_panel, ancho_panel, alto_panel)

    y_btns_inf = alto_menu - 80
    w_btn, h_btn = 238, 70
    gap_btns = 24

    if tiene_partidas:
        # Volver y Nueva Partida lado a lado, perfectamente centrados juntos
        total_w = w_btn * 2 + gap_btns
        x_inicio = (ancho_menu - total_w) // 2
        btn_volver = pygame.Rect(x_inicio, y_btns_inf, w_btn, h_btn)
        btn_nueva = pygame.Rect(x_inicio + w_btn + gap_btns, y_btns_inf, w_btn, h_btn)
    else:
        # Si no hay partidas previas, Volver queda centrado en el medio
        btn_volver = pygame.Rect((ancho_menu - w_btn) // 2, y_btns_inf, w_btn, h_btn)
        btn_nueva = pygame.Rect(0, 0, 0, 0)

    btn_iniciar_primera = pygame.Rect(rect_panel.centerx - 136, rect_panel.centery + 35, 272, 80)

    return rect_panel, btn_volver, btn_nueva, btn_iniciar_primera


def obtener_geometria_tarjeta_partida(rect_panel, idx_slot, alto_card=84, gap_cards=10):
    """
    Calcula los rectángulos de cada elemento dentro de la tarjeta de partida:
    - r_card: rectángulo general de la tarjeta
    - r_badge: rectángulo del badge de mundo a la izquierda
    - r_btn_cargar: botón principal «CARGAR»
    - r_btn_borrar: botón secundario «BORRAR»
    - (x_texto, ancho_max_texto): zona exclusiva para los textos a la izquierda de los botones
    """
    r_card = pygame.Rect(
        rect_panel.left + 18,
        rect_panel.top + 16 + idx_slot * (alto_card + gap_cards),
        rect_panel.width - 36,
        alto_card,
    )

    # Badge a la izquierda
    w_badge, h_badge = 110, 48
    r_badge = pygame.Rect(r_card.left + 16, r_card.centery - (h_badge // 2), w_badge, h_badge)

    # Botones a la derecha con ancho y separación reservados para no superponerse
    w_borrar = 100
    w_cargar = 126
    h_btn = 37
    gap_btns = 12
    margin_der = 16

    r_btn_borrar = pygame.Rect(r_card.right - margin_der - w_borrar, r_card.centery - (40 // 2), w_borrar, 40)
    r_btn_cargar = pygame.Rect(r_btn_borrar.left - gap_btns - w_cargar, r_card.centery - (h_btn // 2), w_cargar, h_btn)

    # Zona disponible para información a la izquierda de los botones
    x_texto = r_badge.right + 18
    x_limite_texto = r_btn_cargar.left - 18
    ancho_max_texto = max(80, x_limite_texto - x_texto)

    return r_card, r_badge, r_btn_cargar, r_btn_borrar, (x_texto, ancho_max_texto)


def dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel, pos_mouse, fuentes, sprites_botones=None):
    """Dibuja una tarjeta de partida organizada con información a la izquierda y botones a la derecha."""
    fuente_titulo_card = fuentes.get("titulo_card", fuentes["btn"])
    fuente_sub_card = fuentes.get("sub_card", fuentes["sub_btn"])
    fuente_btn_card = fuentes.get("btn_card", fuentes["texto"])

    r_card, r_badge, r_btn_cargar, r_btn_borrar, (x_texto, ancho_max_texto) = obtener_geometria_tarjeta_partida(rect_panel, idx_slot)

    hov_card = r_card.collidepoint(pos_mouse)
    hov_cargar = r_btn_cargar.collidepoint(pos_mouse)
    hov_borrar = r_btn_borrar.collidepoint(pos_mouse)

    # Fondo y borde de la tarjeta en tono pastel crema cálido
    col_card = (255, 252, 244) if hov_card else (255, 255, 255)
    borde_card = (225, 145, 75) if hov_card else (220, 202, 178)
    pygame.draw.rect(pantalla, col_card, r_card, border_radius=14)
    pygame.draw.rect(pantalla, borde_card, r_card, width=3 if hov_card else 2, border_radius=14)

    # 1. Badge de Mundo a la izquierda con colores pastel acordes a cada mundo
    m_val = p.get("mundo_max", 1)
    info_b = COLORES_TABS.get(m_val, COLORES_TABS[1])
    pygame.draw.rect(pantalla, info_b["fondo"], r_badge, border_radius=10)
    pygame.draw.rect(pantalla, info_b["borde"], r_badge, width=2, border_radius=10)
    fuente_badge = fuentes.get("badge", fuentes.get("btn"))
    t_badge = fuente_badge.render(f"MUNDO {m_val}", True, info_b["texto"])
    pantalla.blit(t_badge, t_badge.get_rect(center=r_badge.center))

    # 2. Información textual adaptativa (Nombre, nivel, guardado y desbloqueados) en tonos café y terracota
    nombre = p.get("nombre", f"Partida {p.get('id', 1)}")
    mundo_max = p.get("mundo_max", 1)
    nivel_max = p.get("nivel_max", 1)
    fecha = p.get("fecha", "")
    niveles_desc = p.get("niveles_desbloqueados", {})
    total_desbloq = sum(sum(1 for x in bits if x) for bits in niveles_desc.values()) if isinstance(niveles_desc, dict) else 1

    tit_unido = f"{nombre}  —  Nivel Máximo: {mundo_max}-{nivel_max}"
    det_unido = f"Último guardado: {fecha}   |   Niveles desbloqueados: {total_desbloq}/15"

    w_tit = fuente_titulo_card.size(tit_unido)[0]
    w_det = fuente_sub_card.size(det_unido)[0]

    color_tit = (55, 45, 35)
    color_det = (115, 100, 85)
    color_nivel_destacado = (195, 100, 45)

    if w_tit <= ancho_max_texto and w_det <= ancho_max_texto:
        # Modo 2 líneas: todo cabe cómodamente
        t1 = fuente_titulo_card.render(tit_unido, True, color_tit)
        pantalla.blit(t1, (x_texto, r_card.top + 16))

        t2 = fuente_sub_card.render(det_unido, True, color_det)
        pantalla.blit(t2, (x_texto, r_card.top + 48))
    elif w_tit <= ancho_max_texto:
        # El título cabe en una línea, pero los detalles se dividen en 2 líneas
        t1 = fuente_titulo_card.render(tit_unido, True, color_tit)
        pantalla.blit(t1, (x_texto, r_card.top + 12))

        t2 = fuente_sub_card.render(truncar_texto(f"Último guardado: {fecha}", fuente_sub_card, ancho_max_texto), True, color_det)
        pantalla.blit(t2, (x_texto, r_card.top + 37))

        t3 = fuente_sub_card.render(truncar_texto(f"Niveles desbloqueados: {total_desbloq}/15", fuente_sub_card, ancho_max_texto), True, color_det)
        pantalla.blit(t3, (x_texto, r_card.top + 58))
    else:
        # El título no cabe completo en una línea: se divide ordenadamente nombre y nivel
        t1_nom = truncar_texto(nombre, fuente_titulo_card, ancho_max_texto)
        t1 = fuente_titulo_card.render(t1_nom, True, color_tit)
        pantalla.blit(t1, (x_texto, r_card.top + 12))

        txt_nivel = f"Nivel Máximo: Mundo {mundo_max} - Nivel {nivel_max}"
        t2 = fuente_sub_card.render(truncar_texto(txt_nivel, fuente_sub_card, ancho_max_texto), True, color_nivel_destacado)
        pantalla.blit(t2, (x_texto, r_card.top + 37))

        txt_info = f"Guardado: {fecha}  •  Desbloqueados: {total_desbloq}/15"
        t3 = fuente_sub_card.render(truncar_texto(txt_info, fuente_sub_card, ancho_max_texto), True, color_det)
        pantalla.blit(t3, (x_texto, r_card.top + 58))

    # 3. Botón «CARGAR» (Sprite oficial mundos/boton-cargar o fallback)
    if sprites_botones and sprites_botones.get("cargar_normal"):
        spr_cn = sprites_botones["cargar_normal"]
        spr_ch = sprites_botones.get("cargar_hover")
        pantalla.blit(spr_ch if (hov_cargar and spr_ch) else spr_cn, r_btn_cargar)
    else:
        col_bc = (82, 194, 114) if hov_cargar else (68, 172, 98)
        borde_bc = (255, 255, 255) if hov_cargar else (45, 130, 70)
        pygame.draw.rect(pantalla, col_bc, r_btn_cargar, border_radius=10)
        pygame.draw.rect(pantalla, borde_bc, r_btn_cargar, width=2, border_radius=10)
        t_bc = fuente_btn_card.render("CARGAR", True, (255, 255, 255))
        pantalla.blit(t_bc, t_bc.get_rect(center=r_btn_cargar.center))

    # 4. Botón «BORRAR» (Rojo terracota / coral pastel con fuente pixel art)
    col_bb = (240, 105, 100) if hov_borrar else (220, 85, 80)
    borde_bb = (255, 255, 255) if hov_borrar else (170, 55, 50)
    pygame.draw.rect(pantalla, col_bb, r_btn_borrar, border_radius=10)
    pygame.draw.rect(pantalla, borde_bb, r_btn_borrar, width=2, border_radius=10)
    t_bb = fuente_btn_card.render("BORRAR", True, (255, 255, 255))
    pantalla.blit(t_bb, t_bb.get_rect(center=r_btn_borrar.center))

    return r_card, r_btn_cargar, r_btn_borrar


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
    try:
        from pygame._sdl2.video import Window
        ventana = Window.from_display_module()
        ventana.maximize()
    except Exception:
        pass

    pygame.display.set_caption("Pico Park")
    reloj = pygame.time.Clock()
    fuente_pixel_titulo = cargar_fuente_pixel(30, fallback_tamano=55)
    fuente_pixel_btn_grande = cargar_fuente_pixel(20, fallback_tamano=32)
    fuente_pixel_btn = cargar_fuente_pixel(15, fallback_tamano=32)
    fuente_pixel_sub_btn = cargar_fuente_pixel(14, fallback_tamano=24)
    fuente_pixel_card_btn = cargar_fuente_pixel(14, fallback_tamano=25)
    fuente_pixel_badge = cargar_fuente_pixel(15, fallback_tamano=28)

    fuente_titulo = pygame.font.Font(None, 55)
    fuente_subtitulo = pygame.font.Font(None, 36)
    fuente_btn = pygame.font.Font(None, 32)
    fuente_texto = pygame.font.Font(None, 26)
    fuente_sub_btn = pygame.font.Font(None, 22)
    fuentes_menu = {
        "titulo": fuente_pixel_titulo,
        "tab": cargar_fuente_pixel(18, fallback_tamano=34),
        "card": cargar_fuente_pixel(13, fallback_tamano=28),
    }
    fuente_card_titulo = pygame.font.Font(None, 29)
    fuente_card_sub = pygame.font.Font(None, 22)

    ANCHO_MENU = pantalla.get_width()
    ALTO_MENU = pantalla.get_height()

    niveles_desbloqueados = crear_desbloqueados_inicial()
    partida_actual_id = None
    partida_actual_nombre = None

    TAM_BOTON_HUD = 92
    MARGEN_DER, MARGEN_SUP = 25, 20
    rect_btn_x = pygame.Rect(ANCHO_MENU - MARGEN_DER - TAM_BOTON_HUD, MARGEN_SUP, TAM_BOTON_HUD, TAM_BOTON_HUD)

    def _cargar_hud(nombre):
        img = cargar_boton(nombre)
        return pygame.transform.scale(img, (TAM_BOTON_HUD, TAM_BOTON_HUD)) if img else None

    spr_x_normal = _cargar_hud("boton-x.png")
    spr_x_hover = aclarar_boton(spr_x_normal)
    spr_x_semi = _cargar_hud("boton-x-semiapretado.png")
    spr_x_apretado = _cargar_hud("boton-x-apretado.png")

    fondo_btn_x = None

    ANCHO_BOTON, ALTO_BOTON, ESPACIO = 306, 90, 18
    x_centro = (ANCHO_MENU - ANCHO_BOTON) // 2
    total_h_menu = (ALTO_BOTON * 4) + (ESPACIO * 3)
    y_inicio_principal = (ALTO_MENU - total_h_menu) // 2 + 30

    def _cargar_menu_btn(nombre):
        img = cargar_boton(nombre)
        return pygame.transform.scale(img, (ANCHO_BOTON, ALTO_BOTON)) if img else None

    # Sprites animados de los botones del menú principal
    spr_jugar_normal = _cargar_menu_btn("jugar.png")
    spr_jugar_hover = aclarar_boton(spr_jugar_normal)
    spr_jugar_semi = _cargar_menu_btn("jugar-preapretado.png")
    spr_jugar_apretado = _cargar_menu_btn("jugar-apretado.png")

    spr_personajes_normal = _cargar_menu_btn("personajes.png")
    spr_personajes_hover = aclarar_boton(spr_personajes_normal)
    spr_personajes_semi = _cargar_menu_btn("personajes-preapretado.png")
    spr_personajes_apretado = _cargar_menu_btn("personajes-apretado.png")

    spr_opciones_normal = _cargar_menu_btn("opciones.png")
    spr_opciones_hover = aclarar_boton(spr_opciones_normal)
    spr_opciones_semi = _cargar_menu_btn("opciones-preapretado.png")
    spr_opciones_apretado = _cargar_menu_btn("opciones-apretado.png")

    spr_salir_normal = _cargar_menu_btn("salir.png")
    spr_salir_hover = aclarar_boton(spr_salir_normal)
    spr_salir_semi = _cargar_menu_btn("salir-preapretado.png")
    spr_salir_apretado = _cargar_menu_btn("salir-apretado.png")

    btn_jugar = pygame.Rect(x_centro, y_inicio_principal, ANCHO_BOTON, ALTO_BOTON)
    btn_personajes = pygame.Rect(x_centro, y_inicio_principal + ALTO_BOTON + ESPACIO, ANCHO_BOTON, ALTO_BOTON)
    btn_config = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON)
    btn_salir = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON)

    fondo_limpio_btn = pygame.Surface((ANCHO_BOTON, ALTO_BOTON))
    fondo_limpio_btn.fill((30, 30, 30))

    color_p1 = "Celeste"
    color_p2 = "Violeta"

    preview_sprites = {}
    for p in PERSONAJES_DISPONIBLES:
        sp = cargar_sprites(p["nombre"])
        preview_sprites[p["nombre"]] = pygame.transform.scale(
            sp.get("quieto", list(sp.values())[0]), (90, 105)
        )

    W_VOLVER, H_VOLVER = 238, 70
    btn_volver_personajes = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)
    btn_guardar = btn_volver_personajes
    btn_volver_config = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)
    btn_volver_creditos = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)
    btn_volver_niveles = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 75, W_VOLVER, H_VOLVER)

    def _cargar_scaled(nombre, w, h):
        img = cargar_boton(nombre)
        return pygame.transform.smoothscale(img, (w, h)) if img else None

    # Sprites botón «VOLVER» (mundos)
    spr_volver_normal = _cargar_scaled("mundos/boton-volver.png", W_VOLVER, H_VOLVER)
    spr_volver_hover = aclarar_boton(spr_volver_normal)
    spr_volver_semi = _cargar_scaled("mundos/boton-volver-semiapretado.png", W_VOLVER, H_VOLVER)
    spr_volver_apretado = _cargar_scaled("mundos/boton-volver-apretado.png", W_VOLVER, H_VOLVER)

    # Botones interactivos para Modo de Juego (Continuar vs Nueva Partida)
    W_MODO, H_MODO = 425, 100
    x_modo = (ANCHO_MENU - W_MODO) // 2
    btn_continuar = pygame.Rect(x_modo, (ALTO_MENU // 2) - 85, W_MODO, H_MODO)
    btn_nueva_partida = pygame.Rect(x_modo, (ALTO_MENU // 2) + 35, W_MODO, H_MODO)
    btn_volver_modo = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)

    spr_continuar_normal = _cargar_scaled("Menu/boton-continuar-cargar....png", W_MODO, H_MODO)
    spr_continuar_hover = aclarar_boton(spr_continuar_normal)
    spr_continuar_semi = _cargar_scaled("Menu/boton-continuar-cargar...-semiapretado.png", W_MODO, H_MODO)
    spr_continuar_apretado = _cargar_scaled("Menu/boton-continuar-cargar...-apretado.png", W_MODO, H_MODO)

    spr_nueva_modo_normal = _cargar_scaled("mundos/boton-nueva-partida-reiniciar....png", W_MODO, H_MODO)
    spr_nueva_modo_hover = aclarar_boton(spr_nueva_modo_normal)
    spr_nueva_modo_semi = _cargar_scaled("mundos/boton-nueva-partida-reiniciar...-semiapretado.png", W_MODO, H_MODO)
    spr_nueva_modo_apretado = _cargar_scaled("mundos/boton-nueva-partida-reiniciar...-apretado.png", W_MODO, H_MODO)

    # Sprites para Partidas Guardadas (mundos)
    spr_nueva_lista_normal = _cargar_scaled("mundos/boton-nueva-partida.png", W_VOLVER, H_VOLVER)
    spr_nueva_lista_hover = aclarar_boton(spr_nueva_lista_normal)
    spr_nueva_lista_semi = _cargar_scaled("mundos/boton-nueva-partida-semiapretado.png", W_VOLVER, H_VOLVER)
    spr_nueva_lista_apretado = _cargar_scaled("mundos/boton-nueva-partida-apretado.png", W_VOLVER, H_VOLVER)

    spr_nueva_primera_normal = _cargar_scaled("mundos/boton-nueva-partida.png", 272, 80)
    spr_nueva_primera_hover = aclarar_boton(spr_nueva_primera_normal)
    spr_nueva_primera_semi = _cargar_scaled("mundos/boton-nueva-partida-semiapretado.png", 272, 80)
    spr_nueva_primera_apretado = _cargar_scaled("mundos/boton-nueva-partida-apretado.png", 272, 80)

    spr_cargar_normal = _cargar_scaled("mundos/boton-cargar.png", 126, 37)
    spr_cargar_hover = aclarar_boton(spr_cargar_normal)
    spr_cargar_semi = _cargar_scaled("mundos/boton-cargar-semiapretado.png", 126, 37)
    spr_cargar_apretado = _cargar_scaled("mundos/boton-cargar-apretado.png", 126, 37)

    dict_sprites_tarjeta = {
        "cargar_normal": spr_cargar_normal,
        "cargar_hover": spr_cargar_hover,
        "cargar_semi": spr_cargar_semi,
        "cargar_apretado": spr_cargar_apretado,
    }

    # Sprites para teclas de Configuración (Controles)
    TAM_CTRL = 54
    spr_ctrl_w = _cargar_scaled("Controles/boton-w.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_a = _cargar_scaled("Controles/boton-a.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_s = _cargar_scaled("Controles/boton-s.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_d = _cargar_scaled("Controles/boton-d.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_arr = _cargar_scaled("Controles/boton-arriba.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_izq = _cargar_scaled("Controles/boton-izquierda.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_aba = _cargar_scaled("Controles/boton-abajo.png", TAM_CTRL, TAM_CTRL)
    spr_ctrl_der = _cargar_scaled("Controles/boton-derecha.png", TAM_CTRL, TAM_CTRL)

    # Geometría y variables para la Lista de Partidas Guardadas
    pagina_partidas = 0
    MAX_PARTIDAS_POR_PAGINA = 5
    rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
        obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU)
    )

    estado_actual = ESTADO_MENU_PRINCIPAL
    mundo_seleccionado = 1
    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                resp = mostrar_dialogo_guardar_salir(
                    pantalla, reloj,
                    niveles_desbloqueados=niveles_desbloqueados,
                    id_partida=partida_actual_id,
                    nombre_partida=partida_actual_nombre,
                )
                if resp != "cancelar":
                    ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    if spr_x_semi and spr_x_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, fondo_btn_x)
                    if estado_actual == ESTADO_MENU_PRINCIPAL:
                        resp = mostrar_dialogo_guardar_salir(
                            pantalla, reloj,
                            niveles_desbloqueados=niveles_desbloqueados,
                            id_partida=partida_actual_id,
                            nombre_partida=partida_actual_nombre,
                        )
                        if resp != "cancelar":
                            ejecutando = False
                    elif estado_actual == ESTADO_MODO_JUEGO:
                        estado_actual = ESTADO_MENU_PRINCIPAL
                    elif estado_actual == ESTADO_LISTA_PARTIDAS:
                        estado_actual = ESTADO_MODO_JUEGO
                    elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
                        estado_actual = ESTADO_MODO_JUEGO
                    elif estado_actual in (ESTADO_CONFIGURACION, ESTADO_CREDITOS, ESTADO_PERSONAJES):
                        estado_actual = ESTADO_MENU_PRINCIPAL
                    break

                if estado_actual == ESTADO_MENU_PRINCIPAL:
                    if btn_jugar.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_jugar, spr_jugar_semi, spr_jugar_apretado, fondo_limpio_btn)
                        estado_actual = ESTADO_MODO_JUEGO
                    elif btn_personajes.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_personajes, spr_personajes_semi, spr_personajes_apretado, fondo_limpio_btn)
                        estado_actual = ESTADO_PERSONAJES
                    elif btn_config.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_config, spr_opciones_semi, spr_opciones_apretado, fondo_limpio_btn)
                        estado_actual = ESTADO_CONFIGURACION
                    elif btn_salir.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_salir, spr_salir_semi, spr_salir_apretado, fondo_limpio_btn)
                        resp = mostrar_dialogo_guardar_salir(
                            pantalla, reloj,
                            niveles_desbloqueados=niveles_desbloqueados,
                            id_partida=partida_actual_id,
                            nombre_partida=partida_actual_nombre,
                        )
                        if resp != "cancelar":
                            ejecutando = False

                elif estado_actual == ESTADO_MODO_JUEGO:
                    if btn_continuar.collidepoint(evento.pos):
                        if spr_continuar_semi and spr_continuar_apretado:
                            animar_pulsacion_boton(pantalla, btn_continuar, spr_continuar_semi, spr_continuar_apretado, (30, 30, 30))
                        pagina_partidas = 0
                        estado_actual = ESTADO_LISTA_PARTIDAS
                    elif btn_nueva_partida.collidepoint(evento.pos):
                        if spr_nueva_modo_semi and spr_nueva_modo_apretado:
                            animar_pulsacion_boton(pantalla, btn_nueva_partida, spr_nueva_modo_semi, spr_nueva_modo_apretado, (30, 30, 30))
                        niveles_desbloqueados = crear_desbloqueados_inicial()
                        mundo_seleccionado = 1
                        partidas_guardadas = cargar_partidas()
                        nuevo_id = max([p["id"] for p in partidas_guardadas], default=0) + 1
                        partida_actual_id = nuevo_id
                        partida_actual_nombre = f"Partida {nuevo_id}"
                        estado_actual = ESTADO_SELECCION_NIVEL
                    elif btn_volver_modo.collidepoint(evento.pos):
                        if spr_volver_semi and spr_volver_apretado:
                            animar_pulsacion_boton(pantalla, btn_volver_modo, spr_volver_semi, spr_volver_apretado, (30, 30, 30))
                        estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual == ESTADO_LISTA_PARTIDAS:
                    partidas_guardadas = cargar_partidas()
                    rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
                        obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas_guardadas))
                    )
                    total_p = len(partidas_guardadas)
                    total_paginas = max(1, (total_p + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                    if pagina_partidas >= total_paginas:
                        pagina_partidas = max(0, total_paginas - 1)

                    if not partidas_guardadas:
                        if btn_iniciar_primera.collidepoint(evento.pos):
                            if spr_nueva_primera_semi and spr_nueva_primera_apretado:
                                animar_pulsacion_boton(pantalla, btn_iniciar_primera, spr_nueva_primera_semi, spr_nueva_primera_apretado, (255, 240, 195))
                            niveles_desbloqueados = crear_desbloqueados_inicial()
                            mundo_seleccionado = 1
                            partida_actual_id = 1
                            partida_actual_nombre = "Partida 1"
                            estado_actual = ESTADO_SELECCION_NIVEL
                    else:
                        inicio_idx = pagina_partidas * MAX_PARTIDAS_POR_PAGINA
                        fin_idx = inicio_idx + MAX_PARTIDAS_POR_PAGINA
                        partidas_pagina = partidas_guardadas[inicio_idx:fin_idx]

                        accion_ejecutada = False
                        for idx_slot, p in enumerate(partidas_pagina):
                            r_card, _, r_btn_cargar, r_btn_borrar, _ = obtener_geometria_tarjeta_partida(
                                rect_panel_partidas, idx_slot
                            )
                            # Clic en botón BORRAR (dispara confirmación previa)
                            if r_btn_borrar.collidepoint(evento.pos):
                                if mostrar_dialogo_confirmar_borrado(pantalla, reloj, p):
                                    eliminar_partida(p["id"])
                                    if partida_actual_id == p["id"]:
                                        partida_actual_id = None
                                        partida_actual_nombre = None
                                        niveles_desbloqueados = crear_desbloqueados_inicial()
                                    # Recalcular páginas inmediatamente para reorganizar la vista
                                    nuevas_p = cargar_partidas()
                                    nuevas_total_pag = max(1, (len(nuevas_p) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                                    if pagina_partidas >= nuevas_total_pag:
                                        pagina_partidas = max(0, nuevas_total_pag - 1)
                                accion_ejecutada = True
                                break
                            # Clic en botón CARGAR o sobre la tarjeta
                            elif r_btn_cargar.collidepoint(evento.pos) or r_card.collidepoint(evento.pos):
                                if spr_cargar_semi and spr_cargar_apretado:
                                    animar_pulsacion_boton(pantalla, r_btn_cargar, spr_cargar_semi, spr_cargar_apretado, (253, 246, 233))
                                niveles_desbloqueados = copy.deepcopy(p["niveles_desbloqueados"])
                                partida_actual_id = p["id"]
                                partida_actual_nombre = p["nombre"]
                                mundo_seleccionado = p["mundo_max"]
                                estado_actual = ESTADO_SELECCION_NIVEL
                                accion_ejecutada = True
                                break

                        if not accion_ejecutada:
                            if total_paginas > 1:
                                btn_pag_ant = pygame.Rect(rect_panel_partidas.centerx - 130, rect_panel_partidas.bottom + 8, 36, 32)
                                btn_pag_sig = pygame.Rect(rect_panel_partidas.centerx + 94, rect_panel_partidas.bottom + 8, 36, 32)
                                if btn_pag_ant.collidepoint(evento.pos) and pagina_partidas > 0:
                                    pagina_partidas -= 1
                                elif btn_pag_sig.collidepoint(evento.pos) and pagina_partidas < total_paginas - 1:
                                    pagina_partidas += 1

                            if btn_nueva_desde_lista.collidepoint(evento.pos):
                                if spr_nueva_lista_semi and spr_nueva_lista_apretado:
                                    animar_pulsacion_boton(pantalla, btn_nueva_desde_lista, spr_nueva_lista_semi, spr_nueva_lista_apretado, (255, 240, 195))
                                niveles_desbloqueados = crear_desbloqueados_inicial()
                                mundo_seleccionado = 1
                                partidas_actuales = cargar_partidas()
                                nuevo_id = max([p["id"] for p in partidas_actuales], default=0) + 1
                                partida_actual_id = nuevo_id
                                partida_actual_nombre = f"Partida {nuevo_id}"
                                estado_actual = ESTADO_SELECCION_NIVEL

                    if btn_volver_partidas.collidepoint(evento.pos):
                        if spr_volver_semi and spr_volver_apretado:
                            animar_pulsacion_boton(pantalla, btn_volver_partidas, spr_volver_semi, spr_volver_apretado, (255, 240, 195))
                        estado_actual = ESTADO_MODO_JUEGO

                elif estado_actual == ESTADO_PERSONAJES:
                    if btn_volver_personajes.collidepoint(evento.pos) or btn_guardar.collidepoint(evento.pos):
                        if spr_volver_semi and spr_volver_apretado and btn_volver_personajes.collidepoint(evento.pos):
                            animar_pulsacion_boton(pantalla, btn_volver_personajes, spr_volver_semi, spr_volver_apretado, (30, 30, 30))
                        estado_actual = ESTADO_MENU_PRINCIPAL
                        break

                    cols, w_box, h_box, gap = 5, 52, 40, 10
                    grid_w = cols * w_box + (cols - 1) * gap
                    x_p1, x_p2, y_grid_p = (ANCHO_MENU // 4) - (grid_w // 2), (3 * ANCHO_MENU // 4) - (grid_w // 2), 245

                    for idx, p_info in enumerate(PERSONAJES_DISPONIBLES):
                        r, c = idx // cols, idx % cols
                        r1 = pygame.Rect(x_p1 + c * (w_box + gap), y_grid_p + r * (h_box + gap), w_box, h_box)
                        r2 = pygame.Rect(x_p2 + c * (w_box + gap), y_grid_p + r * (h_box + gap), w_box, h_box)
                        if r1.collidepoint(evento.pos): color_p1 = p_info["nombre"]
                        if r2.collidepoint(evento.pos): color_p2 = p_info["nombre"]

                elif estado_actual == ESTADO_CONFIGURACION:
                    if btn_volver_config.collidepoint(evento.pos):
                        if spr_volver_semi and spr_volver_apretado:
                            animar_pulsacion_boton(pantalla, btn_volver_config, spr_volver_semi, spr_volver_apretado, (30, 30, 30))
                        estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual == ESTADO_CREDITOS:
                    if btn_volver_creditos.collidepoint(evento.pos):
                        if spr_volver_semi and spr_volver_apretado:
                            animar_pulsacion_boton(pantalla, btn_volver_creditos, spr_volver_semi, spr_volver_apretado, (30, 30, 30))
                        estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
                    if btn_volver_niveles.collidepoint(evento.pos):
                        if spr_volver_semi and spr_volver_apretado:
                            animar_pulsacion_boton(pantalla, btn_volver_niveles, spr_volver_semi, spr_volver_apretado, (30, 30, 30))
                        estado_actual = ESTADO_MODO_JUEGO
                        break
                    rect_panel, tabs_info, rects_cards = obtener_geometria_menu(ANCHO_MENU, ALTO_MENU)
                    tab_presionada = False
                    for m, t_data in tabs_info.items():
                        if t_data["rect_click"].collidepoint(evento.pos):
                            mundo_seleccionado = m
                            tab_presionada = True
                            break

                    if not tab_presionada:
                        for idx_nivel, rect_c in enumerate(rects_cards):
                            desbloqueado = niveles_desbloqueados[mundo_seleccionado][idx_nivel]
                            if desbloqueado and rect_c.collidepoint(evento.pos):
                                m_idx, n_idx = mundo_seleccionado, idx_nivel

                                mantenimiento = True
                                while mantenimiento:
                                    mecanicas = obtener_mecanicas_nivel(m_idx, n_idx + 1)
                                    res = iniciar_mundo(
                                        mecanicas,
                                        numero_nivel=n_idx + 1,
                                        color_p1=color_p1,
                                        color_p2=color_p2,
                                        mundo=m_idx,
                                        niveles_desbloqueados=niveles_desbloqueados,
                                        partida_id=partida_actual_id,
                                        partida_nombre=partida_actual_nombre,
                                    )
                                    if res == "siguiente":
                                        if n_idx + 1 < 5:
                                            n_idx += 1
                                            niveles_desbloqueados[m_idx][n_idx] = True
                                        elif m_idx + 1 <= 3:
                                            m_idx += 1
                                            n_idx = 0
                                            niveles_desbloqueados[m_idx][n_idx] = True
                                            mundo_seleccionado = m_idx
                                        else:
                                            mantenimiento = False
                                            estado_actual = ESTADO_SELECCION_NIVEL
                                        guardar_partida(
                                            niveles_desbloqueados,
                                            id_partida=partida_actual_id,
                                            nombre_partida=partida_actual_nombre,
                                        )
                                    elif res == "reiniciar":
                                        continue
                                    elif res == "menu":
                                        mantenimiento = False
                                        estado_actual = ESTADO_SELECCION_NIVEL
                                    else:
                                        mantenimiento = False
                                        ejecutando = False
                                break

            elif evento.type == pygame.MOUSEWHEEL:
                if estado_actual == ESTADO_LISTA_PARTIDAS:
                    total_pag = max(1, (len(cargar_partidas()) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                    if total_pag > 1:
                        if evento.y > 0 and pagina_partidas > 0:
                            pagina_partidas -= 1
                        elif evento.y < 0 and pagina_partidas < total_pag - 1:
                            pagina_partidas += 1

        pantalla.fill((30, 30, 30))

        if estado_actual == ESTADO_MENU_PRINCIPAL:
            titulo = fuente_pixel_titulo.render("PICO PARK", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 70)))

            pos_mouse = pygame.mouse.get_pos()
            botones_menu_datos = [
                (btn_jugar, spr_jugar_normal, spr_jugar_hover),
                (btn_personajes, spr_personajes_normal, spr_personajes_hover),
                (btn_config, spr_opciones_normal, spr_opciones_hover),
                (btn_salir, spr_salir_normal, spr_salir_hover),
            ]
            for btn, spr_n, spr_h in botones_menu_datos:
                spr_dib = spr_h if (btn.collidepoint(pos_mouse) and spr_h) else spr_n
                if spr_dib:
                    pantalla.blit(spr_dib, btn)

        elif estado_actual == ESTADO_MODO_JUEGO:
            pos_mouse = pygame.mouse.get_pos()

            titulo = fuente_pixel_titulo.render("MODO DE JUEGO", True, (255, 230, 100))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 85)))

            subt = fuente_subtitulo.render("Selecciona cómo deseas comenzar tu aventura", True, (215, 215, 225))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 135)))

            # Botón Continuar (Menu/boton-continuar-cargar...)
            hov_c = btn_continuar.collidepoint(pos_mouse)
            spr_c = spr_continuar_hover if (hov_c and spr_continuar_hover) else spr_continuar_normal
            if spr_c:
                pantalla.blit(spr_c, btn_continuar)
            else:
                col_c = (55, 165, 88) if hov_c else (42, 138, 72)
                pygame.draw.rect(pantalla, col_c, btn_continuar, border_radius=16)
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_c else (160, 230, 180), btn_continuar, width=3 if hov_c else 2, border_radius=16)
                t_cont_tit = fuente_pixel_btn_grande.render("CONTINUAR", True, (255, 255, 255))
                pantalla.blit(t_cont_tit, t_cont_tit.get_rect(center=(btn_continuar.centerx, btn_continuar.centery)))

            # Botón Nueva Partida (mundos/boton-nueva-partida-reiniciar...)
            hov_n = btn_nueva_partida.collidepoint(pos_mouse)
            spr_n = spr_nueva_modo_hover if (hov_n and spr_nueva_modo_hover) else spr_nueva_modo_normal
            if spr_n:
                pantalla.blit(spr_n, btn_nueva_partida)
            else:
                col_n = (215, 120, 48) if hov_n else (185, 100, 38)
                pygame.draw.rect(pantalla, col_n, btn_nueva_partida, border_radius=16)
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_n else (245, 205, 150), btn_nueva_partida, width=3 if hov_n else 2, border_radius=16)
                t_nueva_tit = fuente_pixel_btn_grande.render("NUEVA PARTIDA", True, (255, 255, 255))
                pantalla.blit(t_nueva_tit, t_nueva_tit.get_rect(center=(btn_nueva_partida.centerx, btn_nueva_partida.centery)))

            # Botón Volver al Menú (mundos/boton-volver)
            hov_v = btn_volver_modo.collidepoint(pos_mouse)
            spr_v = spr_volver_hover if (hov_v and spr_volver_hover) else spr_volver_normal
            if spr_v:
                pantalla.blit(spr_v, btn_volver_modo)
            else:
                col_v = (85, 85, 98) if hov_v else (60, 60, 70)
                pygame.draw.rect(pantalla, col_v, btn_volver_modo, border_radius=10)
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_v else (140, 140, 155), btn_volver_modo, width=2, border_radius=10)
                t_v = fuente_pixel_btn.render("VOLVER AL MENU", True, (255, 255, 255))
                pantalla.blit(t_v, t_v.get_rect(center=btn_volver_modo.center))

        elif estado_actual == ESTADO_LISTA_PARTIDAS:
            ANCHO_MENU = pantalla.get_width()
            ALTO_MENU = pantalla.get_height()
            pos_mouse = pygame.mouse.get_pos()
            partidas = cargar_partidas()

            # Fondo crema uniforme limpio sin franja de suelo
            pantalla.fill((255, 240, 195))

            rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
                obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas))
            )

            # Título con tipografía retro 04B_30 y subtítulo descriptivo
            titulo = fuente_pixel_titulo.render("PARTIDAS JUGADAS", True, (60, 45, 35))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 48)))

            subt = fuente_subtitulo.render("Selecciona tu partida guardada para continuar", True, (115, 95, 80))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 84)))

            # Panel contenedor en crema suave con borde cálido
            pygame.draw.rect(pantalla, COL_PANEL, rect_panel_partidas, border_radius=18)
            pygame.draw.rect(pantalla, COL_BORDE_PANEL, rect_panel_partidas, width=3, border_radius=18)

            if not partidas:
                t_sin = fuente_subtitulo.render("No hay partidas guardadas todavía", True, (60, 45, 35))
                pantalla.blit(t_sin, t_sin.get_rect(center=(rect_panel_partidas.centerx, rect_panel_partidas.centery - 45)))

                t_sin2 = fuente_texto.render("Al jugar y guardar el nivel antes de salir, tus partidas aparecerán aquí.", True, (120, 105, 90))
                pantalla.blit(t_sin2, t_sin2.get_rect(center=(rect_panel_partidas.centerx, rect_panel_partidas.centery - 10)))

                hov_prim = btn_iniciar_primera.collidepoint(pos_mouse)
                spr_prim = spr_nueva_primera_hover if (hov_prim and spr_nueva_primera_hover) else spr_nueva_primera_normal
                if spr_prim:
                    pantalla.blit(spr_prim, btn_iniciar_primera)
                else:
                    col_prim = (82, 194, 114) if hov_prim else (68, 172, 98)
                    pygame.draw.rect(pantalla, col_prim, btn_iniciar_primera, border_radius=12)
                    pygame.draw.rect(pantalla, (45, 130, 70), btn_iniciar_primera, width=2, border_radius=12)
                    t_btn_prim = fuente_pixel_btn.render("COMENZAR NUEVA PARTIDA", True, (255, 255, 255))
                    pantalla.blit(t_btn_prim, t_btn_prim.get_rect(center=btn_iniciar_primera.center))
            else:
                total_paginas = max(1, (len(partidas) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                if pagina_partidas >= total_paginas:
                    pagina_partidas = max(0, total_paginas - 1)

                inicio_idx = pagina_partidas * MAX_PARTIDAS_POR_PAGINA
                fin_idx = inicio_idx + MAX_PARTIDAS_POR_PAGINA
                partidas_pagina = partidas[inicio_idx:fin_idx]

                fuentes_tarjetas = {
                    "titulo_card": fuente_card_titulo,
                    "sub_card": fuente_card_sub,
                    "btn_card": fuente_pixel_card_btn,
                    "badge": fuente_pixel_badge,
                    "btn": fuente_pixel_badge,
                    "texto": fuente_texto,
                    "sub_btn": fuente_sub_btn,
                }

                for idx_slot, p in enumerate(partidas_pagina):
                    dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel_partidas, pos_mouse, fuentes_tarjetas, sprites_botones=dict_sprites_tarjeta)

                # Indicador de paginación si hay más de 1 página
                if total_paginas > 1:
                    btn_pag_ant = pygame.Rect(rect_panel_partidas.centerx - 130, rect_panel_partidas.bottom + 8, 36, 32)
                    btn_pag_sig = pygame.Rect(rect_panel_partidas.centerx + 94, rect_panel_partidas.bottom + 8, 36, 32)

                    # Botón anterior
                    hov_ant = btn_pag_ant.collidepoint(pos_mouse) and pagina_partidas > 0
                    col_ant = (255, 255, 255) if hov_ant else ((253, 246, 233) if pagina_partidas > 0 else (240, 230, 215))
                    borde_ant = (180, 145, 110) if hov_ant else (205, 180, 150)
                    pygame.draw.rect(pantalla, col_ant, btn_pag_ant, border_radius=8)
                    pygame.draw.rect(pantalla, borde_ant, btn_pag_ant, width=2 if hov_ant else 1, border_radius=8)
                    t_ant = fuente_texto.render("◀", True, (60, 45, 35) if pagina_partidas > 0 else (175, 160, 145))
                    pantalla.blit(t_ant, t_ant.get_rect(center=btn_pag_ant.center))

                    # Texto de página
                    t_pag = fuente_texto.render(f"Página {pagina_partidas + 1} de {total_paginas}", True, (60, 45, 35))
                    pantalla.blit(t_pag, t_pag.get_rect(center=(rect_panel_partidas.centerx - 18, rect_panel_partidas.bottom + 24)))

                    # Botón siguiente
                    hov_sig = btn_pag_sig.collidepoint(pos_mouse) and pagina_partidas < total_paginas - 1
                    col_sig = (255, 255, 255) if hov_sig else ((253, 246, 233) if pagina_partidas < total_paginas - 1 else (240, 230, 215))
                    borde_sig = (180, 145, 110) if hov_sig else (205, 180, 150)
                    pygame.draw.rect(pantalla, col_sig, btn_pag_sig, border_radius=8)
                    pygame.draw.rect(pantalla, borde_sig, btn_pag_sig, width=2 if hov_sig else 1, border_radius=8)
                    t_sig = fuente_texto.render("▶", True, (60, 45, 35) if pagina_partidas < total_paginas - 1 else (175, 160, 145))
                    pantalla.blit(t_sig, t_sig.get_rect(center=btn_pag_sig.center))

            # Botón «VOLVER» centrado al pie de la pantalla (mundos/boton-volver)
            hov_vp = btn_volver_partidas.collidepoint(pos_mouse)
            spr_vp = spr_volver_hover if (hov_vp and spr_volver_hover) else spr_volver_normal
            if spr_vp:
                pantalla.blit(spr_vp, btn_volver_partidas)
            else:
                col_vp = (255, 255, 255) if hov_vp else (253, 246, 233)
                borde_vp = (165, 135, 105) if hov_vp else (195, 168, 138)
                pygame.draw.rect(pantalla, col_vp, btn_volver_partidas, border_radius=12)
                pygame.draw.rect(pantalla, borde_vp, btn_volver_partidas, width=2, border_radius=12)
                t_vp = fuente_pixel_btn.render("VOLVER", True, (60, 45, 35))
                pantalla.blit(t_vp, t_vp.get_rect(center=btn_volver_partidas.center))

            if partidas:
                # Botón «NUEVA PARTIDA» ubicado al lado de «VOLVER», centrados juntos (mundos/boton-nueva-partida)
                hov_nd = btn_nueva_desde_lista.collidepoint(pos_mouse)
                spr_nd = spr_nueva_lista_hover if (hov_nd and spr_nueva_lista_hover) else spr_nueva_lista_normal
                if spr_nd:
                    pantalla.blit(spr_nd, btn_nueva_desde_lista)
                else:
                    col_nd = (245, 140, 55) if hov_nd else (225, 120, 38)
                    borde_nd = (255, 255, 255) if hov_nd else (180, 90, 25)
                    pygame.draw.rect(pantalla, col_nd, btn_nueva_desde_lista, border_radius=12)
                    pygame.draw.rect(pantalla, borde_nd, btn_nueva_desde_lista, width=2, border_radius=12)
                    t_nd = fuente_pixel_btn.render("NUEVA PARTIDA", True, (255, 255, 255))
                    pantalla.blit(t_nd, t_nd.get_rect(center=btn_nueva_desde_lista.center))

        elif estado_actual == ESTADO_PERSONAJES:
            pos_mouse = pygame.mouse.get_pos()
            titulo = fuente_pixel_titulo.render("PERSONALIZACION DE PERSONAJES", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 45)))

            t_p1 = fuente_subtitulo.render(f"Personaje 1 ({color_p1})", True, (255, 255, 255))
            pantalla.blit(t_p1, t_p1.get_rect(center=(ANCHO_MENU // 4, 90)))
            pj1_img = preview_sprites.get(color_p1)
            if pj1_img:
                pantalla.blit(pj1_img, pj1_img.get_rect(center=(ANCHO_MENU // 4, 175)))

            t_p2 = fuente_subtitulo.render(f"Personaje 2 ({color_p2})", True, (255, 255, 255))
            pantalla.blit(t_p2, t_p2.get_rect(center=(3 * ANCHO_MENU // 4, 90)))
            pj2_img = preview_sprites.get(color_p2)
            if pj2_img:
                pantalla.blit(pj2_img, pj2_img.get_rect(center=(3 * ANCHO_MENU // 4, 175)))

            cols, w_box, h_box, gap = 5, 52, 40, 10
            grid_w = cols * w_box + (cols - 1) * gap
            x_p1, x_p2, y_grid_p = (ANCHO_MENU // 4) - (grid_w // 2), (3 * ANCHO_MENU // 4) - (grid_w // 2), 245

            for idx, p_info in enumerate(PERSONAJES_DISPONIBLES):
                r, c = idx // cols, idx % cols
                r1 = pygame.Rect(x_p1 + c * (w_box + gap), y_grid_p + r * (h_box + gap), w_box, h_box)
                pygame.draw.rect(pantalla, p_info["color"], r1, border_radius=6)
                if p_info["nombre"] == color_p1:
                    pygame.draw.rect(pantalla, (255, 255, 255), r1, 3, border_radius=6)

                r2 = pygame.Rect(x_p2 + c * (w_box + gap), y_grid_p + r * (h_box + gap), w_box, h_box)
                pygame.draw.rect(pantalla, p_info["color"], r2, border_radius=6)
                if p_info["nombre"] == color_p2:
                    pygame.draw.rect(pantalla, (255, 255, 255), r2, 3, border_radius=6)

            # Botón Volver al Menú (mundos/boton-volver)
            hov_vpj = btn_volver_personajes.collidepoint(pos_mouse)
            spr_vpj = spr_volver_hover if (hov_vpj and spr_volver_hover) else spr_volver_normal
            if spr_vpj:
                pantalla.blit(spr_vpj, btn_volver_personajes)
            else:
                pygame.draw.rect(pantalla, (50, 150, 50), btn_volver_personajes, border_radius=8)
                pygame.draw.rect(pantalla, (255, 255, 255), btn_volver_personajes, 2, border_radius=8)
                t_guardar = fuente_pixel_btn.render("VOLVER", True, (255, 255, 255))
                pantalla.blit(t_guardar, t_guardar.get_rect(center=btn_volver_personajes.center))

        elif estado_actual == ESTADO_CONFIGURACION:
            pos_mouse = pygame.mouse.get_pos()

            titulo = fuente_pixel_titulo.render("CONFIGURACION DE CONTROLES", True, (255, 230, 100))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 55)))

            subt = fuente_subtitulo.render("Teclas de movimiento y acción para cada jugador", True, (215, 215, 225))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 98)))

            # Ancho y alto de los paneles de cada jugador
            w_card_cfg = min(460, (ANCHO_MENU // 2) - 50)
            h_card_cfg = 340
            y_card_cfg = 135
            gap_card_cfg = 40

            x_card_p1 = (ANCHO_MENU // 2) - w_card_cfg - (gap_card_cfg // 2)
            x_card_p2 = (ANCHO_MENU // 2) + (gap_card_cfg // 2)

            rect_card_p1 = pygame.Rect(x_card_p1, y_card_cfg, w_card_cfg, h_card_cfg)
            rect_card_p2 = pygame.Rect(x_card_p2, y_card_cfg, w_card_cfg, h_card_cfg)

            # --- Panel Jugador 1 ---
            pygame.draw.rect(pantalla, (42, 45, 58), rect_card_p1, border_radius=16)
            pygame.draw.rect(pantalla, (124, 231, 255), rect_card_p1, width=3, border_radius=16)

            t_tit_p1 = fuente_pixel_btn_grande.render(f"JUGADOR 1 ({color_p1.upper()})", True, (124, 231, 255))
            pantalla.blit(t_tit_p1, t_tit_p1.get_rect(center=(rect_card_p1.centerx, rect_card_p1.top + 30)))

            # Teclado WASD centrado con botones oficiales de Controles
            tc_w, tc_gap = TAM_CTRL, 8
            x_wasd_centro = rect_card_p1.centerx
            y_wasd_top = rect_card_p1.top + 65

            r_w = pygame.Rect(x_wasd_centro - (tc_w // 2), y_wasd_top, tc_w, tc_w)
            r_s = pygame.Rect(x_wasd_centro - (tc_w // 2), y_wasd_top + tc_w + tc_gap, tc_w, tc_w)
            r_a = pygame.Rect(r_s.left - tc_w - tc_gap, y_wasd_top + tc_w + tc_gap, tc_w, tc_w)
            r_d = pygame.Rect(r_s.right + tc_gap, y_wasd_top + tc_w + tc_gap, tc_w, tc_w)

            if spr_ctrl_w: pantalla.blit(spr_ctrl_w, r_w)
            if spr_ctrl_a: pantalla.blit(spr_ctrl_a, r_a)
            if spr_ctrl_s: pantalla.blit(spr_ctrl_s, r_s)
            if spr_ctrl_d: pantalla.blit(spr_ctrl_d, r_d)

            lbl_p1_mov = fuente_texto.render("A / D : Moverse", True, (230, 230, 230))
            lbl_p1_sal = fuente_texto.render("W : Saltar", True, (255, 255, 255))
            lbl_p1_sub = fuente_texto.render("S : Nadar / Sumergirse (Agua)", True, (190, 210, 225))
            pantalla.blit(lbl_p1_mov, lbl_p1_mov.get_rect(center=(rect_card_p1.centerx, r_s.bottom + 32)))
            pantalla.blit(lbl_p1_sal, lbl_p1_sal.get_rect(center=(rect_card_p1.centerx, r_s.bottom + 60)))
            pantalla.blit(lbl_p1_sub, lbl_p1_sub.get_rect(center=(rect_card_p1.centerx, r_s.bottom + 88)))

            # --- Panel Jugador 2 ---
            pygame.draw.rect(pantalla, (42, 45, 58), rect_card_p2, border_radius=16)
            pygame.draw.rect(pantalla, (200, 160, 255), rect_card_p2, width=3, border_radius=16)

            t_tit_p2 = fuente_pixel_btn_grande.render(f"JUGADOR 2 ({color_p2.upper()})", True, (200, 160, 255))
            pantalla.blit(t_tit_p2, t_tit_p2.get_rect(center=(rect_card_p2.centerx, rect_card_p2.top + 30)))

            # Teclado Flechas centrado con botones oficiales de Controles
            x_arr_centro = rect_card_p2.centerx
            y_arr_top = rect_card_p2.top + 65

            r_arr = pygame.Rect(x_arr_centro - (tc_w // 2), y_arr_top, tc_w, tc_w)
            r_aba = pygame.Rect(x_arr_centro - (tc_w // 2), y_arr_top + tc_w + tc_gap, tc_w, tc_w)
            r_izq = pygame.Rect(r_aba.left - tc_w - tc_gap, y_arr_top + tc_w + tc_gap, tc_w, tc_w)
            r_der = pygame.Rect(r_aba.right + tc_gap, y_arr_top + tc_w + tc_gap, tc_w, tc_w)

            if spr_ctrl_arr: pantalla.blit(spr_ctrl_arr, r_arr)
            if spr_ctrl_izq: pantalla.blit(spr_ctrl_izq, r_izq)
            if spr_ctrl_aba: pantalla.blit(spr_ctrl_aba, r_aba)
            if spr_ctrl_der: pantalla.blit(spr_ctrl_der, r_der)

            lbl_p2_mov = fuente_texto.render("Flechas Izq / Der : Moverse", True, (230, 230, 230))
            lbl_p2_sal = fuente_texto.render("Flecha Arriba : Saltar", True, (255, 255, 255))
            lbl_p2_sub = fuente_texto.render("Flecha Abajo : Nadar / Sumergirse (Agua)", True, (220, 205, 235))
            pantalla.blit(lbl_p2_mov, lbl_p2_mov.get_rect(center=(rect_card_p2.centerx, r_aba.bottom + 32)))
            pantalla.blit(lbl_p2_sal, lbl_p2_sal.get_rect(center=(rect_card_p2.centerx, r_aba.bottom + 60)))
            pantalla.blit(lbl_p2_sub, lbl_p2_sub.get_rect(center=(rect_card_p2.centerx, r_aba.bottom + 88)))

            # Botón Volver al Menú (mundos/boton-volver)
            hov_vcfg = btn_volver_config.collidepoint(pos_mouse)
            spr_vcfg = spr_volver_hover if (hov_vcfg and spr_volver_hover) else spr_volver_normal
            if spr_vcfg:
                pantalla.blit(spr_vcfg, btn_volver_config)

        elif estado_actual == ESTADO_CREDITOS:
            pos_mouse = pygame.mouse.get_pos()
            titulo = fuente_pixel_titulo.render("CREDITOS", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            cred = fuente_texto.render("Desarrollado para Pico Park Fan Project", True, (200, 200, 200))
            pantalla.blit(cred, cred.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2)))

            # Botón Volver al Menú (mundos/boton-volver)
            hov_vcr = btn_volver_creditos.collidepoint(pos_mouse)
            spr_vcr = spr_volver_hover if (hov_vcr and spr_volver_hover) else spr_volver_normal
            if spr_vcr:
                pantalla.blit(spr_vcr, btn_volver_creditos)

        elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            pos_mouse = pygame.mouse.get_pos()
            dibujar_menu_niveles(
                pantalla,
                mundo_seleccionado,
                niveles_desbloqueados,
                pos_mouse,
                fuentes_menu,
            )

            # Botón Volver al Modo de Juego (mundos/boton-volver)
            hov_vn = btn_volver_niveles.collidepoint(pos_mouse)
            spr_vn = spr_volver_hover if (hov_vn and spr_volver_hover) else spr_volver_normal
            if spr_vn:
                pantalla.blit(spr_vn, btn_volver_niveles)

        try:
            fondo_btn_x = pantalla.subsurface(rect_btn_x).copy()
        except Exception:
            pass

        pos_mouse = pygame.mouse.get_pos()
        hov_x = rect_btn_x.collidepoint(pos_mouse)
        spr_x_dib = spr_x_hover if (hov_x and spr_x_hover) else spr_x_normal
        if spr_x_dib: pantalla.blit(spr_x_dib, rect_btn_x)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()