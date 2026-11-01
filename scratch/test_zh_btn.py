import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
import fuentes
import sprites

pygame.init()
btn_norm = sprites.generar_boton_con_texto("mundos/boton-volver.png", 136, 42, "简体中文", (60, 45, 30), 18)
btn_act = sprites.generar_boton_con_texto("mundos/boton-cargar.png", 136, 42, "简体中文", (26, 83, 29), 18)
if btn_norm:
    pygame.image.save(btn_norm, "scratch/test_btn_zh_norm.png")
if btn_act:
    pygame.image.save(btn_act, "scratch/test_btn_zh_act.png")

