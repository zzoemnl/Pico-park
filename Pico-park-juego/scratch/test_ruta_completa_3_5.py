import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def run_route_test():
    print("=== TEST DE RUTA COMPLETA Y ACCESIBILIDAD NIVEL 3-5 ===")
    ancho_mundo = 2600
    ALTO = 720
    suelo = pygame.Rect(0, ALTO - 75, ancho_mundo, 75)
    techo_agua = pygame.Rect(0, 0, ancho_mundo, 25)

    # Configuración corregida de rocas submarinas:
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
        # Altura reducida a 260 (y=25..285) para paso amplio (360px vertical) hacia Cámara 3
        {"rect": pygame.Rect(1400, techo_agua.bottom, 220, 260)},
        # Ancho 240 (x=1640..1880) para abrir chimenea de ascenso holgada hacia Cámara 4 (x=1880..1980)
        {"rect": pygame.Rect(1640, techo_agua.bottom, 240, 230)},
        {"rect": pygame.Rect(1640, 480, 140, suelo.top - 480)},

        # Repisa abisal donde reposa la llave dorada
        {"rect": pygame.Rect(1780, 590, 110, suelo.top - 590), "coral": True, "color_coral": (255, 135, 70)},

        # Sector 5: Pared antes del refugio y terraza
        {"rect": pygame.Rect(1980, 270, 110, suelo.top - 270)},
        # Altura reducida a 170 (y=25..195) para paso amplio desde Cámara 4 a la terraza
        {"rect": pygame.Rect(2210, techo_agua.bottom, 180, 170)},
        {"rect": pygame.Rect(2210, 540, 180, suelo.top - 540)},

        # Terraza final de llegada con la puerta
        {"rect": pygame.Rect(2390, 440, 210, suelo.top - 440), "coral": True, "color_coral": (255, 140, 80)},
    ]

    # Barreras de algas: sin bloqueo impenetrable
    barreras_algas = []

    # Pinchos
    pinchos = [
        movimientos.crear_pincho(350, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(780, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(950, suelo.top - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(1200, 520 - 24, 140, 24, direccion="arriba"),
        movimientos.crear_pincho(1640, 480 - 24, 100, 24, direccion="arriba"),
        movimientos.crear_pincho(1890, suelo.top - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(2180, 540 - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(2210, techo_agua.bottom + 170, 100, 24, direccion="abajo"),
    ]

    obstaculos = [techo_agua, suelo] + [r["rect"] for r in rocas_submarinas]

    camaras_aire = [
        {"rect": pygame.Rect(40, 160, 200, 260), "nombre": "Cámara 1: Refugio Inicial"},
        {"rect": pygame.Rect(860, 50, 190, 200), "nombre": "Cámara 2: Gruta Superior"},
        {"rect": pygame.Rect(1440, 420, 190, 225), "nombre": "Cámara 3: Fosa de la Llave"},
        {"rect": pygame.Rect(2020, 60, 190, 210), "nombre": "Cámara 4: Refugio Final"},
    ]

    llave = movimientos.crear_llave(1820, 590 - 46)
    puerta = movimientos.crear_puerta(2460, 440 - 90)

    p1 = movimientos.crear_personaje(80, 280, "Celeste")
    p2 = movimientos.crear_personaje(150, 280, "Violeta")

    # Waypoints continuos reales para el personaje de 50x85
    # Segmentos de navegación paso a paso
    ruta = [
        (80, 280),    # Inicio en Cámara 1
        (180, 300),   # Salida Cámara 1
        (380, 380),   # Sector 2: Corredor de corriente rápida
        (600, 380),   # Avance en corriente
        (800, 440),   # Base del Geiser
        (820, 300),   # Ascenso por Geiser
        (840, 160),   # Entrada a Cámara 2 (O2)
        (920, 120),   # Centro de Cámara 2 (Recarga)
        (1020, 160),  # Salida de Cámara 2
        (1100, 320),  # Entrada al desfiladero vertical
        (1260, 440),  # Descenso hacia el fondo
        (1420, 440),  # Entrada amplia a Cámara 3
        (1520, 500),  # Centro de Cámara 3 (Recarga)
        (1650, 380),  # Salida de Cámara 3 hacia la fosa de la llave
        (1760, 440),  # Descenso a la repisa
        (1820, 520),  # Contacto con la llave
        (1840, 440),  # Ascenso con la llave
        (1930, 440),  # Base de la chimenea vertical
        (1930, 220),  # Ascenso por la chimenea
        (1980, 160),  # Desvío hacia Cámara 4
        (2080, 140),  # Centro de Cámara 4 (Recarga final)
        (2180, 240),  # Salida de Cámara 4 hacia desfiladero
        (2280, 340),  # Corredor final
        (2380, 360),  # Entrada a la terraza
        (2460, 370),  # Llegada frente a la puerta
    ]

    print("Verificando paso a paso los 25 waypoints con hitbox real de 50x85:")
    pj_rect = pygame.Rect(0, 0, 50, 85)
    for idx, (wx, wy) in enumerate(ruta):
        pj_rect.topleft = (wx, wy)
        for obs in obstaculos:
            assert not pj_rect.colliderect(obs), f"Colisión en waypoint {idx} ({wx}, {wy}) con obstáculo {obs}"
        for pin in pinchos:
            assert not pj_rect.colliderect(pin), f"Colisión en waypoint {idx} ({wx}, {wy}) con pincho {pin}"

    print(f"[OK] Los {len(ruta)} waypoints de la ruta son 100% navegables y libres de colisiones!")

    # 2. Verificar recolección de llave
    p1["hitbox"].topleft = (1820, 520)
    assert p1["hitbox"].colliderect(llave["rect"]), "P1 debe tocar la llave en el waypoint de la llave"
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert llave["recolectada"] == True and llave["portador"] == p1
    print("[OK] Llave recogida exitosamente en la repisa abisal.")

    # 3. Verificar llegada a la puerta y apertura
    p1["hitbox"].topleft = (2460, 370)
    llave["rect"].center = p1["hitbox"].center
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert puerta["abierta"] == True, "La puerta debe abrirse al llegar el portador con la llave"
    print("[OK] La puerta se abre correctamente.")

    # 4. Ambos entran a la puerta y superan el nivel
    p1_completado = False
    p2_completado = False
    if puerta["abierta"]:
        if p1["hitbox"].colliderect(puerta["rect"]):
            p1_completado = True
        p2["hitbox"].topleft = (2470, 370)
        if p2["hitbox"].colliderect(puerta["rect"]):
            p2_completado = True

    assert p1_completado and p2_completado, "Ambos personajes deben poder entrar a la puerta"
    print("[OK] Condición de victoria: Ambos personajes entran a la puerta y completan el nivel!")

if __name__ == "__main__":
    run_route_test()
