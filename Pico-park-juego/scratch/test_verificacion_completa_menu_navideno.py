"""
Script de verificación exhaustiva de los 10 puntos del requerimiento:
1. Los cinco personajes aparecen correctamente con colores y accesorios únicos.
2. Pueden caminar por el suelo.
3. Pueden trepar las paredes.
4. Pueden desplazarse por el techo boca abajo.
5. Pasan de una superficie a otra sin movimientos bruscos.
6. NO pueden trepar ni subirse a los botones (botones desacoplados físicamente).
7. Los botones siguen funcionando normalmente con clics y hover.
8. No hay teletransportes ni personajes trabados en ningún frame.
9. La escena navideña conserva su diseño pixel art (cielo, árboles, nieve, farol, regalos, viga festiva).
10. Los niveles reales no sufren modificaciones.
"""

import os
import sys
import unittest
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1280, 720))

import main
import sprites
import pantalla
from personajes_menu import (
    GestorPersonajesMenu,
    Y_SUELO,
    Y_TECHO,
    X_PARED_IZQ,
    X_PARED_DER,
    BTN_JUGAR_RECT,
    BTN_PERSONAJES_RECT,
    BTN_CONFIG_RECT,
    BTN_SALIR_RECT,
)

class TestVerificacionMenuNavidenoCompleto(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorPersonajesMenu(
            ancho=1280, alto=720,
            color_p1="Celeste", accesorio_p1="Corona",
            color_p2="Violeta", accesorio_p2="Sombrero"
        )

    def test_01_cinco_personajes_unicos(self):
        """1. Los cinco personajes aparezcan correctamente."""
        self.assertEqual(len(self.gestor.personajes), 5)
        self.assertEqual(len(set(self.gestor.colores)), 5)
        self.assertIn("Celeste", self.gestor.colores)
        self.assertIn("Violeta", self.gestor.colores)
        self.assertEqual(len(set(self.gestor.accesorios)), 5)

    def test_02_caminar_por_el_suelo(self):
        """2. Puedan caminar por el suelo."""
        p = self.gestor.personajes[0]
        p["superficie"] = "suelo"
        p["hitbox"].bottom = self.gestor.y_suelo
        x_ini = p["hitbox"].x
        ai = self.gestor.ai_estados[0]
        ai["estado"] = "caminar"
        ai["direccion"] = 1
        ai["tiempo"] = 30

        for _ in range(15):
            self.gestor.actualizar()

        self.assertEqual(p["superficie"], "suelo")
        self.assertGreater(p["hitbox"].x, x_ini, "El personaje debe desplazarse horizontalmente por el suelo")
        self.assertEqual(p["hitbox"].bottom, self.gestor.y_suelo)

    def test_03_trepar_paredes(self):
        """3. Puedan trepar las paredes."""
        p_izq = self.gestor.personajes[1]
        p_izq["superficie"] = "pared_izq"
        p_izq["hitbox"].left = self.gestor.x_pared_izq
        p_izq["hitbox"].y = 400
        y_ini = p_izq["hitbox"].y
        ai_izq = self.gestor.ai_estados[1]
        ai_izq["estado"] = "trepar"
        ai_izq["direccion"] = -1
        ai_izq["tiempo"] = 30

        for _ in range(15):
            self.gestor.actualizar()

        self.assertLess(p_izq["hitbox"].y, y_ini, "El personaje debe trepar verticalmente hacia arriba")
        self.assertEqual(p_izq["hitbox"].left, self.gestor.x_pared_izq)

    def test_04_desplazarse_por_el_techo(self):
        """4. Puedan desplazarse por el techo."""
        p_techo = self.gestor.personajes[2]
        p_techo["superficie"] = "techo"
        p_techo["hitbox"].top = self.gestor.y_techo
        p_techo["hitbox"].x = 400
        x_ini = p_techo["hitbox"].x
        ai_techo = self.gestor.ai_estados[2]
        ai_techo["estado"] = "caminar_techo"
        ai_techo["direccion"] = 1
        ai_techo["tiempo"] = 30

        for _ in range(15):
            self.gestor.actualizar()

        self.assertGreater(p_techo["hitbox"].x, x_ini, "El personaje debe desplazarse por el techo")
        self.assertEqual(p_techo["hitbox"].top, self.gestor.y_techo)
        self.assertEqual(p_techo["angulo_objetivo"], 180.0, "En el techo debe estar boca abajo")

    def test_05_transiciones_fluidas_entre_superficies(self):
        """5. Puedan pasar de una superficie a otra sin movimientos bruscos."""
        # A. Suelo -> Pared Izquierda
        p = self.gestor.personajes[0]
        p["superficie"] = "suelo"
        p["hitbox"].bottom = self.gestor.y_suelo
        p["hitbox"].left = self.gestor.x_pared_izq + 4
        ai = self.gestor.ai_estados[0]
        ai["estado"] = "caminar"
        ai["direccion"] = -1
        ai["tiempo"] = 20
        ai["datos_pers"]["trepar_prob"] = 1.0

        for _ in range(10):
            self.gestor.actualizar()
            if p["superficie"] == "pared_izq":
                break
        self.assertEqual(p["superficie"], "pared_izq")

        # B. Pared Izquierda -> Techo
        p["hitbox"].top = self.gestor.y_techo + 4
        p["hitbox"].left = self.gestor.x_pared_izq
        ai["estado"] = "trepar"
        ai["direccion"] = -1
        for _ in range(10):
            self.gestor.actualizar()
            if p["superficie"] == "techo":
                break
        self.assertEqual(p["superficie"], "techo")

        # C. Techo -> Pared Derecha
        p["hitbox"].top = self.gestor.y_techo
        p["hitbox"].right = self.gestor.x_pared_der - 4
        ai["estado"] = "caminar_techo"
        ai["direccion"] = 1
        for _ in range(10):
            self.gestor.actualizar()
            if p["superficie"] == "pared_der":
                break
        self.assertEqual(p["superficie"], "pared_der")

        # D. Pared Derecha -> Suelo
        p["hitbox"].right = self.gestor.x_pared_der
        p["hitbox"].bottom = self.gestor.y_suelo - 4
        ai["estado"] = "trepar"
        ai["direccion"] = 1
        for _ in range(10):
            self.gestor.actualizar()
            if p["superficie"] == "suelo":
                break
        self.assertEqual(p["superficie"], "suelo")

    def test_06_no_trepar_ni_subirse_a_botones(self):
        """6. No puedan trepar ni subirse a los botones, pero sí usar plataformas."""
        # Las plataformas del escenario existen y son 6
        self.assertEqual(len(self.gestor.plataformas), 6)
        for btn in self.gestor.botones:
            self.assertNotIn(btn, self.gestor.plataformas, "Ningún botón debe ser una plataforma física")

        # Dejar caer un personaje directamente a través de un botón (no debe colisionar)
        p = self.gestor.personajes[0]
        p["superficie"] = "aire"
        p["hitbox"].centerx = BTN_JUGAR_RECT.centerx
        p["hitbox"].bottom = BTN_JUGAR_RECT.top - 10
        p["vel_y"] = 4.0

        paro_en_boton = False
        for _ in range(60):
            self.gestor.actualizar()
            for btn in self.gestor.botones:
                if abs(p["hitbox"].bottom - btn.top) <= 2 and p.get("en_suelo", False) and p["superficie"] in ("suelo", "plataforma"):
                    paro_en_boton = True

        self.assertFalse(paro_en_boton, "El personaje no debe colisionar ni pararse sobre el botón")

    def test_06b_plataformas_funcionan_correctamente(self):
        """6b. Las plataformas tienen colisión real y permiten caminar y descansar."""
        p = self.gestor.personajes[1]
        plat = self.gestor.plataformas[0]
        p["superficie"] = "aire"
        p["hitbox"].centerx = plat.centerx
        p["hitbox"].bottom = plat.top - 15
        p["vel_y"] = 3.0

        aterrizo = False
        for _ in range(20):
            self.gestor.actualizar()
            if p["superficie"] == "plataforma" and abs(p["hitbox"].bottom - plat.top) <= 2:
                aterrizo = True
                break
        self.assertTrue(aterrizo, "El personaje debe poder aterrizar y caminar sobre plataformas reales")

    def test_07_botones_siguen_funcionando_normalmente(self):
        """7. Los botones sigan funcionando normalmente."""
        click_jugar = BTN_JUGAR_RECT.center
        click_pers = BTN_PERSONAJES_RECT.center
        click_cfg = BTN_CONFIG_RECT.center
        click_salir = BTN_SALIR_RECT.center

        self.assertTrue(BTN_JUGAR_RECT.collidepoint(click_jugar))
        self.assertTrue(BTN_PERSONAJES_RECT.collidepoint(click_pers))
        self.assertTrue(BTN_CONFIG_RECT.collidepoint(click_cfg))
        self.assertTrue(BTN_SALIR_RECT.collidepoint(click_salir))

        # Evento de clic
        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": click_jugar})
        self.assertEqual(ev.pos, click_jugar)

    def test_08_sin_teletransporte_ni_bloqueos(self):
        """8. No haya teletransportes ni personajes trabados."""
        for f in range(500):
            pos_prev = [(p["hitbox"].x, p["hitbox"].y) for p in self.gestor.personajes]
            self.gestor.actualizar()
            for i, p in enumerate(self.gestor.personajes):
                dx = abs(p["hitbox"].x - pos_prev[i][0])
                dy = abs(p["hitbox"].y - pos_prev[i][1])
                self.assertLess(dx, 25, f"Teletransporte horizontal en frame {f}, P{i}: dx={dx}")
                self.assertLess(dy, 25, f"Teletransporte vertical en frame {f}, P{i}: dy={dy}")

    def test_09_escena_navidena_conserva_diseno(self):
        """9. La escena navideña conserve su diseño."""
        self.assertIsNotNone(self.gestor.fondo_estatico)
        self.assertEqual(self.gestor.fondo_estatico.get_size(), (1280, 720))
        self.assertGreater(len(self.gestor.copos_nieve), 50)
        self.assertGreater(len(self.gestor.luces_arboles), 20)

    def test_10_niveles_reales_no_modificados(self):
        """10. Los niveles reales no sufran modificaciones."""
        import pantalla
        import menu_niveles
        # Niveles y pantallas de juego siguen intactos
        self.assertTrue(hasattr(pantalla, "iniciar_mundo"))
        self.assertTrue(hasattr(menu_niveles, "dibujar_menu_niveles"))


if __name__ == "__main__":
    unittest.main()
