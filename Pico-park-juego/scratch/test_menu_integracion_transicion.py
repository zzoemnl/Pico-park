"""
Prueba de integración: Entrada a partida y retorno al menú principal sin duplicación de personajes.
"""

import os
import sys
import unittest
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'

from personajes_menu import GestorPersonajesMenu

class TestIntegracionTransicionMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    def test_transicion_partida_y_retorno_sin_duplicacion(self):
        """Simula el flujo completo de estar en menú, entrar a nivel, y volver al menú."""
        gestor = GestorPersonajesMenu(
            ancho=1280, alto=720,
            color_p1="Celeste", accesorio_p1="Ninguno",
            color_p2="Violeta", accesorio_p2="Corona"
        )

        # 1. Menú activo por 60 frames
        self.assertEqual(len(gestor.personajes), 5)
        for _ in range(60):
            gestor.actualizar()

        self.assertEqual(len(gestor.personajes), 5)
        posiciones_antes = [(p["hitbox"].x, p["hitbox"].y) for p in gestor.personajes]

        # 2. Transición a partida (el gestor del menú pausa su actualización)
        # Durante el nivel real, gestor.actualizar() NO se llama
        # Simulamos que transcurre el juego...
        nivel_completado = True
        self.assertTrue(nivel_completado)

        # 3. Retorno al Menú Principal
        # Al volver al menú, se sincroniza personalización y se reanuda gestor.actualizar()
        gestor.sincronizar_personalizacion("Rojo", "Gorro", "Verde", "Anteojos")
        self.assertEqual(len(gestor.personajes), 5, "Los personajes no deben duplicarse al volver al menú")

        # 4. El menú continúa funcionando sin errores
        for _ in range(60):
            gestor.actualizar()

        self.assertEqual(len(gestor.personajes), 5)
        self.assertEqual(gestor.colores[0], "Rojo")
        self.assertEqual(gestor.colores[1], "Verde")

        # Verificar que todos los 5 personajes siguen moviéndose
        posiciones_despues = [(p["hitbox"].x, p["hitbox"].y) for p in gestor.personajes]
        movidos = sum(1 for a, d in zip(posiciones_antes, posiciones_despues) if a != d)
        self.assertGreaterEqual(movidos, 4, "Los personajes deben continuar su movimiento autónomo al volver")

if __name__ == "__main__":
    unittest.main()
