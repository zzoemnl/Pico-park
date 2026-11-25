"""
Constantes, iconos y utilidades compartidas por las pantallas del menú.
"""
import pygame
import os
import random
from configuracion import t
from fuentes import dibujar_texto_en_rect
from rutas import ruta_recurso
from sprites import cargar_accesorio, obtener_accesorios_disponibles


# Estados de la máquina de navegación de menús
ESTADO_MENU_PRINCIPAL = "principal"


ESTADO_MODO_JUEGO = "modo_juego"


ESTADO_LISTA_PARTIDAS = "lista_partidas"


ESTADO_CONFIGURACION = "configuracion"


ESTADO_CREDITOS = "creditos"


ESTADO_PERSONAJES = "personajes"


ESTADO_SELECCION_MUNDO = "seleccion_mundo"


ESTADO_SELECCION_NIVEL = "seleccion_nivel"


PERSONAJES_DISPONIBLES = [
    # Tonos Neutros y Tierra
    {"nombre": "Blanco", "color": (232, 232, 232)},
    {"nombre": "Gris", "color": (154, 154, 154)},
    {"nombre": "Negro", "color": (89, 89, 89)},
    {"nombre": "Marron", "color": (206, 136, 111)},
    # Tonos Cálidos
    {"nombre": "Rojo", "color": (255, 137, 134)},
    {"nombre": "Rosa", "color": (255, 150, 240)},
    {"nombre": "Naranja", "color": (255, 160, 100)},
    {"nombre": "Amarillo", "color": (255, 244, 123)},
    # Tonos Verdes
    {"nombre": "Verde", "color": (157, 255, 124)},
    {"nombre": "Verde oscuro", "color": (105, 205, 75)},
    # Tonos Fríos / Azules / Violetas
    {"nombre": "Celeste", "color": (124, 231, 255)},
    {"nombre": "Azul", "color": (36, 166, 247)},
    {"nombre": "Violeta", "color": (161, 123, 255)},
]


NOMBRES_COLORES_MOSTRAR = {
    "Blanco": "Blanco",
    "Gris": "Gris claro",
    "Negro": "Gris oscuro",
    "Marron": "Marrón",
    "Rojo": "Rojo",
    "Rosa": "Rosa",
    "Naranja": "Naranja",
    "Amarillo": "Amarillo",
    "Verde": "Verde claro",
    "Verde oscuro": "Verde",
    "Celeste": "Celeste",
    "Azul": "Azul",
    "Violeta": "Violeta",
}


FILAS_COLORES_SELECCION = [
    [0, 1, 2, 3],       # Fila 1 (Neutros y Tierra): Blanco, Gris claro, Gris oscuro, Marrón
    [4, 5, 6, 7, 8],    # Fila 2 (Cálidos y Verde claro): Rojo, Rosa, Naranja, Amarillo, Verde claro
    [9, 10, 11, 12],    # Fila 3 (Verdes y Fríos): Verde, Celeste, Azul, Violeta
]


def _obtener_nombre_color_visible(nombre_interno, idioma=None):
    nom_base = NOMBRES_COLORES_MOSTRAR.get(nombre_interno, nombre_interno)
    trad = t(nom_base.lower(), idioma) if idioma else t(nom_base.lower())
    return trad if trad else nom_base


_cache_iconos_instrucciones = {}


def _obtener_icono_instruccion(tipo: str, max_w: int = 48, max_h: int = 46) -> "pygame.Surface | None":
    """Carga y escala proporcionalmente los sprites originales del juego para la guía de mundos."""
    key = (tipo, max_w, max_h)
    if key in _cache_iconos_instrucciones:
        return _cache_iconos_instrucciones[key]

    ruta = None
    if tipo == "llave":
        ruta = ruta_recurso("Sprites", "Objetos", "llave.png")
    elif tipo == "caja":
        ruta = ruta_recurso("Sprites", "Objetos", "caja.png")
    elif tipo == "buceo":
        ruta = ruta_recurso("Sprites", "Accesorios", "buceo_m3.png")

    if not ruta or not os.path.isfile(ruta):
        return None

    try:
        surf = pygame.image.load(ruta).convert_alpha()
        w, h = surf.get_size()
        scale = min(max_w / float(w), max_h / float(h))
        nw = max(1, int(round(w * scale)))
        nh = max(1, int(round(h * scale)))
        try:
            res = pygame.transform.smoothscale(surf, (nw, nh))
        except Exception:
            res = pygame.transform.scale(surf, (nw, nh))
        _cache_iconos_instrucciones[key] = res
        return res
    except Exception:
        return None


_cache_previews_accesorios = {}


def _obtener_preview_accesorio_tarjeta(acc_id: str) -> "pygame.Surface | None":
    """
    Obtiene la miniatura oficial del accesorio para la cuadrícula de selección.
    Reutiliza directamente el sprite original de imagen existente en el proyecto,
    manteniendo sus proporciones exactas sin dibujos inventados ni alteraciones por código.
    """
    if not acc_id or acc_id == "Ninguno":
        return None
    if acc_id in _cache_previews_accesorios:
        return _cache_previews_accesorios[acc_id]

    surf = cargar_accesorio(acc_id)
    if not surf:
        return None

    w, h = surf.get_size()
    max_w, max_h = 48, 38
    if w > max_w or h > max_h:
        ratio = min(max_w / float(w), max_h / float(h))
        nw = max(1, int(round(w * ratio)))
        nh = max(1, int(round(h * ratio)))
        res = pygame.transform.scale(surf, (nw, nh))
    else:
        res = surf

    _cache_previews_accesorios[acc_id] = res
    return res


def _dibujar_icono_tecla(surf, texto, rect, activo=False, tamano_fuente=14):
    col_bg = (255, 252, 245) if not activo else (255, 242, 210)
    col_sombra = (150, 140, 135)
    col_borde = (75, 60, 50)
    col_txt = (30, 20, 15)
    r_som = pygame.Rect(rect.left, rect.top + 3, rect.width, rect.height - 3)
    pygame.draw.rect(surf, col_sombra, r_som, border_radius=6)
    r_key = pygame.Rect(rect.left, rect.top, rect.width, rect.height - 4)
    pygame.draw.rect(surf, col_bg, r_key, border_radius=6)
    pygame.draw.rect(surf, col_borde, r_key, 2, border_radius=6)
    dibujar_texto_en_rect(surf, texto, r_key, categoria="boton", tamano=tamano_fuente, color=col_txt, negrita=True, padding=2)


def _dibujar_icono_candado(s, cx, cy, abierto=False):
    """Dibuja un pequeño candado pixel art (7x9 px) para fichas de diario."""
    col_arco = (90, 70, 55)
    col_cuerpo = (212, 160, 55)
    col_luz = (248, 210, 110)
    col_borde = (65, 45, 30)
    col_ojo = (50, 35, 20)

    # Arco
    offset_abierto = -2 if abierto else 0
    for dy in range(4):
        for dx in range(-2, 3):
            if abs(dx) == 2 or dy == 0:
                px, py = cx + dx + offset_abierto, cy - 3 + dy
                s.set_at((px, py), col_arco)

    # Cuerpo
    for dy in range(5):
        for dx in range(-3, 4):
            px, py = cx + dx, cy + 1 + dy
            if abs(dx) == 3 or dy == 0 or dy == 4:
                s.set_at((px, py), col_borde)
            elif dy == 1 and dx < 2:
                s.set_at((px, py), col_luz)
            else:
                s.set_at((px, py), col_cuerpo)

    # Ojo de cerradura
    s.set_at((cx, cy + 3), col_ojo)


def _dibujar_icono_calendario(s, cx, cy):
    """Dibuja un icono de calendario pixel art nítido (11x11 px)."""
    col_papel = (252, 248, 238)
    col_rojo = (210, 65, 55)
    col_borde = (110, 80, 55)
    col_linea = (150, 125, 95)
    # Anillas superiores
    s.set_at((cx - 3, cy - 5), col_borde)
    s.set_at((cx + 3, cy - 5), col_borde)
    # Cuerpo
    for dy in range(-4, 6):
        for dx in range(-5, 6):
            if dx in (-5, 5) or dy in (-4, 5):
                s.set_at((cx + dx, cy + dy), col_borde)
            elif dy <= -2:
                s.set_at((cx + dx, cy + dy), col_rojo)
            else:
                s.set_at((cx + dx, cy + dy), col_papel)
    # Puntos de días
    for px, py in [(-2, 0), (0, 0), (2, 0), (-2, 2), (0, 2), (2, 2)]:
        s.set_at((cx + px, cy + py), col_linea)


def _dibujar_icono_reloj(s, cx, cy):
    """Dibuja un reloj pixel art nítido (11x11 px)."""
    col_cuerpo = (252, 248, 238)
    col_borde = (95, 75, 55)
    col_agujas = (55, 38, 24)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            d2 = dx * dx + dy * dy
            if 15 <= d2 <= 26:
                s.set_at((cx + dx, cy + dy), col_borde)
            elif d2 < 15:
                s.set_at((cx + dx, cy + dy), col_cuerpo)
    # Agujas
    s.set_at((cx, cy), col_agujas)
    s.set_at((cx, cy - 1), col_agujas)
    s.set_at((cx, cy - 2), col_agujas)
    s.set_at((cx + 1, cy), col_agujas)
    s.set_at((cx + 2, cy), col_agujas)


def _dibujar_icono_trofeo(s, cx, cy):
    """Dibuja un trofeo pixel art nítido (11x12 px) para niveles completados."""
    col_oro = (245, 195, 45)
    col_luz = (255, 240, 140)
    col_borde = (120, 80, 20)
    col_base = (145, 95, 35)
    # Copa
    for dy in range(-5, 0):
        w = 4 - abs(dy + 3) // 2
        for dx in range(-w, w + 1):
            col = col_luz if (dx < 0 and dy < -2) else col_oro
            s.set_at((cx + dx, cy + dy), col)
    # Asas
    for y_asa in [-4, -3, -2]:
        s.set_at((cx - 4, cy + y_asa), col_borde)
        s.set_at((cx + 4, cy + y_asa), col_borde)
    # Borde superior copa
    for dx in range(-3, 4):
        s.set_at((cx + dx, cy - 6), col_borde)
    # Tallo
    s.set_at((cx, cy), col_borde)
    s.set_at((cx, cy + 1), col_base)
    # Base
    for dx in range(-3, 4):
        s.set_at((cx + dx, cy + 2), col_base)
        s.set_at((cx + dx, cy + 3), col_borde)


def _dibujar_icono_estrella_nivel(s, cx, cy):
    """Dibuja una gema / estrella pixel art nítida (11x11 px)."""
    col_gema = (235, 130, 35)
    col_luz = (255, 220, 110)
    col_borde = (130, 65, 15)
    for dy in range(-5, 6):
        w = 5 - abs(dy)
        for dx in range(-w, w + 1):
            if abs(dx) == w or abs(dy) == 5:
                s.set_at((cx + dx, cy + dy), col_borde)
            elif dy <= 0 and dx <= 0:
                s.set_at((cx + dx, cy + dy), col_luz)
            else:
                s.set_at((cx + dx, cy + dy), col_gema)


def _seleccionar_accesorios_sesion_aleatorios(color_p1="Celeste", color_p2="Violeta"):
    """
    Selecciona aleatoriamente al iniciar una nueva sesión del juego los accesorios que llevan los personajes:
    - Utiliza exclusivamente los accesorios existentes con sprites reales en el proyecto.
    - La selección se realiza una sola vez al iniciar la sesión.
    - Los dos personajes tienen combinaciones diferentes sin accesorios duplicados.
    - Respeta la disponibilidad de accesorios para cada personaje.
    """
    disp_p1 = [a["id"] for a in obtener_accesorios_disponibles(color_p1) if a["id"] != "Ninguno"]
    disp_p2 = [a["id"] for a in obtener_accesorios_disponibles(color_p2) if a["id"] != "Ninguno"]

    if not disp_p1 or not disp_p2:
        return "Ninguno", "Ninguno"

    acc_p1 = random.choice(disp_p1)
    candidatos_p2 = [a for a in disp_p2 if a != acc_p1]
    acc_p2 = random.choice(candidatos_p2) if candidatos_p2 else random.choice(disp_p2)
    return acc_p1, acc_p2
