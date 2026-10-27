import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.abspath("c:/Users/Malena/Documents/GitHub/Pico-park/Pico-park-juego"))

import pantalla
import sprites

# Crear superficie de 1280x720
surf = pygame.Surface((1280, 720))
surf.fill((25, 20, 30))  # Fondo oscuro industrial

# Inicializar nivel 2-5 simulando la lógica de pantalla.py
ALTO = 720
ancho_mundo_nivel = 1300
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

plat_inicio = pygame.Rect(0, 520, 200, 26)
plat_inicio_base = pygame.Rect(0, 546, 200, suelo.top - 546 + 80)

plat_llegada = pygame.Rect(840, 480, 460, 26)
plat_llegada_base = pygame.Rect(840, 506, 460, suelo.top - 506 + 80)

plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]

plataformas_alternadas = [
    pygame.Rect(240, 440, 220, 24),  # P1: Izquierda (y=440)
    pygame.Rect(500, 365, 220, 24),  # P2: Derecha   (y=365)
    pygame.Rect(180, 290, 230, 24),  # P3: Izquierda (y=290)
    pygame.Rect(540, 215, 220, 24),  # P4: Derecha   (y=215)
]
plataformas = list(plataformas_base) + list(plataformas_alternadas)

pozo_nivel = {
    "x": 200,
    "y": 570,
    "ancho": 640,
    "alto": 70,
}
from movimientos import crear_pincho, crear_llave, crear_puerta, crear_personaje
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 835, 32)]
llave = crear_llave(650 - 12, 215 - 46)
puerta = crear_puerta(980, 480 - 90)

p1 = crear_personaje(50, 520 - 85, "Celeste")
p2 = crear_personaje(120, 520 - 85, "Violeta")

# Dibujar suelo y plataformas
pygame.draw.rect(surf, (180, 90, 65), suelo)
for plat in plataformas:
    pygame.draw.rect(surf, (200, 105, 75), plat, border_radius=4)
    pygame.draw.rect(surf, (120, 55, 35), plat, width=2, border_radius=4)

# Dibujar pinchos
pantalla.dibujar_pinchos_escenario(surf, pinchos)

# Dibujar cables y detalles de plataformas alternadas
pantalla.dibujar_plataformas_alternadas_escenario(surf, plataformas_alternadas, pozo_nivel)

# Dibujar personajes, soga, llave y puerta
pantalla.dibujar_soga_escenario(surf, p1, p2)
sprites.dibujar_personaje(surf, p1)
sprites.dibujar_personaje(surf, p2)

# Dibujar llave
surf.blit(llave["sprite"], llave["rect"])

# Dibujar puerta
surf.blit(puerta["sprites"]["cerrada"], puerta["rect"])

# Dibujar etiquetas de texto explicativas
fuente = pygame.font.SysFont("Arial", 18, bold=True)
txt_inicio = fuente.render("INICIO", True, (255, 255, 255))
surf.blit(txt_inicio, (50, 490))

txt_salida = fuente.render("SALIDA", True, (255, 255, 255))
surf.blit(txt_salida, (990, 440))

for idx, p in enumerate(plataformas_alternadas):
    lado = "IZQ" if p.centerx < 450 else "DER"
    lbl = fuente.render(f"P{idx+1} ({lado})", True, (255, 240, 180))
    surf.blit(lbl, (p.centerx - 30, p.top - 25))

# Dibujar líneas guía de alternancia zig-zag
pts = [(plat_inicio.centerx, plat_inicio.top)] + [(p.centerx, p.top) for p in plataformas_alternadas] + [(plat_llegada.left + 80, plat_llegada.top)]
for i in range(len(pts) - 1):
    pygame.draw.line(surf, (255, 230, 80), pts[i], pts[i+1], 3)

out_path = r"c:\Users\Malena\Documents\GitHub\Pico-park\Pico-park-juego\scratch\nivel_2_5_verificacion.png"
pygame.image.save(surf, out_path)
print(f"Captura guardada en {out_path}")
