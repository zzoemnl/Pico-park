"""
Prueba de regresión visual y de rendimiento, sin ventana (SDL "dummy").

Corre cada escena N frames de forma determinista (reloj, ticks y azar fijados),
guarda capturas y mide los ms por frame sin el límite de 60 fps. Comparando las
capturas de antes y después de un cambio se demuestra que no cambió ni un píxel.

Escenas:
    1-1 … 3-5        el nivel, sin tocar nada (captura del frame 100)
    3-5/split        los jugadores se separan: pantalla dividida
    3-5/victoria     puerta abierta y los dos entran: transición de nivel completado
    3-5/reinicio     tecla R a mitad del nivel (regenera laberintos aleatorios)
    3-5/muerte       muere el jugador 1: pantalla de muerte
    menu             menú principal
    menu/modo        clic en JUGAR: pantalla de modo de juego
    menu/partidas    JUGAR -> CONTINUAR: lista de partidas
    menu/nueva       JUGAR -> NUEVA PARTIDA
    menu/personajes  clic en PERSONAJES
    menu/config      clic en OPCIONES
Los escenarios capturan los frames 60, 100 y 130.

Uso (desde la raíz del repo, con el .venv activado):
    python herramientas/regresion_visual.py capturar <carpeta>              # todas las escenas
    python herramientas/regresion_visual.py capturar <carpeta> 3-5 menu/config
    python herramientas/regresion_visual.py comparar <carpeta_a> <carpeta_b>

Cada escena corre en un proceso aparte para que no se contaminen entre sí.
"""
import os
import subprocess
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NIVELES = [f"{m}-{n}" for m in (1, 2, 3) for n in (1, 2, 3, 4, 5)]
ESCENARIOS_NIVEL = ["split", "victoria", "reinicio", "muerte"]
ESCENARIOS_MENU = ["modo", "partidas", "nueva", "personajes", "config"]
ESCENAS = (NIVELES
           + [f"{n}/{e}" for n in ("1-3", "2-2", "3-5") for e in ESCENARIOS_NIVEL]
           + ["menu"] + [f"menu/{e}" for e in ESCENARIOS_MENU])
FRAMES_TOTAL = 160

# Centros de los botones del menú (ventana lógica de 1280x720; ver main.py)
BOTONES_MENU = {
    "jugar": (640, 254), "personajes": (640, 348), "opciones": (640, 442),
    "continuar": (640, 325), "nueva_partida": (640, 445),
}


def _clic(pos):
    return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1)]


def _correr_escena(carpeta, escena):
    """Se ejecuta en un proceso hijo: una escena, sus capturas, una medición."""
    import random
    import time
    global pygame
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    sys.path.insert(0, os.path.join(RAIZ, "Pico-park-juego"))
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))

    base, _, modo = escena.partition("/")
    nombre_archivo = escena.replace("/", "_")
    capturas = (60, 100, 130) if modo else (100,)
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
        if estado["f"] in capturas:
            sufijo = f"_{estado['f']}" if modo else ""
            pygame.image.save(pygame.display.get_surface(), os.path.join(carpeta, f"{nombre_archivo}{sufijo}.png"))
        flip_original()

    # Eventos sintéticos por frame: clics del menú, tecla R, cierre
    eventos_programados = {}
    if base == "menu":
        secuencia = {"modo": ["jugar"], "partidas": ["jugar", "continuar"], "nueva": ["jugar", "nueva_partida"],
                     "personajes": ["personajes"], "config": ["opciones"]}.get(modo, [])
        for i, boton in enumerate(secuencia):
            eventos_programados[40 + i * 30] = _clic(BOTONES_MENU[boton])
    elif modo == "reinicio":
        eventos_programados[45] = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r, mod=0, unicode="r", scancode=0)]

    get_original = pygame.event.get

    def get(*args, **kwargs):
        eventos = get_original(*args, **kwargs)
        eventos += eventos_programados.pop(estado["f"], [])
        if estado["f"] >= FRAMES_TOTAL:
            eventos.append(pygame.event.Event(pygame.QUIT))
        return eventos

    pygame.display.flip = flip
    pygame.event.get = get

    # Los personajes quietos no deben morir solos (salvo en el escenario de muerte)
    matar_original = pantalla.matar_personaje
    if modo != "muerte":
        pantalla.matar_personaje = lambda p: None

    # Ganchos sobre el nivel: se cuelgan de actualizar_llave, que recibe jugadores y puerta
    llave_original = pantalla.actualizar_llave

    def gancho_llave(llave, personajes, puerta):
        f = estado["f"]
        if modo == "split" and f == 40 and len(personajes) == 2:
            personajes[1]["hitbox"].x = min(1900, puerta["rect"].x - 200)
        elif modo == "victoria" and f == 50:
            puerta["abierta"] = True
            entrada = puerta.get("rect_entrada", puerta["rect"])
            for p in personajes:
                p["hitbox"].center = entrada.center
        elif modo == "muerte" and f == 40 and personajes:
            matar_original(personajes[0])
        return llave_original(llave, personajes, puerta)

    pantalla.actualizar_llave = gancho_llave

    try:
        if base == "menu":
            main.main()
        else:
            m, n = int(base[0]), int(base[2])
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
        print(linea[-1] if linea else f"{escena}: ERROR\n{res.stderr[-800:]}", flush=True)


def comparar(carpeta_a, carpeta_b):
    import pygame
    pygame.init()
    distintos = 0
    for nombre in sorted(os.listdir(carpeta_a)):
        if not nombre.endswith(".png"):
            continue
        ruta_b = os.path.join(carpeta_b, nombre)
        if not os.path.exists(ruta_b):
            print(f"{nombre}: falta en {carpeta_b}")
            distintos += 1
            continue
        a = pygame.image.tobytes(pygame.image.load(os.path.join(carpeta_a, nombre)), "RGB")
        b = pygame.image.tobytes(pygame.image.load(ruta_b), "RGB")
        if a == b:
            print(f"{nombre}: idéntico")
        else:
            dif = sum(1 for i in range(0, len(a), 3) if a[i:i + 3] != b[i:i + 3])
            print(f"{nombre}: {dif} píxeles distintos")
            distintos += 1
    print(f"\n{'TODO IDÉNTICO' if distintos == 0 else f'{distintos} capturas con diferencias'}")
    return distintos


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "_escena":
        _correr_escena(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == "capturar":
        capturar(sys.argv[2], sys.argv[3:] or ESCENAS)
    elif len(sys.argv) == 4 and sys.argv[1] == "comparar":
        sys.exit(1 if comparar(sys.argv[2], sys.argv[3]) else 0)
    else:
        print(__doc__)
        sys.exit(1)
