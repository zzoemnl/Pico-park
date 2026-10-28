import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
from movimientos import crear_personaje, resolver_colisiones

suelo = pygame.Rect(0, 640, 1500, 80)
mundo_rect = pygame.Rect(0, 0, 1500, 720)

# Simular trayectoria de salto libre desde (0, 0)
# Queremos saber las coordenadas (x, y) relativas en cada frame del salto con vel_x = 6
p = crear_personaje(100, 400, "Celeste")
p["en_suelo"] = True
p["vel_y"] = p["fuerza_salto"]
p["en_suelo"] = False

trayectoria = []
x_ini = p["hitbox"].x
y_ini = p["hitbox"].bottom

print(f"Salto inicial: fuerza={p['fuerza_salto']}, vel_x=6, gravedad=0.85")
print(f"Punto de inicio: x={x_ini}, bottom={y_ini}")

for f in range(40):
    p["vel_x"] = 6
    resolver_colisiones(p, None, suelo, mundo_rect)
    dx = p["hitbox"].x - x_ini
    dy = p["hitbox"].bottom - y_ini # negativo = más alto
    trayectoria.append((f, dx, dy, p["vel_y"]))
    if f % 2 == 0 or dy > 0:
        print(f"Frame {f:02d}: dx={dx:3d}, dy={dy:5.1f} (altura={-dy:5.1f}), vel_y={p['vel_y']:5.1f}")
    if dy > 0 and p["vel_y"] > 0:
        break
