"""
Módulo de Configuración, Audio e Internacionalización (i18n) - Pico Park.

Gestiona:
1. Control de volumen del juego (0% a 100%) con retroalimentación sonora y control de canales de Pygame.
2. Selector de idioma global (Español, English, 简体中文) sin reiniciar la partida.
3. Pestaña modal superpuesta de Configuración que conserva el estado y progreso del juego.
"""

import os
import json
import math
import struct
import pygame

from sprites import (
    cargar_boton,
    cargar_boton_escalado,
    animar_pulsacion_boton,
    aclarar_boton,
    generar_boton_con_texto,
    generar_marco_boton,
)
from fuentes import (
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_botones,
    obtener_fuente_pequena,
    obtener_fuente_contador,
    obtener_fuente_dialogos,
    limpiar_cache_fuentes,
    dibujar_texto_en_rect,
)

# ==============================================================================
# VARIABLES CENTRALIZADAS DE AUDIO Y MÚSICA
# ==============================================================================
# Configura aquí las rutas o nombres de archivo de cada pista de música y el volumen.
# Puedes colocar los archivos en 'assets/audio/' o 'Sprites/Audio/' (.mp3, .ogg, .wav).
# ==============================================================================
AUDIO_MENU = "menu.mp3"          # Música del menú principal y pantallas de navegación
AUDIO_MUNDO_1 = "mundo1.mp3"     # Música del Mundo 1
AUDIO_MUNDO_2 = "mundo2.mp3"     # Música del Mundo 2
AUDIO_MUNDO_3 = "mundo3.mp3"     # Música del Mundo 3

VOLUMEN_MUSICA = 70             # Volumen general de la música (0 a 100)
VOLUMEN_EFECTOS = 70            # Volumen general de efectos de sonido (0 a 100)

_volumen = 70                   # Volumen maestro (sincronizado con música y efectos)
_idioma = "es"                  # Idioma actual: "es" | "en" | "zh"

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_CONFIG_JSON = os.path.join(DIRECTORIO_ACTUAL, "configuracion.json")

CARPETAS_AUDIO = [
    os.path.join(DIRECTORIO_ACTUAL, "..", "assets", "audio"),
    os.path.join(DIRECTORIO_ACTUAL, "assets", "audio"),
    os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Audio"),
    os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Audio"),
    os.path.join(DIRECTORIO_ACTUAL, "..", "assets"),
    os.path.join(DIRECTORIO_ACTUAL, "assets"),
]

# Estado interno del reproductor de música
_pista_activa_tipo = None
_archivo_musica_actual = None


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
        "zh": "关卡选择",
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
    "opciones": {
        "es": "OPCIONES",
        "en": "SETTINGS",
        "zh": "设置",
    },
    "modo_juego": {
        "es": "MODO DE JUEGO",
        "en": "GAME MODE",
        "zh": "游戏模式",
    },
    "subtitulo_modo": {
        "es": "Selecciona cómo deseas comenzar tu aventura",
        "en": "Choose how you want to start your adventure",
        "zh": "选择你开始冒险的方式",
    },
    "continuar": {
        "es": "CONTINUAR",
        "en": "CONTINUE",
        "zh": "继续游戏",
    },
    "sub_continuar": {
        "es": "Cargar partida guardada y ver tus niveles alcanzados",
        "en": "Load saved game and view level progress",
        "zh": "加载保存的存档并查看关卡进度",
    },
    "nueva_partida": {
        "es": "NUEVA PARTIDA",
        "en": "NEW GAME",
        "zh": "新建游戏",
    },
    "sub_nueva_partida": {
        "es": "Reiniciar y comenzar desde el Mundo 1 - Nivel 1",
        "en": "Restart and begin from World 1 - Level 1",
        "zh": "重新开始，从世界 1 - 关卡 1 开始",
    },
    "partidas_guardadas": {
        "es": "PARTIDAS GUARDADAS",
        "en": "SAVED GAMES",
        "zh": "保存的游戏",
    },
    "partida": {
        "es": "Partida",
        "en": "Game",
        "zh": "游戏",
    },
    "sub_partidas": {
        "es": "Registro de expediciones y progreso de aventura",
        "en": "Expedition record and adventure progress",
        "zh": "探险记录与冒险进度",
    },
    "todos_desbloqueados": {
        "es": "Todos los niveles desbloqueados",
        "en": "All levels unlocked",
        "zh": "所有关卡已解锁",
    },
    "completados": {
        "es": "completados",
        "en": "completed",
        "zh": "已完成",
    },
    "fecha": {
        "es": "Fecha",
        "en": "Date",
        "zh": "日期",
    },
    "hora": {
        "es": "Hora",
        "en": "Time",
        "zh": "时间",
    },
    "cargar": {
        "es": "CARGAR",
        "en": "LOAD",
        "zh": "加载",
    },
    "gestionar": {
        "es": "GESTIONAR",
        "en": "MANAGE",
        "zh": "管理",
    },
    "borrar": {
        "es": "BORRAR",
        "en": "DELETE",
        "zh": "删除",
    },
    "no_partidas": {
        "es": "No se encontraron registros de expedición",
        "en": "No expedition records found",
        "zh": "未找到探险记录",
    },
    "comenzar_historia": {
        "es": "Comenzá una nueva partida para escribir tu historia en este diario.",
        "en": "Start a new game to write your story in this journal.",
        "zh": "开始新游戏以在此日记中谱写你的故事。",
    },
    "comenzar_aventura": {
        "es": "COMENZAR AVENTURA",
        "en": "START ADVENTURE",
        "zh": "开始冒险",
    },
    "entrada_pagina": {
        "es": "Entrada página {0} de {1}",
        "en": "Journal page {0} of {1}",
        "zh": "档案页码 {0} / {1}",
    },
    "personalizacion_personajes": {
        "es": "PERSONALIZACIÓN DE PERSONAJES",
        "en": "CHARACTER CUSTOMIZATION",
        "zh": "角色定制",
    },
    "sub_personalizacion": {
        "es": "Personaliza el color y los accesorios de cada personaje",
        "en": "Customize the color and accessories of each character",
        "zh": "自定义每个角色的颜色和配饰",
    },
    "colores": {
        "es": "COLORES",
        "en": "COLORS",
        "zh": "颜色",
    },
    "accesorios": {
        "es": "ACCESORIOS",
        "en": "ACCESSORIES",
        "zh": "配饰",
    },
    "jugador": {
        "es": "JUGADOR",
        "en": "PLAYER",
        "zh": "玩家",
    },
    "colores_disponibles": {
        "es": "COLORES DISPONIBLES",
        "en": "AVAILABLE COLORS",
        "zh": "可用颜色",
    },
    "accesorios_disponibles": {
        "es": "ACCESORIOS DISPONIBLES",
        "en": "AVAILABLE ACCESSORIES",
        "zh": "可用配饰",
    },
    "administrar_perfil": {
        "es": "ADMINISTRAR PERFIL",
        "en": "MANAGE PROFILE",
        "zh": "管理档案",
    },
    "eliminar_perfil": {
        "es": "ELIMINAR PERFIL",
        "en": "DELETE PROFILE",
        "zh": "删除档案",
    },
    "confirmar": {
        "es": "CONFIRMAR",
        "en": "CONFIRM",
        "zh": "确认",
    },
    "cambiar_nombre": {
        "es": "CAMBIAR NOMBRE",
        "en": "CHANGE NAME",
        "zh": "更改名称",
    },
    "cambiar_quitar_clave": {
        "es": "CAMBIAR / QUITAR CONTRASEÑA",
        "en": "CHANGE / REMOVE PASSWORD",
        "zh": "更改 / 移除密码",
    },
    "agregar_clave": {
        "es": "AGREGAR CONTRASEÑA",
        "en": "ADD PASSWORD",
        "zh": "添加密码",
    },
    "perfil": {
        "es": "Perfil",
        "en": "Profile",
        "zh": "档案",
    },
    "estado_protegido": {
        "es": "Estado: Protegido con contraseña",
        "en": "Status: Password protected",
        "zh": "状态：密码保护",
    },
    "estado_sin_clave": {
        "es": "Estado: Sin contraseña",
        "en": "Status: No password",
        "zh": "状态：无密码",
    },
    "seguro_eliminar_perfil": {
        "es": "¿Seguro que deseas eliminar este perfil y su partida?",
        "en": "Are you sure you want to delete this profile and its save?",
        "zh": "确定要删除此档案及其存档吗？",
    },
    "aviso_borrado_progreso": {
        "es": "Se borrará todo su progreso y no se podrá recuperar.",
        "en": "All progress will be deleted and cannot be recovered.",
        "zh": "所有进度都将被删除且无法恢复。",
    },
    "borrar_perfil": {
        "es": "BORRAR PERFIL",
        "en": "DELETE PROFILE",
        "zh": "删除档案",
    },
    "partida_existente": {
        "es": "PARTIDA EXISTENTE",
        "en": "EXISTING GAME",
        "zh": "已有存档",
    },
    "ya_existe_partida_con_nombre": {
        "es": "Ya existe una partida guardada con el nombre",
        "en": "A saved game already exists with the name",
        "zh": "已存在同名存档",
    },
    "elegir_otro_o_sobrescribir": {
        "es": "¿Deseas elegir otro nombre o sobrescribir la partida existente?",
        "en": "Do you want to choose another name or overwrite the existing game?",
        "zh": "要选择其他名称还是覆盖现有存档？",
    },
    "otro_nombre": {
        "es": "OTRO NOMBRE",
        "en": "ANOTHER NAME",
        "zh": "其他名称",
    },
    "sobrescribir": {
        "es": "SOBRESCRIBIR",
        "en": "OVERWRITE",
        "zh": "覆盖",
    },
    "ingresa_nombre_partida": {
        "es": "Ingresa un nombre para tu partida:",
        "en": "Enter a name for your game:",
        "zh": "输入存档名称：",
    },
    "contrasena_opcional": {
        "es": "CONTRASEÑA (OPCIONAL)",
        "en": "PASSWORD (OPTIONAL)",
        "zh": "密码（可选）",
    },
    "sub_contrasena_opcional": {
        "es": "Establece una contraseña o deja vacío si no deseas protegerla:",
        "en": "Set a password or leave blank if not needed:",
        "zh": "设置密码，如不需要保护请留空：",
    },
    "campo_no_vacio": {
        "es": "El campo no puede estar vacío.",
        "en": "This field cannot be empty.",
        "zh": "该字段不能为空。",
    },
    "guardar_en": {
        "es": "GUARDAR EN",
        "en": "SAVE TO",
        "zh": "保存到",
    },
    "crear_nueva_partida": {
        "es": "CREAR NUEVA PARTIDA",
        "en": "CREATE NEW GAME",
        "zh": "创建新存档",
    },
    "elige_partida_o_crea": {
        "es": "Elige una partida para actualizar o crea una nueva:",
        "en": "Choose a game to update or create a new one:",
        "zh": "选择要更新的存档或创建新存档：",
    },
    "niveles_completados": {
        "es": "Niveles completados",
        "en": "Completed levels",
        "zh": "已完成关卡",
    },
    "guardado": {
        "es": "Guardado",
        "en": "Saved",
        "zh": "保存时间",
    },
    "partida_actual": {
        "es": "Partida actual",
        "en": "Current game",
        "zh": "当前存档",
    },
    "volver_al_menu": {
        "es": "VOLVER AL MENÚ",
        "en": "BACK TO MENU",
        "zh": "返回主菜单",
    },
    "blanco": {"es": "Blanco", "en": "White", "zh": "白色"},
    "gris": {"es": "Gris", "en": "Gray", "zh": "灰色"},
    "negro": {"es": "Negro", "en": "Black", "zh": "黑色"},
    "marron": {"es": "Marrón", "en": "Brown", "zh": "棕色"},
    "rojo": {"es": "Rojo", "en": "Red", "zh": "红色"},
    "rosa": {"es": "Rosa", "en": "Pink", "zh": "粉色"},
    "naranja": {"es": "Naranja", "en": "Orange", "zh": "橙色"},
    "amarillo": {"es": "Amarillo", "en": "Yellow", "zh": "黄色"},
    "verde": {"es": "Verde", "en": "Green", "zh": "绿色"},
    "verde oscuro": {"es": "Verde oscuro", "en": "Dark Green", "zh": "深绿色"},
    "celeste": {"es": "Celeste", "en": "Sky Blue", "zh": "天蓝色"},
    "azul": {"es": "Azul", "en": "Blue", "zh": "蓝色"},
    "violeta": {"es": "Violeta", "en": "Purple", "zh": "紫色"},
    "ninguno": {"es": "Ninguno", "en": "None", "zh": "无"},
    "corona": {"es": "Corona", "en": "Crown", "zh": "皇冠"},
    "gorro": {"es": "Gorro", "en": "Beanie", "zh": "毛线帽"},
    "anteojos": {"es": "Anteojos", "en": "Glasses", "zh": "眼镜"},
    "moño": {"es": "Moño", "en": "Bowtie", "zh": "蝴蝶结"},
    "sombrero": {"es": "Sombrero", "en": "Hat", "zh": "礼帽"},
    "marrón": {"es": "Marrón", "en": "Brown", "zh": "棕色"},
    "mono": {"es": "Moño", "en": "Bowtie", "zh": "蝴蝶结"},
    "cambiar_atuendos": {
        "es": "CAMBIAR ATUENDOS",
        "en": "CHANGE OUTFITS",
        "zh": "更换装扮",
    },
    "sub_modificaste_personajes": {
        "es": "Modificaste los personajes antes de continuar «{0}».",
        "en": "You modified characters before continuing «{0}».",
        "zh": "继续«{0}»前你修改了角色装扮。",
    },
    "pregunta_mantener_o_cambiar": {
        "es": "¿Deseas mantener los atuendos guardados o aplicar los nuevos?",
        "en": "Do you want to keep saved outfits or apply new ones?",
        "zh": "你想保留已保存的装扮还是应用新装扮？",
    },
    "atuendos_guardados": {
        "es": "ATUENDOS GUARDADOS",
        "en": "SAVED OUTFITS",
        "zh": "已保存装扮",
    },
    "nuevos_atuendos": {
        "es": "NUEVOS ATUENDOS",
        "en": "NEW OUTFITS",
        "zh": "新装扮",
    },
    "mantener_guardados": {
        "es": "MANTENER GUARDADOS",
        "en": "KEEP SAVED",
        "zh": "保留已保存",
    },
    "jugador_1": {
        "es": "Jugador 1",
        "en": "Player 1",
        "zh": "玩家 1",
    },
    "jugador_2": {
        "es": "Jugador 2",
        "en": "Player 2",
        "zh": "玩家 2",
    },
    "accesorio_label": {
        "es": "Accesorio",
        "en": "Accessory",
        "zh": "配饰",
    },
    "sin_accesorio": {
        "es": "Sin accesorio",
        "en": "No accessory",
        "zh": "无配饰",
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
        }
        with open(RUTA_CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
    except Exception:
        pass


def _cargar_configuracion_disco():
    """Carga los ajustes guardados de volumen si existen en disco. Al iniciar el juego siempre debe estar en español."""
    global _volumen, VOLUMEN_MUSICA, VOLUMEN_EFECTOS, _idioma
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
        except Exception:
            pass
    _idioma = "es"


# Carga inicial de ajustes al importar el módulo
_cargar_configuracion_disco()


# ==============================================================================
# GESTIÓN Y REPRODUCCIÓN DE MÚSICA Y AUDIO
# ==============================================================================
def _resolver_ruta_audio(pista_o_nombre):
    """
    Localiza el archivo de audio comprobando rutas absolutas, relativas y carpetas
    assets/audio y Sprites/Audio. Soporta extensiones .mp3, .ogg, .wav.
    """
    if not pista_o_nombre:
        return None

    if os.path.isabs(pista_o_nombre) and os.path.isfile(pista_o_nombre):
        return os.path.normpath(pista_o_nombre)

    base = os.path.basename(pista_o_nombre)
    nombres_a_buscar = [base]
    nombre_raiz, ext = os.path.splitext(base)
    if not ext:
        for posible_ext in [".mp3", ".ogg", ".wav"]:
            nombres_a_buscar.append(nombre_raiz + posible_ext)

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
    Reproduce la pista musical indicada ('menu', 'mundo_1', 'mundo_2', 'mundo_3') en bucle continuo.
    - Si la misma pista ya está sonando, NO se reinicia (conserva la continuidad).
    - Navegar entre pantallas de menú o cambiar de nivel dentro del mismo mundo no corta la música.
    - Si el archivo de audio aún no existe, el juego continúa normalmente sin música ni errores repetidos.
    - Garantiza que nunca se reproduzcan dos pistas simultáneas.
    """
    global _pista_activa_tipo, _archivo_musica_actual

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        return

    # Normalizar identificador del tipo de pista
    tipo_str = str(tipo).lower().strip()
    if tipo_str in ("menu", "principal", "navegacion"):
        tipo_normalizado = "menu"
        pista_config = AUDIO_MENU
    elif tipo_str in ("mundo_1", "mundo1", "1"):
        tipo_normalizado = "mundo_1"
        pista_config = AUDIO_MUNDO_1
    elif tipo_str in ("mundo_2", "mundo2", "2"):
        tipo_normalizado = "mundo_2"
        pista_config = AUDIO_MUNDO_2
    elif tipo_str in ("mundo_3", "mundo3", "3"):
        tipo_normalizado = "mundo_3"
        pista_config = AUDIO_MUNDO_3
    else:
        tipo_normalizado = tipo_str
        pista_config = tipo

    # Si ya está sonando esta misma pista y no se solicita forzar reinicio, conservar reproducción
    if tipo_normalizado == _pista_activa_tipo and not forzar:
        return

    ruta_audio = _resolver_ruta_audio(pista_config)
    _pista_activa_tipo = tipo_normalizado

    if not ruta_audio:
        # Si no existe archivo para esta pista, detener cualquier música previa y continuar en silencio
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        _archivo_musica_actual = None
        return

    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(ruta_audio)
        vol_float = max(0.0, min(1.0, VOLUMEN_MUSICA / 100.0))
        pygame.mixer.music.set_volume(vol_float)
        pygame.mixer.music.play(-1)
        _archivo_musica_actual = ruta_audio
    except Exception:
        _archivo_musica_actual = None


def detener_musica():
    """Detiene la música actual de forma segura."""
    global _pista_activa_tipo, _archivo_musica_actual
    _pista_activa_tipo = None
    _archivo_musica_actual = None
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
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


def reproducir_beep_volumen():
    """Genera y reproduce un tono suave de retroalimentación para escuchar el cambio de volumen."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        vol_float = max(0.0, min(1.0, VOLUMEN_EFECTOS / 100.0))
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
