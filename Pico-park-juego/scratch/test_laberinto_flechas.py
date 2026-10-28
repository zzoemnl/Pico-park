import os
import sys
import pygame
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import pantalla

def _encontrar_camino_bfs(adj, origen, destino):
    if origen == destino:
        return [origen]
    cola = [[origen]]
    visitados = set([origen])
    while cola:
        camino = cola.pop(0)
        nodo = camino[-1]
        for vecino in adj.get(nodo, []):
            if vecino == destino:
                return camino + [vecino]
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(camino + [vecino])
    return [origen, destino]

def generar_flechas_test(adj, start_node, key_cell, exit_node, x_offset, y_techo, w_cell, h_cell):
    camino_llave = _encontrar_camino_bfs(adj, start_node, key_cell)
    camino_salida = _encontrar_camino_bfs(adj, key_cell, exit_node)
    
    flechas = []
    
    # 1. Flechas hacia la llave
    dir_anterior = None
    for i in range(len(camino_llave) - 1):
        curr = camino_llave[i]
        nxt = camino_llave[i + 1]
        
        if nxt[0] > curr[0]: dir_nombre = "derecha"
        elif nxt[0] < curr[0]: dir_nombre = "izquierda"
        elif nxt[1] > curr[1]: dir_nombre = "abajo"
        else: dir_nombre = "arriba"
        
        # Colocar flecha si es inicio, si cambió de dirección, si es intersección o cada 2 pasos
        es_inicio = (i == 0)
        es_giro = (dir_nombre != dir_anterior)
        es_interseccion = len(adj[curr]) >= 3
        
        if es_inicio or es_giro or es_interseccion or (i % 2 == 0):
            cx_min = x_offset + curr[0] * w_cell
            cx_max = x_offset + (curr[0] + 1) * w_cell
            cy_min = y_techo + curr[1] * h_cell
            cy_max = y_techo + (curr[1] + 1) * h_cell
            centro_x = cx_min + w_cell // 2
            centro_y = cy_min + h_cell // 2
            
            if dir_nombre == "derecha":
                fx, fy = cx_max - 50, centro_y
            elif dir_nombre == "izquierda":
                fx, fy = cx_min + 50, centro_y
            elif dir_nombre == "abajo":
                fx, fy = centro_x, cy_max - 40
            else:
                fx, fy = centro_x, cy_min + 40
                
            flechas.append({
                "x": fx, "y": fy,
                "direccion": dir_nombre,
                "tipo": "llave",
                "celda": curr
            })
        dir_anterior = dir_nombre
        
    # 2. Flechas hacia la salida
    dir_anterior = None
    for i in range(len(camino_salida) - 1):
        curr = camino_salida[i]
        nxt = camino_salida[i + 1]
        
        if nxt[0] > curr[0]: dir_nombre = "derecha"
        elif nxt[0] < curr[0]: dir_nombre = "izquierda"
        elif nxt[1] > curr[1]: dir_nombre = "abajo"
        else: dir_nombre = "arriba"
        
        es_inicio = (i == 0)
        es_giro = (dir_nombre != dir_anterior)
        es_interseccion = len(adj[curr]) >= 3
        
        if es_inicio or es_giro or es_interseccion or (i % 2 == 0):
            cx_min = x_offset + curr[0] * w_cell
            cx_max = x_offset + (curr[0] + 1) * w_cell
            cy_min = y_techo + curr[1] * h_cell
            cy_max = y_techo + (curr[1] + 1) * h_cell
            centro_x = cx_min + w_cell // 2
            centro_y = cy_min + h_cell // 2
            
            if dir_nombre == "derecha":
                fx, fy = cx_max - 50, centro_y
            elif dir_nombre == "izquierda":
                fx, fy = cx_min + 50, centro_y
            elif dir_nombre == "abajo":
                fx, fy = centro_x, cy_max - 40
            else:
                fx, fy = centro_x, cy_min + 40
                
            # Evitar flecha duplicada en la misma posición exacta
            if not any(abs(f["x"] - fx) < 20 and abs(f["y"] - fy) < 20 for f in flechas):
                flechas.append({
                    "x": fx, "y": fy,
                    "direccion": dir_nombre,
                    "tipo": "salida",
                    "celda": curr
                })
        dir_anterior = dir_nombre
        
    return flechas

for seed in range(5):
    datos = pantalla.generar_laberinto_oscuro_m3_n4(2600, 720, 645, 25, rng_seed=seed)
    # Reconstruir adj a partir de rocas o calcular dentro de la función
    # Probemos con el generador
    print(f"Seed {seed}: key={datos['key_cell']}, exit={datos['exit_cell']}")
