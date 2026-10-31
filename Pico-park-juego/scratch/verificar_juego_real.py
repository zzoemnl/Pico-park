import os
import sys

# Ensure Pico-park-juego is in path
DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

# Use dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import configuracion
import main

# Check that images in Sprites/Botones/HUD/ are properly oriented
for path in [
    "../Sprites/Botones/HUD/boton-bajar-volumen.png",
    "../Sprites/Botones/HUD/boton-subir-volumen.png"
]:
    abs_p = os.path.normpath(os.path.join(DIRECTORIO_JUEGO, path))
    surf = pygame.image.load(abs_p)
    w, h = surf.get_size()
    px_izq = sum(1 for y in range(h) for x in range(0, w // 2) if surf.get_at((x, y))[0] < 200 and surf.get_at((x, y))[1] < 120 and surf.get_at((x, y))[3] > 0)
    px_der = sum(1 for y in range(h) for x in range(w // 2, w) if surf.get_at((x, y))[0] < 200 and surf.get_at((x, y))[1] < 120 and surf.get_at((x, y))[3] > 0)
    print(f"Resource {os.path.basename(abs_p)}: px_izq={px_izq}, px_der={px_der} -> {'DERECHA (CORRECTO)' if px_izq > px_der else 'IZQUIERDA (ERROR)'}")
    assert px_izq > px_der, f"Error: {abs_p} no apunta a la derecha!"

# Now launch main game flow and simulate:
# 1. Main menu loads
# 2. Click on btn_config (OPCIONES)
# 3. In configuration modal, capture full screenshot
# 4. In configuration modal, capture crop of volume row
# 5. Press ESC to close modal
# 6. Exit game cleanly

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()

# Hook into mostrar_pestana_configuracion to capture actual gameplay screen
orig_mostrar = configuracion.mostrar_pestana_configuracion

captured_data = {}

def hook_mostrar_pestana(pantalla_arg, reloj_arg):
    # Post ESC so it will close on the next event check after rendering
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
    # Run the actual function
    res = orig_mostrar(pantalla_arg, reloj_arg)
    return res

configuracion.mostrar_pestana_configuracion = hook_mostrar_pestana
main.mostrar_pestana_configuracion = hook_mostrar_pestana

# Let's run a test where we render the modal directly using the game's actual function:
# We post an event to capture right inside the loop:
def custom_hook(pantalla_arg, reloj_arg):
    # We want to capture the screen after it renders the modal, so we monkey-patch pygame.display.flip
    orig_flip = pygame.display.flip
    flip_count = [0]
    def hook_flip():
        flip_count[0] += 1
        if flip_count[0] == 2:
            # Capture modal rendered over main menu
            ruta_cap = os.path.join(DIRECTORIO_JUEGO, "scratch", "captura_juego_real_configuracion.png")
            pygame.image.save(pantalla_arg, ruta_cap)
            print("Capturado juego real:", ruta_cap)

            # Also crop and save volume buttons area
            # Modal is centered at 1280, 720: (1280-520)//2 = 380, (720-310)//2 = 205
            rect_vol_area = pygame.Rect(380 + 30, 205 + 85, 460, 75)
            sub = pantalla_arg.subsurface(rect_vol_area)
            ruta_crop = os.path.join(DIRECTORIO_JUEGO, "scratch", "captura_juego_real_botones_volumen.png")
            pygame.image.save(pygame.transform.scale(sub, (sub.get_width() * 2, sub.get_height() * 2)), ruta_crop)
            print("Capturado crop volumen:", ruta_crop)

            # Now close modal
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
        orig_flip()

    pygame.display.flip = hook_flip
    try:
        return orig_mostrar(pantalla_arg, reloj_arg)
    finally:
        pygame.display.flip = orig_flip

# Render a frame of main menu first
from sprites import cargar_boton, cargar_boton_escalado
spr_jugar_normal = cargar_boton("jugar.png")
spr_personajes_normal = cargar_boton("personajes.png")
spr_opciones_normal = cargar_boton("opciones.png")
spr_salir_normal = cargar_boton("salir.png")
rect_btn_x = pygame.Rect(1280 - 40 - 24, 24, 40, 40)
spr_x_normal = cargar_boton_escalado("HUD/boton-x.png", 40, 40)

btn_jugar = pygame.Rect(504, 168, 272, 80)
btn_personajes = pygame.Rect(504, 266, 272, 80)
btn_config = pygame.Rect(504, 364, 272, 80)
btn_salir = pygame.Rect(504, 462, 272, 80)
from personajes_menu import GestorPersonajesMenu
gestor = GestorPersonajesMenu(1280, 720)
for _ in range(30):
    gestor.actualizar()

botones_menu_datos = [
    (btn_jugar, spr_jugar_normal, spr_jugar_normal),
    (btn_personajes, spr_personajes_normal, spr_personajes_normal),
    (btn_config, spr_opciones_normal, spr_opciones_normal),
    (btn_salir, spr_salir_normal, spr_salir_normal),
]
gestor.dibujar_menu_completo(pantalla, botones_menu_datos, (0, 0), spr_x_normal, rect_btn_x)

# Now call the configuration modal as main.py does when clicking OPCIONES
print("Abriendo CONFIGURACIÓN desde el menú principal...")
custom_hook(pantalla, reloj)
print("CONFIGURACIÓN se cerró y volvió al menú principal con éxito.")
