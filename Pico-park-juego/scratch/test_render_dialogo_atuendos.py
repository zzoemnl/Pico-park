import os
import sys
import threading
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from guardado import mostrar_dialogo_confirmar_atuendos

pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()

partida_mock = {
    "id": 1,
    "nombre": "Mi Aventura",
    "mundo_max": 2,
    "nivel_max": 4,
    "color_p1": "Celeste",
    "color_p2": "Violeta",
    "accesorio_p1": "Gorro",
    "accesorio_p2": "Ninguno",
}

def postear_despues(evento, delay=0.08):
    def _run():
        time.sleep(delay)
        pygame.event.post(evento)
    t = threading.Thread(target=_run)
    t.daemon = True
    t.start()

# 1. Probar clic en "mantener"
ev_mantener = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (477, 540)})
postear_despues(ev_mantener)
res_m = mostrar_dialogo_confirmar_atuendos(
    pantalla, reloj, partida_mock,
    color_p1_nuevo="Rojo", color_p2_nuevo="Amarillo",
    acc_p1_nuevo="Corona", acc_p2_nuevo="Sombrero",
)
assert res_m == "mantener", f"Se esperaba 'mantener' pero se obtuvo {res_m}"
print("[OK] mostrar_dialogo_confirmar_atuendos clic MANTENER ->", res_m)

# 2. Probar clic en "cambiar"
ev_cambiar = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (802, 540)})
postear_despues(ev_cambiar)
res_c = mostrar_dialogo_confirmar_atuendos(
    pantalla, reloj, partida_mock,
    color_p1_nuevo="Rojo", color_p2_nuevo="Amarillo",
    acc_p1_nuevo="Corona", acc_p2_nuevo="Sombrero",
)
assert res_c == "cambiar", f"Se esperaba 'cambiar' pero se obtuvo {res_c}"
print("[OK] mostrar_dialogo_confirmar_atuendos clic CAMBIAR ->", res_c)

# 3. Probar tecla ESC
ev_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
postear_despues(ev_esc)
res_esc = mostrar_dialogo_confirmar_atuendos(
    pantalla, reloj, partida_mock,
    color_p1_nuevo="Rojo", color_p2_nuevo="Amarillo",
    acc_p1_nuevo="Corona", acc_p2_nuevo="Sombrero",
)
assert res_esc == "cancelar", f"Se esperaba 'cancelar' pero se obtuvo {res_esc}"
print("[OK] mostrar_dialogo_confirmar_atuendos tecla ESC ->", res_esc)

# 4. Generar screenshot del diálogo renderizado para inspección visual
ev_esc2 = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
# Delay un poco mayor para que pinte la pantalla antes de salir
postear_despues(ev_esc2, delay=0.15)
mostrar_dialogo_confirmar_atuendos(
    pantalla, reloj, partida_mock,
    color_p1_nuevo="Rojo", color_p2_nuevo="Amarillo",
    acc_p1_nuevo="Corona", acc_p2_nuevo="Sombrero",
)
out_png = os.path.join(os.path.dirname(__file__), "dialogo_confirmar_atuendos.png")
pygame.image.save(pantalla, out_png)
print(f"[OK] Screenshot del dialogo guardado en: {out_png}")
