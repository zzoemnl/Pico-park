"""
Módulo de Configuración, Audio e Internacionalización (i18n) - Pico Park.

Gestiona:
1. Control de volumen del juego (0% a 100%) con retroalimentación sonora y control de canales de Pygame.
2. Selector de idioma global (Español, English, 简体中文) sin reiniciar la partida.
3. Pestaña modal superpuesta de Configuración que conserva el estado y progreso del juego.
"""

import os
import math
import struct
import pygame

from sprites import cargar_boton, animar_pulsacion_boton, aclarar_boton
from fuentes import (
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_pequena,
    limpiar_cache_fuentes,
)

# ==============================================================================
# ESTADO GLOBAL DE CONFIGURACIÓN
# ==============================================================================
_volumen = 70          # Porcentaje de volumen (0 a 100)
_idioma = "es"          # Idioma actual: "es" | "en" | "zh"

# ==============================================================================
# DICCIONARIO DE TRADUCCIONES
# ==============================================================================
DICCIONARIO = {
    # Pestaña de configuración
    "configuracion": {
        "es": "CONFIGURACIÓN",
        "en": "SETTINGS",
        "zh": "设置",
    },
    "volumen": {
        "es": "VOLUMEN",
        "en": "VOLUME",
        "zh": "音量",
    },
    "idioma": {
        "es": "IDIOMA",
        "en": "LANGUAGE",
        "zh": "语言",
    },
    "cerrar": {
        "es": "CERRAR",
        "en": "CLOSE",
        "zh": "关闭",
    },
    "volver_juego": {
        "es": "VOLVER AL JUEGO",
        "en": "BACK TO GAME",
        "zh": "返回游戏",
    },

    # Idiomas
    "idioma_es": {
        "es": "Español",
        "en": "Spanish",
        "zh": "西班牙语",
    },
    "idioma_en": {
        "es": "English",
        "en": "English",
        "zh": "英语",
    },
    "idioma_zh": {
        "es": "简体中文",
        "en": "Chinese",
        "zh": "简体中文",
    },

    # Pantallas de Juego y Muerte
    "te_moriste": {
        "es": "¡Te moriste!",
        "en": "You died!",
        "zh": "你失败了！",
    },
    "reiniciar_o_salir": {
        "es": "¿Querés reiniciar o salir?",
        "en": "Do you want to restart or quit?",
        "zh": "你想重新开始还是退出？",
    },
    "nivel_completado": {
        "es": "¡NIVEL COMPLETADO!",
        "en": "LEVEL COMPLETED!",
        "zh": "关卡完成！",
    },
    "buen_trabajo": {
        "es": "¡Buen trabajo!",
        "en": "Good job!",
        "zh": "干得漂亮！",
    },
    "siguiente": {
        "es": "SIGUIENTE",
        "en": "NEXT",
        "zh": "下一关",
    },
    "finalizar": {
        "es": "FINALIZAR",
        "en": "FINISH",
        "zh": "完成",
    },
    "reiniciar": {
        "es": "REINICIAR",
        "en": "RESTART",
        "zh": "重新开始",
    },
    "menu": {
        "es": "MENÚ",
        "en": "MENU",
        "zh": "主菜单",
    },

    # Diálogos de guardado y confirmación
    "deseas_guardar": {
        "es": "¿Deseas guardar antes de salir?",
        "en": "Save before quitting?",
        "zh": "退出前是否保存进度？",
    },
    "guardar_salir": {
        "es": "Guardar y salir",
        "en": "Save and quit",
        "zh": "保存并退出",
    },
    "salir_sin_guardar": {
        "es": "Salir sin guardar",
        "en": "Quit without saving",
        "zh": "不保存退出",
    },
    "cancelar": {
        "es": "Cancelar",
        "en": "Cancel",
        "zh": "取消",
    },

    # Menú y niveles
    "mundo": {
        "es": "MUNDO",
        "en": "WORLD",
        "zh": "世界",
    },
    "nivel": {
        "es": "NIVEL",
        "en": "LEVEL",
        "zh": "关卡",
    },
    "jugar": {
        "es": "JUGAR",
        "en": "PLAY",
        "zh": "开始游戏",
    },
    "personajes": {
        "es": "PERSONAJES",
        "en": "CHARACTERS",
        "zh": "角色设置",
    },
    "salir": {
        "es": "SALIR",
        "en": "QUIT",
        "zh": "退出游戏",
    },
    "volver": {
        "es": "VOLVER",
        "en": "BACK",
        "zh": "返回",
    },
    "seleccion_nivel": {
        "es": "SELECCIÓN DE NIVEL",
        "en": "LEVEL SELECTION",
        "zh": "选择关卡",
    },
    "bloqueado": {
        "es": "BLOQUEADO",
        "en": "LOCKED",
        "zh": "未解锁",
    },
    "deseas_guardar_sub": {
        "es": "Puedes guardar tu partida en un perfil antes de salir.",
        "en": "You can save your game before exiting.",
        "zh": "退出前您可以将游戏进度保存到档案中。",
    },
}


def t(clave, default=None):
    """
    Retorna la traducción de una clave en el idioma actual.
    Si no existe la traducción, retorna el valor predeterminado o la clave misma.
    """
    info = DICCIONARIO.get(clave)
    if isinstance(info, dict):
        return info.get(_idioma, info.get("es", default or clave))
    return default if default is not None else clave


def obtener_idioma():
    """Retorna el código del idioma activo ('es', 'en', 'zh')."""
    return _idioma


def cambiar_idioma(nuevo_idioma):
    """Cambia el idioma activo y purga el caché de fuentes para soporte CJK instantáneo."""
    global _idioma
    if nuevo_idioma in ("es", "en", "zh"):
        _idioma = nuevo_idioma
        try:
            limpiar_cache_fuentes()
        except Exception:
            pass


# ==============================================================================
# GESTIÓN DE AUDIO Y VOLUMEN
# ==============================================================================
def obtener_volumen():
    """Retorna el volumen actual como entero entre 0 y 100."""
    return _volumen


def _aplicar_volumen_audio():
    """Aplica el nivel de volumen al subsistema de audio y música de Pygame."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        vol_float = max(0.0, min(1.0, _volumen / 100.0))
        pygame.mixer.music.set_volume(vol_float)
        num_canales = pygame.mixer.get_num_channels()
        for i in range(num_canales):
            pygame.mixer.Channel(i).set_volume(vol_float)
    except Exception:
        pass


def reproducir_beep_volumen():
    """Genera y reproduce un tono suave de retroalimentación para escuchar el cambio de volumen."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        vol_float = max(0.0, min(1.0, _volumen / 100.0))
        if vol_float <= 0.001:
            return

        sample_rate = 22050
        duration = 0.05
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            val = int(32767 * 0.28 * math.sin(2 * math.pi * 520 * i / sample_rate))
            buf += struct.pack('<h', val)

        snd = pygame.mixer.Sound(buffer=bytes(buf))
        snd.set_volume(vol_float)
        snd.play()
    except Exception:
        pass


def fijar_volumen(nuevo_volumen):
    """Establece el volumen a un porcentaje exacto (0 a 100)."""
    global _volumen
    _volumen = max(0, min(100, int(nuevo_volumen)))
    _aplicar_volumen_audio()


def cambiar_volumen(delta):
    """Incrementa o decrementa el volumen por un valor delta y emite retroalimentación sonora."""
    fijar_volumen(_volumen + delta)
    reproducir_beep_volumen()


# ==============================================================================
# PESTAÑA MODAL SUPERPUESTA DE CONFIGURACIÓN
# ==============================================================================
def mostrar_pestana_configuracion(pantalla, reloj):
    """
    Despliega la pestaña modal de configuración superpuesta al juego actual.
    - No reinicia la partida ni cambia de pantalla.
    - Permite subir/bajar volumen con sus tres estados visuales (0 % a 100 %).
    - Permite alternar entre Español, English y 简体中文 sin perder progreso.
    - Bloquea los clics a elementos de fondo.
    """
    ancho_p, alto_p = pantalla.get_size()

    # Captura de pantalla congelada del juego para restaurar al cerrar
    fondo_juego = pantalla.copy()

    # Capa de oscurecimiento semitransparente sobre el juego
    capa_oscura = pygame.Surface((ancho_p, alto_p), pygame.SRCALPHA)
    capa_oscura.fill((0, 0, 0, 150))

    # Dimensiones y posición del panel central
    W_MODAL = 520
    H_MODAL = 400
    rect_modal = pygame.Rect((ancho_p - W_MODAL) // 2, (alto_p - H_MODAL) // 2, W_MODAL, H_MODAL)

    # Botón de cerrar (X) en la esquina superior derecha del panel
    TAM_X_CFG = 34
    rect_x_header = pygame.Rect(rect_modal.right - TAM_X_CFG - 12, rect_modal.top + 12, TAM_X_CFG, TAM_X_CFG)

    # Cargar sprites para los botones de volumen (con tamaño HUD moderado)
    TAM_BTN_VOL = 52
    def _cargar_scaled(nombre, w, h):
        img = cargar_boton(nombre)
        return pygame.transform.smoothscale(img, (w, h)) if img else None

    # Botón Bajar Volumen (Parlante con X / Silencio)
    spr_menos_norm = _cargar_scaled("HUD/boton-bajar-volumen.png", TAM_BTN_VOL, TAM_BTN_VOL) or _cargar_scaled("boton-bajar-volumen.png", TAM_BTN_VOL, TAM_BTN_VOL)
    spr_menos_semi = _cargar_scaled("HUD/boton-bajar-volumen-semiapretado.png", TAM_BTN_VOL, TAM_BTN_VOL) or _cargar_scaled("boton-bajar-volumen-semiapretado.png", TAM_BTN_VOL, TAM_BTN_VOL)
    spr_menos_apr = _cargar_scaled("HUD/boton-bajar-volumen-apretado.png", TAM_BTN_VOL, TAM_BTN_VOL) or _cargar_scaled("boton-bajar-volumen-apretado.png", TAM_BTN_VOL, TAM_BTN_VOL)
    spr_menos_hov = aclarar_boton(spr_menos_norm)

    # Botón Subir Volumen (Parlante con ondas sonoras)
    spr_mas_norm = _cargar_scaled("HUD/boton-subir-volumen.png", TAM_BTN_VOL, TAM_BTN_VOL) or _cargar_scaled("boton-subir-volumen.png", TAM_BTN_VOL, TAM_BTN_VOL)
    spr_mas_semi = _cargar_scaled("HUD/boton-subir-volumen-semiapretado.png", TAM_BTN_VOL, TAM_BTN_VOL) or _cargar_scaled("boton-subir-volumen-semiapretado.png", TAM_BTN_VOL, TAM_BTN_VOL)
    spr_mas_apr = _cargar_scaled("HUD/boton-subir-volumen-apretado.png", TAM_BTN_VOL, TAM_BTN_VOL) or _cargar_scaled("boton-subir-volumen-apretado.png", TAM_BTN_VOL, TAM_BTN_VOL)
    spr_mas_hov = aclarar_boton(spr_mas_norm)

    # Botón X de cabecera
    spr_x_norm = _cargar_scaled("HUD/boton-x.png", TAM_X_CFG, TAM_X_CFG) or _cargar_scaled("boton-x.png", TAM_X_CFG, TAM_X_CFG)
    spr_x_semi = _cargar_scaled("HUD/boton-x-semiapretado.png", TAM_X_CFG, TAM_X_CFG) or _cargar_scaled("boton-x-semiapretado.png", TAM_X_CFG, TAM_X_CFG)
    spr_x_apr = _cargar_scaled("HUD/boton-x-apretado.png", TAM_X_CFG, TAM_X_CFG) or _cargar_scaled("boton-x-apretado.png", TAM_X_CFG, TAM_X_CFG)
    spr_x_hov = aclarar_boton(spr_x_norm)

    # Layout interno del panel
    y_seccion_vol = rect_modal.top + 80
    rect_btn_menos = pygame.Rect(rect_modal.left + 46, y_seccion_vol + 26, TAM_BTN_VOL, TAM_BTN_VOL)
    rect_barra_bg = pygame.Rect(rect_btn_menos.right + 16, y_seccion_vol + 38, 230, 26)
    rect_btn_mas = pygame.Rect(rect_barra_bg.right + 16, y_seccion_vol + 26, TAM_BTN_VOL, TAM_BTN_VOL)

    y_seccion_idioma = rect_modal.top + 195
    w_btn_lang, h_btn_lang, gap_lang = 136, 42, 14
    x_inicio_lang = rect_modal.left + (W_MODAL - (3 * w_btn_lang + 2 * gap_lang)) // 2
    rect_lang_es = pygame.Rect(x_inicio_lang, y_seccion_idioma + 32, w_btn_lang, h_btn_lang)
    rect_lang_en = pygame.Rect(rect_lang_es.right + gap_lang, y_seccion_idioma + 32, w_btn_lang, h_btn_lang)
    rect_lang_zh = pygame.Rect(rect_lang_en.right + gap_lang, y_seccion_idioma + 32, w_btn_lang, h_btn_lang)

    rect_btn_cerrar = pygame.Rect(rect_modal.centerx - 100, rect_modal.bottom - 60, 200, 44)

    modal_activo = True
    while modal_activo:
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                modal_activo = False
                break

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    modal_activo = False
                    break

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # 1. Clic en botón X de cabecera
                if rect_x_header.collidepoint(evento.pos):
                    pulsado = True
                    if spr_x_semi and spr_x_apr:
                        pulsado = animar_pulsacion_boton(pantalla, rect_x_header, spr_x_semi, spr_x_apr, (46, 52, 68), spr_x_norm)
                    if pulsado:
                        modal_activo = False
                        break

                # 2. Clic en botón Bajar Volumen
                elif rect_btn_menos.collidepoint(evento.pos):
                    if spr_menos_semi and spr_menos_apr:
                        if animar_pulsacion_boton(pantalla, rect_btn_menos, spr_menos_semi, spr_menos_apr, (36, 40, 52), spr_menos_norm):
                            cambiar_volumen(-10)
                    else:
                        cambiar_volumen(-10)

                # 3. Clic en botón Subir Volumen
                elif rect_btn_mas.collidepoint(evento.pos):
                    if spr_mas_semi and spr_mas_apr:
                        if animar_pulsacion_boton(pantalla, rect_btn_mas, spr_mas_semi, spr_mas_apr, (36, 40, 52), spr_mas_norm):
                            cambiar_volumen(+10)
                    else:
                        cambiar_volumen(+10)

                # 4. Clic en la barra de volumen (ajuste directo)
                elif rect_barra_bg.collidepoint(evento.pos):
                    ratio = (evento.pos[0] - rect_barra_bg.left) / float(rect_barra_bg.width)
                    nuevo_v = int(round(ratio * 10) * 10)
                    fijar_volumen(nuevo_v)
                    reproducir_beep_volumen()

                # 5. Clic en botones de idioma
                elif rect_lang_es.collidepoint(evento.pos):
                    cambiar_idioma("es")
                elif rect_lang_en.collidepoint(evento.pos):
                    cambiar_idioma("en")
                elif rect_lang_zh.collidepoint(evento.pos):
                    cambiar_idioma("zh")

                # 6. Clic en botón inferior CERRAR
                elif rect_btn_cerrar.collidepoint(evento.pos):
                    modal_activo = False
                    break

                # 7. Si hace clic fuera del modal, también cerramos elegantemente
                elif not rect_modal.collidepoint(evento.pos):
                    modal_activo = False
                    break

        if not modal_activo:
            break

        # Redibujar la escena congelada + capa oscura
        pantalla.blit(fondo_juego, (0, 0))
        pantalla.blit(capa_oscura, (0, 0))

        # --- DIBUJO DEL PANEL MODAL ---
        # Sombra del modal
        rect_sombra = rect_modal.move(6, 8)
        pygame.draw.rect(pantalla, (15, 18, 25), rect_sombra, border_radius=18)

        # Fondo del modal (Dark Slate / Charcoal)
        pygame.draw.rect(pantalla, (36, 40, 52), rect_modal, border_radius=18)
        # Borde exterior cálido con el color del HUD
        pygame.draw.rect(pantalla, (255, 160, 100), rect_modal, width=3, border_radius=18)

        # Cabecera
        rect_header = pygame.Rect(rect_modal.left, rect_modal.top, W_MODAL, 54)
        pygame.draw.rect(pantalla, (46, 52, 68), rect_header, border_top_left_radius=18, border_top_right_radius=18)
        pygame.draw.line(pantalla, (70, 78, 100), (rect_modal.left, rect_header.bottom), (rect_modal.right, rect_header.bottom), 2)

        # Título de Cabecera
        fuente_titulo = obtener_fuente_titulo(22, tamano_fallback=20)
        t_tit = fuente_titulo.render(t("configuracion"), True, (255, 235, 195))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_modal.centerx, rect_header.centery)))

        mouse_down = pygame.mouse.get_pressed()[0]

        # Dibujar botón X de cabecera
        hov_x = rect_x_header.collidepoint(pos_mouse)
        spr_x_dib = spr_x_hov if (hov_x and spr_x_hov) else spr_x_norm
        if spr_x_dib:
            pantalla.blit(spr_x_dib, rect_x_header)

        # --- SECCIÓN 1: VOLUMEN ---
        fuente_seccion = obtener_fuente_subtitulo(18, negrita=True, tamano_fallback=18)
        t_vol_lbl = fuente_seccion.render(t("volumen"), True, (255, 195, 140))
        pantalla.blit(t_vol_lbl, (rect_modal.left + 46, y_seccion_vol))

        # Botón Bajar Volumen
        hov_menos = rect_btn_menos.collidepoint(pos_mouse)
        spr_m_dib = spr_menos_hov if (hov_menos and spr_menos_hov) else spr_menos_norm
        if spr_m_dib:
            pantalla.blit(spr_m_dib, rect_btn_menos)

        # Barra de progreso de volumen
        pygame.draw.rect(pantalla, (22, 24, 32), rect_barra_bg, border_radius=8)
        ancho_relleno = int((rect_barra_bg.width - 4) * (_volumen / 100.0))
        if ancho_relleno > 0:
            rect_relleno = pygame.Rect(rect_barra_bg.left + 2, rect_barra_bg.top + 2, ancho_relleno, rect_barra_bg.height - 4)
            pygame.draw.rect(pantalla, (255, 160, 100), rect_relleno, border_radius=6)
        pygame.draw.rect(pantalla, (80, 88, 110), rect_barra_bg, width=2, border_radius=8)

        # Texto de porcentaje centrado sobre la barra
        fuente_pct = obtener_fuente_boton(16, negrita=True, tamano_fallback=16)
        t_pct = fuente_pct.render(f"{_volumen} %", True, (255, 255, 255))
        rect_pct = t_pct.get_rect(center=rect_barra_bg.center)
        # Sombra de texto para alta legibilidad sobre la barra
        t_pct_sombra = fuente_pct.render(f"{_volumen} %", True, (20, 20, 20))
        pantalla.blit(t_pct_sombra, rect_pct.move(1, 1))
        pantalla.blit(t_pct, rect_pct)

        # Botón Subir Volumen
        hov_mas = rect_btn_mas.collidepoint(pos_mouse)
        spr_p_dib = spr_mas_hov if (hov_mas and spr_mas_hov) else spr_mas_norm
        if spr_p_dib:
            pantalla.blit(spr_p_dib, rect_btn_mas)

        # --- SECCIÓN 2: SELECTOR DE IDIOMA ---
        t_lang_lbl = fuente_seccion.render(t("idioma"), True, (255, 195, 140))
        pantalla.blit(t_lang_lbl, (rect_modal.left + 46, y_seccion_idioma))

        opciones_idioma = [
            ("es", "Español", rect_lang_es),
            ("en", "English", rect_lang_en),
            ("zh", "简体中文", rect_lang_zh),
        ]

        fuente_btn_lang = obtener_fuente_boton(16, negrita=True, tamano_fallback=16)
        for cod, etiqueta, rect_btn in opciones_idioma:
            es_activo = (_idioma == cod)
            hov_btn = rect_btn.collidepoint(pos_mouse)

            if es_activo:
                col_bg = (210, 115, 60)
                col_borde = (255, 220, 150)
                col_txt = (255, 255, 255)
                grosor_borde = 3
            elif hov_btn:
                col_bg = (64, 70, 90)
                col_borde = (120, 130, 160)
                col_txt = (240, 240, 240)
                grosor_borde = 2
            else:
                col_bg = (46, 52, 68)
                col_borde = (75, 82, 104)
                col_txt = (195, 200, 215)
                grosor_borde = 2

            pygame.draw.rect(pantalla, col_bg, rect_btn, border_radius=10)
            pygame.draw.rect(pantalla, col_borde, rect_btn, width=grosor_borde, border_radius=10)

            texto_render = f"✓ {etiqueta}" if es_activo else etiqueta
            t_lbl = fuente_btn_lang.render(texto_render, True, col_txt)
            pantalla.blit(t_lbl, t_lbl.get_rect(center=rect_btn.center))

        # --- BOTÓN INFERIOR: CERRAR / VOLVER AL JUEGO ---
        hov_cerrar = rect_btn_cerrar.collidepoint(pos_mouse)
        col_c_bg = (182, 88, 43) if hov_cerrar else (150, 70, 32)
        col_c_bd = (255, 195, 140) if hov_cerrar else (210, 140, 95)
        pygame.draw.rect(pantalla, col_c_bg, rect_btn_cerrar, border_radius=12)
        pygame.draw.rect(pantalla, col_c_bd, rect_btn_cerrar, width=2, border_radius=12)

        fuente_btn_cerrar = obtener_fuente_boton(18, negrita=True, tamano_fallback=18)
        t_btn_c = fuente_btn_cerrar.render(t("cerrar"), True, (255, 255, 255))
        pantalla.blit(t_btn_c, t_btn_c.get_rect(center=rect_btn_cerrar.center))

        pygame.display.flip()
        reloj.tick(60)

    # Al salir del modal, restauramos el frame original del juego inmediatamente
    pantalla.blit(fondo_juego, (0, 0))
    pygame.display.flip()
