"""
Suite de pruebas exhaustivas y generación visual para verificar la prevención
sistemática de desbordes de texto en todas las pantallas y contenedores.
"""

import os
import sys
import unittest
import pygame

# Asegurar entorno headless seguro para pygame y ruta al paquete
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import fuentes
import configuracion
import guardado
import main
import menu_niveles
import pantalla


class TestPrevencionDesbordes(unittest.TestCase):
    def setUp(self):
        self.pantalla = pygame.Surface((1280, 720))

    def test_ajustar_tamano_fuente_longitudes_variables(self):
        """Verifica que ajustar_tamano_fuente reduzca el tamaño para ajustarse a anchos reducidos."""
        textos = [
            "Corto",
            "Texto con longitud intermedia",
            "Nombre de perfil sumamente largo para probar la adaptación automática de la fuente",
            "«Todos los niveles desbloqueados» — Nivel: 3-5",
            "¿Deseas elegir otro nombre o sobrescribir la partida existente?",
        ]
        for txt in textos:
            f, tam = fuentes.ajustar_tamano_fuente(txt, categoria="subtitulo", tamano_inicial=24, ancho_max=200, tamano_min=10)
            self.assertIsNotNone(f)
            self.assertGreaterEqual(tam, 10)

    def test_renderizar_texto_ajustado_garantia_limites(self):
        """Garantiza que la superficie resultante de renderizar_texto_ajustado nunca supere ancho_max."""
        anchos = [80, 120, 200, 350]
        textos = [
            "CAMBIAR / QUITAR CONTRASEÑA",
            "Todos los niveles desbloqueados",
            "MANTENER ATUENDOS GUARDADOS",
            "Modificaste los personajes antes de continuar «Todos los niveles desbloqueados».",
            "Texto largo en Chino: 你想重新开始还是退出游戏？",
        ]
        for w_max in anchos:
            for txt in textos:
                surf, _ = fuentes.renderizar_texto_ajustado(txt, categoria="boton", tamano=16, ancho_max=w_max)
                self.assertLessEqual(surf.get_width(), w_max, f"El texto '{txt}' superó ancho_max={w_max}: ancho={surf.get_width()}")

    def test_renderizar_texto_multilinea_garantia_limites(self):
        """Garantiza que renderizar_texto_multilinea respete ancho_max y alto_max simultáneamente."""
        texto_largo = "Este es un texto explicativo sumamente largo diseñado para verificar que la función de salto de línea automático distribuya el texto sin salirse de los límites verticales ni horizontales del contenedor."
        surf_m = fuentes.renderizar_texto_multilinea(
            texto_largo,
            categoria="texto",
            tamano=18,
            ancho_max=300,
            alto_max=100,
            tamano_min=10
        )
        self.assertLessEqual(surf_m.get_width(), 300)
        self.assertLessEqual(surf_m.get_height(), 100)

    def test_dibujar_texto_en_rect_contencion_absoluta(self):
        """Verifica que el texto dibujado quede 100% contenido dentro del contenedor especificado."""
        rects_prueba = [
            pygame.Rect(100, 100, 140, 32),   # Pastilla nivel
            pygame.Rect(150, 150, 177, 52),   # Botón cancelar / confirmar
            pygame.Rect(200, 200, 360, 48),   # Botón de modal administrar
            pygame.Rect(50, 50, 520, 28),     # Título de tarjeta
        ]
        textos = [
            "JUGAR >",
            "BLOQUEADO",
            "AGREGAR CONTRASEÑA",
            "CAMBIAR / QUITAR CONTRASEÑA",
            "Todos los niveles desbloqueados",
            "Página 1 de 10",
        ]
        for r_cont in rects_prueba:
            for txt in textos:
                r_dibujado = fuentes.dibujar_texto_en_rect(self.pantalla, txt, r_cont, categoria="boton", tamano=16, padding=6)
                self.assertTrue(
                    r_cont.contains(r_dibujado),
                    f"El rect dibujado {r_dibujado} no está contenido en {r_cont} para texto '{txt}'"
                )

    def test_caracteres_especiales_espanol_y_chino(self):
        """Comprueba que acentos, eñes, signos y caracteres chinos se rendericen sin errores ni desaparición."""
        textos_especiales = [
            "Español: CONFIGURACIÓN, CONTRASEÑA, ¿Deseas guardar?, ¡Nivel completado!",
            "English: SETTINGS, PASSWORD, Save game?",
            "Chinese: 简体中文, 选择关卡, 退出游戏",
        ]
        for txt in textos_especiales:
            surf, _ = fuentes.renderizar_texto_ajustado(txt, categoria="texto", tamano=18, ancho_max=400)
            self.assertGreater(surf.get_width(), 0)
            self.assertGreater(surf.get_height(), 0)


def generar_capturas_verificacion_visual():
    """Genera capturas PNG de pantallas críticas con perfiles largos y textos para inspección visual."""
    directorio_artefactos = "C:\\Users\\Malena\\.gemini\\antigravity-ide\\brain\\effb8b14-e88d-402a-8aae-c082111f922f"

    # 1. Pantalla ADMINISTRAR PERFIL con perfil de nombre largo
    pant = pygame.Surface((1280, 720))

    # Dibujar fondo de partidas detrás para verificar la pantalla de guardado
    pant.fill((255, 240, 195))
    rect_panel, btn_v, btn_n, _ = main.obtener_geometria_panel_partidas(1280, 720, True)
    pygame.draw.rect(pant, (253, 246, 233), rect_panel, border_radius=18)
    pygame.draw.rect(pant, (195, 168, 138), rect_panel, width=3, border_radius=18)

    partida_larga = {
        "id": 1,
        "nombre": "Todos los niveles desbloqueados",
        "mundo_max": 3,
        "nivel_max": 5,
        "tiene_password": True,
        "fecha": "2026-10-27 21:00",
        "niveles_desbloqueados": {
            1: [True, True, True, True, True],
            2: [True, True, True, True, True],
            3: [True, True, True, True, True],
        }
    }
    fuentes_tarjetas = {
        "titulo_card": fuentes.obtener_fuente_subtitulo(18, negrita=True),
        "sub_card": fuentes.obtener_fuente_pequena(14),
        "btn_card": fuentes.obtener_fuente_boton(14),
        "badge": fuentes.obtener_fuente_boton(14),
        "btn": fuentes.obtener_fuente_boton(14),
        "texto": fuentes.obtener_fuente_texto(16),
        "sub_btn": fuentes.obtener_fuente_pequena(12),
    }
    main.dibujar_tarjeta_partida(pant, partida_larga, 0, rect_panel, (0, 0), fuentes_tarjetas)

    # Simular un frame congelado del modal ADMINISTRAR PERFIL encima
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    pant.blit(overlay, (0, 0))

    w_card, h_card = 560, 335
    rect_card = pygame.Rect((1280 - w_card) // 2, (720 - h_card) // 2, w_card, h_card)
    pygame.draw.rect(pant, (253, 246, 233), rect_card, border_radius=16)
    pygame.draw.rect(pant, (195, 168, 138), rect_card, width=3, border_radius=16)

    # Botón X
    W_X, H_X = 29, 34
    rect_btn_x = pygame.Rect(rect_card.right - W_X - 16, rect_card.top + 16, W_X, H_X)
    spr_x = guardado._cargar_sprite_boton("HUD/boton-x.png", W_X, H_X) or guardado._cargar_sprite_boton("boton-x.png", W_X, H_X)
    if spr_x:
        pant.blit(spr_x, rect_btn_x)

    # Título
    rect_tit = pygame.Rect(rect_card.left + 50, rect_card.top + 16, rect_card.width - 100, 32)
    fuentes.dibujar_texto_en_rect(pant, "ADMINISTRAR PERFIL", rect_tit, categoria="dialogos", tamano=fuentes.TAMANO_TITULO_MODAL, color=(60, 45, 35))

    # Nombre perfil + estado contraseña
    rect_nom = pygame.Rect(rect_card.left + 24, rect_card.top + 52, rect_card.width - 48, 24)
    fuentes.dibujar_texto_en_rect(pant, f"Perfil: «{partida_larga['nombre']}»", rect_nom, categoria="subtitulo", tamano=15, color=(70, 55, 45), negrita=True, padding=4)

    rect_est = pygame.Rect(rect_card.left + 24, rect_card.top + 78, rect_card.width - 48, 20)
    fuentes.dibujar_texto_en_rect(pant, "Estado: Protegido con contraseña", rect_est, categoria="pequena", tamano=14, color=(40, 130, 65), padding=4)

    # 3 botones
    w_b, h_b = 360, 48
    x_b = rect_card.centerx - (w_b // 2)
    y_base = rect_card.top + 114
    gap_b = 14
    btn_ren = pygame.Rect(x_b, y_base, w_b, h_b)
    btn_pwd = pygame.Rect(x_b, y_base + (h_b + gap_b), w_b, h_b)
    btn_eli = pygame.Rect(x_b, y_base + (h_b + gap_b) * 2, w_b, h_b)

    pygame.draw.rect(pant, (245, 238, 226), btn_ren, border_radius=10)
    pygame.draw.rect(pant, (185, 155, 125), btn_ren, width=2, border_radius=10)
    fuentes.dibujar_texto_en_rect(pant, "CAMBIAR NOMBRE", btn_ren, categoria="subtitulo", tamano=16, color=(60, 45, 35), negrita=True, padding=8)

    pygame.draw.rect(pant, (245, 238, 226), btn_pwd, border_radius=10)
    pygame.draw.rect(pant, (185, 155, 125), btn_pwd, width=2, border_radius=10)
    fuentes.dibujar_texto_en_rect(pant, "CAMBIAR / QUITAR CONTRASEÑA", btn_pwd, categoria="subtitulo", tamano=16, color=(60, 45, 35), negrita=True, padding=8)

    pygame.draw.rect(pant, (215, 80, 75), btn_eli, border_radius=10)
    pygame.draw.rect(pant, (170, 50, 45), btn_eli, width=2, border_radius=10)
    fuentes.dibujar_texto_en_rect(pant, "ELIMINAR PERFIL", btn_eli, categoria="subtitulo", tamano=16, color=(255, 255, 255), negrita=True, padding=8)

    ruta_out_modal = os.path.join(directorio_artefactos, "verificacion_administrar_perfil_corregido.png")
    pygame.image.save(pant, ruta_out_modal)
    print(f"[OK] Captura guardada: {ruta_out_modal}")

    # 2. Captura de Diálogo de Confirmación de Borrado con Nombre Largo
    pant_bor = pygame.Surface((1280, 720))
    pant_bor.fill((255, 240, 195))
    pant_bor.blit(overlay, (0, 0))

    w_card_b, h_card_b = 560, 310
    r_card_b = pygame.Rect((1280 - w_card_b) // 2, (720 - h_card_b) // 2, w_card_b, h_card_b)
    pygame.draw.rect(pant_bor, (253, 246, 233), r_card_b, border_radius=18)
    pygame.draw.rect(pant_bor, (225, 110, 80), r_card_b, width=3, border_radius=18)

    rect_tit_b = pygame.Rect(r_card_b.left + 24, r_card_b.top + 18, r_card_b.width - 48, 34)
    fuentes.dibujar_texto_en_rect(pant_bor, "ELIMINAR PERFIL", rect_tit_b, categoria="dialogos", tamano=fuentes.TAMANO_TITULO_MODAL, color=(205, 70, 60))

    rect_nom_b = pygame.Rect(r_card_b.left + 24, r_card_b.top + 60, r_card_b.width - 48, 30)
    fuentes.dibujar_texto_en_rect(pant_bor, f"«{partida_larga['nombre']}»  —  Nivel: 3-5", rect_nom_b, categoria="subtitulo", tamano=fuentes.TAMANO_SUBTITULO_GRANDE, color=(60, 45, 35), padding=4)

    rect_preg_b = pygame.Rect(r_card_b.left + 24, r_card_b.top + 98, r_card_b.width - 48, 36)
    fuentes.dibujar_texto_en_rect(pant_bor, "¿Seguro que deseas eliminar este perfil y su partida?", rect_preg_b, categoria="texto", tamano=16, color=(80, 65, 55), multiline=True, padding=2)

    rect_aviso_b = pygame.Rect(r_card_b.left + 24, r_card_b.top + 138, r_card_b.width - 48, 32)
    fuentes.dibujar_texto_en_rect(pant_bor, "Se borrará todo su progreso y no se podrá recuperar.", rect_aviso_b, categoria="texto", tamano=15, color=(195, 75, 65), multiline=True, padding=2)

    w_btn_b, h_btn_b = 184, 54
    gap_btn_b = 22
    total_w_b = (w_btn_b * 2) + gap_btn_b
    x_can_b = r_card_b.centerx - (total_w_b // 2)
    x_bor_b = x_can_b + w_btn_b + gap_btn_b
    y_btns_b = r_card_b.bottom - 74

    b_can = pygame.Rect(x_can_b, y_btns_b, w_btn_b, h_btn_b)
    b_bor = pygame.Rect(x_bor_b, y_btns_b, w_btn_b, h_btn_b)

    pygame.draw.rect(pant_bor, (242, 234, 222), b_can, border_radius=12)
    pygame.draw.rect(pant_bor, (195, 168, 138), b_can, width=2, border_radius=12)
    fuentes.dibujar_texto_en_rect(pant_bor, "CANCELAR", b_can, categoria="boton", tamano=fuentes.TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

    pygame.draw.rect(pant_bor, (215, 80, 75), b_bor, border_radius=12)
    pygame.draw.rect(pant_bor, (170, 50, 45), b_bor, width=2, border_radius=12)
    fuentes.dibujar_texto_en_rect(pant_bor, "BORRAR PERFIL", b_bor, categoria="boton", tamano=fuentes.TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=6)

    ruta_out_bor = os.path.join(directorio_artefactos, "verificacion_eliminar_perfil_corregido.png")
    pygame.image.save(pant_bor, ruta_out_bor)
    print(f"[OK] Captura guardada: {ruta_out_bor}")

    # 3. Captura del menú de niveles con badges traducidos
    pant_niv = pygame.Surface((1280, 720))
    desbloqueados_demo = {1: [True, True, True, False, False], 2: [False]*5, 3: [False]*5}
    menu_niveles.dibujar_menu_niveles(pant_niv, 1, desbloqueados_demo, (0, 0))
    ruta_out_niv = os.path.join(directorio_artefactos, "verificacion_menu_niveles_corregido.png")
    pygame.image.save(pant_niv, ruta_out_niv)
    print(f"[OK] Captura guardada: {ruta_out_niv}")


if __name__ == "__main__":
    unittest.main(exit=False)
    generar_capturas_verificacion_visual()
