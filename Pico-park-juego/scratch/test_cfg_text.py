import os
import sys
import pygame

sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from fuentes import obtener_fuente_subtitulo

for s in [16, 17, 18, 19, 20]:
    f = obtener_fuente_subtitulo(s, negrita=True)
    f_zh = pygame.font.SysFont("Microsoft YaHei", s, bold=True)
    w_es = f.size("Español")[0]
    w_en = f.size("English")[0]
    w_zh = f_zh.size("简体中文")[0]
    print(f"size {s}: Español={w_es}px, English={w_en}px, Chinese={w_zh}px (btn width: 136px)")
