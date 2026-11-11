import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Pico-park-juego"))

import pygame
from test_landscape import generar_fondo_atardecer
from test_full_ui import crear_boton_pixel_art
import fuentes

def probar_interfaz_real():
    pygame.init()
    W, H = 1280, 720
    pantalla = pygame.Surface((W, H))

    # Generar fondo
    fondo = generar_fondo_atardecer(W, H)
    pantalla.blit(fondo, (0, 0))

    # Obtener fuentes oficiales del juego
    fuente_pixel_titulo = fuentes.obtener_fuente_titulo(36, tamano_fallback=36)
    fuente_subtitulo = fuentes.obtener_fuente_subtitulo(24)
    fuente_pixel_btn_grande = fuentes.obtener_fuente_botones(20, tamano_fallback=20)
    fuente_pixel_btn = fuentes.obtener_fuente_botones(18, tamano_fallback=18)
    fuente_sub_btn = fuentes.obtener_fuente_pequena(16)

    # 1. Marquesina sutil / Placa cálida semitransparente para TÍTULO y SUBTÍTULO
    # Dimensiones elegantes, sin tapar las montañas
    w_placa, h_placa = 720, 110
    x_placa = (W - w_placa) // 2
    y_placa = 42

    surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    # Fondo ciruela / vino atardecer semitransparente con desenfoque cálido
    pygame.draw.rect(surf_placa, (36, 14, 30, 185), (0, 0, w_placa, h_placa), border_radius=16)
    # Borde dorado / coral escalonado
    pygame.draw.rect(surf_placa, (235, 142, 72, 230), (0, 0, w_placa, h_placa), width=3, border_radius=16)
    pygame.draw.rect(surf_placa, (255, 218, 140, 150), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)

    # Gemas en las esquinas de la placa
    for cx_d, cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
        pygame.draw.circle(surf_placa, (255, 225, 120, 240), (cx_d, cy_d), 4)
        pygame.draw.circle(surf_placa, (65, 24, 18, 240), (cx_d, cy_d), 2)

    pantalla.blit(surf_placa, (x_placa, y_placa))

    # Título «MODO DE JUEGO»
    # Sombra doble en violeta profundo / bordó para máximo contraste y legibilidad
    txt_tit = "MODO DE JUEGO"
    t_somb1 = fuente_pixel_titulo.render(txt_tit, True, (20, 6, 16))
    t_somb2 = fuente_pixel_titulo.render(txt_tit, True, (88, 28, 48))
    t_tit = fuente_pixel_titulo.render(txt_tit, True, (255, 242, 224))

    rect_tit = t_tit.get_rect(center=(W // 2, y_placa + 40))
    pantalla.blit(t_somb1, (rect_tit.x + 3, rect_tit.y + 3))
    pantalla.blit(t_somb2, (rect_tit.x + 1, rect_tit.y + 1))
    pantalla.blit(t_tit, rect_tit)

    # Subtítulo
    txt_sub = "Selecciona cómo deseas comenzar tu aventura"
    t_sub_s = fuente_subtitulo.render(txt_sub, True, (24, 8, 18))
    t_sub = fuente_subtitulo.render(txt_sub, True, (255, 208, 168))
    rect_sub = t_sub.get_rect(center=(W // 2, y_placa + 80))
    pantalla.blit(t_sub_s, (rect_sub.x + 2, rect_sub.y + 2))
    pantalla.blit(t_sub, rect_sub)

    # 2. Botones en sus posiciones exactas del juego:
    # btn_continuar: x_modo, (ALTO_MENU // 2) - 85 -> y = 275
    # btn_nueva_partida: x_modo, (ALTO_MENU // 2) + 35 -> y = 395
    # btn_volver_modo: (ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85 -> y = 635
    W_MODO, H_MODO = 425, 100
    x_modo = (W - W_MODO) // 2
    y_cont = 275
    y_nueva = 395
    W_VOLVER, H_VOLVER = 238, 70
    x_volver = (W - W_VOLVER) // 2
    y_volver = 635

    btn_continuar = crear_boton_pixel_art(
        W_MODO, H_MODO,
        "CONTINUAR",
        subtexto="Cargar partida guardada",
        icono="play",
        estilo="ambar",
        estado="normal",
        fuente_tit=fuente_pixel_btn_grande,
        fuente_sub=fuente_sub_btn,
    )
    pantalla.blit(btn_continuar, (x_modo, y_cont))

    btn_nueva = crear_boton_pixel_art(
        W_MODO, H_MODO,
        "NUEVA PARTIDA",
        subtexto="Iniciar una nueva aventura",
        icono="estrella",
        estilo="violeta",
        estado="normal",
        fuente_tit=fuente_pixel_btn_grande,
        fuente_sub=fuente_sub_btn,
    )
    pantalla.blit(btn_nueva, (x_modo, y_nueva))

    btn_volver = crear_boton_pixel_art(
        W_VOLVER, H_VOLVER,
        "VOLVER AL MENU",
        icono="volver",
        estilo="crema",
        estado="normal",
        fuente_tit=fuente_pixel_btn,
    )
    pantalla.blit(btn_volver, (x_volver, y_volver))

    output_path = "scratch/pantalla_modo_juego_oficial.png"
    pygame.image.save(pantalla, output_path)
    print(f"Pantalla guardada exitosamente en: {output_path}")

if __name__ == '__main__':
    probar_interfaz_real()
