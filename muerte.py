import os
import sys
import pygame

# --- CONFIGURACIÓN GLOBAL ---
ANCHO, ALTO = 800, 600
FPS = 60
GRAVEDAD = 0.8

# Tamaño del sprite visual
ANCHO_PERSONAJE = 70
ALTO_PERSONAJE = 85

# Tamaño de la Hitbox
ANCHO_HITBOX = 45
ALTO_HITBOX = ALTO_PERSONAJE
COLOR_JUGADOR1 = "Celeste"
COLOR_JUGADOR2 = "Violeta"

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))

# Carpeta donde están los sprites de los botones
RUTA_BOTONES = os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Botones")
RUTA_BASE = os.path.join(DIRECTORIO_ACTUAL, "Sprites", "Personajes")


def cargar_sprites(nombre_color):
    """Carga y escala todos los sprites."""
    ruta_carpeta = os.path.join(RUTA_BASE,nombre_color)
    sprites = {}

    estados = [
        "quieto",
        "muerto",
        "caminar-1",
        "caminar-2",
        "caminar-3",
        "caminar-4",
        "caminar-5",
        "caminar-6",
        "caminar-7",
        "caminar-8",
        "saltar",
        "caminar-empujar-1",
        "caminar-empujar-2",
        "caminar-empujar-3",
        "caminar-empujar-4",
        "caminar-empujar-5",
        "caminar-empujar-6",
        "caminar-empujar-7",
        "caminar-empujar-8",
        "saltar-empujar",
        "pestañear",
    ]

    for estado in estados:
        img_temp = pygame.Surface((ANCHO_PERSONAJE, ALTO_PERSONAJE))
        img_temp.fill((50, 120, 240))
        sprites[estado] = img_temp

    if os.path.exists(ruta_carpeta):
        for estado in estados:
            ruta_archivo = os.path.join(ruta_carpeta,f"{estado}.png")

            if os.path.isfile(ruta_archivo):
                try:
                    img = pygame.image.load(ruta_archivo).convert_alpha()
                    sprites[estado] = pygame.transform.scale(img,(ANCHO_PERSONAJE, ALTO_PERSONAJE))

                except pygame.error:
                    pass

    return sprites


def crear_personaje(x, y, color_carpeta):
    """Inicializa al personaje usando la hitbox."""

    return {
        "hitbox": pygame.Rect(x,y,ANCHO_HITBOX,ALTO_HITBOX ),
        "vel_x": 0,
        "vel_y": 0,

        "velocidad_mov": 5,
        "velocidad_muerte": -17,
        "fuerza_salto": -15,

        "en_suelo": False,

        "sprites": cargar_sprites(
            color_carpeta
        ),

        "mirando_derecha": True,

        "frame_animacion": 1,
        "contador_anim": 0,

        "tocando_otro": False,

        "tiempo_muerte": 0,
        "tiempo_quieto": 0,

        "mostrando_pestañeo": False,

        "muerto": False,
        "muerte_terminada": False,
    }

def actualizar_temporizadores(p):
    """Maneja el tiempo quieto y el pestañeo."""
    esta_quieto = (p["vel_x"] == 0 and p["en_suelo"])

    if esta_quieto and not p["tocando_otro"]:
        p["tiempo_quieto"] += 1
        frames_15_seg = 15 * FPS
        frames_10_seg = 10 * FPS
        duracion_pestañeo = int(0.5 * FPS)

        if p["tiempo_quieto"] >= frames_15_seg:
            tiempo_post_15 = (p["tiempo_quieto"]- frames_15_seg)

            if (tiempo_post_15 % frames_10_seg) < duracion_pestañeo:
                p["mostrando_pestañeo"] = True

            else:
                p["mostrando_pestañeo"] = False
        else:
            p["mostrando_pestañeo"] = False
    else:
        p["tiempo_quieto"] = 0
        p["mostrando_pestañeo"] = False


def obtener_estado(p):
    # --- ANIMACIÓN DE MUERTO ---
    if p["muerto"]:
        return "muerto"

    # --- SALTAR ---
    if not p["en_suelo"]:

        if (p["tocando_otro"] and p["vel_x"] != 0):
            return "saltar-empujar"
        return "saltar"

    # --- EMPUJAR ---
    if (p["tocando_otro"] and p["vel_x"] != 0):
        p["contador_anim"] += 1

        if p["contador_anim"] % 8 == 0:
            p["frame_animacion"] += 1

            if p["frame_animacion"] > 8:
                p["frame_animacion"] = 1

        return f"caminar-empujar-{p['frame_animacion']}"

    # --- CAMINAR ---

    if p["vel_x"] != 0:
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


def resolver_colisiones(p1, p2, suelo):
    """Resuelve las físicas de los personajes."""
    hb1 = p1["hitbox"]
    hb2 = p2["hitbox"]

    # --- 1. MOVIMIENTO HORIZONTAL ---
    hb1.x += p1["vel_x"]
    p1["tocando_otro"] = hb1.colliderect(hb2)

    if p1["tocando_otro"]:
        margen_cabeza = 12
        p2_esta_encima = (hb2.bottom <= hb1.top + margen_cabeza)

        if hb1.bottom <= hb2.top + margen_cabeza:
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

        elif not p2_esta_encima:
            if p1["vel_x"] > 0:
                hb1.right = hb2.left

            elif p1["vel_x"] < 0:
                hb1.left = hb2.right

    # --- 2. MOVIMIENTO VERTICAL Y GRAVEDAD ---

    p1["vel_y"] += GRAVEDAD
    hb1.y += int(p1["vel_y"])

    if hb1.colliderect(hb2):
        if (p1["vel_y"] >= 0 and hb1.top < hb2.top):
            hb1.bottom = hb2.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True

        elif ( p1["vel_y"] < 0 and hb1.bottom > hb2.bottom):
            hb1.top = hb2.bottom
            p1["vel_y"] = 0

    # --- 3. COLISIÓN CON EL SUELO ---

    if hb1.colliderect(suelo):
        if p1["vel_y"] >= 0:

            hb1.bottom = suelo.top
            p1["vel_y"] = 0
            p1["en_suelo"] = True


# ============================================================
# TRANSPORTAR PERSONAJE ENCIMA
# ============================================================

def transportar_personaje_encima(p_arriba,p_abajo):
    """El personaje de abajo lleva al de arriba."""

    if (p_arriba["muerto"] or p_abajo["muerto"]):
        return
    
    hb_arriba = p_arriba["hitbox"]
    hb_abajo = p_abajo["hitbox"]
    margen = 4
    esta_encima = (abs(hb_arriba.bottom - hb_abajo.top) <= margen and hb_arriba.right > hb_abajo.left and hb_arriba.left < hb_abajo.right)

    if esta_encima:
        hb_arriba.x += p_abajo["vel_x"]
        hb_arriba.bottom = hb_abajo.top
        p_arriba["vel_y"] = 0
        p_arriba["en_suelo"] = True


# ============================================================
# PINCHOS
# ============================================================

def crear_pinchos():
    pinchos = []
    posiciones = [(220, 500),(400, 500),(580, 500)]

    for x, y in posiciones:
        pincho = pygame.Rect(x,y,50,20)
        pinchos.append(pincho)
    return pinchos


def dibujar_pinchos(pantalla, pinchos):

    for pincho in pinchos:
        puntos = [(pincho.left, pincho.bottom),(pincho.centerx, pincho.top),(pincho.right, pincho.bottom),]
        pygame.draw.polygon(pantalla,(220, 220, 220),puntos)
        pygame.draw.polygon(pantalla,(80, 80, 80),puntos,2)


def comprobar_pinchos(p, pinchos):
    if p["muerto"]:
        return

    for pincho in pinchos:
        if p["hitbox"].colliderect(pincho):
            p["muerto"] = True
            p["tiempo_muerte"] = 0
            p["vel_y"] = p["velocidad_muerte"]
            p["vel_x"] = 0
            p["en_suelo"] = False
            break

# ============================================================
# ACTUALIZAR MUERTE
# ============================================================

def actualizar_muerte(p, suelo):
    if not p["muerto"]:
        return

    p["tiempo_muerte"] += 1
    p["vel_y"] += GRAVEDAD
    p["hitbox"].y += int(p["vel_y"])

    if p["hitbox"].top > ALTO:
        p["muerte_terminada"] = True


# ============================================================
# DIBUJAR PERSONAJE
# ============================================================

def dibujar_personaje(pantalla, p):

    if p["muerto"]:
        estado = "muerto"
        sprite = p["sprites"].get(estado,p["sprites"]["quieto"])

        if not p["mirando_derecha"]:
            sprite = pygame.transform.flip(sprite,True,False)

        rect_sprite = sprite.get_rect(center=p["hitbox"].center)
        pantalla.blit(sprite,rect_sprite)

        return

    actualizar_temporizadores(p)
    estado = obtener_estado(p)

    sprite = p["sprites"].get(estado,p["sprites"]["quieto"])

    if p["vel_x"] > 0:
        p["mirando_derecha"] = True

    elif p["vel_x"] < 0:
        p["mirando_derecha"] = False

    if not p["mirando_derecha"]:
        sprite = pygame.transform.flip(sprite,True,False)

    rect_sprite = sprite.get_rect(center=p["hitbox"].center)
    pantalla.blit(sprite,rect_sprite)


# ============================================================
# PANTALLA DE MUERTE
# ============================================================

def pantalla_muerte(pantalla, reloj):

    fuente_titulo = pygame.font.Font(None,60)
    fuente_texto = pygame.font.Font(None,36)

    # ========================================================
    # CARGAR IMÁGENES DE LOS BOTONES
    # ========================================================

    def cargar_boton(nombre):
        ruta = os.path.join(RUTA_BOTONES,nombre)

        try:
            imagen = pygame.image.load(ruta).convert_alpha()
            print("Botón cargado:",ruta)
            return imagen
        
        except (FileNotFoundError, pygame.error) as error:
            print("ERROR AL CARGAR:",ruta)
            print(error)
            return None

    boton_salir_normal = cargar_boton("boton-salir.png")

    boton_salir_apretado = cargar_boton("boton-salir-apretado.png")

    boton_reiniciar_normal = cargar_boton("boton-reiniciar.png")

    boton_reiniciar_apretado = cargar_boton("boton-reiniciar-apretado.png")

    # ========================================================
    # COMPROBAR IMÁGENES
    # ========================================================

    if (
        boton_salir_normal is None
        or boton_salir_apretado is None
        or boton_reiniciar_normal is None
        or boton_reiniciar_apretado is None
    ):

        print(
            "ERROR: No se pudieron cargar "
            "los sprites de los botones."
        )

        pygame.quit()

        sys.exit()

    # ========================================================
    # ESCALAR BOTONES
    # ========================================================

    boton_reiniciar_normal = pygame.transform.scale(
        boton_reiniciar_normal,
        (260, 80)
    )

    boton_reiniciar_apretado = pygame.transform.scale(
        boton_reiniciar_apretado,
        (260, 80)
    )

    boton_salir_normal = pygame.transform.scale(
        boton_salir_normal,
        (260, 80)
    )

    boton_salir_apretado = pygame.transform.scale(
        boton_salir_apretado,
        (260, 80)
    )

    # ========================================================
    # POSICIONES
    # ========================================================

    boton_reiniciar = boton_reiniciar_normal.get_rect(
        center=(ANCHO // 2 - 150, 400)
    )

    boton_salir = boton_salir_normal.get_rect(
        center=(ANCHO // 2 + 150, 400)
    )

    # ========================================================
    # BUCLE DE LA PANTALLA
    # ========================================================

    while True:

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                pygame.quit()

                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:

                # ====================================================
                # BOTÓN REINICIAR
                # ====================================================

                if boton_reiniciar.collidepoint(
                    evento.pos
                ):

                    pantalla.fill(
                        (25, 25, 25)
                    )

                    titulo = fuente_titulo.render(
                        "¡Te moriste!",
                        True,
                        (255, 80, 80)
                    )

                    texto = fuente_texto.render(
                        "¿Querés reiniciar o salir?",
                        True,
                        (255, 255, 255)
                    )

                    pantalla.blit(
                        titulo,
                        titulo.get_rect(
                            center=(ANCHO // 2, 180)
                        )
                    )

                    pantalla.blit(
                        texto,
                        texto.get_rect(
                            center=(ANCHO // 2, 250)
                        )
                    )

                    pantalla.blit(
                        boton_reiniciar_apretado,
                        boton_reiniciar
                    )

                    pantalla.blit(
                        boton_salir_normal,
                        boton_salir
                    )

                    pygame.display.flip()

                    pygame.time.delay(200)

                    pantalla.fill(
                        (25, 25, 25)
                    )

                    pantalla.blit(
                        titulo,
                        titulo.get_rect(
                            center=(ANCHO // 2, 180)
                        )
                    )

                    pantalla.blit(
                        texto,
                        texto.get_rect(
                            center=(ANCHO // 2, 250)
                        )
                    )

                    pantalla.blit(
                        boton_reiniciar_normal,
                        boton_reiniciar
                    )

                    pantalla.blit(
                        boton_salir_normal,
                        boton_salir
                    )

                    pygame.display.flip()

                    pygame.time.delay(100)

                    return "reiniciar"

                # ====================================================
                # BOTÓN SALIR
                # ====================================================

                if boton_salir.collidepoint(
                    evento.pos
                ):

                    pantalla.fill(
                        (25, 25, 25)
                    )

                    titulo = fuente_titulo.render(
                        "¡Te moriste!",
                        True,
                        (255, 80, 80)
                    )

                    texto = fuente_texto.render(
                        "¿Querés reiniciar o salir?",
                        True,
                        (255, 255, 255)
                    )

                    pantalla.blit(
                        titulo,
                        titulo.get_rect(
                            center=(ANCHO // 2, 180)
                        )
                    )

                    pantalla.blit(
                        texto,
                        texto.get_rect(
                            center=(ANCHO // 2, 250)
                        )
                    )

                    pantalla.blit(
                        boton_reiniciar_normal,
                        boton_reiniciar
                    )

                    pantalla.blit(
                        boton_salir_apretado,
                        boton_salir
                    )

                    pygame.display.flip()

                    pygame.time.delay(200)

                    pantalla.fill(
                        (25, 25, 25)
                    )

                    pantalla.blit(
                        titulo,
                        titulo.get_rect(
                            center=(ANCHO // 2, 180)
                        )
                    )

                    pantalla.blit(
                        texto,
                        texto.get_rect(
                            center=(ANCHO // 2, 250)
                        )
                    )

                    pantalla.blit(
                        boton_reiniciar_normal,
                        boton_reiniciar
                    )

                    pantalla.blit(
                        boton_salir_normal,
                        boton_salir
                    )

                    pygame.display.flip()

                    pygame.time.delay(100)

                    return "salir"

        # ====================================================
        # DIBUJAR PANTALLA NORMAL
        # ====================================================

        pantalla.fill(
            (25, 25, 25)
        )

        titulo = fuente_titulo.render(
            "¡Te moriste!",
            True,
            (255, 80, 80)
        )

        texto = fuente_texto.render(
            "¿Querés reiniciar o salir?",
            True,
            (255, 255, 255)
        )

        pantalla.blit(
            titulo,
            titulo.get_rect(
                center=(ANCHO // 2, 180)
            )
        )

        pantalla.blit(
            texto,
            texto.get_rect(
                center=(ANCHO // 2, 250)
            )
        )

        pantalla.blit(
            boton_reiniciar_normal,
            boton_reiniciar
        )

        pantalla.blit(
            boton_salir_normal,
            boton_salir
        )

        pygame.display.flip()

        reloj.tick(FPS)


# ============================================================
# MAIN
# ============================================================

def main():

    pygame.init()

    pantalla = pygame.display.set_mode(
        (ANCHO, ALTO)
    )

    pygame.display.set_caption(
        "Juego con 2 Personajes - Hitbox y Animaciones"
    )

    reloj = pygame.time.Clock()

    jugador1 = crear_personaje(100, 300, COLOR_JUGADOR1)

    jugador2 = crear_personaje(300, 300, COLOR_JUGADOR2)

    suelo = pygame.Rect(0,520,ANCHO,80)

    pinchos = crear_pinchos()

    ejecutando = True

    while ejecutando:

        reloj.tick(FPS)

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                ejecutando = False

        teclas = pygame.key.get_pressed()

        # ====================================================
        # CONTROLES JUGADOR 1 (FLECHAS)
        # ====================================================

        if not jugador1["muerto"]:

            jugador1["vel_x"] = 0

            if teclas[pygame.K_LEFT]:

                jugador1["vel_x"] = (
                    -jugador1["velocidad_mov"]
                )

            if teclas[pygame.K_RIGHT]:

                jugador1["vel_x"] = (
                    jugador1["velocidad_mov"]
                )

            if (
                teclas[pygame.K_UP]
                and jugador1["en_suelo"]
            ):

                jugador1["vel_y"] = (
                    jugador1["fuerza_salto"]
                )

                jugador1["en_suelo"] = False

        # ====================================================
        # CONTROLES JUGADOR 2 (WASD)
        # ====================================================

        if not jugador2["muerto"]:

            jugador2["vel_x"] = 0

            if teclas[pygame.K_a]:

                jugador2["vel_x"] = (
                    -jugador2["velocidad_mov"]
                )

            if teclas[pygame.K_d]:

                jugador2["vel_x"] = (
                    jugador2["velocidad_mov"]
                )

            if (
                teclas[pygame.K_w]
                and jugador2["en_suelo"]
            ):

                jugador2["vel_y"] = (
                    jugador2["fuerza_salto"]
                )

                jugador2["en_suelo"] = False

        # ====================================================
        # FÍSICAS
        # ====================================================

        if not jugador1["muerto"]:

            resolver_colisiones(
                jugador1,
                jugador2,
                suelo
            )

        if not jugador2["muerto"]:

            resolver_colisiones(
                jugador2,
                jugador1,
                suelo
            )

        # ====================================================
        # TRANSPORTAR PERSONAJE ENCIMA
        # ====================================================

        transportar_personaje_encima(
            jugador1,
            jugador2
        )

        transportar_personaje_encima(
            jugador2,
            jugador1
        )

        # ====================================================
        # COMPROBAR PINCHOS
        # ====================================================

        comprobar_pinchos(
            jugador1,
            pinchos
        )

        comprobar_pinchos(
            jugador2,
            pinchos
        )

        # ====================================================
        # ACTUALIZAR MUERTE
        # ====================================================

        actualizar_muerte(
            jugador1,
            suelo
        )

        actualizar_muerte(
            jugador2,
            suelo
        )

        # ====================================================
        # BORDES DE LA PANTALLA
        # ====================================================

        if not jugador1["muerto"]:

            jugador1["hitbox"].x = max(
                0,
                min(jugador1["hitbox"].x, ANCHO - ANCHO_HITBOX)
            )

        if not jugador2["muerto"]:

            jugador2["hitbox"].x = max(
                0,
                min(jugador2["hitbox"].x, ANCHO - ANCHO_HITBOX)
            )

        # ====================================================
        # RENDERIZADO
        # ====================================================

        pantalla.fill(
            (30, 30, 30)
        )

        pygame.draw.rect(
            pantalla,
            (100, 100, 100),
            suelo
        )

        dibujar_pinchos(
            pantalla,
            pinchos
        )

        dibujar_personaje(
            pantalla,
            jugador1
        )

        dibujar_personaje(
            pantalla,
            jugador2
        )

        pygame.display.flip()

        # ====================================================
        # PANTALLA DE MUERTE
        # ====================================================

        if (
            jugador1["muerte_terminada"]
            or jugador2["muerte_terminada"]
        ):

            resultado = pantalla_muerte(
                pantalla,
                reloj
            )

            if resultado == "salir":

                ejecutando = False

            elif resultado == "reiniciar":

                jugador1 = crear_personaje(100,-ALTO_PERSONAJE,"Celeste")
                jugador2 = crear_personaje(300,-ALTO_PERSONAJE,"Violeta")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":

    main()