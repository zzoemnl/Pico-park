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

pulsaciones = []

orig_animar = sprites.animar_pulsacion_boton

def hook_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    idioma = configuracion.obtener_idioma()
    print(f"[PULSACION REGISTRADA] idioma={idioma} rect={rect}")
    pulsaciones.append({
        "idioma": idioma,
        "rect": rect,
        "semi": spr_semi.copy() if spr_semi else None,
        "apretado": spr_apretado.copy() if spr_apretado else None,
        "normal": spr_normal.copy() if spr_normal else None,
    })
    return True

sprites.animar_pulsacion_boton = hook_animar

import main

# Secuencia de navegacion completa:
# 1. En Menu Principal: Clic en btn_jugar (640, 250) -> va a Modo Juego
# 2. En Modo Juego: Clic en btn_continuar (490, 260) -> va a Partidas Guardadas
# 3. En Partidas Guardadas: Clic en btn_volver_partidas (390, 670) -> regresa a Modo Juego
# 4. En Modo Juego: Clic en btn_volver_modo (640, 520) -> regresa a Menu Principal
# 5. En Menu Principal: Clic en btn_personajes (640, 345) -> va a Personajes
# 6. En Personajes: Clic en btn_volver_personajes (220, 665) -> regresa a Menu Principal
# 7. En Menu Principal: Salir

for lang in ["zh", "en", "es"]:
    cambiar_idioma(lang)
    print(f"\n==================== INICIANDO PRUEBA NAVEGACION COMPLETA EN: {lang} ====================")
    pulsaciones.clear()

    local_step = [0]
    def make_hook(current_lang):
        def h_flip():
            local_step[0] += 1
            st = local_step[0]
            # 1. Clic btn_jugar (640, 250)
            if st == 2:
                print("Accion 1: Clic JUGAR")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 250), "button": 1}))
            # 2. Clic btn_continuar (490, 260)
            elif st == 5:
                print("Accion 2: Clic CONTINUAR")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (490, 260), "button": 1}))
            # 3. Clic btn_volver_partidas (390, 670)
            elif st == 8:
                print("Accion 3: Clic VOLVER (desde partidas)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (390, 670), "button": 1}))
            # 4. Clic btn_volver_modo (640, 520)
            elif st == 11:
                print("Accion 4: Clic VOLVER (desde modo)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 520), "button": 1}))
            # 5. Clic btn_personajes (640, 345)
            elif st == 14:
                print("Accion 5: Clic PERSONAJES")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 345), "button": 1}))
            # 6. Clic btn_volver_personajes (220, 665)
            elif st == 17:
                print("Accion 6: Clic VOLVER (desde personajes)")
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (220, 665), "button": 1}))
            # 7. Fin
            elif st >= 20:
                print("Fin de secuencia")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        return h_flip

    pygame.display.flip = make_hook(lang)

    try:
        main.main()
    except SystemExit:
        pass

    out_dir = f"scratch/test_nav_{lang}"
    os.makedirs(out_dir, exist_ok=True)
    print(f"Total pulsaciones capturadas en {lang}: {len(pulsaciones)}")
    for i, p in enumerate(pulsaciones):
        if p["semi"]:
            pygame.image.save(p["semi"], f"{out_dir}/p_{i+1}_semi.png")
        if p["apretado"]:
            pygame.image.save(p["apretado"], f"{out_dir}/p_{i+1}_apr.png")
        if p["normal"]:
            pygame.image.save(p["normal"], f"{out_dir}/p_{i+1}_norm.png")

print("\nTodas las pruebas de navegacion completadas con exito.")

