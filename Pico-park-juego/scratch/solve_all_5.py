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

plat_inicio = pygame.Rect(0, 520, 200, 26)
suelo = pygame.Rect(0, 640, 1300, 80)
mundo_rect = pygame.Rect(0, 0, 1300, 720)

def test_full_layout(p1, p2, p3, p4, salida):
    plataformas = [plat_inicio, p1, p2, p3, p4, salida]
    transiciones = [
        (plat_inicio, p1, 1, "Inicio -> P1"),
        (p1, p2, 1, "P1 -> P2"),
        (p2, p3, -1, "P2 -> P3"),
        (p3, p4, 1, "P3 -> P4"),
        (p4, salida, 1, "P4 -> Salida"),
    ]
    
    for pa, pb, dir_x, name in transiciones:
        estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}
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
        
        if not j1["en_suelo"] or not j2["en_suelo"] or j1["hitbox"].bottom != pa.top or j2["hitbox"].bottom != pa.top:
            return False, f"{name}: Initial standing failed"
            
        # J1 jumps
        j1_ok = False
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
            
            if estado_soga["distancia"] > DISTANCIA_SOGA_MAXIMA or estado_soga.get("rota", False):
                return False, f"{name}: J1 rope broke"
            if j1["en_suelo"] and pb.collidepoint(j1["hitbox"].centerx, j1["hitbox"].bottom):
                j1_ok = True
                break
        if not j1_ok:
            return False, f"{name}: J1 jump failed"
            
        # J2 walks to edge
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
            if estado_soga["distancia"] > DISTANCIA_SOGA_MAXIMA or estado_soga.get("rota", False):
                return False, f"{name}: J2 walk rope broke"
                
        # J2 jumps
        j2_ok = False
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
            
            if estado_soga["distancia"] > DISTANCIA_SOGA_MAXIMA or estado_soga.get("rota", False):
                return False, f"{name}: J2 rope broke"
            if j2["en_suelo"] and pb.collidepoint(j2["hitbox"].centerx, j2["hitbox"].bottom):
                j2_ok = True
                break
        if not j2_ok:
            return False, f"{name}: J2 jump failed"
            
    return True, "ALL 5 TRANSITIONS PASSED 100%"

# Search loop over candidate staggered positions
solutions = []
for p1_x in range(160, 220, 10):
    for p2_x in range(360, 420, 10):
        for p3_x in range(100, 160, 10):
            for p4_x in range(360, 430, 10):
                for sal_x in range(540, 620, 15):
                    # Staggering checks:
                    c1 = p1_x + 110
                    c2 = p2_x + 110
                    c3 = p3_x + 110
                    c4 = p4_x + 110
                    if abs(c1 - c3) < 40: continue
                    if abs(c2 - c4) < 30: continue
                    # Left-right checks:
                    if c2 <= c1 or c3 >= c2 or c4 <= c3: continue
                    
                    p1 = pygame.Rect(p1_x, 465, 220, 24)
                    p2 = pygame.Rect(p2_x, 410, 220, 24)
                    p3 = pygame.Rect(p3_x, 355, 220, 24)
                    p4 = pygame.Rect(p4_x, 300, 220, 24)
                    salida = pygame.Rect(sal_x, 245, 1300 - sal_x, 26)
                    
                    ok, msg = test_full_layout(p1, p2, p3, p4, salida)
                    if ok:
                        solutions.append((p1_x, p2_x, p3_x, p4_x, sal_x))
                        print(f"FOUND SOLUTION: P1={p1_x}, P2={p2_x}, P3={p3_x}, P4={p4_x}, Sal={sal_x}")
                        print(f"  Centros: P1={c1}, P2={c2}, P3={c3}, P4={c4}, Sal={sal_x + 200}")
                        print(f"  Offsets: P1 vs P3 = {abs(c1-c3)}px, P2 vs P4 = {abs(c2-c4)}px")
                        break
                if solutions: break
            if solutions: break
        if solutions: break
    if solutions: break

print("Total solutions found:", len(solutions))
