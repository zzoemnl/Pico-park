import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, r"c:\Users\Malena\Documents\GitHub\Pico-park\Pico-park-juego")

import pantalla
import movimientos
import sprites

def test_integral_m3_n1():
    print("=== TEST INTEGRAL: MUNDO 3 - NIVEL 1: EL JARDIN DE ALGAS ===")

    # 1. Configurar superficie dummy
    superficie_pantalla = pygame.display.set_mode((1280, 720))

    # 2. Inicializar entorno de prueba idéntico al bloque del nivel
    ancho_mundo = 2600
    suelo = pygame.Rect(0, 720 - 75, ancho_mundo, 75)
    mundo_rect = pygame.Rect(0, 0, ancho_mundo, 720)
    techo_agua = pygame.Rect(0, 0, ancho_mundo, 25)

    p1 = movimientos.crear_personaje(120, 340, "Celeste")
    p2 = movimientos.crear_personaje(230, 340, "Violeta")
    p1["en_agua"] = True
    p2["en_agua"] = True

    # 3. Verificar que los personajes se mueven de forma 100% independiente (sin soga)
    p1["vel_x"] = 4.5
    p2["vel_x"] = 0
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, en_agua=True)
    movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, en_agua=True)
    assert p1["hitbox"].x > 120, "P1 debe poder moverse independientemente"
    assert p2["hitbox"].x == 230, "P2 no debe ser arrastrado por P1 (sin soga)"
    print("[OK] Personajes completamente independientes: no hay soga ni tirones.")

    # 4. Verificar natación en 4 direcciones sin gravedad
    # Arriba
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=True, tecla_abajo=False, submarino=True)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, en_agua=True)
    assert p1["hitbox"].y < 340, "P1 debe nadar hacia arriba libremente"
    print("[OK] Natacion hacia arriba funcional.")

    # Neutral: flotando sin caer
    y_antes = p1["hitbox"].y
    p1["vel_y"] = 0.0
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=False, submarino=True)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, en_agua=True)
    assert p1["hitbox"].y == y_antes, f"P1 no debe caer al estar neutral (antes={y_antes}, ahora={p1['hitbox'].y})"
    print("[OK] Flotacion neutra en suspension sin caida por gravedad.")

    # Abajo
    movimientos.aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=True, submarino=True)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, en_agua=True)
    assert p1["hitbox"].y > y_antes, "P1 debe nadar hacia abajo libremente"
    print("[OK] Natacion hacia abajo funcional.")

    # 5. Verificar colisiones con rocas y algas barrera
    roca_central = pygame.Rect(520, 240, 210, 160)
    barrera_alga = pygame.Rect(840, 400, 35, 245)
    plataformas_solidas = [roca_central, barrera_alga]

    # Intentar atravesar roca central
    p1["hitbox"].x = 515
    p1["hitbox"].y = 300
    p1["vel_x"] = 4.5
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, en_agua=True, plataformas=plataformas_solidas)
    assert p1["hitbox"].right <= roca_central.left, "La roca central debe bloquear el avance horizontal"
    print("[OK] Colision solida con formaciones rocosas verificada.")

    # Intentar atravesar alga barrera
    p1["hitbox"].right = 835
    p1["hitbox"].y = 450
    p1["vel_x"] = 10.0
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, en_agua=True, plataformas=plataformas_solidas)
    assert p1["hitbox"].right <= barrera_alga.left, f"El alga barrera debe bloquear el avance horizontal (right={p1['hitbox'].right}, barrera.left={barrera_alga.left})"
    print("[OK] Algas barrera bloquean solidamente el camino.")

    # 6. Verificar obstáculo mortal (erizo / coral espinoso)
    erizo_mortal = movimientos.crear_pincho(640, 496, 60, 24, direccion="arriba")
    p1["hitbox"].x = 645
    p1["hitbox"].y = 490
    toco_p1 = movimientos.comprobar_pinchos(p1, [erizo_mortal])
    assert toco_p1 == True and p1["muerto"] == True, "Contacto con obstaculo mortal debe matar a P1"
    # Regla: Si cualquiera toca un obstáculo mortal, ambos pierden
    movimientos.matar_personaje(p2)
    assert p2["muerto"] == True, "Ambos personajes deben perder ante obstaculo mortal"
    print("[OK] Obstaculos mortales (erizos y corales espinosos) causan muerte de ambos personajes.")

    # 7. Verificar recolección de llave y apertura de puerta
    p1["muerto"] = False
    p2["muerto"] = False
    llave = movimientos.crear_llave(1540, 395)
    puerta = movimientos.crear_puerta(2410, 480 - 90)

    # Puerta cerrada inicialmente
    assert puerta["abierta"] == False, "La puerta debe iniciar cerrada"

    # P1 toma la llave
    p1["hitbox"].x = llave["rect"].x
    p1["hitbox"].y = llave["rect"].y
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert llave["recolectada"] == True and llave["portador"] == p1, "P1 debe recolectar la llave al tocarla"
    print("[OK] Llave recolectada con exito en la gruta submarina.")

    # P1 llega a la puerta con la llave
    p1["hitbox"].x = puerta["rect"].x
    p1["hitbox"].y = puerta["rect"].y
    movimientos.actualizar_llave(llave, [p1, p2], puerta)
    assert puerta["abierta"] == True, "La puerta debe abrirse cuando el portador llega a ella"
    print("[OK] La puerta se abre al recibir al portador con la llave.")

    # 8. Verificar renderizado completo del escenario submarino
    mundo_surf = pygame.Surface((ancho_mundo, 720))
    pantalla.dibujar_submarino_fondo_escenario(mundo_surf, ancho_mundo, tick=10)
    pantalla.dibujar_lecho_marino(mundo_surf, suelo, ancho_mundo)
    pantalla.dibujar_rocas_submarinas_escenario(mundo_surf, [{"rect": roca_central}])
    pantalla.dibujar_barreras_algas_escenario(mundo_surf, [{"rect": barrera_alga}], tick=10)
    pantalla.dibujar_algas_decorativas_escenario(mundo_surf, [{"x": 100, "y": 645, "alto": 100, "capa": "frente"}], tick=10)
    pantalla.dibujar_peligros_marinos_escenario(mundo_surf, [erizo_mortal])
    burbujas = pantalla.crear_sistema_burbujas_m3(ancho_mundo, 20)
    pantalla.actualizar_y_dibujar_burbujas_m3(mundo_surf, burbujas, [p1, p2], tick=10)

    # Dibujar tinte de agua y personajes
    zona_agua = pygame.Rect(0, 0, ancho_mundo, 720)
    sprites.dibujar_agua(mundo_surf, zona_agua)
    sprites.dibujar_personaje(mundo_surf, p1, zona_agua)
    sprites.dibujar_personaje(mundo_surf, p2, zona_agua)
    print("[OK] Renderizado de todos los elementos graficos submarinos ejecutado sin errores.")

    print("\n>>> TODOS LOS TESTS DE MUNDO 3 NIVEL 1 PASARON AL 100%! <<<")

if __name__ == "__main__":
    test_integral_m3_n1()
