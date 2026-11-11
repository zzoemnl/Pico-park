"""
Genera capturas visuales de alta fidelidad del Menú Principal 100% Pixel Art con Plataformas.
"""
import os
import sys
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

import sprites
import fuentes
from personajes_menu import (
    GestorPersonajesMenu,
    BTN_JUGAR_RECT,
    BTN_PERSONAJES_RECT,
    BTN_CONFIG_RECT,
    BTN_SALIR_RECT,
)

CARPETA_ARTIFACTS = r"C:\Users\Malena\.gemini\antigravity-ide\brain\e4ef99ac-8461-4560-8170-5a437f43e801"

gestor = GestorPersonajesMenu(
    ancho=1280, alto=720,
    color_p1="Celeste", accesorio_p1="Corona",
    color_p2="Violeta", accesorio_p2="Sombrero"
)

# Cargar sprites de botones
spr_jugar = sprites.cargar_boton_escalado("jugar.png", 272, 80)
spr_jugar_h = sprites.cargar_boton_escalado("jugar-preapretado.png", 272, 80)
spr_pers = sprites.cargar_boton_escalado("personajes.png", 272, 80)
spr_pers_h = sprites.cargar_boton_escalado("personajes-preapretado.png", 272, 80)
spr_cfg = sprites.cargar_boton_escalado("opciones.png", 272, 80)
spr_cfg_h = sprites.cargar_boton_escalado("opciones-preapretado.png", 272, 80)
spr_salir = sprites.cargar_boton_escalado("salir.png", 272, 80)
spr_salir_h = sprites.cargar_boton_escalado("salir-preapretado.png", 272, 80)

botones_datos = [
    (BTN_JUGAR_RECT, spr_jugar, spr_jugar_h),
    (BTN_PERSONAJES_RECT, spr_pers, spr_pers_h),
    (BTN_CONFIG_RECT, spr_cfg, spr_cfg_h),
    (BTN_SALIR_RECT, spr_salir, spr_salir_h),
]

fuente_tit = fuentes.obtener_fuente(80, negrita=True)

# Simular 20 frames iniciales
for _ in range(20):
    gestor.actualizar()

# Captura 1: Vista general del Menú Navideño Pixel Art con plataformas y distribución inicial
pantalla.fill((0, 0, 0))
gestor.dibujar_menu_completo(pantalla, botones_datos, pos_mouse=(640, 250), fuente_titulo=fuente_tit)
ruta_cap1 = os.path.join(CARPETA_ARTIFACTS, "menu_navideno_pixel_art_general.png")
pygame.image.save(pantalla, ruta_cap1)
print(f"Captura general guardada en: {ruta_cap1}")

# Simular 140 frames más (acción continua con personajes explorando plataformas y suelo)
for _ in range(140):
    gestor.actualizar()

# Captura 2: Momento dinámico con personajes en suelo, plataformas y ambiente festivo
pantalla.fill((0, 0, 0))
gestor.dibujar_menu_completo(pantalla, botones_datos, pos_mouse=(0, 0), fuente_titulo=fuente_tit)
ruta_cap2 = os.path.join(CARPETA_ARTIFACTS, "menu_navideno_pixel_art_accion.png")
pygame.image.save(pantalla, ruta_cap2)
print(f"Captura acción guardada en: {ruta_cap2}")

# Simular 200 frames más para capturar otra configuración aleatoria
for _ in range(200):
    gestor.actualizar()

pantalla.fill((0, 0, 0))
gestor.dibujar_menu_completo(pantalla, botones_datos, pos_mouse=(0, 0), fuente_titulo=fuente_tit)
ruta_cap3 = os.path.join(CARPETA_ARTIFACTS, "menu_navideno_pixel_art_variado.png")
pygame.image.save(pantalla, ruta_cap3)
print(f"Captura variada guardada en: {ruta_cap3}")
