import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

import sprites
import main

print("=== TEST: SELECCIÓN Y PRUEBA DE ACCESORIOS EN EL MENÚ Y JUEGO ===")

accesorios = sprites.obtener_accesorios_disponibles()
print(f"Accesorios disponibles ({len(accesorios)}): {[a['id'] for a in accesorios]}")

# 1. Probar que todos los accesorios se pueden dibujar en el preview de personajes de main.py
cx_p1 = 360
cx_p2 = 920
colores = ["Celeste", "Violeta", "Rojo", "Rosa", "Verde"]

for acc in accesorios:
    acc_id = acc["id"]
    for col in colores:
        sp_pj = sprites.cargar_sprites(col)
        img_pj = sp_pj.get("quieto", list(sp_pj.values())[0])
        rect_pj = img_pj.get_rect(center=(cx_p1, 236))
        pantalla.blit(img_pj, rect_pj)

        if acc_id and acc_id != "Ninguno":
            # Llamada idéntica a la línea 1181 de main.py
            sprites.dibujar_accesorio_en_personaje(pantalla, acc_id, rect_pj, mirando_derecha=True)
            sprites.dibujar_accesorio_en_personaje(pantalla, acc_id, rect_pj, mirando_derecha=False)

print("[OK] Test 1: Previsualización de todos los accesorios en personajes completada sin errores.")

# 2. Probar que dibujar_accesorio_en_personaje funciona con el diccionario del personaje del juego
for acc in accesorios:
    p_juego = {
        "accesorio": acc["id"],
        "mirando_derecha": True,
        "hitbox": pygame.Rect(100, 200, 70, 85),
    }
    surf_dummy = pygame.Surface((70, 85))
    rect_dummy = surf_dummy.get_rect()
    sprites.dibujar_accesorio_en_personaje(pantalla, p_juego, surf_dummy, rect_dummy)

print("[OK] Test 2: Renderizado in-game de accesorios sobre entidades de personaje completado.")

print("==================================================================")
print("¡TODAS LAS PRUEBAS DE ACCESORIOS FUNCIONAN CORRECTAMENTE (100%)!")
print("==================================================================")
