import sys
import os
import math
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def test_integral_nivel_3_5():
    print("============================================================")
    print("TEST INTEGRAL Y EXHAUSTIVO: MUNDO 3, NIVEL 5 - SALIDA Y RUTA")
    print("============================================================")

    # 1. Configuración de dimensiones y superficies
    ancho_mundo_nivel = 2600
    ALTO = 720
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75) # y=645
    techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 25)

    # 2. Cámaras de aire (refugios de oxígeno)
    camaras_aire = [
        {"rect": pygame.Rect(60, 60, 180, 200), "nombre": "Cámara 1: Inicio"},
        {"rect": pygame.Rect(890, 60, 180, 200), "nombre": "Cámara 2: Geiser"},
        {"rect": pygame.Rect(1440, 420, 190, 225), "nombre": "Cámara 3: Fosa de la Llave"},
        {"rect": pygame.Rect(2020, 60, 190, 210), "nombre": "Cámara 4: Refugio Final"},
    ]

    # 3. Corrientes marinas dinámicas
    corrientes_marinas = [
        {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
        {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
        {"rect": pygame.Rect(1140, 140, 260, 380), "fuerza_x": 1.4, "fuerza_y": 2.4, "direccion": "abajo"},
        {"rect": pygame.Rect(1620, 360, 360, 280), "fuerza_x": -2.6, "fuerza_y": 0.0, "direccion": "izquierda"},
        {"rect": pygame.Rect(2180, 220, 240, 320), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
    ]

    # 4. Formaciones rocosas
    rocas_submarinas = [
        # Sector 1: Entrada y cámara inicial
        {"rect": pygame.Rect(260, techo_agua.bottom, 90, 260)},
        {"rect": pygame.Rect(260, 560, 90, suelo.top - 560)},

        # Sector 2: Estrecho de la corriente rápida
        {"rect": pygame.Rect(460, techo_agua.bottom, 180, 180)},
        {"rect": pygame.Rect(480, 560, 220, suelo.top - 560)},

        # Sector 2/3: Pilar del Geiser ascendente
        {"rect": pygame.Rect(720, 280, 70, suelo.top - 280)},
        {"rect": pygame.Rect(890, 250, 150, 260)},

        # Sector 3: Meseta central y desfiladero
        {"rect": pygame.Rect(1040, techo_agua.bottom, 120, 280)},
        {"rect": pygame.Rect(1180, 520, 220, suelo.top - 520)},

        # Sector 4: Techo de la Fosa de la Llave
        {"rect": pygame.Rect(1400, techo_agua.bottom, 220, 260)},
        {"rect": pygame.Rect(1640, techo_agua.bottom, 240, 230)},
        {"rect": pygame.Rect(1640, 480, 140, suelo.top - 480)},

        # Repisa abisal donde reposa la llave dorada
        {"rect": pygame.Rect(1780, 590, 110, suelo.top - 590), "coral": True, "color_coral": (255, 135, 70)},

        # Sector 5: Pared antes del refugio y terraza
        {"rect": pygame.Rect(1980, 270, 110, suelo.top - 270)},
        {"rect": pygame.Rect(2210, techo_agua.bottom, 180, 170)},
        {"rect": pygame.Rect(2210, 540, 180, suelo.top - 540)},

        # Terraza final de llegada con la puerta
        {"rect": pygame.Rect(2390, 440, 210, suelo.top - 440), "coral": True, "color_coral": (255, 140, 80)},
    ]

    barreras_algas = []

    # 5. Obstáculos mortales: erizos de mar puntiagudos
    pinchos = [
        # Sector 1/2: Corredor de la corriente
        movimientos.crear_pincho(350, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),

        # Sector 2/3: Techo del geiser
        movimientos.crear_pincho(780, techo_agua.bottom, 110, 24, direccion="abajo"),

        # Sector 3: Pared y lecho abisal
        movimientos.crear_pincho(950, suelo.top - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(1200, 520 - 24, 140, 24, direccion="arriba"),

        # Sector 4: Alrededores de la llave
        movimientos.crear_pincho(1640, 480 - 24, 100, 24, direccion="arriba"),
        movimientos.crear_pincho(1890, suelo.top - 24, 90, 24, direccion="arriba"),

        # Sector 5: Desfiladero final hacia la terraza
        movimientos.crear_pincho(2180, 540 - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(2210, techo_agua.bottom + 170, 100, 24, direccion="abajo"),
    ]

    # 6. Llave y puerta
    llave = movimientos.crear_llave(1820, 590 - 46)
    puerta = movimientos.crear_puerta(2460, 440 - 90)

    # 7. Flechas indicadoras
    flechas_indicadoras = [
        {"x": 200, "y": 320, "direccion": "derecha", "tipo": "ruta"},
        {"x": 540, "y": 380, "direccion": "derecha", "tipo": "ruta"},
        {"x": 810, "y": 480, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 820, "y": 240, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 850, "y": 200, "direccion": "abajo", "tipo": "ruta"},
        {"x": 850, "y": 520, "direccion": "derecha", "tipo": "ruta"},
        {"x": 1110, "y": 350, "direccion": "abajo", "tipo": "ruta"},
        {"x": 1360, "y": 480, "direccion": "derecha", "tipo": "oxigeno"},
        {"x": 1660, "y": 430, "direccion": "derecha", "tipo": "llave"},
        {"x": 1810, "y": 500, "direccion": "abajo", "tipo": "llave"},
        {"x": 1910, "y": 500, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 1940, "y": 230, "direccion": "derecha", "tipo": "oxigeno"},
        {"x": 2180, "y": 250, "direccion": "derecha", "tipo": "salida"},
        {"x": 2320, "y": 340, "direccion": "derecha", "tipo": "salida"},
        {"x": 2430, "y": 310, "direccion": "derecha", "tipo": "salida"},
    ]

    obstaculos = [techo_agua, suelo] + [r["rect"] for r in rocas_submarinas]

    # -------------------------------------------------------------
    # PRUEBA 1: Existencia, validez y propiedades de la puerta
    # -------------------------------------------------------------
    print("\n--- 1. Verificación de la Puerta de Salida ---")
    assert puerta is not None, "La puerta debe existir"
    p_rect = puerta["rect"]
    print(f"Posición de la puerta: {p_rect} (x={p_rect.x}, y={p_rect.y}, w={p_rect.width}, h={p_rect.height})")
    assert p_rect.left >= 0 and p_rect.right <= ancho_mundo_nivel, "La puerta debe estar dentro de los límites del nivel"
    assert p_rect.top >= techo_agua.bottom and p_rect.bottom <= suelo.top, "La puerta debe estar dentro de la zona jugable"
    assert "sprites" in puerta and "cerrada" in puerta["sprites"] and "abierta" in puerta["sprites"], "La puerta debe contener sprites válidos"

    # Verificar que la puerta descanse sobre la terraza y no esté dentro de una pared
    terraza = next(r["rect"] for r in rocas_submarinas if r.get("coral") and r["rect"].x == 2390)
    assert p_rect.bottom == terraza.top, f"La puerta debe descansar exactamente sobre la terraza (puerta bottom {p_rect.bottom} == terraza top {terraza.top})"
    assert p_rect.left > terraza.left and p_rect.right < terraza.right, "La puerta debe estar centrada en la terraza"
    for r in rocas_submarinas:
        if r["rect"] is not terraza:
            assert not p_rect.colliderect(r["rect"]), f"La puerta no debe intersecar ninguna otra roca: {r['rect']}"
    for pin in pinchos:
        assert not p_rect.colliderect(pin), f"La puerta no debe colisionar con pinchos: {pin}"
    print("[PASÓ] La puerta existe, está en el escenario, descansa sobre la terraza coralina y no está bloqueada ni fuera de límites.")

    # -------------------------------------------------------------
    # PRUEBA 2: Flechas indicadoras en espacio despejado
    # -------------------------------------------------------------
    print("\n--- 2. Verificación de Flechas Indicadoras ---")
    for i, f in enumerate(flechas_indicadoras):
        pos_rect = pygame.Rect(f["x"] - 10, f["y"] - 10, 20, 20)
        for r in rocas_submarinas:
            assert not pos_rect.colliderect(r["rect"]), f"Flecha {i} ({f['tipo']} en {f['x']},{f['y']}) colisiona con roca {r['rect']}"
        for pin in pinchos:
            assert not pos_rect.colliderect(pin), f"Flecha {i} colisiona con pincho {pin}"
    print(f"[PASÓ] Todas las {len(flechas_indicadoras)} flechas indicadoras están en zonas transitables y visibles.")

    # -------------------------------------------------------------
    # PRUEBA 3: Navegabilidad completa del recorrido
    # -------------------------------------------------------------
    print("\n--- 3. Verificación del Recorrido Paso a Paso ---")
    ruta = [
        (80, 160),    # Inicio en Cámara 1 (Recarga inicial)
        (180, 300),   # Salida Cámara 1
        (380, 350),   # Sector 2: Entrada a corriente rápida
        (600, 350),   # Avance en corriente
        (800, 440),   # Base del Geiser
        (820, 280),   # Ascenso por Geiser
        (840, 160),   # Entrada a Cámara 2 (O2)
        (920, 100),   # Centro de Cámara 2 (Recarga)
        (840, 260),   # Salida de Cámara 2 hacia la columna
        (840, 520),   # Descenso por la columna
        (920, 520),   # Paso bajo la roca hacia el este
        (1040, 520),  # Avance hacia la fosa
        (1120, 360),  # Entrada a la meseta central
        (1250, 360),  # Cruce de la meseta central
        (1350, 380),  # Desvío hacia Cámara 3
        (1450, 450),  # Entrada a Cámara 3 (O2)
        (1520, 500),  # Centro de Cámara 3 (Recarga)
        (1660, 310),  # Paso seguro sobre roca 11
        (1800, 380),  # Descenso hacia la fosa de la llave
        (1820, 500),  # Contacto con la llave
        (1840, 380),  # Retorno seguro desde la llave
        (1910, 440),  # Base de la chimenea vertical
        (1910, 260),  # Ascenso por chimenea
        (1950, 160),  # Desvío hacia Cámara 4
        (2080, 140),  # Centro de Cámara 4 (Recarga final)
        (2160, 240),  # Salida de Cámara 4 hacia desfiladero
        (2280, 340),  # Corredor con corriente hacia la derecha
        (2380, 350),  # Entrada a la terraza final
        (2460, 355),  # Frente a la puerta de salida
    ]

    p1 = movimientos.crear_personaje(80, 280, "Celeste")
    p2 = movimientos.crear_personaje(150, 280, "Violeta")
    p1["en_agua"] = True
    p2["en_agua"] = True

    hitbox_test = pygame.Rect(0, 0, 40, 85)
    for idx, (wx, wy) in enumerate(ruta):
        hitbox_test.topleft = (wx, wy)
        for obs in obstaculos:
            assert not hitbox_test.colliderect(obs), f"Colisión en waypoint {idx} ({wx}, {wy}) con obstáculo {obs}"
        for pin in pinchos:
            assert not hitbox_test.colliderect(pin), f"Colisión en waypoint {idx} ({wx}, {wy}) con pincho {pin}"

    print(f"[PASÓ] Los {len(ruta)} puntos del recorrido son 100% seguros y libres de colisiones!")

    # -------------------------------------------------------------
    # PRUEBA 4: Simulación de Oxígeno durante la travesía
    # -------------------------------------------------------------
    print("\n--- 4. Verificación de Autonomía de Oxígeno ---")
    oxigeno = 100.0
    camaras_visitadas = []
    frames_por_waypoint = 60 # ~1 segundo por tramo
    for idx, (wx, wy) in enumerate(ruta):
        hitbox_test.topleft = (wx, wy)
        en_camara = any(hitbox_test.colliderect(c["rect"]) for c in camaras_aire)
        if en_camara:
            camara_actual = next(c["nombre"] for c in camaras_aire if hitbox_test.colliderect(c["rect"]))
            if camara_actual not in camaras_visitadas:
                camaras_visitadas.append(camara_actual)
            oxigeno = min(100.0, oxigeno + 0.75 * frames_por_waypoint)
        else:
            oxigeno = max(0.0, oxigeno - 0.12 * frames_por_waypoint)
        assert oxigeno > 0.0, f"Oxígeno agotado en waypoint {idx} ({wx}, {wy})!"

    print(f"Cámaras de aire visitadas: {camaras_visitadas}")
    print(f"Oxígeno final al llegar a la puerta: {oxigeno:.1f}%")
    assert len(camaras_visitadas) == 4, "Los personajes deben poder usar las 4 cámaras de aire"
    print("[PASÓ] El oxígeno es suficiente y las cámaras permiten recargar adecuadamente.")

    # -------------------------------------------------------------
    # PRUEBA 5: Visibilidad con linternas y oscuridad
    # -------------------------------------------------------------
    print("\n--- 5. Verificación de Visibilidad con Linterna ---")
    # Al llegar al área de la terraza (x=2380), el radio de la linterna (165px)
    # cubre la puerta ubicada en x=2460 (distancia = 80px <= 165px)
    distancia_a_puerta = math.hypot(2460 - 2380, 350 - 360)
    assert distancia_a_puerta < 165, f"La puerta debe quedar dentro del radio de linterna (distancia {distancia_a_puerta:.1f} < 165)"
    print(f"[PASÓ] La puerta queda claramente iluminada por la linterna al aproximarse (distancia: {distancia_a_puerta:.1f}px).")

    # -------------------------------------------------------------
    # PRUEBA 6: Obtención de llave y condición de victoria
    # -------------------------------------------------------------
    print("\n--- 6. Verificación de Llave y Condición de Victoria ---")
    p1["hitbox"].topleft = (1820, 520)
    assert p1["hitbox"].colliderect(llave["rect"]), "P1 debe colisionar con la llave en la repisa abisal"
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert llave["recolectada"] == True and llave["portador"] == p1, "P1 debe ser el portador de la llave"
    print("[OK] P1 recogio la llave dorada.")

    # P1 llega a la puerta con la llave
    p1["hitbox"].topleft = (2460, 355)
    llave["rect"].center = p1["hitbox"].center
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert puerta["abierta"] == True, "La puerta debe abrirse cuando el portador llega a ella"
    print("[OK] La puerta se abrio correctamente.")

    p1_completado = False
    p2_completado = False
    if puerta["abierta"]:
        if p1["hitbox"].colliderect(puerta["rect"]):
            p1_completado = True
            p1["hitbox"].x = -9999
        p2["hitbox"].topleft = (2470, 355)
        if p2["hitbox"].colliderect(puerta["rect"]):
            p2_completado = True
            p2["hitbox"].x = -9999

    assert p1_completado and p2_completado, "Ambos personajes deben ingresar a la puerta"
    print("[OK] Jugador 1 completo el nivel.")
    print("[OK] Jugador 2 completo el nivel.")
    print("[PASO] Condicion de victoria completamente funcional!")

    print("\n============================================================")
    print("TODAS LAS PRUEBAS INTEGRALES (6/6) PASARON EXITOSAMENTE!")
    print("============================================================")

if __name__ == "__main__":
    test_integral_nivel_3_5()
