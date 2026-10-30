"""
Generador y validador del Escenario Navideño Completo en Pixel Art (640x360 -> 1280x720)
con plataformas, árboles, cabaña, cielo dithered, suelo y decoraciones.
"""
import math
import random
import os
import sys
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

CARPETA_ARTIFACTS = r"C:\Users\Malena\.gemini\antigravity-ide\brain\e4ef99ac-8461-4560-8170-5a437f43e801"

# Paleta pixel art navideña consistente
CIELO_1 = (22, 30, 56)      # Noche profunda
CIELO_2 = (38, 54, 94)      # Azul crepúsculo
CIELO_3 = (68, 92, 140)     # Índigo suave
CIELO_4 = (128, 148, 188)   # Lavanda fría
CIELO_5 = (198, 178, 192)   # Resplandor horizonte cálido

MONTANA_LUZ = (82, 102, 142)
MONTANA_SOMBRA = (58, 74, 108)
NIEVE_PURA = (255, 255, 255)
NIEVE_SOMBRA = (185, 205, 235)
NIEVE_BASE = (215, 230, 248)

PINO_OSCURO = (18, 52, 28)
PINO_MEDIO = (28, 80, 44)
PINO_CLARO = (44, 112, 62)

MADERA_OSCURA = (42, 24, 14)
MADERA_MEDIA = (72, 44, 26)
MADERA_CLARA = (108, 68, 42)

ESTRELLA_ORO = (255, 218, 50)
ESTRELLA_BRILLO = (255, 245, 170)

def dibujar_arbol_pixel(surf, cx, cy_base, w_arbol, h_arbol):
    # Tronco pixel
    w_t = max(4, w_arbol // 7)
    h_t = max(6, h_arbol // 8)
    pygame.draw.rect(surf, MADERA_OSCURA, (cx - w_t // 2, cy_base - h_t, w_t, h_t))
    pygame.draw.rect(surf, MADERA_MEDIA, (cx - w_t // 2 + 1, cy_base - h_t, w_t - 2, h_t))

    # Tiers de follaje (4 capas)
    num_tiers = 4
    tier_h = (h_arbol - h_t) // num_tiers
    for t in range(num_tiers):
        y_b = cy_base - h_t - (t * (tier_h - 2))
        y_top = y_b - tier_h - 4
        ancho_t = int(w_arbol * (1.0 - t * 0.18))
        
        # Bloques de follaje en pasos pixel art
        for y in range(y_top, y_b):
            prog = (y - y_top) / float(max(1, y_b - y_top))
            span = int((ancho_t // 2) * prog)
            # Follaje izquierdo (con sombra o luz)
            for x in range(cx - span, cx):
                col = PINO_CLARO if (x - cx) % 3 == 0 else PINO_MEDIO
                surf.set_at((x, y), col)
            # Follaje derecho (sombra)
            for x in range(cx, cx + span + 1):
                col = PINO_MEDIO if (x - cx) % 3 == 0 else PINO_OSCURO
                surf.set_at((x, y), col)
            # Manto de nieve sobre la parte superior del tier
            if y < y_top + 3:
                for x in range(cx - span, cx + span + 1):
                    surf.set_at((x, y), NIEVE_PURA)
            elif y < y_top + 5:
                for x in range(cx - span, cx + span + 1):
                    if (x + y) % 2 == 0:
                        surf.set_at((x, y), NIEVE_SOMBRA)

        # Bolas navideñas en el tier
        if t < 3:
            colores_baubles = [(235, 50, 60), (255, 215, 40), (50, 200, 240), (210, 80, 220)]
            bx1 = cx - ancho_t // 3
            bx2 = cx + ancho_t // 4
            by = y_b - 3
            c1 = colores_baubles[(t * 2) % len(colores_baubles)]
            c2 = colores_baubles[(t * 2 + 1) % len(colores_baubles)]
            surf.set_at((bx1, by), c1)
            surf.set_at((bx1, by - 1), (255, 255, 255))
            surf.set_at((bx2, by - 2), c2)
            surf.set_at((bx2, by - 3), (255, 255, 255))

    # Estrella dorada pixel art en la cima
    y_est = cy_base - h_arbol
    for dx, dy in [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        surf.set_at((cx + dx, y_est + dy), ESTRELLA_ORO)
    surf.set_at((cx, y_est), ESTRELLA_BRILLO)

def dibujar_plataforma_pixel(surf, rx, ry, rw, rh):
    # Cuerpo de madera pixel art
    pygame.draw.rect(surf, MADERA_OSCURA, (rx, ry, rw, rh))
    pygame.draw.rect(surf, MADERA_MEDIA, (rx + 1, ry + 2, rw - 2, rh - 3))
    # Vetas de madera
    for x in range(rx + 4, rx + rw - 4, 8):
        surf.set_at((x, ry + 4), MADERA_CLARA)
        surf.set_at((x + 1, ry + 5), MADERA_CLARA)

    # Nieve esponjosa en la parte superior
    pygame.draw.rect(surf, NIEVE_PURA, (rx - 1, ry - 3, rw + 2, 4))
    pygame.draw.line(surf, NIEVE_SOMBRA, (rx, ry + 1), (rx + rw, ry + 1), 1)

    # Pequeños carámbanos de hielo pixel art colgando abajo
    for ix in range(rx + 6, rx + rw - 6, 10):
        h_icicle = ((ix * 7) % 3) + 2
        for dy in range(h_icicle):
            col_ice = NIEVE_PURA if dy == 0 else (180, 215, 245)
            surf.set_at((ix, ry + rh + dy), col_ice)

def generar_fondo_completo():
    w, h = 640, 360
    surf = pygame.Surface((w, h))

    # 1. Cielo en bandas dithered
    bandas = [
        (0, 60, CIELO_1),
        (60, 120, CIELO_2),
        (120, 180, CIELO_3),
        (180, 240, CIELO_4),
        (240, 360, CIELO_5),
    ]
    for y1, y2, col in bandas:
        pygame.draw.rect(surf, col, (0, y1, w, y2 - y1))

    for i in range(len(bandas) - 1):
        yt = bandas[i][1]
        c_up = bandas[i][2]
        c_dn = bandas[i + 1][2]
        for y in range(yt - 2, yt + 2):
            for x in range(w):
                if y == yt - 2 and x % 4 == 0:
                    surf.set_at((x, y), c_dn)
                elif y == yt - 1 and (x + y) % 2 == 0:
                    surf.set_at((x, y), c_dn)
                elif y == yt and (x + y) % 2 == 0:
                    surf.set_at((x, y), c_up)
                elif y == yt + 1 and x % 4 == 0:
                    surf.set_at((x, y), c_up)

    # Estrellas pixel en el cielo
    rnd = random.Random(42)
    for _ in range(35):
        sx = rnd.randint(10, w - 10)
        sy = rnd.randint(8, 110)
        surf.set_at((sx, sy), (255, 255, 255))
        if rnd.random() < 0.3:
            surf.set_at((sx + 1, sy), (255, 240, 180))

    # Nubes pixel art esponjosas en la distancia
    def _nube_pixel(nx, ny, nw, nh):
        for cy in range(ny, ny + nh):
            p_y = (cy - ny) / float(nh)
            rx = int((nw // 2) * math.sin(p_y * math.pi))
            for cx in range(nx - rx, nx + rx):
                surf.set_at((cx, cy), (170, 190, 220))
                if cy < ny + nh // 2:
                    surf.set_at((cx, cy), (225, 235, 248))
    _nube_pixel(110, 100, 70, 16)
    _nube_pixel(460, 95, 80, 18)
    _nube_pixel(280, 130, 60, 14)

    # 2. Montañas lejanas pixel art
    picos = [(90, 120, 160), (220, 95, 180), (350, 130, 150), (460, 105, 170), (560, 125, 160)]
    y_base_montana = 260
    for px, py, ancho_m in picos:
        for y in range(py, y_base_montana):
            prog = (y - py) / float(y_base_montana - py)
            half = int((ancho_m // 2) * prog)
            for x in range(px - half, px):
                surf.set_at((x, y), MONTANA_LUZ)
            for x in range(px, px + half + 1):
                surf.set_at((x, y), MONTANA_SOMBRA)
            if prog < 0.28:
                for x in range(px - half, px):
                    surf.set_at((x, y), NIEVE_PURA)
                for x in range(px, px + half + 1):
                    surf.set_at((x, y), NIEVE_SOMBRA)

    # 3. Colina intermedia con pinos y cabaña acogedora
    for x in range(w):
        y_col = int(245 + 16 * math.sin(x * 0.012 + 0.5))
        for y in range(y_col, 360):
            surf.set_at((x, y), (175, 195, 225))

    # Cabaña pixel en (170, 240)
    cx_cab, cy_cab = 175, 242
    pygame.draw.rect(surf, MADERA_OSCURA, (cx_cab, cy_cab, 32, 22))
    for ly in range(cy_cab + 4, cy_cab + 22, 4):
        pygame.draw.line(surf, MADERA_MEDIA, (cx_cab + 1, ly), (cx_cab + 30, ly), 1)
    # Techo nevado cabaña
    pts_t = [(cx_cab - 4, cy_cab), (cx_cab + 16, cy_cab - 12), (cx_cab + 36, cy_cab)]
    pygame.draw.polygon(surf, NIEVE_PURA, pts_t)
    pygame.draw.line(surf, NIEVE_SOMBRA, pts_t[0], pts_t[2], 1)
    # Ventana iluminada
    pygame.draw.rect(surf, (255, 215, 60), (cx_cab + 6, cy_cab + 6, 8, 8))
    pygame.draw.line(surf, MADERA_OSCURA, (cx_cab + 10, cy_cab + 6), (cx_cab + 10, cy_cab + 13), 1)
    pygame.draw.line(surf, MADERA_OSCURA, (cx_cab + 6, cy_cab + 10), (cx_cab + 13, cy_cab + 10), 1)
    # Chimenea y humo
    pygame.draw.rect(surf, (90, 95, 105), (cx_cab + 22, cy_cab - 14, 6, 10))
    surf.set_at((cx_cab + 24, cy_cab - 17), (230, 235, 245))
    surf.set_at((cx_cab + 25, cy_cab - 18), (230, 235, 245))
    surf.set_at((cx_cab + 26, cy_cab - 22), (210, 220, 235))
    surf.set_at((cx_cab + 28, cy_cab - 26), (200, 215, 230))

    # 4. Árboles de Navidad principales
    # Izquierda
    dibujar_arbol_pixel(surf, cx=90, cy_base=325, w_arbol=95, h_arbol=145)
    dibujar_arbol_pixel(surf, cx=32, cy_base=325, w_arbol=60, h_arbol=100)
    # Derecha
    dibujar_arbol_pixel(surf, cx=550, cy_base=325, w_arbol=95, h_arbol=145)
    dibujar_arbol_pixel(surf, cx=608, cy_base=325, w_arbol=60, h_arbol=100)

    # 5. Suelo nevado (y = 325 a 360, equivalente a 650 en 720p)
    y_suelo = 325
    pygame.draw.rect(surf, (165, 190, 220), (0, y_suelo, w, h - y_suelo))
    pygame.draw.rect(surf, NIEVE_PURA, (0, y_suelo - 2, w, 6))
    pygame.draw.line(surf, (245, 250, 255), (0, y_suelo - 2), (w, y_suelo - 2), 1)
    pygame.draw.line(surf, NIEVE_SOMBRA, (0, y_suelo + 4), (w, y_suelo + 4), 1)
    for x in range(4, w, 6):
        if x % 12 == 0:
            surf.set_at((x, y_suelo + 8), NIEVE_PURA)
            surf.set_at((x + 1, y_suelo + 9), NIEVE_SOMBRA)

    # Regalos pixel bajo los árboles
    # Rojo y oro (izq)
    pygame.draw.rect(surf, (225, 45, 50), (60, y_suelo - 12, 13, 12))
    pygame.draw.line(surf, ESTRELLA_ORO, (66, y_suelo - 12), (66, y_suelo - 1), 1)
    pygame.draw.line(surf, ESTRELLA_ORO, (60, y_suelo - 7), (72, y_suelo - 7), 1)
    # Celeste (izq)
    pygame.draw.rect(surf, (50, 170, 230), (120, y_suelo - 9, 11, 9))
    pygame.draw.line(surf, NIEVE_PURA, (125, y_suelo - 9), (125, y_suelo - 1), 1)
    # Oro (der)
    pygame.draw.rect(surf, (250, 205, 40), (510, y_suelo - 11, 12, 11))
    pygame.draw.line(surf, (30, 140, 60), (515, y_suelo - 11), (515, y_suelo - 1), 1)

    # Farolito de madera cálido (der)
    fx = 465
    pygame.draw.line(surf, MADERA_OSCURA, (fx, y_suelo - 22), (fx, y_suelo), 2)
    pygame.draw.rect(surf, (255, 230, 80), (fx - 3, y_suelo - 22, 6, 6))
    surf.set_at((fx, y_suelo - 20), (255, 255, 255))
    pygame.draw.rect(surf, NIEVE_PURA, (fx - 4, y_suelo - 24, 8, 2))

    # 6. Plataformas Pixel Art (en coordenadas escaladas 2x: divididas por 2)
    # 6 plataformas: 3 izquierda, 3 derecha
    dibujar_plataforma_pixel(surf, 65, 260, 75, 9)     # Izq baja (equiv 130, 520, 150, 18)
    dibujar_plataforma_pixel(surf, 22, 190, 65, 9)     # Izq media (equiv 44, 380, 130, 18)
    dibujar_plataforma_pixel(surf, 130, 130, 65, 9)    # Centro-izq alta (equiv 260, 260, 130, 18)
    dibujar_plataforma_pixel(surf, 500, 260, 75, 9)    # Der baja (equiv 1000, 520, 150, 18)
    dibujar_plataforma_pixel(surf, 553, 190, 65, 9)    # Der media (equiv 1106, 380, 130, 18)
    dibujar_plataforma_pixel(surf, 445, 130, 65, 9)    # Centro-der alta (equiv 890, 260, 130, 18)

    # 7. Viga del techo y guirnalda pixel (y = 0 a 17, equiv 0 a 34)
    pygame.draw.rect(surf, MADERA_OSCURA, (0, 0, w, 12))
    pygame.draw.line(surf, MADERA_MEDIA, (0, 1), (w, 1), 1)
    pygame.draw.line(surf, (26, 14, 8), (0, 11), (w, 11), 1)
    # Festones de guirnalda
    for gx in range(0, w, 12):
        pts_g = [(gx, 8), (gx + 6, 15), (gx + 12, 8)]
        pygame.draw.polygon(surf, PINO_OSCURO, pts_g)
        surf.set_at((gx + 6, 13), PINO_MEDIO)
        surf.set_at((gx + 6, 14), PINO_CLARO)
    pygame.draw.rect(surf, NIEVE_PURA, (0, 15, w, 2))

    # Pilares de pared laterales (x=0..14 y x=626..640)
    pygame.draw.rect(surf, MADERA_OSCURA, (0, 0, 14, y_suelo))
    pygame.draw.line(surf, MADERA_MEDIA, (1, 0), (1, y_suelo), 1)
    pygame.draw.rect(surf, NIEVE_PURA, (12, 0, 2, y_suelo))

    pygame.draw.rect(surf, MADERA_OSCURA, (w - 14, 0, 14, y_suelo))
    pygame.draw.line(surf, MADERA_MEDIA, (w - 2, 0), (w - 2, y_suelo), 1)
    pygame.draw.rect(surf, NIEVE_PURA, (w - 14, 0, 2, y_suelo))

    return surf

fondo_640 = generar_fondo_completo()
fondo_1280 = pygame.transform.scale(fondo_640, (1280, 720))
pygame.image.save(fondo_1280, os.path.join(CARPETA_ARTIFACTS, "test_fondo_pixel_art_completo.png"))
print("Fondo pixel art completo guardado.")
