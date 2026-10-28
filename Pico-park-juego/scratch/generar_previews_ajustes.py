import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import pantalla
import movimientos
import sprites

artifact_dir = r"C:\Users\Malena\.gemini\antigravity-ide\brain\effb8b14-e88d-402a-8aae-c082111f922f"

# ==========================================
# 1. RENDER MUNDO 2 NIVEL 4 (Escala 2600x720 -> vista panoramica)
# ==========================================
ancho_mundo = 2600
ALTO = 720
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo, 80)

# Inicializar nivel 2-4 llamando a pantalla.iniciar_mundo o construyendolo
surf_m2 = pygame.Surface((ancho_mundo, ALTO))
surf_m2.fill((25, 20, 28))

# Dibujar fondo y elementos
plat_inicio = pygame.Rect(0, 460, 200, 26)
plat_inicio_base = pygame.Rect(0, 486, 200, suelo.top - 486 + 80)
plat_llegada = pygame.Rect(2190, 460, 410, 26)
plat_llegada_base = pygame.Rect(2190, 486, 410, suelo.top - 486 + 80)

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

pozo_nivel = {"x": 200, "y": 570, "ancho": 1990, "alto": 70}
pinchos_m2 = [movimientos.crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 2185, 35)]
llave_m2 = movimientos.crear_llave(1075, 420 - 46)
puerta_m2 = movimientos.crear_puerta(2380, 460 - 90)

# Dibujar suelo
pygame.draw.rect(surf_m2, (40, 35, 45), suelo)
pygame.draw.rect(surf_m2, (15, 10, 20), pygame.Rect(pozo_nivel["x"], pozo_nivel["y"], pozo_nivel["ancho"], pozo_nivel["alto"]))

# Dibujar pinchos
pantalla.dibujar_pinchos_escenario(surf_m2, pinchos_m2)

# Dibujar plataformas base
for pbase in [plat_inicio_base, plat_llegada_base]:
    pygame.draw.rect(surf_m2, (55, 48, 60), pbase)
for ptop in [plat_inicio, plat_llegada]:
    pygame.draw.rect(surf_m2, (110, 100, 120), ptop)
    pygame.draw.rect(surf_m2, (170, 160, 185), ptop, 2)

# Dibujar plataformas derrumbables
for px, py in coords_plats:
    r = pygame.Rect(px, py, 110, 22)
    pygame.draw.rect(surf_m2, (180, 140, 60), r)
    pygame.draw.rect(surf_m2, (230, 190, 100), r, 2)

surf_m2.blit(llave_m2["sprite"], llave_m2["rect"])
surf_m2.blit(puerta_m2["sprites"]["cerrada"], puerta_m2["rect"])

# Escalar a 1280x360 para vista previa nitida
preview_m2 = pygame.transform.smoothscale(surf_m2, (1280, 354))
out_m2 = os.path.join(artifact_dir, "nivel_2_4_separacion_aumentada.png")
pygame.image.save(preview_m2, out_m2)
print("Preview M2-4 guardado en:", out_m2)

# ==========================================
# 2. RENDER MUNDO 3 NIVEL 3 (2700x720)
# ==========================================
ancho_mundo_3 = 2700
suelo_3 = pygame.Rect(0, ALTO - 75, ancho_mundo_3, 75)
surf_m3 = pygame.Surface((ancho_mundo_3, ALTO))
surf_m3.fill((10, 30, 60))

pantalla.dibujar_submarino_fondo_escenario(surf_m3, ancho_mundo_3, tick=10)
pantalla.dibujar_lecho_marino(surf_m3, suelo_3, ancho_mundo_3)

# Dibujar rocas submarinas y corales
rocas_submarinas = [
    {"rect": pygame.Rect(320, 30, 120, 85)},
    {"rect": pygame.Rect(320, 530, 120, suelo_3.top - 530)},
    {"rect": pygame.Rect(480, 30, 160, 210)},
    {"rect": pygame.Rect(720, 420, 180, suelo_3.top - 420)},
    {"rect": pygame.Rect(720, 30, 180, 85)},
    {"rect": pygame.Rect(980, 30, 140, 210)},
    {"rect": pygame.Rect(1140, 30, 480, 50)},
    {"rect": pygame.Rect(1200, 280, 360, 90), "coral": True, "color_coral": (245, 110, 140)},
    {"rect": pygame.Rect(1350, 230, 80, 18), "coral": True, "color_coral": (255, 180, 80)},
    {"rect": pygame.Rect(1240, 555, 260, suelo_3.top - 555)},
    {"rect": pygame.Rect(1760, 30, 75, 270)},
    {"rect": pygame.Rect(1960, 340, 75, suelo_3.top - 340)},
    {"rect": pygame.Rect(2160, 30, 75, 260)},
    {"rect": pygame.Rect(2150, 560, 95, suelo_3.top - 560)},
    {"rect": pygame.Rect(2380, 480, 320, suelo_3.top - 480), "coral": True, "color_coral": (255, 140, 80)},
]

pinchos_m3 = [
    movimientos.crear_pincho(340, 30 + 85, 75, 20, direccion="abajo"),
    movimientos.crear_pincho(340, 530 - 20, 75, 20, direccion="arriba"),
    movimientos.crear_pincho(500, 30 + 210, 120, 20, direccion="abajo"),
    movimientos.crear_pincho(510, suelo_3.top - 20, 110, 20, direccion="arriba"),
    movimientos.crear_pincho(740, 420 - 20, 140, 20, direccion="arriba"),
    movimientos.crear_pincho(740, 30 + 85, 140, 20, direccion="abajo"),
    movimientos.crear_pincho(1000, 30 + 210, 100, 20, direccion="abajo"),
    movimientos.crear_pincho(1000, suelo_3.top - 20, 100, 20, direccion="arriba"),
    movimientos.crear_pincho(1200, 30 + 50, 100, 20, direccion="abajo"),
    movimientos.crear_pincho(1460, 30 + 50, 100, 20, direccion="abajo"),
    movimientos.crear_pincho(1210, 280 - 20, 90, 20, direccion="arriba"),
    movimientos.crear_pincho(1465, 280 - 20, 90, 20, direccion="arriba"),
    movimientos.crear_pincho(1280, 370, 130, 20, direccion="abajo"),
    movimientos.crear_pincho(1285, 555 - 20, 140, 20, direccion="arriba"),
    movimientos.crear_pincho(1765, 30 + 270, 65, 20, direccion="abajo"),
    movimientos.crear_pincho(1755, suelo_3.top - 20, 85, 20, direccion="arriba"),
    movimientos.crear_pincho(1965, 340 - 20, 65, 20, direccion="arriba"),
    movimientos.crear_pincho(1960, 30, 75, 20, direccion="abajo"),
    movimientos.crear_pincho(2165, 30 + 260, 65, 20, direccion="abajo"),
    movimientos.crear_pincho(2155, 560 - 20, 85, 20, direccion="arriba"),
]

pantalla.dibujar_rocas_submarinas_escenario(surf_m3, rocas_submarinas)
pantalla.dibujar_peligros_marinos_escenario(surf_m3, pinchos_m3)

llave_m3 = movimientos.crear_llave(1378, 230 - 46)
puerta_m3 = movimientos.crear_puerta(2480, 480 - 90)

surf_m3.blit(llave_m3["sprite"], llave_m3["rect"])
surf_m3.blit(puerta_m3["sprites"]["cerrada"], puerta_m3["rect"])

preview_m3 = pygame.transform.smoothscale(surf_m3, (1280, 341))
out_m3 = os.path.join(artifact_dir, "nivel_3_3_pasadizos_amplios.png")
pygame.image.save(preview_m3, out_m3)
print("Preview M3-3 guardado en:", out_m3)
