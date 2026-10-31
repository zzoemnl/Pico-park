import os
import sys
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from personajes_menu import GestorPersonajesMenu

def test_simulacion_trepada():
    gestor = GestorPersonajesMenu()
    
    eventos_trepada = {i: [] for i in range(5)}
    llegadas_techo = {i: 0 for i in range(5)}
    llegadas_suelo_desde_pared = {i: 0 for i in range(5)}
    llegadas_plat_desde_pared = {i: 0 for i in range(5)}
    tiempo_por_superficie = {i: {"suelo": 0, "plataforma": 0, "pared_izq": 0, "pared_der": 0, "techo": 0, "aire": 0} for i in range(5)}
    
    superficies_previas = [gestor.personajes[i]["superficie"] for i in range(5)]
    
    # Interceptar _al_tocar_pared para contar decisiones
    decisiones_cont = {i: {} for i in range(5)}
    orig_al_tocar_pared = gestor._al_tocar_pared
    def wrap_al_tocar_pared(idx, lado):
        prev_act_len = len(gestor.ai_estados[idx].get("historial_acciones", []))
        orig_al_tocar_pared(idx, lado)
        hist = gestor.ai_estados[idx].get("historial_acciones", [])
        if len(hist) > prev_act_len or hist:
            ultima = hist[-1]
            decisiones_cont[idx][ultima] = decisiones_cont[idx].get(ultima, 0) + 1
    gestor._al_tocar_pared = wrap_al_tocar_pared

    # Simular 7200 frames (2 minutos)
    for frame in range(7200):
        for i in range(5):
            p = gestor.personajes[i]
            ai = gestor.ai_estados[i]
            sup = p["superficie"]
            prev = superficies_previas[i]
            tiempo_por_superficie[i][sup] = tiempo_por_superficie[i].get(sup, 0) + 1
            
            # Transición a trepada
            if sup in ("pared_izq", "pared_der") and prev not in ("pared_izq", "pared_der"):
                eventos_trepada[i].append((frame, prev, sup, ai.get("direccion")))
            
            # Transición de pared al techo
            if prev in ("pared_izq", "pared_der") and sup == "techo":
                llegadas_techo[i] += 1
                
            # Transición de pared al suelo
            if prev in ("pared_izq", "pared_der") and sup == "suelo":
                llegadas_suelo_desde_pared[i] += 1
                
            # Transición de pared a plataforma
            if prev in ("pared_izq", "pared_der") and sup == "plataforma":
                llegadas_plat_desde_pared[i] += 1
                
            superficies_previas[i] = sup
            
        gestor.actualizar()
        
    print("=== RESULTADOS DE SIMULACION DE 7200 FRAMES (2 MINUTOS) ===")
    for i in range(5):
        print(f"\n--- Personaje {i} ({gestor.colores[i]} - {gestor.ai_estados[i]['personalidad']}) ---")
        print(f"  Veces que inicio trepada: {len(eventos_trepada[i])}")
        print(f"  Llegadas al techo: {llegadas_techo[i]}")
        print(f"  Llegadas al suelo desde pared: {llegadas_suelo_desde_pared[i]}")
        print(f"  Llegadas a plataforma desde pared: {llegadas_plat_desde_pared[i]}")
        print(f"  Decisiones al tocar pared: {decisiones_cont[i]}")
        print(f"  Tiempo por superficie (frames): {tiempo_por_superficie[i]}")

if __name__ == "__main__":
    test_simulacion_trepada()
