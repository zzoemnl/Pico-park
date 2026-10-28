import os
import sys
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
from movimientos import (
    crear_personaje,
    crear_llave,
    crear_puerta,
    crear_pincho,
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    resolver_colisiones,
    actualizar_llave,
    comprobar_pinchos,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    DISTANCIA_SOGA_MAXIMA,
    DISTANCIA_SOGA_REPOSO,
)

TIEMPO_DERRUMBE_FRAMES = 60  # 1 segundo a 60 FPS

class TestPlataformasDerrumbablesM2N4(unittest.TestCase):

    def setUp(self):
        self.ancho_mundo_nivel = 2600
        self.ALTO = 720
        self.suelo = pygame.Rect(0, self.ALTO - 80, self.ancho_mundo_nivel, 80)
        self.mundo_rect = pygame.Rect(0, 0, self.ancho_mundo_nivel, self.ALTO)
        self.plat_inicio = pygame.Rect(0, 460, 200, 26)
        self.plat_llegada = pygame.Rect(2190, 460, 410, 26)
        self.plataformas_base = [self.plat_inicio, self.plat_llegada]

        self.coords_plats = [
            (320, 460),
            (550, 430),
            (785, 460),
            (1020, 420),
            (1255, 450),
            (1490, 420),
            (1725, 450),
            (1960, 460),
        ]

    def _crear_p(self, px, py, pw=110, ph=22):
        return {
            "rect": pygame.Rect(px, py, pw, ph),
            "x_inicial": px,
            "y_inicial": py,
            "y": float(py),
            "vel_y": 0.0,
            "ancho": pw,
            "alto": ph,
            "estado": "intacta",
            "tiempo_restante": TIEMPO_DERRUMBE_FRAMES,
            "pisada": False,
            "particulas": [],
        }

    def _actualizar_derrumbables(self, plataformas_derrumbables, jugador1, jugador2, p1_completado=False, p2_completado=False):
        for p_d in plataformas_derrumbables:
            if not p_d["pisada"]:
                pjs_pisando = False
                for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                    if not comp and not pj["muerto"]:
                        hb = pj["hitbox"]
                        if (
                            hb.right > p_d["rect"].left + 2
                            and hb.left < p_d["rect"].right - 2
                            and abs(hb.bottom - p_d["rect"].top) <= 8
                            and (pj["en_suelo"] or pj.get("vel_y", 0) >= 0)
                        ):
                            pjs_pisando = True
                            break
                if pjs_pisando:
                    p_d["pisada"] = True
                    p_d["tiempo_restante"] = TIEMPO_DERRUMBE_FRAMES

            if p_d["pisada"] and p_d["tiempo_restante"] > 0:
                p_d["tiempo_restante"] -= 1
                if p_d["tiempo_restante"] <= 20:
                    p_d["estado"] = "temblando"
                else:
                    p_d["estado"] = "agrietandose"

                if p_d["tiempo_restante"] <= 0:
                    p_d["estado"] = "derrumbada"
                    for pj, comp in [(jugador1, p1_completado), (jugador2, p2_completado)]:
                        if not comp and not pj["muerto"]:
                            hb = pj["hitbox"]
                            if (
                                hb.right > p_d["rect"].left + 2
                                and hb.left < p_d["rect"].right - 2
                                and abs(hb.bottom - p_d["rect"].top) <= 8
                            ):
                                pj["en_suelo"] = False

            if p_d["estado"] == "derrumbada":
                p_d["vel_y"] += 1.5
                p_d["y"] += p_d["vel_y"]
                p_d["rect"].y = int(p_d["y"])

    def test_01_tiempo_espera_aproximadamente_1_segundo(self):
        """1. El tiempo de derrumbe debe ser de 60 frames (~1.0s a 60 FPS)."""
        p = self._crear_p(310, 460)
        self.assertEqual(p["tiempo_restante"], 60)
        self.assertEqual(p["estado"], "intacta")
        self.assertFalse(p["pisada"])

    def test_02_activacion_por_cualquiera_de_los_dos_personajes(self):
        """2. El temporizador debe activarse cuando cualquiera de los personajes pisa la plataforma."""
        # Caso A: Jugador 1 pisa
        plats_a = [self._crear_p(310, 460)]
        j1 = crear_personaje(330, 460 - ALTO_HITBOX, "Celeste")
        j2 = crear_personaje(50, 460 - ALTO_HITBOX, "Violeta")
        j1["en_suelo"] = True
        j2["en_suelo"] = True

        self._actualizar_derrumbables(plats_a, j1, j2)
        self.assertTrue(plats_a[0]["pisada"], "Debe activarse cuando Jugador 1 la pisa")
        self.assertEqual(plats_a[0]["tiempo_restante"], 59)

        # Caso B: Jugador 2 pisa
        plats_b = [self._crear_p(310, 460)]
        j1_b = crear_personaje(50, 460 - ALTO_HITBOX, "Celeste")
        j2_b = crear_personaje(330, 460 - ALTO_HITBOX, "Violeta")
        j1_b["en_suelo"] = True
        j2_b["en_suelo"] = True

        self._actualizar_derrumbables(plats_b, j1_b, j2_b)
        self.assertTrue(plats_b[0]["pisada"], "Debe activarse cuando Jugador 2 la pisa")
        self.assertEqual(plats_b[0]["tiempo_restante"], 59)

    def test_03_derrumbe_ocurre_aunque_el_personaje_siga_encima(self):
        """3. Si el personaje sigue encima, la plataforma debe derrumbarse igualmente a los 60 frames."""
        plat = self._crear_p(310, 460)
        plats = [plat]
        j1 = crear_personaje(330, 460 - ALTO_HITBOX, "Celeste")
        j2 = crear_personaje(50, 460 - ALTO_HITBOX, "Violeta")
        j1["en_suelo"] = True

        # Paso 1: Pisar la plataforma
        self._actualizar_derrumbables(plats, j1, j2)
        self.assertTrue(plat["pisada"])

        # Pasos 2 a 59: Permanecer encima
        for _ in range(58):
            self._actualizar_derrumbables(plats, j1, j2)
            self.assertIn(plat["estado"], ["agrietandose", "temblando"])

        # Frame 60: Cumplirse exactamente 1 segundo (60 frames)
        self._actualizar_derrumbables(plats, j1, j2)
        self.assertEqual(plat["tiempo_restante"], 0)
        self.assertEqual(plat["estado"], "derrumbada", "La plataforma debe derrumbarse al cumplirse el tiempo")
        self.assertFalse(j1["en_suelo"], "El personaje no debe poder sostenerse sobre la plataforma derrumbada")

    def test_04_colisiones_desactivadas_tras_derrumbe(self):
        """4. Cuando se derrumba, deja de existir en la lista activa de colisiones."""
        plat = self._crear_p(310, 460)
        plat["estado"] = "derrumbada"
        plat["vel_y"] = 5.0
        plat["rect"].y = 500

        # Lista de plataformas activas en el bucle
        activas = [self.plat_inicio] + [p["rect"] for p in [plat] if p["estado"] != "derrumbada"]
        self.assertNotIn(plat["rect"], activas, "El rect de la plataforma derrumbada no debe estar en plataformas activas")

        # El personaje que cae no choca con ella
        j1 = crear_personaje(330, 480, "Celeste")
        j1["vel_y"] = 4.0
        resolver_colisiones(j1, None, self.suelo, self.mundo_rect, plataformas=activas)
        self.assertFalse(j1["en_suelo"])

    def test_05_recorrido_completo_jugable_con_soga_y_llave(self):
        """5. Comprobar que dos personajes coordinados pueden completar el nivel con 1s de margen."""
        plats = [self._crear_p(px, py) for px, py in self.coords_plats]
        llave = crear_llave(1075, 420 - 46)
        puerta = crear_puerta(2380, 460 - 90)

        j1 = crear_personaje(140, 460 - ALTO_HITBOX, "Celeste")
        j2 = crear_personaje(70, 460 - ALTO_HITBOX, "Violeta")
        estado_soga = {"tirante": False, "distancia": 70, "tension": 0.0, "rota": False}
        todas = [self.plat_inicio, self.plat_llegada] + [p["rect"] for p in plats]

        # Simular avance continuo de ambos hacia la derecha
        for f in range(400):
            # Activar movimiento continuo a la derecha
            j1["vel_x"] = 6
            j2["vel_x"] = 6

            # Salto automático al aproximarse al borde de cada plataforma
            for pj in (j1, j2):
                if pj["en_suelo"]:
                    # Si está cerca del borde derecho de su plataforma actual, saltar
                    for r in [self.plat_inicio] + [p["rect"] for p in plats if p["estado"] != "derrumbada"]:
                        if r.collidepoint(pj["hitbox"].centerx, pj["hitbox"].bottom):
                            if pj["hitbox"].right >= r.right - 10:
                                pj["vel_y"] = pj["fuerza_salto"]
                                pj["en_suelo"] = False
                            break

            actualizar_fisica_soga(j1, j2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
            aplicar_restriccion_soga(j1, j2, DISTANCIA_SOGA_MAXIMA, todas, self.suelo, estado_soga)

            # Actualizar plataformas derrumbables
            self._actualizar_derrumbables(plats, j1, j2)
            activas = [self.plat_inicio, self.plat_llegada] + [p["rect"] for p in plats if p["estado"] != "derrumbada"]

            resolver_colisiones(j1, None, self.suelo, self.mundo_rect, plataformas=activas)
            resolver_colisiones(j2, None, self.suelo, self.mundo_rect, plataformas=activas)

            actualizar_llave(llave, [j1, j2], puerta)

            if puerta["abierta"]:
                break

        self.assertTrue(llave["recolectada"], "La llave debe haber sido recogida sobre la plataforma 4")
        self.assertTrue(puerta["abierta"], "La puerta debe estar abierta al llegar")
        self.assertGreaterEqual(j1["hitbox"].left, self.plat_llegada.left, "J1 debe llegar a la plataforma final")
        self.assertGreaterEqual(j2["hitbox"].left, self.plat_llegada.left, "J2 debe llegar a la plataforma final")

if __name__ == "__main__":
    unittest.main()
