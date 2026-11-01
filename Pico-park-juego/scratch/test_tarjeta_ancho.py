import os
import sys
import pygame

sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from fuentes import obtener_fuente, obtener_fuente_subtitulo, obtener_fuente_pequena, obtener_fuente_contador

# Test metadata text widths with different fonts at size 18 (up from 14, +28.5%)
txt_nivel = "Nivel 2-5"
txt_prog = "9/15 completados"
txt_fecha = "31/10/2026"
txt_hora = "17:05"

for font_name in ["subtitulo", "pequena", "texto", "contador"]:
    f = obtener_fuente(font_name, tamano=18)
    w_n = f.size(txt_nivel)[0]
    w_p = f.size(txt_prog)[0]
    w_f = f.size(txt_fecha)[0]
    w_h = f.size(txt_hora)[0]
    total = w_n + w_p + w_f + w_h + 30 # with spacing
    print(f"Font {font_name} (18): Nivel={w_n}px, Prog={w_p}px, Fecha={w_f}px, Hora={w_h}px -> Total={total}px (Available: ~384px)")

