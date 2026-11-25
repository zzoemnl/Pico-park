"""
Diálogos modales de partidas: pedir nombre y contraseña, crear o cargar una partida, guardar al salir,
confirmar borrado, confirmar atuendos y administrar perfil. Los datos los maneja guardado.py.
"""
import pygame
from configuracion import obtener_idioma, reproducir_sonido_ui, t
from fuentes import (
    TAMANO_BOTON_MODAL,
    TAMANO_INPUT,
    TAMANO_ITEM_TITULO,
    TAMANO_PEQUENA,
    TAMANO_SUBTITULO,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO,
    TAMANO_TEXTO_GRANDE,
    TAMANO_TITULO_MODAL,
    dibujar_texto_en_rect,
    obtener_fuente_boton,
    obtener_fuente_contador,
    obtener_fuente_dialogos,
    obtener_fuente_pequena,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_titulo,
    renderizar_texto_ajustado,
)
from guardado import (
    calcular_niveles_completados,
    cambiar_password_partida,
    cargar_partidas,
    crear_desbloqueados_inicial,
    eliminar_partida,
    es_partida_admin,
    guardar_partida,
    obtener_maximo_alcanzado,
    obtener_nombre_partida_visible,
    renombrar_partida,
    verify_password,
)
from sprites import aclarar_boton, animar_pulsacion_boton, cargar_boton_escalado, generar_boton_con_texto


def _cargar_sprite_boton(nombre, w, h):
    """Carga y escala suavemente un botón oficial del proyecto con proporciones exactas usando caché."""
    return cargar_boton_escalado(nombre, w, h)


def solicitar_texto_modal(pantalla, reloj, titulo, subtitulo, valor_inicial="", es_password=False, permitir_vacio=False, max_caracteres=18):
    """
    Muestra un diálogo modal interactivo para introducir texto (nombre o contraseña).
    Retorna la cadena introducida si se confirma, o None si se cancela con ESC o el botón Cancelar.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_input = obtener_fuente_texto(TAMANO_INPUT)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=24)

    w_card, h_card = 520, 310
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    rect_input = pygame.Rect(rect_card.left + 50, rect_card.top + 115, w_card - 100, 46)

    w_btn, h_btn = 177, 52
    y_btns = rect_card.top + 218
    btn_cancelar = pygame.Rect(rect_card.centerx - w_btn - 12, y_btns, w_btn, h_btn)
    btn_confirmar = pygame.Rect(rect_card.centerx + 12, y_btns, w_btn, h_btn)

    idm_modal = obtener_idioma()
    spr_can_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 0)
    spr_can_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 1)
    spr_can_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 2)
    spr_can_hover = aclarar_boton(spr_can_norm) if spr_can_norm else None

    spr_ace_norm = generar_boton_con_texto("Ventanas/aceptar.png", w_btn, h_btn, t("aceptar", "ACEPTAR"), (28, 82, 37), TAMANO_BOTON_MODAL, 0, idm_modal)
    spr_ace_semi = generar_boton_con_texto("Ventanas/aceptar-semiapretado.png", w_btn, h_btn, t("aceptar", "ACEPTAR"), (28, 82, 37), TAMANO_BOTON_MODAL, 1, idm_modal)
    spr_ace_apret = generar_boton_con_texto("Ventanas/aceptar-apretado.png", w_btn, h_btn, t("aceptar", "ACEPTAR"), (28, 82, 37), TAMANO_BOTON_MODAL, 2, idm_modal)
    spr_ace_hover = aclarar_boton(spr_ace_norm) if spr_ace_norm else None
    fondo_tarjeta = (253, 246, 233)

    rect_ojo = pygame.Rect(rect_input.right - 42, rect_input.top + 5, 36, 36) if es_password else None
    mostrar_caracteres = not es_password

    texto = valor_inicial
    cursor_visible = True
    contador_cursor = 0
    mensaje_error = None

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    # Limpiar eventos previos al abrir la ventana modal
    pygame.event.clear()

    while True:
        reloj.tick(60)
        contador_cursor = (contador_cursor + 1) % 60
        cursor_visible = contador_cursor < 30
        pos_mouse = pygame.mouse.get_pos()

        hov_can = btn_cancelar.collidepoint(pos_mouse)
        hov_con = btn_confirmar.collidepoint(pos_mouse)
        hov_ojo = rect_ojo.collidepoint(pos_mouse) if rect_ojo else False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.event.clear()
                return None

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    return None
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    val = texto.strip()
                    if not val and not permitir_vacio:
                        mensaje_error = t("campo_no_vacio")
                    else:
                        pulsado = True
                        if spr_ace_semi and spr_ace_apret:
                            pulsado = animar_pulsacion_boton(pantalla, btn_confirmar, spr_ace_semi, spr_ace_apret, fondo_tarjeta, spr_ace_norm, tipo_sonido="ventana_aceptar")
                        else:
                            reproducir_sonido_ui("ventana_aceptar")
                            pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, border_radius=10)
                            pygame.draw.rect(pantalla, (30, 95, 50), btn_confirmar, width=2, border_radius=10)
                            dibujar_texto_en_rect(pantalla, t("aceptar", "ACEPTAR"), btn_confirmar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(230, 230, 230))
                            pygame.display.flip()
                            pygame.time.delay(60)
                        if pulsado:
                            pygame.event.clear()
                            return val
                elif evento.key == pygame.K_BACKSPACE:
                    texto = texto[:-1]
                    mensaje_error = None
                else:
                    if len(texto) < max_caracteres and evento.unicode and evento.unicode.isprintable() and evento.unicode != "|":
                        texto += evento.unicode
                        mensaje_error = None

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_ojo and rect_ojo.collidepoint(evento.pos):
                    mostrar_caracteres = not mostrar_caracteres
                    reproducir_sonido_ui("select")
                elif btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_can_semi and spr_can_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_can_semi, spr_can_apret, fondo_tarjeta, spr_can_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        pygame.event.clear()
                        return None
                elif btn_confirmar.collidepoint(evento.pos):
                    val = texto.strip()
                    if not val and not permitir_vacio:
                        mensaje_error = t("campo_no_vacio")
                    else:
                        pulsado = True
                        if spr_ace_semi and spr_ace_apret:
                            pulsado = animar_pulsacion_boton(pantalla, btn_confirmar, spr_ace_semi, spr_ace_apret, fondo_tarjeta, spr_ace_norm, tipo_sonido="ventana_aceptar")
                        else:
                            reproducir_sonido_ui("ventana_aceptar")
                            pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, border_radius=10)
                            pygame.draw.rect(pantalla, (30, 95, 50), btn_confirmar, width=2, border_radius=10)
                            dibujar_texto_en_rect(pantalla, t("aceptar", "ACEPTAR"), btn_confirmar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(230, 230, 230))
                            pygame.display.flip()
                            pygame.time.delay(60)
                        if pulsado:
                            pygame.event.clear()
                            return val

        # Dibujar fondo capturado + overlay
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        # Tarjeta modal pastel crema
        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        # Título centrado seguro
        tamano_tit = 30 if titulo == "PERFIL PROTEGIDO" else TAMANO_TITULO_MODAL
        rect_tit = pygame.Rect(rect_card.left + 30, rect_card.top + 14, rect_card.width - 60, 36)
        dibujar_texto_en_rect(pantalla, titulo, rect_tit, categoria="dialogos", tamano=tamano_tit, color=(60, 45, 35), padding=2)

        # Subtítulo multilínea con autoajuste para nombres largos
        rect_sub = pygame.Rect(rect_card.left + 24, rect_card.top + 54, rect_card.width - 48, 52)
        dibujar_texto_en_rect(pantalla, subtitulo, rect_sub, categoria="subtitulo", tamano=15, color=(115, 95, 80), multiline=True, padding=2)

        # Caja de texto
        pygame.draw.rect(pantalla, (255, 255, 255), rect_input, border_radius=8)
        pygame.draw.rect(pantalla, (175, 140, 105), rect_input, width=2, border_radius=8)

        # Renderizado del texto introducido con ajuste dinámico dentro del input
        texto_mostrar = texto if mostrar_caracteres else ("•" * len(texto))
        max_w_inp = rect_input.width - (54 if rect_ojo else 24)
        t_txt, _ = renderizar_texto_ajustado(texto_mostrar, categoria="texto", tamano=TAMANO_INPUT, ancho_max=max_w_inp, color=(40, 30, 25))
        pantalla.blit(t_txt, (rect_input.left + 12, rect_input.centery - (t_txt.get_height() // 2)))

        # Cursor parpadeante
        if cursor_visible:
            cur_x = rect_input.left + 12 + t_txt.get_width() + 2
            pygame.draw.line(pantalla, (50, 40, 35), (cur_x, rect_input.top + 10), (cur_x, rect_input.bottom - 10), 2)

        # Botón de visibilidad de contraseña
        if rect_ojo:
            pygame.draw.rect(pantalla, (245, 238, 226) if hov_ojo else (235, 226, 212), rect_ojo, border_radius=6)
            pygame.draw.rect(pantalla, (185, 160, 135), rect_ojo, width=1, border_radius=6)
            simbolo_ojo = "👁" if mostrar_caracteres else "🔒"
            dibujar_texto_en_rect(pantalla, simbolo_ojo, rect_ojo, categoria="subtitulo", tamano=16, color=(60, 45, 35), padding=2)

        # Mensaje de error
        if mensaje_error:
            rect_err = pygame.Rect(rect_card.left + 24, rect_input.bottom + 8, rect_card.width - 48, 26)
            dibujar_texto_en_rect(pantalla, mensaje_error, rect_err, categoria="subtitulo", tamano=14, color=(215, 50, 50), padding=2)

        # Botón Cancelar (reutiliza el botón existente oficial de la carpeta de botones)
        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            dibujar_texto_en_rect(pantalla, t("cancelar").upper(), btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        # Botón Aceptar
        if spr_ace_norm:
            pantalla.blit(spr_ace_hover if (hov_con and spr_ace_hover) else spr_ace_norm, btn_confirmar)
        else:
            col_con = (82, 194, 114) if hov_con else (68, 172, 98)
            pygame.draw.rect(pantalla, col_con, btn_confirmar, border_radius=10)
            pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, width=2, border_radius=10)
            dibujar_texto_en_rect(pantalla, t("aceptar", "ACEPTAR"), btn_confirmar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=6)

        pygame.display.flip()


def pedir_password_modal(pantalla, reloj, partida):
    """
    Solicita la contraseña de un perfil protegido y valida que sea correcta.
    Permite reintentar si es errónea o cancelar.
    Retorna True si la autenticación fue exitosa, o False si se canceló.
    """
    nombre = obtener_nombre_partida_visible(partida)
    p_hash = partida.get("password_hash", "")
    p_salt = partida.get("password_salt", "")

    if not p_hash:
        return True

    pygame.event.clear()

    while True:
        pwd = solicitar_texto_modal(
            pantalla, reloj,
            titulo="PERFIL PROTEGIDO",
            subtitulo=f"Introduce la contraseña de «{nombre}»:",
            es_password=True,
            permitir_vacio=False,
        )
        if pwd is None:
            pygame.event.clear()
            return False

        if verify_password(pwd, p_hash, p_salt):
            pygame.event.clear()
            return True

        # Mostrar aviso de contraseña incorrecta
        ancho, alto = pantalla.get_width(), pantalla.get_height()
        fuente_tit = obtener_fuente_dialogos(32, tamano_fallback=32)
        fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=22)

        w_a, h_a = 480, 230
        r_a = pygame.Rect((ancho - w_a) // 2, (alto - h_a) // 2, w_a, h_a)
        w_btn, h_btn = 160, 48
        b_rein = pygame.Rect(r_a.centerx - w_btn - 12, r_a.bottom - 68, w_btn, h_btn)
        b_canc = pygame.Rect(r_a.centerx + 12, r_a.bottom - 68, w_btn, h_btn)

        idm_g = obtener_idioma()
        spr_rein_norm = generar_boton_con_texto("Ventanas/boton-reintentar.png", w_btn, h_btn, t("reintentar", "REINTENTAR"), (60, 45, 35), TAMANO_BOTON_MODAL, 0, idm_g)
        spr_rein_semi = generar_boton_con_texto("Ventanas/boton-reintentar-semiapretado.png", w_btn, h_btn, t("reintentar", "REINTENTAR"), (60, 45, 35), TAMANO_BOTON_MODAL, 1, idm_g)
        spr_rein_apret = generar_boton_con_texto("Ventanas/boton-reintentar-apretado.png", w_btn, h_btn, t("reintentar", "REINTENTAR"), (60, 45, 35), TAMANO_BOTON_MODAL, 2, idm_g)
        spr_rein_hover = aclarar_boton(spr_rein_norm) if spr_rein_norm else None

        spr_canc_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 0, idm_g)
        spr_canc_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 1, idm_g)
        spr_canc_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 2, idm_g)
        spr_canc_hover = aclarar_boton(spr_canc_norm) if spr_canc_norm else None

        captura_aviso = pantalla.copy()
        esperando = True
        reintentar = False

        pygame.event.clear()

        while esperando:
            reloj.tick(60)
            pos_m = pygame.mouse.get_pos()
            h_rein = b_rein.collidepoint(pos_m)
            h_canc = b_canc.collidepoint(pos_m)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    pygame.event.clear()
                    return False
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    esperando = False
                    reintentar = True
                    pygame.event.clear()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if b_rein.collidepoint(ev.pos):
                        pulsado = True
                        if spr_rein_semi and spr_rein_apret:
                            pulsado = animar_pulsacion_boton(pantalla, b_rein, spr_rein_semi, spr_rein_apret, (253, 246, 233), spr_rein_norm, tipo_sonido="ventana_reintentar")
                        else:
                            reproducir_sonido_ui("ventana_reintentar")
                        if pulsado:
                            esperando = False
                            reintentar = True
                            pygame.event.clear()
                    elif b_canc.collidepoint(ev.pos):
                        pulsado = True
                        if spr_canc_semi and spr_canc_apret:
                            pulsado = animar_pulsacion_boton(pantalla, b_canc, spr_canc_semi, spr_canc_apret, (253, 246, 233), spr_canc_norm, tipo_sonido="ventana_cancelar")
                        else:
                            reproducir_sonido_ui("ventana_cancelar")
                        if pulsado:
                            pygame.event.clear()
                            return False

            pantalla.blit(captura_aviso, (0, 0))
            pygame.draw.rect(pantalla, (253, 246, 233), r_a, border_radius=14)
            pygame.draw.rect(pantalla, (220, 70, 60), r_a, width=3, border_radius=14)

            t_err_tit = fuente_tit.render("ACCESO DENEGADO", True, (215, 50, 50))
            pantalla.blit(t_err_tit, t_err_tit.get_rect(center=(r_a.centerx, r_a.top + 38)))

            rect_err_desc = pygame.Rect(r_a.left + 30, r_a.top + 64, r_a.width - 60, 80)
            dibujar_texto_en_rect(
                pantalla,
                "La contraseña introducida\nes incorrecta.",
                rect_err_desc,
                categoria="texto",
                tamano=17,
                color=(70, 55, 45),
                multiline=True,
                alineacion="centro",
                alineacion_v="centro",
                padding=2,
                interlineado=4
            )

            if spr_rein_norm:
                pantalla.blit(spr_rein_hover if (h_rein and spr_rein_hover) else spr_rein_norm, b_rein)
            else:
                pygame.draw.rect(pantalla, (82, 194, 114) if h_rein else (68, 172, 98), b_rein, border_radius=8)
                t_br = fuente_btn.render("REINTENTAR", True, (255, 255, 255))
                pantalla.blit(t_br, t_br.get_rect(center=b_rein.center))

            if spr_canc_norm:
                pantalla.blit(spr_canc_hover if (h_canc and spr_canc_hover) else spr_canc_norm, b_canc)
            else:
                pygame.draw.rect(pantalla, (255, 255, 255) if h_canc else (242, 234, 222), b_canc, border_radius=8)
                pygame.draw.rect(pantalla, (185, 155, 125), b_canc, width=2, border_radius=8)
                t_bc = fuente_btn.render("CANCELAR", True, (60, 45, 35))
                pantalla.blit(t_bc, t_bc.get_rect(center=b_canc.center))

            pygame.display.flip()

        if not reintentar:
            pygame.event.clear()
            return False


def modal_administrar_perfil(pantalla, reloj, partida):
    """
    Diálogo para administrar un perfil:
    - Cambiar nombre
    - Agregar / Cambiar / Quitar contraseña
    - Eliminar perfil
    - Botón «VOLVER» oficial del proyecto para regresar sin cambios
    Retorna True si hubo cambios que requieren refrescar la lista, o False al salir.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(15, negrita=False)
    fuente_btn = obtener_fuente_subtitulo(16, negrita=True)

    # Dimensiones equilibradas del modal sin botón inferior (cerrado mediante la X)
    w_card, h_card = 560, 335
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    # Botón X en la esquina superior derecha del modal
    W_X, H_X = 29, 34
    rect_btn_x = pygame.Rect(rect_card.right - W_X - 16, rect_card.top + 16, W_X, H_X)
    spr_x_norm = _cargar_sprite_boton("HUD/boton-x.png", W_X, H_X) or _cargar_sprite_boton("boton-x.png", W_X, H_X)
    spr_x_semi = _cargar_sprite_boton("HUD/boton-x-semiapretado.png", W_X, H_X) or _cargar_sprite_boton("boton-x-semiapretado.png", W_X, H_X)
    spr_x_apr = _cargar_sprite_boton("HUD/boton-x-apretado.png", W_X, H_X) or _cargar_sprite_boton("boton-x-apretado.png", W_X, H_X)
    spr_x_hover = aclarar_boton(spr_x_norm) if spr_x_norm else None

    w_b, h_b = 360, 48
    x_b = rect_card.centerx - (w_b // 2)
    y_base = rect_card.top + 114
    gap_b = 14

    btn_renombrar = pygame.Rect(x_b, y_base, w_b, h_b)
    btn_password = pygame.Rect(x_b, y_base + (h_b + gap_b), w_b, h_b)
    btn_eliminar = pygame.Rect(x_b, y_base + (h_b + gap_b) * 2, w_b, h_b)

    fondo_tarjeta = (253, 246, 233)
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    hubo_cambios = False

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        hov_ren = btn_renombrar.collidepoint(pos_mouse)
        hov_pwd = btn_password.collidepoint(pos_mouse)
        hov_eli = btn_eliminar.collidepoint(pos_mouse)
        hov_x = rect_btn_x.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return hubo_cambios

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # 1. Clic en botón X de cerrar
                if rect_btn_x.collidepoint(evento.pos):
                    pulsado = True
                    if spr_x_semi and spr_x_apr:
                        pulsado = animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apr, fondo_tarjeta, spr_x_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        return hubo_cambios

                # 2. Clic en Cambiar Nombre
                elif btn_renombrar.collidepoint(evento.pos):
                    reproducir_sonido_ui("partida_gestionar")
                    nuevo_nom = solicitar_texto_modal(
                        pantalla, reloj,
                        titulo=t("cambiar_nombre"),
                        subtitulo=f"Introduce el nuevo nombre para «{partida['nombre']}»:",
                        valor_inicial=partida["nombre"],
                        permitir_vacio=False,
                    )
                    if nuevo_nom and nuevo_nom != partida["nombre"]:
                        renombrar_partida(partida["id"], nuevo_nom)
                        partida["nombre"] = nuevo_nom
                        hubo_cambios = True

                # 3. Clic en Contraseña
                elif btn_password.collidepoint(evento.pos):
                    reproducir_sonido_ui("partida_gestionar")
                    # Si ya tiene contraseña, autenticar primero
                    if partida.get("tiene_password", False):
                        if not pedir_password_modal(pantalla, reloj, partida):
                            continue
                        # Preguntar nueva contraseña o dejar vacío para quitar
                        nueva_pwd = solicitar_texto_modal(
                            pantalla, reloj,
                            titulo=t("cambiar_quitar_clave"),
                            subtitulo="Escribe una nueva contraseña o deja vacío para quitarla:",
                            es_password=True,
                            permitir_vacio=True,
                        )
                        if nueva_pwd is not None:
                            cambiar_password_partida(partida["id"], nueva_pwd)
                            partida["tiene_password"] = bool(nueva_pwd.strip())
                            hubo_cambios = True
                    else:
                        # No tiene contraseña: agregar una
                        nueva_pwd = solicitar_texto_modal(
                            pantalla, reloj,
                            titulo=t("agregar_clave"),
                            subtitulo=f"Asigna una contraseña de acceso a «{partida['nombre']}»:",
                            es_password=True,
                            permitir_vacio=False,
                        )
                        if nueva_pwd:
                            cambiar_password_partida(partida["id"], nueva_pwd)
                            partida["tiene_password"] = True
                            hubo_cambios = True

                # 4. Clic en Eliminar
                elif btn_eliminar.collidepoint(evento.pos):
                    reproducir_sonido_ui("partida_borrar")
                    if mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
                        eliminar_partida(partida["id"])
                        return True

                # 5. Clic fuera del modal para salir
                elif not rect_card.collidepoint(evento.pos):
                    return hubo_cambios

        # Dibujar modal
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        # Botón X de cabecera
        spr_x_dib = spr_x_hover if (hov_x and spr_x_hover) else spr_x_norm
        if spr_x_dib:
            pantalla.blit(spr_x_dib, rect_btn_x)

        # Título centrado con margen seguro
        rect_tit = pygame.Rect(rect_card.left + 44, rect_card.top + 14, rect_card.width - 88, 34)
        dibujar_texto_en_rect(pantalla, t("administrar_perfil"), rect_tit, categoria="titulo", tamano=22, color=(60, 45, 35))

        # Información distribuida en dos líneas con autoajuste para nombres extensos
        nom_perfil = obtener_nombre_partida_visible(partida)
        rect_nom = pygame.Rect(rect_card.left + 24, rect_card.top + 52, rect_card.width - 48, 28)
        dibujar_texto_en_rect(pantalla, f"{t('perfil')}: «{nom_perfil}»", rect_nom, categoria="subtitulo", tamano=22, color=(70, 55, 45), negrita=True, padding=4)

        tiene_p = partida.get("tiene_password", False)
        txt_est = t("estado_protegido") if tiene_p else t("estado_sin_clave")
        col_est = (40, 130, 65) if tiene_p else (125, 105, 90)
        rect_est = pygame.Rect(rect_card.left + 24, rect_card.top + 82, rect_card.width - 48, 24)
        dibujar_texto_en_rect(pantalla, txt_est, rect_est, categoria="subtitulo", tamano=18, color=col_est, padding=4)

        # 1. Renombrar (Sprite oficial)
        spr_ren = generar_boton_con_texto("mundos/boton-volver.png", w_b, h_b, t("cambiar_nombre"), (60, 45, 30), 16)
        if hov_ren and spr_ren: spr_ren = aclarar_boton(spr_ren)
        if spr_ren: pantalla.blit(spr_ren, btn_renombrar)

        # 2. Contraseña (Sprite oficial)
        txt_btn_pwd = t("cambiar_quitar_clave") if tiene_p else t("agregar_clave")
        spr_pwd = generar_boton_con_texto("mundos/boton-volver.png", w_b, h_b, txt_btn_pwd, (60, 45, 30), 16)
        if hov_pwd and spr_pwd: spr_pwd = aclarar_boton(spr_pwd)
        if spr_pwd: pantalla.blit(spr_pwd, btn_password)

        # 3. Eliminar (Sprite oficial)
        spr_eli = generar_boton_con_texto("Menu/salir.png", w_b, h_b, t("eliminar_perfil"), (125, 48, 17), 16)
        if hov_eli and spr_eli: spr_eli = aclarar_boton(spr_eli)
        if spr_eli: pantalla.blit(spr_eli, btn_eliminar)

        pygame.display.flip()


def mostrar_dialogo_partida_existente(pantalla, reloj, nombre):
    """
    Diálogo modal de confirmación cuando ya existe una partida con el nombre ingresado.
    Ofrece 3 opciones:
    - «OTRO NOMBRE»: para ingresar otro nombre identificador.
    - «SOBRESCRIBIR»: confirmación explícita para reemplazar la partida existente.
    - «CANCELAR»: aborta la operación y regresa utilizando el botón oficial existente.
    Retorna "cambiar", "sobrescribir" o "cancelar".
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=22)

    w_card, h_card = 560, 290
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    w_btn, h_btn = 163, 48
    gap_btn = 16
    total_w = w_btn * 3 + gap_btn * 2
    x_base = rect_card.centerx - (total_w // 2)
    y_btns = rect_card.top + 210

    btn_cambiar = pygame.Rect(x_base, y_btns, w_btn, h_btn)
    btn_sobrescribir = pygame.Rect(x_base + w_btn + gap_btn, y_btns, w_btn, h_btn)
    btn_cancelar = pygame.Rect(x_base + (w_btn + gap_btn) * 2, y_btns, w_btn, h_btn)

    spr_canc_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 0)
    spr_canc_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 1)
    spr_canc_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 2)
    spr_canc_hover = aclarar_boton(spr_canc_norm) if spr_canc_norm else None
    fondo_tarjeta = (253, 246, 233)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        hov_cam = btn_cambiar.collidepoint(pos_mouse)
        hov_sob = btn_sobrescribir.collidepoint(pos_mouse)
        hov_can = btn_cancelar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cambiar.collidepoint(evento.pos):
                    reproducir_sonido_ui("ventana_aceptar")
                    return "cambiar"
                elif btn_sobrescribir.collidepoint(evento.pos):
                    reproducir_sonido_ui("ventana_aceptar")
                    return "sobrescribir"
                elif btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_canc_semi and spr_canc_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_canc_semi, spr_canc_apret, fondo_tarjeta, spr_canc_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        return "cancelar"

        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (225, 120, 48), rect_card, width=3, border_radius=16)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 24, rect_card.top + 16, rect_card.width - 48, 32)
        dibujar_texto_en_rect(pantalla, t("partida_existente"), rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(205, 80, 40))

        # Mensaje de advertencia con soporte de ajuste automático
        rect_msg = pygame.Rect(rect_card.left + 24, rect_card.top + 54, rect_card.width - 48, 32)
        dibujar_texto_en_rect(pantalla, f"{t('ya_existe_partida_con_nombre')} «{nombre}».", rect_msg, categoria="subtitulo", tamano=16, color=(60, 45, 35), multiline=True, padding=2)

        rect_sub = pygame.Rect(rect_card.left + 24, rect_card.top + 92, rect_card.width - 48, 44)
        dibujar_texto_en_rect(pantalla, t("elegir_otro_o_sobrescribir"), rect_sub, categoria="subtitulo", tamano=15, color=(115, 95, 80), multiline=True, padding=2)

        # Botón 1: Cambiar nombre (Sprite oficial)
        spr_cam = generar_boton_con_texto("mundos/boton-volver.png", btn_cambiar.w, btn_cambiar.h, t("otro_nombre"), (60, 45, 30), TAMANO_BOTON_MODAL)
        if hov_cam and spr_cam: spr_cam = aclarar_boton(spr_cam)
        if spr_cam: pantalla.blit(spr_cam, btn_cambiar)

        # Botón 2: Sobrescribir (Sprite oficial)
        spr_sob = generar_boton_con_texto("Menu/salir.png", btn_sobrescribir.w, btn_sobrescribir.h, t("sobrescribir"), (255, 255, 255), TAMANO_BOTON_MODAL)
        if hov_sob and spr_sob: spr_sob = aclarar_boton(spr_sob)
        if spr_sob: pantalla.blit(spr_sob, btn_sobrescribir)

        # Botón 3: Cancelar (reutiliza el botón oficial del proyecto)
        if spr_canc_norm:
            pantalla.blit(spr_canc_hover if (hov_can and spr_canc_hover) else spr_canc_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            dibujar_texto_en_rect(pantalla, t("cancelar").upper(), btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        pygame.display.flip()


def flujo_crear_nueva_partida(
    pantalla,
    reloj,
    color_p1="Celeste",
    color_p2="Violeta",
    accesorio_p1="Ninguno",
    accesorio_p2="Ninguno",
):
    """
    Permite crear una partida independiente:
    - Pide un nombre para identificarla.
    - Si ya existe una con ese nombre, pide confirmación o solicita otro nombre (nunca sobrescribe silenciosamente).
    - Permite establecer una contraseña opcional.
    - Guarda la personalización actual de ambos personajes (colores y accesorios) en esta partida.
    - Si se cancela en cualquier paso, retorna None y no persiste ningún cambio.
    - Retorna el diccionario de la nueva partida creada, o None si se canceló.
    """
    partidas = cargar_partidas()
    nuevo_id = max([p["id"] for p in partidas], default=0) + 1
    nombre_sugerido = f"{t('partida')} {nuevo_id}"

    nombre_final = None
    id_sobrescribir = None

    while True:
        nom = solicitar_texto_modal(
            pantalla, reloj,
            titulo=t("nueva_partida"),
            subtitulo=t("ingresa_nombre_partida"),
            valor_inicial=nombre_sugerido,
            es_password=False,
            permitir_vacio=False,
            max_caracteres=18,
        )
        if not nom:
            return None

        nom = nom.strip()
        partidas = cargar_partidas()
        existente = next((p for p in partidas if p["nombre"].strip().lower() == nom.lower() or obtener_nombre_partida_visible(p).lower() == nom.lower()), None)

        if existente:
            decision = mostrar_dialogo_partida_existente(pantalla, reloj, existente["nombre"])
            if decision == "cambiar":
                nombre_sugerido = nom
                continue
            elif decision == "sobrescribir":
                if existente.get("tiene_password"):
                    if not pedir_password_modal(pantalla, reloj, existente):
                        continue
                nombre_final = existente["nombre"]
                id_sobrescribir = existente["id"]
                break
            else:
                return None
        else:
            nombre_final = nom
            id_sobrescribir = None
            break

    # Contraseña opcional
    pwd = solicitar_texto_modal(
        pantalla, reloj,
        titulo=t("contrasena_opcional"),
        subtitulo=t("sub_contrasena_opcional"),
        es_password=True,
        permitir_vacio=True,
        max_caracteres=18,
    )
    if pwd is None:
        return None

    es_adm = es_partida_admin(nombre_final)
    desbloqueados_nuevos = crear_desbloqueados_inicial(es_admin=es_adm)
    partida_creada = guardar_partida(
        desbloqueados_nuevos,
        id_partida=id_sobrescribir,
        nombre_partida=nombre_final,
        password=pwd,
        color_p1=color_p1,
        color_p2=color_p2,
        accesorio_p1=accesorio_p1,
        accesorio_p2=accesorio_p2,
    )
    if partida_creada is None:
        return None
    partida_creada["password_plain"] = pwd or ""
    partida_creada["es_admin"] = es_adm
    return partida_creada


def modal_flujo_guardar_perfil(
    pantalla,
    reloj,
    niveles_desbloqueados,
    id_partida_actual=None,
    nombre_partida_actual=None,
    password_partida_actual=None,
    color_p1=None,
    color_p2=None,
    accesorio_p1=None,
    accesorio_p2=None,
):
    """
    Flujo interactivo completo al presionar «Guardar y salir»:
    Permite:
    1. Si hay una partida actual provisional, guardarla directamente con su nombre elegido.
    2. Seleccionar un perfil existente para actualizarlo.
    3. Crear un perfil nuevo con nombre y contraseña opcional.
    Retorna True si el guardado fue exitoso y se completó, o False si se canceló.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_item_tit = obtener_fuente_boton(TAMANO_ITEM_TITULO, tamano_fallback=22)
    fuente_item_det = obtener_fuente_pequena(TAMANO_PEQUENA)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=22)
    fuente_pag = obtener_fuente_contador(TAMANO_SUBTITULO)

    w_card, h_card = 640, 570
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    pagina_guardar = 0
    MAX_SLOTS = 4
    partidas = cargar_partidas()

    # Reutilizar el botón Cancelar oficial del proyecto con proporciones exactas
    w_can, h_can = 204, 60
    btn_cancelar = pygame.Rect(rect_card.centerx - (w_can // 2), rect_card.top + 488, w_can, h_can)
    spr_can_norm = _cargar_sprite_boton("Menu/boton-cancelar.png", w_can, h_can) or _cargar_sprite_boton("boton-cancelar.png", w_can, h_can)
    spr_can_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_can, h_can, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 0)
    spr_can_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_can, h_can, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 1)
    spr_can_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_can, h_can, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 2)
    spr_can_hover = aclarar_boton(spr_can_norm) if spr_can_norm else None
    fondo_tarjeta = (253, 246, 233)

    # Identificar si la partida actual está en memoria o registrada
    es_provisional = bool(nombre_partida_actual and not any(p.get("id") == id_partida_actual for p in partidas))
    nom_actual_vis = obtener_nombre_partida_visible(nombre_partida_actual) if nombre_partida_actual else ""
    texto_btn_crear = f"+ {t('guardar_en')} «{nom_actual_vis}»" if nom_actual_vis else f"+ {t('crear_nueva_partida')}"

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        # Botón superior
        btn_crear_nuevo = pygame.Rect(rect_card.left + 40, rect_card.top + 76, w_card - 80, 42)
        hov_crear = btn_crear_nuevo.collidepoint(pos_mouse)
        hov_can = btn_cancelar.collidepoint(pos_mouse)

        total_paginas = max(1, (len(partidas) + MAX_SLOTS - 1) // MAX_SLOTS)
        if pagina_guardar >= total_paginas:
            pagina_guardar = max(0, total_paginas - 1)

        idx_inicio = pagina_guardar * MAX_SLOTS
        partidas_mostrar = partidas[idx_inicio:idx_inicio + MAX_SLOTS]

        # Slots organizados con altura y separación fijas sin superposición (top + 130 a top + 396)
        slots = []
        y_slot = rect_card.top + 130
        h_slot = 62
        gap_slot = 6

        for idx, p in enumerate(partidas_mostrar):
            r_s = pygame.Rect(rect_card.left + 40, y_slot + idx * (h_slot + gap_slot), w_card - 80, h_slot)
            slots.append((r_s, p))

        # Paginación organizada entre slots y botón cancelar (top + 418 a top + 446)
        btn_pag_ant = pygame.Rect(rect_card.centerx - 100, rect_card.top + 418, 32, 28) if total_paginas > 1 else None
        btn_pag_sig = pygame.Rect(rect_card.centerx + 68, rect_card.top + 418, 32, 28) if total_paginas > 1 else None

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_can_semi and spr_can_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_can_semi, spr_can_apret, fondo_tarjeta, spr_can_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        return False

                if btn_pag_ant and btn_pag_ant.collidepoint(evento.pos) and pagina_guardar > 0:
                    pagina_guardar -= 1
                    reproducir_sonido_ui("pagina")
                    continue
                elif btn_pag_sig and btn_pag_sig.collidepoint(evento.pos) and pagina_guardar < total_paginas - 1:
                    pagina_guardar += 1
                    reproducir_sonido_ui("pagina")
                    continue

                if btn_crear_nuevo.collidepoint(evento.pos):
                    reproducir_sonido_ui("partida_nueva")
                    if nombre_partida_actual:
                        res = guardar_partida(
                            niveles_desbloqueados,
                            id_partida=id_partida_actual,
                            nombre_partida=nombre_partida_actual,
                            password=password_partida_actual,
                            color_p1=color_p1,
                            color_p2=color_p2,
                            accesorio_p1=accesorio_p1,
                            accesorio_p2=accesorio_p2,
                        )
                        if res is not None:
                            return True
                    else:
                        # Pedir nombre de partida
                        partidas_actuales = cargar_partidas()
                        nuevo_id = max([p["id"] for p in partidas_actuales], default=0) + 1
                        sug_nom = f"{t('partida')} {nuevo_id}"

                        nom_final = None
                        id_sobrescribir = None

                        while True:
                            nom = solicitar_texto_modal(
                                pantalla, reloj,
                                titulo=t("nueva_partida"),
                                subtitulo=t("ingresa_nombre_partida"),
                                valor_inicial=sug_nom,
                                permitir_vacio=False,
                            )
                            if not nom:
                                break

                            nom = nom.strip()
                            partidas_actuales = cargar_partidas()
                            existente = next((p for p in partidas_actuales if p["nombre"].strip().lower() == nom.lower() or obtener_nombre_partida_visible(p).lower() == nom.lower()), None)
                            if existente:
                                decision = mostrar_dialogo_partida_existente(pantalla, reloj, existente["nombre"])
                                if decision == "cambiar":
                                    sug_nom = nom
                                    continue
                                elif decision == "sobrescribir":
                                    if existente.get("tiene_password"):
                                        if not pedir_password_modal(pantalla, reloj, existente):
                                             continue
                                    nom_final = existente["nombre"]
                                    id_sobrescribir = existente["id"]
                                    break
                                else:
                                    break
                            else:
                                nom_final = nom
                                id_sobrescribir = None
                                break

                        if not nom_final:
                            continue

                        # Preguntar contraseña opcional
                        pwd = solicitar_texto_modal(
                            pantalla, reloj,
                            titulo="CONTRASEÑA (OPCIONAL)",
                            subtitulo="Asigna una contraseña o deja vacío si no deseas protegerla:",
                            es_password=True,
                            permitir_vacio=True,
                        )
                        if pwd is None:
                            continue

                        res = guardar_partida(
                            niveles_desbloqueados,
                            id_partida=id_sobrescribir,
                            nombre_partida=nom_final,
                            password=pwd,
                            color_p1=color_p1,
                            color_p2=color_p2,
                            accesorio_p1=accesorio_p1,
                            accesorio_p2=accesorio_p2,
                        )
                        if res is not None:
                            return True

                for r_s, p in slots:
                    if r_s.collidepoint(evento.pos):
                        reproducir_sonido_ui("partida_cargar")
                        # Si tiene contraseña, pedirla antes de actualizar
                        if p.get("tiene_password", False):
                            if not pedir_password_modal(pantalla, reloj, p):
                                break

                        res = guardar_partida(
                            niveles_desbloqueados,
                            id_partida=p["id"],
                            nombre_partida=p["nombre"],
                            color_p1=color_p1 if color_p1 is not None else p.get("color_p1"),
                            color_p2=color_p2 if color_p2 is not None else p.get("color_p2"),
                            accesorio_p1=accesorio_p1 if accesorio_p1 is not None else p.get("accesorio_p1"),
                            accesorio_p2=accesorio_p2 if accesorio_p2 is not None else p.get("accesorio_p2"),
                        )
                        if res is not None:
                            return True

        # Dibujar pantalla
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        t_tit = fuente_titulo.render(t("guardar_salir"), True, (60, 45, 35))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 30)))

        t_sub = fuente_sub.render(t("elige_partida_o_crea"), True, (115, 95, 80))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 56)))

        # Botón crear nuevo / guardar sesión provisional
        col_cr = (82, 194, 114) if hov_crear else (68, 172, 98)
        pygame.draw.rect(pantalla, col_cr, btn_crear_nuevo, border_radius=8)
        pygame.draw.rect(pantalla, (45, 130, 70), btn_crear_nuevo, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, texto_btn_crear, btn_crear_nuevo, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=4)

        if not partidas:
            t_sin = fuente_sub.render("Todavía no tenés partidas guardadas.", True, (120, 105, 90))
            pantalla.blit(t_sin, t_sin.get_rect(center=(rect_card.centerx, rect_card.top + 220)))
            t_sin2 = fuente_item_det.render("Pulsa «+ CREAR NUEVA PARTIDA» arriba para guardar tu progreso.", True, (140, 125, 110))
            pantalla.blit(t_sin2, t_sin2.get_rect(center=(rect_card.centerx, rect_card.top + 250)))
        else:
            # Lista de perfiles
            for r_s, p in slots:
                hov_s = r_s.collidepoint(pos_mouse)
                es_actual = (id_partida_actual is not None and p["id"] == id_partida_actual)
                col_s = (255, 252, 244) if hov_s else (255, 255, 255)
                borde_s = (45, 145, 75) if es_actual else ((225, 145, 75) if hov_s else (220, 202, 178))
                pygame.draw.rect(pantalla, col_s, r_s, border_radius=8)
                pygame.draw.rect(pantalla, borde_s, r_s, width=2 if (hov_s or es_actual) else 1, border_radius=8)

                nom_s_vis = obtener_nombre_partida_visible(p)
                txt_nom = f"{nom_s_vis} ({t('mundo')} {p['mundo_max']}-{p['nivel_max']})"
                if es_actual:
                    txt_nom += f"  [{t('partida_actual')}]"
                r_nom_s = pygame.Rect(r_s.left + 16, r_s.top + 8, r_s.width - 55, 22)
                dibujar_texto_en_rect(pantalla, txt_nom, r_nom_s, categoria="subtitulo", tamano=16, color=(40, 115, 60) if es_actual else (55, 45, 35), alineacion="izquierda", padding=0)

                if es_partida_admin(p):
                    det = f"{t('todos_desbloqueados')}  •  {t('guardado')}: {p.get('fecha', '')}"
                else:
                    cant_comp = calcular_niveles_completados(p.get("niveles_desbloqueados", {}))
                    det = f"{t('niveles_completados')}: {cant_comp}/15  •  {t('guardado')}: {p.get('fecha', '')}"
                r_det_s = pygame.Rect(r_s.left + 16, r_s.top + 32, r_s.width - 55, 20)
                dibujar_texto_en_rect(pantalla, det, r_det_s, categoria="pequena", tamano=13, color=(115, 100, 85), alineacion="izquierda", padding=0)

                candado = "🔒" if p.get("tiene_password") else "🔓"
                t_cand = fuente_sub.render(candado, True, (60, 45, 35))
                pantalla.blit(t_cand, (r_s.right - 35, r_s.centery - 10))

            # Paginación
            if total_paginas > 1:
                hov_p_ant = btn_pag_ant.collidepoint(pos_mouse) and pagina_guardar > 0
                hov_p_sig = btn_pag_sig.collidepoint(pos_mouse) and pagina_guardar < total_paginas - 1
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_p_ant else (240, 230, 215), btn_pag_ant, border_radius=6)
                pygame.draw.rect(pantalla, (180, 150, 120), btn_pag_ant, width=1, border_radius=6)
                col_fl_ant = (60, 45, 35) if pagina_guardar > 0 else (175, 160, 145)
                cx_pa, cy_pa = btn_pag_ant.center
                for dy in range(-5, 6):
                    ancho_f = 5 - abs(dy)
                    for dx in range(ancho_f + 1):
                        pantalla.set_at((cx_pa + 2 - dx, cy_pa + dy), col_fl_ant)

                t_pnum = fuente_pag.render(f"{pagina_guardar + 1} / {total_paginas}", True, (80, 65, 55))
                pantalla.blit(t_pnum, t_pnum.get_rect(center=(rect_card.centerx, rect_card.top + 432)))

                pygame.draw.rect(pantalla, (255, 255, 255) if hov_p_sig else (240, 230, 215), btn_pag_sig, border_radius=6)
                pygame.draw.rect(pantalla, (180, 150, 120), btn_pag_sig, width=1, border_radius=6)
                col_fl_sig = (60, 45, 35) if pagina_guardar < total_paginas - 1 else (175, 160, 145)
                cx_ps, cy_ps = btn_pag_sig.center
                for dy in range(-5, 6):
                    ancho_f = 5 - abs(dy)
                    for dx in range(ancho_f + 1):
                        pantalla.set_at((cx_ps - 2 + dx, cy_ps + dy), col_fl_sig)

        # Botón Cancelar (reutiliza el botón oficial del proyecto con proporciones 3.4:1)
        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_c = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_c, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            dibujar_texto_en_rect(pantalla, t("cancelar").upper(), btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=4)

        pygame.display.flip()


def mostrar_dialogo_guardar_salir(
    pantalla,
    reloj,
    niveles_desbloqueados,
    id_partida=None,
    nombre_partida=None,
    password_partida=None,
    color_p1=None,
    color_p2=None,
    accesorio_p1=None,
    accesorio_p2=None,
):
    """
    Muestra la confirmación clara obligatoria con las tres opciones:
    1. «GUARDAR Y SALIR»: abre el procedimiento para guardar y cierra solo si finalizó con éxito.
    2. «SALIR SIN GUARDAR»: cierra el juego sin persistir los cambios pendientes ni alterar guardados.
    3. «CANCELAR»: cierra el diálogo y vuelve exactamente a la pantalla en que estaba el jugador.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    mundo_max, nivel_max = obtener_maximo_alcanzado(niveles_desbloqueados)

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=36)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO_GRANDE)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=28)

    ancho_card, alto_card = 560, 480
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 272, 80
    x_btn = rect_card.centerx - (w_btn // 2)
    y_base_btns = rect_card.top + 140
    espacio_btns = 14

    btn_guardar = pygame.Rect(x_btn, y_base_btns, w_btn, h_btn)
    btn_no_guardar = pygame.Rect(x_btn, y_base_btns + h_btn + espacio_btns, w_btn, h_btn)
    btn_cancelar = pygame.Rect(x_btn, y_base_btns + (h_btn + espacio_btns) * 2, w_btn, h_btn)

    def _scale_btn(nombre, w, h):
        return cargar_boton_escalado(nombre, w, h)

    idm_act = obtener_idioma()
    if idm_act == "es":
        spr_g_norm = _scale_btn("Ventanas/boton-guardar-y-salir.png", w_btn, h_btn) or _scale_btn("boton-guardar-y-salir.png", w_btn, h_btn)
        spr_g_semi = _scale_btn("Ventanas/boton-guardar-y-salir-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-guardar-y-salir-semiapretado.png", w_btn, h_btn)
        spr_g_apret = _scale_btn("Ventanas/boton-guardar-y-salir-apretado.png", w_btn, h_btn) or _scale_btn("boton-guardar-y-salir-apretado.png", w_btn, h_btn)

        spr_s_norm = _scale_btn("Ventanas/boton-salir-sin-guardar.png", w_btn, h_btn) or _scale_btn("Menu/boton-salir-sin-guardar.png", w_btn, h_btn) or _scale_btn("boton-salir-sin-guardar.png", w_btn, h_btn)
        spr_s_semi = _scale_btn("Menu/boton-salir-sin-guardar-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-salir-sin-guardar-semiapretado.png", w_btn, h_btn)
        spr_s_apret = _scale_btn("Ventanas/boton-salir-sin-guardar-apretado.png", w_btn, h_btn) or _scale_btn("Menu/boton-salir-sin-guardar-apretado.png", w_btn, h_btn) or _scale_btn("boton-salir-sin-guardar-apretado.png", w_btn, h_btn)

        spr_c_norm = _scale_btn("Menu/boton-cancelar.png", w_btn, h_btn) or _scale_btn("boton-cancelar.png", w_btn, h_btn)
        spr_c_semi = _scale_btn("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-cancelar-semiapretado.png", w_btn, h_btn)
        spr_c_apret = _scale_btn("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _scale_btn("boton-cancelar-apretado.png", w_btn, h_btn)
    else:
        spr_g_norm = generar_boton_con_texto("Ventanas/boton-guardar-y-salir.png", w_btn, h_btn, t("guardar_salir").upper(), (255, 255, 255), TAMANO_BOTON_MODAL)
        spr_g_semi = generar_boton_con_texto("Ventanas/boton-guardar-y-salir-semiapretado.png", w_btn, h_btn, t("guardar_salir").upper(), (255, 255, 255), TAMANO_BOTON_MODAL, 1) or spr_g_norm
        spr_g_apret = generar_boton_con_texto("Ventanas/boton-guardar-y-salir-apretado.png", w_btn, h_btn, t("guardar_salir").upper(), (255, 255, 255), TAMANO_BOTON_MODAL, 2) or spr_g_norm

        spr_s_norm = generar_boton_con_texto("Ventanas/boton-salir-sin-guardar.png", w_btn, h_btn, t("salir_sin_guardar").upper(), (255, 255, 255), TAMANO_BOTON_MODAL)
        spr_s_semi = generar_boton_con_texto("Menu/boton-salir-sin-guardar-semiapretado.png", w_btn, h_btn, t("salir_sin_guardar").upper(), (255, 255, 255), TAMANO_BOTON_MODAL, 1) or spr_s_norm
        spr_s_apret = generar_boton_con_texto("Ventanas/boton-salir-sin-guardar-apretado.png", w_btn, h_btn, t("salir_sin_guardar").upper(), (255, 255, 255), TAMANO_BOTON_MODAL, 2) or spr_s_norm

        spr_c_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL)
        spr_c_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 1) or spr_c_norm
        spr_c_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 2) or spr_c_norm

    spr_g_hover = aclarar_boton(spr_g_norm) if spr_g_norm else None
    spr_s_hover = aclarar_boton(spr_s_norm) if spr_s_norm else None
    spr_c_hover = aclarar_boton(spr_c_norm) if spr_c_norm else None
    fondo_tarjeta = (253, 246, 233)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    captura_previa = pantalla.copy()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()
        hov_g = btn_guardar.collidepoint(pos_mouse)
        hov_s = btn_no_guardar.collidepoint(pos_mouse)
        hov_c = btn_cancelar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "cancelar"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_guardar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_g_semi and spr_g_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_guardar, spr_g_semi, spr_g_apret, fondo_tarjeta, spr_g_norm, tipo_sonido="ventana_aceptar")
                    else:
                        reproducir_sonido_ui("ventana_aceptar")
                    if pulsado:
                        guardado_ok = modal_flujo_guardar_perfil(
                            pantalla, reloj,
                            niveles_desbloqueados=niveles_desbloqueados,
                            id_partida_actual=id_partida,
                            nombre_partida_actual=nombre_partida,
                            password_partida_actual=password_partida,
                            color_p1=color_p1,
                            color_p2=color_p2,
                            accesorio_p1=accesorio_p1,
                            accesorio_p2=accesorio_p2,
                        )
                        if guardado_ok:
                            return "guardar_salir"

                elif btn_no_guardar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_s_semi and spr_s_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_no_guardar, spr_s_semi, spr_s_apret, fondo_tarjeta, spr_s_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        return "salir_sin_guardar"

                elif btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_c_semi and spr_c_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_c_semi, spr_c_apret, fondo_tarjeta, spr_c_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        return "cancelar"

        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=18)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 24, rect_card.top + 20, rect_card.width - 48, 36)
        dibujar_texto_en_rect(pantalla, t("deseas_guardar"), rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(60, 45, 35))

        # Información de mundo y nivel
        rect_info = pygame.Rect(rect_card.left + 24, rect_card.top + 64, rect_card.width - 48, 28)
        dibujar_texto_en_rect(pantalla, f"{t('mundo')} {mundo_max} - {t('nivel')} {nivel_max}", rect_info, categoria="texto", tamano=TAMANO_TEXTO, color=(55, 45, 35))

        # Subtítulo explicativo con multilínea segura
        rect_sub = pygame.Rect(rect_card.left + 24, rect_card.top + 96, rect_card.width - 48, 36)
        dibujar_texto_en_rect(pantalla, t("deseas_guardar_sub", default="Puedes guardar tu partida en un perfil antes de salir."), rect_sub, categoria="texto", tamano=15, color=(120, 105, 90), multiline=True, padding=2)

        if spr_g_norm:
            pantalla.blit(spr_g_hover if (hov_g and spr_g_hover) else spr_g_norm, btn_guardar)
        else:
            pygame.draw.rect(pantalla, (82, 194, 114) if hov_g else (68, 172, 98), btn_guardar, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("guardar_salir"), btn_guardar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=8)

        if spr_s_norm:
            pantalla.blit(spr_s_hover if (hov_s and spr_s_hover) else spr_s_norm, btn_no_guardar)
        else:
            pygame.draw.rect(pantalla, (235, 95, 90) if hov_s else (215, 80, 75), btn_no_guardar, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("salir_sin_guardar"), btn_no_guardar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=8)

        if spr_c_norm:
            pantalla.blit(spr_c_hover if (hov_c and spr_c_hover) else spr_c_norm, btn_cancelar)
        else:
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_c else (242, 234, 222), btn_cancelar, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("cancelar").upper(), btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=8)

        pygame.display.flip()


def mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
    """
    Muestra un diálogo modal interactivo con estética pastel crema solicitando confirmación para borrar una partida.
    Advierte que se eliminará permanentemente la partida guardada correspondiente.
    Retorna True si se confirma («BORRAR PARTIDA»), o False si se cancela.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=34)
    fuente_nombre = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=24)

    ancho_card, alto_card = 560, 310
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 184, 54
    gap_btn = 22
    total_w_btns = (w_btn * 2) + gap_btn
    x_cancelar = rect_card.centerx - (total_w_btns // 2)
    x_borrar = x_cancelar + w_btn + gap_btn
    y_btns = rect_card.bottom - 74

    btn_cancelar = pygame.Rect(x_cancelar, y_btns, w_btn, h_btn)
    btn_borrar = pygame.Rect(x_borrar, y_btns, w_btn, h_btn)

    def _scale_btn(nombre, w, h):
        return cargar_boton_escalado(nombre, w, h)

    spr_can_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 0)
    spr_can_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 1)
    spr_can_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_btn, h_btn, t("cancelar").upper(), (60, 45, 35), TAMANO_BOTON_MODAL, 2)
    spr_can_hover = aclarar_boton(spr_can_norm) if spr_can_norm else None

    spr_bor_norm = generar_boton_con_texto("Menu/salir.png", w_btn, h_btn, t("borrar_perfil"), (255, 255, 255), TAMANO_BOTON_MODAL, 0)
    spr_bor_semi = generar_boton_con_texto("Menu/salir-preapretado.png", w_btn, h_btn, t("borrar_perfil"), (255, 255, 255), TAMANO_BOTON_MODAL, 1)
    spr_bor_apret = generar_boton_con_texto("Menu/salir-apretado.png", w_btn, h_btn, t("borrar_perfil"), (255, 255, 255), TAMANO_BOTON_MODAL, 2)
    spr_bor_hover = aclarar_boton(spr_bor_norm) if spr_bor_norm else None
    fondo_tarjeta = (253, 246, 233)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((45, 35, 25, 140))
    captura_previa = pantalla.copy()

    nombre = obtener_nombre_partida_visible(partida)
    mundo_max = partida.get("mundo_max", 1)
    nivel_max = partida.get("nivel_max", 1)

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()
        hov_can = btn_cancelar.collidepoint(pos_mouse)
        hov_bor = btn_borrar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_can_semi and spr_can_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_can_semi, spr_can_apret, fondo_tarjeta, spr_can_norm, tipo_sonido="ventana_cancelar")
                    else:
                        reproducir_sonido_ui("ventana_cancelar")
                    if pulsado:
                        return False
                elif btn_borrar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_bor_semi and spr_bor_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_borrar, spr_bor_semi, spr_bor_apret, fondo_tarjeta, spr_bor_norm, tipo_sonido="partida_borrar")
                    else:
                        reproducir_sonido_ui("partida_borrar")
                    if pulsado:
                        return True

        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (225, 110, 80), rect_card, width=3, border_radius=18)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 24, rect_card.top + 18, rect_card.width - 48, 34)
        dibujar_texto_en_rect(pantalla, t("eliminar_perfil"), rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(205, 70, 60))

        # Nombre del perfil con ajuste automático
        rect_nom = pygame.Rect(rect_card.left + 24, rect_card.top + 60, rect_card.width - 48, 30)
        dibujar_texto_en_rect(pantalla, f"«{nombre}»  —  {t('nivel')}: {mundo_max}-{nivel_max}", rect_nom, categoria="subtitulo", tamano=TAMANO_SUBTITULO_GRANDE, color=(60, 45, 35), padding=4)

        rect_preg = pygame.Rect(rect_card.left + 24, rect_card.top + 98, rect_card.width - 48, 36)
        dibujar_texto_en_rect(pantalla, t("seguro_eliminar_perfil"), rect_preg, categoria="texto", tamano=16, color=(80, 65, 55), multiline=True, padding=2)

        rect_aviso = pygame.Rect(rect_card.left + 24, rect_card.top + 138, rect_card.width - 48, 32)
        dibujar_texto_en_rect(pantalla, t("aviso_borrado_progreso"), rect_aviso, categoria="texto", tamano=15, color=(195, 75, 65), multiline=True, padding=2)

        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=12)
            pygame.draw.rect(pantalla, (195, 168, 138), btn_cancelar, width=2, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("cancelar").upper(), btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        if spr_bor_norm:
            pantalla.blit(spr_bor_hover if (hov_bor and spr_bor_hover) else spr_bor_norm, btn_borrar)
        else:
            col_bor = (235, 95, 90) if hov_bor else (215, 80, 75)
            pygame.draw.rect(pantalla, col_bor, btn_borrar, border_radius=12)
            pygame.draw.rect(pantalla, (170, 50, 45), btn_borrar, width=2, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("borrar_perfil"), btn_borrar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=6)

        pygame.display.flip()


COLORES_RGB_MAP = {
    "Blanco": (232, 232, 232),
    "Gris": (154, 154, 154),
    "Negro": (89, 89, 89),
    "Marron": (206, 136, 111),
    "Rojo": (255, 137, 134),
    "Rosa": (255, 150, 240),
    "Naranja": (255, 160, 100),
    "Amarillo": (255, 244, 123),
    "Verde": (157, 255, 124),
    "Verde oscuro": (105, 205, 75),
    "Celeste": (124, 231, 255),
    "Azul": (36, 166, 247),
    "Violeta": (161, 123, 255),
}


def _obtener_rgb_color(nombre_color, fallback=(124, 231, 255)):
    if not nombre_color:
        return fallback
    if nombre_color in COLORES_RGB_MAP:
        return COLORES_RGB_MAP[nombre_color]
    norm = str(nombre_color).strip().capitalize()
    if norm in COLORES_RGB_MAP:
        return COLORES_RGB_MAP[norm]
    for k, v in COLORES_RGB_MAP.items():
        if k.lower() == str(nombre_color).strip().lower():
            return v
    return fallback


def _traducir_color(nombre_color):
    if not nombre_color:
        return ""
    norm = str(nombre_color).strip().lower()
    if norm == "marrón":
        norm = "marron"
    return t(norm, default=str(nombre_color))


def _traducir_accesorio(nombre_acc):
    if not nombre_acc or str(nombre_acc).strip().lower() in ("ninguno", "none", "无", ""):
        return t("sin_accesorio")
    norm = str(nombre_acc).strip().lower()
    if norm in ("mono", "moño"):
        norm = "moño"
    return t(norm, default=str(nombre_acc))


def mostrar_dialogo_confirmar_atuendos(
    pantalla,
    reloj,
    partida,
    color_p1_nuevo,
    color_p2_nuevo,
    acc_p1_nuevo,
    acc_p2_nuevo,
):
    """
    Diálogo modal de confirmación cuando se modificaron colores o accesorios en el menú
    antes de continuar una partida guardada con atuendos diferentes.
    Opciones:
    - «Mantener atuendos guardados»: carga la partida con los colores y accesorios que tenía
      guardados cada personaje. Descarta para esa partida los cambios realizados antes de entrar. (Retorna "mantener")
    - «Cambiar atuendos»: carga la partida con su progreso guardado, pero aplica y guarda los
      colores y accesorios seleccionados para ambos personajes en esa partida. (Retorna "cambiar")
    - Cancelar (ESC o botón X): cancela la carga de la partida y regresa al selector de partidas. (Retorna "cancelar")
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_box_tit = obtener_fuente_boton(18, tamano_fallback=18)
    fuente_item = obtener_fuente_texto(TAMANO_TEXTO)
    fuente_item_acc = obtener_fuente_pequena(TAMANO_PEQUENA)
    fuente_btn_main = obtener_fuente_boton(18, tamano_fallback=18)
    fuente_btn_sub = obtener_fuente_pequena(13)

    w_card, h_card = 720, 480
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    btn_cerrar = pygame.Rect(rect_card.right - 44, rect_card.top + 14, 30, 30)
    spr_x_norm = _cargar_sprite_boton("HUD/boton-x.png", 30, 30) or _cargar_sprite_boton("boton-x.png", 30, 30)
    spr_x_hover = aclarar_boton(spr_x_norm) if spr_x_norm else None

    w_box = 315
    h_box = 205
    y_box = rect_card.top + 120
    rect_box_izq = pygame.Rect(rect_card.centerx - w_box - 14, y_box, w_box, h_box)
    rect_box_der = pygame.Rect(rect_card.centerx + 14, y_box, w_box, h_box)

    w_btn = 315
    h_btn = 64
    y_btns = rect_card.bottom - 86
    btn_mantener = pygame.Rect(rect_card.centerx - w_btn - 14, y_btns, w_btn, h_btn)
    btn_cambiar = pygame.Rect(rect_card.centerx + 14, y_btns, w_btn, h_btn)

    c_p1_g = partida.get("color_p1", "Celeste")
    c_p2_g = partida.get("color_p2", "Violeta")
    a_p1_g = partida.get("accesorio_p1", "Ninguno")
    a_p2_g = partida.get("accesorio_p2", "Ninguno")

    nombre_partida = obtener_nombre_partida_visible(partida)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 185))
    captura_previa = pantalla.copy()

    pygame.event.clear()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        hov_cerrar = btn_cerrar.collidepoint(pos_mouse)
        hov_mantener = btn_mantener.collidepoint(pos_mouse)
        hov_cambiar = btn_cambiar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                pygame.event.clear()
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cerrar.collidepoint(evento.pos):
                    reproducir_sonido_ui("ventana_cancelar")
                    pygame.event.clear()
                    return "cancelar"

                elif btn_mantener.collidepoint(evento.pos):
                    reproducir_sonido_ui("ventana_aceptar")
                    pygame.draw.rect(pantalla, (230, 220, 205), btn_mantener, border_radius=12)
                    pygame.draw.rect(pantalla, (160, 130, 100), btn_mantener, width=2, border_radius=12)
                    dibujar_texto_en_rect(pantalla, t("mantener_guardados"), btn_mantener, categoria="boton", tamano=16, color=(60, 45, 35))
                    pygame.display.flip()
                    pygame.time.delay(60)
                    pygame.event.clear()
                    return "mantener"

                elif btn_cambiar.collidepoint(evento.pos):
                    reproducir_sonido_ui("ventana_aceptar")
                    pygame.draw.rect(pantalla, (45, 130, 70), btn_cambiar, border_radius=12)
                    pygame.draw.rect(pantalla, (30, 95, 50), btn_cambiar, width=2, border_radius=12)
                    dibujar_texto_en_rect(pantalla, t("cambiar_atuendos"), btn_cambiar, categoria="boton", tamano=16, color=(255, 255, 255))
                    pygame.display.flip()
                    pygame.time.delay(60)
                    pygame.event.clear()
                    return "cambiar"

        # Fondo capturado + oscurecimiento
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        # Tarjeta modal pastel crema
        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=18)

        # Botón de cerrar (X)
        spr_x_dib = spr_x_hover if (hov_cerrar and spr_x_hover) else spr_x_norm
        if spr_x_dib:
            pantalla.blit(spr_x_dib, btn_cerrar)
        else:
            col_x = (220, 60, 50) if hov_cerrar else (145, 125, 110)
            t_x = fuente_sub.render("X", True, col_x)
            pantalla.blit(t_x, t_x.get_rect(center=btn_cerrar.center))

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 50, rect_card.top + 16, rect_card.width - 100, 34)
        dibujar_texto_en_rect(pantalla, t("cambiar_atuendos"), rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(60, 45, 35))

        # Subtítulo descriptivo con autoajuste para nombres extensos de partida
        plantilla_sub = t("sub_modificaste_personajes")
        if "{0}" in plantilla_sub:
            sub_txt = plantilla_sub.format(nombre_partida)
        else:
            sub_txt = f"{plantilla_sub} «{nombre_partida}»."
        rect_sub1 = pygame.Rect(rect_card.left + 30, rect_card.top + 54, rect_card.width - 60, 26)
        dibujar_texto_en_rect(pantalla, sub_txt, rect_sub1, categoria="subtitulo", tamano=16, color=(115, 95, 80), padding=2)

        rect_sub2 = pygame.Rect(rect_card.left + 30, rect_card.top + 82, rect_card.width - 60, 24)
        dibujar_texto_en_rect(pantalla, t("pregunta_mantener_o_cambiar"), rect_sub2, categoria="subtitulo", tamano=15, color=(135, 110, 90), padding=2)

        # ----------------- CAJA IZQUIERDA: ATUENDOS GUARDADOS -----------------
        pygame.draw.rect(pantalla, (246, 238, 224), rect_box_izq, border_radius=12)
        pygame.draw.rect(pantalla, (215, 195, 175), rect_box_izq, width=2, border_radius=12)

        r_cab_izq = pygame.Rect(rect_box_izq.left + 10, rect_box_izq.top + 10, rect_box_izq.width - 20, 32)
        pygame.draw.rect(pantalla, (235, 223, 206), r_cab_izq, border_radius=8)
        dibujar_texto_en_rect(pantalla, t("atuendos_guardados"), r_cab_izq, categoria="boton", tamano=18, color=(90, 70, 55), padding=4)

        # P1 Guardado
        rgb_p1_g = _obtener_rgb_color(c_p1_g, (124, 231, 255))
        y_p1_g = rect_box_izq.top + 58
        pygame.draw.circle(pantalla, rgb_p1_g, (rect_box_izq.left + 38, y_p1_g + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_izq.left + 38, y_p1_g + 20), 17, 2)
        txt_p1_nom_g = f"{t('jugador_1')}: {_traducir_color(c_p1_g)}"
        rect_p1_nom_g = pygame.Rect(rect_box_izq.left + 66, y_p1_g + 4, rect_box_izq.width - 76, 22)
        dibujar_texto_en_rect(pantalla, txt_p1_nom_g, rect_p1_nom_g, categoria="texto", tamano=16, color=(55, 45, 35), alineacion="izquierda", padding=0)

        acc_txt_p1_g = f"{t('accesorio_label')}: {_traducir_accesorio(a_p1_g)}" if a_p1_g not in ("Ninguno", "None", "无", "") else t("sin_accesorio")
        rect_p1_acc_g = pygame.Rect(rect_box_izq.left + 66, y_p1_g + 26, rect_box_izq.width - 76, 20)
        dibujar_texto_en_rect(pantalla, acc_txt_p1_g, rect_p1_acc_g, categoria="pequena", tamano=14, color=(120, 100, 85), alineacion="izquierda", padding=0)

        # P2 Guardado
        rgb_p2_g = _obtener_rgb_color(c_p2_g, (161, 123, 255))
        y_p2_g = rect_box_izq.top + 126
        pygame.draw.circle(pantalla, rgb_p2_g, (rect_box_izq.left + 38, y_p2_g + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_izq.left + 38, y_p2_g + 20), 17, 2)
        txt_p2_nom_g = f"{t('jugador_2')}: {_traducir_color(c_p2_g)}"
        rect_p2_nom_g = pygame.Rect(rect_box_izq.left + 66, y_p2_g + 4, rect_box_izq.width - 76, 22)
        dibujar_texto_en_rect(pantalla, txt_p2_nom_g, rect_p2_nom_g, categoria="texto", tamano=16, color=(55, 45, 35), alineacion="izquierda", padding=0)

        acc_txt_p2_g = f"{t('accesorio_label')}: {_traducir_accesorio(a_p2_g)}" if a_p2_g not in ("Ninguno", "None", "无", "") else t("sin_accesorio")
        rect_p2_acc_g = pygame.Rect(rect_box_izq.left + 66, y_p2_g + 26, rect_box_izq.width - 76, 20)
        dibujar_texto_en_rect(pantalla, acc_txt_p2_g, rect_p2_acc_g, categoria="pequena", tamano=14, color=(120, 100, 85), alineacion="izquierda", padding=0)

        # ----------------- CAJA DERECHA: NUEVOS ATUENDOS -----------------
        pygame.draw.rect(pantalla, (255, 250, 242), rect_box_der, border_radius=12)
        pygame.draw.rect(pantalla, (230, 155, 85), rect_box_der, width=2, border_radius=12)

        r_cab_der = pygame.Rect(rect_box_der.left + 10, rect_box_der.top + 10, rect_box_der.width - 20, 32)
        pygame.draw.rect(pantalla, (255, 235, 215), r_cab_der, border_radius=8)
        dibujar_texto_en_rect(pantalla, t("nuevos_atuendos"), r_cab_der, categoria="boton", tamano=18, color=(205, 80, 35), padding=4)

        # P1 Nuevo
        rgb_p1_n = _obtener_rgb_color(color_p1_nuevo, (124, 231, 255))
        y_p1_n = rect_box_der.top + 58
        pygame.draw.circle(pantalla, rgb_p1_n, (rect_box_der.left + 38, y_p1_n + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_der.left + 38, y_p1_n + 20), 17, 2)
        txt_p1_nom_n = f"{t('jugador_1')}: {_traducir_color(color_p1_nuevo)}"
        rect_p1_nom_n = pygame.Rect(rect_box_der.left + 66, y_p1_n + 4, rect_box_der.width - 76, 22)
        dibujar_texto_en_rect(pantalla, txt_p1_nom_n, rect_p1_nom_n, categoria="texto", tamano=16, color=(55, 45, 35), alineacion="izquierda", padding=0)

        acc_txt_p1_n = f"{t('accesorio_label')}: {_traducir_accesorio(acc_p1_nuevo)}" if acc_p1_nuevo not in ("Ninguno", "None", "无", "") else t("sin_accesorio")
        rect_p1_acc_n = pygame.Rect(rect_box_der.left + 66, y_p1_n + 26, rect_box_der.width - 76, 20)
        dibujar_texto_en_rect(pantalla, acc_txt_p1_n, rect_p1_acc_n, categoria="pequena", tamano=14, color=(120, 100, 85), alineacion="izquierda", padding=0)

        # P2 Nuevo
        rgb_p2_n = _obtener_rgb_color(color_p2_nuevo, (161, 123, 255))
        y_p2_n = rect_box_der.top + 126
        pygame.draw.circle(pantalla, rgb_p2_n, (rect_box_der.left + 38, y_p2_n + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_der.left + 38, y_p2_n + 20), 17, 2)
        txt_p2_nom_n = f"{t('jugador_2')}: {_traducir_color(color_p2_nuevo)}"
        rect_p2_nom_n = pygame.Rect(rect_box_der.left + 66, y_p2_n + 4, rect_box_der.width - 76, 22)
        dibujar_texto_en_rect(pantalla, txt_p2_nom_n, rect_p2_nom_n, categoria="texto", tamano=16, color=(55, 45, 35), alineacion="izquierda", padding=0)

        acc_txt_p2_n = f"{t('accesorio_label')}: {_traducir_accesorio(acc_p2_nuevo)}" if acc_p2_nuevo not in ("Ninguno", "None", "无", "") else t("sin_accesorio")
        rect_p2_acc_n = pygame.Rect(rect_box_der.left + 66, y_p2_n + 26, rect_box_der.width - 76, 20)
        dibujar_texto_en_rect(pantalla, acc_txt_p2_n, rect_p2_acc_n, categoria="pequena", tamano=14, color=(120, 100, 85), alineacion="izquierda", padding=0)

        idm_g = obtener_idioma()
        # ----------------- BOTÓN 1: MANTENER ATUENDOS GUARDADOS -----------------
        spr_m_norm = generar_boton_con_texto("mundos/boton-volver.png", btn_mantener.w, btn_mantener.h, t("mantener_guardados"), (60, 45, 30), 16, 0, idm_g)
        if hov_mantener and spr_m_norm: spr_m_norm = aclarar_boton(spr_m_norm)
        if spr_m_norm:
            pantalla.blit(spr_m_norm, btn_mantener)
        else:
            col_m = (255, 255, 255) if hov_mantener else (242, 234, 222)
            pygame.draw.rect(pantalla, col_m, btn_mantener, border_radius=12)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_mantener, width=2, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("mantener_guardados"), btn_mantener, categoria="boton", tamano=16, color=(60, 45, 35))

        # ----------------- BOTÓN 2: CAMBIAR ATUENDOS -----------------
        spr_c_norm = generar_boton_con_texto("mundos/boton-cargar.png", btn_cambiar.w, btn_cambiar.h, t("cambiar_atuendos"), (26, 83, 29), 16, 0, idm_g)
        if hov_cambiar and spr_c_norm: spr_c_norm = aclarar_boton(spr_c_norm)
        if spr_c_norm:
            pantalla.blit(spr_c_norm, btn_cambiar)
        else:
            col_c = (82, 194, 114) if hov_cambiar else (68, 172, 98)
            pygame.draw.rect(pantalla, col_c, btn_cambiar, border_radius=12)
            pygame.draw.rect(pantalla, (45, 130, 70), btn_cambiar, width=2, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("cambiar_atuendos"), btn_cambiar, categoria="boton", tamano=16, color=(255, 255, 255))

        pygame.display.flip()
