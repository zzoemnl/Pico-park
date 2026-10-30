"""
Prueba visual de estilos pixel art: 320x180 (4x) vs 640x360 (2x)
"""
import os
import sys
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

CARPETA_ARTIFACTS = r"C:\Users\Malena\.gemini\antigravity-ide\brain\e4ef99ac-8461-4560-8170-5a437f43e801"

# Paleta pixel art
CIELO_1 = (24, 32, 60)
CIELO_2 = (42, 62, 104)
CIELO_3 = (78, 108, 156)
CIELO_4 = (142, 166, 204)
CIELO_5 = (210, 192, 204)

MONTANA_DARK = (60, 76, 110)
MONTANA_LIGHT = (84, 104, 144)
NIEVE_BASE = (240, 246, 255)
NIEVE_SOMBRA = (180, 200, 230)
PINO_DARK = (20, 52, 32)
PINO_MED = (32, 82, 48)
PINO_LIGHT = (48, 116, 68)

def generar_fondo_pixel(w, h):
    surf = pygame.Surface((w, h))
    
    # 1. Bandas de cielo con tramado / dithering pixel art
    bandas = [
        (0, int(h * 0.18), CIELO_1),
        (int(h * 0.18), int(h * 0.35), CIELO_2),
        (int(h * 0.35), int(h * 0.52), CIELO_3),
        (int(h * 0.52), int(h * 0.70), CIELO_4),
        (int(h * 0.70), h, CIELO_5),
    ]
    for y_ini, y_fin, col in bandas:
        pygame.draw.rect(surf, col, (0, y_ini, w, y_fin - y_ini))
    
    # Dithering entre bandas
    for i in range(len(bandas) - 1):
        y_trans = bandas[i][1]
        col_arriba = bandas[i][2]
        col_abajo = bandas[i + 1][2]
        # 4 líneas de tramado checkerboard
        for y in range(y_trans - 2, y_trans + 3):
            for x in range(w):
                if y == y_trans - 2 and (x % 4 == 0):
                    surf.set_at((x, y), col_abajo)
                elif y == y_trans - 1 and ((x + y) % 2 == 0):
                    surf.set_at((x, y), col_abajo)
                elif y == y_trans and ((x + y) % 2 == 0):
                    surf.set_at((x, y), col_arriba)
                elif y == y_trans + 1 and (x % 4 == 0):
                    surf.set_at((x, y), col_arriba)

    # 2. Montañas pixel art con escalones
    y_base_montana = int(h * 0.72)
    picos = [(int(w * 0.15), int(h * 0.32)), (int(w * 0.40), int(h * 0.24)), (int(w * 0.65), int(h * 0.28)), (int(w * 0.88), int(h * 0.35))]
    for px, py in picos:
        ancho_m = int(w * 0.28)
        # Dibujar montaña paso a paso con bloques
        for step_y in range(py, y_base_montana):
            prog = (step_y - py) / float(y_base_montana - py)
            ancho_step = int(ancho_m * prog)
            x_left = px - ancho_step // 2
            x_right = px + ancho_step // 2
            # Sombra derecha, luz izquierda
            for x in range(x_left, px):
                if 0 <= x < w:
                    surf.set_at((x, step_y), MONTANA_LIGHT)
            for x in range(px, x_right):
                if 0 <= x < w:
                    surf.set_at((x, step_y), MONTANA_DARK)
            # Nieve en la cima
            if prog < 0.28:
                for x in range(x_left, px):
                    if 0 <= x < w:
                        surf.set_at((x, step_y), NIEVE_BASE)
                for x in range(px, x_right):
                    if 0 <= x < w:
                        surf.set_at((x, step_y), NIEVE_SOMBRA)

    # 3. Suelo nevado pixel art
    y_suelo = int(h * 0.88)
    pygame.draw.rect(surf, NIEVE_BASE, (0, y_suelo, w, h - y_suelo))
    pygame.draw.line(surf, (255, 255, 255), (0, y_suelo), (w, y_suelo), 1)
    pygame.draw.line(surf, NIEVE_SOMBRA, (0, y_suelo + 2), (w, y_suelo + 2), 1)

    return surf

# Generar versión 320x180
s320 = generar_fondo_pixel(320, 180)
s320_scaled = pygame.transform.scale(s320, (1280, 720))
pygame.image.save(s320_scaled, os.path.join(CARPETA_ARTIFACTS, "test_pixel_320.png"))

# Generar versión 640x360
s640 = generar_fondo_pixel(640, 360)
s640_scaled = pygame.transform.scale(s640, (1280, 720))
pygame.image.save(s640_scaled, os.path.join(CARPETA_ARTIFACTS, "test_pixel_640.png"))

print("Pruebas generadas en artifacts.")
