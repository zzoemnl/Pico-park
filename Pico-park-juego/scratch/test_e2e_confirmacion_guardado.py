import os
import sys
import copy
import shutil
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

import guardado
from guardado import (
    crear_desbloqueados_inicial,
    hay_progreso_sin_guardar,
    guardar_partida,
    cargar_partidas,
    RUTA_PARTIDAS,
)
import main


class TestE2EConfirmacionGuardado(unittest.TestCase):
    def setUp(self):
        self.backup_path = RUTA_PARTIDAS + ".bak_e2e"
        if os.path.exists(RUTA_PARTIDAS):
            shutil.copyfile(RUTA_PARTIDAS, self.backup_path)

    def tearDown(self):
        if os.path.exists(self.backup_path):
            shutil.copyfile(self.backup_path, RUTA_PARTIDAS)
            os.remove(self.backup_path)
            guardado.invalidar_cache_partidas()

    def test_e2e_flujo_completo(self):
        # 1. Simular inicialización de main()
        niveles_desbloqueados = crear_desbloqueados_inicial()
        partida_actual_id = None
        partida_actual_nombre = None
        partida_actual_password = None
        snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
        sesion_activa = False
        partida_cargada_flag = False
        partida_creada_flag = False

        dialogo_invocado = [0]
        def mock_dialogo(*args, **kwargs):
            dialogo_invocado[0] += 1
            return "cancelar"

        # Simular intentar_salir como en main()
        def intentar_salir(ejecutando_ref):
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_dialogo()
                if resp in ("guardar_salir", "salir_sin_guardar"):
                    ejecutando_ref[0] = False
            else:
                ejecutando_ref[0] = False

        # Paso 1: Salir directamente desde el menú principal
        ref = [True]
        intentar_salir(ref)
        self.assertFalse(ref[0], "Debe cerrarse directamente")
        self.assertEqual(dialogo_invocado[0], 0, "No debe mostrar diálogo")

        # Paso 2: Entrar a PERSONAJES y salir
        estado_actual = main.ESTADO_PERSONAJES
        # Vuelve a menú
        estado_actual = main.ESTADO_MENU_PRINCIPAL
        ref = [True]
        intentar_salir(ref)
        self.assertFalse(ref[0], "Debe cerrarse directamente tras personajes")
        self.assertEqual(dialogo_invocado[0], 0, "No debe mostrar diálogo tras personajes")

        # Paso 3: Crear nueva partida sin avanzar
        p_nueva = guardar_partida(crear_desbloqueados_inicial(), nombre_partida="PartidaE2ENueva")
        partida_actual_id = p_nueva["id"]
        partida_actual_nombre = p_nueva["nombre"]
        niveles_desbloqueados = copy.deepcopy(p_nueva["niveles_desbloqueados"])
        snapshot_guardado = copy.deepcopy(p_nueva["niveles_desbloqueados"])
        partida_creada_flag = True
        sesion_activa = True

        ref = [True]
        intentar_salir(ref)
        self.assertFalse(ref[0], "Debe cerrarse directamente sin progreso pendiente")
        self.assertEqual(dialogo_invocado[0], 0, "No debe mostrar diálogo tras crear nueva partida")

        # Paso 4: Cargar partida existente y salir sin jugar
        p_cargada = guardar_partida(crear_desbloqueados_inicial(), nombre_partida="PartidaE2ECargada")
        partida_actual_id = p_cargada["id"]
        partida_actual_nombre = p_cargada["nombre"]
        niveles_desbloqueados = copy.deepcopy(p_cargada["niveles_desbloqueados"])
        snapshot_guardado = copy.deepcopy(p_cargada["niveles_desbloqueados"])
        partida_cargada_flag = True
        sesion_activa = True

        ref = [True]
        intentar_salir(ref)
        self.assertFalse(ref[0], "Debe cerrarse directamente tras cargar sin cambios")
        self.assertEqual(dialogo_invocado[0], 0, "No debe mostrar diálogo al cargar sin cambios")

        # Paso 5: Avanzar nivel (Mundo 1 Nivel 2 desbloqueado)
        niveles_desbloqueados[1][1] = True

        # Paso 5a: Intentar salir y elegir CANCELAR
        ref = [True]
        dialogo_invocado[0] = 0
        def mock_dialogo_cancelar(*args, **kwargs):
            dialogo_invocado[0] += 1
            return "cancelar"

        def intentar_salir_con(mock_fn, ejecutando_ref):
            nonlocal snapshot_guardado
            if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
                resp = mock_fn()
                if resp == "guardar_salir":
                    guardar_partida(niveles_desbloqueados, id_partida=partida_actual_id, nombre_partida=partida_actual_nombre)
                    snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
                    ejecutando_ref[0] = False
                elif resp == "salir_sin_guardar":
                    ejecutando_ref[0] = False
                elif resp == "cancelar":
                    pass
            else:
                ejecutando_ref[0] = False

        intentar_salir_con(mock_dialogo_cancelar, ref)
        self.assertTrue(ref[0], "El juego NO debe cerrarse tras cancelar")
        self.assertEqual(dialogo_invocado[0], 1, "Debe haber preguntado para guardar")
        self.assertTrue(niveles_desbloqueados[1][1], "El progreso desbloqueado sigue intacto")

        # Paso 5b: Intentar salir y elegir GUARDAR Y SALIR
        dialogo_invocado[0] = 0
        def mock_dialogo_guardar(*args, **kwargs):
            dialogo_invocado[0] += 1
            return "guardar_salir"

        ref = [True]
        intentar_salir_con(mock_dialogo_guardar, ref)
        self.assertFalse(ref[0], "El juego debe cerrarse tras guardar y salir")
        self.assertEqual(dialogo_invocado[0], 1, "Debe haber preguntado")
        self.assertEqual(snapshot_guardado, niveles_desbloqueados, "El snapshot ahora está sincronizado")

        # Paso 6: Volver a salir con todo guardado -> no debe preguntar
        dialogo_invocado[0] = 0
        ref = [True]
        intentar_salir_con(mock_dialogo_guardar, ref)
        self.assertFalse(ref[0], "Debe cerrarse directamente")
        self.assertEqual(dialogo_invocado[0], 0, "NO debe preguntar porque ya está todo guardado")


if __name__ == "__main__":
    unittest.main()
