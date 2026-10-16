import sys
import copy
import pygame

from sprites import ANCHO, ALTO, FPS, aplicar_tinta, cargar_sprites
from pantalla import iniciar_mundo, cargar_boton, animar_pulsacion_boton
from menu_niveles import (
    dibujar_menu_niveles,
    obtener_geometria_menu,
    obtener_mecanicas_nivel,
)
from guardado import (
    crear_desbloqueados_inicial,
    cargar_partidas,
    guardar_partida,
    mostrar_dialogo_guardar_salir,
)

ESTADO_MENU_PRINCIPAL = "principal"
ESTADO_MODO_JUEGO = "modo_juego"
ESTADO_LISTA_PARTIDAS = "lista_partidas"
ESTADO_CONFIGURACION = "configuracion"
ESTADO_CREDITOS = "creditos"
ESTADO_PERSONAJES = "personajes"
ESTADO_SELECCION_MUNDO = "seleccion_mundo"
ESTADO_SELECCION_NIVEL = "seleccion_nivel"

MECANICAS_MUNDOS = {
    1: ["caja"],
    2: ["soga"],
    3: ["agua"],
}

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
    fuente_titulo = pygame.font.Font(None, 55)
    fuente_subtitulo = pygame.font.Font(None, 36)
    fuente_btn = pygame.font.Font(None, 32)
    fuente_texto = pygame.font.Font(None, 26)
    fuente_sub_btn = pygame.font.Font(None, 22)
    fuentes_menu = {
        "titulo": fuente_titulo,
        "tab": pygame.font.Font(None, 34),
        "card": pygame.font.Font(None, 28),
    }

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
    spr_jugar_semi = _cargar_menu_btn("jugar-preapretado.png")
    spr_jugar_apretado = _cargar_menu_btn("jugar-apretado.png")

    spr_personajes_normal = _cargar_menu_btn("personajes.png")
    spr_personajes_semi = _cargar_menu_btn("personajes-preapretado.png")
    spr_personajes_apretado = _cargar_menu_btn("personajes-apretado.png")

    spr_opciones_normal = _cargar_menu_btn("opciones.png")
    spr_opciones_semi = _cargar_menu_btn("opciones-preapretado.png")
    spr_opciones_apretado = _cargar_menu_btn("opciones-apretado.png")

    spr_salir_normal = _cargar_menu_btn("salir.png")
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

    btn_guardar = pygame.Rect((ANCHO_MENU - 220) // 2, ALTO_MENU - 80, 220, 50)

    # Botones interactivos para Modo de Juego (Continuar vs Nueva Partida)
    W_MODO, H_MODO = 440, 95
    x_modo = (ANCHO_MENU - W_MODO) // 2
    btn_continuar = pygame.Rect(x_modo, (ALTO_MENU // 2) - 80, W_MODO, H_MODO)
    btn_nueva_partida = pygame.Rect(x_modo, (ALTO_MENU // 2) + 35, W_MODO, H_MODO)
    btn_volver_modo = pygame.Rect((ANCHO_MENU - 220) // 2, ALTO_MENU - 75, 220, 50)

    # Geometría y botones para la Lista de Partidas Guardadas
    ancho_panel_p = min(740, ANCHO_MENU - 80)
    alto_panel_p = min(420, ALTO_MENU - 190)
    rect_panel_partidas = pygame.Rect((ANCHO_MENU - ancho_panel_p) // 2, 115, ancho_panel_p, alto_panel_p)
    btn_iniciar_primera = pygame.Rect(rect_panel_partidas.centerx - 170, rect_panel_partidas.centery + 35, 340, 52)
    btn_volver_partidas = pygame.Rect((ANCHO_MENU - 460) // 2, ALTO_MENU - 65, 210, 48)
    btn_nueva_desde_lista = pygame.Rect((ANCHO_MENU - 460) // 2 + 250, ALTO_MENU - 65, 210, 48)

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
                        estado_actual = ESTADO_LISTA_PARTIDAS
                    elif btn_nueva_partida.collidepoint(evento.pos):
                        niveles_desbloqueados = crear_desbloqueados_inicial()
                        mundo_seleccionado = 1
                        partidas_guardadas = cargar_partidas()
                        nuevo_id = max([p["id"] for p in partidas_guardadas], default=0) + 1
                        partida_actual_id = nuevo_id
                        partida_actual_nombre = f"Partida {nuevo_id}"
                        estado_actual = ESTADO_SELECCION_NIVEL
                    elif btn_volver_modo.collidepoint(evento.pos):
                        estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual == ESTADO_LISTA_PARTIDAS:
                    partidas_guardadas = cargar_partidas()
                    if not partidas_guardadas:
                        if btn_iniciar_primera.collidepoint(evento.pos):
                            niveles_desbloqueados = crear_desbloqueados_inicial()
                            mundo_seleccionado = 1
                            partida_actual_id = 1
                            partida_actual_nombre = "Partida 1"
                            estado_actual = ESTADO_SELECCION_NIVEL
                    else:
                        for idx_p, p in enumerate(partidas_guardadas[:5]):
                            r_card = pygame.Rect(rect_panel_partidas.left + 20, rect_panel_partidas.top + 20 + idx_p * (72 + 12), rect_panel_partidas.width - 40, 72)
                            if r_card.collidepoint(evento.pos):
                                niveles_desbloqueados = copy.deepcopy(p["niveles_desbloqueados"])
                                partida_actual_id = p["id"]
                                partida_actual_nombre = p["nombre"]
                                mundo_seleccionado = p["mundo_max"]
                                estado_actual = ESTADO_SELECCION_NIVEL
                                break
                        if btn_nueva_desde_lista.collidepoint(evento.pos):
                            niveles_desbloqueados = crear_desbloqueados_inicial()
                            mundo_seleccionado = 1
                            nuevo_id = max([p["id"] for p in partidas_guardadas], default=0) + 1
                            partida_actual_id = nuevo_id
                            partida_actual_nombre = f"Partida {nuevo_id}"
                            estado_actual = ESTADO_SELECCION_NIVEL
                    if btn_volver_partidas.collidepoint(evento.pos):
                        estado_actual = ESTADO_MODO_JUEGO

                elif estado_actual == ESTADO_PERSONAJES:
                    if btn_guardar.collidepoint(evento.pos):
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


                elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
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
                                    elif res == "reiniciar":
                                        continue
                                    elif res == "menu":
                                        mantenimiento = False
                                        estado_actual = ESTADO_SELECCION_NIVEL
                                    else:
                                        mantenimiento = False
                                        ejecutando = False
                                break

        pantalla.fill((30, 30, 30))

        if estado_actual == ESTADO_MENU_PRINCIPAL:
            titulo = fuente_titulo.render("PICO PARK", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 70)))

            botones_menu_datos = [
                (btn_jugar, spr_jugar_normal),
                (btn_personajes, spr_personajes_normal),
                (btn_config, spr_opciones_normal),
                (btn_salir, spr_salir_normal),
            ]
            for btn, spr in botones_menu_datos:
                if spr:
                    pantalla.blit(spr, btn)

        elif estado_actual == ESTADO_MODO_JUEGO:
            pos_mouse = pygame.mouse.get_pos()

            titulo = fuente_titulo.render("MODO DE JUEGO", True, (255, 230, 100))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 85)))

            subt = fuente_subtitulo.render("Selecciona cómo deseas comenzar tu aventura", True, (215, 215, 225))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 135)))

            # Botón Continuar
            hov_c = btn_continuar.collidepoint(pos_mouse)
            col_c = (55, 165, 88) if hov_c else (42, 138, 72)
            pygame.draw.rect(pantalla, col_c, btn_continuar, border_radius=16)
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_c else (160, 230, 180), btn_continuar, width=3 if hov_c else 2, border_radius=16)
            t_cont_tit = fuente_btn.render("▶  CONTINUAR", True, (255, 255, 255))
            pantalla.blit(t_cont_tit, t_cont_tit.get_rect(center=(btn_continuar.centerx, btn_continuar.centery - 16)))
            t_cont_desc = fuente_sub_btn.render("Cargar partida guardada y ver tus niveles alcanzados", True, (220, 245, 225))
            pantalla.blit(t_cont_desc, t_cont_desc.get_rect(center=(btn_continuar.centerx, btn_continuar.centery + 18)))

            # Botón Nueva Partida
            hov_n = btn_nueva_partida.collidepoint(pos_mouse)
            col_n = (215, 120, 48) if hov_n else (185, 100, 38)
            pygame.draw.rect(pantalla, col_n, btn_nueva_partida, border_radius=16)
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_n else (245, 205, 150), btn_nueva_partida, width=3 if hov_n else 2, border_radius=16)
            t_nueva_tit = fuente_btn.render("★  NUEVA PARTIDA", True, (255, 255, 255))
            pantalla.blit(t_nueva_tit, t_nueva_tit.get_rect(center=(btn_nueva_partida.centerx, btn_nueva_partida.centery - 16)))
            t_nueva_desc = fuente_sub_btn.render("Reiniciar todo y comenzar desde el Mundo 1 - Nivel 1", True, (255, 235, 215))
            pantalla.blit(t_nueva_desc, t_nueva_desc.get_rect(center=(btn_nueva_partida.centerx, btn_nueva_partida.centery + 18)))

            # Botón Volver al Menú
            hov_v = btn_volver_modo.collidepoint(pos_mouse)
            col_v = (85, 85, 98) if hov_v else (60, 60, 70)
            pygame.draw.rect(pantalla, col_v, btn_volver_modo, border_radius=10)
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_v else (140, 140, 155), btn_volver_modo, width=2, border_radius=10)
            t_v = fuente_texto.render("VOLVER AL MENÚ", True, (255, 255, 255))
            pantalla.blit(t_v, t_v.get_rect(center=btn_volver_modo.center))

        elif estado_actual == ESTADO_LISTA_PARTIDAS:
            pos_mouse = pygame.mouse.get_pos()
            partidas = cargar_partidas()

            titulo = fuente_titulo.render("PARTIDAS JUGADAS", True, (255, 230, 100))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 50)))

            subt = fuente_subtitulo.render("Selecciona tu partida guardada para continuar", True, (215, 215, 225))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 90)))

            # Panel contenedor
            pygame.draw.rect(pantalla, (36, 36, 44), rect_panel_partidas, border_radius=16)
            pygame.draw.rect(pantalla, (85, 85, 105), rect_panel_partidas, width=2, border_radius=16)

            if not partidas:
                t_sin = fuente_subtitulo.render("No hay partidas guardadas todavía", True, (230, 230, 240))
                pantalla.blit(t_sin, t_sin.get_rect(center=(rect_panel_partidas.centerx, rect_panel_partidas.centery - 45)))

                t_sin2 = fuente_texto.render("Al jugar y guardar el nivel antes de salir, tus partidas aparecerán aquí.", True, (170, 170, 185))
                pantalla.blit(t_sin2, t_sin2.get_rect(center=(rect_panel_partidas.centerx, rect_panel_partidas.centery - 10)))

                hov_prim = btn_iniciar_primera.collidepoint(pos_mouse)
                col_prim = (55, 165, 88) if hov_prim else (42, 138, 72)
                pygame.draw.rect(pantalla, col_prim, btn_iniciar_primera, border_radius=12)
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_prim else (160, 230, 180), btn_iniciar_primera, width=2, border_radius=12)
                t_btn_prim = fuente_btn.render("COMENZAR NUEVA PARTIDA", True, (255, 255, 255))
                pantalla.blit(t_btn_prim, t_btn_prim.get_rect(center=btn_iniciar_primera.center))
            else:
                for idx_p, p in enumerate(partidas[:5]):
                    r_card = pygame.Rect(rect_panel_partidas.left + 20, rect_panel_partidas.top + 20 + idx_p * (72 + 12), rect_panel_partidas.width - 40, 72)
                    hov_card = r_card.collidepoint(pos_mouse)

                    col_card = (56, 56, 70) if hov_card else (45, 45, 54)
                    borde_card = (255, 230, 120) if hov_card else (75, 75, 90)
                    pygame.draw.rect(pantalla, col_card, r_card, border_radius=12)
                    pygame.draw.rect(pantalla, borde_card, r_card, width=2 if hov_card else 1, border_radius=12)

                    # Badge de mundo
                    m_val = p.get("mundo_max", 1)
                    colores_badge = {
                        1: ((246, 215, 153), (50, 40, 30)),
                        2: ((203, 195, 227), (45, 35, 45)),
                        3: ((185, 222, 253), (30, 45, 55)),
                    }
                    bg_badge, fg_badge = colores_badge.get(m_val, ((246, 215, 153), (50, 40, 30)))
                    r_badge = pygame.Rect(r_card.left + 14, r_card.top + 14, 115, 44)
                    pygame.draw.rect(pantalla, bg_badge, r_badge, border_radius=8)
                    t_badge = fuente_btn.render(f"MUNDO {m_val}", True, fg_badge)
                    pantalla.blit(t_badge, t_badge.get_rect(center=r_badge.center))

                    # Título de la partida y nivel alcanzado
                    t_nom = fuente_btn.render(f"{p['nombre']}  —  Nivel Máximo: {p['mundo_max']}-{p['nivel_max']}", True, (255, 255, 255))
                    pantalla.blit(t_nom, (r_card.left + 145, r_card.top + 15))

                    # Cantidad de niveles desbloqueados
                    total_desbloq = sum(sum(1 for x in bits if x) for bits in p["niveles_desbloqueados"].values())
                    t_detalle = fuente_sub_btn.render(f"Último guardado: {p['fecha']}   |   Niveles desbloqueados: {total_desbloq}/15", True, (185, 190, 205))
                    pantalla.blit(t_detalle, (r_card.left + 145, r_card.top + 43))

                    # Botón Cargar a la derecha
                    r_btn_cargar = pygame.Rect(r_card.right - 130, r_card.top + 15, 116, 42)
                    col_bc = (55, 165, 88) if hov_card else (42, 138, 72)
                    pygame.draw.rect(pantalla, col_bc, r_btn_cargar, border_radius=8)
                    pygame.draw.rect(pantalla, (255, 255, 255), r_btn_cargar, width=1, border_radius=8)
                    t_bc = fuente_texto.render("CARGAR ▶", True, (255, 255, 255))
                    pantalla.blit(t_bc, t_bc.get_rect(center=r_btn_cargar.center))

            # Botones inferiores de navegación
            hov_vp = btn_volver_partidas.collidepoint(pos_mouse)
            col_vp = (85, 85, 98) if hov_vp else (60, 60, 70)
            pygame.draw.rect(pantalla, col_vp, btn_volver_partidas, border_radius=10)
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_vp else (140, 140, 155), btn_volver_partidas, width=2, border_radius=10)
            t_vp = fuente_texto.render("VOLVER", True, (255, 255, 255))
            pantalla.blit(t_vp, t_vp.get_rect(center=btn_volver_partidas.center))

            if partidas:
                hov_nd = btn_nueva_desde_lista.collidepoint(pos_mouse)
                col_nd = (215, 120, 48) if hov_nd else (185, 100, 38)
                pygame.draw.rect(pantalla, col_nd, btn_nueva_desde_lista, border_radius=10)
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_nd else (245, 205, 150), btn_nueva_desde_lista, width=2, border_radius=10)
                t_nd = fuente_texto.render("+ NUEVA PARTIDA", True, (255, 255, 255))
                pantalla.blit(t_nd, t_nd.get_rect(center=btn_nueva_desde_lista.center))

        elif estado_actual == ESTADO_PERSONAJES:
            titulo = fuente_titulo.render("PERSONALIZACIÓN DE PERSONAJES", True, (255, 255, 255))
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

            pygame.draw.rect(pantalla, (50, 150, 50), btn_guardar, border_radius=8)
            pygame.draw.rect(pantalla, (255, 255, 255), btn_guardar, 2, border_radius=8)
            t_guardar = fuente_btn.render("GUARDAR", True, (255, 255, 255))
            pantalla.blit(t_guardar, t_guardar.get_rect(center=btn_guardar.center))

        elif estado_actual == ESTADO_CONFIGURACION:
            titulo = fuente_titulo.render("CONFIGURACIÓN", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            i1 = fuente_texto.render("Jugador 1: Flechas Izq / Der (Mover) | Flecha Arriba (Saltar)", True, (220, 220, 220))
            i2 = fuente_texto.render("Jugador 2: Teclas A / D (Mover) | W (Saltar)", True, (220, 220, 220))
            pantalla.blit(i1, i1.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2 - 20)))
            pantalla.blit(i2, i2.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2 + 20)))

        elif estado_actual == ESTADO_CREDITOS:
            titulo = fuente_titulo.render("CRÉDITOS", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            cred = fuente_texto.render("Desarrollado para Pico Park Fan Project", True, (200, 200, 200))
            pantalla.blit(cred, cred.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2)))

        elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            pos_mouse = pygame.mouse.get_pos()
            dibujar_menu_niveles(
                pantalla,
                mundo_seleccionado,
                niveles_desbloqueados,
                pos_mouse,
                fuentes_menu,
            )

        try:
            fondo_btn_x = pantalla.subsurface(rect_btn_x).copy()
        except Exception:
            pass

        if spr_x_normal: pantalla.blit(spr_x_normal, rect_btn_x)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()