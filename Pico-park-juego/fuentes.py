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

# ==============================================================================
# 1. VARIABLES CENTRALIZADAS PARA LAS TIPOGRAFÍAS
# ==============================================================================
# Para cambiar la tipografía de una categoría en todo el juego, modifica estas variables:
# - Puedes asignar el nombre de archivo en Sprites/Fuentes o ruta: ej. "04B_30__.TTF"
# - Puedes asignar el nombre de una fuente del sistema: ej. "Arial", "Segoe UI", "Verdana"
# - Puedes asignar None para usar la tipografía predeterminada de Pygame
# ==============================================================================
FUENTE_TITULO = "04B_30__.TTF"      # Títulos principales de las pantallas
FUENTE_SUBTITULO = None            # Subtítulos y encabezados secundarios
FUENTE_TEXTO = None                # Textos normales, descripciones y mensajes
FUENTE_BOTON = "04B_30__.TTF"      # Texto de los botones y badges interactivos
FUENTE_PEQUENA = None              # Textos secundarios, indicaciones y datos pequeños

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

TAMANO_BOTON = 15                  # Botones estándar del menú y tarjetas
TAMANO_BOTON_GRANDE = 20           # Botones destacados y primarios
TAMANO_BOTON_MODAL = 12            # Botones de modales y acciones secundarias

TAMANO_PEQUENA = 20                # Indicaciones pequeñas y detalles de partida
TAMANO_ITEM_TITULO = 14            # Títulos de ítems en listas de partidas y cards
TAMANO_BADGE = 15                  # Badges de estado, checkmarks y etiquetas
TAMANO_CARD = 13                   # Etiquetas en cards de niveles


# ==============================================================================
# 3. GESTIÓN Y CARGA OPTIMIZADA CON CACHÉ
# ==============================================================================
_CACHE_FUENTES = {}


def limpiar_cache_fuentes():
    """Limpia el caché interno para forzar la recarga si se cambian variables dinámicamente."""
    _CACHE_FUENTES.clear()


def _resolver_ruta_fuente(nombre_o_ruta):
    """Resuelve la ruta absoluta al archivo de fuente, descomprimiendo el zip si es necesario."""
    if not nombre_o_ruta:
        return None

    if os.path.isabs(nombre_o_ruta) and os.path.isfile(nombre_o_ruta):
        return nombre_o_ruta

    # Buscar en Sprites/Fuentes
    ruta_en_sprites = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes", os.path.basename(nombre_o_ruta))
    if os.path.isfile(ruta_en_sprites):
        return ruta_en_sprites

    # Intentar extraer desde zip si no está extraída
    if os.path.isfile(RUTA_FUENTE_ZIP):
        try:
            import zipfile
            dest_dir = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes")
            with zipfile.ZipFile(RUTA_FUENTE_ZIP, "r") as z:
                z.extractall(dest_dir)
            if os.path.isfile(ruta_en_sprites):
                return ruta_en_sprites
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
    elif cat == "boton":
        fuente_config = FUENTE_BOTON
        tamano_defecto = TAMANO_BOTON
    elif cat == "pequena":
        fuente_config = FUENTE_PEQUENA
        tamano_defecto = TAMANO_PEQUENA
    else:  # "texto" o general
        fuente_config = FUENTE_TEXTO
        tamano_defecto = TAMANO_TEXTO

    tamano_final = tamano if tamano is not None else tamano_defecto

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

    if font_obj is None:
        if cat in ("subtitulo", "texto", "pequena", "general") or fuente_config is None:
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


def obtener_fuente_titulo(tamano=None, tamano_fallback=None):
    """Retorna la fuente configurada para títulos principales."""
    return obtener_fuente("titulo", tamano=tamano, tamano_fallback=tamano_fallback)


def obtener_fuente_subtitulo(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para subtítulos y encabezados."""
    return obtener_fuente("subtitulo", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_texto(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para textos normales y descripciones."""
    return obtener_fuente("texto", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_boton(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para botones y opciones."""
    return obtener_fuente("boton", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def obtener_fuente_pequena(tamano=None, negrita=False, tamano_fallback=None):
    """Retorna la fuente configurada para textos secundarios y detalles."""
    return obtener_fuente("pequena", tamano=tamano, negrita=negrita, tamano_fallback=tamano_fallback)


def cargar_fuente_pixel(tamano, fallback_tamano=None):
    """Función de compatibilidad retroactiva con código existente."""
    return obtener_fuente_titulo(tamano=tamano, tamano_fallback=fallback_tamano)

