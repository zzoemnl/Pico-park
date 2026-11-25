"""
Selección de mundo y nivel, y el paso de un nivel al siguiente (jugar_niveles_desde).
"""
import pygame
from configuracion import (
    mostrar_pestana_configuracion,
    reproducir_musica,
    reproducir_sonido_ui,
    seleccionar_musica_menu_aleatoria,
)
from guardado import NIVELES_POR_MUNDO, es_partida_admin
from menu_niveles import dibujar_menu_niveles, obtener_geometria_menu, obtener_mecanicas_nivel
from menus.comunes import ESTADO_MENU_PRINCIPAL, ESTADO_SELECCION_NIVEL
from pantalla import iniciar_mundo
from sprites import animar_pulsacion_boton


def jugar_niveles_desde(
    m_inicial, n_inicial,
    color_p1, color_p2,
    niveles_desbloqueados,
    partida_actual_id,
    partida_actual_nombre,
    snapshot_guardado,
    accesorio_p1=None,
    accesorio_p2=None,
    partida_actual_password=None,
):
    """
    Ejecuta el ciclo de juego continuo de niveles a partir de un mundo y nivel dados.
    Retorna (accion_final, mundo_seleccionado), donde accion_final es 'menu' o 'salir'.
    """
    m_idx, n_idx = m_inicial, n_inicial
    mundo_sel = m_idx
    mantenimiento = True
    es_admin = es_partida_admin(partida_actual_nombre, partida_actual_id)
    while mantenimiento:
        mecanicas = obtener_mecanicas_nivel(m_idx, n_idx + 1)
        res = iniciar_mundo(
            mecanicas,
            numero_nivel=n_idx + 1,
            color_p1=color_p1,
            color_p2=color_p2,
            mundo=m_idx,
            niveles_desbloqueados=niveles_desbloqueados,
            partida_id=partida_actual_id,
            partida_nombre=partida_actual_nombre,
            snapshot_guardado=snapshot_guardado,
            accesorio_p1=accesorio_p1,
            accesorio_p2=accesorio_p2,
            partida_password=partida_actual_password,
        )
        if res == "siguiente":
            if n_idx + 1 < NIVELES_POR_MUNDO[m_idx]:
                n_idx += 1
                niveles_desbloqueados[m_idx][n_idx] = True
            elif m_idx + 1 <= 3:
                m_idx += 1
                n_idx = 0
                niveles_desbloqueados[m_idx][n_idx] = True
                mundo_sel = m_idx
            else:
                seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                reproducir_musica("menu", forzar=True)
                return "menu", mundo_sel
        elif res == "reiniciar":
            continue
        elif res == "menu":
            seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
            reproducir_musica("menu", forzar=True)
            return "menu", mundo_sel
        else:
            return "salir", mundo_sel
    seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
    reproducir_musica("menu", forzar=True)
    return "menu", mundo_sel


def _eventos_seleccion_nivel(m, evento):
    """Clic izquierdo en la pantalla «seleccion_nivel». Devuelve True si hay que cortar el resto de eventos del frame."""
    # Iconos superiores de Selección de Niveles (Configuración, Casita y X)
    if m.rect_btn_config_niveles.collidepoint(evento.pos):
        m.pulsado = True
        if m.spr_confign_semi and m.spr_confign_apretado:
            m.f_limpio = m.fondo_btn_config_niveles if m.fondo_btn_config_niveles else (255, 240, 195)
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.rect_btn_config_niveles, m.spr_confign_semi, m.spr_confign_apretado, m.f_limpio, m.spr_confign_normal, tipo_sonido="menu")
        if m.pulsado:
            mostrar_pestana_configuracion(m.pantalla, m.reloj)
            return True
    if m.rect_btn_casa_niveles.collidepoint(evento.pos):
        m.pulsado = True
        if m.spr_casa_semi and m.spr_casa_apretado:
            m.f_limpio = m.fondo_btn_casa_niveles if m.fondo_btn_casa_niveles else (255, 240, 195)
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.rect_btn_casa_niveles, m.spr_casa_semi, m.spr_casa_apretado, m.f_limpio, m.spr_casa_normal, tipo_sonido="menu")
        if m.pulsado:
            m.estado_actual = ESTADO_MENU_PRINCIPAL
            return True
    if m.rect_btn_x_niveles.collidepoint(evento.pos):
        m.pulsado = True
        if m.spr_xn_semi and m.spr_xn_apretado:
            m.f_limpio = m.fondo_btn_x_niveles if m.fondo_btn_x_niveles else (255, 240, 195)
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.rect_btn_x_niveles, m.spr_xn_semi, m.spr_xn_apretado, m.f_limpio, m.spr_xn_normal, tipo_sonido="ventana_cancelar")
        if m.pulsado:
            m.intentar_salir()
            return True

    m.rect_panel, m.tabs_info, m.rects_cards = obtener_geometria_menu(m.ANCHO_MENU, m.ALTO_MENU, NIVELES_POR_MUNDO[m.mundo_seleccionado])
    m.tab_presionada = False
    for m.m, m.t_data in m.tabs_info.items():
        if m.t_data["rect_click"].collidepoint(evento.pos):
            if m.mundo_seleccionado != m.m:
                reproducir_sonido_ui("tab")
            m.mundo_seleccionado = m.m
            m.tab_presionada = True
            break

    if not m.tab_presionada:
        m.es_admin_partida = es_partida_admin(m.partida_actual_nombre, m.partida_actual_id)
        for m.idx_nivel, m.rect_c in enumerate(m.rects_cards):
            m.desbloqueado = m.niveles_desbloqueados[m.mundo_seleccionado][m.idx_nivel]
            if m.rect_c.collidepoint(evento.pos):
                if m.desbloqueado or m.es_admin_partida:
                    reproducir_sonido_ui("menu")
                    m.fin_acc, m.mundo_seleccionado = jugar_niveles_desde(
                        m.mundo_seleccionado,
                        m.idx_nivel,
                        m.color_p1,
                        m.color_p2,
                        m.niveles_desbloqueados,
                        m.partida_actual_id,
                        m.partida_actual_nombre,
                        m.snapshot_guardado,
                        accesorio_p1=m.accesorio_p1,
                        accesorio_p2=m.accesorio_p2,
                        partida_actual_password=m.partida_actual_password,
                    )
                    if m.fin_acc == "menu":
                        m.estado_actual = ESTADO_SELECCION_NIVEL
                        seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                        reproducir_musica("menu", forzar=True)
                    else:
                        m.ejecutando = False
                    break
    return False


def _dibujar_seleccion_nivel(m):
    """Dibuja la pantalla «seleccion_nivel»."""
    m.pos_mouse = pygame.mouse.get_pos()
    dibujar_menu_niveles(
        m.pantalla,
        m.mundo_seleccionado,
        m.niveles_desbloqueados,
        m.pos_mouse,
        m.fuentes_menu,
        es_admin=es_partida_admin(m.partida_actual_nombre, m.partida_actual_id),
    )

    # Capturar fondo limpio de los iconos antes de dibujarlos sobre la pantalla
    m.fondo_btn_config_niveles = m.pantalla.subsurface(m.rect_btn_config_niveles).copy()
    m.fondo_btn_casa_niveles = m.pantalla.subsurface(m.rect_btn_casa_niveles).copy()
    m.fondo_btn_x_niveles = m.pantalla.subsurface(m.rect_btn_x_niveles).copy()

    # Iconos superiores de Selección de Niveles: Configuración, Casita (Menú Principal) y X (Salir)
    hov_cfg = m.rect_btn_config_niveles.collidepoint(m.pos_mouse)
    spr_cfg_dib = m.spr_confign_hover if (hov_cfg and m.spr_confign_hover) else m.spr_confign_normal
    if spr_cfg_dib:
        m.pantalla.blit(spr_cfg_dib, m.rect_btn_config_niveles)

    hov_casa = m.rect_btn_casa_niveles.collidepoint(m.pos_mouse)
    spr_c_dib = m.spr_casa_hover if (hov_casa and m.spr_casa_hover) else m.spr_casa_normal
    if spr_c_dib:
        m.pantalla.blit(spr_c_dib, m.rect_btn_casa_niveles)

    hov_xn = m.rect_btn_x_niveles.collidepoint(m.pos_mouse)
    spr_xn_dib = m.spr_xn_hover if (hov_xn and m.spr_xn_hover) else m.spr_xn_normal
    if spr_xn_dib:
        m.pantalla.blit(spr_xn_dib, m.rect_btn_x_niveles)
