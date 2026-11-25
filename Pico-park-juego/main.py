"""
Arranque del juego: crea el estado de los menús (_EstadoMenu) y corre el loop que despacha
los eventos y el dibujo a la pantalla activa (ver menus/). Los niveles corren en pantalla.iniciar_mundo.
"""
import os
import sys

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

import pygame
from configuracion import detener_musica, obtener_idioma, reproducir_musica, reproducir_sonido_ui
from guardado import cargar_partidas
from menus.comunes import (
    ESTADO_CONFIGURACION,
    ESTADO_CREDITOS,
    ESTADO_LISTA_PARTIDAS,
    ESTADO_MENU_PRINCIPAL,
    ESTADO_MODO_JUEGO,
    ESTADO_PERSONAJES,
    ESTADO_SELECCION_MUNDO,
    ESTADO_SELECCION_NIVEL,
)
from menus.estado import _EstadoMenu
from menus.modo_juego import _dibujar_modo_juego, _eventos_modo_juego
from menus.opciones import _dibujar_configuracion, _eventos_configuracion
from menus.partidas import _dibujar_lista_partidas, _eventos_lista_partidas
from menus.personajes import _dibujar_personajes, _eventos_personajes
from menus.principal import (
    _dibujar_creditos,
    _dibujar_menu_principal,
    _eventos_creditos,
    _eventos_menu_principal,
)
from menus.seleccion_nivel import _dibujar_seleccion_nivel, _eventos_seleccion_nivel
from sprites import FPS, animar_pulsacion_boton


def main():
    m = _EstadoMenu()   # estado compartido de los menús (ver _EstadoMenu)

    while m.ejecutando:
        m.reloj.tick(FPS)
        reproducir_musica("menu")

        m.idm_act = obtener_idioma()
        if m.idm_act != m._ultimo_idioma_menu:
            m._cache_botones_menu.clear()
            m._cache_botones_modo.clear()
            m._cache_botones_volver.clear()
            m._cache_botones_nueva_lista.clear()
            m._cache_botones_primera.clear()
            m._cache_sprites_tarjeta.clear()
            m._ultimo_idioma_menu = m.idm_act

        # Cargar recursos bajo demanda según el estado actual antes de procesar eventos o dibujar
        if m.estado_actual == ESTADO_MODO_JUEGO:
            m._cargar_recursos_modo_juego()
        elif m.estado_actual == ESTADO_LISTA_PARTIDAS:
            m._cargar_recursos_partidas()
        elif m.estado_actual == ESTADO_PERSONAJES:
            m._cargar_recursos_volver()
        elif m.estado_actual == ESTADO_CONFIGURACION:
            m._cargar_recursos_controles()
        elif m.estado_actual == ESTADO_CREDITOS:
            m._cargar_recursos_volver()
        elif m.estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            m._cargar_recursos_niveles()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                m.intentar_salir()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # El botón X general: en Opciones regresa al menú principal; en el resto intenta salir
                if m.rect_btn_x.collidepoint(evento.pos):
                    if m.estado_actual == ESTADO_CONFIGURACION:
                        m._asegurar_semi_apretados_menu()
                        m.f_limpio = m.fondo_btn_x_main if m.fondo_btn_x_main else (30, 30, 30)
                        if animar_pulsacion_boton(m.pantalla, m.rect_btn_x, m.spr_x_semi, m.spr_x_apretado, m.f_limpio, m.spr_x_normal, tipo_sonido="ventana_cancelar"):
                            m.estado_actual = ESTADO_MENU_PRINCIPAL
                        break
                    elif m.estado_actual != ESTADO_SELECCION_NIVEL:
                        m._asegurar_semi_apretados_menu()
                        m.f_limpio = m.fondo_btn_x_main if m.fondo_btn_x_main else (30, 30, 30)
                        if animar_pulsacion_boton(m.pantalla, m.rect_btn_x, m.spr_x_semi, m.spr_x_apretado, m.f_limpio, m.spr_x_normal, tipo_sonido="ventana_cancelar"):
                            m.intentar_salir()
                        break

                if m.estado_actual == ESTADO_MENU_PRINCIPAL:
                    if _eventos_menu_principal(m, evento):
                        break

                elif m.estado_actual == ESTADO_MODO_JUEGO:
                    if _eventos_modo_juego(m, evento):
                        break

                elif m.estado_actual == ESTADO_LISTA_PARTIDAS:
                    if _eventos_lista_partidas(m, evento):
                        break

                elif m.estado_actual == ESTADO_PERSONAJES:
                    if _eventos_personajes(m, evento):
                        break

                elif m.estado_actual == ESTADO_CONFIGURACION:
                    if _eventos_configuracion(m, evento):
                        break

                elif m.estado_actual == ESTADO_CREDITOS:
                    if _eventos_creditos(m, evento):
                        break

                elif m.estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
                    if _eventos_seleccion_nivel(m, evento):
                        break

            elif evento.type == pygame.MOUSEWHEEL:
                if m.estado_actual == ESTADO_LISTA_PARTIDAS:
                    m.total_pag = max(1, (len(cargar_partidas()) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
                    if m.total_pag > 1:
                        if evento.y > 0 and m.pagina_partidas > 0:
                            m.pagina_partidas -= 1
                            reproducir_sonido_ui("pagina")
                        elif evento.y < 0 and m.pagina_partidas < m.total_pag - 1:
                            m.pagina_partidas += 1
                            reproducir_sonido_ui("pagina")

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if m.estado_actual == ESTADO_CONFIGURACION:
                        m.estado_actual = ESTADO_MENU_PRINCIPAL

        m.pantalla.fill((30, 30, 30))

        if m.estado_actual == ESTADO_MENU_PRINCIPAL:
            _dibujar_menu_principal(m)

        elif m.estado_actual == ESTADO_MODO_JUEGO:
            _dibujar_modo_juego(m)

        elif m.estado_actual == ESTADO_LISTA_PARTIDAS:
            _dibujar_lista_partidas(m)

        elif m.estado_actual == ESTADO_PERSONAJES:
            _dibujar_personajes(m)

        elif m.estado_actual == ESTADO_CONFIGURACION:
            _dibujar_configuracion(m)

        elif m.estado_actual == ESTADO_CREDITOS:
            _dibujar_creditos(m)

        elif m.estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            _dibujar_seleccion_nivel(m)

        if m.estado_actual != ESTADO_SELECCION_NIVEL:
            m.pos_mouse = pygame.mouse.get_pos()
            m.fondo_btn_x_main = m.pantalla.subsurface(m.rect_btn_x).copy()
            m.hov_x = m.rect_btn_x.collidepoint(m.pos_mouse)
            m.spr_x_dib = m.spr_x_hover if (m.hov_x and m.spr_x_hover) else m.spr_x_normal
            if m.spr_x_dib: m.pantalla.blit(m.spr_x_dib, m.rect_btn_x)

        pygame.display.flip()

    detener_musica()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    from errores import ejecutar_protegido
    ejecutar_protegido(main)
