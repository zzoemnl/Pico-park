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
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    resolver_colisiones,
    actualizar_llave,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    DISTANCIA_SOGA_MAXIMA,
    DISTANCIA_SOGA_REPOSO,
)
import pantalla

ALTO = 720
ancho_mundo_nivel = 1300
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

# Nueva configuración de plataformas del Nivel 2-5
plat_inicio = pygame.Rect(0, 520, 200, 26)
plat_inicio_base = pygame.Rect(0, 546, 200, suelo.top - 546 + 80)

# Plataformas en zigzag dinámico equilibrado:
# P1: Izquierda (x: 180..400, y: 465, centro 290)
# P2: Derecha   (x: 440..660, y: 415, centro 550) - Desplazamiento +260 hacia la derecha
# P3: Izquierda (x: 260..480, y: 365, centro 370) - Desplazamiento -180 hacia la izquierda
# P4: Derecha   (x: 520..740, y: 315, centro 630) - Desplazamiento +260 hacia la derecha, cumbre con Llave
# Plataforma de llegada segura a la derecha en la cima (x: 760..1300, y: 265)
p1 = pygame.Rect(180, 465, 220, 24)
p2 = pygame.Rect(440, 415, 220, 24)
p3 = pygame.Rect(260, 365, 220, 24)
p4 = pygame.Rect(520, 315, 220, 24)

plat_llegada = pygame.Rect(760, 265, 540, 26)
plat_llegada_base = pygame.Rect(760, 291, 540, suelo.top - 291 + 80)

plataformas_alternadas = [p1, p2, p3, p4]
plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]
plataformas = list(plataformas_base) + list(plataformas_alternadas)

# Abismo con pinchos cubriendo desde el final de plat_inicio (x=200) hasta plat_llegada (x=760)
pozo_nivel = {
    "x": 200,
    "y": 570,
    "ancho": 560,
    "alto": 70,
}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(205, 755, 32)]

llave = crear_llave(p4.centerx - 12, p4.top - 46)
puerta = crear_puerta(880, plat_llegada.top - 90)

print(f"Total plataformas alternadas: {len(plataformas_alternadas)}")
for i, p in enumerate(plataformas_alternadas):
    print(f"  P{i+1}: Rect(x={p.x}, y={p.y}, w={p.w}, h={p.h}), Centro X={p.centerx}")

# Validar alternancia izquierda / derecha
centros = [p.centerx for p in plataformas_alternadas]
dx_12 = centros[1] - centros[0] # P1 -> P2 (debe ser > 0, hacia derecha)
dx_23 = centros[2] - centros[1] # P2 -> P3 (debe ser < 0, hacia izquierda)
dx_34 = centros[3] - centros[2] # P3 -> P4 (debe ser > 0, hacia derecha)
dx_4salida = plat_llegada.centerx - centros[3]

print(f"Desplazamientos: P1->P2: {dx_12}, P2->P3: {dx_23}, P3->P4: {dx_34}, P4->Salida: {dx_4salida}")
assert dx_12 > 0, "P2 debe estar desplazada a la DERECHA de P1"
assert dx_23 < 0, "P3 debe estar desplazada a la IZQUIERDA de P2"
assert dx_34 > 0, "P4 debe estar desplazada a la DERECHA de P3"

# Validar que NO están alineadas verticalmente
assert centros[0] != centros[2], "P1 y P3 NO deben estar alineadas verticalmente"
assert centros[1] != centros[3], "P2 y P4 NO deben estar alineadas verticalmente"
print(f"Desfase P1 vs P3: {abs(centros[2] - centros[0])}px | Desfase P2 vs P4: {abs(centros[3] - centros[1])}px")
print("[OK] Alternancia y ausencia de alineación paralela verificadas.")

# Simulación de saltos cooperativos
def simular_salto(plat_a, plat_b, dir_x, nombre):
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}
    if dir_x > 0:
        p1_x = plat_a.right - 40
        p2_x = plat_a.right - 65
    else:
        p1_x = plat_a.left + 5
        p2_x = plat_a.left + 30

    jug1 = crear_personaje(p1_x, plat_a.top - ALTO_HITBOX, "Celeste")
    jug2 = crear_personaje(p2_x, plat_a.top - ALTO_HITBOX, "Violeta")

    resolver_colisiones(jug1, None, suelo, mundo_rect, plataformas=plataformas)
    resolver_colisiones(jug2, None, suelo, mundo_rect, plataformas=todas_base if 'todas_base' in locals() else plataformas)

    # Fase 1: jug1 salta
    jug1_ok = False
    for f in range(40):
        if f == 0:
            jug1["vel_y"] = jug1["fuerza_salto"]
            jug1["en_suelo"] = False
        jug1["vel_x"] = dir_x * 6
        jug2["vel_x"] = 0

        actualizar_fisica_soga(jug1, jug2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(jug1, jug2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(jug1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(jug2, None, suelo, mundo_rect, plataformas=plataformas)

        if jug1["en_suelo"] and plat_b.collidepoint(jug1["hitbox"].centerx, jug1["hitbox"].bottom):
            jug1_ok = True
            break

    if not jug1_ok:
        return False, f"Jug1 no llegó a {nombre}"

    # Fase 2: jug2 salta
    jug2_ok = False
    for f in range(40):
        if f == 0:
            jug2["vel_y"] = jug2["fuerza_salto"]
            jug2["en_suelo"] = False
        jug2["vel_x"] = dir_x * 6
        jug1["vel_x"] = 0

        actualizar_fisica_soga(jug1, jug2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(jug1, jug2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(jug1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(jug2, None, suelo, mundo_rect, plataformas=plataformas)

        if jug2["en_suelo"] and plat_b.collidepoint(jug2["hitbox"].centerx, jug2["hitbox"].bottom):
            jug2_ok = True
            break

    if not jug2_ok:
        return False, f"Jug2 no llegó a {nombre}"

    return True, f"{nombre}: 100% superado"

transiciones = [
    (plat_inicio, p1, 1, "Inicio -> P1 (Izq)"),
    (p1, p2, 1, "P1 (Izq) -> P2 (Der)"),
    (p2, p3, -1, "P2 (Der) -> P3 (Izq)"),
    (p3, p4, 1, "P3 (Izq) -> P4 (Der)"),
    (p4, plat_llegada, 1, "P4 (Der) -> Salida"),
]

print("\n--- Ejecutando simulación de saltos para cada transición ---")
for pa, pb, dx, n in transiciones:
    ok, m = simular_salto(pa, pb, dx, n)
    print(f"  {n}: {ok} | {m}")
    assert ok, f"Fallo en {n}: {m}"

print("\n>>> TODOS LOS SALTOS COOPERATIVOS SON 100% VIABLES Y JUGABLES CON SOGA <<<")

# Renderizar imagen para verificación visual
superficie = pygame.Surface((ancho_mundo_nivel, ALTO))
superficie.fill((25, 20, 28)) # Fondo industrial Mundo 2

# Dibujar pozo de pinchos
pygame.draw.rect(superficie, (40, 25, 25), (pozo_nivel["x"], pozo_nivel["y"], pozo_nivel["ancho"], pozo_nivel["alto"]))
for pi in pinchos:
    superficie.blit(pi["sprite"], pi["rect"])

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

# Dibujar personajes en la cima de P4
j1 = crear_personaje(p4.centerx - 30, p4.top - ALTO_HITBOX, "Blanco")
j2 = crear_personaje(p4.centerx + 10, p4.top - ALTO_HITBOX, "Blanco")
pantalla.dibujar_personaje(superficie, j1, None)
pantalla.dibujar_personaje(superficie, j2, None)
pantalla.dibujar_soga_escenario(superficie, j1, j2, {"tirante": False, "distancia": 40}, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)

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
fuente = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 14, bold=True)
for i, p in enumerate(plataformas_alternadas):
    lado = "IZQ" if i % 2 == 0 else "DER"
    lbl = fuente.render(f"P{i+1} ({lado})", True, (255, 255, 200))
    superficie.blit(lbl, (p.centerx - lbl.get_width() // 2, p.top - 20))

pygame.image.save(superficie, "scratch/preview_nivel_2_5_zigzag.png")
print("[OK] Imagen de previsualización guardada en scratch/preview_nivel_2_5_zigzag.png")
