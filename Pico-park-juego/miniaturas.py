import os
import pygame

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_SPRITES = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites")
RUTA_PERSONAJES = os.path.join(RUTA_SPRITES, "Personajes")
RUTA_OBJETOS = os.path.join(RUTA_SPRITES, "Objetos")
RUTA_MINIATURAS = os.path.join(RUTA_SPRITES, "Miniaturas")

# Constantes de colores originales del juego
COL_FONDO_M1 = (255, 240, 195)
COL_SUELO_M1 = (225, 110, 80)
COL_PLATAFORMA_M1 = (110, 110, 115)
COL_BORDE_PLAT = (80, 80, 85)
COLOR_SOGA = (200, 160, 100)

ANCHO_MINI = 176
ALTO_MINI = 112

_CACHE_MINIATURAS = None


def _cargar_recurso_original(ruta, tamano):
    """Carga una imagen y la escala al tamaño requerido manteniendo transparencia."""
    if os.path.isfile(ruta):
        try:
            img = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(img, tamano)
        except Exception:
            pass
    # Fallback si el display aún no se inicializó
    if os.path.isfile(ruta):
        try:
            img = pygame.image.load(ruta)
            return pygame.transform.scale(img, tamano)
        except Exception:
            pass
    return None


def _cargar_personaje(color_nombre="Celeste", tamano=(16, 20), tinte_agua=False):
    """Carga el sprite en reposo del personaje original."""
    ruta = os.path.join(RUTA_PERSONAJES, color_nombre, "quieto.png")
    sp = _cargar_recurso_original(ruta, tamano)
    if sp is None:
        sp = pygame.Surface(tamano, pygame.SRCALPHA)
        color = (124, 231, 255) if color_nombre == "Celeste" else (161, 123, 255)
        pygame.draw.rect(sp, color, (0, 0, *tamano), border_radius=4)

    if tinte_agua:
        sp_agua = sp.copy()
        filtro = pygame.Surface(tamano, pygame.SRCALPHA)
        filtro.fill((0, 100, 180, 80))
        sp_agua.blit(filtro, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return sp_agua
    return sp


def _cargar_caja(tamano=(18, 18)):
    """Carga la caja original del juego."""
    ruta = os.path.join(RUTA_OBJETOS, "caja.png")
    sp = _cargar_recurso_original(ruta, tamano)
    if sp is None:
        sp = pygame.Surface(tamano, pygame.SRCALPHA)
        pygame.draw.rect(sp, (185, 130, 75), (0, 0, *tamano))
        pygame.draw.rect(sp, (90, 55, 25), (0, 0, *tamano), 2)
        pygame.draw.line(sp, (90, 55, 25), (0, 0), (tamano[0], tamano[1]), 2)
        pygame.draw.line(sp, (90, 55, 25), (tamano[0], 0), (0, tamano[1]), 2)
    return sp


def _cargar_llave(tamano=(10, 18)):
    """Carga la llave original del juego."""
    ruta = os.path.join(RUTA_OBJETOS, "llave.png")
    sp = _cargar_recurso_original(ruta, tamano)
    if sp is None:
        sp = pygame.Surface(tamano, pygame.SRCALPHA)
        pygame.draw.circle(sp, (255, 215, 0), (tamano[0] // 2, 5), 4)
        pygame.draw.rect(sp, (255, 215, 0), (tamano[0] // 2 - 1, 5, 2, tamano[1] - 5))
        pygame.draw.rect(sp, (255, 215, 0), (tamano[0] // 2 + 1, tamano[1] - 6, 3, 2))
    return sp


def _crear_puerta_original(tamano=(16, 26)):
    """Representación fiel en pixel art de la puerta de madera con marco y pomo dorado."""
    p = pygame.Surface(tamano, pygame.SRCALPHA)
    w, h = tamano
    # Marco exterior
    pygame.draw.rect(p, (90, 45, 15), (0, 0, w, h), border_radius=2)
    # Hoja de madera
    pygame.draw.rect(p, (139, 69, 19), (2, 2, w - 4, h - 2), border_radius=2)
    # Tablones decorativos sutiles
    pygame.draw.line(p, (115, 55, 15), (w // 2, 3), (w // 2, h - 2), 1)
    # Pomo dorado
    pygame.draw.circle(p, (255, 215, 0), (w - 4, h // 2 + 2), 2)
    return p


def _dibujar_pinchos(surf, x_inicio, x_fin, y_base, hacia_arriba=True, w_p=10, h_p=10):
    """Dibuja una hilera de pinchos triangulares clásicos."""
    col_cuerpo = (235, 235, 240)
    col_borde = (110, 110, 115)
    x = x_inicio
    while x + w_p <= x_fin:
        if hacia_arriba:
            puntos = [(x, y_base), (x + w_p // 2, y_base - h_p), (x + w_p, y_base)]
        else:
            puntos = [(x, y_base), (x + w_p // 2, y_base + h_p), (x + w_p, y_base)]
        pygame.draw.polygon(surf, col_cuerpo, puntos)
        pygame.draw.polygon(surf, col_borde, puntos, 1)
        x += w_p


def _dibujar_soga(surf, p1, p2):
    """Traza la soga entre dos coordenadas de personaje."""
    pygame.draw.line(surf, COLOR_SOGA, p1, p2, 2)


# ==============================================================================
# MUNDO 1: BÁSICO (Fondo cálido original, sin soga)
# ==============================================================================

def _crear_m1_n1():
    """1-1: Tutorial (Suelo continuo, 2 personajes, llave, puerta)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 88
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (24, y_suelo - 20))
    s.blit(pj2, (48, y_suelo - 20))
    s.blit(llave, (98, y_suelo - 22))
    s.blit(puerta, (142, y_suelo - 26))
    return s


def _crear_m1_n2():
    """1-2: La torre humana (Bloque elevado, personajes uno encima del otro, llave arriba)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 88
    # Suelo izquierdo
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, 100, ALTO_MINI - y_suelo))

    # Bloque/Pared elevada a la derecha
    rect_bloque = pygame.Rect(102, 50, 74, ALTO_MINI - 50)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, rect_bloque)
    pygame.draw.rect(s, COL_BORDE_PLAT, rect_bloque, 2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Torre humana: Celeste abajo, Violeta arriba
    s.blit(pj1, (70, y_suelo - 20))
    s.blit(pj2, (70, y_suelo - 39))

    # Llave en la cima del bloque elevado
    s.blit(llave, (126, 50 - 18))
    s.blit(puerta, (150, 50 - 26))
    return s


def _crear_m1_n3():
    """1-3: La caja y el botón (Caja sobre botón en el suelo, pared fina, llave al otro lado)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_suelo = 88
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))

    # Botón en el suelo
    pygame.draw.rect(s, (190, 40, 40), (52, y_suelo - 3, 24, 4), border_radius=1)

    # Caja colocada sobre el botón
    caja = _cargar_caja()
    s.blit(caja, (55, y_suelo - 20))

    # Pared fina que bloquea el camino
    rect_pared = pygame.Rect(96, 26, 6, y_suelo - 26)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, rect_pared)
    pygame.draw.rect(s, COL_BORDE_PLAT, rect_pared, 1)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (16, y_suelo - 20))
    s.blit(pj2, (34, y_suelo - 20))
    # Llave y puerta detrás de la pared
    s.blit(llave, (120, y_suelo - 22))
    s.blit(puerta, (146, y_suelo - 26))
    return s


def _crear_m1_n4():
    """1-4: El láser y la caja (Pozo profundo entre dos plataformas, láser horizontal izquierda a derecha bloqueado por la caja, llave detrás)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_plat = 68

    # Plataforma izquierda elevada
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_plat, 42, ALTO_MINI - y_plat))
    pygame.draw.line(s, (245, 140, 110), (0, y_plat), (42, y_plat), 1)
    pygame.draw.line(s, (180, 80, 50), (42, y_plat), (42, ALTO_MINI), 1)

    # Plataforma derecha elevada
    pygame.draw.rect(s, COL_SUELO_M1, (88, y_plat, ANCHO_MINI - 88, ALTO_MINI - y_plat))
    pygame.draw.line(s, (245, 140, 110), (88, y_plat), (ANCHO_MINI, y_plat), 1)
    pygame.draw.line(s, (180, 80, 50), (88, y_plat), (88, ALTO_MINI), 1)

    # Pozo profundo entre las dos plataformas
    y_fondo = 96
    pygame.draw.rect(s, (45, 32, 28), (42, y_fondo, 46, ALTO_MINI - y_fondo))
    _dibujar_pinchos(s, 44, 88, y_fondo, hacia_arriba=True, w_p=7, h_p=6)

    # Emisor de láser colocado horizontalmente a la izquierda
    pygame.draw.rect(s, (80, 80, 90), (10, y_plat - 14, 14, 14), border_radius=2)
    pygame.draw.rect(s, (50, 50, 60), (10, y_plat - 14, 14, 14), 1, border_radius=2)
    pygame.draw.rect(s, (110, 110, 125), (24, y_plat - 12, 6, 8))
    pygame.draw.rect(s, (60, 60, 70), (24, y_plat - 12, 6, 8), 1)
    pygame.draw.rect(s, (255, 60, 60), (28, y_plat - 10, 2, 4))

    # Rayo láser horizontal apuntando de izquierda a derecha a la altura de la llave
    y_laser = 59
    x_caja = 94
    pygame.draw.line(s, (255, 45, 45), (30, y_laser), (x_caja, y_laser), 3)
    pygame.draw.line(s, (255, 230, 230), (30, y_laser), (x_caja, y_laser), 1)

    # Destellos de impacto: la caja intercepta el láser
    pygame.draw.rect(s, (255, 220, 100), (x_caja - 1, y_laser - 2, 2, 5))
    pygame.draw.rect(s, (255, 140, 40), (x_caja - 2, y_laser - 1, 1, 3))

    # Caja bloqueando el rayo en la plataforma derecha
    caja = _cargar_caja((18, 18))
    s.blit(caja, (x_caja, y_plat - 18))

    # Personajes y llave detrás de la caja
    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave((10, 18))
    puerta = _crear_puerta_original((16, 26))

    # Celeste empuja la caja para bloquear el rayo
    s.blit(pj1, (113, y_plat - 20))
    # Llave detrás de la caja, a la misma altura que el láser
    s.blit(llave, (131, y_plat - 18))
    # Violeta avanzando hacia la llave y la puerta
    s.blit(pj2, (143, y_plat - 20))
    # Puerta al final
    s.blit(puerta, (158, y_plat - 26))

    return s


def _crear_m1_n5():
    """1-5: Las cuatro paredes de colores (Recorrido superior: paredes roja, azul, roja, azul. Recorrido inferior: botones correspondientes)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    y_techo = 10
    y_div = 52
    y_suelo = 94

    # Techo superior
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (0, 0, ANCHO_MINI, y_techo))
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, 0, ANCHO_MINI, y_techo), 1)

    # Plataforma divisoria central entre ambos recorridos
    pygame.draw.rect(s, COL_PLATAFORMA_M1, (0, y_div, ANCHO_MINI, 6))
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, y_div, ANCHO_MINI, 6), 1)

    # Suelo del recorrido inferior
    pygame.draw.rect(s, COL_SUELO_M1, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo))
    pygame.draw.line(s, (245, 140, 110), (0, y_suelo), (ANCHO_MINI, y_suelo), 1)
    pygame.draw.rect(s, COL_BORDE_PLAT, (0, y_suelo, ANCHO_MINI, ALTO_MINI - y_suelo), 1)

    # RECORRIDO SUPERIOR: 4 paredes verticales en orden ROJO, AZUL, ROJO, AZUL
    colores_pared = [
        (225, 45, 45),   # 1. Roja
        (45, 110, 225),  # 2. Azul
        (225, 45, 45),   # 3. Roja
        (45, 110, 225),  # 4. Azul
    ]
    xs_pared = [48, 76, 104, 132]
    for col, xp in zip(colores_pared, xs_pared):
        r_p = pygame.Rect(xp, y_techo, 6, y_div - y_techo)
        pygame.draw.rect(s, col, r_p)
        pygame.draw.rect(s, (30, 30, 30), r_p, 1)

    # RECORRIDO INFERIOR: Botones en el suelo (Rojo, Azul, Rojo, Azul)
    colores_boton = [
        (225, 45, 45),   # 1. Rojo
        (45, 110, 225),  # 2. Azul
        (225, 45, 45),   # 3. Rojo
        (45, 110, 225),  # 4. Azul
    ]
    xs_boton = [32, 66, 100, 132]
    for i, (col, xb) in enumerate(zip(colores_boton, xs_boton)):
        pygame.draw.rect(s, (70, 60, 55), (xb - 2, y_suelo - 1, 16, 2))
        if i == 0:
            # Botón 1 presionado por el personaje
            pygame.draw.rect(s, col, (xb, y_suelo - 2, 12, 2), border_radius=1)
        else:
            pygame.draw.rect(s, col, (xb, y_suelo - 4, 12, 4), border_radius=1)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Celeste arriba en el recorrido superior frente a las paredes
    s.blit(pj1, (20, y_div - 20))
    # Violeta abajo en el recorrido inferior colaborando al presionar el primer botón
    s.blit(pj2, (30, y_suelo - 20))

    # Llave y puerta al final del recorrido superior
    s.blit(llave, (144, y_div - 18))
    s.blit(puerta, (156, y_div - 26))

    return s


def _crear_m2_n1():
    """2-1: El arrastre básico (Plataformas separadas a distintas alturas con vacíos entre sí, pozo con pinchos debajo, personajes unidos por soga, llave y puerta)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Debajo de todo el recorrido: pozo profundo con pinchos
    pygame.draw.rect(s, (45, 35, 35), (0, 96, ANCHO_MINI, ALTO_MINI - 96))
    _dibujar_pinchos(s, 0, ANCHO_MINI, 96, hacia_arriba=True, w_p=8, h_p=8)

    # Plataformas separadas entre sí, con espacios vacíos a distintas alturas (no escalera continua)
    plats = [
        pygame.Rect(8, 74, 30, 8),    # 1. Plataforma inicial
        pygame.Rect(48, 60, 44, 8),   # 2. Plataforma con personajes
        pygame.Rect(102, 50, 28, 8),  # 3. Plataforma intermedia con llave
        pygame.Rect(142, 62, 26, 8),  # 4. Plataforma final con puerta
    ]
    for p in plats:
        pygame.draw.rect(s, COL_PLATAFORMA_M1, p, border_radius=2)
        pygame.draw.rect(s, COL_BORDE_PLAT, p, 1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Personajes en la plataforma 2 unidos por la soga
    pos_v = (52, 60 - 20)
    pos_c = (74, 60 - 20)
    _dibujar_soga(s, (pos_v[0] + 12, pos_v[1] + 12), (pos_c[0] + 4, pos_c[1] + 12))

    s.blit(pj2, pos_v)
    s.blit(pj1, pos_c)

    # Llave en la plataforma intermedia
    s.blit(llave, (111, 50 - 18))

    # Puerta de salida al final del recorrido después de las plataformas
    s.blit(puerta, (147, 62 - 26))

    return s


def _crear_m2_n2():
    """2-2: La plataforma móvil (Plataforma sobre abismo con pinchos, bloque obstáculo, llave)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Bordes de suelo
    pygame.draw.rect(s, COL_SUELO_M1, (0, 78, 25, ALTO_MINI - 78))
    pygame.draw.rect(s, COL_SUELO_M1, (151, 78, 25, ALTO_MINI - 78))

    # Abismo con pinchos en el fondo
    pygame.draw.rect(s, (45, 35, 35), (25, 96, 126, ALTO_MINI - 96))
    _dibujar_pinchos(s, 25, 151, 96, hacia_arriba=True)

    # Plataforma móvil suspendida sobre el abismo
    plat_movil = pygame.Rect(42, 66, 68, 8)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat_movil, border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat_movil, 1, border_radius=2)

    # Bloque en medio del trayecto de la plataforma
    bloque = pygame.Rect(72, 46, 14, 20)
    pygame.draw.rect(s, (95, 75, 65), bloque)
    pygame.draw.rect(s, (45, 30, 20), bloque, 1)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()

    pos1 = (46, 66 - 20)
    pos2 = (90, 66 - 20)
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 10), (pos2[0] + 8, pos2[1] + 10))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)
    s.blit(llave, (126, 52))
    return s


def _crear_m2_n3():
    """2-3: El péndulo (Plataforma elevada, un personaje encima, otro colgado de la soga sobre abismo con pinchos)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Abismo inferior con pinchos
    pygame.draw.rect(s, (45, 35, 35), (0, 98, ANCHO_MINI, ALTO_MINI - 98))
    _dibujar_pinchos(s, 0, ANCHO_MINI, 98, hacia_arriba=True)

    # Plataforma elevada
    plat = pygame.Rect(25, 36, 60, 8)
    pygame.draw.rect(s, COL_PLATAFORMA_M1, plat, border_radius=2)
    pygame.draw.rect(s, COL_BORDE_PLAT, plat, 1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()

    # Celeste encima de la plataforma
    pos1 = (45, 36 - 20)
    # Violeta colgando por debajo en diagonal péndulo
    pos2 = (95, 68)

    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 12), (pos2[0] + 8, pos2[1] + 8))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)

    # Llave en la zona inferior que intenta alcanzar
    s.blit(llave, (120, 72))
    return s


def _crear_m2_n4():
    """2-4: Las plataformas que se derrumban (Abismo con pinchos, plataformas pequeñas separadas con fisuras)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Abismo de pinchos en el fondo
    pygame.draw.rect(s, (45, 35, 35), (0, 98, ANCHO_MINI, ALTO_MINI - 98))
    _dibujar_pinchos(s, 0, ANCHO_MINI, 98, hacia_arriba=True)

    # Plataformas pequeñas agrietadas
    plats = [
        pygame.Rect(12, 78, 26, 8),
        pygame.Rect(52, 68, 26, 8),
        pygame.Rect(96, 62, 26, 8),
        pygame.Rect(138, 72, 26, 8),
    ]
    for p in plats:
        pygame.draw.rect(s, (155, 125, 100), p, border_radius=1)
        pygame.draw.rect(s, (90, 70, 50), p, 1, border_radius=1)
        # Grieta en la plataforma que se derrumba
        pygame.draw.line(s, (50, 35, 25), (p.x + 8, p.y + 1), (p.x + 12, p.y + 7), 1)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    llave = _cargar_llave()

    pos1 = (56, 68 - 20)
    pos2 = (100, 62 - 20)
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 10), (pos2[0] + 8, pos2[1] + 10))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)
    s.blit(llave, (78, 42))
    return s


def _crear_m2_n5():
    """2-5: Las plataformas alternadas (Escalera intercalada de plataformas, soga, puerta en la cima)."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill(COL_FONDO_M1)

    # Abismo inferior
    pygame.draw.rect(s, (50, 40, 35), (0, 102, ANCHO_MINI, ALTO_MINI - 102))

    # Plataformas alternadas hacia arriba
    plats = [
        pygame.Rect(10, 86, 40, 8),   # 1 izq
        pygame.Rect(65, 72, 40, 8),   # 2 der
        pygame.Rect(25, 56, 40, 8),   # 3 izq
        pygame.Rect(80, 42, 40, 8),   # 4 der
        pygame.Rect(130, 30, 40, 8),  # 5 cima
    ]
    for p in plats:
        pygame.draw.rect(s, COL_PLATAFORMA_M1, p, border_radius=2)
        pygame.draw.rect(s, COL_BORDE_PLAT, p, 1, border_radius=2)

    pj1 = _cargar_personaje("Celeste")
    pj2 = _cargar_personaje("Violeta")
    puerta = _crear_puerta_original()

    pos1 = (35, 56 - 20)
    pos2 = (75, 72 - 20)
    _dibujar_soga(s, (pos1[0] + 8, pos1[1] + 10), (pos2[0] + 8, pos2[1] + 10))

    s.blit(pj1, pos1)
    s.blit(pj2, pos2)
    s.blit(puerta, (142, 30 - 26))
    return s


# ==============================================================================
# MUNDO 3: SUBMARINO (Agua, rocas, corales, algas, tinte azul, sin soga)
# ==============================================================================

def _dibujar_alga(surf, x, y_base, alto=28, color=(40, 160, 80)):
    """Dibuja un tallo de alga marina ondeante pixel art."""
    puntos = [
        (x, y_base),
        (x + 3, y_base - alto // 3),
        (x - 3, y_base - 2 * alto // 3),
        (x + 1, y_base - alto)
    ]
    pygame.draw.lines(surf, color, False, puntos, 3)


def _dibujar_coral(surf, x, y_base, color=(235, 105, 130)):
    """Dibuja una ramificación de coral marino."""
    pygame.draw.line(surf, color, (x, y_base), (x, y_base - 14), 3)
    pygame.draw.line(surf, color, (x, y_base - 8), (x - 6, y_base - 16), 2)
    pygame.draw.line(surf, color, (x, y_base - 8), (x + 6, y_base - 16), 2)


def _crear_fondo_submarino():
    """Fondo base acuático con superficie y burbujas."""
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill((25, 115, 195))

    # Olas en la superficie superior
    for i in range(11):
        wx = i * 16
        pygame.draw.arc(s, (140, 220, 255), (wx, 0, 18, 10), 0, 3.14, 2)

    # Burbujas flotantes
    burbujas = [(25, 30, 2), (65, 45, 3), (115, 25, 2), (145, 55, 3), (85, 80, 2)]
    for bx, by, br in burbujas:
        pygame.draw.circle(s, (190, 240, 255), (bx, by), br, 1)

    return s


def _crear_m3_n1():
    """3-1: El jardín de algas (Zona abierta submarina, algas, rocas, corales, llave entre rocas, puerta)."""
    s = _crear_fondo_submarino()

    # Lecho marino rocoso
    y_lecho = 90
    pygame.draw.rect(s, (45, 75, 105), (0, y_lecho, ANCHO_MINI, ALTO_MINI - y_lecho))

    # Formaciones rocosas
    pygame.draw.ellipse(s, (65, 95, 125), (75, y_lecho - 14, 35, 24))
    pygame.draw.ellipse(s, (55, 85, 115), (95, y_lecho - 18, 28, 28))

    # Algas y corales
    _dibujar_alga(s, 15, y_lecho, alto=32)
    _dibujar_alga(s, 22, y_lecho, alto=40)
    _dibujar_alga(s, 65, y_lecho, alto=35)
    _dibujar_coral(s, 45, y_lecho, (240, 110, 130))
    _dibujar_coral(s, 128, y_lecho, (245, 160, 90))

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (30, 48))
    s.blit(pj2, (50, 38))
    # Llave entre rocas
    s.blit(llave, (88, y_lecho - 22))
    # Puerta al final
    s.blit(puerta, (146, y_lecho - 26))
    return s


def _crear_m3_n2():
    """3-2: El laberinto de coral (Paredes de roca marina, corales, caminos y callejones, llave escondida)."""
    s = _crear_fondo_submarino()

    col_roca = (55, 85, 115)
    col_borde_roca = (35, 60, 85)

    # Estructura del laberinto submarino (muros y callejones)
    paredes_laberinto = [
        pygame.Rect(0, 0, ANCHO_MINI, 8),                  # Techo
        pygame.Rect(0, 104, ANCHO_MINI, 8),                # Suelo
        pygame.Rect(40, 8, 12, 60),                       # Muro 1 bajando
        pygame.Rect(40, 68, 45, 10),                      # Conector 1
        pygame.Rect(85, 35, 12, 69),                      # Muro 2 subiendo
        pygame.Rect(125, 8, 12, 65),                      # Muro 3 bajando
        pygame.Rect(125, 73, 35, 10),                     # Callejón sin salida
    ]
    for p in paredes_laberinto:
        pygame.draw.rect(s, col_roca, p)
        pygame.draw.rect(s, col_borde_roca, p, 1)

    # Corales y algas decorando las esquinas del laberinto
    _dibujar_coral(s, 35, 68, (230, 95, 120))
    _dibujar_coral(s, 105, 104, (245, 150, 80))
    _dibujar_alga(s, 15, 104, alto=28)
    _dibujar_alga(s, 120, 104, alto=24)

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()

    s.blit(pj1, (16, 35))
    s.blit(pj2, (58, 40))
    # Llave escondida en la sección interior del laberinto
    s.blit(llave, (102, 22))
    return s


def _crear_m3_n3():
    """3-3: Las rocas peligrosas (Pasillos estrechos, rocas y pinchos en suelo y techo, llave en zona peligrosa)."""
    s = _crear_fondo_submarino()

    col_roca = (55, 80, 105)

    # Techo y suelo rocosos
    pygame.draw.rect(s, col_roca, (0, 0, ANCHO_MINI, 18))
    pygame.draw.rect(s, col_roca, (0, 94, ANCHO_MINI, 18))

    # Pinchos saliendo del techo hacia abajo
    _dibujar_pinchos(s, 35, 125, 18, hacia_arriba=False, w_p=10, h_p=12)
    # Pinchos saliendo del suelo hacia arriba
    _dibujar_pinchos(s, 55, 135, 94, hacia_arriba=True, w_p=10, h_p=12)

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    # Personajes maniobrando en el pasillo estrecho
    s.blit(pj1, (14, 46))
    s.blit(pj2, (34, 46))

    # Llave detrás de la zona peligrosa
    s.blit(llave, (98, 46))
    # Puerta al otro lado
    s.blit(puerta, (146, 94 - 26))
    return s


def _crear_m3_n4():
    """3-4: El laberinto oscuro (Zona oscura, círculos de luz de linternas alrededor de personajes)."""
    # Fondo de oscuridad abisal profunda
    s = pygame.Surface((ANCHO_MINI, ALTO_MINI))
    s.fill((12, 18, 30))

    # Paredes oscuras del laberinto
    paredes = [
        pygame.Rect(35, 0, 10, 50),
        pygame.Rect(75, 45, 10, 67),
        pygame.Rect(115, 0, 10, 60),
    ]
    for p in paredes:
        pygame.draw.rect(s, (25, 35, 50), p)

    # Capa de linternas con luz cálida/cian translúcida
    pos_pj1 = (52, 50)
    pos_pj2 = (95, 42)

    luz_surf = pygame.Surface((ANCHO_MINI, ALTO_MINI), pygame.SRCALPHA)
    # Haz de luz de Celeste
    pygame.draw.circle(luz_surf, (220, 245, 255, 110), (pos_pj1[0] + 8, pos_pj1[1] + 10), 32)
    pygame.draw.circle(luz_surf, (255, 255, 255, 170), (pos_pj1[0] + 8, pos_pj1[1] + 10), 18)
    # Haz de luz de Violeta
    pygame.draw.circle(luz_surf, (220, 245, 255, 110), (pos_pj2[0] + 8, pos_pj2[1] + 10), 30)
    pygame.draw.circle(luz_surf, (255, 255, 255, 170), (pos_pj2[0] + 8, pos_pj2[1] + 10), 16)
    s.blit(luz_surf, (0, 0))

    # Corales visibles sólo donde alumbra la luz
    _dibujar_coral(s, 68, 90, (190, 80, 100))
    _dibujar_alga(s, 48, 112, alto=24, color=(35, 110, 65))

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, pos_pj1)
    s.blit(pj2, pos_pj2)

    # Llave y puerta emergiendo en la penumbra
    s.blit(llave, (132, 28))
    s.blit(puerta, (148, 70))
    return s


def _crear_m3_n5():
    """3-5: El abismo submarino (Gran abismo, pasillos estrechos, pinchos, corrientes de agua con flechas)."""
    s = _crear_fondo_submarino()

    col_roca = (45, 75, 105)

    # Plataforma rocosa izquierda elevada
    pygame.draw.rect(s, col_roca, (0, 48, 45, ALTO_MINI - 48))
    # Gran abismo central profundo
    pygame.draw.rect(s, (20, 45, 70), (45, 96, 75, ALTO_MINI - 96))
    _dibujar_pinchos(s, 45, 120, 96, hacia_arriba=True, w_p=10, h_p=10)
    # Saliente superior derecho
    pygame.draw.rect(s, col_roca, (120, 40, 56, ALTO_MINI - 40))

    # Pinchos en el techo saliente
    _dibujar_pinchos(s, 50, 95, 0, hacia_arriba=False, w_p=10, h_p=10)

    # Corrientes de agua marinas representadas con líneas y flechas cian translúcidas
    for cy in [26, 68]:
        pygame.draw.line(s, (180, 245, 255), (55, cy), (105, cy), 2)
        # Flecha de corriente
        pygame.draw.polygon(s, (180, 245, 255), [(105, cy - 4), (112, cy), (105, cy + 4)])

    pj1 = _cargar_personaje("Celeste", tinte_agua=True)
    pj2 = _cargar_personaje("Violeta", tinte_agua=True)
    llave = _cargar_llave()
    puerta = _crear_puerta_original()

    s.blit(pj1, (16, 28))
    s.blit(pj2, (28, 28))

    # Llave en cavidad profunda del abismo
    s.blit(llave, (78, 74))
    # Puerta en la cima derecha
    s.blit(puerta, (146, 40 - 26))
    return s


# ==============================================================================
# DICCIONARIO Y GENERADOR PRINCIPAL
# ==============================================================================

CREADORES_MINIATURAS = {
    1: {
        1: _crear_m1_n1,
        2: _crear_m1_n2,
        3: _crear_m1_n3,
        4: _crear_m1_n4,
        5: _crear_m1_n5,
    },
    2: {
        1: _crear_m2_n1,
        2: _crear_m2_n2,
        3: _crear_m2_n3,
        4: _crear_m2_n4,
        5: _crear_m2_n5,
    },
    3: {
        1: _crear_m3_n1,
        2: _crear_m3_n2,
        3: _crear_m3_n3,
        4: _crear_m3_n4,
        5: _crear_m3_n5,
    },
}


def generar_todas_las_miniaturas(guardar_en_disco=True):
    """
    Genera las 15 miniaturas temáticas y opcionalmente las guarda como PNGs
    en la carpeta Sprites/Miniaturas/ (nivel_{mundo}_{nivel}.png).
    Retorna un diccionario {mundo: {nivel: Surface}}.
    """
    if guardar_en_disco:
        os.makedirs(RUTA_MINIATURAS, exist_ok=True)

    resultado = {}
    for mundo in (1, 2, 3):
        resultado[mundo] = {}
        for nivel in range(1, 6):
            creador = CREADORES_MINIATURAS[mundo][nivel]
            surf = creador()

            # Añadir borde pixel art sutil para tarjeta
            pygame.draw.rect(surf, (165, 140, 115), (0, 0, ANCHO_MINI, ALTO_MINI), 2, border_radius=6)

            resultado[mundo][nivel] = surf

            if guardar_en_disco:
                ruta_archivo = os.path.join(RUTA_MINIATURAS, f"nivel_{mundo}_{nivel}.png")
                try:
                    pygame.image.save(surf, ruta_archivo)
                except Exception:
                    pass

    return resultado


def obtener_miniaturas():
    """
    Retorna el diccionario de las 15 miniaturas en memoria (con caché).
    Si los archivos PNG ya existen en disco, los carga para máxima velocidad.
    """
    global _CACHE_MINIATURAS
    if _CACHE_MINIATURAS is not None:
        return _CACHE_MINIATURAS

    _CACHE_MINIATURAS = {}
    archivos_completos = True

    for mundo in (1, 2, 3):
        _CACHE_MINIATURAS[mundo] = {}
        for nivel in range(1, 6):
            ruta_img = os.path.join(RUTA_MINIATURAS, f"nivel_{mundo}_{nivel}.png")
            if os.path.isfile(ruta_img):
                try:
                    _CACHE_MINIATURAS[mundo][nivel] = pygame.image.load(ruta_img).convert_alpha()
                except Exception:
                    archivos_completos = False
            else:
                archivos_completos = False

    if not archivos_completos:
        _CACHE_MINIATURAS = generar_todas_las_miniaturas(guardar_en_disco=True)

    return _CACHE_MINIATURAS


def obtener_miniatura(mundo, nivel):
    """Retorna la miniatura específica de un mundo y nivel."""
    todos = obtener_miniaturas()
    return todos.get(mundo, {}).get(nivel)


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1, 1))
    mins = generar_todas_las_miniaturas(guardar_en_disco=True)
    print(f"¡Las 15 miniaturas fueron creadas y guardadas exitosamente en {RUTA_MINIATURAS}!")
