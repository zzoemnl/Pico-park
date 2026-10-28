"""
Módulo de Configuración Centralizada de Fuentes y Tipografías - Pico Park.

Este archivo centraliza la definición y tamaños de todas las fuentes del juego,
permitiendo cambiarlas de manera global desde un único lugar sin modificar cada pantalla.
"""

import os
import pygame

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_FUENTE_PIXEL = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes", "04B_30__.TTF")
RUTA_FUENTE_ZIP = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes", "04b_30.zip")
CARPETAS_FUENTES = [
    os.path.join(DIRECTORIO_ACTUAL, "..", "assets", "fuentes"),
    os.path.join(DIRECTORIO_ACTUAL, "assets", "fuentes"),
    os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes"),
    os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Fuentes"),
]

# ==============================================================================
# 1. VARIABLES CENTRALIZADAS PARA LAS TIPOGRAFÍAS
# ==============================================================================
# Para cambiar la tipografía de una categoría en todo el juego, modifica estas variables:
# - Puedes asignar el nombre de archivo en Sprites/Fuentes o assets/fuentes: ej. "04B_30__.TTF"
# - Puedes asignar el nombre de una fuente del sistema: ej. "Arial", "Segoe UI", "Verdana"
# - Puedes asignar None para usar la tipografía predeterminada del sistema con soporte Unicode
# ==============================================================================
FUENTE_TITULO = "04B_30__.TTF"      # Títulos principales de las pantallas
FUENTE_SUBTITULO = None            # Subtítulos y encabezados de secciones
FUENTE_TEXTO = None                # Textos normales, descripciones y mensajes
FUENTE_BOTONES = "04B_30__.TTF"    # Textos de los botones y badges interactivos
FUENTE_BOTON = FUENTE_BOTONES      # Alias de compatibilidad
FUENTE_PEQUENA = None              # Indicaciones y textos secundarios
FUENTE_CONTADOR = None             # Números, porcentajes, temporizadores y contadores
FUENTE_DIALOGOS = None             # Mensajes, confirmaciones y ventanas emergentes

# ==============================================================================
# 2. VARIABLES CENTRALIZADAS PARA LOS TAMAÑOS
# ==============================================================================
# Modifica los tamaños globales desde estas variables para ajustar la escala visual:
# ==============================================================================
TAMANO_TITULO = 30                 # Títulos principales de pantallas
TAMANO_TITULO_GRANDE = 40          # Títulos destacados (victoria, muerte)
TAMANO_TITULO_MODAL = 18           # Títulos de ventanas modales y confirmaciones

TAMANO_SUBTITULO = 24              # Subtítulos y encabezados de secciones
TAMANO_SUBTITULO_GRANDE = 28       # Subtítulos destacados

TAMANO_TEXTO = 24                  # Texto estándar de lectura e instrucciones
TAMANO_TEXTO_GRANDE = 26           # Texto en cuadros de confirmación y advertencias
TAMANO_INPUT = 30                  # Campos de entrada de texto (nombre, clave)

TAMANO_BOTONES = 15                # Botones estándar del menú y tarjetas
TAMANO_BOTON = TAMANO_BOTONES      # Alias de compatibilidad
TAMANO_BOTON_GRANDE = 20           # Botones destacados y primarios
TAMANO_BOTON_MODAL = 12            # Botones de modales y acciones secundarias

TAMANO_PEQUENA = 20                # Indicaciones pequeñas y detalles de partida
TAMANO_ITEM_TITULO = 14            # Títulos de ítems en listas de partidas y cards
TAMANO_BADGE = 15                  # Badges de estado, checkmarks y etiquetas
TAMANO_CARD = 13                   # Etiquetas en cards de niveles

TAMANO_CONTADOR = 16               # Números, porcentajes, temporizadores y contadores
TAMANO_DIALOGOS = 22               # Ventanas emergentes, avisos y confirmaciones


# ==============================================================================
# 3. GESTIÓN Y CARGA OPTIMIZADA CON CACHÉ
# ==============================================================================
_CACHE_FUENTES = {}


def limpiar_cache_fuentes():
    """Limpia el caché interno para forzar la recarga si se cambian variables dinámicamente."""
    _CACHE_FUENTES.clear()


def _resolver_ruta_fuente(nombre_o_ruta):
    """Resuelve la ruta absoluta al archivo de fuente, buscando en assets y descomprimiendo zips si es necesario."""
    if not nombre_o_ruta:
        return None

    if os.path.isabs(nombre_o_ruta) and os.path.isfile(nombre_o_ruta):
        return nombre_o_ruta

    base = os.path.basename(nombre_o_ruta)

    # 1. Buscar directamente en carpetas de fuentes configuradas
    for carpeta in CARPETAS_FUENTES:
        ruta_directa = os.path.join(carpeta, base)
        if os.path.isfile(ruta_directa):
            return os.path.normpath(ruta_directa)

    # 2. Intentar buscar dentro de archivos ZIP en las carpetas de fuentes
    for carpeta in CARPETAS_FUENTES:
        if os.path.isdir(carpeta):
            for arch in os.listdir(carpeta):
                if arch.lower().endswith(".zip"):
                    zip_path = os.path.join(carpeta, arch)
                    try:
                        import zipfile
                        with zipfile.ZipFile(zip_path, "r") as z:
                            for miembro in z.namelist():
                                if os.path.basename(miembro).lower() == base.lower():
                                    z.extract(miembro, carpeta)
                                    ruta_extraida = os.path.join(carpeta, miembro)
                                    if os.path.isfile(ruta_extraida):
                                        return os.path.normpath(ruta_extraida)
                    except Exception:
                        pass

    return None


def obtener_fuente(categoria="texto", tamano=None, negrita=False, tamano_fallback=None):
    """
    Retorna una instancia reutilizable de pygame.font.Font según la categoría y tamaño.
    Reutiliza instancias cacheadas para evitar recargas en cada fotograma.
    """
    if not pygame.font.get_init():
        pygame.font.init()

    cat = str(categoria).lower().strip()
    if cat == "titulo":
        fuente_config = FUENTE_TITULO
        tamano_defecto = TAMANO_TITULO
    elif cat == "subtitulo":
        fuente_config = FUENTE_SUBTITULO
        tamano_defecto = TAMANO_SUBTITULO
    elif cat in ("boton", "botones"):
        fuente_config = FUENTE_BOTONES
        tamano_defecto = TAMANO_BOTONES
    elif cat == "pequena":
        fuente_config = FUENTE_PEQUENA
        tamano_defecto = TAMANO_PEQUENA
    elif cat == "contador":
        fuente_config = FUENTE_CONTADOR
        tamano_defecto = TAMANO_CONTADOR
    elif cat in ("dialogos", "dialogo"):
        fuente_config = FUENTE_DIALOGOS
        tamano_defecto = TAMANO_DIALOGOS
    else:  # "texto" o general
        fuente_config = FUENTE_TEXTO
        tamano_defecto = TAMANO_TEXTO

    tamano_final = tamano if tamano is not None else tamano_defecto

    # Soporte automático de glifos para Chino Simplificado
    try:
        import configuracion
        idioma_actual = configuracion.obtener_idioma()
    except Exception:
        idioma_actual = "es"

    if idioma_actual == "zh":
        cache_key_zh = ("zh", cat, tamano_final, negrita)
        if cache_key_zh in _CACHE_FUENTES:
            return _CACHE_FUENTES[cache_key_zh]
        for f_cjk in ["Microsoft YaHei", "SimHei", "SimSun", "Segoe UI", "Arial Unicode MS"]:
            try:
                font_obj = pygame.font.SysFont(f_cjk, tamano_final, bold=negrita)
                if font_obj is not None:
                    _CACHE_FUENTES[cache_key_zh] = font_obj
                    return font_obj
            except Exception:
                pass

    cache_key = (cat, fuente_config, tamano_final, negrita, tamano_fallback)
    if cache_key in _CACHE_FUENTES:
        return _CACHE_FUENTES[cache_key]

    font_obj = None

    if fuente_config:
        ruta_archivo = _resolver_ruta_fuente(fuente_config)
        if ruta_archivo and os.path.isfile(ruta_archivo):
            try:
                font_obj = pygame.font.Font(ruta_archivo, tamano_final)
            except Exception:
                font_obj = None

        if font_obj is None and isinstance(fuente_config, str) and not fuente_config.lower().endswith((".ttf", ".otf")):
            try:
                font_obj = pygame.font.SysFont(fuente_config, tamano_final, bold=negrita)
            except Exception:
                font_obj = None

    # Fallback robusto con tipografías del sistema que garantizan caracteres en español (acentos, ñ, ¿, ¡)
    if font_obj is None:
        for nombre_sys in ["Segoe UI", "Arial Rounded MT Bold", "Arial", "Trebuchet MS", "DejaVu Sans"]:
            try:
                font_obj = pygame.font.SysFont(nombre_sys, tamano_final, bold=negrita)
                if font_obj is not None:
                    break
            except Exception:
                pass

    if font_obj is None:
        try:
            tam_fb = tamano_fallback or tamano_final
            font_obj = pygame.font.Font(None, tam_fb)
            if negrita:
                font_obj.set_bold(True)
        except Exception:
            font_obj = pygame.font.Font(None, 24)

    _CACHE_FUENTES[cache_key] = font_obj
    return font_obj


def obtener_fuente_titulo(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para títulos principales."""
    return obtener_fuente("titulo", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_subtitulo(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para subtítulos y encabezados."""
    return obtener_fuente("subtitulo", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_texto(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para textos normales y descripciones."""
    return obtener_fuente("texto", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_botones(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para botones y opciones."""
    return obtener_fuente("botones", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_boton(tamano=None, negrita=False, tamano_fallback=None):
    """Alias retrocompatible de obtener_fuente_botones."""
    return obtener_fuente_botones(tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_pequena(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para textos secundarios y detalles."""
    return obtener_fuente("pequena", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_contador(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para números, porcentajes, temporizadores y contadores."""
    return obtener_fuente("contador", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_dialogos(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para mensajes, confirmaciones y ventanas emergentes."""
    return obtener_fuente("dialogos", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def cargar_fuente_pixel(tamano, fallback_tamano=None):
    """Función de compatibilidad retroactiva con código existente."""
    return obtener_fuente_titulo(tamano=tamano, tamano_fallback=fallback_tamano)


# ==============================================================================
# 4. FUNCIONES REUTILIZABLES DE MEDICIÓN, AJUSTE Y RENDERIZADO SEGURO
# ==============================================================================

def dividir_texto_en_lineas(texto, fuente, ancho_max):
    """
    Divide un texto en múltiples líneas para que ninguna supere el ancho máximo en píxeles.
    Respeta saltos de línea explícitos (\n) y distribuye palabras de forma fluida.
    Si una palabra individual supera ancho_max, la divide de forma segura para evitar desbordes.
    """
    if not texto:
        return []

    lineas_resultado = []
    parrafos = str(texto).split("\n")
    for parrafo in parrafos:
        palabras = parrafo.split(" ")
        if not palabras:
            lineas_resultado.append("")
            continue

        linea_actual = ""
        for palabra in palabras:
            if not palabra:
                continue
            candidata = f"{linea_actual} {palabra}".strip() if linea_actual else palabra
            ancho_w, _ = fuente.size(candidata)
            if ancho_w <= ancho_max:
                linea_actual = candidata
            else:
                if linea_actual:
                    lineas_resultado.append(linea_actual)
                    linea_actual = ""
                # Si una sola palabra es más ancha que ancho_max, partirla letra por letra
                ancho_p, _ = fuente.size(palabra)
                if ancho_p > ancho_max:
                    trozo = ""
                    for char in palabra:
                        if fuente.size(trozo + char)[0] <= ancho_max:
                            trozo += char
                        else:
                            if trozo:
                                lineas_resultado.append(trozo)
                            trozo = char
                    linea_actual = trozo
                else:
                    linea_actual = palabra
        if linea_actual:
            lineas_resultado.append(linea_actual)

    return lineas_resultado


def ajustar_tamano_fuente(texto, categoria="texto", tamano_inicial=None, ancho_max=None, alto_max=None, tamano_min=10, negrita=False):
    """
    Calcula y retorna la mejor fuente (pygame.font.Font) y tamaño para que el texto quepa en ancho_max y alto_max.
    Reduce el tamaño de forma gradual desde tamano_inicial hasta tamano_min respetando la jerarquía visual.
    """
    if tamano_inicial is None:
        cat = str(categoria).lower().strip()
        if cat == "titulo":
            tamano_inicial = TAMANO_TITULO
        elif cat == "subtitulo":
            tamano_inicial = TAMANO_SUBTITULO
        elif cat in ("boton", "botones"):
            tamano_inicial = TAMANO_BOTONES
        elif cat == "pequena":
            tamano_inicial = TAMANO_PEQUENA
        elif cat == "contador":
            tamano_inicial = TAMANO_CONTADOR
        elif cat in ("dialogos", "dialogo"):
            tamano_inicial = TAMANO_DIALOGOS
        else:
            tamano_inicial = TAMANO_TEXTO

    t_actual = tamano_inicial
    f_actual = obtener_fuente(categoria, tamano=t_actual, negrita=negrita)

    if not texto or (ancho_max is None and alto_max is None):
        return f_actual, t_actual

    while t_actual > tamano_min:
        w, h = f_actual.size(str(texto))
        cabe_ancho = (ancho_max is None) or (w <= ancho_max)
        cabe_alto = (alto_max is None) or (h <= alto_max)
        if cabe_ancho and cabe_alto:
            return f_actual, t_actual
        t_actual -= 1
        f_actual = obtener_fuente(categoria, tamano=t_actual, negrita=negrita)

    return f_actual, t_actual


def renderizar_texto_ajustado(texto, categoria="texto", tamano=None, ancho_max=None, alto_max=None, color=(255, 255, 255), tamano_min=10, negrita=False):
    """
    Renderiza un texto en una superficie ajustando automáticamente su tamaño de fuente para no desbordar.
    Si incluso en el tamaño mínimo supera los límites, escala proporcionalmente de forma suave.
    Retorna la tupla (superficie_renderizada, fuente_utilizada).
    """
    str_txt = str(texto if texto is not None else "")
    if not str_txt:
        return pygame.Surface((0, 0), pygame.SRCALPHA), obtener_fuente(categoria, tamano=tamano, negrita=negrita)

    fuente_opt, _ = ajustar_tamano_fuente(
        texto=str_txt,
        categoria=categoria,
        tamano_inicial=tamano,
        ancho_max=ancho_max,
        alto_max=alto_max,
        tamano_min=tamano_min,
        negrita=negrita
    )
    surf = fuente_opt.render(str_txt, True, color)

    # Garantía absoluta: si aún supera ancho_max o alto_max por límites de la tipografía, escalar suavemente
    cur_w, cur_h = surf.get_size()
    escala_x = (ancho_max / cur_w) if (ancho_max and cur_w > ancho_max) else 1.0
    escala_y = (alto_max / cur_h) if (alto_max and cur_h > alto_max) else 1.0
    factor = min(escala_x, escala_y)

    if factor < 0.999:
        nuevo_w = max(1, int(cur_w * factor))
        nuevo_h = max(1, int(cur_h * factor))
        try:
            surf = pygame.transform.smoothscale(surf, (nuevo_w, nuevo_h))
        except Exception:
            surf = pygame.transform.scale(surf, (nuevo_w, nuevo_h))

    return surf, fuente_opt


def renderizar_texto_multilinea(
    texto,
    categoria="texto",
    tamano=None,
    ancho_max=None,
    alto_max=None,
    color=(255, 255, 255),
    alineacion="centro",
    interlineado=4,
    negrita=False,
    tamano_min=10
):
    """
    Distribuye y renderiza un texto en múltiples líneas dentro de ancho_max.
    Si se especifica alto_max y las líneas no caben, reduce la fuente gradualmente hasta tamano_min.
    Retorna la superficie compuesta transparente (pygame.SRCALPHA).
    """
    str_txt = str(texto if texto is not None else "")
    if not str_txt:
        return pygame.Surface((0, 0), pygame.SRCALPHA)

    if tamano is None:
        cat = str(categoria).lower().strip()
        if cat == "titulo":
            tamano = TAMANO_TITULO
        elif cat == "subtitulo":
            tamano = TAMANO_SUBTITULO
        elif cat in ("boton", "botones"):
            tamano = TAMANO_BOTONES
        elif cat in ("dialogos", "dialogo"):
            tamano = TAMANO_DIALOGOS
        elif cat == "pequena":
            tamano = TAMANO_PEQUENA
        else:
            tamano = TAMANO_TEXTO

    t_actual = tamano
    f_actual = obtener_fuente(categoria, tamano=t_actual, negrita=negrita)
    max_w_calc = ancho_max or 500

    while True:
        lineas = dividir_texto_en_lineas(str_txt, f_actual, max_w_calc)
        h_linea = f_actual.get_linesize()
        total_h = len(lineas) * h_linea + max(0, len(lineas) - 1) * interlineado
        if alto_max is None or total_h <= alto_max or t_actual <= tamano_min:
            break
        t_actual -= 1
        f_actual = obtener_fuente(categoria, tamano=t_actual, negrita=negrita)

    ancho_total = 0
    surfs_lineas = []
    for l in lineas:
        s = f_actual.render(l, True, color)
        surfs_lineas.append(s)
        if s.get_width() > ancho_total:
            ancho_total = s.get_width()

    ancho_comp = max(ancho_total, 1)
    if ancho_max is not None and alineacion == "centro":
        ancho_comp = max(ancho_comp, ancho_max)
    alto_comp = max(total_h, 1)

    surf_resultado = pygame.Surface((ancho_comp, alto_comp), pygame.SRCALPHA)
    cur_y = 0
    for s in surfs_lineas:
        if alineacion == "centro":
            cur_x = (ancho_comp - s.get_width()) // 2
        elif alineacion == "derecha":
            cur_x = ancho_comp - s.get_width()
        else:
            cur_x = 0
        surf_resultado.blit(s, (cur_x, cur_y))
        cur_y += h_linea + interlineado

    # Si supera alto_max o ancho_max por restricciones de tamano_min, escalar suavemente
    cur_w, cur_h = surf_resultado.get_size()
    escala_x = (ancho_max / cur_w) if (ancho_max and cur_w > ancho_max) else 1.0
    escala_y = (alto_max / cur_h) if (alto_max and cur_h > alto_max) else 1.0
    factor = min(escala_x, escala_y)
    if factor < 0.999:
        nuevo_w = max(1, int(cur_w * factor))
        nuevo_h = max(1, int(cur_h * factor))
        try:
            surf_resultado = pygame.transform.smoothscale(surf_resultado, (nuevo_w, nuevo_h))
        except Exception:
            surf_resultado = pygame.transform.scale(surf_resultado, (nuevo_w, nuevo_h))

    return surf_resultado


def dibujar_texto_en_rect(
    superficie_destino,
    texto,
    rect_contenedor,
    categoria="texto",
    tamano=None,
    color=(255, 255, 255),
    padding=6,
    multiline=False,
    alineacion="centro",
    alineacion_v="centro",
    negrita=False,
    tamano_min=10,
    interlineado=4
):
    """
    Dibuja un texto centrado o alineado dentro de un contenedor respetando márgenes interiores.
    Ajusta automáticamente el tamaño de la fuente o distribuye en múltiples líneas para evitar cualquier desborde.
    Retorna el pygame.Rect ocupado por el texto dibujado.
    """
    if not texto:
        return pygame.Rect(0, 0, 0, 0)

    rect_c = pygame.Rect(rect_contenedor)
    pad_h = min(padding, max(0, (rect_c.width - 10) // 2))
    pad_v = min(padding, max(0, (rect_c.height - 10) // 2))
    inner_w = max(10, rect_c.width - (pad_h * 2))
    inner_h = max(10, rect_c.height - (pad_v * 2))

    if multiline:
        surf_txt = renderizar_texto_multilinea(
            texto=texto,
            categoria=categoria,
            tamano=tamano,
            ancho_max=inner_w,
            alto_max=inner_h,
            color=color,
            alineacion=alineacion,
            interlineado=interlineado,
            negrita=negrita,
            tamano_min=tamano_min
        )
    else:
        surf_txt, _ = renderizar_texto_ajustado(
            texto=texto,
            categoria=categoria,
            tamano=tamano,
            ancho_max=inner_w,
            alto_max=inner_h,
            color=color,
            tamano_min=tamano_min,
            negrita=negrita
        )

    # Posicionamiento horizontal
    if alineacion == "centro":
        dest_x = rect_c.centerx - (surf_txt.get_width() // 2)
    elif alineacion == "derecha":
        dest_x = rect_c.right - pad_h - surf_txt.get_width()
    else:  # "izquierda"
        dest_x = rect_c.left + pad_h

    # Posicionamiento vertical
    if alineacion_v == "centro":
        dest_y = rect_c.centery - (surf_txt.get_height() // 2)
    elif alineacion_v == "abajo":
        dest_y = rect_c.bottom - pad_v - surf_txt.get_height()
    else:  # "arriba"
        dest_y = rect_c.top + pad_v

    rect_dibujado = superficie_destino.blit(surf_txt, (dest_x, dest_y))
    return rect_dibujado



