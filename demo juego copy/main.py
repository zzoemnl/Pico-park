import pygame

from sprites import ANCHO, ALTO, FPS
from pantalla import iniciar_mundo


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pico Park - Mundos")

    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 34)

    botones = [
        pygame.Rect(250, 70, 300, 70),
        pygame.Rect(250, 160, 300, 70),
        pygame.Rect(250, 250, 300, 70),
        pygame.Rect(250, 340, 300, 70),
        pygame.Rect(250, 430, 300, 70),
    ]

    textos = [
        "Mundo 1 - Caja",
        "Mundo 2 - Soga",
        "Mundo 3 - Agua",
        "Mundo 4 - Pinchos",
        "Mundo 5 - Llave y Puerta",
    ]

    mecanicas_mundos = [
        ["caja"],
        ["soga"],
        ["agua"],
        ["pinchos"],
        ["llave"],
    ]

    ejecutando = True

    while ejecutando:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for i, boton in enumerate(botones):
                    if boton.collidepoint(evento.pos):
                        iniciar_mundo(mecanicas_mundos[i])
                        break

        pantalla.fill((30, 30, 30))

        titulo = fuente.render("ELEGÍ UN MUNDO", True, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 35)))

        for i, boton in enumerate(botones):
            pygame.draw.rect(pantalla, (70, 70, 70), boton, border_radius=8)
            pygame.draw.rect(
                pantalla,
                (255, 255, 255),
                boton,
                2,
                border_radius=8
            )
            texto = fuente.render(textos[i], True, (255, 255, 255))
            pantalla.blit(texto, texto.get_rect(center=boton.center))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
