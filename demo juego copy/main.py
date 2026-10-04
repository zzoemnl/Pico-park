import pygame

from sprites import ANCHO, ALTO, FPS
from pantalla import iniciar_mundo, cargar_boton, animar_pulsacion_boton


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
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

    ANCHO_MENU = pantalla.get_width()
    ALTO_MENU = pantalla.get_height()

    # Botón X de cerrar en el menú (arriba a la derecha)
    TAM_BOTON_HUD = 80
    MARGEN_DER = 25
    MARGEN_SUP = 20

    rect_btn_x = pygame.Rect(
        ANCHO_MENU - MARGEN_DER - TAM_BOTON_HUD,
        MARGEN_SUP,
        TAM_BOTON_HUD,
        TAM_BOTON_HUD
    )

    def _cargar_hud(nombre):
        img = cargar_boton(nombre)
        if img is not None:
            return pygame.transform.scale(img, (TAM_BOTON_HUD, TAM_BOTON_HUD))
        return None

    spr_x_normal = _cargar_hud("boton-x.png")
    spr_x_semi = _cargar_hud("boton-x-semiapretado.png")
    spr_x_apretado = _cargar_hud("boton-x-apretado.png")

    # ========================================================
    # BOTONES DE EJEMPLO
    # ========================================================
    ANCHO_BOTON = 300
    ALTO_BOTON = 70
    ESPACIO = 30

    x_boton = (ANCHO_MENU - ANCHO_BOTON) // 2
    alto_total = (ALTO_BOTON * 4) + (ESPACIO * 3)
    y_inicial = (ALTO_MENU - alto_total) // 2

    botones = [
        pygame.Rect(x_boton, y_inicial, ANCHO_BOTON, ALTO_BOTON),
        pygame.Rect(x_boton, y_inicial + (ALTO_BOTON + ESPACIO), ANCHO_BOTON, ALTO_BOTON),
        pygame.Rect(x_boton, y_inicial + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON),
        pygame.Rect(x_boton, y_inicial + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON),
    ]

    textos = [
        "Mundo 1 - Caja",
        "Mundo 2 - Soga",
        "Mundo 3 - Agua",
        "Mundo 4 - Pinchos",
    ]

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
                if rect_btn_x.collidepoint(evento.pos):
                    if spr_x_semi and spr_x_apretado:
                        animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apretado)
                    ejecutando = False
                    break

                for i, boton in enumerate(botones):
                    if boton.collidepoint(evento.pos):
                        resultado = iniciar_mundo(mecanicas_mundos[i])

                        if resultado == "salir":
                            break

        pantalla.fill((30, 30, 30))

        titulo = fuente.render("ELEGÍ UN MUNDO", True, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 45)))

        for i, boton in enumerate(botones):
            pygame.draw.rect(pantalla, (70, 70, 70), boton, border_radius=8)
            pygame.draw.rect(pantalla, (255, 255, 255), boton, 2, border_radius=8)

            texto = fuente.render(textos[i], True, (255, 255, 255))
            pantalla.blit(texto, texto.get_rect(center=boton.center))

        # Dibujar botón X en el menú
        if spr_x_normal:
            pantalla.blit(spr_x_normal, rect_btn_x)

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
