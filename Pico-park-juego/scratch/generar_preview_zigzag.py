import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
from movimientos import (
    crear_personaje,
    crear_llave,
    crear_puerta,
    crear_pincho,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    DISTANCIA_SOGA_MAXIMA,
    DISTANCIA_SOGA_REPOSO,
)
import pantalla
import sprites

ALTO = 720
ancho_mundo_nivel = 1300
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

# Plataforma de inicio
plat_inicio = pygame.Rect(0, 520, 200, 26)
plat_inicio_base = pygame.Rect(0, 546, 200, suelo.top - 546 + 80)

# Plataformas alternadas (Zigzag lateral sin alineación paralela)
p1 = pygame.Rect(200, 465, 220, 24)  # P1 (Izquierda, centro 310)
p2 = pygame.Rect(400, 410, 220, 24)  # P2 (Derecha,   centro 510)
p3 = pygame.Rect(130, 355, 220, 24)  # P3 (Izquierda, centro 240)
p4 = pygame.Rect(450, 300, 220, 24)  # P4 (Derecha,   centro 560)

# Plataforma de llegada segura a la derecha en la cima
plat_llegada = pygame.Rect(690, 245, 610, 26)
plat_llegada_base = pygame.Rect(690, 271, 610, suelo.top - 271 + 80)

plataformas_alternadas = [p1, p2, p3, p4]
plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]
plataformas = list(plataformas_base) + list(plataformas_alternadas)

# Abismo con pinchos bajo todo el recorrido suspendido (x: 200..690)
pozo_nivel = {
    "x": 200,
    "y": 570,
    "ancho": 490,
    "alto": 70,
}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 685, 32)]

# Llave en P4 y Puerta en plat_llegada
llave = crear_llave(p4.centerx - 12, p4.top - 46)
puerta = crear_puerta(820, plat_llegada.top - 90)

# Renderizar imagen para verificación visual
superficie = pygame.Surface((1280, 720))
superficie.fill((25, 20, 28)) # Fondo oscuro industrial Mundo 2

# Dibujar suelo base
pygame.draw.rect(superficie, (180, 90, 65), suelo)

# Dibujar pozo de pinchos
pygame.draw.rect(superficie, (40, 25, 25), (pozo_nivel["x"], pozo_nivel["y"], pozo_nivel["ancho"], pozo_nivel["alto"]))
pantalla.dibujar_pinchos_escenario(superficie, pinchos)

# Dibujar plataformas base y alternadas
for pl in plataformas_base:
    pygame.draw.rect(superficie, (185, 95, 65), pl, border_radius=4)
    pygame.draw.rect(superficie, (110, 45, 30), pl, width=2, border_radius=4)

for pl in plataformas_alternadas:
    pygame.draw.rect(superficie, (200, 105, 75), pl, border_radius=4)
    pygame.draw.rect(superficie, (130, 55, 35), pl, width=2, border_radius=4)

pantalla.dibujar_plataformas_alternadas_escenario(superficie, plataformas_alternadas, pozo_nivel)

# Dibujar llave y puerta
superficie.blit(llave["sprite"], llave["rect"])
superficie.blit(puerta["sprites"]["cerrada"], puerta["rect"])

# Dibujar personajes en la plataforma inicial
j1 = crear_personaje(50, 520 - ALTO_HITBOX, "Celeste")
j2 = crear_personaje(120, 520 - ALTO_HITBOX, "Violeta")
pantalla.dibujar_personaje(superficie, j1, None)
pantalla.dibujar_personaje(superficie, j2, None)
pantalla.dibujar_soga_escenario(superficie, j1, j2, {"tirante": False, "distancia": 70}, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)

# Trazar línea de trayectoria zigzag
puntos_trayectoria = [
    (plat_inicio.centerx, plat_inicio.top),
    (p1.centerx, p1.top),
    (p2.centerx, p2.top),
    (p3.centerx, p3.top),
    (p4.centerx, p4.top),
    (plat_llegada.left + 80, plat_llegada.top)
]
pygame.draw.lines(superficie, (255, 230, 80), False, puntos_trayectoria, 3)
for pt in puntos_trayectoria:
    pygame.draw.circle(superficie, (255, 255, 220), pt, 6)

# Etiquetas
fuente = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
txt_inicio = fuente.render("INICIO", True, (255, 255, 255))
superficie.blit(txt_inicio, (50, 490))

txt_salida = fuente.render("SALIDA", True, (255, 255, 255))
superficie.blit(txt_salida, (820, plat_llegada.top - 115))

for i, p in enumerate(plataformas_alternadas):
    lado = "IZQ" if i % 2 == 0 else "DER"
    lbl = fuente.render(f"P{i+1} ({lado})", True, (255, 255, 180))
    superficie.blit(lbl, (p.centerx - lbl.get_width() // 2, p.top - 24))

out_img = "scratch/nivel_2_5_zigzag_corregido.png"
pygame.image.save(superficie, out_img)
print(f"[OK] Imagen guardada en {out_img}")
