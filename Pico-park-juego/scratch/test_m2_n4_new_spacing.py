import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
sys.path.insert(0, ".")
from movimientos import *

ancho_mundo_nivel = 2600
ALTO = 720
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

plat_inicio = pygame.Rect(0, 460, 200, 26)
plat_llegada = pygame.Rect(2190, 460, 410, 26)
plataformas_base = [plat_inicio, plat_llegada]

pw = 110
ph = 22

coords_plats = [
    (320, 460),
    (550, 430),
    (785, 460),
    (1020, 420),
    (1255, 450),
    (1490, 420),
    (1725, 450),
    (1960, 460),
]

def _crear_p(px, py):
    return {
        "rect": pygame.Rect(px, py, pw, ph),
        "x_inicial": px,
        "y_inicial": py,
        "y": float(py),
        "vel_y": 0.0,
        "ancho": pw,
        "alto": ph,
        "estado": "intacta",
        "tiempo_restante": 60,
        "pisada": False,
        "particulas": [],
    }

def _actualizar_derrumbables(plats, j1, j2):
    for p_d in plats:
        if not p_d["pisada"]:
            pjs_pisando = False
            for pj in (j1, j2):
                if not pj["muerto"]:
                    hb = pj["hitbox"]
                    if (
                        hb.right > p_d["rect"].left + 2
                        and hb.left < p_d["rect"].right - 2
                        and abs(hb.bottom - p_d["rect"].top) <= 8
                        and (pj["en_suelo"] or pj.get("vel_y", 0) >= 0)
                    ):
                        pjs_pisando = True
                        break
            if pjs_pisando:
                p_d["pisada"] = True
                p_d["tiempo_restante"] = 60

        if p_d["pisada"] and p_d["tiempo_restante"] > 0:
            p_d["tiempo_restante"] -= 1
            if p_d["tiempo_restante"] <= 20:
                p_d["estado"] = "temblando"
            else:
                p_d["estado"] = "agrietandose"

            if p_d["tiempo_restante"] <= 0:
                p_d["estado"] = "derrumbada"
                for pj in (j1, j2):
                    if not pj["muerto"]:
                        hb = pj["hitbox"]
                        if (
                            hb.right > p_d["rect"].left + 2
                            and hb.left < p_d["rect"].right - 2
                            and abs(hb.bottom - p_d["rect"].top) <= 8
                        ):
                            pj["en_suelo"] = False

        if p_d["estado"] == "derrumbada":
            p_d["vel_y"] += 1.5
            p_d["y"] += p_d["vel_y"]
            p_d["rect"].y = int(p_d["y"])

print("=== VERIFICACIÓN DE GAPS EN MUNDO 2 NIVEL 4 ===")
gaps = []
prev_right = plat_inicio.right
for i, (px, py) in enumerate(coords_plats):
    gap = px - prev_right
    gaps.append(gap)
    print(f"Gap {i} (-> P{i+1}): {gap}px, dy={py - 460 if i==0 else py - coords_plats[i-1][1]}px")
    prev_right = px + pw
gap_final = plat_llegada.left - prev_right
gaps.append(gap_final)
print(f"Gap final (P8 -> Llegada): {gap_final}px")
print(f"Gaps mínimos/máximos: {min(gaps)}px / {max(gaps)}px (todos >= 120px, con riesgo real de caer)")

# Test 1: Simulación cooperativa completa con soga
print("\n--- TEST 1: RECORRIDO COOPERATIVO CON SOGA Y DERRUMBE ---")
plats = [_crear_p(px, py) for px, py in coords_plats]
llave = crear_llave(1075, 420 - 46)
puerta = crear_puerta(2380, 460 - 90)

j1 = crear_personaje(140, 460 - ALTO_HITBOX, "Celeste")
j2 = crear_personaje(70, 460 - ALTO_HITBOX, "Violeta")
estado_soga = {"tirante": False, "distancia": 70, "tension": 0.0, "rota": False}
todas_inicial = [plat_inicio, plat_llegada] + [p["rect"] for p in plats]

pozo_nivel = {"x": 200, "y": 570, "ancho": 1990, "alto": 70}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 2185, 35)]

exito = False
for f in range(450):
    j1["vel_x"] = 6
    j2["vel_x"] = 6

    # Salto automático al aproximarse al borde
    for pj in (j1, j2):
        if pj["en_suelo"]:
            for r in [plat_inicio] + [p["rect"] for p in plats if p["estado"] != "derrumbada"]:
                if r.collidepoint(pj["hitbox"].centerx, pj["hitbox"].bottom):
                    if pj["hitbox"].right >= r.right - 10:
                        pj["vel_y"] = pj["fuerza_salto"]
                        pj["en_suelo"] = False
                    break

    actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    activas = [plat_inicio, plat_llegada] + [p["rect"] for p in plats if p["estado"] != "derrumbada"]
    aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, activas, suelo, estado_soga)

    _actualizar_derrumbables(plats, j1, j2)
    activas = [plat_inicio, plat_llegada] + [p["rect"] for p in plats if p["estado"] != "derrumbada"]

    resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=activas)
    resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=activas)

    if comprobar_pinchos(j1, pinchos) or comprobar_pinchos(j2, pinchos):
        print(f"FALLO en frame {f}: personaje tocó pinchos!")
        break

    actualizar_llave(llave, [j1, j2], puerta)
    if puerta["abierta"] and j1["hitbox"].left >= plat_llegada.left and j2["hitbox"].left >= plat_llegada.left:
        print(f"[OK] Ambos llegaron a la meta y abrieron la puerta en frame {f}!")
        exito = True
        break

assert exito, "El recorrido cooperativo debe ser exitoso"

# Test 2: Comprobar que caminar sin saltar resulta en caída al abismo y muerte
print("\n--- TEST 2: VERIFICAR QUE SIN SALTO CAEN AL ABISMO (RIESGO REAL) ---")
j_sin_salto = crear_personaje(140, 460 - ALTO_HITBOX, "Celeste")
cayo = False
for f in range(50):
    j_sin_salto["vel_x"] = 6  # corre pero no salta
    resolver_colisiones(j_sin_salto, None, suelo, mundo_rect, plataformas=[plat_inicio] + [p["rect"] for p in plats])
    if comprobar_pinchos(j_sin_salto, pinchos):
        cayo = True
        print(f"[OK] Personaje sin saltar cayó al abismo y murió en frame {f}!")
        break

assert cayo, "Un personaje que camina sin saltar debe caer al abismo"

print("\n¡TODAS LAS PRUEBAS DE MUNDO 2 NIVEL 4 PASARON CON ÉXITO!")
