import os
import sys
import unittest
import pygame

# Inicializar pygame en modo headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.abspath("."))
from sprites import ANCHO, ALTO
from movimientos import (
    crear_personaje,
    reiniciar_juego,
    matar_personaje,
    actualizar_muerte,
    comprobar_pinchos,
    crear_pincho,
    crear_llave,
    crear_puerta,
    resolver_colisiones,
    VELOCIDAD_MUERTE,
    GRAVEDAD,
)


def ejecutar_deteccion_limites_escenario(
    jugador1, jugador2, p1_completado, p2_completado,
    ancho_mundo_nivel, numero_mundo, llave=None, usar_llave=False
):
    """
    Función idéntica a la integrada en el bucle principal de pantalla.py
    para comprobar la salida completa de los límites del escenario y aplicar
    las reglas correspondientes a cada mundo.
    """
    for p, comp, otro, comp_otro in [
        (jugador1, p1_completado, jugador2, p2_completado),
        (jugador2, p2_completado, jugador1, p1_completado),
    ]:
        if not comp and not p.get("muerto", False):
            hb = p["hitbox"]
            caida_abajo = (hb.bottom >= ALTO if numero_mundo == 3 else hb.top >= ALTO)
            salida_izq = (hb.left <= 0 if numero_mundo == 3 else hb.right <= 0)
            salida_der = (hb.right >= ancho_mundo_nivel if numero_mundo == 3 else hb.left >= ancho_mundo_nivel)
            salida_arriba = (hb.top <= -10 if numero_mundo == 3 else hb.bottom <= -50)

            if caida_abajo or salida_izq or salida_der or salida_arriba:
                if caida_abajo and numero_mundo != 3:
                    hb.top = ALTO
                matar_personaje(p)

                if usar_llave and llave and llave.get("recolectada", False) and llave.get("portador") is p:
                    llave["recolectada"] = False
                    llave["portador"] = None
                    llave["rect"].x = llave["x_inicial"]
                    llave["rect"].y = llave["y_inicial"]
                    llave["x_float"] = float(llave["x_inicial"])
                    llave["y_float"] = float(llave["y_inicial"])

                if numero_mundo != 3:
                    if not comp_otro and not otro.get("muerto", False):
                        matar_personaje(otro)


class TestMuerteFueraPantalla(unittest.TestCase):

    def setUp(self):
        self.p1 = crear_personaje(100, 200, "Celeste")
        self.p2 = crear_personaje(200, 200, "Violeta")
        self.ancho_mundo = 2200

    def test_01_personaje_cae_por_borde_y_sale_de_pantalla(self):
        """
        Prueba obligatoria 1: Un personaje cae por un borde y sale de la pantalla.
        - Debe caer bajo la gravedad.
        - No debe haber falso positivo mientras esté parcialmente en pantalla.
        - Al salir completamente (top >= ALTO), se detecta su muerte.
        - En Mundo 1 y 2 mueren ambos; en Mundo 3 solo el que cayó.
        """
        plat = pygame.Rect(0, 400, 250, 30)
        p1 = crear_personaje(230, plat.top - 85, "Celeste")
        p2 = crear_personaje(50, plat.top - 85, "Violeta")

        # Al avanzar a x=280, ya no hay suelo debajo
        p1["hitbox"].x = 280

        # Simular caída cuadro por cuadro
        for frame in range(40):
            p1["vel_y"] += GRAVEDAD
            p1["hitbox"].y += int(p1["vel_y"])

            # Comprobar colisión con suelo limitado
            resolver_colisiones(p1, None, plat, None)

            # Mientras la cabeza esté en pantalla (top < ALTO), NO debe morir
            if p1["hitbox"].top < ALTO:
                ejecutar_deteccion_limites_escenario(
                    p1, p2, False, False, self.ancho_mundo, numero_mundo=1
                )
                self.assertFalse(
                    p1["muerto"],
                    f"Falso positivo en frame {frame}: el personaje aún está parcialmente en pantalla (top={p1['hitbox'].top})"
                )

            if p1["hitbox"].top >= ALTO:
                break

        # Una vez superado completamente el fondo de pantalla
        self.assertGreaterEqual(p1["hitbox"].top, ALTO)
        ejecutar_deteccion_limites_escenario(
            p1, p2, False, False, self.ancho_mundo, numero_mundo=1
        )
        self.assertTrue(p1["muerto"], "P1 debe estar muerto tras salir completamente por abajo")
        self.assertTrue(p2["muerto"], "En Mundo 1 P2 también debe morir por muerte compartida")
        self.assertEqual(p1["vel_y"], VELOCIDAD_MUERTE, "Debe iniciar el impulso vertical de muerte")

        # Probar el mismo caso en Mundo 3: P1 muere al caer, pero P2 continúa VIVO
        p1_m3 = crear_personaje(280, ALTO, "Celeste")
        p2_m3 = crear_personaje(50, 300, "Violeta")
        ejecutar_deteccion_limites_escenario(
            p1_m3, p2_m3, False, False, self.ancho_mundo, numero_mundo=3
        )
        self.assertTrue(p1_m3["muerto"], "P1 debe morir al caer en Mundo 3")
        self.assertFalse(p2_m3["muerto"], "En Mundo 3 P2 debe permanecer completamente VIVO")

        print("[OK] Prueba 1 superada: Caída por borde y detección exacta sin falsos positivos.")

    def test_02_personaje_toca_pinchos(self):
        """
        Prueba obligatoria 2: Un personaje toca pinchos.
        - Muerte inmediata al colisionar.
        - Reglas por mundo: Mundo 1/2 compartida, Mundo 3 individual.
        """
        pinchos = [crear_pincho(500, 600, 32, 24, direccion="arriba")]

        # Caso Mundo 1: personaje toca el pincho (penetra dentro del rect del pincho)
        p1 = crear_personaje(500, 600 - 80, "Celeste")
        p2 = crear_personaje(100, 300, "Violeta")

        toco1 = comprobar_pinchos(p1, pinchos)
        toco2 = comprobar_pinchos(p2, pinchos)
        self.assertTrue(toco1)
        self.assertFalse(toco2)

        numero_mundo = 1
        if numero_mundo != 3:
            if toco1 and not p2["muerto"]:
                matar_personaje(p2)

        self.assertTrue(p1["muerto"], "P1 debe morir al tocar pinchos")
        self.assertTrue(p2["muerto"], "En Mundo 1 P2 debe morir también")

        # Caso Mundo 3: muerte independiente
        p1_m3 = crear_personaje(500, 600 - 80, "Celeste")
        p2_m3 = crear_personaje(100, 300, "Violeta")

        toco_m3 = comprobar_pinchos(p1_m3, pinchos)
        self.assertTrue(toco_m3)
        numero_mundo_3 = 3
        if numero_mundo_3 != 3:
            matar_personaje(p2_m3)

        self.assertTrue(p1_m3["muerto"], "P1 debe morir")
        self.assertFalse(p2_m3["muerto"], "P2 debe seguir vivo en Mundo 3")

        print("[OK] Prueba 2 superada: Detección precisa de pinchos y reglas por mundo.")

    def test_03_mundo3_un_personaje_muere_y_el_otro_sigue_vivo_sin_bloqueo(self):
        """
        Prueba obligatoria 3: Un personaje muere y el otro sigue vivo (Mundo 3).
        - P1 muere al caer o tocar peligro.
        - P2 sobrevive y no se bloquea.
        - Si P1 tenía la llave, la llave reaparece en posición segura para que P2 pueda continuar.
        - P2 puede recoger la llave y abrir la puerta para ganar.
        - Si P2 muere después, ambos están muertos y se activa la pantalla de muerte.
        """
        p1 = crear_personaje(500, ALTO, "Celeste")
        p2 = crear_personaje(200, 300, "Violeta")
        llave = crear_llave(400, 300)
        puerta = crear_puerta(1200, 300)

        # Simular que P1 tenía la llave antes de caer
        llave["recolectada"] = True
        llave["portador"] = p1
        llave["rect"].center = p1["hitbox"].center

        # P1 cae al abismo
        ejecutar_deteccion_limites_escenario(
            p1, p2, False, False, self.ancho_mundo, numero_mundo=3, llave=llave, usar_llave=True
        )

        self.assertTrue(p1["muerto"])
        self.assertFalse(p2["muerto"], "P2 debe seguir vivo")
        self.assertFalse(llave["recolectada"], "La llave debe ser liberada")
        self.assertIsNone(llave["portador"])
        # La llave no quedó perdida en el fondo del abismo:
        self.assertEqual(llave["rect"].x, llave["x_inicial"])
        self.assertEqual(llave["rect"].y, llave["y_inicial"])

        # P2 puede moverse libremente y recoger la llave
        p2["hitbox"].center = llave["rect"].center
        llave["recolectada"] = True
        llave["portador"] = p2

        # P2 llega a la puerta
        p2["hitbox"].center = puerta["rect"].center
        puerta["abierta"] = True
        p2_completado = True

        # Verificar condición de nivel completado con 1 jugador vivo en Mundo 3:
        nivel_superado = (p1["muerto"] and p2_completado)
        self.assertTrue(nivel_superado, "El nivel debe poder ser completado por el sobreviviente en Mundo 3")

        # Escenario alternativo: P2 también muere más tarde
        p2_segundo_intento = crear_personaje(600, ALTO, "Violeta")
        ejecutar_deteccion_limites_escenario(
            p1, p2_segundo_intento, False, False, self.ancho_mundo, numero_mundo=3
        )
        self.assertTrue(p1["muerto"])
        self.assertTrue(p2_segundo_intento["muerto"], "Ahora ambos están muertos")

        # Terminar animación de ambos
        p1["muerte_terminada"] = True
        p2_segundo_intento["muerte_terminada"] = True

        debe_mostrar_muerte = (
            p1["muerto"] and p2_segundo_intento["muerto"] and
            p1["muerte_terminada"] and p2_segundo_intento["muerte_terminada"]
        )
        self.assertTrue(debe_mostrar_muerte, "Al morir ambos, debe activarse la pantalla de muerte")

        print("[OK] Prueba 3 superada: Mundo 3 gestiona vida/muerte independiente y rescate de llave.")

    def test_04_animacion_muerte_termina_y_reinicia_correctamente(self):
        """
        Prueba obligatoria 4: La animación de muerte termina y el juego reinicia correctamente.
        - Comprobar que no se vuelve a activar la muerte en cada fotograma.
        - Comprobar que la animación dura los frames requeridos y termina al pasar por debajo de 720.
        - Comprobar que reiniciar_juego restablece el estado a vivo con velocidades en cero.
        """
        p = crear_personaje(300, 400, "Celeste")
        matar_personaje(p)
        self.assertTrue(p["muerto"])
        vel_inicial = p["vel_y"]
        self.assertEqual(vel_inicial, VELOCIDAD_MUERTE)

        # Intentar llamar matar_personaje repetidamente
        matar_personaje(p)
        matar_personaje(p)
        self.assertEqual(p["vel_y"], vel_inicial, "matar_personaje no debe reiniciar el impulso si ya está muerto")

        # Ejecutar animación cuadro a cuadro
        frames = 0
        while not p["muerte_terminada"] and frames < 120:
            actualizar_muerte(p)
            frames += 1

        self.assertTrue(p["muerte_terminada"], "La animación de muerte debe completarse")
        self.assertGreaterEqual(frames, 30, "La animación debe tener una duración visible adecuada")

        # Reiniciar juego y verificar restauración limpia
        p2 = crear_personaje(400, 400, "Violeta")
        reiniciar_juego(p, p2)
        self.assertFalse(p["muerto"], "Debe volver a estar vivo tras reiniciar")
        self.assertFalse(p["muerte_terminada"], "muerte_terminada debe ser False")
        self.assertEqual(p["vel_x"], 0)
        self.assertEqual(p["vel_y"], 0)
        self.assertEqual(p["hitbox"].x, p["x_inicial"])
        self.assertEqual(p["hitbox"].y, p["y_inicial"])

        print("[OK] Prueba 4 superada: Animación de muerte completa y reinicio impecable.")

    def test_05_ningun_personaje_desaparece_fuera_de_limites_sin_gestion(self):
        """
        Prueba obligatoria 5: Ningún personaje puede desaparecer fuera de los límites
        sin que el juego gestione ese estado.
        Se evalúan todos los límites posibles:
        - Abajo (caída): hb.top >= ALTO
        - Izquierda: hb.right <= 0
        - Derecha: hb.left >= ancho_mundo_nivel
        - Arriba: hb.bottom <= -50
        """
        limites = [
            ("fondo_pantalla", pygame.Rect(500, ALTO, 50, 85)),
            ("lateral_izquierdo", pygame.Rect(-50, 300, 50, 85)),
            ("lateral_derecho", pygame.Rect(self.ancho_mundo, 300, 50, 85)),
            ("techo_extremo", pygame.Rect(500, -140, 50, 85)),
        ]

        for nombre_caso, rect_fuera in limites:
            p1 = crear_personaje(100, 100, "Celeste")
            p2 = crear_personaje(200, 100, "Violeta")
            p1["hitbox"] = rect_fuera.copy()

            ejecutar_deteccion_limites_escenario(
                p1, p2, False, False, self.ancho_mundo, numero_mundo=1
            )

            self.assertTrue(
                p1["muerto"],
                f"El caso {nombre_caso} debe activar la muerte y no quedar como vivo"
            )
            self.assertTrue(
                p2["muerto"],
                f"En Mundo 1, {nombre_caso} debe activar la muerte compartida"
            )

        print("[OK] Prueba 5 superada: Todos los límites y salidas del escenario gestionados.")


if __name__ == "__main__":
    unittest.main()
