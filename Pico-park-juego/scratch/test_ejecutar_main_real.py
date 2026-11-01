import os
import sys

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import main

print("Iniciando main() de prueba...")

# Interceptar pygame.display.flip para capturar los primeros frames y luego salir
frame_count = 0
def hook_flip():
    global frame_count
    frame_count += 1
    if frame_count == 3:
        pantalla = pygame.display.get_surface()
        pygame.image.save(pantalla, "scratch/captura_juego_main_real.png")
        print("Captura del juego real guardada en scratch/captura_juego_main_real.png")
        # Forzar salida limpia del bucle principal
        pygame.event.post(pygame.event.Event(pygame.QUIT))

pygame.display.flip = hook_flip

try:
    main.main()
except SystemExit:
    pass

print("Ejecución de main() finalizada con éxito!")
