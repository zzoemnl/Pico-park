import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
sys.path.insert(0, ".")
from movimientos import *
import pantalla

ancho_mundo_nivel = 2700
ALTO = 720
suelo = pygame.Rect(0, ALTO - 75, ancho_mundo_nivel, 75)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)
techo_agua = pygame.Rect(0, 0, ancho_mundo_nivel, 30)

rocas_submarinas = [
    # Zona 1: Entrada y primer estrechamiento (x = 0 .. 440)
    {"rect": pygame.Rect(320, techo_agua.bottom, 120, 85)},
    {"rect": pygame.Rect(320, 530, 120, suelo.top - 530)},

    # Zona 2: Desfiladero serpenteante en S con chimeneas amplias (x = 450 .. 1120)
    {"rect": pygame.Rect(480, techo_agua.bottom, 160, 210)},
    {"rect": pygame.Rect(720, 420, 180, suelo.top - 420)},
    {"rect": pygame.Rect(720, techo_agua.bottom, 180, 85)},
    {"rect": pygame.Rect(980, techo_agua.bottom, 140, 210)},

    # Zona 3: Gran bifurcación y Gruta de la Llave con pasajes holgados (x = 1140 .. 1720)
    {"rect": pygame.Rect(1140, techo_agua.bottom, 480, 50)},
    {"rect": pygame.Rect(1200, 280, 360, 90), "coral": True, "color_coral": (245, 110, 140)},
    {"rect": pygame.Rect(1350, 230, 80, 18), "coral": True, "color_coral": (255, 180, 80)},
    {"rect": pygame.Rect(1240, 555, 260, suelo.top - 555)},

    # Zona 4: Laberinto de pilares con espacio para maniobrar (x = 1750 .. 2320)
    {"rect": pygame.Rect(1760, techo_agua.bottom, 75, 270)},
    {"rect": pygame.Rect(1960, 340, 75, suelo.top - 340)},
    {"rect": pygame.Rect(2160, techo_agua.bottom, 75, 260)},
    {"rect": pygame.Rect(2150, 560, 95, suelo.top - 560)},

    # Zona 5: Terraza final de llegada con la puerta (x = 2380 .. 2700)
    {"rect": pygame.Rect(2380, 480, 320, suelo.top - 480), "coral": True, "color_coral": (255, 140, 80)},
]

pinchos = [
    # Zona 1: Primer estrechamiento
    crear_pincho(340, techo_agua.bottom + 85, 75, 20, direccion="abajo"),
    crear_pincho(340, 530 - 20, 75, 20, direccion="arriba"),

    # Zona 2: Serpentín en S
    crear_pincho(500, techo_agua.bottom + 210, 120, 20, direccion="abajo"),
    crear_pincho(510, suelo.top - 20, 110, 20, direccion="arriba"),
    crear_pincho(740, 420 - 20, 140, 20, direccion="arriba"),
    crear_pincho(740, techo_agua.bottom + 85, 140, 20, direccion="abajo"),
    crear_pincho(1000, techo_agua.bottom + 210, 100, 20, direccion="abajo"),
    crear_pincho(1000, suelo.top - 20, 100, 20, direccion="arriba"),

    # Zona 3: La gruta de la llave
    crear_pincho(1200, techo_agua.bottom + 50, 100, 20, direccion="abajo"),
    crear_pincho(1460, techo_agua.bottom + 50, 100, 20, direccion="abajo"),
    crear_pincho(1210, 280 - 20, 90, 20, direccion="arriba"),
    crear_pincho(1465, 280 - 20, 90, 20, direccion="arriba"),
    crear_pincho(1280, 370, 130, 20, direccion="abajo"),
    crear_pincho(1285, 555 - 20, 140, 20, direccion="arriba"),

    # Zona 4: Pilares y desfiladero final
    crear_pincho(1765, techo_agua.bottom + 270, 65, 20, direccion="abajo"),
    crear_pincho(1755, suelo.top - 20, 85, 20, direccion="arriba"),
    crear_pincho(1965, 340 - 20, 65, 20, direccion="arriba"),
    crear_pincho(1960, techo_agua.bottom, 75, 20, direccion="abajo"),
    crear_pincho(2165, techo_agua.bottom + 260, 65, 20, direccion="abajo"),
    crear_pincho(2155, 560 - 20, 85, 20, direccion="arriba"),
]

barreras_algas = [
    {"rect": pygame.Rect(1620, 420, 35, suelo.top - 420)},
]

plataformas_base = [techo_agua] + [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas]
plataformas = list(plataformas_base)

llave = crear_llave(1378, 230 - 46)
puerta = crear_puerta(2480, 480 - 90)

print("=== VERIFICACIÓN DE PASAJES EN MUNDO 3 NIVEL 3 ===")
gap_z3_sup = (280 - 20) - (techo_agua.bottom + 50 + 20)
print(f"Zona 3 Canal Superior (Llave): gap = {gap_z3_sup}px (margen con pj de 85px: {gap_z3_sup - 85}px)")
assert gap_z3_sup - 85 >= 60

gap_z3_inf = (555 - 20) - (370 + 20)
print(f"Zona 3 Canal Inferior: gap = {gap_z3_inf}px (margen con pj de 85px: {gap_z3_inf - 85}px)")
assert gap_z3_inf - 85 >= 45

gap_z4_p1_p2 = 1960 - (1760 + 75)
gap_z4_p2_p3 = 2160 - (1960 + 75)
print(f"Zona 4 Pilares: gap horizontal P1-P2 = {gap_z4_p1_p2}px, P2-P3 = {gap_z4_p2_p3}px (margen ancho 50px: {gap_z4_p1_p2 - 50}px)")
assert gap_z4_p1_p2 - 50 >= 60

waypoints = [
    (110, 330),   # Inicio seguro
    (380, 270),   # Cruce Zona 1
    (540, 480),   # Canal inferior Zona 2
    (660, 480),   # Base de chimenea ascendente Zona 2
    (660, 200),   # Cima de chimenea ascendente Zona 2
    (810, 200),   # Canal superior Zona 2
    (925, 200),   # Cima de chimenea descendente Zona 2
    (925, 480),   # Base de chimenea descendente Zona 2
    (1050, 480),  # Canal inferior bajo Roca 4
    (1140, 140),  # Entrada Gruta de la Llave
    (1378, 140),  # Recolección de Llave en repisa
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

muros = [r["rect"] for r in rocas_submarinas] + [b["rect"] for b in barreras_algas] + [
    pygame.Rect(0, 0, ancho_mundo_nivel, techo_agua.bottom),
    pygame.Rect(0, suelo.top, ancho_mundo_nivel, 75)
]

for idx, (wx, wy) in enumerate(waypoints):
    pj_box = pygame.Rect(wx, wy, ANCHO_HITBOX, ALTO_HITBOX)
    for m in muros:
        assert not pj_box.colliderect(m), f"Waypoint {idx} ({wx}, {wy}) colisiona con muro {m}"
    for pin in pinchos:
        assert not pj_box.colliderect(pin), f"Waypoint {idx} ({wx}, {wy}) colisiona con pincho {pin}"

print(f"[OK] Todos los {len(waypoints)} waypoints con hitboxes REALES de 50x85 transitables y seguros!")

# Simular recorrido de natación continuo
p1 = crear_personaje(110, 330, "Celeste")
p2 = crear_personaje(110, 330, "Violeta")
p1["en_agua"] = True
p2["en_agua"] = True

for target_wx, target_wy in waypoints[1:]:
    llegaron = False
    for frame in range(120):
        for pj in (p1, p2):
            dx = target_wx - pj["hitbox"].x
            dy = target_wy - pj["hitbox"].y
            pj["vel_x"] = 4 if dx > 4 else (-4 if dx < -4 else 0)
            pj["vel_y"] = 4 if dy > 4 else (-4 if dy < -4 else 0)
            resolver_colisiones(pj, None, suelo, mundo_rect, plataformas=plataformas)
            if comprobar_pinchos(pj, pinchos):
                raise AssertionError(f"Personaje murió en ({pj['hitbox'].x}, {pj['hitbox'].y}) camino a ({target_wx}, {target_wy})")

        dist1 = abs(p1["hitbox"].x - target_wx) + abs(p1["hitbox"].y - target_wy)
        dist2 = abs(p2["hitbox"].x - target_wx) + abs(p2["hitbox"].y - target_wy)
        if dist1 < 25 and dist2 < 25:
            llegaron = True
            break
    assert llegaron, f"No llegaron a ({target_wx}, {target_wy})"

# Recoger llave
p1["hitbox"].topleft = (1378, 140)
actualizar_llave(llave, [p1, p2], puerta)
assert llave["recolectada"], "Llave debe haber sido recolectada"

# Abrir puerta
p1["hitbox"].topleft = (2480, 370)
p2["hitbox"].topleft = (2480, 370)
actualizar_llave(llave, [p1, p2], puerta)
assert puerta["abierta"], "Puerta debe abrirse"

print("[OK] Recorrido completo de natación, llave y puerta superado al 100%!")
print("\n¡TODAS LAS PRUEBAS DE MUNDO 3 NIVEL 3 PASARON EXITOSAMENTE!")
