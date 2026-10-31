import math
import random
import pygame
import os

def generar_fondo_diario(ancho=1280, alto=720):
    """
    Fondo estilo Antiguo Diario de Aventuras / Registro de Expediciones.
    - Paleta: pergamino crema, beige, marfil, marrón cuero y acentos dorados.
    - Textura sutil de papel antiguo con fibras tenues.
    - Bordes suavemente envejecidos con esquinas cantoneras de cuero/latón.
    - Dibujos discretos a tinta sepia: montañitas de mapa, líneas de ruta punteada,
      brújula de expedición y estrellas de navegación.
    - Centro despejado y limpio para el panel de fichas.
    """
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. Base pergamino: gradiente cálido crema-beige
    for y in range(H):
        t = y / H
        r = int(246 - 16 * t)
        g = int(235 - 18 * t)
        b = int(208 - 22 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W - 1, y))

    # 2. Textura sutil de papel antiguo (grano fino y fibras dispersas)
    rnd_papel = random.Random(3344)
    for _ in range(3500):
        px = rnd_papel.randint(0, W - 1)
        py = rnd_papel.randint(0, H - 1)
        c = surf.get_at((px, py))
        delta = rnd_papel.randint(-8, 6)
        surf.set_at((px, py), (
            max(0, min(255, c.r + delta)),
            max(0, min(255, c.g + delta)),
            max(0, min(255, c.b + delta)),
        ))

    # Pequeñas fibras longitudinales de papel artesanal
    for _ in range(60):
        fx = rnd_papel.randint(10, W - 20)
        fy = rnd_papel.randint(5, H - 5)
        flen = rnd_papel.randint(3, 8)
        col_fibra = (220, 205, 178)
        for dx in range(flen):
            if fx + dx < W:
                surf.set_at((fx + dx, fy), col_fibra)

    # 3. Viñeta y bordes envejecidos (envejecimiento suave en los extremos)
    for y in range(H):
        for x in range(W):
            # Distancia a los bordes
            dist_x = min(x, W - 1 - x)
            dist_y = min(y, H - 1 - y)
            dist_borde = min(dist_x, dist_y)
            if dist_borde < 24:
                factor = dist_borde / 24.0
                c = surf.get_at((x, y))
                surf.set_at((x, y), (
                    int(c.r * (0.82 + 0.18 * factor)),
                    int(c.g * (0.80 + 0.20 * factor)),
                    int(c.b * (0.75 + 0.25 * factor)),
                ))

    # 4. Marco / Filete perimetral doble estilo encuadernación de diario
    col_filete = (195, 172, 138)
    col_filete_dorado = (215, 185, 125)
    m1 = 8
    m2 = 12
    # Filete exterior
    pygame.draw.rect(surf, col_filete, (m1, m1, W - m1 * 2, H - m1 * 2), 1)
    # Filete interior
    pygame.draw.rect(surf, col_filete_dorado, (m2, m2, W - m2 * 2, H - m2 * 2), 1)

    # 5. Cantoneras decorativas en las 4 esquinas (estilo esquinas de cuero / herrajes de diario)
    def _cantonera(s, cx, cy, dir_x, dir_y):
        tam = 14
        col_cuero = (118, 72, 45)
        col_oro = (210, 175, 95)
        col_remache = (245, 220, 140)
        # Triángulo de cantonera
        for i in range(tam):
            x1 = cx
            x2 = cx + dir_x * (tam - i)
            y = cy + dir_y * i
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < W and 0 <= y < H:
                    s.set_at((x, y), col_cuero if (x + y) % 3 != 0 else col_oro)
        # Remache dorado
        rx = cx + dir_x * 5
        ry = cy + dir_y * 5
        if 0 <= rx < W and 0 <= ry < H:
            s.set_at((rx, ry), col_remache)
            s.set_at((rx + dir_x, ry), col_oro)
            s.set_at((rx, ry + dir_y), col_oro)

    _cantonera(surf, m1, m1, 1, 1)
    _cantonera(surf, W - m1 - 1, m1, -1, 1)
    _cantonera(surf, m1, H - m1 - 1, 1, -1)
    _cantonera(surf, W - m1 - 1, H - m1 - 1, -1, -1)

    # 6. DIBUJOS ILUSTRADOS DISCRETOS A TINTA SEPIA (Bordes / márgenes)
    col_tinta = (135, 102, 72)
    col_tinta_suave = (168, 138, 105)
    col_tinta_tenue = (195, 170, 138)

    # A) Pequeña cordillera de mapa ilustrada en la esquina superior izquierda
    # (x: 25 a 115, y: 22 a 65)
    picos_mapa = [(38, 38, 16), (56, 30, 22), (76, 34, 18), (95, 42, 14)]
    for mx, my, mh in picos_mapa:
        # Silueta dibujada a plumilla
        w_b = int(mh * 0.9)
        # Línea izquierda
        pygame.draw.line(surf, col_tinta, (mx, my), (mx - w_b, my + mh), 1)
        # Línea derecha
        pygame.draw.line(surf, col_tinta, (mx, my), (mx + w_b, my + mh), 1)
        # Arista central
        pygame.draw.line(surf, col_tinta_suave, (mx, my), (mx + 2, my + mh), 1)
        # Rayado de sombra (hatching) en cara derecha
        for h_step in range(4, mh, 3):
            y_h = my + h_step
            prog = h_step / mh
            x_start = mx + int(2 * prog)
            x_end = mx + int(w_b * prog)
            pygame.draw.line(surf, col_tinta_tenue, (x_start, y_h), (x_end, y_h), 1)

    # B) Rosa de los vientos / Brújula de explorador discreta en esquina inferior izquierda
    # (cx: 48, cy: 318)
    bx, by, br = 46, 318, 18
    # Círculo exterior e interior
    pygame.draw.circle(surf, col_tinta_suave, (bx, by), br, 1)
    pygame.draw.circle(surf, col_filete_dorado, (bx, by), br - 3, 1)
    # Puntas N, S, E, O
    for ang, tam_p in [(0, br), (90, br - 3), (180, br - 3), (270, br - 3)]:
        rad = math.radians(ang - 90)
        x_tip = bx + int(math.cos(rad) * tam_p)
        y_tip = by + int(math.sin(rad) * tam_p)
        rad_izq = math.radians(ang - 90 - 25)
        rad_der = math.radians(ang - 90 + 25)
        x_izq = bx + int(math.cos(rad_izq) * 4)
        y_izq = by + int(math.sin(rad_izq) * 4)
        x_der = bx + int(math.cos(rad_der) * 4)
        y_der = by + int(math.sin(rad_der) * 4)
        col_punta = (185, 65, 52) if ang == 0 else col_tinta  # Norte rojo explorador
        pygame.draw.polygon(surf, col_punta, [(bx, by), (x_tip, y_tip), (x_izq, y_izq)])
        pygame.draw.polygon(surf, col_tinta_suave, [(bx, by), (x_tip, y_tip), (x_der, y_der)], 1)
    # Letra 'N' pequeña sobre la brújula
    surf.set_at((bx - 1, by - br - 5), col_tinta)
    surf.set_at((bx - 1, by - br - 4), col_tinta)
    surf.set_at((bx - 1, by - br - 3), col_tinta)
    surf.set_at((bx, by - br - 4), col_tinta)
    surf.set_at((bx + 1, by - br - 5), col_tinta)
    surf.set_at((bx + 1, by - br - 4), col_tinta)
    surf.set_at((bx + 1, by - br - 3), col_tinta)

    # C) Ruta de expedición punteada (curva suave que conecta puntos)
    puntos_ruta = [
        (bx + 26, by - 8),
        (bx + 40, by - 16),
        (bx + 56, by - 12),
        (bx + 72, by - 22),
    ]
    for rx, ry in puntos_ruta:
        surf.set_at((rx, ry), col_tinta_suave)
        surf.set_at((rx + 1, ry), col_tinta_suave)

    # D) Constelación de estrellas y pequeña cordillera en la esquina derecha
    picos_der = [(555, 36, 16), (575, 28, 22), (595, 34, 18), (612, 42, 14)]
    for mx, my, mh in picos_der:
        w_b = int(mh * 0.9)
        pygame.draw.line(surf, col_tinta, (mx, my), (mx - w_b, my + mh), 1)
        pygame.draw.line(surf, col_tinta, (mx, my), (mx + w_b, my + mh), 1)
        pygame.draw.line(surf, col_tinta_suave, (mx, my), (mx - 2, my + mh), 1)
        for h_step in range(4, mh, 3):
            y_h = my + h_step
            prog = h_step / mh
            x_start = mx - int(w_b * prog)
            x_end = mx - int(2 * prog)
            pygame.draw.line(surf, col_tinta_tenue, (x_start, y_h), (x_end, y_h), 1)

    # Estrellas de navegación en margen derecho superior e inferior
    def _estrella_dibujada(s, ex, ey):
        surf.set_at((ex, ey), (218, 175, 95))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surf.set_at((ex + dx, ey + dy), col_tinta_suave)

    _estrella_dibujada(surf, 535, 30)
    _estrella_dibujada(surf, 520, 48)
    _estrella_dibujada(surf, 605, 318)
    _estrella_dibujada(surf, 585, 332)

    # E) Pequeños arbolitos de mapa a los costados
    def _arbolito_tinta(s, ax, ay):
        col_tronco = (120, 85, 55)
        surf.set_at((ax, ay), col_tronco)
        surf.set_at((ax, ay + 1), col_tronco)
        # Copa triangular
        surf.set_at((ax, ay - 4), col_tinta)
        for dx in range(-1, 2):
            surf.set_at((ax + dx, ay - 3), col_tinta)
        for dx in range(-2, 3):
            surf.set_at((ax + dx, ay - 2), col_tinta)
        for dx in range(-2, 3):
            surf.set_at((ax + dx, ay - 1), col_tinta)

    for ax, ay in [(26, 85), (32, 98), (614, 85), (608, 98), (605, 300)]:
        _arbolito_tinta(surf, ax, ay)

    return pygame.transform.scale(surf, (ancho, alto))


if __name__ == '__main__':
    pygame.init()
    fondo = generar_fondo_diario(1280, 720)
    pygame.image.save(fondo, "scratch/test_fondo_diario.png")
    print("Fondo generado: scratch/test_fondo_diario.png")
