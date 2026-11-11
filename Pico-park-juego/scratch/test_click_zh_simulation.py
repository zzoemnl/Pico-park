import os
import sys

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DIRECTORIO_JUEGO)
os.chdir(DIRECTORIO_JUEGO)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import configuracion
import sprites

captures = []

# Guardar la funcion original de animar_pulsacion_boton
orig_animar = sprites.animar_pulsacion_boton

def hooked_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    print(f"[HOOK] animar_pulsacion_boton called for rect={rect}:")
    print(f"       spr_semi: {spr_semi}")
    print(f"       spr_apretado: {spr_apretado}")
    print(f"       spr_normal: {spr_normal}")
    captures.append({
        "rect": rect,
        "semi": spr_semi.copy() if spr_semi else None,
        "apretado": spr_apretado.copy() if spr_apretado else None,
        "normal": spr_normal.copy() if spr_normal else None,
    })
    # Ejecutar animacion original para asegurar consistencia
    return orig_animar(pantalla, rect, spr_semi, spr_apretado, fondo_limpio, spr_normal)

sprites.animar_pulsacion_boton = hooked_animar

import main

# Configurar idioma a Chino Simplificado antes de interactuar
configuracion.cambiar_idioma("zh")
print(f"Idioma actual configurado: {configuracion.obtener_idioma()}")

step = 0
orig_flip = pygame.display.flip

def hooked_flip():
    global step
    step += 1
    pantalla = pygame.display.get_surface()

    # Step 2: Despues de inicializar el menu principal en chino, capturar y simular clic en btn_jugar
    if step == 2:
        os.makedirs("scratch/capturas_click_zh", exist_ok=True)
        pygame.image.save(pantalla, "scratch/capturas_click_zh/1_menu_zh_inicial.png")
        print("Guardado: 1_menu_zh_inicial.png")
        # Inyectar MOUSEBUTTONDOWN sobre btn_jugar (center: ANCHO_MENU // 2, 280)
        # En main.py:
        # btn_jugar = pygame.Rect((ANCHO_MENU - ANCHO_BOTON) // 2, y_inicio, ANCHO_BOTON, ALTO_BOTON) -> y_inicio=280
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 310), "button": 1})
        pygame.event.post(ev_down)
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (640, 310), "button": 1})
        pygame.event.post(ev_up)

    # Step 5: Ya debemos haber pasado a ESTADO_MODO_JUEGO
    elif step == 6:
        pygame.image.save(pantalla, "scratch/capturas_click_zh/2_modo_juego_zh.png")
        print("Guardado: 2_modo_juego_zh.png")
        # Clic en CONTINUAR (btn_continuar center: 640 - 150 = 490, 260)
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (490, 260), "button": 1})
        pygame.event.post(ev_down)
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (490, 260), "button": 1})
        pygame.event.post(ev_up)

    # Step 9: Ya debemos estar en ESTADO_LISTA_PARTIDAS
    elif step == 10:
        pygame.image.save(pantalla, "scratch/capturas_click_zh/3_lista_partidas_zh.png")
        print("Guardado: 3_lista_partidas_zh.png")
        # Clic en VOLVER (btn_volver_partidas: ANCHO_MENU // 2 - 250, ALTO_MENU - 80) -> (390, 670)
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (390, 670), "button": 1})
        pygame.event.post(ev_down)
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (390, 670), "button": 1})
        pygame.event.post(ev_up)

    # Step 14: De regreso a ESTADO_MODO_JUEGO, clic en VOLVER AL MENU (btn_volver_modo: center (640, 520))
    elif step == 14:
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (640, 520), "button": 1})
        pygame.event.post(ev_down)
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (640, 520), "button": 1})
        pygame.event.post(ev_up)

    # Step 18: De regreso en ESTADO_MENU_PRINCIPAL, cerrar limpiamente
    elif step == 18:
        pygame.image.save(pantalla, "scratch/capturas_click_zh/4_menu_zh_final.png")
        print("Guardado: 4_menu_zh_final.png")
        ev_quit = pygame.event.Event(pygame.QUIT)
        pygame.event.post(ev_quit)

    orig_flip()

pygame.display.flip = hooked_flip

try:
    main.main()
except SystemExit:
    pass

print("\n=== RESUMEN DE ANIMACIONES CAPTURADAS ===")
print(f"Total clics capturados: {len(captures)}")
for idx, c in enumerate(captures):
    print(f"Clic #{idx+1} en rect={c['rect']}:")
    if c['semi']:
        fn_s = f"scratch/capturas_click_zh/click_{idx+1}_semi.png"
        pygame.image.save(c['semi'], fn_s)
        print(f"  semi guardado en {fn_s}")
    if c['apretado']:
        fn_a = f"scratch/capturas_click_zh/click_{idx+1}_apr.png"
        pygame.image.save(c['apretado'], fn_a)
        print(f"  apretado guardado en {fn_a}")
    if c['normal']:
        fn_n = f"scratch/capturas_click_zh/click_{idx+1}_norm.png"
        pygame.image.save(c['normal'], fn_n)
        print(f"  normal guardado en {fn_n}")

print("Test de simulacion completado con exito.")

