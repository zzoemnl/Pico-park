import sys
import pygame

from sprites import ANCHO, ALTO, FPS, aplicar_tinta, cargar_sprites
from pantalla import iniciar_mundo, cargar_boton, animar_pulsacion_boton

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

    ANCHO_MENU = pantalla.get_width()
    ALTO_MENU = pantalla.get_height()

    niveles_desbloqueados = {
        1: [True, False, False, False, False],
        2: [False, False, False, False, False],
        3: [False, False, False, False, False],
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

    ANCHO_BOTON, ALTO_BOTON, ESPACIO = 300, 55, 18
    x_centro = (ANCHO_MENU - ANCHO_BOTON) // 2
    y_inicio_principal = (ALTO_MENU - ((ALTO_BOTON * 4) + (ESPACIO * 3))) // 2

    btn_jugar = pygame.Rect(x_centro, y_inicio_principal, ANCHO_BOTON, ALTO_BOTON)
    btn_personajes = pygame.Rect(x_centro, y_inicio_principal + ALTO_BOTON + ESPACIO, ANCHO_BOTON, ALTO_BOTON)
    btn_config = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON)
    btn_creditos = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON)

    color_p1 = "Celeste"
    color_p2 = "Violeta"

    preview_sprites = {}
    for p in PERSONAJES_DISPONIBLES:
        sp = cargar_sprites(p["nombre"])
        preview_sprites[p["nombre"]] = pygame.transform.scale(
            sp.get("quieto", list(sp.values())[0]), (90, 105)
        )

    btn_guardar = pygame.Rect((ANCHO_MENU - 220) // 2, ALTO_MENU - 80, 220, 50)

    y_inicio_mundos = (ALTO_MENU - ((ALTO_BOTON * 3) + (ESPACIO * 2))) // 2
    botones_mundos = [
        (1, pygame.Rect(x_centro, y_inicio_mundos, ANCHO_BOTON, ALTO_BOTON), "Mundo 1 - Tutorial / Caja"),
        (2, pygame.Rect(x_centro, y_inicio_mundos + ALTO_BOTON + ESPACIO, ANCHO_BOTON, ALTO_BOTON), "Mundo 2 - Soga"),
        (3, pygame.Rect(x_centro, y_inicio_mundos + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON), "Mundo 3 - Agua"),
    ]

    TAM_NIVEL, ESPACIO_NIVEL = 85, 20
    ancho_grid = (TAM_NIVEL * 5) + (ESPACIO_NIVEL * 4)
    x_inicio_grid = (ANCHO_MENU - ancho_grid) // 2
    y_grid = (ALTO_MENU - TAM_NIVEL) // 2
    botones_niveles = [pygame.Rect(x_inicio_grid + i * (TAM_NIVEL + ESPACIO_NIVEL), y_grid, TAM_NIVEL, TAM_NIVEL) for i in range(5)]

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
                    elif estado_actual in (ESTADO_CONFIGURACION, ESTADO_CREDITOS, ESTADO_PERSONAJES, ESTADO_SELECCION_MUNDO):
                        estado_actual = ESTADO_MENU_PRINCIPAL
                    elif estado_actual == ESTADO_SELECCION_NIVEL:
                        estado_actual = ESTADO_SELECCION_MUNDO
                    break

                if estado_actual == ESTADO_MENU_PRINCIPAL:
                    if btn_jugar.collidepoint(evento.pos): estado_actual = ESTADO_SELECCION_MUNDO
                    elif btn_personajes.collidepoint(evento.pos): estado_actual = ESTADO_PERSONAJES
                    elif btn_config.collidepoint(evento.pos): estado_actual = ESTADO_CONFIGURACION
                    elif btn_creditos.collidepoint(evento.pos): estado_actual = ESTADO_CREDITOS

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

                elif estado_actual == ESTADO_SELECCION_MUNDO:
                    for num_m, rect_m, _ in botones_mundos:
                        if rect_m.collidepoint(evento.pos):
                            mundo_seleccionado = num_m
                            estado_actual = ESTADO_SELECCION_NIVEL
                            break

                elif estado_actual == ESTADO_SELECCION_NIVEL:
                    for idx_nivel, rect_n in enumerate(botones_niveles):
                        desbloqueado = niveles_desbloqueados[mundo_seleccionado][idx_nivel]
                        if desbloqueado and rect_n.collidepoint(evento.pos):
                            mecanicas = MECANICAS_MUNDOS[mundo_seleccionado]
                            m_idx, n_idx = mundo_seleccionado, idx_nivel

                            mantenimiento = True
                            while mantenimiento:
                                res = iniciar_mundo(mecanicas, numero_nivel=n_idx + 1, color_p1=color_p1, color_p2=color_p2)
                                if res == "siguiente":
                                    if n_idx + 1 < 5:
                                        n_idx += 1
                                        niveles_desbloqueados[m_idx][n_idx] = True
                                    elif m_idx + 1 <= 3:
                                        m_idx += 1
                                        n_idx = 0
                                        mecanicas = MECANICAS_MUNDOS[m_idx]
                                        niveles_desbloqueados[m_idx][n_idx] = True
                                    else:
                                        mantenimiento = False
                                        estado_actual = ESTADO_MENU_PRINCIPAL
                                elif res == "reiniciar":
                                    continue
                                elif res == "menu":
                                    mantenimiento = False
                                    estado_actual = ESTADO_MENU_PRINCIPAL
                                else:
                                    mantenimiento = False
                                    ejecutando = False
                            break

        pantalla.fill((30, 30, 30))

        if estado_actual == ESTADO_MENU_PRINCIPAL:
            titulo = fuente_titulo.render("PICO PARK", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 70)))

            for btn, txt in [(btn_jugar, "JUGAR"), (btn_personajes, "PERSONAJES"), (btn_config, "CONFIGURACIÓN"), (btn_creditos, "CRÉDITOS")]:
                pygame.draw.rect(pantalla, (70, 70, 70), btn, border_radius=8)
                pygame.draw.rect(pantalla, (255, 255, 255), btn, 2, border_radius=8)
                t = fuente_btn.render(txt, True, (255, 255, 255))
                pantalla.blit(t, t.get_rect(center=btn.center))

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

        elif estado_actual == ESTADO_SELECCION_MUNDO:
            titulo = fuente_titulo.render("SELECCIONÁ UN MUNDO", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            for num_m, rect_m, txt_m in botones_mundos:
                pygame.draw.rect(pantalla, (70, 70, 70), rect_m, border_radius=8)
                pygame.draw.rect(pantalla, (255, 255, 255), rect_m, 2, border_radius=8)
                t = fuente_btn.render(txt_m, True, (255, 255, 255))
                pantalla.blit(t, t.get_rect(center=rect_m.center))

        elif estado_actual == ESTADO_SELECCION_NIVEL:
            titulo = fuente_titulo.render(f"MUNDO {mundo_seleccionado} - NIVELES", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            for idx, rect_n in enumerate(botones_niveles):
                desbloqueado = niveles_desbloqueados[mundo_seleccionado][idx]
                col_f = (50, 150, 50) if desbloqueado else (40, 40, 40)
                col_b = (255, 255, 255) if desbloqueado else (90, 90, 90)
                col_t = (255, 255, 255) if desbloqueado else (120, 120, 120)

                pygame.draw.rect(pantalla, col_f, rect_n, border_radius=12)
                pygame.draw.rect(pantalla, col_b, rect_n, 2, border_radius=12)

                txt_num = fuente_btn.render(str(idx + 1), True, col_t)
                pantalla.blit(txt_num, txt_num.get_rect(center=rect_n.center))

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