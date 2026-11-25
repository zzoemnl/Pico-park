"""
Módulo de Configuración, Audio e Internacionalización (i18n) - Pico Park.

Gestiona:
1. Control de volumen del juego (0% a 100%) con retroalimentación sonora y control de canales de Pygame.
2. Selector de idioma global (Español, English, 简体中文) sin reiniciar la partida.
3. Pestaña modal superpuesta de Configuración que conserva el estado y progreso del juego.
"""

import os
import time
import sys
import json
import math
import struct
import random
import unicodedata
import pygame

from rutas import directorio_base, ruta_datos

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from sprites import (
    cargar_boton_escalado,
    animar_pulsacion_boton,
    aclarar_boton,
    generar_boton_con_texto,
)
from fuentes import (
    obtener_fuente_subtitulo,
    obtener_fuente_contador,
    limpiar_cache_fuentes,
    dibujar_texto_en_rect,
)
from idiomas import DICCIONARIO

# ==============================================================================
# VARIABLES CENTRALIZADAS DE AUDIO Y MÚSICA
# ==============================================================================
# Configura aquí las rutas o nombres de archivo de cada pista de música y el volumen.
# Puedes colocar los archivos en 'assets/audio/' o 'Sprites/Audio/' (.mp3, .ogg, .wav).
# ==============================================================================
AUDIO_MENU = "sonidos/menú/menú.mp3"  # Música del menú principal (menú.mp3 o Caillou aleatorio)
AUDIO_MUNDO_1 = "mundo1"  # Música del Mundo 1 (carpeta sonidos/mundo1/)
AUDIO_MUNDO_2 = "mundo2"  # Música del Mundo 2 (carpeta sonidos/mundo2/)
AUDIO_MUNDO_3 = "mundo3"  # Música del Mundo 3 (carpeta sonidos/mundo3/)
AUDIO_AHOGAMIENTO = "sonidos/ahogamiento/ahogamiento.mp3"  # Efecto de sonido de ahogamiento (Mundo 3 niveles 5 y 6)

VOLUMEN_MUSICA = 70             # Volumen general de la música (0 a 100)
VOLUMEN_EFECTOS = 70            # Volumen general de efectos de sonido (0 a 100)

_volumen = 70                   # Volumen maestro (sincronizado con música y efectos)
_idioma = "es"                  # Idioma actual: "es" | "en" | "zh"

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)
DIRECTORIO_RAIZ = directorio_base()
RUTA_CONFIG_JSON = ruta_datos("configuracion.json")

EXTENSIONES_AUDIO_SOPORTADAS = (".mp3", ".wav", ".ogg")

CARPETAS_AUDIO = [
    os.path.join(DIRECTORIO_RAIZ, "mundo1"),
    os.path.join(DIRECTORIO_RAIZ, "mundo2"),
    os.path.join(DIRECTORIO_RAIZ, "mundo3"),
    os.path.join(DIRECTORIO_ACTUAL, "mundo1"),
    os.path.join(DIRECTORIO_ACTUAL, "mundo2"),
    os.path.join(DIRECTORIO_ACTUAL, "mundo3"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "menú"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "menu"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "mundo1"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "mundo2"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "mundo3"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "ahogamiento"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menú"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menu"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "mundo1"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "mundo2"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "mundo3"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "ahogamiento"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos"),
    os.path.join(DIRECTORIO_RAIZ, "assets", "audio"),
    os.path.join(DIRECTORIO_ACTUAL, "assets", "audio"),
    os.path.join(DIRECTORIO_RAIZ, "Sprites", "Audio"),
    os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Audio"),
    os.path.join(DIRECTORIO_RAIZ, "assets"),
    os.path.join(DIRECTORIO_ACTUAL, "assets"),
]

# Estado interno del reproductor de música y efectos
_pista_activa_tipo = None
_archivo_musica_actual = None
# Cada cuántos segundos se vuelve a mirar el disco cuando se pide la pista que ya está sonando
INTERVALO_RECHEQUEO_MUSICA = 2.0
_ultimo_chequeo_musica = 0.0
_ALIAS_TIPO_MUSICA = {
    "menu": ("menu", "principal", "navegacion", "menu_1", "menu1", "menu 1", "menú 1", "menú_1"),
    "mundo_1": ("mundo_1", "mundo1", "1"),
    "mundo_2": ("mundo_2", "mundo2", "2"),
    "mundo_3": ("mundo_3", "mundo3", "3"),
}
_musica_menu_sesion = None
_modo_musica_menu = "aleatorio"  # "aleatorio", "caillou", "christmas"
_CANAL_AHOGAMIENTO = None
_SONIDO_AHOGAMIENTO = None




def t(clave, default=None):
    """
    Retorna la traducción de una clave en el idioma actual.
    Si no existe la traducción, retorna el valor predeterminado o la clave misma.
    """
    info = DICCIONARIO.get(clave)
    if isinstance(info, dict):
        return info.get(_idioma, info.get("es", default or clave))
    if isinstance(clave, str):
        c_low = clave.lower().strip()
        info = DICCIONARIO.get(c_low)
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
        _guardar_configuracion_disco()
        try:
            limpiar_cache_fuentes()
        except Exception:
            pass
        try:
            from sprites import limpiar_cache_botones
            limpiar_cache_botones()
        except Exception:
            pass
        try:
            import menu_niveles
            menu_niveles._CACHE_TABS_MUNDOS.clear()
        except Exception:
            pass


# ==============================================================================
# PERSISTENCIA DE CONFIGURACIÓN
# ==============================================================================
def _guardar_configuracion_disco():
    """Persiste el volumen y las preferencias para conservarlos entre partidas y sesiones."""
    try:
        datos = {
            "volumen": _volumen,
            "volumen_musica": VOLUMEN_MUSICA,
            "volumen_efectos": VOLUMEN_EFECTOS,
            "idioma": "es",
            "musica_menu": _modo_musica_menu,
        }
        # Escritura atómica: primero a un archivo temporal y después se reemplaza, así un corte
        # a mitad de la escritura no deja configuracion.json corrupto (mismo patrón que partidas.txt).
        ruta_tmp = RUTA_CONFIG_JSON + ".tmp"
        with open(ruta_tmp, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(ruta_tmp, RUTA_CONFIG_JSON)
    except Exception:
        pass


def _cargar_configuracion_disco():
    """Carga los ajustes guardados de volumen y música del menú si existen en disco. Al iniciar el juego siempre debe estar en español."""
    global _volumen, VOLUMEN_MUSICA, VOLUMEN_EFECTOS, _idioma, _modo_musica_menu
    _idioma = "es"
    if os.path.isfile(RUTA_CONFIG_JSON):
        try:
            with open(RUTA_CONFIG_JSON, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if "volumen" in datos:
                _volumen = max(0, min(100, int(datos["volumen"])))
            if "volumen_musica" in datos:
                VOLUMEN_MUSICA = max(0, min(100, int(datos["volumen_musica"])))
            else:
                VOLUMEN_MUSICA = _volumen
            if "volumen_efectos" in datos:
                VOLUMEN_EFECTOS = max(0, min(100, int(datos["volumen_efectos"])))
            else:
                VOLUMEN_EFECTOS = _volumen
            if "musica_menu" in datos:
                modo_c = str(datos["musica_menu"]).lower().strip()
                if modo_c in ("aleatorio", "caillou", "christmas"):
                    _modo_musica_menu = modo_c
        except Exception:
            pass
    _idioma = "es"


# Carga inicial de ajustes al importar el módulo
_cargar_configuracion_disco()


# ==============================================================================
# GESTIÓN Y REPRODUCCIÓN DE MÚSICA Y AUDIO
# ==============================================================================
def obtener_audio_mundo(numero_mundo):
    """
    Busca automáticamente el primer archivo de audio compatible (.mp3, .wav, .ogg)
    dentro de la carpeta del mundo correspondiente ('mundo1/', 'mundo2/', 'mundo3/').

    El nombre del archivo puede ser cualquiera (por ejemplo musica.mp3, nivel.wav, bgm.ogg).
    Explora en orden de prioridad:
      1. Raíz del proyecto: mundo{N}/
      2. Directorio del código: Pico-park-juego/mundo{N}/
      3. Carpeta sonidos: sonidos/mundo{N}/
      4. Subcarpeta sonidos con espacio o guion: sonidos/mundo {N}/
      5. Carpeta assets: assets/audio/mundo{N}/
      6. Directorio de trabajo actual: ./mundo{N}/

    Retorna la ruta absoluta normalizada del archivo, o None si la carpeta no existe,
    está vacía o no tiene formatos compatibles.
    """
    try:
        num = int(numero_mundo)
    except (ValueError, TypeError):
        return None

    formatos = EXTENSIONES_AUDIO_SOPORTADAS
    nombres_carpeta = [
        f"mundo{num}",
        f"mundo_{num}",
        f"mundo {num}",
        f"Mundo{num}",
        f"Mundo_{num}",
        f"Mundo {num}",
    ]

    padres = [
        DIRECTORIO_RAIZ,
        DIRECTORIO_ACTUAL,
        os.path.join(DIRECTORIO_RAIZ, "sonidos"),
        os.path.join(DIRECTORIO_ACTUAL, "sonidos"),
        os.path.join(DIRECTORIO_RAIZ, "assets", "audio"),
        os.path.join(DIRECTORIO_ACTUAL, "assets", "audio"),
        os.getcwd(),
        os.path.join(os.getcwd(), "sonidos"),
    ]

    carpetas_vistas = set()

    for p in padres:
        if not p or not os.path.isdir(p):
            continue
        for nom in nombres_carpeta:
            dir_candidato = os.path.normpath(os.path.abspath(os.path.join(p, nom)))
            if dir_candidato in carpetas_vistas:
                continue
            carpetas_vistas.add(dir_candidato)

            if os.path.isdir(dir_candidato):
                try:
                    entradas = sorted(os.listdir(dir_candidato))
                except Exception:
                    continue
                for item in entradas:
                    ruta_archivo = os.path.join(dir_candidato, item)
                    if os.path.isfile(ruta_archivo):
                        _, ext = os.path.splitext(item)
                        if ext.lower() in formatos:
                            return os.path.normpath(os.path.abspath(ruta_archivo))

    # Fallback de compatibilidad hacia pistas antiguas directas si existen (evitando recursión si es alias del mismo mundo)
    alias_mismos = {1: ("mundo1", "mundo_1", "mundo 1"), 2: ("mundo2", "mundo_2", "mundo 2"), 3: ("mundo3", "mundo_3", "mundo 3")}
    pista_leg = {1: AUDIO_MUNDO_1, 2: AUDIO_MUNDO_2, 3: AUDIO_MUNDO_3}.get(num)
    if pista_leg and str(pista_leg).lower().strip() not in alias_mismos.get(num, ()):
        ruta_leg = _resolver_ruta_audio(pista_leg)
        if ruta_leg:
            return ruta_leg

    return None


def obtener_pistas_musica_menu():
    """
    Retorna la lista de rutas absolutas de todos los archivos de música disponibles para el menú principal.
    Busca en carpetas de menús soportadas ('sonidos/menú/', 'sonidos/menu/', 'assets/audio/menu/', etc.).
    """
    formatos = EXTENSIONES_AUDIO_SOPORTADAS
    padres = [
        DIRECTORIO_RAIZ,
        DIRECTORIO_ACTUAL,
        os.path.join(DIRECTORIO_RAIZ, "sonidos"),
        os.path.join(DIRECTORIO_ACTUAL, "sonidos"),
    ]
    pistas_encontradas = []
    rutas_vistas = set()

    for p in padres:
        if not p or not os.path.isdir(p):
            continue
        try:
            entradas_p = os.listdir(p)
        except Exception:
            continue
        for nom in entradas_p:
            norm_nom = unicodedata.normalize('NFD', nom).encode('ascii', 'ignore').decode('utf-8').lower()
            if "menu" in norm_nom:
                dir_c = os.path.join(p, nom)
                if os.path.isdir(dir_c):
                    try:
                        for item in sorted(os.listdir(dir_c)):
                            ruta_arch = os.path.normpath(os.path.abspath(os.path.join(dir_c, item)))
                            if os.path.isfile(ruta_arch) and ruta_arch not in rutas_vistas:
                                _, ext = os.path.splitext(item)
                                if ext.lower() in formatos:
                                    rutas_vistas.add(ruta_arch)
                                    pistas_encontradas.append(ruta_arch)
                    except Exception:
                        pass

    # Incluir AUDIO_MENU si existe en disco y no fue agregado aún
    ruta_leg = _resolver_ruta_audio(AUDIO_MENU)
    if ruta_leg and os.path.isfile(ruta_leg) and ruta_leg not in rutas_vistas:
        pistas_encontradas.append(ruta_leg)

    return pistas_encontradas


def obtener_pista_caillou():
    """Retorna la ruta absoluta del archivo de audio de Caillou si existe en disco."""
    pistas = obtener_pistas_musica_menu()
    for p in pistas:
        nom = unicodedata.normalize('NFD', os.path.basename(p)).encode('ascii', 'ignore').decode('utf-8').lower()
        if "caillou" in nom:
            return p
    # Rutas directas alternativas
    candidatos = [
        os.path.join(DIRECTORIO_RAIZ, "sonidos", "menú", "Caillou Theme [8 Bit Tribute to Caillou & Jeffrey Zann] - 8 Bit Universe.mp3"),
        os.path.join(DIRECTORIO_RAIZ, "sonidos", "menu", "Caillou Theme [8 Bit Tribute to Caillou & Jeffrey Zann] - 8 Bit Universe.mp3"),
        os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menú", "Caillou Theme [8 Bit Tribute to Caillou & Jeffrey Zann] - 8 Bit Universe.mp3"),
        os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menu", "Caillou Theme [8 Bit Tribute to Caillou & Jeffrey Zann] - 8 Bit Universe.mp3"),
    ]
    for c in candidatos:
        if os.path.isfile(c):
            return os.path.normpath(os.path.abspath(c))
    return None


def obtener_pista_christmas():
    """Retorna la ruta absoluta del archivo de audio navideño (menú.mp3) si existe en disco."""
    pistas = obtener_pistas_musica_menu()
    for p in pistas:
        nom = unicodedata.normalize('NFD', os.path.basename(p)).encode('ascii', 'ignore').decode('utf-8').lower()
        if "menu" in nom and "caillou" not in nom:
            return p
    candidatos = [
        os.path.join(DIRECTORIO_RAIZ, "sonidos", "menú", "menú.mp3"),
        os.path.join(DIRECTORIO_RAIZ, "sonidos", "menu", "menú.mp3"),
        os.path.join(DIRECTORIO_RAIZ, "sonidos", "menu", "menu.mp3"),
        os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menú", "menú.mp3"),
        os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menu", "menu.mp3"),
        _resolver_ruta_audio(AUDIO_MENU),
    ]
    for c in candidatos:
        if c and os.path.isfile(c):
            return os.path.normpath(os.path.abspath(c))
    return None


def obtener_modo_musica_menu():
    """Retorna el modo configurado para la música del menú ('aleatorio', 'caillou', o 'christmas')."""
    global _modo_musica_menu
    if _modo_musica_menu not in ("aleatorio", "caillou", "christmas"):
        _modo_musica_menu = "aleatorio"
    return _modo_musica_menu


def fijar_modo_musica_menu(nuevo_modo, reproducir_inmediato=True):
    """
    Fija el modo de reproducción para la música del menú principal:
    - 'aleatorio': 50% de probabilidad entre Caillou y Christmas al iniciar y al volver al menú.
    - 'caillou': Siempre Caillou en el menú principal.
    - 'christmas': Siempre música navideña (menú.mp3) en el menú principal.
    Persiste la elección en configuracion.json y actualiza la reproducción de inmediato si estamos en el menú.
    """
    global _modo_musica_menu, _musica_menu_sesion
    modo_norm = str(nuevo_modo).lower().strip()
    if modo_norm not in ("aleatorio", "caillou", "christmas"):
        modo_norm = "aleatorio"
    _modo_musica_menu = modo_norm
    _guardar_configuracion_disco()

    if modo_norm == "caillou":
        _musica_menu_sesion = obtener_pista_caillou()
    elif modo_norm == "christmas":
        _musica_menu_sesion = obtener_pista_christmas()
    else:  # aleatorio
        seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)

    if reproducir_inmediato and (_pista_activa_tipo == "menu" or _pista_activa_tipo is None):
        reproducir_musica("menu", forzar=True)
    return _modo_musica_menu


def seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=False):
    """
    Selecciona la pista de música para el menú principal según el modo configurado:
    - Si el modo es 'caillou', siempre devuelve la pista de Caillou.
    - Si el modo es 'christmas', siempre devuelve la pista navideña (menú.mp3).
    - Si el modo es 'aleatorio':
        * Elige con probabilidad exacta del 50 % entre Caillou y Christmas mediante entropía del sistema (random.SystemRandom).
        * Si forzar_nueva_eleccion es True (por ejemplo al volver de un nivel o al iniciar el juego), realiza un nuevo sorteo.
    """
    global _musica_menu_sesion, _modo_musica_menu
    modo = obtener_modo_musica_menu()
    pista_caillou = obtener_pista_caillou()
    pista_christmas = obtener_pista_christmas()

    if modo == "caillou":
        _musica_menu_sesion = pista_caillou or pista_christmas or _resolver_ruta_audio(AUDIO_MENU)
        return _musica_menu_sesion
    elif modo == "christmas":
        _musica_menu_sesion = pista_christmas or pista_caillou or _resolver_ruta_audio(AUDIO_MENU)
        return _musica_menu_sesion
    else:
        # Modo 'aleatorio': selección con probabilidad equitativa exacta (50% / 50%)
        if _musica_menu_sesion is not None and not forzar_nueva_eleccion and os.path.isfile(_musica_menu_sesion):
            return _musica_menu_sesion
        candidatos = []
        if pista_caillou and os.path.isfile(pista_caillou):
            candidatos.append(pista_caillou)
        if pista_christmas and os.path.isfile(pista_christmas):
            candidatos.append(pista_christmas)
        if len(candidatos) >= 2:
            _musica_menu_sesion = random.SystemRandom().choice(candidatos)
        elif len(candidatos) == 1:
            _musica_menu_sesion = candidatos[0]
        else:
            pistas = obtener_pistas_musica_menu()
            if pistas:
                _musica_menu_sesion = random.SystemRandom().choice(pistas)
            else:
                _musica_menu_sesion = _resolver_ruta_audio(AUDIO_MENU)
        return _musica_menu_sesion


def _resolver_audio_menu():
    """
    Retorna la ruta del archivo de audio del menú principal según la configuración activa.
    Si aún no ha sido resuelta o seleccionada, ejecuta seleccionar_musica_menu_aleatoria.
    """
    global _musica_menu_sesion
    modo = obtener_modo_musica_menu()
    if modo == "caillou":
        _musica_menu_sesion = obtener_pista_caillou()
        return _musica_menu_sesion
    elif modo == "christmas":
        _musica_menu_sesion = obtener_pista_christmas()
        return _musica_menu_sesion
    else:
        if _musica_menu_sesion is None or not os.path.isfile(_musica_menu_sesion):
            return seleccionar_musica_menu_aleatoria()
        return _musica_menu_sesion


def _resolver_ruta_audio(pista_o_nombre):
    """
    Localiza el archivo de audio comprobando rutas absolutas, relativas y carpetas
    sonidos, assets/audio y Sprites/Audio. Soporta extensiones .mp3, .ogg, .wav.
    """
    if not pista_o_nombre:
        return None

    pista_str = str(pista_o_nombre).lower().strip()
    if pista_str in ("mundo1", "mundo_1", "mundo 1"):
        res_m = obtener_audio_mundo(1)
        if res_m:
            return res_m
    elif pista_str in ("mundo2", "mundo_2", "mundo 2"):
        res_m = obtener_audio_mundo(2)
        if res_m:
            return res_m
    elif pista_str in ("mundo3", "mundo_3", "mundo 3"):
        res_m = obtener_audio_mundo(3)
        if res_m:
            return res_m

    # 1. Comprobar si es ruta absoluta existente
    if os.path.isabs(pista_o_nombre) and os.path.isfile(pista_o_nombre):
        return os.path.normpath(pista_o_nombre)

    # 2. Comprobar ruta directa o relativa respecto al directorio de trabajo o a la raíz
    candidatos_rel = [
        pista_o_nombre,
        os.path.join(DIRECTORIO_RAIZ, pista_o_nombre),
        os.path.join(DIRECTORIO_ACTUAL, "..", pista_o_nombre),
        os.path.join(DIRECTORIO_ACTUAL, pista_o_nombre),
    ]
    for c in candidatos_rel:
        if os.path.isfile(c):
            return os.path.normpath(os.path.abspath(c))

    base = os.path.basename(pista_o_nombre)
    nombres_a_buscar = [base]
    if "menú" in base:
        nombres_a_buscar.append(base.replace("menú", "menu"))
    elif "menu" in base:
        nombres_a_buscar.append(base.replace("menu", "menú"))
    if "mundo1" in base:
        nombres_a_buscar.append(base.replace("mundo1", "mundo 1"))
    elif "mundo 1" in base:
        nombres_a_buscar.append(base.replace("mundo 1", "mundo1"))

    nombre_raiz, ext = os.path.splitext(base)
    if not ext:
        for posible_ext in [".mp3", ".ogg", ".wav"]:
            nombres_a_buscar.append(nombre_raiz + posible_ext)
            if "menú" in nombre_raiz:
                nombres_a_buscar.append(nombre_raiz.replace("menú", "menu") + posible_ext)
            elif "menu" in nombre_raiz:
                nombres_a_buscar.append(nombre_raiz.replace("menu", "menú") + posible_ext)
            if "mundo1" in nombre_raiz:
                nombres_a_buscar.append(nombre_raiz.replace("mundo1", "mundo 1") + posible_ext)
            elif "mundo 1" in nombre_raiz:
                nombres_a_buscar.append(nombre_raiz.replace("mundo 1", "mundo1") + posible_ext)

    for carpeta in CARPETAS_AUDIO:
        for nom in nombres_a_buscar:
            ruta_candidata = os.path.join(carpeta, nom)
            if os.path.isfile(ruta_candidata):
                return os.path.normpath(ruta_candidata)

    # Buscar también en el directorio del script
    for nom in nombres_a_buscar:
        ruta_directa = os.path.join(DIRECTORIO_ACTUAL, nom)
        if os.path.isfile(ruta_directa):
            return os.path.normpath(ruta_directa)

    return None


def reproducir_musica(tipo="menu", forzar=False):
    """
    Reproduce la pista musical indicada ('menu', 'mundo_1', 'mundo_2', 'mundo_3', o número 1, 2, 3) en bucle continuo.
    - Busca automáticamente el archivo de audio (.mp3, .wav, .ogg) en la carpeta del mundo ('mundo1/', 'mundo2/', 'mundo3/').
    - El nombre del archivo puede ser cualquiera (detectado automáticamente).
    - Si la misma pista ya está sonando, NO se reinicia (conserva la continuidad entre niveles del mismo mundo o reinicios).
    - Al pasar de un mundo a otro, la música previa se detiene y comienza la del nuevo mundo.
    - Si una carpeta está vacía o no tiene archivo de audio compatible, detiene la música previa y el juego continúa
      normalmente en silencio sin ningún error ni excepción.
    - Garantiza que nunca se reproduzcan dos pistas simultáneas.
    - Aplica estrictamente el volumen fijado en OPCIONES.
    """
    global _pista_activa_tipo, _archivo_musica_actual

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        return

    # Normalizar identificador del tipo de pista
    tipo_str = str(tipo).lower().strip()

    # El menú llama a esta función en cada frame. Resolver la ruta implica ir al disco
    # (os.path.isfile / os.listdir), así que si la pista pedida es la que ya suena solo se
    # vuelve a comprobar el disco cada INTERVALO_RECHEQUEO_MUSICA segundos.
    global _ultimo_chequeo_musica
    ahora = time.monotonic()
    if not forzar and _pista_activa_tipo is not None and tipo_str in _ALIAS_TIPO_MUSICA.get(_pista_activa_tipo, (_pista_activa_tipo,)):
        if ahora - _ultimo_chequeo_musica < INTERVALO_RECHEQUEO_MUSICA:
            return
    _ultimo_chequeo_musica = ahora

    if tipo_str in ("menu", "principal", "navegacion", "menu_1", "menu1", "menu 1", "menú 1", "menú_1"):
        tipo_normalizado = "menu"
        # Si venimos de un nivel/jefe hacia el menú principal y el modo es aleatorio, forzar nueva elección 50/50
        if _pista_activa_tipo is not None and _pista_activa_tipo != "menu":
            if obtener_modo_musica_menu() == "aleatorio":
                seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
        ruta_audio = _resolver_audio_menu()
    elif tipo_str in ("mundo_1", "mundo1", "1") or tipo == 1:
        tipo_normalizado = "mundo_1"
        ruta_audio = obtener_audio_mundo(1)
    elif tipo_str in ("mundo_2", "mundo2", "2") or tipo == 2:
        tipo_normalizado = "mundo_2"
        ruta_audio = obtener_audio_mundo(2)
    elif tipo_str in ("mundo_3", "mundo3", "3") or tipo == 3:
        tipo_normalizado = "mundo_3"
        ruta_audio = obtener_audio_mundo(3)
    else:
        tipo_normalizado = tipo_str
        ruta_audio = _resolver_ruta_audio(tipo)

    # Si ya está sonando este mismo tipo de pista y no se solicita forzar reinicio:
    if tipo_normalizado == _pista_activa_tipo and not forzar:
        # Si el archivo resuelto en disco no ha cambiado, mantener la reproducción continua sin interrupción
        if ruta_audio == _archivo_musica_actual:
            return

    # Actualizar el tipo de pista activa
    _pista_activa_tipo = tipo_normalizado

    # Detener la música anterior para evitar cualquier superposición
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

    if not ruta_audio or not os.path.isfile(ruta_audio):
        # Si la carpeta está vacía o no contiene audio compatible, continuar en silencio sin fallar
        _archivo_musica_actual = None
        return

    try:
        pygame.mixer.music.load(ruta_audio)
        vol_float = max(0.0, min(1.0, VOLUMEN_MUSICA / 100.0))
        pygame.mixer.music.set_volume(vol_float)
        pygame.mixer.music.play(-1)
        _archivo_musica_actual = ruta_audio
    except Exception:
        # En caso de cualquier error con el formato de audio, continuar normalmente sin cerrar el juego
        _archivo_musica_actual = None


def detener_musica():
    """Detiene la música actual de forma segura y cualquier efecto en bucle."""
    global _pista_activa_tipo, _archivo_musica_actual
    _pista_activa_tipo = None
    _archivo_musica_actual = None
    detener_sonido_ahogamiento()
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


def _obtener_sonido_ahogamiento():
    """Carga y retorna el objeto pygame.mixer.Sound del efecto de ahogamiento."""
    global _SONIDO_AHOGAMIENTO
    if _SONIDO_AHOGAMIENTO is not None:
        return _SONIDO_AHOGAMIENTO

    ruta = _resolver_ruta_audio(AUDIO_AHOGAMIENTO)
    if not ruta or not os.path.isfile(ruta):
        ruta = _resolver_ruta_audio("ahogamiento")
    if ruta and os.path.isfile(ruta):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            _SONIDO_AHOGAMIENTO = pygame.mixer.Sound(ruta)
        except Exception:
            _SONIDO_AHOGAMIENTO = None
    return _SONIDO_AHOGAMIENTO


def reproducir_sonido_ahogamiento():
    """
    Reproduce en bucle el efecto de sonido de ahogamiento ('sonidos/ahogamiento/ahogamiento.mp3')
    en un canal de audio dedicado cuando algún personaje entra en estado crítico de oxígeno (< 25%).
    - Si el sonido ya está activo y reproduciéndose, NO reinicia ni superpone canales.
    - Aplica estrictamente el volumen configurado para efectos de sonido.
    - Garantiza que ambos personajes utilicen el mismo canal limpio sin cacofonías ni desincronización.
    """
    global _CANAL_AHOGAMIENTO
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        snd = _obtener_sonido_ahogamiento()
        if snd is None:
            return

        vol_e = max(0.0, min(1.0, VOLUMEN_EFECTOS / 100.0))

        # Asignar canal dedicado (canal 7 si está disponible, o reservar canal libre)
        if _CANAL_AHOGAMIENTO is None:
            try:
                _CANAL_AHOGAMIENTO = pygame.mixer.Channel(7)
            except Exception:
                _CANAL_AHOGAMIENTO = pygame.mixer.find_channel(force=True)

        if _CANAL_AHOGAMIENTO is not None:
            _CANAL_AHOGAMIENTO.set_volume(vol_e)
        if _CANAL_UI_BOTONES is not None:
            _CANAL_UI_BOTONES.set_volume(vol_e)
            if not _CANAL_AHOGAMIENTO.get_busy():
                _CANAL_AHOGAMIENTO.play(snd, loops=-1)
    except Exception:
        pass


def detener_sonido_ahogamiento():
    """
    Detiene de inmediato el efecto de sonido de ahogamiento cuando los personajes
    recuperan el oxígeno, mueren, reinician o cambian de nivel o pantalla.
    """
    global _CANAL_AHOGAMIENTO
    try:
        if _CANAL_AHOGAMIENTO is not None and _CANAL_AHOGAMIENTO.get_busy():
            _CANAL_AHOGAMIENTO.stop()
    except Exception:
        pass


def pausar_musica():
    """Pausa temporalmente la música actual."""
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.pause()
    except Exception:
        pass


def reanudar_musica():
    """Reanuda la música que fue pausada."""
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.unpause()
    except Exception:
        pass


def obtener_musica_actual():
    """Retorna una tupla (tipo_pista, ruta_archivo) de la música activa."""
    return _pista_activa_tipo, _archivo_musica_actual


# ==============================================================================
# GESTIÓN Y CONTROL DE VOLUMEN
# ==============================================================================
def obtener_volumen():
    """Retorna el volumen maestro actual como entero entre 0 y 100."""
    return _volumen


def obtener_volumen_musica():
    """Retorna el volumen de la música (0 a 100)."""
    return VOLUMEN_MUSICA


def obtener_volumen_efectos():
    """Retorna el volumen de efectos de sonido (0 a 100)."""
    return VOLUMEN_EFECTOS


def _aplicar_volumen_audio():
    """Aplica el nivel de volumen al subsistema de música y canales de Pygame."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        vol_m = max(0.0, min(1.0, VOLUMEN_MUSICA / 100.0))
        pygame.mixer.music.set_volume(vol_m)

        vol_e = max(0.0, min(1.0, VOLUMEN_EFECTOS / 100.0))
        num_canales = pygame.mixer.get_num_channels()
        for i in range(num_canales):
            pygame.mixer.Channel(i).set_volume(vol_e)
        if _CANAL_AHOGAMIENTO is not None:
            _CANAL_AHOGAMIENTO.set_volume(vol_e)
        if _CANAL_UI_BOTONES is not None:
            _CANAL_UI_BOTONES.set_volume(vol_e)
    except Exception:
        pass


def fijar_volumen_musica(nuevo_volumen):
    """Establece el volumen de la música (0 a 100) y lo persiste."""
    global VOLUMEN_MUSICA
    VOLUMEN_MUSICA = max(0, min(100, int(nuevo_volumen)))
    _aplicar_volumen_audio()
    _guardar_configuracion_disco()


def fijar_volumen_efectos(nuevo_volumen):
    """Establece el volumen de los efectos de sonido (0 a 100) y lo persiste."""
    global VOLUMEN_EFECTOS
    VOLUMEN_EFECTOS = max(0, min(100, int(nuevo_volumen)))
    _aplicar_volumen_audio()
    _guardar_configuracion_disco()


def fijar_volumen(nuevo_volumen):
    """Establece el volumen maestro (0 a 100), sincroniza música y efectos, y persiste el ajuste."""
    global _volumen, VOLUMEN_MUSICA, VOLUMEN_EFECTOS
    _volumen = max(0, min(100, int(nuevo_volumen)))
    VOLUMEN_MUSICA = _volumen
    VOLUMEN_EFECTOS = _volumen
    _aplicar_volumen_audio()
    _guardar_configuracion_disco()


def cambiar_volumen(delta):
    """Incrementa o decrementa el volumen por un valor delta y emite retroalimentación sonora."""
    fijar_volumen(_volumen + delta)
    reproducir_beep_volumen()


_SND_BEEP_VOLUMEN = None


def reproducir_beep_volumen():
    """Genera y reproduce un tono suave de retroalimentación para escuchar el cambio de volumen."""
    global _SND_BEEP_VOLUMEN
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        vol_float = max(0.0, min(1.0, VOLUMEN_EFECTOS / 100.0))
        if vol_float <= 0.001:
            return

        if _SND_BEEP_VOLUMEN is None:
            sample_rate = 22050
            duration = 0.05
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(n_samples):
                val = int(32767 * 0.28 * math.sin(2 * math.pi * 520 * i / sample_rate))
                buf += struct.pack('<h', val)
            _SND_BEEP_VOLUMEN = pygame.mixer.Sound(buffer=bytes(buf))

        _SND_BEEP_VOLUMEN.set_volume(vol_float)
        _SND_BEEP_VOLUMEN.play()
    except Exception:
        pass


_CACHE_SONIDOS_UI = {}
_CANAL_UI_BOTONES = None
_ULTIMO_TICK_UI = 0
_ULTIMO_TIPO_UI = None


def reproducir_sonido_ui(tipo="menu"):
    """
    Reproduce un efecto de sonido retro/pixel art suave, sutil y agradable para la interfaz y el juego.
    Diferenciado por sección con identidades sonoras propias:
    1. Menú y opciones: 'menu' (blip suave), 'tab' (pestañas), 'select' (selección), 'pagina' (paginación).
    2. Dentro de los niveles: 'nivel_boton' o 'mecanismo' (pulsación táctil de placa/interruptor).
    3. Ventanas y confirmaciones: 'ventana_aceptar', 'ventana_cancelar', 'ventana_volver',
       'ventana_reintentar', 'ventana_reiniciar'.
    4. Partidas guardadas: 'partida_cargar', 'partida_gestionar', 'partida_borrar', 'partida_nueva'.

    Garantiza:
    - Sonido único por pulsación, sin repetición mientras se mantenga apretado.
    - Canal de audio dedicado con control anti-saturación para que no se superpongan de forma molesta.
    - Volumen bajo/moderado calibrado con VOLUMEN_EFECTOS, estéticamente armonioso con el pixel art.
    """
    global _CANAL_UI_BOTONES, _ULTIMO_TICK_UI, _ULTIMO_TIPO_UI
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        vol_float = max(0.0, min(1.0, VOLUMEN_EFECTOS / 100.0))
        if vol_float <= 0.001:
            return

        now = pygame.time.get_ticks()
        # Cooldown breve anti-rebote (mínimo 30 ms para el mismo tipo)
        if tipo == _ULTIMO_TIPO_UI and (now - _ULTIMO_TICK_UI) < 30:
            return
        _ULTIMO_TICK_UI = now
        _ULTIMO_TIPO_UI = tipo

        if tipo not in _CACHE_SONIDOS_UI:
            mix_info = pygame.mixer.get_init()
            freq = mix_info[0] if mix_info else 44100
            channels = mix_info[2] if mix_info else 2
            dur = 0.05
            n = int(freq * dur)
            buf = bytearray()

            for i in range(n):
                p = i / float(n)
                # Envolvente suave con ataque de 3 ms y caída libre de clics
                env = max(0.0, 1.0 - (p ** 0.8))
                if i < int(freq * 0.003):
                    env *= (i / (freq * 0.003))

                # --- 1. MENÚ Y OPCIONES ---
                if tipo in ("menu", "ui", "click"):
                    f = 540 + 140 * p
                    amp = 0.19
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo == "tab":
                    f = 480 if p < 0.5 else 640
                    amp = 0.18
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo == "select":
                    f = 600 + 240 * p
                    amp = 0.18
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo == "pagina":
                    f = 360
                    amp = 0.16
                    v = math.sin(2 * math.pi * f * i / freq)

                # --- 2. DENTRO DE LOS NIVELES (BOTONES DE PRESIÓN Y MECANISMOS) ---
                elif tipo in ("nivel_boton", "mecanismo", "presion"):
                    f = 220 * (1.0 - 0.3 * p)
                    amp = 0.22
                    v = 0.7 * math.sin(2 * math.pi * f * i / freq) + 0.3 * math.sin(2 * math.pi * (f * 0.5) * i / freq)

                # --- 3. VENTANAS Y CONFIRMACIONES ---
                elif tipo in ("ventana_aceptar", "confirmar"):
                    f = 587 if p < 0.45 else 880
                    amp = 0.20
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo in ("ventana_cancelar", "cerrar"):
                    f = 440 if p < 0.45 else 330
                    amp = 0.18
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo == "ventana_volver":
                    f = 420 - 60 * p
                    amp = 0.18
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo in ("ventana_reintentar", "ventana_reiniciar"):
                    f = 480 + 140 * math.sin(math.pi * p)
                    amp = 0.20
                    v = math.sin(2 * math.pi * f * i / freq)

                # --- 4. PARTIDAS GUARDADAS ---
                elif tipo == "partida_cargar":
                    f = 620 + 164 * p
                    amp = 0.20
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo == "partida_gestionar":
                    f = 500
                    amp = 0.19
                    v = 0.8 * math.sin(2 * math.pi * f * i / freq) + 0.2 * math.sin(2 * math.pi * f * 2 * i / freq)
                elif tipo == "partida_borrar":
                    f = 260 - 85 * p
                    amp = 0.20
                    v = math.sin(2 * math.pi * f * i / freq)
                elif tipo == "partida_nueva":
                    f = 523 if p < 0.33 else (659 if p < 0.66 else 784)
                    amp = 0.20
                    v = math.sin(2 * math.pi * f * i / freq)

                # Fallback neutro
                else:
                    f = 520
                    amp = 0.18
                    v = math.sin(2 * math.pi * f * i / freq)

                val = int(32767 * amp * env * v)
                val = max(-32767, min(32767, val))
                buf += struct.pack('<h', val) * channels

            _CACHE_SONIDOS_UI[tipo] = pygame.mixer.Sound(buffer=bytes(buf))

        snd = _CACHE_SONIDOS_UI[tipo]
        snd.set_volume(vol_float)

        # Usar un canal reservado para la UI para evitar superposiciones discordantes
        if _CANAL_UI_BOTONES is None:
            try:
                _CANAL_UI_BOTONES = pygame.mixer.Channel(6)
            except Exception:
                _CANAL_UI_BOTONES = pygame.mixer.find_channel(force=True)

        if _CANAL_UI_BOTONES is not None:
            _CANAL_UI_BOTONES.play(snd)
        else:
            snd.play()
    except Exception:
        pass



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

    # Dimensiones y posición del panel central (compacto y elegante, cerrado únicamente mediante la X)
    W_MODAL = 520
    H_MODAL = 310
    rect_modal = pygame.Rect((ancho_p - W_MODAL) // 2, (alto_p - H_MODAL) // 2, W_MODAL, H_MODAL)

    # Botón de cerrar (X) en la esquina superior derecha del panel (con proporción nativa 0.8496 y centrado en cabecera)
    W_X_CFG, H_X_CFG = 29, 34
    rect_x_header = pygame.Rect(rect_modal.right - W_X_CFG - 14, rect_modal.top + (54 - H_X_CFG) // 2, W_X_CFG, H_X_CFG)

    # Cargar sprites para los botones de volumen con proporción nativa 0.8496 (870x1024 -> 42x50)
    W_BTN_VOL, H_BTN_VOL = 42, 50
    def _asegurar_orientacion_derecha(surf):
        if surf is None:
            return None
        w, h = surf.get_size()
        # Muestrear densidad de píxeles del dibujo del icono (marrón oscuro sobre botón naranja)
        px_izq = sum(1 for y in range(h) for x in range(0, w // 2) if surf.get_at((x, y))[0] < 200 and surf.get_at((x, y))[1] < 120 and surf.get_at((x, y))[3] > 0)
        px_der = sum(1 for y in range(h) for x in range(w // 2, w) if surf.get_at((x, y))[0] < 200 and surf.get_at((x, y))[1] < 120 and surf.get_at((x, y))[3] > 0)
        # Si la mayor concentración está en la derecha (parlante mirando a la izquierda), invertir horizontalmente
        if px_der > px_izq:
            return pygame.transform.flip(surf, True, False)
        return surf

    def _cargar_scaled(nombre, w, h):
        return cargar_boton_escalado(nombre, w, h)

    # Botón Bajar Volumen (Parlante con X / Silencio orientado a la derecha)
    spr_menos_norm = _asegurar_orientacion_derecha(_cargar_scaled("HUD/boton-bajar-volumen.png", W_BTN_VOL, H_BTN_VOL) or _cargar_scaled("boton-bajar-volumen.png", W_BTN_VOL, H_BTN_VOL))
    spr_menos_semi = _asegurar_orientacion_derecha(_cargar_scaled("HUD/boton-bajar-volumen-semiapretado.png", W_BTN_VOL, H_BTN_VOL) or _cargar_scaled("boton-bajar-volumen-semiapretado.png", W_BTN_VOL, H_BTN_VOL))
    spr_menos_apr = _asegurar_orientacion_derecha(_cargar_scaled("HUD/boton-bajar-volumen-apretado.png", W_BTN_VOL, H_BTN_VOL) or _cargar_scaled("boton-bajar-volumen-apretado.png", W_BTN_VOL, H_BTN_VOL))
    spr_menos_hov = aclarar_boton(spr_menos_norm)

    # Botón Subir Volumen (Parlante con ondas sonoras orientado a la derecha)
    spr_mas_norm = _asegurar_orientacion_derecha(_cargar_scaled("HUD/boton-subir-volumen.png", W_BTN_VOL, H_BTN_VOL) or _cargar_scaled("boton-subir-volumen.png", W_BTN_VOL, H_BTN_VOL))
    spr_mas_semi = _asegurar_orientacion_derecha(_cargar_scaled("HUD/boton-subir-volumen-semiapretado.png", W_BTN_VOL, H_BTN_VOL) or _cargar_scaled("boton-subir-volumen-semiapretado.png", W_BTN_VOL, H_BTN_VOL))
    spr_mas_apr = _asegurar_orientacion_derecha(_cargar_scaled("HUD/boton-subir-volumen-apretado.png", W_BTN_VOL, H_BTN_VOL) or _cargar_scaled("boton-subir-volumen-apretado.png", W_BTN_VOL, H_BTN_VOL))
    spr_mas_hov = aclarar_boton(spr_mas_norm)

    # Botón X de cabecera
    spr_x_norm = _cargar_scaled("HUD/boton-x.png", W_X_CFG, H_X_CFG) or _cargar_scaled("boton-x.png", W_X_CFG, H_X_CFG)
    spr_x_semi = _cargar_scaled("HUD/boton-x-semiapretado.png", W_X_CFG, H_X_CFG) or _cargar_scaled("boton-x-semiapretado.png", W_X_CFG, H_X_CFG)
    spr_x_apr = _cargar_scaled("HUD/boton-x-apretado.png", W_X_CFG, H_X_CFG) or _cargar_scaled("boton-x-apretado.png", W_X_CFG, H_X_CFG)
    spr_x_hov = aclarar_boton(spr_x_norm)

    # Layout interno del panel (simétrico y centrado)
    w_btn_lang, h_btn_lang, gap_lang = 136, 42, 14
    total_w_content = 3 * w_btn_lang + 2 * gap_lang  # 436 px
    x_margen_contenido = rect_modal.left + (W_MODAL - total_w_content) // 2  # 42 px de margen izquierdo y derecho

    # Sección 1: Volumen (alineada exactamente a 436 px con botones proporcionales y centros unificados)
    gap_vol = 14
    w_barra = total_w_content - (2 * W_BTN_VOL + 2 * gap_vol)  # 324 px
    h_barra = 36

    y_seccion_vol = rect_modal.top + 72
    cy_vol_fila = rect_modal.top + 122  # Centro vertical compartido de la fila de volumen

    rect_btn_menos = pygame.Rect(x_margen_contenido, 0, W_BTN_VOL, H_BTN_VOL)
    rect_btn_menos.centery = cy_vol_fila

    rect_barra_bg = pygame.Rect(rect_btn_menos.right + gap_vol, 0, w_barra, h_barra)
    rect_barra_bg.centery = cy_vol_fila

    rect_btn_mas = pygame.Rect(rect_barra_bg.right + gap_vol, 0, W_BTN_VOL, H_BTN_VOL)
    rect_btn_mas.centery = cy_vol_fila

    # Sección 2: Idioma
    y_seccion_idioma = rect_modal.top + 172
    y_btns_lang = y_seccion_idioma + 30
    rect_lang_es = pygame.Rect(x_margen_contenido, y_btns_lang, w_btn_lang, h_btn_lang)
    rect_lang_en = pygame.Rect(rect_lang_es.right + gap_lang, y_btns_lang, w_btn_lang, h_btn_lang)
    rect_lang_zh = pygame.Rect(rect_lang_en.right + gap_lang, y_btns_lang, w_btn_lang, h_btn_lang)

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
                        pulsado = animar_pulsacion_boton(pantalla, rect_x_header, spr_x_semi, spr_x_apr, (46, 52, 68), spr_x_norm, tipo_sonido="ventana_cancelar")
                    if pulsado:
                        modal_activo = False
                        break

                # 2. Clic en botón Bajar Volumen
                elif rect_btn_menos.collidepoint(evento.pos):
                    if spr_menos_semi and spr_menos_apr:
                        if animar_pulsacion_boton(pantalla, rect_btn_menos, spr_menos_semi, spr_menos_apr, (36, 40, 52), spr_menos_norm, tipo_sonido="menu"):
                            cambiar_volumen(-10)
                    else:
                        cambiar_volumen(-10)

                # 3. Clic en botón Subir Volumen
                elif rect_btn_mas.collidepoint(evento.pos):
                    if spr_mas_semi and spr_mas_apr:
                        if animar_pulsacion_boton(pantalla, rect_btn_mas, spr_mas_semi, spr_mas_apr, (36, 40, 52), spr_mas_norm, tipo_sonido="menu"):
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
                    reproducir_sonido_ui("select")
                elif rect_lang_en.collidepoint(evento.pos):
                    cambiar_idioma("en")
                    reproducir_sonido_ui("select")
                elif rect_lang_zh.collidepoint(evento.pos):
                    cambiar_idioma("zh")
                    reproducir_sonido_ui("select")

                # 6. Si hace clic fuera del modal, cerramos mediante la X/fondo
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

        # Título de Cabecera (con soporte tipográfico completo para acentos y ajuste seguro)
        rect_tit_h = pygame.Rect(rect_modal.left + 50, rect_header.top + 8, rect_modal.width - 100, 38)
        dibujar_texto_en_rect(pantalla, t("configuracion"), rect_tit_h, categoria="subtitulo", tamano=22, color=(255, 235, 195), negrita=True, padding=4)

        mouse_down = pygame.mouse.get_pressed()[0]

        # Dibujar botón X de cabecera
        hov_x = rect_x_header.collidepoint(pos_mouse)
        spr_x_dib = spr_x_hov if (hov_x and spr_x_hov) else spr_x_norm
        if spr_x_dib:
            pantalla.blit(spr_x_dib, rect_x_header)

        # --- SECCIÓN 1: VOLUMEN ---
        fuente_seccion = obtener_fuente_subtitulo(20, negrita=True, tamano_fallback=20)
        t_vol_lbl = fuente_seccion.render(t("volumen"), True, (255, 195, 140))
        pantalla.blit(t_vol_lbl, (x_margen_contenido, y_seccion_vol))

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

        # Texto de porcentaje centrado sobre la barra (categoría contador, ampliado 75 % a tamaño 42)
        fuente_pct = obtener_fuente_contador(42, negrita=True, tamano_fallback=42)
        txt_porcentaje = f"{_volumen} %"
        t_pct = fuente_pct.render(txt_porcentaje, True, (255, 255, 255))
        rect_pct = t_pct.get_rect(center=rect_barra_bg.center)

        # Ajuste de centrado óptico vertical por caja de glifos de la fuente
        try:
            mask_pct = pygame.mask.from_surface(t_pct)
            bbs = mask_pct.get_bounding_rects()
            if bbs:
                ubb = bbs[0].unionall(bbs[1:])
                top_offset = (ubb.top - (t_pct.get_height() - ubb.bottom)) // 2
                rect_pct.y -= top_offset
        except Exception:
            pass

        # Contorno oscuro nítido y reforzado para máxima legibilidad sobre cualquier nivel de volumen y color
        t_pct_borde = fuente_pct.render(txt_porcentaje, True, (18, 20, 26))
        for dx_p, dy_p in [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2),
        ]:
            pantalla.blit(t_pct_borde, rect_pct.move(dx_p, dy_p))
        pantalla.blit(t_pct, rect_pct)

        # Botón Subir Volumen
        hov_mas = rect_btn_mas.collidepoint(pos_mouse)
        spr_p_dib = spr_mas_hov if (hov_mas and spr_mas_hov) else spr_mas_norm
        if spr_p_dib:
            pantalla.blit(spr_p_dib, rect_btn_mas)

        # --- SECCIÓN 2: SELECTOR DE IDIOMA ---
        t_lang_lbl = fuente_seccion.render(t("idioma"), True, (255, 195, 140))
        pantalla.blit(t_lang_lbl, (x_margen_contenido, y_seccion_idioma))

        opciones_idioma = [
            ("es", "ESPAÑOL", rect_lang_es),
            ("en", "ENGLISH", rect_lang_en),
            ("zh", "简体中文", rect_lang_zh),
        ]

        for cod, etiqueta, rect_btn in opciones_idioma:
            es_activo = (_idioma == cod)
            hov_btn = rect_btn.collidepoint(pos_mouse)

            base_sprite = "mundos/boton-cargar.png" if es_activo else "mundos/boton-volver.png"
            col_txt = (26, 83, 29) if es_activo else (60, 45, 30)

            btn_surf = generar_boton_con_texto(
                sprite_base=base_sprite,
                w=rect_btn.w,
                h=rect_btn.h,
                texto=etiqueta,
                color_texto=col_txt,
                tamano_fuente=18,
                idioma=cod
            )

            if hov_btn and btn_surf:
                btn_surf = aclarar_boton(btn_surf)

            if btn_surf:
                pantalla.blit(btn_surf, rect_btn)

        pygame.display.flip()
        reloj.tick(60)

    # Al salir del modal, restauramos el frame original del juego inmediatamente
    pantalla.blit(fondo_juego, (0, 0))
    pygame.display.flip()
