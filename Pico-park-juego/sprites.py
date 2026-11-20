import os
import sys
import weakref
import pygame

from rutas import ruta_recurso

ANCHO, ALTO = 1280, 720
FPS = 60
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

COLOR_JUGADOR1 = "Celeste"
COLOR_JUGADOR2 = "Violeta"

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)
RUTA_BASE = ruta_recurso("Sprites", "Personajes")
RUTA_BOTONES = ruta_recurso("Sprites", "Botones")
RUTA_CAJA = os.path.join(DIRECTORIO_ACTUAL, "caja.png")
RUTA_OBJETOS = ruta_recurso("Sprites", "Objetos")

ESTADOS_PERSONAJE = [
    "quieto", "muerto",
    "caminar-1", "caminar-2", "caminar-3", "caminar-4",
    "caminar-5", "caminar-6", "caminar-7", "caminar-8",
    "saltar",
    "caminar-empujar-1", "caminar-empujar-2", "caminar-empujar-3", "caminar-empujar-4",
    "caminar-empujar-5", "caminar-empujar-6", "caminar-empujar-7", "caminar-empujar-8",
    "saltar-empujar", "pestañear"
]


_CACHE_BOTONES = {}
_CACHE_BOTONES_ESCALADOS = {}
_CACHE_BOTONES_ACLARADOS = weakref.WeakKeyDictionary()
_CACHE_MARCOS_BOTONES = {}
_CACHE_BOTONES_PERSONALIZADOS = {}
_MAPA_BOTONES = None
# Ancho máximo al que se retiene un botón en caché (4x el tamaño de dibujo de 272 px).
ANCHO_MAX_BOTON = 1088


def _obtener_mapa_botones():
    global _MAPA_BOTONES
    if _MAPA_BOTONES is None:
        _MAPA_BOTONES = {}
        if os.path.isdir(RUTA_BOTONES):
            for raiz, _, archivos in os.walk(RUTA_BOTONES):
                for arch in archivos:
                    clave = arch.lower()
                    if clave not in _MAPA_BOTONES:
                        _MAPA_BOTONES[clave] = os.path.join(raiz, arch)
    return _MAPA_BOTONES


def cargar_boton(nombre):
    """
    Carga un sprite de botón desde la carpeta Sprites/Botones o cualquiera de sus subcarpetas.
    Permite especificar nombres con o sin subcarpeta (ej. 'boton-volver.png' o 'mundos/boton-volver.png').
    Utiliza caché en memoria para evitar accesos repetitivos a disco y escaneos de carpetas.
    """
    if nombre in _CACHE_BOTONES:
        return _CACHE_BOTONES[nombre]

    def _cargar(ruta_archivo):
        try:
            img = pygame.image.load(ruta_archivo)
            try:
                img = img.convert_alpha()
            except pygame.error:
                pass
            # Los botones se dibujan como máximo a ~272 px de ancho. Si el PNG es
            # más grande que ANCHO_MAX_BOTON se reduce al cargarlo para no retener
            # en caché superficies de decenas de MB que nunca se usan a ese tamaño.
            w, h = img.get_size()
            if w > ANCHO_MAX_BOTON:
                nh = max(1, round(h * ANCHO_MAX_BOTON / w))
                img = pygame.transform.smoothscale(img, (ANCHO_MAX_BOTON, nh))
            return img
        except (FileNotFoundError, pygame.error):
            return None

    # Normalizar separadores de ruta
    nombre_norm = nombre.replace("/", os.sep).replace("\\", os.sep)
    ruta = os.path.join(RUTA_BOTONES, nombre_norm)
    if os.path.isfile(ruta):
        res = _cargar(ruta)
        if res:
            _CACHE_BOTONES[nombre] = res
            return res

    mapa = _obtener_mapa_botones()
    solo_nombre = os.path.basename(nombre_norm).lower()
    if solo_nombre in mapa:
        res = _cargar(mapa[solo_nombre])
        if res:
            _CACHE_BOTONES[nombre] = res
            return res

    _CACHE_BOTONES[nombre] = None
    return None


def cargar_boton_escalado(nombre, w, h):
    """
    Carga y escala suavemente un botón oficial del proyecto con proporciones exactas.
    Cachea en memoria la superficie escalada para evitar recalcular transformaciones pesadas.
    """
    clave = (nombre, w, h)
    if clave in _CACHE_BOTONES_ESCALADOS:
        return _CACHE_BOTONES_ESCALADOS[clave]
    img = cargar_boton(nombre)
    if img is not None:
        scaled = pygame.transform.smoothscale(img, (w, h))
        _CACHE_BOTONES_ESCALADOS[clave] = scaled
        return scaled
    _CACHE_BOTONES_ESCALADOS[clave] = None
    return None


def aclarar_boton(surf, factor=45):
    """
    Genera una versión iluminada / más clara del sprite del botón para el estado hover.
    Mantiene intactos los bordes y la transparencia.
    Cachea el resultado de forma segura con referencias débiles para evitar colisiones de memoria.
    """
    if surf is None:
        return None
    try:
        subdict = _CACHE_BOTONES_ACLARADOS.get(surf)
        if subdict is not None and factor in subdict:
            return subdict[factor]
    except TypeError:
        subdict = None

    brillante = surf.copy()
    capa = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    capa.fill((factor, factor, factor, 0))
    brillante.blit(capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    try:
        if subdict is None:
            subdict = {}
            _CACHE_BOTONES_ACLARADOS[surf] = subdict
        subdict[factor] = brillante
    except TypeError:
        pass
    return brillante


def generar_marco_boton(sprite_nombre, w_target, h_target):
    """
    Genera una base o marco de botón perfectamente escalado a partir de un sprite oficial
    (ej. 'mundos/boton-volver.png', 'Menu/salir.png', 'mundos/boton-cargar.png'),
    conservando bordes pixel art redondeados, biselados y relieves 3D sin el texto central.
    """
    clave = (sprite_nombre, w_target, h_target)
    if clave in _CACHE_MARCOS_BOTONES:
        return _CACHE_MARCOS_BOTONES[clave]

    base = cargar_boton(sprite_nombre)
    if not base:
        return None

    bw, bh = base.get_size()
    # Si la relación de aspecto objetivo coincide aproximadamente con la original,
    # escalar suavemente sin 9-slice para preservar el 100% de la fidelidad pixel art original.
    if abs((w_target / max(1, h_target)) - (bw / max(1, bh))) < 0.08:
        scaled = pygame.transform.smoothscale(base, (w_target, h_target))
        _CACHE_MARCOS_BOTONES[clave] = scaled
        return scaled

    cap_w = 900
    if cap_w >= bw // 2:
        cap_w = bw // 4

    left_cap = base.subsurface((0, 0, cap_w, bh))
    right_cap = base.subsurface((bw - cap_w, 0, cap_w, bh))
    mid_sample = base.subsurface((cap_w - 50, 0, 20, bh))

    native_mid_w = int((w_target / h_target) * bh) - 2 * cap_w
    if native_mid_w < 20:
        native_mid_w = 20

    native_total_w = 2 * cap_w + native_mid_w
    native_surf = pygame.Surface((native_total_w, bh), pygame.SRCALPHA)
    native_surf.blit(left_cap, (0, 0))
    mid_stretched = pygame.transform.scale(mid_sample, (native_mid_w, bh))
    native_surf.blit(mid_stretched, (cap_w, 0))
    native_surf.blit(right_cap, (cap_w + native_mid_w, 0))

    scaled = pygame.transform.smoothscale(native_surf, (w_target, h_target))
    _CACHE_MARCOS_BOTONES[clave] = scaled
    return scaled


COLORES_INTERIORES_BOTONES = {
    # Menu Principal
    "Menu/jugar.png": (155, 255, 124),
    "jugar.png": (155, 255, 124),
    "Menu/jugar-preapretado.png": (142, 237, 115),
    "jugar-preapretado.png": (142, 237, 115),
    "Menu/jugar-apretado.png": (124, 211, 103),
    "jugar-apretado.png": (124, 211, 103),

    "Menu/personajes.png": (122, 230, 255),
    "personajes.png": (122, 230, 255),
    "Menu/personajes-preapretado.png": (114, 214, 242),
    "personajes-preapretado.png": (114, 214, 242),
    "Menu/personajes-apretado.png": (102, 190, 223),
    "personajes-apretado.png": (102, 190, 223),

    "Menu/opciones.png": (255, 243, 123),
    "opciones.png": (255, 243, 123),
    "Menu/opciones-preapretado.png": (240, 226, 113),
    "opciones-preapretado.png": (240, 226, 113),
    "Menu/opciones-apretado.png": (220, 200, 97),
    "opciones-apretado.png": (220, 200, 97),

    "Menu/salir.png": (253, 158, 98),
    "salir.png": (253, 158, 98),
    "Menu/salir-preapretado.png": (240, 147, 89),
    "salir-preapretado.png": (240, 147, 89),
    "Menu/salir-apretado.png": (221, 131, 78),
    "salir-apretado.png": (221, 131, 78),

    # Botones Volver
    "mundos/boton-volver.png": (212, 212, 212),
    "boton-volver.png": (212, 212, 212),
    "mundos/boton-volver-semiapretado.png": (200, 200, 200),
    "boton-volver-semiapretado.png": (200, 200, 200),
    "mundos/boton-volver-apretado.png": (181, 181, 181),
    "boton-volver-apretado.png": (181, 181, 181),

    # Botones Cargar
    "mundos/boton-cargar.png": (155, 255, 124),
    "boton-cargar.png": (155, 255, 124),
    "mundos/boton-cargar-semiapretado.png": (142, 237, 115),
    "boton-cargar-semiapretado.png": (142, 237, 115),
    "mundos/boton-cargar-apretado.png": (124, 211, 103),
    "boton-cargar-apretado.png": (124, 211, 103),

    # Botones Modo de Juego
    "Menu/boton-continuar-cargar....png": (155, 255, 124),
    "boton-continuar-cargar....png": (155, 255, 124),
    "Menu/boton-continuar-cargar...-semiapretado.png": (142, 237, 115),
    "boton-continuar-cargar...-semiapretado.png": (142, 237, 115),
    "Menu/boton-continuar-cargar...-apretado.png": (124, 211, 103),
    "boton-continuar-cargar...-apretado.png": (124, 211, 103),

    "mundos/boton-nueva-partida-reiniciar....png": (254, 137, 134),
    "boton-nueva-partida-reiniciar....png": (254, 137, 134),
    "mundos/boton-nueva-partida-reiniciar...-semiapretado.png": (242, 126, 123),
    "boton-nueva-partida-reiniciar...-semiapretado.png": (242, 126, 123),
    "mundos/boton-nueva-partida-reiniciar...-apretado.png": (225, 114, 112),
    "boton-nueva-partida-reiniciar...-apretado.png": (225, 114, 112),

    # Botones Nueva Partida (Lista)
    "mundos/boton-nueva-partida.png": (255, 159, 99),
    "boton-nueva-partida.png": (255, 159, 99),
    "mundos/boton-nueva-partida-semiapretado.png": (242, 148, 91),
    "boton-nueva-partida-semiapretado.png": (242, 148, 91),
    "mundos/boton-nueva-partida-apretado.png": (223, 132, 79),
    "boton-nueva-partida-apretado.png": (223, 132, 79),

    # Botones Cancelar (Modales)
    "Menu/boton-cancelar.png": (212, 212, 212),
    "boton-cancelar.png": (212, 212, 212),
    "Menu/boton-cancelar-semiapretado.png": (200, 200, 200),
    "boton-cancelar-semiapretado.png": (200, 200, 200),
    "Menu/boton-cancelar-apretado.png": (181, 181, 181),
    "boton-cancelar-apretado.png": (181, 181, 181),

    # Ventanas / Diálogos / Fin de nivel
    "Ventanas/boton-guardar-y-salir.png": (155, 255, 124),
    "boton-guardar-y-salir.png": (155, 255, 124),
    "Ventanas/boton-guardar-y-salir-semiapretado.png": (142, 237, 115),
    "boton-guardar-y-salir-semiapretado.png": (142, 237, 115),
    "Ventanas/boton-guardar-y-salir-apretado.png": (124, 211, 103),
    "boton-guardar-y-salir-apretado.png": (124, 211, 103),

    "Ventanas/boton-menu.png": (255, 159, 99),
    "boton-menu.png": (255, 159, 99),
    "Ventanas/boton-menu-semiapretado.png": (242, 148, 91),
    "boton-menu-semiapretado.png": (242, 148, 91),
    "Ventanas/boton-menu-apretado.png": (223, 132, 79),
    "boton-menu-apretado.png": (223, 132, 79),

    "Ventanas/boton-reiniciar.png": (255, 159, 99),
    "boton-reiniciar.png": (255, 159, 99),
    "Ventanas/boton-reiniciar-semiapretado.png": (242, 148, 91),
    "boton-reiniciar-semiapretado.png": (242, 148, 91),
    "Ventanas/boton-reiniciar-apretado.png": (223, 132, 79),
    "boton-reiniciar-apretado.png": (223, 132, 79),

    "Ventanas/boton-siguiente.png": (255, 159, 99),
    "boton-siguiente.png": (255, 159, 99),
    "Ventanas/boton-siguiente-semiapretado.png": (242, 148, 91),
    "boton-siguiente-semiapretado.png": (242, 148, 91),
    "Ventanas/boton-siguiente-apretado.png": (223, 132, 79),
    "boton-siguiente-apretado.png": (223, 132, 79),

    "Ventanas/boton-salir-sin-guardar.png": (254, 137, 134),
    "boton-salir-sin-guardar.png": (254, 137, 134),
    "Ventanas/boton-salir-sin-guardar-semiapretado.png": (242, 126, 123),
    "Menu/boton-salir-sin-guardar-semiapretado.png": (242, 126, 123),
    "boton-salir-sin-guardar-semiapretado.png": (242, 126, 123),
    "Ventanas/boton-salir-sin-guardar-apretado.png": (225, 114, 112),
    "boton-salir-sin-guardar-apretado.png": (225, 114, 112),
}


def limpiar_cache_botones():
    """Limpia el caché interno de botones personalizados."""
    _CACHE_BOTONES_PERSONALIZADOS.clear()
    _CACHE_MARCOS_BOTONES.clear()
    _CACHE_BOTONES_ESCALADOS.clear()
    _CACHE_BOTONES_ACLARADOS.clear()


def generar_boton_con_texto(sprite_base, w, h, texto=None, color_texto=(60, 45, 30), tamano_fuente=14, offset_y=0, idioma=None):
    """
    Construye un botón temático de alta fidelidad basado en los recursos de Sprites/Botones,
    con el texto especificado centrado y nítido.
    Soporta caracteres especiales como Ñ/ñ con tildes pixel art y CJK/Unicode.
    """
    if idioma is None:
        try:
            from configuracion import obtener_idioma
            idioma = obtener_idioma()
        except Exception:
            idioma = "es"

    clave = (sprite_base, w, h, texto, color_texto, tamano_fuente, offset_y, idioma)
    if clave in _CACHE_BOTONES_PERSONALIZADOS:
        return _CACHE_BOTONES_PERSONALIZADOS[clave]

    base_norm = str(sprite_base).replace("\\", "/")
    from fuentes import contiene_caracteres_cjk, obtener_fuente_cjk, obtener_fuente_boton

    # 1. Determinar si el texto requiere tipografía CJK (chino) o tipografía pixel art oficial (español/inglés)
    es_cjk = contiene_caracteres_cjk(texto) or (idioma == "zh" and any(ord(ch) > 127 for ch in str(texto)))
    if str(texto).strip().upper() in ("ESPAÑOL", "ESPANOL", "ENGLISH") or idioma in ("es", "en"):
        if not contiene_caracteres_cjk(texto):
            es_cjk = False

    # Si el idioma es español y el texto coincide con el texto horneado del sprite, retornar el sprite escalado original
    base_lower = base_norm.lower()
    t_clean = str(texto).strip().upper() if texto else ""
    if idioma == "es":
        es_nativo = False
        if "volver" in base_lower and t_clean == "VOLVER": es_nativo = True
        elif "jugar" in base_lower and t_clean == "JUGAR": es_nativo = True
        elif "personajes" in base_lower and t_clean == "PERSONAJES": es_nativo = True
        elif "opciones" in base_lower and t_clean == "OPCIONES": es_nativo = True
        elif "salir" in base_lower and t_clean == "SALIR": es_nativo = True
        elif "cargar" in base_lower and t_clean == "CARGAR": es_nativo = True
        elif "cancelar" in base_lower and t_clean == "CANCELAR": es_nativo = True
        elif "nueva-partida" in base_lower and t_clean == "NUEVA PARTIDA": es_nativo = True
        elif "reiniciar" in base_lower and t_clean == "REINICIAR": es_nativo = True
        elif "siguiente" in base_lower and t_clean == "SIGUIENTE": es_nativo = True
        elif "menu" in base_lower and t_clean in ("MENÚ", "MENU"): es_nativo = True
        if es_nativo:
            res_btn = cargar_boton_escalado(sprite_base, w, h)
            if res_btn:
                _CACHE_BOTONES_PERSONALIZADOS[clave] = res_btn
                return res_btn

    marco = generar_marco_boton(sprite_base, w, h)
    if not marco:
        return None

    surf = marco.copy()
    if texto:
        # Limpieza interior segura si el marco contiene texto original horneado
        base_key = os.path.basename(base_norm)
        col_interior = COLORES_INTERIORES_BOTONES.get(base_norm) or COLORES_INTERIORES_BOTONES.get(base_key)
        if col_interior:
            is_apr = "apretado" in base_lower and "pre" not in base_lower and "semi" not in base_lower
            is_semi = "semi" in base_lower or "pre" in base_lower
            shift_clear = int(h * 0.10) if is_apr else (int(h * 0.05) if is_semi else 0)
            h_bisel = max(6, int(h * 0.28))
            pad_lat = max(4, int(w * 0.03))
            pad_top = max(4, int(h * 0.08)) + shift_clear
            h_clear = max(10, h - max(4, int(h * 0.08)) - h_bisel)
            rect_int = pygame.Rect(pad_lat, pad_top, w - 2 * pad_lat, h_clear)
            pygame.draw.rect(surf, col_interior, rect_int)

        curr_sz = tamano_fuente
        if es_cjk:
            f_sys = obtener_fuente_cjk(curr_sz, negrita=True)
            txt_surf = f_sys.render(str(texto), True, color_texto)
            while txt_surf.get_width() > w - 16 and curr_sz > 8:
                curr_sz -= 1
                f_sys = obtener_fuente_cjk(curr_sz, negrita=True)
                txt_surf = f_sys.render(str(texto), True, color_texto)
        else:
            def _render_latin(sz):
                f = obtener_fuente_boton(sz, tamano_fallback=sz, idioma="es")
                if any(ch in "ÑñÁÉÍÓÚáéíóú" for ch in str(texto)):
                    txt_limpio = (
                        str(texto).replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                                  .replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    )
                    ancho_t, alto_t = f.size(txt_limpio.replace("Ñ", "N").replace("ñ", "n"))
                    t_s = pygame.Surface((ancho_t, alto_t + 4), pygame.SRCALPHA)
                    curr_x = 0
                    for ch in txt_limpio:
                        if ch in ("Ñ", "ñ"):
                            letra = f.render("N" if ch == "Ñ" else "n", True, color_texto)
                            t_s.blit(letra, (curr_x, 3))
                            lw = letra.get_width()
                            pygame.draw.rect(t_s, color_texto, (curr_x + 2, 0, 3, 2))
                            pygame.draw.rect(t_s, color_texto, (curr_x + 5, 1, 3, 2))
                            curr_x += lw
                        else:
                            letra = f.render(ch, True, color_texto)
                            t_s.blit(letra, (curr_x, 3))
                            curr_x += letra.get_width()
                    return f, t_s
                else:
                    return f, f.render(str(texto), True, color_texto)

            f_lat, txt_surf = _render_latin(curr_sz)
            while txt_surf.get_width() > w - 16 and curr_sz > 8:
                curr_sz -= 1
                f_lat, txt_surf = _render_latin(curr_sz)

        rect_txt = txt_surf.get_rect(center=(w // 2, (h - 4) // 2 + offset_y))
        if color_texto == (255, 255, 255) and ("salir" in base_norm.lower() or "borrar" in str(texto).lower()):
            f_somb = f_sys if es_cjk else f_lat
            somb_surf = f_somb.render(str(texto), True, (127, 49, 19))
            surf.blit(somb_surf, rect_txt.move(1, 1))
        surf.blit(txt_surf, rect_txt)

    _CACHE_BOTONES_PERSONALIZADOS[clave] = surf
    return surf



def precargar_botones_comunes():
    """
    Precarga y prepara en memoria todos los sprites de botones utilizados
    en menús, configuración, selección de niveles, HUD y pantallas de juego.
    Garantiza que el primer fotograma de cualquier pantalla muestre todos los
    botones correspondientes desde el primer momento, sin demoras ni apariciones tardías.
    """
    # 1. Botones del Menú Principal y Diálogos estándar (272, 80)
    botones_menu_272_80 = [
        "jugar.png", "jugar-preapretado.png", "jugar-apretado.png",
        "personajes.png", "personajes-preapretado.png", "personajes-apretado.png",
        "opciones.png", "opciones-preapretado.png", "opciones-apretado.png",
        "salir.png", "salir-preapretado.png", "salir-apretado.png",
        "mundos/boton-nueva-partida.png", "mundos/boton-nueva-partida-semiapretado.png", "mundos/boton-nueva-partida-apretado.png",
        "Ventanas/boton-reiniciar.png", "Ventanas/boton-reiniciar-semiapretado.png", "Ventanas/boton-reiniciar-apretado.png",
        "Ventanas/boton-siguiente.png", "Ventanas/boton-siguiente-semiapretado.png", "Ventanas/boton-siguiente-apretado.png",
        "Ventanas/boton-menu.png", "Ventanas/boton-menu-semiapretado.png", "Ventanas/boton-menu-apretado.png",
    ]
    for b in botones_menu_272_80:
        s = cargar_boton_escalado(b, 272, 80)
        if s:
            aclarar_boton(s)

    # 2. Botones de HUD superior (44, 52)
    botones_hud_44_52 = [
        "boton-x.png", "boton-x-semiapretado.png", "boton-x-apretado.png",
        "HUD/boton-x.png", "HUD/boton-x-semiapretado.png", "HUD/boton-x-apretado.png",
        "boton-casa.png", "boton-casa-semiapretado.png", "boton-casa-apretado.png",
        "HUD/boton-casa.png", "HUD/boton-casa-semiapretado.png", "HUD/boton-casa-apretado.png",
        "boton-configuracion.png", "boton-configuracion-semiapretado.png", "boton-configuracion-apretado.png",
        "HUD/boton-configuracion.png", "HUD/boton-configuracion-semiapretado.png", "HUD/boton-configuracion-apretado.png",
        "boton-reiniciar-icono.png", "boton-reiniciar-icono-semiapretado.png", "boton-reiniciar-icono-apretado.png",
    ]
    for b in botones_hud_44_52:
        s = cargar_boton_escalado(b, 44, 52)
        if s:
            aclarar_boton(s)

    # 3. Botones de Configuración (Volumen y Cerrar)
    botones_cfg = [
        ("HUD/boton-bajar-volumen.png", 42, 50),
        ("HUD/boton-bajar-volumen-semiapretado.png", 42, 50),
        ("HUD/boton-bajar-volumen-apretado.png", 42, 50),
        ("HUD/boton-subir-volumen.png", 42, 50),
        ("HUD/boton-subir-volumen-semiapretado.png", 42, 50),
        ("HUD/boton-subir-volumen-apretado.png", 42, 50),
        ("HUD/boton-x.png", 29, 34),
        ("HUD/boton-x-semiapretado.png", 29, 34),
        ("HUD/boton-x-apretado.png", 29, 34),
    ]
    for b, w, h in botones_cfg:
        s = cargar_boton_escalado(b, w, h)
        if s:
            aclarar_boton(s)

    # 4. Botones de Volver y Navegación (238, 70)
    botones_nav_238_70 = [
        "mundos/boton-volver.png", "mundos/boton-volver-semiapretado.png", "mundos/boton-volver-apretado.png",
        "Ventanas/boton-menu.png", "Ventanas/boton-menu-semiapretado.png", "Ventanas/boton-menu-apretado.png",
        "mundos/boton-nueva-partida.png", "mundos/boton-nueva-partida-semiapretado.png", "mundos/boton-nueva-partida-apretado.png",
    ]
    for b in botones_nav_238_70:
        s = cargar_boton_escalado(b, 238, 70)
        if s:
            aclarar_boton(s)

    # 5. Botones de Selección de Modo (425, 100)
    botones_modo_425_100 = [
        "Menu/boton-continuar-cargar....png", "Menu/boton-continuar-cargar...-semiapretado.png", "Menu/boton-continuar-cargar...-apretado.png",
        "mundos/boton-nueva-partida-reiniciar....png", "mundos/boton-nueva-partida-reiniciar...-semiapretado.png", "mundos/boton-nueva-partida-reiniciar...-apretado.png",
    ]
    for b in botones_modo_425_100:
        s = cargar_boton_escalado(b, 425, 100)
        if s:
            aclarar_boton(s)

    # 6. Botones de Guardar / Salir y Tarjetas
    botones_guardar = [
        ("mundos/boton-cargar.png", 129, 38),
        ("mundos/boton-cargar-semiapretado.png", 129, 38),
        ("mundos/boton-cargar-apretado.png", 129, 38),
        ("Ventanas/boton-guardar-y-salir.png", 260, 64),
        ("Ventanas/boton-guardar-y-salir-semiapretado.png", 260, 64),
        ("Ventanas/boton-guardar-y-salir-apretado.png", 260, 64),
        ("Ventanas/boton-salir-sin-guardar.png", 260, 64),
        ("Menu/boton-salir-sin-guardar-semiapretado.png", 260, 64),
        ("Ventanas/boton-salir-sin-guardar-apretado.png", 260, 64),
        ("Menu/boton-cancelar.png", 260, 64),
        ("Menu/boton-cancelar-semiapretado.png", 260, 64),
        ("Menu/boton-cancelar-apretado.png", 260, 64),
        ("Ventanas/boton-guardar-y-salir.png", 200, 52),
        ("Ventanas/boton-guardar-y-salir-semiapretado.png", 200, 52),
        ("Ventanas/boton-guardar-y-salir-apretado.png", 200, 52),
        ("Ventanas/boton-salir-sin-guardar.png", 200, 52),
        ("Menu/boton-salir-sin-guardar-semiapretado.png", 200, 52),
        ("Ventanas/boton-salir-sin-guardar-apretado.png", 200, 52),
        ("Menu/boton-cancelar.png", 200, 52),
        ("Menu/boton-cancelar-semiapretado.png", 200, 52),
        ("Menu/boton-cancelar-apretado.png", 200, 52),
    ]
    for b, w, h in botones_guardar:
        s = cargar_boton_escalado(b, w, h)
        if s:
            aclarar_boton(s)

    # 7. Controles tutoriales (54, 54) y (32, 32)
    botones_ctrl = [
        "Controles/boton-w.png", "Controles/boton-a.png", "Controles/boton-s.png", "Controles/boton-d.png",
        "Controles/boton-arriba.png", "Controles/boton-abajo.png", "Controles/boton-izquierda.png", "Controles/boton-derecha.png",
    ]
    for b in botones_ctrl:
        cargar_boton_escalado(b, 54, 54)
        cargar_boton_escalado(b, 32, 32)


def animar_pulsacion_boton(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None, spr_normal=None):
    """
    Reproduce una pulsación física real en 4 etapas usando los tres sprites de cada botón:
    1. Normal -> Semiapretado: al hacer clic, pasa rápidamente al sprite semiapretado (~55 ms).
    2. Semiapretado -> Apretado: inmediatamente después pasa al sprite apretado (~60 ms),
       dando la sensación de que el botón se hunde físicamente.
    3. Mientras mantenga presionado el clic: permanece visualmente apretado de forma continua.
    4. Al soltar: realiza una transición rápida de regreso (semiapretado ~45 ms -> normal)
       y ejecuta la acción una sola vez por clic.
    Garantiza dimensiones 1:1 estrictas para impedir cualquier deformación o agrandamiento.
    """
    target_size = (rect.width, rect.height)
    if spr_semi is not None and spr_semi.get_size() != target_size:
        spr_semi = pygame.transform.smoothscale(spr_semi, target_size)
    if spr_apretado is not None and spr_apretado.get_size() != target_size:
        spr_apretado = pygame.transform.smoothscale(spr_apretado, target_size)
    if spr_normal is not None and spr_normal.get_size() != target_size:
        spr_normal = pygame.transform.smoothscale(spr_normal, target_size)

    def _limpiar():
        if fondo_limpio is not None:
            if isinstance(fondo_limpio, (tuple, list)):
                pygame.draw.rect(pantalla, fondo_limpio[:3], rect)
            elif isinstance(fondo_limpio, pygame.Surface):
                fw, fh = fondo_limpio.get_size()
                if (fw, fh) == (rect.width, rect.height):
                    pantalla.blit(fondo_limpio, rect)
                elif fw >= rect.right and fh >= rect.bottom:
                    pantalla.blit(fondo_limpio, rect, rect)
                else:
                    pantalla.blit(fondo_limpio, rect)
        else:
            ancho_p, alto_p = pantalla.get_size()
            x_muestra = max(0, rect.left - 4)
            y_muestra = max(0, min(alto_p - 1, rect.centery))
            col_bg = pantalla.get_at((x_muestra, y_muestra))[:3]
            pygame.draw.rect(pantalla, col_bg, rect)

    # 1. Transición rápida al sprite semiapretado
    if spr_semi:
        _limpiar()
        pantalla.blit(spr_semi, rect)
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(55)

    # 2. Transición inmediata al sprite apretado (hundido físico)
    if spr_apretado:
        _limpiar()
        pantalla.blit(spr_apretado, rect)
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(60)

    # 3. Mantener apretado mientras el botón del mouse continúe presionado
    reloj_anim = pygame.time.Clock()
    fue_soltado_adentro = True

    while pygame.mouse.get_pressed()[0]:
        pygame.event.pump()
        pos_m = pygame.mouse.get_pos()
        esta_adentro = rect.collidepoint(pos_m)

        _limpiar()
        if esta_adentro:
            if spr_apretado:
                pantalla.blit(spr_apretado, rect)
            fue_soltado_adentro = True
        else:
            if spr_normal:
                pantalla.blit(spr_normal, rect)
            elif spr_semi:
                pantalla.blit(spr_semi, rect)
            fue_soltado_adentro = False

        pygame.display.flip()
        reloj_anim.tick(60)

    # 4. Al soltar: transición rápida de regreso hacia normal
    if fue_soltado_adentro:
        if spr_semi:
            _limpiar()
            pantalla.blit(spr_semi, rect)
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.delay(45)

        _limpiar()
        if spr_normal:
            pantalla.blit(spr_normal, rect)
        pygame.display.flip()
        pygame.event.pump()

        # Descartar eventos de MOUSEBUTTONUP generados por este clic
        for _ in pygame.event.get(pygame.MOUSEBUTTONUP):
            pass

        return True
    else:
        _limpiar()
        if spr_normal:
            pantalla.blit(spr_normal, rect)
        pygame.display.flip()
        pygame.event.pump()
        for _ in pygame.event.get(pygame.MOUSEBUTTONUP):
            pass
        return False



def aplicar_tinta(imagen_base, color_rgb):
    """
    Pinta el personaje base con el color seleccionado manteniendo ojos, bordes y transparencia.
    """
    if color_rgb is None or not isinstance(color_rgb, (tuple, list)) or color_rgb[:3] == (255, 255, 255):
        return imagen_base

    img_tintada = imagen_base.copy()
    superficie_color = pygame.Surface(img_tintada.get_size(), flags=pygame.SRCALPHA)
    superficie_color.fill((*color_rgb[:3], 255))
    img_tintada.blit(superficie_color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return img_tintada


_CACHE_SPRITES_PERSONAJES = {}


def cargar_sprites(nombre_color="Celeste"):
    """
    Carga los sprites originales del personaje según la carpeta de color.
    Si falta algún frame, intenta obtenerlo de la carpeta Blanco o quieto como respaldo.
    Utiliza caché en memoria para no recargar desde disco en cada solicitud.
    """
    if nombre_color in _CACHE_SPRITES_PERSONAJES:
        return _CACHE_SPRITES_PERSONAJES[nombre_color]

    ruta_carpeta = os.path.join(RUTA_BASE, nombre_color)
    sprites = {}

    for estado in ESTADOS_PERSONAJE:
        img_cargada = None
        posibles_rutas = [
            os.path.join(ruta_carpeta, f"{estado}.png"),
            os.path.join(ruta_carpeta, "quieto.png"),
            os.path.join(RUTA_BASE, "Blanco", f"{estado}.png"),
            os.path.join(DIRECTORIO_ACTUAL, f"{estado}.png"),
            ruta_recurso("Sprites", f"{estado}.png")
        ]

        for r in posibles_rutas:
            if os.path.isfile(r):
                try:
                    img_cargada = pygame.image.load(r)
                    try:
                        img_cargada = img_cargada.convert_alpha()
                    except pygame.error:
                        pass
                    break
                except pygame.error:
                    pass

        if img_cargada is not None:
            sprites[estado] = pygame.transform.scale(img_cargada, (ANCHO_PERSONAJE, ALTO_PERSONAJE))
        else:
            s = pygame.Surface((ANCHO_PERSONAJE, ALTO_PERSONAJE), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255), (10, 10, 50, 65), border_radius=10)
            pygame.draw.rect(s, (0, 0, 0), (10, 10, 50, 65), 3, border_radius=10)
            pygame.draw.rect(s, (0, 0, 0), (20, 25, 10, 10))
            pygame.draw.rect(s, (0, 0, 0), (40, 25, 10, 10))
            sprites[estado] = s

    _CACHE_SPRITES_PERSONAJES[nombre_color] = sprites
    return sprites


_CACHE_SPRITE_CAJA = {}
_CACHE_SPRITE_LLAVE = None


def cargar_sprite_caja(tamano):
    if tamano in _CACHE_SPRITE_CAJA:
        return _CACHE_SPRITE_CAJA[tamano]
    rutas = [
        ruta_recurso("Sprites", "Objetos", "caja.png"),
        ruta_recurso("Sprites", "Caja", "caja.png"),
        RUTA_CAJA,
    ]
    for ruta in rutas:
        if os.path.isfile(ruta):
            try:
                img = pygame.image.load(ruta).convert_alpha()
                res = pygame.transform.scale(img, (tamano, tamano))
                _CACHE_SPRITE_CAJA[tamano] = res
                return res
            except pygame.error:
                pass

    sprite = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
    sprite.fill((139, 69, 19))
    _CACHE_SPRITE_CAJA[tamano] = sprite
    return sprite


def cargar_sprite_llave():
    global _CACHE_SPRITE_LLAVE
    if _CACHE_SPRITE_LLAVE is not None:
        return _CACHE_SPRITE_LLAVE

    ruta_llave = os.path.join(RUTA_OBJETOS, "llave.png")
    if os.path.isfile(ruta_llave):
        try:
            img = pygame.image.load(ruta_llave).convert_alpha()
            _CACHE_SPRITE_LLAVE = pygame.transform.scale(img, (25, 46))
            return _CACHE_SPRITE_LLAVE
        except pygame.error:
            pass

    surface = pygame.Surface((25, 46), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 215, 0), (12, 12), 10)
    pygame.draw.rect(surface, (255, 215, 0), (10, 12, 5, 30))
    pygame.draw.rect(surface, (255, 215, 0), (15, 32, 6, 4))
    pygame.draw.rect(surface, (255, 215, 0), (15, 38, 6, 4))
    _CACHE_SPRITE_LLAVE = surface
    return surface


_CACHE_SPRITES_PUERTA = {}


def cargar_sprites_puerta(tamano=(146, 180)):
    """
    Carga y cachea los sprites del Portal (animación en bucle de energía verde)
    y del Candado (secuencia de desbloqueo de 4 fases).
    Retorna un diccionario estructurado con:
      - 'portal': lista de 3 superficies [p1, p2, p3] con la energía verde animada
      - 'candado': lista de 4 superficies [c1, c2, c3, c4] con las fases del candado
      - 'abierta': superficie activa del portal desbloqueado
      - 'cerrada': superficie inicial del portal bloqueado con candado cerrado
    """
    clave = tamano
    if clave in _CACHE_SPRITES_PUERTA:
        return _CACHE_SPRITES_PUERTA[clave]

    ruta_portal_dir = ruta_recurso("Sprites", "Objetos", "Portal")
    if not os.path.isdir(ruta_portal_dir):
        ruta_portal_dir = os.path.join(RUTA_OBJETOS, "Portal")

    portales = []
    candados = []

    # 1. Cargar portales 1, 2, 3 (bucle de energía verde)
    for i in (1, 2, 3):
        r = os.path.join(ruta_portal_dir, f"portal_{i}.png")
        if os.path.isfile(r):
            try:
                img = pygame.image.load(r).convert_alpha()
                if img.get_size() != tamano:
                    img = pygame.transform.scale(img, tamano)
                portales.append(img)
            except Exception:
                pass

    # 2. Cargar candados 1, 2, 3, 4 (secuencia de desbloqueo)
    # El candado tiene el mismo tamaño total que el portal (tamano) y sus cadenas se ajustan
    # proporcionalmente para apoyarse en los pilares de piedra sin sobresalir hacia afuera.
    factor_candado = 0.87
    cx_orig, cy_orig = 330, 467
    for i in (1, 2, 3, 4):
        r = os.path.join(ruta_portal_dir, f"candado_{i}.png")
        if os.path.isfile(r):
            try:
                img_raw = pygame.image.load(r).convert_alpha()
                ow, oh = img_raw.get_size()
                nw, nh = int(ow * factor_candado), int(oh * factor_candado)
                scaled_tmp = pygame.transform.smoothscale(img_raw, (nw, nh))

                surf_full = pygame.Surface((ow, oh), pygame.SRCALPHA)
                dx = cx_orig - int(cx_orig * factor_candado)
                dy = cy_orig - int(cy_orig * factor_candado)
                surf_full.blit(scaled_tmp, (dx, dy))

                img = pygame.transform.scale(surf_full, tamano)
                candados.append(img)
            except Exception:
                pass

    # Diseños procedimentales de respaldo si faltaran archivos
    if len(portales) < 3:
        portales = []
        for i in range(3):
            s = pygame.Surface(tamano, pygame.SRCALPHA)
            w, h = tamano
            pygame.draw.rect(s, (88, 88, 88), (0, 0, w, h), border_radius=w // 2)
            pygame.draw.rect(s, (120, 120, 120), (4, 4, w - 8, h - 8), border_radius=(w - 8) // 2)
            col_v = (95, 215, 60) if i == 0 else ((120, 235, 75) if i == 1 else (80, 195, 50))
            pygame.draw.ellipse(s, col_v, (8, 12, w - 16, h - 20))
            portales.append(s)

    if len(candados) < 4:
        candados = []
        for i in range(4):
            s = pygame.Surface(tamano, pygame.SRCALPHA)
            w, h = tamano
            if i == 0:
                pygame.draw.line(s, (215, 175, 40), (4, 15), (w - 4, h - 15), 3)
                pygame.draw.line(s, (215, 175, 40), (w - 4, 15), (4, h - 15), 3)
                pygame.draw.circle(s, (245, 205, 50), (w // 2, h // 2), 10)
            elif i == 1:
                pygame.draw.circle(s, (255, 225, 70), (w // 2, h // 2), 8)
            elif i == 2:
                pygame.draw.circle(s, (215, 175, 40), (w // 2, h - 20), 6)
            else:
                pygame.draw.circle(s, (180, 140, 30), (w // 2, h - 10), 3)
            candados.append(s)

    abierta = portales[0]
    cerrada = portales[0].copy()
    cerrada.blit(candados[0], (0, 0))

    resultado = {
        "portal": portales,
        "candado": candados,
        "abierta": abierta,
        "cerrada": cerrada,
    }
    _CACHE_SPRITES_PUERTA[clave] = resultado
    return resultado


def actualizar_temporizadores(p):
    esta_quieto = (p["vel_x"] == 0) and p["en_suelo"]
    if esta_quieto and not p["empujando"] and not p["muerto"]:
        p["tiempo_quieto"] += 1
        frames_15_seg = 15 * FPS
        frames_10_seg = 10 * FPS
        duracion_pestañeo = int(0.5 * FPS)

        if p["tiempo_quieto"] >= frames_15_seg:
            tiempo_post_15 = p["tiempo_quieto"] - frames_15_seg
            p["mostrando_pestañeo"] = (tiempo_post_15 % frames_10_seg) < duracion_pestañeo
        else:
            p["mostrando_pestañeo"] = False
    else:
        p["tiempo_quieto"] = 0
        p["mostrando_pestañeo"] = False


def obtener_estado(p):
    if p["muerto"]:
        return "muerto"

    if not p["en_suelo"]:
        if p["empujando"]:
            return "saltar-empujar"
        return "saltar"

    if p["empujando"]:
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1
            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1
        return f"caminar-empujar-{p['frame_animacion']}"

    if p["vel_x"] != 0 or p.get("moviendo", False):
        p["contador_anim"] += 1
        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1
            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1
        return f"caminar-{p['frame_animacion']}"

    if p["mostrando_pestañeo"]:
        return "pestañear"

    p["frame_animacion"] = 1
    p["contador_anim"] = 0
    return "quieto"


def dibujar_personaje(pantalla, p, zona_agua=None):
    actualizar_temporizadores(p)
    estado = obtener_estado(p)
    p["estado"] = estado
    sprite_base = p["sprites"].get(estado, p["sprites"]["quieto"])

    col = p.get("color")
    if col is not None and col[:3] != (255, 255, 255):
        sprite = aplicar_tinta(sprite_base, col)
    else:
        sprite = sprite_base

    if p["vel_x"] > 0:
        p["mirando_derecha"] = True
    elif p["vel_x"] < 0:
        p["mirando_derecha"] = False

    if not p["mirando_derecha"]:
        sprite = pygame.transform.flip(sprite, True, False)

    if p.get("equipo_buceo"):
        # Ocultar completamente las piernas y los pies del personaje debajo del equipo
        sprite_a_dibujar = sprite.copy()
        w_s, h_s = sprite_a_dibujar.get_size()
        y_corte = int(h_s * 0.72)
        for y_px in range(y_corte, h_s):
            for x_px in range(w_s):
                sprite_a_dibujar.set_at((x_px, y_px), (0, 0, 0, 0))
    else:
        sprite_a_dibujar = sprite

    rect_sprite = sprite_a_dibujar.get_rect(center=p["hitbox"].center)
    pantalla.blit(sprite_a_dibujar, rect_sprite)
    dibujar_accesorio_en_personaje(pantalla, p, sprite, rect_sprite)

    # Accesorio exclusivo y obligatorio del Mundo 3: Equipo de buceo permanente
    if p.get("equipo_buceo"):
        surf_goggles, surf_amarillo = cargar_partes_equipo_buceo()
        if surf_goggles and surf_amarillo:
            mirando_der = p.get("mirando_derecha", True)
            top_cabeza, eye_cy = calcular_anclaje_sprite(sprite)

            # 1. Antiparras de buceo (lentes): centradas respecto de la cabeza y los ojos
            by_g = rect_sprite.top + int(round(eye_cy - 22))
            bx_g = rect_sprite.centerx - surf_goggles.get_width() // 2
            s_g = surf_goggles if mirando_der else pygame.transform.flip(surf_goggles, True, False)

            # 2. Parte amarilla (base del submarino): ubicada en la zona inferior, debajo de los lentes
            y_amarillo = by_g + surf_goggles.get_height() - 2
            x_amarillo = rect_sprite.centerx - surf_amarillo.get_width() // 2
            s_amarillo = surf_amarillo if mirando_der else pygame.transform.flip(surf_amarillo, True, False)

            pantalla.blit(s_amarillo, (x_amarillo, y_amarillo))
            pantalla.blit(s_g, (bx_g, by_g))

    if zona_agua is not None and p.get("en_agua", False):
        sprite_agua = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        sprite_agua.fill((0, 100, 180, 70))
        sprite_agua.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        clip_anterior = pantalla.get_clip()
        pantalla.set_clip(pygame.Rect(zona_agua.left, zona_agua.top, zona_agua.width, pantalla.get_height() - zona_agua.top))
        pantalla.blit(sprite_agua, rect_sprite)
        pantalla.set_clip(clip_anterior)


_ACCESORIOS_REGISTRADOS = [
    {"id": "Ninguno", "nombre": "Ninguno"},
    {"id": "Corona", "nombre": "Corona"},
    {"id": "Sombrero", "nombre": "Sombrero"},
    {"id": "Gorro Azul", "nombre": "Gorro Azul"},
    {"id": "Gorro Celeste", "nombre": "Gorro Celeste"},
    {"id": "Duende", "nombre": "Duende"},
    {"id": "Papá Noel", "nombre": "Papá Noel"},
    {"id": "Ángel", "nombre": "Ángel"},
    {"id": "Hoja", "nombre": "Hoja"},
    {"id": "Rulo", "nombre": "Rulo"},
    {"id": "Popó", "nombre": "Popó"},
    {"id": "Pelo Arcoíris", "nombre": "Pelo Arcoíris"},
    {"id": "Gorro con Ratón", "nombre": "Gorro con Ratón"},
    {"id": "Chucky", "nombre": "Chucky"},
    {"id": "Orejas de Conejo", "nombre": "Orejas de Conejo"},
    {"id": "Among Us", "nombre": "Among Us"},
    {"id": "Argentina", "nombre": "Argentina"},
    {"id": "Bigote", "nombre": "Bigote"},
    {"id": "Diablo", "nombre": "Diablo"},
    {"id": "Elegante", "nombre": "Elegante"},
    {"id": "EXE", "nombre": "EXE"},
    {"id": "Gorra urbana dorada", "nombre": "Gorra urbana dorada"},
    {"id": "Gorra urbana plateada", "nombre": "Gorra urbana plateada"},
    {"id": "Kenny", "nombre": "Kenny"},
    {"id": "Kyle", "nombre": "Kyle"},
    {"id": "Moño Bi", "nombre": "Moño Bi"},
    {"id": "Moño G", "nombre": "Moño G"},
    {"id": "Moño L", "nombre": "Moño L"},
    {"id": "Moño trans", "nombre": "Moño trans"},
    {"id": "Nerd", "nombre": "Nerd"},
    {"id": "Tatoo", "nombre": "Tatoo"},
]


def obtener_accesorios_disponibles(color_personaje=None):
    """
    Retorna la lista completa de todos los accesorios registrados en el juego.
    Conserva todas las opciones de forma independiente (incluyendo ambos gorritos:
    Gorro Celeste y Gorro Azul) para ambos personajes, asegurando que ninguno pierda
    opciones y que cada accesorio se pueda seleccionar, equipar y desequipar individualmente.
    """
    return list(_ACCESORIOS_REGISTRADOS)


_CACHE_ACCESORIOS = {}


CARPETA_ACCESORIOS = os.path.normpath(ruta_recurso("Sprites", "Accesorios"))

# Mapeo centralizado de archivos para carga automática transparente
NOMBRES_ARCHIVOS_ACCESORIOS = {
    "Corona": ["corona.png"],
    "Sombrero": ["sombrero.png"],
    "Gorro Azul": ["gorro_azul.png"],
    "Gorro Celeste": ["gorro_celeste.png"],
    "Duende": ["duende.png"],
    "Papá Noel": ["papa_noel.png"],
    "Ángel": ["angel.png"],
    "Hoja": ["hoja.png"],
    "Rulo": ["rulo.png"],
    "Popó": ["popo.png", "caca.png"],
    "Pelo Arcoíris": ["arcoiris.png"],
    "Gorro con Ratón": ["gorro_con_raton.png"],
    "Chucky": ["chucky.png"],
    "Orejas de Conejo": ["orejas_conejo.png"],
    "Among Us": ["among-us.png", "among_us.png"],
    "Argentina": ["argentina.png"],
    "Bigote": ["bigote.png"],
    "Diablo": ["diablo.png"],
    "Elegante": ["elegante.png"],
    "EXE": ["exe.png", "EXE.png"],
    "Gorra urbana dorada": ["gorra-urbana-dorada.png", "gorra_urbana_dorada.png"],
    "Gorra urbana plateada": ["gorra-urbana-plateada.png", "gorra_urbana_plateada.png"],
    "Kenny": ["kenny.png"],
    "Kyle": ["kyle.png"],
    "Moño Bi": ["moño-bi.png", "mo\u00f1o-bi.png", "moño_bi.png", "mono-bi.png", "mono_bi.png"],
    "Moño G": ["moño-g.png", "mo\u00f1o-g.png", "moño_g.png", "mono-g.png", "mono_g.png"],
    "Moño L": ["moño-l.png", "mo\u00f1o-l.png", "moño_l.png", "mono-l.png", "mono_l.png"],
    "Moño trans": ["moño-trans.png", "mo\u00f1o-trans.png", "moño_trans.png", "mono-trans.png", "mono_trans.png"],
    "Nerd": ["nerd.png"],
    "Tatoo": ["tatoo.png", "tattoo.png"],
}

# Metadatos de posicionamiento y tamaño nativo para escala 70x85
METADATA_ACCESORIOS = {
    "Corona": {"offset": (21, -8), "size": (28, 18)},
    "Sombrero": {"offset": (21, -18), "size": (28, 28)},
    "Gorro Azul": {"offset": (21, -8), "size": (28, 18)},
    "Gorro Celeste": {"offset": (21, -8), "size": (28, 18)},
    "Duende": {"offset": (4, -12), "size": (46, 21)},
    "Papá Noel": {"offset": (3, -10.5), "size": (49, 75)},
    "Ángel": {"offset": (-2.5, -7), "size": (52, 78)},
    "Hoja": {"offset": (21, -17), "size": (28, 28)},
    "Rulo": {"offset": (28, -8), "size": (18, 18)},
    "Popó": {"offset": (26.5, -8), "size": (21, 18)},
    "Pelo Arcoíris": {"offset": (0, -17), "size": (70, 32)},
    "Gorro con Ratón": {"offset": (13.5, -21), "size": (42, 32)},
    "Chucky": {"offset": (14, 0.5), "size": (46, 53)},
    "Orejas de Conejo": {"offset": (12, -22), "size": (46, 32)},
    "Among Us": {"offset": (10, 21), "size": (64, 36)},
    "Argentina": {"offset": (1, 22), "size": (68, 11)},
    "Bigote": {"offset": (19, 45), "size": (46, 13)},
    "Diablo": {"offset": (-11, -24), "size": (72, 103)},
    "Elegante": {"offset": (14, -30), "size": (64, 105)},
    "EXE": {"offset": (11, 26), "size": (62, 26)},
    "Gorra urbana dorada": {"offset": (-7, -10), "size": (76, 79)},
    "Gorra urbana plateada": {"offset": (-7, -10), "size": (76, 79)},
    "Kenny": {"offset": (-4, -9), "size": (78, 62)},
    "Kyle": {"offset": (-4, -20), "size": (78, 58)},
    "Moño Bi": {"offset": (38, -6), "size": (26, 21)},
    "Moño G": {"offset": (38, -6), "size": (26, 21)},
    "Moño L": {"offset": (38, -6), "size": (26, 21)},
    "Moño trans": {"offset": (38, -6), "size": (26, 21)},
    "Nerd": {"offset": (11, 27), "size": (62, 24)},
    "Tatoo": {"offset": (11, 20), "size": (62, 35)},
}


_CACHE_ANCLAJES = {}


def calcular_anclaje_sprite(sprite):
    """
    Calcula dinámicamente el anclaje de la cabeza y de los ojos para cualquier frame
    o animación del personaje. Retorna (top_cabeza, eye_cy).
    """
    if sprite in _CACHE_ANCLAJES:
        return _CACHE_ANCLAJES[sprite]

    w, h = sprite.get_size()
    top_y = None
    eye_ys = []

    for y in range(h):
        for x in range(w):
            c = sprite.get_at((x, y))
            if c.a > 30:
                if top_y is None:
                    top_y = y
                if y < h * 0.65 and c.r < 55 and c.g < 55 and c.b < 55:
                    eye_ys.append(y)

    if top_y is None:
        top_y = 0
    eye_cy = (sum(eye_ys) / len(eye_ys)) if eye_ys else (top_y + 39.0)

    res = (top_y, eye_cy)
    _CACHE_ANCLAJES[sprite] = res
    return res


_SURF_ACCESORIO_BUCEO = None
_SURF_BUCEO_GOGGLES = None
_SURF_BUCEO_AMARILLO = None


def cargar_partes_equipo_buceo():
    """
    Carga el equipo de buceo original (buceo_m3.png) dividiéndolo en sus dos componentes:
    1. Las antiparras de buceo con esnórquel (ojos / rostro).
    2. El accesorio amarillo de buceo (base del submarino, ubicado en la zona inferior debajo de los lentes).
    """
    global _SURF_BUCEO_GOGGLES, _SURF_BUCEO_AMARILLO
    if _SURF_BUCEO_GOGGLES is not None and _SURF_BUCEO_AMARILLO is not None:
        return _SURF_BUCEO_GOGGLES, _SURF_BUCEO_AMARILLO
    posibles = [
        os.path.join(CARPETA_ACCESORIOS, "especiales", "buceo_m3.png"),
        os.path.join(CARPETA_ACCESORIOS, "buceo_m3.png"),
    ]
    for r in posibles:
        if os.path.isfile(r):
            try:
                raw_b = pygame.image.load(r).convert_alpha()
                w_b, h_b = raw_b.get_size()
                corte_y = int(round(h_b * 0.70))
                goggles_raw = raw_b.subsurface((0, 0, w_b, corte_y))
                yellow_raw = raw_b.subsurface((0, corte_y, w_b, h_b - corte_y))
                _SURF_BUCEO_GOGGLES = pygame.transform.scale(goggles_raw, (78, 50))
                _SURF_BUCEO_AMARILLO = pygame.transform.scale(yellow_raw, (70, 20))
                return _SURF_BUCEO_GOGGLES, _SURF_BUCEO_AMARILLO
            except Exception:
                pass
    return None, None


def cargar_accesorio_buceo():
    global _SURF_ACCESORIO_BUCEO
    if _SURF_ACCESORIO_BUCEO is not None:
        return _SURF_ACCESORIO_BUCEO
    posibles = [
        os.path.join(CARPETA_ACCESORIOS, "especiales", "buceo_m3.png"),
        os.path.join(CARPETA_ACCESORIOS, "buceo_m3.png"),
    ]
    for r in posibles:
        if os.path.isfile(r):
            try:
                img = pygame.image.load(r)
                try:
                    img = img.convert_alpha()
                except pygame.error:
                    pass
                img = pygame.transform.scale(img, (78, 68))
                _SURF_ACCESORIO_BUCEO = img
                return _SURF_ACCESORIO_BUCEO
            except Exception:
                pass
    return None


def recargar_accesorios():
    """Limpia la caché de accesorios para recargar imágenes del disco inmediatamente."""
    global _SURF_ACCESORIO_BUCEO, _SURF_BUCEO_GOGGLES, _SURF_BUCEO_AMARILLO
    _CACHE_ACCESORIOS.clear()
    _SURF_ACCESORIO_BUCEO = None
    _SURF_BUCEO_GOGGLES = None
    _SURF_BUCEO_AMARILLO = None


def agregar_contorno_pixel_art(surf, color_contorno=(65, 45, 30)):
    """
    Agrega un contorno sutil de 1 píxel estilo pixel art alrededor del sprite
    para que destaque perfectamente sobre fondos claros (fondo crema de tarjetas, vestuario, etc.).
    """
    w, h = surf.get_size()
    res = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surf, threshold=30)
    surf_mask = mask.to_surface(setcolor=color_contorno, unsetcolor=(0, 0, 0, 0))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        res.blit(surf_mask, (1 + dx, 1 + dy))
    res.blit(surf, (1, 1))
    return res


ACCESORIOS_CON_CONTORNO = {
    "Orejas de Conejo",
    "Ángel",
    "Papá Noel",
    "Gorro con Ratón",
    "Gorro Celeste",
}


def cargar_accesorio(id_accesorio):
    if not id_accesorio or id_accesorio == "Ninguno":
        return None
    if id_accesorio in _CACHE_ACCESORIOS:
        return _CACHE_ACCESORIOS[id_accesorio]

    # 1. Búsqueda prioritaria en la carpeta centralizada Sprites/Accesorios
    nombres_candidatos = NOMBRES_ARCHIVOS_ACCESORIOS.get(
        id_accesorio,
        [f"{id_accesorio.lower().replace(' ', '_')}.png", f"{id_accesorio.lower()}.png", f"{id_accesorio}.png"]
    )
    for nombre_archivo in nombres_candidatos:
        ruta = os.path.join(CARPETA_ACCESORIOS, nombre_archivo)
        if not os.path.isfile(ruta):
            if os.path.isdir(CARPETA_ACCESORIOS):
                target_norm = nombre_archivo.lower().replace("-", "_").replace("ñ", "n")
                for f_disk in os.listdir(CARPETA_ACCESORIOS):
                    if f_disk.lower().replace("-", "_").replace("ñ", "n") == target_norm:
                        ruta = os.path.join(CARPETA_ACCESORIOS, f_disk)
                        break

        if os.path.isfile(ruta):
            try:
                surf = pygame.image.load(ruta)
                try:
                    surf = surf.convert_alpha()
                except pygame.error:
                    pass
                # Recorte automático si la imagen tiene márgenes transparentes (canvas extendido)
                bbox = surf.get_bounding_rect()
                if 0 < bbox.w < surf.get_width() or 0 < bbox.h < surf.get_height():
                    surf = surf.subsurface(bbox).copy()

                meta = METADATA_ACCESORIOS.get(id_accesorio)
                if meta and "size" in meta and surf.get_size() != meta["size"]:
                    surf = pygame.transform.scale(surf, meta["size"])
                _CACHE_ACCESORIOS[id_accesorio] = surf
                return surf
            except Exception:
                pass

    return None


def dibujar_accesorio_en_personaje(
    pantalla,
    p,
    sprite_personaje=None,
    rect_personaje=None,
    mirando_derecha=None,
):
    if isinstance(p, dict):
        acc_id = p.get("accesorio")
        mirando_der = p.get("mirando_derecha", True) if mirando_derecha is None else bool(mirando_derecha)
    else:
        acc_id = p
        mirando_der = True if mirando_derecha is None else bool(mirando_derecha)

    if not acc_id or acc_id == "Ninguno":
        return
    surf_acc = cargar_accesorio(acc_id)
    if not surf_acc:
        return

    # Determinar el rectángulo sobre el que posicionar el accesorio
    if isinstance(rect_personaje, pygame.Rect):
        rect_base = rect_personaje
    elif isinstance(sprite_personaje, pygame.Rect):
        rect_base = sprite_personaje
    elif isinstance(p, dict) and "hitbox" in p:
        rect_base = p["hitbox"]
    else:
        return

    meta = METADATA_ACCESORIOS.get(acc_id)
    if meta:
        off_x, off_y = meta["offset"]
    else:
        off_x = (rect_base.width - surf_acc.get_width()) // 2
        off_y = -surf_acc.get_height() + 12

    # Anclaje dinámico a la cabeza para todas las animaciones (caminar, saltar, caer, agacharse, etc.)
    top_cabeza = 0
    if isinstance(sprite_personaje, pygame.Surface):
        top_cabeza, _ = calcular_anclaje_sprite(sprite_personaje)
    elif isinstance(p, dict) and "sprites" in p:
        est = p.get("estado", "quieto")
        sp_act = p["sprites"].get(est)
        if sp_act:
            top_cabeza, _ = calcular_anclaje_sprite(sp_act)

    if mirando_der:
        x_acc = rect_base.left + off_x
    else:
        surf_acc = pygame.transform.flip(surf_acc, True, False)
        x_acc = rect_base.left + (rect_base.width - off_x - surf_acc.get_width())

    y_acc = rect_base.top + top_cabeza + off_y
    pantalla.blit(surf_acc, (x_acc, y_acc))


COLOR_AGUA = (0, 140, 240, 130)
_CACHE_AGUA = {}


def dibujar_agua(pantalla, zona_agua=None):
    """
    Dibuja la masa de agua translúcida sobre el escenario.
    Usa una superficie con canal alfa (SRCALPHA) para que los personajes
    y plataformas se vean sumergidos debajo.
    Utiliza caché para no crear una superficie gigante de 3000x420 en cada frame.
    """
    if zona_agua is None:
        zona_agua = pygame.Rect(0, 220, ANCHO, ALTO - 80 - 220)

    clave = (zona_agua.width, zona_agua.height)
    superficie = _CACHE_AGUA.get(clave)
    if superficie is None:
        superficie = pygame.Surface(clave, pygame.SRCALPHA)
        superficie.fill(COLOR_AGUA)
        _CACHE_AGUA[clave] = superficie

    pantalla.blit(superficie, (zona_agua.x, zona_agua.y))
