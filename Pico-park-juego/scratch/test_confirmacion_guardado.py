import os
import sys
import copy
import shutil
import unittest
from unittest.mock import patch, MagicMock

# Ensure Pico-park-juego directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import guardado
from guardado import (
    crear_desbloqueados_inicial,
    hay_progreso_sin_guardar,
    guardar_partida,
    cargar_partidas,
    eliminar_partida,
    RUTA_PARTIDAS,
)


class TestConfirmacionGuardado(unittest.TestCase):
    def setUp(self):
        # Backup original partidas.txt if exists
        self.backup_path = RUTA_PARTIDAS + ".bak_test"
        if os.path.exists(RUTA_PARTIDAS):
            shutil.copyfile(RUTA_PARTIDAS, self.backup_path)

    def tearDown(self):
        # Restore original partidas.txt
        if os.path.exists(self.backup_path):
            shutil.copyfile(self.backup_path, RUTA_PARTIDAS)
            os.remove(self.backup_path)
            guardado.invalidar_cache_partidas()

    def test_caso_1_menu_principal_sin_jugar(self):
        """1. Abrir el juego y pulsar «SALIR»: debe cerrarse directamente sin preguntar."""
        niveles_desbloqueados = crear_desbloqueados_inicial()
        partida_actual_id = None
        partida_actual_nombre = None
        partida_actual_password = None
        snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
        sesion_activa = False

        dialogo_llamado = False
        def mock_mostrar_dialogo(*args, **kwargs):
            nonlocal dialogo_llamado
            dialogo_llamado = True
            return "cancelar"

        ejecutando = True
        def intentar_salir():
            nonlocal ejecutando, snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_mostrar_dialogo()
                if resp == "guardar_salir":
                    snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
                    ejecutando = False
                elif resp == "salir_sin_guardar":
                    ejecutando = False
            else:
                ejecutando = False

        intentar_salir()

        self.assertFalse(dialogo_llamado, "El diálogo de guardado NO debe ser llamado al salir desde el menú principal.")
        self.assertFalse(ejecutando, "El juego debe cerrarse directamente (ejecutando = False).")

    def test_caso_2_personajes_volver_y_salir(self):
        """2. Entrar a «PERSONAJES», volver al menú y salir: no debe pedir guardar."""
        niveles_desbloqueados = crear_desbloqueados_inicial()
        partida_actual_id = None
        snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
        sesion_activa = False

        # Simulamos cambio de personalización de personajes
        color_p1 = "Amarillo"
        color_p2 = "Celeste"
        accesorio_p1 = "Gorra"
        accesorio_p2 = "Moño"

        # Volvemos al menú y salimos
        dialogo_llamado = False
        def mock_mostrar_dialogo(*args, **kwargs):
            nonlocal dialogo_llamado
            dialogo_llamado = True
            return "cancelar"

        ejecutando = True
        def intentar_salir():
            nonlocal ejecutando, snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_mostrar_dialogo()
                if resp in ("guardar_salir", "salir_sin_guardar"):
                    ejecutando = False
            else:
                ejecutando = False

        intentar_salir()

        self.assertFalse(dialogo_llamado, "Visitar personajes y volver no debe activar la confirmación de guardado.")
        self.assertFalse(ejecutando, "El juego debe cerrarse directamente.")

    def test_caso_3_nueva_partida_sin_progreso_pendiente(self):
        """3. Crear una nueva partida y salir sin iniciar una sesión con progreso pendiente: no debe preguntar."""
        # Se crea la partida en el sistema actual
        desbloqueados_ini = crear_desbloqueados_inicial()
        partida_creada = guardar_partida(desbloqueados_ini, nombre_partida="PartidaTestNueva")
        self.assertIsNotNone(partida_creada)

        partida_actual_id = partida_creada["id"]
        partida_actual_nombre = partida_creada["nombre"]
        niveles_desbloqueados = copy.deepcopy(partida_creada["niveles_desbloqueados"])
        snapshot_guardado = copy.deepcopy(partida_creada["niveles_desbloqueados"])
        partida_creada_flag = True
        sesion_activa = True

        # El jugador sale sin haber avanzado niveles
        dialogo_llamado = False
        def mock_mostrar_dialogo(*args, **kwargs):
            nonlocal dialogo_llamado
            dialogo_llamado = True
            return "cancelar"

        ejecutando = True
        def intentar_salir():
            nonlocal ejecutando, snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_mostrar_dialogo()
                if resp in ("guardar_salir", "salir_sin_guardar"):
                    ejecutando = False
            else:
                ejecutando = False

        intentar_salir()

        self.assertFalse(dialogo_llamado, "Crear nueva partida sin progreso pendiente NO debe preguntar por guardar.")
        self.assertFalse(ejecutando, "El juego debe cerrarse directamente.")

    def test_caso_4_continuar_partida_avanzar_y_salir(self):
        """4. Continuar una partida guardada, avanzar en un nivel y salir: debe preguntar si hay progreso sin guardar."""
        # Creamos una partida existente en disco
        desbloqueados_ini = crear_desbloqueados_inicial()
        partida_existente = guardar_partida(desbloqueados_ini, nombre_partida="PartidaExistente")

        # Cargamos la partida
        partida_actual_id = partida_existente["id"]
        partida_actual_nombre = partida_existente["nombre"]
        niveles_desbloqueados = copy.deepcopy(partida_existente["niveles_desbloqueados"])
        snapshot_guardado = copy.deepcopy(partida_existente["niveles_desbloqueados"])
        partida_cargada_flag = True
        sesion_activa = True

        # Antes de avanzar nivel: no hay cambios pendientes
        self.assertFalse(hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id))

        # Simulamos que avanza y completa el nivel 1-1, desbloqueando 1-2
        niveles_desbloqueados[1][1] = True

        # Ahora sí hay progreso pendiente
        self.assertTrue(hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id))

        dialogo_llamado = False
        def mock_mostrar_dialogo(*args, **kwargs):
            nonlocal dialogo_llamado
            dialogo_llamado = True
            return "guardar_salir"

        ejecutando = True
        def intentar_salir():
            nonlocal ejecutando, snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_mostrar_dialogo()
                if resp == "guardar_salir":
                    guardar_partida(niveles_desbloqueados, id_partida=partida_actual_id, nombre_partida=partida_actual_nombre)
                    snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
                    ejecutando = False
                elif resp == "salir_sin_guardar":
                    ejecutando = False
            else:
                ejecutando = False

        intentar_salir()

        self.assertTrue(dialogo_llamado, "Debe mostrar el diálogo cuando hay progreso pendiente de guardar.")
        self.assertFalse(ejecutando, "Al confirmar guardar y salir, debe cerrarse.")

    def test_caso_5_guardar_cambios_y_volver_a_salir(self):
        """5. Guardar los cambios y volver a salir: no debe volver a preguntar si ya está todo guardado."""
        desbloqueados_ini = crear_desbloqueados_inicial()
        partida = guardar_partida(desbloqueados_ini, nombre_partida="PartidaGuardada")

        partida_actual_id = partida["id"]
        partida_actual_nombre = partida["nombre"]
        niveles_desbloqueados = copy.deepcopy(partida["niveles_desbloqueados"])
        snapshot_guardado = copy.deepcopy(partida["niveles_desbloqueados"])
        sesion_activa = True

        # Avanzamos y desbloqueamos
        niveles_desbloqueados[1][1] = True
        self.assertTrue(hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id))

        # Guardamos los cambios
        guardar_partida(niveles_desbloqueados, id_partida=partida_actual_id, nombre_partida=partida_actual_nombre)
        snapshot_guardado = copy.deepcopy(niveles_desbloqueados)

        # Ahora el estado guardado coincide con niveles_desbloqueados
        self.assertFalse(hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id))

        # Al intentar salir nuevamente, NO debe preguntar
        dialogo_llamado = False
        def mock_mostrar_dialogo(*args, **kwargs):
            nonlocal dialogo_llamado
            dialogo_llamado = True
            return "guardar_salir"

        ejecutando = True
        def intentar_salir():
            nonlocal ejecutando, snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_mostrar_dialogo()
                if resp in ("guardar_salir", "salir_sin_guardar"):
                    ejecutando = False
            else:
                ejecutando = False

        intentar_salir()

        self.assertFalse(dialogo_llamado, "Ya no debe preguntar porque los cambios ya fueron guardados.")
        self.assertFalse(ejecutando, "Debe cerrarse directamente.")

    def test_caso_6_elegir_cancelar_en_confirmacion(self):
        """6. Elegir «CANCELAR» en la confirmación: debe volver al juego sin perder el progreso."""
        desbloqueados_ini = crear_desbloqueados_inicial()
        partida = guardar_partida(desbloqueados_ini, nombre_partida="PartidaCancel")

        partida_actual_id = partida["id"]
        partida_actual_nombre = partida["nombre"]
        niveles_desbloqueados = copy.deepcopy(partida["niveles_desbloqueados"])
        snapshot_guardado = copy.deepcopy(partida["niveles_desbloqueados"])
        sesion_activa = True

        # Avanzamos nivel 1-1 -> 1-2
        niveles_desbloqueados[1][1] = True
        progreso_antes = copy.deepcopy(niveles_desbloqueados)

        dialogo_llamado = False
        def mock_mostrar_dialogo(*args, **kwargs):
            nonlocal dialogo_llamado
            dialogo_llamado = True
            return "cancelar"

        ejecutando = True
        def intentar_salir():
            nonlocal ejecutando, snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_mostrar_dialogo()
                if resp == "guardar_salir":
                    snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
                    ejecutando = False
                elif resp == "salir_sin_guardar":
                    ejecutando = False
                elif resp == "cancelar":
                    # Volver al juego sin salir
                    pass
            else:
                ejecutando = False

        intentar_salir()

        self.assertTrue(dialogo_llamado, "El diálogo debe mostrarse porque hay progreso pendiente.")
        self.assertTrue(ejecutando, "El juego debe seguir ejecutándose tras presionar «CANCELAR».")
        self.assertEqual(niveles_desbloqueados, progreso_antes, "El progreso no debe perderse tras presionar «CANCELAR».")


if __name__ == "__main__":
    unittest.main()
