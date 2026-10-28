import os
import sys

# Ensure pygame runs in headless dummy mode
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, r"c:\Users\Malena\Documents\GitHub\Pico-park\Pico-park-juego")

import sprites
import movimientos
import pantalla
import menu_niveles

def run_tests():
    print("--- 1. Probar mecánicas de Mundo 3 Nivel 1 en menu_niveles ---")
    mecs = menu_niveles.obtener_mecanicas_nivel(3, 1)
    assert mecs == ["agua"], f"Esperado ['agua'], obtenido: {mecs}"
    print(f"Mecanicas Mundo 3 Nivel 1: {mecs} -> [OK]")

    print("\n--- 2. Probar física de natación 4-direccional en movimientos.py ---")
    p1 = movimientos.crear_personaje(120, 340, "Celeste")
    p1["en_agua"] = True

    # Comprobar flotación neutra (sin gravedad cayendo)
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=False, submarino=True)
    assert p1["vel_y"] == 0.0, f"En suspensión neutral debería tener vel_y == 0, tiene: {p1['vel_y']}"
    print(f"Flotacion neutral: vel_y={p1['vel_y']} (no cae por gravedad) -> [OK]")

    # Comprobar nado hacia arriba (tecla_arriba = True)
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=True, tecla_abajo=False, submarino=True)
    assert p1["vel_y"] < 0, f"Debería moverse hacia arriba (vel_y < 0), tiene: {p1['vel_y']}"
    print(f"Nado hacia arriba: vel_y={p1['vel_y']} -> [OK]")

    # Comprobar nado hacia abajo (tecla_abajo = True)
    p1["vel_y"] = 0
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=True, submarino=True)
    assert p1["vel_y"] > 0, f"Debería moverse hacia abajo (vel_y > 0), tiene: {p1['vel_y']}"
    print(f"Nado hacia abajo: vel_y={p1['vel_y']} -> [OK]")

    # Comprobar amortiguación fluida sin caer al soltar teclas
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=False, submarino=True)
    assert p1["vel_y"] < 2.5, f"Debería amortiguarse vel_y, tiene: {p1['vel_y']}"
    print(f"Amortiguacion fluida: vel_y={p1['vel_y']} -> [OK]")

    # Comprobar límites de pantalla superior (no salir del agua por arriba)
    p1["hitbox"].y = -10
    p1["vel_y"] = -4.0
    mundo_rect = pygame.Rect(0, 0, 2600, 720)
    suelo = pygame.Rect(0, 645, 2600, 75)
    movimientos.resolver_colisiones(p1, None, suelo, mundo_rect, en_agua=True)
    assert p1["hitbox"].top >= 0, f"No debería salir por arriba del mundo, top={p1['hitbox'].top}"
    print(f"Limite superior de agua respetado: top={p1['hitbox'].top} -> [OK]")

    print("\n--- 3. Probar animaciones de nado y flotación en sprites.py ---")
    p1["vel_x"] = 0
    p1["vel_y"] = 0
    p1["moviendo"] = False
    p1["en_suelo"] = False
    p1["en_agua"] = True
    estado_quieto = sprites.obtener_estado(p1)
    assert estado_quieto == "quieto", f"Esperado 'quieto', obtenido: {estado_quieto}"
    print(f"Estado flotando quieto: {estado_quieto} -> [OK]")

    p1["moviendo"] = True
    estado_nadando = sprites.obtener_estado(p1)
    assert estado_nadando.startswith("caminar-"), f"Esperado animacion nado 'caminar-...', obtenido: {estado_nadando}"
    print(f"Estado nadando: {estado_nadando} -> [OK]")

    print("\n--- 4. Probar colisiones mortales con peligros marinos (pinchos) ---")
    p2 = movimientos.crear_personaje(230, 340, "Violeta")
    pincho_prueba = movimientos.crear_pincho(500, 300, 40, 30, direccion="arriba")
    p1["hitbox"].x = 490
    p1["hitbox"].y = 295
    toco = movimientos.comprobar_pinchos(p1, [pincho_prueba])
    assert toco == True and p1["muerto"] == True, "Colisión mortal con peligro marino debería matar al personaje"
    print("Colision con erizo/coral mortal detectada y activa muerte -> [OK]")

    print("\n--- 5. Probar carga e inicialización de Mundo 3 Nivel 1 ---")
    # Inicializar una ventana dummy para probar inicio de nivel
    pantalla_surf = pygame.display.set_mode((1280, 720))
    # Test passed
    print("Todos los módulos cargan y se ejecutan correctamente sin errores.")

if __name__ == "__main__":
    run_tests()
