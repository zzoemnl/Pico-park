import os
import copy
import datetime
import pygame

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_PARTIDAS = os.path.join(DIRECTORIO_ACTUAL, "partidas.txt")


def cargar_fuente_pixel(tamano, fallback_tamano=None):
    """
    Carga la emblemática fuente retro 04B_30 (pixel art) desde Sprites/Fuentes
    si está disponible, o utiliza la fuente del sistema de respaldo con el tamaño adecuado.
    """
    if not pygame.font.get_init():
        pygame.font.init()

    ruta_fuente = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes", "04B_30__.TTF")
    if os.path.isfile(ruta_fuente):
        try:
            return pygame.font.Font(ruta_fuente, tamano)
        except Exception:
            pass

    zip_ruta = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes", "04b_30.zip")
    if os.path.isfile(zip_ruta):
        try:
            import zipfile
            dest_dir = os.path.join(DIRECTORIO_ACTUAL, "..", "Sprites", "Fuentes")
            with zipfile.ZipFile(zip_ruta, "r") as z:
                z.extractall(dest_dir)
            if os.path.isfile(ruta_fuente):
                return pygame.font.Font(ruta_fuente, tamano)
        except Exception:
            pass

    return pygame.font.Font(None, fallback_tamano or tamano)


def crear_desbloqueados_inicial():
    """Retorna la estructura inicial con solo el Nivel 1 del Mundo 1 desbloqueado."""
    return {
        1: [True, False, False, False, False],
        2: [False, False, False, False, False],
        3: [False, False, False, False, False],
    }


def encode_desbloqueados(d):
    """Convierte el diccionario de niveles desbloqueados en una cadena compacta."""
    partes = []
    for m in sorted(d.keys()):
        bits = "".join("1" if x else "0" for x in d[m])
        partes.append(f"{m}:{bits}")
    return ",".join(partes)


def decode_desbloqueados(s):
    """Convierte la cadena guardada de nuevo a diccionario de booleanos."""
    res = crear_desbloqueados_inicial()
    if not s:
        return res
    for item in s.strip().split(","):
        if not item or ":" not in item:
            continue
        m_str, bits = item.split(":")
        try:
            m = int(m_str)
            res[m] = [c == "1" for c in bits]
        except (ValueError, IndexError):
            pass
    return res


def obtener_maximo_alcanzado(niveles_desbloqueados):
    """Retorna (mundo_max, nivel_max) indicando el nivel más alto alcanzado/desbloqueado."""
    for m in (3, 2, 1):
        if m in niveles_desbloqueados:
            for idx in range(len(niveles_desbloqueados[m]) - 1, -1, -1):
                if niveles_desbloqueados[m][idx]:
                    return m, idx + 1
    return 1, 1


def cargar_partidas():
    """Lee el archivo partidas.txt y retorna la lista de partidas guardadas."""
    if not os.path.isfile(RUTA_PARTIDAS):
        return []

    partidas = []
    try:
        with open(RUTA_PARTIDAS, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                partes = linea.split("|")
                if len(partes) >= 6:
                    try:
                        p = {
                            "id": int(partes[0]),
                            "nombre": partes[1],
                            "mundo_max": int(partes[2]),
                            "nivel_max": int(partes[3]),
                            "fecha": partes[4],
                            "niveles_desbloqueados": decode_desbloqueados(partes[5]),
                        }
                        partidas.append(p)
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        print(f"Error al leer partidas.txt: {e}")
        return []

    return partidas


def guardar_partida(niveles_desbloqueados, id_partida=None, nombre_partida=None):
    """
    Guarda o actualiza una partida en partidas.txt.
    Si id_partida existe, la actualiza; si no, agrega una nueva.
    """
    partidas = cargar_partidas()
    mundo_max, nivel_max = obtener_maximo_alcanzado(niveles_desbloqueados)
    fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    partida_encontrada = None
    if id_partida is not None:
        for p in partidas:
            if p["id"] == id_partida:
                partida_encontrada = p
                break

    if partida_encontrada:
        partida_encontrada["mundo_max"] = mundo_max
        partida_encontrada["nivel_max"] = nivel_max
        partida_encontrada["fecha"] = fecha_actual
        partida_encontrada["niveles_desbloqueados"] = copy.deepcopy(niveles_desbloqueados)
        if nombre_partida:
            partida_encontrada["nombre"] = nombre_partida
        partida_guardada = partida_encontrada
    else:
        nuevo_id = 1
        if partidas:
            nuevo_id = max(p["id"] for p in partidas) + 1
        nuevo_nombre = nombre_partida if nombre_partida else f"Partida {nuevo_id}"
        nueva = {
            "id": nuevo_id,
            "nombre": nuevo_nombre,
            "mundo_max": mundo_max,
            "nivel_max": nivel_max,
            "fecha": fecha_actual,
            "niveles_desbloqueados": copy.deepcopy(niveles_desbloqueados),
        }
        partidas.append(nueva)
        partida_guardada = nueva

    try:
        with open(RUTA_PARTIDAS, "w", encoding="utf-8") as f:
            f.write("# Archivo de guardado de partidas - Pico Park\n")
            f.write("# Formato: ID|Nombre|MundoMax|NivelMax|Fecha|NivelesDesbloqueados\n")
            for p in partidas:
                f.write(
                    f"{p['id']}|{p['nombre']}|{p['mundo_max']}|{p['nivel_max']}|"
                    f"{p['fecha']}|{encode_desbloqueados(p['niveles_desbloqueados'])}\n"
                )
    except Exception as e:
        print(f"Error al escribir en partidas.txt: {e}")

    return partida_guardada


def eliminar_partida(id_partida):
    """
    Elimina del archivo partidas.txt la partida que tenga el ID especificado.
    Conserva intactas las demás partidas.
    Retorna True si fue eliminada con éxito, o False si no se encontró.
    """
    partidas = cargar_partidas()
    partidas_restantes = [p for p in partidas if p["id"] != id_partida]
    if len(partidas_restantes) == len(partidas):
        return False

    try:
        with open(RUTA_PARTIDAS, "w", encoding="utf-8") as f:
            f.write("# Archivo de guardado de partidas - Pico Park\n")
            f.write("# Formato: ID|Nombre|MundoMax|NivelMax|Fecha|NivelesDesbloqueados\n")
            for p in partidas_restantes:
                f.write(
                    f"{p['id']}|{p['nombre']}|{p['mundo_max']}|{p['nivel_max']}|"
                    f"{p['fecha']}|{encode_desbloqueados(p['niveles_desbloqueados'])}\n"
                )
        return True
    except Exception as e:
        print(f"Error al eliminar partida en partidas.txt: {e}")
        return False


def mostrar_dialogo_guardar_salir(pantalla, reloj, niveles_desbloqueados, id_partida=None, nombre_partida=None):
    """
    Muestra un diálogo modal interactivo preguntando si se desea guardar el progreso antes de salir.
    Retorna:
    - 'guardar_salir': se guardó el progreso y debe cerrarse el juego.
    - 'salir_sin_guardar': no se guardó el progreso y debe cerrarse el juego.
    - 'cancelar': no se sale del juego (se cancela la acción).
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    mundo_max, nivel_max = obtener_maximo_alcanzado(niveles_desbloqueados)

    fuente_titulo = cargar_fuente_pixel(22, fallback_tamano=36)
    fuente_texto = pygame.font.Font(None, 26)
    fuente_btn = cargar_fuente_pixel(13, fallback_tamano=28)

    ancho_card, alto_card = 520, 340
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 340, 50
    x_btn = rect_card.centerx - (w_btn // 2)
    y_base_btns = rect_card.top + 145
    espacio_btns = 14

    btn_guardar = pygame.Rect(x_btn, y_base_btns, w_btn, h_btn)
    btn_no_guardar = pygame.Rect(x_btn, y_base_btns + (h_btn + espacio_btns), w_btn, h_btn)
    btn_cancelar = pygame.Rect(x_btn, y_base_btns + (h_btn + espacio_btns) * 2, w_btn, h_btn)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))

    captura_previa = pantalla.copy()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir_sin_guardar"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_guardar.collidepoint(evento.pos):
                    guardar_partida(niveles_desbloqueados, id_partida=id_partida, nombre_partida=nombre_partida)
                    return "guardar_salir"
                elif btn_no_guardar.collidepoint(evento.pos):
                    return "salir_sin_guardar"
                elif btn_cancelar.collidepoint(evento.pos):
                    return "cancelar"

        # Dibujar fondo capturado + overlay cálido
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        # Tarjeta modal pastel crema
        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=18)

        # Título con tipografía pixel art
        t_tit = fuente_titulo.render("GUARDAR PROGRESO", True, (60, 45, 35))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 40)))

        # Info de nivel actual
        t_info = fuente_texto.render(f"Progreso actual: Mundo {mundo_max} - Nivel {nivel_max}", True, (55, 45, 35))
        pantalla.blit(t_info, t_info.get_rect(center=(rect_card.centerx, rect_card.top + 80)))

        t_sub = fuente_texto.render("Podrás continuar desde este nivel más adelante.", True, (120, 105, 90))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 112)))

        # Botones interactivos con fuente pixel
        botones_datos = [
            (btn_guardar, "GUARDAR Y SALIR", (68, 172, 98), (82, 194, 114), (255, 255, 255), (45, 130, 70)),
            (btn_no_guardar, "SALIR SIN GUARDAR", (215, 80, 75), (235, 95, 90), (255, 255, 255), (170, 50, 45)),
            (btn_cancelar, "CANCELAR", (242, 234, 222), (255, 255, 255), (60, 45, 35), (195, 168, 138)),
        ]

        for btn, texto, col_norm, col_hov, col_txt, col_borde in botones_datos:
            hover = btn.collidepoint(pos_mouse)
            color_fondo = col_hov if hover else col_norm
            pygame.draw.rect(pantalla, color_fondo, btn, border_radius=12)
            pygame.draw.rect(pantalla, (255, 255, 255) if hover else col_borde, btn, width=2 if hover else 1, border_radius=12)
            t_btn = fuente_btn.render(texto, True, col_txt)
            pantalla.blit(t_btn, t_btn.get_rect(center=btn.center))

        pygame.display.flip()


def mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
    """
    Muestra un diálogo modal interactivo con estética pastel crema solicitando confirmación para borrar una partida.
    Retorna True si se confirma («BORRAR PARTIDA»), o False si se cancela («CANCELAR» o ESC).
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = cargar_fuente_pixel(22, fallback_tamano=36)
    fuente_nombre = pygame.font.Font(None, 28)
    fuente_texto = pygame.font.Font(None, 25)
    fuente_btn = cargar_fuente_pixel(13, fallback_tamano=26)

    ancho_card, alto_card = 560, 310
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 205, 48
    gap_btn = 22
    total_w_btns = (w_btn * 2) + gap_btn
    x_cancelar = rect_card.centerx - (total_w_btns // 2)
    x_borrar = x_cancelar + w_btn + gap_btn
    y_btns = rect_card.bottom - 72

    btn_cancelar = pygame.Rect(x_cancelar, y_btns, w_btn, h_btn)
    btn_borrar = pygame.Rect(x_borrar, y_btns, w_btn, h_btn)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((45, 35, 25, 140))

    captura_previa = pantalla.copy()

    nombre = partida.get("nombre", f"Partida {partida.get('id', 1)}")
    mundo_max = partida.get("mundo_max", 1)
    nivel_max = partida.get("nivel_max", 1)

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cancelar.collidepoint(evento.pos):
                    return False
                elif btn_borrar.collidepoint(evento.pos):
                    return True

        # Dibujar fondo previo + oscurecimiento cálido
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        # Tarjeta modal estilo panel crema pastel
        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (225, 110, 80), rect_card, width=3, border_radius=18)

        # Título en pixel art tono terracota / rojo cálido
        t_tit = fuente_titulo.render("BORRAR PARTIDA", True, (205, 70, 60))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 40)))

        # Info de la partida seleccionada en marrón café
        t_nom = fuente_nombre.render(f"«{nombre}»  —  Nivel Máximo: {mundo_max}-{nivel_max}", True, (60, 45, 35))
        pantalla.blit(t_nom, t_nom.get_rect(center=(rect_card.centerx, rect_card.top + 85)))

        # Pregunta y advertencia
        t_preg = fuente_texto.render("¿Seguro que querés borrar esta partida?", True, (80, 65, 55))
        pantalla.blit(t_preg, t_preg.get_rect(center=(rect_card.centerx, rect_card.top + 128)))

        t_aviso = fuente_texto.render("Esta acción no se puede deshacer.", True, (195, 75, 65))
        pantalla.blit(t_aviso, t_aviso.get_rect(center=(rect_card.centerx, rect_card.top + 160)))

        # Botón Cancelar (crema / arena pastel)
        hov_can = btn_cancelar.collidepoint(pos_mouse)
        col_can = (255, 255, 255) if hov_can else (242, 234, 222)
        borde_can = (165, 135, 105) if hov_can else (195, 168, 138)
        pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=12)
        pygame.draw.rect(pantalla, borde_can, btn_cancelar, width=2, border_radius=12)
        t_btn_can = fuente_btn.render("CANCELAR", True, (60, 45, 35))
        pantalla.blit(t_btn_can, t_btn_can.get_rect(center=btn_cancelar.center))

        # Botón Borrar Partida (terracota / coral pastel)
        hov_bor = btn_borrar.collidepoint(pos_mouse)
        col_bor = (235, 95, 90) if hov_bor else (215, 80, 75)
        borde_bor = (255, 255, 255) if hov_bor else (170, 50, 45)
        pygame.draw.rect(pantalla, col_bor, btn_borrar, border_radius=12)
        pygame.draw.rect(pantalla, borde_bor, btn_borrar, width=2, border_radius=12)
        t_btn_bor = fuente_btn.render("BORRAR PARTIDA", True, (255, 255, 255))
        pantalla.blit(t_btn_bor, t_btn_bor.get_rect(center=btn_borrar.center))

        pygame.display.flip()
