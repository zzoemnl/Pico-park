import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos

plat = pygame.Rect(180, 480, 230, 24)
plataformas = [plat]
suelo = pygame.Rect(0, 640, 1400, 80)
mundo_rect = pygame.Rect(0, 0, 1400, 720)

print("=== TEST CON w1=0.0 CUANDO P1 ESTÁ EN EL SUELO ===")
# Creamos versión modificada de aplicar_restriccion_soga para probar
def aplicar_restriccion_soga_test(p1, p2, distancia_maxima=movimientos.DISTANCIA_SOGA_MAXIMA, plataformas=None, suelo=None, estado_soga=None):
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

    if p1_suelo and not p2_suelo:
        w1, w2 = 0.0, 1.0
    elif p2_suelo and not p1_suelo:
        w1, w2 = 1.0, 0.0
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

    def ajustar(p, desp):
        if desp.length_squared() == 0:
            return
        hb = p["hitbox"]
        x_prev, y_prev = hb.x, hb.y
        dx = int(round(desp.x))
        if dx != 0:
            hb.x += dx
            if plataformas:
                for pl in plataformas:
                    if hb.colliderect(pl) and hb.bottom > pl.top + 2 and hb.top < pl.bottom - 2:
                        if dx > 0: hb.right = pl.left
                        elif dx < 0: hb.left = pl.right
        dy = int(round(desp.y))
        if dy != 0:
            hb.y += dy
            if plataformas:
                for pl in plataformas:
                    if hb.colliderect(pl):
                        if dy > 0 and y_prev + hb.height <= pl.top + 6:
                            hb.bottom = pl.top
                            p["en_suelo"] = True
                        elif dy < 0 and y_prev >= pl.bottom - 6:
                            hb.top = pl.bottom

    if w1 > 0:
        ajustar(p1, desp1)
    if w2 > 0:
        ajustar(p2, desp2)

p1 = movimientos.crear_personaje(280, 480 - 85, "Celeste")
p1["en_suelo"] = True
p2 = movimientos.crear_personaje(360, 480 + 80, "Violeta")
p2["en_suelo"] = False
estado_soga = {"tirante": False, "distancia": 0, "tension": 0.0, "rota": False}

print("Simulando 60 frames:")
for f in range(60):
    p1["vel_x"] = 0
    movimientos.actualizar_fisica_soga(p1, p2, estado_soga, movimientos.DISTANCIA_SOGA_REPOSO, movimientos.DISTANCIA_SOGA_MAXIMA)
    movimientos.resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    movimientos.resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga_test(p1, p2, movimientos.DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
    if f % 10 == 0:
        print(f"Frame {f:2d}: P1 x={p1['hitbox'].x}, y={p1['hitbox'].y}, vx={p1['vel_x']:.2f}, vy={p1['vel_y']:.2f}, en_suelo={p1['en_suelo']} | P2 x={p2['hitbox'].x}, y={p2['hitbox'].y}")

print(f"\nPosición final P1: x={p1['hitbox'].x}, y={p1['hitbox'].y}")
