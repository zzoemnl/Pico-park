import os
import sys
import copy
import datetime
import hashlib
import secrets
import pygame

from sprites import cargar_boton, animar_pulsacion_boton, aclarar_boton
from configuracion import t

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_PARTIDAS = os.path.join(DIRECTORIO_ACTUAL, "partidas.txt")


def _cargar_sprite_boton(nombre, w, h):
    """Carga y escala suavemente un botón oficial del proyecto con proporciones exactas."""
    img = cargar_boton(nombre)
    return pygame.transform.smoothscale(img, (w, h)) if img else None


from fuentes import (
    obtener_fuente,
    obtener_fuente_titulo,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_boton,
    obtener_fuente_pequena,
    cargar_fuente_pixel,
    TAMANO_TITULO,
    TAMANO_TITULO_MODAL,
    TAMANO_SUBTITULO,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO,
    TAMANO_TEXTO_GRANDE,
    TAMANO_INPUT,
    TAMANO_BOTON,
    TAMANO_BOTON_MODAL,
    TAMANO_PEQUENA,
    TAMANO_ITEM_TITULO,
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
            f.write("# Formato: ID|Nombre|MundoMax|NivelMax|Fecha|NivelesDesbloqueados|PasswordHash|PasswordSalt\n")
            for p in partidas:
                p_hash = p.get("password_hash", "")
                p_salt = p.get("password_salt", "")
                f.write(
                    f"{p['id']}|{p['nombre']}|{p['mundo_max']}|{p['nivel_max']}|"
                    f"{p['fecha']}|{encode_desbloqueados(p['niveles_desbloqueados'])}|{p_hash}|{p_salt}\n"
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


def guardar_partida(niveles_desbloqueados, id_partida=None, nombre_partida=None, password=None, password_hash=None, password_salt=None):
    """
    Guarda o actualiza una partida en partidas.txt.
    Si id_partida existe, la actualiza; si no, crea una nueva.
    Soporta opcionalmente contraseña (texto plano que se hashea con salt o hash precalculado).
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

    w_btn, h_btn = 180, 52
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

        # Título
        t_tit = fuente_titulo.render(titulo, True, (60, 45, 35))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 38)))

        # Subtítulo
        t_sub = fuente_sub.render(subtitulo, True, (115, 95, 80))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 78)))

        # Caja de texto
        pygame.draw.rect(pantalla, (255, 255, 255), rect_input, border_radius=8)
        pygame.draw.rect(pantalla, (175, 140, 105), rect_input, width=2, border_radius=8)

        # Renderizado del texto introducido
        texto_mostrar = texto if mostrar_caracteres else ("•" * len(texto))
        t_txt = fuente_input.render(texto_mostrar, True, (40, 30, 25))
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
            t_ojo = fuente_sub.render(simbolo_ojo, True, (60, 45, 35))
            pantalla.blit(t_ojo, t_ojo.get_rect(center=rect_ojo.center))

        # Mensaje de error
        if mensaje_error:
            t_err = fuente_sub.render(mensaje_error, True, (215, 50, 50))
            pantalla.blit(t_err, t_err.get_rect(center=(rect_card.centerx, rect_input.bottom + 18)))

        # Botón Cancelar (reutiliza el botón existente oficial de la carpeta de botones)
        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            t_can = fuente_btn.render("CANCELAR", True, (60, 45, 35))
            pantalla.blit(t_can, t_can.get_rect(center=btn_cancelar.center))

        # Botón Confirmar
        col_con = (82, 194, 114) if hov_con else (68, 172, 98)
        pygame.draw.rect(pantalla, col_con, btn_confirmar, border_radius=10)
        pygame.draw.rect(pantalla, (45, 130, 70), btn_confirmar, width=2, border_radius=10)
        t_con = fuente_btn.render("CONFIRMAR", True, (255, 255, 255))
        pantalla.blit(t_con, t_con.get_rect(center=btn_confirmar.center))

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
        fuente_tit = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=28)
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

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=30)
    fuente_sub = obtener_fuente_subtitulo(TAMANO_SUBTITULO)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=24)

    w_card, h_card = 560, 460
    rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)

    w_b, h_b = 360, 48
    x_b = rect_card.centerx - (w_b // 2)
    y_base = rect_card.top + 105
    gap_b = 14

    btn_renombrar = pygame.Rect(x_b, y_base, w_b, h_b)
    btn_password = pygame.Rect(x_b, y_base + (h_b + gap_b), w_b, h_b)
    btn_eliminar = pygame.Rect(x_b, y_base + (h_b + gap_b) * 2, w_b, h_b)

    # Botón «VOLVER» oficial reutilizado debajo de las opciones con generosa separación
    w_v, h_v = 210, 62
    x_v = rect_card.centerx - (w_v // 2)
    y_v = rect_card.top + 312
    btn_volver = pygame.Rect(x_v, y_v, w_v, h_v)

    spr_vol_norm = _cargar_sprite_boton("mundos/boton-volver.png", w_v, h_v) or _cargar_sprite_boton("Menu/boton-volver.png", w_v, h_v) or _cargar_sprite_boton("boton-volver.png", w_v, h_v)
    spr_vol_semi = _cargar_sprite_boton("mundos/boton-volver-semiapretado.png", w_v, h_v) or _cargar_sprite_boton("Menu/boton-volver-semiapretado.png", w_v, h_v) or _cargar_sprite_boton("boton-volver-semiapretado.png", w_v, h_v)
    spr_vol_apret = _cargar_sprite_boton("mundos/boton-volver-apretado.png", w_v, h_v) or _cargar_sprite_boton("Menu/boton-volver-apretado.png", w_v, h_v) or _cargar_sprite_boton("boton-volver-apretado.png", w_v, h_v)
    spr_vol_hover = aclarar_boton(spr_vol_norm) if spr_vol_norm else None
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
        hov_vol = btn_volver.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                return hubo_cambios

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_renombrar.collidepoint(evento.pos):
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

                elif btn_eliminar.collidepoint(evento.pos):
                    if mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
                        eliminar_partida(partida["id"])
                        return True

                elif btn_volver.collidepoint(evento.pos):
                    pulsado = True
                    if spr_vol_semi and spr_vol_apret:
                        pulsado = animar_pulsacion_boton(pantalla, btn_volver, spr_vol_semi, spr_vol_apret, fondo_tarjeta, spr_vol_norm)
                    if pulsado:
                        return hubo_cambios

        # Dibujar modal
        pantalla.blit(captura_previa, (0, 0))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
        pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)

        t_tit = fuente_titulo.render("ADMINISTRAR PERFIL", True, (60, 45, 35))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 38)))

        txt_p = f"Perfil: {partida.get('nombre', '')}  •  " + ("🔒 Protegido" if partida.get("tiene_password") else "🔓 Sin contraseña")
        t_sub = fuente_sub.render(txt_p, True, (115, 95, 80))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 72)))

        # 1. Renombrar
        col_ren = (255, 255, 255) if hov_ren else (245, 238, 226)
        pygame.draw.rect(pantalla, col_ren, btn_renombrar, border_radius=10)
        pygame.draw.rect(pantalla, (185, 155, 125), btn_renombrar, width=2, border_radius=10)
        t_ren = fuente_btn.render("CAMBIAR NOMBRE", True, (60, 45, 35))
        pantalla.blit(t_ren, t_ren.get_rect(center=btn_renombrar.center))

        # 2. Contraseña
        txt_btn_pwd = "CAMBIAR / QUITAR CONTRASEÑA" if partida.get("tiene_password") else "AGREGAR CONTRASEÑA"
        col_pwd = (255, 255, 255) if hov_pwd else (245, 238, 226)
        pygame.draw.rect(pantalla, col_pwd, btn_password, border_radius=10)
        pygame.draw.rect(pantalla, (185, 155, 125), btn_password, width=2, border_radius=10)
        t_pw = fuente_btn.render(txt_btn_pwd, True, (60, 45, 35))
        pantalla.blit(t_pw, t_pw.get_rect(center=btn_password.center))

        # 3. Eliminar
        col_eli = (235, 95, 90) if hov_eli else (215, 80, 75)
        pygame.draw.rect(pantalla, col_eli, btn_eliminar, border_radius=10)
        pygame.draw.rect(pantalla, (170, 50, 45), btn_eliminar, width=2, border_radius=10)
        t_el = fuente_btn.render("ELIMINAR PERFIL", True, (255, 255, 255))
        pantalla.blit(t_el, t_el.get_rect(center=btn_eliminar.center))

        # 4. Botón «VOLVER» oficial reutilizado debajo de las opciones con generosa separación
        if spr_vol_norm:
            pantalla.blit(spr_vol_hover if (hov_vol and spr_vol_hover) else spr_vol_norm, btn_volver)
        else:
            col_vol = (255, 255, 255) if hov_vol else (242, 234, 222)
            pygame.draw.rect(pantalla, col_vol, btn_volver, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_volver, width=2, border_radius=10)
            t_v = fuente_btn.render("VOLVER", True, (60, 45, 35))
            pantalla.blit(t_v, t_v.get_rect(center=btn_volver.center))

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

    w_btn, h_btn = 160, 48
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

        t_tit = fuente_titulo.render("PARTIDA EXISTENTE", True, (205, 80, 40))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 36)))

        t_msg = fuente_sub.render(f"Ya existe una partida guardada con el nombre «{nombre}».", True, (60, 45, 35))
        pantalla.blit(t_msg, t_msg.get_rect(center=(rect_card.centerx, rect_card.top + 80)))

        t_sub = fuente_sub.render("¿Deseas elegir otro nombre o sobrescribir la partida existente?", True, (115, 95, 80))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 112)))

        # Botón 1: Cambiar nombre
        col_cam = (255, 255, 255) if hov_cam else (242, 234, 222)
        pygame.draw.rect(pantalla, col_cam, btn_cambiar, border_radius=10)
        pygame.draw.rect(pantalla, (185, 155, 125), btn_cambiar, width=2, border_radius=10)
        t_c = fuente_btn.render("OTRO NOMBRE", True, (60, 45, 35))
        pantalla.blit(t_c, t_c.get_rect(center=btn_cambiar.center))

        # Botón 2: Sobrescribir
        col_sob = (235, 95, 90) if hov_sob else (215, 80, 75)
        pygame.draw.rect(pantalla, col_sob, btn_sobrescribir, border_radius=10)
        pygame.draw.rect(pantalla, (170, 50, 45), btn_sobrescribir, width=2, border_radius=10)
        t_s = fuente_btn.render("SOBRESCRIBIR", True, (255, 255, 255))
        pantalla.blit(t_s, t_s.get_rect(center=btn_sobrescribir.center))

        # Botón 3: Cancelar (reutiliza el botón oficial del proyecto)
        if spr_canc_norm:
            pantalla.blit(spr_canc_hover if (hov_can and spr_canc_hover) else spr_canc_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=10)
            pygame.draw.rect(pantalla, (185, 155, 125), btn_cancelar, width=2, border_radius=10)
            t_can = fuente_btn.render("CANCELAR", True, (60, 45, 35))
            pantalla.blit(t_can, t_can.get_rect(center=btn_cancelar.center))

        pygame.display.flip()


def flujo_crear_nueva_partida(pantalla, reloj):
    """
    Permite crear una partida independiente:
    - Pide un nombre para identificarla.
    - Si ya existe una con ese nombre, pide confirmación o solicita otro nombre (nunca sobrescribe silenciosamente).
    - Permite establecer una contraseña opcional.
    - Crea un progreso nuevo en memoria como provisional (no escribe a disco hasta confirmar «GUARDAR Y SALIR»).
    - Si se cancela en cualquier paso, retorna None y no persiste ningún cambio.
    - Retorna el diccionario de la nueva partida provisional, o None si se canceló.
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
    )
    if partida_creada is None:
        return None
    partida_creada["password_plain"] = pwd or ""
    return partida_creada



def modal_flujo_guardar_perfil(pantalla, reloj, niveles_desbloqueados, id_partida_actual=None, nombre_partida_actual=None, password_partida_actual=None):
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
    fuente_pag = obtener_fuente_pequena(TAMANO_SUBTITULO)

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


def mostrar_dialogo_guardar_salir(pantalla, reloj, niveles_desbloqueados, id_partida=None, nombre_partida=None, password_partida=None):
    """
    Muestra la confirmación clara obligatoria con las tres opciones:
    1. «GUARDAR Y SALIR»: abre el procedimiento para guardar y cierra solo si finalizó con éxito.
    2. «SALIR SIN GUARDAR»: cierra el juego sin persistir los cambios pendientes ni alterar guardados.
    3. «CANCELAR»: cierra el diálogo y vuelve exactamente a la pantalla en que estaba el jugador.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    mundo_max, nivel_max = obtener_maximo_alcanzado(niveles_desbloqueados)

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=36)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO_GRANDE)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=28)

    ancho_card, alto_card = 560, 480
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 260, 72
    x_btn = rect_card.centerx - (w_btn // 2)
    y_base_btns = rect_card.top + 145
    espacio_btns = 16

    btn_guardar = pygame.Rect(x_btn, y_base_btns, w_btn, h_btn)
    btn_no_guardar = pygame.Rect(x_btn, y_base_btns + h_btn + espacio_btns, w_btn, h_btn)
    btn_cancelar = pygame.Rect(x_btn, y_base_btns + (h_btn + espacio_btns) * 2, w_btn, h_btn)

    def _scale(img, w, h):
        return pygame.transform.smoothscale(img, (w, h)) if img else None

    # Sprites oficiales reutilizados con animación
    spr_g_norm = _scale(cargar_boton("Ventanas/boton-guardar-y-salir.png") or cargar_boton("boton-guardar-y-salir.png"), w_btn, h_btn)
    spr_g_semi = _scale(cargar_boton("Ventanas/boton-guardar-y-salir-semiapretado.png") or cargar_boton("boton-guardar-y-salir-semiapretado.png"), w_btn, h_btn)
    spr_g_apret = _scale(cargar_boton("Ventanas/boton-guardar-y-salir-apretado.png") or cargar_boton("boton-guardar-y-salir-apretado.png"), w_btn, h_btn)

    spr_s_norm = _scale(cargar_boton("Ventanas/boton-salir-sin-guardar.png") or cargar_boton("Menu/boton-salir-sin-guardar.png") or cargar_boton("boton-salir-sin-guardar.png"), w_btn, h_btn)
    spr_s_semi = _scale(cargar_boton("Menu/boton-salir-sin-guardar-semiapretado.png") or cargar_boton("boton-salir-sin-guardar-semiapretado.png"), w_btn, h_btn)
    spr_s_apret = _scale(cargar_boton("Ventanas/boton-salir-sin-guardar-apretado.png") or cargar_boton("Menu/boton-salir-sin-guardar-apretado.png") or cargar_boton("boton-salir-sin-guardar-apretado.png"), w_btn, h_btn)

    spr_c_norm = _scale(cargar_boton("Menu/boton-cancelar.png") or cargar_boton("boton-cancelar.png"), w_btn, h_btn)
    spr_c_semi = _scale(cargar_boton("Menu/boton-cancelar-semiapretado.png") or cargar_boton("boton-cancelar-semiapretado.png"), w_btn, h_btn)
    spr_c_apret = _scale(cargar_boton("Menu/boton-cancelar-apretado.png") or cargar_boton("boton-cancelar-apretado.png"), w_btn, h_btn)

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

        t_tit = fuente_titulo.render(t("deseas_guardar"), True, (60, 45, 35))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 40)))

        t_info = fuente_texto.render(f"{t('mundo')} {mundo_max} - {t('nivel')} {nivel_max}", True, (55, 45, 35))
        pantalla.blit(t_info, t_info.get_rect(center=(rect_card.centerx, rect_card.top + 80)))

        t_sub = fuente_texto.render(t("deseas_guardar_sub", default="Puedes guardar tu partida en un perfil antes de salir."), True, (120, 105, 90))
        pantalla.blit(t_sub, t_sub.get_rect(center=(rect_card.centerx, rect_card.top + 112)))

        if spr_g_norm:
            pantalla.blit(spr_g_hover if (hov_g and spr_g_hover) else spr_g_norm, btn_guardar)
        else:
            pygame.draw.rect(pantalla, (82, 194, 114) if hov_g else (68, 172, 98), btn_guardar, border_radius=12)
            t_g = fuente_btn.render(t("guardar_salir"), True, (255, 255, 255))
            pantalla.blit(t_g, t_g.get_rect(center=btn_guardar.center))

        if spr_s_norm:
            pantalla.blit(spr_s_hover if (hov_s and spr_s_hover) else spr_s_norm, btn_no_guardar)
        else:
            pygame.draw.rect(pantalla, (235, 95, 90) if hov_s else (215, 80, 75), btn_no_guardar, border_radius=12)
            t_s = fuente_btn.render(t("salir_sin_guardar"), True, (255, 255, 255))
            pantalla.blit(t_s, t_s.get_rect(center=btn_no_guardar.center))

        if spr_c_norm:
            pantalla.blit(spr_c_hover if (hov_c and spr_c_hover) else spr_c_norm, btn_cancelar)
        else:
            pygame.draw.rect(pantalla, (255, 255, 255) if hov_c else (242, 234, 222), btn_cancelar, border_radius=12)
            t_c = fuente_btn.render(t("cancelar"), True, (60, 45, 35))
            pantalla.blit(t_c, t_c.get_rect(center=btn_cancelar.center))

        pygame.display.flip()


def mostrar_dialogo_confirmar_borrado(pantalla, reloj, partida):
    """
    Muestra un diálogo modal interactivo con estética pastel crema solicitando confirmación para borrar una partida.
    Advierte que se eliminará permanentemente la partida guardada correspondiente.
    Retorna True si se confirma («BORRAR PARTIDA»), o False si se cancela.
    """
    ancho = pantalla.get_width()
    alto = pantalla.get_height()

    fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=34)
    fuente_nombre = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
    fuente_texto = obtener_fuente_texto(TAMANO_TEXTO)
    fuente_btn = obtener_fuente_boton(TAMANO_BOTON_MODAL, tamano_fallback=24)

    ancho_card, alto_card = 560, 310
    rect_card = pygame.Rect((ancho - ancho_card) // 2, (alto - alto_card) // 2, ancho_card, alto_card)

    w_btn, h_btn = 205, 54
    gap_btn = 22
    total_w_btns = (w_btn * 2) + gap_btn
    x_cancelar = rect_card.centerx - (total_w_btns // 2)
    x_borrar = x_cancelar + w_btn + gap_btn
    y_btns = rect_card.bottom - 74

    btn_cancelar = pygame.Rect(x_cancelar, y_btns, w_btn, h_btn)
    btn_borrar = pygame.Rect(x_borrar, y_btns, w_btn, h_btn)

    def _scale(img, w, h):
        return pygame.transform.smoothscale(img, (w, h)) if img else None

    spr_can_norm = _scale(cargar_boton("Menu/boton-cancelar.png") or cargar_boton("boton-cancelar.png"), w_btn, h_btn)
    spr_can_semi = _scale(cargar_boton("Menu/boton-cancelar-semiapretado.png") or cargar_boton("boton-cancelar-semiapretado.png"), w_btn, h_btn)
    spr_can_apret = _scale(cargar_boton("Menu/boton-cancelar-apretado.png") or cargar_boton("boton-cancelar-apretado.png"), w_btn, h_btn)
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

        t_tit = fuente_titulo.render("ELIMINAR PERFIL", True, (205, 70, 60))
        pantalla.blit(t_tit, t_tit.get_rect(center=(rect_card.centerx, rect_card.top + 38)))

        t_nom = fuente_nombre.render(f"«{nombre}»  —  Nivel: {mundo_max}-{nivel_max}", True, (60, 45, 35))
        pantalla.blit(t_nom, t_nom.get_rect(center=(rect_card.centerx, rect_card.top + 82)))

        t_preg = fuente_texto.render("¿Seguro que deseas eliminar este perfil y su partida?", True, (80, 65, 55))
        pantalla.blit(t_preg, t_preg.get_rect(center=(rect_card.centerx, rect_card.top + 126)))

        t_aviso = fuente_texto.render("Se borrará todo su progreso y no se podrá recuperar.", True, (195, 75, 65))
        pantalla.blit(t_aviso, t_aviso.get_rect(center=(rect_card.centerx, rect_card.top + 158)))

        if spr_can_norm:
            pantalla.blit(spr_can_hover if (hov_can and spr_can_hover) else spr_can_norm, btn_cancelar)
        else:
            col_can = (255, 255, 255) if hov_can else (242, 234, 222)
            pygame.draw.rect(pantalla, col_can, btn_cancelar, border_radius=12)
            pygame.draw.rect(pantalla, (195, 168, 138), btn_cancelar, width=2, border_radius=12)
            t_btn_can = fuente_btn.render("CANCELAR", True, (60, 45, 35))
            pantalla.blit(t_btn_can, t_btn_can.get_rect(center=btn_cancelar.center))

        col_bor = (235, 95, 90) if hov_bor else (215, 80, 75)
        pygame.draw.rect(pantalla, col_bor, btn_borrar, border_radius=12)
        pygame.draw.rect(pantalla, (170, 50, 45), btn_borrar, width=2, border_radius=12)
        t_btn_bor = fuente_btn.render("BORRAR PERFIL", True, (255, 255, 255))
        pantalla.blit(t_btn_bor, t_btn_bor.get_rect(center=btn_borrar.center))

        pygame.display.flip()
