import sys, os
sys.path.insert(0, r'c:\Users\Malena\Documents\GitHub\Pico-park\Pico-park-juego')
import pygame
pygame.init()
from personajes_menu import GestorPersonajesMenu

gestor = GestorPersonajesMenu()

historial_sup = [[] for _ in range(5)]
historial_dir = [[] for _ in range(5)]
historial_x = [[] for _ in range(5)]

rapid_reversals = [0] * 5
plat_air_cycles = [0] * 5

for frame in range(1800): # 30 segundos
    gestor.actualizar()
    for idx, p in enumerate(gestor.personajes):
        ai = gestor.ai_estados[idx]
        sup = p["superficie"]
        direc = ai["direccion"]
        x = p["hitbox"].centerx

        historial_sup[idx].append(sup)
        historial_dir[idx].append(direc)
        historial_x[idx].append(x)

        # Detectar ciclo plataforma -> aire -> plataforma en <= 3 frames
        if len(historial_sup[idx]) >= 3:
            s3, s2, s1 = historial_sup[idx][-3], historial_sup[idx][-2], historial_sup[idx][-1]
            if s3 == "plataforma" and s2 == "aire" and s1 == "plataforma":
                plat_air_cycles[idx] += 1
                plat = p.get("plat_actual")
                plat_str = f"L={plat.left}, R={plat.right}" if plat else "None"
                print(f"[Frame {frame}] Personaje {idx} ({ai['personalidad']}) CICLO BORDE: x={x}, plat=[{plat_str}], dir={direc}")

        # Detectar reversiones consecutivas de direccion (cambio en <= 3 frames)
        if len(historial_dir[idx]) >= 4:
            d4, d3, d2, d1 = historial_dir[idx][-4], historial_dir[idx][-3], historial_dir[idx][-2], historial_dir[idx][-1]
            if (d1 != 0 and d2 != 0 and d1 != d2) or (d2 != 0 and d3 != 0 and d2 != d3):
                # Si cambia frecuentemente
                if d1 == -d2 and d2 == -d3:
                    rapid_reversals[idx] += 1
                    print(f"[Frame {frame}] Personaje {idx} OSCILACION RAPIDA DE DIRECCION: d3={d3}, d2={d2}, d1={d1}, sup={sup}, x={x}")

print("\n--- RESUMEN DIAGNÓSTICO ---")
for idx in range(5):
    print(f"P{idx}: Ciclos Plataforma-Aire-Plataforma = {plat_air_cycles[idx]}, Oscilaciones rápidas de dir = {rapid_reversals[idx]}")
