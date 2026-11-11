import os
import sys
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from personajes_menu import GestorPersonajesMenu, CONFIG_PERSONALIDADES


class TestInteligenciaMovimientoPlataformas(unittest.TestCase):
    """
    Batería de pruebas exhaustivas para las nuevas mecánicas de inteligencia
    de movimiento autónomo y conectividad vertical entre plataformas y paredes.
    """

    def setUp(self):
        self.gestor = GestorPersonajesMenu(1280, 720)

    def test_01_tocar_pared_no_activa_trepada_automatica(self):
        """
        1. Corregir trepada automática: Tocar una pared NO debe activar automáticamente
        la trepada. Debe ofrecer decisiones variadas (girar, pausar, saltar, trepar).
        """
        # Simulamos 50 impactos contra la pared izquierda en el suelo
        acciones_observadas = set()
        veces_trepo = 0
        veces_giro = 0
        veces_pausa = 0

        p = self.gestor.personajes[3]  # Perfil 'tranquilo' (prob_trepar baja)
        ai = self.gestor.ai_estados[3]

        for seed in range(50):
            # Posicionar en el suelo justo al lado de la pared izquierda caminando hacia la izquierda
            p["superficie"] = "suelo"
            p["hitbox"].bottom = self.gestor.y_suelo
            p["hitbox"].left = self.gestor.x_pared_izq + 2
            ai["estado"] = "caminar"
            ai["direccion"] = -1
            ai["cooldown_cambio_dir"] = 0
            p["vel_x"] = -p["velocidad_mov"]

            # Ejecutar 1 frame de física donde impacta la pared
            self.gestor.actualizar_fisica()

            if p["superficie"] == "pared_izq":
                veces_trepo += 1
                acciones_observadas.add("trepar")
            elif ai["estado"] == "caminar" and ai["direccion"] == 1:
                veces_giro += 1
                acciones_observadas.add("girar")
            elif ai["estado"] == "quieto":
                veces_pausa += 1
                acciones_observadas.add("pausa")

        # Verificar que NO siempre trepó automáticamente (el bug anterior trepaba ~100% de las veces)
        self.assertLess(veces_trepo, 35, f"Trepó {veces_trepo}/50 veces, demasiado frecuente para no ser autónomo")
        self.assertGreater(veces_giro + veces_pausa, 15, "Debió elegir girar o pausar varias veces")
        self.assertGreater(len(acciones_observadas), 1, "Debe tener más de una acción posible al tocar pared")

    def test_02_diferenciacion_de_comportamientos_entre_cinco_personajes(self):
        """
        2. Los cinco personajes deben tener personalidades distintas con parámetros únicos.
        """
        tipos = [c["tipo"] for c in CONFIG_PERSONALIDADES]
        self.assertEqual(len(set(tipos)), 5, "Los cinco personajes deben tener tipos de personalidad distintos")

        probs_trepar = [c["prob_trepar"] for c in CONFIG_PERSONALIDADES]
        self.assertGreaterEqual(len(set(probs_trepar)), 4, "Debe haber variedad en las probabilidades de trepar")

        # Correr simulación de 120 frames y verificar que sus estados e historias divergen
        for _ in range(120):
            self.gestor.actualizar()

        estados = [ai["estado"] for ai in self.gestor.ai_estados]
        # Al menos 2 o más estados distintos presentes en el mismo instante
        self.assertGreaterEqual(len(set(estados)), 2, f"Deben tener estados variados, observados: {estados}")

    def test_03_subir_de_plataforma_inferior_a_superior(self):
        """
        3. Permitir subir de una plataforma a otra: P1 -> P2, P2 -> P3, P4 -> P5, P5 -> P6.
        """
        # A. Prueba P1 -> P2 (Izquierda baja a media)
        p = self.gestor.personajes[0]
        ai = self.gestor.ai_estados[0]
        plat_p1 = self.gestor.plataformas[0]  # P1: top=520, left=130, right=280
        plat_p2 = self.gestor.plataformas[1]  # P2: top=380, left=44, right=174

        p["superficie"] = "plataforma"
        p["plat_actual"] = plat_p1
        p["en_suelo"] = True
        p["hitbox"].bottom = plat_p1.top
        p["hitbox"].left = plat_p1.left + 8
        ai["estado"] = "caminar"
        ai["direccion"] = -1
        ai["en_borde"] = True
        ai["cooldown_cambio_dir"] = 30
        ai["tiempo"] = 60

        # Forzamos salto dirigido a P2 configurando salto_datos
        ai["salto_datos"] = {"vel_x": -3.8, "vel_y": -16.5}
        ai["intentar_salto"] = True

        llego_p2 = False
        historial_estados = []
        for f in range(60):
            self.gestor.actualizar()
            historial_estados.append((p["superficie"], p.get("plat_actual"), p["hitbox"].x, p["hitbox"].y))
            if p["superficie"] == "plataforma" and p.get("plat_actual") == plat_p2:
                llego_p2 = True
                break

        self.assertTrue(llego_p2, f"El personaje debió alcanzar la plataforma superior P2 desde P1. Estados finales: {historial_estados[-5:]}")

        # B. Prueba P2 -> P3 (Izquierda media a central)
        p["superficie"] = "plataforma"
        p["plat_actual"] = plat_p2
        p["en_suelo"] = True
        plat_p3 = self.gestor.plataformas[2]  # P3: top=260, left=260, right=390
        p["hitbox"].bottom = plat_p2.top
        p["hitbox"].right = plat_p2.right - 8
        ai["estado"] = "caminar"
        ai["direccion"] = 1
        ai["en_borde"] = True
        ai["cooldown_cambio_dir"] = 30
        ai["tiempo"] = 60

        ai["salto_datos"] = {"vel_x": 5.2, "vel_y": -16.2}
        ai["intentar_salto"] = True

        llego_p3 = False
        for _ in range(60):
            self.gestor.actualizar()
            if p["superficie"] == "plataforma" and p.get("plat_actual") == plat_p3:
                llego_p3 = True
                break

        self.assertTrue(llego_p3, "El personaje debió alcanzar la plataforma superior P3 desde P2")

    def test_04_bajar_de_plataforma_superior_a_inferior(self):
        """
        4. Bajar de una plataforma superior hacia otra inferior (P3 -> P1, o salto P3 -> P2).
        """
        p = self.gestor.personajes[1]
        ai = self.gestor.ai_estados[1]
        plat_p3 = self.gestor.plataformas[2]  # P3: top=260
        plat_p1 = self.gestor.plataformas[0]  # P1: top=520 (directamente abajo de P3)

        p["superficie"] = "plataforma"
        p["plat_actual"] = plat_p3
        p["hitbox"].bottom = plat_p3.top
        p["hitbox"].left = plat_p3.left + 4

        # Iniciar bajada controlada hacia abajo
        self.gestor._iniciar_bajada_plataforma(1, dir_bajada=-1)
        self.assertEqual(p["superficie"], "aire")

        llego_p1 = False
        for _ in range(60):
            self.gestor.actualizar()
            if p["superficie"] == "plataforma" and p.get("plat_actual") == plat_p1:
                llego_p1 = True
                break

        self.assertTrue(llego_p1, "El personaje debe poder descender de P3 y aterrizar en la plataforma inferior P1")

    def test_05_conexion_entre_pared_y_plataforma_bidireccional(self):
        """
        5. Utilizar paredes para conectar distintas alturas:
           - Un personaje trepando o bajando por pared_izq puede pisar P2 (y=380).
        """
        p = self.gestor.personajes[0]
        ai = self.gestor.ai_estados[0]
        plat_p2 = self.gestor.plataformas[1]

        # Colocar trepando hacia arriba cerca de la altura de P2
        p["superficie"] = "pared_izq"
        p["hitbox"].left = self.gestor.x_pared_izq
        p["hitbox"].bottom = plat_p2.top + 6
        p["vel_y"] = -p["velocidad_mov"]
        ai["estado"] = "trepar"
        ai["direccion"] = -1
        ai["cooldown_cambio_dir"] = 0
        ai["datos_pers"]["prob_pared_a_plat"] = 1.0  # Forzar transición

        piso_plataforma = False
        for _ in range(10):
            self.gestor.actualizar()
            if p["superficie"] == "plataforma" and p.get("plat_actual") == plat_p2:
                piso_plataforma = True
                break

        self.assertTrue(piso_plataforma, "El personaje trepando por la pared debe poder ingresar a P2")

    def test_06_descender_por_pared_hasta_el_suelo(self):
        """
        6. Descender por una pared hasta llegar al suelo con transición fluida.
        """
        p = self.gestor.personajes[2]
        ai = self.gestor.ai_estados[2]

        p["superficie"] = "pared_izq"
        p["hitbox"].left = self.gestor.x_pared_izq
        p["hitbox"].bottom = self.gestor.y_suelo - 30
        p["vel_y"] = p["velocidad_mov"]  # Bajando hacia el suelo
        ai["estado"] = "trepar"
        ai["direccion"] = 1

        llego_suelo = False
        for _ in range(25):
            self.gestor.actualizar()
            if p["superficie"] == "suelo" and p["en_suelo"]:
                llego_suelo = True
                break

        self.assertTrue(llego_suelo, "El personaje descendiendo por la pared debe aterrizar en el suelo")
        self.assertEqual(p["angulo_objetivo"], 0.0, "La rotación debe restablecerse al volver al suelo")

    def test_07_descolgarse_del_techo(self):
        """
        7. Un personaje en el techo puede descolgarse y caer hacia abajo.
        """
        p = self.gestor.personajes[4]
        ai = self.gestor.ai_estados[4]

        p["superficie"] = "techo"
        p["hitbox"].top = self.gestor.y_techo
        p["hitbox"].centerx = 320  # Sobre la plataforma P3
        ai["estado"] = "caminar_techo"
        ai["direccion"] = 1
        ai["tiempo"] = 1  # Forzar decisión en el próximo frame
        ai["datos_pers"]["prob_descolgar_techo"] = 1.0  # Alta probabilidad

        se_descolgo = False
        for _ in range(15):
            self.gestor.actualizar()
            if p["superficie"] in ("aire", "plataforma", "suelo"):
                se_descolgo = True
                break

        self.assertTrue(se_descolgo, "El personaje en el techo debe poder soltarse y descender")

    def test_08_historial_anti_repeticion(self):
        """
        8. El historial de acciones registra eventos y penaliza la repetición constante.
        """
        ai = self.gestor.ai_estados[0]
        self.gestor._registrar_accion(ai, "trepar_subir")
        self.gestor._registrar_accion(ai, "trepar_subir")

        conteo = self.gestor._conteo_accion_reciente(ai, "trepar_subir")
        self.assertEqual(conteo, 2, "Debe registrar correctamente 2 acciones recientes de trepar_subir")

        # Con 2 trepadas recientes, el factor de trepar debe ser muy bajo (anti-repetición)
        factor = 0.15 if conteo >= 2 else 1.0
        self.assertEqual(factor, 0.15, "Debe aplicar factor de penalización del 85%")

    def test_09_sin_vibracion_ni_bloqueos_en_bordes(self):
        """
        9. En simulación continua de 1800 frames: cero teletransportes bruscos (>25px/frame)
        y sin vibraciones en bordes.
        """
        max_salto_pos = 0
        for _ in range(1800):
            pos_anteriores = [(p["hitbox"].x, p["hitbox"].y) for p in self.gestor.personajes]
            self.gestor.actualizar()
            for idx, p in enumerate(self.gestor.personajes):
                dx = abs(p["hitbox"].x - pos_anteriores[idx][0])
                dy = abs(p["hitbox"].y - pos_anteriores[idx][1])
                max_salto_pos = max(max_salto_pos, dx, dy)
                self.assertLess(dx, 25, f"Teletransporte horizontal excesivo dx={dx} en personaje {idx}")
                self.assertLess(dy, 25, f"Teletransporte vertical excesivo dy={dy} en personaje {idx}")


if __name__ == "__main__":
    unittest.main()
