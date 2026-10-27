import os
import sys
import pygame
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def test_visual_rendering():
    # 1. Probar renderizado de Nivel 3-4 con oscuridad y linternas
    w, h = 1280, 720
    superficie_3_4 = pygame.Surface((w, h))
    superficie_3_4.fill((16, 44, 76)) # Fondo submarino

    # Dibujar elementos del escenario
    pygame.draw.rect(superficie_3_4, (70, 85, 105), (100, 200, 150, 400)) # Roca
    pygame.draw.rect(superficie_3_4, (255, 120, 80), (350, 500, 60, 60)) # Coral
    pygame.draw.circle(superficie_3_4, (255, 215, 0), (700, 350), 18) # Llave dorada

    # P1 con linterna ON en (200, 350)
    p1 = movimientos.crear_personaje(200, 350, "Verde")
    # P2 con linterna OFF en (600, 350)
    p2 = movimientos.crear_personaje(600, 350, "Rosa")

    pantalla.dibujar_personaje(superficie_3_4, p1, None)
    pantalla.dibujar_personaje(superficie_3_4, p2, None)

    surf_oscuridad = pygame.Surface((w, h), pygame.SRCALPHA)
    surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna()

    pantalla.dibujar_oscuridad_laberinto(
        superficie_3_4,
        [(p1, True, False), (p2, False, False)],
        surf_oscuridad,
        surf_luz,
        surf_tenue
    )

    # 2. Probar renderizado de Nivel 3-5 (escenario 100% visible con haz de luz complementario)
    superficie_3_5 = pygame.Surface((w, h))
    superficie_3_5.fill((16, 44, 76))
    pygame.draw.rect(superficie_3_5, (70, 85, 105), (100, 200, 150, 400)) # Roca
    pygame.draw.rect(superficie_3_5, (255, 120, 80), (350, 500, 60, 60)) # Coral
    pygame.draw.circle(superficie_3_5, (255, 215, 0), (700, 350), 18) # Llave dorada

    # P1 con linterna ON en (300, 350), mirando a la derecha
    p1_35 = movimientos.crear_personaje(300, 350, "Verde")
    p1_35["mirando_derecha"] = True
    # P2 con linterna OFF en (600, 350)
    p2_35 = movimientos.crear_personaje(600, 350, "Rosa")

    pantalla.dibujar_personaje(superficie_3_5, p1_35, None)
    pantalla.dibujar_personaje(superficie_3_5, p2_35, None)

    # Validar que toda la superficie permanezca visible antes y después
    col_pre_lejana = superficie_3_5.get_at((1000, 100))

    # Simular dibujo de linternas 3-5
    # (Definiremos la función en pantalla.py, aquí probamos su prototipo)
    s_haz = pygame.Surface((w, h), pygame.SRCALPHA)
    pantalla.dibujar_linterna_minero(superficie_3_5, p1_35, True)
    pantalla.dibujar_linterna_minero(superficie_3_5, p2_35, False)

    # Proyección del haz de luz de P1 con capas suaves y efecto submarino
    hx = p1_35["hitbox"].centerx
    hy = p1_35["hitbox"].top + 10
    lx = hx + 12
    ly = hy - 2

    # Aura radial suave alrededor del buceador
    for r_aura, a_aura in [(75, 10), (55, 18), (35, 28)]:
        pygame.draw.circle(s_haz, (215, 240, 255, a_aura), (hx, p1_35["hitbox"].centery), r_aura)

    # Haz de luz submarino en abanico con degradado suave
    capas_haz = [
        (240, 52, (200, 235, 255, 15)),
        (200, 40, (215, 245, 255, 25)),
        (160, 28, (240, 250, 255, 40)),
        (110, 18, (255, 252, 225, 60)),
        (60, 10, (255, 255, 240, 85)),
    ]
    for largo, apertura, col in capas_haz:
        pts = [(lx, ly - 3), (lx + largo, ly - apertura), (lx + largo, ly + apertura), (lx, ly + 3)]
        pygame.draw.polygon(s_haz, col, pts)

    # Resplandor en la lente y foco frontal
    pygame.draw.circle(s_haz, (255, 250, 210, 120), (lx, ly), 14)
    pygame.draw.circle(s_haz, (255, 255, 255, 190), (lx, ly), 6)

    # Motas de luz reflejadas en el agua dentro del haz
    for offset_m, y_dev, r_mota, alpha_m in [(45, 4, 2, 90), (95, -8, 3, 110), (145, 12, 2, 85), (185, -6, 2, 70)]:
        pygame.draw.circle(s_haz, (255, 255, 240, alpha_m), (lx + offset_m, ly + y_dev), r_mota)

    superficie_3_5.blit(s_haz, (0, 0))

    col_post_lejana = superficie_3_5.get_at((1000, 100))
    col_haz = superficie_3_5.get_at((lx + 80, ly))

    print(f"3-5: Color lejano antes: {col_pre_lejana}, Color lejano después: {col_post_lejana}")
    print(f"3-5: Color dentro del haz iluminado: {col_haz}")

    assert col_pre_lejana == col_post_lejana, "En 3-5 la zona lejana NO debe oscurecerse, debe permanecer 100% visible"
    assert col_haz[0] > col_pre_lejana[0], "El haz de luz debe iluminar el escenario frente al personaje"

    pygame.image.save(superficie_3_4, "scratch/preview_3_4_linternas.png")
    pygame.image.save(superficie_3_5, "scratch/preview_3_5_linternas.png")
    print("[OK] Ambas pruebas de renderizado visual 3-4 y 3-5 completadas exitosamente.")

if __name__ == "__main__":
    test_visual_rendering()
