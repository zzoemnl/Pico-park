import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
sys.path.insert(0, ".")
from movimientos import *

ancho_mundo_nivel = 1400
ALTO = 720
suelo = pygame.Rect(0, ALTO - 80, ancho_mundo_nivel, 80)
mundo_rect = pygame.Rect(0, 0, ancho_mundo_nivel, ALTO)

plat_inicio = pygame.Rect(0, 560, 160, 26)
plat_inicio_base = pygame.Rect(0, 586, 160, suelo.top - 586 + 80)

plat_llegada = pygame.Rect(730, 130, 670, 26)
plat_llegada_base = pygame.Rect(730, 156, 670, suelo.top - 156 + 80)

p1 = pygame.Rect(180, 480, 230, 24)
p2 = pygame.Rect(430, 390, 230, 24)
p3 = pygame.Rect(130, 300, 230, 24)
p4 = pygame.Rect(480, 210, 230, 24)

plataformas_base = [plat_inicio, plat_inicio_base, plat_llegada, plat_llegada_base]
plataformas_alternadas = [p1, p2, p3, p4]
todas = list(plataformas_base) + list(plataformas_alternadas)

llave = crear_llave(p4.centerx - 12, p4.top - 46)
puerta = crear_puerta(plat_llegada.left + 80, plat_llegada.top - 90)

j1 = crear_personaje(40, 560 - ALTO_HITBOX, "Celeste")
j2 = crear_personaje(110, 560 - ALTO_HITBOX, "Violeta")
estado_soga = {"tirante": False, "distancia": 70, "tension": 0.0, "rota": False}

# Abismo con pinchos
pozo_nivel = {
    "x": 160,
    "y": 570,
    "ancho": 570,
    "alto": 70,
}
pinchos = [crear_pincho(x, suelo.top - 24, 32, 24, direccion="arriba") for x in range(165, 725, 32)]

print("Iniciando simulación cooperativa paso a paso...")

etapas = [
    {"nombre": "Inicio -> P1", "target": p1, "dir": 1, "x_salto_p1": 150, "x_salto_p2": 150},
    {"nombre": "P1 -> P2", "target": p2, "dir": 1, "x_salto_p1": p1.right - 10, "x_salto_p2": p1.right - 10},
    {"nombre": "P2 -> P3", "target": p3, "dir": -1, "x_salto_p1": p2.left + 10, "x_salto_p2": p2.left + 10},
    {"nombre": "P3 -> P4", "target": p4, "dir": 1, "x_salto_p1": p3.right - 10, "x_salto_p2": p3.right - 10},
    {"nombre": "P4 -> Llegada", "target": plat_llegada, "dir": 1, "x_salto_p1": p4.right - 10, "x_salto_p2": p4.right - 10},
]

exito_total = True

for etapa in etapas:
    print(f"\n=== Etapa: {etapa['nombre']} ===")
    target = etapa["target"]
    d = etapa["dir"]
    
    # 1. J1 avanza hacia el borde y salta
    saltando_j1 = False
    saltando_j2 = False
    
    for frame in range(120):
        if etapa["nombre"] == "P3 -> P4" and frame < 40:
            print(f"f={frame}: J1=({j1['hitbox'].x}, {j1['hitbox'].y}, ground={j1['en_suelo']}), J2=({j2['hitbox'].x}, {j2['hitbox'].y}, ground={j2['en_suelo']}), soga_d={estado_soga['distancia']:.1f}")

        # Mover J1 si no está en target
        en_target_j1 = target.collidepoint(j1["hitbox"].centerx, j1["hitbox"].bottom) and j1["en_suelo"]
        en_target_j2 = target.collidepoint(j2["hitbox"].centerx, j2["hitbox"].bottom) and j2["en_suelo"]
        
        if en_target_j1 and en_target_j2:
            print(f"Ambos llegaron a {etapa['nombre']} en frame {frame}!")
            break
            
        # Control J1
        if not en_target_j1:
            j1["vel_x"] = 6 * d
            if j1["en_suelo"]:
                # Comprobar si está en posición de saltar
                if d == 1 and j1["hitbox"].right >= etapa["x_salto_p1"]:
                    j1["vel_y"] = j1["fuerza_salto"]
                    j1["en_suelo"] = False
                elif d == -1 and j1["hitbox"].left <= etapa["x_salto_p1"]:
                    j1["vel_y"] = j1["fuerza_salto"]
                    j1["en_suelo"] = False
        else:
            # J1 espera en una posición segura de la plataforma para dejar espacio a J2
            target_wait_x = target.right - 45 if d == 1 else target.left + 35
            if j1["hitbox"].x < target_wait_x - 5:
                j1["vel_x"] = 3
            elif j1["hitbox"].x > target_wait_x + 5:
                j1["vel_x"] = -3
            else:
                j1["vel_x"] = 0
                
        # Control J2: sigue a J1 una vez que J1 está cerca o en target
        if not en_target_j2:
            dist_x = abs(j1["hitbox"].centerx - j2["hitbox"].centerx)
            if dist_x > 50 or en_target_j1:
                j2["vel_x"] = 6 * d
            else:
                j2["vel_x"] = 0
                
            if j2["en_suelo"]:
                if d == 1 and j2["hitbox"].right >= etapa["x_salto_p2"]:
                    j2["vel_y"] = j2["fuerza_salto"]
                    j2["en_suelo"] = False
                elif d == -1 and j2["hitbox"].left <= etapa["x_salto_p2"]:
                    j2["vel_y"] = j2["fuerza_salto"]
                    j2["en_suelo"] = False
        else:
            j2["vel_x"] = 0

        # Física de soga y colisiones
        actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
        aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, todas, suelo, estado_soga)
        
        resolver_colisiones(j1, None, suelo, mundo_rect, plataformas=todas)
        resolver_colisiones(j2, None, suelo, mundo_rect, plataformas=todas)
        
        # Comprobar si golpean techos o caen en pinchos
        if comprobar_pinchos(j1, pinchos) or comprobar_pinchos(j2, pinchos):
            print("ERROR: Un personaje toco pinchos!")
            exito_total = False
            break
            
        actualizar_llave(llave, [j1, j2], puerta)
    else:
        print(f"ERROR: Tiempo agotado en {etapa['nombre']}. J1=({j1['hitbox'].x},{j1['hitbox'].y}) J2=({j2['hitbox'].x},{j2['hitbox'].y})")
        exito_total = False
        break

print(f"\nResultado final simulación:")
print(f"Exito cooperativo: {exito_total}")
print(f"Llave recolectada: {llave['recolectada']}")
print(f"Puerta abierta: {puerta['abierta']}")
print(f"J1 en llegada: {j1['hitbox'].left >= plat_llegada.left}")
print(f"J2 en llegada: {j2['hitbox'].left >= plat_llegada.left}")
