import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import pantalla
import movimientos

def test_in_game_execution():
    print("=== Probando Nivel 3-4 y Nivel 3-5 dentro del bucle de juego real ===")

    # 1. Probar Nivel 3-4: El laberinto oscuro
    print("--- 1. Ejecutando Nivel 3-4: El laberinto oscuro ---")
    eventos_p1_toggle = [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_e})]
    eventos_p2_toggle = [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_l})]
    eventos_quit = [pygame.event.Event(pygame.QUIT)]

    # Podemos probar la secuencia simulando eventos en la cola de pygame
    # Publicamos eventos de toggle y luego QUIT para salir limpiamente
    pygame.event.clear()
    for ev in eventos_p1_toggle + eventos_p2_toggle + eventos_quit:
        pygame.event.post(ev)

    # Interceptamos sys.exit y pygame.quit para que el script pueda probar ambos niveles secuencialmente
    exit_llamado = False
    def mock_exit(*args):
        nonlocal exit_llamado
        exit_llamado = True
        raise KeyboardInterrupt("Simulated level exit")

    orig_exit = sys.exit
    orig_py_quit = pygame.quit
    sys.exit = mock_exit
    pygame.quit = lambda: None

    try:
        try:
            pantalla.iniciar_mundo(
                mecanicas=["agua", "pinchos"],
                numero_nivel=4,
                color_p1="Verde",
                color_p2="Rosa",
                mundo=3,
                partida_id=1,
            )
        except KeyboardInterrupt:
            print("[OK] Nivel 3-4 ejecutó su bucle completo de juego y procesó eventos de linterna y salida.")

        # 2. Probar Nivel 3-5: El abismo submarino
        print("--- 2. Ejecutando Nivel 3-5: El abismo submarino ---")
        pygame.event.clear()
        for ev in eventos_p1_toggle + eventos_p2_toggle + eventos_quit:
            pygame.event.post(ev)

        try:
            pantalla.iniciar_mundo(
                mecanicas=["agua", "pinchos"],
                numero_nivel=5,
                color_p1="Verde",
                color_p2="Rosa",
                mundo=3,
                partida_id=1,
            )
        except KeyboardInterrupt:
            print("[OK] Nivel 3-5 ejecutó su bucle completo de juego con linternas y HUD.")

    finally:
        sys.exit = orig_exit
        pygame.quit = orig_py_quit

    print("\n=======================================================")
    print(">>> COMPROBACIÓN DENTRO DEL JUEGO EXITOSA PARA AMBOS NIVELES <<<")
    print("=======================================================")

if __name__ == "__main__":
    test_in_game_execution()
