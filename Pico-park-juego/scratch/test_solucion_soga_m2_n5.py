import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def nueva_actualizar_fisica_soga(p1, p2, estado_soga=None, d_reposo=movimientos.DISTANCIA_SOGA_REPOSO, d_max=movimientos.DISTANCIA_SOGA_MAXIMA):
    if p1.get("muerto", False) or p2.get("muerto", False) or (estado_soga is not None and estado_soga.get("rota", False)):
        movimientos.actualizar_estado_soga_muerte(p1, p2, estado_soga, d_max)
        if estado_soga is not None:
            estado_soga["tension"] = 0.0
        return

    c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
    c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
    v = c2 - c1
    distancia = v.length()

    if distancia < 0.001:
        if estado_soga is not None:
            estado_soga["tension"] = 0.0
        return

    direccion = v / distancia

    if distancia <= d_reposo:
        if estado_soga is not None:
            estado_soga["tension"] = 0.0
        return

    estiramiento = distancia - d_reposo
    rango = max(1.0, d_max - d_reposo)
    tasa = min(1.0, estiramiento / rango)
    tension_objetivo = tasa * tasa

    if distancia >= d_max:
        tension_objetivo = 1.0

    if estado_soga is not None:
        tension_actual = estado_soga.get("tension", 0.0)
        if tension_objetivo > tension_actual:
            factor_retardo = 0.35 if distancia < d_max else 0.85
            tension_actual += (tension_objetivo - tension_actual) * factor_retardo
        else:
            tension_actual += (tension_objetivo - tension_actual) * 0.50
            if tension_actual < 0.001:
                tension_actual = 0.0
        estado_soga["tension"] = max(0.0, min(1.0, tension_actual))
        t = estado_soga["tension"]
    else:
        t = tension_objetivo

    if t <= 0.01:
        return

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_rel = v2 - v1
    v_separacion = v_rel.dot(direccion)

    # 1. Ambos en el suelo
    if p1_suelo and p2_suelo:
        if v_separacion > 0:
            sep_max_permitida = max(0.0, d_max - distancia)
            exceso_vel = max(0.0, v_separacion - sep_max_permitida)
            if exceso_vel > 0:
                p1_away = max(0.0, -v1.dot(direccion))
                p2_away = max(0.0, v2.dot(direccion))
                tot = p1_away + p2_away
                if tot > 0.001:
                    p1["vel_x"] += direccion.x * (exceso_vel * (p1_away / tot))
                    p2["vel_x"] -= direccion.x * (exceso_vel * (p2_away / tot))
            else:
                factor_freno = t * 0.60
                if v1.dot(direccion) < 0:
                    p1["vel_x"] += direccion.x * (v_separacion * factor_freno * 0.5)
                if v2.dot(direccion) > 0:
                    p2["vel_x"] -= direccion.x * (v_separacion * factor_freno * 0.5)
        return

    # 2. P1 en suelo, P2 en el aire (P1 es el ancla estable sobre la plataforma)
    if p1_suelo and not p2_suelo:
        if direccion.y > 0.05:
            # P2 cuelga por debajo de P1: física de péndulo real
            # P2 siente soporte contra la gravedad y aceleración centrípeta
            p2["vel_y"] -= t * movimientos.GRAVEDAD * (direccion.y * direccion.y)
            p2["vel_x"] -= t * movimientos.GRAVEDAD * (direccion.y * direccion.x)

            v_tan = v_rel - v_separacion * direccion
            v_tan_mag = v_tan.length()
            a_c = min(3.5, (v_tan_mag * v_tan_mag) / max(1.0, distancia))
            p2["vel_x"] -= t * a_c * direccion.x
            p2["vel_y"] -= t * a_c * direccion.y

            if v_separacion > 0:
                damp = v_separacion * (0.45 + 0.35 * t)
                p2["vel_x"] -= direccion.x * damp
                p2["vel_y"] -= direccion.y * damp

            # P1 sobre la plataforma:
            # - Si P1 NO se está moviendo, la fricción estática lo mantiene 100% inmóvil.
            # - Si P1 se mueve caminando, no se le anula la velocidad; puede remolcar a P2 con fluidez.
            if p1.get("moviendo", False):
                # Leve resistencia natural de remolque solo al límite máximo
                if distancia >= d_max and v1.dot(direccion) < 0:
                    p1["vel_x"] *= 0.88
            else:
                # Estable sobre la plataforma: sin vibraciones ni deslizamiento involuntario
                p1["vel_x"] = 0.0
        else:
            # P2 está por encima o al mismo nivel (salto estándar)
            fuerza_tiron = t * 1.3
            if direccion.y < -0.15:
                p2["vel_y"] -= direccion.y * (t * 0.6)
            p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.6)
            if v_separacion > 0:
                p2["vel_x"] -= direccion.x * (v_separacion * 0.5)
        return

    # 3. P2 en suelo, P1 en el aire (P2 es el ancla estable sobre la plataforma)
    if p2_suelo and not p1_suelo:
        if direccion.y < -0.05:
            dir_hacia_p1 = -direccion
            v_rel_p1 = v1 - v2
            v_sep_p1 = v_rel_p1.dot(dir_hacia_p1)

            p1["vel_y"] -= t * movimientos.GRAVEDAD * (dir_hacia_p1.y * dir_hacia_p1.y)
            p1["vel_x"] -= t * movimientos.GRAVEDAD * (dir_hacia_p1.y * dir_hacia_p1.x)

            v_tan = v_rel_p1 - v_sep_p1 * dir_hacia_p1
            v_tan_mag = v_tan.length()
            a_c = min(3.5, (v_tan_mag * v_tan_mag) / max(1.0, distancia))
            p1["vel_x"] -= t * a_c * dir_hacia_p1.x
            p1["vel_y"] -= t * a_c * dir_hacia_p1.y

            if v_sep_p1 > 0:
                damp = v_sep_p1 * (0.45 + 0.35 * t)
                p1["vel_x"] -= dir_hacia_p1.x * damp
                p1["vel_y"] -= dir_hacia_p1.y * damp

            if p2.get("moviendo", False):
                if distancia >= d_max and v2.dot(dir_hacia_p1) < 0:
                    p2["vel_x"] *= 0.88
            else:
                p2["vel_x"] = 0.0
        else:
            fuerza_tiron = t * 1.3
            if direccion.y > 0.15:
                p1["vel_y"] += direccion.y * (t * 0.6)
            p1["vel_x"] += direccion.x * (fuerza_tiron * 0.6)
            if v_separacion > 0:
                p1["vel_x"] += direccion.x * (v_separacion * 0.5)
        return

    # 4. Ambos personajes en el aire
    # Si uno está arriba y el otro abajo:
    fuerza_tiron = t * 1.0
    p1["vel_x"] += direccion.x * (fuerza_tiron * 0.35)
    p2["vel_x"] -= direccion.x * (fuerza_tiron * 0.35)

    # Si el personaje de arriba está saltando (vel_y < 0) y el otro cuelga (direccion.y > 0):
    # La cuerda transmite elevación al personaje de abajo (lo alza), en lugar de cancelar el salto del de arriba
    if v_separacion > 0:
        sep_max_permitida = max(0.0, d_max - distancia)
        exceso_vel = max(0.0, v_separacion - sep_max_permitida)
        if exceso_vel > 0:
            if direccion.y > 0.15:
                # P1 arriba, P2 abajo: P1 eleva a P2 con fuerza de izado
                if p1["vel_y"] < 0:
                    p2["vel_y"] += (p1["vel_y"] - p2["vel_y"]) * 0.45 * t
                    p1["vel_y"] += direccion.y * (exceso_vel * 0.06)
                else:
                    p1["vel_y"] += direccion.y * (exceso_vel * 0.35)
                    p2["vel_y"] -= direccion.y * (exceso_vel * 0.35)
            elif direccion.y < -0.15:
                # P2 arriba, P1 abajo: P2 eleva a P1 con fuerza de izado
                if p2["vel_y"] < 0:
                    p1["vel_y"] += (p2["vel_y"] - p1["vel_y"]) * 0.45 * t
                    p2["vel_y"] -= direccion.y * (exceso_vel * 0.06)
                else:
                    p1["vel_y"] += direccion.y * (exceso_vel * 0.35)
                    p2["vel_y"] -= direccion.y * (exceso_vel * 0.35)
            else:
                p1["vel_y"] += direccion.y * (exceso_vel * 0.35)
                p2["vel_y"] -= direccion.y * (exceso_vel * 0.35)
            p1["vel_x"] += direccion.x * (exceso_vel * 0.25)
            p2["vel_x"] -= direccion.x * (exceso_vel * 0.25)
        else:
            damp = v_separacion * (0.30 + 0.25 * t)
            p1["vel_x"] += direccion.x * (damp * 0.4)
            p1["vel_y"] += direccion.y * (damp * 0.4)
            p2["vel_x"] -= direccion.x * (damp * 0.4)
            p2["vel_y"] -= direccion.y * (damp * 0.4)


def nueva_aplicar_restriccion_soga(p1, p2, distancia_maxima=movimientos.DISTANCIA_SOGA_MAXIMA, plataformas=None, suelo=None, estado_soga=None):
    if p1.get("muerto", False) or p2.get("muerto", False) or (estado_soga is not None and estado_soga.get("rota", False)):
        return

    c1 = pygame.Vector2(p1["hitbox"].centerx, p1["hitbox"].centery + 4)
    c2 = pygame.Vector2(p2["hitbox"].centerx, p2["hitbox"].centery + 4)
    v = c2 - c1
    distancia = v.length()

    if distancia <= distancia_maxima or distancia < 0.001:
        return

    direccion = v / distancia
    exceso = distancia - distancia_maxima

    p1_suelo = p1.get("en_suelo", False)
    p2_suelo = p2.get("en_suelo", False)

    # ASIGNACIÓN DE PESOS: El personaje firme sobre la plataforma no se teletransporta ni desplaza
    if p1_suelo and not p2_suelo:
        w1, w2 = 0.0, 1.0
    elif p2_suelo and not p1_suelo:
        w1, w2 = 1.0, 0.0
    elif not p1_suelo and not p2_suelo:
        if direccion.y > 0.15 and p1.get("vel_y", 0) < 0:
            w1, w2 = 0.0, 1.0
        elif direccion.y < -0.15 and p2.get("vel_y", 0) < 0:
            w1, w2 = 1.0, 0.0
        else:
            w1, w2 = 0.50, 0.50
    else:
        w1, w2 = 0.50, 0.50

    v1 = pygame.Vector2(p1.get("vel_x", 0.0), p1.get("vel_y", 0.0))
    v2 = pygame.Vector2(p2.get("vel_x", 0.0), p2.get("vel_y", 0.0))
    v_separacion = (v2 - v1).dot(direccion)

    if v_separacion > 0:
        if w1 > 0:
            p1["vel_x"] += direccion.x * (v_separacion * w1)
            p1["vel_y"] += direccion.y * (v_separacion * w1)
        if w2 > 0:
            p2["vel_x"] -= direccion.x * (v_separacion * w2)
            p2["vel_y"] -= direccion.y * (v_separacion * w2)

    desp1 = direccion * (exceso * w1)
    desp2 = -direccion * (exceso * w2)

    def ajustar_posicion_con_solidez(p, desp):
        if desp.length_squared() < 0.0001:
            return
        hb = p["hitbox"]
        x_prev = hb.x
        y_prev = hb.y

        dx = int(round(desp.x))
        if dx != 0:
            hb.x += dx
            if plataformas:
                for plat in plataformas:
                    if hb.colliderect(plat) and hb.bottom > plat.top + 2 and hb.top < plat.bottom - 2:
                        if dx > 0 and x_prev + hb.width <= plat.left + 4:
                            hb.right = plat.left
                            if p.get("vel_x", 0) > 0: p["vel_x"] = 0
                        elif dx < 0 and x_prev >= plat.right - 4:
                            hb.left = plat.right
                            if p.get("vel_x", 0) < 0: p["vel_x"] = 0

        dy = int(round(desp.y))
        if dy != 0:
            hb.y += dy
            if suelo is not None and hb.right > suelo.left and hb.left < suelo.right and hb.bottom > suelo.top:
                hb.bottom = suelo.top
                if p.get("vel_y", 0) > 0: p["vel_y"] = 0
                p["en_suelo"] = True

            if plataformas:
                for plat in plataformas:
                    if hb.colliderect(plat):
                        if dy > 0 and y_prev + hb.height <= plat.top + 6:
                            hb.bottom = plat.top
                            if p.get("vel_y", 0) > 0: p["vel_y"] = 0
                            p["en_suelo"] = True
                        elif dy < 0 and y_prev >= plat.bottom - 6:
                            hb.top = plat.bottom
                            if p.get("vel_y", 0) < 0: p["vel_y"] = 0
                        elif y_prev >= plat.bottom:
                            hb.top = plat.bottom
                            if p.get("vel_y", 0) < 0: p["vel_y"] = 0

    if w1 > 0:
        ajustar_posicion_con_solidez(p1, desp1)
    if w2 > 0:
        ajustar_posicion_con_solidez(p2, desp2)


def test_solucion():
    plat = pygame.Rect(430, 390, 230, 24)
    plataformas = [plat]
    suelo = pygame.Rect(0, 640, 1400, 80)
    mundo_rect = pygame.Rect(0, 0, 1400, 720)

    print("==========================================================")
    print("TEST A: ESTABILIDAD DE P1 EN PLATAFORMA CON P2 COLGANDO")
    print("==========================================================")
    p1 = movimientos.crear_personaje(520, 390 - 85, "Celeste")
    p1["en_suelo"] = True
    p2 = movimientos.crear_personaje(670, 420, "Violeta")
    p2["en_suelo"] = False
    p2["vel_y"] = 6.0
    p2["vel_x"] = 2.0
    estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

    for f in range(60):
        p1["vel_x"] = 0
        nueva_actualizar_fisica_soga(p1, p2, estado_soga)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        nueva_aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if f % 10 == 0:
            print(f"F{f:2d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, vx={p1['vel_x']:.2f}, vy={p1['vel_y']:.2f}, suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x}, y={p2['hitbox'].y}, vy={p2['vel_y']:.2f}")

    assert p1["hitbox"].x == 520, f"P1 no debe haberse movido de 520! Actual: {p1['hitbox'].x}"
    assert p1["hitbox"].y == 305, f"P1 debe permanecer en y=305! Actual: {p1['hitbox'].y}"
    assert p1["en_suelo"] == True, "P1 debe permanecer en el suelo firmemente"
    print("[PASO A] P1 permanece 100% estable sobre la plataforma, 0 vibraciones, 0 deslizamiento!")

    print("\n==========================================================")
    print("TEST B: FLUIDEZ AL CAMINAR (P1 CAMINA MIENTRAS P2 CUELGA)")
    print("==========================================================")
    p1_x_ini = p1["hitbox"].x
    for f in range(25):
        p1["vel_x"] = -p1["velocidad_mov"]
        p1["moviendo"] = True
        nueva_actualizar_fisica_soga(p1, p2, estado_soga)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        nueva_aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        if f % 5 == 0:
            print(f"F{f:2d}: P1 x={p1['hitbox'].x}, vx={p1['vel_x']:.2f}, suelo={p1['en_suelo']}")

    dist_caminada = p1_x_ini - p1["hitbox"].x
    print(f"Distancia caminada por P1: {dist_caminada} px")
    assert dist_caminada >= 120, f"P1 debe responder fluidamente al caminar (caminó {dist_caminada}px)"
    print("[PASO B] P1 camina de forma suave y controlada sin cancelaciones ni tirones!")

    print("\n==========================================================")
    print("TEST C: CAPACIDAD DE SALTO (P1 SALTA MIENTRAS P2 CUELGA)")
    print("==========================================================")
    p1["hitbox"].x = 520
    p1["hitbox"].y = 305
    p1["en_suelo"] = True
    p1["vel_x"] = 0
    p1["vel_y"] = p1["fuerza_salto"]
    p1["en_suelo"] = False

    y_inicio = p1["hitbox"].y
    alturas = []
    for f in range(25):
        p1["vel_x"] = 0
        nueva_actualizar_fisica_soga(p1, p2, estado_soga)
        movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
        movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
        nueva_aplicar_restriccion_soga(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
        alturas.append(p1["hitbox"].y)
        if f % 5 == 0:
            print(f"F{f:2d}: P1 y={p1['hitbox'].y}, vy={p1['vel_y']:.2f}, suelo={p1['en_suelo']} | P2 y={p2['hitbox'].y}")

    altura_max = y_inicio - min(alturas)
    print(f"Altura de salto alcanzada por P1: {altura_max} px (anteriormente 13px)")
    assert altura_max >= 60, f"P1 debe poder saltar efectivamente (alcanzó {altura_max}px)"
    print("[PASO C] P1 salta de forma natural y eficaz, levantando a su compañero!")

if __name__ == "__main__":
    test_solucion()
