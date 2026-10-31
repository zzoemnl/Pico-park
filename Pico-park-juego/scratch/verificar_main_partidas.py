import os
import sys
import pygame

# Set dummy audio driver
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Initialize pygame
pygame.init()
pygame.font.init()

# Import main functions
import main
ANCHO_MENU = 1280
ALTO_MENU = 720

from main import (
    _obtener_fondo_partidas,
    obtener_geometria_panel_partidas,
    dibujar_tarjeta_partida,
    cargar_partidas,
)

pantalla = pygame.Surface((ANCHO_MENU, ALTO_MENU))

# 1. Test background generation
fondo = _obtener_fondo_partidas(ANCHO_MENU, ALTO_MENU)
assert fondo.get_size() == (ANCHO_MENU, ALTO_MENU)
print("Background generation: OK")

# 2. Test rendering actual saved games
partidas = cargar_partidas()
print(f"Loaded saves count: {len(partidas)}")

pantalla.blit(fondo, (0, 0))
rect_panel, btn_volver, btn_nueva, btn_iniciar = obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas))

# Render page folio
col_pagina = (252, 246, 235)
col_borde_pag = (190, 160, 125)
col_linea_int = (225, 200, 160)
pygame.draw.rect(pantalla, col_pagina, rect_panel, border_radius=16)
pygame.draw.rect(pantalla, col_borde_pag, rect_panel, width=3, border_radius=16)
pygame.draw.rect(pantalla, col_linea_int, rect_panel.inflate(-8, -8), width=1, border_radius=12)

# Faint lines
for y_linea in range(rect_panel.top + 28, rect_panel.bottom - 20, 22):
    pygame.draw.line(pantalla, (238, 230, 216), (rect_panel.left + 14, y_linea), (rect_panel.right - 14, y_linea), 1)

# Rivets
for rx, ry in [
    (rect_panel.left + 12, rect_panel.top + 12),
    (rect_panel.right - 12, rect_panel.top + 12),
    (rect_panel.left + 12, rect_panel.bottom - 12),
    (rect_panel.right - 12, rect_panel.bottom - 12),
]:
    pygame.draw.circle(pantalla, (205, 175, 105), (rx, ry), 3)
    pygame.draw.circle(pantalla, (100, 70, 40), (rx, ry), 3, width=1)

# Fonts
import fuentes
fuentes_tarjetas = {
    "titulo_card": fuentes.obtener_fuente("subtitulo", 18),
    "sub_card": fuentes.obtener_fuente("pequena", 14),
    "btn_card": fuentes.obtener_fuente("pixel", 13),
    "badge": fuentes.obtener_fuente("pixel", 14),
    "btn": fuentes.obtener_fuente("pixel", 14),
    "texto": fuentes.obtener_fuente("texto", 12),
    "sub_btn": fuentes.obtener_fuente("texto", 10),
}

# Draw cards
for idx, p in enumerate(partidas[:4]):
    r_card, r_bc, r_bg, r_bb = dibujar_tarjeta_partida(
        pantalla, p, idx, rect_panel, (0, 0), fuentes_tarjetas
    )
    print(f"Card {idx}: {p.get('nombre')} -> Rect: {r_card}")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captura_verificacion_main.png")
pygame.image.save(pantalla, out_path)
print(f"Saved verification screenshot to {out_path}")
