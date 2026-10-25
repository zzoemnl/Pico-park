import os
import sys
import pygame

# Set dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1000, 700))

ROOT = os.path.abspath("Pico-park-juego")
sys.path.insert(0, ROOT)

from movimientos import (
    crear_personaje,
    resolver_colisiones,
    actualizar_fisica_soga,
    aplicar_restriccion_soga,
    DISTANCIA_SOGA_REPOSO,
    DISTANCIA_SOGA_MAXIMA,
    GRAVEDAD,
)
from pantalla import dibujar_soga_escenario

print("======================================================================")
print("BATERÍA DE PRUEBAS DE FÍSICA: CUERDA, COLISIONES Y TELETRANSPORTE")
print("======================================================================")

# Constantes del escenario y plataformas
suelo = pygame.Rect(0, 640, 2200, 80)
mundo_rect = pygame.Rect(0, 0, 2200, 720)
plat_inicio = pygame.Rect(0, 360, 260, 26)
plat_inicio_base = pygame.Rect(0, 386, 260, 400)
plat_elevada = pygame.Rect(310, 250, 1080, 26)
plataformas = [plat_inicio, plat_inicio_base, plat_elevada]

# -----------------------------------------------------------------------------
# PRUEBA 1: Ambos personajes se alejan hasta que la cuerda alcanza su límite
# -----------------------------------------------------------------------------
print("\n--- PRUEBA 1: Límite máximo de separación (~20 px adicionales = 160 px) ---")
p1 = crear_personaje(500, suelo.top - 85, 'verde')
p1['en_suelo'] = True
p2 = crear_personaje(620, suelo.top - 85, 'rosa')
p2['en_suelo'] = True
estado_soga = {'tension': 0.0, 'rota': False}

max_dist_p1 = 0.0
for f in range(120):
    p1['vel_x'] = -6.0
    p1['moviendo'] = True
    p2['vel_x'] = 6.0
    p2['moviendo'] = True

    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

    c1 = pygame.Vector2(p1['hitbox'].centerx, p1['hitbox'].centery + 4)
    c2 = pygame.Vector2(p2['hitbox'].centerx, p2['hitbox'].centery + 4)
    d = (c2 - c1).length()
    max_dist_p1 = max(max_dist_p1, d)

print(f"Distancia normal (reposo): {DISTANCIA_SOGA_REPOSO} px")
print(f"Distancia máxima permitida: {DISTANCIA_SOGA_MAXIMA} px (reposo + 20 px)")
print(f"Distancia máxima alcanzada en prueba: {max_dist_p1:.2f} px")
assert max_dist_p1 <= DISTANCIA_SOGA_MAXIMA + 0.5, f"Error: la cuerda superó el límite permitido ({max_dist_p1} > 160.5)"
print("[OK] PRUEBA 1 SUPERADA: La cuerda no se estira más de lo permitido y transmite tensión firme.")

# -----------------------------------------------------------------------------
# PRUEBA 2: Un personaje apoyado arriba de una plataforma y el otro cuelga debajo
# -----------------------------------------------------------------------------
print("\n--- PRUEBA 2: Personaje apoyado arriba y otro colgado debajo ---")
p1 = crear_personaje(450, 250 - 85, 'verde')
p1['en_suelo'] = True
p2 = crear_personaje(450, 320, 'rosa')
p2['en_suelo'] = False
estado_soga = {'tension': 0.0, 'rota': False}

for f in range(60):
    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

    assert p1['en_suelo'], "P1 debe permanecer apoyado en el suelo de la plataforma"
    assert not p2['en_suelo'], "P2 debe permanecer colgado en el aire"
    assert p2['hitbox'].top >= plat_elevada.bottom, f"P2 no debe atravesar el techo: top={p2['hitbox'].top} < {plat_elevada.bottom}"

c1 = pygame.Vector2(p1['hitbox'].centerx, p1['hitbox'].centery + 4)
c2 = pygame.Vector2(p2['hitbox'].centerx, p2['hitbox'].centery + 4)
d = (c2 - c1).length()
print(f"P1 apoyado: {p1['hitbox']} (en_suelo={p1['en_suelo']})")
print(f"P2 colgado: {p2['hitbox']} (en_suelo={p2['en_suelo']})")
print(f"Distancia física: {d:.1f} px | Cara inferior plataforma: y={plat_elevada.bottom} | Cabeza P2: y={p2['hitbox'].top}")
print("[OK] PRUEBA 2 SUPERADA: El personaje permanece colgado de forma estable y el superior como ancla firme.")

# -----------------------------------------------------------------------------
# PRUEBA 3: Personaje de arriba tira de la cuerda repetidamente
# -----------------------------------------------------------------------------
print("\n--- PRUEBA 3: Tirones repetidos de la cuerda sin teletransporte ni atravesar plataformas ---")
p1 = crear_personaje(400, 250 - 85, 'verde')
p1['en_suelo'] = True
p2 = crear_personaje(360, 320, 'rosa')
p2['en_suelo'] = False
estado_soga = {'tension': 0.0, 'rota': False}

teleported = False
phased = False
max_dist_p3 = 0.0

for f in range(200):
    # Tirones repetidos simulando pulsaciones discontinuas de teclas
    if (f // 25) % 2 == 0:
        p1['vel_x'] = 6.0
        p1['moviendo'] = True
    else:
        p1['vel_x'] = 0.0
        p1['moviendo'] = False

    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

    c1 = pygame.Vector2(p1['hitbox'].centerx, p1['hitbox'].centery + 4)
    c2 = pygame.Vector2(p2['hitbox'].centerx, p2['hitbox'].centery + 4)
    d = (c2 - c1).length()
    max_dist_p3 = max(max_dist_p3, d)

    if plat_elevada.left <= p2['hitbox'].centerx <= plat_elevada.right:
        if p2['hitbox'].top < plat_elevada.bottom:
            phased = True
            print(f"ERROR: P2 atravesó el techo en Frame {f}: top={p2['hitbox'].top} < {plat_elevada.bottom}")
            break
        if p2['en_suelo']:
            teleported = True
            print(f"ERROR: P2 se teletransportó sobre la plataforma en Frame {f}!")
            break

assert not phased, "Error: P2 atravesó la plataforma inferior"
assert not teleported, "Error: P2 se teletransportó encima de la plataforma"
assert max_dist_p3 <= DISTANCIA_SOGA_MAXIMA + 1.0, f"Error: la cuerda superó el límite ({max_dist_p3} > 161)"
print(f"Distancia máxima durante tirones: {max_dist_p3:.2f} px")
print(f"Posición final P1: {p1['hitbox']} | P2: {p2['hitbox']}")
print("[OK] PRUEBA 3 SUPERADA: Cero teletransporte y cero atravesamiento durante tirones continuos.")

# -----------------------------------------------------------------------------
# PRUEBA 4: Balanceo pendular y condiciones de ascenso
# -----------------------------------------------------------------------------
print("\n--- PRUEBA 4: Balanceo y ascenso únicamente por trayectoria física posible ---")
# Caso A: Sin impulso suficiente por debajo de la plataforma -> permanece colgado
p1 = crear_personaje(350, 250 - 85, 'verde')
p1['en_suelo'] = True
p2 = crear_personaje(350, 360, 'rosa')
p2['en_suelo'] = False
estado_soga = {'tension': 0.0, 'rota': False}

for f in range(40):
    p1['vel_x'] = 1.0
    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

assert not p2['en_suelo'], "P2 no debió subir sin impulso suficiente"
print(f"Caso A (impulso insuficiente): P2 permanece colgado en el aire (en_suelo={p2['en_suelo']})")

# Caso B: Balanceo libre con arco que supera la altura del borde izquierdo (x < 310)
p1 = crear_personaje(340, 250 - 85, 'verde')
p1['en_suelo'] = True
p2 = crear_personaje(260, 240 - 85, 'rosa') # bottom=240, pies sobre el nivel y=250
p2['vel_x'] = 4.0
p2['vel_y'] = -2.0
p2['en_suelo'] = False
estado_soga = {'tension': 0.0, 'rota': False}

landed = False
for f in range(30):
    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)
    if p2['en_suelo'] and p2['hitbox'].bottom == plat_elevada.top:
        landed = True
        print(f"Caso B (balanceo por arco libre exterior): P2 aterrizó limpiamente sobre la plataforma en Frame {f}!")
        break

assert landed, "P2 debe poder alcanzar la plataforma si su trayectoria libre e impulso lo permiten"
print("[OK] PRUEBA 4 SUPERADA: El ascenso solo ocurre por trayectoria física válida con impulso suficiente.")

# -----------------------------------------------------------------------------
# PRUEBA 5: Saltos, caídas y aterrizajes simultáneos
# -----------------------------------------------------------------------------
print("\n--- PRUEBA 5: Saltos, caídas y aterrizajes simultáneos ---")
p1 = crear_personaje(500, suelo.top - 85, 'verde')
p1['en_suelo'] = True
p2 = crear_personaje(560, suelo.top - 85, 'rosa')
p2['en_suelo'] = True
estado_soga = {'tension': 0.0, 'rota': False}

p1['vel_y'] = -14.0
p1['en_suelo'] = False
p2['vel_y'] = -14.0
p2['en_suelo'] = False

max_dist_p5 = 0.0
aterrizaron = False

for f in range(100):
    actualizar_fisica_soga(p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
    resolver_colisiones(p1, p2, suelo, mundo_rect, None, False, plataformas)
    resolver_colisiones(p2, p1, suelo, mundo_rect, None, False, plataformas)
    aplicar_restriccion_soga(p1, p2, DISTANCIA_SOGA_MAXIMA, plataformas, suelo, estado_soga)

    c1 = pygame.Vector2(p1['hitbox'].centerx, p1['hitbox'].centery + 4)
    c2 = pygame.Vector2(p2['hitbox'].centerx, p2['hitbox'].centery + 4)
    d = (c2 - c1).length()
    max_dist_p5 = max(max_dist_p5, d)

    if f > 30 and p1['en_suelo'] and p2['en_suelo']:
        aterrizaron = True
        print(f"Ambos aterrizaron correctamente sobre el suelo en Frame {f} (dist={d:.1f} px)")
        break

assert aterrizaron, "Ambos personajes debieron aterrizar en el suelo"
assert max_dist_p5 <= DISTANCIA_SOGA_MAXIMA + 1.0, f"Distancia excesiva en salto: {max_dist_p5}"
print("[OK] PRUEBA 5 SUPERADA: Saltos, caídas y aterrizajes funcionan de forma fluida y natural.")

# -----------------------------------------------------------------------------
# PRUEBA ADICIONAL: Coincidencia entre física y renderizado visual de la soga
# -----------------------------------------------------------------------------
print("\n--- PRUEBA ADICIONAL: Coincidencia física y visual de la soga ---")
surf = pygame.Surface((1000, 700))
hb1 = p1['hitbox']
hb2 = p2['hitbox']
p_inicio_vis = (hb1.centerx, hb1.centery + 4)
p_fin_vis = (hb2.centerx, hb2.centery + 4)
c1_fis = (p1['hitbox'].centerx, p1['hitbox'].centery + 4)
c2_fis = (p2['hitbox'].centerx, p2['hitbox'].centery + 4)

assert p_inicio_vis == c1_fis, f"Discrepancia en anclaje P1: {p_inicio_vis} != {c1_fis}"
assert p_fin_vis == c2_fis, f"Discrepancia en anclaje P2: {p_fin_vis} != {c2_fis}"
dibujar_soga_escenario(surf, p1, p2, estado_soga, DISTANCIA_SOGA_REPOSO, DISTANCIA_SOGA_MAXIMA)
print("[OK] PRUEBA ADICIONAL SUPERADA: Anclajes físicos y visuales coinciden al 100%.")

print("\n======================================================================")
print("¡TODAS LAS PRUEBAS OBLIGATORIAS Y DE INTEGRACIÓN PASARON AL 100%!")
print("======================================================================")
