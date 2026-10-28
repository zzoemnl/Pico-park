import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos

# Plataforma 2 del Mundo 2 Nivel 5: x=430..660, y=390
plat = pygame.Rect(430, 390, 230, 24)
plataformas = [plat]
suelo = pygame.Rect(0, 640, 1400, 80)
mundo_rect = pygame.Rect(0, 0, 1400, 720)

p1 = movimientos.crear_personaje(520, 390 - 85, "Celeste")
p1["en_suelo"] = True

# P2 cuelga 150px abajo y 40px a la izquierda, oscilando
p2 = movimientos.crear_personaje(480, 390 - 85 + 150, "Violeta")
p2["en_suelo"] = False
p2["vel_x"] = 2.0
p2["vel_y"] = 0.0

estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

print("=== SITUACIÓN EXACTA DEL NIVEL 2-5: P1 EN PLATAFORMA, P2 COLGANDO ===")
print(f"P1 inicial: x={p1['hitbox'].x}, y={p1['hitbox'].y}")
print(f"P2 inicial: x={p2['hitbox'].x}, y={p2['hitbox'].y}")

historial_p1 = []
for f in range(120):
    # P1 no toca controles
    p1["vel_x"] = 0

    movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    movimientos.aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

    historial_p1.append({
        "frame": f,
        "x": p1["hitbox"].x,
        "y": p1["hitbox"].y,
        "vx": p1["vel_x"],
        "vy": p1["vel_y"],
        "suelo": p1["en_suelo"],
        "dist": estado_soga["distancia"],
        "tension": estado_soga["tension"]
    })

print("\n--- Registro de frames seleccionados ---")
for f in [0, 1, 2, 5, 10, 15, 20, 30, 45, 60, 90, 119]:
    h = historial_p1[f]
    print(f"Frame {h['frame']:3d}: P1 x={h['x']:3d}, y={h['y']:3d}, vx={h['vx']:6.2f}, vy={h['vy']:6.2f}, suelo={h['suelo']} | dist={h['dist']:5.1f}, tension={h['tension']:.2f}")

# Métricas de inestabilidad
posiciones_x = [h["x"] for h in historial_p1]
posiciones_y = [h["y"] for h in historial_p1]
cambios_x = sum(1 for i in range(1, len(posiciones_x)) if posiciones_x[i] != posiciones_x[i-1])
cambios_y = sum(1 for i in range(1, len(posiciones_y)) if posiciones_y[i] != posiciones_y[i-1])
min_x, max_x = min(posiciones_x), max(posiciones_x)
min_y, max_y = min(posiciones_y), max(posiciones_y)

print("\n=== DIAGNÓSTICO DE INESTABILIDAD ===")
print(f"Rango de X de P1: [{min_x}, {max_x}] (desplazamiento: {max_x - min_x} px)")
print(f"Rango de Y de P1: [{min_y}, {max_y}] (desplazamiento: {max_y - min_y} px)")
print(f"Cantidad de frames con cambio involuntario de X: {cambios_x} / 119")
print(f"Cantidad de frames con cambio involuntario de Y: {cambios_y} / 119")
