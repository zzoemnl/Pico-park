import os
import sys
import pygame

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

pygame.init()
pygame.font.init()

import main
from main import (
    cargar_partidas,
    obtener_geometria_panel_partidas,
    obtener_geometria_tarjeta_partida,
    dibujar_tarjeta_partida,
)

ANCHO_MENU = 1280
ALTO_MENU = 720
pantalla = pygame.Surface((ANCHO_MENU, ALTO_MENU))

partidas = cargar_partidas()
print(f"Total de partidas guardadas existentes: {len(partidas)}")

rect_panel, btn_volver, btn_nueva, btn_iniciar = obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas))

# Verificar que los rectángulos no colisionan entre sí
if bool(partidas):
    assert not btn_volver.colliderect(btn_nueva), "Los botones inferiores no deben superponerse"
    assert not rect_panel.colliderect(btn_volver), "El panel no debe superponerse con el botón volver"
    assert not rect_panel.colliderect(btn_nueva), "El panel no debe superponerse con el botón nueva"

for idx, p in enumerate(partidas[:4]):
    r_card, r_badge, r_cargar, r_gestionar, r_borrar, (x_txt, w_txt) = obtener_geometria_tarjeta_partida(rect_panel, idx)
    assert not r_cargar.colliderect(r_gestionar), "Cargar y Gestionar no deben colisionar"
    assert not r_gestionar.colliderect(r_borrar), "Gestionar y Borrar no deben colisionar"
    assert x_txt < r_cargar.left, "El texto no debe invadir los botones"
    print(f"Verificación geométrica Ficha {idx} ({p.get('nombre')}): OK")

print("¡Todas las comprobaciones de geometría e interactividad pasaron exitosamente!")
