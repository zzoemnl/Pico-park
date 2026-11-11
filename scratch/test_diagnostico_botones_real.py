import os
import sys

DIRECTORIO_JUEGO = os.path.abspath("Pico-park-juego")
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

import configuracion
import sprites

orig_animar = sprites.animar_pulsacion_boton

def debug_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    idioma = configuracion.obtener_idioma()
    print(f"\n[ANIMAR] lang={idioma} rect={rect}")
    print(f"         semi: {spr_semi.get_size() if spr_semi else None}")
    print(f"         apretado: {spr_apretado.get_size() if spr_apretado else None}")
    print(f"         normal: {spr_normal.get_size() if spr_normal else None}")
    if isinstance(fondo_limpio, pygame.Surface):
        print(f"         fondo_limpio: Surface {fondo_limpio.get_size()}")
    else:
        print(f"         fondo_limpio: {fondo_limpio}")
    return orig_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio, spr_normal)

sprites.animar_pulsacion_boton = debug_animar

import main

def run_test_interactive(lang):
    configuracion.cambiar_idioma(lang)
    print(f"\n==========================================")
    print(f"   STARTING FLOW TEST FOR: {lang}")
    print(f"==========================================")

    frame = [0]
    orig_flip = pygame.display.flip
    orig_get = pygame.event.get

    actions = [
        # (frame, (x, y), label)
        (5, (640, 239), "CLICK JUGAR"),
        (15, (639, 325), "CLICK CONTINUAR"),
        (25, (509, 655), "CLICK VOLVER PARTIDAS"),
        (35, (640, 670), "CLICK VOLVER MODO"),
        (45, (640, 343), "CLICK PERSONAJES"),
        (55, (640, 670), "CLICK VOLVER PERSONAJES"),
        (65, None, "QUIT")
    ]
    action_idx = [0]

    def fake_get(event_type=None):
        if event_type is not None:
            return orig_get(event_type)
        f = frame[0]
        evs = []
        if action_idx[0] < len(actions):
            act_f, act_pos, act_lbl = actions[action_idx[0]]
            if f == act_f:
                action_idx[0] += 1
                if act_pos is None:
                    print(f"Frame {f}: Action -> {act_lbl}")
                    evs.append(pygame.event.Event(pygame.QUIT))
                else:
                    print(f"Frame {f}: Action -> {act_lbl} at {act_pos}")
                    evs.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': act_pos, 'button': 1}))
        return evs

    def fake_flip():
        frame[0] += 1
        f = frame[0]
        surf = pygame.display.get_surface()
        os.makedirs(f"scratch/trace_{lang}", exist_ok=True)
        if f in (4, 6, 14, 16, 24, 26, 34, 36, 44, 46, 54, 56, 64):
            pygame.image.save(surf, f"scratch/trace_{lang}/f_{f:03d}.png")
        orig_flip()

    pygame.display.flip = fake_flip
    pygame.event.get = fake_get
    pygame.mouse.get_pressed = lambda: (False, False, False)

    try:
        main.main()
    except SystemExit:
        pass
    finally:
        pygame.display.flip = orig_flip
        pygame.event.get = orig_get

for lang in ["es", "zh", "en"]:
    run_test_interactive(lang)

print("\nAll interactive tests done!")
