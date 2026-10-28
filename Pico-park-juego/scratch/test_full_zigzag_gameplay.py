import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
from movimientos import (
    crear_personaje,
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    resolver_colisiones,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    DISTANCIA_SOGA_MAXIMA,
    DISTANCIA_SOGA_REPOSO,
)

# Proposed Zigzag Layout
# Base Start: x: 0..200, y: 520
# P1 (Izquierda): x: 180..400, y: 465 (center 290)
# P2 (Derecha):   x: 420..640, y: 410 (center 530) -> Shift +240 right!
# P3 (Izquierda): x: 120..340, y: 355 (center 230) -> Shift -300 left! Staggered vs P1 by 60px!
# P4 (Derecha):   x: 360..580, y: 300 (center 470) -> Shift +240 right! Staggered vs P2 by 60px!
# Salida (Cima):  x: 600..1300, y: 245 (center 950) -> Shift +480 right!
plat_inicio = pygame.Rect(0, 520, 200, 26)
p1 = pygame.Rect(180, 465, 220, 24)
p2 = pygame.Rect(420, 410, 220, 24)
p3 = pygame.Rect(120, 355, 220, 24)
p4 = pygame.Rect(360, 300, 220, 24)
salida = pygame.Rect(600, 245, 700, 26)

plataformas = [plat_inicio, p1, p2, p3, p4, salida]
suelo = pygame.Rect(0, 640, 1300, 80)
mundo_rect = pygame.Rect(0, 0, 1300, 720)

transiciones = [
    (plat_inicio, p1, 1, "1. Inicio -> P1 (Izquierda)"),
    (p1, p2, 1, "2. P1 (Izquierda) -> P2 (Derecha)"),
    (p2, p3, -1, "3. P2 (Derecha) -> P3 (Izquierda)"),
    (p3, p4, 1, "4. P3 (Izquierda) -> P4 (Derecha)"),
    (p4, salida, 1, "5. P4 (Derecha) -> Salida (Cima)"),
]

print("=== VERIFICACIÓN COOPERATIVA COMPLETA CON SOGA ===")
all_ok = True

for pa, pb, dir_x, name in transiciones:
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}
    
    # Ambos inician en pa
    if dir_x > 0:
        j1_x = pa.right - ANCHO_HITBOX - 5
        j2_x = pa.right - ANCHO_HITBOX - 30
    else:
        j1_x = pa.left + 5
        j2_x = pa.left + 30
        
    j1 = crear_personaje(j1_x, pa.top - ALTO_HITBOX, "Celeste")
    j2 = crear_personaje(j2_x, pa.top - ALTO_HITBOX, "Violeta")
    
    resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
    resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)
    
    assert j1["en_suelo"] and j1["hitbox"].bottom == pa.top, f"{name}: J1 no quedó en suelo inicial"
    assert j2["en_suelo"] and j2["hitbox"].bottom == pa.top, f"{name}: J2 no quedó en suelo inicial"
    
    max_soga = 0.0
    
    # Fase 1: J1 salta a pb
    j1_llego = False
    for f in range(40):
        if f == 0:
            j1["vel_y"] = j1["fuerza_salto"]
            j1["en_suelo"] = False
        j1["vel_x"] = dir_x * 6
        j2["vel_x"] = 0
        actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)
        max_soga = max(max_soga, estado_soga["distancia"])
        
        if j1["en_suelo"] and pb.collidepoint(j1["hitbox"].centerx, j1["hitbox"].bottom):
            j1_llego = True
            break
            
    if not j1_llego:
        print(f"FAILED: J1 no llegó en {name}")
        all_ok = False
        break
        
    # Fase 2: J2 camina al borde de salto de pa
    for f in range(15):
        if dir_x > 0:
            if j2["hitbox"].right >= pa.right - 8:
                break
            j2["vel_x"] = 5
        else:
            if j2["hitbox"].left <= pa.left + 8:
                break
            j2["vel_x"] = -5
            
        j1["vel_x"] = 0
        actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)
        max_soga = max(max_soga, estado_soga["distancia"])
        
    # Fase 3: J2 salta a pb
    j2_llego = False
    for f in range(40):
        if f == 0:
            j2["vel_y"] = j2["fuerza_salto"]
            j2["en_suelo"] = False
        j2["vel_x"] = dir_x * 6
        j1["vel_x"] = 0
        actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=plataformas)
        resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=plataformas)
        max_soga = max(max_soga, estado_soga["distancia"])
        
        if j2["en_suelo"] and pb.collidepoint(j2["hitbox"].centerx, j2["hitbox"].bottom):
            j2_llego = True
            break
            
    if not j2_llego:
        print(f"FAILED: J2 no llegó en {name}")
        all_ok = False
        break
        
    print(f"  [OK] {name}: Ambos superaron el salto. Max tensión soga: {max_soga:.1f}px (Límite: {DISTANCIA_SOGA_MAXIMA}px)")

print(f"\nResultado global: {'EXITO TOTAL 100%' if all_ok else 'FALLO'}")
