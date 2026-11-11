import pygame
import os
import sys

sys.path.insert(0, "Pico-park-juego")
import fuentes
import sprites

pygame.init()
pantalla = pygame.Surface((600, 300))

# Test both "Español" and "ESPAÑOL"
for txt in ["Español", "ESPAÑOL", "English", "ENGLISH"]:
    btn_norm = sprites.generar_boton_con_texto("mundos/boton-volver.png", 136, 42, txt, (60, 45, 30), 18)
    btn_act = sprites.generar_boton_con_texto("mundos/boton-cargar.png", 136, 42, txt, (26, 83, 29), 18)
    if btn_norm:
        pygame.image.save(btn_norm, f"scratch/test_btn_{txt}_norm.png")
    if btn_act:
        pygame.image.save(btn_act, f"scratch/test_btn_{txt}_act.png")

print("Generated test buttons successfully!")

