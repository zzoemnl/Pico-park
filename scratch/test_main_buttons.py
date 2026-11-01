import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
pygame.init()
import sprites

for b in ["Menu/jugar.png", "Menu/personajes.png", "Menu/opciones.png", "Menu/salir.png"]:
    marco = sprites.generar_marco_boton(b, 272, 80)
    print(b, "marco:", marco is not None)
    btn_zh = sprites.generar_boton_con_texto(b, 272, 80, "测试", (255, 255, 255), 24, 0, "zh")
    print(b, "btn_zh:", btn_zh is not None)
    if btn_zh:
        pygame.image.save(btn_zh, f"scratch/test_{os.path.basename(b)}_zh.png")

print("Generated test main buttons!")

