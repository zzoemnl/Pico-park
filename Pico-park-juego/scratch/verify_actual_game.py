import pygame
import os
import time

os.environ['SDL_VIDEODRIVER'] = 'dummy' # Run headless or offscreen to capture actual game frame
import main

def test_actual_menu_flow():
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720))
    reloj = pygame.time.Clock()

    # Load resources
    main._cargar_recursos_modo_juego()
    bg = main._obtener_fondo_modo_juego(1280, 720)
    print("Background loaded:", bg.get_size())

if __name__ == '__main__':
    test_actual_menu_flow()
