import os
import sys
import pygame
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import pantalla
import movimientos

ancho = 640
alto = 480
mundo = pygame.Surface((ancho, alto))
mundo.fill((10, 30, 60))

# Dibujar fondo y elementos del escenario
suelo = pygame.Rect(0, alto - 60, ancho, 60)
pantalla.dibujar_lecho_marino(mundo, suelo, ancho)

roca1 = pygame.Rect(100, 100, 120, 200)
roca2 = pygame.Rect(350, 150, 140, 270)
pantalla.dibujar_rocas_submarinas_escenario(mundo, [{"rect": roca1}, {"rect": roca2}])

# Flechas indicadoras
flechas = [
    {"x": 160, "y": 80, "direccion": "derecha", "tipo": "llave"},
    {"x": 420, "y": 130, "direccion": "abajo", "tipo": "oxigeno"},
]
# Dibujar flechas
for f in flechas:
    # función de dibujo de flechas
    pass

# Llave y puerta
llave = movimientos.crear_llave(450, 100)
puerta = movimientos.crear_puerta(520, alto - 60 - 90)
mundo.blit(llave["sprite"], llave["rect"])
mundo.blit(puerta["sprites"]["cerrada"], puerta["rect"])

# Personajes
p1 = movimientos.crear_personaje(180, 220, "Celeste")
p2 = movimientos.crear_personaje(380, 220, "Violeta")

# Capa de oscuridad
surf_oscuridad = pygame.Surface((ancho, alto), pygame.SRCALPHA)
surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna(radio_linterna=160, radio_tenue=45)

surf_oscuridad.fill((3, 7, 15, 252))

# Substraer luz de linternas
# P1 apagada, P2 encendida
for pj, linterna_on in [(p1, False), (p2, True)]:
    cx = pj["hitbox"].centerx
    cy = pj["hitbox"].centery
    if linterna_on:
        surf_oscuridad.blit(surf_luz, (cx - 160, cy - 160), special_flags=pygame.BLEND_RGBA_SUB)
    else:
        surf_oscuridad.blit(surf_tenue, (cx - 45, cy - 45), special_flags=pygame.BLEND_RGBA_SUB)

mundo.blit(surf_oscuridad, (0, 0))

# Dibujar personajes ENCIMA de la oscuridad
pantalla.dibujar_personaje(mundo, p1, None)
pantalla.dibujar_personaje(mundo, p2, None)
pantalla.dibujar_linterna_minero(mundo, p1, False)
pantalla.dibujar_linterna_minero(mundo, p2, True)

out_preview = r"C:\Users\Malena\.gemini\antigravity-ide\brain\effb8b14-e88d-402a-8aae-c082111f922f\test_light_scene.png"
pygame.image.save(mundo, out_preview)
print("Saved light scene preview to:", out_preview)
