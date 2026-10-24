import os
import pygame

ANCHO, ALTO = 1280, 720
FPS = 60
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

COLOR_JUGADOR1 = "Celeste"
COLOR_JUGADOR2 = "Violeta"

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Personajes")
RUTA_BOTONES = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Botones")
RUTA_CAJA = os.path.join(DIRECTORIO_ACTUAL, "caja.png")
RUTA_OBJETOS = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Objetos")

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
                return img.convert_alpha()
            except pygame.error:
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

    solo_nombre = os.path.basename(nombre_norm)
    for raiz, _, archivos in os.walk(RUTA_BOTONES):
        if solo_nombre in archivos:
            res = _cargar(os.path.join(raiz, solo_nombre))
            if res:
                _CACHE_BOTONES[nombre] = res
                return res

    _CACHE_BOTONES[nombre] = None
    return None


def aclarar_boton(surf, factor=45):
    """
    Genera una versión iluminada / más clara del sprite del botón para el estado hover.
    Mantiene intactos los bordes y la transparencia.
    """
    if surf is None:
        return None
    brillante = surf.copy()
    capa = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    capa.fill((factor, factor, factor, 0))
    brillante.blit(capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return brillante


def animar_pulsacion_boton(pantalla, rect, spr_semi, spr_apretado, fondo_limpio=None):
    """
    Reproduce la animación de pulsación en dos etapas (semiapretado y apretado)
    al hacer clic sobre un botón.
    Limpia completamente el fondo para evitar que el botón sin apretar quede visible debajo.
    """
    def _limpiar():
        if fondo_limpio is not None:
            if isinstance(fondo_limpio, (tuple, list)):
                pygame.draw.rect(pantalla, fondo_limpio[:3], rect)
            elif isinstance(fondo_limpio, pygame.Surface):
                if fondo_limpio.get_size() == (rect.width, rect.height):
                    pantalla.blit(fondo_limpio, rect)
                else:
                    pantalla.blit(fondo_limpio, rect, rect)
        else:
            ancho_p, alto_p = pantalla.get_size()
            x_muestra = max(0, rect.left - 4)
            y_muestra = max(0, min(alto_p - 1, rect.centery))
            col_bg = pantalla.get_at((x_muestra, y_muestra))[:3]
            pygame.draw.rect(pantalla, col_bg, rect)

    if spr_semi:
        _limpiar()
        pantalla.blit(spr_semi, rect)
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(50)

    if spr_apretado:
        _limpiar()
        pantalla.blit(spr_apretado, rect)
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(80)



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


def cargar_sprites(nombre_color="Celeste"):
    """
    Carga los sprites originales del personaje según la carpeta de color.
    Si falta algún frame, intenta obtenerlo de la carpeta Blanco o quieto como respaldo.
    """
    ruta_carpeta = os.path.join(RUTA_BASE, nombre_color)
    sprites = {}

    for estado in ESTADOS_PERSONAJE:
        img_cargada = None
        posibles_rutas = [
            os.path.join(ruta_carpeta, f"{estado}.png"),
            os.path.join(ruta_carpeta, "quieto.png"),
            os.path.join(RUTA_BASE, "Blanco", f"{estado}.png"),
            os.path.join(DIRECTORIO_ACTUAL, f"{estado}.png"),
            os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", f"{estado}.png")
        ]

        for r in posibles_rutas:
            if os.path.isfile(r):
                try:
                    img_cargada = pygame.image.load(r).convert_alpha()
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

    return sprites


def cargar_sprite_caja(tamano):
    rutas = [
        RUTA_CAJA,
        os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Caja", "caja.png"),
        os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Objetos", "caja.png"),
    ]
    for ruta in rutas:
        if os.path.isfile(ruta):
            try:
                img = pygame.image.load(ruta).convert_alpha()
                return pygame.transform.scale(img, (tamano, tamano))
            except pygame.error:
                pass

    sprite = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
    sprite.fill((139, 69, 19))
    return sprite


def cargar_sprite_llave():
    ruta_llave = os.path.join(RUTA_OBJETOS, "llave.png")
    if os.path.isfile(ruta_llave):
        try:
            img = pygame.image.load(ruta_llave).convert_alpha()
            return pygame.transform.scale(img, (25, 46))
        except pygame.error:
            pass

    surface = pygame.Surface((25, 46), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 215, 0), (12, 12), 10)
    pygame.draw.rect(surface, (255, 215, 0), (10, 12, 5, 30))
    pygame.draw.rect(surface, (255, 215, 0), (15, 32, 6, 4))
    pygame.draw.rect(surface, (255, 215, 0), (15, 38, 6, 4))
    return surface


def cargar_sprites_puerta():
    ruta_cerrada = os.path.join(RUTA_OBJETOS, "Puerta", "puerta_cerrada.png")
    ruta_abierta = os.path.join(RUTA_OBJETOS, "Puerta", "puerta_abierta.png")

    if not os.path.isfile(ruta_cerrada):
        ruta_cerrada = os.path.join(RUTA_OBJETOS, "puerta.png")

    sprites = {"cerrada": None, "abierta": None}

    if os.path.isfile(ruta_cerrada):
        try:
            img = pygame.image.load(ruta_cerrada).convert_alpha()
            sprites["cerrada"] = pygame.transform.scale(img, (60, 90))
        except pygame.error:
            pass

    if os.path.isfile(ruta_abierta):
        try:
            img = pygame.image.load(ruta_abierta).convert_alpha()
            sprites["abierta"] = pygame.transform.scale(img, (60, 90))
        except pygame.error:
            pass

    if sprites["cerrada"] is None:
        sprites["cerrada"] = pygame.Surface((60, 90), pygame.SRCALPHA)
        sprites["cerrada"].fill((139, 69, 19))
        pygame.draw.circle(sprites["cerrada"], (255, 215, 0), (50, 45), 5)

    if sprites["abierta"] is None:
        sprites["abierta"] = pygame.Surface((60, 90), pygame.SRCALPHA)
        pygame.draw.rect(sprites["abierta"], (139, 69, 19), (0, 0, 15, 90))

    return sprites


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

    rect_sprite = sprite.get_rect(center=p["hitbox"].center)
    pantalla.blit(sprite, rect_sprite)

    if zona_agua is not None and p.get("en_agua", False):
        sprite_agua = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        sprite_agua.fill((0, 100, 180, 70))
        sprite_agua.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        clip_anterior = pantalla.get_clip()
        pantalla.set_clip(pygame.Rect(zona_agua.left, zona_agua.top, zona_agua.width, pantalla.get_height() - zona_agua.top))
        pantalla.blit(sprite_agua, rect_sprite)
        pantalla.set_clip(clip_anterior)


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