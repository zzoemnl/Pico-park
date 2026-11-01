import os
import sys
import pygame

DIRECTORIO_JUEGO = os.path.abspath("Pico-park-juego")
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import configuracion
import sprites

captured_states = []

orig_animar = sprites.animar_pulsacion_boton

def hook_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    lang = configuracion.obtener_idioma()
    print(f"[TEST ANIMAR] lang={lang} rect={rect}")
    assert spr_semi is not None, f"spr_semi is None for {rect} in {lang}"
    assert spr_apretado is not None, f"spr_apretado is None for {rect} in {lang}"
    assert spr_normal is not None, f"spr_normal is None for {rect} in {lang}"
    
    # Assert exact sizes match rect
    assert spr_semi.get_size() == (rect.width, rect.height), f"spr_semi size mismatch: {spr_semi.get_size()} != {rect.size}"
    assert spr_apretado.get_size() == (rect.width, rect.height), f"spr_apretado size mismatch: {spr_apretado.get_size()} != {rect.size}"
    assert spr_normal.get_size() == (rect.width, rect.height), f"spr_normal size mismatch: {spr_normal.get_size()} != {rect.size}"
    
    captured_states.append({
        "lang": lang,
        "rect": rect,
        "semi": spr_semi.copy(),
        "apretado": spr_apretado.copy(),
        "normal": spr_normal.copy()
    })
    return orig_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio, spr_normal)

sprites.animar_pulsacion_boton = hook_animar

import main

def test_language_flow(lang):
    configuracion.cambiar_idioma(lang)
    print(f"\n=======================================================")
    print(f"   STARTING FULL INTERACTIVE VERIFICATION: {lang}")
    print(f"=======================================================")

    frame = [0]
    hold_frames = [0]
    mouse_pos = [(0, 0)]
    orig_flip = pygame.display.flip
    orig_get = pygame.event.get

    actions = [
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
                    mouse_pos[0] = act_pos
                    hold_frames[0] = 2  # Hold pressed for 2 frames
                    evs.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': act_pos, 'button': 1}))
        return evs

    def fake_mouse_pressed():
        if hold_frames[0] > 0:
            hold_frames[0] -= 1
            return (True, False, False)
        return (False, False, False)

    def fake_flip():
        frame[0] += 1
        f = frame[0]
        surf = pygame.display.get_surface()
        os.makedirs(f"scratch/roundtrip_{lang}", exist_ok=True)
        if f in (4, 6, 14, 16, 24, 26, 34, 36, 44, 46, 54, 56, 64):
            pygame.image.save(surf, f"scratch/roundtrip_{lang}/f_{f:03d}.png")
        orig_flip()

    pygame.display.flip = fake_flip
    pygame.event.get = fake_get
    pygame.mouse.get_pressed = fake_mouse_pressed
    pygame.mouse.get_pos = lambda: mouse_pos[0]

    try:
        main.main()
    except SystemExit:
        pass
    finally:
        pygame.display.flip = orig_flip
        pygame.event.get = orig_get

for test_lang in ["es", "zh", "en"]:
    test_language_flow(test_lang)

print(f"\nTotal button click animations verified: {len(captured_states)}")
assert len(captured_states) == 18, f"Expected 18 animations (6 clicks * 3 langs), got {len(captured_states)}"

print("\nALL INTERACTIVE VERIFICATIONS PASSED WITH 100% SUCCESS!")
