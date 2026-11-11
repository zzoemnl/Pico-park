import math
import random
import pygame
import os

def crear_boton_pixel_art(
    ancho, alto,
    texto_principal,
    subtexto=None,
    icono=None,
    estilo="ambar",  # "ambar", "violeta", "crema"
    estado="normal", # "normal", "hover", "semi", "apretado"
    fuente_tit=None,
    fuente_sub=None,
):
    """
    Genera una superficie con un botón pixel art profesional de videojuego:
    - Bordes escalonados (pixel stepped).
    - Biselado de relieve 3D con luz y sombra.
    - Textura sutil y detalles en esquinas.
    - Tipografía retro con sombra proyectada de 1-2px.
    - Desplazamiento físico en estados semi y apretado.
    """
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    # Paletas por estilo y estado
    if estilo == "ambar":
        # CONTINUAR: Ámbar atardecer / coral dorado
        col_borde_ext = (46, 18, 12)
        col_sombra_ext = (32, 12, 8)
        if estado == "hover":
            col_cara = (235, 128, 48)
            col_luz_sup = (255, 198, 115)
            col_luz_cara = (248, 155, 68)
            col_somb_cara = (185, 88, 32)
            col_somb_inf = (135, 52, 18)
            col_texto = (255, 255, 255)
            col_texto_somb = (64, 22, 10)
            col_sub = (255, 235, 205)
        elif estado in ("semi", "apretado"):
            col_cara = (175, 82, 28)
            col_luz_sup = (125, 48, 16)   # Bisel invertido por hundimiento
            col_luz_cara = (155, 68, 22)
            col_somb_cara = (135, 54, 18)
            col_somb_inf = (215, 112, 42)
            col_texto = (245, 235, 220)
            col_texto_somb = (45, 15, 8)
            col_sub = (230, 205, 180)
        else: # normal
            col_cara = (215, 110, 42)
            col_luz_sup = (252, 178, 92)
            col_luz_cara = (232, 132, 52)
            col_somb_cara = (168, 74, 26)
            col_somb_inf = (118, 44, 14)
            col_texto = (255, 255, 255)
            col_texto_somb = (58, 20, 10)
            col_sub = (255, 225, 195)

    elif estilo == "violeta":
        # NUEVA PARTIDA: Ciruela / Violeta / Berry atardecer
        col_borde_ext = (38, 14, 30)
        col_sombra_ext = (26, 8, 20)
        if estado == "hover":
            col_cara = (168, 62, 108)
            col_luz_sup = (225, 128, 172)
            col_luz_cara = (188, 82, 128)
            col_somb_cara = (128, 42, 82)
            col_somb_inf = (92, 26, 58)
            col_texto = (255, 255, 255)
            col_texto_somb = (52, 14, 38)
            col_sub = (255, 225, 240)
        elif estado in ("semi", "apretado"):
            col_cara = (118, 38, 74)
            col_luz_sup = (82, 22, 52)
            col_luz_cara = (102, 32, 64)
            col_somb_cara = (88, 26, 55)
            col_somb_inf = (162, 58, 102)
            col_texto = (245, 230, 240)
            col_texto_somb = (38, 10, 26)
            col_sub = (220, 195, 212)
        else: # normal
            col_cara = (145, 52, 92)
            col_luz_sup = (205, 105, 150)
            col_luz_cara = (165, 68, 108)
            col_somb_cara = (112, 34, 70)
            col_somb_inf = (78, 20, 48)
            col_texto = (255, 255, 255)
            col_texto_somb = (45, 12, 30)
            col_sub = (250, 212, 230)

    else: # "crema"
        # VOLVER: Pergamino / Crema atardecer con toques caramelo
        col_borde_ext = (54, 28, 22)
        col_sombra_ext = (35, 16, 12)
        if estado == "hover":
            col_cara = (255, 248, 238)
            col_luz_sup = (255, 255, 255)
            col_luz_cara = (255, 252, 245)
            col_somb_cara = (225, 205, 185)
            col_somb_inf = (185, 155, 130)
            col_texto = (58, 24, 18)
            col_texto_somb = (235, 215, 195)
            col_sub = (115, 75, 55)
        elif estado in ("semi", "apretado"):
            col_cara = (222, 205, 185)
            col_luz_sup = (168, 140, 115)
            col_luz_cara = (205, 185, 165)
            col_somb_cara = (185, 160, 138)
            col_somb_inf = (245, 232, 218)
            col_texto = (48, 18, 14)
            col_texto_somb = (240, 225, 210)
            col_sub = (95, 60, 42)
        else: # normal
            col_cara = (245, 234, 218)
            col_luz_sup = (255, 250, 242)
            col_luz_cara = (250, 242, 230)
            col_somb_cara = (212, 192, 168)
            col_somb_inf = (168, 138, 112)
            col_texto = (65, 30, 22)
            col_texto_somb = (255, 245, 235)
            col_sub = (125, 82, 60)

    # Offset vertical según estado de pulsación física
    offset_y = 4 if estado == "apretado" else (2 if estado == "semi" else 0)
    h_sombra_ext = 5 if estado == "normal" else (3 if estado == "hover" else (1 if estado == "semi" else 0))

    # Geometría del botón
    bx = 4
    by = 4 + offset_y
    bw = ancho - 8
    bh = alto - 10 - offset_y

    # 1. Sombra exterior pixelada debajo del botón
    if h_sombra_ext > 0:
        rect_somb = pygame.Rect(bx + 3, by + bh - 2, bw - 6, h_sombra_ext + 2)
        pygame.draw.rect(surf, col_sombra_ext, rect_somb)

    # 2. Borde exterior pixelado con esquinas recortadas en píxeles (pixel stepped)
    corte = 6
    # Cuerpo central
    pygame.draw.rect(surf, col_borde_ext, (bx + corte, by, bw - corte * 2, bh))
    pygame.draw.rect(surf, col_borde_ext, (bx, by + corte, bw, bh - corte * 2))
    # Esquinas pixeladas
    for step in range(1, corte):
        dx = corte - step
        pygame.draw.rect(surf, col_borde_ext, (bx + dx, by + step, bw - dx * 2, bh - step * 2))

    # 3. Biselado 3D interno
    # Bisel de luz superior e izquierdo (3px)
    b_in = 3
    pygame.draw.rect(surf, col_luz_sup, (bx + b_in + 3, by + b_in, bw - (b_in + 3) * 2, 4))
    pygame.draw.rect(surf, col_luz_sup, (bx + b_in, by + b_in + 3, 4, bh - (b_in + 3) * 2))

    # Bisel de sombra inferior y derecho (3px)
    pygame.draw.rect(surf, col_somb_inf, (bx + b_in + 3, by + bh - b_in - 4, bw - (b_in + 3) * 2, 4))
    pygame.draw.rect(surf, col_somb_inf, (bx + bw - b_in - 4, by + b_in + 3, 4, bh - (b_in + 3) * 2))

    # 4. Cara central del botón
    cx = bx + b_in + 4
    cy = by + b_in + 4
    cw = bw - (b_in + 4) * 2
    ch = bh - (b_in + 4) * 2
    pygame.draw.rect(surf, col_cara, (cx, cy, cw, ch))

    # Franja de resplandor sutil en la mitad superior de la cara
    pygame.draw.rect(surf, col_luz_cara, (cx, cy, cw, ch // 2))

    # Detalle de esquinas interiores (puntos decorativos retro)
    col_dot = col_luz_sup if estado != "apretado" else col_somb_inf
    surf.set_at((cx + 2, cy + 2), col_dot)
    surf.set_at((cx + cw - 3, cy + 2), col_dot)
    surf.set_at((cx + 2, cy + ch - 3), col_somb_inf)
    surf.set_at((cx + cw - 3, cy + ch - 3), col_somb_inf)

    # 5. Icono decorativo pixel art (si corresponde)
    y_centro_contenido = cy + ch // 2
    if icono == "play":
        # Flecha play / triángulo dorado de aventura
        ix = cx + 24
        iy = y_centro_contenido
        for d_col in range(12):
            h_linea = 12 - d_col
            for dy in range(-h_linea, h_linea + 1):
                col_ic = (255, 235, 140) if d_col < 6 else (225, 175, 75)
                surf.set_at((ix + d_col, iy + dy), col_ic)
                surf.set_at((ix + d_col + 1, iy + dy + 1), (50, 18, 8))
    elif icono == "estrella":
        # Estrella pixel art de nueva partida
        ix = cx + 24
        iy = y_centro_contenido
        for dx in range(-7, 8):
            for dy in range(-7, 8):
                dist = abs(dx) + abs(dy)
                if dist <= 6:
                    c_st = (255, 245, 180) if dist <= 2 else (255, 205, 95)
                    surf.set_at((ix + dx, iy + dy), c_st)
                elif dist == 7:
                    surf.set_at((ix + dx, iy + dy), (60, 15, 30))
    elif icono == "volver":
        # Flecha pixel retro apuntando a la izquierda
        ix = cx + 18
        iy = y_centro_contenido
        for d_col in range(10):
            h_linea = d_col
            for dy in range(-h_linea, h_linea + 1):
                col_ic = (70, 32, 24)
                surf.set_at((ix + d_col, iy + dy), col_ic)

    # 6. Texto del botón
    if fuente_tit:
        # Texto principal con sombra pixel art de 2px
        t_somb = fuente_tit.render(texto_principal, True, col_texto_somb)
        t_tit = fuente_tit.render(texto_principal, True, col_texto)

        # Si hay subtexto, desplazar título un poco arriba
        offset_tit_y = -10 if subtexto else 0
        rect_tit = t_tit.get_rect(center=(ancho // 2, y_centro_contenido + offset_tit_y))

        # Sombra proyectada
        surf.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
        surf.blit(t_tit, rect_tit)

        if subtexto and fuente_sub:
            t_sub = fuente_sub.render(subtexto, True, col_sub)
            rect_sub = t_sub.get_rect(center=(ancho // 2, y_centro_contenido + 18))
            # Sombra sutil subtexto
            t_sub_s = fuente_sub.render(subtexto, True, col_texto_somb)
            surf.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
            surf.blit(t_sub, rect_sub)

    return surf


def generar_pantalla_completa():
    pygame.init()
    W, H = 1280, 720
    pantalla = pygame.Surface((W, H))

    # Cargar fondo generado
    from test_landscape import generar_fondo_atardecer
    fondo = generar_fondo_atardecer(W, H)
    pantalla.blit(fondo, (0, 0))

    # Fuentes
    try:
        from fuentes import obtener_fuente_titulo, obtener_fuente_subtitulo, obtener_fuente_botones, obtener_fuente_pequena
        fuente_titulo = obtener_fuente_titulo(46, tamano_fallback=46)
        fuente_sub = obtener_fuente_subtitulo(24)
        fuente_btn = obtener_fuente_botones(22, tamano_fallback=22)
        fuente_sub_btn = obtener_fuente_pequena(15)
        fuente_volver = obtener_fuente_botones(18, tamano_fallback=18)
    except Exception as e:
        print("Fallback font:", e)
        fuente_titulo = pygame.font.SysFont("Verdana", 42, bold=True)
        fuente_sub = pygame.font.SysFont("Verdana", 20)
        fuente_btn = pygame.font.SysFont("Verdana", 22, bold=True)
        fuente_sub_btn = pygame.font.SysFont("Verdana", 14)
        fuente_volver = pygame.font.SysFont("Verdana", 18, bold=True)

    # Placa / Marquesina elegante semitransparente para el TÍTULO y SUBTÍTULO
    w_placa, h_placa = 760, 116
    x_placa = (W - w_placa) // 2
    y_placa = 45

    surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    # Fondo pergamino atardecer semitransparente cálido
    pygame.draw.rect(surf_placa, (38, 16, 32, 175), (0, 0, w_placa, h_placa), border_radius=18)
    # Borde dorado / coral pixelado
    pygame.draw.rect(surf_placa, (238, 145, 78, 220), (0, 0, w_placa, h_placa), width=3, border_radius=18)
    pygame.draw.rect(surf_placa, (255, 215, 140, 180), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=16)

    # Esquinas decorativas
    for cx_d, cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
        pygame.draw.circle(surf_placa, (255, 225, 120, 240), (cx_d, cy_d), 4)
        pygame.draw.circle(surf_placa, (65, 24, 18, 240), (cx_d, cy_d), 2)

    pantalla.blit(surf_placa, (x_placa, y_placa))

    # Título «MODO DE JUEGO»
    # Sombra doble para máxima nitidez y estilo retro
    txt_tit = "MODO DE JUEGO"
    t_somb1 = fuente_titulo.render(txt_tit, True, (24, 8, 18))
    t_somb2 = fuente_titulo.render(txt_tit, True, (82, 28, 48))
    t_tit = fuente_titulo.render(txt_tit, True, (255, 242, 220))

    rect_tit = t_tit.get_rect(center=(W // 2, y_placa + 42))
    pantalla.blit(t_somb1, (rect_tit.x + 3, rect_tit.y + 3))
    pantalla.blit(t_somb2, (rect_tit.x + 1, rect_tit.y + 1))
    pantalla.blit(t_tit, rect_tit)

    # Subtítulo
    txt_sub = "Selecciona como deseas comenzar tu aventura"
    t_sub_s = fuente_sub.render(txt_sub, True, (28, 10, 20))
    t_sub = fuente_sub.render(txt_sub, True, (255, 205, 160))
    rect_sub = t_sub.get_rect(center=(W // 2, y_placa + 84))
    pantalla.blit(t_sub_s, (rect_sub.x + 2, rect_sub.y + 2))
    pantalla.blit(t_sub, rect_sub)

    # Botones
    W_MODO, H_MODO = 440, 104
    x_modo = (W - W_MODO) // 2
    y_cont = 230
    y_nueva = 365
    W_VOLVER, H_VOLVER = 240, 68
    x_volver = (W - W_VOLVER) // 2
    y_volver = 625

    # 1. CONTINUAR
    btn_c = crear_boton_pixel_art(
        W_MODO, H_MODO,
        "CONTINUAR",
        subtexto="Cargar partida guardada",
        icono="play",
        estilo="ambar",
        estado="normal",
        fuente_tit=fuente_btn,
        fuente_sub=fuente_sub_btn,
    )
    pantalla.blit(btn_c, (x_modo, y_cont))

    # 2. NUEVA PARTIDA
    btn_n = crear_boton_pixel_art(
        W_MODO, H_MODO,
        "NUEVA PARTIDA",
        subtexto="Comenzar desde el principio",
        icono="estrella",
        estilo="violeta",
        estado="normal",
        fuente_tit=fuente_btn,
        fuente_sub=fuente_sub_btn,
    )
    pantalla.blit(btn_n, (x_modo, y_nueva))

    # 3. VOLVER AL MENÚ
    btn_v = crear_boton_pixel_art(
        W_VOLVER, H_VOLVER,
        "VOLVER AL MENU",
        icono="volver",
        estilo="crema",
        estado="normal",
        fuente_tit=fuente_volver,
    )
    pantalla.blit(btn_v, (x_volver, y_volver))

    pygame.image.save(pantalla, "scratch/pantalla_modo_juego_completa.png")
    print("Captura guardada en: scratch/pantalla_modo_juego_completa.png")

if __name__ == '__main__':
    generar_pantalla_completa()
