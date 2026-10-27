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
ancho_mundo_nivel = 1400
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

# Plataforma de inicio (y=560)
plat_inicio = pygame.Rect(0, 560, 160, 26)
plat_inicio_base = pygame.Rect(0, 586, 160, suelo.top - 586 + 80)

# Plataformas alternadas (Zigzag lateral con amplio despeje vertical)
p1 = pygame.Rect(180, 480, 230, 24)  # P1 (Izquierda, centro 295, y=480)
p2 = pygame.Rect(430, 390, 230, 24)  # P2 (Derecha,   centro 545, y=390)
p3 = pygame.Rect(130, 300, 230, 24)  # P3 (Izquierda, centro 245, y=300)
p4 = pygame.Rect(480, 210, 230, 24)  # P4 (Derecha,   centro 595, y=210)

# Plataforma de llegada segura a la derecha en la cima (y=130)
plat_llegada = pygame.Rect(730, 130, 670, 26)
plat_llegada_base = pygame.Rect(730, 156, 670, suelo.top - 156 + 80)

plataformas_alternadas = [p1, p2, p3, p4]
plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]
plataformas = list(plataformas_base) + list(plataformas_alternadas)

# Abismo con pinchos bajo todo el recorrido suspendido (x: 160..730)
pozo_nivel = {
    "x": 160,
    "y": 570,
    "ancho": 570,
    "alto": 70,
}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(165, 725, 32)]

# Llave en P4 y Puerta en plat_llegada
llave = crear_llave(p4.centerx - 12, p4.top - 46)
puerta = crear_puerta(810, plat_llegada.top - 90)

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

# Dibujar personajes en P1 para mostrar el amplio despeje vertical respecto a P3
j1 = crear_personaje(200, p1.top - ALTO_HITBOX, "Celeste")
j2 = crear_personaje(270, p1.top - ALTO_HITBOX, "Violeta")
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
    (810, plat_llegada.top)
]
pygame.draw.lines(superficie, (255, 230, 80), False, puntos_trayectoria, 3)
for pt in puntos_trayectoria:
    pygame.draw.circle(superficie, (255, 255, 220), pt, 6)

# Indicadores de despeje vertical
# Entre cabeza de j2 en P1 (y=395) y fondo de P3 (y=324): 71px
pygame.draw.line(superficie, (80, 220, 120), (330, 324), (330, 395), 2)
pygame.draw.line(superficie, (80, 220, 120), (324, 324), (336, 324), 2)
pygame.draw.line(superficie, (80, 220, 120), (324, 395), (336, 395), 2)

fuente = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
fuente_peq = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 12, bold=True)

txt_headroom = fuente_peq.render("Despeje: 71px (libre)", True, (80, 255, 140))
superficie.blit(txt_headroom, (342, 350))

# Etiquetas
txt_inicio = fuente.render("INICIO", True, (255, 255, 255))
superficie.blit(txt_inicio, (50, 520))

txt_salida = fuente.render("SALIDA", True, (255, 255, 255))
superficie.blit(txt_salida, (820, plat_llegada.top - 115))

for i, p in enumerate(plataformas_alternadas):
    lado = "IZQ" if i % 2 == 0 else "DER"
    lbl = fuente.render(f"P{i+1} ({lado})", True, (255, 255, 180))
    superficie.blit(lbl, (p.centerx - lbl.get_width() // 2, p.top - 24))

out_img1 = "scratch/nivel_2_5_zigzag_despejado.png"
out_img2 = "C:/Users/Malena/.gemini/antigravity-ide/brain/effb8b14-e88d-402a-8aae-c082111f922f/nivel_2_5_zigzag_despejado.png"
pygame.image.save(superficie, out_img1)
pygame.image.save(superficie, out_img2)
print(f"[OK] Imagen guardada en {out_img1} y {out_img2}")
