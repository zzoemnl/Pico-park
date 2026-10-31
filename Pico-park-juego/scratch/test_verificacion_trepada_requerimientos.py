import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from personajes_menu import GestorPersonajesMenu

class TestVerificacionTrepadaRequerimientos(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorPersonajesMenu()

    def test_01_recuperar_trepada_efectiva(self):
        """1. Los personajes trepan efectivamente y llegan a otras superficies."""
        trepadas = {i: 0 for i in range(5)}
        llegadas_techo = 0
        llegadas_plat = 0
        llegadas_suelo = 0
        prev_sups = [self.gestor.personajes[i]["superficie"] for i in range(5)]

        for _ in range(3600):
            for i in range(5):
                sup = self.gestor.personajes[i]["superficie"]
                prev = prev_sups[i]
                if sup in ("pared_izq", "pared_der") and prev not in ("pared_izq", "pared_der"):
                    trepadas[i] += 1
                if prev in ("pared_izq", "pared_der") and sup == "techo":
                    llegadas_techo += 1
                elif prev in ("pared_izq", "pared_der") and sup == "plataforma":
                    llegadas_plat += 1
                elif prev in ("pared_izq", "pared_der") and sup == "suelo":
                    llegadas_suelo += 1
                prev_sups[i] = sup
            self.gestor.actualizar()

        total_trepadas = sum(trepadas.values())
        self.assertGreater(total_trepadas, 0, "Al menos algunos personajes deben trepar")
        self.assertGreater(llegadas_techo + llegadas_plat + llegadas_suelo, 0, "Deben llegar a otras superficies")

    def test_02_evitar_trepar_siempre(self):
        """2. Tocar una pared permite considerar trepar, pero no lo fuerza siempre."""
        acciones_en_pared = []
        orig_al_tocar = self.gestor._al_tocar_pared

        def intercept_tocar(idx, lado):
            orig_al_tocar(idx, lado)
            hist = self.gestor.ai_estados[idx].get("historial_acciones", [])
            if hist:
                acciones_en_pared.append(hist[-1])

        self.gestor._al_tocar_pared = intercept_tocar

        for _ in range(4000):
            self.gestor.actualizar()

        self.assertGreater(len(acciones_en_pared), 5, "Debe haber múltiples toques de pared")
        trepadas = sum(1 for a in acciones_en_pared if "trepar" in a)
        otras_acciones = len(acciones_en_pared) - trepadas

        self.assertGreater(trepadas, 0, "Debe haber trepadas como opción frecuente")
        self.assertGreater(otras_acciones, 0, "Debe haber otras acciones (girar, quieto, salto, bajar)")
        # Comprobar que no trepan el 100% de las veces
        ratio_trepada = trepadas / len(acciones_en_pared)
        self.assertLess(ratio_trepada, 0.85, f"La tasa de trepada no debe ser absoluta ({ratio_trepada:.2f})")

    def test_03_independencia_cinco_personajes(self):
        """3. Cada uno de los 5 personajes toma decisiones independientes."""
        superficies_visitadas = {i: set() for i in range(5)}
        for _ in range(3000):
            for i in range(5):
                superficies_visitadas[i].add(self.gestor.personajes[i]["superficie"])
            self.gestor.actualizar()

        for i in range(5):
            # Cada personaje debe haber explorado al menos 3 tipos de superficie distintas
            self.assertGreaterEqual(len(superficies_visitadas[i]), 3, f"Personaje {i} debe explorar múltiples superficies")

    def test_04_no_abandonar_trepada_a_mitad_de_camino(self):
        """4. La trepada no se cancela abruptamente hacia el vacío; llega a superficie o salta."""
        # Colocar un personaje en la pared trepando y verificar que avanza
        p = self.gestor.personajes[2]
        ai = self.gestor.ai_estados[2]
        p["superficie"] = "pared_izq"
        p["hitbox"].left = self.gestor.x_pared_izq
        p["hitbox"].bottom = self.gestor.y_suelo - 100
        p["vel_y"] = -p["velocidad_mov"]
        ai["estado"] = "trepar"
        ai["direccion"] = -1
        ai["tiempo"] = 150

        alcanzo_destino = False
        for _ in range(300):
            self.gestor.actualizar()
            if p["superficie"] in ("techo", "plataforma"):
                alcanzo_destino = True
                break

        self.assertTrue(alcanzo_destino, "El personaje debió alcanzar el techo o una plataforma")

    def test_05_sin_vibraciones_ni_bloqueos(self):
        """5. Ausencia de vibración rápida y atascos."""
        oscilaciones = 0
        prev_dirs = [self.gestor.ai_estados[i].get("direccion", 0) for i in range(5)]
        frames_mismo_lugar = [0] * 5
        prev_pos = [(self.gestor.personajes[i]["hitbox"].x, self.gestor.personajes[i]["hitbox"].y) for i in range(5)]

        for _ in range(3000):
            self.gestor.actualizar()
            for i in range(5):
                d = self.gestor.ai_estados[i].get("direccion", 0)
                pd = prev_dirs[i]
                if d != 0 and pd != 0 and d == -pd:
                    oscilaciones += 1
                prev_dirs[i] = d

                pos = (self.gestor.personajes[i]["hitbox"].x, self.gestor.personajes[i]["hitbox"].y)
                if pos == prev_pos[i] and self.gestor.ai_estados[i]["estado"] != "quieto":
                    frames_mismo_lugar[i] += 1
                else:
                    frames_mismo_lugar[i] = 0
                prev_pos[i] = pos

                self.assertLess(frames_mismo_lugar[i], 80, f"Personaje {i} no debe quedarse trabado")

        self.assertLess(oscilaciones, 100, "No debe haber oscilaciones excesivas ni vibración")

if __name__ == "__main__":
    unittest.main()
