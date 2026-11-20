"""
Jefe final (nivel 3-6): el Kraken de las profundidades.

Mecánica cooperativa (nadando, con oxígeno y cámaras de aire como en 3-5):
- Tentáculos que suben del lecho marino en posiciones avisadas con burbujas.
  Tocarlos mata (en el mundo 3 la muerte es individual).
- A partir del segundo golpe también escupe tinta que flota hacia los jugadores.
- Para golpearlo aparece un ORBE de luz en algún lugar del agua. Los dos jugadores
  tienen que estar dentro del orbe AL MISMO TIEMPO un instante para cargarlo;
  entonces el orbe vuela al ojo del Kraken y lo hiere. Tres golpes y se hunde,
  dejando libres la llave y la puerta que esconde con su cuerpo.
"""
import math
import random
import pygame

CLAVE_PISTA = "jefe_pista_kraken"
GOLPES_PARA_VENCER = 3
FRAMES_CARGA_ORBE = 60
RADIO_ORBE = 78
FRAMES_PAUSA_ORBE = (120, 150, 170)       # espera antes de que aparezca el orbe en cada fase
FRAMES_ENTRE_OLEADAS = (170, 130, 100)
TENTACULOS_POR_OLEADA = (2, 3, 4)
ALTURAS_TENTACULO = (220, 300, 380)
FRAMES_AVISO = 42
FRAMES_SUBIDA = 26
FRAMES_ARRIBA = (70, 60, 50)
FRAMES_TINTA = (0, 150, 110)               # 0 = sin tinta
VELOCIDAD_TINTA = (0, 2.2, 2.8)
ANCHO_TENTACULO = 40
POSICIONES_TENTACULO = (120, 270, 420, 570, 720, 870)
POSICIONES_ORBE = ((260, 300), (520, 180), (700, 420), (380, 480), (820, 240), (200, 520))

COL_KRAKEN = (112, 62, 152)
COL_KRAKEN_OSC = (72, 36, 102)
COL_KRAKEN_LUZ = (150, 95, 190)
COL_VENTOSA = (205, 145, 225)
COL_OJO = (255, 220, 60)
COL_PUPILA = (30, 20, 40)
COL_ORBE = (255, 240, 150)
COL_TINTA = (25, 15, 40)


def crear_jefe(suelo, ancho_mundo):
    x_cuerpo = ancho_mundo - 280
    return {
        "cx": x_cuerpo + 140,
        "cuerpo": pygame.Rect(x_cuerpo, 0, 280, suelo.top),
        "fase": 0,
        "golpe_tick": 0,
        "timer_oleada": 90,
        "tentaculos": [],      # {"x", "alto_max", "estado": aviso|sube|arriba|baja, "timer", "alto"}
        "tinta": [],           # {"x","y","vx","fase_sin","r"}
        "timer_tinta": 0,
        "orbe": None,          # {"x","y","carga","volando": bool, "progreso"}
        "timer_orbe": FRAMES_PAUSA_ORBE[0],
        "idx_orbe": 0,
        "derrotado": False,
        "hundido": 0.0,
        "burbujas": [],        # decorativas {"x","y","vy","r","vida"}
        "tick": 0,
    }


def reiniciar_jefe(jefe, botones_colores, suelo):
    nuevo = crear_jefe(suelo, jefe["cuerpo"].right)
    for clave, valor in nuevo.items():
        if clave != "cuerpo":
            jefe[clave] = valor


def _burbujas(jefe, x, y, cantidad=6):
    for _ in range(cantidad):
        jefe["burbujas"].append({"x": x + random.randint(-16, 16), "y": y, "vy": random.uniform(-2.5, -1.0),
                                 "r": random.randint(2, 5), "vida": random.randint(25, 50)})


def _rect_tentaculo(t, suelo):
    return pygame.Rect(t["x"] - ANCHO_TENTACULO // 2, suelo.top - int(t["alto"]), ANCHO_TENTACULO, int(t["alto"]))


def actualizar_jefe(jefe, botones_colores, jugadores, suelo, plataformas):
    """Devuelve (jugadores golpeados, recién derrotado)."""
    jefe["tick"] += 1
    fase = min(jefe["fase"], GOLPES_PARA_VENCER - 1)

    vivas = []
    for b in jefe["burbujas"]:
        b["y"] += b["vy"]; b["x"] += math.sin(jefe["tick"] * 0.2 + b["r"]) * 0.4; b["vida"] -= 1
        if b["vida"] > 0 and b["y"] > 0:
            vivas.append(b)
    jefe["burbujas"] = vivas

    if jefe["derrotado"]:
        jefe["hundido"] = min(1.0, jefe["hundido"] + 1 / 90)
        if jefe["hundido"] < 1.0 and jefe["tick"] % 3 == 0:
            _burbujas(jefe, jefe["cx"] + random.randint(-100, 100), suelo.top - 40, 2)
        jefe["tentaculos"] = []
        jefe["tinta"] = []
        return [], False

    if jefe["golpe_tick"] > 0:
        jefe["golpe_tick"] -= 1

    vivos = [p for p, comp in jugadores if not comp and not p["muerto"]]
    golpeados = []

    # Oleadas de tentáculos
    jefe["timer_oleada"] -= 1
    if jefe["timer_oleada"] <= 0:
        jefe["timer_oleada"] = FRAMES_ENTRE_OLEADAS[fase]
        posiciones = random.sample(POSICIONES_TENTACULO, TENTACULOS_POR_OLEADA[fase])
        for i, x in enumerate(posiciones):
            jefe["tentaculos"].append({
                "x": x, "alto_max": random.choice(ALTURAS_TENTACULO[:fase + 1] or ALTURAS_TENTACULO[:1]),
                "estado": "aviso", "timer": FRAMES_AVISO + i * 8, "alto": 0.0,
            })
    vivas = []
    for t in jefe["tentaculos"]:
        t["timer"] -= 1
        if t["estado"] == "aviso":
            if t["timer"] % 6 == 0:
                _burbujas(jefe, t["x"], suelo.top - 6, 1)
            if t["timer"] <= 0:
                t["estado"] = "sube"; t["timer"] = FRAMES_SUBIDA
        elif t["estado"] == "sube":
            t["alto"] = t["alto_max"] * (1 - t["timer"] / FRAMES_SUBIDA)
            if t["timer"] <= 0:
                t["estado"] = "arriba"; t["timer"] = FRAMES_ARRIBA[fase]; t["alto"] = t["alto_max"]
        elif t["estado"] == "arriba":
            if t["timer"] <= 0:
                t["estado"] = "baja"; t["timer"] = FRAMES_SUBIDA
        elif t["estado"] == "baja":
            t["alto"] = t["alto_max"] * (t["timer"] / FRAMES_SUBIDA)
            if t["timer"] <= 0:
                continue
        if t["alto"] > 8:
            zona = _rect_tentaculo(t, suelo).inflate(-12, -10)
            for p in vivos:
                if p["hitbox"].colliderect(zona):
                    golpeados.append(p)
        vivas.append(t)
    jefe["tentaculos"] = vivas

    # Tinta (desde la fase 1)
    if FRAMES_TINTA[fase] > 0:
        jefe["timer_tinta"] -= 1
        if jefe["timer_tinta"] <= 0:
            jefe["timer_tinta"] = FRAMES_TINTA[fase]
            objetivo = random.choice(vivos)["hitbox"].centery if vivos else 300
            jefe["tinta"].append({"x": float(jefe["cuerpo"].left - 20), "y": float(objetivo), "vx": -VELOCIDAD_TINTA[fase],
                                  "fase_sin": random.uniform(0, 6.28), "r": 22})
    vivas = []
    for m in jefe["tinta"]:
        m["x"] += m["vx"]
        m["y"] += math.sin(jefe["tick"] * 0.08 + m["fase_sin"]) * 1.4
        if m["x"] < -40:
            continue
        zona = pygame.Rect(int(m["x"]) - m["r"] + 6, int(m["y"]) - m["r"] + 6, 2 * m["r"] - 12, 2 * m["r"] - 12)
        for p in vivos:
            if p["hitbox"].colliderect(zona):
                golpeados.append(p)
        vivas.append(m)
    jefe["tinta"] = vivas

    # Orbe de luz
    recien_derrotado = False
    orbe = jefe["orbe"]
    if orbe is None:
        jefe["timer_orbe"] -= 1
        if jefe["timer_orbe"] <= 0:
            x, y = POSICIONES_ORBE[jefe["idx_orbe"] % len(POSICIONES_ORBE)]
            jefe["idx_orbe"] += 1
            jefe["orbe"] = {"x": x, "y": y, "carga": 0, "volando": False, "progreso": 0.0, "x0": x, "y0": y}
    elif orbe["volando"]:
        orbe["progreso"] += 1 / 30
        ojo_x, ojo_y = jefe["cx"] - 60, 250
        orbe["x"] = orbe["x0"] + (ojo_x - orbe["x0"]) * orbe["progreso"]
        orbe["y"] = orbe["y0"] + (ojo_y - orbe["y0"]) * orbe["progreso"]
        if orbe["progreso"] >= 1.0:
            jefe["orbe"] = None
            jefe["fase"] += 1
            jefe["golpe_tick"] = 45
            jefe["tentaculos"] = []
            jefe["tinta"] = []
            _burbujas(jefe, ojo_x, ojo_y, 14)
            if jefe["fase"] >= GOLPES_PARA_VENCER:
                jefe["derrotado"] = True
                recien_derrotado = True
            else:
                jefe["timer_orbe"] = FRAMES_PAUSA_ORBE[min(jefe["fase"], 2)]
                jefe["timer_oleada"] = 90
    else:
        dentro = 0
        for p in vivos:
            hb = p["hitbox"]
            if math.hypot(hb.centerx - orbe["x"], hb.centery - orbe["y"]) <= RADIO_ORBE:
                dentro += 1
        if dentro >= 2:
            orbe["carga"] += 1
        else:
            orbe["carga"] = max(0, orbe["carga"] - 2)
        if orbe["carga"] >= FRAMES_CARGA_ORBE:
            orbe["volando"] = True
            orbe["x0"], orbe["y0"] = orbe["x"], orbe["y"]

    return golpeados, recien_derrotado


# ------------------------------------------------------------------------------
# Dibujo
# ------------------------------------------------------------------------------

def _dibujar_tentaculo(surf, rect, tick, desfase=0):
    if rect.height <= 2:
        return
    cuerpo = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    puntos_i, puntos_d = [], []
    pasos = max(2, rect.height // 12)
    for i in range(pasos + 1):
        y = rect.height * i / pasos
        ancho = rect.width * (0.45 + 0.55 * (y / rect.height))   # más fino en la punta
        ondu = math.sin(tick * 0.1 + desfase + i * 0.6) * 5 * (1 - y / rect.height)
        cx = cuerpo.get_width() // 2 + ondu
        puntos_i.append((cx - ancho / 2, y + 10)); puntos_d.append((cx + ancho / 2, y + 10))
    pts = puntos_i + puntos_d[::-1]
    pygame.draw.polygon(cuerpo, COL_KRAKEN_OSC, [(x + 3, y + 3) for x, y in pts])
    pygame.draw.polygon(cuerpo, COL_KRAKEN, pts)
    pygame.draw.polygon(cuerpo, COL_KRAKEN_OSC, pts, 2)
    for i in range(1, pasos):
        y = rect.height * i / pasos + 10
        cx = (puntos_i[i][0] + puntos_d[i][0]) / 2
        pygame.draw.circle(cuerpo, COL_VENTOSA, (int(cx), int(y)), 4)
    surf.blit(cuerpo, (rect.left - 10, rect.top - 10))


def dibujar_proyectiles(surf, jefe):
    # El dibujo de tentáculos/orbe/tinta necesita el suelo; se guarda en el jefe al dibujar el cuerpo.
    suelo_top = jefe.get("_suelo_top")
    if suelo_top is None:
        return
    tick = jefe["tick"]
    for t in jefe["tentaculos"]:
        if t["estado"] == "aviso":
            alpha = 90 + int(60 * math.sin(tick * 0.4))
            aviso = pygame.Surface((ANCHO_TENTACULO + 30, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(aviso, (220, 120, 255, alpha), aviso.get_rect())
            surf.blit(aviso, (t["x"] - aviso.get_width() // 2, suelo_top - 8))
        else:
            r = pygame.Rect(t["x"] - ANCHO_TENTACULO // 2, suelo_top - int(t["alto"]), ANCHO_TENTACULO, int(t["alto"]))
            _dibujar_tentaculo(surf, r, tick, t["x"])
    for m in jefe["tinta"]:
        mancha = pygame.Surface((m["r"] * 2 + 8, m["r"] * 2 + 8), pygame.SRCALPHA)
        c = mancha.get_width() // 2
        pygame.draw.circle(mancha, (*COL_TINTA, 200), (c, c), m["r"])
        for k in range(4):
            ang = tick * 0.15 + k * 1.6
            pygame.draw.circle(mancha, (*COL_TINTA, 150), (c + int(math.cos(ang) * m["r"] * 0.7), c + int(math.sin(ang) * m["r"] * 0.7)), m["r"] // 2)
        surf.blit(mancha, (int(m["x"]) - c, int(m["y"]) - c))
    for b in jefe["burbujas"]:
        pygame.draw.circle(surf, (200, 235, 255), (int(b["x"]), int(b["y"])), b["r"], 1)
    orbe = jefe["orbe"]
    if orbe is not None:
        r = RADIO_ORBE
        halo = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
        c = halo.get_width() // 2
        pulso = 0.5 + 0.5 * math.sin(tick * 0.12)
        if orbe["volando"]:
            pygame.draw.circle(halo, (*COL_ORBE, 230), (c, c), 22)
            pygame.draw.circle(halo, (*COL_ORBE, 90), (c, c), 34)
        else:
            pygame.draw.circle(halo, (*COL_ORBE, int(45 + 30 * pulso)), (c, c), r)
            pygame.draw.circle(halo, (*COL_ORBE, 180), (c, c), r, 3)
            pygame.draw.circle(halo, (255, 252, 220, 220), (c, c), 14)
            if orbe["carga"] > 0:
                ang_fin = -math.pi / 2 + 2 * math.pi * orbe["carga"] / FRAMES_CARGA_ORBE
                pygame.draw.arc(halo, (255, 255, 255, 255), (c - r - 6, c - r - 6, 2 * r + 12, 2 * r + 12), -ang_fin, math.pi / 2, 6)
        surf.blit(halo, (int(orbe["x"]) - c, int(orbe["y"]) - c))


def dibujar_jefe(surf, jefe, suelo):
    jefe["_suelo_top"] = suelo.top
    cx = jefe["cx"]
    tick = jefe["tick"]
    cuerpo = jefe["cuerpo"]
    fase = min(jefe["fase"], 2)

    hund = jefe["hundido"] if jefe["derrotado"] else 0.0
    desplaz_y = int(hund * 900)
    if hund >= 1.0:
        return          # ya se hundió del todo: deja libres la llave y la puerta
    if jefe["golpe_tick"] > 0:
        cx += int(math.sin(tick * 1.4) * 8)
    flot = int(math.sin(tick * 0.04) * 8)

    # Cuerpo: masa oscura que ocupa toda la columna derecha (tapa llave y puerta) + cabeza
    masa = pygame.Rect(cuerpo.left + 20, 140 + flot + desplaz_y, cuerpo.width + 40, cuerpo.height)
    pygame.draw.ellipse(surf, COL_KRAKEN_OSC, masa)
    cabeza = pygame.Rect(cx - 120, 110 + flot + desplaz_y, 260, 230)
    pygame.draw.ellipse(surf, COL_KRAKEN_OSC, cabeza.move(6, 8))
    pygame.draw.ellipse(surf, COL_KRAKEN, cabeza)
    pygame.draw.ellipse(surf, COL_KRAKEN_LUZ, (cabeza.left + 40, cabeza.top + 20, 90, 50))
    pygame.draw.ellipse(surf, COL_KRAKEN_OSC, cabeza, 4)

    # Tentáculos propios colgando del cuerpo (decorativos)
    for i in range(4):
        tx = cuerpo.left + 30 + i * 60
        alto = 150 + int(math.sin(tick * 0.05 + i) * 20)
        r = pygame.Rect(tx - 18, cabeza.bottom - 30, 36, alto)
        _dibujar_tentaculo(surf, pygame.Rect(r.left, r.top, r.width, r.height), tick, i * 1.3)

    # Ojos (el izquierdo es el que recibe el orbe)
    for ex in (cx - 60, cx + 30):
        ojo = pygame.Rect(ex - 26, 225 + flot + desplaz_y, 52, 52)
        if jefe["derrotado"]:
            pygame.draw.line(surf, COL_PUPILA, (ojo.left + 10, ojo.top + 10), (ojo.right - 10, ojo.bottom - 10), 5)
            pygame.draw.line(surf, COL_PUPILA, (ojo.right - 10, ojo.top + 10), (ojo.left + 10, ojo.bottom - 10), 5)
            continue
        pygame.draw.ellipse(surf, COL_OJO, ojo)
        pygame.draw.ellipse(surf, COL_KRAKEN_OSC, ojo, 3)
        pupila_x = ojo.centerx - 6 + (4 if fase > 0 else 0)
        pygame.draw.ellipse(surf, COL_PUPILA, (pupila_x - 6, ojo.centery - 14, 14, 28))
        if fase > 0:
            pygame.draw.polygon(surf, COL_KRAKEN_OSC, [(ojo.left - 4, ojo.top - 2), (ojo.right + 4, ojo.top + 14), (ojo.right + 4, ojo.top - 6)])

    # Boca
    boca_y = cabeza.bottom - 40
    if fase > 0 and not jefe["derrotado"]:
        pygame.draw.arc(surf, COL_PUPILA, (cx - 50, boca_y - 10, 100, 40), math.pi, 2 * math.pi, 5)
    else:
        pygame.draw.arc(surf, COL_PUPILA, (cx - 40, boca_y - 25, 80, 40), 0, math.pi, 5)

    if jefe["derrotado"]:
        return

    # Vida restante (ojos chicos en columna a la izquierda de la cabeza, lejos del HUD)
    for i in range(GOLPES_PARA_VENCER):
        x = cabeza.left - 34
        y = cabeza.top + 50 + i * 36
        lleno = i < GOLPES_PARA_VENCER - jefe["fase"]
        pygame.draw.circle(surf, COL_KRAKEN_OSC, (x, y), 12)
        pygame.draw.circle(surf, COL_OJO if lleno else (90, 80, 110), (x, y), 9)
        if lleno:
            pygame.draw.circle(surf, COL_PUPILA, (x, y), 4)
