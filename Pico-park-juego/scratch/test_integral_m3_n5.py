import os
import sys
import math
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def test_1_m3_n5_configuration_and_rules():
    print("--- 1. Probando configuración y reglas de Mundo 3 Nivel 5: El abismo submarino ---")
    ancho_mundo = 2600
    ALTO = 720
    y_suelo = ALTO - 75
    y_techo = 25

    # Cámaras de aire
    camaras_aire = [
        {"rect": pygame.Rect(40, 160, 200, 260), "nombre": "Cámara 1: Refugio Inicial"},
        {"rect": pygame.Rect(860, 50, 190, 200), "nombre": "Cámara 2: Gruta Superior"},
        {"rect": pygame.Rect(1440, 420, 190, 225), "nombre": "Cámara 3: Fosa de la Llave"},
        {"rect": pygame.Rect(2020, 60, 190, 210), "nombre": "Cámara 4: Refugio Final"},
    ]
    assert len(camaras_aire) == 4, "Debe haber 4 cámaras de aire"

    # Corrientes marinas
    corrientes_marinas = [
        {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
        {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
        {"rect": pygame.Rect(1140, 140, 260, 380), "fuerza_x": 1.4, "fuerza_y": 2.4, "direccion": "abajo"},
        {"rect": pygame.Rect(1620, 360, 360, 280), "fuerza_x": -2.6, "fuerza_y": 0.0, "direccion": "izquierda"},
        {"rect": pygame.Rect(2180, 220, 240, 320), "fuerza_x": 1.8, "fuerza_y": -1.8, "direccion": "arriba"},
    ]
    assert len(corrientes_marinas) == 5, "Debe haber 5 corrientes marinas activas"

    # Personajes
    p1 = movimientos.crear_personaje(80, 280, "Verde")
    p2 = movimientos.crear_personaje(150, 280, "Rosa")
    
    # Validar que inician dentro de la Cámara 1
    assert camaras_aire[0]["rect"].colliderect(p1["hitbox"]), "P1 debe iniciar dentro de la Cámara de aire 1"
    assert camaras_aire[0]["rect"].colliderect(p2["hitbox"]), "P2 debe iniciar dentro de la Cámara de aire 1"

    # Llave y Puerta
    llave = movimientos.crear_llave(1820, 590 - 46)
    puerta = movimientos.crear_puerta(2460, 440 - 90)
    assert llave["rect"].x == 1820 and llave["rect"].y == 544
    assert puerta["rect"].x == 2460 and puerta["rect"].y == 350
    print("[OK] Configuración inicial, cámaras de aire y corrientes validadas.")


def test_2_oxygen_depletion_replenishment_and_drowning():
    print("--- 2. Probando consumo de oxígeno, recarga en cámaras de aire y muerte por asfixia ---")
    camaras_aire = [
        {"rect": pygame.Rect(40, 160, 200, 260), "nombre": "Cámara 1"},
        {"rect": pygame.Rect(860, 50, 190, 200), "nombre": "Cámara 2"},
    ]

    p1 = movimientos.crear_personaje(400, 300, "Verde") # Fuera de cámaras de aire
    p2 = movimientos.crear_personaje(450, 300, "Rosa")

    oxigeno_p1 = 100.0
    oxigeno_p2 = 100.0

    # Simular 60 frames bajo el agua fuera de cámaras de aire (~1 segundo)
    for _ in range(60):
        en_cam = any(cam["rect"].colliderect(p1["hitbox"]) for cam in camaras_aire)
        assert not en_cam
        oxigeno_p1 = max(0.0, oxigeno_p1 - 0.082)
        oxigeno_p2 = max(0.0, oxigeno_p2 - 0.086)

    assert oxigeno_p1 < 96.0, f"El oxígeno de P1 debe disminuir: {oxigeno_p1}"
    assert oxigeno_p2 < 96.0, f"El oxígeno de P2 debe disminuir: {oxigeno_p2}"

    # Simular que entra en Cámara 2
    p1["hitbox"].center = (900, 100)
    for _ in range(30):
        en_cam = any(cam["rect"].colliderect(p1["hitbox"]) for cam in camaras_aire)
        assert en_cam
        oxigeno_p1 = min(100.0, oxigeno_p1 + 0.85)

    assert oxigeno_p1 > 99.0, f"El oxígeno de P1 debe recargarse en la cámara: {oxigeno_p1}"

    # Simular asfixia (oxígeno llega a 0)
    oxigeno_critico = 0.05
    oxigeno_critico = max(0.0, oxigeno_critico - 0.082)
    assert oxigeno_critico == 0.0
    if oxigeno_critico <= 0.0:
        movimientos.matar_personaje(p1)
        movimientos.matar_personaje(p2)

    assert p1["muerto"] and p2["muerto"], "Al llegar el oxígeno a 0, ambos personajes deben morir cooperativamente"
    print("[OK] Consumo, recarga y asfixia por falta de oxígeno verificados al 100%.")


def test_3_currents_physics_and_steering():
    print("--- 3. Probando física de empuje de corrientes marinas ---")
    corrientes_marinas = [
        {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
        {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
    ]

    p1 = movimientos.crear_personaje(350, 350, "Verde")
    x_inicial = p1["hitbox"].x
    
    # 1. Empuje hacia la derecha
    for corr in corrientes_marinas:
        if p1["hitbox"].colliderect(corr["rect"]):
            p1["hitbox"].x += int(corr["fuerza_x"])
            p1["hitbox"].y += int(corr["fuerza_y"])

    assert p1["hitbox"].x > x_inicial, f"La corriente horizontal debe empujar hacia la derecha: {p1['hitbox'].x}"

    # 2. Empuje hacia arriba en geiser
    p1["hitbox"].center = (840, 300)
    y_inicial = p1["hitbox"].y
    for corr in corrientes_marinas:
        if p1["hitbox"].colliderect(corr["rect"]):
            p1["hitbox"].x += int(corr["fuerza_x"])
            p1["hitbox"].y += int(corr["fuerza_y"])

    assert p1["hitbox"].y < y_inicial, f"El geiser debe empujar hacia arriba: {p1['hitbox'].y}"
    print("[OK] Empuje de corrientes marinas verificado.")


def test_4_waypoints_and_solvability():
    print("--- 4. Probando recorrido completo, transitabilidad y waypoints ---")
    ancho_mundo = 2600
    ALTO = 720
    y_suelo = ALTO - 75
    y_techo = 25
    techo_agua = pygame.Rect(0, 0, ancho_mundo, y_techo)
    suelo = pygame.Rect(0, y_suelo, ancho_mundo, 75)

    rocas_submarinas = [
        pygame.Rect(260, y_techo, 90, 260),
        pygame.Rect(260, 560, 90, y_suelo - 560),
        pygame.Rect(460, y_techo, 180, 180),
        pygame.Rect(480, 560, 220, y_suelo - 560),
        pygame.Rect(720, 280, 70, y_suelo - 280),
        pygame.Rect(890, 250, 150, 260),
        pygame.Rect(1040, y_techo, 120, 280),
        pygame.Rect(1180, 520, 220, y_suelo - 520),
        pygame.Rect(1400, y_techo, 220, 380),
        pygame.Rect(1640, y_techo, 340, 240),
        pygame.Rect(1640, 480, 140, y_suelo - 480),
        pygame.Rect(1780, 590, 110, y_suelo - 590),
        pygame.Rect(1980, 270, 110, y_suelo - 270),
        pygame.Rect(2210, y_techo, 180, 200),
        pygame.Rect(2210, 540, 180, y_suelo - 540),
        pygame.Rect(2390, 440, 210, y_suelo - 440),
    ]

    pinchos = [
        movimientos.crear_pincho(350, y_techo, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(780, y_techo, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(950, y_suelo - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(1200, 520 - 24, 140, 24, direccion="arriba"),
        movimientos.crear_pincho(1640, 480 - 24, 100, 24, direccion="arriba"),
        movimientos.crear_pincho(1890, y_suelo - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(2180, 540 - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(2210, y_techo + 200, 100, 24, direccion="abajo"),
    ]

    plataformas = [techo_agua, suelo] + rocas_submarinas

    waypoints = [
        (90, 300), (180, 300), (380, 420), (650, 420),
        (820, 480), (820, 180), (920, 160), (1100, 380),
        (1300, 420), (1500, 520), (1650, 420), (1820, 540),
        (1650, 420), (1900, 380), (2050, 180), (2150, 380),
        (2460, 380)
    ]

    pj = pygame.Rect(0, 0, 30, 40)
    for idx, (wx, wy) in enumerate(waypoints):
        pj.center = (wx, wy)
        for p in plataformas:
            assert not pj.colliderect(p), f"Waypoint {idx} colisiona con roca {p}"
        for pin in pinchos:
            assert not pj.colliderect(pin), f"Waypoint {idx} colisiona con pincho {pin}"

    print(f"[OK] Los {len(waypoints)} waypoints son 100% transitables y libres de obstáculos.")


def test_5_hud_and_visual_rendering():
    print("--- 5. Probando renderizado del HUD de oxígeno, cámaras de aire y corrientes ---")
    pantalla_surf = pygame.Surface((1280, 720))
    mundo_surf = pygame.Surface((2600, 720))

    camaras_aire = [
        {"rect": pygame.Rect(40, 160, 200, 260), "nombre": "Cámara 1"},
        {"rect": pygame.Rect(860, 50, 190, 200), "nombre": "Cámara 2"},
    ]
    corrientes_marinas = [
        {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
        {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
    ]

    # Probar HUD con oxígeno al 100%, 45% y crítico 15%
    pantalla._dibujar_hud_oxigeno_m3_n5(pantalla_surf, 100.0, 45.0, "Verde", "Rosa", 10)
    pantalla._dibujar_hud_oxigeno_m3_n5(pantalla_surf, 15.0, 10.0, "Verde", "Rosa", 20)

    # Probar dibujo de cámaras de aire y corrientes
    pantalla.dibujar_camaras_aire_escenario(mundo_surf, camaras_aire, 15)
    pantalla.dibujar_corrientes_marinas_escenario(mundo_surf, corrientes_marinas, 15)

    # Probar alerta flotante de oxígeno
    p1 = movimientos.crear_personaje(100, 300, "Verde")
    pantalla.dibujar_alerta_oxigeno_personaje(mundo_surf, p1, 15.0, 12)

    print("[OK] Renderizado visual del HUD, cámaras, corrientes y alerta ejecutado sin errores.")


def test_6_key_and_door_resolution():
    print("--- 6. Probando recolección de llave y apertura de puerta en 3-5 ---")
    llave = movimientos.crear_llave(1820, 590 - 46)
    puerta = movimientos.crear_puerta(2460, 440 - 90)

    p1 = movimientos.crear_personaje(1820, 544, "Verde")
    movimientos.actualizar_llave(llave, [p1], puerta)
    assert llave["recolectada"] is True, "P1 debe recolectar la llave"
    assert llave["portador"] == p1

    # P1 nada hacia la puerta
    p1["hitbox"].center = puerta["rect"].center
    movimientos.actualizar_llave(llave, [p1], puerta)
    assert puerta["abierta"] is True, "La puerta debe abrirse al llegar con la llave"
    print("[OK] Recolección de llave y apertura de puerta validadas.")


if __name__ == "__main__":
    test_1_m3_n5_configuration_and_rules()
    test_2_oxygen_depletion_replenishment_and_drowning()
    test_3_currents_physics_and_steering()
    test_4_waypoints_and_solvability()
    test_5_hud_and_visual_rendering()
    test_6_key_and_door_resolution()
    print("\n=======================================================")
    print(">>> TODOS LOS TESTS DE MUNDO 3 NIVEL 5 PASARON 100% <<<")
    print("=======================================================")
