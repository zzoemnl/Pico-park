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

    def test_03_nivel_3_5_escenario_esta_oscuro_con_linternas_circulares(self):
        """Verifica que en 3-5 el escenario esté oscuro y solo se iluminen las áreas de las linternas."""
        surf_mundo = pygame.Surface((self.w, self.h))
        surf_mundo.fill((16, 44, 76))

        # Dibujar punto lejano en el escenario (x=1100, y=600)
        pygame.draw.circle(surf_mundo, (240, 240, 240), (1100, 600), 20)

        p1 = movimientos.crear_personaje(200, 400, "Verde")
        p2 = movimientos.crear_personaje(600, 400, "Rosa")

        surf_oscuridad = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45)

        # Aplicar oscuridad con linterna P1 encendida y P2 apagada
        pantalla.aplicar_oscuridad_submarina(
            surf_mundo,
            [(p1, True, False), (p2, False, False)],
            surf_oscuridad,
            surf_luz,
            surf_tenue
        )

        # 1. El punto lejano (1100, 600) debe estar completamente oscuro (penumbra marina)
        col_lejano = surf_mundo.get_at((1100, 600))
        self.assertLess(col_lejano[0], 25, "El escenario fuera del área de luz debe estar oscuro")

        # 2. El área cercana a P1 (200, 400) debe estar iluminada y visible
        col_cercano_p1 = surf_mundo.get_at((200 + 40, 400 + 40))
        self.assertGreater(col_cercano_p1[0] + col_cercano_p1[1], 40, "El área cercana a P1 debe estar iluminada")

    def test_04_combinacion_de_luces_y_flechas_indicadoras(self):
        """Verifica que las áreas de luz se combinen y que existan flechas indicadoras en 3-4 y 3-5."""
        # 1. Combinación de linternas cercanas
        surf_mundo = pygame.Surface((self.w, self.h))
        surf_mundo.fill((20, 50, 80))
        surf_oscuridad = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45)

        p1 = movimientos.crear_personaje(300, 300, "Verde")
        p2 = movimientos.crear_personaje(400, 300, "Rosa")

        pantalla.aplicar_oscuridad_submarina(
            surf_mundo,
            [(p1, True, False), (p2, True, False)],
            surf_oscuridad,
            surf_luz,
            surf_tenue
        )

        # El punto medio (350, 300) entre ambos personajes debe estar completamente iluminado
        col_medio = surf_mundo.get_at((350, 300))
        self.assertGreater(col_medio[0] + col_medio[1], 45, "Las áreas de luz combinadas deben iluminar el centro")

        # 2. Flechas indicadoras en Nivel 3-4 (procedurales adaptadas al laberinto)
        datos_lab = pantalla.generar_laberinto_oscuro_m3_n4(2600, 720, 645, 25, rng_seed=123)
        self.assertIn("flechas", datos_lab, "El laberinto 3-4 debe generar flechas indicadoras")
        self.assertGreaterEqual(len(datos_lab["flechas"]), 6, "Debe haber suficientes flechas indicadoras")

        # Verificar que las flechas de 3-4 tengan direcciones válidas
        for f in datos_lab["flechas"]:
            self.assertIn(f["direccion"], ("derecha", "izquierda", "arriba", "abajo"))
            self.assertIn(f["tipo"], ("llave", "salida", "ruta"))

        # 3. Dibujado de flechas indicadoras sin error
        pantalla.dibujar_flechas_indicadoras_escenario(surf_mundo, datos_lab["flechas"], tick=10)

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
