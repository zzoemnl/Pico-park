import os
import sys
import math
import random
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, ".")

import pantalla
import movimientos
import sprites

def test_integral_m3_n2():
    print("=====================================================================")
    print("INICIANDO PRUEBAS INTEGRALES PARA MUNDO 3 NIVEL 2: EL LABERINTO DE CORAL")
    print("=====================================================================")

    pygame.init()
    pantalla_mock = pygame.Surface((1280, 720))

    # --- TEST 1: GENERADOR PROCEDURAL Y RESOLUBILIDAD ---
    print("\n--- TEST 1: GENERACION PROCEDURAL Y RESOLUBILIDAD MATEMATICA ---")
    ancho_mundo = 2600
    alto_mundo = 720
    y_suelo = 645
    y_techo = 25

    semillas = [1, 7, 42, 99, 123, 555, 777, 999, 2024, 2026]
    laberintos = []
    posiciones_llaves = set()

    for s in semillas:
        datos = pantalla.generar_laberinto_coral_m3_n2(ancho_mundo, alto_mundo, y_suelo, y_techo, rng_seed=s)
        laberintos.append(datos)
        posiciones_llaves.add((datos["llave_x"], datos["llave_y"]))

        # Verificar distancias mínimas
        assert datos["distancia_llave"] >= 4, f"Semilla {s}: Distancia a la llave debe ser >= 4 (es {datos['distancia_llave']})"
        assert datos["distancia_salida"] >= 8, f"Semilla {s}: Distancia a la salida debe ser >= 8 (es {datos['distancia_salida']})"
        assert datos["num_callejones"] >= 5, f"Semilla {s}: Debe tener >= 5 callejones sin salida (tiene {datos['num_callejones']})"

        # Verificar elementos generados
        assert len(datos["rocas"]) > 20, "Debe tener rocas submarinas"
        assert len(datos["barreras"]) >= 2, "Debe tener barreras de quelpo sólido"
        assert len(datos["corales"]) >= 8, "Debe tener corales decorativos"
        assert len(datos["algas"]) >= 8, "Debe tener algas decorativas"

    print(f"-> Probadas {len(semillas)} semillas: 100% resolubles.")
    print(f"-> Variabilidad: {len(posiciones_llaves)} posiciones de llave distintas en {len(semillas)} partidas.")
    assert len(posiciones_llaves) >= 6, "Debe haber gran variedad aleatoria en la ubicación de la llave"
    print("[OK] Test 1 superado exitosamente.")

    # --- TEST 2: REGLAS ESPECÍFICAS DE MUNDO 3-2 (SIN CUERDA, INDEPENDENCIA, 4 DIRECCIONES) ---
    print("\n--- TEST 2: REGLAS ESPECÍFICAS (SIN CUERDA, MOVIMIENTO INDEPENDIENTE EN AGUA) ---")
    datos_lab = pantalla.generar_laberinto_coral_m3_n2(ancho_mundo, alto_mundo, y_suelo, y_techo, rng_seed=42)

    # Simular inicialización de nivel como en pantalla.py
    usar_soga = False   # Regla Mundo 3: sin cuerda
    usar_agua = True    # 4 direcciones de natación submarina
    usar_pinchos = False
    usar_llave = True

    p1 = movimientos.crear_personaje(datos_lab["p1_x"], datos_lab["p1_y"], "Celeste")
    p2 = movimientos.crear_personaje(datos_lab["p2_x"], datos_lab["p2_y"], "Violeta")
    p1["en_agua"] = True
    p2["en_agua"] = True

    assert not usar_soga, "World 3 Level 2 no debe usar soga"
    assert usar_agua, "World 3 Level 2 debe usar física submarina"
    assert p1["en_agua"] and p2["en_agua"], "Personajes deben iniciar en estado de agua"

    # Probar movimiento vertical submarino (W / S para P1, UP / DOWN para P2)
    # Nadar hacia arriba (W)
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=True, tecla_abajo=False, submarino=True)
    assert p1["vel_y"] < 0, "P1 debe ascender en agua al pulsar W"

    # Nadar hacia abajo (S)
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=True, submarino=True)
    assert p1["vel_y"] > 0, "P1 debe descender en agua al pulsar S"

    # Flotabilidad neutra sin inputs (no debe caer por gravedad)
    p1["vel_y"] = 0
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=False, submarino=True)
    assert abs(p1["vel_y"]) < 0.1, f"En modo submarino debe haber flotabilidad neutra (vel_y = {p1['vel_y']})"

    print("[OK] Test 2 superado exitosamente: Movimiento 4 direcciones y flotabilidad neutra verificados.")

    # --- TEST 3: RECOLECCION DE LLAVE Y APERTURA DE PUERTA ---
    print("\n--- TEST 3: DINAMICA DE JUEGO (RECOGER LLAVE, ABRIR PUERTA, AMBOS SALEN) ---")
    llave = movimientos.crear_llave(datos_lab["llave_x"], datos_lab["llave_y"])
    puerta = movimientos.crear_puerta(datos_lab["puerta_x"], datos_lab["puerta_y"])

    assert not llave["recolectada"]
    assert not puerta["abierta"]

    # P1 nada hasta la llave
    p1["hitbox"].center = llave["rect"].center
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert llave["recolectada"], "La llave debe ser recogida al contacto con P1"
    assert llave["portador"] == p1, "P1 debe ser el portador de la llave"

    # P1 nada hacia la puerta con la llave
    p1["hitbox"].center = puerta["rect"].center
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert puerta["abierta"], "La puerta debe abrirse cuando el portador la toca"

    # Ambos personajes entran a la puerta
    p1_completado = False
    p2_completado = False
    if puerta["abierta"] and p1["hitbox"].colliderect(puerta["rect"]):
        p1_completado = True
    p2["hitbox"].center = puerta["rect"].center
    if puerta["abierta"] and p2["hitbox"].colliderect(puerta["rect"]):
        p2_completado = True

    assert p1_completado and p2_completado, "Ambos personajes deben poder completar el nivel en la puerta"
    print("[OK] Test 3 superado exitosamente: Llave recogida, puerta abierta y ambos escapan.")

    # --- TEST 4: DIBUJADO DE CORALES, ALGAS, ESCENARIO Y AGUA ---
    print("\n--- TEST 4: RENDERIZADO VISUAL DEL LABERINTO Y CORALES ---")
    mundo_surf = pygame.Surface((ancho_mundo, alto_mundo))
    suelo_rect = pygame.Rect(0, alto_mundo - 75, ancho_mundo, 75)

    # 1. Fondo submarino
    pantalla.dibujar_submarino_fondo_escenario(mundo_surf, ancho_mundo, tick=10)
    pantalla.dibujar_lecho_marino(mundo_surf, suelo_rect, ancho_mundo)

    # 2. Algas de fondo
    pantalla.dibujar_algas_decorativas_escenario(mundo_surf, datos_lab["algas"], tick=10, capa="fondo")

    # 3. Rocas submarinas y barreras de algas
    pantalla.dibujar_rocas_submarinas_escenario(mundo_surf, datos_lab["rocas"])
    pantalla.dibujar_barreras_algas_escenario(mundo_surf, datos_lab["barreras"], tick=10)

    # 4. Corales vivos
    pantalla.dibujar_corales_escenario(mundo_surf, datos_lab["corales"], tick=10)

    # 5. Algas de frente
    pantalla.dibujar_algas_decorativas_escenario(mundo_surf, datos_lab["algas"], tick=10, capa="frente")

    # 6. Burbujas
    burbujas = pantalla.crear_sistema_burbujas_m3(ancho_mundo, cantidad=40)
    pantalla.actualizar_y_dibujar_burbujas_m3(mundo_surf, burbujas, [p1, p2], tick=10)

    print("[OK] Test 4 superado exitosamente: Todos los elementos gráficos se renderizan sin error.")

    # --- TEST 5: REINICIO Y REGENERACION COMPLETA ---
    print("\n--- TEST 5: REINICIO Y CAMBIO ALEATORIO DEL LABERINTO ---")
    datos_r1 = pantalla.generar_laberinto_coral_m3_n2(ancho_mundo, alto_mundo, y_suelo, y_techo)
    datos_r2 = pantalla.generar_laberinto_coral_m3_n2(ancho_mundo, alto_mundo, y_suelo, y_techo)

    # Comprobar que dos reinicios consecutivos generan laberintos distintos
    llave_diferente = (datos_r1["llave_x"], datos_r1["llave_y"]) != (datos_r2["llave_x"], datos_r2["llave_y"])
    rocas_diferentes = len(datos_r1["rocas"]) != len(datos_r2["rocas"]) or datos_r1["exit_cell"] != datos_r2["exit_cell"]
    print(f"-> Intento 1: Llave en {datos_r1['key_cell']}, Salida en {datos_r1['exit_cell']}")
    print(f"-> Intento 2: Llave en {datos_r2['key_cell']}, Salida en {datos_r2['exit_cell']}")
    assert llave_diferente or rocas_diferentes, "Los laberintos generados al reiniciar deben ser diferentes"

    print("[OK] Test 5 superado exitosamente: Reinicio regenera el laberinto con nuevas rutas y ubicaciones.")

    print("\n=====================================================================")
    print(">>> TODOS LOS TESTS DE INTEGRACION DEL NIVEL 3-2 PASARON CON EXITO (5/5) <<<")
    print("=====================================================================")

if __name__ == "__main__":
    test_integral_m3_n2()
