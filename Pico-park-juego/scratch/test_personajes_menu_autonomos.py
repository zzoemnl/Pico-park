"""
Pruebas exhaustivas y validación visual para los 5 Personajes Autónomos del Menú Principal - Pico Park.
Desplazamiento por Suelo, Paredes y Techo. Cero interacción con botones.
"""

import os
import sys
import unittest
import pygame

# Asegurar importación de módulos del juego
DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'

import main
import personajes_menu
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


class TestPersonajesMenuAutonomos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    def setUp(self):
        self.gestor = GestorPersonajesMenu(
            ancho=1280, alto=720,
            color_p1="Celeste", accesorio_p1="Ninguno",
            color_p2="Violeta", accesorio_p2="Corona"
        )

    def test_inicializacion_escenario_y_5_personajes(self):
        """Verifica que existan exactamente los 5 personajes originales y las 4 superficies perimetrales."""
        self.assertEqual(len(self.gestor.personajes), 5, "Deben existir exactamente 5 personajes")
        self.assertEqual(self.gestor.y_suelo, 650)
        self.assertEqual(self.gestor.y_techo, 0)
        self.assertEqual(self.gestor.x_pared_izq, 0)
        self.assertEqual(self.gestor.x_pared_der, 1280)

        # Comprobar que no existen cajas decorativas ni obstáculos artificiales
        self.assertEqual(len(self.gestor.bloques_decorativos), 0, "No debe haber cajas ni bloques decorativos")
        # El escenario cuenta con las 6 plataformas agregadas por requerimiento
        self.assertEqual(len(self.gestor.plataformas), 6, "Deben existir las 6 plataformas del escenario")
        for btn in self.gestor.botones:
            self.assertNotIn(btn, self.gestor.plataformas, "Ningún botón debe ser una plataforma física")

        # Comprobar que los 5 personajes tienen colores distintos
        colores_carpetas = [self.gestor.colores[i] for i in range(5)]
        self.assertEqual(len(set(colores_carpetas)), 5, "Los 5 personajes deben tener 5 colores totalmente distintos")

        # Comprobar superficies iniciales variadas (suelo, plataforma, pared, techo)
        superficies_ini = {p["superficie"] for p in self.gestor.personajes}
        self.assertIn("suelo", superficies_ini)
        self.assertIn("plataforma", superficies_ini)
        self.assertIn("techo", superficies_ini)
        self.assertTrue("pared_izq" in superficies_ini or "pared_der" in superficies_ini)

    def test_simulacion_autonoma_600_frames(self):
        """Simula 600 frames y comprueba desplazamiento por suelo, plataformas, paredes y techo."""
        posiciones = {i: set() for i in range(5)}
        superficies_vistas = {i: set() for i in range(5)}
        saltos = {i: 0 for i in range(5)}
        pisadas_en_botones = 0

        for i, p in enumerate(self.gestor.personajes):
            posiciones[i].add((p["hitbox"].x, p["hitbox"].y))
            superficies_vistas[i].add(p["superficie"])

        for f in range(600):
            pos_prev = [(p["hitbox"].x, p["hitbox"].y) for p in self.gestor.personajes]
            self.gestor.actualizar()

            for i, p in enumerate(self.gestor.personajes):
                ai = self.gestor.ai_estados[i]
                hb = p["hitbox"]
                posiciones[i].add((hb.x, hb.y))
                superficies_vistas[i].add(p["superficie"])

                # Cero teletransportes
                dx = abs(hb.x - pos_prev[i][0])
                dy = abs(hb.y - pos_prev[i][1])
                self.assertLess(dx, 25, f"Teletransporte horizontal en frame {f}, P{i}: dx={dx}")
                self.assertLess(dy, 25, f"Teletransporte vertical en frame {f}, P{i}: dy={dy}")

                # Contención estricta en el perímetro
                self.assertGreaterEqual(hb.left, self.gestor.x_pared_izq - 4)
                self.assertLessEqual(hb.right, self.gestor.x_pared_der + 4)
                self.assertGreaterEqual(hb.top, self.gestor.y_techo - 6)
                self.assertLessEqual(hb.bottom, self.gestor.y_suelo + 2)

                # Comprobar que NINGÚN personaje se pare o camine sobre botones
                for btn in self.gestor.botones:
                    if abs(hb.bottom - btn.top) <= 2 and btn.left - 5 <= hb.centerx <= btn.right + 5:
                        if p.get("en_suelo", False) and p["superficie"] == "suelo":
                            pisadas_en_botones += 1

        self.assertEqual(pisadas_en_botones, 0, "Los personajes no deben usar los botones como plataformas")

        # Comprobar que en conjunto exploran el suelo, paredes y techo
        todas_superficies = set()
        for i in range(5):
            todas_superficies.update(superficies_vistas[i])
            self.assertGreater(len(posiciones[i]), 35, f"Personaje {i} debe desplazarse activamente")

        self.assertIn("suelo", todas_superficies)
        self.assertIn("pared_izq", todas_superficies)
        self.assertIn("techo", todas_superficies)
        self.assertIn("pared_der", todas_superficies)

    def test_transicion_de_pared_a_techo(self):
        """Verifica que un personaje trepando por la pared izquierda pase fluidamente al techo."""
        p = self.gestor.personajes[1]
        p["superficie"] = "pared_izq"
        p["hitbox"].left = self.gestor.x_pared_izq
        p["hitbox"].top = self.gestor.y_techo + 10
        p["vel_y"] = -3.5
        p["vel_x"] = 0
        ai = self.gestor.ai_estados[1]
        ai["estado"] = "trepar"
        ai["direccion"] = -1

        paso_al_techo = False
        for _ in range(30):
            self.gestor.actualizar()
            if p["superficie"] == "techo":
                paso_al_techo = True
                break

        self.assertTrue(paso_al_techo, "El personaje debe pasar de la pared al techo de manera fluida")
        self.assertEqual(p["angulo_objetivo"], 180.0, "En el techo el personaje debe orientarse boca abajo")

    def test_transicion_de_techo_a_pared(self):
        """Verifica que un personaje caminando por el techo pase fluidamente a una pared."""
        p = self.gestor.personajes[2]
        p["superficie"] = "techo"
        p["hitbox"].top = self.gestor.y_techo
        p["hitbox"].right = self.gestor.x_pared_der - 10
        p["vel_x"] = 3.5
        p["vel_y"] = 0
        ai = self.gestor.ai_estados[2]
        ai["estado"] = "caminar_techo"
        ai["direccion"] = 1

        paso_a_pared = False
        for _ in range(30):
            self.gestor.actualizar()
            if p["superficie"] == "pared_der":
                paso_a_pared = True
                break

        self.assertTrue(paso_a_pared, "El personaje debe pasar del techo a la pared derecha fluidamente")
        self.assertEqual(p["angulo_objetivo"], 90.0)

    def test_descenso_de_pared_a_suelo(self):
        """Verifica que un personaje bajando por una pared regrese al suelo."""
        p = self.gestor.personajes[3]
        p["superficie"] = "pared_der"
        p["hitbox"].right = self.gestor.x_pared_der
        p["hitbox"].bottom = self.gestor.y_suelo - 10
        p["vel_y"] = 3.5
        p["vel_x"] = 0
        ai = self.gestor.ai_estados[3]
        ai["estado"] = "trepar"
        ai["direccion"] = 1

        paso_al_suelo = False
        for _ in range(30):
            self.gestor.actualizar()
            if p["superficie"] == "suelo":
                paso_al_suelo = True
                break

        self.assertTrue(paso_al_suelo, "El personaje debe regresar al suelo desde la pared")
        self.assertEqual(p["angulo_objetivo"], 0.0)


if __name__ == "__main__":
    unittest.main()
