import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
import sprites

pygame.init()
m1 = sprites.generar_marco_boton("Menu/boton-continuar-cargar....png", 425, 100)
m2 = sprites.generar_marco_boton("mundos/boton-nueva-partida-reiniciar....png", 425, 100)

if m1: pygame.image.save(m1, "scratch/test_marco_continuar.png")
if m2: pygame.image.save(m2, "scratch/test_marco_nueva.png")
print("Saved marco test")

