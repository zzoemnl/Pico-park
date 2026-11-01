import os
import sys
import pygame

sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from main import (
    obtener_geometria_panel_partidas,
    COLORES_TABS,
    _dibujar_icono_candado,
)
from fuentes import (
    obtener_fuente,
    obtener_fuente_subtitulo,
    obtener_fuente_pequena,
    obtener_fuente_contador,
    dibujar_texto_en_rect,
)
import sprites

# High quality pixel art icons at ~11-13px
def dibujar_icono_estrella(s, cx, cy):
    """Gema / estrella pixel art nítida (11x11 px)"""
    col_gema = (235, 130, 35)
    col_luz = (255, 220, 110)
    col_borde = (130, 65, 15)
    # Diamante estilizado
    for dy in range(-5, 6):
        w = 5 - abs(dy)
        for dx in range(-w, w + 1):
            if abs(dx) == w or abs(dy) == 5:
                s.set_at((cx + dx, cy + dy), col_borde)
            elif dy <= 0 and dx <= 0:
                s.set_at((cx + dx, cy + dy), col_luz)
            else:
                s.set_at((cx + dx, cy + dy), col_gema)

def dibujar_icono_trofeo(s, cx, cy):
    """Trofeo pixel art nítido (11x12 px)"""
    col_oro = (245, 195, 45)
    col_luz = (255, 240, 140)
    col_borde = (120, 80, 20)
    col_base = (145, 95, 35)
    # Copa
    for dy in range(-5, 0):
        w = 4 - abs(dy + 3) // 2
        for dx in range(-w, w + 1):
            col = col_luz if (dx < 0 and dy < -2) else col_oro
            s.set_at((cx + dx, cy + dy), col)
    # Asas
    for y_asa in [-4, -3, -2]:
        s.set_at((cx - 4, cy + y_asa), col_borde)
        s.set_at((cx + 4, cy + y_asa), col_borde)
    # Borde superior copa
    for dx in range(-3, 4):
        s.set_at((cx + dx, cy - 6), col_borde)
    # Tallo
    s.set_at((cx, cy), col_borde)
    s.set_at((cx, cy + 1), col_base)
    # Base
    for dx in range(-3, 4):
        s.set_at((cx + dx, cy + 2), col_base)
        s.set_at((cx + dx, cy + 3), col_borde)

def dibujar_icono_calendario(s, cx, cy):
    """Calendario pixel art nítido (11x11 px)"""
    col_papel = (252, 248, 238)
    col_rojo = (210, 65, 55)
    col_borde = (110, 80, 55)
    col_linea = (150, 125, 95)
    # Anillas superiores
    s.set_at((cx - 3, cy - 5), col_borde)
    s.set_at((cx + 3, cy - 5), col_borde)
    # Cuerpo
    for dy in range(-4, 6):
        for dx in range(-5, 6):
            if dx in (-5, 5) or dy in (-4, 5):
                s.set_at((cx + dx, cy + dy), col_borde)
            elif dy <= -2:
                s.set_at((cx + dx, cy + dy), col_rojo)
            else:
                s.set_at((cx + dx, cy + dy), col_papel)
    # Puntos de días
    for px, py in [(-2, 0), (0, 0), (2, 0), (-2, 2), (0, 2), (2, 2)]:
        s.set_at((cx + px, cy + py), col_linea)

def dibujar_icono_reloj(s, cx, cy):
    """Reloj pixel art nítido (11x11 px)"""
    col_cuerpo = (252, 248, 238)
    col_borde = (95, 75, 55)
    col_agujas = (55, 38, 24)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            d2 = dx * dx + dy * dy
            if 15 <= d2 <= 26:
                s.set_at((cx + dx, cy + dy), col_borde)
            elif d2 < 15:
                s.set_at((cx + dx, cy + dy), col_cuerpo)
    # Agujas
    s.set_at((cx, cy), col_agujas)
    s.set_at((cx, cy - 1), col_agujas)
    s.set_at((cx, cy - 2), col_agujas)
    s.set_at((cx + 1, cy), col_agujas)
    s.set_at((cx + 2, cy), col_agujas)

print("Icons defined successfully")

