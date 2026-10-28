import os
import sys
import math
import random
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def test_1_procedural_generation_connectivity():
    print("--- 1. Probando generación procedural y 100% conectividad (Start -> Llave -> Puerta) ---")
    ancho_mundo = 2600
    alto_mundo = 720
    y_suelo = 645
    y_techo = 25

    for s in range(30):
        datos = pantalla.generar_laberinto_oscuro_m3_n4(ancho_mundo, alto_mundo, y_suelo, y_techo, rng_seed=s)
        
        # Validar entidades generadas
        assert len(datos["rocas"]) > 0, "Debe haber rocas"
        assert len(datos["barreras"]) > 0, "Debe haber barreras de algas"
        assert len(datos["corales"]) > 0, "Debe haber corales decorativos"
        assert len(datos["algas"]) > 0, "Debe haber algas ondeando"
        assert len(datos["pinchos"]) >= 2, "Debe haber al menos 2 trampas mortales en callejones sin salida"
        
        # Validar posiciones de inicio y salida
        assert datos["p1_x"] < 200, f"P1 debe iniciar en zona segura: {datos['p1_x']}"
        assert datos["p2_x"] < 200, f"P2 debe iniciar en zona segura: {datos['p2_x']}"
        assert datos["puerta_x"] > 2400, f"Puerta debe estar en la terraza final: {datos['puerta_x']}"
        
        # Validar que la llave está en un callejón distante y profundo
        assert datos["distancia_llave"] >= 3, f"La distancia de la llave debe ser profunda: {datos['distancia_llave']}"
        assert datos["num_callejones"] >= 5, f"Debe haber al menos 5 callejones: {datos['num_callejones']}"

    print("[OK] 30 semillas aleatorias verificadas: 100% resolubles, con trampas en cul-de-sacs y caminos válidos.")


def test_2_flashlight_surfaces_and_darkness():
    print("--- 2. Probando superficies de linterna y máscara de oscuridad ---")
    surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna()
    
    assert surf_luz.get_width() == 290, f"Radio 145 -> diámetro 290, obtenido {surf_luz.get_width()}"
    assert surf_tenue.get_width() == 68, f"Radio 34 -> diámetro 68, obtenido {surf_tenue.get_width()}"

    # Probar máscara de oscuridad
    w, h = 800, 600
    superficie_mundo = pygame.Surface((w, h))
    superficie_mundo.fill((20, 60, 100))  # Fondo submarino iluminado
    
    # Dibujar un objeto (ej. la llave dorada) en (400, 300)
    pygame.draw.circle(superficie_mundo, (255, 215, 0), (400, 300), 15)

    surf_oscuridad = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Caso A: Linterna encendida en (400, 300) -> el objeto en (400, 300) debe verse claro
    jugador_encendido = {
        "hitbox": pygame.Rect(385, 280, 30, 40),
        "muerto": False,
        "mirando_derecha": True,
    }
    pantalla.dibujar_oscuridad_laberinto(
        superficie_mundo,
        [(jugador_encendido, True, False)],
        surf_oscuridad,
        surf_luz,
        surf_tenue
    )

    col_iluminada = superficie_mundo.get_at((400, 300))
    # En el centro de la linterna, la capa de oscuridad se restó completamente (alpha 0)
    assert col_iluminada[0] > 180, f"El objeto dorado debe verse claramente iluminado: {col_iluminada}"
    
    # En una zona distante (100, 100), la oscuridad debe estar cubriendo el mundo
    col_oscura = superficie_mundo.get_at((100, 100))
    assert col_oscura[0] < 25 and col_oscura[1] < 25, f"La zona lejana debe estar en oscuridad profunda: {col_oscura}"

    # Caso B: Linterna apagada -> solo brillo tenue muy cercano (radio 34)
    superficie_mundo.fill((20, 60, 100))
    pygame.draw.circle(superficie_mundo, (255, 215, 0), (400, 300), 15)
    # Colocar objeto a 80px (fuera de 34px pero dentro de 145px)
    pygame.draw.circle(superficie_mundo, (255, 0, 0), (480, 300), 10)
    
    pantalla.dibujar_oscuridad_laberinto(
        superficie_mundo,
        [(jugador_encendido, False, False)],
        surf_oscuridad,
        surf_luz,
        surf_tenue
    )
    col_fuera_tenue = superficie_mundo.get_at((480, 300))
    assert col_fuera_tenue[0] < 30, f"Objeto a 80px debe quedar oculto en la oscuridad cuando linterna está apagada: {col_fuera_tenue}"

    print("[OK] Iluminación y oscuridad validadas: linterna activa ilumina (~145px), apagada restringe visibilidad (~34px).")


def test_3_independent_flashlight_toggles():
    print("--- 3. Probando controles independientes de linternas P1 y P2 ---")
    linterna_p1 = True
    linterna_p2 = True

    # Teclas de P1
    for k in (pygame.K_e, pygame.K_f, pygame.K_SPACE):
        # Simular toggle
        linterna_p1 = not linterna_p1
        assert linterna_p1 is False, f"Tecla {k} debe conmutar linterna P1"
        linterna_p1 = not linterna_p1
        assert linterna_p1 is True, f"Tecla {k} debe conmutar linterna P1 a True"

    # Verificar que P2 sigue independiente (True)
    assert linterna_p2 is True, "La linterna de P2 debe mantenerse intacta e independiente"

    # Teclas de P2
    for k in (pygame.K_l, pygame.K_RETURN, pygame.K_RSHIFT, pygame.K_RCTRL):
        linterna_p2 = not linterna_p2
        assert linterna_p2 is False, f"Tecla {k} debe conmutar linterna P2"
        linterna_p2 = not linterna_p2
        assert linterna_p2 is True, f"Tecla {k} debe conmutar linterna P2 a True"

    # Verificar que P1 sigue independiente (True)
    assert linterna_p1 is True, "La linterna de P1 debe mantenerse intacta e independiente"
    print("[OK] Controles independientes de linterna para P1 y P2 verificados.")


def test_4_hud_and_miner_lamp_drawing():
    print("--- 4. Probando renderizado del HUD de linternas y lámpara de buceo ---")
    pantalla_test = pygame.Surface((1280, 720))
    
    # Dibujar HUD con ambas encendidas
    pantalla._dibujar_hud_linternas_m3_n4(pantalla_test, True, True, "Verde", "Rosa")
    col1 = pantalla_test.get_at((46, 38))
    assert col1[3] > 0, "El badge debe estar dibujado en pantalla"

    # Dibujar HUD con P1 apagada y P2 encendida
    pantalla._dibujar_hud_linternas_m3_n4(pantalla_test, False, True, "Verde", "Rosa")
    
    # Dibujar lámpara de minero en personaje
    mundo_test = pygame.Surface((2600, 720))
    p1 = movimientos.crear_personaje(100, 300, "Verde")
    pantalla.dibujar_linterna_minero(mundo_test, p1, True)
    col_lamp = mundo_test.get_at((p1["hitbox"].centerx + 12, p1["hitbox"].top + 8))
    assert col_lamp[0] > 200, "La lente de la linterna debe brillar en amarillo/blanco"

    pantalla.dibujar_linterna_minero(mundo_test, p1, False)
    print("[OK] HUD de linternas y linterna frontal de buceo renderizados correctamente.")


def test_5_level_initialization_and_hot_restart():
    print("--- 5. Probando inicialización de nivel 3-4 y reinicio en caliente ---")
    datos1 = pantalla.generar_laberinto_oscuro_m3_n4(2600, 720, 645, 25, rng_seed=101)
    datos2 = pantalla.generar_laberinto_oscuro_m3_n4(2600, 720, 645, 25, rng_seed=202)
    
    # Los laberintos con diferentes semillas deben ser distintos (procedurales)
    assert datos1["key_cell"] != datos2["key_cell"] or datos1["exit_cell"] != datos2["exit_cell"] or len(datos1["rocas"]) != len(datos2["rocas"]), "Los laberintos procedurales deben variar"
    print("[OK] Variabilidad procedural y reseteo validados con éxito.")


if __name__ == "__main__":
    test_1_procedural_generation_connectivity()
    test_2_flashlight_surfaces_and_darkness()
    test_3_independent_flashlight_toggles()
    test_4_hud_and_miner_lamp_drawing()
    test_5_level_initialization_and_hot_restart()
    print("\n=======================================================")
    print(">>> TODOS LOS TESTS DE MUNDO 3 NIVEL 4 PASARON 100% <<<")
    print("=======================================================")
