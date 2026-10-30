import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1280, 720))
from personajes_menu import GestorPersonajesMenu

g = GestorPersonajesMenu()
max_dx = 0
max_dy = 0

for f in range(500):
    pos_prev = [(p["hitbox"].x, p["hitbox"].y) for p in g.personajes]
    g.actualizar()
    for i, p in enumerate(g.personajes):
        dx = abs(p["hitbox"].x - pos_prev[i][0])
        dy = abs(p["hitbox"].y - pos_prev[i][1])
        if dx > max_dx:
            max_dx = dx
        if dy > max_dy:
            max_dy = dy
        if dx >= 25 or dy >= 25:
            print(f"Teletransporte f={f}, P{i}: dx={dx}, dy={dy}, sup={p['superficie']}")

print(f"Max dx: {max_dx}, Max dy: {max_dy}")
