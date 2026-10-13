import sys
import pygame

from sprites import ANCHO, ALTO, FPS, aplicar_tinta, cargar_sprites
from pantalla import iniciar_mundo, cargar_boton, animar_pulsacion_boton
from menu_niveles import (
    dibujar_menu_niveles,
    obtener_geometria_menu,
    obtener_mecanicas_nivel,
)

ESTADO_MENU_PRINCIPAL = "principal"
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
    fuentes_menu = {
        "titulo": fuente_titulo,
        "tab": pygame.font.Font(None, 34),
        "card": pygame.font.Font(None, 28),
    }

    ANCHO_MENU = pantalla.get_width()
    ALTO_MENU = pantalla.get_height()

    niveles_desbloqueados = {
        1: [True, False, False, False, False],
        2: [True, False, False, False, False],
        3: [True, False, False, False, False],
    }

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

    estado_actual = ESTADO_MENU_PRINCIPAL
    mundo_seleccionado = 1
    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_btn_x.collidepoint(evento.pos):
                    if spr_x_semi and spr_x_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, fondo_btn_x)
                    if estado_actual == ESTADO_MENU_PRINCIPAL:
                        ejecutando = False
                    elif estado_actual in (ESTADO_CONFIGURACION, ESTADO_CREDITOS, ESTADO_PERSONAJES, ESTADO_SELECCION_MUNDO, ESTADO_SELECCION_NIVEL):
                        estado_actual = ESTADO_MENU_PRINCIPAL
                    break

                if estado_actual == ESTADO_MENU_PRINCIPAL:
                    if btn_jugar.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_jugar, spr_jugar_semi, spr_jugar_apretado, fondo_limpio_btn)
                        estado_actual = ESTADO_SELECCION_NIVEL
                    elif btn_personajes.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_personajes, spr_personajes_semi, spr_personajes_apretado, fondo_limpio_btn)
                        estado_actual = ESTADO_PERSONAJES
                    elif btn_config.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_config, spr_opciones_semi, spr_opciones_apretado, fondo_limpio_btn)
                        estado_actual = ESTADO_CONFIGURACION
                    elif btn_salir.collidepoint(evento.pos):
                        animar_pulsacion_boton(pantalla, btn_salir, spr_salir_semi, spr_salir_apretado, fondo_limpio_btn)
                        ejecutando = False

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
                                    res = iniciar_mundo(mecanicas, numero_nivel=n_idx + 1, color_p1=color_p1, color_p2=color_p2)
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