import os
import sys
import copy
import pygame

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

pygame.init()
pygame.font.init()

import main
import fuentes

ANCHO_MENU = 1280
ALTO_MENU = 720
pantalla = pygame.Surface((ANCHO_MENU, ALTO_MENU))

# Test with 5 mock saves (dynamic test for pagination)
partidas_mock = [
    {
        "id": 1,
        "nombre": "Expedición Alfa",
        "mundo_max": 1,
        "nivel_max": 3,
        "fecha": "15/10/2026 18:30",
        "niveles_desbloqueados": {1: [True, True, True, False, False]},
        "tiene_password": False,
    },
    {
        "id": 2,
        "nombre": "Ruta de los Picos Nevados",
        "mundo_max": 2,
        "nivel_max": 4,
        "fecha": "22/10/2026 21:15",
        "niveles_desbloqueados": {1: [True]*5, 2: [True, True, True, True, False]},
        "tiene_password": True,
    },
    {
        "id": 3,
        "nombre": "Aventura en Solitario",
        "mundo_max": 3,
        "nivel_max": 5,
        "fecha": "28/10/2026 14:00",
        "niveles_desbloqueados": {1: [True]*5, 2: [True]*5, 3: [True]*5},
        "tiene_password": False,
    },
    {
        "id": 4,
        "nombre": "Exploradores Perdidos",
        "mundo_max": 2,
        "nivel_max": 1,
        "fecha": "29/10/2026 19:45",
        "niveles_desbloqueados": {1: [True]*5, 2: [True, False, False, False, False]},
        "tiene_password": True,
    },
    {
        "id": 5,
        "nombre": "Travesía del Valle Secreto",
        "mundo_max": 1,
        "nivel_max": 5,
        "fecha": "30/10/2026 11:20",
        "niveles_desbloqueados": {1: [True]*5},
        "tiene_password": False,
    },
]

# Render complete screen using main logic
pos_mouse = (0, 0)
pantalla.blit(main._obtener_fondo_partidas(ANCHO_MENU, ALTO_MENU), (0, 0))

rect_panel, btn_volver, btn_nueva, btn_iniciar = main.obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas_mock))

fuente_pixel_titulo = fuentes.obtener_fuente("pixel_titulo", 32)
fuente_subtitulo = fuentes.obtener_fuente("subtitulo", 17)
fuente_contador = fuentes.obtener_fuente("contador", 15)
fuente_pixel_btn = fuentes.obtener_fuente("pixel", 18)
fuente_texto = fuentes.obtener_fuente("texto", 14)

# Title
t_somb = fuente_pixel_titulo.render("PARTIDAS GUARDADAS", True, (195, 170, 140))
t_tit = fuente_pixel_titulo.render("PARTIDAS GUARDADAS", True, (58, 38, 24))
rect_tit = t_tit.get_rect(center=(ANCHO_MENU // 2, 46))
pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
pantalla.blit(t_tit, rect_tit)

subt = fuente_subtitulo.render("Registro de expediciones y progreso de aventura", True, (125, 95, 65))
pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 78)))

# Folio panel
col_pagina = (252, 246, 235)
col_borde_pag = (190, 160, 125)
col_linea_int = (225, 200, 160)
pygame.draw.rect(pantalla, col_pagina, rect_panel, border_radius=16)
pygame.draw.rect(pantalla, col_borde_pag, rect_panel, width=3, border_radius=16)
pygame.draw.rect(pantalla, col_linea_int, rect_panel.inflate(-8, -8), width=1, border_radius=12)

for y_linea in range(rect_panel.top + 28, rect_panel.bottom - 20, 22):
    pygame.draw.line(pantalla, (238, 230, 216), (rect_panel.left + 14, y_linea), (rect_panel.right - 14, y_linea), 1)

for rx, ry in [
    (rect_panel.left + 12, rect_panel.top + 12),
    (rect_panel.right - 12, rect_panel.top + 12),
    (rect_panel.left + 12, rect_panel.bottom - 12),
    (rect_panel.right - 12, rect_panel.bottom - 12),
]:
    pygame.draw.circle(pantalla, (205, 175, 105), (rx, ry), 3)
    pygame.draw.circle(pantalla, (100, 70, 40), (rx, ry), 3, width=1)

# Render 4 cards for page 0
fuentes_tarjetas = {
    "titulo_card": fuentes.obtener_fuente("subtitulo", 18),
    "sub_card": fuentes.obtener_fuente("pequena", 14),
    "btn_card": fuentes.obtener_fuente("pixel", 13),
    "badge": fuentes.obtener_fuente("pixel", 14),
    "btn": fuentes.obtener_fuente("pixel", 14),
    "texto": fuentes.obtener_fuente("texto", 12),
    "sub_btn": fuentes.obtener_fuente("texto", 10),
}

pagina_partidas = 0
MAX_PARTIDAS = 4
partidas_pagina = partidas_mock[:MAX_PARTIDAS]
total_paginas = 2

for idx_slot, p in enumerate(partidas_pagina):
    main.dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel, pos_mouse, fuentes_tarjetas)

# Pagination
btn_pag_ant = pygame.Rect(rect_panel.centerx - 120, 508, 36, 30)
btn_pag_sig = pygame.Rect(rect_panel.centerx + 84, 508, 36, 30)

pygame.draw.rect(pantalla, (240, 230, 215), btn_pag_ant, border_radius=6)
pygame.draw.rect(pantalla, (195, 168, 138), btn_pag_ant, width=1, border_radius=6)
col_flecha_ant = (175, 155, 135)
cx_a, cy_a = btn_pag_ant.center
for dy in range(-4, 5):
    ancho_f = 4 - abs(dy)
    for dx in range(ancho_f + 1):
        pantalla.set_at((cx_a + 2 - dx, cy_a + dy), col_flecha_ant)

t_pag = fuente_contador.render(f"Entrada página {pagina_partidas + 1} de {total_paginas}", True, (75, 55, 38))
pantalla.blit(t_pag, t_pag.get_rect(center=(rect_panel.centerx, 523)))

pygame.draw.rect(pantalla, (253, 246, 233), btn_pag_sig, border_radius=6)
pygame.draw.rect(pantalla, (195, 168, 138), btn_pag_sig, width=1, border_radius=6)
col_flecha_sig = (65, 45, 30)
cx_s, cy_s = btn_pag_sig.center
for dy in range(-4, 5):
    ancho_f = 4 - abs(dy)
    for dx in range(ancho_f + 1):
        pantalla.set_at((cx_s - 2 + dx, cy_s + dy), col_flecha_sig)

# Bottom buttons
spr_volver = main._crear_boton_pixel_art(btn_volver.width, btn_volver.height, "VOLVER", icono="volver", estilo="crema", estado="normal", fuente_tit=fuente_pixel_btn)
pantalla.blit(spr_volver, btn_volver)

spr_nueva = main._crear_boton_pixel_art(btn_nueva.width, btn_nueva.height, "NUEVA PARTIDA", icono="estrella", estilo="ambar", estado="normal", fuente_tit=fuente_pixel_btn)
pantalla.blit(spr_nueva, btn_nueva)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captura_diario_completo_4partidas.png")
pygame.image.save(pantalla, out_path)
print(f"Full 4-save screen with pagination saved to {out_path}")
