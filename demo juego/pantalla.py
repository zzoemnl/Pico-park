import sys
import pygame

from sprites import (
    ANCHO,
    ALTO,
    FPS,
    COLOR_JUGADOR1,
    COLOR_JUGADOR2,
    dibujar_personaje
)
from movimientos import (
    crear_personaje,
    reiniciar_juego,
    resolver_colisiones
)

# ============================================================
# RENDERIZADO DE INTERFAZ
# ============================================================

def dibujar_boton_reiniciar(pantalla, fuente, btn_rect):
    pygame.draw.rect(pantalla, (180, 40, 40), btn_rect, border_radius=6)
    pygame.draw.rect(pantalla, (255, 255, 255), btn_rect, 2, border_radius=6)
    texto = fuente.render("Reiniciar (R)", True, (255, 255, 255))
    pantalla.blit(texto, texto.get_rect(center=btn_rect.center))


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pantalla_rect = pantalla.get_rect()
    pygame.display.set_caption("Juego con 2 Personajes - Hitbox Centrada")

    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial", 14, bold=True)

    btn_reiniciar = pygame.Rect(ANCHO - 130, 15, 115, 32)

    jugador1 = crear_personaje(100, 0, COLOR_JUGADOR1)
    jugador2 = crear_personaje(300, 0, COLOR_JUGADOR2)
    suelo = pygame.Rect(0, 520, ANCHO, 80)

    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_reiniciar.collidepoint(evento.pos):
                    reiniciar_juego(jugador1, jugador2)

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                reiniciar_juego(jugador1, jugador2)

        teclas = pygame.key.get_pressed()

        # Controles Jugador 1
        jugador1["vel_x"] = 0

        if teclas[pygame.K_LEFT]:
            jugador1["vel_x"] = -jugador1["velocidad_mov"]

        if teclas[pygame.K_RIGHT]:
            jugador1["vel_x"] = jugador1["velocidad_mov"]

        if teclas[pygame.K_UP] and jugador1["en_suelo"]:
            jugador1["vel_y"] = jugador1["fuerza_salto"]
            jugador1["en_suelo"] = False

        # Controles Jugador 2
        jugador2["vel_x"] = 0

        if teclas[pygame.K_a]:
            jugador2["vel_x"] = -jugador2["velocidad_mov"]

        if teclas[pygame.K_d]:
            jugador2["vel_x"] = jugador2["velocidad_mov"]

        if teclas[pygame.K_w] and jugador2["en_suelo"]:
            jugador2["vel_y"] = jugador2["fuerza_salto"]
            jugador2["en_suelo"] = False

        # Actualizar Física
        resolver_colisiones(jugador1, jugador2, suelo, pantalla_rect)
        resolver_colisiones(jugador2, jugador1, suelo, pantalla_rect)

        jugador1["hitbox"].clamp_ip(pantalla_rect)
        jugador2["hitbox"].clamp_ip(pantalla_rect)

        # Dibujado
        pantalla.fill((30, 30, 30))
        pygame.draw.rect(pantalla, (100, 100, 100), suelo)

        dibujar_personaje(pantalla, jugador1)
        dibujar_personaje(pantalla, jugador2)

        dibujar_boton_reiniciar(pantalla, fuente, btn_reiniciar)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()