import os
import sys

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import configuracion
from configuracion import cambiar_idioma, obtener_idioma, t
import sprites

pulsaciones_por_idioma = {}

orig_animar = sprites.animar_pulsacion_boton

def hook_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    idioma = configuracion.obtener_idioma()
    print(f"  [INTERCEPTADO] idioma={idioma} rect={rect}")
    pulsaciones_por_idioma.setdefault(idioma, []).append({
        "rect": rect,
        "semi": spr_semi.copy() if spr_semi else None,
        "apretado": spr_apretado.copy() if spr_apretado else None,
        "normal": spr_normal.copy() if spr_normal else None,
    })
    return True

sprites.animar_pulsacion_boton = hook_animar

import main

for lang in ["zh", "en", "es"]:
    cambiar_idioma(lang)
    print(f"\n=== TEST FULL ROUNDTRIP IN: {lang} ===")
    
    local_step = [0]
    def make_hook(current_lang):
        def h_flip():
            local_step[0] += 1
            st = local_step[0]
            # Paso 1: Clic JUGAR en Menu Principal
            if st == 2:
                print("1. Click JUGAR (640, 254)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 254), "button": 1}))
            # Paso 2: Clic CONTINUAR en Modo Juego
            elif st == 5:
                print("2. Click CONTINUAR (639, 325)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (639, 325), "button": 1}))
            # Paso 3: Clic VOLVER en Partidas Guardadas
            elif st == 8:
                print("3. Click VOLVER en Partidas (509, 655)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (509, 655), "button": 1}))
            # Paso 4: Clic VOLVER en Modo Juego
            elif st == 11:
                print("4. Click VOLVER en Modo Juego (640, 670)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 670), "button": 1}))
            # Paso 5: Clic PERSONAJES en Menu Principal
            elif st == 14:
                print("5. Click PERSONAJES (640, 345)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 345), "button": 1}))
            # Paso 6: Clic VOLVER en Personajes
            elif st == 17:
                print("6. Click VOLVER en Personajes (640, 670)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 670), "button": 1}))
            # Paso 7: Clic SALIR en Menu Principal
            elif st == 20:
                print("7. Click SALIR (640, 535)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 535), "button": 1}))
            elif st >= 24:
                print("8. Forzar salida si aun corre")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        return h_flip

    pygame.display.flip = make_hook(lang)

    try:
        main.main()
    except SystemExit:
        pass

    clicks = pulsaciones_por_idioma.get(lang, [])
    print(f"Total clicks interceptados para {lang}: {len(clicks)}")
    assert len(clicks) >= 7, f"Se esperaban al menos 7 clicks para {lang}, se obtuvieron {len(clicks)}"
    out_dir = f"scratch/roundtrip_{lang}"
    os.makedirs(out_dir, exist_ok=True)
    for idx, c in enumerate(clicks):
        if c["semi"]: pygame.image.save(c["semi"], f"{out_dir}/click_{idx+1}_semi.png")
        if c["apretado"]: pygame.image.save(c["apretado"], f"{out_dir}/click_{idx+1}_apr.png")
        if c["normal"]: pygame.image.save(c["normal"], f"{out_dir}/click_{idx+1}_norm.png")

print("\nALL ROUNDTRIP TESTS COMPLETED SUCCESSFULLY!")

