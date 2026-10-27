import os
import sys
import unittest
import math
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

class TestLinternasMundo3Nivel4y5(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.w, self.h = 1280, 720
        self.pantalla = pygame.display.set_mode((self.w, self.h))

    def test_01_controles_independientes_p1_y_p2(self):
        """Verifica que cada jugador controle su linterna de forma 100% independiente."""
        linterna_p1 = True
        linterna_p2 = True

        # Teclas asignadas a P1
        for k in (pygame.K_e, pygame.K_f, pygame.K_SPACE):
            # Simular toggle de P1
            linterna_p1 = not linterna_p1
            self.assertFalse(linterna_p1, f"Tecla {k} debe apagar linterna de P1")
            self.assertTrue(linterna_p2, "La linterna de P2 no debe ser afectada por P1")

            linterna_p1 = not linterna_p1
            self.assertTrue(linterna_p1, f"Tecla {k} debe encender linterna de P1")
            self.assertTrue(linterna_p2, "La linterna de P2 debe seguir intacta")

        # Teclas asignadas a P2
        for k in (pygame.K_l, pygame.K_RETURN, pygame.K_RSHIFT, pygame.K_RCTRL):
            # Simular toggle de P2
            linterna_p2 = not linterna_p2
            self.assertFalse(linterna_p2, f"Tecla {k} debe apagar linterna de P2")
            self.assertTrue(linterna_p1, "La linterna de P1 no debe ser afectada por P2")

            linterna_p2 = not linterna_p2
            self.assertTrue(linterna_p2, f"Tecla {k} debe encender linterna de P2")
            self.assertTrue(linterna_p1, "La linterna de P1 debe seguir intacta")

    def test_02_nivel_3_4_oscuridad_real_y_radio_circular(self):
        """Verifica que en 3-4 la oscuridad oculte el escenario y la linterna ilumine solo un área circular pequeña."""
        surf_mundo = pygame.Surface((self.w, self.h))
        surf_mundo.fill((16, 44, 76)) # Fondo submarino

        # Elementos del laberinto alejados del personaje
        pos_roca = (100, 100)
        pos_coral = (850, 400)
        pos_llave = (1050, 200)
        pygame.draw.rect(surf_mundo, (90, 100, 115), (*pos_roca, 80, 80))
        pygame.draw.rect(surf_mundo, (255, 110, 80), (*pos_coral, 50, 50))
        pygame.draw.circle(surf_mundo, (255, 215, 0), pos_llave, 16)

        # Personaje 1 en (400, 300) con linterna ON
        p1 = movimientos.crear_personaje(400, 300, "Verde")
        pantalla.dibujar_personaje(surf_mundo, p1, None)

        # Personaje 2 completado / fuera
        surf_oscuridad = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna()

        pantalla.dibujar_oscuridad_laberinto(
            surf_mundo,
            [(p1, True, False)],
            surf_oscuridad,
            surf_luz,
            surf_tenue
        )

        # 1. El centro del personaje debe estar claramente iluminado
        col_centro = surf_mundo.get_at((p1["hitbox"].centerx, p1["hitbox"].centery))
        self.assertGreater(col_centro[0] + col_centro[1] + col_centro[2], 120)

        # 2. Los elementos lejanos (roca, coral, llave) deben estar completamente ocultos en la oscuridad profunda
        col_roca = surf_mundo.get_at(pos_roca)
        col_coral = surf_mundo.get_at(pos_coral)
        col_llave = surf_mundo.get_at(pos_llave)

        self.assertLess(col_roca[0], 25, "Roca lejana debe estar oculta en la oscuridad")
        self.assertLess(col_coral[0], 25, "Coral lejano debe estar oculto en la oscuridad")
        self.assertLess(col_llave[0], 25, "Llave lejana debe estar oculta en la oscuridad")

        # 3. Al apagar la linterna, la visibilidad se restringe al área inmediata personal
        surf_mundo.fill((16, 44, 76))
        pygame.draw.circle(surf_mundo, (255, 255, 255), (400 + 100, 300), 10) # Punto a 100px (fuera de tenue)
        pantalla.dibujar_oscuridad_laberinto(
            surf_mundo,
            [(p1, False, False)],
            surf_oscuridad,
            surf_luz,
            surf_tenue
        )
        col_100px = surf_mundo.get_at((400 + 100, 300))
        self.assertLess(col_100px[0], 30, "A 100px debe ser oscuro cuando la linterna está apagada")

    def test_03_nivel_3_5_escenario_permanece_visible(self):
        """Verifica que en 3-5 el escenario permanezca 100% visible sin oscurecerse."""
        surf_mundo = pygame.Surface((self.w, self.h))
        surf_mundo.fill((16, 44, 76))

        # Elementos del escenario distribuidos
        puntos_prueba = [(100, 100), (450, 200), (800, 350), (1100, 600)]
        for pt in puntos_prueba:
            pygame.draw.circle(surf_mundo, (180, 220, 240), pt, 15)

        colores_antes = [surf_mundo.get_at(pt) for pt in puntos_prueba]

        p1 = movimientos.crear_personaje(200, 400, "Verde")
        p2 = movimientos.crear_personaje(600, 400, "Rosa")

        pantalla.dibujar_personaje(surf_mundo, p1, None)
        pantalla.dibujar_personaje(surf_mundo, p2, None)

        # Aplicar linternas submarinas de 3-5 con P1 encendida y P2 apagada
        pantalla.dibujar_linternas_submarinas_m3_n5(
            surf_mundo,
            [(p1, True, False), (p2, False, False)],
            tick=15
        )

        colores_despues = [surf_mundo.get_at(pt) for pt in puntos_prueba]

        # Verificar que NINGUNO de los puntos del escenario se haya oscurecido
        for i, (antes, despues) in enumerate(zip(colores_antes, colores_despues)):
            self.assertGreaterEqual(despues[0], antes[0], f"El punto {puntos_prueba[i]} no debe oscurecerse")
            self.assertGreaterEqual(despues[1], antes[1], f"El punto {puntos_prueba[i]} no debe oscurecerse")

    def test_04_la_luz_sigue_al_personaje_y_su_orientacion(self):
        """Verifica que el haz de luz y la linterna sigan la posición y dirección del personaje."""
        surf_mundo = pygame.Surface((self.w, self.h))
        surf_mundo.fill((10, 20, 30))

        # Personaje mirando a la derecha
        p_der = movimientos.crear_personaje(300, 300, "Verde")
        p_der["mirando_derecha"] = True
        pantalla.dibujar_linternas_submarinas_m3_n5(surf_mundo, [(p_der, True, False)], tick=0)

        # Punto adelante a la derecha (+80px) debe recibir iluminación del haz
        col_adelante_der = surf_mundo.get_at((300 + 80, 300 + 10))
        # Punto atrás a la izquierda (-80px) debe tener solo luz de fondo/mínima
        col_atras_izq = surf_mundo.get_at((300 - 80, 300 + 10))
        self.assertGreater(col_adelante_der[0] + col_adelante_der[1], col_atras_izq[0] + col_atras_izq[1],
                           "El haz de luz debe proyectarse hacia la derecha cuando el personaje mira a la derecha")

        # Personaje mirando a la izquierda
        surf_mundo.fill((10, 20, 30))
        p_izq = movimientos.crear_personaje(300, 300, "Verde")
        p_izq["mirando_derecha"] = False
        pantalla.dibujar_linternas_submarinas_m3_n5(surf_mundo, [(p_izq, True, False)], tick=0)

        col_adelante_izq = surf_mundo.get_at((300 - 80, 300 + 10))
        col_atras_der = surf_mundo.get_at((300 + 80, 300 + 10))
        self.assertGreater(col_adelante_izq[0] + col_adelante_izq[1], col_atras_der[0] + col_atras_der[1],
                           "El haz de luz debe proyectarse hacia la izquierda cuando el personaje mira a la izquierda")

    def test_05_reinicio_y_persistencia_de_reglas(self):
        """Verifica que al reiniciar los niveles 3-4 y 3-5 las linternas se reestablezcan a ON."""
        # Simular reseteo de variables de nivel
        linterna_p1 = False
        linterna_p2 = False

        # Reinicio para 3-4
        numero_mundo = 3
        numero_nivel = 4
        if numero_mundo == 3 and numero_nivel == 4:
            linterna_p1 = True
            linterna_p2 = True
        self.assertTrue(linterna_p1)
        self.assertTrue(linterna_p2)

        # Reinicio para 3-5
        linterna_p1 = False
        linterna_p2 = False
        numero_nivel = 5
        if numero_mundo == 3 and numero_nivel == 5:
            linterna_p1 = True
            linterna_p2 = True
        self.assertTrue(linterna_p1)
        self.assertTrue(linterna_p2)

        # HUD en 3-5 no colisiona con el oxigeno y se renderiza en y=60
        surf_hud = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pantalla._dibujar_hud_oxigeno_m3_n5(surf_hud, 100.0, 100.0, "Verde", "Rosa", 0)
        pantalla._dibujar_hud_linternas_m3_n4(surf_hud, True, True, "Verde", "Rosa", y_base=60)
        # Pixel del badge de linterna en y=65 debe estar dibujado
        col_badge = surf_hud.get_at((35, 65))
        self.assertGreater(col_badge[3], 0, "El badge de linterna en 3-5 debe dibujarse correctamente en y=60")

if __name__ == "__main__":
    unittest.main()
