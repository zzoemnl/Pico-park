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
    es_nivel_jefe,
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
            if es_admin:
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
            else:
                # Partidas normales: los jefes (nivel 6) están en proceso.
                # Al completar el último nivel normal (nivel 5), se salta automáticamente el jefe
                # y se avanza directamente al siguiente mundo disponible sin bloquear al jugador.
                if n_idx < 4:
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


def main():
    import os
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    pantalla = crear_ventana()
    pygame.display.set_caption("Pico Park")
    precargar_botones_comunes()
    reloj = pygame.time.Clock()
    seleccionar_musica_menu_aleatoria()
    reproducir_musica("menu")
    fuente_pixel_titulo = obtener_fuente_titulo(TAMANO_TITULO, tamano_fallback=55)
    fuente_pixel_btn_grande = obtener_fuente_botones(TAMANO_BOTON_GRANDE, tamano_fallback=32)
    fuente_pixel_btn = obtener_fuente_botones(TAMANO_BOTON, tamano_fallback=32)
    fuente_pixel_sub_btn = obtener_fuente_botones(TAMANO_ITEM_TITULO, tamano_fallback=24)
    fuente_pixel_card_btn = obtener_fuente_botones(TAMANO_ITEM_TITULO, tamano_fallback=25)
    fuente_pixel_badge = obtener_fuente_botones(TAMANO_BADGE, tamano_fallback=28)

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_GRANDE, tamano_fallback=55)
    fuente_subtitulo = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    fuente_btn = obtener_fuente_botones(TAMANO_BOTON_GRANDE, tamano_fallback=32)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO_GRANDE)
    fuente_sub_btn = obtener_fuente_pequena(TAMANO_PEQUENA)
    fuente_contador = obtener_fuente_contador(TAMANO_CONTADOR)
    fuente_dialogos = obtener_fuente_dialogos(TAMANO_DIALOGOS)
    fuente_decorativa = obtener_fuente_decorativa(TAMANO_DECORATIVA)
    fuentes_menu = {
        "titulo": fuente_pixel_titulo,
        "tab": obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=34),
        "card": obtener_fuente_boton(TAMANO_CARD, tamano_fallback=28),
    }
    fuente_card_titulo = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    fuente_card_sub = obtener_fuente_pequena(28)

    ANCHO_MENU = pantalla.get_width()
    ALTO_MENU = pantalla.get_height()
    _init_copos_modo(ANCHO_MENU, ALTO_MENU)

    niveles_desbloqueados = crear_desbloqueados_inicial()
    partida_actual_id = None
    partida_actual_nombre = None
    partida_actual_password = None
    snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
    sesion_activa = False
    partida_cargada_flag = False
    partida_creada_flag = False

    W_BOTON_HUD, H_BOTON_HUD = 44, 52
    MARGEN_DER, MARGEN_SUP = 18, 16
    rect_btn_x = pygame.Rect(ANCHO_MENU - MARGEN_DER - W_BOTON_HUD, MARGEN_SUP, W_BOTON_HUD, H_BOTON_HUD)

    # Carga anticipada exclusiva de lo indispensable para el Menú Principal
    spr_x_normal = cargar_boton_escalado("boton-x.png", W_BOTON_HUD, H_BOTON_HUD)
    spr_x_hover = aclarar_boton(spr_x_normal)
    spr_x_semi = None
    spr_x_apretado = None

    fondo_btn_x = None

    # Botones principales con proporción nativa exacta 3.4000 (5440x1600 -> 272x80)
    ANCHO_BOTON, ALTO_BOTON, ESPACIO = 272, 80, 14
    x_centro = (ANCHO_MENU - ANCHO_BOTON) // 2
    total_h_menu = (ALTO_BOTON * 4) + (ESPACIO * 3)
    y_inicio_principal = (ALTO_MENU - total_h_menu) // 2 + 35

    spr_jugar_normal = cargar_boton_escalado("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("jugar.png", ANCHO_BOTON, ALTO_BOTON)
    spr_jugar_hover = aclarar_boton(spr_jugar_normal)
    spr_jugar_semi = cargar_boton_escalado("Menu/jugar-preapretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("jugar-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
    spr_jugar_apretado = cargar_boton_escalado("Menu/jugar-apretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("jugar-apretado.png", ANCHO_BOTON, ALTO_BOTON)

    spr_personajes_normal = cargar_boton_escalado("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("personajes.png", ANCHO_BOTON, ALTO_BOTON)
    spr_personajes_hover = aclarar_boton(spr_personajes_normal)
    spr_personajes_semi = cargar_boton_escalado("Menu/personajes-preapretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("personajes-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
    spr_personajes_apretado = cargar_boton_escalado("Menu/personajes-apretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("personajes-apretado.png", ANCHO_BOTON, ALTO_BOTON)

    spr_opciones_normal = cargar_boton_escalado("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("opciones.png", ANCHO_BOTON, ALTO_BOTON)
    spr_opciones_hover = aclarar_boton(spr_opciones_normal)
    spr_opciones_semi = cargar_boton_escalado("Menu/opciones-preapretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("opciones-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
    spr_opciones_apretado = cargar_boton_escalado("Menu/opciones-apretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("opciones-apretado.png", ANCHO_BOTON, ALTO_BOTON)

    spr_salir_normal = cargar_boton_escalado("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("salir.png", ANCHO_BOTON, ALTO_BOTON)
    spr_salir_hover = aclarar_boton(spr_salir_normal)
    spr_salir_semi = cargar_boton_escalado("Menu/salir-preapretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("salir-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
    spr_salir_apretado = cargar_boton_escalado("Menu/salir-apretado.png", ANCHO_BOTON, ALTO_BOTON) or cargar_boton_escalado("salir-apretado.png", ANCHO_BOTON, ALTO_BOTON)

    btn_jugar = pygame.Rect(x_centro, y_inicio_principal, ANCHO_BOTON, ALTO_BOTON)
    btn_personajes = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO), ANCHO_BOTON, ALTO_BOTON)
    btn_config = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON)
    btn_salir = pygame.Rect(x_centro, y_inicio_principal + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON)

    fondo_limpio_btn = pygame.Surface((ANCHO_BOTON, ALTO_BOTON))
    fondo_limpio_btn.fill((30, 30, 30))

    color_p1 = "Celeste"
    color_p2 = "Violeta"
    accesorio_p1, accesorio_p2 = _seleccionar_accesorios_sesion_aleatorios(color_p1, color_p2)
    personalizacion_modificada_en_menu = False
    tab_personajes_actual = "colores"
    items_por_pag = 6
    disp_p1_todos = [a["id"] for a in obtener_accesorios_disponibles(color_p1)]
    disp_p2_todos = [a["id"] for a in obtener_accesorios_disponibles(color_p2)]
    pagina_acc_p1 = (disp_p1_todos.index(accesorio_p1) // items_por_pag) if accesorio_p1 in disp_p1_todos else 0
    pagina_acc_p2 = (disp_p2_todos.index(accesorio_p2) // items_por_pag) if accesorio_p2 in disp_p2_todos else 0

    W_VOLVER, H_VOLVER = 238, 70
    btn_volver_personajes = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 75, W_VOLVER, H_VOLVER)
    btn_guardar = btn_volver_personajes
    btn_volver_config = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 75, W_VOLVER, H_VOLVER)
    btn_volver_creditos = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)

    seccion_opciones_actual = "configuracion"
    rect_btn_sec_cfg = pygame.Rect(70, 120, 240, 64)
    rect_btn_sec_ctrl = pygame.Rect(70, 200, 240, 64)
    rect_btn_sec_inst = pygame.Rect(70, 280, 240, 64)
    rect_btn_x_opciones = pygame.Rect(ANCHO_MENU - 62, 16, 44, 52)

    # Iconos superiores exclusivos de Selección de Niveles (Configuración, Casita y X) con proporción nativa 0.8496
    W_ICONO_NIVELES, H_ICONO_NIVELES = 44, 52
    rect_btn_x_niveles = pygame.Rect(ANCHO_MENU - MARGEN_DER - W_ICONO_NIVELES, MARGEN_SUP, W_ICONO_NIVELES, H_ICONO_NIVELES)
    rect_btn_casa_niveles = pygame.Rect(rect_btn_x_niveles.left - 12 - W_ICONO_NIVELES, MARGEN_SUP, W_ICONO_NIVELES, H_ICONO_NIVELES)
    rect_btn_config_niveles = pygame.Rect(rect_btn_casa_niveles.left - 12 - W_ICONO_NIVELES, MARGEN_SUP, W_ICONO_NIVELES, H_ICONO_NIVELES)

    # Botones interactivos para Modo de Juego (Continuar vs Nueva Partida)
    W_MODO, H_MODO = 425, 100
    x_modo = (ANCHO_MENU - W_MODO) // 2
    btn_continuar = pygame.Rect(x_modo, (ALTO_MENU // 2) - 85, W_MODO, H_MODO)
    btn_nueva_partida = pygame.Rect(x_modo, (ALTO_MENU // 2) + 35, W_MODO, H_MODO)
    btn_volver_modo = pygame.Rect((ANCHO_MENU - W_VOLVER) // 2, ALTO_MENU - 85, W_VOLVER, H_VOLVER)

    # Variables de sprites de submenús (inicialmente None, carga bajo demanda)
    spr_casa_normal = None
    spr_casa_hover = None
    spr_casa_semi = None
    spr_casa_apretado = None

    spr_confign_normal = None
    spr_confign_hover = None
    spr_confign_semi = None
    spr_confign_apretado = None

    spr_xn_normal = None
    spr_xn_hover = None
    spr_xn_semi = None
    spr_xn_apretado = None

    spr_volver_normal = None
    spr_volver_hover = None
    spr_volver_semi = None
    spr_volver_apretado = None

    spr_volver_modo_normal = None
    spr_volver_modo_hover = None
    spr_volver_modo_semi = None
    spr_volver_modo_apretado = None

    spr_menu_nav_normal = None
    spr_menu_nav_hover = None
    spr_menu_nav_semi = None
    spr_menu_nav_apretado = None

    spr_continuar_normal = None
    spr_continuar_hover = None
    spr_continuar_semi = None
    spr_continuar_apretado = None

    spr_nueva_modo_normal = None
    spr_nueva_modo_hover = None
    spr_nueva_modo_semi = None
    spr_nueva_modo_apretado = None

    spr_nueva_lista_normal = None
    spr_nueva_lista_hover = None
    spr_nueva_lista_semi = None
    spr_nueva_lista_apretado = None

    spr_volver_partidas_normal = None
    spr_volver_partidas_hover = None
    spr_volver_partidas_semi = None
    spr_volver_partidas_apretado = None

    spr_nueva_primera_normal = None
    spr_nueva_primera_hover = None
    spr_nueva_primera_semi = None
    spr_nueva_primera_apretado = None

    spr_cargar_normal = None
    spr_cargar_hover = None
    spr_cargar_semi = None
    spr_cargar_apretado = None

    dict_sprites_tarjeta = {
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

    TAM_CTRL = 54
    spr_ctrl_w = None
    spr_ctrl_a = None
    spr_ctrl_s = None
    spr_ctrl_d = None
    spr_ctrl_arr = None
    spr_ctrl_izq = None
    spr_ctrl_aba = None
    spr_ctrl_der = None

    def _asegurar_semi_apretados_menu():
        nonlocal spr_jugar_semi, spr_jugar_apretado
        nonlocal spr_personajes_semi, spr_personajes_apretado
        nonlocal spr_opciones_semi, spr_opciones_apretado
        nonlocal spr_salir_semi, spr_salir_apretado
        nonlocal spr_x_semi, spr_x_apretado
        if spr_jugar_semi is None:
            spr_jugar_semi = cargar_boton_escalado("jugar-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_jugar_apretado = cargar_boton_escalado("jugar-apretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_personajes_semi = cargar_boton_escalado("personajes-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_personajes_apretado = cargar_boton_escalado("personajes-apretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_opciones_semi = cargar_boton_escalado("opciones-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_opciones_apretado = cargar_boton_escalado("opciones-apretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_salir_semi = cargar_boton_escalado("salir-preapretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_salir_apretado = cargar_boton_escalado("salir-apretado.png", ANCHO_BOTON, ALTO_BOTON)
            spr_x_semi = cargar_boton_escalado("boton-x-semiapretado.png", W_BOTON_HUD, H_BOTON_HUD)
            spr_x_apretado = cargar_boton_escalado("boton-x-apretado.png", W_BOTON_HUD, H_BOTON_HUD)

    def _cargar_recursos_volver():
        nonlocal spr_volver_normal, spr_volver_hover, spr_volver_semi, spr_volver_apretado
        nonlocal spr_menu_nav_normal, spr_menu_nav_hover, spr_menu_nav_semi, spr_menu_nav_apretado
        if spr_volver_normal is None:
            spr_volver_normal = cargar_boton_escalado("mundos/boton-volver.png", W_VOLVER, H_VOLVER)
            spr_volver_hover = aclarar_boton(spr_volver_normal)
            spr_volver_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", W_VOLVER, H_VOLVER)
            spr_volver_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", W_VOLVER, H_VOLVER)

            spr_menu_nav_normal = cargar_boton_escalado("Ventanas/boton-menu.png", W_VOLVER, H_VOLVER)
            spr_menu_nav_hover = aclarar_boton(spr_menu_nav_normal)
            spr_menu_nav_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", W_VOLVER, H_VOLVER)
            spr_menu_nav_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", W_VOLVER, H_VOLVER)

    def _cargar_recursos_modo_juego():
        nonlocal spr_continuar_normal, spr_continuar_hover, spr_continuar_semi, spr_continuar_apretado
        nonlocal spr_nueva_modo_normal, spr_nueva_modo_hover, spr_nueva_modo_semi, spr_nueva_modo_apretado
        nonlocal spr_volver_modo_normal, spr_volver_modo_hover, spr_volver_modo_semi, spr_volver_modo_apretado
        _cargar_recursos_volver()
        if spr_continuar_normal is None:
            # Botones oficiales de la carpeta Sprites/Botones
            spr_continuar_normal = cargar_boton_escalado("Menu/boton-continuar-cargar....png", W_MODO, H_MODO) or cargar_boton_escalado("boton-continuar-cargar....png", W_MODO, H_MODO)
            spr_continuar_hover = aclarar_boton(spr_continuar_normal)
            spr_continuar_semi = cargar_boton_escalado("Menu/boton-continuar-cargar...-semiapretado.png", W_MODO, H_MODO) or cargar_boton_escalado("boton-continuar-cargar...-semiapretado.png", W_MODO, H_MODO)
            spr_continuar_apretado = cargar_boton_escalado("Menu/boton-continuar-cargar...-apretado.png", W_MODO, H_MODO) or cargar_boton_escalado("boton-continuar-cargar...-apretado.png", W_MODO, H_MODO)

            spr_nueva_modo_normal = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", W_MODO, H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar....png", W_MODO, H_MODO)
            spr_nueva_modo_hover = aclarar_boton(spr_nueva_modo_normal)
            spr_nueva_modo_semi = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar...-semiapretado.png", W_MODO, H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar...-semiapretado.png", W_MODO, H_MODO)
            spr_nueva_modo_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar...-apretado.png", W_MODO, H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar...-apretado.png", W_MODO, H_MODO)

            spr_volver_modo_normal = cargar_boton_escalado("mundos/boton-volver.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-volver.png", W_VOLVER, H_VOLVER)
            spr_volver_modo_hover = aclarar_boton(spr_volver_modo_normal)
            spr_volver_modo_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-volver-semiapretado.png", W_VOLVER, H_VOLVER)
            spr_volver_modo_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-volver-apretado.png", W_VOLVER, H_VOLVER)

    def _cargar_recursos_partidas():
        nonlocal spr_nueva_lista_normal, spr_nueva_lista_hover, spr_nueva_lista_semi, spr_nueva_lista_apretado
        nonlocal spr_volver_partidas_normal, spr_volver_partidas_hover, spr_volver_partidas_semi, spr_volver_partidas_apretado
        nonlocal spr_nueva_primera_normal, spr_nueva_primera_hover, spr_nueva_primera_semi, spr_nueva_primera_apretado
        nonlocal spr_cargar_normal, spr_cargar_hover, spr_cargar_semi, spr_cargar_apretado
        _cargar_recursos_volver()
        if spr_nueva_lista_normal is None:
            # Botones oficiales para la lista de partidas guardadas
            spr_nueva_lista_normal = cargar_boton_escalado("mundos/boton-nueva-partida.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-nueva-partida.png", W_VOLVER, H_VOLVER)
            spr_nueva_lista_hover = aclarar_boton(spr_nueva_lista_normal)
            spr_nueva_lista_semi = cargar_boton_escalado("mundos/boton-nueva-partida-semiapretado.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-nueva-partida-semiapretado.png", W_VOLVER, H_VOLVER)
            spr_nueva_lista_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-apretado.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-nueva-partida-apretado.png", W_VOLVER, H_VOLVER)

            spr_volver_partidas_normal = cargar_boton_escalado("mundos/boton-volver.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-volver.png", W_VOLVER, H_VOLVER)
            spr_volver_partidas_hover = aclarar_boton(spr_volver_partidas_normal)
            spr_volver_partidas_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-volver-semiapretado.png", W_VOLVER, H_VOLVER)
            spr_volver_partidas_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", W_VOLVER, H_VOLVER) or cargar_boton_escalado("boton-volver-apretado.png", W_VOLVER, H_VOLVER)

            spr_nueva_primera_normal = cargar_boton_escalado("mundos/boton-nueva-partida.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida.png", 272, 80)
            spr_nueva_primera_hover = aclarar_boton(spr_nueva_primera_normal)
            spr_nueva_primera_semi = cargar_boton_escalado("mundos/boton-nueva-partida-semiapretado.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida-semiapretado.png", 272, 80)
            spr_nueva_primera_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-apretado.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida-apretado.png", 272, 80)

            # Botón oficial CARGAR en tarjetas de partida
            spr_cargar_normal = cargar_boton_escalado("mundos/boton-cargar.png", 126, 38) or cargar_boton_escalado("boton-cargar.png", 126, 38)
            spr_cargar_hover = aclarar_boton(spr_cargar_normal)
            spr_cargar_semi = cargar_boton_escalado("mundos/boton-cargar-semiapretado.png", 126, 38) or cargar_boton_escalado("boton-cargar-semiapretado.png", 126, 38)
            spr_cargar_apretado = cargar_boton_escalado("mundos/boton-cargar-apretado.png", 126, 38) or cargar_boton_escalado("boton-cargar-apretado.png", 126, 38)

            # Botones temáticos GESTIONAR y BORRAR basados en los marcos oficiales de Sprites/Botones
            spr_gest_normal = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 0)
            spr_gest_hover = aclarar_boton(spr_gest_normal)
            spr_gest_semi = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 1)
            spr_gest_apretado = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 2)

            spr_borrar_normal = generar_boton_con_texto("Menu/salir.png", 96, 38, "BORRAR", (125, 48, 17), 14, 0)
            spr_borrar_hover = aclarar_boton(spr_borrar_normal)
            spr_borrar_semi = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, "BORRAR", (125, 48, 17), 14, 1)
            spr_borrar_apretado = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, "BORRAR", (125, 48, 17), 14, 2)

            dict_sprites_tarjeta["cargar_normal"] = spr_cargar_normal
            dict_sprites_tarjeta["cargar_hover"] = spr_cargar_hover
            dict_sprites_tarjeta["cargar_semi"] = spr_cargar_semi
            dict_sprites_tarjeta["cargar_apretado"] = spr_cargar_apretado

            dict_sprites_tarjeta["gestionar_normal"] = spr_gest_normal
            dict_sprites_tarjeta["gestionar_hover"] = spr_gest_hover
            dict_sprites_tarjeta["gestionar_semi"] = spr_gest_semi
            dict_sprites_tarjeta["gestionar_apretado"] = spr_gest_apretado

            dict_sprites_tarjeta["borrar_normal"] = spr_borrar_normal
            dict_sprites_tarjeta["borrar_hover"] = spr_borrar_hover
            dict_sprites_tarjeta["borrar_semi"] = spr_borrar_semi
            dict_sprites_tarjeta["borrar_apretado"] = spr_borrar_apretado

    def _cargar_recursos_niveles():
        nonlocal spr_casa_normal, spr_casa_hover, spr_casa_semi, spr_casa_apretado
        nonlocal spr_confign_normal, spr_confign_hover, spr_confign_semi, spr_confign_apretado
        nonlocal spr_xn_normal, spr_xn_hover, spr_xn_semi, spr_xn_apretado
        if spr_casa_normal is None:
            spr_casa_normal = cargar_boton_escalado("HUD/boton-casa.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa.png", W_ICONO_NIVELES, H_ICONO_NIVELES)
            spr_casa_hover = aclarar_boton(spr_casa_normal)
            spr_casa_semi = cargar_boton_escalado("HUD/boton-casa-semiapretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa-semiapretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES)
            spr_casa_apretado = cargar_boton_escalado("HUD/boton-casa-apretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa-apretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES)

            spr_confign_normal = cargar_boton_escalado("HUD/boton-configuracion.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion.png", W_ICONO_NIVELES, H_ICONO_NIVELES)
            spr_confign_hover = aclarar_boton(spr_confign_normal)
            spr_confign_semi = cargar_boton_escalado("HUD/boton-configuracion-semiapretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion-semiapretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES)
            spr_confign_apretado = cargar_boton_escalado("HUD/boton-configuracion-apretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion-apretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES)

            spr_xn_normal = cargar_boton_escalado("HUD/boton-x.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-x.png", W_ICONO_NIVELES, H_ICONO_NIVELES)
            spr_xn_hover = aclarar_boton(spr_xn_normal)
            spr_xn_semi = cargar_boton_escalado("HUD/boton-x-semiapretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-x-semiapretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES)
            spr_xn_apretado = cargar_boton_escalado("HUD/boton-x-apretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES) or cargar_boton_escalado("boton-x-apretado.png", W_ICONO_NIVELES, H_ICONO_NIVELES)

    def _cargar_recursos_controles():
        nonlocal spr_ctrl_w, spr_ctrl_a, spr_ctrl_s, spr_ctrl_d
        nonlocal spr_ctrl_arr, spr_ctrl_izq, spr_ctrl_aba, spr_ctrl_der
        _cargar_recursos_volver()
        if spr_ctrl_w is None:
            spr_ctrl_w = cargar_boton_escalado("Controles/boton-w.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_a = cargar_boton_escalado("Controles/boton-a.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_s = cargar_boton_escalado("Controles/boton-s.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_d = cargar_boton_escalado("Controles/boton-d.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_arr = cargar_boton_escalado("Controles/boton-arriba.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_izq = cargar_boton_escalado("Controles/boton-izquierda.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_aba = cargar_boton_escalado("Controles/boton-abajo.png", TAM_CTRL, TAM_CTRL)
            spr_ctrl_der = cargar_boton_escalado("Controles/boton-derecha.png", TAM_CTRL, TAM_CTRL)

    # Cargar y preparar de forma anticipada todos los recursos de botones para todas las pantallas
    _asegurar_semi_apretados_menu()
    _cargar_recursos_volver()
    _cargar_recursos_modo_juego()
    _cargar_recursos_partidas()
    _cargar_recursos_niveles()
    _cargar_recursos_controles()

    # Funciones de soporte dinámico multiidioma para botones
    _cache_botones_modo = {}
    _cache_botones_volver = {}
    _cache_botones_nueva_lista = {}
    _cache_botones_primera = {}
    _cache_sprites_tarjeta = {}
    _cache_botones_menu = {}

    def _obtener_boton_modo(tipo, estado, idioma):
        tipo_norm = "nueva" if tipo in ("nueva", "nueva_partida") else tipo
        if idioma == "es":
            if tipo_norm == "continuar":
                if estado == "hover": return spr_continuar_hover
                if estado == "semi": return spr_continuar_semi
                if estado == "apretado": return spr_continuar_apretado
                return spr_continuar_normal
            else:
                if estado == "hover": return spr_nueva_modo_hover
                if estado == "semi": return spr_nueva_modo_semi
                if estado == "apretado": return spr_nueva_modo_apretado
                return spr_nueva_modo_normal

        clave = (tipo_norm, estado, idioma)
        if clave in _cache_botones_modo:
            return _cache_botones_modo[clave]

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

        w, h = W_MODO, H_MODO
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

        _cache_botones_modo[clave] = surf
        return surf

    def _obtener_boton_volver(estado, idioma, w=W_VOLVER, h=H_VOLVER):
        if idioma == "es":
            if w == W_VOLVER and h == H_VOLVER:
                if estado == "hover": return spr_volver_modo_hover
                if estado == "semi": return spr_volver_modo_semi
                if estado == "apretado": return spr_volver_modo_apretado
                return spr_volver_modo_normal
            base_p = "mundos/boton-volver.png"
            if estado == "semi": base_p = "mundos/boton-volver-semiapretado.png"
            elif estado == "apretado": base_p = "mundos/boton-volver-apretado.png"
            btn = cargar_boton_escalado(base_p, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
            if estado == "hover":
                btn = aclarar_boton(btn)
            return btn

        clave = (estado, idioma, w, h)
        if clave in _cache_botones_volver:
            return _cache_botones_volver[clave]

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

        _cache_botones_volver[clave] = surf
        return surf

    def _obtener_boton_nueva_lista(estado, idioma):
        if idioma == "es":
            if estado == "hover": return spr_nueva_lista_hover
            if estado == "semi": return spr_nueva_lista_semi
            if estado == "apretado": return spr_nueva_lista_apretado
            return spr_nueva_lista_normal

        clave = (estado, idioma)
        if clave in _cache_botones_nueva_lista:
            return _cache_botones_nueva_lista[clave]

        base_path = "mundos/boton-nueva-partida.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-nueva-partida-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-nueva-partida-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, W_VOLVER, H_VOLVER) or cargar_boton_escalado("mundos/boton-nueva-partida.png", W_VOLVER, H_VOLVER)
        surf = btn_base.copy()

        col_interior = (255, 159, 99) if estado not in ("semi", "apretado") else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        shift_y = 7 if estado == 'apretado' else (3 if estado == 'semi' else 0)
        pad_top = 5 + shift_y
        h_face = 44
        rect_interior = pygame.Rect(6, pad_top, W_VOLVER - 12, h_face)
        pygame.draw.rect(surf, col_interior, rect_interior)

        txt_nl = t("nueva_partida")
        if idioma == "zh":
            f_nl = obtener_fuente_cjk(20, negrita=True)
            t_nl = f_nl.render(txt_nl, True, (115, 35, 20))
        else:
            _, t_nl = renderizar_texto_pixamuse(txt_nl, max(10, int(round(H_VOLVER * 0.28))), (115, 35, 20), max_w=W_VOLVER - 20)

        cy_nl = round(H_VOLVER * 0.42) + shift_y
        bbox_nl = t_nl.get_bounding_rect()
        if bbox_nl.width > 0 and bbox_nl.height > 0:
            surf.blit(t_nl, (round(W_VOLVER / 2.0 - (bbox_nl.left + bbox_nl.width / 2.0)), round(cy_nl - (bbox_nl.top + bbox_nl.height / 2.0))))
        else:
            surf.blit(t_nl, t_nl.get_rect(center=(W_VOLVER // 2, cy_nl)))

        if estado == "hover":
            surf = aclarar_boton(surf)

        _cache_botones_nueva_lista[clave] = surf
        return surf

    def _obtener_boton_primera_partida(estado, idioma):
        if idioma == "es":
            if estado == "hover": return spr_nueva_primera_hover
            if estado == "semi": return spr_nueva_primera_semi
            if estado == "apretado": return spr_nueva_primera_apretado
            return spr_nueva_primera_normal

        clave = (estado, idioma)
        if clave in _cache_botones_primera:
            return _cache_botones_primera[clave]

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

        _cache_botones_primera[clave] = surf
        return surf

    def _obtener_sprites_tarjeta(idioma):
        if idioma == "es":
            return dict_sprites_tarjeta
        if idioma in _cache_sprites_tarjeta:
            return _cache_sprites_tarjeta[idioma]

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
        _cache_sprites_tarjeta[idioma] = res
        return res

    def _obtener_boton_menu_principal_estado(tipo, estado, idioma):
        if idioma == "es":
            if tipo == "jugar":
                if estado == "hover": return spr_jugar_hover
                if estado == "semi": return spr_jugar_semi
                if estado == "apretado": return spr_jugar_apretado
                return spr_jugar_normal
            elif tipo == "personajes":
                if estado == "hover": return spr_personajes_hover
                if estado == "semi": return spr_personajes_semi
                if estado == "apretado": return spr_personajes_apretado
                return spr_personajes_normal
            elif tipo == "opciones":
                if estado == "hover": return spr_opciones_hover
                if estado == "semi": return spr_opciones_semi
                if estado == "apretado": return spr_opciones_apretado
                return spr_opciones_normal
            elif tipo == "salir":
                if estado == "hover": return spr_salir_hover
                if estado == "semi": return spr_salir_semi
                if estado == "apretado": return spr_salir_apretado
                return spr_salir_normal

        clave = (tipo, estado, idioma)
        if clave in _cache_botones_menu:
            return _cache_botones_menu[clave]

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
            surf = generar_boton_con_texto(sprite_path, ANCHO_BOTON, ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        elif estado == "hover":
            norm = _obtener_boton_menu_principal_estado(tipo, "normal", idioma)
            surf = aclarar_boton(norm)
        elif estado == "semi":
            pre_name = f"{base_name}-preapretado.png"
            sprite_path = pre_name
            offset_y = 4
            surf = generar_boton_con_texto(sprite_path, ANCHO_BOTON, ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        elif estado == "apretado":
            apr_name = f"{base_name}-apretado.png"
            sprite_path = apr_name
            offset_y = 8
            surf = generar_boton_con_texto(sprite_path, ANCHO_BOTON, ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        else:
            surf = None

        _cache_botones_menu[clave] = surf
        return surf

    def _obtener_botones_menu_principal(idioma):
        return [
            (btn_jugar, _obtener_boton_menu_principal_estado("jugar", "normal", idioma), _obtener_boton_menu_principal_estado("jugar", "hover", idioma)),
            (btn_personajes, _obtener_boton_menu_principal_estado("personajes", "normal", idioma), _obtener_boton_menu_principal_estado("personajes", "hover", idioma)),
            (btn_config, _obtener_boton_menu_principal_estado("opciones", "normal", idioma), _obtener_boton_menu_principal_estado("opciones", "hover", idioma)),
            (btn_salir, _obtener_boton_menu_principal_estado("salir", "normal", idioma), _obtener_boton_menu_principal_estado("salir", "hover", idioma)),
        ]

    # Instanciar el gestor del escenario interactivo y personajes autónomos del Menú Principal
    gestor_personajes_menu = GestorPersonajesMenu(
        ancho=ANCHO_MENU,
        alto=ALTO_MENU,
        color_p1=color_p1,
        accesorio_p1=accesorio_p1,
        color_p2=color_p2,
        accesorio_p2=accesorio_p2,
    )

    # Renderizar el primer fotograma del Menú Principal con todos los botones e interfaz completamente listos
    pantalla.fill((30, 30, 30))
    pos_mouse_inicial = pygame.mouse.get_pos()
    botones_menu_datos_ini = _obtener_botones_menu_principal(obtener_idioma())
    gestor_personajes_menu.dibujar_menu_completo(
        pantalla,
        botones_menu_datos=botones_menu_datos_ini,
        pos_mouse=pos_mouse_inicial,
        spr_x=spr_x_normal,
        rect_x=rect_btn_x,
        fuente_titulo=fuente_pixel_titulo,
    )
    pygame.display.flip()

    # Geometría y variables para la Lista de Partidas Guardadas
    pagina_partidas = 0
    MAX_PARTIDAS_POR_PAGINA = 4
    rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
        obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU)
    )

    fondo_btn_config_niveles = None
    fondo_btn_casa_niveles = None
    fondo_btn_x_niveles = None
    fondo_btn_x_main = None

    estado_actual = ESTADO_MENU_PRINCIPAL
    mundo_seleccionado = 1
    ejecutando = True
    _ultimo_idioma_menu = obtener_idioma()

    def intentar_salir():
        nonlocal ejecutando, snapshot_guardado
        if sesion_activa and hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado, id_partida=partida_actual_id):
            resp = mostrar_dialogo_guardar_salir(
                pantalla, reloj,
                niveles_desbloqueados=niveles_desbloqueados,
                id_partida=partida_actual_id,
                nombre_partida=partida_actual_nombre,
                password_partida=partida_actual_password,
                color_p1=color_p1,
                color_p2=color_p2,
                accesorio_p1=accesorio_p1,
                accesorio_p2=accesorio_p2,
            )
            if resp == "guardar_salir":
                snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
                ejecutando = False
            elif resp == "salir_sin_guardar":
                ejecutando = False
            elif resp == "cancelar":
                pass
        else:
            ejecutando = False

    while ejecutando:
        reloj.tick(FPS)
        reproducir_musica("menu")

        idm_act = obtener_idioma()
        if idm_act != _ultimo_idioma_menu:
            _cache_botones_menu.clear()
            _cache_botones_modo.clear()
            _cache_botones_volver.clear()
            _cache_botones_nueva_lista.clear()
            _cache_botones_primera.clear()
            _cache_sprites_tarjeta.clear()
            _ultimo_idioma_menu = idm_act

        # Cargar recursos bajo demanda según el estado actual antes de procesar eventos o dibujar
        if estado_actual == ESTADO_MODO_JUEGO:
            _cargar_recursos_modo_juego()
        elif estado_actual == ESTADO_LISTA_PARTIDAS:
            _cargar_recursos_partidas()
        elif estado_actual == ESTADO_PERSONAJES:
            _cargar_recursos_volver()
        elif estado_actual == ESTADO_CONFIGURACION:
            _cargar_recursos_controles()
        elif estado_actual == ESTADO_CREDITOS:
            _cargar_recursos_volver()
        elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            _cargar_recursos_niveles()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                intentar_salir()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # El botón X general: en Opciones regresa al menú principal; en el resto intenta salir
                if rect_btn_x.collidepoint(evento.pos):
                    if estado_actual == ESTADO_CONFIGURACION:
                        _asegurar_semi_apretados_menu()
                        f_limpio = fondo_btn_x_main if fondo_btn_x_main else (30, 30, 30)
                        if animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, f_limpio, spr_x_normal, tipo_sonido="ventana_cancelar"):
                            estado_actual = ESTADO_MENU_PRINCIPAL
                        break
                    elif estado_actual != ESTADO_SELECCION_NIVEL:
                        _asegurar_semi_apretados_menu()
                        f_limpio = fondo_btn_x_main if fondo_btn_x_main else (30, 30, 30)
                        if animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado, f_limpio, spr_x_normal, tipo_sonido="ventana_cancelar"):
                            intentar_salir()
                        break

                if estado_actual == ESTADO_MENU_PRINCIPAL:
                    _asegurar_semi_apretados_menu()
                    idm_act = obtener_idioma()
                    if btn_jugar.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_jugar)
                        sp_s = _obtener_boton_menu_principal_estado("jugar", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("jugar", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("jugar", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_jugar, sp_s, sp_a, f_limp, sp_n, tipo_sonido="menu"):
                            estado_actual = ESTADO_MODO_JUEGO
                    elif btn_personajes.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_personajes)
                        sp_s = _obtener_boton_menu_principal_estado("personajes", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("personajes", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("personajes", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_personajes, sp_s, sp_a, f_limp, sp_n, tipo_sonido="menu"):
                            estado_actual = ESTADO_PERSONAJES
                            acc_list_init = obtener_accesorios_disponibles()
                            for _ia, _acc in enumerate(acc_list_init):
                                if _acc["id"] == accesorio_p1:
                                    pagina_acc_p1 = _ia // 6
                                if _acc["id"] == accesorio_p2:
                                    pagina_acc_p2 = _ia // 6
                    elif btn_config.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_config)
                        sp_s = _obtener_boton_menu_principal_estado("opciones", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("opciones", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("opciones", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_config, sp_s, sp_a, f_limp, sp_n, tipo_sonido="menu"):
                            estado_actual = ESTADO_CONFIGURACION
                            seccion_opciones_actual = "configuracion"
                            break
                    elif btn_salir.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_salir)
                        sp_s = _obtener_boton_menu_principal_estado("salir", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("salir", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("salir", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_salir, sp_s, sp_a, f_limp, sp_n, tipo_sonido="menu"):
                            intentar_salir()

                elif estado_actual == ESTADO_MODO_JUEGO:
                    f_limp_modo = _obtener_fondo_modo_juego(ANCHO_MENU, ALTO_MENU)
                    idm_act = obtener_idioma()
                    if btn_continuar.collidepoint(evento.pos):
                        sp_c_s = _obtener_boton_modo("continuar", "semi", idm_act)
                        sp_c_a = _obtener_boton_modo("continuar", "apretado", idm_act)
                        sp_c_n = _obtener_boton_modo("continuar", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_continuar, sp_c_s, sp_c_a, f_limp_modo, sp_c_n, tipo_sonido="menu"):
                            pagina_partidas = 0
                            estado_actual = ESTADO_LISTA_PARTIDAS
                    elif btn_nueva_partida.collidepoint(evento.pos):
                        sp_n_s = _obtener_boton_modo("nueva_partida", "semi", idm_act)
                        sp_n_a = _obtener_boton_modo("nueva_partida", "apretado", idm_act)
                        sp_n_n = _obtener_boton_modo("nueva_partida", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_nueva_partida, sp_n_s, sp_n_a, f_limp_modo, sp_n_n, tipo_sonido="partida_nueva"):
                            nueva_p = flujo_crear_nueva_partida(
                                pantalla, reloj,
                                color_p1=color_p1, color_p2=color_p2,
                                accesorio_p1=accesorio_p1, accesorio_p2=accesorio_p2,
                            )
                            if nueva_p is not None:
                                personalizacion_modificada_en_menu = False
                                niveles_desbloqueados = copy.deepcopy(nueva_p["niveles_desbloqueados"])
                                snapshot_guardado = copy.deepcopy(nueva_p["niveles_desbloqueados"])
                                partida_actual_id = nueva_p["id"]
                                partida_actual_nombre = nueva_p["nombre"]
                                partida_actual_password = nueva_p.get("password_plain", "")
                                partida_creada_flag = True
                                sesion_activa = True
                                mundo_seleccionado = 1
                                fin_acc, mundo_seleccionado = jugar_niveles_desde(
                                    1, 0,
                                    color_p1, color_p2,
                                    niveles_desbloqueados,
                                    partida_actual_id,
                                    partida_actual_nombre,
                                    snapshot_guardado,
                                    accesorio_p1=accesorio_p1,
                                    accesorio_p2=accesorio_p2,
                                    partida_actual_password=partida_actual_password,
                                    )
                                if fin_acc == "menu":
                                    estado_actual = ESTADO_SELECCION_NIVEL
                                    seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                                    reproducir_musica("menu", forzar=True)
                                else:
                                    ejecutando = False
                    elif btn_volver_modo.collidepoint(evento.pos):
                        sp_v_s = _obtener_boton_volver("semi", idm_act)
                        sp_v_a = _obtener_boton_volver("apretado", idm_act)
                        sp_v_n = _obtener_boton_volver("normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_volver_modo, sp_v_s, sp_v_a, f_limp_modo, sp_v_n, tipo_sonido="ventana_volver"):
                            estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual == ESTADO_LISTA_PARTIDAS:
                    partidas_guardadas = cargar_partidas()
                    rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
                        obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas_guardadas))
                    )
                    total_p = len(partidas_guardadas)
                    total_paginas = max(1, (total_p + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                    if pagina_partidas >= total_paginas:
                        pagina_partidas = max(0, total_paginas - 1)

                    idm_act = obtener_idioma()
                    dict_sp_act = _obtener_sprites_tarjeta(idm_act)

                    if not partidas_guardadas:
                        if btn_iniciar_primera.collidepoint(evento.pos):
                            pulsado = True
                            sp_pr_semi = _obtener_boton_primera_partida("semi", idm_act)
                            sp_pr_apret = _obtener_boton_primera_partida("apretado", idm_act)
                            sp_pr_norm = _obtener_boton_primera_partida("normal", idm_act)
                            if sp_pr_semi and sp_pr_apret:
                                pulsado = animar_pulsacion_boton(pantalla, btn_iniciar_primera, sp_pr_semi, sp_pr_apret, (252, 248, 238), sp_pr_norm, tipo_sonido="partida_nueva")
                            if pulsado:
                                nueva_p = flujo_crear_nueva_partida(
                                    pantalla, reloj,
                                    color_p1=color_p1, color_p2=color_p2,
                                    accesorio_p1=accesorio_p1, accesorio_p2=accesorio_p2,
                                )
                                if nueva_p is not None:
                                    personalizacion_modificada_en_menu = False
                                    niveles_desbloqueados = copy.deepcopy(nueva_p["niveles_desbloqueados"])
                                    snapshot_guardado = copy.deepcopy(nueva_p["niveles_desbloqueados"])
                                    partida_actual_id = nueva_p["id"]
                                    partida_actual_nombre = nueva_p["nombre"]
                                    partida_actual_password = nueva_p.get("password_plain", "")
                                    partida_creada_flag = True
                                    sesion_activa = True
                                    mundo_seleccionado = 1
                                    fin_acc, mundo_seleccionado = jugar_niveles_desde(
                                        1, 0,
                                        color_p1, color_p2,
                                        niveles_desbloqueados,
                                        partida_actual_id,
                                        partida_actual_nombre,
                                        snapshot_guardado,
                                        accesorio_p1=accesorio_p1,
                                        accesorio_p2=accesorio_p2,
                                        partida_actual_password=partida_actual_password,
                                    )
                                    if fin_acc == "menu":
                                        estado_actual = ESTADO_SELECCION_NIVEL
                                        seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                                        reproducir_musica("menu", forzar=True)
                                    else:
                                        ejecutando = False
                    else:
                        inicio_idx = pagina_partidas * MAX_PARTIDAS_POR_PAGINA
                        fin_idx = inicio_idx + MAX_PARTIDAS_POR_PAGINA
                        partidas_pagina = partidas_guardadas[inicio_idx:fin_idx]

                        accion_ejecutada = False
                        for idx_slot, p in enumerate(partidas_pagina):
                            r_card, _, r_btn_cargar, r_btn_gestionar, r_btn_borrar, _ = obtener_geometria_tarjeta_partida(
                                rect_panel_partidas, idx_slot
                            )
                            # Clic en botón BORRAR (dispara confirmación previa con advertencia)
                            if r_btn_borrar.collidepoint(evento.pos):
                                pulsado = True
                                spr_b_s = dict_sp_act.get("borrar_semi")
                                spr_b_a = dict_sp_act.get("borrar_apretado")
                                spr_b_n = dict_sp_act.get("borrar_normal")
                                if spr_b_s and spr_b_a:
                                    pulsado = animar_pulsacion_boton(pantalla, r_btn_borrar, spr_b_s, spr_b_a, (253, 246, 233), spr_b_n, tipo_sonido="partida_borrar")
                                if pulsado:
                                    if mostrar_dialogo_confirmar_borrado(pantalla, reloj, p):
                                        eliminar_partida(p["id"])
                                        if partida_actual_id == p["id"]:
                                            partida_actual_id = None
                                            partida_actual_nombre = None
                                            partida_actual_password = None
                                            niveles_desbloqueados = crear_desbloqueados_inicial()
                                            snapshot_guardado = copy.deepcopy(niveles_desbloqueados)
                                            sesion_activa = False
                                            partida_cargada_flag = False
                                            partida_creada_flag = False
                                        nuevas_p = cargar_partidas()
                                        nuevas_total_pag = max(1, (len(nuevas_p) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                                        if pagina_partidas >= nuevas_total_pag:
                                            pagina_partidas = max(0, nuevas_total_pag - 1)
                                accion_ejecutada = True
                                break

                            # Clic en botón GESTIONAR (renombrar, cambiar/quitar clave, borrar)
                            elif r_btn_gestionar.collidepoint(evento.pos):
                                pulsado = True
                                spr_g_s = dict_sp_act.get("gestionar_semi")
                                spr_g_a = dict_sp_act.get("gestionar_apretado")
                                spr_g_n = dict_sp_act.get("gestionar_normal")
                                if spr_g_s and spr_g_a:
                                    pulsado = animar_pulsacion_boton(pantalla, r_btn_gestionar, spr_g_s, spr_g_a, (253, 246, 233), spr_g_n, tipo_sonido="partida_gestionar")
                                if pulsado:
                                    if modal_administrar_perfil(pantalla, reloj, p):
                                        nuevas_p = cargar_partidas()
                                        nuevas_total_pag = max(1, (len(nuevas_p) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                                        if pagina_partidas >= nuevas_total_pag:
                                            pagina_partidas = max(0, nuevas_total_pag - 1)
                                accion_ejecutada = True
                                break

                            # Clic en botón CARGAR (única y exclusivamente sobre r_btn_cargar)
                            elif r_btn_cargar.collidepoint(evento.pos):
                                pulsado = True
                                spr_c_s = dict_sp_act.get("cargar_semi")
                                spr_c_a = dict_sp_act.get("cargar_apretado")
                                spr_c_n = dict_sp_act.get("cargar_normal")
                                if spr_c_s and spr_c_a:
                                    pulsado = animar_pulsacion_boton(pantalla, r_btn_cargar, spr_c_s, spr_c_a, (253, 246, 233), spr_c_n, tipo_sonido="partida_cargar")
                                if pulsado:
                                    if p.get("tiene_password", False):
                                        if not pedir_password_modal(pantalla, reloj, p):
                                            pygame.event.clear()
                                            accion_ejecutada = True
                                            break
                                        pygame.event.clear()

                                    atuendo_guardado = (
                                        p.get("color_p1", "Celeste"),
                                        p.get("color_p2", "Violeta"),
                                        p.get("accesorio_p1", "Ninguno"),
                                        p.get("accesorio_p2", "Ninguno"),
                                    )
                                    atuendo_actual = (color_p1, color_p2, accesorio_p1, accesorio_p2)
                                    hay_cambios_pendientes = personalizacion_modificada_en_menu and (atuendo_actual != atuendo_guardado)

                                    if hay_cambios_pendientes:
                                        decision = mostrar_dialogo_confirmar_atuendos(
                                            pantalla, reloj, p,
                                            color_p1_nuevo=color_p1,
                                            color_p2_nuevo=color_p2,
                                            acc_p1_nuevo=accesorio_p1,
                                            acc_p2_nuevo=accesorio_p2,
                                        )
                                        if decision == "cancelar":
                                            pygame.event.clear()
                                            accion_ejecutada = True
                                            break
                                        elif decision == "mantener":
                                            color_p1, color_p2, accesorio_p1, accesorio_p2 = atuendo_guardado
                                            personalizacion_modificada_en_menu = False
                                        elif decision == "cambiar":
                                            p_actualizada = guardar_partida(
                                                niveles_desbloqueados=p["niveles_desbloqueados"],
                                                id_partida=p["id"],
                                                nombre_partida=p["nombre"],
                                                password_hash=p.get("password_hash"),
                                                password_salt=p.get("password_salt"),
                                                color_p1=color_p1,
                                                color_p2=color_p2,
                                                accesorio_p1=accesorio_p1,
                                                accesorio_p2=accesorio_p2,
                                            )
                                            if p_actualizada:
                                                p["color_p1"] = color_p1
                                                p["color_p2"] = color_p2
                                                p["accesorio_p1"] = accesorio_p1
                                                p["accesorio_p2"] = accesorio_p2
                                            personalizacion_modificada_en_menu = False
                                    else:
                                        color_p1, color_p2, accesorio_p1, accesorio_p2 = atuendo_guardado
                                        personalizacion_modificada_en_menu = False

                                    niveles_desbloqueados = copy.deepcopy(p["niveles_desbloqueados"])
                                    snapshot_guardado = copy.deepcopy(p["niveles_desbloqueados"])
                                    partida_actual_id = p["id"]
                                    partida_actual_nombre = p["nombre"]
                                    partida_actual_password = None
                                    partida_cargada_flag = True
                                    sesion_activa = True
                                    mundo_seleccionado = p["mundo_max"]
                                    estado_actual = ESTADO_SELECCION_NIVEL
                                    accion_ejecutada = True
                                    break

                        if not accion_ejecutada:
                            if total_paginas > 1:
                                btn_pag_ant = pygame.Rect(rect_panel_partidas.centerx - 120, 508, 36, 32)
                                btn_pag_sig = pygame.Rect(rect_panel_partidas.centerx + 84, 508, 36, 32)
                                if btn_pag_ant.collidepoint(evento.pos) and pagina_partidas > 0:
                                    pagina_partidas -= 1
                                    reproducir_sonido_ui("pagina")
                                elif btn_pag_sig.collidepoint(evento.pos) and pagina_partidas < total_paginas - 1:
                                    pagina_partidas += 1
                                    reproducir_sonido_ui("pagina")

                            if btn_nueva_desde_lista.collidepoint(evento.pos):
                                pulsado = True
                                sp_nl_s = _obtener_boton_nueva_lista("semi", idm_act)
                                sp_nl_a = _obtener_boton_nueva_lista("apretado", idm_act)
                                sp_nl_n = _obtener_boton_nueva_lista("normal", idm_act)
                                if sp_nl_s and sp_nl_a:
                                    f_limp = _obtener_fondo_partidas(ANCHO_MENU, ALTO_MENU)
                                    pulsado = animar_pulsacion_boton(pantalla, btn_nueva_desde_lista, sp_nl_s, sp_nl_a, f_limp, sp_nl_n, tipo_sonido="partida_nueva")
                                if pulsado:
                                    nueva_p = flujo_crear_nueva_partida(
                                        pantalla, reloj,
                                        color_p1=color_p1, color_p2=color_p2,
                                        accesorio_p1=accesorio_p1, accesorio_p2=accesorio_p2,
                                    )
                                    if nueva_p is not None:
                                        personalizacion_modificada_en_menu = False
                                        niveles_desbloqueados = copy.deepcopy(nueva_p["niveles_desbloqueados"])
                                        snapshot_guardado = copy.deepcopy(nueva_p["niveles_desbloqueados"])
                                        partida_actual_id = nueva_p["id"]
                                        partida_actual_nombre = nueva_p["nombre"]
                                        partida_actual_password = nueva_p.get("password_plain", "")
                                        partida_creada_flag = True
                                        sesion_activa = True
                                        mundo_seleccionado = 1
                                        fin_acc, mundo_seleccionado = jugar_niveles_desde(
                                            1, 0,
                                            color_p1, color_p2,
                                            niveles_desbloqueados,
                                            partida_actual_id,
                                            partida_actual_nombre,
                                            snapshot_guardado,
                                            accesorio_p1=accesorio_p1,
                                            accesorio_p2=accesorio_p2,
                                            partida_actual_password=partida_actual_password,
                                        )
                                        if fin_acc == "menu":
                                            estado_actual = ESTADO_SELECCION_NIVEL
                                            seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                                            reproducir_musica("menu", forzar=True)
                                        else:
                                            ejecutando = False

                    if btn_volver_partidas.collidepoint(evento.pos):
                        pulsado = True
                        sp_vp_s = _obtener_boton_volver("semi", idm_act)
                        sp_vp_a = _obtener_boton_volver("apretado", idm_act)
                        sp_vp_n = _obtener_boton_volver("normal", idm_act)
                        if sp_vp_s and sp_vp_a:
                            f_limp = _obtener_fondo_partidas(ANCHO_MENU, ALTO_MENU)
                            pulsado = animar_pulsacion_boton(pantalla, btn_volver_partidas, sp_vp_s, sp_vp_a, f_limp, sp_vp_n, tipo_sonido="ventana_volver")
                        if pulsado:
                            estado_actual = ESTADO_MODO_JUEGO

                elif estado_actual == ESTADO_PERSONAJES:
                    if btn_volver_personajes.collidepoint(evento.pos) or btn_guardar.collidepoint(evento.pos):
                        pulsado = True
                        idm_act = obtener_idioma()
                        sp_vp_s = _obtener_boton_volver("semi", idm_act)
                        sp_vp_a = _obtener_boton_volver("apretado", idm_act)
                        sp_vp_n = _obtener_boton_volver("normal", idm_act)
                        if sp_vp_s and sp_vp_a and btn_volver_personajes.collidepoint(evento.pos):
                            pulsado = animar_pulsacion_boton(pantalla, btn_volver_personajes, sp_vp_s, sp_vp_a, _obtener_fondo_personajes(ANCHO_MENU, ALTO_MENU), sp_vp_n, tipo_sonido="ventana_volver")
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL
                            break

                    # Pestañas [ COLORES ] y [ ACCESORIOS ]
                    rect_tab_col = pygame.Rect(388, 83, 240, 67)
                    rect_tab_acc = pygame.Rect(652, 83, 240, 67)

                    if rect_tab_col.collidepoint(evento.pos):
                        if tab_personajes_actual != "colores":
                            tab_personajes_actual = "colores"
                            reproducir_sonido_ui("tab")
                    elif rect_tab_acc.collidepoint(evento.pos):
                        if tab_personajes_actual != "accesorios":
                            tab_personajes_actual = "accesorios"
                            reproducir_sonido_ui("tab")
                        acc_list_tab = obtener_accesorios_disponibles()
                        for _ia, _acc in enumerate(acc_list_tab):
                            if _acc["id"] == accesorio_p1:
                                pagina_acc_p1 = _ia // 6
                            if _acc["id"] == accesorio_p2:
                                pagina_acc_p2 = _ia // 6

                    # Marcos de selección (Jugador 1: izquierda=125, Jugador 2: izquierda=685)
                    rect_f1_ev = pygame.Rect(125, 295, 470, 276)
                    rect_f2_ev = pygame.Rect(685, 295, 470, 276)

                    if tab_personajes_actual == "colores":
                        w_sw, h_sw = 80, 45
                        y_start_sw = 338
                        h_paso_y = 77
                        for r_idx, fila in enumerate(FILAS_COLORES_SELECCION):
                            n = len(fila)
                            gap_x = 10 if n == 5 else 24
                            row_w = n * w_sw + (n - 1) * gap_x
                            x_start_rel = (rect_f1_ev.width - row_w) // 2
                            y_sw = y_start_sw + r_idx * h_paso_y
                            for c_idx, color_idx in enumerate(fila):
                                p_info = PERSONAJES_DISPONIBLES[color_idx]
                                x_sw_rel = x_start_rel + c_idx * (w_sw + gap_x)
                                r1 = pygame.Rect(rect_f1_ev.left + x_sw_rel, y_sw, w_sw, h_sw + 28)
                                r2 = pygame.Rect(rect_f2_ev.left + x_sw_rel, y_sw, w_sw, h_sw + 28)

                                if r1.collidepoint(evento.pos):
                                    if color_p1 != p_info["nombre"]:
                                        color_p1 = p_info["nombre"]
                                        personalizacion_modificada_en_menu = True
                                        reproducir_sonido_ui("select")
                                        # Respetar accesorios exclusivos: si el equipado no le pertenece, desequipar
                                        permitidos_p1 = [a["id"] for a in obtener_accesorios_disponibles(color_p1)]
                                        if accesorio_p1 not in permitidos_p1:
                                            accesorio_p1 = "Ninguno"
                                if r2.collidepoint(evento.pos):
                                    if color_p2 != p_info["nombre"]:
                                        color_p2 = p_info["nombre"]
                                        personalizacion_modificada_en_menu = True
                                        reproducir_sonido_ui("select")
                                        # Respetar accesorios exclusivos: si el equipado no le pertenece, desequipar
                                        permitidos_p2 = [a["id"] for a in obtener_accesorios_disponibles(color_p2)]
                                        if accesorio_p2 not in permitidos_p2:
                                            accesorio_p2 = "Ninguno"

                    elif tab_personajes_actual == "accesorios":
                        accesorios_p1_disp = obtener_accesorios_disponibles(color_p1)
                        accesorios_p2_disp = obtener_accesorios_disponibles(color_p2)
                        items_por_pag = 6
                        total_pags_p1 = max(1, (len(accesorios_p1_disp) + items_por_pag - 1) // items_por_pag)
                        total_pags_p2 = max(1, (len(accesorios_p2_disp) + items_por_pag - 1) // items_por_pag)

                        # Flechas de paginación para Jugador 1
                        btn_prev_p1 = pygame.Rect(rect_f1_ev.centerx - 72, rect_f1_ev.top + 234, 34, 26)
                        btn_next_p1 = pygame.Rect(rect_f1_ev.centerx + 38, rect_f1_ev.top + 234, 34, 26)
                        if btn_prev_p1.collidepoint(evento.pos):
                            pagina_acc_p1 = (pagina_acc_p1 - 1) % total_pags_p1
                            reproducir_sonido_ui("pagina")
                        elif btn_next_p1.collidepoint(evento.pos):
                            pagina_acc_p1 = (pagina_acc_p1 + 1) % total_pags_p1
                            reproducir_sonido_ui("pagina")

                        # Flechas de paginación para Jugador 2
                        btn_prev_p2 = pygame.Rect(rect_f2_ev.centerx - 72, rect_f2_ev.top + 234, 34, 26)
                        btn_next_p2 = pygame.Rect(rect_f2_ev.centerx + 38, rect_f2_ev.top + 234, 34, 26)
                        if btn_prev_p2.collidepoint(evento.pos):
                            pagina_acc_p2 = (pagina_acc_p2 - 1) % total_pags_p2
                            reproducir_sonido_ui("pagina")
                        elif btn_next_p2.collidepoint(evento.pos):
                            pagina_acc_p2 = (pagina_acc_p2 + 1) % total_pags_p2
                            reproducir_sonido_ui("pagina")

                        w_acc, h_acc, gap_acc_x, gap_acc_y = 126, 82, 16, 10
                        ancho_fila_acc = 3 * w_acc + 2 * gap_acc_x
                        x_offset_acc = (rect_f1_ev.width - ancho_fila_acc) // 2

                        # Selección de accesorios en marco de Jugador 1
                        inicio_p1 = pagina_acc_p1 * items_por_pag
                        for idx_rel, acc in enumerate(accesorios_p1_disp[inicio_p1:inicio_p1 + items_por_pag]):
                            r = idx_rel // 3
                            c = idx_rel % 3
                            x_offset_rel = x_offset_acc + c * (w_acc + gap_acc_x)
                            y_card_a = rect_f1_ev.top + 42 + r * (h_acc + gap_acc_y)
                            ra1 = pygame.Rect(rect_f1_ev.left + x_offset_rel, y_card_a, w_acc, h_acc)
                            if ra1.collidepoint(evento.pos):
                                if accesorio_p1 != acc["id"]:
                                    accesorio_p1 = acc["id"]
                                    personalizacion_modificada_en_menu = True
                                    reproducir_sonido_ui("select")

                        # Selección de accesorios en marco de Jugador 2
                        inicio_p2 = pagina_acc_p2 * items_por_pag
                        for idx_rel, acc in enumerate(accesorios_p2_disp[inicio_p2:inicio_p2 + items_por_pag]):
                            r = idx_rel // 3
                            c = idx_rel % 3
                            x_offset_rel = x_offset_acc + c * (w_acc + gap_acc_x)
                            y_card_a = rect_f2_ev.top + 42 + r * (h_acc + gap_acc_y)
                            ra2 = pygame.Rect(rect_f2_ev.left + x_offset_rel, y_card_a, w_acc, h_acc)
                            if ra2.collidepoint(evento.pos):
                                if accesorio_p2 != acc["id"]:
                                    accesorio_p2 = acc["id"]
                                    personalizacion_modificada_en_menu = True
                                    reproducir_sonido_ui("select")

                elif estado_actual == ESTADO_CONFIGURACION:
                    idm_act = obtener_idioma()
                    if btn_volver_config.collidepoint(evento.pos):
                        sp_v_s = _obtener_boton_volver("semi", idm_act)
                        sp_v_a = _obtener_boton_volver("apretado", idm_act)
                        sp_v_n = _obtener_boton_volver("normal", idm_act)
                        pulsado = animar_pulsacion_boton(pantalla, btn_volver_config, sp_v_s, sp_v_a, _obtener_fondo_opciones(ANCHO_MENU, ALTO_MENU), sp_v_n, tipo_sonido="ventana_volver")
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL
                    elif rect_btn_sec_cfg.collidepoint(evento.pos):
                        if seccion_opciones_actual != "configuracion":
                            reproducir_sonido_ui("tab")
                        seccion_opciones_actual = "configuracion"
                    elif rect_btn_sec_ctrl.collidepoint(evento.pos):
                        if seccion_opciones_actual != "controles":
                            reproducir_sonido_ui("tab")
                        seccion_opciones_actual = "controles"
                    elif rect_btn_sec_inst.collidepoint(evento.pos):
                        if seccion_opciones_actual != "instrucciones":
                            reproducir_sonido_ui("tab")
                        seccion_opciones_actual = "instrucciones"
                    elif seccion_opciones_actual == "configuracion":
                        rect_panel_ev = pygame.Rect(340, 115, 875, 495)
                        y_vol_ev = rect_panel_ev.top + 60
                        r_card_vol_ev = pygame.Rect(rect_panel_ev.left + 45, y_vol_ev + 24, rect_panel_ev.width - 90, 72)
                        cy_v_ev = r_card_vol_ev.centery
                        r_menos_ev = pygame.Rect(r_card_vol_ev.left + 25, cy_v_ev - 22, 50, 44)
                        r_barra_bg_ev = pygame.Rect(r_menos_ev.right + 20, cy_v_ev - 18, 460, 36)
                        r_mas_ev = pygame.Rect(r_barra_bg_ev.right + 20, cy_v_ev - 22, 50, 44)

                        y_idioma_ev = r_card_vol_ev.bottom + 12
                        r_card_idm_ev = pygame.Rect(rect_panel_ev.left + 45, y_idioma_ev + 24, rect_panel_ev.width - 90, 94)
                        w_btn_l_ev = (r_card_idm_ev.width - 60) // 3
                        r_bl_es = pygame.Rect(r_card_idm_ev.left + 20, r_card_idm_ev.top + 11, w_btn_l_ev, 72)
                        r_bl_en = pygame.Rect(r_card_idm_ev.left + 20 + (w_btn_l_ev + 10), r_card_idm_ev.top + 11, w_btn_l_ev, 72)
                        r_bl_zh = pygame.Rect(r_card_idm_ev.left + 20 + 2 * (w_btn_l_ev + 10), r_card_idm_ev.top + 11, w_btn_l_ev, 72)

                        y_musica_ev = r_card_idm_ev.bottom + 12
                        r_card_mus_ev = pygame.Rect(rect_panel_ev.left + 45, y_musica_ev + 24, rect_panel_ev.width - 90, 102)
                        w_btn_m_ev = (r_card_mus_ev.width - 60) // 3
                        r_bm_rnd = pygame.Rect(r_card_mus_ev.left + 20, r_card_mus_ev.top + 10, w_btn_m_ev, 82)
                        r_bm_cai = pygame.Rect(r_card_mus_ev.left + 20 + (w_btn_m_ev + 10), r_card_mus_ev.top + 10, w_btn_m_ev, 82)
                        r_bm_chr = pygame.Rect(r_card_mus_ev.left + 20 + 2 * (w_btn_m_ev + 10), r_card_mus_ev.top + 10, w_btn_m_ev, 82)

                        if r_menos_ev.collidepoint(evento.pos):
                            cambiar_volumen(-10)
                            reproducir_beep_volumen()
                        elif r_mas_ev.collidepoint(evento.pos):
                            cambiar_volumen(+10)
                            reproducir_beep_volumen()
                        elif r_barra_bg_ev.collidepoint(evento.pos):
                            frac = max(0.0, min(1.0, (evento.pos[0] - (r_barra_bg_ev.left + 4)) / float(max(1, r_barra_bg_ev.width - 8))))
                            nuevo_vol = int(round(frac * 10)) * 10
                            fijar_volumen(nuevo_vol)
                            reproducir_beep_volumen()
                        elif r_bl_es.collidepoint(evento.pos):
                            cambiar_idioma("es")
                            reproducir_sonido_ui("select")
                        elif r_bl_en.collidepoint(evento.pos):
                            cambiar_idioma("en")
                            reproducir_sonido_ui("select")
                        elif r_bl_zh.collidepoint(evento.pos):
                            cambiar_idioma("zh")
                            reproducir_sonido_ui("select")
                        elif r_bm_rnd.collidepoint(evento.pos):
                            fijar_modo_musica_menu("aleatorio")
                            reproducir_sonido_ui("select")
                        elif r_bm_cai.collidepoint(evento.pos):
                            fijar_modo_musica_menu("caillou")
                            reproducir_sonido_ui("select")
                        elif r_bm_chr.collidepoint(evento.pos):
                            fijar_modo_musica_menu("christmas")
                            reproducir_sonido_ui("select")

                elif estado_actual == ESTADO_CREDITOS:
                    idm_act = obtener_idioma()
                    if btn_volver_creditos.collidepoint(evento.pos):
                        sp_v_s = _obtener_boton_volver("semi", idm_act)
                        sp_v_a = _obtener_boton_volver("apretado", idm_act)
                        sp_v_n = _obtener_boton_volver("normal", idm_act)
                        pulsado = animar_pulsacion_boton(pantalla, btn_volver_creditos, sp_v_s, sp_v_a, (30, 30, 30), sp_v_n, tipo_sonido="ventana_volver")
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
                    # Iconos superiores de Selección de Niveles (Configuración, Casita y X)
                    if rect_btn_config_niveles.collidepoint(evento.pos):
                        pulsado = True
                        if spr_confign_semi and spr_confign_apretado:
                            f_limpio = fondo_btn_config_niveles if fondo_btn_config_niveles else (255, 240, 195)
                            pulsado = animar_pulsacion_boton(pantalla, rect_btn_config_niveles, spr_confign_semi, spr_confign_apretado, f_limpio, spr_confign_normal, tipo_sonido="menu")
                        if pulsado:
                            mostrar_pestana_configuracion(pantalla, reloj)
                            break
                    if rect_btn_casa_niveles.collidepoint(evento.pos):
                        pulsado = True
                        if spr_casa_semi and spr_casa_apretado:
                            f_limpio = fondo_btn_casa_niveles if fondo_btn_casa_niveles else (255, 240, 195)
                            pulsado = animar_pulsacion_boton(pantalla, rect_btn_casa_niveles, spr_casa_semi, spr_casa_apretado, f_limpio, spr_casa_normal, tipo_sonido="menu")
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL
                            break
                    if rect_btn_x_niveles.collidepoint(evento.pos):
                        pulsado = True
                        if spr_xn_semi and spr_xn_apretado:
                            f_limpio = fondo_btn_x_niveles if fondo_btn_x_niveles else (255, 240, 195)
                            pulsado = animar_pulsacion_boton(pantalla, rect_btn_x_niveles, spr_xn_semi, spr_xn_apretado, f_limpio, spr_xn_normal, tipo_sonido="ventana_cancelar")
                        if pulsado:
                            intentar_salir()
                            break

                    rect_panel, tabs_info, rects_cards = obtener_geometria_menu(ANCHO_MENU, ALTO_MENU, NIVELES_POR_MUNDO[mundo_seleccionado])
                    tab_presionada = False
                    for m, t_data in tabs_info.items():
                        if t_data["rect_click"].collidepoint(evento.pos):
                            if mundo_seleccionado != m:
                                reproducir_sonido_ui("tab")
                            mundo_seleccionado = m
                            tab_presionada = True
                            break

                    if not tab_presionada:
                        es_admin_partida = es_partida_admin(partida_actual_nombre, partida_actual_id)
                        for idx_nivel, rect_c in enumerate(rects_cards):
                            desbloqueado = niveles_desbloqueados[mundo_seleccionado][idx_nivel]
                            if rect_c.collidepoint(evento.pos):
                                if es_nivel_jefe(mundo_seleccionado, idx_nivel + 1) and not es_admin_partida:
                                    # Nivel de jefe en proceso: no jugable en partidas normales
                                    break
                                if desbloqueado or es_admin_partida:
                                    reproducir_sonido_ui("menu")
                                    fin_acc, mundo_seleccionado = jugar_niveles_desde(
                                        mundo_seleccionado,
                                        idx_nivel,
                                        color_p1,
                                        color_p2,
                                        niveles_desbloqueados,
                                        partida_actual_id,
                                        partida_actual_nombre,
                                        snapshot_guardado,
                                        accesorio_p1=accesorio_p1,
                                        accesorio_p2=accesorio_p2,
                                        partida_actual_password=partida_actual_password,
                                    )
                                    if fin_acc == "menu":
                                        estado_actual = ESTADO_SELECCION_NIVEL
                                        seleccionar_musica_menu_aleatoria(forzar_nueva_eleccion=True)
                                        reproducir_musica("menu", forzar=True)
                                    else:
                                        ejecutando = False
                                    break

            elif evento.type == pygame.MOUSEWHEEL:
                if estado_actual == ESTADO_LISTA_PARTIDAS:
                    total_pag = max(1, (len(cargar_partidas()) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                    if total_pag > 1:
                        if evento.y > 0 and pagina_partidas > 0:
                            pagina_partidas -= 1
                            reproducir_sonido_ui("pagina")
                        elif evento.y < 0 and pagina_partidas < total_pag - 1:
                            pagina_partidas += 1
                            reproducir_sonido_ui("pagina")

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if estado_actual == ESTADO_CONFIGURACION:
                        estado_actual = ESTADO_MENU_PRINCIPAL

        pantalla.fill((30, 30, 30))

        if estado_actual == ESTADO_MENU_PRINCIPAL:
            gestor_personajes_menu.sincronizar_personalizacion(color_p1, accesorio_p1, color_p2, accesorio_p2)
            gestor_personajes_menu.actualizar()

            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()
            botones_menu_datos = _obtener_botones_menu_principal(idm_act)
            spr_x_dib = spr_x_hover if (spr_x_hover and rect_btn_x.collidepoint(pos_mouse)) else spr_x_normal
            gestor_personajes_menu.dibujar_menu_completo(
                pantalla,
                botones_menu_datos=botones_menu_datos,
                pos_mouse=pos_mouse,
                spr_x=spr_x_dib,
                rect_x=rect_btn_x,
                fuente_titulo=fuente_pixel_titulo,
            )

        elif estado_actual == ESTADO_MODO_JUEGO:
            # Fondo panorámico de aventura al atardecer en pixel art
            pantalla.blit(_obtener_fondo_modo_juego(ANCHO_MENU, ALTO_MENU), (0, 0))
            _dibujar_copos_modo(pantalla)

            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()

            # Marquesina / Placa cálida para Título y Subtítulo que asegura contraste y armonía
            w_placa = min(680, ANCHO_MENU - 40)
            h_placa = 106
            x_placa = (ANCHO_MENU - w_placa) // 2
            y_placa = 45

            surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
            pygame.draw.rect(surf_placa, (252, 242, 228, 225), (0, 0, w_placa, h_placa), border_radius=16)
            pygame.draw.rect(surf_placa, (85, 28, 48, 240), (0, 0, w_placa, h_placa), width=3, border_radius=16)
            pygame.draw.rect(surf_placa, (235, 142, 72, 180), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)
            for cx_d, cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
                pygame.draw.circle(surf_placa, (215, 110, 42), (cx_d, cy_d), 4)
                pygame.draw.circle(surf_placa, (255, 240, 200), (cx_d, cy_d), 2)
            pantalla.blit(surf_placa, (x_placa, y_placa))

            # Título «MODO DE JUEGO» en bordó profundo con sombra sutil de relieve
            txt_tit = t("modo_juego")
            f_tit_modo = obtener_fuente_para_texto(txt_tit, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
            t_somb = f_tit_modo.render(txt_tit, True, (225, 205, 185))
            t_tit = f_tit_modo.render(txt_tit, True, (68, 20, 42))
            rect_tit = t_tit.get_rect(center=(ANCHO_MENU // 2, y_placa + 38))
            pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
            pantalla.blit(t_tit, rect_tit)

            # Subtítulo en marrón cálido con ajuste dinámico de tamaño y márgenes interiores
            txt_sub = t("subtitulo_modo")
            ancho_max_sub = w_placa - 70  # Margen interior de al menos 35px a cada lado
            f_sub_modo, _ = ajustar_tamano_fuente(
                txt_sub,
                categoria="subtitulo",
                tamano_inicial=TAMANO_SUBTITULO,
                ancho_max=ancho_max_sub,
                tamano_min=13
            )
            t_sub_s = f_sub_modo.render(txt_sub, True, (255, 255, 255))
            t_sub = f_sub_modo.render(txt_sub, True, (108, 52, 45))
            rect_sub = t_sub.get_rect(center=(ANCHO_MENU // 2, y_placa + 78))
            pantalla.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
            pantalla.blit(t_sub, rect_sub)

            # Botón CONTINUAR (Ámbar atardecer con relieve y sombra)
            hov_c = btn_continuar.collidepoint(pos_mouse)
            spr_c_norm = _obtener_boton_modo("continuar", "normal", idm_act)
            spr_c_hov = _obtener_boton_modo("continuar", "hover", idm_act)
            spr_c = spr_c_hov if (hov_c and spr_c_hov) else spr_c_norm
            if spr_c:
                pantalla.blit(spr_c, btn_continuar)

            # Botón NUEVA PARTIDA (Violeta/Ciruela atardecer con resplandor)
            hov_n = btn_nueva_partida.collidepoint(pos_mouse)
            spr_n_norm = _obtener_boton_modo("nueva", "normal", idm_act)
            spr_n_hov = _obtener_boton_modo("nueva", "hover", idm_act)
            spr_n = spr_n_hov if (hov_n and spr_n_hov) else spr_n_norm
            if spr_n:
                pantalla.blit(spr_n, btn_nueva_partida)

            # Botón VOLVER AL MENÚ (Pergamino crema con borde bordó y relieve)
            hov_v = btn_volver_modo.collidepoint(pos_mouse)
            spr_v_norm = _obtener_boton_volver("normal", idm_act)
            spr_v_hov = _obtener_boton_volver("hover", idm_act)
            spr_v = spr_v_hov if (hov_v and spr_v_hov) else spr_v_norm
            if spr_v:
                pantalla.blit(spr_v, btn_volver_modo)

        elif estado_actual == ESTADO_LISTA_PARTIDAS:
            ANCHO_MENU = pantalla.get_width()
            ALTO_MENU = pantalla.get_height()
            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()
            partidas = cargar_partidas()

            # Asegurar recursos pixel art del diario cargados
            _cargar_recursos_partidas()

            # Fondo pergamino antiguo con bocetos cartográficos y bordes envejecidos
            pantalla.blit(_obtener_fondo_partidas(ANCHO_MENU, ALTO_MENU), (0, 0))

            rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
                obtener_geometria_panel_partidas(ANCHO_MENU, ALTO_MENU, bool(partidas))
            )

            # Título «PARTIDAS GUARDADAS» en sepia oscuro con relieve y subtítulo de expedición
            txt_tit_lp = t("partidas_guardadas")
            f_tit_lp = obtener_fuente_para_texto(txt_tit_lp, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
            t_somb = f_tit_lp.render(txt_tit_lp, True, (195, 170, 140))
            t_tit = f_tit_lp.render(txt_tit_lp, True, (58, 38, 24))
            rect_tit = t_tit.get_rect(center=(ANCHO_MENU // 2, 46))
            pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
            pantalla.blit(t_tit, rect_tit)

            txt_sub_lp = t("sub_partidas")
            f_sub_lp = obtener_fuente_para_texto(txt_sub_lp, categoria="decorativa", tamano=TAMANO_DECORATIVA)
            subt = f_sub_lp.render(txt_sub_lp, True, (125, 95, 65))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 78)))

            # Contenedor de página del diario (folio pergamino con líneas sutiles y remaches)
            col_pagina = (252, 246, 235)
            col_borde_pag = (190, 160, 125)
            col_linea_int = (225, 200, 160)
            pygame.draw.rect(pantalla, col_pagina, rect_panel_partidas, border_radius=16)
            pygame.draw.rect(pantalla, col_borde_pag, rect_panel_partidas, width=3, border_radius=16)
            pygame.draw.rect(pantalla, col_linea_int, rect_panel_partidas.inflate(-8, -8), width=1, border_radius=12)

            # Pauta de cuaderno sutil (líneas horizontales tenues de diario de campo)
            for y_linea in range(rect_panel_partidas.top + 28, rect_panel_partidas.bottom - 20, 22):
                pygame.draw.line(pantalla, (238, 230, 216), (rect_panel_partidas.left + 14, y_linea), (rect_panel_partidas.right - 14, y_linea), 1)

            # Remaches / clavos metálicos en las esquinas del folio
            for rx, ry in [
                (rect_panel_partidas.left + 12, rect_panel_partidas.top + 12),
                (rect_panel_partidas.right - 12, rect_panel_partidas.top + 12),
                (rect_panel_partidas.left + 12, rect_panel_partidas.bottom - 12),
                (rect_panel_partidas.right - 12, rect_panel_partidas.bottom - 12),
            ]:
                pygame.draw.circle(pantalla, (205, 175, 105), (rx, ry), 3)
                pygame.draw.circle(pantalla, (100, 70, 40), (rx, ry), 3, width=1)

            if not partidas:
                txt_sin = t("no_partidas")
                f_sin = obtener_fuente_para_texto(txt_sin, categoria="subtitulo", tamano=TAMANO_SUBTITULO)
                t_sin = f_sin.render(txt_sin, True, (65, 45, 30))
                pantalla.blit(t_sin, t_sin.get_rect(center=(rect_panel_partidas.centerx, rect_panel_partidas.centery - 40)))

                rect_sin2 = pygame.Rect(rect_panel_partidas.left + 40, rect_panel_partidas.centery - 20, rect_panel_partidas.width - 80, 24)
                dibujar_texto_en_rect(pantalla, t("comenzar_historia"), rect_sin2, categoria="texto", tamano=16, color=(120, 100, 80))

                hov_prim = btn_iniciar_primera.collidepoint(pos_mouse)
                spr_prim_norm = _obtener_boton_primera_partida("normal", idm_act)
                spr_prim_hov = _obtener_boton_primera_partida("hover", idm_act)
                spr_prim = spr_prim_hov if (hov_prim and spr_prim_hov) else spr_prim_norm
                if spr_prim:
                    pantalla.blit(spr_prim, btn_iniciar_primera)
                else:
                    col_prim = (235, 128, 48) if hov_prim else (215, 110, 42)
                    pygame.draw.rect(pantalla, col_prim, btn_iniciar_primera, border_radius=12)
                    pygame.draw.rect(pantalla, (118, 44, 14), btn_iniciar_primera, width=2, border_radius=12)
                    dibujar_texto_en_rect(pantalla, t("comenzar_aventura"), btn_iniciar_primera, categoria="boton", tamano=TAMANO_BOTONES, color=(255, 255, 255), padding=6)
            else:
                total_paginas = max(1, (len(partidas) + MAX_PARTIDAS_POR_PAGINA - 1) // MAX_PARTIDAS_POR_PAGINA)
                if pagina_partidas >= total_paginas:
                    pagina_partidas = max(0, total_paginas - 1)

                inicio_idx = pagina_partidas * MAX_PARTIDAS_POR_PAGINA
                fin_idx = inicio_idx + MAX_PARTIDAS_POR_PAGINA
                partidas_pagina = partidas[inicio_idx:fin_idx]

                fuentes_tarjetas = {
                    "titulo_card": fuente_card_titulo,
                    "sub_card": fuente_card_sub,
                    "btn_card": fuente_pixel_card_btn,
                    "badge": fuente_pixel_badge,
                    "btn": fuente_pixel_badge,
                    "texto": fuente_texto,
                    "sub_btn": fuente_sub_btn,
                }

                dict_sp_partidas = _obtener_sprites_tarjeta(idm_act)
                for idx_slot, p in enumerate(partidas_pagina):
                    dibujar_tarjeta_partida(pantalla, p, idx_slot, rect_panel_partidas, pos_mouse, fuentes_tarjetas, sprites_botones=dict_sp_partidas)

                # Indicador de paginación si hay más de 1 página (y = 508, dentro del panel inferior sin colisiones)
                if total_paginas > 1:
                    btn_pag_ant = pygame.Rect(rect_panel_partidas.centerx - 120, 508, 36, 30)
                    btn_pag_sig = pygame.Rect(rect_panel_partidas.centerx + 84, 508, 36, 30)

                    # Botón página anterior
                    hov_ant = btn_pag_ant.collidepoint(pos_mouse) and pagina_partidas > 0
                    col_ant = (255, 255, 255) if hov_ant else ((253, 246, 233) if pagina_partidas > 0 else (240, 230, 215))
                    borde_ant = (160, 125, 90) if hov_ant else (195, 168, 138)
                    pygame.draw.rect(pantalla, col_ant, btn_pag_ant, border_radius=6)
                    col_flecha_ant = (65, 45, 30) if pagina_partidas > 0 else (175, 155, 135)
                    cx_a, cy_a = btn_pag_ant.center
                    for dy in range(-4, 5):
                        ancho_f = 4 - abs(dy)
                        for dx in range(ancho_f + 1):
                            pantalla.set_at((cx_a + 2 - dx, cy_a + dy), col_flecha_ant)

                    # Contador de página
                    txt_pag = t("entrada_pagina").format(pagina_partidas + 1, total_paginas)
                    f_pag = obtener_fuente_para_texto(txt_pag, categoria="contador", tamano=TAMANO_CONTADOR)
                    t_pag = f_pag.render(txt_pag, True, (75, 55, 38))
                    pantalla.blit(t_pag, t_pag.get_rect(center=(rect_panel_partidas.centerx, 523)))

                    # Botón página siguiente
                    hov_sig = btn_pag_sig.collidepoint(pos_mouse) and pagina_partidas < total_paginas - 1
                    col_sig = (255, 255, 255) if hov_sig else ((253, 246, 233) if pagina_partidas < total_paginas - 1 else (240, 230, 215))
                    borde_sig = (160, 125, 90) if hov_sig else (195, 168, 138)
                    pygame.draw.rect(pantalla, col_sig, btn_pag_sig, border_radius=6)
                    pygame.draw.rect(pantalla, borde_sig, btn_pag_sig, width=2 if hov_sig else 1, border_radius=6)
                    col_flecha_sig = (65, 45, 30) if pagina_partidas < total_paginas - 1 else (175, 155, 135)
                    cx_s, cy_s = btn_pag_sig.center
                    for dy in range(-4, 5):
                        ancho_f = 4 - abs(dy)
                        for dx in range(ancho_f + 1):
                            pantalla.set_at((cx_s - 2 + dx, cy_s + dy), col_flecha_sig)

            # Botón «VOLVER» centrado al pie de la pantalla en tonos pergamino/crema
            hov_vp = btn_volver_partidas.collidepoint(pos_mouse)
            spr_vp_norm = _obtener_boton_volver("normal", idm_act)
            spr_vp_hov = _obtener_boton_volver("hover", idm_act)
            spr_vp = spr_vp_hov if (hov_vp and spr_vp_hov) else spr_vp_norm
            if spr_vp:
                pantalla.blit(spr_vp, btn_volver_partidas)
            else:
                col_vp = (255, 255, 255) if hov_vp else (253, 246, 233)
                borde_vp = (165, 135, 105) if hov_vp else (195, 168, 138)
                pygame.draw.rect(pantalla, col_vp, btn_volver_partidas, border_radius=12)
                pygame.draw.rect(pantalla, borde_vp, btn_volver_partidas, width=2, border_radius=12)
                dibujar_texto_en_rect(pantalla, t("volver"), btn_volver_partidas, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)

            if partidas:
                # Botón «NUEVA PARTIDA» ubicado al lado de «VOLVER», centrados juntos en ámbar/terracota
                hov_nd = btn_nueva_desde_lista.collidepoint(pos_mouse)
                spr_nd_norm = _obtener_boton_nueva_lista("normal", idm_act)
                spr_nd_hov = _obtener_boton_nueva_lista("hover", idm_act)
                spr_nd = spr_nd_hov if (hov_nd and spr_nd_hov) else spr_nd_norm
                if spr_nd:
                    pantalla.blit(spr_nd, btn_nueva_desde_lista)
                else:
                    col_nd = (235, 128, 48) if hov_nd else (215, 110, 42)
                    borde_nd = (255, 255, 255) if hov_nd else (118, 44, 14)
                    pygame.draw.rect(pantalla, col_nd, btn_nueva_desde_lista, border_radius=12)
                    pygame.draw.rect(pantalla, borde_nd, btn_nueva_desde_lista, width=2, border_radius=12)
                    dibujar_texto_en_rect(pantalla, t("nueva_partida"), btn_nueva_desde_lista, categoria="boton", tamano=TAMANO_BOTONES, color=(255, 255, 255), padding=6)

        elif estado_actual == ESTADO_PERSONAJES:
            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()

            # 1. Fondo de habitación de vestuario / camerino pixel art
            pantalla.blit(_obtener_fondo_personajes(ANCHO_MENU, ALTO_MENU), (0, 0))

            # 2. Título y subtítulo centrados
            txt_tit_pj = t("personalizacion_personajes")
            f_tit_pj = obtener_fuente_para_texto(txt_tit_pj, categoria="titulo", tamano=TAMANO_TITULO, negrita=True)
            titulo = f_tit_pj.render(txt_tit_pj, True, (60, 45, 35))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 46)))

            txt_sub_pj = t("sub_personalizacion")
            f_sub_pj = obtener_fuente_para_texto(txt_sub_pj, categoria="subtitulo", tamano=TAMANO_SUBTITULO)
            subt = f_sub_pj.render(txt_sub_pj, True, (120, 100, 85))
            pantalla.blit(subt, subt.get_rect(center=(ANCHO_MENU // 2, 78)))

            # 3. Pestañas visuales [ COLORES ] y [ ACCESORIOS ] con sprites oficiales
            w_tab_pj = 240
            h_tab_pj = round(w_tab_pj * 264 / 950)  # 67 px
            y_tab_pj = 150 - h_tab_pj               # 83 px
            rect_tab_col = pygame.Rect(388, y_tab_pj, w_tab_pj, h_tab_pj)
            rect_tab_acc = pygame.Rect(652, y_tab_pj, w_tab_pj, h_tab_pj)

            hov_tab_col = rect_tab_col.collidepoint(pos_mouse)
            hov_tab_acc = rect_tab_acc.collidepoint(pos_mouse)

            # Dibujar primero la pestaña inactiva y luego la seleccionada para mantener profundidad correcta
            tabs_orden = [
                ("accesorios", rect_tab_acc, hov_tab_acc),
                ("colores", rect_tab_col, hov_tab_col),
            ] if tab_personajes_actual == "colores" else [
                ("colores", rect_tab_col, hov_tab_col),
                ("accesorios", rect_tab_acc, hov_tab_acc),
            ]

            for tab_id, r_tab, hov in tabs_orden:
                es_activa = (tab_personajes_actual == tab_id)
                nom_spr = f"{tab_id}-seleccionado.png" if es_activa else f"{tab_id}.png"
                col_txt_tab = (116, 78, 45) if es_activa else (157, 131, 100)
                spr_tab = generar_boton_con_texto(
                    nom_spr, w_tab_pj, h_tab_pj,
                    texto=t(tab_id).upper(),
                    color_texto=col_txt_tab,
                    tamano_fuente=16,
                    offset_y=0,
                )
                if spr_tab:
                    pantalla.blit(spr_tab, (r_tab.left, r_tab.top))
                    if not es_activa and hov:
                        glow = spr_tab.copy()
                        bright = pygame.Surface(spr_tab.get_size(), pygame.SRCALPHA)
                        bright.fill((35, 35, 35, 0))
                        glow.blit(bright, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                        pantalla.blit(glow, (r_tab.left, r_tab.top))
                else:
                    r_fb = pygame.Rect(r_tab.left, 100, w_tab_pj, 50)
                    col_tab_bg = (246, 215, 153) if es_activa else ((248, 242, 232) if hov else (238, 226, 210))
                    col_tab_borde = (175, 130, 80) if es_activa else (195, 175, 155)
                    ancho_b = 3 if es_activa else 2
                    pygame.draw.rect(pantalla, col_tab_bg, r_fb, border_radius=12)
                    pygame.draw.rect(pantalla, col_tab_borde, r_fb, ancho_b, border_radius=12)

                    col_txt = (50, 40, 30) if es_activa else (130, 115, 100)
                    txt_tab_str = t(tab_id).upper()
                    dibujar_texto_en_rect(pantalla, txt_tab_str, r_fb, categoria="boton", tamano=18, color=col_txt, negrita=True, padding=8)

                    if es_activa:
                        dibujar_mascota_gato(pantalla, r_fb.left + 16, r_fb.top - 18, size=28, color=(246, 215, 153))

            # 4. Columnas simétricas de Jugador 1 y Jugador 2
            cx_p1 = 360
            cx_p2 = 920

            colores_dict = {p["nombre"]: p["color"] for p in PERSONAJES_DISPONIBLES}
            c_p1_val = colores_dict.get(color_p1, (124, 231, 255))
            c_p2_val = colores_dict.get(color_p2, (161, 123, 255))

            # Badges de encabezado de jugador con ajuste automático para nombres extensos de color
            r_badge_p1 = pygame.Rect(cx_p1 - 130, 150, 260, 32)
            pygame.draw.rect(pantalla, c_p1_val, r_badge_p1, border_radius=8)
            pygame.draw.rect(pantalla, (60, 45, 35), r_badge_p1, 2, border_radius=8)
            col_p1_trad = _obtener_nombre_color_visible(color_p1, idm_act).upper()
            dibujar_texto_en_rect(pantalla, f"{t('jugador')} 1  ({col_p1_trad})", r_badge_p1, categoria="boton", tamano=TAMANO_BADGE, color=(35, 30, 25), padding=4)

            r_badge_p2 = pygame.Rect(cx_p2 - 130, 150, 260, 32)
            pygame.draw.rect(pantalla, c_p2_val, r_badge_p2, border_radius=8)
            pygame.draw.rect(pantalla, (60, 45, 35), r_badge_p2, 2, border_radius=8)
            col_p2_trad = _obtener_nombre_color_visible(color_p2, idm_act).upper()
            dibujar_texto_en_rect(pantalla, f"{t('jugador')} 2  ({col_p2_trad})", r_badge_p2, categoria="boton", tamano=TAMANO_BADGE, color=(35, 30, 25), padding=4)

            # Previews de personajes con pedestal y accesorios
            for cx, col_pj, acc_pj in [
                (cx_p1, color_p1, accesorio_p1),
                (cx_p2, color_p2, accesorio_p2),
            ]:
                pygame.draw.ellipse(pantalla, (230, 210, 175), (cx - 50, 276, 100, 16))

                sp_pj = cargar_sprites(col_pj)
                img_pj = sp_pj.get("quieto", list(sp_pj.values())[0])
                rect_pj = img_pj.get_rect(center=(cx, 240))
                pantalla.blit(img_pj, rect_pj)

                if acc_pj and acc_pj != "Ninguno":
                    dibujar_accesorio_en_personaje(pantalla, acc_pj, sprite_personaje=img_pj, rect_personaje=rect_pj, mirando_derecha=True)

            # 5. Marcos rectangulares contenedores de opciones
            w_frame, h_frame = 470, 276
            y_frame = 295
            rect_f1 = pygame.Rect(cx_p1 - w_frame // 2, y_frame, w_frame, h_frame)
            rect_f2 = pygame.Rect(cx_p2 - w_frame // 2, y_frame, w_frame, h_frame)

            for rf in (rect_f1, rect_f2):
                pygame.draw.rect(pantalla, (253, 246, 233), rf, border_radius=16)
                pygame.draw.rect(pantalla, (195, 168, 138), rf, 3, border_radius=16)

                txt_encabezado = t("colores_disponibles") if tab_personajes_actual == "colores" else t("accesorios_disponibles")
                f_enc = obtener_fuente_para_texto(txt_encabezado, categoria="texto", tamano=TAMANO_TEXTO, negrita=True)
                t_enc = f_enc.render(txt_encabezado, True, (115, 95, 80))
                pantalla.blit(t_enc, t_enc.get_rect(center=(rf.centerx, rf.top + 20)))
                pygame.draw.line(pantalla, (235, 215, 195), (rf.left + 24, rf.top + 34), (rf.right - 24, rf.top + 34), 2)

            # 6. Opciones dentro del marco según la pestaña activa
            if tab_personajes_actual == "colores":
                w_sw, h_sw = 80, 45
                y_start_sw = 338
                h_paso_y = 77
                for r_idx, fila in enumerate(FILAS_COLORES_SELECCION):
                    n = len(fila)
                    gap_x = 10 if n == 5 else 24
                    row_w = n * w_sw + (n - 1) * gap_x
                    x_start_rel = (rect_f1.width - row_w) // 2
                    y_sw = y_start_sw + r_idx * h_paso_y

                    for c_idx, color_idx in enumerate(fila):
                        p_info = PERSONAJES_DISPONIBLES[color_idx]
                        x_sw_rel = x_start_rel + c_idx * (w_sw + gap_x)
                        r1 = pygame.Rect(rect_f1.left + x_sw_rel, y_sw, w_sw, h_sw)
                        r2 = pygame.Rect(rect_f2.left + x_sw_rel, y_sw, w_sw, h_sw)
                        nom_col = _obtener_nombre_color_visible(p_info["nombre"], idm_act)
                        f_nom = obtener_fuente_para_texto(nom_col, categoria="dialogos", tamano=22, negrita=True)

                        # P1 swatch
                        sel1 = (p_info["nombre"] == color_p1)
                        hov1 = r1.collidepoint(pos_mouse)
                        pygame.draw.rect(pantalla, p_info["color"], r1, border_radius=8)
                        if sel1:
                            pygame.draw.rect(pantalla, (255, 255, 255), r1, 3, border_radius=8)
                            pygame.draw.rect(pantalla, (40, 30, 25), r1, 1, border_radius=8)
                            cx_k, cy_k = r1.center
                            pts_chk = [(cx_k - 7, cy_k), (cx_k - 2, cy_k + 5), (cx_k + 7, cy_k - 5)]
                            pts_shadow = [(x + 1, y + 1) for x, y in pts_chk]
                            pygame.draw.lines(pantalla, (40, 30, 25), False, pts_shadow, 4)
                            pygame.draw.lines(pantalla, (255, 255, 255), False, pts_chk, 3)
                        elif hov1:
                            pygame.draw.rect(pantalla, (255, 255, 255), r1, 2, border_radius=8)
                        else:
                            pygame.draw.rect(pantalla, (180, 160, 140), r1, 1, border_radius=8)

                        col_t1 = (25, 15, 8) if sel1 else (50, 34, 22)
                        ts1 = f_nom.render(nom_col, True, col_t1)
                        tx1 = r1.centerx - ts1.get_width() // 2
                        ty1 = r1.bottom + 4
                        pantalla.blit(ts1, (tx1, ty1))
                        pantalla.blit(ts1, (tx1 + 1, ty1))

                        # P2 swatch
                        sel2 = (p_info["nombre"] == color_p2)
                        hov2 = r2.collidepoint(pos_mouse)
                        pygame.draw.rect(pantalla, p_info["color"], r2, border_radius=8)
                        if sel2:
                            pygame.draw.rect(pantalla, (255, 255, 255), r2, 3, border_radius=8)
                            pygame.draw.rect(pantalla, (40, 30, 25), r2, 1, border_radius=8)
                            cx_k2, cy_k2 = r2.center
                            pts_chk2 = [(cx_k2 - 7, cy_k2), (cx_k2 - 2, cy_k2 + 5), (cx_k2 + 7, cy_k2 - 5)]
                            pts_shadow2 = [(x + 1, y + 1) for x, y in pts_chk2]
                            pygame.draw.lines(pantalla, (40, 30, 25), False, pts_shadow2, 4)
                            pygame.draw.lines(pantalla, (255, 255, 255), False, pts_chk2, 3)
                        elif hov2:
                            pygame.draw.rect(pantalla, (255, 255, 255), r2, 2, border_radius=8)
                        else:
                            pygame.draw.rect(pantalla, (180, 160, 140), r2, 1, border_radius=8)

                        col_t2 = (25, 15, 8) if sel2 else (50, 34, 22)
                        ts2 = f_nom.render(nom_col, True, col_t2)
                        tx2 = r2.centerx - ts2.get_width() // 2
                        ty2 = r2.bottom + 4
                        pantalla.blit(ts2, (tx2, ty2))
                        pantalla.blit(ts2, (tx2 + 1, ty2))

            elif tab_personajes_actual == "accesorios":
                items_por_pag = 6
                w_acc, h_acc, gap_acc_x, gap_acc_y = 126, 82, 16, 10
                ancho_fila_acc = 3 * w_acc + 2 * gap_acc_x
                x_offset_acc = (w_frame - ancho_fila_acc) // 2

                for rf, acc_actual, pag_num, color_pj_actual in [
                    (rect_f1, accesorio_p1, pagina_acc_p1, color_p1),
                    (rect_f2, accesorio_p2, pagina_acc_p2, color_p2),
                ]:
                    accesorios_disp = obtener_accesorios_disponibles(color_pj_actual)
                    total_pags = max(1, (len(accesorios_disp) + items_por_pag - 1) // items_por_pag)
                    pag_num = min(pag_num, total_pags - 1)
                    # 1. Controles inferiores de paginación
                    btn_prev = pygame.Rect(rf.centerx - 72, rf.top + 234, 34, 26)
                    btn_next = pygame.Rect(rf.centerx + 38, rf.top + 234, 34, 26)

                    for b_rect, es_izq in [(btn_prev, True), (btn_next, False)]:
                        hov_b = b_rect.collidepoint(pos_mouse)
                        col_bg_b = (255, 252, 245) if hov_b else (244, 236, 224)
                        col_brd_b = (220, 180, 120) if hov_b else (195, 168, 138)
                        pygame.draw.rect(pantalla, col_bg_b, b_rect, border_radius=6)
                        pygame.draw.rect(pantalla, col_brd_b, b_rect, 2, border_radius=6)

                        col_arr = (80, 60, 45) if hov_b else (120, 100, 85)
                        cx_b, cy_b = b_rect.center
                        if es_izq:
                            for dy in range(-5, 6):
                                ancho_f = 5 - abs(dy)
                                for dx in range(ancho_f + 1):
                                    pantalla.set_at((cx_b + 2 - dx, cy_b + dy), col_arr)
                        else:
                            for dy in range(-5, 6):
                                ancho_f = 5 - abs(dy)
                                for dx in range(ancho_f + 1):
                                    pantalla.set_at((cx_b - 2 + dx, cy_b + dy), col_arr)

                    txt_pag = f"{pag_num + 1} / {total_pags}"
                    f_pag = obtener_fuente_para_texto(txt_pag, categoria="texto", tamano=TAMANO_BADGE, negrita=True)
                    t_pag = f_pag.render(txt_pag, True, (115, 95, 80))
                    pantalla.blit(t_pag, t_pag.get_rect(center=(rf.centerx, rf.top + 247)))

                    # 2. Tarjetas de accesorios de la página activa con fondo crema claro de alto contraste
                    inicio = pag_num * items_por_pag
                    for idx_rel, acc in enumerate(accesorios_disp[inicio:inicio + items_por_pag]):
                        r = idx_rel // 3
                        c = idx_rel % 3
                        x_offset_rel = x_offset_acc + c * (w_acc + gap_acc_x)
                        y_card_a = rf.top + 42 + r * (h_acc + gap_acc_y)
                        r_card_a = pygame.Rect(rf.left + x_offset_rel, y_card_a, w_acc, h_acc)

                        sel = (acc["id"] == acc_actual or acc["id"].lower() == str(acc_actual).lower())
                        hov = r_card_a.collidepoint(pos_mouse)

                        col_bg_a = (242, 252, 244) if sel else ((255, 252, 246) if hov else (248, 242, 232))
                        col_brd_a = (45, 165, 85) if sel else ((180, 145, 110) if hov else (195, 168, 138))
                        pygame.draw.rect(pantalla, col_bg_a, r_card_a, border_radius=10)
                        pygame.draw.rect(pantalla, col_brd_a, r_card_a, 3 if sel else 2, border_radius=10)

                        if sel:
                            cx_ca = r_card_a.right - 14
                            cy_ca = r_card_a.top + 14
                            pygame.draw.circle(pantalla, (45, 165, 85), (cx_ca, cy_ca), 9)
                            pts_ca = [(cx_ca - 4, cy_ca), (cx_ca - 1, cy_ca + 3), (cx_ca + 4, cy_ca - 3)]
                            pygame.draw.lines(pantalla, (255, 255, 255), False, pts_ca, 2)

                        if acc["id"] == "Ninguno":
                            cx_ic, cy_ic = r_card_a.centerx, r_card_a.top + 25
                            pygame.draw.circle(pantalla, (220, 80, 75), (cx_ic, cy_ic), 13, width=2)
                            pygame.draw.line(pantalla, (220, 80, 75), (cx_ic - 8, cy_ic - 8), (cx_ic + 8, cy_ic + 8), 2)
                        else:
                            surf_icon = _obtener_preview_accesorio_tarjeta(acc["id"])
                            if surf_icon:
                                r_mini = surf_icon.get_rect(center=(r_card_a.centerx, r_card_a.top + 25))
                                pantalla.blit(surf_icon, r_mini)

                        col_nom = (25, 75, 35) if sel else ((45, 30, 18) if hov else (55, 38, 25))
                        rect_nom_acc = pygame.Rect(r_card_a.left + 2, r_card_a.bottom - 32, r_card_a.width - 4, 30)
                        nom_acc_trad = t(acc["id"].lower())
                        dibujar_texto_en_rect(pantalla, nom_acc_trad, rect_nom_acc, categoria="boton", tamano=13, color=col_nom, negrita=True, multiline=True, alineacion="centro", padding=0, interlineado=1)

            # 7. Botón Volver al Menú
            hov_vpj = btn_volver_personajes.collidepoint(pos_mouse)
            spr_vpj_norm = _obtener_boton_volver("normal", idm_act)
            spr_vpj_hov = _obtener_boton_volver("hover", idm_act)
            spr_vpj = spr_vpj_hov if (hov_vpj and spr_vpj_hov) else spr_vpj_norm
            if spr_vpj:
                pantalla.blit(spr_vpj, btn_volver_personajes)
            else:
                col_v = (255, 255, 255) if hov_vpj else (242, 234, 222)
                pygame.draw.rect(pantalla, col_v, btn_volver_personajes, border_radius=10)
                pygame.draw.rect(pantalla, (185, 155, 125), btn_volver_personajes, width=2, border_radius=10)
                dibujar_texto_en_rect(pantalla, t("volver_al_menu"), btn_volver_personajes, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)

        elif estado_actual == ESTADO_CONFIGURACION:
            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()

            # 1. Fondo de paisaje invernal pixel art con copos de nieve cayendo
            pantalla.blit(_obtener_fondo_opciones(ANCHO_MENU, ALTO_MENU), (0, 0))
            _dibujar_copos_opciones(pantalla)

            # 2. Título y Subtítulo
            txt_tit = t("opciones").upper()
            f_tit = obtener_fuente_para_texto(txt_tit, categoria="titulo", tamano=TAMANO_TITULO + 2, negrita=True)
            t_tit = f_tit.render(txt_tit, True, (255, 240, 195))
            t_tit_s = f_tit.render(txt_tit, True, (15, 20, 35))
            rc_tit = t_tit.get_rect(center=(ANCHO_MENU // 2, 44))
            pantalla.blit(t_tit_s, (rc_tit.x + 2, rc_tit.y + 2))
            pantalla.blit(t_tit, rc_tit)

            txt_sub = t("sub_opciones")
            f_sub = obtener_fuente_para_texto(txt_sub, categoria="subtitulo", tamano=TAMANO_SUBTITULO - 2)
            t_sub = f_sub.render(txt_sub, True, (215, 230, 255))
            pantalla.blit(t_sub, t_sub.get_rect(center=(ANCHO_MENU // 2, 78)))

            # 3. Barra lateral izquierda (3 botones de secciones)
            botones_sec = [
                ("configuracion", t("configuracion").upper(), rect_btn_sec_cfg),
                ("controles", t("controles").upper(), rect_btn_sec_ctrl),
                ("instrucciones", t("instrucciones").upper(), rect_btn_sec_inst),
            ]

            for sec_id, sec_nom, r_b in botones_sec:
                es_activa = (seccion_opciones_actual == sec_id)
                hov_b = r_b.collidepoint(pos_mouse)

                if es_activa:
                    col_bg = (250, 225, 165)
                    col_brd = (185, 110, 60)
                    col_txt = (45, 30, 15)
                    pygame.draw.rect(pantalla, (140, 80, 40), (r_b.left, r_b.top + 4, r_b.width, r_b.height), border_radius=12)
                    pygame.draw.rect(pantalla, col_bg, (r_b.left, r_b.top, r_b.width, r_b.height - 2), border_radius=12)
                    pygame.draw.rect(pantalla, col_brd, (r_b.left, r_b.top, r_b.width, r_b.height - 2), 3, border_radius=12)
                    # Indicador rombo / gema
                    cy_g = r_b.centery - 1
                    pts_gema = [(r_b.left + 16, cy_g), (r_b.left + 22, cy_g - 6), (r_b.left + 28, cy_g), (r_b.left + 22, cy_g + 6)]
                    pygame.draw.polygon(pantalla, (225, 110, 80), pts_gema)
                    pygame.draw.polygon(pantalla, (150, 60, 30), pts_gema, 1)
                else:
                    col_bg = (38, 52, 82) if hov_b else (28, 38, 62)
                    col_brd = (110, 140, 185) if hov_b else (85, 110, 150)
                    col_txt = (255, 255, 255) if hov_b else (220, 230, 245)
                    pygame.draw.rect(pantalla, (15, 22, 38), (r_b.left, r_b.top + 4, r_b.width, r_b.height), border_radius=12)
                    pygame.draw.rect(pantalla, col_bg, (r_b.left, r_b.top, r_b.width, r_b.height - 2), border_radius=12)
                    pygame.draw.rect(pantalla, col_brd, (r_b.left, r_b.top, r_b.width, r_b.height - 2), 2, border_radius=12)

                r_txt_b = pygame.Rect(r_b.left + (36 if es_activa else 12), r_b.top, r_b.width - (44 if es_activa else 24), r_b.height - 2)
                dibujar_texto_en_rect(pantalla, sec_nom, r_txt_b, categoria="boton", tamano=15, color=col_txt, negrita=True, alineacion="centro")

            # Personajes decorativos en la barra lateral izquierda
            cx_dec, cy_dec = 190, 430
            pygame.draw.ellipse(pantalla, (220, 235, 255), (cx_dec - 80, cy_dec + 45, 160, 24))
            sp_p1_d = cargar_sprites(color_p1).get("quieto")
            sp_p2_d = cargar_sprites(color_p2).get("quieto")
            r_mini_p1 = pygame.Rect(cx_dec - 55, cy_dec, 50, 62)
            r_mini_p2 = pygame.Rect(cx_dec + 5, cy_dec, 50, 62)
            if sp_p1_d:
                pantalla.blit(pygame.transform.scale(sp_p1_d, (50, 62)), r_mini_p1)
                if accesorio_p1:
                    dibujar_accesorio_en_personaje(pantalla, accesorio_p1, sprite_personaje=sp_p1_d, rect_personaje=r_mini_p1, mirando_derecha=True)
            if sp_p2_d:
                pantalla.blit(pygame.transform.scale(sp_p2_d, (50, 62)), r_mini_p2)
                if accesorio_p2:
                    dibujar_accesorio_en_personaje(pantalla, accesorio_p2, sprite_personaje=sp_p2_d, rect_personaje=r_mini_p2, mirando_derecha=True)

            # 4. Panel central grande de color crema
            rect_panel = pygame.Rect(340, 115, 875, 495)
            # Sombra del panel
            pygame.draw.rect(pantalla, (15, 20, 35), (rect_panel.left + 5, rect_panel.top + 5, rect_panel.width, rect_panel.height), border_radius=18)
            # Fondo crema
            pygame.draw.rect(pantalla, (253, 248, 238), rect_panel, border_radius=18)
            # Borde exterior marrón
            pygame.draw.rect(pantalla, (115, 75, 48), rect_panel, 4, border_radius=18)
            # Borde interior coral
            rect_in = pygame.Rect(rect_panel.left + 6, rect_panel.top + 6, rect_panel.width - 12, rect_panel.height - 12)
            pygame.draw.rect(pantalla, (225, 115, 85), rect_in, 2, border_radius=14)

            # Cabecera dentro del panel
            nom_seccion = {
                "configuracion": t("ajustes_generales"),
                "controles": t("controles_teclado"),
                "instrucciones": t("guia_juego"),
            }.get(seccion_opciones_actual, t("opciones"))

            f_p_tit = obtener_fuente_para_texto(nom_seccion, categoria="titulo", tamano=19, negrita=True)
            t_p_tit = f_p_tit.render(nom_seccion, True, (60, 42, 30))
            pantalla.blit(t_p_tit, t_p_tit.get_rect(center=(rect_panel.centerx, rect_panel.top + 28)))
            # Línea divisoria decorativa
            pygame.draw.line(pantalla, (225, 115, 85), (rect_panel.left + 35, rect_panel.top + 48), (rect_panel.right - 35, rect_panel.top + 48), 2)
            pygame.draw.circle(pantalla, (180, 90, 55), (rect_panel.centerx, rect_panel.top + 48), 4)

            # =========================================================================
            # SECCIÓN: CONFIGURACIÓN
            # =========================================================================
            if seccion_opciones_actual == "configuracion":
                # Bloque A: Volumen
                y_vol = rect_panel.top + 60
                txt_vol_b = t("volumen_musica_y_sonido")
                f_bloq = obtener_fuente_para_texto(txt_vol_b, categoria="texto", tamano=15, negrita=True)
                pantalla.blit(f_bloq.render(txt_vol_b, True, (65, 45, 32)), (rect_panel.left + 45, y_vol))

                # Tarjeta contenedora de volumen
                r_card_vol = pygame.Rect(rect_panel.left + 45, y_vol + 24, rect_panel.width - 90, 72)
                pygame.draw.rect(pantalla, (244, 236, 222), r_card_vol, border_radius=12)
                pygame.draw.rect(pantalla, (200, 175, 145), r_card_vol, 2, border_radius=12)

                vol_actual = obtener_volumen()
                cy_v = r_card_vol.centery

                # Botón [-]
                r_menos = pygame.Rect(r_card_vol.left + 25, cy_v - 22, 50, 44)
                hov_m = r_menos.collidepoint(pos_mouse)
                col_bm = (235, 115, 85) if hov_m else (215, 105, 75)
                pygame.draw.rect(pantalla, col_bm, r_menos, border_radius=8)
                pygame.draw.rect(pantalla, (140, 60, 40), r_menos, 2, border_radius=8)
                f_btn_v = obtener_fuente_para_texto("-", categoria="boton", tamano=22, negrita=True)
                pantalla.blit(f_btn_v.render("-", True, (255, 255, 255)), f_btn_v.render("-", True, (255, 255, 255)).get_rect(center=r_menos.center))

                # Barra de volumen
                r_barra_bg = pygame.Rect(r_menos.right + 20, cy_v - 18, 460, 36)
                pygame.draw.rect(pantalla, (40, 46, 62), r_barra_bg, border_radius=8)
                pygame.draw.rect(pantalla, (150, 160, 185), r_barra_bg, 2, border_radius=8)

                # Relleno de la barra (por bloques de 10%)
                bloques = vol_actual // 10
                ancho_bloque = (r_barra_bg.width - 8) / 10.0
                for b in range(bloques):
                    bx = r_barra_bg.left + 4 + int(b * ancho_bloque)
                    bw = int(ancho_bloque) - 3
                    col_b = (255, 150, 70) if b < 4 else ((255, 195, 65) if b < 8 else (255, 225, 95))
                    pygame.draw.rect(pantalla, col_b, (bx, r_barra_bg.top + 4, bw, r_barra_bg.height - 8), border_radius=4)

                # Botón [+]
                r_mas = pygame.Rect(r_barra_bg.right + 20, cy_v - 22, 50, 44)
                hov_p = r_mas.collidepoint(pos_mouse)
                col_bp = (95, 200, 120) if hov_p else (85, 180, 110)
                pygame.draw.rect(pantalla, col_bp, r_mas, border_radius=8)
                pygame.draw.rect(pantalla, (45, 120, 65), r_mas, 2, border_radius=8)
                f_btn_mas = obtener_fuente_para_texto("+", categoria="boton", tamano=20, negrita=True)
                pantalla.blit(f_btn_mas.render("+", True, (255, 255, 255)), f_btn_mas.render("+", True, (255, 255, 255)).get_rect(center=r_mas.center))

                # Porcentaje numérico badge
                r_pct = pygame.Rect(r_mas.right + 20, cy_v - 22, 85, 44)
                pygame.draw.rect(pantalla, (255, 255, 255), r_pct, border_radius=8)
                pygame.draw.rect(pantalla, (180, 155, 125), r_pct, 2, border_radius=8)
                str_pct = f"{vol_actual}%"
                f_pct = obtener_fuente_para_texto(str_pct, categoria="boton", tamano=16, negrita=True)
                pantalla.blit(f_pct.render(str_pct, True, (45, 35, 25)), f_pct.render(str_pct, True, (45, 35, 25)).get_rect(center=r_pct.center))

                # Bloque B: Idioma
                y_idioma = r_card_vol.bottom + 12
                txt_idm_b = t("seleccion_idioma")
                pantalla.blit(f_bloq.render(txt_idm_b, True, (65, 45, 32)), (rect_panel.left + 45, y_idioma))

                r_card_idm = pygame.Rect(rect_panel.left + 45, y_idioma + 24, rect_panel.width - 90, 94)
                pygame.draw.rect(pantalla, (244, 236, 222), r_card_idm, border_radius=12)
                pygame.draw.rect(pantalla, (200, 175, 145), r_card_idm, 2, border_radius=12)

                langs = [
                    ("es", "ESPAÑOL", "Español (Latinoamérica / España)"),
                    ("en", "ENGLISH", "English (United States / UK)"),
                    ("zh", "中文 (CHINO)", "简体中文 (Simplified Chinese)"),
                ]
                w_btn_l = (r_card_idm.width - 60) // 3
                for l_idx, (l_code, l_tit, l_sub) in enumerate(langs):
                    rx_l = r_card_idm.left + 20 + l_idx * (w_btn_l + 10)
                    r_bl = pygame.Rect(rx_l, r_card_idm.top + 11, w_btn_l, 72)
                    es_sel = (idm_act == l_code)
                    hov_l = r_bl.collidepoint(pos_mouse)

                    col_l_bg = (255, 250, 235) if es_sel else ((248, 240, 228) if hov_l else (238, 228, 212))
                    col_l_brd = (225, 110, 80) if es_sel else ((205, 180, 150) if hov_l else (185, 160, 130))
                    pygame.draw.rect(pantalla, col_l_bg, r_bl, border_radius=10)
                    pygame.draw.rect(pantalla, col_l_brd, r_bl, 3 if es_sel else 2, border_radius=10)

                    if es_sel:
                        cx_ck, cy_ck = r_bl.right - 13, r_bl.top + 13
                        pygame.draw.circle(pantalla, (80, 185, 105), (cx_ck, cy_ck), 8)
                        pts_ck = [(cx_ck - 4, cy_ck), (cx_ck - 1, cy_ck + 3), (cx_ck + 4, cy_ck - 3)]
                        pygame.draw.lines(pantalla, (255, 255, 255), False, pts_ck, 2)

                    col_lt = (45, 30, 20) if es_sel else (95, 75, 60)
                    if contiene_caracteres_cjk(l_tit):
                        f_lt = obtener_fuente_para_texto(l_tit, categoria="boton", tamano=16, negrita=True)
                        t_lt = f_lt.render(l_tit, True, col_lt)
                    else:
                        _, t_lt = renderizar_texto_pixamuse(l_tit, 15, col_lt, max_w=r_bl.width - 28)
                    pantalla.blit(t_lt, t_lt.get_rect(center=(r_bl.centerx, r_bl.top + 23)))

                    dibujar_texto_en_rect(pantalla, l_sub, pygame.Rect(r_bl.left + 6, r_bl.top + 36, r_bl.width - 12, 32), categoria="texto", tamano=12, color=(80, 60, 45), alineacion="centro", multiline=True, interlineado=1)

                # Bloque C: Música del Menú
                y_musica = r_card_idm.bottom + 12
                txt_mus_b = t("musica_menu_titulo")
                pantalla.blit(f_bloq.render(txt_mus_b, True, (65, 45, 32)), (rect_panel.left + 45, y_musica))

                r_card_musica = pygame.Rect(rect_panel.left + 45, y_musica + 24, rect_panel.width - 90, 102)
                pygame.draw.rect(pantalla, (244, 236, 222), r_card_musica, border_radius=12)
                pygame.draw.rect(pantalla, (200, 175, 145), r_card_musica, 2, border_radius=12)

                modo_musica_act = obtener_modo_musica_menu()
                opciones_musica = [
                    ("aleatorio", t("modo_aleatorio"), t("desc_aleatorio")),
                    ("caillou", t("modo_caillou"), t("desc_caillou")),
                    ("christmas", t("modo_christmas"), t("desc_christmas")),
                ]
                w_btn_m = (r_card_musica.width - 60) // 3
                for m_idx, (m_code, m_tit, m_sub) in enumerate(opciones_musica):
                    rx_m = r_card_musica.left + 20 + m_idx * (w_btn_m + 10)
                    r_bm = pygame.Rect(rx_m, r_card_musica.top + 10, w_btn_m, 82)
                    es_sel_m = (modo_musica_act == m_code)
                    hov_m = r_bm.collidepoint(pos_mouse)

                    col_m_bg = (255, 250, 235) if es_sel_m else ((248, 240, 228) if hov_m else (238, 228, 212))
                    col_m_brd = (225, 110, 80) if es_sel_m else ((205, 180, 150) if hov_m else (185, 160, 130))
                    pygame.draw.rect(pantalla, col_m_bg, r_bm, border_radius=10)
                    pygame.draw.rect(pantalla, col_m_brd, r_bm, 3 if es_sel_m else 2, border_radius=10)

                    if es_sel_m:
                        cx_ck, cy_ck = r_bm.right - 13, r_bm.top + 13
                        pygame.draw.circle(pantalla, (80, 185, 105), (cx_ck, cy_ck), 8)
                        pts_ck = [(cx_ck - 4, cy_ck), (cx_ck - 1, cy_ck + 3), (cx_ck + 4, cy_ck - 3)]
                        pygame.draw.lines(pantalla, (255, 255, 255), False, pts_ck, 2)

                    col_mt = (45, 30, 20) if es_sel_m else (95, 75, 60)
                    if contiene_caracteres_cjk(m_tit):
                        f_mt = obtener_fuente_para_texto(m_tit, categoria="boton", tamano=16, negrita=True)
                        t_mt = f_mt.render(m_tit, True, col_mt)
                    else:
                        _, t_mt = renderizar_texto_pixamuse(m_tit, 15, col_mt, max_w=r_bm.width - 28)
                    pantalla.blit(t_mt, t_mt.get_rect(center=(r_bm.centerx, r_bm.top + 20)))

                    r_sub_m = pygame.Rect(r_bm.left + 4, r_bm.top + 34, r_bm.width - 8, 44)
                    dibujar_texto_en_rect(pantalla, m_sub, r_sub_m, categoria="texto", tamano=15, color=(80, 60, 45), alineacion="centro", multiline=True, interlineado=2, padding=1)

                # Nota al pie de ajustes (agrandada y más legible con sombra suave)
                txt_not = t("cambios_guardados_auto")
                f_not = obtener_fuente_para_texto(txt_not, categoria="texto", tamano=14, negrita=True)
                pantalla.blit(f_not.render(txt_not, True, (245, 235, 220)), (rect_panel.left + 51, rect_panel.bottom - 32))
                pantalla.blit(f_not.render(txt_not, True, (55, 38, 25)), (rect_panel.left + 50, rect_panel.bottom - 33))

            # =========================================================================
            # SECCIÓN: CONTROLES
            # =========================================================================
            elif seccion_opciones_actual == "controles":
                w_pj_card = (rect_panel.width - 60) // 2
                h_pj_card = 356
                y_pj_top = rect_panel.top + 60

                # --- TARJETA JUGADOR 1 ---
                r_card_p1 = pygame.Rect(rect_panel.left + 22, y_pj_top, w_pj_card, h_pj_card)
                pygame.draw.rect(pantalla, (244, 238, 226), r_card_p1, border_radius=14)
                pygame.draw.rect(pantalla, (124, 210, 240), r_card_p1, 3, border_radius=14)

                r_head_p1 = pygame.Rect(r_card_p1.left + 14, r_card_p1.top + 10, r_card_p1.width - 28, 34)
                pygame.draw.rect(pantalla, (124, 231, 255), r_head_p1, border_radius=8)
                pygame.draw.rect(pantalla, (50, 40, 30), r_head_p1, 2, border_radius=8)
                tit_head_p1 = f"{t('jugador_1').upper()}  (WASD)"
                dibujar_texto_en_rect(pantalla, tit_head_p1, r_head_p1, categoria="boton", tamano=16, color=(35, 30, 25), negrita=True, padding=2)

                filas_p1 = [
                    (t("accion_moverse"), ["A", "D"], t("desc_moverse")),
                    (t("accion_saltar"), ["W"], t("desc_saltar")),
                    (t("accion_nadar"), ["W", "S"], t("desc_nadar_p1")),
                    (t("accion_empujar"), ["A", "D"], t("desc_empujar")),
                    (t("accion_linterna"), ["E", "F", "ESP"], t("desc_linterna")),
                ]
                for f_idx, (accion, teclas, desc) in enumerate(filas_p1):
                    yf = r_card_p1.top + 52 + f_idx * 58
                    # Línea 1: Nombre de la acción a la izquierda y teclas alineadas a la derecha
                    f_act = obtener_fuente_para_texto(accion, categoria="boton", tamano=15, negrita=True)
                    pantalla.blit(f_act.render(accion, True, (45, 32, 20)), (r_card_p1.left + 16, yf + 3))

                    xk = r_card_p1.right - 14
                    for tk in reversed(teclas):
                        kw = 56 if len(tk) > 2 else 38
                        xk -= kw
                        rk = pygame.Rect(xk, yf, kw, 30)
                        _dibujar_icono_tecla(pantalla, tk, rk, activo=True, tamano_fuente=15)
                        xk -= 6

                    # Línea 2: Texto descriptivo amplio y claro (completamente separado sin superposición)
                    f_dsc = obtener_fuente_para_texto(desc, categoria="texto", tamano=14, negrita=False)
                    pantalla.blit(f_dsc.render(f"• {desc}", True, (80, 60, 45)), (r_card_p1.left + 16, yf + 33))

                    if f_idx < len(filas_p1) - 1:
                        pygame.draw.line(pantalla, (230, 218, 200), (r_card_p1.left + 14, yf + 54), (r_card_p1.right - 14, yf + 54), 1)

                # --- TARJETA JUGADOR 2 ---
                r_card_p2 = pygame.Rect(r_card_p1.right + 16, y_pj_top, w_pj_card, h_pj_card)
                pygame.draw.rect(pantalla, (244, 238, 226), r_card_p2, border_radius=14)
                pygame.draw.rect(pantalla, (180, 140, 255), r_card_p2, 3, border_radius=14)

                r_head_p2 = pygame.Rect(r_card_p2.left + 14, r_card_p2.top + 10, r_card_p2.width - 28, 34)
                pygame.draw.rect(pantalla, (180, 140, 255), r_head_p2, border_radius=8)
                pygame.draw.rect(pantalla, (50, 40, 30), r_head_p2, 2, border_radius=8)
                tit_head_p2 = f"{t('jugador_2').upper()}  ({t('flechas_direccion')})"
                dibujar_texto_en_rect(pantalla, tit_head_p2, r_head_p2, categoria="boton", tamano=16, color=(35, 30, 25), negrita=True, padding=2)

                filas_p2 = [
                    (t("accion_moverse"), ["←", "→"], t("desc_moverse")),
                    (t("accion_saltar"), ["↑"], t("desc_saltar")),
                    (t("accion_nadar"), ["↑", "↓"], t("desc_nadar_p2")),
                    (t("accion_empujar"), ["←", "→"], t("desc_empujar")),
                    (t("accion_linterna"), ["L", "ENT"], t("desc_linterna")),
                ]
                for f_idx, (accion, teclas, desc) in enumerate(filas_p2):
                    yf = r_card_p2.top + 52 + f_idx * 58
                    f_act = obtener_fuente_para_texto(accion, categoria="boton", tamano=15, negrita=True)
                    pantalla.blit(f_act.render(accion, True, (45, 32, 20)), (r_card_p2.left + 16, yf + 3))

                    xk = r_card_p2.right - 14
                    for tk in reversed(teclas):
                        kw = 56 if len(tk) > 2 else 38
                        xk -= kw
                        rk = pygame.Rect(xk, yf, kw, 30)
                        _dibujar_icono_tecla(pantalla, tk, rk, activo=True, tamano_fuente=15)
                        xk -= 6

                    f_dsc = obtener_fuente_para_texto(desc, categoria="texto", tamano=14, negrita=False)
                    pantalla.blit(f_dsc.render(f"• {desc}", True, (80, 60, 45)), (r_card_p2.left + 16, yf + 33))

                    if f_idx < len(filas_p2) - 1:
                        pygame.draw.line(pantalla, (230, 218, 200), (r_card_p2.left + 14, yf + 54), (r_card_p2.right - 14, yf + 54), 1)

                # Fila inferior: Tecla R y Menú ESC (Agrandadas y legibles)
                r_inf_ctrl = pygame.Rect(rect_panel.left + 22, r_card_p1.bottom + 10, rect_panel.width - 44, 52)
                pygame.draw.rect(pantalla, (238, 230, 215), r_inf_ctrl, border_radius=10)
                pygame.draw.rect(pantalla, (195, 170, 140), r_inf_ctrl, 2, border_radius=10)

                rk_r = pygame.Rect(r_inf_ctrl.left + 18, r_inf_ctrl.top + 9, 42, 34)
                _dibujar_icono_tecla(pantalla, "R", rk_r, activo=False, tamano_fuente=16)
                txt_r = t("reiniciar_nivel_act")
                f_r = obtener_fuente_para_texto(txt_r, categoria="texto", tamano=15, negrita=True)
                pantalla.blit(f_r.render(txt_r, True, (55, 40, 30)), (rk_r.right + 12, r_inf_ctrl.top + 16))

                rk_esc = pygame.Rect(r_inf_ctrl.centerx + 20, r_inf_ctrl.top + 9, 58, 34)
                _dibujar_icono_tecla(pantalla, "ESC", rk_esc, activo=False, tamano_fuente=16)
                txt_esc = t("pausa_volver_menu")
                f_esc = obtener_fuente_para_texto(txt_esc, categoria="texto", tamano=15, negrita=True)
                pantalla.blit(f_esc.render(txt_esc, True, (55, 40, 30)), (rk_esc.right + 12, r_inf_ctrl.top + 16))

            # =========================================================================
            # SECCIÓN: INSTRUCCIONES
            # =========================================================================
            elif seccion_opciones_actual == "instrucciones":
                w_c = (rect_panel.width - 60) // 2
                h_c = 202

                tarjetas_inst = [
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

                for idx_t, (tit_t, lines_t, tipo_ico) in enumerate(tarjetas_inst):
                    col_idx = idx_t % 2
                    row_idx = idx_t // 2
                    x_tc = rect_panel.left + 20 + col_idx * (w_c + 20)
                    y_tc = rect_panel.top + 58 + row_idx * (h_c + 12)
                    rtc = pygame.Rect(x_tc, y_tc, w_c, h_c)

                    pygame.draw.rect(pantalla, (246, 240, 228), rtc, border_radius=12)
                    pygame.draw.rect(pantalla, (215, 175, 140), rtc, 2, border_radius=12)

                    # Encabezado con título centrado y multilínea para que nunca se desborde
                    r_head_t = pygame.Rect(rtc.left + 8, rtc.top + 8, rtc.width - 16, 36)
                    pygame.draw.rect(pantalla, (235, 218, 195), r_head_t, border_radius=6)
                    dibujar_texto_en_rect(pantalla, tit_t, r_head_t, categoria="boton", tamano=13, color=(55, 38, 25), negrita=True, multiline=True, padding=2, alineacion="centro")

                    # Recuadro de ilustración con los sprites reales del juego
                    r_box_ico = pygame.Rect(rtc.right - 56, rtc.top + 46, 48, 48)
                    pygame.draw.rect(pantalla, (232, 222, 205), r_box_ico, border_radius=8)
                    pygame.draw.rect(pantalla, (180, 150, 120), r_box_ico, 1, border_radius=8)

                    cx_i, cy_i = r_box_ico.center
                    if tipo_ico == "llave_puerta":
                        spr_ico = _obtener_icono_instruccion("llave", 40, 44)
                        if spr_ico:
                            pantalla.blit(spr_ico, spr_ico.get_rect(center=r_box_ico.center))
                    elif tipo_ico == "caja_boton":
                        spr_ico = _obtener_icono_instruccion("caja", 44, 42)
                        if spr_ico:
                            pantalla.blit(spr_ico, spr_ico.get_rect(center=r_box_ico.center))
                    elif tipo_ico == "soga_salto":
                        pts_soga = [(cx_i - 15, cy_i - 8), (cx_i - 5, cy_i + 8), (cx_i + 5, cy_i - 6), (cx_i + 15, cy_i + 8)]
                        pygame.draw.lines(pantalla, (160, 110, 60), False, pts_soga, 3)
                        pygame.draw.circle(pantalla, (124, 231, 255), (cx_i - 13, cy_i - 8), 5)
                        pygame.draw.circle(pantalla, (180, 140, 255), (cx_i + 13, cy_i + 8), 5)
                    elif tipo_ico == "submarino":
                        spr_ico = _obtener_icono_instruccion("buceo", 44, 40)
                        if spr_ico:
                            pantalla.blit(spr_ico, spr_ico.get_rect(center=r_box_ico.center))

                    for l_num, line_txt in enumerate(lines_t):
                        yf_l = rtc.top + 50 + l_num * 36
                        bx = rtc.left + 14
                        by = yf_l + 6
                        pygame.draw.rect(pantalla, (215, 175, 140), (bx + 1, by + 1, 4, 4))
                        pygame.draw.rect(pantalla, (65, 45, 30), (bx, by, 4, 4))

                        clean_txt = line_txt.lstrip("•- \t")
                        f_lin = obtener_fuente_para_texto(clean_txt, categoria="dialogos", tamano=18, negrita=True)
                        ts_lin = f_lin.render(clean_txt, True, (45, 32, 20))
                        pantalla.blit(ts_lin, (rtc.left + 24, yf_l))
                        pantalla.blit(ts_lin, (rtc.left + 25, yf_l))

            # 5. Botón Volver al Menú (mundos/boton-volver)
            hov_vcfg = btn_volver_config.collidepoint(pos_mouse)
            spr_vcfg_norm = _obtener_boton_volver("normal", idm_act)
            spr_vcfg_hov = _obtener_boton_volver("hover", idm_act)
            spr_vcfg = spr_vcfg_hov if (hov_vcfg and spr_vcfg_hov) else spr_vcfg_norm
            if spr_vcfg:
                pantalla.blit(spr_vcfg, btn_volver_config)
            else:
                col_v = (255, 255, 255) if hov_vcfg else (242, 234, 222)
                pygame.draw.rect(pantalla, col_v, btn_volver_config, border_radius=10)
                pygame.draw.rect(pantalla, (185, 155, 125), btn_volver_config, width=2, border_radius=10)
                dibujar_texto_en_rect(pantalla, t("volver_al_menu"), btn_volver_config, categoria="boton", tamano=TAMANO_BOTONES, color=(60, 45, 35), padding=6)

        elif estado_actual == ESTADO_CREDITOS:
            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()
            titulo = fuente_pixel_titulo.render("CREDITOS", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            cred = fuente_texto.render("Desarrollado para Pico Park Fan Project", True, (200, 200, 200))
            pantalla.blit(cred, cred.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2)))

            # Botón Volver al Menú (mundos/boton-volver)
            hov_vcr = btn_volver_creditos.collidepoint(pos_mouse)
            spr_vcr_norm = _obtener_boton_volver("normal", idm_act)
            spr_vcr_hov = _obtener_boton_volver("hover", idm_act)
            spr_vcr = spr_vcr_hov if (hov_vcr and spr_vcr_hov) else spr_vcr_norm
            if spr_vcr:
                pantalla.blit(spr_vcr, btn_volver_creditos)

        elif estado_actual in (ESTADO_SELECCION_NIVEL, ESTADO_SELECCION_MUNDO):
            pos_mouse = pygame.mouse.get_pos()
            dibujar_menu_niveles(
                pantalla,
                mundo_seleccionado,
                niveles_desbloqueados,
                pos_mouse,
                fuentes_menu,
                es_admin=es_partida_admin(partida_actual_nombre, partida_actual_id),
            )

            # Capturar fondo limpio de los iconos antes de dibujarlos sobre la pantalla
            fondo_btn_config_niveles = pantalla.subsurface(rect_btn_config_niveles).copy()
            fondo_btn_casa_niveles = pantalla.subsurface(rect_btn_casa_niveles).copy()
            fondo_btn_x_niveles = pantalla.subsurface(rect_btn_x_niveles).copy()

            # Iconos superiores de Selección de Niveles: Configuración, Casita (Menú Principal) y X (Salir)
            hov_cfg = rect_btn_config_niveles.collidepoint(pos_mouse)
            spr_cfg_dib = spr_confign_hover if (hov_cfg and spr_confign_hover) else spr_confign_normal
            if spr_cfg_dib:
                pantalla.blit(spr_cfg_dib, rect_btn_config_niveles)

            hov_casa = rect_btn_casa_niveles.collidepoint(pos_mouse)
            spr_c_dib = spr_casa_hover if (hov_casa and spr_casa_hover) else spr_casa_normal
            if spr_c_dib:
                pantalla.blit(spr_c_dib, rect_btn_casa_niveles)

            hov_xn = rect_btn_x_niveles.collidepoint(pos_mouse)
            spr_xn_dib = spr_xn_hover if (hov_xn and spr_xn_hover) else spr_xn_normal
            if spr_xn_dib:
                pantalla.blit(spr_xn_dib, rect_btn_x_niveles)

        if estado_actual != ESTADO_SELECCION_NIVEL:
            pos_mouse = pygame.mouse.get_pos()
            fondo_btn_x_main = pantalla.subsurface(rect_btn_x).copy()
            hov_x = rect_btn_x.collidepoint(pos_mouse)
            spr_x_dib = spr_x_hover if (hov_x and spr_x_hover) else spr_x_normal
            if spr_x_dib: pantalla.blit(spr_x_dib, rect_btn_x)

        pygame.display.flip()

    detener_musica()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    from errores import ejecutar_protegido
    ejecutar_protegido(main)