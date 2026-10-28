import os
import sys
import copy
import datetime
import hashlib
import secrets
import pygame

from sprites import cargar_boton, cargar_boton_escalado, animar_pulsacion_boton, aclarar_boton
from configuracion import t

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_PARTIDAS = os.path.join(DIRECTORIO_ACTUAL, "partidas.txt")


def _cargar_sprite_boton(nombre, w, h):
    """Carga y escala suavemente un botón oficial del proyecto con proporciones exactas usando caché."""
    return cargar_boton_escalado(nombre, w, h)


from fuentes import (
    obtener_fuente,
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_botones,
    obtener_fuente_pequena,
    obtener_fuente_contador,
    obtener_fuente_dialogos,
    cargar_fuente_pixel,
    TAMANO_TITULO,
    TAMANO_TITULO_MODAL,
    TAMANO_SUBTITULO,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO,
    TAMANO_TEXTO_GRANDE,
    TAMANO_INPUT,
    TAMANO_BOTON,
    TAMANO_BOTONES,
    TAMANO_BOTON_MODAL,
    TAMANO_PEQUENA,
    TAMANO_ITEM_TITULO,
    TAMANO_CONTADOR,
    TAMANO_DIALOGOS,
    dividir_texto_en_lineas,
    ajustar_tamano_fuente,
    renderizar_texto_ajustado,
    renderizar_texto_multilinea,
    dibujar_texto_en_rect,
)



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
    if not niveles_desbloqueados:
        return 1, 1
    for m in (3, 2, 1):
        if m in niveles_desbloqueados:
            for idx in range(len(niveles_desbloqueados[m]) - 1, -1, -1):
                if niveles_desbloqueados[m][idx]:
                    return m, idx + 1
    return 1, 1


def calcular_niveles_completados(niveles_desbloqueados):
    """
    Calcula la cantidad real de niveles completados en base a los datos registrados.
    Cada nivel desbloqueado adicional al inicial (1-1) representa un nivel completado con éxito.
    """
    if not niveles_desbloqueados:
        return 0
    total_desbloq = sum(sum(1 for x in bits if x) for bits in niveles_desbloqueados.values())
    return max(0, min(15, total_desbloq - 1))


def obtener_ultimo_nivel_completado(niveles_desbloqueados):
    """
    Retorna (mundo, nivel) del último nivel completado, o None si no se ha completado ninguno.
    """
    if not niveles_desbloqueados:
        return None
    completados = calcular_niveles_completados(niveles_desbloqueados)
    if completados == 0:
        return None
    m = (completados - 1) // 5 + 1
    n = (completados - 1) % 5 + 1
    return m, n


def hay_progreso_sin_guardar(niveles_desbloqueados, snapshot_guardado=None, id_partida=None):
    """
    Determina si existen cambios en los niveles desbloqueados de la sesión
    que difieren de lo que realmente se encuentra guardado en el archivo de partidas
    o en el snapshot de guardado.
    """
    if niveles_desbloqueados is None:
        return False
    if snapshot_guardado is not None:
        return niveles_desbloqueados != snapshot_guardado
    if id_partida is not None:
        partidas = cargar_partidas()
        for p in partidas:
            if p.get("id") == id_partida:
                return niveles_desbloqueados != p.get("niveles_desbloqueados")
    inicial = crear_desbloqueados_inicial()
    return niveles_desbloqueados != inicial



def hash_password(password, salt=None):
    """
    Genera un hash seguro de la contraseña mediante PBKDF2-HMAC-SHA256 con salt.
    Si password está vacío o es None, retorna ("", "").
    """
    if not password:
        return "", ""
    if not salt:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return dk.hex(), salt


def verify_password(password, expected_hash, salt):
    """
    Verifica si una contraseña ingresada coincide con el hash almacenado usando tiempo constante.
    """
    if not expected_hash:
        return True
    if not password or not salt:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return secrets.compare_digest(dk.hex(), expected_hash)


_CACHE_PARTIDAS = None
_CACHE_MTIME = None


def invalidar_cache_partidas():
    global _CACHE_PARTIDAS, _CACHE_MTIME
    _CACHE_PARTIDAS = None
    _CACHE_MTIME = None


def cargar_partidas():
    """
    Lee el archivo partidas.txt y retorna la lista de partidas guardadas.
    Es compatible tanto con el formato anterior (6 campos) como con el nuevo (8 campos con contraseña hasheada).
    Utiliza caché basado en fecha de modificación para evitar sobrecarga de I/O de disco.
    """
    global _CACHE_PARTIDAS, _CACHE_MTIME

    if not os.path.isfile(RUTA_PARTIDAS):
        _CACHE_PARTIDAS = []
        _CACHE_MTIME = None
        return []

    try:
        mtime = os.path.getmtime(RUTA_PARTIDAS)
        if _CACHE_PARTIDAS is not None and _CACHE_MTIME == mtime:
            return copy.deepcopy(_CACHE_PARTIDAS)
    except OSError:
        mtime = None

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
                        pwd_hash = partes[6] if len(partes) > 6 else ""
                        pwd_salt = partes[7] if len(partes) > 7 else ""
                        c_p1 = "Celeste"
                        c_p2 = "Violeta"
                        a_p1 = "Ninguno"
                        a_p2 = "Ninguno"
                        if len(partes) >= 9 and partes[8].strip():
                            pers_partes = [x.strip() for x in partes[8].strip().split(",")]
                            if len(pers_partes) >= 1 and pers_partes[0]:
                                c_p1 = pers_partes[0]
                            if len(pers_partes) >= 2 and pers_partes[1]:
                                c_p2 = pers_partes[1]
                            if len(pers_partes) >= 3 and pers_partes[2]:
                                a_p1 = pers_partes[2]
                            if len(pers_partes) >= 4 and pers_partes[3]:
                                a_p2 = pers_partes[3]
                        p = {
                            "id": int(partes[0]),
                            "nombre": partes[1],
                            "mundo_max": int(partes[2]),
                            "nivel_max": int(partes[3]),
                            "fecha": partes[4],
                            "niveles_desbloqueados": decode_desbloqueados(partes[5]),
                            "password_hash": pwd_hash,
                            "password_salt": pwd_salt,
                            "tiene_password": bool(pwd_hash and pwd_salt),
                            "color_p1": c_p1,
                            "color_p2": c_p2,
                            "accesorio_p1": a_p1,
                            "accesorio_p2": a_p2,
                        }
                        partidas.append(p)
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        print(f"Error al leer partidas.txt: {e}")
        return []

    _CACHE_PARTIDAS = partidas
    _CACHE_MTIME = mtime
    return copy.deepcopy(partidas)


def guardar_partidas_seguras(partidas):
    """
    Escribe de forma atómica la lista de partidas en partidas.txt.
    Usa un archivo temporal (.tmp) y reemplazo atómico para evitar corrupción en disco.
    Retorna True si tuvo éxito, o False si ocurrió un error.
    """
    ruta_tmp = RUTA_PARTIDAS + ".tmp"
    try:
        with open(ruta_tmp, "w", encoding="utf-8") as f:
            f.write("# Archivo de guardado de partidas - Pico Park\n")
            f.write("# Formato: ID|Nombre|MundoMax|NivelMax|Fecha|NivelesDesbloqueados|PasswordHash|PasswordSalt|Personalizacion\n")
            for p in partidas:
                p_hash = p.get("password_hash", "")
                p_salt = p.get("password_salt", "")
                c_p1 = p.get("color_p1", "Celeste")
                c_p2 = p.get("color_p2", "Violeta")
                a_p1 = p.get("accesorio_p1", "Ninguno")
                a_p2 = p.get("accesorio_p2", "Ninguno")
                pers_str = f"{c_p1},{c_p2},{a_p1},{a_p2}"
                f.write(
                    f"{p['id']}|{p['nombre']}|{p['mundo_max']}|{p['nivel_max']}|"
                    f"{p['fecha']}|{encode_desbloqueados(p['niveles_desbloqueados'])}|{p_hash}|{p_salt}|{pers_str}\n"
                )
            f.flush()
            os.fsync(f.fileno())

        os.replace(ruta_tmp, RUTA_PARTIDAS)
        invalidar_cache_partidas()
        return True
    except Exception as e:
        print(f"Error crítico al guardar partidas.txt: {e}")
        invalidar_cache_partidas()
        if os.path.exists(ruta_tmp):
            try:
                os.remove(ruta_tmp)
            except Exception:
                pass
        return False


def guardar_partida(
    niveles_desbloqueados,
    id_partida=None,
    nombre_partida=None,
    password=None,
    password_hash=None,
    password_salt=None,
    color_p1=None,
    color_p2=None,
    accesorio_p1=None,
    accesorio_p2=None,
):
    """
    Guarda o actualiza una partida en partidas.txt.
    Si id_partida existe, la actualiza; si no, crea una nueva.
    Soporta opcionalmente contraseña y personalización individual de los personajes (colores y accesorios).
    Retorna la partida guardada si tuvo éxito, o None si falló.
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

    # Resolver contraseña
    if password is not None:
        if password.strip():
            p_hash, p_salt = hash_password(password.strip())
        else:
            p_hash, p_salt = "", ""
    elif password_hash is not None:
        p_hash = password_hash
        p_salt = password_salt or ""
    else:
        p_hash = partida_encontrada.get("password_hash", "") if partida_encontrada else ""
        p_salt = partida_encontrada.get("password_salt", "") if partida_encontrada else ""

    if partida_encontrada:
        partida_encontrada["mundo_max"] = mundo_max
        partida_encontrada["nivel_max"] = nivel_max
        partida_encontrada["fecha"] = fecha_actual
        partida_encontrada["niveles_desbloqueados"] = copy.deepcopy(niveles_desbloqueados)
        if nombre_partida:
            partida_encontrada["nombre"] = nombre_partida.replace("|", "-").strip()
        partida_encontrada["password_hash"] = p_hash
        partida_encontrada["password_salt"] = p_salt
        partida_encontrada["tiene_password"] = bool(p_hash and p_salt)

        if color_p1 is not None:
            partida_encontrada["color_p1"] = color_p1
        elif "color_p1" not in partida_encontrada:
            partida_encontrada["color_p1"] = "Celeste"

        if color_p2 is not None:
            partida_encontrada["color_p2"] = color_p2
        elif "color_p2" not in partida_encontrada:
            partida_encontrada["color_p2"] = "Violeta"

        if accesorio_p1 is not None:
            partida_encontrada["accesorio_p1"] = accesorio_p1
        elif "accesorio_p1" not in partida_encontrada:
            partida_encontrada["accesorio_p1"] = "Ninguno"

        if accesorio_p2 is not None:
            partida_encontrada["accesorio_p2"] = accesorio_p2
        elif "accesorio_p2" not in partida_encontrada:
            partida_encontrada["accesorio_p2"] = "Ninguno"

        partida_guardada = partida_encontrada
    else:
        nuevo_id = 1
        if partidas:
            nuevo_id = max(p["id"] for p in partidas) + 1
        nuevo_nombre = nombre_partida.replace("|", "-").strip() if nombre_partida else f"Partida {nuevo_id}"
        nueva = {
            "id": nuevo_id,
            "nombre": nuevo_nombre,
            "mundo_max": mundo_max,
            "nivel_max": nivel_max,
            "fecha": fecha_actual,
            "niveles_desbloqueados": copy.deepcopy(niveles_desbloqueados),
            "password_hash": p_hash,
            "password_salt": p_salt,
            "tiene_password": bool(p_hash and p_salt),
            "color_p1": color_p1 if color_p1 is not None else "Celeste",
            "color_p2": color_p2 if color_p2 is not None else "Violeta",
            "accesorio_p1": accesorio_p1 if accesorio_p1 is not None else "Ninguno",
            "accesorio_p2": accesorio_p2 if accesorio_p2 is not None else "Ninguno",
        }
        partidas.append(nueva)
        partida_guardada = nueva

    ok = guardar_partidas_seguras(partidas)
    return partida_guardada if ok else None


def eliminar_partida(id_partida):
    """
    Elimina del archivo partidas.txt la partida que tenga el ID especificado.
    Conserva intactas las demás partidas.
    Retorna True si fue eliminada con éxito, o False en caso contrario.
    """
    partidas = cargar_partidas()
    partidas_restantes = [p for p in partidas if p["id"] != id_partida]
    if len(partidas_restantes) == len(partidas):
        return False
    return guardar_partidas_seguras(partidas_restantes)


def renombrar_partida(id_partida, nuevo_nombre):
    """Cambia el nombre de un perfil de forma segura."""
    partidas = cargar_partidas()
    for p in partidas:
        if p["id"] == id_partida:
            p["nombre"] = nuevo_nombre.replace("|", "-").strip()
            return guardar_partidas_seguras(partidas)
    return False


def cambiar_password_partida(id_partida, nuevo_password):
    """
    Actualiza la contraseña de un perfil.
    Si nuevo_password está vacío o es None, quita la protección por contraseña.
    """
    partidas = cargar_partidas()
    for p in partidas:
        if p["id"] == id_partida:
            if nuevo_password and nuevo_password.strip():
                p_hash, p_salt = hash_password(nuevo_password.strip())
            else:
                p_hash, p_salt = "", ""
            p["password_hash"] = p_hash
            p["password_salt"] = p_salt
            p["tiene_password"] = bool(p_hash and p_salt)
            return guardar_partidas_seguras(partidas)
    return False


def solicitar_texto_modal(pantalla, reloj, titulo, subtitulo, valor_inicial="", es_password=False, permitir_vacio=False, max_caracteres=18):
    """
    Muestra un diálogo modal interactivo para introducir texto (nombre o contraseña).
    Retorna la cadena introducida si se confirma, o None si se cancela con ESC o el botón Cancelar.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_input = obtener_fuente_texto(TAMANO_INPUT)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=24)

    w_card, h_card = 520, 310
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    rect_input = pygame.Rect(rect_card.left + 50, rect_card.top + 115, w_card - 100, 46)

    w_btn, h_btn = 177, 52
    y_btns = rect_card.top + 218
    btn_cancelar = pygame.Rect(rect_card.centerx - w_btn - 12, y_btns, w_btn, h_btn)
    btn_confirmar = pygame.Rect(rect_card.centerx + 12, y_btns, w_btn, h_btn)

    spr_can_norm = _cargar_sprite_boton("Menu/boton-cancelar.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar.png", w_btn, h_btn)
    spr_can_semi = _cargar_sprite_boton("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-semiapretado.png", w_btn, h_btn)
    spr_can_apret = _cargar_sprite_boton("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-apretado.png", w_btn, h_btn)
    spr_can_hover = aclarar_boton(spr_can_norm) if spr_can_norm else None
    fondo_tarjeta = (253, 246, 233)

    rect_ojo = pygame.Rect(rect_input.right - 42, rect_input.top + 5, 36, 36) if es_password else None
    mostrar_caracteres = not es_password

    texto = valor_inicial
    cursor_visible = True
    contador_cursor = 0
    mensaje_error = None

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    # Limpiar eventos previos al abrir la ventana modal
    pygame.event.clear()

    while True:
        reloj.tick(60)
        contador_cursor = (contador_cursor + 1) % 60
        cursor_visible = contador_cursor < 30
        pos_mouse = pygame.mouse.get_pos()

        hov_can = btn_cancelar.collidepoint(pos_mouse)
        hov_con = btn_confirmar.collidepoint(pos_mouse)
        hov_ojo = rect_ojo.collidepoint(pos_mouse) if rect_ojo else False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.event.clear()
                return None

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    return None
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    val = texto.strip()
                    if not val and not permitir_vacio:
                        mensaje_error = "El campo no puede estar vacío."
                    else:
                        # Animar visualmente el botón CONFIRMAR dentro de la ventana modal
                        pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, border_radius=10)
                        pygame.draw.rect(pantalla, (30, 95, 50), btn_confirmar, width=2, border_radius=10)
                        t_con = fuente_btn.render("CONFIRMAR", True, (230, 230, 230))
                        pantalla.blit(t_con, t_con.get_rect(center=(btn_confirmar.centerx, btn_confirmar.centery + 1)))
                        pygame.display.flip()
                        pygame.time.delay(60)
                        # Limpiar eventos para evitar propagación al menú subyacente
                        pygame.event.clear()
                        return val
                elif evento.key == pygame.K_BACKSPACE:
                    texto = texto[:-1]
                    mensaje_error = None
                else:
                    if len(texto) < max_caracteres and evento.unicode and evento.unicode.isprintable() and evento.unicode != "|":
                        texto += evento.unicode
                        mensaje_error = None

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_ojo and rect_ojo.collidepoint(evento.pos):
                    mostrar_caracteres = not mostrar_caracteres
                elif btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_can_semi and spr_can_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_can_semi, spr_can_apret, fondo_tarjeta, spr_can_norm)
                    if pulsado:
                        pygame.event.clear()
                        return None
                elif btn_confirmar.collidepoint(evento.pos):
                    val = texto.strip()
                    if not val and not permitir_vacio:
                        mensaje_error = "El campo no puede estar vacío."
                    else:
                        pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, border_radius=10)
                        pygame.draw.rect(pantalla, (30, 95, 50), btn_confirmar, width=2, border_radius=10)
                        t_con = fuente_btn.render("CONFIRMAR", True, (230, 230, 230))
                        pantalla.blit(t_con, t_con.get_rect(center=(btn_confirmar.centerx, btn_confirmar.centery + 1)))
                        pygame.display.flip()
                        pygame.time.delay(60)
                        pygame.event.clear()
                        return val

        # Dibujar fondo capturado + overlay
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        # Tarjeta modal pastel crema
        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 30, rect_card.top + 16, rect_card.width - 60, 32)
        dibujar_texto_en_rect(pantalla, titulo, rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(60, 45, 35))

        # Subtítulo multilínea con autoajuste para nombres largos
        rect_sub = pygame.Rect(rect_card.left + 24, rect_card.top + 52, rect_card.width - 48, 54)
        dibujar_texto_en_rect(pantalla, subtitulo, rect_sub, categoria="subtitulo", tamano=15, color=(115, 95, 80), multiline=True, padding=2)

        # Caja de texto
        pygame.draw.rect(pantalla, (255, 255, 255), rect_input, border_radius=8)
        pygame.draw.rect(pantalla, (175, 140, 105), rect_input, width=2, border_radius=8)

        # Renderizado del texto introducido con ajuste dinámico dentro del input
        texto_mostrar = texto if mostrar_caracteres else ("•" * len(texto))
        max_w_inp = rect_input.width - (54 if rect_ojo else 24)
        t_txt, _ = renderizar_texto_ajustado(texto_mostrar, categoria="texto", tamano=TAMANO_INPUT, ancho_max=max_w_inp, color=(40, 30, 25))
        pantalla.blit(t_txt, (rect_input.left + 12, rect_input.centery - (t_txt.get_height() // 2)))

        # Cursor parpadeante
        if cursor_visible:
            cur_x = rect_input.left + 12 + t_txt.get_width() + 2
            pygame.draw.line(pantalla, (50, 40, 35), (cur_x, rect_input.top + 10), (cur_x, rect_input.bottom - 10), 2)

        # Botón de visibilidad de contraseña
        if rect_ojo:
            pygame.draw.rect(pantalla, (245, 238, 226) if hov_ojo else (235, 226, 212), rect_ojo, border_radius=6)
            pygame.draw.rect(pantalla, (185, 160, 135), rect_ojo, width=1, border_radius=6)
            simbolo_ojo = "👁" if mostrar_caracteres else "🔒"
            dibujar_texto_en_rect(pantalla, simbolo_ojo, rect_ojo, categoria="subtitulo", tamano=16, color=(60, 45, 35), padding=2)

        # Mensaje de error
        if mensaje_error:
            rect_err = pygame.Rect(rect_card.left + 24, rect_input.bottom + 8, rect_card.width - 48, 26)
            dibujar_texto_en_rect(pantalla, mensaje_error, rect_err, categoria="subtitulo", tamano=14, color=(215, 50, 50), padding=2)

        # Botón Cancelar (reutiliza el botón existente oficial de la carpeta de botones)
        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            dibujar_texto_en_rect(pantalla, "CANCELAR", btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        # Botón Confirmar
        col_con = (82, 194, 114) if hov_con else (68, 172, 98)
        pygame.draw.rect(pantalla, col_con, btn_confirmar, border_radius=10)
        pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, width=2, border_radius=10)
        dibujar_texto_en_rect(pantalla, "CONFIRMAR", btn_confirmar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=6)

        pygame.display.flip()


def pedir_password_modal(pantalla, reloj, partida):
    """
    Solicita la contraseña de un perfil protegido y valida que sea correcta.
    Permite reintentar si es errónea o cancelar.
    Retorna True si la autenticación fue exitosa, o False si se canceló.
    """
    nombre = partida.get("nombre", f"Partida {partida.get('id', 1)}")
    p_hash = partida.get("password_hash", "")
    p_salt = partida.get("password_salt", "")

    if not p_hash:
        return True

    pygame.event.clear()

    while True:
        pwd = solicitar_texto_modal(
            pantalla, reloj,
            titulo="PERFIL PROTEGIDO",
            subtitulo=f"Introduce la contraseña de «{nombre}»:",
            es_password=True,
            permitir_vacio=False,
        )
        if pwd is None:
            pygame.event.clear()
            return False

        if verify_password(pwd, p_hash, p_salt):
            pygame.event.clear()
            return True

        # Mostrar aviso de contraseña incorrecta
        ancho, alto = pantalla.get_width(), pantalla.get_height()
        fuente_tit = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=28)
        fuente_txt = obtener_fuente_texto(TAMANO_TEXTO)
        fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=22)

        w_a, h_a = 480, 230
        r_a = pygame.Rect((ancho - w_a) // 2, (alto - h_a) // 2, w_a, h_a)
        w_btn, h_btn = 160, 48
        b_rein = pygame.Rect(r_a.centerx - w_btn - 12, r_a.bottom - 68, w_btn, h_btn)
        b_canc = pygame.Rect(r_a.centerx + 12, r_a.bottom - 68, w_btn, h_btn)

        spr_canc_norm = _cargar_sprite_boton("Menu/boton-cancelar.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar.png", w_btn, h_btn)
        spr_canc_semi = _cargar_sprite_boton("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-semiapretado.png", w_btn, h_btn)
        spr_canc_apret = _cargar_sprite_boton("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-apretado.png", w_btn, h_btn)
        spr_canc_hover = aclarar_boton(spr_canc_norm) if spr_canc_norm else None

        captura_aviso = pantalla.copy()
        esperando = True
        reintentar = False

        pygame.event.clear()

        while esperando:
            reloj.tick(60)
            pos_m = pygame.mouse.get_pos()
            h_rein = b_rein.collidepoint(pos_m)
            h_canc = b_canc.collidepoint(pos_m)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    pygame.event.clear()
                    return False
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    esperando = False
                    reintentar = True
                    pygame.event.clear()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if b_rein.collidepoint(ev.pos):
                        esperando = False
                        reintentar = True
                        pygame.event.clear()
                    elif b_canc.collidepoint(ev.pos):
                        pulsado = True
                        if spr_canc_semi and spr_canc_apret:
                            pulsado = animar_pulsacion_boton(pantalla, b_canc, spr_canc_semi, spr_canc_apret, (253, 246, 233), spr_canc_norm)
                        if pulsado:
                            pygame.event.clear()
                            return False

            pantalla.blit(captura_aviso, (0, 0))
            pygame.draw.rect(pantalla, (253, 246, 233), r_a, border_radius=14)
            pygame.draw.rect(pantalla, (220, 70, 60), r_a, width=3, border_radius=14)

            t_err_tit = fuente_tit.render("ACCESO DENEGADO", True, (215, 50, 50))
            pantalla.blit(t_err_tit, t_err_tit.get_rect(center=(r_a.centerx, r_a.top + 38)))

            t_err_desc = fuente_txt.render("La contraseña introducida es incorrecta.", True, (70, 55, 45))
            pantalla.blit(t_err_desc, t_err_desc.get_rect(center=(r_a.centerx, r_a.top + 80)))

            pygame.draw.rect(pantalla, (82, 194, 114) if h_rein else (68, 172, 98), b_rein, border_radius=8)
            t_br = fuente_btn.render("REINTENTAR", True, (255, 255, 255))
            pantalla.blit(t_br, t_br.get_rect(center=b_rein.center))

            if spr_canc_norm:
                pantalla.blit(spr_canc_hover if (h_canc and spr_canc_hover) else spr_canc_norm, b_canc)
            else:
                pygame.draw.rect(pantalla, (255, 255, 255) if h_canc else (242, 234, 222), b_canc, border_radius=8)
                pygame.draw.rect(pantalla, (185, 155, 125), b_canc, width=2, border_radius=8)
                t_bc = fuente_btn.render("CANCELAR", True, (60, 45, 35))
                pantalla.blit(t_bc, t_bc.get_rect(center=b_canc.center))

            pygame.display.flip()

        if not reintentar:
            pygame.event.clear()
            return False


def modal_administrar_perfil(pantalla, reloj, partida):
    """
    Diálogo para administrar un perfil:
    - Cambiar nombre
    - Agregar / Cambiar / Quitar contraseña
    - Eliminar perfil
    - Botón «VOLVER» oficial del proyecto para regresar sin cambios
    Retorna True si hubo cambios que requieren refrescar la lista, o False al salir.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(15, negrita=False)
    fuente_btn = obtener_fuente_subtitulo(16, negrita=True)

    # Dimensiones equilibradas del modal sin botón inferior (cerrado mediante la X)
    w_card, h_card = 560, 335
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    # Botón X en la esquina superior derecha del modal
    W_X, H_X = 29, 34
    rect_btn_x = pygame.Rect(rect_card.right - W_X - 16, rect_card.top + 16, W_X, H_X)
    spr_x_norm = _cargar_sprite_boton("HUD/boton-x.png", W_X, H_X) or _cargar_sprite_boton("boton-x.png", W_X, H_X)
    spr_x_semi = _cargar_sprite_boton("HUD/boton-x-semiapretado.png", W_X, H_X) or _cargar_sprite_boton("boton-x-semiapretado.png", W_X, H_X)
    spr_x_apr = _cargar_sprite_boton("HUD/boton-x-apretado.png", W_X, H_X) or _cargar_sprite_boton("boton-x-apretado.png", W_X, H_X)
    spr_x_hover = aclarar_boton(spr_x_norm) if spr_x_norm else None

    w_b, h_b = 360, 48
    x_b = rect_card.centerx - (w_b // 2)
    y_base = rect_card.top + 114
    gap_b = 14

    btn_renombrar = pygame.Rect(x_b, y_base, w_b, h_b)
    btn_password = pygame.Rect(x_b, y_base + (h_b + gap_b), w_b, h_b)
    btn_eliminar = pygame.Rect(x_b, y_base + (h_b + gap_b) * 2, w_b, h_b)

    fondo_tarjeta = (253, 246, 233)
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    hubo_cambios = False

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        hov_ren = btn_renombrar.collidepoint(pos_mouse)
        hov_pwd = btn_password.collidepoint(pos_mouse)
        hov_eli = btn_eliminar.collidepoint(pos_mouse)
        hov_x = rect_btn_x.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return hubo_cambios

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # 1. Clic en botón X de cerrar
                if rect_btn_x.collidepoint(evento.pos):
                    pulsado = True
                    if spr_x_semi and spr_x_apr:
                        pulsado = animar_pulsacion_boton(pantalla, rect_btn_x, spr_x_semi, spr_x_apr, fondo_tarjeta, spr_x_norm)
                    if pulsado:
                        return hubo_cambios

                # 2. Clic en Cambiar Nombre
                elif btn_renombrar.collidepoint(evento.pos):
                    nuevo_nom = solicitar_texto_modal(
                        pantalla, reloj,
                        titulo="CAMBIAR NOMBRE",
                        subtitulo=f"Introduce el nuevo nombre para «{partida['nombre']}»:",
                        valor_inicial=partida["nombre"],
                        permitir_vacio=False,
                    )
                    if nuevo_nom and nuevo_nom != partida["nombre"]:
                        renombrar_partida(partida["id"], nuevo_nom)
                        partida["nombre"] = nuevo_nom
                        hubo_cambios = True

                # 3. Clic en Contraseña
                elif btn_password.collidepoint(evento.pos):
                    # Si ya tiene contraseña, autenticar primero
                    if partida.get("tiene_password", False):
                        if not pedir_password_modal(pantalla, reloj, partida):
                            continue
                        # Preguntar nueva contraseña o dejar vacío para quitar
                        nueva_pwd = solicitar_texto_modal(
                            pantalla, reloj,
                            titulo="GESTIONAR CONTRASEÑA",
                            subtitulo="Escribe una nueva contraseña o deja vacío para quitarla:",
                            es_password=True,
                            permitir_vacio=True,
                        )
                        if nueva_pwd is not None:
                            cambiar_password_partida(partida["id"], nueva_pwd)
                            partida["tiene_password"] = bool(nueva_pwd.strip())
                            hubo_cambios = True
                    else:
                        # No tiene contraseña: agregar una
                        nueva_pwd = solicitar_texto_modal(
                            pantalla, reloj,
                            titulo="AGREGAR CONTRASEÑA",
                            subtitulo=f"Asigna una contraseña de acceso a «{partida['nombre']}»:",
                            es_password=True,
                            permitir_vacio=False,
                        )
                        if nueva_pwd:
                            cambiar_password_partida(partida["id"], nueva_pwd)
                            partida["tiene_password"] = True
                            hubo_cambios = True

                # 4. Clic en Eliminar
                elif btn_eliminar.collidepoint(evento.pos):
                    if mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
                        eliminar_partida(partida["id"])
                        return True

                # 5. Clic fuera del modal para salir
                elif not rect_card.collidepoint(evento.pos):
                    return hubo_cambios

        # Dibujar modal
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        # Botón X de cabecera
        spr_x_dib = spr_x_hover if (hov_x and spr_x_hover) else spr_x_norm
        if spr_x_dib:
            pantalla.blit(spr_x_dib, rect_btn_x)

        # Título centrado con margen seguro
        rect_tit = pygame.Rect(rect_card.left + 50, rect_card.top + 16, rect_card.width - 100, 32)
        dibujar_texto_en_rect(pantalla, "ADMINISTRAR PERFIL", rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(60, 45, 35))

        # Información distribuida en dos líneas con autoajuste para nombres extensos
        nom_perfil = partida.get("nombre", "")
        rect_nom = pygame.Rect(rect_card.left + 24, rect_card.top + 52, rect_card.width - 48, 24)
        dibujar_texto_en_rect(pantalla, f"Perfil: «{nom_perfil}»", rect_nom, categoria="subtitulo", tamano=15, color=(70, 55, 45), negrita=True, padding=4)

        tiene_p = partida.get("tiene_password", False)
        txt_est = "Estado: Protegido con contraseña" if tiene_p else "Estado: Sin contraseña"
        col_est = (40, 130, 65) if tiene_p else (125, 105, 90)
        rect_est = pygame.Rect(rect_card.left + 24, rect_card.top + 78, rect_card.width - 48, 20)
        dibujar_texto_en_rect(pantalla, txt_est, rect_est, categoria="pequena", tamano=14, color=col_est, padding=4)

        # 1. Renombrar
        col_ren = (255, 255, 255) if hov_ren else (245, 238, 226)
        pygame.draw.rect(pantalla, col_ren, btn_renombrar, border_radius=10)
        pygame.draw.rect(pantalla, (185, 155, 125), btn_renombrar, width=2, border_radius=10)
        dibujar_texto_en_rect(pantalla, "CAMBIAR NOMBRE", btn_renombrar, categoria="subtitulo", tamano=16, color=(60, 45, 35), negrita=True, padding=8)

        # 2. Contraseña (renderiza 'Ñ' perfectamente y autoajusta texto largo)
        txt_btn_pwd = "CAMBIAR / QUITAR CONTRASEÑA" if tiene_p else "AGREGAR CONTRASEÑA"
        col_pwd = (255, 255, 255) if hov_pwd else (245, 238, 226)
        pygame.draw.rect(pantalla, col_pwd, btn_password, border_radius=10)
        pygame.draw.rect(pantalla, (185, 155, 125), btn_password, width=2, border_radius=10)
        dibujar_texto_en_rect(pantalla, txt_btn_pwd, btn_password, categoria="subtitulo", tamano=16, color=(60, 45, 35), negrita=True, padding=8)

        # 3. Eliminar
        col_eli = (235, 95, 90) if hov_eli else (215, 80, 75)
        pygame.draw.rect(pantalla, col_eli, btn_eliminar, border_radius=10)
        pygame.draw.rect(pantalla, (170, 50, 45), btn_eliminar, width=2, border_radius=10)
        dibujar_texto_en_rect(pantalla, "ELIMINAR PERFIL", btn_eliminar, categoria="subtitulo", tamano=16, color=(255, 255, 255), negrita=True, padding=8)

        pygame.display.flip()


def mostrar_dialogo_partida_existente(pantalla, reloj, nombre):
    """
    Diálogo modal de confirmación cuando ya existe una partida con el nombre ingresado.
    Ofrece 3 opciones:
    - «OTRO NOMBRE»: para ingresar otro nombre identificador.
    - «SOBRESCRIBIR»: confirmación explícita para reemplazar la partida existente.
    - «CANCELAR»: aborta la operación y regresa utilizando el botón oficial existente.
    Retorna "cambiar", "sobrescribir" o "cancelar".
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=22)

    w_card, h_card = 560, 290
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    w_btn, h_btn = 163, 48
    gap_btn = 16
    total_w = w_btn * 3 + gap_btn * 2
    x_base = rect_card.centerx - (total_w // 2)
    y_btns = rect_card.top + 210

    btn_cambiar = pygame.Rect(x_base, y_btns, w_btn, h_btn)
    btn_sobrescribir = pygame.Rect(x_base + w_btn + gap_btn, y_btns, w_btn, h_btn)
    btn_cancelar = pygame.Rect(x_base + (w_btn + gap_btn) * 2, y_btns, w_btn, h_btn)

    spr_canc_norm = _cargar_sprite_boton("Menu/boton-cancelar.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar.png", w_btn, h_btn)
    spr_canc_semi = _cargar_sprite_boton("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-semiapretado.png", w_btn, h_btn)
    spr_canc_apret = _cargar_sprite_boton("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-apretado.png", w_btn, h_btn)
    spr_canc_hover = aclarar_boton(spr_canc_norm) if spr_canc_norm else None
    fondo_tarjeta = (253, 246, 233)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        hov_cam = btn_cambiar.collidepoint(pos_mouse)
        hov_sob = btn_sobrescribir.collidepoint(pos_mouse)
        hov_can = btn_cancelar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cambiar.collidepoint(evento.pos):
                    return "cambiar"
                elif btn_sobrescribir.collidepoint(evento.pos):
                    return "sobrescribir"
                elif btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_canc_semi and spr_canc_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_canc_semi, spr_canc_apret, fondo_tarjeta, spr_canc_norm)
                    if pulsado:
                        return "cancelar"

        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (225, 120, 48), rect_card, width=3, border_radius=16)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 24, rect_card.top + 16, rect_card.width - 48, 32)
        dibujar_texto_en_rect(pantalla, "PARTIDA EXISTENTE", rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(205, 80, 40))

        # Mensaje de advertencia con soporte de ajuste automático
        rect_msg = pygame.Rect(rect_card.left + 24, rect_card.top + 54, rect_card.width - 48, 32)
        dibujar_texto_en_rect(pantalla, f"Ya existe una partida guardada con el nombre «{nombre}».", rect_msg, categoria="subtitulo", tamano=16, color=(60, 45, 35), multiline=True, padding=2)

        rect_sub = pygame.Rect(rect_card.left + 24, rect_card.top + 92, rect_card.width - 48, 44)
        dibujar_texto_en_rect(pantalla, "¿Deseas elegir otro nombre o sobrescribir la partida existente?", rect_sub, categoria="subtitulo", tamano=15, color=(115, 95, 80), multiline=True, padding=2)

        # Botón 1: Cambiar nombre
        col_cam = (255, 255, 255) if hov_cam else (242, 234, 222)
        pygame.draw.rect(pantalla, col_cam, btn_cambiar, border_radius=10)
        pygame.draw.rect(pantalla, (185, 155, 125), btn_cambiar, width=2, border_radius=10)
        dibujar_texto_en_rect(pantalla, "OTRO NOMBRE", btn_cambiar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        # Botón 2: Sobrescribir
        col_sob = (235, 95, 90) if hov_sob else (215, 80, 75)
        pygame.draw.rect(pantalla, col_sob, btn_sobrescribir, border_radius=10)
        pygame.draw.rect(pantalla, (170, 50, 45), btn_sobrescribir, width=2, border_radius=10)
        dibujar_texto_en_rect(pantalla, "SOBRESCRIBIR", btn_sobrescribir, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=6)

        # Botón 3: Cancelar (reutiliza el botón oficial del proyecto)
        if spr_canc_norm:
            pantalla.blit(spr_canc_hover if (hov_can and spr_canc_hover) else spr_canc_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            dibujar_texto_en_rect(pantalla, "CANCELAR", btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        pygame.display.flip()


def flujo_crear_nueva_partida(
    pantalla,
    reloj,
    color_p1="Celeste",
    color_p2="Violeta",
    accesorio_p1="Ninguno",
    accesorio_p2="Ninguno",
):
    """
    Permite crear una partida independiente:
    - Pide un nombre para identificarla.
    - Si ya existe una con ese nombre, pide confirmación o solicita otro nombre (nunca sobrescribe silenciosamente).
    - Permite establecer una contraseña opcional.
    - Guarda la personalización actual de ambos personajes (colores y accesorios) en esta partida.
    - Si se cancela en cualquier paso, retorna None y no persiste ningún cambio.
    - Retorna el diccionario de la nueva partida creada, o None si se canceló.
    """
    partidas = cargar_partidas()
    nuevo_id = max([p["id"] for p in partidas], default=0) + 1
    nombre_sugerido = f"Partida {nuevo_id}"

    nombre_final = None
    id_sobrescribir = None

    while True:
        nom = solicitar_texto_modal(
            pantalla, reloj,
            titulo="NUEVA PARTIDA",
            subtitulo="Ingresa un nombre para tu partida:",
            valor_inicial=nombre_sugerido,
            es_password=False,
            permitir_vacio=False,
            max_caracteres=18,
        )
        if not nom:
            return None

        nom = nom.strip()
        partidas = cargar_partidas()
        existente = next((p for p in partidas if p["nombre"].strip().lower() == nom.lower()), None)

        if existente:
            decision = mostrar_dialogo_partida_existente(pantalla, reloj, existente["nombre"])
            if decision == "cambiar":
                nombre_sugerido = nom
                continue
            elif decision == "sobrescribir":
                if existente.get("tiene_password"):
                    if not pedir_password_modal(pantalla, reloj, existente):
                        continue
                nombre_final = existente["nombre"]
                id_sobrescribir = existente["id"]
                break
            else:
                return None
        else:
            nombre_final = nom
            id_sobrescribir = None
            break

    # Contraseña opcional
    pwd = solicitar_texto_modal(
        pantalla, reloj,
        titulo="CONTRASEÑA (OPCIONAL)",
        subtitulo="Establece una contraseña o deja vacío si no deseas protegerla:",
        es_password=True,
        permitir_vacio=True,
        max_caracteres=18,
    )
    if pwd is None:
        return None

    desbloqueados_nuevos = crear_desbloqueados_inicial()
    partida_creada = guardar_partida(
        desbloqueados_nuevos,
        id_partida=id_sobrescribir,
        nombre_partida=nombre_final,
        password=pwd,
        color_p1=color_p1,
        color_p2=color_p2,
        accesorio_p1=accesorio_p1,
        accesorio_p2=accesorio_p2,
    )
    if partida_creada is None:
        return None
    partida_creada["password_plain"] = pwd or ""
    return partida_creada



def modal_flujo_guardar_perfil(
    pantalla,
    reloj,
    niveles_desbloqueados,
    id_partida_actual=None,
    nombre_partida_actual=None,
    password_partida_actual=None,
    color_p1=None,
    color_p2=None,
    accesorio_p1=None,
    accesorio_p2=None,
):
    """
    Flujo interactivo completo al presionar «Guardar y salir»:
    Permite:
    1. Si hay una partida actual provisional, guardarla directamente con su nombre elegido.
    2. Seleccionar un perfil existente para actualizarlo.
    3. Crear un perfil nuevo con nombre y contraseña opcional.
    Retorna True si el guardado fue exitoso y se completó, o False si se canceló.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_item_tit = obtener_fuente_boton(TAMANO_ITEM_TITULO, tamano_fallback=22)
    fuente_item_det = obtener_fuente_pequena(TAMANO_PEQUENA)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=22)
    fuente_pag = obtener_fuente_contador(TAMANO_SUBTITULO)

    w_card, h_card = 640, 570
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 175))
    captura_previa = pantalla.copy()

    pagina_guardar = 0
    MAX_SLOTS = 4
    partidas = cargar_partidas()

    # Reutilizar el botón Cancelar oficial del proyecto con proporciones exactas
    w_can, h_can = 204, 60
    btn_cancelar = pygame.Rect(rect_card.centerx - (w_can // 2), rect_card.top + 488, w_can, h_can)
    spr_can_norm = _cargar_sprite_boton("Menu/boton-cancelar.png", w_can, h_can) or _cargar_sprite_boton("boton-cancelar.png", w_can, h_can)
    spr_can_semi = _cargar_sprite_boton("Menu/boton-cancelar-semiapretado.png", w_can, h_can) or _cargar_sprite_boton("boton-cancelar-semiapretado.png", w_can, h_can)
    spr_can_apret = _cargar_sprite_boton("Menu/boton-cancelar-apretado.png", w_can, h_can) or _cargar_sprite_boton("boton-cancelar-apretado.png", w_can, h_can)
    spr_can_hover = aclarar_boton(spr_can_norm) if spr_can_norm else None
    fondo_tarjeta = (253, 246, 233)

    # Identificar si la partida actual está en memoria o registrada
    es_provisional = bool(nombre_partida_actual and not any(p.get("id") == id_partida_actual for p in partidas))
    texto_btn_crear = f"+ GUARDAR EN «{nombre_partida_actual}»" if nombre_partida_actual else "+ CREAR NUEVA PARTIDA"

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        # Botón superior
        btn_crear_nuevo = pygame.Rect(rect_card.left + 40, rect_card.top + 76, w_card - 80, 42)
        hov_crear = btn_crear_nuevo.collidepoint(pos_mouse)
        hov_can = btn_cancelar.collidepoint(pos_mouse)

        total_paginas = max(1, (len(partidas) + MAX_SLOTS - 1) // MAX_SLOTS)
        if pagina_guardar >= total_paginas:
            pagina_guardar = max(0, total_paginas - 1)

        idx_inicio = pagina_guardar * MAX_SLOTS
        partidas_mostrar = partidas[idx_inicio:idx_inicio + MAX_SLOTS]

        # Slots organizados con altura y separación fijas sin superposición (top + 130 a top + 396)
        slots = []
        y_slot = rect_card.top + 130
        h_slot = 62
        gap_slot = 6

        for idx, p in enumerate(partidas_mostrar):
            r_s = pygame.Rect(rect_card.left + 40, y_slot + idx * (h_slot + gap_slot), w_card - 80, h_slot)
            slots.append((r_s, p))

        # Paginación organizada entre slots y botón cancelar (top + 418 a top + 446)
        btn_pag_ant = pygame.Rect(rect_card.centerx - 100, rect_card.top + 418, 32, 28) if total_paginas > 1 else None
        btn_pag_sig = pygame.Rect(rect_card.centerx + 68, rect_card.top + 418, 32, 28) if total_paginas > 1 else None

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_can_semi and spr_can_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_can_semi, spr_can_apret, fondo_tarjeta, spr_can_norm)
                    if pulsado:
                        return False

                if btn_pag_ant and btn_pag_ant.collidepoint(evento.pos) and pagina_guardar > 0:
                    pagina_guardar -= 1
                    continue
                elif btn_pag_sig and btn_pag_sig.collidepoint(evento.pos) and pagina_guardar < total_paginas - 1:
                    pagina_guardar += 1
                    continue

                if btn_crear_nuevo.collidepoint(evento.pos):
                    if nombre_partida_actual:
                        res = guardar_partida(
                            niveles_desbloqueados,
                            id_partida=id_partida_actual,
                            nombre_partida=nombre_partida_actual,
                            password=password_partida_actual,
                            color_p1=color_p1,
                            color_p2=color_p2,
                            accesorio_p1=accesorio_p1,
                            accesorio_p2=accesorio_p2,
                        )
                        if res is not None:
                            return True
                    else:
                        # Pedir nombre de partida
                        partidas_actuales = cargar_partidas()
                        nuevo_id = max([p["id"] for p in partidas_actuales], default=0) + 1
                        sug_nom = f"Partida {nuevo_id}"

                        nom_final = None
                        id_sobrescribir = None

                        while True:
                            nom = solicitar_texto_modal(
                                pantalla, reloj,
                                titulo="NUEVA PARTIDA",
                                subtitulo="Escribe un nombre para identificar tu partida:",
                                valor_inicial=sug_nom,
                                permitir_vacio=False,
                            )
                            if not nom:
                                break

                            nom = nom.strip()
                            partidas_actuales = cargar_partidas()
                            existente = next((p for p in partidas_actuales if p["nombre"].strip().lower() == nom.lower()), None)
                            if existente:
                                decision = mostrar_dialogo_partida_existente(pantalla, reloj, existente["nombre"])
                                if decision == "cambiar":
                                    sug_nom = nom
                                    continue
                                elif decision == "sobrescribir":
                                    if existente.get("tiene_password"):
                                        if not pedir_password_modal(pantalla, reloj, existente):
                                             continue
                                    nom_final = existente["nombre"]
                                    id_sobrescribir = existente["id"]
                                    break
                                else:
                                    break
                            else:
                                nom_final = nom
                                id_sobrescribir = None
                                break

                        if not nom_final:
                            continue

                        # Preguntar contraseña opcional
                        pwd = solicitar_texto_modal(
                            pantalla, reloj,
                            titulo="CONTRASEÑA (OPCIONAL)",
                            subtitulo="Asigna una contraseña o deja vacío si no deseas protegerla:",
                            es_password=True,
                            permitir_vacio=True,
                        )
                        if pwd is None:
                            continue

                        res = guardar_partida(
                            niveles_desbloqueados,
                            id_partida=id_sobrescribir,
                            nombre_partida=nom_final,
                            password=pwd,
                            color_p1=color_p1,
                            color_p2=color_p2,
                            accesorio_p1=accesorio_p1,
                            accesorio_p2=accesorio_p2,
                        )
                        if res is not None:
                            return True

                for r_s, p in slots:
                    if r_s.collidepoint(evento.pos):
                        # Si tiene contraseña, pedirla antes de actualizar
                        if p.get("tiene_password", False):
                            if not pedir_password_modal(pantalla, reloj, p):
                                break

                        res = guardar_partida(
                            niveles_desbloqueados,
                            id_partida=p["id"],
                            nombre_partida=p["nombre"],
                            color_p1=color_p1 if color_p1 is not None else p.get("color_p1"),
                            color_p2=color_p2 if color_p2 is not None else p.get("color_p2"),
                            accesorio_p1=accesorio_p1 if accesorio_p1 is not None else p.get("accesorio_p1"),
                            accesorio_p2=accesorio_p2 if accesorio_p2 is not None else p.get("accesorio_p2"),
                        )
                        if res is not None:
                            return True

        # Dibujar pantalla
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        t_tit = fuente_titulo.render("GUARDAR Y SALIR", True, (60, 45, 35))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 30)))

        t_sub = fuente_sub.render("Elige una partida para actualizar o crea una nueva:", True, (115, 95, 80))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 56)))

        # Botón crear nuevo / guardar sesión provisional
        col_cr = (82, 194, 114) if hov_crear else (68, 172, 98)
        pygame.draw.rect(pantalla, col_cr, btn_crear_nuevo, border_radius=8)
        pygame.draw.rect(pantalla, (45, 130, 70), btn_crear_nuevo, width=2, border_radius=8)
        t_cr = fuente_btn.render(texto_btn_crear, True, (255, 255, 255))
        pantalla.blit(t_cr, t_cr.get_rect(center=btn_crear_nuevo.center))

        if not partidas:
            t_sin = fuente_sub.render("Todavía no tenés partidas guardadas.", True, (120, 105, 90))
            pantalla.blit(t_sin, t_sin.get_rect(center=(rect_card.centerx, rect_card.top + 220)))
            t_sin2 = fuente_item_det.render("Pulsa «+ CREAR NUEVA PARTIDA» arriba para guardar tu progreso.", True, (140, 125, 110))
            pantalla.blit(t_sin2, t_sin2.get_rect(center=(rect_card.centerx, rect_card.top + 250)))
        else:
            # Lista de perfiles
            for r_s, p in slots:
                hov_s = r_s.collidepoint(pos_mouse)
                es_actual = (id_partida_actual is not None and p["id"] == id_partida_actual)
                col_s = (255, 252, 244) if hov_s else (255, 255, 255)
                borde_s = (45, 145, 75) if es_actual else ((225, 145, 75) if hov_s else (220, 202, 178))
                pygame.draw.rect(pantalla, col_s, r_s, border_radius=8)
                pygame.draw.rect(pantalla, borde_s, r_s, width=2 if (hov_s or es_actual) else 1, border_radius=8)

                txt_nom = f"{p['nombre']} (Mundo {p['mundo_max']}-{p['nivel_max']})"
                if es_actual:
                    txt_nom += "  [Partida actual]"
                t_n = fuente_item_tit.render(txt_nom, True, (40, 115, 60) if es_actual else (55, 45, 35))
                pantalla.blit(t_n, (r_s.left + 16, r_s.top + 10))

                cant_comp = calcular_niveles_completados(p.get("niveles_desbloqueados", {}))
                det = f"Niveles completados: {cant_comp}/15  •  Guardado: {p.get('fecha', '')}"
                t_d = fuente_item_det.render(det, True, (115, 100, 85))
                pantalla.blit(t_d, (r_s.left + 16, r_s.top + 34))

                candado = "🔒" if p.get("tiene_password") else "🔓"
                t_cand = fuente_sub.render(candado, True, (60, 45, 35))
                pantalla.blit(t_cand, (r_s.right - 35, r_s.centery - 10))

            # Paginación
            if total_paginas > 1:
                hov_p_ant = btn_pag_ant.collidepoint(pos_mouse) and pagina_guardar > 0
                hov_p_sig = btn_pag_sig.collidepoint(pos_mouse) and pagina_guardar < total_paginas - 1
                pygame.draw.rect(pantalla, (255, 255, 255) if hov_p_ant else (240, 230, 215), btn_pag_ant, border_radius=6)
                pygame.draw.rect(pantalla, (180, 150, 120), btn_pag_ant, width=1, border_radius=6)
                t_pa = fuente_pag.render("◀", True, (60, 45, 35) if pagina_guardar > 0 else (175, 160, 145))
                pantalla.blit(t_pa, t_pa.get_rect(center=btn_pag_ant.center))

                t_pnum = fuente_pag.render(f"{pagina_guardar + 1} / {total_paginas}", True, (80, 65, 55))
                pantalla.blit(t_pnum, t_pnum.get_rect(center=(rect_card.centerx, rect_card.top + 432)))

                pygame.draw.rect(pantalla, (255, 255, 255) if hov_p_sig else (240, 230, 215), btn_pag_sig, border_radius=6)
                pygame.draw.rect(pantalla, (180, 150, 120), btn_pag_sig, width=1, border_radius=6)
                t_ps = fuente_pag.render("▶", True, (60, 45, 35) if pagina_guardar < total_paginas - 1 else (175, 160, 145))
                pantalla.blit(t_ps, t_ps.get_rect(center=btn_pag_sig.center))

        # Botón Cancelar (reutiliza el botón oficial del proyecto con proporciones 3.4:1)
        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_c = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_c, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            t_can = fuente_btn.render("CANCELAR", True, (60, 45, 35))
            pantalla.blit(t_can, t_can.get_rect(center=btn_cancelar.center))

        pygame.display.flip()


def mostrar_dialogo_guardar_salir(
    pantalla,
    reloj,
    niveles_desbloqueados,
    id_partida=None,
    nombre_partida=None,
    password_partida=None,
    color_p1=None,
    color_p2=None,
    accesorio_p1=None,
    accesorio_p2=None,
):
    """
    Muestra la confirmación clara obligatoria con las tres opciones:
    1. «GUARDAR Y SALIR»: abre el procedimiento para guardar y cierra solo si finalizó con éxito.
    2. «SALIR SIN GUARDAR»: cierra el juego sin persistir los cambios pendientes ni alterar guardados.
    3. «CANCELAR»: cierra el diálogo y vuelve exactamente a la pantalla en que estaba el jugador.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    mundo_max, nivel_max = obtener_maximo_alcanzado(niveles_desbloqueados)

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=36)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO_GRANDE)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=28)

    ancho_card, alto_card = 560, 480
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 272, 80
    x_btn = rect_card.centerx - (w_btn // 2)
    y_base_btns = rect_card.top + 140
    espacio_btns = 14

    btn_guardar = pygame.Rect(x_btn, y_base_btns, w_btn, h_btn)
    btn_no_guardar = pygame.Rect(x_btn, y_base_btns + h_btn + espacio_btns, w_btn, h_btn)
    btn_cancelar = pygame.Rect(x_btn, y_base_btns + (h_btn + espacio_btns) * 2, w_btn, h_btn)

    def _scale_btn(nombre, w, h):
        return cargar_boton_escalado(nombre, w, h)

    # Sprites oficiales reutilizados con animación
    spr_g_norm = _scale_btn("Ventanas/boton-guardar-y-salir.png", w_btn, h_btn) or _scale_btn("boton-guardar-y-salir.png", w_btn, h_btn)
    spr_g_semi = _scale_btn("Ventanas/boton-guardar-y-salir-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-guardar-y-salir-semiapretado.png", w_btn, h_btn)
    spr_g_apret = _scale_btn("Ventanas/boton-guardar-y-salir-apretado.png", w_btn, h_btn) or _scale_btn("boton-guardar-y-salir-apretado.png", w_btn, h_btn)

    spr_s_norm = _scale_btn("Ventanas/boton-salir-sin-guardar.png", w_btn, h_btn) or _scale_btn("Menu/boton-salir-sin-guardar.png", w_btn, h_btn) or _scale_btn("boton-salir-sin-guardar.png", w_btn, h_btn)
    spr_s_semi = _scale_btn("Menu/boton-salir-sin-guardar-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-salir-sin-guardar-semiapretado.png", w_btn, h_btn)
    spr_s_apret = _scale_btn("Ventanas/boton-salir-sin-guardar-apretado.png", w_btn, h_btn) or _scale_btn("Menu/boton-salir-sin-guardar-apretado.png", w_btn, h_btn) or _scale_btn("boton-salir-sin-guardar-apretado.png", w_btn, h_btn)

    spr_c_norm = _scale_btn("Menu/boton-cancelar.png", w_btn, h_btn) or _scale_btn("boton-cancelar.png", w_btn, h_btn)
    spr_c_semi = _scale_btn("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-cancelar-semiapretado.png", w_btn, h_btn)
    spr_c_apret = _scale_btn("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _scale_btn("boton-cancelar-apretado.png", w_btn, h_btn)

    spr_g_hover = aclarar_boton(spr_g_norm) if spr_g_norm else None
    spr_s_hover = aclarar_boton(spr_s_norm) if spr_s_norm else None
    spr_c_hover = aclarar_boton(spr_c_norm) if spr_c_norm else None
    fondo_tarjeta = (253, 246, 233)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    captura_previa = pantalla.copy()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()
        hov_g = btn_guardar.collidepoint(pos_mouse)
        hov_s = btn_no_guardar.collidepoint(pos_mouse)
        hov_c = btn_cancelar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "cancelar"

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_guardar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_g_semi and spr_g_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_guardar, spr_g_semi, spr_g_apret, fondo_tarjeta, spr_g_norm)
                    if pulsado:
                        guardado_ok = modal_flujo_guardar_perfil(
                            pantalla, reloj,
                            niveles_desbloqueados=niveles_desbloqueados,
                            id_partida_actual=id_partida,
                            nombre_partida_actual=nombre_partida,
                            password_partida_actual=password_partida,
                            color_p1=color_p1,
                            color_p2=color_p2,
                            accesorio_p1=accesorio_p1,
                            accesorio_p2=accesorio_p2,
                        )
                        if guardado_ok:
                            return "guardar_salir"

                elif btn_no_guardar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_s_semi and spr_s_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_no_guardar, spr_s_semi, spr_s_apret, fondo_tarjeta, spr_s_norm)
                    if pulsado:
                        return "salir_sin_guardar"

                elif btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_c_semi and spr_c_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_c_semi, spr_c_apret, fondo_tarjeta, spr_c_norm)
                    if pulsado:
                        return "cancelar"

        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=18)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 24, rect_card.top + 20, rect_card.width - 48, 36)
        dibujar_texto_en_rect(pantalla, t("deseas_guardar"), rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(60, 45, 35))

        # Información de mundo y nivel
        rect_info = pygame.Rect(rect_card.left + 24, rect_card.top + 64, rect_card.width - 48, 28)
        dibujar_texto_en_rect(pantalla, f"{t('mundo')} {mundo_max} - {t('nivel')} {nivel_max}", rect_info, categoria="texto", tamano=TAMANO_TEXTO, color=(55, 45, 35))

        # Subtítulo explicativo con multilínea segura
        rect_sub = pygame.Rect(rect_card.left + 24, rect_card.top + 96, rect_card.width - 48, 36)
        dibujar_texto_en_rect(pantalla, t("deseas_guardar_sub", default="Puedes guardar tu partida en un perfil antes de salir."), rect_sub, categoria="texto", tamano=15, color=(120, 105, 90), multiline=True, padding=2)

        if spr_g_norm:
            pantalla.blit(spr_g_hover if (hov_g and spr_g_hover) else spr_g_norm, btn_guardar)
        else:
            pygame.draw.rect(pantalla, (82, 194, 114) if hov_g else (68, 172, 98), btn_guardar, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("guardar_salir"), btn_guardar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=8)

        if spr_s_norm:
            pantalla.blit(spr_s_hover if (hov_s and spr_s_hover) else spr_s_norm, btn_no_guardar)
        else:
            pygame.draw.rect(pantalla, (235, 95, 90) if hov_s else (215, 80, 75), btn_no_guardar, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("salir_sin_guardar"), btn_no_guardar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=8)

        if spr_c_norm:
            pantalla.blit(spr_c_hover if (hov_c and spr_c_hover) else spr_c_norm, btn_cancelar)
        else:
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_c else (242, 234, 222), btn_cancelar, border_radius=12)
            dibujar_texto_en_rect(pantalla, t("cancelar"), btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=8)

        pygame.display.flip()


def mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
    """
    Muestra un diálogo modal interactivo con estética pastel crema solicitando confirmación para borrar una partida.
    Advierte que se eliminará permanentemente la partida guardada correspondiente.
    Retorna True si se confirma («BORRAR PARTIDA»), o False si se cancela.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=34)
    fuente_nombre = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=24)

    ancho_card, alto_card = 560, 310
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 184, 54
    gap_btn = 22
    total_w_btns = (w_btn * 2) + gap_btn
    x_cancelar = rect_card.centerx - (total_w_btns // 2)
    x_borrar = x_cancelar + w_btn + gap_btn
    y_btns = rect_card.bottom - 74

    btn_cancelar = pygame.Rect(x_cancelar, y_btns, w_btn, h_btn)
    btn_borrar = pygame.Rect(x_borrar, y_btns, w_btn, h_btn)

    def _scale_btn(nombre, w, h):
        return cargar_boton_escalado(nombre, w, h)

    spr_can_norm = _scale_btn("Menu/boton-cancelar.png", w_btn, h_btn) or _scale_btn("boton-cancelar.png", w_btn, h_btn)
    spr_can_semi = _scale_btn("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _scale_btn("boton-cancelar-semiapretado.png", w_btn, h_btn)
    spr_can_apret = _scale_btn("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _scale_btn("boton-cancelar-apretado.png", w_btn, h_btn)
    spr_can_hover = aclarar_boton(spr_can_norm) if spr_can_norm else None
    fondo_tarjeta = (253, 246, 233)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((45, 35, 25, 140))
    captura_previa = pantalla.copy()

    nombre = partida.get("nombre", f"Partida {partida.get('id', 1)}")
    mundo_max = partida.get("mundo_max", 1)
    nivel_max = partida.get("nivel_max", 1)

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()
        hov_can = btn_cancelar.collidepoint(pos_mouse)
        hov_bor = btn_borrar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cancelar.collidepoint(evento.pos):
                    pulsado = True
                    if spr_can_semi and spr_can_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_cancelar, spr_can_semi, spr_can_apret, fondo_tarjeta, spr_can_norm)
                    if pulsado:
                        return False
                elif btn_borrar.collidepoint(evento.pos):
                    return True

        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (225, 110, 80), rect_card, width=3, border_radius=18)

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 24, rect_card.top + 18, rect_card.width - 48, 34)
        dibujar_texto_en_rect(pantalla, "ELIMINAR PERFIL", rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(205, 70, 60))

        # Nombre del perfil con ajuste automático
        rect_nom = pygame.Rect(rect_card.left + 24, rect_card.top + 60, rect_card.width - 48, 30)
        dibujar_texto_en_rect(pantalla, f"«{nombre}»  —  Nivel: {mundo_max}-{nivel_max}", rect_nom, categoria="subtitulo", tamano=TAMANO_SUBTITULO_GRANDE, color=(60, 45, 35), padding=4)

        rect_preg = pygame.Rect(rect_card.left + 24, rect_card.top + 98, rect_card.width - 48, 36)
        dibujar_texto_en_rect(pantalla, "¿Seguro que deseas eliminar este perfil y su partida?", rect_preg, categoria="texto", tamano=16, color=(80, 65, 55), multiline=True, padding=2)

        rect_aviso = pygame.Rect(rect_card.left + 24, rect_card.top + 138, rect_card.width - 48, 32)
        dibujar_texto_en_rect(pantalla, "Se borrará todo su progreso y no se podrá recuperar.", rect_aviso, categoria="texto", tamano=15, color=(195, 75, 65), multiline=True, padding=2)

        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=12)
            pygame.draw.rect(pantalla, (195, 168, 138), btn_cancelar, width=2, border_radius=12)
            dibujar_texto_en_rect(pantalla, "CANCELAR", btn_cancelar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(60, 45, 35), padding=6)

        col_bor = (235, 95, 90) if hov_bor else (215, 80, 75)
        pygame.draw.rect(pantalla, col_bor, btn_borrar, border_radius=12)
        pygame.draw.rect(pantalla, (170, 50, 45), btn_borrar, width=2, border_radius=12)
        dibujar_texto_en_rect(pantalla, "BORRAR PERFIL", btn_borrar, categoria="boton", tamano=TAMANO_BOTON_MODAL, color=(255, 255, 255), padding=6)

        pygame.display.flip()


COLORES_RGB_MAP = {
    "Blanco": (232, 232, 232),
    "Gris": (154, 154, 154),
    "Negro": (89, 89, 89),
    "Marron": (206, 136, 111),
    "Rojo": (255, 137, 134),
    "Rosa": (255, 150, 240),
    "Naranja": (255, 160, 100),
    "Amarillo": (255, 244, 123),
    "Verde": (157, 255, 124),
    "Verde oscuro": (105, 205, 75),
    "Celeste": (124, 231, 255),
    "Azul": (36, 166, 247),
    "Violeta": (161, 123, 255),
}


def mostrar_dialogo_confirmar_atuendos(
    pantalla,
    reloj,
    partida,
    color_p1_nuevo,
    color_p2_nuevo,
    acc_p1_nuevo,
    acc_p2_nuevo,
):
    """
    Diálogo modal de confirmación cuando se modificaron colores o accesorios en el menú
    antes de continuar una partida guardada con atuendos diferentes.
    Opciones:
    - «Mantener atuendos guardados»: carga la partida con los colores y accesorios que tenía
      guardados cada personaje. Descarta para esa partida los cambios realizados antes de entrar. (Retorna "mantener")
    - «Cambiar atuendos»: carga la partida con su progreso guardado, pero aplica y guarda los
      colores y accesorios seleccionados para ambos personajes en esa partida. (Retorna "cambiar")
    - Cancelar (ESC o botón X): cancela la carga de la partida y regresa al selector de partidas. (Retorna "cancelar")
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_dialogos(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_box_tit = obtener_fuente_boton(18, tamano_fallback=18)
    fuente_item = obtener_fuente_texto(TAMANO_TEXTO)
    fuente_item_acc = obtener_fuente_pequena(TAMANO_PEQUENA)
    fuente_btn_main = obtener_fuente_boton(18, tamano_fallback=18)
    fuente_btn_sub = obtener_fuente_pequena(13)

    w_card, h_card = 720, 480
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    btn_cerrar = pygame.Rect(rect_card.right - 44, rect_card.top + 14, 30, 30)

    w_box = 315
    h_box = 205
    y_box = rect_card.top + 120
    rect_box_izq = pygame.Rect(rect_card.centerx - w_box - 14, y_box, w_box, h_box)
    rect_box_der = pygame.Rect(rect_card.centerx + 14, y_box, w_box, h_box)

    w_btn = 315
    h_btn = 64
    y_btns = rect_card.bottom - 86
    btn_mantener = pygame.Rect(rect_card.centerx - w_btn - 14, y_btns, w_btn, h_btn)
    btn_cambiar = pygame.Rect(rect_card.centerx + 14, y_btns, w_btn, h_btn)

    c_p1_g = partida.get("color_p1", "Celeste")
    c_p2_g = partida.get("color_p2", "Violeta")
    a_p1_g = partida.get("accesorio_p1", "Ninguno")
    a_p2_g = partida.get("accesorio_p2", "Ninguno")

    nombre_partida = partida.get("nombre", f"Partida {partida.get('id', 1)}")

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((20, 15, 10, 185))
    captura_previa = pantalla.copy()

    pygame.event.clear()

    while True:
        reloj.tick(60)
        pos_mouse = pygame.mouse.get_pos()

        hov_cerrar = btn_cerrar.collidepoint(pos_mouse)
        hov_mantener = btn_mantener.collidepoint(pos_mouse)
        hov_cambiar = btn_cambiar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                pygame.event.clear()
                return "cancelar"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_cerrar.collidepoint(evento.pos):
                    pygame.event.clear()
                    return "cancelar"

                elif btn_mantener.collidepoint(evento.pos):
                    pygame.draw.rect(pantalla, (230, 220, 205), btn_mantener, border_radius=12)
                    pygame.draw.rect(pantalla, (160, 130, 100), btn_mantener, width=2, border_radius=12)
                    pygame.display.flip()
                    pygame.time.delay(60)
                    pygame.event.clear()
                    return "mantener"

                elif btn_cambiar.collidepoint(evento.pos):
                    pygame.draw.rect(pantalla, (45, 130, 70), btn_cambiar, border_radius=12)
                    pygame.draw.rect(pantalla, (30, 95, 50), btn_cambiar, width=2, border_radius=12)
                    pygame.display.flip()
                    pygame.time.delay(60)
                    pygame.event.clear()
                    return "cambiar"

        # Fondo capturado + oscurecimiento
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        # Tarjeta modal pastel crema
        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=18)

        # Botón de cerrar (X)
        col_x = (220, 60, 50) if hov_cerrar else (145, 125, 110)
        t_x = fuente_sub.render("X", True, col_x)
        pantalla.blit(t_x, t_x.get_rect(center=btn_cerrar.center))

        # Título centrado seguro
        rect_tit = pygame.Rect(rect_card.left + 50, rect_card.top + 16, rect_card.width - 100, 34)
        dibujar_texto_en_rect(pantalla, "CAMBIAR ATUENDOS", rect_tit, categoria="dialogos", tamano=TAMANO_TITULO_MODAL, color=(60, 45, 35))

        # Subtítulo descriptivo con autoajuste para nombres extensos de partida
        sub_txt = f"Modificaste los personajes antes de continuar «{nombre_partida}»."
        rect_sub1 = pygame.Rect(rect_card.left + 30, rect_card.top + 54, rect_card.width - 60, 26)
        dibujar_texto_en_rect(pantalla, sub_txt, rect_sub1, categoria="subtitulo", tamano=16, color=(115, 95, 80), padding=2)

        rect_sub2 = pygame.Rect(rect_card.left + 30, rect_card.top + 82, rect_card.width - 60, 24)
        dibujar_texto_en_rect(pantalla, "¿Deseas mantener los atuendos guardados o aplicar los nuevos?", rect_sub2, categoria="subtitulo", tamano=15, color=(135, 110, 90), padding=2)

        # ----------------- CAJA IZQUIERDA: ATUENDOS GUARDADOS -----------------
        pygame.draw.rect(pantalla, (246, 238, 224), rect_box_izq, border_radius=12)
        pygame.draw.rect(pantalla, (215, 195, 175), rect_box_izq, width=2, border_radius=12)

        r_cab_izq = pygame.Rect(rect_box_izq.left + 10, rect_box_izq.top + 10, rect_box_izq.width - 20, 32)
        pygame.draw.rect(pantalla, (235, 223, 206), r_cab_izq, border_radius=8)
        dibujar_texto_en_rect(pantalla, "ATUENDOS GUARDADOS", r_cab_izq, categoria="boton", tamano=18, color=(90, 70, 55), padding=4)

        # P1 Guardado
        rgb_p1_g = COLORES_RGB_MAP.get(c_p1_g, (124, 231, 255))
        y_p1_g = rect_box_izq.top + 58
        pygame.draw.circle(pantalla, rgb_p1_g, (rect_box_izq.left + 38, y_p1_g + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_izq.left + 38, y_p1_g + 20), 17, 2)
        t_p1_nom_g = fuente_item.render(f"Jugador 1: {c_p1_g}", True, (55, 45, 35))
        pantalla.blit(t_p1_nom_g, (rect_box_izq.left + 66, y_p1_g + 6))
        acc_txt_p1_g = f"Accesorio: {a_p1_g}" if a_p1_g != "Ninguno" else "Sin accesorio"
        t_p1_acc_g = fuente_item_acc.render(acc_txt_p1_g, True, (120, 100, 85))
        pantalla.blit(t_p1_acc_g, (rect_box_izq.left + 66, y_p1_g + 26))

        # P2 Guardado
        rgb_p2_g = COLORES_RGB_MAP.get(c_p2_g, (161, 123, 255))
        y_p2_g = rect_box_izq.top + 126
        pygame.draw.circle(pantalla, rgb_p2_g, (rect_box_izq.left + 38, y_p2_g + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_izq.left + 38, y_p2_g + 20), 17, 2)
        t_p2_nom_g = fuente_item.render(f"Jugador 2: {c_p2_g}", True, (55, 45, 35))
        pantalla.blit(t_p2_nom_g, (rect_box_izq.left + 66, y_p2_g + 6))
        acc_txt_p2_g = f"Accesorio: {a_p2_g}" if a_p2_g != "Ninguno" else "Sin accesorio"
        t_p2_acc_g = fuente_item_acc.render(acc_txt_p2_g, True, (120, 100, 85))
        pantalla.blit(t_p2_acc_g, (rect_box_izq.left + 66, y_p2_g + 26))

        # ----------------- CAJA DERECHA: NUEVOS ATUENDOS -----------------
        pygame.draw.rect(pantalla, (255, 250, 242), rect_box_der, border_radius=12)
        pygame.draw.rect(pantalla, (230, 155, 85), rect_box_der, width=2, border_radius=12)

        r_cab_der = pygame.Rect(rect_box_der.left + 10, rect_box_der.top + 10, rect_box_der.width - 20, 32)
        pygame.draw.rect(pantalla, (255, 235, 215), r_cab_der, border_radius=8)
        dibujar_texto_en_rect(pantalla, "NUEVOS ATUENDOS", r_cab_der, categoria="boton", tamano=18, color=(205, 80, 35), padding=4)

        # P1 Nuevo
        rgb_p1_n = COLORES_RGB_MAP.get(color_p1_nuevo, (124, 231, 255))
        y_p1_n = rect_box_der.top + 58
        pygame.draw.circle(pantalla, rgb_p1_n, (rect_box_der.left + 38, y_p1_n + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_der.left + 38, y_p1_n + 20), 17, 2)
        t_p1_nom_n = fuente_item.render(f"Jugador 1: {color_p1_nuevo}", True, (55, 45, 35))
        pantalla.blit(t_p1_nom_n, (rect_box_der.left + 66, y_p1_n + 6))
        acc_txt_p1_n = f"Accesorio: {acc_p1_nuevo}" if acc_p1_nuevo != "Ninguno" else "Sin accesorio"
        t_p1_acc_n = fuente_item_acc.render(acc_txt_p1_n, True, (120, 100, 85))
        pantalla.blit(t_p1_acc_n, (rect_box_der.left + 66, y_p1_n + 26))

        # P2 Nuevo
        rgb_p2_n = COLORES_RGB_MAP.get(color_p2_nuevo, (161, 123, 255))
        y_p2_n = rect_box_der.top + 126
        pygame.draw.circle(pantalla, rgb_p2_n, (rect_box_der.left + 38, y_p2_n + 20), 17)
        pygame.draw.circle(pantalla, (70, 55, 45), (rect_box_der.left + 38, y_p2_n + 20), 17, 2)
        t_p2_nom_n = fuente_item.render(f"Jugador 2: {color_p2_nuevo}", True, (55, 45, 35))
        pantalla.blit(t_p2_nom_n, (rect_box_der.left + 66, y_p2_n + 6))
        acc_txt_p2_n = f"Accesorio: {acc_p2_nuevo}" if acc_p2_nuevo != "Ninguno" else "Sin accesorio"
        t_p2_acc_n = fuente_item_acc.render(acc_txt_p2_n, True, (120, 100, 85))
        pantalla.blit(t_p2_acc_n, (rect_box_der.left + 66, y_p2_n + 26))

        # ----------------- BOTÓN 1: MANTENER ATUENDOS GUARDADOS -----------------
        col_m = (255, 255, 255) if hov_mantener else (242, 234, 222)
        borde_m = (165, 135, 105) if hov_mantener else (185, 155, 125)
        pygame.draw.rect(pantalla, col_m, btn_mantener, border_radius=12)
        pygame.draw.rect(pantalla, borde_m, btn_mantener, width=2, border_radius=12)
        r_m1 = pygame.Rect(btn_mantener.left + 8, btn_mantener.top + 8, btn_mantener.width - 16, 24)
        dibujar_texto_en_rect(pantalla, "MANTENER GUARDADOS", r_m1, categoria="boton", tamano=18, color=(60, 45, 35), padding=2)
        r_m2 = pygame.Rect(btn_mantener.left + 8, btn_mantener.top + 34, btn_mantener.width - 16, 20)
        dibujar_texto_en_rect(pantalla, "Conservar atuendos guardados", r_m2, categoria="pequena", tamano=13, color=(125, 105, 90), padding=2)

        # ----------------- BOTÓN 2: CAMBIAR ATUENDOS -----------------
        col_c = (82, 194, 114) if hov_cambiar else (68, 172, 98)
        borde_c = (35, 115, 55) if hov_cambiar else (45, 130, 70)
        pygame.draw.rect(pantalla, col_c, btn_cambiar, border_radius=12)
        pygame.draw.rect(pantalla, borde_c, btn_cambiar, width=2, border_radius=12)
        r_c1 = pygame.Rect(btn_cambiar.left + 8, btn_cambiar.top + 8, btn_cambiar.width - 16, 24)
        dibujar_texto_en_rect(pantalla, "CAMBIAR ATUENDOS", r_c1, categoria="boton", tamano=18, color=(255, 255, 255), padding=2)
        r_c2 = pygame.Rect(btn_cambiar.left + 8, btn_cambiar.top + 34, btn_cambiar.width - 16, 20)
        dibujar_texto_en_rect(pantalla, "Aplicar y guardar los nuevos", r_c2, categoria="pequena", tamano=13, color=(235, 255, 240), padding=2)

        pygame.display.flip()

