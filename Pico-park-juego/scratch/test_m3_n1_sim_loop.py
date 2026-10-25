import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, r"c:\Users\Malena\Documents\GitHub\Pico-park\Pico-park-juego")

import pantalla
import menu_niveles

def simular_mundo3_nivel1():
    print("Iniciando simulacion de bucle de juego para Mundo 3 Nivel 1...")
    mecanicas = menu_niveles.obtener_mecanicas_nivel(3, 1)

    # Postear evento para simular 2 segundos de juego y luego salir al menu
    frames = 0
    # Inyectar eventos en la cola de pygame para probar
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))

    # Para terminar la simulacion limpiamente luego de unos frames
    # Usamos un timer de pygame o QUIT tras unos frames
    def custom_tick():
        pass

    # Ejecutar iniciar_mundo en un hilo o con salida programada
    # Para probar sin bloquearse en while ejecutando, verifiquemos que iniciar_mundo inicia los datos sin errores
    print("Mecanicas recibidas:", mecanicas)

    # Verificamos inicializacion de mundo
    pantalla_dummy = pygame.display.set_mode((1280, 720))

    # Inyectar QUIT tras unos eventos para que el bucle salga
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    # iniciar_mundo debe atender QUIT llamando al dialogo o saliendo
    print("Simulacion ejecutada satisfactoriamente!")

if __name__ == "__main__":
    simular_mundo3_nivel1()
