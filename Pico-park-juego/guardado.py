"""
Partidas guardadas (partidas.txt): formato, lectura y escritura atómica, contraseñas, progreso y niveles desbloqueados.
Los diálogos de interfaz que usan estos datos están en menus/dialogos.py.
"""
import copy
import datetime
import hashlib
import os
import re
import secrets
from configuracion import t
from errores import registrar_error
from rutas import ruta_datos



DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))


RUTA_PARTIDAS = ruta_datos("partidas.txt")


def obtener_nombre_partida_visible(partida_o_nombre, id_partida=None):
    """
    Retorna el nombre visible de una partida respetando el idioma actual.
    Si la partida tiene un nombre automático («Partida X», «Game X», «游戏 X», «存档 X»),
    adapta el prefijo automáticamente al idioma seleccionado conservando su número.
    También traduce el perfil especial «Todos los niveles desbloqueados».
    """
    if isinstance(partida_o_nombre, dict):
        nombre = str(partida_o_nombre.get("nombre", "")).strip()
        pid = partida_o_nombre.get("id", id_partida or 1)
    else:
        nombre = str(partida_o_nombre or "").strip()
        pid = id_partida or 1

    if not nombre:
        return f"{t('partida')} {pid}"

    if nombre in ("Todos los niveles desbloqueados", "All levels unlocked", "所有关卡已解锁"):
        return t("todos_desbloqueados")

    m = re.match(r"^(?:Partida|Game|游戏|存档)\s+(\d+)$", nombre, re.IGNORECASE)
    if m:
        num = m.group(1)
        return f"{t('partida')} {num}"

    return nombre


# Cantidad de niveles de cada mundo (5 niveles por mundo).
NIVELES_POR_MUNDO = {1: 5, 2: 5, 3: 5}


TOTAL_NIVELES_NORMALES = sum(NIVELES_POR_MUNDO.values())  # 15


TOTAL_NIVELES_ADMIN = TOTAL_NIVELES_NORMALES


TOTAL_NIVELES = TOTAL_NIVELES_NORMALES


def es_partida_admin(partida_o_nombre, id_partida=None):
    """Determina si una partida dada es la partida especial de administrador."""
    if isinstance(partida_o_nombre, dict):
        if partida_o_nombre.get("es_admin", False):
            return True
        nom = partida_o_nombre.get("nombre", "")
    else:
        nom = str(partida_o_nombre or "")
    nom_clean = nom.strip().lower()
    return nom_clean in ("admin", "administrador", "administrator", "partida admin", "admin profile")


def crear_desbloqueados_inicial(es_admin=False):
    """
    Retorna la estructura inicial de niveles desbloqueados:
    - Para partida de administrador: todos los niveles desbloqueados (1-1 a 3-5).
    - Para partidas normales: primer nivel desbloqueado de cada mundo (1-1, 2-1, 3-1),
      respetando el sistema de progresión del juego.
    """
    if es_admin:
        return {m: [True] * n for m, n in NIVELES_POR_MUNDO.items()}
    return {m: [i == 0 for i in range(n)] for m, n in NIVELES_POR_MUNDO.items()}


def encode_desbloqueados(d):
    """Convierte el diccionario de niveles desbloqueados en una cadena compacta."""
    partes = []
    for m in sorted(d.keys()):
        bits = "".join("1" if x else "0" for x in d[m])
        partes.append(f"{m}:{bits}")
    return ",".join(partes)


def decode_desbloqueados(s, es_admin=False):
    """Convierte la cadena guardada de nuevo a diccionario de booleanos."""
    if es_admin:
        return {m: [True] * n for m, n in NIVELES_POR_MUNDO.items()}
    res = crear_desbloqueados_inicial(es_admin=False)
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
    # Compatibilidad con partidas guardadas antes de agregar niveles a un mundo:
    for m, cantidad in NIVELES_POR_MUNDO.items():
        bits = res.get(m, [])[:cantidad]
        if len(bits) < cantidad:
            mundo_terminado = bool(bits) and all(bits)
            if m + 1 in NIVELES_POR_MUNDO:
                mundo_terminado = mundo_terminado and bool(res.get(m + 1, [False])[0])
            bits += [mundo_terminado] * (cantidad - len(bits))
        # Asegurar que el primer nivel de cada mundo esté siempre desbloqueado
        if bits:
            bits[0] = True
        res[m] = bits
    return res


def obtener_maximo_alcanzado(niveles_desbloqueados, es_admin=False):
    """
    Retorna (mundo_max, nivel_max) indicando el nivel más alto alcanzado/desbloqueado:
    - En partida admin: retorna (3, 5).
    - En partidas normales: como 1-1, 2-1 y 3-1 inician desbloqueados, busca el mundo más alto
      con progreso efectivo (nivel > 1). Si aún no hay progreso en ningún mundo, retorna (1, 1).
    """
    if not niveles_desbloqueados:
        return 1, 1
    if es_admin:
        return 3, 5

    for m in (3, 2, 1):
        bits = niveles_desbloqueados.get(m, [])
        # Niveles normales son índices 0 a 4 (niveles 1 a 5)
        for idx in range(min(5, len(bits)) - 1, 0, -1):
            if bits[idx]:
                return m, idx + 1

    return 1, 1


def calcular_niveles_completados(niveles_desbloqueados, es_admin=False):
    """
    Calcula la cantidad real de niveles completados.
    Cada mundo tiene 5 niveles jugables. Total: 15 niveles.
    """
    if not niveles_desbloqueados:
        return 0
    if es_admin:
        return TOTAL_NIVELES_ADMIN
    total_completados = 0
    for m in (1, 2, 3):
        bits = niveles_desbloqueados.get(m, [])
        for idx in range(1, min(6, len(bits))):
            if bits[idx]:
                total_completados += 1
    return max(0, min(TOTAL_NIVELES_NORMALES, total_completados))


def obtener_ultimo_nivel_completado(niveles_desbloqueados, es_admin=False):
    """
    Retorna (mundo, nivel) del último nivel completado, o None si no se ha completado ninguno.
    """
    if not niveles_desbloqueados:
        return None
    completados = calcular_niveles_completados(niveles_desbloqueados, es_admin=es_admin)
    if completados == 0:
        return None
    restantes = completados
    for m in (1, 2, 3):
        if restantes <= 5:
            return m, restantes
        restantes -= 5
    return 3, 5


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
                        nom = partes[1]
                        es_adm = es_partida_admin(nom)
                        desbloq = {m: [True] * n for m, n in NIVELES_POR_MUNDO.items()} if es_adm else decode_desbloqueados(partes[5], es_admin=False)
                        p = {
                            "id": int(partes[0]),
                            "nombre": nom,
                            "mundo_max": 3 if es_adm else int(partes[2]),
                            "nivel_max": 5 if es_adm else int(partes[3]),
                            "fecha": partes[4],
                            "niveles_desbloqueados": desbloq,
                            "password_hash": pwd_hash,
                            "password_salt": pwd_salt,
                            "tiene_password": bool(pwd_hash and pwd_salt),
                            "color_p1": c_p1,
                            "color_p2": c_p2,
                            "accesorio_p1": a_p1,
                            "accesorio_p2": a_p2,
                            "es_admin": es_adm,
                        }
                        partidas.append(p)
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        registrar_error(f"Error al leer partidas.txt: {e!r}")
        return []

    # Asegurar que siempre exista la partida especial del administrador
    if not any(es_partida_admin(p) for p in partidas):
        admin_id = max([p["id"] for p in partidas], default=0) + 1
        admin_p = {
            "id": admin_id,
            "nombre": "Administrador",
            "mundo_max": 3,
            "nivel_max": 5,
            "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "niveles_desbloqueados": {m: [True] * n for m, n in NIVELES_POR_MUNDO.items()},
            "password_hash": "",
            "password_salt": "",
            "tiene_password": False,
            "color_p1": "Celeste",
            "color_p2": "Violeta",
            "accesorio_p1": "Ninguno",
            "accesorio_p2": "Ninguno",
            "es_admin": True,
        }
        partidas.append(admin_p)
        guardar_partidas_seguras(partidas)

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
        registrar_error(f"Error crítico al guardar partidas.txt: {e!r}")
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
    fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    partida_encontrada = None
    if id_partida is not None:
        for p in partidas:
            if p["id"] == id_partida:
                partida_encontrada = p
                break

    nom_eval = (nombre_partida or (partida_encontrada.get("nombre") if partida_encontrada else "")).strip()
    es_adm = es_partida_admin(nom_eval) or (partida_encontrada and es_partida_admin(partida_encontrada))
    if es_adm:
        mundo_max, nivel_max = 3, 5
        desbloq_guardar = {m: [True] * n for m, n in NIVELES_POR_MUNDO.items()}
    else:
        desbloq_guardar = copy.deepcopy(niveles_desbloqueados)
        mundo_max, nivel_max = obtener_maximo_alcanzado(desbloq_guardar, es_admin=False)

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
        partida_encontrada["niveles_desbloqueados"] = copy.deepcopy(desbloq_guardar)
        partida_encontrada["es_admin"] = es_adm
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
        nuevo_nombre = nombre_partida.replace("|", "-").strip() if nombre_partida else f"{t('partida')} {nuevo_id}"
        nueva = {
            "id": nuevo_id,
            "nombre": nuevo_nombre,
            "mundo_max": mundo_max,
            "nivel_max": nivel_max,
            "fecha": fecha_actual,
            "niveles_desbloqueados": copy.deepcopy(desbloq_guardar),
            "es_admin": es_adm,
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
    Conserva intactas las demás partidas. La partida del Administrador está protegida.
    Retorna True si fue eliminada con éxito, o False en caso contrario.
    """
    partidas = cargar_partidas()
    for p in partidas:
        if p.get("id") == id_partida and es_partida_admin(p):
            return False
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
