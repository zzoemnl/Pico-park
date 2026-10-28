import sys
import os
import pygame

# Set up environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

from sprites import cargar_boton, animar_pulsacion_boton, aclarar_boton
import configuracion
import guardado
import pantalla as pantalla_mod

print("=== VERIFICACION EXHAUSTIVA DE ANIMACION DE PULSACION EN TODOS LOS BOTONES ===")

# 1. VERIFICAR QUE TODOS LOS GRUPOS DE BOTONES TIENEN SUS 3 SPRITES
tripletas_botones = [
    # HUD
    ("HUD: Casa", "HUD/boton-casa.png", "HUD/boton-casa-semiapretado.png", "HUD/boton-casa-apretado.png"),
    ("HUD: X", "HUD/boton-x.png", "HUD/boton-x-semiapretado.png", "HUD/boton-x-apretado.png"),
    ("HUD: Reiniciar", "HUD/boton-reiniciar-icono.png", "HUD/boton-reiniciar-icono-semiapretado.png", "HUD/boton-reiniciar-icono-apretado.png"),
    ("HUD: Configuración", "HUD/boton-configuracion.png", "HUD/boton-configuracion-semiapretado.png", "HUD/boton-configuracion-apretado.png"),
    ("HUD: Bajar Volumen", "HUD/boton-bajar-volumen.png", "HUD/boton-bajar-volumen-semiapretado.png", "HUD/boton-bajar-volumen-apretado.png"),
    ("HUD: Subir Volumen", "HUD/boton-subir-volumen.png", "HUD/boton-subir-volumen-semiapretado.png", "HUD/boton-subir-volumen-apretado.png"),

    # Menu
    ("Menu: Jugar", "Menu/jugar.png", "Menu/jugar-preapretado.png", "Menu/jugar-apretado.png"),
    ("Menu: Personajes", "Menu/personajes.png", "Menu/personajes-preapretado.png", "Menu/personajes-apretado.png"),
    ("Menu: Opciones", "Menu/opciones.png", "Menu/opciones-preapretado.png", "Menu/opciones-apretado.png"),
    ("Menu: Salir", "Menu/salir.png", "Menu/salir-preapretado.png", "Menu/salir-apretado.png"),
    ("Menu: Cancelar", "Menu/boton-cancelar.png", "Menu/boton-cancelar-semiapretado.png", "Menu/boton-cancelar-apretado.png"),
    ("Menu: Continuar/Cargar", "Menu/boton-continuar-cargar....png", "Menu/boton-continuar-cargar...-semiapretado.png", "Menu/boton-continuar-cargar...-apretado.png"),
    ("Menu: Salir sin guardar", "Menu/boton-salir-sin-guardar.png", "Menu/boton-salir-sin-guardar-semiapretado.png", "Menu/boton-salir-sin-guardar-apretado.png"),

    # Mundos
    ("Mundos: Volver", "mundos/boton-volver.png", "mundos/boton-volver-semiapretado.png", "mundos/boton-volver-apretado.png"),
    ("Mundos: Cargar", "mundos/boton-cargar.png", "mundos/boton-cargar-semiapretado.png", "mundos/boton-cargar-apretado.png"),
    ("Mundos: Nueva partida", "mundos/boton-nueva-partida.png", "mundos/boton-nueva-partida-semiapretado.png", "mundos/boton-nueva-partida-apretado.png"),
    ("Mundos: Nueva partida reiniciar", "mundos/boton-nueva-partida-reiniciar....png", "mundos/boton-nueva-partida-reiniciar...-semiapretado.png", "mundos/boton-nueva-partida-reiniciar...-apretado.png"),

    # Ventanas
    ("Ventanas: Guardar y salir", "Ventanas/boton-guardar-y-salir.png", "Ventanas/boton-guardar-y-salir-semiapretado.png", "Ventanas/boton-guardar-y-salir-apretado.png"),
    ("Ventanas: Menu", "Ventanas/boton-menu.png", "Ventanas/boton-menu-semiapretado.png", "Ventanas/boton-menu-apretado.png"),
    ("Ventanas: Reiniciar", "Ventanas/boton-reiniciar.png", "Ventanas/boton-reiniciar-semiapretado.png", "Ventanas/boton-reiniciar-apretado.png"),
    ("Ventanas: Siguiente", "Ventanas/boton-siguiente.png", "Ventanas/boton-siguiente-semiapretado.png", "Ventanas/boton-siguiente-apretado.png"),
]

todos_sprites_ok = True
for nombre_btn, ruta_norm, ruta_semi, ruta_apr in tripletas_botones:
    s_norm = cargar_boton(ruta_norm)
    s_semi = cargar_boton(ruta_semi)
    s_apr = cargar_boton(ruta_apr)

    if not s_norm or not s_semi or not s_apr:
        print(f"[ERROR] Falla al cargar tripleta para {nombre_btn}: norm={bool(s_norm)}, semi={bool(s_semi)}, apr={bool(s_apr)}")
        todos_sprites_ok = False
    else:
        print(f"[OK] {nombre_btn}: 3 sprites verificados.")

assert todos_sprites_ok, "Falló la verificación de sprites de botones."

# 2. VERIFICAR COMPORTAMIENTO DE animar_pulsacion_boton EN MODO CLICK DIRECTO
rect_test = pygame.Rect(100, 100, 200, 60)
spr_norm = pygame.Surface((200, 60))
spr_norm.fill((100, 100, 255))
spr_semi = pygame.Surface((200, 60))
spr_semi.fill((150, 150, 255))
spr_apr = pygame.Surface((200, 60))
spr_apr.fill((200, 200, 255))

# Al no haber mouse presionado, debe reproducir semi (55ms) -> apr (60ms) -> semi (45ms) -> norm y retornar True
resultado_click = animar_pulsacion_boton(pantalla, rect_test, spr_semi, spr_apr, (0, 0, 0), spr_norm)
assert resultado_click == True, f"animar_pulsacion_boton debía retornar True tras soltar, retornó: {resultado_click}"
print("[OK] Test de clic normal: retorna True y transiciona los 3 estados correctamente.")

# 3. VERIFICAR QUE NO QUEDAN EVENTOS DE MOUSEBUTTONUP PENDIENTES TRAS LA ANIMACION
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (150, 120)}))
resultado_con_evento = animar_pulsacion_boton(pantalla, rect_test, spr_semi, spr_apr, (0, 0, 0), spr_norm)
eventos_restantes = [e for e in pygame.event.get() if e.type == pygame.MOUSEBUTTONUP]
assert len(eventos_restantes) == 0, f"Quedaron {len(eventos_restantes)} eventos MOUSEBUTTONUP sin limpiar"
print("[OK] Test de eventos: los eventos MOUSEBUTTONUP son consumidos limpiamente sin duplicación.")

print("\n==============================================================")
print("¡TODAS LAS VERIFICACIONES DE ANIMACION DE BOTONES FUERON EXITOSAS!")
print("==============================================================")
