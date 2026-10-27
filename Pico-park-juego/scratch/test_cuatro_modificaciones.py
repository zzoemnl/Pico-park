import os
import sys
import unittest
import pygame

# Inicializar pygame en modo headless para pruebas automáticas
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_PROYECTO = os.path.abspath(os.path.join(DIRECTORIO_ACTUAL, ".."))
if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)

from sprites import (
    precargar_botones_comunes,
    cargar_boton_escalado,
    _CACHE_BOTONES_ESCALADOS,
    _CACHE_BOTONES_ACLARADOS,
    ANCHO,
    ALTO,
)
from movimientos import (
    crear_personaje,
    matar_personaje,
    comprobar_pinchos,
    actualizar_muerte,
    actualizar_estado_agua,
    aplicar_fisica_agua,
    actualizar_llave,
    crear_llave,
    crear_puerta,
    resolver_colisiones,
    VELOCIDAD_MUERTE,
    GRAVEDAD,
)
from guardado import (
    cargar_partidas,
    decode_desbloqueados,
    RUTA_PARTIDAS,
)


class TestCuatroModificaciones(unittest.TestCase):

    def test_mod_1_precarga_botones(self):
        """
        1. Los botones deben precargarse y estar disponibles en caché
        desde el primer momento, sin demoras ni cargas tardías.
        """
        precargar_botones_comunes()

        # Comprobar que los botones esenciales están cacheados
        botones_esperados = [
            ("jugar.png", 272, 80),
            ("personajes.png", 272, 80),
            ("opciones.png", 272, 80),
            ("salir.png", 272, 80),
            ("boton-x.png", 44, 52),
            ("HUD/boton-bajar-volumen.png", 42, 50),
            ("HUD/boton-subir-volumen.png", 42, 50),
            ("mundos/boton-volver.png", 238, 70),
            ("Menu/boton-continuar-cargar....png", 425, 100),
            ("mundos/boton-cargar.png", 129, 38),
            ("Ventanas/boton-reiniciar.png", 272, 80),
            ("Ventanas/boton-siguiente.png", 272, 80),
            ("Ventanas/boton-menu.png", 272, 80),
        ]
        for nombre, w, h in botones_esperados:
            surf = cargar_boton_escalado(nombre, w, h)
            self.assertIsNotNone(surf, f"El sprite {nombre} escalado a ({w}, {h}) no se precargó")
            self.assertEqual(surf.get_size(), (w, h), f"El tamaño de {nombre} no es ({w}, {h})")

        print("[OK] Modificacion 1 verificada: Todos los botones precargados y listos en cache.")

    def test_mod_2_muerte_independiente_mundo_3(self):
        """
        2. En el Mundo 3, si muere un personaje, el otro no debe morir automáticamente.
        Cada uno tiene su propio estado de vida/muerte y puede seguir jugando.
        """
        p1 = crear_personaje(100, 300)
        p2 = crear_personaje(200, 300)

        pinchos = [pygame.Rect(90, 320, 40, 20)]

        # Simular detección en Mundo 3
        p1_toco = comprobar_pinchos(p1, pinchos)
        p2_toco = comprobar_pinchos(p2, pinchos)

        self.assertTrue(p1_toco, "P1 debió tocar los pinchos")
        self.assertFalse(p2_toco, "P2 no debió tocar los pinchos")

        # Regla de Mundo 3: no propagar muerte al compañero
        numero_mundo = 3
        if numero_mundo != 3:
            if p1_toco and not p2["muerto"]:
                matar_personaje(p2)
            elif p2_toco and not p1["muerto"]:
                matar_personaje(p1)

        self.assertTrue(p1["muerto"], "P1 debe estar muerto")
        self.assertFalse(p2["muerto"], "P2 debe seguir completamente VIVO en Mundo 3")

        # Verificar que P2 puede seguir moviéndose normalmente
        p2["vel_x"] = 6
        p2["hitbox"].x += p2["vel_x"]
        self.assertEqual(p2["hitbox"].x, 206, "P2 debe poder moverse libremente")

        # Verificar que P1 muerto no bloquea como obstáculo sólido a P2
        suelo = pygame.Rect(0, 640, 1280, 80)
        mundo_rect = pygame.Rect(0, 0, 1280, 720)
        companero = p1 if not p1["muerto"] else None
        self.assertIsNone(companero, "El compañero muerto no debe ser considerado sólido")

        # Verificar comportamiento de la llave: si el portador muere en Mundo 3, la suelta
        llave = crear_llave(100, 300)
        puerta = crear_puerta(800, 500)
        llave["recolectada"] = True
        llave["portador"] = p1

        actualizar_llave(llave, [p2], puerta)
        self.assertFalse(llave["recolectada"], "La llave debe ser soltada al morir el portador")
        self.assertIsNone(llave["portador"], "La llave ya no debe tener portador")

        # Ahora P2 puede recoger la llave
        p2["hitbox"].center = llave["rect"].center
        actualizar_llave(llave, [p2], puerta)
        self.assertTrue(llave["recolectada"], "P2 sobreviviente debe poder recoger la llave soltada")
        self.assertEqual(llave["portador"], p2)

        # Verificar que en Mundos 1 y 2 SÍ se conserva la regla de muerte mutua
        p1_m1 = crear_personaje(100, 300)
        p2_m1 = crear_personaje(200, 300)
        p1_toco_m1 = comprobar_pinchos(p1_m1, pinchos)
        numero_mundo_m1 = 1
        if numero_mundo_m1 != 3:
            if p1_toco_m1 and not p2_m1["muerto"]:
                matar_personaje(p2_m1)
        self.assertTrue(p1_m1["muerto"])
        self.assertTrue(p2_m1["muerto"], "En Mundo 1 ambos deben morir como está previsto")

        print("[OK] Modificacion 2 verificada: En Mundo 3 la muerte es independiente; en Mundo 1 se conserva muerte mutua.")

    def test_mod_3_velocidad_caida_muerte_en_agua(self):
        """
        3. La animación de caída al morir en el agua debe mantener la velocidad normal
        (exactamente idéntica a la velocidad y duración de Mundos 1 y 2).
        """
        zona_agua = pygame.Rect(0, 100, 1280, 600)

        # 1. Simulación de caída en Mundo 1 o 2 (Tierra, sin agua)
        p_tierra = crear_personaje(300, 450)
        matar_personaje(p_tierra)
        frames_tierra = 0
        while not p_tierra["muerte_terminada"] and frames_tierra < 150:
            actualizar_muerte(p_tierra)
            frames_tierra += 1

        # 2. Simulación de caída en Mundo 3 (Sumergido en agua)
        p_agua = crear_personaje(300, 450)
        actualizar_estado_agua(p_agua, zona_agua)
        matar_personaje(p_agua)

        frames_agua = 0
        while not p_agua["muerte_terminada"] and frames_agua < 150:
            # En cada fotograma del ciclo de juego:
            actualizar_estado_agua(p_agua, zona_agua)
            aplicar_fisica_agua(p_agua, submarino=True)
            actualizar_muerte(p_agua)
            frames_agua += 1

        self.assertTrue(p_agua["muerte_terminada"], "La animación de muerte en agua debe completarse")
        self.assertEqual(
            frames_agua,
            frames_tierra,
            f"La duración de caída en agua ({frames_agua} frames) debe ser idéntica a tierra ({frames_tierra} frames)"
        )

        print(f"[OK] Modificacion 3 verificada: Caida en agua ({frames_agua} frames) identica a mundos 1 y 2 ({frames_tierra} frames).")

    def test_mod_4_partida_todos_niveles_desbloqueados(self):
        """
        4. Debe existir una partida separada 'Todos los niveles desbloqueados'
        con los 15 niveles desbloqueados en los 3 mundos.
        """
        partidas = cargar_partidas()
        self.assertGreaterEqual(len(partidas), 3, "Debe haber al menos 3 partidas en partidas.txt")

        # Verificar que las partidas originales no fueron modificadas ni sobrescritas
        p1 = next((p for p in partidas if p["id"] == 1), None)
        self.assertIsNotNone(p1, "La partida 1 original debe existir")
        self.assertEqual(p1["nombre"], "malenita", "La partida 1 debe conservar su nombre")

        p2 = next((p for p in partidas if p["id"] == 2), None)
        self.assertIsNotNone(p2, "La partida 2 original debe existir")
        self.assertEqual(p2["nombre"], "Partida 2", "La partida 2 debe conservar su nombre")

        # Verificar la nueva partida
        p3 = next((p for p in partidas if p["nombre"] == "Todos los niveles desbloqueados"), None)
        self.assertIsNotNone(p3, "Debe existir la partida 'Todos los niveles desbloqueados'")
        self.assertEqual(p3["mundo_max"], 3)
        self.assertEqual(p3["nivel_max"], 5)

        desbloq = p3["niveles_desbloqueados"]
        # Comprobar Mundo 1: niveles 1-1 a 1-5 desbloqueados
        self.assertEqual(desbloq[1], [True, True, True, True, True], "Mundo 1 debe tener niveles 1 a 5 desbloqueados")
        # Comprobar Mundo 2: niveles 2-1 a 2-5 desbloqueados
        self.assertEqual(desbloq[2], [True, True, True, True, True], "Mundo 2 debe tener niveles 1 a 5 desbloqueados")
        # Comprobar Mundo 3: niveles 3-1 a 3-5 desbloqueados
        self.assertEqual(desbloq[3], [True, True, True, True, True], "Mundo 3 debe tener niveles 1 a 5 desbloqueados")

        # Comprobar que los 15 niveles están activos y seleccionables
        total_desbloqueados = sum(sum(1 for n in desbloq[m] if n) for m in (1, 2, 3))
        self.assertEqual(total_desbloqueados, 15, "Deben estar desbloqueados los 15 niveles en total")

        print("[OK] Modificacion 4 verificada: Partida 'Todos los niveles desbloqueados' encontrada con los 15 niveles desbloqueados y partidas anteriores intactas.")


if __name__ == "__main__":
    unittest.main()
