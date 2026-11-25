"""
Pantalla del menú principal (JUGAR / PERSONAJES / OPCIONES / SALIR) y créditos.
"""
import pygame
from configuracion import obtener_idioma
from menus.comunes import ESTADO_CONFIGURACION, ESTADO_MENU_PRINCIPAL, ESTADO_MODO_JUEGO, ESTADO_PERSONAJES
from sprites import animar_pulsacion_boton, obtener_accesorios_disponibles


def _eventos_menu_principal(m, evento):
    """Clic izquierdo en la pantalla «menu_principal». Devuelve True si hay que cortar el resto de eventos del frame."""
    m._asegurar_semi_apretados_menu()
    m.idm_act = obtener_idioma()
    if m.btn_jugar.collidepoint(evento.pos):
        m.f_limp = m.gestor_personajes_menu.fondo_estatico.subsurface(m.btn_jugar)
        m.sp_s = m._obtener_boton_menu_principal_estado("jugar", "semi", m.idm_act)
        m.sp_a = m._obtener_boton_menu_principal_estado("jugar", "apretado", m.idm_act)
        m.sp_n = m._obtener_boton_menu_principal_estado("jugar", "normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_jugar, m.sp_s, m.sp_a, m.f_limp, m.sp_n, tipo_sonido="menu"):
            m.estado_actual = ESTADO_MODO_JUEGO
    elif m.btn_personajes.collidepoint(evento.pos):
        m.f_limp = m.gestor_personajes_menu.fondo_estatico.subsurface(m.btn_personajes)
        m.sp_s = m._obtener_boton_menu_principal_estado("personajes", "semi", m.idm_act)
        m.sp_a = m._obtener_boton_menu_principal_estado("personajes", "apretado", m.idm_act)
        m.sp_n = m._obtener_boton_menu_principal_estado("personajes", "normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_personajes, m.sp_s, m.sp_a, m.f_limp, m.sp_n, tipo_sonido="menu"):
            m.estado_actual = ESTADO_PERSONAJES
            m.acc_list_init = obtener_accesorios_disponibles()
            for m._ia, m._acc in enumerate(m.acc_list_init):
                if m._acc["id"] == m.accesorio_p1:
                    m.pagina_acc_p1 = m._ia // 6
                if m._acc["id"] == m.accesorio_p2:
                    m.pagina_acc_p2 = m._ia // 6
    elif m.btn_config.collidepoint(evento.pos):
        m.f_limp = m.gestor_personajes_menu.fondo_estatico.subsurface(m.btn_config)
        m.sp_s = m._obtener_boton_menu_principal_estado("opciones", "semi", m.idm_act)
        m.sp_a = m._obtener_boton_menu_principal_estado("opciones", "apretado", m.idm_act)
        m.sp_n = m._obtener_boton_menu_principal_estado("opciones", "normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_config, m.sp_s, m.sp_a, m.f_limp, m.sp_n, tipo_sonido="menu"):
            m.estado_actual = ESTADO_CONFIGURACION
            m.seccion_opciones_actual = "configuracion"
            return True
    elif m.btn_salir.collidepoint(evento.pos):
        m.f_limp = m.gestor_personajes_menu.fondo_estatico.subsurface(m.btn_salir)
        m.sp_s = m._obtener_boton_menu_principal_estado("salir", "semi", m.idm_act)
        m.sp_a = m._obtener_boton_menu_principal_estado("salir", "apretado", m.idm_act)
        m.sp_n = m._obtener_boton_menu_principal_estado("salir", "normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_salir, m.sp_s, m.sp_a, m.f_limp, m.sp_n, tipo_sonido="menu"):
            m.intentar_salir()
    return False


def _eventos_creditos(m, evento):
    """Clic izquierdo en la pantalla «creditos». Devuelve True si hay que cortar el resto de eventos del frame."""
    m.idm_act = obtener_idioma()
    if m.btn_volver_creditos.collidepoint(evento.pos):
        m.sp_v_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_v_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_v_n = m._obtener_boton_volver("normal", m.idm_act)
        m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_creditos, m.sp_v_s, m.sp_v_a, (30, 30, 30), m.sp_v_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MENU_PRINCIPAL
    return False


def _dibujar_menu_principal(m):
    """Dibuja la pantalla «menu_principal»."""
    m.gestor_personajes_menu.sincronizar_personalizacion(m.color_p1, m.accesorio_p1, m.color_p2, m.accesorio_p2)
    m.gestor_personajes_menu.actualizar()

    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()
    botones_menu_datos = m._obtener_botones_menu_principal(m.idm_act)
    m.spr_x_dib = m.spr_x_hover if (m.spr_x_hover and m.rect_btn_x.collidepoint(m.pos_mouse)) else m.spr_x_normal
    m.gestor_personajes_menu.dibujar_menu_completo(
        m.pantalla,
        botones_menu_datos=botones_menu_datos,
        pos_mouse=m.pos_mouse,
        spr_x=m.spr_x_dib,
        rect_x=m.rect_btn_x,
        fuente_titulo=m.fuente_pixel_titulo,
    )


def _dibujar_creditos(m):
    """Dibuja la pantalla «creditos»."""
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()
    m.titulo = m.fuente_pixel_titulo.render("CREDITOS", True, (255, 255, 255))
    m.pantalla.blit(m.titulo, m.titulo.get_rect(center=(m.ANCHO_MENU // 2, 100)))

    cred = m.fuente_texto.render("Desarrollado para Pico Park Fan Project", True, (200, 200, 200))
    m.pantalla.blit(cred, cred.get_rect(center=(m.ANCHO_MENU // 2, m.ALTO_MENU // 2)))

    # Botón Volver al Menú (mundos/boton-volver)
    hov_vcr = m.btn_volver_creditos.collidepoint(m.pos_mouse)
    spr_vcr_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vcr_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vcr = spr_vcr_hov if (hov_vcr and spr_vcr_hov) else spr_vcr_norm
    if spr_vcr:
        m.pantalla.blit(spr_vcr, m.btn_volver_creditos)
