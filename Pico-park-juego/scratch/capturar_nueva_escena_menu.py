import os
import sys
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

from personajes_menu import (
    GestorPersonajesMenu,
    BTN_JUGAR_RECT,
    BTN_PERSONAJES_RECT,
    BTN_CONFIG_RECT,
    BTN_SALIR_RECT,
)

gestor = GestorPersonajesMenu(
    ancho=1280,
    alto=720,
    color_p1="Celeste",
    accesorio_p1="Gorro",
    color_p2="Violeta",
    accesorio_p2="Corona",
)

CARPETA_ARTIFACTS = r"C:\Users\Malena\.gemini\antigravity-ide\brain\075ec917-8912-4614-bbb5-e85478e4eea3"

# Crear botones dummy
def _crear_surf_boton(texto, bg_col):
    surf = pygame.Surface((272, 80))
    surf.fill(bg_col)
    fuente = pygame.font.SysFont("arial", 28, bold=True)
    t = fuente.render(texto, True, (255, 255, 255))
    r = t.get_rect(center=(136, 40))
    surf.blit(t, r)
    return surf

spr_jugar = _crear_surf_boton("JUGAR", (60, 160, 80))
spr_pers = _crear_surf_boton("PERSONAJES", (70, 120, 200))
spr_cfg = _crear_surf_boton("OPCIONES", (210, 150, 40))
spr_salir = _crear_surf_boton("SALIR", (200, 60, 60))

botones_datos = [
    (BTN_JUGAR_RECT, spr_jugar, spr_jugar),
    (BTN_PERSONAJES_RECT, spr_pers, spr_pers),
    (BTN_CONFIG_RECT, spr_cfg, spr_cfg),
    (BTN_SALIR_RECT, spr_salir, spr_salir),
]

fuente_titulo = pygame.font.SysFont("arial", 56, bold=True)

# Capturas en distintos momentos para observar el movimiento del fondo y el comportamiento de los personajes
capturas = [
    (1, "menu_navideno_t0.png"),
    (90, "menu_navideno_t1_nubes_humo.png"),
    (240, "menu_navideno_t2_desplazamiento.png"),
    (480, "menu_navideno_t3_bordes_estables.png"),
]

siguiente_cap_idx = 0
for f in range(500):
    gestor.actualizar()
    if siguiente_cap_idx < len(capturas) and f == capturas[siguiente_cap_idx][0]:
        nombre = capturas[siguiente_cap_idx][1]
        gestor.dibujar_menu_completo(
            pantalla,
            botones_menu_datos=botones_datos,
            pos_mouse=(0, 0),
            fuente_titulo=fuente_titulo,
        )
        ruta = os.path.join(CARPETA_ARTIFACTS, nombre)
        pygame.image.save(pantalla, ruta)
        print(f"Captura guardada: {ruta}")
        siguiente_cap_idx += 1

print("Capturas completadas con éxito.")
