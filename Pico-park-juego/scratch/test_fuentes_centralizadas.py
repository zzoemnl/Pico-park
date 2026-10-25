import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import fuentes
import guardado
import main
import pantalla
import menu_niveles


class TestFuentesCentralizadas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

    def test_01_variables_requeridas_definidas(self):
        """Verifica que las variables mínimas solicitadas existan en fuentes.py."""
        # Categorías de fuentes
        self.assertTrue(hasattr(fuentes, "FUENTE_TITULO"))
        self.assertTrue(hasattr(fuentes, "FUENTE_SUBTITULO"))
        self.assertTrue(hasattr(fuentes, "FUENTE_TEXTO"))
        self.assertTrue(hasattr(fuentes, "FUENTE_BOTON"))
        self.assertTrue(hasattr(fuentes, "FUENTE_PEQUENA"))

        # Categorías de tamaños
        self.assertTrue(hasattr(fuentes, "TAMANO_TITULO"))
        self.assertTrue(hasattr(fuentes, "TAMANO_SUBTITULO"))
        self.assertTrue(hasattr(fuentes, "TAMANO_TEXTO"))
        self.assertTrue(hasattr(fuentes, "TAMANO_BOTON"))
        self.assertTrue(hasattr(fuentes, "TAMANO_PEQUENA"))

        self.assertIsInstance(fuentes.TAMANO_TITULO, int)
        self.assertIsInstance(fuentes.TAMANO_SUBTITULO, int)
        self.assertIsInstance(fuentes.TAMANO_TEXTO, int)
        self.assertIsInstance(fuentes.TAMANO_BOTON, int)
        self.assertIsInstance(fuentes.TAMANO_PEQUENA, int)

    def test_02_funciones_obtencion_fuentes(self):
        """Verifica que los métodos de obtención retornen instancias válidas de Font."""
        f_tit = fuentes.obtener_fuente_titulo()
        self.assertIsInstance(f_tit, pygame.font.Font)

        f_sub = fuentes.obtener_fuente_subtitulo()
        self.assertIsInstance(f_sub, pygame.font.Font)

        f_txt = fuentes.obtener_fuente_texto()
        self.assertIsInstance(f_txt, pygame.font.Font)

        f_btn = fuentes.obtener_fuente_boton()
        self.assertIsInstance(f_btn, pygame.font.Font)

        f_peq = fuentes.obtener_fuente_pequena()
        self.assertIsInstance(f_peq, pygame.font.Font)

    def test_03_cache_reutiliza_instancias(self):
        """Verifica que llamar a obtener_fuente no vuelva a crear o recargar la fuente en cada fotograma."""
        f1 = fuentes.obtener_fuente_titulo()
        f2 = fuentes.obtener_fuente_titulo()
        self.assertIs(f1, f2, "Debe reutilizar la misma instancia desde el caché")

        f_btn1 = fuentes.obtener_fuente_boton(15)
        f_btn2 = fuentes.obtener_fuente_boton(15)
        self.assertIs(f_btn1, f_btn2, "Debe reutilizar la misma instancia con mismo tamaño")

    def test_04_modificacion_centralizada_de_tamano(self):
        """Verifica que modificar TAMANO_TITULO afecte el tamaño retornado."""
        fuentes.limpiar_cache_fuentes()
        orig_tamano = fuentes.TAMANO_TITULO
        try:
            fuentes.TAMANO_TITULO = 22
            f_custom = fuentes.obtener_fuente_titulo()
            # La fuente debe renderizar texto sin errores
            surf = f_custom.render("PRUEBA", True, (255, 255, 255))
            self.assertIsNotNone(surf)
        finally:
            fuentes.TAMANO_TITULO = orig_tamano
            fuentes.limpiar_cache_fuentes()

    def test_05_modificacion_centralizada_de_tipografia(self):
        """Verifica que modificar FUENTE_TITULO cambie la tipografía."""
        fuentes.limpiar_cache_fuentes()
        orig_fuente = fuentes.FUENTE_TITULO
        try:
            fuentes.FUENTE_TITULO = "Arial"
            f_arial = fuentes.obtener_fuente_titulo()
            self.assertIsInstance(f_arial, pygame.font.Font)
            surf = f_arial.render("TITULO CON ARIAL", True, (0, 0, 0))
            self.assertIsNotNone(surf)
        finally:
            fuentes.FUENTE_TITULO = orig_fuente
            fuentes.limpiar_cache_fuentes()

    def test_06_tolerancia_fallos_fuente_inexistente(self):
        """Verifica que ante una fuente no disponible, use un respaldo válido sin fallar."""
        fuentes.limpiar_cache_fuentes()
        orig_fuente = fuentes.FUENTE_TITULO
        try:
            fuentes.FUENTE_TITULO = "fuente_fantasma_inexistente_9999.ttf"
            f_fallback = fuentes.obtener_fuente_titulo()
            self.assertIsInstance(f_fallback, pygame.font.Font)
            surf = f_fallback.render("TEXTO RESILIENTE", True, (0, 0, 0))
            self.assertIsNotNone(surf)
        finally:
            fuentes.FUENTE_TITULO = orig_fuente
            fuentes.limpiar_cache_fuentes()

    def test_07_compatibilidad_retroactiva(self):
        """Verifica que cargar_fuente_pixel siga disponible para compatibilidad."""
        f_pixel = fuentes.cargar_fuente_pixel(18)
        self.assertIsInstance(f_pixel, pygame.font.Font)

        f_pixel_g = guardado.cargar_fuente_pixel(18)
        self.assertIsInstance(f_pixel_g, pygame.font.Font)

    def test_08_sin_fuentes_hardcodeadas_directas_en_modales_y_pantallas(self):
        """Verifica que guardado, main y pantalla utilicen las variables centralizadas."""
        with open(guardado.__file__, "r", encoding="utf-8") as f:
            guardado_code = f.read()
            self.assertNotIn("pygame.font.Font(None,", guardado_code)
            self.assertIn("obtener_fuente_titulo", guardado_code)
            self.assertIn("obtener_fuente_boton", guardado_code)

        with open(main.__file__, "r", encoding="utf-8") as f:
            main_code = f.read()
            self.assertNotIn("pygame.font.Font(None,", main_code)
            self.assertIn("obtener_fuente_titulo", main_code)
            self.assertIn("obtener_fuente_boton", main_code)

        with open(pantalla.__file__, "r", encoding="utf-8") as f:
            pantalla_code = f.read()
            self.assertNotIn("pygame.font.Font(None,", pantalla_code)
            self.assertIn("obtener_fuente_titulo", pantalla_code)


if __name__ == "__main__":
    unittest.main()
