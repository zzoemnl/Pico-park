import os
import sys
import pygame

sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from fuentes import obtener_fuente_pequena

for s in [14, 17, 18, 19]:
    f = obtener_fuente_pequena(s)
    print(f"Nanoplex {s}: Nivel={f.size('Nivel 2-5')}, Prog={f.size('9/15 completados')}, Fecha={f.size('31/10/2026')}, Hora={f.size('17:05')}")
