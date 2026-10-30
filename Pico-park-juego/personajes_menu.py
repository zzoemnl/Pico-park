"""
Módulo de Personajes Autónomos y Escenario para la Pantalla de Inicio - Pico Park.
Edición Navideña Pixel Art con Plataformas, Muros, Techo y Comportamiento Autónomo Independiente.

Gestiona:
1. Un escenario navideño 100% pixel art uniforme y acogedor para el Menú Principal:
   - Cielo nocturno/crepuscular en bandas con tramado clásico (dithering) de píxeles.
   - Nubes invernales pixel art y estrellas nítidas parpadeantes.
   - Montañas lejanas con picos nevados facetados, crestas de sombra y grietas pixel art.
   - Colina intermedia con siluetas de pinos y cabaña acogedora con ventana iluminada y chimenea humeante.
   - Dos árboles de Navidad principales profusamente decorados con follaje escalonado,
     mantos de nieve, esferas de colores, luces parpadeantes y estrellas doradas en la cima.
   - Plataformas de madera invernal con manto de nieve y carámbanos de hielo colgando,
     ubicadas a distintas alturas para permitir saltos, caminatas y rutas variadas.
   - Suelo con textura completa de nieve espesa, paquetes de regalo festivos y farol con luz cálida.
   - Viga de madera con guirnalda de pino en el techo y pilares en las paredes perfectamente integrados.
   - Copos de nieve pixel art (2x2, 4x4 y estrellas de 6x6) con oscilación natural.
2. Los 5 personajes originales de Pico Park con comportamientos 100% autónomos e independientes:
   - Distribución balanceada y orgánica: la mayoría camina por el suelo o salta sobre plataformas,
     mientras otros exploran las paredes, caminan por el techo o descansan.
   - Tiempos de decisión aleatorios y desfasados: nunca cambian de acción todos a la vez.
   - Repertorio variado: caminar, quedarse quieto observando, saltar, trepar paredes, bajar paredes,
     caminar por el techo boca abajo, saltar a plataformas, descolgarse, seguir a un compañero o apilarse.
   - Físicas reales continuas, sin teletransportes ni personajes trabados.
3. Botones del Menú Principal como elementos de interfaz limpios y desacoplados:
   - CERO colisiones físicas con los personajes: no caminan ni se posan sobre los botones.
   - Los botones permanecen 100% legibles, interactivos y con respuesta inmediata a clics y hover.
4. Organización de recursos lista para reemplazar accesorios futuros sin tocar código.
5. Total independencia de los niveles y mundos reales de juego.
"""

import math
import random
import pygame

from sprites import (
    dibujar_personaje,
    cargar_sprites,
    cargar_accesorio,
    aplicar_tinta,
    actualizar_temporizadores,
    obtener_estado,
    ANCHO as ANCHO_DEFECTO,
    ALTO as ALTO_DEFECTO,
)
from movimientos import (
    crear_personaje,
    ANCHO_HITBOX,
    ALTO_HITBOX,
    GRAVEDAD,
)

# Paleta de colores pixel art navideña coherente
COLOR_CIELO_1 = (22, 30, 56)      # Noche profunda
COLOR_CIELO_2 = (38, 54, 94)      # Azul crepúsculo
COLOR_CIELO_3 = (68, 92, 140)     # Índigo suave
COLOR_CIELO_4 = (128, 148, 188)   # Lavanda fría
COLOR_CIELO_5 = (198, 178, 192)   # Resplandor horizonte cálido

COLOR_MONTANA_LUZ = (82, 102, 142)
COLOR_MONTANA_SOMBRA = (58, 74, 108)
COLOR_NIEVE_PURA = (255, 255, 255)
COLOR_NIEVE_SOMBRA = (185, 205, 235)
COLOR_NIEVE_BASE = (215, 230, 248)

COLOR_PINO_OSCURO = (18, 52, 28)
COLOR_PINO_MEDIO = (28, 80, 44)
COLOR_PINO_CLARO = (44, 112, 62)

COLOR_MADERA_OSCURA = (42, 24, 14)
COLOR_MADERA_MEDIA = (72, 44, 26)
COLOR_MADERA_CLARA = (108, 68, 42)

COLOR_ESTRELLA_ORO = (255, 218, 50)
COLOR_ESTRELLA_BRILLO = (255, 245, 170)

# Pool de colores oficiales para los 5 personajes
COLOR_POOL = ["Celeste", "Violeta", "Amarillo", "Verde", "Rojo", "Naranja", "Rosa", "Azul", "Blanco"]

# Perfiles de personalidad variados para los 5 personajes
CONFIG_PERSONALIDADES = [
    {
        "tipo": "explorador", "vel": 3.8, "trepar_prob": 0.35, "plat_prob": 0.50, "salto_prob": 0.020, "pausa_prob": 0.20,
        "borde_parar": 0.15, "borde_girar": 0.30, "borde_saltar": 0.30, "borde_bajar": 0.25,
    },
    {
        "tipo": "curioso",    "vel": 3.6, "trepar_prob": 0.30, "plat_prob": 0.45, "salto_prob": 0.025, "pausa_prob": 0.28,
        "borde_parar": 0.30, "borde_girar": 0.35, "borde_saltar": 0.15, "borde_bajar": 0.20,
    },
    {
        "tipo": "saltarin",   "vel": 4.1, "trepar_prob": 0.25, "plat_prob": 0.65, "salto_prob": 0.055, "pausa_prob": 0.15,
        "borde_parar": 0.15, "borde_girar": 0.25, "borde_saltar": 0.50, "borde_bajar": 0.10,
    },
    {
        "tipo": "tranquilo",  "vel": 3.2, "trepar_prob": 0.15, "plat_prob": 0.35, "salto_prob": 0.012, "pausa_prob": 0.40,
        "borde_parar": 0.45, "borde_girar": 0.40, "borde_saltar": 0.05, "borde_bajar": 0.10,
    },
    {
        "tipo": "jugueton",   "vel": 3.9, "trepar_prob": 0.30, "plat_prob": 0.55, "salto_prob": 0.040, "pausa_prob": 0.22,
        "borde_parar": 0.20, "borde_girar": 0.25, "borde_saltar": 0.35, "borde_bajar": 0.20,
    },
]

# Límites del perímetro de desplazamiento
Y_SUELO = 650
Y_TECHO = 34
X_PARED_IZQ = 28
X_PARED_DER = 1252

# Plataformas del escenario a distintas alturas (ordenadas, atractivas y sin colisión con los botones)
# Los botones están centrados en X in [504, 776]. Las plataformas quedan en los laterales libres.
PLATAFORMAS_ESCENARIO = [
    pygame.Rect(130, 520, 150, 18),   # P1: Izquierda baja (accesible desde el suelo)
    pygame.Rect(44, 380, 130, 18),    # P2: Izquierda media (cerca de pared izquierda)
    pygame.Rect(260, 260, 130, 18),   # P3: Izquierda alta (hacia el centro-izq)
    pygame.Rect(1000, 520, 150, 18),  # P4: Derecha baja (accesible desde el suelo)
    pygame.Rect(1106, 380, 130, 18),  # P5: Derecha media (cerca de pared derecha)
    pygame.Rect(890, 260, 130, 18),   # P6: Derecha alta (hacia el centro-der)
]

# Geometría exacta de los botones principales del Menú (interfaz limpia)
ANCHO_BOTON_MENU = 272
ALTO_BOTON_MENU = 80
ESPACIO_BOTONES = 14
X_CENTRO_BOTONES = (1280 - ANCHO_BOTON_MENU) // 2  # 504
TOTAL_H_BOTONES = (ALTO_BOTON_MENU * 4) + (ESPACIO_BOTONES * 3)  # 362
Y_INICIO_BOTONES = (720 - TOTAL_H_BOTONES) // 2 + 35  # 214

BTN_JUGAR_RECT = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
BTN_PERSONAJES_RECT = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES + ALTO_BOTON_MENU + ESPACIO_BOTONES, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
BTN_CONFIG_RECT = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES + (ALTO_BOTON_MENU + ESPACIO_BOTONES) * 2, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
BTN_SALIR_RECT = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES + (ALTO_BOTON_MENU + ESPACIO_BOTONES) * 3, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)


def dibujar_personaje_rotado(pantalla, p):
    """
    Renderiza al personaje en cualquier orientación angular (0° suelo/plataforma, -90° pared izq,
    180° techo boca abajo, 90° pared der) manteniendo el accesorio perfectamente unido
    a la cabeza mediante composición previa.
    """
    angulo = p.get("angulo", 0.0)
    if abs(angulo) < 1.0:
        dibujar_personaje(pantalla, p)
        return

    actualizar_temporizadores(p)
    estado = obtener_estado(p)
    sprite_base = p["sprites"].get(estado, p["sprites"]["quieto"])

    col = p.get("color")
    if col is not None and col[:3] != (255, 255, 255):
        sprite = aplicar_tinta(sprite_base, col)
    else:
        sprite = sprite_base

    mirando_der = p.get("mirando_derecha", True)
    if not mirando_der:
        sprite = pygame.transform.flip(sprite, True, False)

    w_base, h_base = sprite.get_size()
    extra_h = 32
    comp = pygame.Surface((w_base, h_base + extra_h), pygame.SRCALPHA)
    comp.blit(sprite, (0, extra_h))

    acc_id = p.get("accesorio", "Ninguno")
    if acc_id and acc_id != "Ninguno":
        surf_acc = cargar_accesorio(acc_id)
        if surf_acc:
            if not mirando_der:
                surf_acc = pygame.transform.flip(surf_acc, True, False)
            if acc_id in ("Corona", "Gorro", "Gorra", "Sombrero"):
                x_acc = (w_base - surf_acc.get_width()) // 2
                y_acc = extra_h - surf_acc.get_height() + 8
            elif acc_id == "Anteojos":
                x_acc = (w_base - surf_acc.get_width()) // 2 + (2 if mirando_der else -2)
                y_acc = extra_h + 16
            elif acc_id in ("Moño", "Mono"):
                x_acc = (w_base - surf_acc.get_width()) // 2
                y_acc = extra_h + 46
            else:
                x_acc = (w_base - surf_acc.get_width()) // 2
                y_acc = extra_h - 5
            comp.blit(surf_acc, (x_acc, y_acc))

    rot_surf = pygame.transform.rotate(comp, angulo)
    rect_rot = rot_surf.get_rect(center=p["hitbox"].center)
    pantalla.blit(rot_surf, rect_rot)


class GestorPersonajesMenu:
    """
    Controla el escenario navideño interactivo 100% pixel art y la inteligencia artificial
    autónoma de los 5 personajes durante la pantalla de inicio de Pico Park.
    """

    def __init__(
        self,
        ancho=1280,
        alto=720,
        color_p1="Celeste",
        accesorio_p1="Ninguno",
        color_p2="Violeta",
        accesorio_p2="Ninguno"
    ):
        self.ancho = ancho
        self.alto = alto
        self.pantalla_rect = pygame.Rect(0, 0, ancho, alto)

        # 1. Geometría perimetral del escenario
        self.y_suelo = Y_SUELO
        self.y_techo = Y_TECHO
        self.x_pared_izq = X_PARED_IZQ
        self.x_pared_der = X_PARED_DER
        self.suelo = pygame.Rect(0, self.y_suelo, self.ancho, self.alto - self.y_suelo)

        # 2. Plataformas escalables a distintas alturas (CERO colisiones con botones)
        self.plataformas = list(PLATAFORMAS_ESCENARIO)
        self.bloques_decorativos = []

        # Botones del menú como interfaz pura (sin plataformas)
        self.btn_jugar = BTN_JUGAR_RECT
        self.btn_personajes = BTN_PERSONAJES_RECT
        self.btn_config = BTN_CONFIG_RECT
        self.btn_salir = BTN_SALIR_RECT
        self.botones = [self.btn_jugar, self.btn_personajes, self.btn_config, self.btn_salir]

        # 3. Distribución de colores y accesorios para los 5 personajes
        self.color_p1 = color_p1
        self.accesorio_p1 = accesorio_p1
        self.color_p2 = color_p2
        self.accesorio_p2 = accesorio_p2

        colores, accesorios = self._obtener_distribucion_personajes(
            color_p1, accesorio_p1, color_p2, accesorio_p2
        )
        self.colores = colores
        self.accesorios = accesorios

        # Posiciones y modos iniciales vivos, variados y naturales:
        # P0: Suelo izquierdo caminando
        # P1: En plataforma izquierda media
        # P2: Trepando pared izquierda
        # P3: En el techo boca abajo
        # P4: Descansando en suelo derecho
        posiciones_iniciales = [
            (210, self.y_suelo - ALTO_HITBOX, "suelo", 0.0, None),
            (PLATAFORMAS_ESCENARIO[1].centerx - 23, PLATAFORMAS_ESCENARIO[1].top - ALTO_HITBOX, "plataforma", 0.0, PLATAFORMAS_ESCENARIO[1]),
            (self.x_pared_izq, 290, "pared_izq", -90.0, None),
            (730, self.y_techo, "techo", 180.0, None),
            (980, self.y_suelo - ALTO_HITBOX, "suelo", 0.0, None),
        ]

        self.personajes = []
        self.ai_estados = []

        # Tiempos de decisión deliberadamente desfasados para evitar cambios simultáneos
        tiempos_desfasados = [45, 75, 30, 95, 60]

        for i in range(5):
            x, y, sup_ini, ang_ini, plat_ini = posiciones_iniciales[i]
            col = colores[i]
            acc = accesorios[i]
            conf = CONFIG_PERSONALIDADES[i]

            p = crear_personaje(x, y, color_carpeta=col, accesorio=acc)
            p["velocidad_mov"] = conf["vel"]
            p["fuerza_salto"] = -15.5
            p["superficie"] = sup_ini
            p["plat_actual"] = plat_ini
            p["ignorar_plat"] = None
            p["cooldown_ignorar_plat"] = 0
            p["angulo"] = ang_ini
            p["angulo_objetivo"] = ang_ini
            p["en_suelo"] = (sup_ini in ("suelo", "plataforma"))
            self.personajes.append(p)

            ai = {
                "idx": i,
                "estado": "trepar" if sup_ini in ("pared_izq", "pared_der") else ("caminar_techo" if sup_ini == "techo" else ("quieto" if i == 4 else "caminar")),
                "tiempo": tiempos_desfasados[i],
                "direccion": 1 if i in (0, 3) else (-1 if i in (1, 2) else 0),
                "frames_bloqueado": 0,
                "pos_x_anterior": x,
                "pos_y_anterior": y,
                "personalidad": conf["tipo"],
                "datos_pers": conf,
                "intentar_salto": False,
                "cooldown_cambio_dir": 0,
                "en_borde": False,
            }
            self.ai_estados.append(ai)

        self.p1 = self.personajes[0]
        self.p2 = self.personajes[1]
        self.ai1 = self.ai_estados[0]
        self.ai2 = self.ai_estados[1]

        # 4. Sistema dinámico de copos de nieve pixel art (dos capas para sensación de profundidad)
        self.copos_nieve = []
        # Capa lejana (50 copos lentos y tenues)
        for _ in range(50):
            self.copos_nieve.append({
                "x": random.uniform(0, self.ancho),
                "y": random.uniform(0, self.alto),
                "vel_y": random.uniform(0.7, 1.3),
                "vel_x": random.uniform(-0.25, 0.25),
                "tamano": random.choice([2, 2, 2, 4]),
                "fase": random.uniform(0, math.pi * 2),
                "frecuencia": random.uniform(0.015, 0.03),
                "capa": "fondo",
            })
        # Capa cercana (35 copos activos y nítidos)
        for _ in range(35):
            self.copos_nieve.append({
                "x": random.uniform(0, self.ancho),
                "y": random.uniform(0, self.alto),
                "vel_y": random.uniform(1.4, 2.5),
                "vel_x": random.uniform(-0.35, 0.35),
                "tamano": random.choice([2, 4, 4, 6]),
                "fase": random.uniform(0, math.pi * 2),
                "frecuencia": random.uniform(0.02, 0.04),
                "capa": "frente",
            })

        # 5. Nubes pixel art con desplazamiento suave por el cielo
        self.nubes = self._generar_nubes()

        # 6. Partículas de humo animadas para la chimenea de la cabaña
        self.particulas_humo = self._generar_humo_chimenea()

        # 7. Destellos mágicos ambientales en la nieve
        self.destellos_nieve = self._generar_destellos_nieve()

        # 8. Luces navideñas festivas parpadeantes
        self.luces_arboles = self._generar_luces_navidenas()

        # 9. Fondo 100% pixel art generado en resolución retro interna (640x360) y escalado entero 2x
        self.fondo_estatico = self._generar_fondo_estatico()

        self.contador_frames = 0

    def _crear_superficie_nube_pixel(self, nw_retro, nh_retro):
        """Crea una nube pixel art auténtica pre-renderizada en escala 2x."""
        surf_retro = pygame.Surface((nw_retro, nh_retro), pygame.SRCALPHA)
        col_clara = (228, 238, 250)
        col_sombra = (165, 185, 215)
        for cy in range(nh_retro):
            prog = cy / float(max(1, nh_retro - 1))
            ancho_fila = int((nw_retro // 2) * math.sin(prog * math.pi))
            col = col_sombra if cy > nh_retro // 2 else col_clara
            for cx in range(nw_retro // 2 - ancho_fila, nw_retro // 2 + ancho_fila):
                if 0 <= cx < nw_retro:
                    surf_retro.set_at((cx, cy), col)
        return pygame.transform.scale(surf_retro, (nw_retro * 2, nh_retro * 2))

    def _generar_nubes(self):
        """Genera las 4 nubes pixel art del cielo con velocidades y profundidades distintas."""
        configs = [
            {"nw": 75, "nh": 18, "y": 140, "vel": 0.22, "x": 80.0},
            {"nw": 85, "nh": 20, "y": 180, "vel": 0.32, "x": 420.0},
            {"nw": 65, "nh": 15, "y": 100, "vel": 0.16, "x": 780.0},
            {"nw": 50, "nh": 12, "y": 215, "vel": 0.26, "x": 1060.0},
        ]
        nubes = []
        for c in configs:
            surf_nube = self._crear_superficie_nube_pixel(c["nw"], c["nh"])
            nubes.append({
                "surf": surf_nube,
                "x": c["x"],
                "y": c["y"],
                "vel": c["vel"],
                "w": c["nw"] * 2,
                "h": c["nh"] * 2,
            })
        return nubes

    def _generar_humo_chimenea(self):
        """Genera partículas cíclicas de humo pixel art para la chimenea de la cabaña."""
        particulas = []
        for i in range(5):
            particulas.append({
                "progreso": i * 20,
            })
        return particulas

    def _generar_destellos_nieve(self):
        """Posiciones fijas de destellos sutiles sobre la nieve de las montañas y pinos."""
        return [
            {"x": 240, "y": 530, "fase": 10},
            {"x": 360, "y": 590, "fase": 35},
            {"x": 1030, "y": 535, "fase": 60},
            {"x": 1140, "y": 595, "fase": 85},
            {"x": 150, "y": 485, "fase": 20},
            {"x": 1110, "y": 485, "fase": 70},
            {"x": 60, "y": 645, "fase": 45},
            {"x": 1220, "y": 645, "fase": 95},
        ]

    def _generar_luces_navidenas(self):
        """Genera las posiciones y colores festivos de las luces navideñas pixel art."""
        luces = []
        colores_luces = [
            (255, 60, 60),    # Rojo rubí
            (255, 215, 50),   # Oro cálido
            (60, 225, 100),   # Verde esmeralda
            (60, 210, 255),   # Celeste eléctrico
            (255, 90, 190),   # Magenta festivo
            (255, 255, 255),  # Blanco hielo
        ]

        # Árbol izquierdo
        coords_izq = [
            (185, 415), (150, 455), (215, 460), (130, 500), (185, 505), (235, 500),
            (110, 555), (160, 560), (210, 560), (255, 550), (95, 610), (145, 615),
            (190, 618), (235, 615), (275, 610)
        ]
        for idx, (lx, ly) in enumerate(coords_izq):
            luces.append({
                "x": lx, "y": ly,
                "color": colores_luces[idx % len(colores_luces)],
                "fase": idx * 7,
            })

        # Árbol derecho
        coords_der = [
            (1095, 415), (1060, 455), (1125, 460), (1040, 500), (1095, 505), (1145, 500),
            (1020, 555), (1070, 560), (1120, 560), (1165, 550), (1005, 610), (1055, 615),
            (1100, 618), (1145, 615), (1185, 610)
        ]
        for idx, (lx, ly) in enumerate(coords_der):
            luces.append({
                "x": lx, "y": ly,
                "color": colores_luces[(idx + 2) % len(colores_luces)],
                "fase": idx * 7 + 11,
            })

        # Luces festivas en la guirnalda del techo (y=26)
        for idx, lx in enumerate(range(70, self.ancho - 70, 60)):
            luces.append({
                "x": lx, "y": 27,
                "color": colores_luces[(idx * 2) % len(colores_luces)],
                "fase": idx * 5 + 3,
            })

        return luces

    def _obtener_distribucion_personajes(self, col1, acc1, col2, acc2):
        """Calcula 5 colores y accesorios totalmente distintos sin repetición."""
        usados = [col1, col2]
        restantes = [c for c in COLOR_POOL if c not in usados]
        colores = [col1, col2, restantes[0], restantes[1], restantes[2]]

        acc_predeterminados = ["Gorro", "Anteojos", "Sombrero", "Corona", "Moño"]
        acc_usados = [acc1, acc2]
        acc_restantes = [a for a in acc_predeterminados if a not in acc_usados]

        accesorios = [
            acc1,
            acc2,
            acc_restantes[0] if len(acc_restantes) > 0 else "Gorro",
            acc_restantes[1] if len(acc_restantes) > 1 else "Anteojos",
            acc_restantes[2] if len(acc_restantes) > 2 else "Sombrero",
        ]
        return colores, accesorios

    def sincronizar_personalizacion(self, color_p1, accesorio_p1, color_p2, accesorio_p2):
        """Actualiza dinámicamente colores y accesorios si el jugador los cambió en opciones."""
        hubo_cambio = False
        if color_p1 != self.color_p1 or accesorio_p1 != self.accesorio_p1:
            self.color_p1 = color_p1
            self.accesorio_p1 = accesorio_p1
            hubo_cambio = True

        if color_p2 != self.color_p2 or accesorio_p2 != self.accesorio_p2:
            self.color_p2 = color_p2
            self.accesorio_p2 = accesorio_p2
            hubo_cambio = True

        if hubo_cambio:
            nuevos_colores, nuevos_accesorios = self._obtener_distribucion_personajes(
                self.color_p1, self.accesorio_p1, self.color_p2, self.accesorio_p2
            )
            self.colores = nuevos_colores
            self.accesorios = nuevos_accesorios

            for i in range(5):
                col = nuevos_colores[i]
                acc = nuevos_accesorios[i]
                self.personajes[i]["sprites"] = cargar_sprites(col)
                self.personajes[i]["accesorio"] = acc

    def _generar_fondo_estatico(self):
        """
        Genera el escenario navideño completo con estética 100% pixel art auténtica.
        Renderizado en cuadrícula retro 640x360 y escalado con algoritmo de vecino más próximo a 1280x720.
        """
        w, h = 640, 360
        surf = pygame.Surface((w, h))

        # 1. Cielo pixel art en 5 bandas con tramado dithered
        bandas = [
            (0, 60, COLOR_CIELO_1),
            (60, 120, COLOR_CIELO_2),
            (120, 180, COLOR_CIELO_3),
            (180, 240, COLOR_CIELO_4),
            (240, 360, COLOR_CIELO_5),
        ]
        for y1, y2, col in bandas:
            pygame.draw.rect(surf, col, (0, y1, w, y2 - y1))

        # Dithering checkerboard entre bandas
        for i in range(len(bandas) - 1):
            yt = bandas[i][1]
            c_up = bandas[i][2]
            c_dn = bandas[i + 1][2]
            for y in range(yt - 2, yt + 2):
                for x in range(w):
                    if y == yt - 2 and x % 4 == 0:
                        surf.set_at((x, y), c_dn)
                    elif y == yt - 1 and (x + y) % 2 == 0:
                        surf.set_at((x, y), c_dn)
                    elif y == yt and (x + y) % 2 == 0:
                        surf.set_at((x, y), c_up)
                    elif y == yt + 1 and x % 4 == 0:
                        surf.set_at((x, y), c_up)

        # Estrellas pixel art en el cielo
        rnd_estrellas = random.Random(1234)
        for _ in range(40):
            sx = rnd_estrellas.randint(12, w - 12)
            sy = rnd_estrellas.randint(8, 115)
            surf.set_at((sx, sy), (255, 255, 255))
            if rnd_estrellas.random() < 0.25:
                surf.set_at((sx + 1, sy), (255, 240, 180))
                surf.set_at((sx, sy + 1), (255, 240, 180))

        # 2. Montañas lejanas con picos nevados y sombreado pixel art
        picos = [(90, 115, 160), (220, 90, 180), (350, 125, 150), (460, 100, 170), (560, 120, 160)]
        y_base_montana = 260
        for px, py, ancho_m in picos:
            for y in range(py, y_base_montana):
                prog = (y - py) / float(y_base_montana - py)
                half = int((ancho_m // 2) * prog)
                for x in range(px - half, px):
                    surf.set_at((x, y), COLOR_MONTANA_LUZ)
                for x in range(px, px + half + 1):
                    surf.set_at((x, y), COLOR_MONTANA_SOMBRA)
                # Capuchón de nieve en la cima
                if prog < 0.28:
                    for x in range(px - half, px):
                        surf.set_at((x, y), COLOR_NIEVE_PURA)
                    for x in range(px, px + half + 1):
                        surf.set_at((x, y), COLOR_NIEVE_SOMBRA)

        # 3. Colina intermedia nevada con bosque de pinos
        for x in range(w):
            y_col = int(245 + 16 * math.sin(x * 0.012 + 0.5))
            for y in range(y_col, 360):
                surf.set_at((x, y), (175, 195, 225))

        # Siluetas de pinos en la colina lejana
        for px_col in range(40, w - 40, 28):
            py_col = int(245 + 16 * math.sin(px_col * 0.012 + 0.5))
            pygame.draw.polygon(surf, COLOR_PINO_OSCURO, [(px_col, py_col - 14), (px_col - 5, py_col), (px_col + 5, py_col)])
            surf.set_at((px_col, py_col - 14), COLOR_NIEVE_PURA)

        # Cabaña navideña acogedora
        cx_cab, cy_cab = 175, 242
        pygame.draw.rect(surf, COLOR_MADERA_OSCURA, (cx_cab, cy_cab, 32, 22))
        for ly in range(cy_cab + 4, cy_cab + 22, 4):
            pygame.draw.line(surf, COLOR_MADERA_MEDIA, (cx_cab + 1, ly), (cx_cab + 30, ly), 1)
        # Techo con nieve espesa
        pts_techo = [(cx_cab - 4, cy_cab), (cx_cab + 16, cy_cab - 12), (cx_cab + 36, cy_cab)]
        pygame.draw.polygon(surf, COLOR_NIEVE_PURA, pts_techo)
        pygame.draw.line(surf, COLOR_NIEVE_SOMBRA, pts_techo[0], pts_techo[2], 1)
        # Ventana iluminada
        pygame.draw.rect(surf, (255, 215, 60), (cx_cab + 6, cy_cab + 6, 8, 8))
        pygame.draw.line(surf, COLOR_MADERA_OSCURA, (cx_cab + 10, cy_cab + 6), (cx_cab + 10, cy_cab + 13), 1)
        pygame.draw.line(surf, COLOR_MADERA_OSCURA, (cx_cab + 6, cy_cab + 10), (cx_cab + 13, cy_cab + 10), 1)
        # Chimenea (el humo se renderiza dinámicamente)
        pygame.draw.rect(surf, (90, 95, 105), (cx_cab + 22, cy_cab - 14, 6, 10))

        # 4. Árboles de Navidad principales profusamente decorados
        def _dibujar_arbol(cx, cy_base, w_arbol, h_arbol):
            w_t = max(4, w_arbol // 7)
            h_t = max(6, h_arbol // 8)
            pygame.draw.rect(surf, COLOR_MADERA_OSCURA, (cx - w_t // 2, cy_base - h_t, w_t, h_t))
            pygame.draw.rect(surf, COLOR_MADERA_MEDIA, (cx - w_t // 2 + 1, cy_base - h_t, w_t - 2, h_t))

            num_tiers = 4
            tier_h = (h_arbol - h_t) // num_tiers
            for t in range(num_tiers):
                y_b = cy_base - h_t - (t * (tier_h - 2))
                y_top = y_b - tier_h - 4
                ancho_t = int(w_arbol * (1.0 - t * 0.18))

                for y in range(y_top, y_b):
                    prog = (y - y_top) / float(max(1, y_b - y_top))
                    span = int((ancho_t // 2) * prog)
                    for x in range(cx - span, cx):
                        col = COLOR_PINO_CLARO if (x - cx) % 3 == 0 else COLOR_PINO_MEDIO
                        surf.set_at((x, y), col)
                    for x in range(cx, cx + span + 1):
                        col = COLOR_PINO_MEDIO if (x - cx) % 3 == 0 else COLOR_PINO_OSCURO
                        surf.set_at((x, y), col)
                    # Nieve en el follaje
                    if y < y_top + 3:
                        for x in range(cx - span, cx + span + 1):
                            surf.set_at((x, y), COLOR_NIEVE_PURA)
                    elif y < y_top + 5:
                        for x in range(cx - span, cx + span + 1):
                            if (x + y) % 2 == 0:
                                surf.set_at((x, y), COLOR_NIEVE_SOMBRA)

                # Esferas navideñas decorativas
                if t < 3:
                    colores_baubles = [(235, 50, 60), (255, 215, 40), (50, 200, 240), (210, 80, 220)]
                    bx1 = cx - ancho_t // 3
                    bx2 = cx + ancho_t // 4
                    by = y_b - 3
                    c1 = colores_baubles[(t * 2) % len(colores_baubles)]
                    c2 = colores_baubles[(t * 2 + 1) % len(colores_baubles)]
                    surf.set_at((bx1, by), c1)
                    surf.set_at((bx1, by - 1), (255, 255, 255))
                    surf.set_at((bx2, by - 2), c2)
                    surf.set_at((bx2, by - 3), (255, 255, 255))

            # Gran Estrella dorada pixel art
            y_est = cy_base - h_arbol
            for dx, dy in [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                surf.set_at((cx + dx, y_est + dy), COLOR_ESTRELLA_ORO)
            surf.set_at((cx, y_est), COLOR_ESTRELLA_BRILLO)

        # Árboles laterales
        _dibujar_arbol(cx=90, cy_base=325, w_arbol=95, h_arbol=145)
        _dibujar_arbol(cx=32, cy_base=325, w_arbol=60, h_arbol=100)
        _dibujar_arbol(cx=550, cy_base=325, w_arbol=95, h_arbol=145)
        _dibujar_arbol(cx=608, cy_base=325, w_arbol=60, h_arbol=100)

        # 5. Suelo nevado (y = 325 a 360)
        y_suelo = 325
        pygame.draw.rect(surf, (165, 190, 220), (0, y_suelo, w, h - y_suelo))
        pygame.draw.rect(surf, COLOR_NIEVE_PURA, (0, y_suelo - 2, w, 6))
        pygame.draw.line(surf, (245, 250, 255), (0, y_suelo - 2), (w, y_suelo - 2), 1)
        pygame.draw.line(surf, COLOR_NIEVE_SOMBRA, (0, y_suelo + 4), (w, y_suelo + 4), 1)
        for x in range(4, w, 6):
            if x % 12 == 0:
                surf.set_at((x, y_suelo + 8), COLOR_NIEVE_PURA)
                surf.set_at((x + 1, y_suelo + 9), COLOR_NIEVE_SOMBRA)

        # Paquetes de regalo pixel art bajo los árboles
        pygame.draw.rect(surf, (225, 45, 50), (60, y_suelo - 12, 13, 12))
        pygame.draw.line(surf, COLOR_ESTRELLA_ORO, (66, y_suelo - 12), (66, y_suelo - 1), 1)
        pygame.draw.line(surf, COLOR_ESTRELLA_ORO, (60, y_suelo - 7), (72, y_suelo - 7), 1)

        pygame.draw.rect(surf, (50, 170, 230), (120, y_suelo - 9, 11, 9))
        pygame.draw.line(surf, COLOR_NIEVE_PURA, (125, y_suelo - 9), (125, y_suelo - 1), 1)

        pygame.draw.rect(surf, (250, 205, 40), (510, y_suelo - 11, 12, 11))
        pygame.draw.line(surf, (30, 140, 60), (515, y_suelo - 11), (515, y_suelo - 1), 1)

        # Farolito de madera cálido
        fx = 465
        pygame.draw.line(surf, COLOR_MADERA_OSCURA, (fx, y_suelo - 22), (fx, y_suelo), 2)
        pygame.draw.rect(surf, (255, 230, 80), (fx - 3, y_suelo - 22, 6, 6))
        surf.set_at((fx, y_suelo - 20), (255, 255, 255))
        pygame.draw.rect(surf, COLOR_NIEVE_PURA, (fx - 4, y_suelo - 24, 8, 2))

        # 6. Plataformas de madera y nieve pixel art (coordenadas escaladas a 640x360)
        def _dibujar_plat_pixel(rx, ry, rw, rh):
            pygame.draw.rect(surf, COLOR_MADERA_OSCURA, (rx, ry, rw, rh))
            pygame.draw.rect(surf, COLOR_MADERA_MEDIA, (rx + 1, ry + 2, rw - 2, rh - 3))
            for x in range(rx + 4, rx + rw - 4, 8):
                surf.set_at((x, ry + 4), COLOR_MADERA_CLARA)
                surf.set_at((x + 1, ry + 5), COLOR_MADERA_CLARA)

            pygame.draw.rect(surf, COLOR_NIEVE_PURA, (rx - 1, ry - 3, rw + 2, 4))
            pygame.draw.line(surf, COLOR_NIEVE_SOMBRA, (rx, ry + 1), (rx + rw, ry + 1), 1)

            for ix in range(rx + 6, rx + rw - 6, 10):
                h_icicle = ((ix * 7) % 3) + 2
                for dy in range(h_icicle):
                    col_ice = COLOR_NIEVE_PURA if dy == 0 else (180, 215, 245)
                    surf.set_at((ix, ry + rh + dy), col_ice)

        # Dibujar las 6 plataformas
        for p in PLATAFORMAS_ESCENARIO:
            _dibujar_plat_pixel(p.x // 2, p.y // 2, p.width // 2, p.height // 2)

        # 7. Viga del techo y guirnalda pixel art
        pygame.draw.rect(surf, COLOR_MADERA_OSCURA, (0, 0, w, 12))
        pygame.draw.line(surf, COLOR_MADERA_MEDIA, (0, 1), (w, 1), 1)
        pygame.draw.line(surf, (26, 14, 8), (0, 11), (w, 11), 1)
        for gx in range(0, w, 12):
            pts_g = [(gx, 8), (gx + 6, 15), (gx + 12, 8)]
            pygame.draw.polygon(surf, COLOR_PINO_OSCURO, pts_g)
            surf.set_at((gx + 6, 13), COLOR_PINO_MEDIO)
            surf.set_at((gx + 6, 14), COLOR_PINO_CLARO)
        pygame.draw.rect(surf, COLOR_NIEVE_PURA, (0, 15, w, 2))

        # Pilares en paredes laterales
        pygame.draw.rect(surf, COLOR_MADERA_OSCURA, (0, 0, 14, y_suelo))
        pygame.draw.line(surf, COLOR_MADERA_MEDIA, (1, 0), (1, y_suelo), 1)
        pygame.draw.rect(surf, COLOR_NIEVE_PURA, (12, 0, 2, y_suelo))

        pygame.draw.rect(surf, COLOR_MADERA_OSCURA, (w - 14, 0, 14, y_suelo))
        pygame.draw.line(surf, COLOR_MADERA_MEDIA, (w - 2, 0), (w - 2, y_suelo), 1)
        pygame.draw.rect(surf, COLOR_NIEVE_PURA, (w - 14, 0, 2, y_suelo))

        # Moños festivos en las esquinas
        for cx_m in (14, w - 14):
            pygame.draw.circle(surf, (225, 45, 50), (cx_m, 14), 4)
            surf.set_at((cx_m, 14), COLOR_ESTRELLA_ORO)

        # Escalar 2x mediante algoritmo de vecino más próximo (nearest-neighbor)
        return pygame.transform.scale(surf, (self.ancho, self.alto))

    def _fijar_direccion_ai(self, ai, nueva_dir, cooldown=25, forzar=False):
        """
        Asigna la nueva dirección del personaje respetando el tiempo mínimo
        entre cambios de dirección para evitar decisiones contradictorias consecutivas.
        """
        dir_actual = ai.get("direccion", 0)
        if nueva_dir == dir_actual:
            return
        if not forzar and dir_actual != 0 and nueva_dir != 0 and nueva_dir == -dir_actual:
            if ai.get("cooldown_cambio_dir", 0) > 0:
                return
        ai["direccion"] = nueva_dir
        if nueva_dir != 0:
            ai["cooldown_cambio_dir"] = max(ai.get("cooldown_cambio_dir", 0), cooldown)

    def _anticipar_borde_plataforma(self, idx):
        """
        Sistema de anticipación de bordes para plataformas.
        Detecta cuándo el personaje se aproxima al final de una plataforma y elige
        una acción coherente y deliberada (detenerse, darse vuelta, saltar o bajar),
        evitando cualquier tipo de vibración o cambio de dirección frame a frame.
        """
        p = self.personajes[idx]
        ai = self.ai_estados[idx]
        plat = p.get("plat_actual")
        if not plat or p["superficie"] != "plataforma":
            ai["en_borde"] = False
            return

        hb = p["hitbox"]
        dir_act = ai["direccion"]
        conf = ai["datos_pers"]

        # Margen de anticipación desde el borde (en píxeles)
        margen = 8

        # Verificar proximidad al borde en la dirección de avance
        cerca_borde = False
        lado_borde = None

        if dir_act > 0:
            dist = plat.right - hb.right
            if dist <= margen:
                cerca_borde = True
                lado_borde = "der"
        elif dir_act < 0:
            dist = hb.left - plat.left
            if dist <= margen:
                cerca_borde = True
                lado_borde = "izq"

        if not cerca_borde:
            # Si no está en el borde o se está alejando, resetear flag
            if dir_act > 0 and hb.left > plat.left + 16:
                ai["en_borde"] = False
            elif dir_act < 0 and hb.right < plat.right - 16:
                ai["en_borde"] = False
            return

        # Si ya está procesando una acción en este borde con cooldown activo, mantenerla
        if ai.get("en_borde", False) and ai.get("cooldown_cambio_dir", 0) > 0:
            return

        # Transición natural si la plataforma está adyacente a una pared perimetral
        if plat.right >= 1230 and lado_borde == "der":
            if random.random() < conf.get("trepar_prob", 0.35) + 0.35:
                p["superficie"] = "pared_der"
                p["plat_actual"] = None
                p["angulo_objetivo"] = 90.0
                hb.right = self.x_pared_der
                p["vel_x"] = 0
                p["vel_y"] = -p["velocidad_mov"]
                p["en_suelo"] = False
                ai["estado"] = "trepar"
                ai["direccion"] = -1 if random.random() < 0.6 else 1
                ai["tiempo"] = random.randint(45, 95)
                ai["cooldown_cambio_dir"] = 30
                ai["en_borde"] = False
                return

        if plat.left <= 50 and lado_borde == "izq":
            if random.random() < conf.get("trepar_prob", 0.35) + 0.35:
                p["superficie"] = "pared_izq"
                p["plat_actual"] = None
                p["angulo_objetivo"] = -90.0
                hb.left = self.x_pared_izq
                p["vel_x"] = 0
                p["vel_y"] = -p["velocidad_mov"]
                p["en_suelo"] = False
                ai["estado"] = "trepar"
                ai["direccion"] = -1 if random.random() < 0.6 else 1
                ai["tiempo"] = random.randint(45, 95)
                ai["cooldown_cambio_dir"] = 30
                ai["en_borde"] = False
                return

        ai["en_borde"] = True
        rnd = random.random()
        p_parar = conf.get("borde_parar", 0.25)
        p_girar = p_parar + conf.get("borde_girar", 0.35)
        p_saltar = p_girar + conf.get("borde_saltar", 0.25)

        # 1. DETENERSE TRANQUILAMENTE A OBSERVAR EL BORDE
        if rnd < p_parar:
            ai["estado"] = "quieto"
            self._fijar_direccion_ai(ai, 0, cooldown=35)
            p["vel_x"] = 0
            p["moviendo"] = False
            ai["tiempo"] = random.randint(40, 90)
            # Mira hacia el borde
            p["mirando_derecha"] = (lado_borde == "der")
            if lado_borde == "der":
                hb.right = min(hb.right, plat.right - 2)
            else:
                hb.left = max(hb.left, plat.left + 2)

        # 2. DARSE VUELTA Y CAMINAR HACIA EL INTERIOR
        elif rnd < p_girar:
            nueva_dir = -1 if lado_borde == "der" else 1
            ai["estado"] = "caminar"
            self._fijar_direccion_ai(ai, nueva_dir, cooldown=30, forzar=True)
            p["mirando_derecha"] = (nueva_dir > 0)
            ai["tiempo"] = random.randint(45, 100)
            if lado_borde == "der":
                hb.right = min(hb.right, plat.right - 4)
            else:
                hb.left = max(hb.left, plat.left + 4)

        # 3. SALTAR HACIA OTRA PLATAFORMA O ADELANTE
        elif rnd < p_saltar:
            salto_dir = 1 if lado_borde == "der" else -1
            self._fijar_direccion_ai(ai, salto_dir, cooldown=30, forzar=True)
            ai["intentar_salto"] = True
            ai["tiempo"] = random.randint(30, 60)
            p["mirando_derecha"] = (salto_dir > 0)

        # 4. BAJAR / DESCOLGARSE DE LA PLATAFORMA
        else:
            bajar_dir = 1 if lado_borde == "der" else -1
            p["superficie"] = "aire"
            p["plat_actual"] = None
            p["ignorar_plat"] = plat
            p["cooldown_ignorar_plat"] = 35
            p["vel_x"] = bajar_dir * (p["velocidad_mov"] * 0.75)
            p["vel_y"] = 2.0
            p["en_suelo"] = False
            ai["estado"] = "caminar"
            self._fijar_direccion_ai(ai, bajar_dir, cooldown=30, forzar=True)
            p["mirando_derecha"] = (bajar_dir > 0)
            ai["tiempo"] = random.randint(35, 70)
            ai["en_borde"] = False

    def _decidir_proxima_accion(self, idx):
        """
        Genera decisiones autónomas, independientes y variadas para cada personaje.
        Equilibra el uso del suelo, plataformas, paredes y techo de forma orgánica.
        """
        p = self.personajes[idx]
        ai = self.ai_estados[idx]
        sup = p["superficie"]
        conf = ai["datos_pers"]
        rnd = random.random()

        # 1. SI ESTÁ EN EL SUELO
        if sup == "suelo":
            if rnd < conf["pausa_prob"]:
                ai["estado"] = "quieto"
                self._fijar_direccion_ai(ai, 0, cooldown=25)
                ai["tiempo"] = random.randint(40, 120)
                if random.random() < 0.4:
                    p["mirando_derecha"] = not p.get("mirando_derecha", True)
            elif rnd < 0.65:
                ai["estado"] = "caminar"
                # Dirección de exploración amplia para recorrer todo el escenario
                if p["hitbox"].centerx < 120:
                    d_exp = 1 if random.random() < 0.60 else -1
                elif p["hitbox"].centerx > 1160:
                    d_exp = -1 if random.random() < 0.60 else 1
                else:
                    d_exp = 1 if random.random() < 0.50 else -1
                self._fijar_direccion_ai(ai, d_exp, cooldown=25)
                ai["tiempo"] = random.randint(50, 140)
                if random.random() < conf["salto_prob"] * 12:
                    ai["intentar_salto"] = True
            elif rnd < 0.85:
                # Intentar saltar hacia una plataforma baja cercana
                ai["estado"] = "caminar"
                if p["hitbox"].centerx < 500:
                    d_salto = 1 if p["hitbox"].centerx < PLATAFORMAS_ESCENARIO[0].centerx else -1
                else:
                    d_salto = 1 if p["hitbox"].centerx < PLATAFORMAS_ESCENARIO[3].centerx else -1
                self._fijar_direccion_ai(ai, d_salto, cooldown=25)
                ai["intentar_salto"] = True
                ai["tiempo"] = random.randint(35, 75)
            else:
                # Socializar con compañeros en el suelo
                amigos_suelo = [j for j in range(5) if j != idx and self.personajes[j]["superficie"] == "suelo"]
                if amigos_suelo:
                    target = random.choice(amigos_suelo)
                    p_target = self.personajes[target]
                    dist_x = p_target["hitbox"].centerx - p["hitbox"].centerx
                    ai["estado"] = "caminar"
                    self._fijar_direccion_ai(ai, 1 if dist_x > 0 else -1, cooldown=25)
                    ai["tiempo"] = random.randint(40, 80)
                    if abs(dist_x) < 70 and random.random() < 0.4:
                        ai["intentar_salto"] = True
                else:
                    ai["estado"] = "caminar"
                    self._fijar_direccion_ai(ai, 1 if random.random() < 0.5 else -1, cooldown=25)
                    ai["tiempo"] = random.randint(40, 90)

        # 2. SI ESTÁ EN UNA PLATAFORMA
        elif sup == "plataforma":
            plat = p.get("plat_actual")
            if plat:
                dist_izq = p["hitbox"].centerx - plat.left
                dist_der = plat.right - p["hitbox"].centerx
                # Favorecer dirección hacia el interior si está en los laterales
                if dist_izq < 24:
                    dir_favorita = 1
                elif dist_der < 24:
                    dir_favorita = -1
                else:
                    dir_favorita = 1 if random.random() < 0.5 else -1
            else:
                dir_favorita = 1 if random.random() < 0.5 else -1

            if rnd < 0.30:
                ai["estado"] = "quieto"
                self._fijar_direccion_ai(ai, 0, cooldown=25)
                ai["tiempo"] = random.randint(35, 90)
                if random.random() < 0.4:
                    p["mirando_derecha"] = not p.get("mirando_derecha", True)
            elif rnd < 0.70:
                # Caminar por la plataforma
                ai["estado"] = "caminar"
                self._fijar_direccion_ai(ai, dir_favorita, cooldown=25)
                ai["tiempo"] = random.randint(45, 110)
            elif rnd < 0.88:
                # Saltar hacia una plataforma superior o pared
                ai["estado"] = "caminar"
                self._fijar_direccion_ai(ai, dir_favorita, cooldown=25)
                ai["intentar_salto"] = True
                ai["tiempo"] = random.randint(30, 60)
            else:
                # Bajar/descolgarse de la plataforma hacia el suelo limpiamente
                bajar_dir = dir_favorita
                p["superficie"] = "aire"
                p["plat_actual"] = None
                p["ignorar_plat"] = plat
                p["cooldown_ignorar_plat"] = 35
                p["vel_x"] = bajar_dir * (p["velocidad_mov"] * 0.75)
                p["vel_y"] = 2.0
                p["en_suelo"] = False
                ai["estado"] = "caminar"
                self._fijar_direccion_ai(ai, bajar_dir, cooldown=30, forzar=True)
                ai["tiempo"] = random.randint(35, 70)
                ai["en_borde"] = False

        # 3. SI ESTÁ EN UNA PARED
        elif sup in ("pared_izq", "pared_der"):
            lado = sup
            if rnd < 0.20:
                ai["estado"] = "quieto"
                ai["direccion"] = 0
                ai["tiempo"] = random.randint(25, 60)
                ai["cooldown_cambio_dir"] = 20
            elif rnd < 0.50:
                # Trepar hacia arriba
                ai["estado"] = "trepar"
                ai["direccion"] = -1
                ai["tiempo"] = random.randint(40, 90)
                ai["cooldown_cambio_dir"] = 20
            elif rnd < 0.75:
                # Bajar hacia el suelo
                ai["estado"] = "trepar"
                ai["direccion"] = 1
                ai["tiempo"] = random.randint(40, 90)
                ai["cooldown_cambio_dir"] = 20
            else:
                # Salto acrobático impulsándose hacia plataformas o centro
                p["superficie"] = "aire"
                p["plat_actual"] = None
                p["ignorar_plat"] = None
                p["cooldown_ignorar_plat"] = 0
                p["vel_x"] = 4.8 if lado == "pared_izq" else -4.8
                p["vel_y"] = -8.5
                p["angulo_objetivo"] = 0.0
                ai["estado"] = "caminar"
                ai["tiempo"] = random.randint(35, 65)
                ai["cooldown_cambio_dir"] = 30

        # 4. SI ESTÁ EN EL TECHO
        elif sup == "techo":
            if rnd < 0.22:
                # Descolgarse y flotar suavemente hacia una plataforma o suelo
                p["superficie"] = "aire"
                p["plat_actual"] = None
                p["ignorar_plat"] = None
                p["cooldown_ignorar_plat"] = 0
                p["vel_x"] = random.uniform(-1.5, 1.5)
                p["vel_y"] = 2.5
                p["angulo_objetivo"] = 0.0
                ai["estado"] = "caminar"
                ai["tiempo"] = random.randint(35, 70)
                ai["cooldown_cambio_dir"] = 25
            elif rnd < 0.55:
                # Caminar por el techo
                ai["estado"] = "caminar_techo"
                ai["direccion"] = 1 if random.random() < 0.5 else -1
                ai["tiempo"] = random.randint(40, 100)
                ai["cooldown_cambio_dir"] = 25
            elif rnd < 0.88:
                # Dirigirse hacia una de las paredes laterales para trepar hacia abajo
                ai["estado"] = "caminar_techo"
                ai["direccion"] = -1 if p["hitbox"].centerx < 640 else 1
                ai["tiempo"] = random.randint(50, 120)
                ai["cooldown_cambio_dir"] = 25
            else:
                ai["estado"] = "quieto"
                ai["direccion"] = 0
                ai["tiempo"] = random.randint(25, 60)
                ai["cooldown_cambio_dir"] = 20

    def _actualizar_ai(self, idx):
        """Actualiza intenciones, temporizadores y comandos de movimiento para un personaje."""
        p = self.personajes[idx]
        ai = self.ai_estados[idx]
        ai["tiempo"] -= 1

        # Decrementar cooldown de cambio de dirección
        if ai.get("cooldown_cambio_dir", 0) > 0:
            ai["cooldown_cambio_dir"] -= 1

        # Anticipación de bordes en plataformas
        if p["superficie"] == "plataforma":
            self._anticipar_borde_plataforma(idx)

        dx_real = abs(p["hitbox"].x - ai["pos_x_anterior"])
        dy_real = abs(p["hitbox"].y - ai["pos_y_anterior"])
        if ai["estado"] in ("caminar", "trepar", "caminar_techo") and (dx_real < 1 and dy_real < 1):
            ai["frames_bloqueado"] += 1
        else:
            ai["frames_bloqueado"] = 0

        ai["pos_x_anterior"] = p["hitbox"].x
        ai["pos_y_anterior"] = p["hitbox"].y

        # Solo invertir dirección si el cooldown lo permite
        if ai["frames_bloqueado"] >= 18:
            ai["frames_bloqueado"] = 0
            if ai.get("cooldown_cambio_dir", 0) <= 0:
                if random.random() < 0.4 and p["superficie"] in ("suelo", "plataforma"):
                    ai["intentar_salto"] = True
                else:
                    self._fijar_direccion_ai(ai, -ai["direccion"], cooldown=25)
                ai["tiempo"] = random.randint(40, 80)

        if ai["tiempo"] <= 0:
            self._decidir_proxima_accion(idx)

        sup = p["superficie"]
        vel = p["velocidad_mov"]
        dir_act = ai["direccion"]

        if sup in ("suelo", "plataforma"):
            p["vel_x"] = dir_act * vel
            p["moviendo"] = (dir_act != 0)
            if dir_act > 0:
                p["mirando_derecha"] = True
            elif dir_act < 0:
                p["mirando_derecha"] = False

            if ai["intentar_salto"]:
                ai["intentar_salto"] = False
                if p.get("en_suelo", False):
                    p["vel_y"] = p["fuerza_salto"]
                    p["en_suelo"] = False
                    p["superficie"] = "aire"
                    if p.get("plat_actual"):
                        p["ignorar_plat"] = p["plat_actual"]
                        p["cooldown_ignorar_plat"] = 25
                    p["plat_actual"] = None

        elif sup == "techo":
            p["vel_x"] = dir_act * vel
            p["vel_y"] = 0
            p["moviendo"] = (dir_act != 0)
            if dir_act > 0:
                p["mirando_derecha"] = True
            elif dir_act < 0:
                p["mirando_derecha"] = False

        elif sup in ("pared_izq", "pared_der"):
            p["vel_x"] = 0
            p["vel_y"] = dir_act * vel
            p["moviendo"] = (dir_act != 0)
            p["mirando_derecha"] = (dir_act <= 0)

        elif sup == "aire":
            p["moviendo"] = False

    def actualizar_fisica(self):
        """
        Simulación física continua, fluida y sin teletransportes.
        Soporte para Suelo, Plataformas sólidas, Paredes y Techo. CERO colisiones con botones.
        """
        for i, p in enumerate(self.personajes):
            ai = self.ai_estados[i]
            sup = p["superficie"]
            hb = p["hitbox"]
            pos_x_prev = hb.x
            pos_y_prev = hb.y

            # Interpolación suave y orgánica de la rotación visual
            diff = p["angulo_objetivo"] - p["angulo"]
            while diff > 180.0:
                diff -= 360.0
            while diff < -180.0:
                diff += 360.0
            if abs(diff) < 1.0:
                p["angulo"] = p["angulo_objetivo"]
            else:
                paso = max(-18.0, min(18.0, diff * 0.35))
                p["angulo"] = (p["angulo"] + paso) % 360.0

            # --- CASO 1: SUELO ---
            if sup == "suelo":
                hb.x += int(round(p["vel_x"]))
                hb.bottom = self.y_suelo
                p["en_suelo"] = True
                p["vel_y"] = 0
                p["plat_actual"] = None
                p["ignorar_plat"] = None
                p["cooldown_ignorar_plat"] = 0
                p["angulo_objetivo"] = 0.0

                # Llegó a la pared izquierda
                if hb.left <= self.x_pared_izq:
                    hb.left = self.x_pared_izq
                    if random.random() < ai["datos_pers"]["trepar_prob"]:
                        p["superficie"] = "pared_izq"
                        p["angulo_objetivo"] = -90.0
                        hb.bottom = self.y_suelo - 4
                        p["vel_x"] = 0
                        p["vel_y"] = -p["velocidad_mov"]
                        p["en_suelo"] = False
                        ai["estado"] = "trepar"
                        ai["direccion"] = -1
                        ai["tiempo"] = random.randint(45, 95)
                        ai["cooldown_cambio_dir"] = 30
                    else:
                        ai["direccion"] = 1
                        ai["estado"] = "caminar"
                        ai["tiempo"] = random.randint(45, 95)
                        ai["cooldown_cambio_dir"] = 30

                # Llegó a la pared derecha
                elif hb.right >= self.x_pared_der:
                    hb.right = self.x_pared_der
                    if random.random() < ai["datos_pers"]["trepar_prob"]:
                        p["superficie"] = "pared_der"
                        p["angulo_objetivo"] = 90.0
                        hb.bottom = self.y_suelo - 4
                        p["vel_x"] = 0
                        p["vel_y"] = -p["velocidad_mov"]
                        p["en_suelo"] = False
                        ai["estado"] = "trepar"
                        ai["direccion"] = -1
                        ai["tiempo"] = random.randint(45, 95)
                        ai["cooldown_cambio_dir"] = 30
                    else:
                        ai["direccion"] = -1
                        ai["estado"] = "caminar"
                        ai["tiempo"] = random.randint(45, 95)
                        ai["cooldown_cambio_dir"] = 30

            # --- CASO 2: PLATAFORMA ---
            elif sup == "plataforma":
                plat = p.get("plat_actual")
                if plat:
                    hb.x += int(round(p["vel_x"]))
                    hb.bottom = plat.top
                    p["en_suelo"] = True
                    p["vel_y"] = 0
                    p["angulo_objetivo"] = 0.0

                    # Contención en paredes perimetrales
                    if hb.left <= self.x_pared_izq:
                        hb.left = self.x_pared_izq
                        if random.random() < ai["datos_pers"]["trepar_prob"]:
                            p["superficie"] = "pared_izq"
                            p["plat_actual"] = None
                            p["angulo_objetivo"] = -90.0
                            p["vel_x"] = 0
                            p["vel_y"] = -p["velocidad_mov"]
                            p["en_suelo"] = False
                            ai["estado"] = "trepar"
                            ai["direccion"] = -1
                            ai["tiempo"] = random.randint(45, 90)
                            ai["cooldown_cambio_dir"] = 30
                        else:
                            ai["direccion"] = 1
                            ai["tiempo"] = random.randint(40, 80)
                            ai["cooldown_cambio_dir"] = 30
                    elif hb.right >= self.x_pared_der:
                        hb.right = self.x_pared_der
                        if random.random() < ai["datos_pers"]["trepar_prob"]:
                            p["superficie"] = "pared_der"
                            p["plat_actual"] = None
                            p["angulo_objetivo"] = 90.0
                            p["vel_x"] = 0
                            p["vel_y"] = -p["velocidad_mov"]
                            p["en_suelo"] = False
                            ai["estado"] = "trepar"
                            ai["direccion"] = -1
                            ai["tiempo"] = random.randint(45, 90)
                            ai["cooldown_cambio_dir"] = 30
                        else:
                            ai["direccion"] = -1
                            ai["tiempo"] = random.randint(40, 80)
                            ai["cooldown_cambio_dir"] = 30

                    # Soporte sólido: el personaje no se desliza accidentalmente al vacío
                    # a menos que haya decidido bajar o saltar conscientemente
                    if p.get("ignorar_plat") != plat:
                        if hb.right > plat.right:
                            hb.right = plat.right
                            p["vel_x"] = 0
                        elif hb.left < plat.left:
                            hb.left = plat.left
                            p["vel_x"] = 0
                else:
                    p["superficie"] = "aire"
                    p["en_suelo"] = False

            # --- CASO 3: PARED IZQUIERDA ---
            elif sup == "pared_izq":
                hb.y += int(round(p["vel_y"]))
                hb.left = self.x_pared_izq
                p["vel_x"] = 0
                p["en_suelo"] = False
                p["angulo_objetivo"] = -90.0

                # Pasar de pared al techo
                if hb.top <= self.y_techo:
                    p["superficie"] = "techo"
                    p["angulo_objetivo"] = 180.0
                    hb.top = self.y_techo
                    hb.left = self.x_pared_izq + 2
                    p["vel_y"] = 0
                    p["vel_x"] = p["velocidad_mov"]
                    ai["estado"] = "caminar_techo"
                    ai["direccion"] = 1
                    ai["tiempo"] = random.randint(50, 110)
                    ai["cooldown_cambio_dir"] = 30

                # Regresar de la pared al suelo
                elif hb.bottom >= self.y_suelo:
                    p["superficie"] = "suelo"
                    p["angulo_objetivo"] = 0.0
                    hb.bottom = self.y_suelo
                    hb.left = self.x_pared_izq + 4
                    p["vel_y"] = 0
                    p["vel_x"] = p["velocidad_mov"]
                    p["en_suelo"] = True
                    ai["estado"] = "caminar"
                    ai["direccion"] = 1
                    ai["tiempo"] = random.randint(45, 100)
                    ai["cooldown_cambio_dir"] = 30

            # --- CASO 4: PARED DERECHA ---
            elif sup == "pared_der":
                hb.y += int(round(p["vel_y"]))
                hb.right = self.x_pared_der
                p["vel_x"] = 0
                p["en_suelo"] = False
                p["angulo_objetivo"] = 90.0

                # Pasar de pared al techo
                if hb.top <= self.y_techo:
                    p["superficie"] = "techo"
                    p["angulo_objetivo"] = 180.0
                    hb.top = self.y_techo
                    hb.right = self.x_pared_der - 2
                    p["vel_y"] = 0
                    p["vel_x"] = -p["velocidad_mov"]
                    ai["estado"] = "caminar_techo"
                    ai["direccion"] = -1
                    ai["tiempo"] = random.randint(50, 110)
                    ai["cooldown_cambio_dir"] = 30

                # Regresar de la pared al suelo
                elif hb.bottom >= self.y_suelo:
                    p["superficie"] = "suelo"
                    p["angulo_objetivo"] = 0.0
                    hb.bottom = self.y_suelo
                    hb.right = self.x_pared_der - 4
                    p["vel_y"] = 0
                    p["vel_x"] = -p["velocidad_mov"]
                    p["en_suelo"] = True
                    ai["estado"] = "caminar"
                    ai["direccion"] = -1
                    ai["tiempo"] = random.randint(45, 100)
                    ai["cooldown_cambio_dir"] = 30

            # --- CASO 5: TECHO (BOCA ABAJO) ---
            elif sup == "techo":
                hb.x += int(round(p["vel_x"]))
                hb.top = self.y_techo
                p["vel_y"] = 0
                p["en_suelo"] = False
                p["angulo_objetivo"] = 180.0

                # Pasar a la pared derecha
                if hb.right >= self.x_pared_der:
                    p["superficie"] = "pared_der"
                    p["angulo_objetivo"] = 90.0
                    hb.right = self.x_pared_der
                    hb.top = self.y_techo + 2
                    p["vel_x"] = 0
                    p["vel_y"] = p["velocidad_mov"]
                    ai["estado"] = "trepar"
                    ai["direccion"] = 1
                    ai["tiempo"] = random.randint(45, 90)
                    ai["cooldown_cambio_dir"] = 30

                # Pasar a la pared izquierda
                elif hb.left <= self.x_pared_izq:
                    p["superficie"] = "pared_izq"
                    p["angulo_objetivo"] = -90.0
                    hb.left = self.x_pared_izq
                    hb.top = self.y_techo + 2
                    p["vel_x"] = 0
                    p["vel_y"] = p["velocidad_mov"]
                    ai["estado"] = "trepar"
                    ai["direccion"] = 1
                    ai["tiempo"] = random.randint(45, 90)
                    ai["cooldown_cambio_dir"] = 30

            # --- CASO 6: AIRE (SALTO O CAÍDA LIBRE) ---
            elif sup == "aire":
                # Decrementar cooldown para volver a interactuar con la plataforma abandonada
                if p.get("cooldown_ignorar_plat", 0) > 0:
                    p["cooldown_ignorar_plat"] -= 1
                    ign_plat = p.get("ignorar_plat")
                    if p["cooldown_ignorar_plat"] <= 0 or (ign_plat and hb.top > ign_plat.bottom):
                        p["ignorar_plat"] = None
                        p["cooldown_ignorar_plat"] = 0

                p["vel_y"] = min(14.0, p["vel_y"] + GRAVEDAD)
                hb.x += int(round(p["vel_x"]))
                hb.y += int(round(p["vel_y"]))
                p["angulo_objetivo"] = 0.0
                p["en_suelo"] = False

                # Contención en paredes y techo
                if hb.left < self.x_pared_izq:
                    hb.left = self.x_pared_izq
                    p["vel_x"] = 0
                elif hb.right > self.x_pared_der:
                    hb.right = self.x_pared_der
                    p["vel_x"] = 0
                if hb.top < self.y_techo:
                    hb.top = self.y_techo
                    p["vel_y"] = max(0.0, p["vel_y"])

                # Aterrizaje en plataformas sólidas (desde arriba)
                aterrizo_plat = False
                if p["vel_y"] >= 0:
                    for plat in self.plataformas:
                        if plat == p.get("ignorar_plat"):
                            continue
                        # El centro del personaje debe estar apoyado firmemente sobre la plataforma
                        if plat.left + 4 <= hb.centerx <= plat.right - 4:
                            if hb.bottom >= plat.top and pos_y_prev + hb.height <= plat.top + max(12, int(p["vel_y"]) + 4):
                                hb.bottom = plat.top
                                p["vel_y"] = 0
                                p["en_suelo"] = True
                                p["superficie"] = "plataforma"
                                p["plat_actual"] = plat
                                p["ignorar_plat"] = None
                                p["cooldown_ignorar_plat"] = 0
                                p["angulo_objetivo"] = 0.0

                                # Al aterrizar, orientar la dirección con inteligencia hacia el interior
                                dist_izq = hb.centerx - plat.left
                                dist_der = plat.right - hb.centerx
                                if dist_izq < 24:
                                    nueva_d = 1 if random.random() < 0.75 else 0
                                elif dist_der < 24:
                                    nueva_d = -1 if random.random() < 0.75 else 0
                                else:
                                    nueva_d = 1 if random.random() < 0.5 else -1

                                self._fijar_direccion_ai(ai, nueva_d, cooldown=30)
                                ai["estado"] = "quieto" if ai["direccion"] == 0 else "caminar"
                                ai["tiempo"] = random.randint(45, 95)
                                ai["en_borde"] = False
                                aterrizo_plat = True
                                break

                # Aterrizaje en el suelo
                if not aterrizo_plat and hb.bottom >= self.y_suelo:
                    hb.bottom = self.y_suelo
                    p["vel_y"] = 0
                    p["en_suelo"] = True
                    p["superficie"] = "suelo"
                    p["plat_actual"] = None
                    p["ignorar_plat"] = None
                    p["cooldown_ignorar_plat"] = 0
                    p["angulo"] = 0.0
                    p["angulo_objetivo"] = 0.0
                    ai["estado"] = "caminar" if random.random() < 0.75 else "quieto"
                    nueva_d = (1 if random.random() < 0.5 else -1) if ai["estado"] == "caminar" else 0
                    self._fijar_direccion_ai(ai, nueva_d, cooldown=30)
                    ai["tiempo"] = random.randint(45, 95)
                    ai["cooldown_cambio_dir"] = 30
                    ai["en_borde"] = False

        # Colisión suave entre personajes en suelo o misma plataforma (evitar superposición)
        for i in range(5):
            for j in range(i + 1, 5):
                p_a = self.personajes[i]
                p_b = self.personajes[j]
                if p_a["superficie"] in ("suelo", "plataforma") and p_b["superficie"] == p_a["superficie"]:
                    if p_a.get("plat_actual") == p_b.get("plat_actual"):
                        hb_a = p_a["hitbox"]
                        hb_b = p_b["hitbox"]
                        if hb_a.colliderect(hb_b):
                            plat = p_a.get("plat_actual")
                            if hb_a.centerx < hb_b.centerx:
                                overlap = hb_a.right - hb_b.left
                                sep_step = min(6, (overlap + 1) // 2)
                                hb_a.x -= sep_step
                                hb_b.x += sep_step
                            else:
                                overlap = hb_b.right - hb_a.left
                                sep_step = min(6, (overlap + 1) // 2)
                                hb_b.x -= sep_step
                                hb_a.x += sep_step

                            if plat:
                                hb_a.left = max(plat.left + 2, hb_a.left)
                                hb_a.right = min(plat.right - 2, hb_a.right)
                                hb_b.left = max(plat.left + 2, hb_b.left)
                                hb_b.right = min(plat.right - 2, hb_b.right)
                            else:
                                hb_a.left = max(self.x_pared_izq, hb_a.left)
                                hb_a.right = min(self.x_pared_der, hb_a.right)
                                hb_b.left = max(self.x_pared_izq, hb_b.left)
                                hb_b.right = min(self.x_pared_der, hb_b.right)

    def actualizar(self):
        """Actualiza un fotograma completo de la simulación autónoma y elementos del fondo."""
        self.contador_frames += 1

        # 1. Movimiento lento y sutil de nubes pixel art (profundidad con distintas velocidades)
        for nube in self.nubes:
            nube["x"] += nube["vel"]
            if nube["x"] > self.ancho + 40:
                nube["x"] = -nube["w"] - 20

        # 2. Partículas de humo animadas de la chimenea de la cabaña
        for p_humo in self.particulas_humo:
            p_humo["progreso"] = (p_humo["progreso"] + 1) % 100

        # 3. Copos de nieve pixel art (ambas capas de profundidad)
        for copo in self.copos_nieve:
            copo["y"] += copo["vel_y"]
            copo["x"] += copo["vel_x"] + 0.45 * math.sin(copo["fase"] + self.contador_frames * copo["frecuencia"])
            if copo["y"] > self.alto + 5:
                copo["y"] = -6.0
                copo["x"] = random.uniform(0, self.ancho)
            if copo["x"] < -10:
                copo["x"] = self.ancho + 5
            elif copo["x"] > self.ancho + 10:
                copo["x"] = -5

        # 4. Actualizar IA de los 5 personajes independientes
        for i in range(5):
            self._actualizar_ai(i)

        # 5. Resolver físicas y desplazamientos
        self.actualizar_fisica()

    def _dibujar_nubes(self, superficie):
        """Dibuja las nubes pixel art desplazándose suavemente por el cielo crepuscular."""
        for nube in self.nubes:
            superficie.blit(nube["surf"], (int(nube["x"]), int(nube["y"])))

    def _dibujar_humo_chimenea(self, superficie):
        """Dibuja el humo animado de la chimenea con bocanadas sutiles pixel art."""
        base_x = 398
        base_y = 456
        for p in self.particulas_humo:
            prog = p["progreso"] / 100.0
            dy = prog * 32.0
            dx = prog * 14.0 + 2.0 * math.sin(prog * math.pi * 2 + self.contador_frames * 0.04)
            px = int(base_x + dx)
            py = int(base_y - dy)

            if prog < 0.35:
                col = (235, 240, 248)
                tam = 2
            elif prog < 0.70:
                col = (210, 220, 235)
                tam = 4
            else:
                col = (185, 200, 220)
                tam = 4

            pygame.draw.rect(superficie, col, (px, py, tam, tam))

    def _dibujar_copos_fondo(self, superficie):
        """Dibuja la capa lejana de copos de nieve (pequeños y suaves, tras los personajes)."""
        for copo in self.copos_nieve:
            if copo.get("capa") != "fondo":
                continue
            cx = int(copo["x"])
            cy = int(copo["y"])
            tam = copo["tamano"]
            col = (185, 205, 230)
            pygame.draw.rect(superficie, col, (cx, cy, tam, tam))

    def _dibujar_copos_frente(self, superficie):
        """Dibuja la capa cercana de copos de nieve (brillantes y con forma en primer plano)."""
        for copo in self.copos_nieve:
            if copo.get("capa") == "fondo":
                continue
            cx = int(copo["x"])
            cy = int(copo["y"])
            tam = copo["tamano"]

            if tam <= 2:
                pygame.draw.rect(superficie, (230, 245, 255), (cx, cy, 2, 2))
            elif tam <= 4:
                pygame.draw.rect(superficie, (255, 255, 255), (cx, cy, 4, 4))
                pygame.draw.rect(superficie, (210, 230, 255), (cx + 1, cy + 1, 2, 2))
            else:
                # Estrella de nieve de 6x6 (+)
                pygame.draw.rect(superficie, (255, 255, 255), (cx - 2, cy, 5, 2))
                pygame.draw.rect(superficie, (255, 255, 255), (cx, cy - 2, 2, 5))

    def _dibujar_copos_nieve(self, superficie):
        """Compatibilidad para renderizar copos en primer plano."""
        self._dibujar_copos_frente(superficie)

    def _dibujar_luces_animadas(self, superficie):
        """Dibuja el parpadeo de las luces navideñas, el farol y los destellos en pixel art."""
        # 1. Luces de los árboles de Navidad
        for luz in self.luces_arboles:
            lx = luz["x"]
            ly = luz["y"]
            col = luz["color"]
            fase = luz["fase"]
            estado = (self.contador_frames // 16 + fase) % 3

            if estado == 0:
                pygame.draw.rect(superficie, (255, 255, 255), (lx - 1, ly - 1, 2, 2))
                pygame.draw.rect(superficie, col, (lx - 2, ly - 2, 4, 4), 1)
            elif estado == 1:
                pygame.draw.rect(superficie, col, (lx - 1, ly - 1, 3, 3))
            else:
                col_tenue = (col[0] // 2, col[1] // 2, col[2] // 2)
                pygame.draw.rect(superficie, col_tenue, (lx - 1, ly - 1, 2, 2))

        # 2. Resplandor sutil de las estrellas doradas en la cima de los árboles
        for cx_est, cy_est in [(180, 360), (1100, 360)]:
            fase_est = (self.contador_frames // 24) % 4
            if fase_est in (0, 2):
                pygame.draw.rect(superficie, (255, 250, 190), (cx_est - 1, cy_est - 1, 2, 2))
            elif fase_est == 1:
                pygame.draw.rect(superficie, (255, 255, 230), (cx_est - 2, cy_est - 2, 4, 4), 1)

        # 3. Parpadeo cálido del farolito navideño en el suelo
        fx, fy = 930, 610
        flicker = (self.contador_frames // 14) % 2
        col_llama = (255, 235, 80) if flicker == 0 else (255, 205, 45)
        pygame.draw.rect(superficie, col_llama, (fx - 4, fy - 6, 8, 8))
        pygame.draw.rect(superficie, (255, 255, 220), (fx - 2, fy - 4, 4, 4))

        # 4. Destellos mágicos sutiles en la nieve
        for d in self.destellos_nieve:
            if (self.contador_frames + d["fase"]) % 90 < 8:
                pygame.draw.rect(superficie, (255, 255, 255), (d["x"], d["y"], 2, 2))

    def dibujar_escenario(self, superficie):
        """Dibuja el fondo pixel art navideño, nubes en movimiento, humo, luces y nieve lejana."""
        superficie.blit(self.fondo_estatico, (0, 0))
        self._dibujar_nubes(superficie)
        self._dibujar_humo_chimenea(superficie)
        self._dibujar_luces_animadas(superficie)
        self._dibujar_copos_fondo(superficie)

    def dibujar(self, superficie):
        """Renderiza el escenario, plataformas, personajes animados y nieve en capas."""
        self.dibujar_escenario(superficie)
        for p in self.personajes:
            dibujar_personaje_rotado(superficie, p)
        self._dibujar_copos_frente(superficie)

    def dibujar_menu_completo(
        self,
        superficie,
        botones_menu_datos,
        pos_mouse,
        spr_x=None,
        rect_x=None,
        fuente_titulo=None
    ):
        """
        Renderiza el Menú Principal con capas limpias:
        1. Fondo navideño 100% pixel art con nubes en movimiento, humo y luces.
        2. Capa lejana de nieve.
        3. Los 5 personajes animados en suelo, plataformas, paredes y techo.
        4. Botones del Menú como interfaz pura con 100% de visibilidad, respuesta y legibilidad.
        5. Título "PICO PARK" con sombra de contraste y botón de cierre X.
        6. Capa de nieve en primer plano con oscilación natural.
        """
        # 1. Fondo navideño pixel art, nubes, humo, luces y nieve de fondo
        self.dibujar_escenario(superficie)

        # 2. Dibujar personajes en sus respectivas superficies
        for p in self.personajes:
            dibujar_personaje_rotado(superficie, p)

        # 3. Dibujar los botones del Menú como interfaz limpia en primer plano
        for b_idx in range(len(botones_menu_datos)):
            btn_r, spr_n, spr_h = botones_menu_datos[b_idx]
            spr_dib = spr_h if (btn_r.collidepoint(pos_mouse) and spr_h) else spr_n
            if spr_dib:
                superficie.blit(spr_dib, btn_r)

        # 4. Título "PICO PARK" con sombra de contraste
        if fuente_titulo:
            titulo = fuente_titulo.render("PICO PARK", True, (255, 255, 255))
            r_tit = titulo.get_rect(center=(self.ancho // 2, 70))
            t_sombra = fuente_titulo.render("PICO PARK", True, (35, 35, 45))
            superficie.blit(t_sombra, r_tit.move(3, 3))
            superficie.blit(titulo, r_tit)

        # Botón X de salir
        if spr_x and rect_x:
            superficie.blit(spr_x, rect_x)

        # 5. Capa cercana de copos de nieve flotando en primer plano
        self._dibujar_copos_frente(superficie)
