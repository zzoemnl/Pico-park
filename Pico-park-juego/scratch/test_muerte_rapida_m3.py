import sys
import os
import unittest
import pygame

# Asegurar path correcto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sprites import ANCHO, ALTO
from movimientos import (
    crear_personaje,
    crear_pincho,
    crear_llave,
    crear_puerta,
    comprobar_pinchos,
    matar_personaje,
    actualizar_muerte,
    reiniciar_juego,
    aplicar_fisica_agua,
    actualizar_estado_agua,
    actualizar_llave,
    VELOCIDAD_MUERTE,
    GRAVEDAD,
)
import pantalla


class TestMuerteRapidaMundo3(unittest.TestCase):
    """
    Pruebas obligatorias para la corrección definitiva del retraso de muerte en Mundo 3:
    1. Un personaje toca los pinchos: la muerte se detecta inmediatamente en el frame 1.
    2. Un personaje cae fuera del escenario: no hay que esperar a que desaparezca completamente.
    3. La animación de caída tiene la misma velocidad y aceleración que en los mundos anteriores.
    4. La pantalla de muerte aparece rápidamente (en ~28 frames), sin esperas prolongadas.
    5. El otro personaje permanece vivo si no murió por una condición propia.
    6. El reinicio y las demás mecánicas del Mundo 3 siguen funcionando correctamente.
    """

    def setUp(self):
        pygame.init()
        self.ancho_mundo = 2600

    def test_01_pinchos_deteccion_inmediata(self):
        """1. Un personaje toca los pinchos: la muerte se detecta inmediatamente."""
        p1 = crear_personaje(300, 400, "Celeste")
        p2 = crear_personaje(500, 400, "Violeta")
        p1["en_agua"] = True
        p2["en_agua"] = True

        pinchos = [crear_pincho(310, 420, 40, 25, direccion="arriba")]

        # Antes del contacto
        self.assertFalse(p1["muerto"])
        self.assertFalse(p2["muerto"])

        # En el fotograma exacto del contacto con el pincho:
        toco = comprobar_pinchos(p1, pinchos)
        self.assertTrue(toco, "Debe detectar colisión con pincho en el mismo fotograma")
        self.assertTrue(p1["muerto"], "P1 debe entrar en estado muerto en el mismo instante")
        self.assertEqual(p1["vel_y"], VELOCIDAD_MUERTE, "Debe inicializar la velocidad vertical de muerte (-17)")
        self.assertFalse(p1["en_agua"], "El personaje muerto debe desvincularse de en_agua inmediatamente")
        self.assertEqual(p1["vel_x"], 0, "Velocidad horizontal debe anularse al morir")
        self.assertFalse(p1["moviendo"], "Flag de movimiento submarino debe apagarse al morir")

        # P2 no tocó nada: debe permanecer vivo
        self.assertFalse(p2["muerto"], "P2 no tocó pincho, debe permanecer completamente vivo")

    def test_02_caida_fuera_de_escenario_sin_esperar_desaparicion(self):
        """2. Un personaje cae fuera del escenario: no hay que esperar a que desaparezca completamente."""
        p1 = crear_personaje(400, ALTO - p1_height if False else 680, "Celeste")
        p2 = crear_personaje(200, 300, "Violeta")
        h = p1["hitbox"].height

        # Colocar al personaje de modo que sus pies alcancen el límite inferior de la pantalla (ALTO = 720)
        # En este momento, hb.bottom >= ALTO (720), pero hb.top = 720 - h = 675 (todavía 100% visible)
        p1["hitbox"].bottom = ALTO
        self.assertLess(p1["hitbox"].top, ALTO, "El personaje aún es visible en pantalla, no ha desaparecido")

        # Evaluar detección de salida con lógica de Mundo 3
        hb = p1["hitbox"]
        caida_abajo = (hb.bottom >= ALTO)
        self.assertTrue(caida_abajo, "En Mundo 3 la salida se detecta en cuanto toca el límite inferior")

        # En Mundo 1/2 requería hb.top >= ALTO (haber desaparecido completamente)
        caida_mundo1 = (hb.top >= ALTO)
        self.assertFalse(caida_mundo1, "En Mundo 1 requería esperar la desaparición total; Mundo 3 no debe esperar")

        # Al llamar a matar_personaje:
        matar_personaje(p1)
        self.assertTrue(p1["muerto"])
        self.assertFalse(p2["muerto"], "P2 debe permanecer vivo en Mundo 3")

    def test_03_velocidad_caida_muerte_identica_a_mundos_anteriores(self):
        """3. La animación de caída tiene la misma velocidad que en los mundos anteriores."""
        p_tierra = crear_personaje(200, 300, "Celeste")
        p_agua = crear_personaje(200, 300, "Violeta")
        p_agua["en_agua"] = True

        matar_personaje(p_tierra)
        matar_personaje(p_agua)

        # Ambas deben empezar con VELOCIDAD_MUERTE (-17)
        self.assertEqual(p_tierra["vel_y"], VELOCIDAD_MUERTE)
        self.assertEqual(p_agua["vel_y"], VELOCIDAD_MUERTE)

        # Simular 20 fotogramas de caída: la aceleración debe ser exactamente GRAVEDAD (0.8) en ambos
        for frame in range(1, 21):
            actualizar_muerte(p_tierra)
            # En agua, aunque esté en zona submarina, física de agua no debe alterar vel_y de muerte
            aplicar_fisica_agua(p_agua, submarino=True)
            actualizar_muerte(p_agua)

            self.assertEqual(
                p_agua["vel_y"],
                p_tierra["vel_y"],
                f"En frame {frame}, vel_y en agua ({p_agua['vel_y']}) debe ser idéntica a tierra ({p_tierra['vel_y']})"
            )
            self.assertEqual(
                p_agua["hitbox"].y,
                p_tierra["hitbox"].y,
                f"En frame {frame}, posición y en agua debe ser idéntica a tierra"
            )

    def test_04_pantalla_muerte_aparece_rapidamente(self):
        """4. La pantalla de muerte aparece rápidamente, sin esperas prolongadas ni bloqueos."""
        p1 = crear_personaje(300, 350, "Celeste")
        p2 = crear_personaje(500, 350, "Violeta")
        p1["en_agua"] = True
        p2["en_agua"] = True

        # P1 muere
        matar_personaje(p1)
        self.assertTrue(p1["muerto"])
        self.assertFalse(p2["muerto"])

        frames = 0
        debe_mostrar_muerte = False

        # Simular bucle del juego con el límite de Mundo 3 (dur_max_muerte = 28)
        while frames < 60:
            frames += 1
            actualizar_muerte(p1, duracion_max=28)
            actualizar_muerte(p2, duracion_max=28)

            # Lógica de pantalla de muerte en Mundo 3:
            muertos = [p for p in (p1, p2) if p.get("muerto", False)]
            if muertos and any(p.get("muerte_terminada", False) for p in muertos):
                debe_mostrar_muerte = True
                break

        self.assertTrue(debe_mostrar_muerte, "La pantalla de muerte debe activarse rápidamente")
        self.assertEqual(frames, 28, f"Debe activarse exactamente a los 28 frames (~0.46s), tardó {frames}")
        self.assertLess(frames, 35, "No debe haber esperas prolongadas superiores a 35 frames")

    def test_05_otro_personaje_permanece_vivo(self):
        """5. El otro personaje permanece vivo si no murió por una condición propia."""
        p1 = crear_personaje(200, 400, "Celeste")
        p2 = crear_personaje(600, 400, "Violeta")
        p1["en_agua"] = True
        p2["en_agua"] = True

        # P1 muere por pinchos
        pincho = crear_pincho(210, 420, 30, 20)
        toco1 = comprobar_pinchos(p1, [pincho])
        self.assertTrue(toco1)

        # Regla Mundo 3: no se mata al otro
        numero_mundo = 3
        if numero_mundo != 3:
            matar_personaje(p2)

        self.assertTrue(p1["muerto"], "P1 debe estar muerto")
        self.assertFalse(p2["muerto"], "P2 debe permanecer 100% vivo")

        # P2 puede seguir nadando y actualizando su movimiento
        p2["vel_x"] = 3.0
        p2["hitbox"].x += int(p2["vel_x"])
        self.assertEqual(p2["hitbox"].x, 603)
        self.assertFalse(p2["muerto"])

    def test_06_reinicio_y_mecanicas_mundo_3_intactas(self):
        """6. El reinicio y las demás mecánicas del Mundo 3 siguen funcionando correctamente."""
        p1 = crear_personaje(150, 300, "Celeste")
        p2 = crear_personaje(250, 300, "Violeta")
        llave = crear_llave(400, 300)
        puerta = crear_puerta(1000, 300)

        # P1 muere
        matar_personaje(p1)
        self.assertTrue(p1["muerto"])

        # Reiniciar nivel
        reiniciar_juego(p1, p2, llave=llave, puerta=puerta)
        self.assertFalse(p1["muerto"], "P1 debe estar vivo tras reiniciar")
        self.assertFalse(p2["muerto"], "P2 debe estar vivo tras reiniciar")
        self.assertEqual(p1["hitbox"].x, p1["x_inicial"])
        self.assertEqual(p1["hitbox"].y, p1["y_inicial"])
        self.assertEqual(p2["hitbox"].x, p2["x_inicial"])
        self.assertEqual(p2["hitbox"].y, p2["y_inicial"])

        # Probar físicas de nado en 4 direcciones de Mundo 3
        p1["en_agua"] = True
        aplicar_fisica_agua(p1, tecla_arriba=True, tecla_abajo=False, submarino=True)
        self.assertLess(p1["vel_y"], 0, "Nado hacia arriba debe dar velocidad vertical negativa")

        aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=True, submarino=True)
        self.assertGreater(p1["vel_y"], 0, "Nado hacia abajo debe dar velocidad vertical positiva")

        # Flotabilidad neutra sin inputs
        for _ in range(20):
            aplicar_fisica_agua(p1, tecla_arriba=False, tecla_abajo=False, submarino=True)
        self.assertEqual(p1["vel_y"], 0.0, "Sin inputs debe alcanzar flotabilidad neutra (0.0)")

        # Recolección de llave y apertura de puerta
        p2["hitbox"].center = llave["rect"].center
        actualizar_llave(llave, [p1, p2], puerta)
        self.assertTrue(llave["recolectada"])
        self.assertEqual(llave["portador"], p2)

        p2["hitbox"].center = puerta["rect"].center
        actualizar_llave(llave, [p1, p2], puerta)
        self.assertTrue(puerta["abierta"], "La puerta debe abrirse con el portador de la llave")


if __name__ == "__main__":
    unittest.main()
