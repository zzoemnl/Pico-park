import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.abspath("c:/Users/Malena/Documents/GitHub/Pico-park/Pico-park-juego"))

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

ALTO = 720
ancho_mundo_nivel = 1300
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

plat_inicio = pygame.Rect(0, 520, 200, 26)
plat_inicio_base = pygame.Rect(0, 546, 200, suelo.top - 546 + 80)

plat_llegada = pygame.Rect(840, 480, 320, 26)
plat_llegada_base = pygame.Rect(840, 506, 320, suelo.top - 506 + 80)

# Layout alternado definitivo:
# P1: Izquierda (x: 240..460, y: 440) - Centro 350
# P2: Derecha   (x: 500..720, y: 365) - Centro 610
# P3: Izquierda (x: 180..410, y: 290) - Centro 295
# P4: Derecha   (x: 540..760, y: 215) - Centro 650
plataformas_alternadas = [
    pygame.Rect(240, 440, 220, 24),  # P1 (Izquierda, y=440)
    pygame.Rect(500, 365, 220, 24),  # P2 (Derecha,   y=365)
    pygame.Rect(180, 290, 230, 24),  # P3 (Izquierda, y=290)
    pygame.Rect(540, 215, 220, 24),  # P4 (Derecha,   y=215)
]

plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]
plataformas = list(plataformas_base) + list(plataformas_alternadas)

pozo_nivel = {
    "x": 200,
    "y": 570,
    "ancho": 640,
    "alto": 70,
}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 835, 32)]

llave = crear_llave(650 - 12, 215 - 46)
puerta = crear_puerta(980, 480 - 90)

print(f"Total pinchos en el abismo: {len(pinchos)}")
print(f"Pozo: x={pozo_nivel['x']}..{pozo_nivel['x'] + pozo_nivel['ancho']}")
print("Plataformas alternadas:")
for i, p in enumerate(plataformas_alternadas):
    lado = "IZQUIERDA" if p.centerx < 450 else "DERECHA"
    print(f"  P{i+1}: {lado} -> Rect({p.x}, {p.y}, {p.w}, {p.h}), Centro=({p.centerx}, {p.centery})")

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
        assert p_cur.centerx < 450 and p_next.centerx > 450
    else:
        # Hacia la izquierda
        assert dx < 0, f"Debe avanzar hacia la IZQUIERDA de P{i+1} a P{i+2}"
        assert p_cur.centerx > 450 and p_next.centerx < 450

print(f"Deltas horizontales entre plataformas: {deltas_x}")
assert deltas_x[0] > 0 and deltas_x[1] < 0 and deltas_x[2] > 0
print("[OK] Alternancia horizontal Izquierda -> Derecha -> Izquierda -> Derecha comprobada!")

# 2. Comprobar que no es una escalera continua (no todas las plataformas avanzan en la misma dirección)
assert not all(d > 0 for d in deltas_x), "Las plataformas NO deben formar una escalera continua hacia la derecha"

# 3. Comprobar pozo de pinchos bajo todo el recorrido entre plat_inicio y plat_llegada
assert pozo_nivel["x"] == plat_inicio.right
assert pozo_nivel["x"] + pozo_nivel["ancho"] == plat_llegada.left
for p in pinchos:
    assert pozo_nivel["x"] <= p.x <= plat_llegada.left
print(f"[OK] Abismo continuo bajo todas las plataformas con {len(pinchos)} pinchos mortales.")

# 4. Probar muerte al caer en pinchos o abismo
p_muere = crear_personaje(500, 600, "Celeste")
assert comprobar_pinchos(p_muere, pinchos) == True and p_muere["muerto"] == True
print("[OK] Detección de muerte por pinchos/abismo correcta.")

# 5. Simular recorrido cooperativo con física real
p1 = crear_personaje(50, 520 - ALTO_HITBOX, "Celeste")
p2 = crear_personaje(120, 520 - ALTO_HITBOX, "Violeta")

def simular_paso_jugador(p, dir_x, saltar=False):
    if saltar and p["en_suelo"]:
        p["vel_y"] = p["fuerza_salto"]
        p["en_suelo"] = False
    p["vel_x"] = dir_x * p["velocidad_mov"]
    resolver_colisiones(p, None, suelo, mundo_rect, caja=None, plataformas=plataformas)

# Inicio en plat_inicio
resolver_colisiones(p1, None, suelo, mundo_rect, caja=None, plataformas=plataformas)
resolver_colisiones(p2, None, suelo, mundo_rect, caja=None, plataformas=plataformas)
assert p1["en_suelo"] and p1["hitbox"].bottom == plat_inicio.top
assert p2["en_suelo"] and p2["hitbox"].bottom == plat_inicio.top
print("[OK] Inicio en plat_inicio correcto.")

# Salto a P1 (Izquierda)
p1["hitbox"].x = 150
for f in range(35):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[0].top:
        print(f"P1 llegó a Plataforma 1 (Izquierda) en frame {f}!")
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[0].top

# Salto a P2 (Derecha)
p1["hitbox"].x = plataformas_alternadas[0].right - ANCHO_HITBOX
p1["hitbox"].bottom = plataformas_alternadas[0].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(45):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[1].top:
        print(f"P1 llegó a Plataforma 2 (Derecha) en frame {f}!")
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[1].top

# Salto a P3 (Izquierda)
p1["hitbox"].x = plataformas_alternadas[1].left
p1["hitbox"].bottom = plataformas_alternadas[1].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(45):
    simular_paso_jugador(p1, dir_x=-1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[2].top:
        print(f"P1 llegó a Plataforma 3 (Izquierda) en frame {f}!")
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[2].top

# Salto a P4 (Derecha)
p1["hitbox"].x = plataformas_alternadas[2].right - ANCHO_HITBOX
p1["hitbox"].bottom = plataformas_alternadas[2].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(45):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[3].top:
        print(f"P1 llegó a Plataforma 4 (Derecha) en frame {f}!")
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plataformas_alternadas[3].top

# Recoger llave en P4
p1["hitbox"].centerx = plataformas_alternadas[3].centerx
p1["hitbox"].bottom = plataformas_alternadas[3].top
actualizar_llave(llave, [p1, p2], puerta)
assert llave["recolectada"] == True
print("[OK] Llave recogida con éxito en Plataforma 4!")

# Salto / descenso a plat_llegada con la puerta de salida
p1["hitbox"].x = plataformas_alternadas[3].right - ANCHO_HITBOX
p1["hitbox"].bottom = plataformas_alternadas[3].top
p1["vel_y"] = 0
p1["en_suelo"] = True
for f in range(50):
    simular_paso_jugador(p1, dir_x=1, saltar=(f==0))
    if p1["en_suelo"] and p1["hitbox"].bottom == plat_llegada.top:
        print(f"P1 llegó a plat_llegada (Salida) en frame {f}!")
        break
assert p1["en_suelo"] and p1["hitbox"].bottom == plat_llegada.top
print("[OK] P1 llegó a la plataforma de llegada con la salida!")

print("\n=== ¡SIMULACIÓN COMPLETA DE MUNDO 2 NIVEL 5 EXITOSA (100%)! ===")
