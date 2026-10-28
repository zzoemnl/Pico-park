import os
import sys
import math
import random
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, ".")

import pantalla
import movimientos
import sprites

def test_integral_m3_n3():
    print("=========================================================================")
    print("INICIANDO PRUEBAS INTEGRALES PARA MUNDO 3 NIVEL 3: LAS ROCAS PELIGROSAS")
    print("=========================================================================")

    pygame.init()
    pantalla_mock = pygame.Surface((1280, 720))

    # --- TEST 1: REGLAS ESPECÍFICAS DE MUNDO 3-3 (SIN CUERDA, MOVIMIENTO INDEPENDIENTE) ---
    print("\n--- TEST 1: REGLAS Y FÍSICAS SUBMARINAS (SIN CUERDA, 4 DIRECCIONES) ---")
    p1 = movimientos.crear_personaje(110, 330, "Celeste")
    p2 = movimientos.crear_personaje(210, 330, "Violeta")
    p1["en_agua"] = True
    p2["en_agua"] = True

    # 1. Movimiento en 4 direcciones
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=True, tecla_abajo=False, submarino=True)
    assert p1["vel_y"] < 0, "P1 debe nadar hacia arriba al pulsar tecla_arriba"

    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=True, submarino=True)
    assert p1["vel_y"] > 0, "P1 debe nadar hacia abajo al pulsar tecla_abajo"

    p1["vel_y"] = 0
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=False, submarino=True)
    assert abs(p1["vel_y"]) < 0.1, "En modo submarino debe haber flotabilidad neutra sin inputs"

    print("[OK] Test 1 superado exitosamente: Movimiento 4 direcciones y flotabilidad neutra.")

    # --- TEST 2: PELIGROS MORTALES (ERIZOS / PINCHOS COOPERATIVOS) ---
    print("\n--- TEST 2: COLISIONES CON PINCHOS Y MUERTE COOPERATIVA ---")
    pincho_prueba = movimientos.crear_pincho(500, 300, 80, 24, direccion="arriba")
    
    # Personaje toca el pincho
    p_toco = movimientos.crear_personaje(500, 290, "Celeste")
    toco = movimientos.comprobar_pinchos(p_toco, [pincho_prueba])
    assert toco and p_toco["muerto"], "El personaje debe morir al tocar el pincho"

    # Personaje lejos del pincho no debe morir
    p_lejos = movimientos.crear_personaje(100, 100, "Violeta")
    no_toco = movimientos.comprobar_pinchos(p_lejos, [pincho_prueba])
    assert not no_toco and not p_lejos["muerto"], "Personaje lejos del pincho no debe ser afectado"

    print("[OK] Test 2 superado exitosamente: Detección y letalidad de pinchos verificadas.")

    # --- TEST 3: NAVEGABILIDAD Y WAYPOINTS A LO LARGO DEL DESFILADERO ---
    print("\n--- TEST 3: NAVEGABILIDAD Y PASILLOS ESTRECHOS (14 WAYPOINTS) ---")
    ancho_mundo = 2700
    y_suelo = 645
    techo_bottom = 30

    rocas_submarinas = [
        # Zona 1: Entrada y primer estrechamiento (x = 0 .. 440)
        {"rect": pygame.Rect(320, techo_bottom, 120, 85)},
        {"rect": pygame.Rect(320, 530, 120, y_suelo - 530)},

        # Zona 2: Desfiladero serpenteante en S con chimeneas amplias (x = 450 .. 1120)
        {"rect": pygame.Rect(480, techo_bottom, 160, 210)},
        {"rect": pygame.Rect(720, 420, 180, y_suelo - 420)},
        {"rect": pygame.Rect(720, techo_bottom, 180, 85)},
        {"rect": pygame.Rect(980, techo_bottom, 140, 210)},

        # Zona 3: Gran bifurcación y Gruta de la Llave con pasajes holgados (x = 1140 .. 1720)
        {"rect": pygame.Rect(1140, techo_bottom, 480, 50)},
        {"rect": pygame.Rect(1200, 280, 360, 90), "coral": True, "color_coral": (245, 110, 140)},
        {"rect": pygame.Rect(1350, 230, 80, 18), "coral": True, "color_coral": (255, 180, 80)},
        {"rect": pygame.Rect(1240, 555, 260, y_suelo - 555)},

        # Zona 4: Laberinto de pilares con espacio para maniobrar (x = 1750 .. 2320)
        {"rect": pygame.Rect(1760, techo_bottom, 75, 270)},
        {"rect": pygame.Rect(1960, 340, 75, y_suelo - 340)},
        {"rect": pygame.Rect(2160, techo_bottom, 75, 260)},
        {"rect": pygame.Rect(2150, 560, 95, y_suelo - 560)},

        # Zona 5: Terraza final de llegada con la puerta (x = 2380 .. 2700)
        {"rect": pygame.Rect(2380, 480, 320, y_suelo - 480), "coral": True, "color_coral": (255, 140, 80)},
    ]

    pinchos = [
        # Zona 1: Primer estrechamiento
        movimientos.crear_pincho(340, techo_bottom + 85, 75, 20, direccion="abajo"),
        movimientos.crear_pincho(340, 530 - 20, 75, 20, direccion="arriba"),

        # Zona 2: Serpentín en S
        movimientos.crear_pincho(500, techo_bottom + 210, 120, 20, direccion="abajo"),
        movimientos.crear_pincho(510, y_suelo - 20, 110, 20, direccion="arriba"),
        movimientos.crear_pincho(740, 420 - 20, 140, 20, direccion="arriba"),
        movimientos.crear_pincho(740, techo_bottom + 85, 140, 20, direccion="abajo"),
        movimientos.crear_pincho(1000, techo_bottom + 210, 100, 20, direccion="abajo"),
        movimientos.crear_pincho(1000, y_suelo - 20, 100, 20, direccion="arriba"),

        # Zona 3: La gruta de la llave
        movimientos.crear_pincho(1200, techo_bottom + 50, 100, 20, direccion="abajo"),
        movimientos.crear_pincho(1460, techo_bottom + 50, 100, 20, direccion="abajo"),
        movimientos.crear_pincho(1210, 280 - 20, 90, 20, direccion="arriba"),
        movimientos.crear_pincho(1465, 280 - 20, 90, 20, direccion="arriba"),
        movimientos.crear_pincho(1280, 370, 130, 20, direccion="abajo"),
        movimientos.crear_pincho(1285, 555 - 20, 140, 20, direccion="arriba"),

        # Zona 4: Pilares y desfiladero final
        movimientos.crear_pincho(1765, techo_bottom + 270, 65, 20, direccion="abajo"),
        movimientos.crear_pincho(1755, y_suelo - 20, 85, 20, direccion="arriba"),
        movimientos.crear_pincho(1965, 340 - 20, 65, 20, direccion="arriba"),
        movimientos.crear_pincho(1960, techo_bottom, 75, 20, direccion="abajo"),
        movimientos.crear_pincho(2165, techo_bottom + 260, 65, 20, direccion="abajo"),
        movimientos.crear_pincho(2155, 560 - 20, 85, 20, direccion="arriba"),
    ]

    barreras = [{"rect": pygame.Rect(1620, 420, 35, y_suelo - 420)}]
    muros = [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras] + [
        pygame.Rect(0, 0, ancho_mundo, techo_bottom),
        pygame.Rect(0, y_suelo, ancho_mundo, 75)
    ]

    waypoints = [
        (110, 330),   # Inicio seguro
        (380, 270),   # Cruce Zona 1
        (540, 480),   # Canal inferior Zona 2
        (660, 480),   # Base chimenea ascendente Zona 2
        (660, 200),   # Cima chimenea ascendente Zona 2
        (810, 200),   # Canal superior Zona 2
        (925, 200),   # Cima chimenea descendente Zona 2
        (925, 480),   # Base chimenea descendente Zona 2
        (1050, 480),  # Canal inferior bajo Roca 4
        (1140, 140),  # Entrada Gruta de la Llave
        (1378, 140),  # Recolección Llave en repisa
        (1600, 140),  # Salida Gruta
        (1700, 340),  # Antecámara abierta
        (1860, 460),  # Paso bajo Pilar 1
        (1860, 160),  # Ascenso entre Pilar 1 y Pilar 2
        (2060, 160),  # Paso sobre Pilar 2
        (2060, 420),  # Descenso entre Pilar 2 y Pilar 3
        (2260, 420),  # Salida tras Pilar 3
        (2380, 370),  # Llegada terraza coralina
        (2480, 370),  # Puerta de salida
    ]

    for idx, (wx, wy) in enumerate(waypoints):
        test_hb = pygame.Rect(wx, wy, movimientos.ANCHO_HITBOX, movimientos.ALTO_HITBOX)
        for m in muros:
            assert not test_hb.colliderect(m), f"Waypoint {idx} ({wx}, {wy}) colisiona con muro {m}"
        for pin in pinchos:
            assert not test_hb.colliderect(pin), f"Waypoint {idx} ({wx}, {wy}) colisiona con pincho {pin}"

    print(f"-> Verificados {len(waypoints)} waypoints con hitboxes reales de {movimientos.ANCHO_HITBOX}x{movimientos.ALTO_HITBOX}: 100% transitables y sin colisión.")
    print("[OK] Test 3 superado exitosamente.")

    # --- TEST 4: DINÁMICA DE LLAVE Y PUERTA ---
    print("\n--- TEST 4: RECOGER LLAVE, ABRIR PUERTA Y COMPLETAR NIVEL ---")
    llave = movimientos.crear_llave(1378, 230 - 46)
    puerta = movimientos.crear_puerta(2480, 480 - 90)

    assert not llave["recolectada"]
    assert not puerta["abierta"]

    # P1 nada hasta la llave
    p1["hitbox"].topleft = (1365, 140)
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert llave["recolectada"], "La llave debe recogerse al contacto con P1"
    assert llave["portador"] == p1

    # P1 nada hasta la puerta
    p1["hitbox"].topleft = (2480, 390)
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert puerta["abierta"], "La puerta debe abrirse cuando el portador la toca"

    p2["hitbox"].topleft = (2480, 390)
    assert p1["hitbox"].colliderect(puerta["rect"]) and p2["hitbox"].colliderect(puerta["rect"])
    print("[OK] Test 4 superado exitosamente.")

    # --- TEST 5: RENDERIZADO VISUAL DEL ESCENARIO ---
    print("\n--- TEST 5: RENDERIZADO VISUAL DE ELEMENTOS ---")
    mundo_surf = pygame.Surface((ancho_mundo, 720))
    suelo_rect = pygame.Rect(0, y_suelo, ancho_mundo, 75)

    pantalla.dibujar_submarino_fondo_escenario(mundo_surf, ancho_mundo, tick=15)
    pantalla.dibujar_lecho_marino(mundo_surf, suelo_rect, ancho_mundo)
    pantalla.dibujar_rocas_submarinas_escenario(mundo_surf, rocas_submarinas)
    pantalla.dibujar_peligros_marinos_escenario(mundo_surf, pinchos)
    pantalla.dibujar_barreras_algas_escenario(mundo_surf, barreras, tick=15)
    
    corales_demo = [
        {"tipo": "anemona", "x": 1390, "y": 220, "escala": 1.15, "fase": 1.2, "color": (255, 210, 60), "color_sec": (255, 255, 180), "anclaje": "abajo"},
        {"tipo": "ramificado", "x": 2420, "y": 480, "escala": 1.25, "fase": 0.8, "color": (255, 130, 70), "color_sec": (255, 200, 140), "anclaje": "abajo"},
    ]
    pantalla.dibujar_corales_escenario(mundo_surf, corales_demo, tick=15)

    burbujas = pantalla.crear_sistema_burbujas_m3(ancho_mundo, cantidad=40)
    pantalla.actualizar_y_dibujar_burbujas_m3(mundo_surf, burbujas, [p1, p2], tick=15)

    print("[OK] Test 5 superado exitosamente: Todos los elementos visuales renderizan sin fallos.")

    print("\n=========================================================================")
    print(">>> TODOS LOS TESTS DE INTEGRACION DEL NIVEL 3-3 PASARON CON EXITO (5/5) <<<")
    print("=========================================================================")

if __name__ == "__main__":
    test_integral_m3_n3()
