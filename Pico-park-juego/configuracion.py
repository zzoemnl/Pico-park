"""
Módulo de Configuración, Audio e Internacionalización (i18n) - Pico Park.

Gestiona:
1. Control de volumen del juego (0% a 100%) con retroalimentación sonora y control de canales de Pygame.
2. Selector de idioma global (Español, English, 简体中文) sin reiniciar la partida.
3. Pestaña modal superpuesta de Configuración que conserva el estado y progreso del juego.
"""

import os
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
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "jefe1"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos", "ahogamiento"),
    os.path.join(DIRECTORIO_RAIZ, "sonidos"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menú"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "menu"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "mundo1"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "mundo2"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "mundo3"),
    os.path.join(DIRECTORIO_ACTUAL, "sonidos", "jefe1"),
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
_musica_menu_sesion = None
_modo_musica_menu = "aleatorio"  # "aleatorio", "caillou", "christmas"
_CANAL_AHOGAMIENTO = None
_SONIDO_AHOGAMIENTO = None


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
    "jefe_pista": {
        "es": "¡Pisen los dos botones al mismo tiempo!",
        "en": "Step on both buttons at the same time!",
        "zh": "同时踩下两个按钮！",
    },
    "jefe_pista_ruinas": {
        "es": "Cuando quede aturdido, hagan una torre y toquen la runa de su pecho",
        "en": "When it is stunned, stack up and touch the rune on its chest",
        "zh": "它眩晕时，叠罗汉触碰它胸口的符文",
    },
    "jefe_pista_kraken": {
        "es": "¡Métanse los dos dentro del orbe de luz y aguanten!",
        "en": "Both of you get inside the light orb and hold on!",
        "zh": "两人一起进入光球并坚持住！",
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
    "en_proceso": {
        "es": "EN PROCESO",
        "en": "IN PROGRESS",
        "zh": "开发中",
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
    "controles": {
        "es": "CONTROLES",
        "en": "CONTROLS",
        "zh": "操作控制",
    },
    "instrucciones": {
        "es": "INSTRUCCIONES",
        "en": "INSTRUCTIONS",
        "zh": "游戏说明",
    },
    "sub_opciones": {
        "es": "Configuración general, controles y guía de aventura",
        "en": "General settings, controls and adventure guide",
        "zh": "通用设置、操作控制与冒险指南",
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
    "gris claro": {"es": "Gris claro", "en": "Light Gray", "zh": "浅灰色"},
    "gris oscuro": {"es": "Gris oscuro", "en": "Dark Gray", "zh": "深灰色"},
    "negro": {"es": "Gris oscuro", "en": "Dark Gray", "zh": "深灰色"},
    "marron": {"es": "Marrón", "en": "Brown", "zh": "棕色"},
    "rojo": {"es": "Rojo", "en": "Red", "zh": "红色"},
    "rosa": {"es": "Rosa", "en": "Pink", "zh": "粉色"},
    "naranja": {"es": "Naranja", "en": "Orange", "zh": "橙色"},
    "amarillo": {"es": "Amarillo", "en": "Yellow", "zh": "黄色"},
    "verde": {"es": "Verde", "en": "Green", "zh": "绿色"},
    "verde claro": {"es": "Verde claro", "en": "Light Green", "zh": "浅绿色"},
    "verde oscuro": {"es": "Verde", "en": "Green", "zh": "绿色"},
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
    "gorro azul": {"es": "Gorro Azul", "en": "Blue Beanie", "zh": "蓝帽子"},
    "gorro_azul": {"es": "Gorro Azul", "en": "Blue Beanie", "zh": "蓝帽子"},
    "gorro celeste": {"es": "Gorro Celeste", "en": "Cyan Beanie", "zh": "青色帽子"},
    "gorro_celeste": {"es": "Gorro Celeste", "en": "Cyan Beanie", "zh": "青色帽子"},
    "duende": {"es": "Duende", "en": "Elf Hat", "zh": "精灵帽"},
    "papá noel": {"es": "Papá Noel", "en": "Santa", "zh": "圣诞老人"},
    "papa noel": {"es": "Papá Noel", "en": "Santa", "zh": "圣诞老人"},
    "papa_noel": {"es": "Papá Noel", "en": "Santa", "zh": "圣诞老人"},
    "ángel": {"es": "Ángel", "en": "Angel", "zh": "天使"},
    "angel": {"es": "Ángel", "en": "Angel", "zh": "天使"},
    "hoja": {"es": "Hoja", "en": "Sprout", "zh": "小树苗"},
    "rulo": {"es": "Rulo", "en": "Curl", "zh": "卷发"},
    "popó": {"es": "Popó", "en": "Poop", "zh": "便便"},
    "popo": {"es": "Popó", "en": "Poop", "zh": "便便"},
    "caca": {"es": "Popó", "en": "Poop", "zh": "便便"},
    "pelo arcoíris": {"es": "Pelo Arcoíris", "en": "Rainbow Hair", "zh": "彩虹假发"},
    "pelo arcoiris": {"es": "Pelo Arcoíris", "en": "Rainbow Hair", "zh": "彩虹假发"},
    "arcoíris": {"es": "Pelo Arcoíris", "en": "Rainbow Hair", "zh": "彩虹假发"},
    "arcoiris": {"es": "Pelo Arcoíris", "en": "Rainbow Hair", "zh": "彩虹假发"},
    "gorro con ratón": {"es": "Gorro con Ratón", "en": "Mouse Hat", "zh": "老鼠帽"},
    "gorro con raton": {"es": "Gorro con Ratón", "en": "Mouse Hat", "zh": "老鼠帽"},
    "chucky": {"es": "Chucky", "en": "Chucky", "zh": "恰吉"},
    "orejas de conejo": {"es": "Orejas de Conejo", "en": "Rabbit Ears", "zh": "兔耳朵"},
    "among us": {"es": "Among Us", "en": "Among Us", "zh": "Among Us"},
    "among_us": {"es": "Among Us", "en": "Among Us", "zh": "Among Us"},
    "argentina": {"es": "Argentina", "en": "Argentina", "zh": "阿根廷"},
    "bigote": {"es": "Bigote", "en": "Mustache", "zh": "胡子"},
    "diablo": {"es": "Diablo", "en": "Devil", "zh": "恶魔"},
    "elegante": {"es": "Elegante", "en": "Fancy", "zh": "绅士"},
    "exe": {"es": "EXE", "en": "EXE", "zh": "EXE"},
    "gorra urbana dorada": {"es": "Gorra urbana dorada", "en": "Gold Urban Cap", "zh": "金色潮帽"},
    "gorra_urbana_dorada": {"es": "Gorra urbana dorada", "en": "Gold Urban Cap", "zh": "金色潮帽"},
    "gorra urbana plateada": {"es": "Gorra urbana plateada", "en": "Silver Urban Cap", "zh": "银色潮帽"},
    "gorra_urbana_plateada": {"es": "Gorra urbana plateada", "en": "Silver Urban Cap", "zh": "银色潮帽"},
    "kenny": {"es": "Kenny", "en": "Kenny", "zh": "肯尼"},
    "kyle": {"es": "Kyle", "en": "Kyle", "zh": "凯尔"},
    "moño bi": {"es": "Moño Bi", "en": "Bi Bow", "zh": "双性恋结"},
    "mono bi": {"es": "Moño Bi", "en": "Bi Bow", "zh": "双性恋结"},
    "moño_bi": {"es": "Moño Bi", "en": "Bi Bow", "zh": "双性恋结"},
    "mono_bi": {"es": "Moño Bi", "en": "Bi Bow", "zh": "双性恋结"},
    "moño g": {"es": "Moño G", "en": "Gay Bow", "zh": "彩虹结"},
    "mono g": {"es": "Moño G", "en": "Gay Bow", "zh": "彩虹结"},
    "moño_g": {"es": "Moño G", "en": "Gay Bow", "zh": "彩虹结"},
    "mono_g": {"es": "Moño G", "en": "Gay Bow", "zh": "彩虹结"},
    "moño l": {"es": "Moño L", "en": "Lesbian Bow", "zh": "女同结"},
    "mono l": {"es": "Moño L", "en": "Lesbian Bow", "zh": "女同结"},
    "moño_l": {"es": "Moño L", "en": "Lesbian Bow", "zh": "女同结"},
    "mono_l": {"es": "Moño L", "en": "Lesbian Bow", "zh": "女同结"},
    "moño trans": {"es": "Moño trans", "en": "Trans Bow", "zh": "跨性别结"},
    "mono trans": {"es": "Moño trans", "en": "Trans Bow", "zh": "跨性别结"},
    "moño_trans": {"es": "Moño trans", "en": "Trans Bow", "zh": "跨性别结"},
    "mono_trans": {"es": "Moño trans", "en": "Trans Bow", "zh": "跨性别结"},
    "nerd": {"es": "Nerd", "en": "Nerd", "zh": "书呆子"},
    "tatoo": {"es": "Tatoo", "en": "Tattoo", "zh": "纹身"},
    "tattoo": {"es": "Tatoo", "en": "Tattoo", "zh": "纹身"},
    "minion": {"es": "Minion", "en": "Minion", "zh": "小黄人"},
    "pou": {"es": "Pou", "en": "Pou", "zh": "外星宠物Pou"},
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
    "ajustes_generales": {
        "es": "AJUSTES GENERALES DEL JUEGO",
        "en": "GENERAL GAME SETTINGS",
        "zh": "游戏通用设置",
    },
    "controles_teclado": {
        "es": "CONTROLES Y TECLADO DE LOS JUGADORES",
        "en": "PLAYER CONTROLS & KEYBOARD",
        "zh": "玩家操作与键盘按键",
    },
    "guia_juego": {
        "es": "GUÍA DE JUEGO Y MECÁNICAS DE LOS MUNDOS",
        "en": "GAME GUIDE & WORLD MECHANICS",
        "zh": "游戏指南与关卡机制",
    },
    "volumen_musica_y_sonido": {
        "es": "VOLUMEN DE MÚSICA Y SONIDO",
        "en": "MUSIC & SOUND VOLUME",
        "zh": "音乐与音效音量",
    },
    "seleccion_idioma": {
        "es": "SELECCIÓN DE IDIOMA / LANGUAGE",
        "en": "LANGUAGE SELECTION",
        "zh": "语言选择",
    },
    "musica_menu_titulo": {
        "es": "MÚSICA DEL MENÚ",
        "en": "MENU MUSIC",
        "zh": "菜单音乐",
    },
    "modo_aleatorio": {
        "es": "ALEATORIO",
        "en": "RANDOM",
        "zh": "随机",
    },
    "desc_aleatorio": {
        "es": "Mezcla\n(Caillou / Christmas)",
        "en": "Mix\n(Caillou / Christmas)",
        "zh": "随机混合\n(卡由 / 圣诞)",
    },
    "modo_caillou": {
        "es": "CAILLOU",
        "en": "CAILLOU",
        "zh": "卡由",
    },
    "desc_caillou": {
        "es": "Tema de Caillou\n[Versión 8-bit]",
        "en": "Caillou Theme\n[8-bit Tribute]",
        "zh": "卡由主题曲\n[8位像素音乐]",
    },
    "modo_christmas": {
        "es": "CHRISTMAS",
        "en": "CHRISTMAS",
        "zh": "圣诞 (CHRISTMAS)",
    },
    "desc_christmas": {
        "es": "Música Navideña\n[menú.mp3]",
        "en": "Christmas Music\n[menú.mp3]",
        "zh": "圣诞节日音乐\n[menú.mp3]",
    },
    "cambios_guardados_auto": {
        "es": "Los cambios se guardan y sincronizan automáticamente.",
        "en": "Changes are saved and synced automatically.",
        "zh": "更改将自动保存并同步。",
    },
    "flechas_direccion": {
        "es": "FLECHAS DE DIRECCIÓN",
        "en": "ARROW KEYS",
        "zh": "方向键",
    },
    "accion_moverse": {
        "es": "Moverse",
        "en": "Move",
        "zh": "移动",
    },
    "desc_moverse": {
        "es": "Izquierda / Derecha",
        "en": "Left / Right",
        "zh": "向左 / 向右",
    },
    "accion_saltar": {
        "es": "Saltar",
        "en": "Jump",
        "zh": "跳跃",
    },
    "desc_saltar": {
        "es": "Salto normal y rebote",
        "en": "Normal jump and bounce",
        "zh": "普通跳跃与弹跳",
    },
    "accion_nadar": {
        "es": "Nadar (Agua)",
        "en": "Swim (Water)",
        "zh": "游泳（水下）",
    },
    "desc_nadar_p1": {
        "es": "W: Nadar arriba / S: Sumergirse",
        "en": "W: Swim up / S: Dive down",
        "zh": "W: 向上游 / S: 向下潜",
    },
    "desc_nadar_p2": {
        "es": "↑: Nadar arriba / ↓: Sumergirse",
        "en": "↑: Swim up / ↓: Dive down",
        "zh": "↑: 向上游 / ↓: 向下潜",
    },
    "accion_empujar": {
        "es": "Empujar",
        "en": "Push",
        "zh": "推动",
    },
    "desc_empujar": {
        "es": "Caminar de frente contra cajas",
        "en": "Walk forward against boxes",
        "zh": "迎面走向箱子以推动",
    },
    "accion_linterna": {
        "es": "Linterna (M3)",
        "en": "Flashlight (W3)",
        "zh": "手电筒（第3世界）",
    },
    "desc_linterna": {
        "es": "Encender / Apagar en oscuridad",
        "en": "Turn on / off in dark areas",
        "zh": "在黑暗洞穴中开启/关闭",
    },
    "reiniciar_nivel_act": {
        "es": "Reiniciar nivel actual",
        "en": "Restart current level",
        "zh": "重新开始当前关卡",
    },
    "pausa_volver_menu": {
        "es": "Pausa / Volver al menú",
        "en": "Pause / Return to menu",
        "zh": "暂停 / 返回主菜单",
    },
    "inst_tit_1": {
        "es": "1. OBJETIVO Y LLAVE DORADA",
        "en": "1. GOAL & GOLDEN KEY",
        "zh": "1. 目标与金色钥匙",
    },
    "inst_1_1": {
        "es": "• Cooperen en equipo para guiar a ambos personajes.",
        "en": "• Cooperate as a team to guide both characters.",
        "zh": "• 团队协作引导两名角色前进。",
    },
    "inst_1_2": {
        "es": "• Encuentren y recojan la LLAVE DORADA del nivel.",
        "en": "• Find and collect the level's GOLDEN KEY.",
        "zh": "• 寻找并拾取关卡中的金色钥匙。",
    },
    "inst_1_3": {
        "es": "• La llave abre el candado de la PUERTA DE SALIDA.",
        "en": "• The key unlocks the EXIT DOOR lock.",
        "zh": "• 钥匙可解开终点大门的门锁。",
    },
    "inst_1_4": {
        "es": "• ¡Ambos jugadores deben entrar para ganar!",
        "en": "• Both players must enter together to win!",
        "zh": "• 两名玩家必须全部进入方可通关！",
    },
    "inst_tit_2": {
        "es": "2. CAJAS Y BOTONES DE PRESIÓN",
        "en": "2. CRATES & PRESSURE BUTTONS",
        "zh": "2. 木箱与压力开关",
    },
    "inst_2_1": {
        "es": "• Empujen cajas juntos caminando hacia ellas.",
        "en": "• Push crates together by walking into them.",
        "zh": "• 迎面走向木箱合力将其推动。",
    },
    "inst_2_2": {
        "es": "• Las cajas sirven como escalón o contrapeso.",
        "en": "• Crates serve as step-ups or counterweights.",
        "zh": "• 木箱可用作垫脚台阶或重力配重。",
    },
    "inst_2_3": {
        "es": "• Pisen los BOTONES del suelo para abrir compuertas.",
        "en": "• Step on floor BUTTONS to open gates.",
        "zh": "• 踩下地面开关以开启机关闸门。",
    },
    "inst_2_4": {
        "es": "• Algunos botones requieren peso continuo encima.",
        "en": "• Some buttons require continuous weight on them.",
        "zh": "• 部分开关需要持续保持重压。",
    },
    "inst_tit_3": {
        "es": "3. MUNDOS 1 Y 2: TRABAJO EN EQUIPO",
        "en": "3. WORLDS 1 & 2: TEAMWORK",
        "zh": "3. 世界1与2：团队协作",
    },
    "inst_3_1": {
        "es": "• Mundo 1: Suban uno encima de otro para llegar alto.",
        "en": "• World 1: Climb on each other to reach heights.",
        "zh": "• 世界1：叠罗汉踩在队友头上跳上高处。",
    },
    "inst_3_2": {
        "es": "• Mundo 2: ¡Están unidos por una SOGA resistente!",
        "en": "• World 2: Connected by a sturdy ROPE!",
        "zh": "• 世界2：两名玩家由坚韧绳索相连！",
    },
    "inst_3_3": {
        "es": "• La soga tiene distancia máxima y transmite tirones.",
        "en": "• The rope has max length and pulls each other.",
        "zh": "• 绳索有长度上限并会相互拉拽牵引。",
    },
    "inst_3_4": {
        "es": "• Si un jugador cae, tirará de su compañero.",
        "en": "• If one player falls, they pull their partner.",
        "zh": "• 一人跌落将会把同伴一同拽下。",
    },
    "inst_tit_4": {
        "es": "4. MUNDO 3: AVENTURA SUBMARINA",
        "en": "4. WORLD 3: UNDERWATER ADVENTURE",
        "zh": "4. 世界3：水下奇妙冒险",
    },
    "inst_4_1": {
        "es": "• Zonas sumergidas con físicas de natación y buceo.",
        "en": "• Underwater zones with swim and dive physics.",
        "zh": "• 水下区域具有真实游泳与潜水浮力。",
    },
    "inst_4_2": {
        "es": "• Atentos al nivel de OXÍGENO y burbujas de aire.",
        "en": "• Keep an eye on OXYGEN level and bubbles.",
        "zh": "• 密切留意氧气存量并及时吸取气泡。",
    },
    "inst_4_3": {
        "es": "• Las CORRIENTES marinas arrastran con fuerza.",
        "en": "• Ocean CURRENTS push with strong forces.",
        "zh": "• 强劲的水下暗流会产生推动与阻力。",
    },
    "inst_4_4": {
        "es": "• Usen LINTERNAS en las cavernas oscuras (E / L).",
        "en": "• Use FLASHLIGHTS in dark caves (E / L).",
        "zh": "• 在漆黑洞穴中开启手电筒照明 (E / L)。",
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
        with open(RUTA_CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
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
