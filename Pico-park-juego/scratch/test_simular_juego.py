import sys
import os
import pygame

def simular_modo_juego():
    # Lanzar una simulación directa de la pantalla MODO DE JUEGO
    pygame.init()
    pantalla = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Pico Park - Test MODO DE JUEGO")
    reloj = pygame.time.Clock()

    import main
    
    # Simular la inicialización de recursos de main()
    fuente_pixel_titulo = main.obtener_fuente_titulo(main.TAMANO_TITULO, tamano_fallback=55)
    fuente_pixel_btn_grande = main.obtener_fuente_botones(main.TAMANO_BOTON_GRANDE, tamano_fallback=32)
    fuente_pixel_btn = main.obtener_fuente_botones(main.TAMANO_BOTON, tamano_fallback=32)
    fuente_subtitulo = main.obtener_fuente_subtitulo(main.TAMANO_SUBTITULO_GRANDE)
    fuente_sub_btn = main.obtener_fuente_pequena(main.TAMANO_PEQUENA)

    ANCHO_MENU, ALTO_MENU = 1280, 720
    main._init_copos_modo(ANCHO_MENU, ALTO_MENU)

    W_MODO, H_MODO = 425, 100
    x_modo = (ANCHO_MENU - W_MODO) // 2
    btn_continuar = pygame.Rect(x_modo, (ALTO_MENU // 2) - 85, W_MODO, H_MODO)
    btn_nueva_partida = pygame.Rect(x_modo, (ALTO_MENU // 2) + 35, W_MODO, H_MODO)
    W_VOLVER, H_VOLVER = 238, 70
    btn_volver_modo = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)

    spr_continuar_normal = main._crear_boton_pixel_art(
        W_MODO, H_MODO, "CONTINUAR", subtexto="Cargar partida guardada",
        icono="play", estilo="ambar", estado="normal",
        fuente_tit=fuente_pixel_btn_grande, fuente_sub=fuente_sub_btn,
    )
    spr_continuar_hover = main._crear_boton_pixel_art(
        W_MODO, H_MODO, "CONTINUAR", subtexto="Cargar partida guardada",
        icono="play", estilo="ambar", estado="hover",
        fuente_tit=fuente_pixel_btn_grande, fuente_sub=fuente_sub_btn,
    )
    spr_nueva_modo_normal = main._crear_boton_pixel_art(
        W_MODO, H_MODO, "NUEVA PARTIDA", subtexto="Iniciar una nueva aventura",
        icono="estrella", estilo="violeta", estado="normal",
        fuente_tit=fuente_pixel_btn_grande, fuente_sub=fuente_sub_btn,
    )
    spr_nueva_modo_hover = main._crear_boton_pixel_art(
        W_MODO, H_MODO, "NUEVA PARTIDA", subtexto="Iniciar una nueva aventura",
        icono="estrella", estilo="violeta", estado="hover",
        fuente_tit=fuente_pixel_btn_grande, fuente_sub=fuente_sub_btn,
    )
    spr_volver_modo_normal = main._crear_boton_pixel_art(
        W_VOLVER, H_VOLVER, "VOLVER AL MENU",
        icono="volver", estilo="crema", estado="normal",
        fuente_tit=fuente_pixel_btn,
    )

    # Renderizar exactamente como hace el bucle de main.py
    pantalla.blit(main._obtener_fondo_modo_juego(ANCHO_MENU, ALTO_MENU), (0, 0))
    main._dibujar_copos_modo(pantalla)

    w_placa, h_placa = 680, 106
    x_placa = (ANCHO_MENU - w_placa) // 2
    y_placa = 45

    surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    pygame.draw.rect(surf_placa, (252, 242, 228, 225), (0, 0, w_placa, h_placa), border_radius=16)
    pygame.draw.rect(surf_placa, (85, 28, 48, 240), (0, 0, w_placa, h_placa), width=3, border_radius=16)
    pygame.draw.rect(surf_placa, (235, 142, 72, 180), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)
    for cx_d, cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
        pygame.draw.circle(surf_placa, (215, 110, 42), (cx_d, cy_d), 4)
        pygame.draw.circle(surf_placa, (255, 240, 200), (cx_d, cy_d), 2)
    pantalla.blit(surf_placa, (x_placa, y_placa))

    txt_tit = "MODO DE JUEGO"
    t_somb = fuente_pixel_titulo.render(txt_tit, True, (225, 205, 185))
    t_tit = fuente_pixel_titulo.render(txt_tit, True, (68, 20, 42))
    rect_tit = t_tit.get_rect(center=(ANCHO_MENU // 2, y_placa + 38))
    pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
    pantalla.blit(t_tit, rect_tit)

    txt_sub = "Selecciona cómo deseas comenzar tu aventura"
    t_sub_s = fuente_subtitulo.render(txt_sub, True, (255, 255, 255))
    t_sub = fuente_subtitulo.render(txt_sub, True, (108, 52, 45))
    rect_sub = t_sub.get_rect(center=(ANCHO_MENU // 2, y_placa + 78))
    pantalla.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
    pantalla.blit(t_sub, rect_sub)

    pantalla.blit(spr_continuar_normal, btn_continuar)
    pantalla.blit(spr_nueva_modo_normal, btn_nueva_partida)
    pantalla.blit(spr_volver_modo_normal, btn_volver_modo)

    captura = "scratch/captura_final_modo_juego.png"
    pygame.image.save(pantalla, captura)
    print("Captura final guardada:", captura)

if __name__ == '__main__':
    simular_modo_juego()
