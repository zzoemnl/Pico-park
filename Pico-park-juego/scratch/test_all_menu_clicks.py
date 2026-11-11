import os
import sys

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import configuracion
from configuracion import cambiar_idioma, t
import sprites

# Interceptar animar_pulsacion_boton para registrar todas las llamadas
pulsaciones = []

orig_animar = sprites.animar_pulsacion_boton

def hook_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    idioma = configuracion.obtener_idioma()
    print(f"[TEST ANIMACION] Idioma={idioma} rect={rect}")
    pulsaciones.append({
        "idioma": idioma,
        "rect": rect,
        "semi": spr_semi.copy() if spr_semi else None,
        "apretado": spr_apretado.copy() if spr_apretado else None,
        "normal": spr_normal.copy() if spr_normal else None,
    })
    return True  # Retorna True simulando clic completado sin demoras de animacion

sprites.animar_pulsacion_boton = hook_animar

import main

# Ejecutaremos la prueba en 3 pasadas: zh, en, es
for lang in ["zh", "en", "es"]:
    cambiar_idioma(lang)
    print(f"\n==================== PROBANDO IDIOMA: {lang} ====================")
    pulsaciones.clear()

    # Enviar clics secuenciales en el menu principal
    step = 0
    def make_hook(current_lang):
        local_step = [0]
        def h_flip():
            local_step[0] += 1
            st = local_step[0]
            # Clic 1: btn_jugar (center 640, 250)
            if st == 2:
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 250), "button": 1}))
            # Clic 2: btn_personajes (center 640, 345)
            elif st == 4:
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 345), "button": 1}))
            # Clic 3: btn_config (center 640, 440)
            elif st == 6:
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 440), "button": 1}))
            # Clic 4: btn_salir (center 640, 535)
            elif st == 8:
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 535), "button": 1}))
            elif st >= 10:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        return h_flip

    pygame.display.flip = make_hook(lang)

    try:
        main.main()
    except SystemExit:
        pass

    out_dir = f"scratch/test_clicks_{lang}"
    os.makedirs(out_dir, exist_ok=True)
    print(f"Total pulsaciones capturadas en {lang}: {len(pulsaciones)}")
    for i, p in enumerate(pulsaciones):
        if p["semi"]:
            pygame.image.save(p["semi"], f"{out_dir}/p_{i+1}_semi.png")
        if p["apretado"]:
            pygame.image.save(p["apretado"], f"{out_dir}/p_{i+1}_apr.png")
        if p["normal"]:
            pygame.image.save(p["normal"], f"{out_dir}/p_{i+1}_norm.png")

print("\nTodas las pasadas de idioma completadas exitosamente.")

