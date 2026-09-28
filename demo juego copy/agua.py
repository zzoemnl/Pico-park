import pygame

# ============================================================
# AGUA
# ============================================================

ZONA_AGUA = pygame.Rect(0, 220, 800, 380)
GRAVEDAD_AGUA = 0.15
VELOCIDAD_NADO_VERTICAL = 0.6
FRICCION_AGUA = 0.90
COLOR_AGUA = (0, 140, 240, 130)


def actualizar_estado_agua(p, zona_agua=ZONA_AGUA):
    p["en_agua"] = zona_agua.colliderect(p["hitbox"])
    return p["en_agua"]


def aplicar_fisica_agua(p, tecla_arriba=False, tecla_abajo=False):
    p["vel_y"] += GRAVEDAD_AGUA

    if tecla_arriba:
        p["vel_y"] -= VELOCIDAD_NADO_VERTICAL

    if tecla_abajo:
        p["vel_y"] += VELOCIDAD_NADO_VERTICAL

    p["vel_y"] *= FRICCION_AGUA


def puede_saltar(p):
    return p["en_suelo"] and not p["en_agua"] and not p["muerto"]


def dibujar_agua(pantalla, zona_agua=ZONA_AGUA):
    superficie = pygame.Surface(
        (zona_agua.width, zona_agua.height),
        pygame.SRCALPHA
    )
    superficie.fill(COLOR_AGUA)
    pantalla.blit(superficie, (zona_agua.x, zona_agua.y))
