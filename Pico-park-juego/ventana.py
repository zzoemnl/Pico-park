"""
Creación de la ventana del juego en pantalla completa adaptada al monitor.

El juego está diseñado para una resolución fija de 1280x720. En lugar de
reescribir todas las coordenadas, se usa pygame.SCALED: el juego sigue dibujando
en una superficie lógica de 1280x720 y pygame la escala al tamaño real de la
pantalla, con bandas negras si la proporción no es 16:9. Las coordenadas del
mouse ya llegan traducidas a la resolución lógica, así que el resto del código
no necesita cambios.

F11 alterna entre pantalla completa y ventana. Como el juego tiene decenas de
loops de eventos distintos, en vez de agregar el manejo en cada uno se
intercepta una sola vez envolviendo pygame.event.get.
"""
import pygame

ANCHO_LOGICO, ALTO_LOGICO = 1280, 720
TECLA_PANTALLA_COMPLETA = pygame.K_F11

_event_get_original = None


def crear_ventana(pantalla_completa=True):
    global _event_get_original
    flags = pygame.SCALED | (pygame.FULLSCREEN if pantalla_completa else 0)
    superficie = pygame.display.set_mode((ANCHO_LOGICO, ALTO_LOGICO), flags)
    if _event_get_original is None:
        _event_get_original = pygame.event.get
        pygame.event.get = _event_get_con_f11
    return superficie


def alternar_pantalla_completa():
    pygame.display.toggle_fullscreen()


def _event_get_con_f11(*args, **kwargs):
    eventos = _event_get_original(*args, **kwargs)
    restantes = []
    for evento in eventos:
        if evento.type == pygame.KEYDOWN and evento.key == TECLA_PANTALLA_COMPLETA:
            alternar_pantalla_completa()
        else:
            restantes.append(evento)
    return restantes
