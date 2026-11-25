import os
import sys
import copy
import random
import pygame

from rutas import ruta_recurso
from ventana import crear_ventana

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from sprites import (
    escalar_cacheado,
    ANCHO,
    ALTO,
    FPS,
    cargar_sprites,
    cargar_boton_escalado,
    precargar_botones_comunes,
    animar_pulsacion_boton,
    aclarar_boton, 
    generar_boton_con_texto,
    renderizar_texto_pixamuse,
    obtener_accesorios_disponibles,
    cargar_accesorio,
    dibujar_accesorio_en_personaje,
)
from pantalla import iniciar_mundo
from configuracion import (
    t, mostrar_pestana_configuracion, reproducir_musica, detener_musica,
    obtener_idioma, cambiar_idioma, obtener_volumen, fijar_volumen,
    cambiar_volumen, reproducir_beep_volumen, reproducir_sonido_ui,
    seleccionar_musica_menu_aleatoria,
    obtener_modo_musica_menu, fijar_modo_musica_menu,
)
from menu_niveles import (
    dibujar_menu_niveles,
    obtener_geometria_menu,
    obtener_mecanicas_nivel,  
    dibujar_mascota_gato,
    COLORES_TABS,
)
from personajes_menu import GestorPersonajesMenu
from guardado import (
    NIVELES_POR_MUNDO,
    TOTAL_NIVELES,
    TOTAL_NIVELES_NORMALES,
    TOTAL_NIVELES_ADMIN,
    crear_desbloqueados_inicial,
    cargar_partidas,
    guardar_partida,
    eliminar_partida,
    mostrar_dialogo_guardar_salir,
    mostrar_dialogo_confirmar_borrado,
    mostrar_dialogo_confirmar_atuendos,
    hay_progreso_sin_guardar,
    calcular_niveles_completados,
    pedir_password_modal,
    modal_administrar_perfil,
    flujo_crear_nueva_partida,
    obtener_nombre_partida_visible,
    es_partida_admin,
)
from fuentes import (
    contiene_caracteres_cjk,
    obtener_fuente_para_texto,
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_botones,
    obtener_fuente_pequena,
    obtener_fuente_cjk,
    obtener_fuente_contador,
    obtener_fuente_dialogos,
    obtener_fuente_decorativa,
    TAMANO_TITULO,
    TAMANO_TITULO_GRANDE,
    TAMANO_TITULO_MODAL,
    TAMANO_DECORATIVA,
    TAMANO_SUBTITULO,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO,
    TAMANO_TEXTO_GRANDE,
    TAMANO_BOTON,
    TAMANO_BOTONES,
    TAMANO_BOTON_GRANDE,
    TAMANO_PEQUENA,
    TAMANO_ITEM_TITULO,
    TAMANO_BADGE,
    TAMANO_CARD,
    TAMANO_CONTADOR,
    TAMANO_DIALOGOS,
    ajustar_tamano_fuente,
    dibujar_texto_en_rect,
)

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


# ==============================================================================
# FONDOS PIXEL ART  –  Modo de Juego  &  Partidas Guardadas
# ==============================================================================
import math as _math
import random as _random

_fondo_modo_juego_cache: "pygame.Surface | None" = None
_fondo_partidas_cache: "pygame.Surface | None" = None


def _generar_fondo_modo_juego(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    """
    Paisaje panorámico de aventura al atardecer en pixel art para «MODO DE JUEGO».
    Renderizado en 640x360 y escalado 2x a 1280x720 para auténtica estética 16-bit.
    - Cielo de atardecer con bandas degradadas (violeta, coral, ámbar y dorado) con dithering retro.
    - Montañas alpinas orgánicas en segundo plano con nieve iluminada y sombras profundas.
    - Lago sereno que refleja el resplandor del cielo, el sol y las montañas.
    - Árboles altos concentrados en los laterales para despejar la interfaz central.
    - Terreno en primer plano con nieve texturada y rocas.
    """
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. Cielo de atardecer con bandas y dithering escalonado
    bandas_cielo = [
        (0,   42,  (34,  16,  48)),   # Violeta crepúsculo profundo
        (42,  84,  (58,  24,  66)),   # Ciruela / mora oscuro
        (84,  125, (115, 42,  76)),   # Magenta / vino atardecer
        (125, 162, (185, 68,  62)),   # Coral cálido
        (162, 196, (228, 115, 52)),   # Naranja ámbar vibrante
        (196, 224, (248, 168, 68)),   # Amarillo dorado
        (224, 250, (255, 218, 120)),  # Resplandor dorado de horizonte
    ]
    for y1, y2, col in bandas_cielo:
        pygame.draw.rect(surf, col, (0, y1, W, y2 - y1))

    # Dithering retro estilo 16-bit entre bandas
    for i in range(len(bandas_cielo) - 1):
        yt = bandas_cielo[i][1]
        c_up = bandas_cielo[i][2]
        c_dn = bandas_cielo[i + 1][2]
        for dy in range(-3, 4):
            y = yt + dy
            if 0 <= y < H:
                for x in range(W):
                    if dy == -3 and (x % 4 == 0 and y % 4 == 0):
                        surf.set_at((x, y), c_dn)
                    elif dy == -2 and (x + y) % 4 == 0:
                        surf.set_at((x, y), c_dn)
                    elif dy == -1 and (x % 2 == 0 and y % 2 == 0):
                        surf.set_at((x, y), c_dn)
                    elif dy == 0 and (x + y) % 2 == 0:
                        surf.set_at((x, y), c_dn)
                    elif dy == 1 and (x % 2 == 0 and y % 2 == 0):
                        surf.set_at((x, y), c_up)
                    elif dy == 2 and (x + y) % 4 == 0:
                        surf.set_at((x, y), c_up)
                    elif dy == 3 and (x % 4 == 0 and y % 4 == 0):
                        surf.set_at((x, y), c_up)

    # 2. Primeras estrellas del anochecer en la parte superior
    rnd_stars = _random.Random(999)
    for _ in range(28):
        sx = rnd_stars.randint(40, W - 40)
        sy = rnd_stars.randint(4, 52)
        surf.set_at((sx, sy), (255, 240, 220))
        if rnd_stars.random() < 0.25:
            surf.set_at((sx + 1, sy), (230, 195, 225))
            surf.set_at((sx, sy + 1), (230, 195, 225))

    # 3. Resplandor del sol en el horizonte
    sun_x, sun_y = 320, 206
    for r in range(54, 0, -2):
        prog = 1.0 - (r / 54)
        col_sun = (
            min(255, int(250 + 5 * prog)),
            min(255, int(185 + 70 * prog)),
            min(255, int(85 + 140 * prog))
        )
        for dy in range(-r, r + 1):
            w_line = int(_math.sqrt(max(0, r * r - dy * dy)))
            y_pix = sun_y + dy
            if 0 <= y_pix < 232:
                for x_pix in range(sun_x - w_line, sun_x + w_line + 1):
                    if r > 30:
                        if (x_pix + y_pix) % 2 == 0:
                            surf.set_at((x_pix, y_pix), col_sun)
                    else:
                        surf.set_at((x_pix, y_pix), col_sun)

    # 4. Nubes pixeladas de atardecer
    def _dibujar_nube(s, x_centro, y_base, largo, alto_nube, rnd_seed):
        rnd_c = _random.Random(rnd_seed)
        col_sombra = (74, 28, 62)
        col_medio = (158, 58, 76)
        col_luz = (235, 148, 82)
        col_borde = (255, 218, 145)

        tramos = []
        pasos = largo // 5
        for p in range(pasos):
            rx = x_centro - (largo // 2) + p * 5
            dist_c = abs(p - pasos / 2) / (pasos / 2)
            alt_local = int(alto_nube * (1.0 - dist_c * 0.75) * rnd_c.uniform(0.75, 1.25))
            tramos.append((rx, y_base, alt_local))

        for rx, yb, al in tramos:
            for dy in range(-al, 2):
                y = yb + dy
                if 0 <= y < H:
                    w_bloque = 6
                    for dx in range(w_bloque):
                        x = rx + dx
                        if 0 <= x < W:
                            if dy == -al:
                                s.set_at((x, y), col_borde)
                            elif dy < -al // 2:
                                s.set_at((x, y), col_luz)
                            elif dy <= 0:
                                s.set_at((x, y), col_medio)
                            else:
                                s.set_at((x, y), col_sombra)

    nubes = [
        (130, 42, 130, 11, 101),
        (510, 52, 160, 13, 202),
        (275, 88, 115, 9,  303),
        (575, 102, 95, 8,  404),
        (85,  124, 135, 10, 505),
        (395, 136, 125, 9,  606),
    ]
    for nc in nubes:
        _dibujar_nube(surf, nc[0], nc[1], nc[2], nc[3], nc[4])

    # Bandada de pájaros lejanos
    for px, py in [(215, 80), (227, 76), (239, 73), (251, 77), (263, 81)]:
        surf.set_at((px, py), (58, 20, 42))
        surf.set_at((px - 1, py - 1), (58, 20, 42))
        surf.set_at((px + 1, py - 1), (58, 20, 42))

    # 5. Grandes montañas con crestas rocosas y facetas de relieve
    def _crear_perfil_montaña(px, py, am, rnd_val):
        rnd_m = _random.Random(rnd_val)
        y_base = 232
        puntos_izq = []
        puntos_der = []
        for y in range(py, y_base):
            prog = (y - py) / max(1, y_base - py)
            half = int((am // 2) * (prog ** 0.88))
            desvio = int(rnd_m.uniform(-3, 3) * (prog ** 0.5))
            crest_offset = int(rnd_m.uniform(-2, 2) * (1.0 - prog))
            puntos_izq.append((y, px - half + desvio, px + crest_offset))
            puntos_der.append((y, px + crest_offset, px + half + desvio))
        return puntos_izq, puntos_der

    # Capa 1: Picos lejanos
    picos_lej = [
        (65,   72, 150, 1111),
        (170,  58, 175, 2222),
        (280,  90, 135, 3333),
        (375,  68, 165, 4444),
        (485,  52, 185, 5555),
        (585,  82, 150, 6666),
    ]
    col_lej_somb = (52, 26, 62)
    col_lej_cuerpo = (75, 36, 78)
    col_lej_luz = (102, 48, 98)
    col_nieve_lej_luz = (248, 198, 182)
    col_nieve_lej_somb = (178, 132, 168)

    for px, py, am, r_seed in picos_lej:
        p_izq, p_der = _crear_perfil_montaña(px, py, am, r_seed)
        for (y, x_min, x_crest), (_, _, x_max) in zip(p_izq, p_der):
            h_tot = 232 - py
            prog = (y - py) / max(1, h_tot)
            for x in range(x_min, x_crest):
                if 0 <= x < W:
                    col_p = col_lej_luz if x < (x_min + x_crest) // 2 else col_lej_cuerpo
                    surf.set_at((x, y), col_p)
            for x in range(x_crest, x_max + 1):
                if 0 <= x < W:
                    surf.set_at((x, y), col_lej_somb)
            if prog < 0.32:
                for x in range(x_min, x_crest):
                    if 0 <= x < W:
                        surf.set_at((x, y), col_nieve_lej_luz)
                for x in range(x_crest, x_max + 1):
                    if 0 <= x < W and prog < 0.28:
                        surf.set_at((x, y), col_nieve_lej_somb)

    # Capa 2: Picos medios
    picos_med = [
        (25,  125, 130, 7771),
        (125, 110, 150, 7772),
        (225, 138, 125, 7773),
        (320, 152, 115, 7774),
        (420, 118, 155, 7775),
        (525, 104, 160, 7776),
        (625, 130, 120, 7777),
    ]
    col_med_somb = (42, 18, 44)
    col_med_cuerpo = (68, 28, 58)
    col_med_luz = (118, 48, 76)
    col_nieve_med_luz = (245, 175, 142)
    col_nieve_med_somb = (165, 95, 125)

    for px, py, am, r_seed in picos_med:
        p_izq, p_der = _crear_perfil_montaña(px, py, am, r_seed)
        for (y, x_min, x_crest), (_, _, x_max) in zip(p_izq, p_der):
            h_tot = 232 - py
            prog = (y - py) / max(1, h_tot)
            for x in range(x_min, x_crest):
                if 0 <= x < W:
                    c_fac = col_med_luz if x < (x_min * 2 + x_crest) // 3 else col_med_cuerpo
                    surf.set_at((x, y), c_fac)
            for x in range(x_crest, x_max + 1):
                if 0 <= x < W:
                    surf.set_at((x, y), col_med_somb)
            if prog < 0.26:
                for x in range(x_min, x_crest):
                    if 0 <= x < W:
                        surf.set_at((x, y), col_nieve_med_luz)
                for x in range(x_crest, x_max + 1):
                    if 0 <= x < W and prog < 0.22:
                        surf.set_at((x, y), col_nieve_med_somb)

    # 6. Colinas bajas y siluetas de pinos distantes
    for x in range(W):
        y_col = int(214 + 8 * _math.sin(x * 0.022 + 0.8) + 3 * _math.cos(x * 0.05))
        for y in range(y_col, 230):
            surf.set_at((x, y), (32, 14, 35))
        if x % 6 in (0, 1):
            h_p = 3 + (x % 4)
            for dy in range(h_p):
                surf.set_at((x, y_col - dy), (24, 10, 26))

    # 7. Lago de atardecer con reflejos dorados y ciruela
    y_lago_top = 222
    y_lago_bot = 276
    for y in range(y_lago_top, y_lago_bot):
        prog_l = (y - y_lago_top) / (y_lago_bot - y_lago_top)
        r_l = int(248 - 165 * prog_l)
        g_l = int(178 - 135 * prog_l)
        b_l = int(88 - 35 * prog_l)
        pygame.draw.line(surf, (max(0, min(255, r_l)), max(0, min(255, g_l)), max(0, min(255, b_l))), (0, y), (W - 1, y))

    # Reflejos oscuros bajo montañas laterales
    for y in range(y_lago_top, y_lago_top + 28):
        for x in range(W):
            if x < 180 or x > 460:
                dist_borde = min(x, W - 1 - x) / 180
                factor_somb = 0.45 + 0.55 * dist_borde
                if (x + y) % 2 == 0:
                    c_orig = surf.get_at((x, y))
                    surf.set_at((x, y), (
                        int(c_orig.r * factor_somb),
                        int(c_orig.g * factor_somb),
                        int(c_orig.b * factor_somb + 25 * (1.0 - factor_somb))
                    ))

    # Reflejo central del sol y ondulaciones en el agua
    rnd_w = _random.Random(777)
    for y in range(y_lago_top, y_lago_bot):
        prog = (y - y_lago_top) / (y_lago_bot - y_lago_top)
        ancho_reflejo = int(80 + 140 * prog)
        for dx in range(-ancho_reflejo // 2, ancho_reflejo // 2 + 1):
            x = 320 + dx
            if 0 <= x < W:
                if (y + (x // 5)) % 3 == 0:
                    c_act = surf.get_at((x, y))
                    factor = 1.0 - (abs(dx) / (ancho_reflejo // 2))
                    surf.set_at((x, y), (
                        min(255, c_act.r + int(55 * factor)),
                        min(255, c_act.g + int(45 * factor)),
                        min(255, c_act.b + int(20 * factor)),
                    ))
        if y % 2 == 0:
            for _ in range(int(10 * (1.0 - prog * 0.8))):
                wx = rnd_w.randint(70, W - 70)
                w_len = rnd_w.randint(4, 15)
                c_onda = (255, 238, 175) if prog < 0.45 else (228, 142, 108)
                for w_dx in range(w_len):
                    if 0 <= wx + w_dx < W:
                        surf.set_at((wx + w_dx, y), c_onda)

    # Bruma sobre el agua
    for dy in range(5):
        y_b = y_lago_top + dy
        for x in range(W):
            if (x * 11 + y_b * 7) % 6 == 0:
                surf.set_at((x, y_b), (238, 198, 178))

    # 8. Terreno en primer plano: orilla, nieve cálida y rocas
    def _altura_suelo(x):
        dist_centro = abs(x - 320) / 320
        y_b = 265 - int(25 * (dist_centro ** 1.35))
        y_b += int(4 * _math.sin(x * 0.038) + 3 * _math.cos(x * 0.075))
        return y_b

    col_nieve_luz = (246, 228, 220)
    col_nieve_medio = (218, 192, 192)
    col_nieve_sombra = (155, 122, 150)
    col_tierra = (64, 38, 42)

    for x in range(W):
        y_top = _altura_suelo(x)
        if 0 <= y_top < H:
            surf.set_at((x, y_top), col_tierra)
            if y_top + 1 < H:
                surf.set_at((x, y_top + 1), col_tierra)

        for y in range(y_top + 2, H):
            prog_y = (y - y_top) / max(1, H - y_top)
            if prog_y < 0.16:
                c = col_nieve_luz
            elif prog_y < 0.42:
                c = col_nieve_luz if (x + y) % 2 == 0 else col_nieve_medio
            elif prog_y < 0.72:
                c = col_nieve_medio if (x + y) % 3 != 0 else col_nieve_sombra
            else:
                c = col_nieve_sombra if (x + y) % 2 == 0 else col_nieve_medio
            surf.set_at((x, y), c)

    # Rocas con nieve
    rocas = [
        (135, 256, 18, 10),
        (210, 267, 14, 8),
        (435, 266, 16, 9),
        (515, 254, 20, 12),
        (75,  276, 22, 12),
        (560, 274, 24, 13),
        (280, 280, 12, 7),
        (360, 283, 15, 8),
    ]
    col_roca_oscura = (46, 28, 34)
    col_roca_media = (76, 48, 56)
    col_roca_luz = (116, 80, 86)

    for rx, ry, rw, rh in rocas:
        for dy in range(rh):
            y_r = ry + dy
            w_linea = int(rw * _math.sin((dy + 1) / (rh + 1) * _math.pi))
            for dx in range(-w_linea // 2, w_linea // 2 + 1):
                x_r = rx + dx
                if 0 <= x_r < W and 0 <= y_r < H:
                    if dy == 0 or (dy == 1 and dx < 0):
                        surf.set_at((x_r, y_r), col_nieve_luz)
                    elif dx < 0:
                        surf.set_at((x_r, y_r), col_roca_luz)
                    elif dx == 0:
                        surf.set_at((x_r, y_r), col_roca_media)
                    else:
                        surf.set_at((x_r, y_r), col_roca_oscura)

    # Cañas de invierno en la orilla
    for cx in [155, 175, 195, 410, 430, 450, 470]:
        cy = _altura_suelo(cx)
        for h_c in range(5, 12):
            surf.set_at((cx, cy - h_c), (142, 92, 58))
        surf.set_at((cx + 1, cy - 8), (172, 122, 78))

    # 9. Árboles altos a ambos lados del escenario (dejando el centro despejado)
    def _dibujar_pino(s, cx, base_y, alt_total, ancho_max):
        col_tronco = (50, 26, 22)
        col_tronco_luz = (82, 44, 36)
        col_pino_sombra = (18, 36, 26)
        col_pino_medio = (32, 64, 44)
        col_pino_luz = (54, 96, 64)
        col_nieve_pino_luz = (248, 226, 218)
        col_nieve_pino_somb = (152, 120, 142)

        for dy in range(12):
            y_t = base_y + dy
            if 0 <= y_t < H:
                for dx in range(-2, 3):
                    c_tr = col_tronco_luz if dx < 0 else col_tronco
                    if 0 <= cx + dx < W:
                        s.set_at((cx + dx, y_t), c_tr)

        pisos = 6
        for piso in range(pisos):
            f_piso = (piso + 1) / pisos
            ancho_piso = int(ancho_max * (0.35 + 0.65 * f_piso))
            h_piso = int((alt_total // pisos) * 1.35)
            y_cima_piso = base_y - alt_total + int(alt_total * (piso / pisos))
            y_base_piso = y_cima_piso + h_piso

            for y in range(y_cima_piso, y_base_piso + 1):
                prog = (y - y_cima_piso) / max(1, y_base_piso - y_cima_piso)
                w_rama = int(ancho_piso * prog)
                for dx in range(-w_rama, w_rama + 1):
                    x = cx + dx
                    if 0 <= x < W and 0 <= y < H:
                        if dx < -w_rama // 2:
                            col_f = col_pino_luz
                        elif dx < 0:
                            col_f = col_pino_medio
                        else:
                            col_f = col_pino_sombra
                        s.set_at((x, y), col_f)

            for dx in range(-ancho_piso, ancho_piso + 1):
                x = cx + dx
                y_n = y_cima_piso + int(abs(dx) * 0.28)
                if 0 <= x < W and 0 <= y_n < H:
                    c_sn = col_nieve_pino_luz if dx < 0 else col_nieve_pino_somb
                    s.set_at((x, y_n), c_sn)
                    if 0 <= y_n + 1 < H and abs(dx) % 2 == 0:
                        s.set_at((x, y_n + 1), c_sn)

    pines_izq = [
        (18,  275, 115, 38),
        (52,  285, 135, 44),
        (88,  292, 105, 34),
        (120, 305, 85,  28),
    ]
    for px, by, ah, aw in pines_izq:
        _dibujar_pino(surf, px, by, ah, aw)

    pines_der = [
        (622, 275, 115, 38),
        (588, 285, 135, 44),
        (552, 292, 105, 34),
        (520, 305, 85,  28),
    ]
    for px, by, ah, aw in pines_der:
        _dibujar_pino(surf, px, by, ah, aw)

    # Arbustos nevados en las esquinas inferiores
    def _dibujar_arbusto(s, cx, cy, rad):
        for dy in range(-rad, 2):
            for dx in range(-rad, rad + 1):
                if dx * dx + dy * dy <= rad * rad:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < W and 0 <= y < H:
                        s.set_at((x, y), (26, 52, 34) if dx > 0 else (42, 78, 52))
        for dx in range(-rad, rad + 1):
            y_c = cy - int(_math.sqrt(max(0, rad * rad - dx * dx)))
            if 0 <= cx + dx < W and 0 <= y_c < H:
                s.set_at((cx + dx, y_c), (245, 222, 215))

    for ax, ay, ar in [(35, 315, 10), (70, 320, 8), (605, 315, 10), (570, 320, 8)]:
        _dibujar_arbusto(surf, ax, ay, ar)

    return pygame.transform.scale(surf, (ancho, alto))


# Partículas sutiles de atardecer / copos de invierno para MODO DE JUEGO
_copos_modo: list[dict] = []


def _init_copos_modo(ancho: int = 1280, alto: int = 720) -> None:
    global _copos_modo
    rnd = _random.Random(9191)
    colores_particula = [
        (255, 245, 235),  # Nieve blanca
        (255, 225, 180),  # Dorado suave atardecer
        (255, 205, 190),  # Melocotón / coral tenue
    ]
    _copos_modo = [
        {
            "x": rnd.uniform(0, ancho),
            "y": rnd.uniform(0, alto),
            "vy": rnd.uniform(0.4, 1.1),
            "vx": rnd.uniform(-0.25, 0.25),
            "r": rnd.choice([1, 2, 2, 3]),
            "alpha": rnd.randint(110, 190),
            "color": rnd.choice(colores_particula),
        }
        for _ in range(50)
    ]


def _dibujar_copos_modo(pantalla: "pygame.Surface") -> None:
    """Actualiza y dibuja partículas ambientales sutiles de atardecer para MODO DE JUEGO."""
    w, h = pantalla.get_size()
    for c in _copos_modo:
        c["x"] += c["vx"]
        c["y"] += c["vy"]
        if c["y"] > h:
            c["y"] = -4
            c["x"] = _random.uniform(0, w)
        if c["x"] < 0:
            c["x"] = w
        elif c["x"] > w:
            c["x"] = 0
        r = c["r"]
        col = c.get("color", (255, 245, 235))
        surf_c = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf_c, (col[0], col[1], col[2], c["alpha"]), (r, r), r)
        pantalla.blit(surf_c, (int(c["x"]) - r, int(c["y"]) - r))



def _generar_fondo_partidas(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    """
    Fondo pixel art estilo Diario de Aventuras / Registro de Expediciones.
    - Tonos cálidos pergamino: crema, beige, avellana, toques dorados y detalles sutiles de atardecer.
    - Textura de papel envejecido y bordes desgastados.
    - Bocetos discretos de mapa y expedición: montañas en tinta sepia, rosa de los vientos/brújula,
      rutas punteadas, pequeños árboles y estrellas de navegación.
    - Cantoneras de cuero y latón en las esquinas.
    """
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. Base pergamino con gradiente cálido vertical y leve curvatura de tomo abierto
    col_centro = (246, 236, 214)
    col_extremo = (226, 206, 172)
    for y in range(H):
        t_y = y / H
        for x in range(W):
            t_x = abs(x - W / 2) / (W / 2)
            t_diag = (t_x * 0.6 + t_y * 0.4)
            r = int(col_centro[0] * (1 - t_diag) + col_extremo[0] * t_diag)
            g = int(col_centro[1] * (1 - t_diag) + col_extremo[1] * t_diag)
            b = int(col_centro[2] * (1 - t_diag) + col_extremo[2] * t_diag)
            surf.set_at((x, y), (r, g, b))

    # 2. Textura sutil de papel antiguo (grano fino de fibra vegetal)
    rnd_fibra = _random.Random(1842)
    for _ in range(3500):
        fx = rnd_fibra.randint(0, W - 1)
        fy = rnd_fibra.randint(0, H - 1)
        c_orig = surf.get_at((fx, fy))
        delta = rnd_fibra.choice([-7, -4, 4, 6])
        surf.set_at((fx, fy), (
            max(0, min(255, c_orig.r + delta)),
            max(0, min(255, c_orig.g + delta)),
            max(0, min(255, c_orig.b + delta)),
        ))

    # 3. Bordes envejecidos / efecto papel quemado y biselado
    for b in range(12):
        factor_osc = 1.0 - (b / 12.0) * 0.45
        for x in range(b, W - b):
            # Arriba y abajo
            for y_b in (b, H - 1 - b):
                c = surf.get_at((x, y_b))
                surf.set_at((x, y_b), (int(c.r * factor_osc), int(c.g * factor_osc), int(c.b * factor_osc)))
        for y in range(b, H - b):
            # Izquierda y derecha
            for x_b in (b, W - 1 - b):
                c = surf.get_at((x_b, y))
                surf.set_at((x_b, y), (int(c.r * factor_osc), int(c.g * factor_osc), int(c.b * factor_osc)))

    # Línea de encuadre perimetral interior en tinta sepia tenue
    m_int = 14
    col_marco_int = (185, 155, 120)
    col_marco_fino = (215, 192, 160)
    pygame.draw.rect(surf, col_marco_int, (m_int, m_int, W - m_int * 2, H - m_int * 2), width=2)
    pygame.draw.rect(surf, col_marco_fino, (m_int + 3, m_int + 3, W - (m_int + 3) * 2, H - (m_int + 3) * 2), width=1)

    # 4. Líneas guía muy sutiles de cuaderno/diario
    col_pauta = (212, 195, 168)
    for y in range(54, H - 30, 24):
        for x in range(m_int + 8, W - m_int - 8, 4):
            surf.set_at((x, y), col_pauta)

    # 5. Bocetos ilustrados discretos en tinta sepia (Montañas estilo cartografía)
    col_tinta_mont = (150, 115, 80)
    col_tinta_clara = (190, 160, 125)

    def _dibujar_montana_boceto(cx, base_y, ancho, alto):
        mitad = ancho // 2
        for dy in range(alto):
            y_cur = base_y - dy
            prog = dy / max(1, alto)
            w_act = int(mitad * (1.0 - prog))
            x_izq = cx - w_act
            x_der = cx + w_act
            if 0 <= y_cur < H:
                if 0 <= x_izq < W:
                    surf.set_at((x_izq, y_cur), col_tinta_mont)
                if 0 <= x_der < W:
                    surf.set_at((x_der, y_cur), col_tinta_mont)
                # Sombreado rayado en la ladera este
                for sx in range(cx, x_der):
                    if (sx + y_cur) % 3 == 0 and 0 <= sx < W:
                        surf.set_at((sx, y_cur), col_tinta_clara)
        for dy in range(alto):
            y_cur = base_y - dy
            c_offset = int(_math.sin(dy * 0.25) * 2)
            if 0 <= cx + c_offset < W and 0 <= y_cur < H:
                surf.set_at((cx + c_offset, y_cur), col_tinta_mont)

    # Grupo de montañas en el margen izquierdo
    _dibujar_montana_boceto(48, 120, 42, 32)
    _dibujar_montana_boceto(76, 128, 50, 40)
    _dibujar_montana_boceto(108, 134, 38, 28)

    # Pequeño macizo en el margen derecho inferior
    _dibujar_montana_boceto(585, 305, 46, 36)
    _dibujar_montana_boceto(555, 312, 38, 26)

    # 6. Pequeños pinos/árboles en tinta sepia en los márgenes
    def _dibujar_arbolito_tinta(tx, ty):
        if not (0 <= tx < W and 0 <= ty < H - 12):
            return
        for dy in range(4):
            surf.set_at((tx, ty + 8 + dy), col_tinta_mont)
        for r_fila in range(4):
            y_f = ty + r_fila * 2
            ancho_f = r_fila + 1
            for dx in range(-ancho_f, ancho_f + 1):
                if 0 <= tx + dx < W and 0 <= y_f < H:
                    surf.set_at((tx + dx, y_f), col_tinta_mont)

    for ax, ay in [(32, 130), (42, 138), (62, 142), (92, 145), (120, 148), (530, 318), (542, 322), (610, 315)]:
        _dibujar_arbolito_tinta(ax, ay)

    # 7. Brújula / Rosa de los vientos ilustrada en margen superior derecho
    bx, by = 585, 58
    radio_b = 20
    pygame.draw.circle(surf, col_tinta_clara, (bx, by), radio_b, width=1)
    pygame.draw.circle(surf, (218, 172, 70), (bx, by), radio_b - 3, width=1)
    col_aguja_norte = (195, 65, 55)   # Acento coral/terracota aventura
    col_aguja_sur = (75, 95, 125)     # Acento azul expedición
    col_aguja_sepia = col_tinta_mont

    for dy in range(radio_b - 2):
        w_ag = int(3 * (1.0 - dy / (radio_b - 2)))
        for dx in range(-w_ag, w_ag + 1):
            if 0 <= bx + dx < W and 0 <= by - dy < H:
                surf.set_at((bx + dx, by - dy), col_aguja_norte if dx <= 0 else (235, 125, 115))
    for dy in range(radio_b - 2):
        w_ag = int(3 * (1.0 - dy / (radio_b - 2)))
        for dx in range(-w_ag, w_ag + 1):
            if 0 <= bx + dx < W and 0 <= by + dy < H:
                surf.set_at((bx + dx, by + dy), col_aguja_sur if dx <= 0 else (120, 145, 175))
    for dx in range(radio_b - 4):
        w_ag = int(3 * (1.0 - dx / (radio_b - 4)))
        for dy in range(-w_ag, w_ag + 1):
            if 0 <= bx + dx < W and 0 <= by + dy < H:
                surf.set_at((bx + dx, by + dy), col_aguja_sepia)
            if 0 <= bx - dx < W and 0 <= by + dy < H:
                surf.set_at((bx - dx, by + dy), col_aguja_sepia)
    pygame.draw.circle(surf, (235, 195, 80), (bx, by), 3)
    pygame.draw.circle(surf, (110, 65, 30), (bx, by), 3, width=1)

    # 8. Camino de expedición punteado (ruta de viaje en mapa)
    puntos_ruta = [
        (65, 145), (85, 162), (112, 175), (145, 182), (170, 205),
        (190, 240), (200, 280), (215, 315), (240, 335)
    ]
    for i in range(len(puntos_ruta) - 1):
        x1, y1 = puntos_ruta[i]
        x2, y2 = puntos_ruta[i + 1]
        dist = int(_math.hypot(x2 - x1, y2 - y1))
        for step in range(0, dist, 6):
            t = step / max(1, dist)
            px = int(x1 + (x2 - x1) * t)
            py = int(y1 + (y2 - y1) * t)
            if 0 <= px < W and 0 <= py < H:
                surf.set_at((px, py), (175, 110, 65))
                if 0 <= px + 1 < W:
                    surf.set_at((px + 1, py), (175, 110, 65))

    cx_camp, cy_camp = puntos_ruta[4]
    for d_cruz in range(-2, 3):
        if 0 <= cx_camp + d_cruz < W and 0 <= cy_camp + d_cruz < H:
            surf.set_at((cx_camp + d_cruz, cy_camp + d_cruz), (195, 55, 45))
            surf.set_at((cx_camp + d_cruz, cy_camp - d_cruz), (195, 55, 45))

    # 9. Estrellas de orientación tenues en tinta dorada
    estrellas_mapa = [(38, 45), (120, 38), (520, 48), (608, 145), (35, 325), (480, 320)]
    col_estrella = (205, 165, 85)
    for ex, ey in estrellas_mapa:
        if 0 <= ex < W and 0 <= ey < H:
            surf.set_at((ex, ey), col_estrella)
            surf.set_at((ex + 1, ey), col_estrella)
            surf.set_at((ex - 1, ey), col_estrella)
            surf.set_at((ex, ey + 1), col_estrella)
            surf.set_at((ex, ey - 1), col_estrella)

    # 10. Cantoneras de latón / cuero en las 4 esquinas del diario
    tam_cantonera = 22
    col_cant_laton = (195, 155, 65)
    col_cant_sombra = (95, 65, 30)
    col_cant_remache = (245, 215, 115)

    def _dibujar_cantonera(x_origen, y_origen, dir_x, dir_y):
        for dx in range(tam_cantonera):
            for dy in range(tam_cantonera):
                if dx + dy < tam_cantonera:
                    x = x_origen + dx * dir_x
                    y = y_origen + dy * dir_y
                    if 0 <= x < W and 0 <= y < H:
                        if dx + dy == tam_cantonera - 1 or dx == 0 or dy == 0:
                            surf.set_at((x, y), col_cant_sombra)
                        elif dx + dy < tam_cantonera - 3:
                            surf.set_at((x, y), col_cant_laton)
                        else:
                            surf.set_at((x, y), (145, 110, 48))
        rx = x_origen + 7 * dir_x
        ry = y_origen + 7 * dir_y
        if 0 <= rx < W and 0 <= ry < H:
            surf.set_at((rx, ry), col_cant_remache)
            surf.set_at((rx + dir_x, ry), col_cant_sombra)

    _dibujar_cantonera(4, 4, 1, 1)
    _dibujar_cantonera(W - 5, 4, -1, 1)
    _dibujar_cantonera(4, H - 5, 1, -1)
    _dibujar_cantonera(W - 5, H - 5, -1, -1)

    # 11. Escalar a resolución final
    surf_final = pygame.transform.scale(surf, (ancho, alto))
    return surf_final


def _obtener_fondo_modo_juego(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_modo_juego_cache
    if _fondo_modo_juego_cache is None:
        _fondo_modo_juego_cache = _generar_fondo_modo_juego(ancho, alto)
    return _fondo_modo_juego_cache


def _obtener_fondo_partidas(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_partidas_cache
    if _fondo_partidas_cache is None:
        _fondo_partidas_cache = _generar_fondo_partidas(ancho, alto)
    return _fondo_partidas_cache


_fondo_opciones_cache: "pygame.Surface | None" = None
_copos_opciones: list[dict] = []


def _generar_fondo_opciones(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    """
    Paisaje invernal pixel art con montañas nevadas, árboles de invierno y cielo nocturno
    estrellado con luna suave para la pantalla completa de «OPCIONES».
    """
    W, H = 640, 360
    surf = pygame.Surface((W, H))

    # 1. Cielo nocturno invernal profundo
    bandas = [
        (0,   60,  (12, 16, 32)),   # Azul medianoche oscuro
        (60,  130, (20, 28, 54)),   # Azul zafiro profundo
        (130, 200, (32, 45, 78)),   # Azul frío
        (200, 255, (48, 64, 102)),  # Azul noche boreal tenue
        (255, 300, (68, 86, 124)),  # Brillo frío sobre montañas
    ]
    for y1, y2, col in bandas:
        pygame.draw.rect(surf, col, (0, y1, W, y2 - y1))

    for i in range(len(bandas) - 1):
        yt = bandas[i][1]
        c1, c2 = bandas[i][2], bandas[i+1][2]
        for dy in range(-3, 4):
            y = yt + dy
            if 0 <= y < H:
                for x in range(W):
                    if dy == -3 and (x % 4 == 0 and y % 4 == 0): surf.set_at((x, y), c2)
                    elif dy == -2 and (x + y) % 4 == 0: surf.set_at((x, y), c2)
                    elif dy == -1 and (x % 2 == 0 and y % 2 == 0): surf.set_at((x, y), c2)
                    elif dy == 0 and (x + y) % 2 == 0: surf.set_at((x, y), c2)
                    elif dy == 1 and (x % 2 == 0 and y % 2 == 0): surf.set_at((x, y), c1)
                    elif dy == 2 and (x + y) % 4 == 0: surf.set_at((x, y), c1)
                    elif dy == 3 and (x % 4 == 0 and y % 4 == 0): surf.set_at((x, y), c1)

    # 2. Estrellas nocturnas
    rnd = _random.Random(4242)
    for _ in range(65):
        sx = rnd.randint(10, W - 10)
        sy = rnd.randint(6, 190)
        alpha = rnd.choice([(255, 255, 255), (200, 220, 255), (230, 240, 255), (170, 190, 230)])
        surf.set_at((sx, sy), alpha)
        if rnd.random() < 0.15:
            surf.set_at((sx + 1, sy), (180, 205, 240))
            surf.set_at((sx - 1, sy), (180, 205, 240))
            surf.set_at((sx, sy + 1), (180, 205, 240))
            surf.set_at((sx, sy - 1), (180, 205, 240))

    # Luna invernal suave
    mx, my, mr = 540, 55, 20
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            d2 = dx * dx + dy * dy
            if d2 <= mr * mr:
                surf.set_at((mx + dx, my + dy), (245, 248, 255))
            elif d2 <= (mr + 3) * (mr + 3):
                surf.set_at((mx + dx, my + dy), (120, 150, 200))

    # 3. Montañas lejanas nevadas
    def mnt(x, seed, h_base, amp):
        return h_base - int(amp * _math.sin(x * 0.008 + seed) + amp * 0.5 * _math.sin(x * 0.021 + seed * 2))

    for x in range(W):
        y_m1 = mnt(x, 12, 225, 45)
        for y in range(y_m1, 280):
            surf.set_at((x, y), (195, 215, 240) if y < y_m1 + 18 else (55, 70, 105))

    for x in range(W):
        y_m2 = mnt(x, 77, 245, 38)
        for y in range(y_m2, 310):
            surf.set_at((x, y), (225, 238, 255) if y < y_m2 + 15 else (38, 52, 85))

    # 4. Colinas nevadas en primer plano
    for x in range(W):
        y_col = 285 + int(12 * _math.sin(x * 0.015))
        for y in range(y_col, H):
            prog = (y - y_col) / max(1, H - y_col)
            if prog < 0.2:
                col = (235, 242, 255)
            elif prog < 0.6:
                col = (210, 225, 248) if (x + y) % 2 == 0 else (185, 205, 235)
            else:
                col = (160, 182, 215)
            surf.set_at((x, y), col)

    # 5. Pinos nevados en los laterales
    def pino_nevado(cx, by, alt, anc):
        for y in range(by - alt, by):
            prog = (y - (by - alt)) / alt
            w_act = int(anc * prog)
            for dx in range(-w_act // 2, w_act // 2 + 1):
                px = cx + dx
                if 0 <= px < W and 0 <= y < H:
                    if dx == -w_act // 2 or dx == w_act // 2 or (y % 6 in (0, 1)):
                        surf.set_at((px, y), (230, 240, 255))
                    else:
                        surf.set_at((px, y), (24, 48, 42))

    pino_nevado(30, 310, 85, 32)
    pino_nevado(65, 320, 95, 38)
    pino_nevado(100, 335, 75, 30)
    pino_nevado(610, 310, 85, 32)
    pino_nevado(575, 320, 95, 38)
    pino_nevado(540, 335, 75, 30)

    return pygame.transform.scale(surf, (ancho, alto))


def _obtener_fondo_opciones(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_opciones_cache
    if _fondo_opciones_cache is None:
        _fondo_opciones_cache = _generar_fondo_opciones(ancho, alto)
    return _fondo_opciones_cache


_fondo_camerino_personajes_cache: "pygame.Surface | None" = None


def _generar_fondo_camerino_personajes(W: int = 1280, H: int = 720) -> "pygame.Surface":
    """
    Genera un fondo pixel art auténtico estilo habitación de vestuario / camerino cálido
    para la pantalla de PERSONALIZACIÓN DE PERSONAJES de Las Aventurillas de Pico en el Parque.
    Paleta: Rosa pastel, durazno, beige cálido, marrón suave, detalles en coral y crema.
    """
    sw, sh = 640, 360
    surf = pygame.Surface((sw, sh))

    # =========================================================================
    # 1. PARED DE HABITACIÓN DE VESTUARIO (y = 0 a 282)
    # =========================================================================
    c_pared_base = (246, 222, 224)
    c_pared_raya = (252, 230, 232)
    c_pared_sombra = (240, 212, 216)

    surf.fill(c_pared_base)

    # Rayas de papel tapiz vertical sutil
    for x in range(sw):
        if x % 10 in (0, 1, 2, 3):
            pygame.draw.line(surf, c_pared_raya, (x, 0), (x, 225))
        elif x % 10 == 9:
            pygame.draw.line(surf, c_pared_sombra, (x, 0), (x, 225))

    # Moldura superior del techo (Cornisa de yeso / madera crema)
    pygame.draw.rect(surf, (253, 248, 242), (0, 0, sw, 3))
    pygame.draw.rect(surf, (242, 230, 218), (0, 3, sw, 3))
    pygame.draw.rect(surf, (218, 196, 180), (0, 6, sw, 2))

    # Moldura intermedia (Chair rail / moldura a y = 222..228)
    pygame.draw.rect(surf, (255, 250, 244), (0, 222, sw, 2))
    pygame.draw.rect(surf, (235, 215, 198), (0, 224, sw, 3))
    pygame.draw.rect(surf, (208, 184, 165), (0, 227, sw, 2))

    # Panel inferior de pared (Wainscoting en crema / durazno suave y = 229..282)
    c_wains_base = (252, 238, 232)
    c_wains_luz = (255, 248, 244)
    c_wains_som = (230, 212, 202)
    pygame.draw.rect(surf, c_wains_base, (0, 229, sw, 53))

    # Paneles moldurados en la parte inferior
    w_pnl = 38
    for px in range(6, sw - 6, w_pnl + 6):
        r_pnl = pygame.Rect(px, 233, w_pnl, 45)
        pygame.draw.rect(surf, c_wains_som, r_pnl, 1)
        pygame.draw.line(surf, c_wains_luz, (r_pnl.left + 1, r_pnl.top + 1), (r_pnl.right - 1, r_pnl.top + 1))
        pygame.draw.line(surf, c_wains_luz, (r_pnl.left + 1, r_pnl.top + 1), (r_pnl.left + 1, r_pnl.bottom - 1))

    # =========================================================================
    # 2. ZÓCALO Y SUELO DE MADERA EN TONOS CÁLIDOS (y = 282 a 360)
    # =========================================================================
    # Zócalo de madera cálida
    pygame.draw.rect(surf, (232, 188, 142), (0, 282, sw, 2)) # Bisel superior de luz
    pygame.draw.rect(surf, (168, 116, 75), (0, 284, sw, 4))  # Madera base
    pygame.draw.rect(surf, (115, 75, 45), (0, 288, sw, 2))   # Sombra de contacto

    # Suelo de madera: tablones de parquet cálidos
    col_tablones = [
        (198, 144, 96),
        (184, 130, 82),
        (206, 152, 104),
        (190, 136, 88),
        (178, 124, 76),
        (200, 146, 98),
        (186, 132, 84),
    ]
    h_tab = 10
    rnd_wood = _random.Random(789)

    for i, c_tab in enumerate(col_tablones):
        y_tab = 290 + i * h_tab
        h_act = min(h_tab, sh - y_tab)
        pygame.draw.rect(surf, c_tab, (0, y_tab, sw, h_act))
        # Vetas de madera
        for vy in range(y_tab + 2, y_tab + h_act - 2, 3):
            c_veta = (max(0, c_tab[0] - 14), max(0, c_tab[1] - 12), max(0, c_tab[2] - 10))
            for vx in range(0, sw, rnd_wood.randint(10, 24)):
                pygame.draw.line(surf, c_veta, (vx, vy), (min(sw, vx + rnd_wood.randint(8, 20)), vy))
        # Línea de unión horizontal oscura
        pygame.draw.line(surf, (115, 75, 45), (0, y_tab + h_act - 1), (sw, y_tab + h_act - 1))
        # Juntas verticales escalonadas
        offset_junta = (i * 41) % 70
        for jx in range(offset_junta, sw, 70):
            pygame.draw.line(surf, (110, 70, 40), (jx, y_tab), (jx, y_tab + h_act - 1))
            surf.set_at((jx + 2, y_tab + 3), (85, 52, 28))
            surf.set_at((jx - 3, y_tab + h_act - 4), (85, 52, 28))

    # =========================================================================
    # 3. ALFOMBRA OVALADA GRANDE Y DISCRETA (debajo de la interfaz)
    # =========================================================================
    cx_alf, cy_alf = 320, 324
    rx_alf, ry_alf = 276, 33

    s_alf = pygame.Surface((sw, sh), pygame.SRCALPHA)

    c_fringe_ext = (226, 132, 114, 255)
    c_fringe_int = (242, 162, 146, 255)
    c_alf_borde = (252, 214, 198, 255)
    c_alf_cuerpo = (254, 248, 240, 255)
    c_alf_textura = (246, 238, 226, 255)

    pygame.draw.ellipse(s_alf, c_fringe_ext, (cx_alf - rx_alf, cy_alf - ry_alf, rx_alf * 2, ry_alf * 2))
    pygame.draw.ellipse(s_alf, c_fringe_int, (cx_alf - rx_alf + 2, cy_alf - ry_alf + 2, (rx_alf - 2) * 2, (ry_alf - 2) * 2))
    pygame.draw.ellipse(s_alf, c_alf_borde, (cx_alf - rx_alf + 5, cy_alf - ry_alf + 4, (rx_alf - 5) * 2, (ry_alf - 4) * 2))
    pygame.draw.ellipse(s_alf, c_alf_cuerpo, (cx_alf - rx_alf + 10, cy_alf - ry_alf + 7, (rx_alf - 10) * 2, (ry_alf - 7) * 2))

    # Textura tejida suave
    for y in range(cy_alf - ry_alf + 8, cy_alf + ry_alf - 7, 2):
        for x in range(cx_alf - rx_alf + 12, cx_alf + rx_alf - 12, 4):
            dx = (x - cx_alf) / float(rx_alf - 12)
            dy = (y - cy_alf) / float(ry_alf - 9)
            if dx * dx + dy * dy < 0.95:
                if (x + y) % 4 == 0:
                    s_alf.set_at((x, y), c_alf_textura)

    # Ribete decorativo interno
    rx_rib, ry_rib = rx_alf - 22, ry_alf - 12
    pygame.draw.ellipse(s_alf, (240, 180, 168, 180), (cx_alf - rx_rib, cy_alf - ry_rib, rx_rib * 2, ry_rib * 2), 1)

    surf.blit(s_alf, (0, 0))

    # =========================================================================
    # 4. ELEMENTOS DECORATIVOS: PARTE SUPERIOR (Guirnalda de luces y plantas)
    # =========================================================================
    # Guirnalda de luces cálidas pegada al techo (y entre 7 y 14) para no tocar el título
    pts_guirnalda = []
    tramos = [
        (0, 105, 7, 14),
        (105, 210, 7, 13),
        (210, 315, 7, 12),
        (315, 420, 7, 12),
        (420, 525, 7, 13),
        (525, 640, 7, 14),
    ]
    for x0, x1, y_top, y_dip in tramos:
        mid = (x0 + x1) / 2.0
        w_t = (x1 - x0) / 2.0
        for x in range(x0, x1 + 1):
            norm = (x - mid) / w_t
            y = int(y_dip - (y_dip - y_top) * (1 - norm * norm))
            pts_guirnalda.append((x, y))

    for i in range(len(pts_guirnalda) - 1):
        pygame.draw.line(surf, (95, 80, 65), pts_guirnalda[i], pts_guirnalda[i+1], 1)

    c_halo = (255, 235, 175, 75)
    s_halo = pygame.Surface((sw, sh), pygame.SRCALPHA)

    for i in range(10, len(pts_guirnalda) - 10, 22):
        bx, by = pts_guirnalda[i]
        by += 1
        surf.set_at((bx, by), (115, 95, 75))
        surf.set_at((bx, by + 1), (255, 255, 235))
        surf.set_at((bx - 1, by + 2), (255, 225, 130))
        surf.set_at((bx, by + 2), (255, 255, 245))
        surf.set_at((bx + 1, by + 2), (255, 225, 130))
        surf.set_at((bx, by + 3), (255, 190, 105))
        pygame.draw.circle(s_halo, c_halo, (bx, by + 2), 5)
        pygame.draw.circle(s_halo, (255, 245, 205, 130), (bx, by + 2), 2)

    surf.blit(s_halo, (0, 0))

    # Plantas colgantes en las esquinas superiores
    def dibujar_maceta_colgante(s, cx, cy, flip=False):
        col_cuerda = (235, 220, 205)
        pygame.draw.line(s, col_cuerda, (cx - 6, 0), (cx - 4, cy - 3))
        pygame.draw.line(s, col_cuerda, (cx + 6, 0), (cx + 4, cy - 3))
        pygame.draw.line(s, col_cuerda, (cx, 0), (cx, cy - 3))

        r_pot = pygame.Rect(cx - 6, cy - 3, 13, 8)
        pygame.draw.rect(s, (225, 125, 95), r_pot, border_radius=2)
        pygame.draw.rect(s, (248, 165, 138), (r_pot.left + 1, r_pot.top + 1, r_pot.width - 2, 2))
        pygame.draw.rect(s, (165, 80, 55), r_pot, 1, border_radius=2)

        col_v1 = (72, 142, 68)
        col_v2 = (110, 182, 95)
        col_v3 = (46, 102, 45)
        hojas = [
            (cx - 4, cy + 5, 5, 8, col_v1),
            (cx + 2, cy + 6, 6, 12, col_v2),
            (cx - 2, cy + 10, 5, 15, col_v1),
            (cx + 4, cy + 14, 4, 10, col_v3),
            (cx - 5, cy + 18, 5, 8, col_v2),
            (cx, cy + 24, 4, 12, col_v1),
            (cx + 1, cy + 34, 3, 6, col_v2),
        ]
        if flip:
            hojas = [(cx - (hx - cx), hy, w, h, c) for hx, hy, w, h, c in hojas]
        for hx, hy, hw, hh, hc in hojas:
            pygame.draw.ellipse(s, hc, (hx - hw//2, hy, hw, hh))
            s.set_at((hx, hy + 2), col_v2)
            pygame.draw.line(s, col_v3, (cx, cy + 2), (hx, hy), 1)

    dibujar_maceta_colgante(surf, 18, 11, flip=False)
    dibujar_maceta_colgante(surf, sw - 18, 11, flip=True)

    # =========================================================================
    # 5. ELEMENTOS DECORATIVOS: LADO IZQUIERDO
    # =========================================================================
    # a) Cuadrito pixel art en la pared (x = 12..44, y = 46..76)
    r_cuadro = pygame.Rect(12, 46, 33, 29)
    pygame.draw.rect(surf, (165, 110, 60), r_cuadro, border_radius=2)
    pygame.draw.rect(surf, (220, 175, 105), (r_cuadro.left + 1, r_cuadro.top + 1, r_cuadro.width - 2, r_cuadro.height - 2), 1)
    pygame.draw.rect(surf, (110, 68, 35), r_cuadro, 1, border_radius=2)

    r_lienzo = pygame.Rect(r_cuadro.left + 3, r_cuadro.top + 3, r_cuadro.width - 6, r_cuadro.height - 6)
    pygame.draw.rect(surf, (253, 248, 238), r_lienzo)
    pygame.draw.rect(surf, (255, 185, 160), (r_lienzo.left, r_lienzo.top, r_lienzo.width, 9))
    pygame.draw.rect(surf, (255, 218, 175), (r_lienzo.left, r_lienzo.top + 9, r_lienzo.width, 6))
    surf.set_at((r_lienzo.right - 7, r_lienzo.top + 4), (255, 245, 210))
    pts_colina = [(r_lienzo.left, r_lienzo.bottom), (r_lienzo.left + 9, r_lienzo.top + 11), (r_lienzo.right, r_lienzo.bottom)]
    pygame.draw.polygon(surf, (105, 165, 95), pts_colina)
    gx, gy = r_lienzo.left + 7, r_lienzo.bottom - 6
    pygame.draw.rect(surf, (55, 45, 40), (gx, gy, 4, 4))
    surf.set_at((gx, gy - 1), (55, 45, 40))
    surf.set_at((gx + 2, gy - 1), (55, 45, 40))
    surf.set_at((gx + 4, gy + 2), (55, 45, 40))
    pygame.draw.line(surf, (140, 100, 65), (r_cuadro.centerx, r_cuadro.top - 5), (r_cuadro.left + 5, r_cuadro.top), 1)
    pygame.draw.line(surf, (140, 100, 65), (r_cuadro.centerx, r_cuadro.top - 5), (r_cuadro.right - 6, r_cuadro.top), 1)
    surf.set_at((r_cuadro.centerx, r_cuadro.top - 6), (110, 75, 45))

    # b) Repisa de madera en la pared izquierda (x = 8..48, y = 94..98)
    r_rep1 = pygame.Rect(8, 94, 41, 5)
    pygame.draw.rect(surf, (175, 120, 72), r_rep1, border_radius=1)
    pygame.draw.rect(surf, (215, 165, 115), (r_rep1.left, r_rep1.top, r_rep1.width, 2))
    pygame.draw.rect(surf, (115, 75, 40), r_rep1, 1)
    pygame.draw.polygon(surf, (135, 85, 50), [(12, 99), (16, 99), (12, 106)])
    pygame.draw.polygon(surf, (135, 85, 50), [(42, 99), (46, 99), (46, 106)])

    # Perfume vintage
    r_perf = pygame.Rect(30, 82, 8, 12)
    pygame.draw.rect(surf, (250, 175, 195), r_perf, border_radius=2)
    pygame.draw.rect(surf, (255, 220, 232), (r_perf.left + 1, r_perf.top + 2, 2, 8))
    surf.set_at((33, 80), (225, 180, 75))
    surf.set_at((34, 80), (225, 180, 75))
    pygame.draw.line(surf, (170, 130, 50), (35, 81), (39, 84))
    pygame.draw.circle(surf, (225, 175, 80), (40, 85), 2)

    # Maceta con enredadera / suculenta
    r_pot_rep = pygame.Rect(11, 85, 11, 9)
    pygame.draw.rect(surf, (230, 135, 100), r_pot_rep, border_radius=2)
    pygame.draw.rect(surf, (155, 80, 55), r_pot_rep, 1)
    surf.set_at((13, 83), (105, 175, 90))
    surf.set_at((15, 82), (72, 142, 68))
    surf.set_at((17, 83), (115, 185, 98))
    surf.set_at((19, 84), (72, 142, 68))
    pts_enredadera = [(12, 94), (10, 101), (13, 108), (9, 116), (12, 124), (10, 131)]
    for i in range(len(pts_enredadera) - 1):
        pygame.draw.line(surf, (60, 120, 55), pts_enredadera[i], pts_enredadera[i+1], 1)
    for px, py in [(9, 98), (14, 105), (8, 113), (14, 120), (9, 128)]:
        pygame.draw.circle(surf, (95, 168, 85), (px, py), 2)
        surf.set_at((px, py), (140, 205, 125))

    # c) Perchero de madera de pie con prendas colgadas (x = 6..44, y = 142..288)
    cx_perch = 24
    pygame.draw.circle(surf, (205, 150, 95), (cx_perch, 144), 3)
    surf.set_at((cx_perch, 143), (240, 190, 140))
    pygame.draw.line(surf, (165, 112, 68), (cx_perch, 147), (cx_perch, 280), 2)
    pygame.draw.line(surf, (205, 155, 105), (cx_perch - 1, 147), (cx_perch - 1, 280), 1)
    pygame.draw.line(surf, (115, 75, 42), (cx_perch + 1, 147), (cx_perch + 1, 280), 1)

    pygame.draw.line(surf, (155, 105, 62), (cx_perch, 154), (cx_perch - 11, 149), 2)
    pygame.draw.circle(surf, (195, 145, 95), (cx_perch - 11, 149), 2)
    pygame.draw.line(surf, (155, 105, 62), (cx_perch, 154), (cx_perch + 11, 149), 2)
    pygame.draw.circle(surf, (195, 145, 95), (cx_perch + 11, 149), 2)

    # Prendas colgadas:
    # 1. Chaqueta coral
    pts_tapado = [
        (cx_perch - 11, 151), (cx_perch - 1, 155), (cx_perch, 205),
        (cx_perch - 7, 208), (cx_perch - 17, 204), (cx_perch - 19, 172)
    ]
    pygame.draw.polygon(surf, (230, 115, 98), pts_tapado)
    pygame.draw.polygon(surf, (175, 78, 65), pts_tapado, 1)
    pygame.draw.line(surf, (248, 155, 138), (cx_perch - 6, 155), (cx_perch - 6, 205), 1)
    for by in [165, 175, 185]:
        surf.set_at((cx_perch - 8, by), (255, 235, 160))

    # 2. Bufanda celeste abrigada
    pts_bufanda = [
        (cx_perch - 5, 162), (cx_perch + 7, 160), (cx_perch + 10, 192),
        (cx_perch + 5, 195), (cx_perch + 2, 170), (cx_perch - 4, 168)
    ]
    pygame.draw.polygon(surf, (125, 188, 218), pts_bufanda)
    pygame.draw.polygon(surf, (85, 140, 168), pts_bufanda, 1)
    for fx in range(cx_perch + 5, cx_perch + 11, 2):
        surf.set_at((fx, 196), (125, 188, 218))

    # 3. Suéter mostaza
    pts_sueter = [
        (cx_perch + 2, 152), (cx_perch + 12, 151), (cx_perch + 14, 180),
        (cx_perch + 9, 182), (cx_perch + 3, 172)
    ]
    pygame.draw.polygon(surf, (242, 195, 88), pts_sueter)
    pygame.draw.polygon(surf, (180, 138, 52), pts_sueter, 1)

    # Patas de madera
    pygame.draw.line(surf, (140, 92, 55), (cx_perch, 276), (cx_perch - 13, 287), 2)
    pygame.draw.line(surf, (140, 92, 55), (cx_perch, 276), (cx_perch + 13, 287), 2)
    pygame.draw.line(surf, (110, 70, 40), (cx_perch, 276), (cx_perch, 289), 2)

    # =========================================================================
    # 6. ELEMENTOS DECORATIVOS: LADO DERECHO
    # =========================================================================
    # a) Repisa de madera en la pared derecha (x = 590..634, y = 88..92)
    r_rep2 = pygame.Rect(590, 88, 42, 5)
    pygame.draw.rect(surf, (175, 120, 72), r_rep2, border_radius=1)
    pygame.draw.rect(surf, (215, 165, 115), (r_rep2.left, r_rep2.top, r_rep2.width, 2))
    pygame.draw.rect(surf, (115, 75, 40), r_rep2, 1)
    pygame.draw.polygon(surf, (135, 85, 50), [(595, 93), (599, 93), (595, 100)])
    pygame.draw.polygon(surf, (135, 85, 50), [(625, 93), (629, 93), (629, 100)])

    # Cajas sombrereras
    r_box1 = pygame.Rect(594, 71, 22, 17)
    pygame.draw.rect(surf, (244, 182, 190), r_box1, border_radius=3)
    pygame.draw.rect(surf, (255, 238, 240), (r_box1.left, r_box1.top, r_box1.width, 4), border_radius=2)
    pygame.draw.rect(surf, (185, 120, 130), r_box1, 1, border_radius=3)
    pygame.draw.rect(surf, (230, 110, 95), (r_box1.centerx - 2, r_box1.top, 4, r_box1.height))

    r_box2 = pygame.Rect(597, 56, 16, 15)
    pygame.draw.rect(surf, (252, 212, 185), r_box2, border_radius=3)
    pygame.draw.rect(surf, (255, 246, 235), (r_box2.left, r_box2.top, r_box2.width, 4), border_radius=2)
    pygame.draw.rect(surf, (195, 145, 120), r_box2, 1, border_radius=3)
    pygame.draw.rect(surf, (235, 185, 75), (r_box2.centerx - 1, r_box2.top, 3, r_box2.height))
    surf.set_at((r_box2.centerx - 2, r_box2.top - 1), (235, 185, 75))
    surf.set_at((r_box2.centerx + 2, r_box2.top - 1), (235, 185, 75))
    surf.set_at((r_box2.centerx, r_box2.top - 1), (255, 220, 110))

    # Florerito decorativo
    r_vaso = pygame.Rect(620, 74, 9, 14)
    pygame.draw.rect(surf, (175, 215, 230), r_vaso, border_radius=3)
    pygame.draw.rect(surf, (230, 245, 252), (r_vaso.left + 1, r_vaso.top + 2, 2, 10))
    pygame.draw.rect(surf, (120, 160, 175), r_vaso, 1, border_radius=3)
    pygame.draw.line(surf, (140, 100, 65), (624, 74), (622, 65))
    pygame.draw.line(surf, (140, 100, 65), (625, 74), (627, 63))
    pygame.draw.circle(surf, (248, 165, 165), (622, 64), 2)
    pygame.draw.circle(surf, (252, 210, 140), (627, 62), 2)

    # b) Soporte / maniquí con sombrero (posicionado a x = 556..580, y = 100..144)
    cx_man = 566
    pygame.draw.ellipse(surf, (165, 112, 68), (cx_man - 7, 141, 15, 5))
    pygame.draw.ellipse(surf, (205, 155, 105), (cx_man - 6, 142, 13, 2))
    pygame.draw.line(surf, (155, 105, 65), (cx_man, 126), (cx_man, 142), 2)
    pygame.draw.circle(surf, (225, 185, 145), (cx_man, 122), 6)

    pygame.draw.ellipse(surf, (185, 75, 70), (cx_man - 14, 117, 28, 8))
    pygame.draw.ellipse(surf, (215, 105, 100), (cx_man - 13, 118, 26, 5))
    r_copa = pygame.Rect(cx_man - 7, 108, 15, 10)
    pygame.draw.rect(surf, (185, 75, 70), r_copa, border_radius=4)
    pygame.draw.rect(surf, (220, 110, 105), (r_copa.left + 2, r_copa.top + 1, r_copa.width - 4, 3))
    pygame.draw.rect(surf, (255, 245, 230), (r_copa.left, r_copa.bottom - 3, r_copa.width, 3))
    surf.set_at((r_copa.right + 1, r_copa.top + 2), (255, 220, 120))

    # c) Espejo grande de cuerpo entero con marco de madera (x = 590..630, y = 138..288)
    cx_esp = 610
    w_esp = 38
    h_esp = 142
    r_esp_marco = pygame.Rect(cx_esp - w_esp // 2, 138, w_esp, h_esp)

    pygame.draw.line(surf, (135, 88, 50), (r_esp_marco.left + 2, r_esp_marco.bottom - 10), (r_esp_marco.left - 5, r_esp_marco.bottom + 6), 3)
    pygame.draw.line(surf, (135, 88, 50), (r_esp_marco.right - 2, r_esp_marco.bottom - 10), (r_esp_marco.right + 5, r_esp_marco.bottom + 6), 3)

    pygame.draw.rect(surf, (165, 112, 68), r_esp_marco, border_radius=8)
    pygame.draw.circle(surf, (195, 145, 95), (cx_esp, r_esp_marco.top + 2), 4)
    surf.set_at((cx_esp, r_esp_marco.top + 1), (240, 190, 135))
    pygame.draw.rect(surf, (115, 75, 42), r_esp_marco, 1, border_radius=8)
    pygame.draw.rect(surf, (215, 165, 115), (r_esp_marco.left + 1, r_esp_marco.top + 1, r_esp_marco.width - 2, r_esp_marco.height - 2), 1, border_radius=7)

    r_vidrio = pygame.Rect(r_esp_marco.left + 3, r_esp_marco.top + 6, r_esp_marco.width - 6, r_esp_marco.height - 10)
    pygame.draw.rect(surf, (218, 234, 244), r_vidrio, border_radius=5)
    pygame.draw.rect(surf, (235, 222, 224), (r_vidrio.left, r_vidrio.top + 20, r_vidrio.width, r_vidrio.height - 35))

    for d in range(12):
        surf.set_at((r_vidrio.left + 5 + d, r_vidrio.top + 8 + d * 2), (255, 255, 255))
        surf.set_at((r_vidrio.left + 6 + d, r_vidrio.top + 8 + d * 2), (255, 255, 255))
        if d < 18:
            surf.set_at((r_vidrio.left + 4 + d, r_vidrio.top + 45 + d * 2), (255, 255, 255))
            surf.set_at((r_vidrio.left + 5 + d, r_vidrio.top + 45 + d * 2), (255, 255, 255))

    pygame.draw.circle(surf, (210, 160, 100), (r_esp_marco.left - 1, r_esp_marco.top + 60), 3)
    pygame.draw.circle(surf, (210, 160, 100), (r_esp_marco.right + 1, r_esp_marco.top + 60), 3)

    return pygame.transform.scale(surf, (W, H))


def _obtener_fondo_personajes(ancho: int = 1280, alto: int = 720) -> "pygame.Surface":
    global _fondo_camerino_personajes_cache
    if _fondo_camerino_personajes_cache is None:
        _fondo_camerino_personajes_cache = _generar_fondo_camerino_personajes(ancho, alto)
    return _fondo_camerino_personajes_cache


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


def _init_copos_opciones(ancho: int = 1280, alto: int = 720) -> None:
    global _copos_opciones
    rnd = _random.Random(1337)
    _copos_opciones = [
        {
            "x": rnd.uniform(0, ancho),
            "y": rnd.uniform(0, alto),
            "vy": rnd.uniform(0.5, 1.4),
            "vx": rnd.uniform(-0.3, 0.3),
            "r": rnd.choice([1, 2, 2, 3]),
            "alpha": rnd.randint(120, 210),
        }
        for _ in range(45)
    ]


def _dibujar_copos_opciones(pantalla: "pygame.Surface") -> None:
    global _copos_opciones
    if not _copos_opciones:
        _init_copos_opciones(pantalla.get_width(), pantalla.get_height())
    w, h = pantalla.get_size()
    for c in _copos_opciones:
        c["x"] += c["vx"]
        c["y"] += c["vy"]
        if c["y"] > h:
            c["y"] = -4
            c["x"] = _random.uniform(0, w)
        if c["x"] < 0:
            c["x"] = w
        elif c["x"] > w:
            c["x"] = 0
        r = c["r"]
        surf_c = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf_c, (235, 245, 255, c["alpha"]), (r, r), r)
        pantalla.blit(surf_c, (int(c["x"]) - r, int(c["y"]) - r))


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


def obtener_geometria_panel_partidas(ancho_menu, alto_menu, tiene_partidas=True):
    """
    Calcula dinámicamente las dimensiones y posiciones del panel y botones
    de la pantalla de partidas guardadas adaptadas al formato Diario de Aventuras.
    Garantiza que «VOLVER» y «NUEVA PARTIDA» queden perfectamente centrados juntos
    y sin colisión vertical con la paginación ni con las fichas de registro.
    """
    ancho_panel = min(960, max(680, ancho_menu - 80))
    alto_panel = 448
    x_panel = (ancho_menu - ancho_panel) // 2
    y_panel = 96
    rect_panel = pygame.Rect(x_panel, y_panel, ancho_panel, alto_panel)

    y_btns_inf = 620
    w_btn, h_btn = 238, 70
    gap_btns = 24

    if tiene_partidas:
        total_w = w_btn * 2 + gap_btns
        x_inicio = (ancho_menu - total_w) // 2
        btn_volver = pygame.Rect(x_inicio, y_btns_inf, w_btn, h_btn)
        btn_nueva = pygame.Rect(x_inicio + w_btn + gap_btns, y_btns_inf, w_btn, h_btn)
    else:
        btn_volver = pygame.Rect((ancho_menu - w_btn) // 2, y_btns_inf, w_btn, h_btn)
        btn_nueva = pygame.Rect(0, 0, 0, 0)

    btn_iniciar_primera = pygame.Rect(rect_panel.centerx - 136, rect_panel.centery + 35, 272, 80)

    return rect_panel, btn_volver, btn_nueva, btn_iniciar_primera


def obtener_geometria_tarjeta_partida(rect_panel, idx_slot, alto_card=90, gap_cards=6):
    """
    Calcula los rectángulos de cada elemento dentro de la ficha de registro de partida:
    - r_card: rectángulo general de la ficha (papel antiguo, altura optimizada 90 px)
    - r_badge: rectángulo del sello/badge de mundo a la izquierda
    - r_btn_cargar: botón principal «CARGAR» (126x38)
    - r_btn_gestionar: botón de administración «GESTIONAR» (118x38)
    - r_btn_borrar: botón secundario «BORRAR» (96x38)
    - (x_texto, ancho_max_texto): zona exclusiva para los textos y metadatos organizados en 2 líneas
    """
    r_card = pygame.Rect(
        rect_panel.left + 20,
        rect_panel.top + 12 + idx_slot * (alto_card + gap_cards),
        rect_panel.width - 40,
        alto_card,
    )

    # Badge de mundo / expedición a la izquierda
    w_badge, h_badge = 112, 48
    r_badge = pygame.Rect(r_card.left + 16, r_card.centery - (h_badge // 2), w_badge, h_badge)

    # Botones a la derecha
    w_borrar = 96
    w_gestionar = 118
    w_cargar = 126
    h_btn = 38
    gap_btns = 10
    margin_der = 16

    r_btn_borrar = pygame.Rect(r_card.right - margin_der - w_borrar, r_card.centery - (h_btn // 2), w_borrar, h_btn)
    r_btn_gestionar = pygame.Rect(r_btn_borrar.left - gap_btns - w_gestionar, r_card.centery - (h_btn // 2), w_gestionar, h_btn)
    r_btn_cargar = pygame.Rect(r_btn_gestionar.left - gap_btns - w_cargar, r_card.centery - (h_btn // 2), w_cargar, h_btn)

    # Zona disponible para información textual a la izquierda de los botones
    x_texto = r_badge.right + 18
    x_limite_texto = r_btn_cargar.left - 14
    ancho_max_texto = max(80, x_limite_texto - x_texto)

    return r_card, r_badge, r_btn_cargar, r_btn_gestionar, r_btn_borrar, (x_texto, ancho_max_texto)


def dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel, pos_mouse, fuentes, sprites_botones=None):
    """
    Dibuja una ficha de registro dentro del diario antiguo de expediciones.
    - Ficha de papel antiguo con bordes envejecidos y tira de lomo decorativa.
    - Sello heráldico de expedición para el mundo alcanzado.
    - Símbolo de aventura dorado, nombre y detalles con iconos pixel art (candado y diario).
    - Botones de acción integrados a la paleta cálida (verde oliva, pergamino tostado y terracota).
    """
    r_card, r_badge, r_btn_cargar, r_btn_gestionar, r_btn_borrar, (x_texto, ancho_max_texto) = obtener_geometria_tarjeta_partida(rect_panel, idx_slot)

    hov_card = r_card.collidepoint(pos_mouse)
    hov_cargar = r_btn_cargar.collidepoint(pos_mouse)
    hov_gestionar = r_btn_gestionar.collidepoint(pos_mouse)
    hov_borrar = r_btn_borrar.collidepoint(pos_mouse)

    # 1. Base de la ficha: papel antiguo con sutil sombreado y borde cálido
    col_card = (255, 253, 245) if hov_card else (253, 248, 238)
    borde_card = (210, 130, 45) if hov_card else (185, 150, 110)
    pygame.draw.rect(pantalla, col_card, r_card, border_radius=12)
    pygame.draw.rect(pantalla, borde_card, r_card, width=3 if hov_card else 2, border_radius=12)

    # Filete perimetral interior suave estilo documento antiguo
    pygame.draw.rect(pantalla, (235, 220, 195), r_card.inflate(-6, -6), width=1, border_radius=8)

    # Tira de lomo / acento decorativo a la izquierda
    col_tira = (195, 120, 50) if hov_card else (160, 120, 80)
    pygame.draw.rect(pantalla, col_tira, (r_card.left + 3, r_card.top + 8, 4, r_card.height - 16), border_radius=2)

    # 2. Sello / Badge de Mundo y Expedición
    m_val = p.get("mundo_max", 1)
    info_b = COLORES_TABS.get(m_val, COLORES_TABS[1])
    pygame.draw.rect(pantalla, info_b["fondo"], r_badge, border_radius=8)
    pygame.draw.rect(pantalla, info_b["borde"], r_badge, width=2, border_radius=8)
    pygame.draw.rect(pantalla, (245, 235, 220), r_badge.inflate(-4, -4), width=1, border_radius=6)

    fuente_badge = fuentes.get("badge", fuentes.get("btn"))
    txt_badge = f"{t('mundo')} {m_val}"
    f_badge = obtener_fuente_para_texto(txt_badge, categoria="botones", tamano=TAMANO_BADGE)
    t_badge = f_badge.render(txt_badge, True, info_b["texto"])
    pantalla.blit(t_badge, t_badge.get_rect(center=r_badge.center))

    # 3. Metadatos de la aventura
    nombre = obtener_nombre_partida_visible(p)
    es_adm = es_partida_admin(p)
    mundo_max = p.get("mundo_max", 1)
    nivel_max = p.get("nivel_max", 1)
    fecha = p.get("fecha", "")
    cant_comp = calcular_niveles_completados(p.get("niveles_desbloqueados", {}), es_admin=es_adm)
    tiene_pwd = p.get("tiene_password", False)

    # Símbolo decorativo de aventura: diamante / gema dorada pixel art
    diam_cx = x_texto + 4
    diam_cy = r_card.top + 18
    for d_diam in range(-4, 5):
        w_diam = 4 - abs(d_diam)
        for dx in range(-w_diam, w_diam + 1):
            c_d = (245, 215, 110) if (d_diam <= 0 and dx <= 0) else (210, 145, 35)
            pantalla.set_at((diam_cx + dx, diam_cy + d_diam), c_d)

    # Línea 1: Nombre de la partida en sepia profundo con soporte para clave
    cur_x_tit = x_texto + 16
    if tiene_pwd:
        _dibujar_icono_candado(pantalla, cur_x_tit + 3, r_card.top + 18, abierto=False)
        cur_x_tit += 14

    rect_tit_card = pygame.Rect(cur_x_tit, r_card.top + 7, ancho_max_texto - (cur_x_tit - x_texto), 24)
    dibujar_texto_en_rect(pantalla, nombre, rect_tit_card, categoria="subtitulo", tamano=21, color=(55, 42, 30), negrita=True, alineacion="izquierda", padding=0)

    # Metadatos ampliados (+60% a +70%, tamano=28) distribuidos en dos líneas claras sin superposiciones
    partes_f = fecha.strip().split(" ") if fecha else []
    str_fecha = partes_f[0] if len(partes_f) > 0 else ""
    str_hora = partes_f[1] if len(partes_f) > 1 else ""
    tiene_fecha_hora = bool(str_fecha or str_hora)

    # Línea 2: Nivel alcanzado y Progreso de expedición
    y_fila2 = (r_card.top + 35) if tiene_fecha_hora else (r_card.top + 45)
    cur_x2 = x_texto + 4

    # 1. Nivel alcanzado
    _dibujar_icono_estrella_nivel(pantalla, cur_x2 + 5, y_fila2 + 14)
    cur_x2 += 16
    str_niv = f"{t('nivel')} {mundo_max}-{nivel_max}"
    f_niv = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_niv) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
    t_niv = f_niv.render(str_niv, True, (75, 48, 30))
    pantalla.blit(t_niv, (cur_x2, y_fila2))
    cur_x2 += t_niv.get_width() + 14

    # Separador sutil
    pygame.draw.circle(pantalla, (180, 150, 120), (cur_x2, y_fila2 + 14), 2)
    cur_x2 += 10

    # 2. Niveles completados
    _dibujar_icono_trofeo(pantalla, cur_x2 + 6, y_fila2 + 14)
    cur_x2 += 18
    tot_niv = TOTAL_NIVELES_ADMIN if es_adm else TOTAL_NIVELES_NORMALES
    str_comp = f"{cant_comp}/{tot_niv} {t('completados')}"
    f_comp = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_comp) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
    t_comp = f_comp.render(str_comp, True, (90, 65, 45))
    pantalla.blit(t_comp, (cur_x2, y_fila2))

    # Línea 3: Fecha y Hora (perfectamente alineadas debajo, aprovechando el ancho con holgura segura)
    if tiene_fecha_hora:
        y_fila3 = r_card.top + 61
        cur_x3 = x_texto + 4
        

        # 3. Fecha
        if str_fecha:
            _dibujar_icono_calendario(pantalla, cur_x3 + 6, y_fila3 + 14)
            cur_x3 += 16
            f_fec = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_fecha) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
            t_fec = f_fec.render(str_fecha, True, (105, 80, 60))
            pantalla.blit(t_fec, (cur_x3, y_fila3))
            cur_x3 += t_fec.get_width() + 16

        # 4. Hora
        if str_hora:
            _dibujar_icono_reloj(pantalla, cur_x3 + 6, y_fila3 + 14)
            cur_x3 += 16
            f_hor = obtener_fuente_cjk(16, negrita=False) if contiene_caracteres_cjk(str_hora) else (fuentes.get("sub_card") or obtener_fuente_pequena(28))
            t_hor = f_hor.render(str_hora, True, (105, 80, 60))
            pantalla.blit(t_hor, (cur_x3, y_fila3))

    # 4. Botón «CARGAR» (Verde bosque cálido de expedición - Sprite oficial)
    if sprites_botones and sprites_botones.get("cargar_normal"):
        spr_cn = sprites_botones["cargar_normal"]
        spr_ch = sprites_botones.get("cargar_hover")
        pantalla.blit(spr_ch if (hov_cargar and spr_ch) else spr_cn, r_btn_cargar)
    else:
        col_bc = (78, 155, 82) if hov_cargar else (65, 138, 72)
        borde_bc = (22, 45, 24)
        pygame.draw.rect(pantalla, col_bc, r_btn_cargar, border_radius=8)
        pygame.draw.rect(pantalla, borde_bc, r_btn_cargar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, t("cargar"), r_btn_cargar, categoria="boton", tamano=14, color=(255, 255, 255), padding=4)

    # 5. Botón «GESTIONAR» (Pergamino tostado - Sprite oficial)
    if sprites_botones and sprites_botones.get("gestionar_normal"):
        spr_gn = sprites_botones["gestionar_normal"]
        spr_gh = sprites_botones.get("gestionar_hover")
        pantalla.blit(spr_gh if (hov_gestionar and spr_gh) else spr_gn, r_btn_gestionar)
    else:
        col_bg = (255, 252, 246) if hov_gestionar else (246, 238, 224)
        borde_bg = (150, 115, 80) if hov_gestionar else (185, 155, 120)
        pygame.draw.rect(pantalla, col_bg, r_btn_gestionar, border_radius=8)
        pygame.draw.rect(pantalla, borde_bg, r_btn_gestionar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, t("gestionar"), r_btn_gestionar, categoria="boton", tamano=13, color=(82, 83, 83), padding=4)

    # 6. Botón «BORRAR» (Terracota cálido suave - Sprite oficial) - Oculto y protegido para la partida especial de Administrador
    if not es_adm:
        if sprites_botones and sprites_botones.get("borrar_normal"):
            spr_bn = sprites_botones["borrar_normal"]
            spr_bh = sprites_botones.get("borrar_hover")
            pantalla.blit(spr_bh if (hov_borrar and spr_bh) else spr_bn, r_btn_borrar)
        else:
            col_bb = (235, 95, 85) if hov_borrar else (205, 80, 70)
            borde_bb = (255, 255, 255) if hov_borrar else (150, 50, 45)
            pygame.draw.rect(pantalla, col_bb, r_btn_borrar, border_radius=8)
            pygame.draw.rect(pantalla, borde_bb, r_btn_borrar, width=2, border_radius=8)
            dibujar_texto_en_rect(pantalla, t("borrar"), r_btn_borrar, categoria="boton", tamano=14, color=(125, 48, 17), padding=4)
    else:
        r_btn_borrar = pygame.Rect(0, 0, 0, 0)

    return r_card, r_btn_cargar, r_btn_gestionar, r_btn_borrar


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


def _eventos_modo_juego(m, evento):
    """Clic izquierdo en la pantalla «modo_juego». Devuelve True si hay que cortar el resto de eventos del frame."""
    m.f_limp_modo = _obtener_fondo_modo_juego(m.ANCHO_MENU, m.ALTO_MENU)
    m.idm_act = obtener_idioma()
    if m.btn_continuar.collidepoint(evento.pos):
        m.sp_c_s = m._obtener_boton_modo("continuar", "semi", m.idm_act)
        m.sp_c_a = m._obtener_boton_modo("continuar", "apretado", m.idm_act)
        m.sp_c_n = m._obtener_boton_modo("continuar", "normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_continuar, m.sp_c_s, m.sp_c_a, m.f_limp_modo, m.sp_c_n, tipo_sonido="menu"):
            m.pagina_partidas = 0
            m.estado_actual = ESTADO_LISTA_PARTIDAS
    elif m.btn_nueva_partida.collidepoint(evento.pos):
        m.sp_n_s = m._obtener_boton_modo("nueva_partida", "semi", m.idm_act)
        m.sp_n_a = m._obtener_boton_modo("nueva_partida", "apretado", m.idm_act)
        m.sp_n_n = m._obtener_boton_modo("nueva_partida", "normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_nueva_partida, m.sp_n_s, m.sp_n_a, m.f_limp_modo, m.sp_n_n, tipo_sonido="partida_nueva"):
            m.nueva_p = flujo_crear_nueva_partida(
                m.pantalla, m.reloj,
                color_p1=m.color_p1, color_p2=m.color_p2,
                accesorio_p1=m.accesorio_p1, accesorio_p2=m.accesorio_p2,
            )
            if m.nueva_p is not None:
                m.personalizacion_modificada_en_menu = False
                m.niveles_desbloqueados = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                m.snapshot_guardado = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                m.partida_actual_id = m.nueva_p["id"]
                m.partida_actual_nombre = m.nueva_p["nombre"]
                m.partida_actual_password = m.nueva_p.get("password_plain", "")
                m.partida_creada_flag = True
                m.sesion_activa = True
                m.mundo_seleccionado = 1
                m.fin_acc, m.mundo_seleccionado = jugar_niveles_desde(
                    1, 0,
                    m.color_p1, m.color_p2,
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
    elif m.btn_volver_modo.collidepoint(evento.pos):
        m.sp_v_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_v_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_v_n = m._obtener_boton_volver("normal", m.idm_act)
        if animar_pulsacion_boton(m.pantalla, m.btn_volver_modo, m.sp_v_s, m.sp_v_a, m.f_limp_modo, m.sp_v_n, tipo_sonido="ventana_volver"):
            m.estado_actual = ESTADO_MENU_PRINCIPAL
    return False


def _eventos_lista_partidas(m, evento):
    """Clic izquierdo en la pantalla «lista_partidas». Devuelve True si hay que cortar el resto de eventos del frame."""
    m.partidas_guardadas = cargar_partidas()
    m.rect_panel_partidas, m.btn_volver_partidas, m.btn_nueva_desde_lista, m.btn_iniciar_primera = (
        obtener_geometria_panel_partidas(m.ANCHO_MENU, m.ALTO_MENU, bool(m.partidas_guardadas))
    )
    m.total_p = len(m.partidas_guardadas)
    m.total_paginas = max(1, (m.total_p + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
    if m.pagina_partidas >= m.total_paginas:
        m.pagina_partidas = max(0, m.total_paginas - 1)

    m.idm_act = obtener_idioma()
    m.dict_sp_act = m._obtener_sprites_tarjeta(m.idm_act)

    if not m.partidas_guardadas:
        if m.btn_iniciar_primera.collidepoint(evento.pos):
            m.pulsado = True
            m.sp_pr_semi = m._obtener_boton_primera_partida("semi", m.idm_act)
            m.sp_pr_apret = m._obtener_boton_primera_partida("apretado", m.idm_act)
            m.sp_pr_norm = m._obtener_boton_primera_partida("normal", m.idm_act)
            if m.sp_pr_semi and m.sp_pr_apret:
                m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_iniciar_primera, m.sp_pr_semi, m.sp_pr_apret, (252, 248, 238), m.sp_pr_norm, tipo_sonido="partida_nueva")
            if m.pulsado:
                m.nueva_p = flujo_crear_nueva_partida(
                    m.pantalla, m.reloj,
                    color_p1=m.color_p1, color_p2=m.color_p2,
                    accesorio_p1=m.accesorio_p1, accesorio_p2=m.accesorio_p2,
                )
                if m.nueva_p is not None:
                    m.personalizacion_modificada_en_menu = False
                    m.niveles_desbloqueados = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                    m.snapshot_guardado = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                    m.partida_actual_id = m.nueva_p["id"]
                    m.partida_actual_nombre = m.nueva_p["nombre"]
                    m.partida_actual_password = m.nueva_p.get("password_plain", "")
                    m.partida_creada_flag = True
                    m.sesion_activa = True
                    m.mundo_seleccionado = 1
                    m.fin_acc, m.mundo_seleccionado = jugar_niveles_desde(
                        1, 0,
                        m.color_p1, m.color_p2,
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
    else:
        m.inicio_idx = m.pagina_partidas * m.MAX_PARTIDAS_POR_PAGINA
        m.fin_idx = m.inicio_idx + m.MAX_PARTIDAS_POR_PAGINA
        m.partidas_pagina = m.partidas_guardadas[m.inicio_idx:m.fin_idx]

        m.accion_ejecutada = False
        for m.idx_slot, m.p in enumerate(m.partidas_pagina):
            m.r_card, m._, m.r_btn_cargar, m.r_btn_gestionar, m.r_btn_borrar, m._ = obtener_geometria_tarjeta_partida(
                m.rect_panel_partidas, m.idx_slot
            )
            # Clic en botón BORRAR (dispara confirmación previa con advertencia)
            if m.r_btn_borrar.collidepoint(evento.pos):
                m.pulsado = True
                m.spr_b_s = m.dict_sp_act.get("borrar_semi")
                m.spr_b_a = m.dict_sp_act.get("borrar_apretado")
                m.spr_b_n = m.dict_sp_act.get("borrar_normal")
                if m.spr_b_s and m.spr_b_a:
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.r_btn_borrar, m.spr_b_s, m.spr_b_a, (253, 246, 233), m.spr_b_n, tipo_sonido="partida_borrar")
                if m.pulsado:
                    if mostrar_dialogo_confirmar_borrado(m.pantalla, m.reloj, m.p):
                        eliminar_partida(m.p["id"])
                        if m.partida_actual_id == m.p["id"]:
                            m.partida_actual_id = None
                            m.partida_actual_nombre = None
                            m.partida_actual_password = None
                            m.niveles_desbloqueados = crear_desbloqueados_inicial()
                            m.snapshot_guardado = copy.deepcopy(m.niveles_desbloqueados)
                            m.sesion_activa = False
                            m.partida_cargada_flag = False
                            m.partida_creada_flag = False
                        m.nuevas_p = cargar_partidas()
                        m.nuevas_total_pag = max(1, (len(m.nuevas_p) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
                        if m.pagina_partidas >= m.nuevas_total_pag:
                            m.pagina_partidas = max(0, m.nuevas_total_pag - 1)
                m.accion_ejecutada = True
                break

            # Clic en botón GESTIONAR (renombrar, cambiar/quitar clave, borrar)
            elif m.r_btn_gestionar.collidepoint(evento.pos):
                m.pulsado = True
                m.spr_g_s = m.dict_sp_act.get("gestionar_semi")
                m.spr_g_a = m.dict_sp_act.get("gestionar_apretado")
                m.spr_g_n = m.dict_sp_act.get("gestionar_normal")
                if m.spr_g_s and m.spr_g_a:
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.r_btn_gestionar, m.spr_g_s, m.spr_g_a, (253, 246, 233), m.spr_g_n, tipo_sonido="partida_gestionar")
                if m.pulsado:
                    if modal_administrar_perfil(m.pantalla, m.reloj, m.p):
                        m.nuevas_p = cargar_partidas()
                        m.nuevas_total_pag = max(1, (len(m.nuevas_p) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
                        if m.pagina_partidas >= m.nuevas_total_pag:
                            m.pagina_partidas = max(0, m.nuevas_total_pag - 1)
                m.accion_ejecutada = True
                break

            # Clic en botón CARGAR (única y exclusivamente sobre r_btn_cargar)
            elif m.r_btn_cargar.collidepoint(evento.pos):
                m.pulsado = True
                m.spr_c_s = m.dict_sp_act.get("cargar_semi")
                m.spr_c_a = m.dict_sp_act.get("cargar_apretado")
                m.spr_c_n = m.dict_sp_act.get("cargar_normal")
                if m.spr_c_s and m.spr_c_a:
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.r_btn_cargar, m.spr_c_s, m.spr_c_a, (253, 246, 233), m.spr_c_n, tipo_sonido="partida_cargar")
                if m.pulsado:
                    if m.p.get("tiene_password", False):
                        if not pedir_password_modal(m.pantalla, m.reloj, m.p):
                            pygame.event.clear()
                            m.accion_ejecutada = True
                            break
                        pygame.event.clear()

                    m.atuendo_guardado = (
                        m.p.get("color_p1", "Celeste"),
                        m.p.get("color_p2", "Violeta"),
                        m.p.get("accesorio_p1", "Ninguno"),
                        m.p.get("accesorio_p2", "Ninguno"),
                    )
                    m.atuendo_actual = (m.color_p1, m.color_p2, m.accesorio_p1, m.accesorio_p2)
                    m.hay_cambios_pendientes = m.personalizacion_modificada_en_menu and (m.atuendo_actual != m.atuendo_guardado)

                    if m.hay_cambios_pendientes:
                        m.decision = mostrar_dialogo_confirmar_atuendos(
                            m.pantalla, m.reloj, m.p,
                            color_p1_nuevo=m.color_p1,
                            color_p2_nuevo=m.color_p2,
                            acc_p1_nuevo=m.accesorio_p1,
                            acc_p2_nuevo=m.accesorio_p2,
                        )
                        if m.decision == "cancelar":
                            pygame.event.clear()
                            m.accion_ejecutada = True
                            break
                        elif m.decision == "mantener":
                            m.color_p1, m.color_p2, m.accesorio_p1, m.accesorio_p2 = m.atuendo_guardado
                            m.personalizacion_modificada_en_menu = False
                        elif m.decision == "cambiar":
                            m.p_actualizada = guardar_partida(
                                niveles_desbloqueados=m.p["niveles_desbloqueados"],
                                id_partida=m.p["id"],
                                nombre_partida=m.p["nombre"],
                                password_hash=m.p.get("password_hash"),
                                password_salt=m.p.get("password_salt"),
                                color_p1=m.color_p1,
                                color_p2=m.color_p2,
                                accesorio_p1=m.accesorio_p1,
                                accesorio_p2=m.accesorio_p2,
                            )
                            if m.p_actualizada:
                                m.p["color_p1"] = m.color_p1
                                m.p["color_p2"] = m.color_p2
                                m.p["accesorio_p1"] = m.accesorio_p1
                                m.p["accesorio_p2"] = m.accesorio_p2
                            m.personalizacion_modificada_en_menu = False
                    else:
                        m.color_p1, m.color_p2, m.accesorio_p1, m.accesorio_p2 = m.atuendo_guardado
                        m.personalizacion_modificada_en_menu = False

                    m.niveles_desbloqueados = copy.deepcopy(m.p["niveles_desbloqueados"])
                    m.snapshot_guardado = copy.deepcopy(m.p["niveles_desbloqueados"])
                    m.partida_actual_id = m.p["id"]
                    m.partida_actual_nombre = m.p["nombre"]
                    m.partida_actual_password = None
                    m.partida_cargada_flag = True
                    m.sesion_activa = True
                    m.mundo_seleccionado = m.p["mundo_max"]
                    m.estado_actual = ESTADO_SELECCION_NIVEL
                    m.accion_ejecutada = True
                    break

        if not m.accion_ejecutada:
            if m.total_paginas > 1:
                m.btn_pag_ant = pygame.Rect(m.rect_panel_partidas.centerx - 120, 508, 36, 32)
                m.btn_pag_sig = pygame.Rect(m.rect_panel_partidas.centerx + 84, 508, 36, 32)
                if m.btn_pag_ant.collidepoint(evento.pos) and m.pagina_partidas > 0:
                    m.pagina_partidas -= 1
                    reproducir_sonido_ui("pagina")
                elif m.btn_pag_sig.collidepoint(evento.pos) and m.pagina_partidas < m.total_paginas - 1:
                    m.pagina_partidas += 1
                    reproducir_sonido_ui("pagina")

            if m.btn_nueva_desde_lista.collidepoint(evento.pos):
                m.pulsado = True
                m.sp_nl_s = m._obtener_boton_nueva_lista("semi", m.idm_act)
                m.sp_nl_a = m._obtener_boton_nueva_lista("apretado", m.idm_act)
                m.sp_nl_n = m._obtener_boton_nueva_lista("normal", m.idm_act)
                if m.sp_nl_s and m.sp_nl_a:
                    m.f_limp = _obtener_fondo_partidas(m.ANCHO_MENU, m.ALTO_MENU)
                    m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_nueva_desde_lista, m.sp_nl_s, m.sp_nl_a, m.f_limp, m.sp_nl_n, tipo_sonido="partida_nueva")
                if m.pulsado:
                    m.nueva_p = flujo_crear_nueva_partida(
                        m.pantalla, m.reloj,
                        color_p1=m.color_p1, color_p2=m.color_p2,
                        accesorio_p1=m.accesorio_p1, accesorio_p2=m.accesorio_p2,
                    )
                    if m.nueva_p is not None:
                        m.personalizacion_modificada_en_menu = False
                        m.niveles_desbloqueados = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                        m.snapshot_guardado = copy.deepcopy(m.nueva_p["niveles_desbloqueados"])
                        m.partida_actual_id = m.nueva_p["id"]
                        m.partida_actual_nombre = m.nueva_p["nombre"]
                        m.partida_actual_password = m.nueva_p.get("password_plain", "")
                        m.partida_creada_flag = True
                        m.sesion_activa = True
                        m.mundo_seleccionado = 1
                        m.fin_acc, m.mundo_seleccionado = jugar_niveles_desde(
                            1, 0,
                            m.color_p1, m.color_p2,
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

    if m.btn_volver_partidas.collidepoint(evento.pos):
        m.pulsado = True
        m.sp_vp_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_vp_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_vp_n = m._obtener_boton_volver("normal", m.idm_act)
        if m.sp_vp_s and m.sp_vp_a:
            m.f_limp = _obtener_fondo_partidas(m.ANCHO_MENU, m.ALTO_MENU)
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_partidas, m.sp_vp_s, m.sp_vp_a, m.f_limp, m.sp_vp_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MODO_JUEGO
    return False


def _eventos_personajes(m, evento):
    """Clic izquierdo en la pantalla «personajes». Devuelve True si hay que cortar el resto de eventos del frame."""
    if m.btn_volver_personajes.collidepoint(evento.pos) or m.btn_guardar.collidepoint(evento.pos):
        m.pulsado = True
        m.idm_act = obtener_idioma()
        m.sp_vp_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_vp_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_vp_n = m._obtener_boton_volver("normal", m.idm_act)
        if m.sp_vp_s and m.sp_vp_a and m.btn_volver_personajes.collidepoint(evento.pos):
            m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_personajes, m.sp_vp_s, m.sp_vp_a, _obtener_fondo_personajes(m.ANCHO_MENU, m.ALTO_MENU), m.sp_vp_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MENU_PRINCIPAL
            return True

    # Pestañas [ COLORES ] y [ ACCESORIOS ]
    m.rect_tab_col = pygame.Rect(388, 83, 240, 67)
    m.rect_tab_acc = pygame.Rect(652, 83, 240, 67)

    if m.rect_tab_col.collidepoint(evento.pos):
        if m.tab_personajes_actual != "colores":
            m.tab_personajes_actual = "colores"
            reproducir_sonido_ui("tab")
    elif m.rect_tab_acc.collidepoint(evento.pos):
        if m.tab_personajes_actual != "accesorios":
            m.tab_personajes_actual = "accesorios"
            reproducir_sonido_ui("tab")
        m.acc_list_tab = obtener_accesorios_disponibles()
        for m._ia, m._acc in enumerate(m.acc_list_tab):
            if m._acc["id"] == m.accesorio_p1:
                m.pagina_acc_p1 = m._ia // 6
            if m._acc["id"] == m.accesorio_p2:
                m.pagina_acc_p2 = m._ia // 6

    # Marcos de selección (Jugador 1: izquierda=125, Jugador 2: izquierda=685)
    m.rect_f1_ev = pygame.Rect(125, 295, 470, 276)
    m.rect_f2_ev = pygame.Rect(685, 295, 470, 276)

    if m.tab_personajes_actual == "colores":
        m.w_sw, m.h_sw = 80, 45
        m.y_start_sw = 338
        m.h_paso_y = 77
        for m.r_idx, m.fila in enumerate(FILAS_COLORES_SELECCION):
            m.n = len(m.fila)
            m.gap_x = 10 if m.n == 5 else 24
            m.row_w = m.n * m.w_sw + (m.n - 1) * m.gap_x
            m.x_start_rel = (m.rect_f1_ev.width - m.row_w) // 2
            m.y_sw = m.y_start_sw + m.r_idx * m.h_paso_y
            for m.c_idx, m.color_idx in enumerate(m.fila):
                m.p_info = PERSONAJES_DISPONIBLES[m.color_idx]
                m.x_sw_rel = m.x_start_rel + m.c_idx * (m.w_sw + m.gap_x)
                m.r1 = pygame.Rect(m.rect_f1_ev.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw + 28)
                m.r2 = pygame.Rect(m.rect_f2_ev.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw + 28)

                if m.r1.collidepoint(evento.pos):
                    if m.color_p1 != m.p_info["nombre"]:
                        m.color_p1 = m.p_info["nombre"]
                        m.personalizacion_modificada_en_menu = True
                        reproducir_sonido_ui("select")
                        # Respetar accesorios exclusivos: si el equipado no le pertenece, desequipar
                        m.permitidos_p1 = [a["id"] for a in obtener_accesorios_disponibles(m.color_p1)]
                        if m.accesorio_p1 not in m.permitidos_p1:
                            m.accesorio_p1 = "Ninguno"
                if m.r2.collidepoint(evento.pos):
                    if m.color_p2 != m.p_info["nombre"]:
                        m.color_p2 = m.p_info["nombre"]
                        m.personalizacion_modificada_en_menu = True
                        reproducir_sonido_ui("select")
                        # Respetar accesorios exclusivos: si el equipado no le pertenece, desequipar
                        m.permitidos_p2 = [a["id"] for a in obtener_accesorios_disponibles(m.color_p2)]
                        if m.accesorio_p2 not in m.permitidos_p2:
                            m.accesorio_p2 = "Ninguno"

    elif m.tab_personajes_actual == "accesorios":
        m.accesorios_p1_disp = obtener_accesorios_disponibles(m.color_p1)
        m.accesorios_p2_disp = obtener_accesorios_disponibles(m.color_p2)
        m.items_por_pag = 6
        m.total_pags_p1 = max(1, (len(m.accesorios_p1_disp) + m.items_por_pag - 1) // m.items_por_pag)
        m.total_pags_p2 = max(1, (len(m.accesorios_p2_disp) + m.items_por_pag - 1) // m.items_por_pag)

        # Flechas de paginación para Jugador 1
        m.btn_prev_p1 = pygame.Rect(m.rect_f1_ev.centerx - 72, m.rect_f1_ev.top + 234, 34, 26)
        m.btn_next_p1 = pygame.Rect(m.rect_f1_ev.centerx + 38, m.rect_f1_ev.top + 234, 34, 26)
        if m.btn_prev_p1.collidepoint(evento.pos):
            m.pagina_acc_p1 = (m.pagina_acc_p1 - 1) % m.total_pags_p1
            reproducir_sonido_ui("pagina")
        elif m.btn_next_p1.collidepoint(evento.pos):
            m.pagina_acc_p1 = (m.pagina_acc_p1 + 1) % m.total_pags_p1
            reproducir_sonido_ui("pagina")

        # Flechas de paginación para Jugador 2
        m.btn_prev_p2 = pygame.Rect(m.rect_f2_ev.centerx - 72, m.rect_f2_ev.top + 234, 34, 26)
        m.btn_next_p2 = pygame.Rect(m.rect_f2_ev.centerx + 38, m.rect_f2_ev.top + 234, 34, 26)
        if m.btn_prev_p2.collidepoint(evento.pos):
            m.pagina_acc_p2 = (m.pagina_acc_p2 - 1) % m.total_pags_p2
            reproducir_sonido_ui("pagina")
        elif m.btn_next_p2.collidepoint(evento.pos):
            m.pagina_acc_p2 = (m.pagina_acc_p2 + 1) % m.total_pags_p2
            reproducir_sonido_ui("pagina")

        m.w_acc, m.h_acc, m.gap_acc_x, m.gap_acc_y = 126, 82, 16, 10
        m.ancho_fila_acc = 3 * m.w_acc + 2 * m.gap_acc_x
        m.x_offset_acc = (m.rect_f1_ev.width - m.ancho_fila_acc) // 2

        # Selección de accesorios en marco de Jugador 1
        m.inicio_p1 = m.pagina_acc_p1 * m.items_por_pag
        for m.idx_rel, m.acc in enumerate(m.accesorios_p1_disp[m.inicio_p1:m.inicio_p1 + m.items_por_pag]):
            m.r = m.idx_rel // 3
            m.c = m.idx_rel % 3
            m.x_offset_rel = m.x_offset_acc + m.c * (m.w_acc + m.gap_acc_x)
            m.y_card_a = m.rect_f1_ev.top + 42 + m.r * (m.h_acc + m.gap_acc_y)
            m.ra1 = pygame.Rect(m.rect_f1_ev.left + m.x_offset_rel, m.y_card_a, m.w_acc, m.h_acc)
            if m.ra1.collidepoint(evento.pos):
                if m.accesorio_p1 != m.acc["id"]:
                    m.accesorio_p1 = m.acc["id"]
                    m.personalizacion_modificada_en_menu = True
                    reproducir_sonido_ui("select")

        # Selección de accesorios en marco de Jugador 2
        m.inicio_p2 = m.pagina_acc_p2 * m.items_por_pag
        for m.idx_rel, m.acc in enumerate(m.accesorios_p2_disp[m.inicio_p2:m.inicio_p2 + m.items_por_pag]):
            m.r = m.idx_rel // 3
            m.c = m.idx_rel % 3
            m.x_offset_rel = m.x_offset_acc + m.c * (m.w_acc + m.gap_acc_x)
            m.y_card_a = m.rect_f2_ev.top + 42 + m.r * (m.h_acc + m.gap_acc_y)
            m.ra2 = pygame.Rect(m.rect_f2_ev.left + m.x_offset_rel, m.y_card_a, m.w_acc, m.h_acc)
            if m.ra2.collidepoint(evento.pos):
                if m.accesorio_p2 != m.acc["id"]:
                    m.accesorio_p2 = m.acc["id"]
                    m.personalizacion_modificada_en_menu = True
                    reproducir_sonido_ui("select")
    return False


def _eventos_configuracion(m, evento):
    """Clic izquierdo en la pantalla «configuracion». Devuelve True si hay que cortar el resto de eventos del frame."""
    m.idm_act = obtener_idioma()
    if m.btn_volver_config.collidepoint(evento.pos):
        m.sp_v_s = m._obtener_boton_volver("semi", m.idm_act)
        m.sp_v_a = m._obtener_boton_volver("apretado", m.idm_act)
        m.sp_v_n = m._obtener_boton_volver("normal", m.idm_act)
        m.pulsado = animar_pulsacion_boton(m.pantalla, m.btn_volver_config, m.sp_v_s, m.sp_v_a, _obtener_fondo_opciones(m.ANCHO_MENU, m.ALTO_MENU), m.sp_v_n, tipo_sonido="ventana_volver")
        if m.pulsado:
            m.estado_actual = ESTADO_MENU_PRINCIPAL
    elif m.rect_btn_sec_cfg.collidepoint(evento.pos):
        if m.seccion_opciones_actual != "configuracion":
            reproducir_sonido_ui("tab")
        m.seccion_opciones_actual = "configuracion"
    elif m.rect_btn_sec_ctrl.collidepoint(evento.pos):
        if m.seccion_opciones_actual != "controles":
            reproducir_sonido_ui("tab")
        m.seccion_opciones_actual = "controles"
    elif m.rect_btn_sec_inst.collidepoint(evento.pos):
        if m.seccion_opciones_actual != "instrucciones":
            reproducir_sonido_ui("tab")
        m.seccion_opciones_actual = "instrucciones"
    elif m.seccion_opciones_actual == "configuracion":
        m.rect_panel_ev = pygame.Rect(340, 115, 875, 495)
        m.y_vol_ev = m.rect_panel_ev.top + 60
        m.r_card_vol_ev = pygame.Rect(m.rect_panel_ev.left + 45, m.y_vol_ev + 24, m.rect_panel_ev.width - 90, 72)
        m.cy_v_ev = m.r_card_vol_ev.centery
        m.r_menos_ev = pygame.Rect(m.r_card_vol_ev.left + 25, m.cy_v_ev - 22, 50, 44)
        m.r_barra_bg_ev = pygame.Rect(m.r_menos_ev.right + 20, m.cy_v_ev - 18, 460, 36)
        m.r_mas_ev = pygame.Rect(m.r_barra_bg_ev.right + 20, m.cy_v_ev - 22, 50, 44)

        m.y_idioma_ev = m.r_card_vol_ev.bottom + 12
        m.r_card_idm_ev = pygame.Rect(m.rect_panel_ev.left + 45, m.y_idioma_ev + 24, m.rect_panel_ev.width - 90, 94)
        m.w_btn_l_ev = (m.r_card_idm_ev.width - 60) // 3
        m.r_bl_es = pygame.Rect(m.r_card_idm_ev.left + 20, m.r_card_idm_ev.top + 11, m.w_btn_l_ev, 72)
        m.r_bl_en = pygame.Rect(m.r_card_idm_ev.left + 20 + (m.w_btn_l_ev + 10), m.r_card_idm_ev.top + 11, m.w_btn_l_ev, 72)
        m.r_bl_zh = pygame.Rect(m.r_card_idm_ev.left + 20 + 2 * (m.w_btn_l_ev + 10), m.r_card_idm_ev.top + 11, m.w_btn_l_ev, 72)

        m.y_musica_ev = m.r_card_idm_ev.bottom + 12
        m.r_card_mus_ev = pygame.Rect(m.rect_panel_ev.left + 45, m.y_musica_ev + 24, m.rect_panel_ev.width - 90, 102)
        m.w_btn_m_ev = (m.r_card_mus_ev.width - 60) // 3
        m.r_bm_rnd = pygame.Rect(m.r_card_mus_ev.left + 20, m.r_card_mus_ev.top + 10, m.w_btn_m_ev, 82)
        m.r_bm_cai = pygame.Rect(m.r_card_mus_ev.left + 20 + (m.w_btn_m_ev + 10), m.r_card_mus_ev.top + 10, m.w_btn_m_ev, 82)
        m.r_bm_chr = pygame.Rect(m.r_card_mus_ev.left + 20 + 2 * (m.w_btn_m_ev + 10), m.r_card_mus_ev.top + 10, m.w_btn_m_ev, 82)

        if m.r_menos_ev.collidepoint(evento.pos):
            cambiar_volumen(-10)
            reproducir_beep_volumen()
        elif m.r_mas_ev.collidepoint(evento.pos):
            cambiar_volumen(+10)
            reproducir_beep_volumen()
        elif m.r_barra_bg_ev.collidepoint(evento.pos):
            m.frac = max(0.0, min(1.0, (evento.pos[0] - (m.r_barra_bg_ev.left + 4)) / float(max(1, m.r_barra_bg_ev.width - 8))))
            m.nuevo_vol = int(round(m.frac * 10)) * 10
            fijar_volumen(m.nuevo_vol)
            reproducir_beep_volumen()
        elif m.r_bl_es.collidepoint(evento.pos):
            cambiar_idioma("es")
            reproducir_sonido_ui("select")
        elif m.r_bl_en.collidepoint(evento.pos):
            cambiar_idioma("en")
            reproducir_sonido_ui("select")
        elif m.r_bl_zh.collidepoint(evento.pos):
            cambiar_idioma("zh")
            reproducir_sonido_ui("select")
        elif m.r_bm_rnd.collidepoint(evento.pos):
            fijar_modo_musica_menu("aleatorio")
            reproducir_sonido_ui("select")
        elif m.r_bm_cai.collidepoint(evento.pos):
            fijar_modo_musica_menu("caillou")
            reproducir_sonido_ui("select")
        elif m.r_bm_chr.collidepoint(evento.pos):
            fijar_modo_musica_menu("christmas")
            reproducir_sonido_ui("select")
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


def _dibujar_modo_juego(m):
    """Dibuja la pantalla «modo_juego»."""
    # Fondo panorámico de aventura al atardecer en pixel art
    m.pantalla.blit(_obtener_fondo_modo_juego(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))
    _dibujar_copos_modo(m.pantalla)

    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()

    # Marquesina / Placa cálida para Título y Subtítulo que asegura contraste y armonía
    w_placa = min(680, m.ANCHO_MENU - 40)
    h_placa = 106
    x_placa = (m.ANCHO_MENU - w_placa) // 2
    y_placa = 45

    surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
    pygame.draw.rect(surf_placa, (252, 242, 228, 225), (0, 0, w_placa, h_placa), border_radius=16)
    pygame.draw.rect(surf_placa, (85, 28, 48, 240), (0, 0, w_placa, h_placa), width=3, border_radius=16)
    pygame.draw.rect(surf_placa, (235, 142, 72, 180), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)
    for m.cx_d, m.cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
        pygame.draw.circle(surf_placa, (215, 110, 42), (m.cx_d, m.cy_d), 4)
        pygame.draw.circle(surf_placa, (255, 240, 200), (m.cx_d, m.cy_d), 2)
    m.pantalla.blit(surf_placa, (x_placa, y_placa))

    # Título «MODO DE JUEGO» en bordó profundo con sombra sutil de relieve
    m.txt_tit = t("modo_juego")
    f_tit_modo = obtener_fuente_para_texto(m.txt_tit, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
    m.t_somb = f_tit_modo.render(m.txt_tit, True, (225, 205, 185))
    m.t_tit = f_tit_modo.render(m.txt_tit, True, (68, 20, 42))
    m.rect_tit = m.t_tit.get_rect(center=(m.ANCHO_MENU // 2, y_placa + 38))
    m.pantalla.blit(m.t_somb, (m.rect_tit.x + 2, m.rect_tit.y + 2))
    m.pantalla.blit(m.t_tit, m.rect_tit)

    # Subtítulo en marrón cálido con ajuste dinámico de tamaño y márgenes interiores
    m.txt_sub = t("subtitulo_modo")
    ancho_max_sub = w_placa - 70  # Margen interior de al menos 35px a cada lado
    f_sub_modo, m._ = ajustar_tamano_fuente(
        m.txt_sub,
        categoria="subtitulo",
        tamano_inicial=TAMANO_SUBTITULO,
        ancho_max=ancho_max_sub,
        tamano_min=13
    )
    t_sub_s = f_sub_modo.render(m.txt_sub, True, (255, 255, 255))
    m.t_sub = f_sub_modo.render(m.txt_sub, True, (108, 52, 45))
    rect_sub = m.t_sub.get_rect(center=(m.ANCHO_MENU // 2, y_placa + 78))
    m.pantalla.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
    m.pantalla.blit(m.t_sub, rect_sub)

    # Botón CONTINUAR (Ámbar atardecer con relieve y sombra)
    hov_c = m.btn_continuar.collidepoint(m.pos_mouse)
    spr_c_norm = m._obtener_boton_modo("continuar", "normal", m.idm_act)
    spr_c_hov = m._obtener_boton_modo("continuar", "hover", m.idm_act)
    spr_c = spr_c_hov if (hov_c and spr_c_hov) else spr_c_norm
    if spr_c:
        m.pantalla.blit(spr_c, m.btn_continuar)

    # Botón NUEVA PARTIDA (Violeta/Ciruela atardecer con resplandor)
    hov_n = m.btn_nueva_partida.collidepoint(m.pos_mouse)
    spr_n_norm = m._obtener_boton_modo("nueva", "normal", m.idm_act)
    spr_n_hov = m._obtener_boton_modo("nueva", "hover", m.idm_act)
    spr_n = spr_n_hov if (hov_n and spr_n_hov) else spr_n_norm
    if spr_n:
        m.pantalla.blit(spr_n, m.btn_nueva_partida)

    # Botón VOLVER AL MENÚ (Pergamino crema con borde bordó y relieve)
    hov_v = m.btn_volver_modo.collidepoint(m.pos_mouse)
    spr_v_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_v_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_v = spr_v_hov if (hov_v and spr_v_hov) else spr_v_norm
    if spr_v:
        m.pantalla.blit(spr_v, m.btn_volver_modo)


def _dibujar_lista_partidas(m):
    """Dibuja la pantalla «lista_partidas»."""
    m.ANCHO_MENU = m.pantalla.get_width()
    m.ALTO_MENU = m.pantalla.get_height()
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()
    partidas = cargar_partidas()

    # Asegurar recursos pixel art del diario cargados
    m._cargar_recursos_partidas()

    # Fondo pergamino antiguo con bocetos cartográficos y bordes envejecidos
    m.pantalla.blit(_obtener_fondo_partidas(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))

    m.rect_panel_partidas, m.btn_volver_partidas, m.btn_nueva_desde_lista, m.btn_iniciar_primera = (
        obtener_geometria_panel_partidas(m.ANCHO_MENU, m.ALTO_MENU, bool(partidas))
    )

    # Título «PARTIDAS GUARDADAS» en sepia oscuro con relieve y subtítulo de expedición
    txt_tit_lp = t("partidas_guardadas")
    f_tit_lp = obtener_fuente_para_texto(txt_tit_lp, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
    m.t_somb = f_tit_lp.render(txt_tit_lp, True, (195, 170, 140))
    m.t_tit = f_tit_lp.render(txt_tit_lp, True, (58, 38, 24))
    m.rect_tit = m.t_tit.get_rect(center=(m.ANCHO_MENU // 2, 46))
    m.pantalla.blit(m.t_somb, (m.rect_tit.x + 2, m.rect_tit.y + 2))
    m.pantalla.blit(m.t_tit, m.rect_tit)

    txt_sub_lp = t("sub_partidas")
    f_sub_lp = obtener_fuente_para_texto(txt_sub_lp, categoria="decorativa", tamano=TAMANO_DECORATIVA)
    m.subt = f_sub_lp.render(txt_sub_lp, True, (125, 95, 65))
    m.pantalla.blit(m.subt, m.subt.get_rect(center=(m.ANCHO_MENU // 2, 78)))

    # Contenedor de página del diario (folio pergamino con líneas sutiles y remaches)
    col_pagina = (252, 246, 235)
    col_borde_pag = (190, 160, 125)
    col_linea_int = (225, 200, 160)
    pygame.draw.rect(m.pantalla, col_pagina, m.rect_panel_partidas, border_radius=16)
    pygame.draw.rect(m.pantalla, col_borde_pag, m.rect_panel_partidas, width=3, border_radius=16)
    pygame.draw.rect(m.pantalla, col_linea_int, m.rect_panel_partidas.inflate(-8, -8), width=1, border_radius=12)

    # Pauta de cuaderno sutil (líneas horizontales tenues de diario de campo)
    for m.y_linea in range(m.rect_panel_partidas.top + 28, m.rect_panel_partidas.bottom - 20, 22):
        pygame.draw.line(m.pantalla, (238, 230, 216), (m.rect_panel_partidas.left + 14, m.y_linea), (m.rect_panel_partidas.right - 14, m.y_linea), 1)

    # Remaches / clavos metálicos en las esquinas del folio
    for m.rx, m.ry in [
        (m.rect_panel_partidas.left + 12, m.rect_panel_partidas.top + 12),
        (m.rect_panel_partidas.right - 12, m.rect_panel_partidas.top + 12),
        (m.rect_panel_partidas.left + 12, m.rect_panel_partidas.bottom - 12),
        (m.rect_panel_partidas.right - 12, m.rect_panel_partidas.bottom - 12),
    ]:
        pygame.draw.circle(m.pantalla, (205, 175, 105), (m.rx, m.ry), 3)
        pygame.draw.circle(m.pantalla, (100, 70, 40), (m.rx, m.ry), 3, width=1)

    if not partidas:
        m.txt_sin = t("no_partidas")
        m.f_sin = obtener_fuente_para_texto(m.txt_sin, categoria="subtitulo", tamano=TAMANO_SUBTITULO)
        m.t_sin = m.f_sin.render(m.txt_sin, True, (65, 45, 30))
        m.pantalla.blit(m.t_sin, m.t_sin.get_rect(center=(m.rect_panel_partidas.centerx, m.rect_panel_partidas.centery - 40)))

        m.rect_sin2 = pygame.Rect(m.rect_panel_partidas.left + 40, m.rect_panel_partidas.centery - 20, m.rect_panel_partidas.width - 80, 24)
        dibujar_texto_en_rect(m.pantalla, t("comenzar_historia"), m.rect_sin2, categoria="texto", tamano=16, color=(120, 100, 80))

        m.hov_prim = m.btn_iniciar_primera.collidepoint(m.pos_mouse)
        m.spr_prim_norm = m._obtener_boton_primera_partida("normal", m.idm_act)
        m.spr_prim_hov = m._obtener_boton_primera_partida("hover", m.idm_act)
        m.spr_prim = m.spr_prim_hov if (m.hov_prim and m.spr_prim_hov) else m.spr_prim_norm
        if m.spr_prim:
            m.pantalla.blit(m.spr_prim, m.btn_iniciar_primera)
        else:
            m.col_prim = (235, 128, 48) if m.hov_prim else (215, 110, 42)
            pygame.draw.rect(m.pantalla, m.col_prim, m.btn_iniciar_primera, border_radius=12)
            pygame.draw.rect(m.pantalla, (118, 44, 14), m.btn_iniciar_primera, width=2, border_radius=12)
            dibujar_texto_en_rect(m.pantalla, t("comenzar_aventura"), m.btn_iniciar_primera, categoria="boton", tamano=TAMANO_BOTONES, color=(255, 255, 255), padding=6)
    else:
        m.total_paginas = max(1, (len(partidas) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
        if m.pagina_partidas >= m.total_paginas:
            m.pagina_partidas = max(0, m.total_paginas - 1)

        m.inicio_idx = m.pagina_partidas * m.MAX_PARTIDAS_POR_PAGINA
        m.fin_idx = m.inicio_idx + m.MAX_PARTIDAS_POR_PAGINA
        m.partidas_pagina = partidas[m.inicio_idx:m.fin_idx]

        m.fuentes_tarjetas = {
            "titulo_card": m.fuente_card_titulo,
            "sub_card": m.fuente_card_sub,
            "btn_card": m.fuente_pixel_card_btn,
            "badge": m.fuente_pixel_badge,
            "btn": m.fuente_pixel_badge,
            "texto": m.fuente_texto,
            "sub_btn": m.fuente_sub_btn,
        }

        m.dict_sp_partidas = m._obtener_sprites_tarjeta(m.idm_act)
        for m.idx_slot, m.p in enumerate(m.partidas_pagina):
            dibujar_tarjeta_partida(m.pantalla, m.p, m.idx_slot, m.rect_panel_partidas, m.pos_mouse, m.fuentes_tarjetas, sprites_botones=m.dict_sp_partidas)

        # Indicador de paginación si hay más de 1 página (y = 508, dentro del panel inferior sin colisiones)
        if m.total_paginas > 1:
            m.btn_pag_ant = pygame.Rect(m.rect_panel_partidas.centerx - 120, 508, 36, 30)
            m.btn_pag_sig = pygame.Rect(m.rect_panel_partidas.centerx + 84, 508, 36, 30)

            # Botón página anterior
            m.hov_ant = m.btn_pag_ant.collidepoint(m.pos_mouse) and m.pagina_partidas > 0
            m.col_ant = (255, 255, 255) if m.hov_ant else ((253, 246, 233) if m.pagina_partidas > 0 else (240, 230, 215))
            m.borde_ant = (160, 125, 90) if m.hov_ant else (195, 168, 138)
            pygame.draw.rect(m.pantalla, m.col_ant, m.btn_pag_ant, border_radius=6)
            m.col_flecha_ant = (65, 45, 30) if m.pagina_partidas > 0 else (175, 155, 135)
            m.cx_a, m.cy_a = m.btn_pag_ant.center
            for m.dy in range(-4, 5):
                m.ancho_f = 4 - abs(m.dy)
                for m.dx in range(m.ancho_f + 1):
                    m.pantalla.set_at((m.cx_a + 2 - m.dx, m.cy_a + m.dy), m.col_flecha_ant)

            # Contador de página
            m.txt_pag = t("entrada_pagina").format(m.pagina_partidas + 1, m.total_paginas)
            m.f_pag = obtener_fuente_para_texto(m.txt_pag, categoria="contador", tamano=TAMANO_CONTADOR)
            m.t_pag = m.f_pag.render(m.txt_pag, True, (75, 55, 38))
            m.pantalla.blit(m.t_pag, m.t_pag.get_rect(center=(m.rect_panel_partidas.centerx, 523)))

            # Botón página siguiente
            m.hov_sig = m.btn_pag_sig.collidepoint(m.pos_mouse) and m.pagina_partidas < m.total_paginas - 1
            m.col_sig = (255, 255, 255) if m.hov_sig else ((253, 246, 233) if m.pagina_partidas < m.total_paginas - 1 else (240, 230, 215))
            m.borde_sig = (160, 125, 90) if m.hov_sig else (195, 168, 138)
            pygame.draw.rect(m.pantalla, m.col_sig, m.btn_pag_sig, border_radius=6)
            pygame.draw.rect(m.pantalla, m.borde_sig, m.btn_pag_sig, width=2 if m.hov_sig else 1, border_radius=6)
            m.col_flecha_sig = (65, 45, 30) if m.pagina_partidas < m.total_paginas - 1 else (175, 155, 135)
            m.cx_s, m.cy_s = m.btn_pag_sig.center
            for m.dy in range(-4, 5):
                m.ancho_f = 4 - abs(m.dy)
                for m.dx in range(m.ancho_f + 1):
                    m.pantalla.set_at((m.cx_s - 2 + m.dx, m.cy_s + m.dy), m.col_flecha_sig)

    # Botón «VOLVER» centrado al pie de la pantalla en tonos pergamino/crema
    hov_vp = m.btn_volver_partidas.collidepoint(m.pos_mouse)
    spr_vp_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vp_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vp = spr_vp_hov if (hov_vp and spr_vp_hov) else spr_vp_norm
    if spr_vp:
        m.pantalla.blit(spr_vp, m.btn_volver_partidas)
    else:
        m.col_vp = (255, 255, 255) if hov_vp else (253, 246, 233)
        m.borde_vp = (165, 135, 105) if hov_vp else (195, 168, 138)
        pygame.draw.rect(m.pantalla, m.col_vp, m.btn_volver_partidas, border_radius=12)
        pygame.draw.rect(m.pantalla, m.borde_vp, m.btn_volver_partidas, width=2, border_radius=12)
        dibujar_texto_en_rect(m.pantalla, t("volver"), m.btn_volver_partidas, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)

    if partidas:
        # Botón «NUEVA PARTIDA» ubicado al lado de «VOLVER», centrados juntos en ámbar/terracota
        m.hov_nd = m.btn_nueva_desde_lista.collidepoint(m.pos_mouse)
        m.spr_nd_norm = m._obtener_boton_nueva_lista("normal", m.idm_act)
        m.spr_nd_hov = m._obtener_boton_nueva_lista("hover", m.idm_act)
        m.spr_nd = m.spr_nd_hov if (m.hov_nd and m.spr_nd_hov) else m.spr_nd_norm
        if m.spr_nd:
            m.pantalla.blit(m.spr_nd, m.btn_nueva_desde_lista)
        else:
            m.col_nd = (235, 128, 48) if m.hov_nd else (215, 110, 42)
            m.borde_nd = (255, 255, 255) if m.hov_nd else (118, 44, 14)
            pygame.draw.rect(m.pantalla, m.col_nd, m.btn_nueva_desde_lista, border_radius=12)
            pygame.draw.rect(m.pantalla, m.borde_nd, m.btn_nueva_desde_lista, width=2, border_radius=12)
            dibujar_texto_en_rect(m.pantalla, t("nueva_partida"), m.btn_nueva_desde_lista, categoria="boton", tamano=TAMANO_BOTONES, color=(255, 255, 255), padding=6)


def _dibujar_personajes(m):
    """Dibuja la pantalla «personajes»."""
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()

    # 1. Fondo de habitación de vestuario / camerino pixel art
    m.pantalla.blit(_obtener_fondo_personajes(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))

    # 2. Título y subtítulo centrados
    txt_tit_pj = t("personalizacion_personajes")
    f_tit_pj = obtener_fuente_para_texto(txt_tit_pj, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
    m.titulo = f_tit_pj.render(txt_tit_pj, True, (60, 45, 35))
    m.pantalla.blit(m.titulo, m.titulo.get_rect(center=(m.ANCHO_MENU // 2, 46)))

    txt_sub_pj = t("sub_personalizacion")
    f_sub_pj = obtener_fuente_para_texto(txt_sub_pj, categoria="subtitulo", tamano=TAMANO_SUBTITULO)
    m.subt = f_sub_pj.render(txt_sub_pj, True, (120, 100, 85))
    m.pantalla.blit(m.subt, m.subt.get_rect(center=(m.ANCHO_MENU // 2, 78)))

    # 3. Pestañas visuales [ COLORES ] y [ ACCESORIOS ] con sprites oficiales
    w_tab_pj = 240
    h_tab_pj = round(w_tab_pj * 264 / 950)  # 67 px
    y_tab_pj = 150 - h_tab_pj               # 83 px
    m.rect_tab_col = pygame.Rect(388, y_tab_pj, w_tab_pj, h_tab_pj)
    m.rect_tab_acc = pygame.Rect(652, y_tab_pj, w_tab_pj, h_tab_pj)

    hov_tab_col = m.rect_tab_col.collidepoint(m.pos_mouse)
    hov_tab_acc = m.rect_tab_acc.collidepoint(m.pos_mouse)

    # Dibujar primero la pestaña inactiva y luego la seleccionada para mantener profundidad correcta
    tabs_orden = [
        ("accesorios", m.rect_tab_acc, hov_tab_acc),
        ("colores", m.rect_tab_col, hov_tab_col),
    ] if m.tab_personajes_actual == "colores" else [
        ("colores", m.rect_tab_col, hov_tab_col),
        ("accesorios", m.rect_tab_acc, hov_tab_acc),
    ]

    for m.tab_id, m.r_tab, m.hov in tabs_orden:
        m.es_activa = (m.tab_personajes_actual == m.tab_id)
        m.nom_spr = f"{m.tab_id}-seleccionado.png" if m.es_activa else f"{m.tab_id}.png"
        m.col_txt_tab = (116, 78, 45) if m.es_activa else (157, 131, 100)
        m.spr_tab = generar_boton_con_texto(
            m.nom_spr, w_tab_pj, h_tab_pj,
            texto=t(m.tab_id).upper(),
            color_texto=m.col_txt_tab,
            tamano_fuente=16,
            offset_y=0,
        )
        if m.spr_tab:
            m.pantalla.blit(m.spr_tab, (m.r_tab.left, m.r_tab.top))
            if not m.es_activa and m.hov:
                m.glow = m.spr_tab.copy()
                m.bright = pygame.Surface(m.spr_tab.get_size(), pygame.SRCALPHA)
                m.bright.fill((35, 35, 35, 0))
                m.glow.blit(m.bright, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                m.pantalla.blit(m.glow, (m.r_tab.left, m.r_tab.top))
        else:
            m.r_fb = pygame.Rect(m.r_tab.left, 100, w_tab_pj, 50)
            m.col_tab_bg = (246, 215, 153) if m.es_activa else ((248, 242, 232) if m.hov else (238, 226, 210))
            m.col_tab_borde = (175, 130, 80) if m.es_activa else (195, 175, 155)
            m.ancho_b = 3 if m.es_activa else 2
            pygame.draw.rect(m.pantalla, m.col_tab_bg, m.r_fb, border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_tab_borde, m.r_fb, m.ancho_b, border_radius=12)

            m.col_txt = (50, 40, 30) if m.es_activa else (130, 115, 100)
            m.txt_tab_str = t(m.tab_id).upper()
            dibujar_texto_en_rect(m.pantalla, m.txt_tab_str, m.r_fb, categoria="boton", tamano=18, color=m.col_txt, negrita=True, padding=8)

            if m.es_activa:
                dibujar_mascota_gato(m.pantalla, m.r_fb.left + 16, m.r_fb.top - 18, size=28, color=(246, 215, 153))

    # 4. Columnas simétricas de Jugador 1 y Jugador 2
    cx_p1 = 360
    cx_p2 = 920

    colores_dict = {p["nombre"]: p["color"] for p in PERSONAJES_DISPONIBLES}
    c_p1_val = colores_dict.get(m.color_p1, (124, 231, 255))
    c_p2_val = colores_dict.get(m.color_p2, (161, 123, 255))

    # Badges de encabezado de jugador con ajuste automático para nombres extensos de color
    r_badge_p1 = pygame.Rect(cx_p1 - 130, 150, 260, 32)
    pygame.draw.rect(m.pantalla, c_p1_val, r_badge_p1, border_radius=8)
    pygame.draw.rect(m.pantalla, (60, 45, 35), r_badge_p1, 2, border_radius=8)
    col_p1_trad = _obtener_nombre_color_visible(m.color_p1, m.idm_act).upper()
    dibujar_texto_en_rect(m.pantalla, f"{t('jugador')} 1  ({col_p1_trad})", r_badge_p1, categoria="boton", tamano=TAMANO_BADGE, color=(35, 30, 25), padding=4)

    r_badge_p2 = pygame.Rect(cx_p2 - 130, 150, 260, 32)
    pygame.draw.rect(m.pantalla, c_p2_val, r_badge_p2, border_radius=8)
    pygame.draw.rect(m.pantalla, (60, 45, 35), r_badge_p2, 2, border_radius=8)
    col_p2_trad = _obtener_nombre_color_visible(m.color_p2, m.idm_act).upper()
    dibujar_texto_en_rect(m.pantalla, f"{t('jugador')} 2  ({col_p2_trad})", r_badge_p2, categoria="boton", tamano=TAMANO_BADGE, color=(35, 30, 25), padding=4)

    # Previews de personajes con pedestal y accesorios
    for m.cx, m.col_pj, m.acc_pj in [
        (cx_p1, m.color_p1, m.accesorio_p1),
        (cx_p2, m.color_p2, m.accesorio_p2),
    ]:
        pygame.draw.ellipse(m.pantalla, (230, 210, 175), (m.cx - 50, 276, 100, 16))

        m.sp_pj = cargar_sprites(m.col_pj)
        m.img_pj = m.sp_pj.get("quieto", list(m.sp_pj.values())[0])
        m.rect_pj = m.img_pj.get_rect(center=(m.cx, 240))
        m.pantalla.blit(m.img_pj, m.rect_pj)

        if m.acc_pj and m.acc_pj != "Ninguno":
            dibujar_accesorio_en_personaje(m.pantalla, m.acc_pj, sprite_personaje=m.img_pj, rect_personaje=m.rect_pj, mirando_derecha=True)

    # 5. Marcos rectangulares contenedores de opciones
    w_frame, h_frame = 470, 276
    y_frame = 295
    rect_f1 = pygame.Rect(cx_p1 - w_frame // 2, y_frame, w_frame, h_frame)
    rect_f2 = pygame.Rect(cx_p2 - w_frame // 2, y_frame, w_frame, h_frame)

    for m.rf in (rect_f1, rect_f2):
        pygame.draw.rect(m.pantalla, (253, 246, 233), m.rf, border_radius=16)
        pygame.draw.rect(m.pantalla, (195, 168, 138), m.rf, 3, border_radius=16)

        m.txt_encabezado = t("colores_disponibles") if m.tab_personajes_actual == "colores" else t("accesorios_disponibles")
        m.f_enc = obtener_fuente_para_texto(m.txt_encabezado, categoria="texto", tamano=TAMANO_TEXTO, negrita=True)
        m.t_enc = m.f_enc.render(m.txt_encabezado, True, (115, 95, 80))
        m.pantalla.blit(m.t_enc, m.t_enc.get_rect(center=(m.rf.centerx, m.rf.top + 20)))
        pygame.draw.line(m.pantalla, (235, 215, 195), (m.rf.left + 24, m.rf.top + 34), (m.rf.right - 24, m.rf.top + 34), 2)

    # 6. Opciones dentro del marco según la pestaña activa
    if m.tab_personajes_actual == "colores":
        m.w_sw, m.h_sw = 80, 45
        m.y_start_sw = 338
        m.h_paso_y = 77
        for m.r_idx, m.fila in enumerate(FILAS_COLORES_SELECCION):
            m.n = len(m.fila)
            m.gap_x = 10 if m.n == 5 else 24
            m.row_w = m.n * m.w_sw + (m.n - 1) * m.gap_x
            m.x_start_rel = (rect_f1.width - m.row_w) // 2
            m.y_sw = m.y_start_sw + m.r_idx * m.h_paso_y

            for m.c_idx, m.color_idx in enumerate(m.fila):
                m.p_info = PERSONAJES_DISPONIBLES[m.color_idx]
                m.x_sw_rel = m.x_start_rel + m.c_idx * (m.w_sw + m.gap_x)
                m.r1 = pygame.Rect(rect_f1.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw)
                m.r2 = pygame.Rect(rect_f2.left + m.x_sw_rel, m.y_sw, m.w_sw, m.h_sw)
                m.nom_col = _obtener_nombre_color_visible(m.p_info["nombre"], m.idm_act)
                m.f_nom = obtener_fuente_para_texto(m.nom_col, categoria="dialogos", tamano=22, negrita=True)

                # P1 swatch
                m.sel1 = (m.p_info["nombre"] == m.color_p1)
                m.hov1 = m.r1.collidepoint(m.pos_mouse)
                pygame.draw.rect(m.pantalla, m.p_info["color"], m.r1, border_radius=8)
                if m.sel1:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r1, 3, border_radius=8)
                    pygame.draw.rect(m.pantalla, (40, 30, 25), m.r1, 1, border_radius=8)
                    m.cx_k, m.cy_k = m.r1.center
                    m.pts_chk = [(m.cx_k - 7, m.cy_k), (m.cx_k - 2, m.cy_k + 5), (m.cx_k + 7, m.cy_k - 5)]
                    m.pts_shadow = [(x + 1, y + 1) for x, y in m.pts_chk]
                    pygame.draw.lines(m.pantalla, (40, 30, 25), False, m.pts_shadow, 4)
                    pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_chk, 3)
                elif m.hov1:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r1, 2, border_radius=8)
                else:
                    pygame.draw.rect(m.pantalla, (180, 160, 140), m.r1, 1, border_radius=8)

                m.col_t1 = (25, 15, 8) if m.sel1 else (50, 34, 22)
                m.ts1 = m.f_nom.render(m.nom_col, True, m.col_t1)
                m.tx1 = m.r1.centerx - m.ts1.get_width() // 2
                m.ty1 = m.r1.bottom + 4
                m.pantalla.blit(m.ts1, (m.tx1, m.ty1))
                m.pantalla.blit(m.ts1, (m.tx1 + 1, m.ty1))

                # P2 swatch
                m.sel2 = (m.p_info["nombre"] == m.color_p2)
                m.hov2 = m.r2.collidepoint(m.pos_mouse)
                pygame.draw.rect(m.pantalla, m.p_info["color"], m.r2, border_radius=8)
                if m.sel2:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r2, 3, border_radius=8)
                    pygame.draw.rect(m.pantalla, (40, 30, 25), m.r2, 1, border_radius=8)
                    m.cx_k2, m.cy_k2 = m.r2.center
                    m.pts_chk2 = [(m.cx_k2 - 7, m.cy_k2), (m.cx_k2 - 2, m.cy_k2 + 5), (m.cx_k2 + 7, m.cy_k2 - 5)]
                    m.pts_shadow2 = [(x + 1, y + 1) for x, y in m.pts_chk2]
                    pygame.draw.lines(m.pantalla, (40, 30, 25), False, m.pts_shadow2, 4)
                    pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_chk2, 3)
                elif m.hov2:
                    pygame.draw.rect(m.pantalla, (255, 255, 255), m.r2, 2, border_radius=8)
                else:
                    pygame.draw.rect(m.pantalla, (180, 160, 140), m.r2, 1, border_radius=8)

                m.col_t2 = (25, 15, 8) if m.sel2 else (50, 34, 22)
                m.ts2 = m.f_nom.render(m.nom_col, True, m.col_t2)
                m.tx2 = m.r2.centerx - m.ts2.get_width() // 2
                m.ty2 = m.r2.bottom + 4
                m.pantalla.blit(m.ts2, (m.tx2, m.ty2))
                m.pantalla.blit(m.ts2, (m.tx2 + 1, m.ty2))

    elif m.tab_personajes_actual == "accesorios":
        m.items_por_pag = 6
        m.w_acc, m.h_acc, m.gap_acc_x, m.gap_acc_y = 126, 82, 16, 10
        m.ancho_fila_acc = 3 * m.w_acc + 2 * m.gap_acc_x
        m.x_offset_acc = (w_frame - m.ancho_fila_acc) // 2

        for m.rf, m.acc_actual, m.pag_num, m.color_pj_actual in [
            (rect_f1, m.accesorio_p1, m.pagina_acc_p1, m.color_p1),
            (rect_f2, m.accesorio_p2, m.pagina_acc_p2, m.color_p2),
        ]:
            m.accesorios_disp = obtener_accesorios_disponibles(m.color_pj_actual)
            m.total_pags = max(1, (len(m.accesorios_disp) + m.items_por_pag - 1) // m.items_por_pag)
            m.pag_num = min(m.pag_num, m.total_pags - 1)
            # 1. Controles inferiores de paginación
            m.btn_prev = pygame.Rect(m.rf.centerx - 72, m.rf.top + 234, 34, 26)
            m.btn_next = pygame.Rect(m.rf.centerx + 38, m.rf.top + 234, 34, 26)

            for m.b_rect, m.es_izq in [(m.btn_prev, True), (m.btn_next, False)]:
                m.hov_b = m.b_rect.collidepoint(m.pos_mouse)
                m.col_bg_b = (255, 252, 245) if m.hov_b else (244, 236, 224)
                m.col_brd_b = (220, 180, 120) if m.hov_b else (195, 168, 138)
                pygame.draw.rect(m.pantalla, m.col_bg_b, m.b_rect, border_radius=6)
                pygame.draw.rect(m.pantalla, m.col_brd_b, m.b_rect, 2, border_radius=6)

                m.col_arr = (80, 60, 45) if m.hov_b else (120, 100, 85)
                m.cx_b, m.cy_b = m.b_rect.center
                if m.es_izq:
                    for m.dy in range(-5, 6):
                        m.ancho_f = 5 - abs(m.dy)
                        for m.dx in range(m.ancho_f + 1):
                            m.pantalla.set_at((m.cx_b + 2 - m.dx, m.cy_b + m.dy), m.col_arr)
                else:
                    for m.dy in range(-5, 6):
                        m.ancho_f = 5 - abs(m.dy)
                        for m.dx in range(m.ancho_f + 1):
                            m.pantalla.set_at((m.cx_b - 2 + m.dx, m.cy_b + m.dy), m.col_arr)

            m.txt_pag = f"{m.pag_num + 1} / {m.total_pags}"
            m.f_pag = obtener_fuente_para_texto(m.txt_pag, categoria="texto", tamano=TAMANO_BADGE, negrita=True)
            m.t_pag = m.f_pag.render(m.txt_pag, True, (115, 95, 80))
            m.pantalla.blit(m.t_pag, m.t_pag.get_rect(center=(m.rf.centerx, m.rf.top + 247)))

            # 2. Tarjetas de accesorios de la página activa con fondo crema claro de alto contraste
            m.inicio = m.pag_num * m.items_por_pag
            for m.idx_rel, m.acc in enumerate(m.accesorios_disp[m.inicio:m.inicio + m.items_por_pag]):
                m.r = m.idx_rel // 3
                m.c = m.idx_rel % 3
                m.x_offset_rel = m.x_offset_acc + m.c * (m.w_acc + m.gap_acc_x)
                m.y_card_a = m.rf.top + 42 + m.r * (m.h_acc + m.gap_acc_y)
                m.r_card_a = pygame.Rect(m.rf.left + m.x_offset_rel, m.y_card_a, m.w_acc, m.h_acc)

                m.sel = (m.acc["id"] == m.acc_actual or m.acc["id"].lower() == str(m.acc_actual).lower())
                m.hov = m.r_card_a.collidepoint(m.pos_mouse)

                m.col_bg_a = (242, 252, 244) if m.sel else ((255, 252, 246) if m.hov else (248, 242, 232))
                m.col_brd_a = (45, 165, 85) if m.sel else ((180, 145, 110) if m.hov else (195, 168, 138))
                pygame.draw.rect(m.pantalla, m.col_bg_a, m.r_card_a, border_radius=10)
                pygame.draw.rect(m.pantalla, m.col_brd_a, m.r_card_a, 3 if m.sel else 2, border_radius=10)

                if m.sel:
                    m.cx_ca = m.r_card_a.right - 14
                    m.cy_ca = m.r_card_a.top + 14
                    pygame.draw.circle(m.pantalla, (45, 165, 85), (m.cx_ca, m.cy_ca), 9)
                    m.pts_ca = [(m.cx_ca - 4, m.cy_ca), (m.cx_ca - 1, m.cy_ca + 3), (m.cx_ca + 4, m.cy_ca - 3)]
                    pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_ca, 2)

                if m.acc["id"] == "Ninguno":
                    m.cx_ic, m.cy_ic = m.r_card_a.centerx, m.r_card_a.top + 25
                    pygame.draw.circle(m.pantalla, (220, 80, 75), (m.cx_ic, m.cy_ic), 13, width=2)
                    pygame.draw.line(m.pantalla, (220, 80, 75), (m.cx_ic - 8, m.cy_ic - 8), (m.cx_ic + 8, m.cy_ic + 8), 2)
                else:
                    m.surf_icon = _obtener_preview_accesorio_tarjeta(m.acc["id"])
                    if m.surf_icon:
                        m.r_mini = m.surf_icon.get_rect(center=(m.r_card_a.centerx, m.r_card_a.top + 25))
                        m.pantalla.blit(m.surf_icon, m.r_mini)

                m.col_nom = (25, 75, 35) if m.sel else ((45, 30, 18) if m.hov else (55, 38, 25))
                m.rect_nom_acc = pygame.Rect(m.r_card_a.left + 2, m.r_card_a.bottom - 32, m.r_card_a.width - 4, 30)
                m.nom_acc_trad = t(m.acc["id"].lower())
                dibujar_texto_en_rect(m.pantalla, m.nom_acc_trad, m.rect_nom_acc, categoria="boton", tamano=13, color=m.col_nom, negrita=True, multiline=True, alineacion="centro", padding=0, interlineado=1)

    # 7. Botón Volver al Menú
    hov_vpj = m.btn_volver_personajes.collidepoint(m.pos_mouse)
    spr_vpj_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vpj_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vpj = spr_vpj_hov if (hov_vpj and spr_vpj_hov) else spr_vpj_norm
    if spr_vpj:
        m.pantalla.blit(spr_vpj, m.btn_volver_personajes)
    else:
        m.col_v = (255, 255, 255) if hov_vpj else (242, 234, 222)
        pygame.draw.rect(m.pantalla, m.col_v, m.btn_volver_personajes, border_radius=10)
        pygame.draw.rect(m.pantalla, (185, 155, 125), m.btn_volver_personajes, width=2, border_radius=10)
        dibujar_texto_en_rect(m.pantalla, t("volver_al_menu"), m.btn_volver_personajes, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)


def _dibujar_configuracion(m):
    """Dibuja la pantalla «configuracion»."""
    m.pos_mouse = pygame.mouse.get_pos()
    m.idm_act = obtener_idioma()

    # 1. Fondo de paisaje invernal pixel art con copos de nieve cayendo
    m.pantalla.blit(_obtener_fondo_opciones(m.ANCHO_MENU, m.ALTO_MENU), (0, 0))
    _dibujar_copos_opciones(m.pantalla)

    # 2. Título y Subtítulo
    m.txt_tit = t("opciones").upper()
    m.f_tit = obtener_fuente_para_texto(m.txt_tit, categoria="titulo", tamano=TAMANO_TITULO + 2, negrita=True)
    m.t_tit = m.f_tit.render(m.txt_tit, True, (255, 240, 195))
    t_tit_s = m.f_tit.render(m.txt_tit, True, (15, 20, 35))
    rc_tit = m.t_tit.get_rect(center=(m.ANCHO_MENU // 2, 44))
    m.pantalla.blit(t_tit_s, (rc_tit.x + 2, rc_tit.y + 2))
    m.pantalla.blit(m.t_tit, rc_tit)

    m.txt_sub = t("sub_opciones")
    m.f_sub = obtener_fuente_para_texto(m.txt_sub, categoria="subtitulo", tamano=TAMANO_SUBTITULO - 2)
    m.t_sub = m.f_sub.render(m.txt_sub, True, (215, 230, 255))
    m.pantalla.blit(m.t_sub, m.t_sub.get_rect(center=(m.ANCHO_MENU // 2, 78)))

    # 3. Barra lateral izquierda (3 botones de secciones)
    botones_sec = [
        ("configuracion", t("configuracion").upper(), m.rect_btn_sec_cfg),
        ("controles", t("controles").upper(), m.rect_btn_sec_ctrl),
        ("instrucciones", t("instrucciones").upper(), m.rect_btn_sec_inst),
    ]

    for m.sec_id, m.sec_nom, m.r_b in botones_sec:
        m.es_activa = (m.seccion_opciones_actual == m.sec_id)
        m.hov_b = m.r_b.collidepoint(m.pos_mouse)

        if m.es_activa:
            m.col_bg = (250, 225, 165)
            m.col_brd = (185, 110, 60)
            m.col_txt = (45, 30, 15)
            pygame.draw.rect(m.pantalla, (140, 80, 40), (m.r_b.left, m.r_b.top + 4, m.r_b.width, m.r_b.height), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_bg, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_brd, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), 3, border_radius=12)
            # Indicador rombo / gema
            m.cy_g = m.r_b.centery - 1
            m.pts_gema = [(m.r_b.left + 16, m.cy_g), (m.r_b.left + 22, m.cy_g - 6), (m.r_b.left + 28, m.cy_g), (m.r_b.left + 22, m.cy_g + 6)]
            pygame.draw.polygon(m.pantalla, (225, 110, 80), m.pts_gema)
            pygame.draw.polygon(m.pantalla, (150, 60, 30), m.pts_gema, 1)
        else:
            m.col_bg = (38, 52, 82) if m.hov_b else (28, 38, 62)
            m.col_brd = (110, 140, 185) if m.hov_b else (85, 110, 150)
            m.col_txt = (255, 255, 255) if m.hov_b else (220, 230, 245)
            pygame.draw.rect(m.pantalla, (15, 22, 38), (m.r_b.left, m.r_b.top + 4, m.r_b.width, m.r_b.height), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_bg, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), border_radius=12)
            pygame.draw.rect(m.pantalla, m.col_brd, (m.r_b.left, m.r_b.top, m.r_b.width, m.r_b.height - 2), 2, border_radius=12)

        m.r_txt_b = pygame.Rect(m.r_b.left + (36 if m.es_activa else 12), m.r_b.top, m.r_b.width - (44 if m.es_activa else 24), m.r_b.height - 2)
        dibujar_texto_en_rect(m.pantalla, m.sec_nom, m.r_txt_b, categoria="boton", tamano=15, color=m.col_txt, negrita=True, alineacion="centro")

    # Personajes decorativos en la barra lateral izquierda
    cx_dec, cy_dec = 190, 430
    pygame.draw.ellipse(m.pantalla, (220, 235, 255), (cx_dec - 80, cy_dec + 45, 160, 24))
    sp_p1_d = cargar_sprites(m.color_p1).get("quieto")
    sp_p2_d = cargar_sprites(m.color_p2).get("quieto")
    r_mini_p1 = pygame.Rect(cx_dec - 55, cy_dec, 50, 62)
    r_mini_p2 = pygame.Rect(cx_dec + 5, cy_dec, 50, 62)
    if sp_p1_d:
        m.pantalla.blit(escalar_cacheado(sp_p1_d, (50, 62)), r_mini_p1)
        if m.accesorio_p1:
            dibujar_accesorio_en_personaje(m.pantalla, m.accesorio_p1, sprite_personaje=sp_p1_d, rect_personaje=r_mini_p1, mirando_derecha=True)
    if sp_p2_d:
        m.pantalla.blit(escalar_cacheado(sp_p2_d, (50, 62)), r_mini_p2)
        if m.accesorio_p2:
            dibujar_accesorio_en_personaje(m.pantalla, m.accesorio_p2, sprite_personaje=sp_p2_d, rect_personaje=r_mini_p2, mirando_derecha=True)

    # 4. Panel central grande de color crema
    m.rect_panel = pygame.Rect(340, 115, 875, 495)
    # Sombra del panel
    pygame.draw.rect(m.pantalla, (15, 20, 35), (m.rect_panel.left + 5, m.rect_panel.top + 5, m.rect_panel.width, m.rect_panel.height), border_radius=18)
    # Fondo crema
    pygame.draw.rect(m.pantalla, (253, 248, 238), m.rect_panel, border_radius=18)
    # Borde exterior marrón
    pygame.draw.rect(m.pantalla, (115, 75, 48), m.rect_panel, 4, border_radius=18)
    # Borde interior coral
    rect_in = pygame.Rect(m.rect_panel.left + 6, m.rect_panel.top + 6, m.rect_panel.width - 12, m.rect_panel.height - 12)
    pygame.draw.rect(m.pantalla, (225, 115, 85), rect_in, 2, border_radius=14)

    # Cabecera dentro del panel
    nom_seccion = {
        "configuracion": t("ajustes_generales"),
        "controles": t("controles_teclado"),
        "instrucciones": t("guia_juego"),
    }.get(m.seccion_opciones_actual, t("opciones"))

    f_p_tit = obtener_fuente_para_texto(nom_seccion, categoria="titulo", tamano=19, negrita=True)
    t_p_tit = f_p_tit.render(nom_seccion, True, (60, 42, 30))
    m.pantalla.blit(t_p_tit, t_p_tit.get_rect(center=(m.rect_panel.centerx, m.rect_panel.top + 28)))
    # Línea divisoria decorativa
    pygame.draw.line(m.pantalla, (225, 115, 85), (m.rect_panel.left + 35, m.rect_panel.top + 48), (m.rect_panel.right - 35, m.rect_panel.top + 48), 2)
    pygame.draw.circle(m.pantalla, (180, 90, 55), (m.rect_panel.centerx, m.rect_panel.top + 48), 4)

    # =========================================================================
    # SECCIÓN: CONFIGURACIÓN
    # =========================================================================
    if m.seccion_opciones_actual == "configuracion":
        # Bloque A: Volumen
        m.y_vol = m.rect_panel.top + 60
        m.txt_vol_b = t("volumen_musica_y_sonido")
        m.f_bloq = obtener_fuente_para_texto(m.txt_vol_b, categoria="texto", tamano=15, negrita=True)
        m.pantalla.blit(m.f_bloq.render(m.txt_vol_b, True, (65, 45, 32)), (m.rect_panel.left + 45, m.y_vol))

        # Tarjeta contenedora de volumen
        m.r_card_vol = pygame.Rect(m.rect_panel.left + 45, m.y_vol + 24, m.rect_panel.width - 90, 72)
        pygame.draw.rect(m.pantalla, (244, 236, 222), m.r_card_vol, border_radius=12)
        pygame.draw.rect(m.pantalla, (200, 175, 145), m.r_card_vol, 2, border_radius=12)

        m.vol_actual = obtener_volumen()
        m.cy_v = m.r_card_vol.centery

        # Botón [-]
        m.r_menos = pygame.Rect(m.r_card_vol.left + 25, m.cy_v - 22, 50, 44)
        m.hov_m = m.r_menos.collidepoint(m.pos_mouse)
        m.col_bm = (235, 115, 85) if m.hov_m else (215, 105, 75)
        pygame.draw.rect(m.pantalla, m.col_bm, m.r_menos, border_radius=8)
        pygame.draw.rect(m.pantalla, (140, 60, 40), m.r_menos, 2, border_radius=8)
        m.f_btn_v = obtener_fuente_para_texto("-", categoria="boton", tamano=22, negrita=True)
        m.pantalla.blit(m.f_btn_v.render("-", True, (255, 255, 255)), m.f_btn_v.render("-", True, (255, 255, 255)).get_rect(center=m.r_menos.center))

        # Barra de volumen
        m.r_barra_bg = pygame.Rect(m.r_menos.right + 20, m.cy_v - 18, 460, 36)
        pygame.draw.rect(m.pantalla, (40, 46, 62), m.r_barra_bg, border_radius=8)
        pygame.draw.rect(m.pantalla, (150, 160, 185), m.r_barra_bg, 2, border_radius=8)

        # Relleno de la barra (por bloques de 10%)
        m.bloques = m.vol_actual // 10
        m.ancho_bloque = (m.r_barra_bg.width - 8) / 10.0
        for m.b in range(m.bloques):
            m.bx = m.r_barra_bg.left + 4 + int(m.b * m.ancho_bloque)
            m.bw = int(m.ancho_bloque) - 3
            m.col_b = (255, 150, 70) if m.b < 4 else ((255, 195, 65) if m.b < 8 else (255, 225, 95))
            pygame.draw.rect(m.pantalla, m.col_b, (m.bx, m.r_barra_bg.top + 4, m.bw, m.r_barra_bg.height - 8), border_radius=4)

        # Botón [+]
        m.r_mas = pygame.Rect(m.r_barra_bg.right + 20, m.cy_v - 22, 50, 44)
        m.hov_p = m.r_mas.collidepoint(m.pos_mouse)
        m.col_bp = (95, 200, 120) if m.hov_p else (85, 180, 110)
        pygame.draw.rect(m.pantalla, m.col_bp, m.r_mas, border_radius=8)
        pygame.draw.rect(m.pantalla, (45, 120, 65), m.r_mas, 2, border_radius=8)
        m.f_btn_mas = obtener_fuente_para_texto("+", categoria="boton", tamano=20, negrita=True)
        m.pantalla.blit(m.f_btn_mas.render("+", True, (255, 255, 255)), m.f_btn_mas.render("+", True, (255, 255, 255)).get_rect(center=m.r_mas.center))

        # Porcentaje numérico badge
        m.r_pct = pygame.Rect(m.r_mas.right + 20, m.cy_v - 22, 85, 44)
        pygame.draw.rect(m.pantalla, (255, 255, 255), m.r_pct, border_radius=8)
        pygame.draw.rect(m.pantalla, (180, 155, 125), m.r_pct, 2, border_radius=8)
        m.str_pct = f"{m.vol_actual}%"
        m.f_pct = obtener_fuente_para_texto(m.str_pct, categoria="boton", tamano=16, negrita=True)
        m.pantalla.blit(m.f_pct.render(m.str_pct, True, (45, 35, 25)), m.f_pct.render(m.str_pct, True, (45, 35, 25)).get_rect(center=m.r_pct.center))

        # Bloque B: Idioma
        m.y_idioma = m.r_card_vol.bottom + 12
        m.txt_idm_b = t("seleccion_idioma")
        m.pantalla.blit(m.f_bloq.render(m.txt_idm_b, True, (65, 45, 32)), (m.rect_panel.left + 45, m.y_idioma))

        m.r_card_idm = pygame.Rect(m.rect_panel.left + 45, m.y_idioma + 24, m.rect_panel.width - 90, 94)
        pygame.draw.rect(m.pantalla, (244, 236, 222), m.r_card_idm, border_radius=12)
        pygame.draw.rect(m.pantalla, (200, 175, 145), m.r_card_idm, 2, border_radius=12)

        m.langs = [
            ("es", "ESPAÑOL", "Español (Latinoamérica / España)"),
            ("en", "ENGLISH", "English (United States / UK)"),
            ("zh", "中文 (CHINO)", "简体中文 (Simplified Chinese)"),
        ]
        m.w_btn_l = (m.r_card_idm.width - 60) // 3
        for m.l_idx, (m.l_code, m.l_tit, m.l_sub) in enumerate(m.langs):
            m.rx_l = m.r_card_idm.left + 20 + m.l_idx * (m.w_btn_l + 10)
            m.r_bl = pygame.Rect(m.rx_l, m.r_card_idm.top + 11, m.w_btn_l, 72)
            m.es_sel = (m.idm_act == m.l_code)
            m.hov_l = m.r_bl.collidepoint(m.pos_mouse)

            m.col_l_bg = (255, 250, 235) if m.es_sel else ((248, 240, 228) if m.hov_l else (238, 228, 212))
            m.col_l_brd = (225, 110, 80) if m.es_sel else ((205, 180, 150) if m.hov_l else (185, 160, 130))
            pygame.draw.rect(m.pantalla, m.col_l_bg, m.r_bl, border_radius=10)
            pygame.draw.rect(m.pantalla, m.col_l_brd, m.r_bl, 3 if m.es_sel else 2, border_radius=10)

            if m.es_sel:
                m.cx_ck, m.cy_ck = m.r_bl.right - 13, m.r_bl.top + 13
                pygame.draw.circle(m.pantalla, (80, 185, 105), (m.cx_ck, m.cy_ck), 8)
                m.pts_ck = [(m.cx_ck - 4, m.cy_ck), (m.cx_ck - 1, m.cy_ck + 3), (m.cx_ck + 4, m.cy_ck - 3)]
                pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_ck, 2)

            m.col_lt = (45, 30, 20) if m.es_sel else (95, 75, 60)
            if contiene_caracteres_cjk(m.l_tit):
                m.f_lt = obtener_fuente_para_texto(m.l_tit, categoria="boton", tamano=16, negrita=True)
                m.t_lt = m.f_lt.render(m.l_tit, True, m.col_lt)
            else:
                m._, m.t_lt = renderizar_texto_pixamuse(m.l_tit, 15, m.col_lt, max_w=m.r_bl.width - 28)
            m.pantalla.blit(m.t_lt, m.t_lt.get_rect(center=(m.r_bl.centerx, m.r_bl.top + 23)))

            dibujar_texto_en_rect(m.pantalla, m.l_sub, pygame.Rect(m.r_bl.left + 6, m.r_bl.top + 36, m.r_bl.width - 12, 32), categoria="texto", tamano=12, color=(80, 60, 45), alineacion="centro", multiline=True, interlineado=1)

        # Bloque C: Música del Menú
        m.y_musica = m.r_card_idm.bottom + 12
        m.txt_mus_b = t("musica_menu_titulo")
        m.pantalla.blit(m.f_bloq.render(m.txt_mus_b, True, (65, 45, 32)), (m.rect_panel.left + 45, m.y_musica))

        m.r_card_musica = pygame.Rect(m.rect_panel.left + 45, m.y_musica + 24, m.rect_panel.width - 90, 102)
        pygame.draw.rect(m.pantalla, (244, 236, 222), m.r_card_musica, border_radius=12)
        pygame.draw.rect(m.pantalla, (200, 175, 145), m.r_card_musica, 2, border_radius=12)

        m.modo_musica_act = obtener_modo_musica_menu()
        m.opciones_musica = [
            ("aleatorio", t("modo_aleatorio"), t("desc_aleatorio")),
            ("caillou", t("modo_caillou"), t("desc_caillou")),
            ("christmas", t("modo_christmas"), t("desc_christmas")),
        ]
        m.w_btn_m = (m.r_card_musica.width - 60) // 3
        for m.m_idx, (m.m_code, m.m_tit, m.m_sub) in enumerate(m.opciones_musica):
            m.rx_m = m.r_card_musica.left + 20 + m.m_idx * (m.w_btn_m + 10)
            m.r_bm = pygame.Rect(m.rx_m, m.r_card_musica.top + 10, m.w_btn_m, 82)
            m.es_sel_m = (m.modo_musica_act == m.m_code)
            m.hov_m = m.r_bm.collidepoint(m.pos_mouse)

            m.col_m_bg = (255, 250, 235) if m.es_sel_m else ((248, 240, 228) if m.hov_m else (238, 228, 212))
            m.col_m_brd = (225, 110, 80) if m.es_sel_m else ((205, 180, 150) if m.hov_m else (185, 160, 130))
            pygame.draw.rect(m.pantalla, m.col_m_bg, m.r_bm, border_radius=10)
            pygame.draw.rect(m.pantalla, m.col_m_brd, m.r_bm, 3 if m.es_sel_m else 2, border_radius=10)

            if m.es_sel_m:
                m.cx_ck, m.cy_ck = m.r_bm.right - 13, m.r_bm.top + 13
                pygame.draw.circle(m.pantalla, (80, 185, 105), (m.cx_ck, m.cy_ck), 8)
                m.pts_ck = [(m.cx_ck - 4, m.cy_ck), (m.cx_ck - 1, m.cy_ck + 3), (m.cx_ck + 4, m.cy_ck - 3)]
                pygame.draw.lines(m.pantalla, (255, 255, 255), False, m.pts_ck, 2)

            m.col_mt = (45, 30, 20) if m.es_sel_m else (95, 75, 60)
            if contiene_caracteres_cjk(m.m_tit):
                m.f_mt = obtener_fuente_para_texto(m.m_tit, categoria="boton", tamano=16, negrita=True)
                m.t_mt = m.f_mt.render(m.m_tit, True, m.col_mt)
            else:
                m._, m.t_mt = renderizar_texto_pixamuse(m.m_tit, 15, m.col_mt, max_w=m.r_bm.width - 28)
            m.pantalla.blit(m.t_mt, m.t_mt.get_rect(center=(m.r_bm.centerx, m.r_bm.top + 20)))

            m.r_sub_m = pygame.Rect(m.r_bm.left + 4, m.r_bm.top + 34, m.r_bm.width - 8, 44)
            dibujar_texto_en_rect(m.pantalla, m.m_sub, m.r_sub_m, categoria="texto", tamano=15, color=(80, 60, 45), alineacion="centro", multiline=True, interlineado=2, padding=1)

        # Nota al pie de ajustes (agrandada y más legible con sombra suave)
        m.txt_not = t("cambios_guardados_auto")
        m.f_not = obtener_fuente_para_texto(m.txt_not, categoria="texto", tamano=14, negrita=True)
        m.pantalla.blit(m.f_not.render(m.txt_not, True, (245, 235, 220)), (m.rect_panel.left + 51, m.rect_panel.bottom - 32))
        m.pantalla.blit(m.f_not.render(m.txt_not, True, (55, 38, 25)), (m.rect_panel.left + 50, m.rect_panel.bottom - 33))

    # =========================================================================
    # SECCIÓN: CONTROLES
    # =========================================================================
    elif m.seccion_opciones_actual == "controles":
        m.w_pj_card = (m.rect_panel.width - 60) // 2
        m.h_pj_card = 356
        m.y_pj_top = m.rect_panel.top + 60

        # --- TARJETA JUGADOR 1 ---
        m.r_card_p1 = pygame.Rect(m.rect_panel.left + 22, m.y_pj_top, m.w_pj_card, m.h_pj_card)
        pygame.draw.rect(m.pantalla, (244, 238, 226), m.r_card_p1, border_radius=14)
        pygame.draw.rect(m.pantalla, (124, 210, 240), m.r_card_p1, 3, border_radius=14)

        m.r_head_p1 = pygame.Rect(m.r_card_p1.left + 14, m.r_card_p1.top + 10, m.r_card_p1.width - 28, 34)
        pygame.draw.rect(m.pantalla, (124, 231, 255), m.r_head_p1, border_radius=8)
        pygame.draw.rect(m.pantalla, (50, 40, 30), m.r_head_p1, 2, border_radius=8)
        m.tit_head_p1 = f"{t('jugador_1').upper()}  (WASD)"
        dibujar_texto_en_rect(m.pantalla, m.tit_head_p1, m.r_head_p1, categoria="boton", tamano=16, color=(35, 30, 25), negrita=True, padding=2)

        m.filas_p1 = [
            (t("accion_moverse"), ["A", "D"], t("desc_moverse")),
            (t("accion_saltar"), ["W"], t("desc_saltar")),
            (t("accion_nadar"), ["W", "S"], t("desc_nadar_p1")),
            (t("accion_empujar"), ["A", "D"], t("desc_empujar")),
            (t("accion_linterna"), ["E", "F", "ESP"], t("desc_linterna")),
        ]
        for m.f_idx, (m.accion, m.teclas, m.desc) in enumerate(m.filas_p1):
            m.yf = m.r_card_p1.top + 52 + m.f_idx * 58
            # Línea 1: Nombre de la acción a la izquierda y teclas alineadas a la derecha
            m.f_act = obtener_fuente_para_texto(m.accion, categoria="boton", tamano=15, negrita=True)
            m.pantalla.blit(m.f_act.render(m.accion, True, (45, 32, 20)), (m.r_card_p1.left + 16, m.yf + 3))

            m.xk = m.r_card_p1.right - 14
            for m.tk in reversed(m.teclas):
                m.kw = 56 if len(m.tk) > 2 else 38
                m.xk -= m.kw
                m.rk = pygame.Rect(m.xk, m.yf, m.kw, 30)
                _dibujar_icono_tecla(m.pantalla, m.tk, m.rk, activo=True, tamano_fuente=15)
                m.xk -= 6

            # Línea 2: Texto descriptivo amplio y claro (completamente separado sin superposición)
            m.f_dsc = obtener_fuente_para_texto(m.desc, categoria="texto", tamano=14, negrita=False)
            m.pantalla.blit(m.f_dsc.render(f"• {m.desc}", True, (80, 60, 45)), (m.r_card_p1.left + 16, m.yf + 33))

            if m.f_idx < len(m.filas_p1) - 1:
                pygame.draw.line(m.pantalla, (230, 218, 200), (m.r_card_p1.left + 14, m.yf + 54), (m.r_card_p1.right - 14, m.yf + 54), 1)

        # --- TARJETA JUGADOR 2 ---
        m.r_card_p2 = pygame.Rect(m.r_card_p1.right + 16, m.y_pj_top, m.w_pj_card, m.h_pj_card)
        pygame.draw.rect(m.pantalla, (244, 238, 226), m.r_card_p2, border_radius=14)
        pygame.draw.rect(m.pantalla, (180, 140, 255), m.r_card_p2, 3, border_radius=14)

        m.r_head_p2 = pygame.Rect(m.r_card_p2.left + 14, m.r_card_p2.top + 10, m.r_card_p2.width - 28, 34)
        pygame.draw.rect(m.pantalla, (180, 140, 255), m.r_head_p2, border_radius=8)
        pygame.draw.rect(m.pantalla, (50, 40, 30), m.r_head_p2, 2, border_radius=8)
        m.tit_head_p2 = f"{t('jugador_2').upper()}  ({t('flechas_direccion')})"
        dibujar_texto_en_rect(m.pantalla, m.tit_head_p2, m.r_head_p2, categoria="boton", tamano=16, color=(35, 30, 25), negrita=True, padding=2)

        m.filas_p2 = [
            (t("accion_moverse"), ["←", "→"], t("desc_moverse")),
            (t("accion_saltar"), ["↑"], t("desc_saltar")),
            (t("accion_nadar"), ["↑", "↓"], t("desc_nadar_p2")),
            (t("accion_empujar"), ["←", "→"], t("desc_empujar")),
            (t("accion_linterna"), ["L", "ENT"], t("desc_linterna")),
        ]
        for m.f_idx, (m.accion, m.teclas, m.desc) in enumerate(m.filas_p2):
            m.yf = m.r_card_p2.top + 52 + m.f_idx * 58
            m.f_act = obtener_fuente_para_texto(m.accion, categoria="boton", tamano=15, negrita=True)
            m.pantalla.blit(m.f_act.render(m.accion, True, (45, 32, 20)), (m.r_card_p2.left + 16, m.yf + 3))

            m.xk = m.r_card_p2.right - 14
            for m.tk in reversed(m.teclas):
                m.kw = 56 if len(m.tk) > 2 else 38
                m.xk -= m.kw
                m.rk = pygame.Rect(m.xk, m.yf, m.kw, 30)
                _dibujar_icono_tecla(m.pantalla, m.tk, m.rk, activo=True, tamano_fuente=15)
                m.xk -= 6

            m.f_dsc = obtener_fuente_para_texto(m.desc, categoria="texto", tamano=14, negrita=False)
            m.pantalla.blit(m.f_dsc.render(f"• {m.desc}", True, (80, 60, 45)), (m.r_card_p2.left + 16, m.yf + 33))

            if m.f_idx < len(m.filas_p2) - 1:
                pygame.draw.line(m.pantalla, (230, 218, 200), (m.r_card_p2.left + 14, m.yf + 54), (m.r_card_p2.right - 14, m.yf + 54), 1)

        # Fila inferior: Tecla R y Menú ESC (Agrandadas y legibles)
        m.r_inf_ctrl = pygame.Rect(m.rect_panel.left + 22, m.r_card_p1.bottom + 10, m.rect_panel.width - 44, 52)
        pygame.draw.rect(m.pantalla, (238, 230, 215), m.r_inf_ctrl, border_radius=10)
        pygame.draw.rect(m.pantalla, (195, 170, 140), m.r_inf_ctrl, 2, border_radius=10)

        m.rk_r = pygame.Rect(m.r_inf_ctrl.left + 18, m.r_inf_ctrl.top + 9, 42, 34)
        _dibujar_icono_tecla(m.pantalla, "R", m.rk_r, activo=False, tamano_fuente=16)
        m.txt_r = t("reiniciar_nivel_act")
        m.f_r = obtener_fuente_para_texto(m.txt_r, categoria="texto", tamano=15, negrita=True)
        m.pantalla.blit(m.f_r.render(m.txt_r, True, (55, 40, 30)), (m.rk_r.right + 12, m.r_inf_ctrl.top + 16))

        m.rk_esc = pygame.Rect(m.r_inf_ctrl.centerx + 20, m.r_inf_ctrl.top + 9, 58, 34)
        _dibujar_icono_tecla(m.pantalla, "ESC", m.rk_esc, activo=False, tamano_fuente=16)
        m.txt_esc = t("pausa_volver_menu")
        m.f_esc = obtener_fuente_para_texto(m.txt_esc, categoria="texto", tamano=15, negrita=True)
        m.pantalla.blit(m.f_esc.render(m.txt_esc, True, (55, 40, 30)), (m.rk_esc.right + 12, m.r_inf_ctrl.top + 16))

    # =========================================================================
    # SECCIÓN: INSTRUCCIONES
    # =========================================================================
    elif m.seccion_opciones_actual == "instrucciones":
        m.w_c = (m.rect_panel.width - 60) // 2
        m.h_c = 202

        m.tarjetas_inst = [
            (
                t("inst_tit_1"),
                [
                    t("inst_1_1"),
                    t("inst_1_2"),
                    t("inst_1_3"),
                    t("inst_1_4"),
                ],
                "llave_puerta"
            ),
            (
                t("inst_tit_2"),
                [
                    t("inst_2_1"),
                    t("inst_2_2"),
                    t("inst_2_3"),
                    t("inst_2_4"),
                ],
                "caja_boton"
            ),
            (
                t("inst_tit_3"),
                [
                    t("inst_3_1"),
                    t("inst_3_2"),
                    t("inst_3_3"),
                    t("inst_3_4"),
                ],
                "soga_salto"
            ),
            (
                t("inst_tit_4"),
                [
                    t("inst_4_1"),
                    t("inst_4_2"),
                    t("inst_4_3"),
                    t("inst_4_4"),
                ],
                "submarino"
            ),
        ]

        for m.idx_t, (m.tit_t, m.lines_t, m.tipo_ico) in enumerate(m.tarjetas_inst):
            m.col_idx = m.idx_t % 2
            m.row_idx = m.idx_t // 2
            m.x_tc = m.rect_panel.left + 20 + m.col_idx * (m.w_c + 20)
            m.y_tc = m.rect_panel.top + 58 + m.row_idx * (m.h_c + 12)
            m.rtc = pygame.Rect(m.x_tc, m.y_tc, m.w_c, m.h_c)

            pygame.draw.rect(m.pantalla, (246, 240, 228), m.rtc, border_radius=12)
            pygame.draw.rect(m.pantalla, (215, 175, 140), m.rtc, 2, border_radius=12)

            # Encabezado con título centrado y multilínea para que nunca se desborde
            m.r_head_t = pygame.Rect(m.rtc.left + 8, m.rtc.top + 8, m.rtc.width - 16, 36)
            pygame.draw.rect(m.pantalla, (235, 218, 195), m.r_head_t, border_radius=6)
            dibujar_texto_en_rect(m.pantalla, m.tit_t, m.r_head_t, categoria="boton", tamano=13, color=(55, 38, 25), negrita=True, multiline=True, padding=2, alineacion="centro")

            # Recuadro de ilustración con los sprites reales del juego
            m.r_box_ico = pygame.Rect(m.rtc.right - 56, m.rtc.top + 46, 48, 48)
            pygame.draw.rect(m.pantalla, (232, 222, 205), m.r_box_ico, border_radius=8)
            pygame.draw.rect(m.pantalla, (180, 150, 120), m.r_box_ico, 1, border_radius=8)

            m.cx_i, m.cy_i = m.r_box_ico.center
            if m.tipo_ico == "llave_puerta":
                m.spr_ico = _obtener_icono_instruccion("llave", 40, 44)
                if m.spr_ico:
                    m.pantalla.blit(m.spr_ico, m.spr_ico.get_rect(center=m.r_box_ico.center))
            elif m.tipo_ico == "caja_boton":
                m.spr_ico = _obtener_icono_instruccion("caja", 44, 42)
                if m.spr_ico:
                    m.pantalla.blit(m.spr_ico, m.spr_ico.get_rect(center=m.r_box_ico.center))
            elif m.tipo_ico == "soga_salto":
                m.pts_soga = [(m.cx_i - 15, m.cy_i - 8), (m.cx_i - 5, m.cy_i + 8), (m.cx_i + 5, m.cy_i - 6), (m.cx_i + 15, m.cy_i + 8)]
                pygame.draw.lines(m.pantalla, (160, 110, 60), False, m.pts_soga, 3)
                pygame.draw.circle(m.pantalla, (124, 231, 255), (m.cx_i - 13, m.cy_i - 8), 5)
                pygame.draw.circle(m.pantalla, (180, 140, 255), (m.cx_i + 13, m.cy_i + 8), 5)
            elif m.tipo_ico == "submarino":
                m.spr_ico = _obtener_icono_instruccion("buceo", 44, 40)
                if m.spr_ico:
                    m.pantalla.blit(m.spr_ico, m.spr_ico.get_rect(center=m.r_box_ico.center))

            for m.l_num, m.line_txt in enumerate(m.lines_t):
                m.yf_l = m.rtc.top + 50 + m.l_num * 36
                m.bx = m.rtc.left + 14
                m.by = m.yf_l + 6
                pygame.draw.rect(m.pantalla, (215, 175, 140), (m.bx + 1, m.by + 1, 4, 4))
                pygame.draw.rect(m.pantalla, (65, 45, 30), (m.bx, m.by, 4, 4))

                m.clean_txt = m.line_txt.lstrip("•- \t")
                m.f_lin = obtener_fuente_para_texto(m.clean_txt, categoria="dialogos", tamano=18, negrita=True)
                m.ts_lin = m.f_lin.render(m.clean_txt, True, (45, 32, 20))
                m.pantalla.blit(m.ts_lin, (m.rtc.left + 24, m.yf_l))
                m.pantalla.blit(m.ts_lin, (m.rtc.left + 25, m.yf_l))

    # 5. Botón Volver al Menú (mundos/boton-volver)
    hov_vcfg = m.btn_volver_config.collidepoint(m.pos_mouse)
    spr_vcfg_norm = m._obtener_boton_volver("normal", m.idm_act)
    spr_vcfg_hov = m._obtener_boton_volver("hover", m.idm_act)
    spr_vcfg = spr_vcfg_hov if (hov_vcfg and spr_vcfg_hov) else spr_vcfg_norm
    if spr_vcfg:
        m.pantalla.blit(spr_vcfg, m.btn_volver_config)
    else:
        m.col_v = (255, 255, 255) if hov_vcfg else (242, 234, 222)
        pygame.draw.rect(m.pantalla, m.col_v, m.btn_volver_config, border_radius=10)
        pygame.draw.rect(m.pantalla, (185, 155, 125), m.btn_volver_config, width=2, border_radius=10)
        dibujar_texto_en_rect(m.pantalla, t("volver_al_menu"), m.btn_volver_config, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)


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



class _EstadoMenu:
    """
    Estado compartido de las pantallas del menú (antes eran variables locales de main()).
    Cada pantalla tiene su función de eventos y de dibujo que reciben este objeto; main()
    hace la configuración inicial y el loop. Los atributos se crean en main() a medida que
    se inicializan; las funciones auxiliares anidadas también quedan colgadas acá.
    """


def main():
    m = _EstadoMenu()   # estado compartido de los menús (ver _EstadoMenu)
    import os
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    m.pantalla = crear_ventana()
    pygame.display.set_caption("Pico Park")
    precargar_botones_comunes()
    m.reloj = pygame.time.Clock()
    seleccionar_musica_menu_aleatoria()
    reproducir_musica("menu")
    m.fuente_pixel_titulo = obtener_fuente_titulo(TAMANO_TITULO, tamano_fallback=55)
    m.fuente_pixel_btn_grande = obtener_fuente_botones(TAMANO_BOTON_GRANDE, tamano_fallback=32)
    m.fuente_pixel_btn = obtener_fuente_botones(TAMANO_BOTON, tamano_fallback=32)
    m.fuente_pixel_sub_btn = obtener_fuente_botones(TAMANO_ITEM_TITULO, tamano_fallback=24)
    m.fuente_pixel_card_btn = obtener_fuente_botones(TAMANO_ITEM_TITULO, tamano_fallback=25)
    m.fuente_pixel_badge = obtener_fuente_botones(TAMANO_BADGE, tamano_fallback=28)

    m.fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_GRANDE, tamano_fallback=55)
    m.fuente_subtitulo = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    m.fuente_btn = obtener_fuente_botones(TAMANO_BOTON_GRANDE, tamano_fallback=32)
    m.fuente_texto = obtener_fuente_texto(TAMANO_TEXTO_GRANDE)
    m.fuente_sub_btn = obtener_fuente_pequena(TAMANO_PEQUENA)
    m.fuente_contador = obtener_fuente_contador(TAMANO_CONTADOR)
    m.fuente_dialogos = obtener_fuente_dialogos(TAMANO_DIALOGOS)
    m.fuente_decorativa = obtener_fuente_decorativa(TAMANO_DECORATIVA)
    m.fuentes_menu = {
        "titulo": m.fuente_pixel_titulo,
        "tab": obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=34),
        "card": obtener_fuente_boton(TAMANO_CARD, tamano_fallback=28),
    }
    m.fuente_card_titulo = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    m.fuente_card_sub = obtener_fuente_pequena(28)

    m.ANCHO_MENU = m.pantalla.get_width()
    m.ALTO_MENU = m.pantalla.get_height()
    _init_copos_modo(m.ANCHO_MENU, m.ALTO_MENU)

    m.niveles_desbloqueados = crear_desbloqueados_inicial()
    m.partida_actual_id = None
    m.partida_actual_nombre = None
    m.partida_actual_password = None
    m.snapshot_guardado = copy.deepcopy(m.niveles_desbloqueados)
    m.sesion_activa = False
    m.partida_cargada_flag = False
    m.partida_creada_flag = False

    m.W_BOTON_HUD, m.H_BOTON_HUD = 44, 52
    m.MARGEN_DER, m.MARGEN_SUP = 18, 16
    m.rect_btn_x = pygame.Rect(m.ANCHO_MENU - m.MARGEN_DER - m.W_BOTON_HUD, m.MARGEN_SUP, m.W_BOTON_HUD, m.H_BOTON_HUD)

    # Carga anticipada exclusiva de lo indispensable para el Menú Principal
    m.spr_x_normal = cargar_boton_escalado("boton-x.png", m.W_BOTON_HUD, m.H_BOTON_HUD)
    m.spr_x_hover = aclarar_boton(m.spr_x_normal)
    m.spr_x_semi = None
    m.spr_x_apretado = None

    m.fondo_btn_x = None

    # Botones principales con proporción nativa exacta 3.4000 (5440x1600 -> 272x80)
    m.ANCHO_BOTON, m.ALTO_BOTON, m.ESPACIO = 272, 80, 14
    m.x_centro = (m.ANCHO_MENU - m.ANCHO_BOTON) // 2
    m.total_h_menu = (m.ALTO_BOTON * 4) + (m.ESPACIO * 3)
    m.y_inicio_principal = (m.ALTO_MENU - m.total_h_menu) // 2 + 35

    m.spr_jugar_normal = cargar_boton_escalado("Menu/jugar.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("jugar.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_jugar_hover = aclarar_boton(m.spr_jugar_normal)
    m.spr_jugar_semi = cargar_boton_escalado("Menu/jugar-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("jugar-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_jugar_apretado = cargar_boton_escalado("Menu/jugar-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("jugar-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)

    m.spr_personajes_normal = cargar_boton_escalado("Menu/personajes.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("personajes.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_personajes_hover = aclarar_boton(m.spr_personajes_normal)
    m.spr_personajes_semi = cargar_boton_escalado("Menu/personajes-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("personajes-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_personajes_apretado = cargar_boton_escalado("Menu/personajes-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("personajes-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)

    m.spr_opciones_normal = cargar_boton_escalado("Menu/opciones.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("opciones.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_opciones_hover = aclarar_boton(m.spr_opciones_normal)
    m.spr_opciones_semi = cargar_boton_escalado("Menu/opciones-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("opciones-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_opciones_apretado = cargar_boton_escalado("Menu/opciones-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("opciones-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)

    m.spr_salir_normal = cargar_boton_escalado("Menu/salir.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("salir.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_salir_hover = aclarar_boton(m.spr_salir_normal)
    m.spr_salir_semi = cargar_boton_escalado("Menu/salir-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("salir-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
    m.spr_salir_apretado = cargar_boton_escalado("Menu/salir-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON) or cargar_boton_escalado("salir-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)

    m.btn_jugar = pygame.Rect(m.x_centro, m.y_inicio_principal, m.ANCHO_BOTON, m.ALTO_BOTON)
    m.btn_personajes = pygame.Rect(m.x_centro, m.y_inicio_principal + (m.ALTO_BOTON + m.ESPACIO), m.ANCHO_BOTON, m.ALTO_BOTON)
    m.btn_config = pygame.Rect(m.x_centro, m.y_inicio_principal + (m.ALTO_BOTON + m.ESPACIO) * 2, m.ANCHO_BOTON, m.ALTO_BOTON)
    m.btn_salir = pygame.Rect(m.x_centro, m.y_inicio_principal + (m.ALTO_BOTON + m.ESPACIO) * 3, m.ANCHO_BOTON, m.ALTO_BOTON)

    m.fondo_limpio_btn = pygame.Surface((m.ANCHO_BOTON, m.ALTO_BOTON))
    m.fondo_limpio_btn.fill((30, 30, 30))

    m.color_p1 = "Celeste"
    m.color_p2 = "Violeta"
    m.accesorio_p1, m.accesorio_p2 = _seleccionar_accesorios_sesion_aleatorios(m.color_p1, m.color_p2)
    m.personalizacion_modificada_en_menu = False
    m.tab_personajes_actual = "colores"
    m.items_por_pag = 6
    m.disp_p1_todos = [a["id"] for a in obtener_accesorios_disponibles(m.color_p1)]
    m.disp_p2_todos = [a["id"] for a in obtener_accesorios_disponibles(m.color_p2)]
    m.pagina_acc_p1 = (m.disp_p1_todos.index(m.accesorio_p1) // m.items_por_pag) if m.accesorio_p1 in m.disp_p1_todos else 0
    m.pagina_acc_p2 = (m.disp_p2_todos.index(m.accesorio_p2) // m.items_por_pag) if m.accesorio_p2 in m.disp_p2_todos else 0

    m.W_VOLVER, m.H_VOLVER = 238, 70
    m.btn_volver_personajes = pygame.Rect((m.ANCHO_MENU - m.W_VOLVER) // 2, m.ALTO_MENU - 75, m.W_VOLVER, m.H_VOLVER)
    m.btn_guardar = m.btn_volver_personajes
    m.btn_volver_config = pygame.Rect((m.ANCHO_MENU - m.W_VOLVER) // 2, m.ALTO_MENU - 75, m.W_VOLVER, m.H_VOLVER)
    m.btn_volver_creditos = pygame.Rect((m.ANCHO_MENU - m.W_VOLVER) // 2, m.ALTO_MENU - 85, m.W_VOLVER, m.H_VOLVER)

    m.seccion_opciones_actual = "configuracion"
    m.rect_btn_sec_cfg = pygame.Rect(70, 120, 240, 64)
    m.rect_btn_sec_ctrl = pygame.Rect(70, 200, 240, 64)
    m.rect_btn_sec_inst = pygame.Rect(70, 280, 240, 64)
    m.rect_btn_x_opciones = pygame.Rect(m.ANCHO_MENU - 62, 16, 44, 52)

    # Iconos superiores exclusivos de Selección de Niveles (Configuración, Casita y X) con proporción nativa 0.8496
    m.W_ICONO_NIVELES, m.H_ICONO_NIVELES = 44, 52
    m.rect_btn_x_niveles = pygame.Rect(m.ANCHO_MENU - m.MARGEN_DER - m.W_ICONO_NIVELES, m.MARGEN_SUP, m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
    m.rect_btn_casa_niveles = pygame.Rect(m.rect_btn_x_niveles.left - 12 - m.W_ICONO_NIVELES, m.MARGEN_SUP, m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
    m.rect_btn_config_niveles = pygame.Rect(m.rect_btn_casa_niveles.left - 12 - m.W_ICONO_NIVELES, m.MARGEN_SUP, m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)

    # Botones interactivos para Modo de Juego (Continuar vs Nueva Partida)
    m.W_MODO, m.H_MODO = 425, 100
    m.x_modo = (m.ANCHO_MENU - m.W_MODO) // 2
    m.btn_continuar = pygame.Rect(m.x_modo, (m.ALTO_MENU // 2) - 85, m.W_MODO, m.H_MODO)
    m.btn_nueva_partida = pygame.Rect(m.x_modo, (m.ALTO_MENU // 2) + 35, m.W_MODO, m.H_MODO)
    m.btn_volver_modo = pygame.Rect((m.ANCHO_MENU - m.W_VOLVER) // 2, m.ALTO_MENU - 85, m.W_VOLVER, m.H_VOLVER)

    # Variables de sprites de submenús (inicialmente None, carga bajo demanda)
    m.spr_casa_normal = None
    m.spr_casa_hover = None
    m.spr_casa_semi = None
    m.spr_casa_apretado = None

    m.spr_confign_normal = None
    m.spr_confign_hover = None
    m.spr_confign_semi = None
    m.spr_confign_apretado = None

    m.spr_xn_normal = None
    m.spr_xn_hover = None
    m.spr_xn_semi = None
    m.spr_xn_apretado = None

    m.spr_volver_normal = None
    m.spr_volver_hover = None
    m.spr_volver_semi = None
    m.spr_volver_apretado = None

    m.spr_volver_modo_normal = None
    m.spr_volver_modo_hover = None
    m.spr_volver_modo_semi = None
    m.spr_volver_modo_apretado = None

    m.spr_menu_nav_normal = None
    m.spr_menu_nav_hover = None
    m.spr_menu_nav_semi = None
    m.spr_menu_nav_apretado = None

    m.spr_continuar_normal = None
    m.spr_continuar_hover = None
    m.spr_continuar_semi = None
    m.spr_continuar_apretado = None

    m.spr_nueva_modo_normal = None
    m.spr_nueva_modo_hover = None
    m.spr_nueva_modo_semi = None
    m.spr_nueva_modo_apretado = None

    m.spr_nueva_lista_normal = None
    m.spr_nueva_lista_hover = None
    m.spr_nueva_lista_semi = None
    m.spr_nueva_lista_apretado = None

    m.spr_volver_partidas_normal = None
    m.spr_volver_partidas_hover = None
    m.spr_volver_partidas_semi = None
    m.spr_volver_partidas_apretado = None

    m.spr_nueva_primera_normal = None
    m.spr_nueva_primera_hover = None
    m.spr_nueva_primera_semi = None
    m.spr_nueva_primera_apretado = None

    m.spr_cargar_normal = None
    m.spr_cargar_hover = None
    m.spr_cargar_semi = None
    m.spr_cargar_apretado = None

    m.dict_sprites_tarjeta = {
        "cargar_normal": None,
        "cargar_hover": None,
        "cargar_semi": None,
        "cargar_apretado": None,
        "gestionar_normal": None,
        "gestionar_hover": None,
        "gestionar_semi": None,
        "gestionar_apretado": None,
        "borrar_normal": None,
        "borrar_hover": None,
        "borrar_semi": None,
        "borrar_apretado": None,
    }

    m.TAM_CTRL = 54
    m.spr_ctrl_w = None
    m.spr_ctrl_a = None
    m.spr_ctrl_s = None
    m.spr_ctrl_d = None
    m.spr_ctrl_arr = None
    m.spr_ctrl_izq = None
    m.spr_ctrl_aba = None
    m.spr_ctrl_der = None

    def _asegurar_semi_apretados_menu():
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        if m.spr_jugar_semi is None:
            m.spr_jugar_semi = cargar_boton_escalado("jugar-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_jugar_apretado = cargar_boton_escalado("jugar-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_personajes_semi = cargar_boton_escalado("personajes-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_personajes_apretado = cargar_boton_escalado("personajes-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_opciones_semi = cargar_boton_escalado("opciones-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_opciones_apretado = cargar_boton_escalado("opciones-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_salir_semi = cargar_boton_escalado("salir-preapretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_salir_apretado = cargar_boton_escalado("salir-apretado.png", m.ANCHO_BOTON, m.ALTO_BOTON)
            m.spr_x_semi = cargar_boton_escalado("boton-x-semiapretado.png", m.W_BOTON_HUD, m.H_BOTON_HUD)
            m.spr_x_apretado = cargar_boton_escalado("boton-x-apretado.png", m.W_BOTON_HUD, m.H_BOTON_HUD)
    m._asegurar_semi_apretados_menu = _asegurar_semi_apretados_menu

    def _cargar_recursos_volver():
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        if m.spr_volver_normal is None:
            m.spr_volver_normal = cargar_boton_escalado("mundos/boton-volver.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_volver_hover = aclarar_boton(m.spr_volver_normal)
            m.spr_volver_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_volver_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", m.W_VOLVER, m.H_VOLVER)

            m.spr_menu_nav_normal = cargar_boton_escalado("Ventanas/boton-menu.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_menu_nav_hover = aclarar_boton(m.spr_menu_nav_normal)
            m.spr_menu_nav_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_menu_nav_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", m.W_VOLVER, m.H_VOLVER)
    m._cargar_recursos_volver = _cargar_recursos_volver

    def _cargar_recursos_modo_juego():
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        m._cargar_recursos_volver()
        if m.spr_continuar_normal is None:
            # Botones oficiales de la carpeta Sprites/Botones
            m.spr_continuar_normal = cargar_boton_escalado("Menu/boton-continuar-cargar....png", m.W_MODO, m.H_MODO) or cargar_boton_escalado("boton-continuar-cargar....png", m.W_MODO, m.H_MODO)
            m.spr_continuar_hover = aclarar_boton(m.spr_continuar_normal)
            m.spr_continuar_semi = cargar_boton_escalado("Menu/boton-continuar-cargar...-semiapretado.png", m.W_MODO, m.H_MODO) or cargar_boton_escalado("boton-continuar-cargar...-semiapretado.png", m.W_MODO, m.H_MODO)
            m.spr_continuar_apretado = cargar_boton_escalado("Menu/boton-continuar-cargar...-apretado.png", m.W_MODO, m.H_MODO) or cargar_boton_escalado("boton-continuar-cargar...-apretado.png", m.W_MODO, m.H_MODO)

            m.spr_nueva_modo_normal = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", m.W_MODO, m.H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar....png", m.W_MODO, m.H_MODO)
            m.spr_nueva_modo_hover = aclarar_boton(m.spr_nueva_modo_normal)
            m.spr_nueva_modo_semi = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar...-semiapretado.png", m.W_MODO, m.H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar...-semiapretado.png", m.W_MODO, m.H_MODO)
            m.spr_nueva_modo_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar...-apretado.png", m.W_MODO, m.H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar...-apretado.png", m.W_MODO, m.H_MODO)

            m.spr_volver_modo_normal = cargar_boton_escalado("mundos/boton-volver.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-volver.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_volver_modo_hover = aclarar_boton(m.spr_volver_modo_normal)
            m.spr_volver_modo_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-volver-semiapretado.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_volver_modo_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-volver-apretado.png", m.W_VOLVER, m.H_VOLVER)
    m._cargar_recursos_modo_juego = _cargar_recursos_modo_juego

    def _cargar_recursos_partidas():
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        m._cargar_recursos_volver()
        if m.spr_nueva_lista_normal is None:
            # Botones oficiales para la lista de partidas guardadas
            m.spr_nueva_lista_normal = cargar_boton_escalado("mundos/boton-nueva-partida.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-nueva-partida.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_nueva_lista_hover = aclarar_boton(m.spr_nueva_lista_normal)
            m.spr_nueva_lista_semi = cargar_boton_escalado("mundos/boton-nueva-partida-semiapretado.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-nueva-partida-semiapretado.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_nueva_lista_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-apretado.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-nueva-partida-apretado.png", m.W_VOLVER, m.H_VOLVER)

            m.spr_volver_partidas_normal = cargar_boton_escalado("mundos/boton-volver.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-volver.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_volver_partidas_hover = aclarar_boton(m.spr_volver_partidas_normal)
            m.spr_volver_partidas_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-volver-semiapretado.png", m.W_VOLVER, m.H_VOLVER)
            m.spr_volver_partidas_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("boton-volver-apretado.png", m.W_VOLVER, m.H_VOLVER)

            m.spr_nueva_primera_normal = cargar_boton_escalado("mundos/boton-nueva-partida.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida.png", 272, 80)
            m.spr_nueva_primera_hover = aclarar_boton(m.spr_nueva_primera_normal)
            m.spr_nueva_primera_semi = cargar_boton_escalado("mundos/boton-nueva-partida-semiapretado.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida-semiapretado.png", 272, 80)
            m.spr_nueva_primera_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-apretado.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida-apretado.png", 272, 80)

            # Botón oficial CARGAR en tarjetas de partida
            m.spr_cargar_normal = cargar_boton_escalado("mundos/boton-cargar.png", 126, 38) or cargar_boton_escalado("boton-cargar.png", 126, 38)
            m.spr_cargar_hover = aclarar_boton(m.spr_cargar_normal)
            m.spr_cargar_semi = cargar_boton_escalado("mundos/boton-cargar-semiapretado.png", 126, 38) or cargar_boton_escalado("boton-cargar-semiapretado.png", 126, 38)
            m.spr_cargar_apretado = cargar_boton_escalado("mundos/boton-cargar-apretado.png", 126, 38) or cargar_boton_escalado("boton-cargar-apretado.png", 126, 38)

            # Botones temáticos GESTIONAR y BORRAR basados en los marcos oficiales de Sprites/Botones
            spr_gest_normal = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 0)
            spr_gest_hover = aclarar_boton(spr_gest_normal)
            spr_gest_semi = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 1)
            spr_gest_apretado = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 2)

            spr_borrar_normal = generar_boton_con_texto("Menu/salir.png", 96, 38, "BORRAR", (125, 48, 17), 14, 0)
            spr_borrar_hover = aclarar_boton(spr_borrar_normal)
            spr_borrar_semi = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, "BORRAR", (125, 48, 17), 14, 1)
            spr_borrar_apretado = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, "BORRAR", (125, 48, 17), 14, 2)

            m.dict_sprites_tarjeta["cargar_normal"] = m.spr_cargar_normal
            m.dict_sprites_tarjeta["cargar_hover"] = m.spr_cargar_hover
            m.dict_sprites_tarjeta["cargar_semi"] = m.spr_cargar_semi
            m.dict_sprites_tarjeta["cargar_apretado"] = m.spr_cargar_apretado

            m.dict_sprites_tarjeta["gestionar_normal"] = spr_gest_normal
            m.dict_sprites_tarjeta["gestionar_hover"] = spr_gest_hover
            m.dict_sprites_tarjeta["gestionar_semi"] = spr_gest_semi
            m.dict_sprites_tarjeta["gestionar_apretado"] = spr_gest_apretado

            m.dict_sprites_tarjeta["borrar_normal"] = spr_borrar_normal
            m.dict_sprites_tarjeta["borrar_hover"] = spr_borrar_hover
            m.dict_sprites_tarjeta["borrar_semi"] = spr_borrar_semi
            m.dict_sprites_tarjeta["borrar_apretado"] = spr_borrar_apretado
    m._cargar_recursos_partidas = _cargar_recursos_partidas

    def _cargar_recursos_niveles():
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        if m.spr_casa_normal is None:
            m.spr_casa_normal = cargar_boton_escalado("HUD/boton-casa.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
            m.spr_casa_hover = aclarar_boton(m.spr_casa_normal)
            m.spr_casa_semi = cargar_boton_escalado("HUD/boton-casa-semiapretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa-semiapretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
            m.spr_casa_apretado = cargar_boton_escalado("HUD/boton-casa-apretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa-apretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)

            m.spr_confign_normal = cargar_boton_escalado("HUD/boton-configuracion.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
            m.spr_confign_hover = aclarar_boton(m.spr_confign_normal)
            m.spr_confign_semi = cargar_boton_escalado("HUD/boton-configuracion-semiapretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion-semiapretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
            m.spr_confign_apretado = cargar_boton_escalado("HUD/boton-configuracion-apretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion-apretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)

            m.spr_xn_normal = cargar_boton_escalado("HUD/boton-x.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-x.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
            m.spr_xn_hover = aclarar_boton(m.spr_xn_normal)
            m.spr_xn_semi = cargar_boton_escalado("HUD/boton-x-semiapretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-x-semiapretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
            m.spr_xn_apretado = cargar_boton_escalado("HUD/boton-x-apretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES) or cargar_boton_escalado("boton-x-apretado.png", m.W_ICONO_NIVELES, m.H_ICONO_NIVELES)
    m._cargar_recursos_niveles = _cargar_recursos_niveles

    def _cargar_recursos_controles():
        pass  # (antes: nonlocal; ahora son atributos de m)
        pass  # (antes: nonlocal; ahora son atributos de m)
        m._cargar_recursos_volver()
        if m.spr_ctrl_w is None:
            m.spr_ctrl_w = cargar_boton_escalado("Controles/boton-w.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_a = cargar_boton_escalado("Controles/boton-a.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_s = cargar_boton_escalado("Controles/boton-s.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_d = cargar_boton_escalado("Controles/boton-d.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_arr = cargar_boton_escalado("Controles/boton-arriba.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_izq = cargar_boton_escalado("Controles/boton-izquierda.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_aba = cargar_boton_escalado("Controles/boton-abajo.png", m.TAM_CTRL, m.TAM_CTRL)
            m.spr_ctrl_der = cargar_boton_escalado("Controles/boton-derecha.png", m.TAM_CTRL, m.TAM_CTRL)
    m._cargar_recursos_controles = _cargar_recursos_controles

    # Cargar y preparar de forma anticipada todos los recursos de botones para todas las pantallas
    m._asegurar_semi_apretados_menu()
    m._cargar_recursos_volver()
    m._cargar_recursos_modo_juego()
    m._cargar_recursos_partidas()
    m._cargar_recursos_niveles()
    m._cargar_recursos_controles()

    # Funciones de soporte dinámico multiidioma para botones
    m._cache_botones_modo = {}
    m._cache_botones_volver = {}
    m._cache_botones_nueva_lista = {}
    m._cache_botones_primera = {}
    m._cache_sprites_tarjeta = {}
    m._cache_botones_menu = {}

    def _obtener_boton_modo(tipo, estado, idioma):
        tipo_norm = "nueva" if tipo in ("nueva", "nueva_partida") else tipo
        if idioma == "es":
            if tipo_norm == "continuar":
                if estado == "hover": return m.spr_continuar_hover
                if estado == "semi": return m.spr_continuar_semi
                if estado == "apretado": return m.spr_continuar_apretado
                return m.spr_continuar_normal
            else:
                if estado == "hover": return m.spr_nueva_modo_hover
                if estado == "semi": return m.spr_nueva_modo_semi
                if estado == "apretado": return m.spr_nueva_modo_apretado
                return m.spr_nueva_modo_normal

        clave = (tipo_norm, estado, idioma)
        if clave in m._cache_botones_modo:
            return m._cache_botones_modo[clave]

        if tipo_norm == "continuar":
            base_path = "Menu/boton-continuar-cargar....png"
            if estado == "semi": base_path = "Menu/boton-continuar-cargar...-semiapretado.png"
            elif estado == "apretado": base_path = "Menu/boton-continuar-cargar...-apretado.png"
            col_bg = (155, 255, 124) if estado not in ("semi", "apretado") else ((142, 237, 115) if estado == "semi" else (124, 211, 103))
            col_tit = (18, 55, 24)
            col_sub = (25, 75, 30)
            tit = t("continuar")
            sub = t("sub_continuar")
        else:
            base_path = "mundos/boton-nueva-partida-reiniciar....png"
            if estado == "semi": base_path = "mundos/boton-nueva-partida-reiniciar...-semiapretado.png"
            elif estado == "apretado": base_path = "mundos/boton-nueva-partida-reiniciar...-apretado.png"
            col_bg = (254, 137, 134) if estado not in ("semi", "apretado") else ((242, 126, 123) if estado == "semi" else (225, 114, 112))
            col_tit = (95, 25, 35)
            col_sub = (115, 30, 42)
            tit = t("nueva_partida")
            sub = t("sub_nueva_partida")

        w, h = m.W_MODO, m.H_MODO
        btn_base = cargar_boton_escalado(base_path, w, h)
        if not btn_base:
            btn_base = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", w, h)
        surf = btn_base.copy()

        # Limpiar suavemente solo la cara interior manteniendo intactos los bordes y biseles 3D
        shift_y = 10 if estado == 'apretado' else (5 if estado == 'semi' else 0)
        pad_top = 6 + shift_y
        h_int = 68
        rect_interior = pygame.Rect(6, pad_top, w - 12, h_int)
        pygame.draw.rect(surf, col_bg, rect_interior)

        if idioma == "zh":
            f_tit = obtener_fuente_cjk(24, negrita=True)
            f_sub = obtener_fuente_cjk(14, negrita=False)
            t_tit = f_tit.render(tit, True, col_tit)
        else:
            _, t_tit = renderizar_texto_pixamuse(tit, 20, col_tit, max_w=w - 24)
            f_sub = obtener_fuente_para_texto(sub, categoria="texto", tamano=12, negrita=False)

        t_sub = f_sub.render(sub, True, col_sub)

        offset_y = shift_y
        bbox_tit = t_tit.get_bounding_rect()
        if bbox_tit.width > 0 and bbox_tit.height > 0:
            surf.blit(t_tit, (round(w / 2.0 - (bbox_tit.left + bbox_tit.width / 2.0)), round(30 + offset_y - (bbox_tit.top + bbox_tit.height / 2.0))))
        else:
            surf.blit(t_tit, t_tit.get_rect(center=(w // 2, 30 + offset_y)))

        r_sub = t_sub.get_rect(center=(w // 2, 59 + offset_y))
        surf.blit(t_sub, r_sub)

        if estado == "hover":
            surf = aclarar_boton(surf)

        m._cache_botones_modo[clave] = surf
        return surf
    m._obtener_boton_modo = _obtener_boton_modo

    def _obtener_boton_volver(estado, idioma, w=m.W_VOLVER, h=m.H_VOLVER):
        if idioma == "es":
            if w == m.W_VOLVER and h == m.H_VOLVER:
                if estado == "hover": return m.spr_volver_modo_hover
                if estado == "semi": return m.spr_volver_modo_semi
                if estado == "apretado": return m.spr_volver_modo_apretado
                return m.spr_volver_modo_normal
            base_p = "mundos/boton-volver.png"
            if estado == "semi": base_p = "mundos/boton-volver-semiapretado.png"
            elif estado == "apretado": base_p = "mundos/boton-volver-apretado.png"
            btn = cargar_boton_escalado(base_p, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
            if estado == "hover":
                btn = aclarar_boton(btn)
            return btn

        clave = (estado, idioma, w, h)
        if clave in m._cache_botones_volver:
            return m._cache_botones_volver[clave]

        base_path = "mundos/boton-volver.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-volver-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-volver-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
        surf = btn_base.copy()

        col_interior = (212, 212, 212) if estado not in ("semi", "apretado") else ((200, 200, 200) if estado == "semi" else (181, 181, 181))
        shift_y = 7 if estado == 'apretado' else (3 if estado == 'semi' else 0)
        pad_top = 5 + shift_y
        h_face = 44
        rect_interior = pygame.Rect(6, pad_top, w - 12, h_face)
        pygame.draw.rect(surf, col_interior, rect_interior)

        txt_v = t("volver")
        if idioma == "zh":
            f_v = obtener_fuente_cjk(min(24, max(12, int(round(h * 0.40)))), negrita=True)
            t_v = f_v.render(txt_v, True, (60, 60, 60))
        else:
            _, t_v = renderizar_texto_pixamuse(txt_v, max(10, int(round(h * 0.29))), (60, 60, 60), max_w=w - 20)

        cy_v = round(h * 0.42) + shift_y
        bbox_v = t_v.get_bounding_rect()
        if bbox_v.width > 0 and bbox_v.height > 0:
            surf.blit(t_v, (round(w / 2.0 - (bbox_v.left + bbox_v.width / 2.0)), round(cy_v - (bbox_v.top + bbox_v.height / 2.0))))
        else:
            surf.blit(t_v, t_v.get_rect(center=(w // 2, cy_v)))

        if estado == "hover":
            surf = aclarar_boton(surf)

        m._cache_botones_volver[clave] = surf
        return surf
    m._obtener_boton_volver = _obtener_boton_volver

    def _obtener_boton_nueva_lista(estado, idioma):
        if idioma == "es":
            if estado == "hover": return m.spr_nueva_lista_hover
            if estado == "semi": return m.spr_nueva_lista_semi
            if estado == "apretado": return m.spr_nueva_lista_apretado
            return m.spr_nueva_lista_normal

        clave = (estado, idioma)
        if clave in m._cache_botones_nueva_lista:
            return m._cache_botones_nueva_lista[clave]

        base_path = "mundos/boton-nueva-partida.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-nueva-partida-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-nueva-partida-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, m.W_VOLVER, m.H_VOLVER) or cargar_boton_escalado("mundos/boton-nueva-partida.png", m.W_VOLVER, m.H_VOLVER)
        surf = btn_base.copy()

        col_interior = (255, 159, 99) if estado not in ("semi", "apretado") else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        shift_y = 7 if estado == 'apretado' else (3 if estado == 'semi' else 0)
        pad_top = 5 + shift_y
        h_face = 44
        rect_interior = pygame.Rect(6, pad_top, m.W_VOLVER - 12, h_face)
        pygame.draw.rect(surf, col_interior, rect_interior)

        txt_nl = t("nueva_partida")
        if idioma == "zh":
            f_nl = obtener_fuente_cjk(20, negrita=True)
            t_nl = f_nl.render(txt_nl, True, (115, 35, 20))
        else:
            _, t_nl = renderizar_texto_pixamuse(txt_nl, max(10, int(round(m.H_VOLVER * 0.28))), (115, 35, 20), max_w=m.W_VOLVER - 20)

        cy_nl = round(m.H_VOLVER * 0.42) + shift_y
        bbox_nl = t_nl.get_bounding_rect()
        if bbox_nl.width > 0 and bbox_nl.height > 0:
            surf.blit(t_nl, (round(m.W_VOLVER / 2.0 - (bbox_nl.left + bbox_nl.width / 2.0)), round(cy_nl - (bbox_nl.top + bbox_nl.height / 2.0))))
        else:
            surf.blit(t_nl, t_nl.get_rect(center=(m.W_VOLVER // 2, cy_nl)))

        if estado == "hover":
            surf = aclarar_boton(surf)

        m._cache_botones_nueva_lista[clave] = surf
        return surf
    m._obtener_boton_nueva_lista = _obtener_boton_nueva_lista

    def _obtener_boton_primera_partida(estado, idioma):
        if idioma == "es":
            if estado == "hover": return m.spr_nueva_primera_hover
            if estado == "semi": return m.spr_nueva_primera_semi
            if estado == "apretado": return m.spr_nueva_primera_apretado
            return m.spr_nueva_primera_normal

        clave = (estado, idioma)
        if clave in m._cache_botones_primera:
            return m._cache_botones_primera[clave]

        base_path = "mundos/boton-nueva-partida.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-nueva-partida-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-nueva-partida-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, 272, 80) or cargar_boton_escalado("mundos/boton-nueva-partida.png", 272, 80)
        surf = btn_base.copy()
        col_interior = (255, 159, 99) if estado not in ("semi", "apretado") else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        shift_y = 8 if estado == 'apretado' else (4 if estado == 'semi' else 0)
        pad_top = 6 + shift_y
        h_face = 50
        rect_interior = pygame.Rect(6, pad_top, 272 - 12, h_face)
        pygame.draw.rect(surf, col_interior, rect_interior)

        txt_p = t("comenzar_aventura")
        if idioma == "zh":
            f_p = obtener_fuente_cjk(22, negrita=True)
            t_p = f_p.render(txt_p, True, (115, 35, 20))
        else:
            _, t_p = renderizar_texto_pixamuse(txt_p, 22, (115, 35, 20), max_w=272 - 24)

        cy_p = 33 + shift_y
        bbox_p = t_p.get_bounding_rect()
        if bbox_p.width > 0 and bbox_p.height > 0:
            surf.blit(t_p, (round(136 - (bbox_p.left + bbox_p.width / 2.0)), round(cy_p - (bbox_p.top + bbox_p.height / 2.0))))
        else:
            surf.blit(t_p, t_p.get_rect(center=(136, cy_p)))

        if estado == "hover":
            surf = aclarar_boton(surf)

        m._cache_botones_primera[clave] = surf
        return surf
    m._obtener_boton_primera_partida = _obtener_boton_primera_partida

    def _obtener_sprites_tarjeta(idioma):
        if idioma == "es":
            return m.dict_sprites_tarjeta
        if idioma in m._cache_sprites_tarjeta:
            return m._cache_sprites_tarjeta[idioma]

        sp_c_n = generar_boton_con_texto("mundos/boton-cargar.png", 126, 38, t("cargar"), (26, 83, 29), 14, 0, idioma)
        sp_c_h = aclarar_boton(sp_c_n)
        sp_c_s = generar_boton_con_texto("mundos/boton-cargar-semiapretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 1, idioma)
        sp_c_a = generar_boton_con_texto("mundos/boton-cargar-apretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 2, idioma)

        sp_g_n = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, t("gestionar"), (82, 83, 83), 13, 0, idioma)
        sp_g_h = aclarar_boton(sp_g_n)
        sp_g_s = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, t("gestionar"), (82, 83, 83), 13, 1, idioma)
        sp_g_a = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, t("gestionar"), (82, 83, 83), 13, 2, idioma)

        sp_b_n = generar_boton_con_texto("Menu/salir.png", 96, 38, t("borrar"), (125, 48, 17), 14, 0, idioma)
        sp_b_h = aclarar_boton(sp_b_n)
        sp_b_s = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, t("borrar"), (125, 48, 17), 14, 1, idioma)
        sp_b_a = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, t("borrar"), (125, 48, 17), 14, 2, idioma)

        res = {
            "cargar_normal": sp_c_n,
            "cargar_hover": sp_c_h,
            "cargar_semi": sp_c_s,
            "cargar_apretado": sp_c_a,
            "gestionar_normal": sp_g_n,
            "gestionar_hover": sp_g_h,
            "gestionar_semi": sp_g_s,
            "gestionar_apretado": sp_g_a,
            "borrar_normal": sp_b_n,
            "borrar_hover": sp_b_h,
            "borrar_semi": sp_b_s,
            "borrar_apretado": sp_b_a,
        }
        m._cache_sprites_tarjeta[idioma] = res
        return res
    m._obtener_sprites_tarjeta = _obtener_sprites_tarjeta

    def _obtener_boton_menu_principal_estado(tipo, estado, idioma):
        if idioma == "es":
            if tipo == "jugar":
                if estado == "hover": return m.spr_jugar_hover
                if estado == "semi": return m.spr_jugar_semi
                if estado == "apretado": return m.spr_jugar_apretado
                return m.spr_jugar_normal
            elif tipo == "personajes":
                if estado == "hover": return m.spr_personajes_hover
                if estado == "semi": return m.spr_personajes_semi
                if estado == "apretado": return m.spr_personajes_apretado
                return m.spr_personajes_normal
            elif tipo == "opciones":
                if estado == "hover": return m.spr_opciones_hover
                if estado == "semi": return m.spr_opciones_semi
                if estado == "apretado": return m.spr_opciones_apretado
                return m.spr_opciones_normal
            elif tipo == "salir":
                if estado == "hover": return m.spr_salir_hover
                if estado == "semi": return m.spr_salir_semi
                if estado == "apretado": return m.spr_salir_apretado
                return m.spr_salir_normal

        clave = (tipo, estado, idioma)
        if clave in m._cache_botones_menu:
            return m._cache_botones_menu[clave]

        cfg_botones = {
            "jugar": ("Menu/jugar", (27, 82, 36), 26),
            "personajes": ("Menu/personajes", (42, 68, 124), 22 if idioma == "en" else 24),
            "opciones": ("Menu/opciones", (115, 67, 16), 26),
            "salir": ("Menu/salir", (127, 49, 19), 26),
        }
        base_name, col_txt, sz = cfg_botones[tipo]

        if estado == "normal":
            sprite_path = f"{base_name}.png"
            offset_y = 0
            surf = generar_boton_con_texto(sprite_path, m.ANCHO_BOTON, m.ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        elif estado == "hover":
            norm = m._obtener_boton_menu_principal_estado(tipo, "normal", idioma)
            surf = aclarar_boton(norm)
        elif estado == "semi":
            pre_name = f"{base_name}-preapretado.png"
            sprite_path = pre_name
            offset_y = 4
            surf = generar_boton_con_texto(sprite_path, m.ANCHO_BOTON, m.ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        elif estado == "apretado":
            apr_name = f"{base_name}-apretado.png"
            sprite_path = apr_name
            offset_y = 8
            surf = generar_boton_con_texto(sprite_path, m.ANCHO_BOTON, m.ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        else:
            surf = None

        m._cache_botones_menu[clave] = surf
        return surf
    m._obtener_boton_menu_principal_estado = _obtener_boton_menu_principal_estado

    def _obtener_botones_menu_principal(idioma):
        return [
            (m.btn_jugar, m._obtener_boton_menu_principal_estado("jugar", "normal", idioma), m._obtener_boton_menu_principal_estado("jugar", "hover", idioma)),
            (m.btn_personajes, m._obtener_boton_menu_principal_estado("personajes", "normal", idioma), m._obtener_boton_menu_principal_estado("personajes", "hover", idioma)),
            (m.btn_config, m._obtener_boton_menu_principal_estado("opciones", "normal", idioma), m._obtener_boton_menu_principal_estado("opciones", "hover", idioma)),
            (m.btn_salir, m._obtener_boton_menu_principal_estado("salir", "normal", idioma), m._obtener_boton_menu_principal_estado("salir", "hover", idioma)),
        ]
    m._obtener_botones_menu_principal = _obtener_botones_menu_principal

    # Instanciar el gestor del escenario interactivo y personajes autónomos del Menú Principal
    m.gestor_personajes_menu = GestorPersonajesMenu(
        ancho=m.ANCHO_MENU,
        alto=m.ALTO_MENU,
        color_p1=m.color_p1,
        accesorio_p1=m.accesorio_p1,
        color_p2=m.color_p2,
        accesorio_p2=m.accesorio_p2,
    )

    # Renderizar el primer fotograma del Menú Principal con todos los botones e interfaz completamente listos
    m.pantalla.fill((30, 30, 30))
    m.pos_mouse_inicial = pygame.mouse.get_pos()
    m.botones_menu_datos_ini = m._obtener_botones_menu_principal(obtener_idioma())
    m.gestor_personajes_menu.dibujar_menu_completo(
        m.pantalla,
        botones_menu_datos=m.botones_menu_datos_ini,
        pos_mouse=m.pos_mouse_inicial,
        spr_x=m.spr_x_normal,
        rect_x=m.rect_btn_x,
        fuente_titulo=m.fuente_pixel_titulo,
    )
    pygame.display.flip()

    # Geometría y variables para la Lista de Partidas Guardadas
    m.pagina_partidas = 0
    m.MAX_PARTIDAS_POR_PAGINA = 4
    m.rect_panel_partidas, m.btn_volver_partidas, m.btn_nueva_desde_lista, m.btn_iniciar_primera = (
        obtener_geometria_panel_partidas(m.ANCHO_MENU, m.ALTO_MENU)
    )

    m.fondo_btn_config_niveles = None
    m.fondo_btn_casa_niveles = None
    m.fondo_btn_x_niveles = None
    m.fondo_btn_x_main = None

    m.estado_actual = ESTADO_MENU_PRINCIPAL
    m.mundo_seleccionado = 1
    m.ejecutando = True
    m._ultimo_idioma_menu = obtener_idioma()

    def intentar_salir():
        pass  # (antes: nonlocal; ahora son atributos de m)
        if m.sesion_activa and hay_progreso_sin_guardar(m.niveles_desbloqueados, m.snapshot_guardado, id_partida=m.partida_actual_id):
            resp = mostrar_dialogo_guardar_salir(
                m.pantalla, m.reloj,
                niveles_desbloqueados=m.niveles_desbloqueados,
                id_partida=m.partida_actual_id,
                nombre_partida=m.partida_actual_nombre,
                password_partida=m.partida_actual_password,
                color_p1=m.color_p1,
                color_p2=m.color_p2,
                accesorio_p1=m.accesorio_p1,
                accesorio_p2=m.accesorio_p2,
            )
            if resp == "guardar_salir":
                m.snapshot_guardado = copy.deepcopy(m.niveles_desbloqueados)
                m.ejecutando = False
            elif resp == "salir_sin_guardar":
                m.ejecutando = False
            elif resp == "cancelar":
                pass
        else:
            m.ejecutando = False
    m.intentar_salir = intentar_salir

    while m.ejecutando:
        m.reloj.tick(FPS)
        reproducir_musica("menu")

        m.idm_act = obtener_idioma()
        if m.idm_act != m._ultimo_idioma_menu:
            m._cache_botones_menu.clear()
            m._cache_botones_modo.clear()
            m._cache_botones_volver.clear()
            m._cache_botones_nueva_lista.clear()
            m._cache_botones_primera.clear()
            m._cache_sprites_tarjeta.clear()
            m._ultimo_idioma_menu = m.idm_act

        # Cargar recursos bajo demanda según el estado actual antes de procesar eventos o dibujar
        if m.estado_actual == ESTADO_MODO_JUEGO:
            m._cargar_recursos_modo_juego()
        elif m.estado_actual == ESTADO_LISTA_PARTIDAS:
            m._cargar_recursos_partidas()
        elif m.estado_actual == ESTADO_PERSONAJES:
            m._cargar_recursos_volver()
        elif m.estado_actual == ESTADO_CONFIGURACION:
            m._cargar_recursos_controles()
        elif m.estado_actual == ESTADO_CREDITOS:
            m._cargar_recursos_volver()
        elif m.estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            m._cargar_recursos_niveles()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                m.intentar_salir()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # El botón X general: en Opciones regresa al menú principal; en el resto intenta salir
                if m.rect_btn_x.collidepoint(evento.pos):
                    if m.estado_actual == ESTADO_CONFIGURACION:
                        m._asegurar_semi_apretados_menu()
                        m.f_limpio = m.fondo_btn_x_main if m.fondo_btn_x_main else (30, 30, 30)
                        if animar_pulsacion_boton(m.pantalla, m.rect_btn_x, m.spr_x_semi, m.spr_x_apretado, m.f_limpio, m.spr_x_normal, tipo_sonido="ventana_cancelar"):
                            m.estado_actual = ESTADO_MENU_PRINCIPAL
                        break
                    elif m.estado_actual != ESTADO_SELECCION_NIVEL:
                        m._asegurar_semi_apretados_menu()
                        m.f_limpio = m.fondo_btn_x_main if m.fondo_btn_x_main else (30, 30, 30)
                        if animar_pulsacion_boton(m.pantalla, m.rect_btn_x, m.spr_x_semi, m.spr_x_apretado, m.f_limpio, m.spr_x_normal, tipo_sonido="ventana_cancelar"):
                            m.intentar_salir()
                        break

                if m.estado_actual == ESTADO_MENU_PRINCIPAL:
                    if _eventos_menu_principal(m, evento):
                        break

                elif m.estado_actual == ESTADO_MODO_JUEGO:
                    if _eventos_modo_juego(m, evento):
                        break

                elif m.estado_actual == ESTADO_LISTA_PARTIDAS:
                    if _eventos_lista_partidas(m, evento):
                        break

                elif m.estado_actual == ESTADO_PERSONAJES:
                    if _eventos_personajes(m, evento):
                        break

                elif m.estado_actual == ESTADO_CONFIGURACION:
                    if _eventos_configuracion(m, evento):
                        break

                elif m.estado_actual == ESTADO_CREDITOS:
                    if _eventos_creditos(m, evento):
                        break

                elif m.estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
                    if _eventos_seleccion_nivel(m, evento):
                        break

            elif evento.type == pygame.MOUSEWHEEL:
                if m.estado_actual == ESTADO_LISTA_PARTIDAS:
                    m.total_pag = max(1, (len(cargar_partidas()) + m.MAX_PARTIDAS_POR_PAGINA - 1) // m.MAX_PARTIDAS_POR_PAGINA)
                    if m.total_pag > 1:
                        if evento.y > 0 and m.pagina_partidas > 0:
                            m.pagina_partidas -= 1
                            reproducir_sonido_ui("pagina")
                        elif evento.y < 0 and m.pagina_partidas < m.total_pag - 1:
                            m.pagina_partidas += 1
                            reproducir_sonido_ui("pagina")

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if m.estado_actual == ESTADO_CONFIGURACION:
                        m.estado_actual = ESTADO_MENU_PRINCIPAL

        m.pantalla.fill((30, 30, 30))

        if m.estado_actual == ESTADO_MENU_PRINCIPAL:
            _dibujar_menu_principal(m)

        elif m.estado_actual == ESTADO_MODO_JUEGO:
            _dibujar_modo_juego(m)

        elif m.estado_actual == ESTADO_LISTA_PARTIDAS:
            _dibujar_lista_partidas(m)

        elif m.estado_actual == ESTADO_PERSONAJES:
            _dibujar_personajes(m)

        elif m.estado_actual == ESTADO_CONFIGURACION:
            _dibujar_configuracion(m)

        elif m.estado_actual == ESTADO_CREDITOS:
            _dibujar_creditos(m)

        elif m.estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            _dibujar_seleccion_nivel(m)

        if m.estado_actual != ESTADO_SELECCION_NIVEL:
            m.pos_mouse = pygame.mouse.get_pos()
            m.fondo_btn_x_main = m.pantalla.subsurface(m.rect_btn_x).copy()
            m.hov_x = m.rect_btn_x.collidepoint(m.pos_mouse)
            m.spr_x_dib = m.spr_x_hover if (m.hov_x and m.spr_x_hover) else m.spr_x_normal
            if m.spr_x_dib: m.pantalla.blit(m.spr_x_dib, m.rect_btn_x)

        pygame.display.flip()

    detener_musica()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    from errores import ejecutar_protegido
    ejecutar_protegido(main)