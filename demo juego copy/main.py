import pygame

from sprites import ANCHO, ALTO, FPS
from pantalla import iniciar_mundo


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO),pygame.RESIZABLE)
    # Maximizar la ventana automáticamente
    try:
        from pygame._sdl2.video import Window
        ventana = Window.from_display_module()
        ventana.maximize()
    except Exception:
        pass

    pygame.display.set_caption("Pico Park - Mundos")
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 38)

    # ========================================================
    # BOTONES DE EJEMPLO
    # ========================================================
    #
    # Acá solamente elegís qué mecánicas tiene cada mundo.
    #
    # Ejemplo:
    # ["caja", "soga", "agua"]
    #
    # La estructura común (movimiento, salto, gravedad,
    # colisiones, personajes, etc.) ya viene incluida.
    # ========================================================

    ANCHO_MENU = pantalla.get_width()
    ALTO_MENU = pantalla.get_height()

    ANCHO_BOTON = 300
    ALTO_BOTON = 70
    ESPACIO = 30

    x_boton = (ANCHO_MENU - ANCHO_BOTON) // 2
    alto_total = (ALTO_BOTON * 4) + (ESPACIO * 3)
    y_inicial = (ALTO_MENU - alto_total) // 2

    botones = [
        pygame.Rect(x_boton, y_inicial,ANCHO_BOTON,ALTO_BOTON),
        pygame.Rect(x_boton,y_inicial + (ALTO_BOTON + ESPACIO),ANCHO_BOTON, ALTO_BOTON),
        pygame.Rect(x_boton,y_inicial + (ALTO_BOTON + ESPACIO) * 2,ANCHO_BOTON,ALTO_BOTON),
        pygame.Rect(x_boton, y_inicial + (ALTO_BOTON + ESPACIO) * 3,ANCHO_BOTON,ALTO_BOTON),]

    textos = [
        "Mundo 1 - Caja",
        "Mundo 2 - Soga",
        "Mundo 3 - Agua",
        "Mundo 4 - Pinchos",
    ]

    # Cada nivel tiene automáticamente: pantalla larga,
    # cámara/split-screen cuando los jugadores se separan,
    # llave y puerta. Acá solamente elegimos la mecánica especial.
    mecanicas_mundos = [
        ["caja"],
        ["soga"],
        ["agua"],
        ["pinchos"],
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
                        resultado = iniciar_mundo(mecanicas_mundos[i])

                        if resultado == "salir":
                            break

        pantalla.fill((30, 30, 30))

        titulo = fuente.render("ELEGÍ UN MUNDO", True, (255, 255, 255))
        pantalla.blit(titulo,titulo.get_rect(center=(ANCHO_MENU // 2, 45)))

        for i, boton in enumerate(botones):
            pygame.draw.rect(pantalla,(70, 70, 70),boton,border_radius=8)
            pygame.draw.rect(pantalla,(255, 255, 255),boton,2,border_radius=8)

            texto = fuente.render(textos[i], True, (255, 255, 255))
            pantalla.blit(texto,texto.get_rect(center=boton.center))

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
