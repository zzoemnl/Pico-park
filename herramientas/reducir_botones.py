"""
Reduce los PNG de Sprites/Botones a un ancho máximo razonable.

Los botones se dibujan como máximo a 272x80 px, pero los archivos originales
están a 5440x1600 o 6800x1600, lo que ocupa ~1,7 GB de RAM al cargarlos.
Este script los reescala a ANCHO_MAX px de ancho (4x el tamaño de dibujo,
suficiente para que smoothscale no pierda calidad) manteniendo la proporción.

Uso (desde la raíz del repo, con el .venv activado):
    python herramientas/reducir_botones.py            # aplica
    python herramientas/reducir_botones.py --dry-run  # solo muestra qué haría
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame  # noqa: E402

ANCHO_MAX = 1088
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CARPETA = os.path.join(RAIZ, "Sprites", "Botones")


def main():
    dry_run = "--dry-run" in sys.argv
    pygame.init()
    pygame.display.set_mode((1, 1))

    bytes_antes = bytes_despues = 0
    reducidos = 0
    for carpeta, _, archivos in os.walk(CARPETA):
        for nombre in archivos:
            if not nombre.lower().endswith(".png"):
                continue
            ruta = os.path.join(carpeta, nombre)
            tam_antes = os.path.getsize(ruta)
            bytes_antes += tam_antes
            img = pygame.image.load(ruta).convert_alpha()
            w, h = img.get_size()
            if w <= ANCHO_MAX:
                bytes_despues += tam_antes
                continue
            nw = ANCHO_MAX
            nh = max(1, round(h * ANCHO_MAX / w))
            rel = os.path.relpath(ruta, RAIZ)
            print(f"{rel}: {w}x{h} -> {nw}x{nh}")
            reducidos += 1
            if dry_run:
                bytes_despues += tam_antes
                continue
            nueva = pygame.transform.smoothscale(img, (nw, nh))
            pygame.image.save(nueva, ruta)
            bytes_despues += os.path.getsize(ruta)

    print(f"\n{reducidos} archivos reducidos. Disco: {bytes_antes / 2**20:.1f} MB -> {bytes_despues / 2**20:.1f} MB"
          + (" (dry-run, sin cambios)" if dry_run else ""))


if __name__ == "__main__":
    main()
