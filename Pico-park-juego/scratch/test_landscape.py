import math
import random
import pygame

def generar_fondo_atardecer(ancho=1280, alto=720):
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. CIELO DE ATARDECER (Bandas ricas con dithering escalonado estilo 16-bit)
    bandas_cielo = [
        (0,   42,  (34,  16,  48)),   # Violeta profundo noche/crepúsculo
        (42,  84,  (58,  24,  66)),   # Ciruela / mora oscuro
        (84,  125, (115, 42,  76)),   # Magenta / vino atardecer
        (125, 162, (185, 68,  62)),   # Coral cálido
        (162, 196, (228, 115, 52)),   # Naranja ámbar vibrante
        (196, 224, (248, 168, 68)),   # Amarillo dorado brillante
        (224, 250, (255, 218, 120)),  # Resplandor dorado de horizonte
    ]
    for y1, y2, col in bandas_cielo:
        pygame.draw.rect(surf, col, (0, y1, W, y2 - y1))

    # Dithering estilo 16-bit entre bandas
    for i in range(len(bandas_cielo) - 1):
        yt = bandas_cielo[i][1]
        c_up = bandas_cielo[i][2]
        c_dn = bandas_cielo[i + 1][2]
        for dy in range(-3, 4):
            y = yt + dy
            if 0 <= y < H:
                for x in range(W):
                    if dy == -3 and (x % 4 == 0 and y % 4 == 0):
                        surf.set_at((x, y), c_dn)
                    elif dy == -2 and (x + y) % 4 == 0:
                        surf.set_at((x, y), c_dn)
                    elif dy == -1 and (x % 2 == 0 and y % 2 == 0):
                        surf.set_at((x, y), c_dn)
                    elif dy == 0 and (x + y) % 2 == 0:
                        surf.set_at((x, y), c_dn)
                    elif dy == 1 and (x % 2 == 0 and y % 2 == 0):
                        surf.set_at((x, y), c_up)
                    elif dy == 2 and (x + y) % 4 == 0:
                        surf.set_at((x, y), c_up)
                    elif dy == 3 and (x % 4 == 0 and y % 4 == 0):
                        surf.set_at((x, y), c_up)

    # 2. PRIMERAS ESTRELLAS DEL CREPÚSCULO (en la parte superior más oscura)
    rnd_stars = random.Random(999)
    for _ in range(28):
        sx = rnd_stars.randint(40, W - 40)
        sy = rnd_stars.randint(4, 52)
        surf.set_at((sx, sy), (255, 240, 220))
        if rnd_stars.random() < 0.25:
            surf.set_at((sx + 1, sy), (230, 195, 225))
            surf.set_at((sx, sy + 1), (230, 195, 225))

    # 3. RESPLANDOR DEL SOL EN EL HORIZONTE (detrás del lago y colinas)
    sun_x, sun_y = 320, 206
    for r in range(54, 0, -2):
        prog = 1.0 - (r / 54)
        col_sun = (
            min(255, int(250 + 5 * prog)),
            min(255, int(185 + 70 * prog)),
            min(255, int(85 + 140 * prog))
        )
        for dy in range(-r, r + 1):
            w_line = int(math.sqrt(max(0, r * r - dy * dy)))
            y_pix = sun_y + dy
            if 0 <= y_pix < 232:
                for x_pix in range(sun_x - w_line, sun_x + w_line + 1):
                    # Dither suave en el halo exterior
                    if r > 30:
                        if (x_pix + y_pix) % 2 == 0:
                            surf.set_at((x_pix, y_pix), col_sun)
                    else:
                        surf.set_at((x_pix, y_pix), col_sun)

    # 4. NUBES PIXELADAS HORIZONTALES (con relieve de atardecer)
    def _dibujar_nube_pixel(s, x_centro, y_base, largo, alto_nube, rnd_seed):
        rnd_c = random.Random(rnd_seed)
        col_sombra = (74, 28, 62)
        col_medio = (158, 58, 76)
        col_luz = (235, 148, 82)
        col_borde = (255, 218, 145)

        tramos = []
        pasos = largo // 5
        for p in range(pasos):
            rx = x_centro - (largo // 2) + p * 5
            dist_c = abs(p - pasos / 2) / (pasos / 2)
            alt_local = int(alto_nube * (1.0 - dist_c * 0.75) * rnd_c.uniform(0.75, 1.25))
            tramos.append((rx, y_base, alt_local))

        for rx, yb, al in tramos:
            for dy in range(-al, 2):
                y = yb + dy
                if 0 <= y < H:
                    w_bloque = 6
                    for dx in range(w_bloque):
                        x = rx + dx
                        if 0 <= x < W:
                            if dy == -al:
                                s.set_at((x, y), col_borde)
                            elif dy < -al // 2:
                                s.set_at((x, y), col_luz)
                            elif dy <= 0:
                                s.set_at((x, y), col_medio)
                            else:
                                s.set_at((x, y), col_sombra)

    nubes = [
        (130, 42, 130, 11, 101),
        (510, 52, 160, 13, 202),
        (275, 88, 115, 9,  303),
        (575, 102, 95, 8,  404),
        (85,  124, 135, 10, 505),
        (395, 136, 125, 9,  606),
    ]
    for nc in nubes:
        _dibujar_nube_pixel(surf, nc[0], nc[1], nc[2], nc[3], nc[4])

    # Bandada de pájaros lejanos
    pajaros = [(215, 80), (227, 76), (239, 73), (251, 77), (263, 81)]
    col_pajaro = (58, 20, 42)
    for px, py in pajaros:
        surf.set_at((px, py), col_pajaro)
        surf.set_at((px - 1, py - 1), col_pajaro)
        surf.set_at((px + 1, py - 1), col_pajaro)

    # 5. GRANDES MONTAÑAS AL FONDO (Orgánicas, con crestas irregulares y facetas de roca)
    # Función para generar silueta de montaña con crestas angulares reales (no simples triángulos)
    def _crear_montaña_organica(px, py, am, rnd_val):
        # Genera puntos de perfil izquierdo y derecho con desvíos
        rnd_m = random.Random(rnd_val)
        y_base = 232
        puntos_izq = []
        puntos_der = []
        for y in range(py, y_base):
            prog = (y - py) / max(1, y_base - py)
            # Curvatura alpina con pendientes cambiantes
            half = int((am // 2) * (prog ** 0.88))
            # Añadir escalones rocosos y quiebres
            desvio = int(rnd_m.uniform(-3, 3) * (prog ** 0.5))
            crest_offset = int(rnd_m.uniform(-2, 2) * (1.0 - prog))
            puntos_izq.append((y, px - half + desvio, px + crest_offset))
            puntos_der.append((y, px + crest_offset, px + half + desvio))
        return puntos_izq, puntos_der

    # Capa 1: Picos lejanos majestuosos
    montañas_lejanas = [
        (65,   72, 150, 1111),
        (170,  58, 175, 2222),
        (280,  90, 135, 3333),
        (375,  68, 165, 4444),
        (485,  52, 185, 5555),
        (585,  82, 150, 6666),
    ]
    col_lej_somb = (52, 26, 62)
    col_lej_cuerpo = (75, 36, 78)
    col_lej_luz = (102, 48, 98)
    col_nieve_lej_luz = (248, 198, 182)
    col_nieve_lej_somb = (178, 132, 168)

    for px, py, am, r_seed in montañas_lejanas:
        p_izq, p_der = _crear_montaña_organica(px, py, am, r_seed)
        for (y, x_min, x_crest), (_, _, x_max) in zip(p_izq, p_der):
            h_tot = 232 - py
            prog = (y - py) / max(1, h_tot)
            # Cara iluminada (oeste)
            for x in range(x_min, x_crest):
                if 0 <= x < W:
                    # Faceta intermedia
                    col_p = col_lej_luz if x < (x_min + x_crest) // 2 else col_lej_cuerpo
                    surf.set_at((x, y), col_p)
            # Cara en sombra (este)
            for x in range(x_crest, x_max + 1):
                if 0 <= x < W:
                    surf.set_at((x, y), col_lej_somb)
            # Nieve en la cima y couloirs
            if prog < 0.32:
                # Línea de nieve escalonada
                for x in range(x_min, x_crest):
                    if 0 <= x < W:
                        surf.set_at((x, y), col_nieve_lej_luz)
                for x in range(x_crest, x_max + 1):
                    if 0 <= x < W and prog < 0.28:
                        surf.set_at((x, y), col_nieve_lej_somb)

    # Capa 2: Montañas medias (con mayor relieve, riscos y gargantas)
    montañas_medias = [
        (25,  125, 130, 7771),
        (125, 110, 150, 7772),
        (225, 138, 125, 7773),
        (320, 152, 115, 7774),
        (420, 118, 155, 7775),
        (525, 104, 160, 7776),
        (625, 130, 120, 7777),
    ]
    col_med_somb = (42, 18, 44)
    col_med_cuerpo = (68, 28, 58)
    col_med_luz = (118, 48, 76)
    col_nieve_med_luz = (245, 175, 142)
    col_nieve_med_somb = (165, 95, 125)

    for px, py, am, r_seed in montañas_medias:
        p_izq, p_der = _crear_montaña_organica(px, py, am, r_seed)
        for (y, x_min, x_crest), (_, _, x_max) in zip(p_izq, p_der):
            h_tot = 232 - py
            prog = (y - py) / max(1, h_tot)
            for x in range(x_min, x_crest):
                if 0 <= x < W:
                    c_fac = col_med_luz if x < (x_min * 2 + x_crest) // 3 else col_med_cuerpo
                    surf.set_at((x, y), c_fac)
            for x in range(x_crest, x_max + 1):
                if 0 <= x < W:
                    surf.set_at((x, y), col_med_somb)
            # Nieve en picos medios
            if prog < 0.26:
                for x in range(x_min, x_crest):
                    if 0 <= x < W:
                        surf.set_at((x, y), col_nieve_med_luz)
                for x in range(x_crest, x_max + 1):
                    if 0 <= x < W and prog < 0.22:
                        surf.set_at((x, y), col_nieve_med_somb)

    # 6. COLINAS BAJAS CON SILUETAS DE PINOS (Transición montaña -> lago)
    for x in range(W):
        y_col = int(214 + 8 * math.sin(x * 0.022 + 0.8) + 3 * math.cos(x * 0.05))
        for y in range(y_col, 230):
            surf.set_at((x, y), (32, 14, 35))
        if x % 6 in (0, 1):
            h_p = 3 + (x % 4)
            for dy in range(h_p):
                surf.set_at((x, y_col - dy), (24, 10, 26))

    # 7. EL LAGO DE ATARDECER (Reflejo del cielo, montañas y luz dorada)
    y_lago_top = 222
    y_lago_bot = 276
    for y in range(y_lago_top, y_lago_bot):
        prog_l = (y - y_lago_top) / (y_lago_bot - y_lago_top)
        # Reflejo base: dorado en la parte superior, ciruela/violeta en la inferior
        r_l = int(248 - 165 * prog_l)
        g_l = int(178 - 135 * prog_l)
        b_l = int(88 - 35 * prog_l)
        pygame.draw.line(surf, (max(0, min(255, r_l)), max(0, min(255, g_l)), max(0, min(255, b_l))), (0, y), (W - 1, y))

    # Reflejos oscuros de las masas de montaña en los lados del lago
    for y in range(y_lago_top, y_lago_top + 28):
        prog_prof = (y - y_lago_top) / 28
        for x in range(W):
            # En laterales (debajo de grandes picos), reflejo más oscuro
            if x < 180 or x > 460:
                dist_borde = min(x, W - 1 - x) / 180
                factor_somb = 0.45 + 0.55 * dist_borde
                if (x + y) % 2 == 0:
                    c_orig = surf.get_at((x, y))
                    surf.set_at((x, y), (
                        int(c_orig.r * factor_somb),
                        int(c_orig.g * factor_somb),
                        int(c_orig.b * factor_somb + 25 * (1.0 - factor_somb))
                    ))

    # Reflejo central del sol y ondas brillantes en el agua
    rnd_w = random.Random(777)
    for y in range(y_lago_top, y_lago_bot):
        prog = (y - y_lago_top) / (y_lago_bot - y_lago_top)
        ancho_reflejo = int(80 + 140 * prog)
        for dx in range(-ancho_reflejo // 2, ancho_reflejo // 2 + 1):
            x = 320 + dx
            if 0 <= x < W:
                # Patrón ondulado de agua
                if (y + (x // 5)) % 3 == 0:
                    c_act = surf.get_at((x, y))
                    factor = 1.0 - (abs(dx) / (ancho_reflejo // 2))
                    surf.set_at((x, y), (
                        min(255, c_act.r + int(55 * factor)),
                        min(255, c_act.g + int(45 * factor)),
                        min(255, c_act.b + int(20 * factor)),
                    ))
        # Ondas brillantes de agua
        if y % 2 == 0:
            for _ in range(int(10 * (1.0 - prog * 0.8))):
                wx = rnd_w.randint(70, W - 70)
                w_len = rnd_w.randint(4, 15)
                c_onda = (255, 238, 175) if prog < 0.45 else (228, 142, 108)
                for w_dx in range(w_len):
                    if 0 <= wx + w_dx < W:
                        surf.set_at((wx + w_dx, y), c_onda)

    # Bruma sutil al ras del agua
    for dy in range(5):
        y_b = y_lago_top + dy
        for x in range(W):
            if (x * 11 + y_b * 7) % 6 == 0:
                surf.set_at((x, y_b), (238, 198, 178))

    # 8. TERRENO EN PRIMER PLANO (Orilla curva, nieve con luz cálida de atardecer)
    def _altura_suelo(x):
        dist_centro = abs(x - 320) / 320
        # Más bajo en el centro (y=265) para exhibir el reflejo del lago
        y_b = 265 - int(25 * (dist_centro ** 1.35))
        y_b += int(4 * math.sin(x * 0.038) + 3 * math.cos(x * 0.075))
        return y_b

    col_nieve_luz = (246, 228, 220)     # Nieve cálida iluminada por el sol poniente
    col_nieve_medio = (218, 192, 192)   # Tono medio
    col_nieve_sombra = (155, 122, 150)  # Sombra malva/violeta
    col_tierra = (64, 38, 42)          # Borde de roca en la orilla

    for x in range(W):
        y_top = _altura_suelo(x)
        if 0 <= y_top < H:
            surf.set_at((x, y_top), col_tierra)
            if y_top + 1 < H:
                surf.set_at((x, y_top + 1), col_tierra)

        for y in range(y_top + 2, H):
            prog_y = (y - y_top) / max(1, H - y_top)
            if prog_y < 0.16:
                c = col_nieve_luz
            elif prog_y < 0.42:
                c = col_nieve_luz if (x + y) % 2 == 0 else col_nieve_medio
            elif prog_y < 0.72:
                c = col_nieve_medio if (x + y) % 3 != 0 else col_nieve_sombra
            else:
                c = col_nieve_sombra if (x + y) % 2 == 0 else col_nieve_medio
            surf.set_at((x, y), c)

    # Rocas pixel art con nieve en el primer plano
    rocas = [
        (135, 256, 18, 10),
        (210, 267, 14, 8),
        (435, 266, 16, 9),
        (515, 254, 20, 12),
        (75,  276, 22, 12),
        (560, 274, 24, 13),
        (280, 280, 12, 7),
        (360, 283, 15, 8),
    ]
    col_roca_oscura = (46, 28, 34)
    col_roca_media = (76, 48, 56)
    col_roca_luz = (116, 80, 86)

    for rx, ry, rw, rh in rocas:
        for dy in range(rh):
            y_r = ry + dy
            w_linea = int(rw * math.sin((dy + 1) / (rh + 1) * math.pi))
            for dx in range(-w_linea // 2, w_linea // 2 + 1):
                x_r = rx + dx
                if 0 <= x_r < W and 0 <= y_r < H:
                    if dy == 0 or (dy == 1 and dx < 0):
                        surf.set_at((x_r, y_r), col_nieve_luz)
                    elif dx < 0:
                        surf.set_at((x_r, y_r), col_roca_luz)
                    elif dx == 0:
                        surf.set_at((x_r, y_r), col_roca_media)
                    else:
                        surf.set_at((x_r, y_r), col_roca_oscura)

    # Cañas / juncos de invierno en la orilla
    for cx in [155, 175, 195, 410, 430, 450, 470]:
        cy = _altura_suelo(cx)
        for h_c in range(5, 12):
            surf.set_at((cx, cy - h_c), (142, 92, 58))
        surf.set_at((cx + 1, cy - 8), (172, 122, 78))

    # 9. ÁRBOLES ALTOS EN LOS LATERALES (Despejando el centro para la interfaz)
    def _dibujar_pino_majestuoso(s, cx, base_y, alt_total, ancho_max):
        col_tronco = (50, 26, 22)
        col_tronco_luz = (82, 44, 36)
        col_pino_sombra = (18, 36, 26)
        col_pino_medio = (32, 64, 44)
        col_pino_luz = (54, 96, 64)
        col_nieve_pino_luz = (248, 226, 218)
        col_nieve_pino_somb = (152, 120, 142)

        # Tronco
        for dy in range(12):
            y_t = base_y + dy
            if 0 <= y_t < H:
                for dx in range(-2, 3):
                    c_tr = col_tronco_luz if dx < 0 else col_tronco
                    if 0 <= cx + dx < W:
                        s.set_at((cx + dx, y_t), c_tr)

        # Pisos de ramas
        pisos = 6
        for piso in range(pisos):
            f_piso = (piso + 1) / pisos
            ancho_piso = int(ancho_max * (0.35 + 0.65 * f_piso))
            h_piso = int((alt_total // pisos) * 1.35)
            y_cima_piso = base_y - alt_total + int(alt_total * (piso / pisos))
            y_base_piso = y_cima_piso + h_piso

            for y in range(y_cima_piso, y_base_piso + 1):
                prog = (y - y_cima_piso) / max(1, y_base_piso - y_cima_piso)
                w_rama = int(ancho_piso * prog)
                for dx in range(-w_rama, w_rama + 1):
                    x = cx + dx
                    if 0 <= x < W and 0 <= y < H:
                        if dx < -w_rama // 2:
                            col_f = col_pino_luz
                        elif dx < 0:
                            col_f = col_pino_medio
                        else:
                            col_f = col_pino_sombra
                        s.set_at((x, y), col_f)

            # Capa gruesa de nieve sobre las ramas
            for dx in range(-ancho_piso, ancho_piso + 1):
                x = cx + dx
                y_n = y_cima_piso + int(abs(dx) * 0.28)
                if 0 <= x < W and 0 <= y_n < H:
                    c_sn = col_nieve_pino_luz if dx < 0 else col_nieve_pino_somb
                    s.set_at((x, y_n), c_sn)
                    if 0 <= y_n + 1 < H and abs(dx) % 2 == 0:
                        s.set_at((x, y_n + 1), c_sn)

    pines_izq = [
        (18,  275, 115, 38),
        (52,  285, 135, 44),
        (88,  292, 105, 34),
        (120, 305, 85,  28),
    ]
    for px, by, ah, aw in pines_izq:
        _dibujar_pino_majestuoso(surf, px, by, ah, aw)

    pines_der = [
        (622, 275, 115, 38),
        (588, 285, 135, 44),
        (552, 292, 105, 34),
        (520, 305, 85,  28),
    ]
    for px, by, ah, aw in pines_der:
        _dibujar_pino_majestuoso(surf, px, by, ah, aw)

    # Arbustos nevados en las esquinas inferiores
    def _dibujar_arbusto_nevado(s, cx, cy, rad):
        for dy in range(-rad, 2):
            for dx in range(-rad, rad + 1):
                if dx * dx + dy * dy <= rad * rad:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < W and 0 <= y < H:
                        s.set_at((x, y), (26, 52, 34) if dx > 0 else (42, 78, 52))
        for dx in range(-rad, rad + 1):
            y_c = cy - int(math.sqrt(max(0, rad * rad - dx * dx)))
            if 0 <= cx + dx < W and 0 <= y_c < H:
                s.set_at((cx + dx, y_c), (245, 222, 215))

    for ax, ay, ar in [(35, 315, 10), (70, 320, 8), (605, 315, 10), (570, 320, 8)]:
        _dibujar_arbusto_nevado(surf, ax, ay, ar)

    return pygame.transform.scale(surf, (ancho, alto))
