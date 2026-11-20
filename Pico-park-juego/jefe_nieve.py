"""
Jefe del mundo 1 (nivel 1-6): el Muñeco de Nieve gigante.

Mecánica cooperativa:
- El muñeco ocupa el lado derecho de la arena y lanza bolas de nieve que ruedan
  hacia la izquierda. Tocar una bola mata (y en el mundo 1 la muerte es compartida).
- Hay dos botones de colores en el suelo. Para "golpear" al jefe los dos jugadores
  tienen que pisar los dos botones AL MISMO TIEMPO y mantenerlos unos instantes.
- Cada golpe cambia la posición de los botones y acelera las bolas. Al tercer
  golpe el muñeco se derrite, su cuerpo deja de bloquear el paso y aparecen la
  llave y la puerta detrás.

Los sprites se dibujan con código (igual que los fondos del mundo 1). Si en el
futuro se quiere arte dibujado a mano basta con reemplazar las funciones de dibujo.
"""
import math
import random
import pygame

from movimientos import GRAVEDAD

CLAVE_PISTA = "jefe_pista"
GOLPES_PARA_VENCER = 3
FRAMES_CARGA_GOLPE = 45          # cuánto hay que mantener los dos botones (0,75 s)
FRAMES_PAUSA_TRAS_GOLPE = 70
FRAMES_PRIMER_LANZAMIENTO = 110

# Por fase (0, 1, 2): intervalo entre lanzamientos, velocidad de las bolas y si vienen de a dos
INTERVALO_POR_FASE = (150, 115, 90)
VELOCIDAD_POR_FASE = (4.0, 5.0, 6.0)
PARES_POR_FASE = (False, False, True)
TAMANO_BOLA = 48
SEPARACION_PAR = 100

# Posiciones x de los botones (rojo, azul) en cada fase
BOTONES_POR_FASE = ((300, 760), (460, 900), (160, 880))

COL_NIEVE = (248, 250, 255)
COL_NIEVE_SOMBRA = (205, 220, 238)
COL_NIEVE_BORDE = (165, 188, 215)
COL_CARBON = (38, 38, 46)
COL_ZANAHORIA = (245, 140, 40)
COL_RAMA = (120, 80, 40)
COL_BUFANDA = (220, 60, 60)


def crear_jefe(suelo, ancho_mundo):
    """Estado inicial del jefe. `cuerpo` es la pared sólida que esconde la llave y la puerta."""
    x_cuerpo = ancho_mundo - 260
    return {
        "cx": x_cuerpo + 120,
        "cuerpo": pygame.Rect(x_cuerpo, 0, 240, suelo.top),
        "fase": 0,
        "carga": 0,
        "golpe_tick": 0,
        "pausa": FRAMES_PRIMER_LANZAMIENTO,
        "timer": 0,
        "bolas": [],
        "derrotado": False,
        "derretido": 0.0,        # 0..1 animación de derrota
        "tick": 0,
    }


def crear_botones_jefe(suelo, fase=0):
    """Botones de colores con el mismo formato que usa el resto del juego."""
    x_rojo, x_azul = BOTONES_POR_FASE[fase]
    return [
        {
            "id": 1, "color": "rojo",
            "col_fill": (235, 55, 55), "col_borde": (150, 25, 25), "col_luz": (255, 140, 140),
            "rect": pygame.Rect(x_rojo, suelo.top - 12, 70, 12), "presionado": False,
        },
        {
            "id": 2, "color": "azul",
            "col_fill": (45, 125, 245), "col_borde": (20, 65, 160), "col_luz": (140, 200, 255),
            "rect": pygame.Rect(x_azul, suelo.top - 12, 70, 12), "presionado": False,
        },
    ]


def reiniciar_jefe(jefe, botones_colores, suelo):
    nuevo = crear_jefe(suelo, jefe["cuerpo"].right + 20)
    for clave, valor in nuevo.items():
        if clave != "cuerpo":          # se conservan cuerpo y plataformas_iniciales
            jefe[clave] = valor
    for btn, nuevo_btn in zip(botones_colores, crear_botones_jefe(suelo, 0)):
        btn["rect"] = nuevo_btn["rect"]
        btn["presionado"] = False


def _lanzar_bola(jefe, suelo, desplazamiento=0):
    rect = pygame.Rect(0, 0, TAMANO_BOLA, TAMANO_BOLA)
    rect.bottom = suelo.top - 30
    rect.right = jefe["cuerpo"].left - 10 + desplazamiento
    jefe["bolas"].append({"rect": rect, "vx": -VELOCIDAD_POR_FASE[jefe["fase"]], "vy": 0.0, "giro": 0.0})


def actualizar_jefe(jefe, botones_colores, jugadores, suelo, plataformas):
    """
    Avanza un frame. `jugadores` es una lista de (personaje, completado).
    Devuelve la lista de personajes alcanzados por una bola (para que el nivel aplique la muerte)
    y True en el frame exacto en que el jefe queda derrotado.
    """
    jefe["tick"] += 1
    recien_derrotado = False

    if jefe["derrotado"]:
        jefe["derretido"] = min(1.0, jefe["derretido"] + 1 / 60)
        jefe["bolas"] = []
        return [], False

    if jefe["golpe_tick"] > 0:
        jefe["golpe_tick"] -= 1

    # Carga del golpe: los dos botones pisados a la vez
    if all(btn["presionado"] for btn in botones_colores):
        jefe["carga"] += 1
    else:
        jefe["carga"] = max(0, jefe["carga"] - 2)

    if jefe["carga"] >= FRAMES_CARGA_GOLPE:
        jefe["carga"] = 0
        jefe["fase"] += 1
        jefe["golpe_tick"] = 40
        jefe["bolas"] = []
        jefe["pausa"] = FRAMES_PAUSA_TRAS_GOLPE
        jefe["timer"] = 0
        if jefe["fase"] >= GOLPES_PARA_VENCER:
            jefe["derrotado"] = True
            recien_derrotado = True
            return [], True
        for btn, nuevo_btn in zip(botones_colores, crear_botones_jefe(suelo, jefe["fase"])):
            btn["rect"] = nuevo_btn["rect"]
            btn["presionado"] = False

    # Lanzamientos
    if jefe["pausa"] > 0:
        jefe["pausa"] -= 1
    else:
        jefe["timer"] += 1
        if jefe["timer"] >= INTERVALO_POR_FASE[jefe["fase"]]:
            jefe["timer"] = 0
            _lanzar_bola(jefe, suelo)
            if PARES_POR_FASE[jefe["fase"]]:
                _lanzar_bola(jefe, suelo, SEPARACION_PAR)

    # Física de las bolas: ruedan, caen con gravedad y se apoyan en suelo y plataformas
    golpeados = []
    vivas = []
    for bola in jefe["bolas"]:
        r = bola["rect"]
        r.x += int(round(bola["vx"]))
        bola["giro"] += bola["vx"] / (TAMANO_BOLA / 2)
        bola["vy"] += GRAVEDAD
        r.y += int(round(bola["vy"]))
        if r.bottom >= suelo.top:
            r.bottom = suelo.top
            bola["vy"] = 0.0
        else:
            for plat in plataformas:
                if r.colliderect(plat) and bola["vy"] > 0 and r.bottom - int(bola["vy"]) <= plat.top + 2:
                    r.bottom = plat.top
                    bola["vy"] = 0.0
                    break
        if r.right < -20:
            continue
        zona = r.inflate(-12, -12)
        for personaje, completado in jugadores:
            if not completado and not personaje["muerto"] and personaje["hitbox"].colliderect(zona):
                golpeados.append(personaje)
        vivas.append(bola)
    jefe["bolas"] = vivas
    return golpeados, recien_derrotado


# ------------------------------------------------------------------------------
# Dibujo
# ------------------------------------------------------------------------------

def _circulo_nieve(surf, cx, cy, r):
    pygame.draw.circle(surf, COL_NIEVE_SOMBRA, (cx + 4, cy + 5), r)
    pygame.draw.circle(surf, COL_NIEVE, (cx, cy), r)
    pygame.draw.circle(surf, COL_NIEVE_BORDE, (cx, cy), r, 3)
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3), max(3, r // 5))


def dibujar_proyectiles(surf, jefe):
    for bola in jefe["bolas"]:
        r = bola["rect"]
        _circulo_nieve(surf, r.centerx, r.centery, r.width // 2)
        # mancha que gira para que se note que rueda
        ang = bola["giro"]
        mx = r.centerx + int(math.cos(ang) * r.width * 0.28)
        my = r.centery + int(math.sin(ang) * r.width * 0.28)
        pygame.draw.circle(surf, COL_NIEVE_SOMBRA, (mx, my), 6)


def dibujar_jefe(surf, jefe, suelo):
    cx = jefe["cx"]
    base_y = suelo.top
    tick = jefe["tick"]

    if jefe["derrotado"]:
        _dibujar_derretido(surf, cx, base_y, jefe["derretido"])
        return

    # Sacudida al recibir un golpe
    if jefe["golpe_tick"] > 0:
        cx += int(math.sin(tick * 1.3) * 6)
    # Respiración leve
    sube = int(math.sin(tick * 0.05) * 3)

    # Montículo de nieve detrás del muñeco: tapa la llave y la puerta mientras está en pie
    cuerpo = jefe["cuerpo"]
    monticulo = pygame.Rect(cuerpo.left - 40, base_y - 230, cuerpo.width + 80, 460)
    clip_previo = surf.get_clip()
    surf.set_clip(pygame.Rect(monticulo.left - 8, 0, monticulo.width + 16, base_y))  # solo la mitad de arriba
    pygame.draw.ellipse(surf, COL_NIEVE_SOMBRA, monticulo.move(4, 6))
    pygame.draw.ellipse(surf, COL_NIEVE, monticulo)
    pygame.draw.ellipse(surf, COL_NIEVE_BORDE, monticulo, 3)
    surf.set_clip(clip_previo)

    fase = jefe["fase"]
    r_base, r_medio, r_cabeza = 92, 70, 50
    y_base = base_y - r_base + 6
    y_medio = y_base - r_base - r_medio + 26 + sube
    y_cabeza = y_medio - r_medio - r_cabeza + 22 + sube

    _circulo_nieve(surf, cx, y_base, r_base)
    _circulo_nieve(surf, cx, y_medio, r_medio)
    _circulo_nieve(surf, cx, y_cabeza, r_cabeza)

    # Grietas según el daño recibido
    for i in range(fase):
        gx = cx - 30 + i * 28
        pygame.draw.lines(surf, COL_NIEVE_BORDE, False,
                          [(gx, y_base - 40), (gx + 8, y_base - 20), (gx - 4, y_base), (gx + 6, y_base + 24)], 3)

    # Botones de carbón en la panza
    for i in range(3):
        pygame.draw.circle(surf, COL_CARBON, (cx, y_medio - 28 + i * 26), 6)

    # Bufanda
    pygame.draw.rect(surf, COL_BUFANDA, (cx - r_cabeza + 6, y_cabeza + r_cabeza - 14, 2 * r_cabeza - 12, 16), border_radius=6)
    pygame.draw.rect(surf, COL_BUFANDA, (cx + 10, y_cabeza + r_cabeza - 6, 16, 44), border_radius=4)

    # Cara: ojos, zanahoria y boca (enojada cuando ya lo golpearon)
    pygame.draw.circle(surf, COL_CARBON, (cx - 18, y_cabeza - 10), 6)
    pygame.draw.circle(surf, COL_CARBON, (cx + 18, y_cabeza - 10), 6)
    if fase > 0:
        pygame.draw.line(surf, COL_CARBON, (cx - 30, y_cabeza - 26), (cx - 10, y_cabeza - 18), 4)
        pygame.draw.line(surf, COL_CARBON, (cx + 30, y_cabeza - 26), (cx + 10, y_cabeza - 18), 4)
    pygame.draw.polygon(surf, COL_ZANAHORIA, [(cx - 4, y_cabeza + 2), (cx - 46, y_cabeza + 12), (cx - 4, y_cabeza + 14)])
    boca_y = y_cabeza + 26
    for i in range(5):
        bx = cx - 20 + i * 10
        by = boca_y + (abs(i - 2) * 2 if fase == 0 else -abs(i - 2) * 2)
        pygame.draw.circle(surf, COL_CARBON, (bx, by), 3)

    # Sombrero
    ala = pygame.Rect(cx - r_cabeza - 2, y_cabeza - r_cabeza + 4, 2 * r_cabeza + 4, 12)
    copa = pygame.Rect(cx - 34, y_cabeza - r_cabeza - 52, 68, 58)
    pygame.draw.rect(surf, COL_CARBON, ala, border_radius=4)
    pygame.draw.rect(surf, COL_CARBON, copa, border_top_left_radius=6, border_top_right_radius=6)
    pygame.draw.rect(surf, COL_BUFANDA, (copa.left, copa.bottom - 14, copa.width, 8))

    # Brazo de rama que "lanza" (se levanta justo antes de cada bola)
    inminente = jefe["pausa"] == 0 and jefe["timer"] > INTERVALO_POR_FASE[fase] - 25
    ang = -0.9 if inminente else -0.35 + math.sin(tick * 0.08) * 0.08
    hombro = (cx - r_medio + 10, y_medio - 10)
    mano = (hombro[0] + int(math.cos(ang) * -70), hombro[1] + int(math.sin(ang) * 70))
    pygame.draw.line(surf, COL_RAMA, hombro, mano, 6)
    pygame.draw.line(surf, COL_RAMA, mano, (mano[0] - 12, mano[1] - 14), 4)
    pygame.draw.line(surf, COL_RAMA, mano, (mano[0] - 16, mano[1] + 4), 4)
    if inminente:
        _circulo_nieve(surf, mano[0] - 6, mano[1] - 20, TAMANO_BOLA // 2 - 4)

    # Vida restante (copos) y barra de carga del golpe
    for i in range(GOLPES_PARA_VENCER):
        x_copo = cx - 40 + i * 40
        y_copo = copa.top - 30
        lleno = i < GOLPES_PARA_VENCER - fase
        _dibujar_copo(surf, x_copo, y_copo, lleno)
    if jefe["carga"] > 0:
        ancho = 120
        progreso = jefe["carga"] / FRAMES_CARGA_GOLPE
        barra = pygame.Rect(cx - ancho // 2, copa.top - 56, ancho, 12)
        pygame.draw.rect(surf, (60, 60, 70), barra, border_radius=5)
        pygame.draw.rect(surf, (255, 215, 70), (barra.x, barra.y, int(ancho * progreso), 12), border_radius=5)
        pygame.draw.rect(surf, COL_CARBON, barra, 2, border_radius=5)


def _dibujar_copo(surf, x, y, lleno):
    col = (120, 200, 255) if lleno else (190, 200, 210)
    for i in range(3):
        ang = i * math.pi / 3
        dx, dy = math.cos(ang) * 12, math.sin(ang) * 12
        pygame.draw.line(surf, col, (x - dx, y - dy), (x + dx, y + dy), 3)
    pygame.draw.circle(surf, col, (x, y), 4)


def _dibujar_derretido(surf, cx, base_y, progreso):
    """El muñeco se achata hasta quedar un charco con el sombrero encima."""
    alto = int(180 * (1 - progreso)) + 24
    ancho = 180 + int(90 * progreso)
    charco = pygame.Rect(cx - ancho // 2, base_y - alto, ancho, alto)
    pygame.draw.ellipse(surf, COL_NIEVE_SOMBRA, charco.move(4, 5))
    pygame.draw.ellipse(surf, COL_NIEVE, charco)
    pygame.draw.ellipse(surf, COL_NIEVE_BORDE, charco, 3)
    # sombrero caído y zanahoria, corridos a la izquierda para no tapar la puerta
    pygame.draw.rect(surf, COL_CARBON, (cx - 110, charco.top - 10, 60, 14), border_radius=4)
    pygame.draw.rect(surf, COL_CARBON, (cx - 98, charco.top - 44, 36, 36), border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.polygon(surf, COL_ZANAHORIA, [(cx - 30, charco.top + 4), (cx - 66, charco.top - 8), (cx - 28, charco.top - 6)])
    if progreso < 1.0:
        random.seed(int(progreso * 40))
        for _ in range(6):
            gx = cx + random.randint(-ancho // 2, ancho // 2)
            gy = charco.top + random.randint(0, alto // 2)
            pygame.draw.circle(surf, (170, 215, 255), (gx, gy), 3)
