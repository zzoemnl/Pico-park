"""
Prueba de regresión visual y de rendimiento, sin ventana (SDL "dummy").

Corre cada nivel (o el menú) N frames de forma determinista (reloj, ticks y
azar fijados), guarda una captura del frame 100 y mide los ms por frame sin el
límite de 60 fps. Comparando las capturas de antes y después de un cambio se
puede demostrar que una optimización no cambió ni un píxel.

Uso (desde la raíz del repo, con el .venv activado):
    python herramientas/regresion_visual.py capturar <carpeta>            # todas las escenas
    python herramientas/regresion_visual.py capturar <carpeta> 3-5 menu   # solo algunas
    python herramientas/regresion_visual.py comparar <carpeta_a> <carpeta_b>

Cada escena corre en un proceso aparte para que no se contaminen entre sí.
"""
import os
import subprocess
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ESCENAS = [f"{m}-{n}" for m in (1, 2, 3) for n in (1, 2, 3, 4, 5)] + ["menu"]
FRAME_CAPTURA, FRAMES_TOTAL = 100, 160


def _correr_escena(carpeta, escena):
    """Se ejecuta en un proceso hijo: una escena, una captura, una medición."""
    import random
    import time
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    sys.path.insert(0, os.path.join(RAIZ, "Pico-park-juego"))
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))

    estado = {"f": 0, "t0": None}
    reloj_original = pygame.time.Clock

    class RelojSinLimite:
        def __init__(self):
            self._reloj = reloj_original()

        def tick(self, fps=0):
            return 16

        def get_fps(self):
            return 60.0

    pygame.time.Clock = RelojSinLimite
    pygame.time.get_ticks = lambda: estado["f"] * 16
    random_original = random.Random
    random.Random = lambda seed=None: random_original(777 if seed is None else seed)
    random.seed(12345)

    import ventana
    ventana.crear_ventana = lambda pantalla_completa=True: pygame.display.set_mode((1280, 720))
    import pantalla
    import main
    from menu_niveles import obtener_mecanicas_nivel

    flip_original = pygame.display.flip

    def flip():
        estado["f"] += 1
        if estado["f"] == 20:
            estado["t0"] = time.perf_counter()
        if estado["f"] == FRAME_CAPTURA:
            pygame.image.save(pygame.display.get_surface(), os.path.join(carpeta, f"{escena}.png"))
        flip_original()

    get_original = pygame.event.get

    def get(*args, **kwargs):
        eventos = get_original(*args, **kwargs)
        if estado["f"] >= FRAMES_TOTAL:
            eventos.append(pygame.event.Event(pygame.QUIT))
        return eventos

    pygame.display.flip = flip
    pygame.event.get = get
    pantalla.matar_personaje = lambda p: None   # los personajes quietos no deben morir

    try:
        if escena == "menu":
            main.main()
        else:
            m, n = int(escena[0]), int(escena[2])
            pantalla.iniciar_mundo(obtener_mecanicas_nivel(m, n), numero_nivel=n,
                                   color_p1="Celeste", color_p2="Violeta", mundo=m)
    except SystemExit:
        pass
    dt = time.perf_counter() - estado["t0"]
    print(f"{escena}: {dt * 1000 / (estado['f'] - 20):.2f} ms/frame", flush=True)


def capturar(carpeta, escenas):
    os.makedirs(carpeta, exist_ok=True)
    for escena in escenas:
        res = subprocess.run([sys.executable, __file__, "_escena", carpeta, escena],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        linea = [l for l in res.stdout.splitlines() if "ms/frame" in l]
        print(linea[-1] if linea else f"{escena}: ERROR\n{res.stderr[-800:]}")


def comparar(carpeta_a, carpeta_b):
    import pygame
    pygame.init()
    for nombre in sorted(os.listdir(carpeta_a)):
        if not nombre.endswith(".png"):
            continue
        ruta_b = os.path.join(carpeta_b, nombre)
        if not os.path.exists(ruta_b):
            print(f"{nombre}: falta en {carpeta_b}")
            continue
        a = pygame.image.tobytes(pygame.image.load(os.path.join(carpeta_a, nombre)), "RGB")
        b = pygame.image.tobytes(pygame.image.load(ruta_b), "RGB")
        if a == b:
            print(f"{nombre}: idéntico")
        else:
            dif = sum(1 for i in range(0, len(a), 3) if a[i:i + 3] != b[i:i + 3])
            print(f"{nombre}: {dif} píxeles distintos")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "_escena":
        _correr_escena(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == "capturar":
        capturar(sys.argv[2], sys.argv[3:] or ESCENAS)
    elif len(sys.argv) == 4 and sys.argv[1] == "comparar":
        comparar(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)
