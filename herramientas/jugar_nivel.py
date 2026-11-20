"""
Abre directamente un nivel, sin pasar por el menú ni por las partidas guardadas.
Pensado para probar niveles (por ejemplo los jefes) sin tener que desbloquearlos.

Uso (desde la raíz del repo, con el .venv activado):
    python herramientas/jugar_nivel.py 1 6          # jefe del mundo 1
    python herramientas/jugar_nivel.py 3 6 Rojo Verde   # colores opcionales de P1 y P2

Controles: los del juego (WASD / flechas, R reinicia, F11 pantalla completa / ventana).
Al ganar o volver al menú el script termina.
"""
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "Pico-park-juego"))

import pygame  # noqa: E402


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mundo, nivel = int(sys.argv[1]), int(sys.argv[2])
    color_p1 = sys.argv[3] if len(sys.argv) > 3 else "Celeste"
    color_p2 = sys.argv[4] if len(sys.argv) > 4 else "Violeta"

    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.init()
    from ventana import crear_ventana
    from sprites import precargar_botones_comunes
    from menu_niveles import obtener_mecanicas_nivel
    from pantalla import iniciar_mundo

    crear_ventana(pantalla_completa=False)
    pygame.display.set_caption(f"Pico Park - prueba {mundo}-{nivel}")
    precargar_botones_comunes()

    resultado = iniciar_mundo(
        obtener_mecanicas_nivel(mundo, nivel),
        numero_nivel=nivel,
        color_p1=color_p1,
        color_p2=color_p2,
        mundo=mundo,
    )
    print(f"Nivel {mundo}-{nivel} terminado con resultado: {resultado}")
    pygame.quit()


if __name__ == "__main__":
    main()
