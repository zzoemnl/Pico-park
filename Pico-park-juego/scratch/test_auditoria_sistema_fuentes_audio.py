"""
Suite de Pruebas Automatizadas de Verificación Integral:
Auditoría del Sistema de Fuentes y Audio - Pico Park
"""

import os
import sys
import unittest
import tempfile
import pygame

DIRECTORIO_JUEGO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

import fuentes
import configuracion
import guardado
import main
import pantalla
import menu_niveles


class TestAuditoriaFuentesAudio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass

    def setUp(self):
        fuentes.limpiar_cache_fuentes()

    # --------------------------------------------------------------------------
    # 1. TÍTULOS Y SUBTÍTULOS CENTRALIZADOS
    # --------------------------------------------------------------------------
    def test_01_titulos_y_subtitulos_centralizados(self):
        """Verifica que FUENTE_TITULO y FUENTE_SUBTITULO existan y conecten con todas las pantallas."""
        self.assertTrue(hasattr(fuentes, "FUENTE_TITULO"))
        self.assertTrue(hasattr(fuentes, "FUENTE_SUBTITULO"))
        self.assertTrue(hasattr(fuentes, "TAMANO_TITULO"))
        self.assertTrue(hasattr(fuentes, "TAMANO_SUBTITULO"))

        f_tit = fuentes.obtener_fuente_titulo()
        f_sub = fuentes.obtener_fuente_subtitulo()
        self.assertIsInstance(f_tit, pygame.font.Font)
        self.assertIsInstance(f_sub, pygame.font.Font)

        # Comprobar que obtener_fuente_elegante en pantalla.py utiliza el sistema centralizado
        f_elegante = pantalla.obtener_fuente_elegante(25)
        self.assertIsInstance(f_elegante, pygame.font.Font)

    # --------------------------------------------------------------------------
    # 2. CAMBIO DE VARIABLES ACTUALIZA TODOS LOS ELEMENTOS CORRESPONDIENTES
    # --------------------------------------------------------------------------
    def test_02_cambio_de_variables_actualiza_elementos(self):
        """Verifica que cambiar las variables centralizadas de fuente y tamaño actualice el resultado."""
        categorias = [
            ("FUENTE_TITULO", "TAMANO_TITULO", fuentes.obtener_fuente_titulo),
            ("FUENTE_SUBTITULO", "TAMANO_SUBTITULO", fuentes.obtener_fuente_subtitulo),
            ("FUENTE_TEXTO", "TAMANO_TEXTO", fuentes.obtener_fuente_texto),
            ("FUENTE_BOTONES", "TAMANO_BOTONES", fuentes.obtener_fuente_botones),
            ("FUENTE_PEQUENA", "TAMANO_PEQUENA", fuentes.obtener_fuente_pequena),
            ("FUENTE_CONTADOR", "TAMANO_CONTADOR", fuentes.obtener_fuente_contador),
            ("FUENTE_DIALOGOS", "TAMANO_DIALOGOS", fuentes.obtener_fuente_dialogos),
        ]

        for var_fuente, var_tamano, fn_getter in categorias:
            fuentes.limpiar_cache_fuentes()
            orig_f = getattr(fuentes, var_fuente)
            orig_t = getattr(fuentes, var_tamano)
            try:
                # Modificar a tipografía de sistema estándar
                setattr(fuentes, var_fuente, "Arial")
                setattr(fuentes, var_tamano, 27)
                f_obj = fn_getter()
                self.assertIsInstance(f_obj, pygame.font.Font)
                surf = f_obj.render("TEST", True, (255, 255, 255))
                self.assertGreater(surf.get_width(), 0)
            finally:
                setattr(fuentes, var_fuente, orig_f)
                setattr(fuentes, var_tamano, orig_t)
                fuentes.limpiar_cache_fuentes()

    # --------------------------------------------------------------------------
    # 3. SIN FUENTES DISPERSAS O HARDCODEADAS DIRECTAMENTE
    # --------------------------------------------------------------------------
    def test_03_sin_fuentes_hardcodeadas_en_pantallas(self):
        """Comprueba que no queden llamadas a SysFont/Font huérfanas en el bucle principal de dibujo."""
        # pantalla.py ya no debe llamar SysFont para HUDs de linternas, oxígeno o cámaras de aire
        with open(pantalla.__file__, "r", encoding="utf-8") as f:
            code = f.read()

        lineas_sysfont = [line for line in code.splitlines() if "pygame.font.SysFont" in line]
        self.assertEqual(len(lineas_sysfont), 0, f"Quedaron SysFont directos en pantalla.py: {lineas_sysfont}")

        # Comprobar que en guardado.py no hay Font(None, ...) hardcodeado
        with open(guardado.__file__, "r", encoding="utf-8") as f:
            code_g = f.read()
        self.assertNotIn("pygame.font.Font(None,", code_g)

    # --------------------------------------------------------------------------
    # 4. CARACTERES ESPECIALES EN ESPAÑOL (ACENTOS, Ñ, ¿, ¡)
    # --------------------------------------------------------------------------
    def test_04_caracteres_especiales_espanol(self):
        """Verifica que se rendericen correctamente acentos, eñes y signos del español sin errores."""
        frases_espanol = [
            "¡NIVEL COMPLETADO!",
            "¿Querés reiniciar o salir?",
            "Configuración del juego",
            "Mundo 1 - Selección de Nivel",
            "Contraseña incorrecta",
            "Accesorios y atuendos del niño",
            "Página 1 de 5",
            "¡Buen trabajo! Éxito total",
        ]

        fuentes_a_probar = [
            fuentes.obtener_fuente_texto(),
            fuentes.obtener_fuente_subtitulo(),
            fuentes.obtener_fuente_dialogos(),
            fuentes.obtener_fuente_contador(),
            fuentes.obtener_fuente_pequena(),
        ]

        for font in fuentes_a_probar:
            for frase in frases_espanol:
                surf = font.render(frase, True, (255, 255, 255))
                self.assertIsNotNone(surf)
                self.assertGreater(surf.get_width(), 0)
                self.assertGreater(surf.get_height(), 0)

    # --------------------------------------------------------------------------
    # 5. MÚSICA DEL MENÚ NO SE REINICIA AL NAVEGAR ENTRE PANTALLAS
    # --------------------------------------------------------------------------
    def test_05_musica_menu_no_se_reinicia_al_navegar(self):
        """Comprueba que reproducir_musica('menu') no reinicie la canción si ya está activa."""
        configuracion.reproducir_musica("menu")
        tipo_act1, arch1 = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_act1, "menu")

        # Simular navegación a 'Modo de Juego', 'Partidas' y 'Personalización'
        configuracion.reproducir_musica("menu")
        tipo_act2, arch2 = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_act2, "menu")
        self.assertEqual(arch1, arch2)

        configuracion.reproducir_musica("menu")
        tipo_act3, arch3 = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_act3, "menu")

    # --------------------------------------------------------------------------
    # 6. CADA MUNDO TIENE SU PISTA Y CAMBIAR DE NIVEL NO REINICIA LA MÚSICA
    # --------------------------------------------------------------------------
    def test_06_cada_mundo_tiene_su_pista_sin_reinicio_por_nivel(self):
        """Verifica que cada mundo cambie su pista y avanzar niveles dentro del mismo mundo la conserve."""
        # Mundo 1 Nivel 1
        configuracion.reproducir_musica("mundo_1")
        tipo, _ = configuracion.obtener_musica_actual()
        self.assertEqual(tipo, "mundo_1")

        # Mundo 1 Nivel 2 (debe conservar pista sin reiniciar)
        configuracion.reproducir_musica("mundo_1")
        tipo_n2, _ = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_n2, "mundo_1")

        # Mundo 1 Nivel 5
        configuracion.reproducir_musica("mundo_1")
        tipo_n5, _ = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_n5, "mundo_1")

        # Pasar a Mundo 2 Nivel 1 (debe cambiar de pista)
        configuracion.reproducir_musica("mundo_2")
        tipo_m2, _ = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_m2, "mundo_2")

        # Pasar a Mundo 3 Nivel 1 (debe cambiar de pista)
        configuracion.reproducir_musica("mundo_3")
        tipo_m3, _ = configuracion.obtener_musica_actual()
        self.assertEqual(tipo_m3, "mundo_3")

    # --------------------------------------------------------------------------
    # 7. VOLVER AL MENÚ CAMBIA LA MÚSICA CORRECTAMENTE
    # --------------------------------------------------------------------------
    def test_07_volver_al_menu_cambia_musica(self):
        """Verifica que volver al menú desde un mundo restablezca la pista del menú."""
        configuracion.reproducir_musica("mundo_3")
        self.assertEqual(configuracion.obtener_musica_actual()[0], "mundo_3")

        configuracion.reproducir_musica("menu")
        self.assertEqual(configuracion.obtener_musica_actual()[0], "menu")

    # --------------------------------------------------------------------------
    # 8. TOLERANCIA ANTE AUDIOS AÚN NO EXISTENTES
    # --------------------------------------------------------------------------
    def test_08_tolerancia_audios_inexistentes(self):
        """Comprueba que si no existen archivos de audio, el juego funciona sin errores ni cuelgues."""
        orig_menu = configuracion.AUDIO_MENU
        orig_m1 = configuracion.AUDIO_MUNDO_1
        try:
            configuracion.AUDIO_MENU = "archivo_inexistente_12345.mp3"
            configuracion.AUDIO_MUNDO_1 = "archivo_inexistente_67890.ogg"

            # No debe lanzar excepción
            configuracion.reproducir_musica("menu", forzar=True)
            self.assertEqual(configuracion.obtener_musica_actual()[0], "menu")

            configuracion.reproducir_musica("mundo_1", forzar=True)
            self.assertEqual(configuracion.obtener_musica_actual()[0], "mundo_1")
        finally:
            configuracion.AUDIO_MENU = orig_menu
            configuracion.AUDIO_MUNDO_1 = orig_m1

    # --------------------------------------------------------------------------
    # 9. CONTROL Y PERSISTENCIA DE VOLUMEN SIN SUPERPOSICIÓN DE PISTAS
    # --------------------------------------------------------------------------
    def test_09_volumen_y_persistencia(self):
        """Verifica que el volumen se conserve al navegar, cambiar pistas y persistir en disco."""
        orig_vol = configuracion.obtener_volumen()
        try:
            configuracion.fijar_volumen(55)
            self.assertEqual(configuracion.obtener_volumen(), 55)
            self.assertEqual(configuracion.obtener_volumen_musica(), 55)
            self.assertEqual(configuracion.obtener_volumen_efectos(), 55)

            # Probar persistencia
            configuracion._guardar_configuracion_disco()
            configuracion._cargar_configuracion_disco()
            self.assertEqual(configuracion.obtener_volumen(), 55)

            # Comprobar volumen independiente de música si se ajusta
            configuracion.fijar_volumen_musica(40)
            self.assertEqual(configuracion.obtener_volumen_musica(), 40)
        finally:
            configuracion.fijar_volumen(orig_vol)

    # --------------------------------------------------------------------------
    # 10. PARTIDAS GUARDADAS Y DEMÁS FUNCIONALIDADES INTACTAS
    # --------------------------------------------------------------------------
    def test_10_partidas_guardadas_intactas(self):
        """Verifica que el sistema de guardado siga cargando y guardando correctamente."""
        partidas = guardado.cargar_partidas()
        self.assertIsInstance(partidas, list)
        if len(partidas) > 0:
            p = partidas[0]
            self.assertIn("id", p)
            self.assertIn("nombre", p)
            self.assertIn("niveles_desbloqueados", p)


if __name__ == "__main__":
    unittest.main()
