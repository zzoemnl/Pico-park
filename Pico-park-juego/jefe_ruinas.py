"""
Jefe del mundo 2 (nivel 2-6): el Guardián de piedra de las ruinas.

Mecánica cooperativa (los jugadores están unidos por la soga):
- El guardián golpea el suelo: sale una onda expansiva que recorre el piso (hay que
  saltarla) y caen rocas sobre la posición de cada jugador, avisadas por una sombra.
- Después de cada golpe queda ATURDIDO unos segundos y la runa de su pecho brilla.
  La runa está demasiado alta para un salto normal: hay que hacer la torre humana
  (un jugador salta desde la cabeza del otro) y tocarla.
- Cada toque lo enfurece: ataca más seguido y con más rocas. Al tercer toque se
  desmorona, deja de bloquear el paso y aparecen la llave y la puerta.
"""
import math
import random
import pygame

from movimientos import GRAVEDAD

CLAVE_PISTA = "jefe_pista_ruinas"
GOLPES_PARA_VENCER = 3

# Duraciones (frames) por fase (0, 1, 2)
FRAMES_IDLE = (90, 60, 40)
FRAMES_TELEGRAFO = (50, 40, 32)
FRAMES_ATURDIDO = (210, 180, 150)
ROCAS_POR_JUGADOR = (1, 1, 2)
VELOCIDAD_ONDA = (6.0, 7.0, 8.5)
FRAMES_SOMBRA_ROCA = 38
TAMANO_ROCA = 44
ALTURA_RUNA = 280     # base de la runa a ~260 px del suelo: un salto llega a ~210, la torre humana a ~300

COL_PIEDRA = (122, 126, 138)
COL_PIEDRA_LUZ = (160, 164, 176)
COL_PIEDRA_BORDE = (68, 70, 82)
COL_MUSGO = (70, 120, 60)
COL_RUNA = (120, 220, 255)
COL_RUNA_APAGADA = (60, 80, 110)
COL_OJOS = (255, 200, 60)
COL_POLVO = (205, 180, 140)


def crear_jefe(suelo, ancho_mundo):
    x_cuerpo = ancho_mundo - 260
    cx = x_cuerpo + 80
    return {
        "cx": cx,
        "cuerpo": pygame.Rect(x_cuerpo, 0, 240, suelo.top),
        "runa": pygame.Rect(x_cuerpo - 30, suelo.top - ALTURA_RUNA - 22, 44, 44),
        "fase": 0,
        "estado": "idle",         # idle -> telegrafo -> golpe (1 frame) -> aturdido -> idle
        "timer": FRAMES_IDLE[0] + 60,
        "golpe_tick": 0,
        "rocas": [],              # {"rect", "vy", "sombra": frames restantes antes de caer, "x"}
        "ondas": [],              # {"rect", "vx"}
        "polvo": [],              # partículas {"x","y","vx","vy","vida"}
        "derrotado": False,
        "derrumbe": 0.0,
        "tick": 0,
    }


def reiniciar_jefe(jefe, botones_colores, suelo):
    nuevo = crear_jefe(suelo, jefe["cuerpo"].right + 20)
    for clave, valor in nuevo.items():
        if clave != "cuerpo":
            jefe[clave] = valor


def _polvo(jefe, x, y, cantidad=10, fuerza=4.0):
    for _ in range(cantidad):
        jefe["polvo"].append({
            "x": x + random.randint(-14, 14), "y": y,
            "vx": random.uniform(-fuerza, fuerza), "vy": random.uniform(-fuerza * 1.5, -1.0),
            "vida": random.randint(18, 34),
        })


def actualizar_jefe(jefe, botones_colores, jugadores, suelo, plataformas):
    """Devuelve (jugadores golpeados, recién derrotado)."""
    jefe["tick"] += 1
    fase = min(jefe["fase"], GOLPES_PARA_VENCER - 1)

    # Partículas de polvo (decorativas)
    vivas = []
    for p in jefe["polvo"]:
        p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.3; p["vida"] -= 1
        if p["vida"] > 0 and p["y"] < suelo.top + 10:
            vivas.append(p)
    jefe["polvo"] = vivas

    if jefe["derrotado"]:
        jefe["derrumbe"] = min(1.0, jefe["derrumbe"] + 1 / 75)
        if jefe["derrumbe"] < 1.0 and jefe["tick"] % 4 == 0:
            _polvo(jefe, jefe["cx"] + random.randint(-90, 90), suelo.top, 3, 3.0)
        return [], False

    if jefe["golpe_tick"] > 0:
        jefe["golpe_tick"] -= 1

    vivos = [p for p, comp in jugadores if not comp and not p["muerto"]]

    # Máquina de estados del ataque
    jefe["timer"] -= 1
    if jefe["estado"] == "idle" and jefe["timer"] <= 0:
        jefe["estado"] = "telegrafo"
        jefe["timer"] = FRAMES_TELEGRAFO[fase]
    elif jefe["estado"] == "telegrafo" and jefe["timer"] <= 0:
        # Golpe al suelo: onda expansiva + rocas sobre cada jugador
        onda = pygame.Rect(0, 0, 54, 26)
        onda.bottomright = (jefe["cuerpo"].left - 4, suelo.top)
        jefe["ondas"].append({"rect": onda, "vx": -VELOCIDAD_ONDA[fase]})
        _polvo(jefe, jefe["cuerpo"].left - 10, suelo.top, 16, 5.0)
        for p in vivos:
            for i in range(ROCAS_POR_JUGADOR[fase]):
                x = p["hitbox"].centerx + (0 if i == 0 else random.choice((-90, 90)))
                x = max(TAMANO_ROCA, min(jefe["cuerpo"].left - TAMANO_ROCA, x))
                jefe["rocas"].append({
                    "x": x, "sombra": FRAMES_SOMBRA_ROCA + i * 12,
                    "rect": pygame.Rect(x - TAMANO_ROCA // 2, -TAMANO_ROCA - 10, TAMANO_ROCA, TAMANO_ROCA),
                    "vy": 0.0,
                })
        jefe["estado"] = "aturdido"
        jefe["timer"] = FRAMES_ATURDIDO[fase]
    elif jefe["estado"] == "aturdido" and jefe["timer"] <= 0:
        jefe["estado"] = "idle"
        jefe["timer"] = FRAMES_IDLE[fase]

    golpeados = []

    # Ondas expansivas
    vivas = []
    for o in jefe["ondas"]:
        o["rect"].x += int(round(o["vx"]))
        if o["rect"].right < -10:
            continue
        zona = o["rect"].inflate(-10, -6)
        for p in vivos:
            if p["hitbox"].colliderect(zona):
                golpeados.append(p)
        vivas.append(o)
    jefe["ondas"] = vivas

    # Rocas: primero la sombra de aviso, después caen
    vivas = []
    for r in jefe["rocas"]:
        if r["sombra"] > 0:
            r["sombra"] -= 1
            vivas.append(r)
            continue
        r["vy"] += GRAVEDAD
        r["rect"].y += int(round(r["vy"]))
        aterrizo = r["rect"].bottom >= suelo.top
        if not aterrizo:
            for plat in plataformas:
                if plat is jefe["cuerpo"]:
                    continue
                if r["rect"].colliderect(plat) and r["rect"].bottom - int(r["vy"]) <= plat.top + 2:
                    aterrizo = True
                    r["rect"].bottom = plat.top
                    break
        if aterrizo:
            _polvo(jefe, r["rect"].centerx, min(r["rect"].bottom, suelo.top), 10, 3.5)
            continue
        zona = r["rect"].inflate(-10, -10)
        for p in vivos:
            if p["hitbox"].colliderect(zona):
                golpeados.append(p)
        vivas.append(r)
    jefe["rocas"] = vivas

    # Runa: solo cuenta mientras está aturdido
    recien_derrotado = False
    if jefe["estado"] == "aturdido":
        for p in vivos:
            if p["hitbox"].colliderect(jefe["runa"]):
                jefe["fase"] += 1
                jefe["golpe_tick"] = 45
                jefe["rocas"] = []
                jefe["ondas"] = []
                _polvo(jefe, jefe["runa"].centerx, jefe["runa"].centery, 14, 4.0)
                if jefe["fase"] >= GOLPES_PARA_VENCER:
                    jefe["derrotado"] = True
                    recien_derrotado = True
                else:
                    jefe["estado"] = "idle"
                    jefe["timer"] = FRAMES_IDLE[min(jefe["fase"], 2)]
                break

    return golpeados, recien_derrotado


# ------------------------------------------------------------------------------
# Dibujo
# ------------------------------------------------------------------------------

def _bloque(surf, rect, color=COL_PIEDRA):
    pygame.draw.rect(surf, COL_PIEDRA_BORDE, rect.move(3, 4), border_radius=5)
    pygame.draw.rect(surf, color, rect, border_radius=5)
    pygame.draw.rect(surf, COL_PIEDRA_LUZ, (rect.left + 4, rect.top + 4, rect.width - 8, 4), border_radius=2)
    pygame.draw.rect(surf, COL_PIEDRA_BORDE, rect, 2, border_radius=5)


def dibujar_proyectiles(surf, jefe):
    for o in jefe["ondas"]:
        r = o["rect"]
        for i in range(4):
            px = r.left + 6 + i * 12
            alto = 14 + (i % 2) * 8
            pygame.draw.rect(surf, COL_PIEDRA, (px, r.bottom - alto, 10, alto), border_radius=3)
            pygame.draw.rect(surf, COL_PIEDRA_BORDE, (px, r.bottom - alto, 10, alto), 1, border_radius=3)
        pygame.draw.ellipse(surf, COL_POLVO, (r.left - 10, r.bottom - 10, r.width + 16, 10))
    for r in jefe["rocas"]:
        if r["sombra"] > 0:
            # sombra que crece a medida que la roca está por caer
            escala = 1.0 - r["sombra"] / (FRAMES_SOMBRA_ROCA + 24)
            ancho = int(TAMANO_ROCA * (0.5 + escala))
            sombra = pygame.Surface((ancho, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra, (30, 20, 10, 120), sombra.get_rect())
            surf.blit(sombra, (r["x"] - ancho // 2, jefe["cuerpo"].bottom - 10))
        else:
            _bloque(surf, r["rect"])
    for p in jefe["polvo"]:
        pygame.draw.circle(surf, COL_POLVO, (int(p["x"]), int(p["y"])), 3)


def dibujar_jefe(surf, jefe, suelo):
    cx = jefe["cx"]
    base_y = suelo.top
    tick = jefe["tick"]
    cuerpo = jefe["cuerpo"]

    # Muro de ruinas detrás (tapa la llave y la puerta mientras el guardián está en pie)
    if not jefe["derrotado"]:
        muro = pygame.Rect(cuerpo.left - 20, base_y - 300, cuerpo.width + 40, 300)
        pygame.draw.rect(surf, (150, 128, 98), muro)
        for fila in range(10):
            y = muro.top + fila * 30
            desf = 0 if fila % 2 == 0 else 30
            for x in range(muro.left - desf, muro.right, 60):
                pygame.draw.rect(surf, (115, 88, 58), (x, y, 60, 30), 2)
        pygame.draw.rect(surf, (188, 158, 118), (muro.left, muro.top, muro.width, 8))

    if jefe["derrotado"]:
        _dibujar_derrumbe(surf, cx, base_y, jefe["derrumbe"])
        return

    if jefe["golpe_tick"] > 0:
        cx += int(math.sin(tick * 1.4) * 7)
    estado = jefe["estado"]
    fase = min(jefe["fase"], 2)

    # Proporciones
    alto_pierna, alto_torso, alto_cabeza = 90, 210, 60   # alto para que la runa quede en el pecho
    y_torso = base_y - alto_pierna - alto_torso
    y_cabeza = y_torso - alto_cabeza + 6
    inclinacion = 0
    if estado == "telegrafo":
        inclinacion = -int(18 * (1 - jefe["timer"] / max(1, FRAMES_TELEGRAFO[fase])))
    elif estado == "aturdido":
        inclinacion = int(math.sin(tick * 0.15) * 6)

    pierna_i = pygame.Rect(cx - 80, base_y - alto_pierna, 48, alto_pierna)
    pierna_d = pygame.Rect(cx + 30, base_y - alto_pierna, 48, alto_pierna)
    torso = pygame.Rect(cx - 104 + inclinacion, y_torso, 200, alto_torso)
    cabeza = pygame.Rect(cx - 44 + inclinacion * 2, y_cabeza, 88, alto_cabeza)
    _bloque(surf, pierna_i); _bloque(surf, pierna_d)
    _bloque(surf, torso)
    pygame.draw.rect(surf, COL_MUSGO, (torso.left + 10, torso.top + 10, 30, 10), border_radius=4)

    # Brazos: el izquierdo (hacia los jugadores) se levanta para el golpe
    if estado == "telegrafo":
        brazo_i = pygame.Rect(cx - 176 + inclinacion, y_torso - 60, 50, 120)
    elif estado == "aturdido":
        brazo_i = pygame.Rect(cx - 166, base_y - 70, 50, 70)
    else:
        osc = int(math.sin(tick * 0.06) * 4)
        brazo_i = pygame.Rect(cx - 154 + inclinacion, y_torso + 10 + osc, 50, 120)
    brazo_d = pygame.Rect(cx + 98 + inclinacion, y_torso + 14, 46, 110)
    _bloque(surf, brazo_d); _bloque(surf, brazo_i)
    _bloque(surf, cabeza)

    # Ojos
    col_ojos = (120, 120, 140) if estado == "aturdido" else COL_OJOS
    for ex in (cabeza.left + 22, cabeza.right - 36):
        pygame.draw.rect(surf, col_ojos, (ex, cabeza.top + 18, 14, 8))
    if estado == "aturdido":
        # estrellitas girando sobre la cabeza
        for i in range(3):
            ang = tick * 0.12 + i * 2.1
            sx = cabeza.centerx + int(math.cos(ang) * 50)
            sy = cabeza.top - 14 + int(math.sin(ang) * 10)
            pygame.draw.circle(surf, COL_OJOS, (sx, sy), 4)

    # Runa del pecho (brilla solo aturdido)
    runa = jefe["runa"]
    if estado == "aturdido":
        pulso = 0.5 + 0.5 * math.sin(tick * 0.25)
        halo = pygame.Surface((runa.width + 60, runa.height + 60), pygame.SRCALPHA)
        pygame.draw.circle(halo, (120, 220, 255, int(60 + 70 * pulso)), (halo.get_width() // 2, halo.get_height() // 2), runa.width // 2 + 24)
        surf.blit(halo, (runa.centerx - halo.get_width() // 2, runa.centery - halo.get_height() // 2))
        col = COL_RUNA
    else:
        col = COL_RUNA_APAGADA
    pygame.draw.circle(surf, COL_PIEDRA_BORDE, runa.center, runa.width // 2 + 4)
    pygame.draw.circle(surf, col, runa.center, runa.width // 2)
    pts = [(runa.centerx, runa.top + 8), (runa.right - 8, runa.centery), (runa.centerx, runa.bottom - 8), (runa.left + 8, runa.centery)]
    pygame.draw.polygon(surf, (240, 252, 255) if estado == "aturdido" else COL_PIEDRA_BORDE, pts, 3)
    # Grietas por golpes recibidos
    for i in range(fase):
        gx = torso.left + 30 + i * 40
        pygame.draw.lines(surf, COL_PIEDRA_BORDE, False, [(gx, torso.top + 30), (gx + 8, torso.top + 55), (gx - 4, torso.top + 80), (gx + 6, torso.bottom - 10)], 3)

    # Vida restante (runas chicas sobre la cabeza)
    for i in range(GOLPES_PARA_VENCER):
        x = cx - 40 + i * 40
        y = cabeza.top - 40
        lleno = i < GOLPES_PARA_VENCER - jefe["fase"]
        pygame.draw.circle(surf, COL_PIEDRA_BORDE, (x, y), 12)
        pygame.draw.circle(surf, COL_RUNA if lleno else COL_RUNA_APAGADA, (x, y), 9)


def _dibujar_derrumbe(surf, cx, base_y, progreso):
    """Los bloques se desploman hasta quedar en una pila de escombros."""
    random.seed(7)
    bloques = []
    for i in range(14):
        w = random.randint(34, 70); h = random.randint(24, 46)
        x_fin = cx - 30 + random.randint(0, 150)      # a la derecha de la llave
        y_fin = base_y - h - random.randint(0, 40) * (1 if i % 3 == 0 else 0)
        y_ini = base_y - 260 + i * 10
        y = y_ini + (y_fin - y_ini) * min(1.0, progreso * 1.3)
        bloques.append(pygame.Rect(x_fin, int(y), w, h))
    for b in bloques:
        _bloque(surf, b)
    # la runa apagada entre los escombros
    pygame.draw.circle(surf, COL_PIEDRA_BORDE, (cx + 60, base_y - 24), 16)
    pygame.draw.circle(surf, COL_RUNA_APAGADA, (cx + 60, base_y - 24), 12)
