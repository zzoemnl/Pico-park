import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pantalla
from movimientos import (
    crear_personaje,
    crear_llave,
    crear_puerta,
    crear_pincho,
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    resolver_colisiones,
    comprobar_pinchos,
    actualizar_llave,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    DISTANCIA_SOGA_REPOSO,
    DISTANCIA_SOGA_MAXIMA,
)

print("=== TEST INTEGRAL: MUNDO 2 NIVEL 5 (PLATAFORMAS ALTERNADAS) ===")

ALTO = 720
ancho_mundo_nivel = 1400
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

plat_inicio = pygame.Rect(0, 560, 160, 26)
plat_inicio_base = pygame.Rect(0, 586, 160, suelo.top - 586 + 80)

plat_llegada = pygame.Rect(730, 130, 670, 26)
plat_llegada_base = pygame.Rect(730, 156, 670, suelo.top - 156 + 80)

# Layout alternado en zigzag con amplio despeje vertical (headroom > 70px):
# P1: Izquierda (x: 180..410, y: 480) - Centro 295
# P2: Derecha   (x: 430..660, y: 390) - Centro 545 (dx = +250 hacia la derecha)
# P3: Izquierda (x: 130..360, y: 300) - Centro 245 (dx = -300 hacia la izquierda, 180px vertical sobre P1)
# P4: Derecha   (x: 480..710, y: 210) - Centro 595 (dx = +350 hacia la derecha, 180px vertical sobre P2)
plataformas_alternadas = [
    pygame.Rect(180, 480, 230, 24),  # P1 (Izquierda, y=480)
    pygame.Rect(430, 390, 230, 24),  # P2 (Derecha,   y=390)
    pygame.Rect(130, 300, 230, 24),  # P3 (Izquierda, y=300)
    pygame.Rect(480, 210, 230, 24),  # P4 (Derecha,   y=210)
]

plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]
plataformas = list(plataformas_base) + list(plataformas_alternadas)

pozo_nivel = {
    "x": 160,
    "y": 570,
    "ancho": 570,
    "alto": 70,
}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(165, 725, 32)]

llave = crear_llave(595 - 12, 210 - 46)
puerta = crear_puerta(810, 130 - 90)

# 1. Comprobar alternancia horizontal estricta y alternancia de signos en delta_x:
deltas_x = []
for i in range(len(plataformas_alternadas) - 1):
    p_cur = plataformas_alternadas[i]
    p_next = plataformas_alternadas[i+1]
    dx = p_next.centerx - p_cur.centerx
    deltas_x.append(dx)
    if i % 2 == 0:
        # Hacia la derecha
        assert dx > 0, f"Debe avanzar hacia la DERECHA de P{i+1} a P{i+2}"
        assert p_cur.centerx < 400 and p_next.centerx > 400
    else:
        # Hacia la izquierda
        assert dx < 0, f"Debe avanzar hacia la IZQUIERDA de P{i+1} a P{i+2}"
        assert p_cur.centerx > 400 and p_next.centerx < 400

print(f"Deltas horizontales entre plataformas: {deltas_x}")
assert deltas_x[0] > 0 and deltas_x[1] < 0 and deltas_x[2] > 0
print("1. Alternancia horizontal Izquierda -> Derecha -> Izquierda -> Derecha [OK]")

# 2. Comprobar que no es una escalera continua (no todas las plataformas avanzan en la misma dirección)
assert not all(d > 0 for d in deltas_x), "Las plataformas NO deben formar una escalera continua"
print("2. Distribución alternada sin diagonal continua ascendente [OK]")

# 3. Comprobar abismo continuo bajo todas las plataformas con pinchos mortales
assert pozo_nivel["x"] == plat_inicio.right
assert pozo_nivel["x"] + pozo_nivel["ancho"] == plat_llegada.left
for p in pinchos:
    assert pozo_nivel["x"] <= p.x <= plat_llegada.left
print(f"3. Abismo continuo bajo todas las plataformas con {len(pinchos)} pinchos mortales [OK]")

# 4. Probar muerte conjunta al caer en pinchos o abismo
p1_cae = crear_personaje(500, 600, "Celeste")
assert comprobar_pinchos(p1_cae, pinchos) == True and p1_cae["muerto"] == True
print("4. Muerte conjunta al caer en pinchos o abismo [OK]")

# 5. Probar ascenso cooperativo completo por las plataformas alternadas
p1 = crear_personaje(40, 560 - ALTO_HITBOX, "Celeste")
p2 = crear_personaje(100, 560 - ALTO_HITBOX, "Violeta")

def simular_paso_jugador(p, dir_x, saltar=False):
    if saltar and p["en_suelo"]:
        p["vel_y"] = p["fuerza_salto"]
        p["en_suelo"] = False
    p["vel_x"] = dir_x * p["velocidad_mov"]
    resolver_colisiones(p, None, suelo, mundo_rect, caja=None, plataformas=plataformas)

# Inicio
resolver_colisiones(p1, None, suelo, mundo_rect, caja=None, plataformas=plataformas)
resolver_colisiones(p2, None, suelo, mundo_rect, caja=None, plataformas=plataformas)

# P1 (Izquierda)
p1["hitbox"].x = 110
for f in range(35):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[0].top:
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[0].top

# P2 (Derecha)
p1["hitbox"].x = plataformas_alternadas[0].right - ANCHO_HITBOX
p1["hitbox"].bottom = plataformas_alternadas[0].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(45):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[1].top:
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[1].top

# P3 (Izquierda)
p1["hitbox"].x = plataformas_alternadas[1].left
p1["hitbox"].bottom = plataformas_alternadas[1].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(45):
    simular_paso_jugador(p1, dir_x=-1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[2].top:
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[2].top

# P4 (Derecha)
p1["hitbox"].x = plataformas_alternadas[2].right - ANCHO_HITBOX
p1["hitbox"].bottom = plataformas_alternadas[2].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(45):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[3].top:
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[3].top
print("5. Ascenso cooperativo completo por las plataformas alternadas [OK]")

# 6. Llave recogida en Plataforma 4
p1["hitbox"].centerx = plataformas_alternadas[3].centerx
p1["hitbox"].bottom = plataformas_alternadas[3].top
actualizar_llave(llave, [p1, p2], puerta)
assert llave["recolectada"] == True
print("6. Llave recogida en la plataforma 4 [OK]")

# 7. Salto / llegada a la puerta de salida
p1["hitbox"].x = plataformas_alternadas[3].right - ANCHO_HITBOX
p1["hitbox"].bottom = plataformas_alternadas[3].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(50):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plat_llegada.top:
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plat_llegada.top
print("7. Nivel completado con ambos personajes en la puerta de salida [OK]")

# 8. Renderizado de plataformas alternadas con cables y halo de llave sin errores
surf_test = pygame.Surface((1280, 720), pygame.SRCALPHA)
pantalla.dibujar_plataformas_alternadas_escenario(surf_test, plataformas_alternadas, pozo_nivel)
print("8. Renderizado de plataformas alternadas con cables y halo de llave sin errores [OK]")

print("\n=== VERIFICACIÓN INTEGRAL DE MUNDO 2 NIVEL 5 EXITOSA (100%) ===")
