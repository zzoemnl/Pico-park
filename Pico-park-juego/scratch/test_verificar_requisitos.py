import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set headless / off-screen environment
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import configuracion
from configuracion import (
    mostrar_pestana_configuracion,
    obtener_volumen,
    fijar_volumen,
    cambiar_volumen,
    obtener_idioma,
    cambiar_idioma,
    _guardar_configuracion_disco,
    _cargar_configuracion_disco,
    RUTA_CONFIG_JSON
)

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()

print("--- TEST 1: Verificar persistencia de volumen e idioma ---")
fijar_volumen(80)
cambiar_idioma("en")
assert obtener_volumen() == 80, f"Expected 80, got {obtener_volumen()}"
assert obtener_idioma() == "en", f"Expected en, got {obtener_idioma()}"

_cargar_configuracion_disco()
assert obtener_volumen() == 80
assert obtener_idioma() == "en"
print("OK: Persistencia funciona correctamente.")

# Reset to defaults for test
fijar_volumen(70)
cambiar_idioma("es")

print("--- TEST 2: Simulación de interacción en ventana CONFIGURACIÓN ---")
# Post events to test volume buttons and closing via X
# Sequence:
# 1. Click rect_btn_menos (lower volume -> 60)
# 2. Click rect_btn_mas (raise volume -> 70)
# 3. Click rect_btn_mas again (raise volume -> 80)
# 4. Click rect_x_header (close modal)

# Let's compute modal rects as in configuracion.py
W_MODAL = 520
H_MODAL = 310
ancho_p, alto_p = 1280, 720
rect_modal = pygame.Rect((ancho_p - W_MODAL) // 2, (alto_p - H_MODAL) // 2, W_MODAL, H_MODAL)
W_X_CFG, H_X_CFG = 29, 34
rect_x_header = pygame.Rect(rect_modal.right - W_X_CFG - 14, rect_modal.top + (54 - H_X_CFG) // 2, W_X_CFG, H_X_CFG)

W_BTN_VOL, H_BTN_VOL = 42, 50
w_btn_lang, h_btn_lang, gap_lang = 136, 42, 14
total_w_content = 3 * w_btn_lang + 2 * gap_lang
x_margen_contenido = rect_modal.left + (W_MODAL - total_w_content) // 2
gap_vol = 14
w_barra = total_w_content - (2 * W_BTN_VOL + 2 * gap_vol)
h_barra = 28
cy_vol_fila = rect_modal.top + 122

rect_btn_menos = pygame.Rect(x_margen_contenido, 0, W_BTN_VOL, H_BTN_VOL)
rect_btn_menos.centery = cy_vol_fila
rect_barra_bg = pygame.Rect(rect_btn_menos.right + gap_vol, 0, w_barra, h_barra)
rect_barra_bg.centery = cy_vol_fila
rect_btn_mas = pygame.Rect(rect_barra_bg.right + gap_vol, 0, W_BTN_VOL, H_BTN_VOL)
rect_btn_mas.centery = cy_vol_fila

# Fill background with a test pattern representing main menu
pantalla.fill((255, 240, 200))
pygame.draw.circle(pantalla, (200, 100, 50), (400, 300), 100)

# Queue clicks:
# 1. Click menos
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': rect_btn_menos.center, 'button': 1}))
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': rect_btn_menos.center, 'button': 1}))
# 2. Click mas
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': rect_btn_mas.center, 'button': 1}))
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': rect_btn_mas.center, 'button': 1}))
# 3. Click mas
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': rect_btn_mas.center, 'button': 1}))
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': rect_btn_mas.center, 'button': 1}))
# 4. Click X
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': rect_x_header.center, 'button': 1}))
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': rect_x_header.center, 'button': 1}))

# Run modal
mostrar_pestana_configuracion(pantalla, reloj)

print(f"Volumen final: {obtener_volumen()}% (esperado: 80%)")
assert obtener_volumen() == 80, f"Error: Volumen esperado 80, obtenido {obtener_volumen()}"
print("OK: Modal funcionó, actualizó volumen y cerró con la X.")

print("--- TEST COMPLETADO CON ÉXITO ---")
