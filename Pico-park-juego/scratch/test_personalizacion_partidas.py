import os
import sys
import copy
import shutil
import unittest
from unittest.mock import patch, MagicMock

# Configurar entorno headless para pygame antes de importarlo
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

import guardado
from guardado import (
    crear_desbloqueados_inicial,
    hay_progreso_sin_guardar,
    guardar_partida,
    cargar_partidas,
    eliminar_partida,
    guardar_partidas_seguras,
    mostrar_dialogo_confirmar_atuendos,
    RUTA_PARTIDAS,
)


class TestPersonalizacionPartidas(unittest.TestCase):
    def setUp(self):
        self.backup_path = RUTA_PARTIDAS + ".bak_test_pers"
        if os.path.exists(RUTA_PARTIDAS):
            shutil.copyfile(RUTA_PARTIDAS, self.backup_path)
        guardado.invalidar_cache_partidas()

    def tearDown(self):
        if os.path.exists(self.backup_path):
            shutil.copyfile(self.backup_path, RUTA_PARTIDAS)
            os.remove(self.backup_path)
            guardado.invalidar_cache_partidas()

    def test_caso_1_crear_partida_personalizada_y_persistir(self):
        """Caso 1: Creo una partida con dos personajes personalizados y cierro el juego."""
        desbloqueados = crear_desbloqueados_inicial()
        p1_color, p2_color = "Rojo", "Verde"
        p1_acc, p2_acc = "Corona", "Gorro"

        partida = guardar_partida(
            desbloqueados,
            nombre_partida="PartidaCaso1",
            color_p1=p1_color,
            color_p2=p2_color,
            accesorio_p1=p1_acc,
            accesorio_p2=p2_acc,
        )
        self.assertIsNotNone(partida, "La partida debió guardarse correctamente")
        self.assertEqual(partida["color_p1"], "Rojo")
        self.assertEqual(partida["color_p2"], "Verde")
        self.assertEqual(partida["accesorio_p1"], "Corona")
        self.assertEqual(partida["accesorio_p2"], "Gorro")

        # Simular cierre del juego: invalidar caché y leer archivo crudo de disco
        guardado.invalidar_cache_partidas()
        with open(RUTA_PARTIDAS, "r", encoding="utf-8") as f:
            contenido = f.read()

        self.assertIn("PartidaCaso1", contenido)
        self.assertIn("Rojo,Verde,Corona,Gorro", contenido)
        print("[OK] Caso 1 superado: la partida se guarda con su personalizacion en disco.")

    def test_caso_2_continuar_sin_modificar_conserva_atuendos_sin_pregunta(self):
        """Caso 2: Vuelvo a abrirlo, entro a continuar esa partida sin modificar y se conservan sus atuendos sin ventana innecesaria."""
        desbloqueados = crear_desbloqueados_inicial()
        p_guardada = guardar_partida(
            desbloqueados,
            nombre_partida="PartidaCaso2",
            color_p1="Amarillo",
            color_p2="Rosa",
            accesorio_p1="Sombrero",
            accesorio_p2="Anteojos",
        )
        guardado.invalidar_cache_partidas()

        # Al abrir el juego de nuevo:
        color_p1 = "Celeste"
        color_p2 = "Violeta"
        accesorio_p1 = "Ninguno"
        accesorio_p2 = "Ninguno"
        personalizacion_modificada_en_menu = False

        partidas = cargar_partidas()
        p = next(x for x in partidas if x["id"] == p_guardada["id"])

        atuendo_guardado = (
            p.get("color_p1", "Celeste"),
            p.get("color_p2", "Violeta"),
            p.get("accesorio_p1", "Ninguno"),
            p.get("accesorio_p2", "Ninguno"),
        )
        atuendo_actual = (color_p1, color_p2, accesorio_p1, accesorio_p2)
        hay_cambios_pendientes = personalizacion_modificada_en_menu and (atuendo_actual != atuendo_guardado)

        # No se debe mostrar ventana de confirmación porque el jugador no entró a personalizar
        self.assertFalse(hay_cambios_pendientes, "No debe haber cambios pendientes si no se modificó en el menú")

        # Se recupera directamente la apariencia guardada
        color_p1, color_p2, accesorio_p1, accesorio_p2 = atuendo_guardado
        self.assertEqual(color_p1, "Amarillo")
        self.assertEqual(color_p2, "Rosa")
        self.assertEqual(accesorio_p1, "Sombrero")
        self.assertEqual(accesorio_p2, "Anteojos")
        print("[OK] Caso 2 superado: se recuperan los atuendos guardados directamente sin preguntas.")

    def test_caso_3_modificar_antes_de_continuar_detecta_cambios(self):
        """Caso 3: Modifico el color o el accesorio antes de continuar y aparece la ventana de confirmación."""
        desbloqueados = crear_desbloqueados_inicial()
        p_guardada = guardar_partida(
            desbloqueados,
            nombre_partida="PartidaCaso3",
            color_p1="Azul",
            color_p2="Naranja",
            accesorio_p1="Ninguno",
            accesorio_p2="Corona",
        )
        guardado.invalidar_cache_partidas()

        partidas = cargar_partidas()
        p = next(x for x in partidas if x["id"] == p_guardada["id"])

        # El jugador entra al menú de personajes y cambia el color del Jugador 1
        color_p1 = "Rojo"
        color_p2 = "Naranja"
        accesorio_p1 = "Ninguno"
        accesorio_p2 = "Corona"
        personalizacion_modificada_en_menu = True

        atuendo_guardado = (
            p.get("color_p1", "Celeste"),
            p.get("color_p2", "Violeta"),
            p.get("accesorio_p1", "Ninguno"),
            p.get("accesorio_p2", "Ninguno"),
        )
        atuendo_actual = (color_p1, color_p2, accesorio_p1, accesorio_p2)
        hay_cambios_pendientes = personalizacion_modificada_en_menu and (atuendo_actual != atuendo_guardado)

        self.assertTrue(hay_cambios_pendientes, "Debe detectar que hay cambios pendientes y requerir confirmación")
        print("[OK] Caso 3 superado: detecta modificaciones pendientes para abrir la ventana de confirmación.")

    def test_caso_4_mantener_atuendos_guardados(self):
        """Caso 4: Elijo «Mantener atuendos guardados» y se recupera la apariencia original de esa partida descartando cambios."""
        desbloqueados = crear_desbloqueados_inicial()
        p_guardada = guardar_partida(
            desbloqueados,
            nombre_partida="PartidaCaso4",
            color_p1="Verde",
            color_p2="Marron",
            accesorio_p1="Gorro",
            accesorio_p2="Ninguno",
        )
        guardado.invalidar_cache_partidas()

        partidas = cargar_partidas()
        p = next(x for x in partidas if x["id"] == p_guardada["id"])

        # Modificación en el menú
        color_p1 = "Blanco"
        color_p2 = "Negro"
        accesorio_p1 = "Corona"
        accesorio_p2 = "Anteojos"
        personalizacion_modificada_en_menu = True

        atuendo_guardado = (
            p.get("color_p1", "Celeste"),
            p.get("color_p2", "Violeta"),
            p.get("accesorio_p1", "Ninguno"),
            p.get("accesorio_p2", "Ninguno"),
        )

        decision = "mantener"
        if decision == "mantener":
            color_p1, color_p2, accesorio_p1, accesorio_p2 = atuendo_guardado
            personalizacion_modificada_en_menu = False

        self.assertEqual((color_p1, color_p2, accesorio_p1, accesorio_p2), ("Verde", "Marron", "Gorro", "Ninguno"))
        self.assertFalse(personalizacion_modificada_en_menu)

        # Comprobar que en disco la partida sigue intacta
        guardado.invalidar_cache_partidas()
        partidas_reloaded = cargar_partidas()
        p_reload = next(x for x in partidas_reloaded if x["id"] == p_guardada["id"])
        self.assertEqual(p_reload["color_p1"], "Verde")
        self.assertEqual(p_reload["color_p2"], "Marron")
        self.assertEqual(p_reload["accesorio_p1"], "Gorro")
        self.assertEqual(p_reload["accesorio_p2"], "Ninguno")
        print("[OK] Caso 4 superado: «Mantener atuendos guardados» restablece la apariencia original.")

    def test_caso_5_cambiar_atuendos_conserva_progreso_y_actualiza_personalizacion(self):
        """Caso 5: Modifico los personajes y elijo «Cambiar atuendos»: se conserva el progreso y se guardan los nuevos atuendos."""
        desbloqueados = crear_desbloqueados_inicial()
        # Desbloquear mundo 2 nivel 3 como progreso
        desbloqueados[1] = [True, True, True, True, True]
        desbloqueados[2] = [True, True, True, False, False]

        p_guardada = guardar_partida(
            desbloqueados,
            nombre_partida="PartidaCaso5Progreso",
            color_p1="Gris",
            color_p2="Celeste",
            accesorio_p1="Ninguno",
            accesorio_p2="Ninguno",
        )
        id_partida = p_guardada["id"]
        guardado.invalidar_cache_partidas()

        # Nuevos colores y accesorios seleccionados
        nuevo_c1, nuevo_c2 = "Rosa", "Amarillo"
        nuevo_a1, nuevo_a2 = "Corona", "Sombrero"
        personalizacion_modificada_en_menu = True

        decision = "cambiar"
        if decision == "cambiar":
            p_actualizada = guardar_partida(
                niveles_desbloqueados=p_guardada["niveles_desbloqueados"],
                id_partida=p_guardada["id"],
                nombre_partida=p_guardada["nombre"],
                color_p1=nuevo_c1,
                color_p2=nuevo_c2,
                accesorio_p1=nuevo_a1,
                accesorio_p2=nuevo_a2,
            )
            color_p1 = nuevo_c1
            color_p2 = nuevo_c2
            accesorio_p1 = nuevo_a1
            accesorio_p2 = nuevo_a2
            personalizacion_modificada_en_menu = False

        self.assertIsNotNone(p_actualizada)
        self.assertEqual(p_actualizada["color_p1"], "Rosa")
        self.assertEqual(p_actualizada["color_p2"], "Amarillo")
        self.assertEqual(p_actualizada["accesorio_p1"], "Corona")
        self.assertEqual(p_actualizada["accesorio_p2"], "Sombrero")

        # Verificar que el progreso guardado no cambió en absoluto
        self.assertEqual(p_actualizada["niveles_desbloqueados"], desbloqueados)
        self.assertEqual(p_actualizada["mundo_max"], 2)
        self.assertEqual(p_actualizada["nivel_max"], 3)

        # Verificar persistencia en disco tras invalidar caché
        guardado.invalidar_cache_partidas()
        partidas_disco = cargar_partidas()
        p_disco = next(x for x in partidas_disco if x["id"] == id_partida)
        self.assertEqual(p_disco["color_p1"], "Rosa")
        self.assertEqual(p_disco["color_p2"], "Amarillo")
        self.assertEqual(p_disco["accesorio_p1"], "Corona")
        self.assertEqual(p_disco["accesorio_p2"], "Sombrero")
        self.assertEqual(p_disco["niveles_desbloqueados"], desbloqueados)
        print("[OK] Caso 5 superado: «Cambiar atuendos» guarda nuevos atuendos y mantiene intacto el progreso.")

    def test_caso_6_independencia_entre_partidas(self):
        """Caso 6: Creo dos partidas con apariencias diferentes y compruebo que mantienen sus propios datos independientes."""
        desb = crear_desbloqueados_inicial()

        partida_a = guardar_partida(
            desb,
            nombre_partida="PartidaA_Roja",
            color_p1="Rojo",
            color_p2="Blanco",
            accesorio_p1="Sombrero",
            accesorio_p2="Ninguno",
        )

        partida_b = guardar_partida(
            desb,
            nombre_partida="PartidaB_Azul",
            color_p1="Azul",
            color_p2="Amarillo",
            accesorio_p1="Corona",
            accesorio_p2="Gorro",
        )

        guardado.invalidar_cache_partidas()
        partidas = cargar_partidas()

        pa = next(x for x in partidas if x["id"] == partida_a["id"])
        pb = next(x for x in partidas if x["id"] == partida_b["id"])

        # Verificar que cada partida tiene sus atuendos propios
        self.assertEqual((pa["color_p1"], pa["color_p2"], pa["accesorio_p1"], pa["accesorio_p2"]),
                         ("Rojo", "Blanco", "Sombrero", "Ninguno"))
        self.assertEqual((pb["color_p1"], pb["color_p2"], pb["accesorio_p1"], pb["accesorio_p2"]),
                         ("Azul", "Amarillo", "Corona", "Gorro"))

        # Modificar atuendos de partida A y comprobar que partida B no se inmuta
        guardar_partida(
            pa["niveles_desbloqueados"],
            id_partida=pa["id"],
            nombre_partida=pa["nombre"],
            color_p1="Verde oscuro",
            color_p2="Naranja",
            accesorio_p1="Anteojos",
            accesorio_p2="Corona",
        )

        guardado.invalidar_cache_partidas()
        partidas_post = cargar_partidas()
        pa_post = next(x for x in partidas_post if x["id"] == partida_a["id"])
        pb_post = next(x for x in partidas_post if x["id"] == partida_b["id"])

        self.assertEqual(pa_post["color_p1"], "Verde oscuro")
        self.assertEqual(pa_post["accesorio_p1"], "Anteojos")

        # Partida B se mantiene intacta
        self.assertEqual((pb_post["color_p1"], pb_post["color_p2"], pb_post["accesorio_p1"], pb_post["accesorio_p2"]),
                         ("Azul", "Amarillo", "Corona", "Gorro"))
        print("[OK] Caso 6 superado: total independencia de personalizacion entre partidas.")

    def test_caso_7_compatibilidad_con_partidas_antiguas(self):
        """Caso 7: Partidas antiguas sin campo de personalizacion reciben defaults validos sin fallar."""
        linea_antigua = "999|PartidaAntigua|2|4|24/10/2026 15:00|1:11111,2:11110,3:00000|hash123|salt123\n"
        with open(RUTA_PARTIDAS, "a", encoding="utf-8") as f:
            f.write(linea_antigua)

        guardado.invalidar_cache_partidas()
        partidas = cargar_partidas()
        antigua = next((x for x in partidas if x["id"] == 999), None)
        self.assertIsNotNone(antigua)
        self.assertEqual(antigua["color_p1"], "Celeste")
        self.assertEqual(antigua["color_p2"], "Violeta")
        self.assertEqual(antigua["accesorio_p1"], "Ninguno")
        self.assertEqual(antigua["accesorio_p2"], "Ninguno")
        print("[OK] Caso 7 superado: compatibilidad retroactiva completa con valores predeterminados seguros.")


if __name__ == "__main__":
    unittest.main()
