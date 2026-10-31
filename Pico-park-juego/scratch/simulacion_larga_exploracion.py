import os
import sys
import time
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from personajes_menu import GestorPersonajesMenu


def simular_exploracion():
    print("Iniciando simulación de larga duración (6000 frames = 100 segundos de juego)...")
    gestor = GestorPersonajesMenu(1280, 720)

    zonas_visitadas = {i: set() for i in range(5)}
    conteo_superficies = {i: {} for i in range(5)}
    conteo_acciones = {}
    vibraciones = 0
    anomalias_movimiento = 0

    t_inicio = time.time()
    total_frames = 6000

    for f in range(total_frames):
        pos_anteriores = [(p["hitbox"].x, p["hitbox"].y) for p in gestor.personajes]
        gestor.actualizar()

        for i, p in enumerate(gestor.personajes):
            sup = p["superficie"]
            plat = p.get("plat_actual")
            if sup == "plataforma" and plat:
                idx_plat = gestor.plataformas.index(plat) + 1
                zona = f"P{idx_plat}"
            else:
                zona = sup

            zonas_visitadas[i].add(zona)
            conteo_superficies[i][zona] = conteo_superficies[i].get(zona, 0) + 1

            ai = gestor.ai_estados[i]
            act = ai.get("estado", "desconocido")
            conteo_acciones[act] = conteo_acciones.get(act, 0) + 1

            dx = abs(p["hitbox"].x - pos_anteriores[i][0])
            dy = abs(p["hitbox"].y - pos_anteriores[i][1])
            if dx > 24 or dy > 24:
                anomalias_movimiento += 1

    t_total = time.time() - t_inicio
    fps = total_frames / max(0.001, t_total)

    print("\n--- RESULTADOS DE EXPLORACIÓN EXTENSA ---")
    print(f"Frames procesados: {total_frames} ({t_total:.2f}s, {fps:.1f} FPS)")
    print(f"Anomalías o teletransportes bruscos: {anomalias_movimiento}")
    print(f"Distribución general de estados: {conteo_acciones}")

    nombres = ["P1 (Explorador)", "P2 (Saltarín)", "P3 (Curioso)", "P4 (Tranquilo)", "P5 (Juguetón)"]
    for i in range(5):
        print(f"\n{nombres[i]}:")
        print(f"  Zonas visitadas: {sorted(list(zonas_visitadas[i]))}")
        print(f"  Tiempo por zona: {conteo_superficies[i]}")

    # Aserciones de calidad
    assert anomalias_movimiento == 0, f"Se detectaron {anomalias_movimiento} anomalías de movimiento"
    for i in range(5):
        assert len(zonas_visitadas[i]) >= 2, f"Personaje {i} no exploró suficientes zonas: {zonas_visitadas[i]}"

    print("\n[ÉXITO] Simulación de exploración completada con éxito impecable.")


if __name__ == "__main__":
    simular_exploracion()
