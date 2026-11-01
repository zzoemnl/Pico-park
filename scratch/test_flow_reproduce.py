import sys, os
sys.path.insert(0, os.path.abspath('Pico-park-juego'))
os.chdir('Pico-park-juego')
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()

import configuracion
import main

def test_language(lang):
    configuracion.cambiar_idioma(lang)
    print(f"=== TESTING LANGUAGE: {lang} ===")

    frame = [0]

    orig_flip = pygame.display.flip
    orig_get = pygame.event.get

    def fake_get(event_type=None):
        if event_type is not None:
            return orig_get(event_type)
        evs = []
        f = frame[0]
        if f == 5:
            # Click JUGAR (center approx: 640, 240)
            print(f"Frame {f}: Injected click JUGAR")
            evs.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (640, 240), 'button': 1}))
        elif f == 15:
            # In Modo Juego: click CONTINUAR (640, 275)
            print(f"Frame {f}: Injected click CONTINUAR")
            evs.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (640, 275), 'button': 1}))
        elif f == 25:
            print(f"Frame {f}: Injected click VOLVER PARTIDAS")
            evs.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (509, 654), 'button': 1}))
        elif f == 35:
            print(f"Frame {f}: Reached end, quitting")
            evs.append(pygame.event.Event(pygame.QUIT))
        return evs

    def fake_flip():
        frame[0] += 1
        f = frame[0]
        surf = pygame.display.get_surface()
        if f == 14:
            path = f"scratch/flow_{lang}_1_modo.png"
            pygame.image.save(surf, path)
            print(f"Saved {path}")
        elif f == 24:
            path = f"scratch/flow_{lang}_2_partidas.png"
            pygame.image.save(surf, path)
            print(f"Saved {path}")
        elif f == 34:
            path = f"scratch/flow_{lang}_3_modo_returned.png"
            pygame.image.save(surf, path)
            print(f"Saved {path}")
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

test_language("es")
test_language("zh")
print("All flow tests completed!")
