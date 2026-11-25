"""
Registro de errores no controlados.

El ejecutable se genera en modo --windowed (sin consola), así que si el juego
falla se cierra sin mostrar nada. Este módulo escribe el traceback en
errores.log al lado del .exe (o del código, en desarrollo) y, en Windows,
muestra un aviso para que el usuario sepa qué archivo enviar.
"""
import datetime
import os
import sys
import traceback

from rutas import ruta_datos

RUTA_LOG = ruta_datos("errores.log")


def registrar_excepcion(exc_type, exc_value, exc_tb):
    texto = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    marca = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(RUTA_LOG, "a", encoding="utf-8") as f:
            f.write(f"===== {marca} =====\n{texto}\n")
    except OSError:
        pass
    # En desarrollo también va a la consola, como siempre.
    sys.stderr.write(texto)


def registrar_error(mensaje):
    """Anota un error recuperable (sin cerrar el juego) en errores.log y en la consola."""
    marca = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(RUTA_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{marca}] {mensaje}\n")
    except OSError:
        pass
    sys.stderr.write(f"{mensaje}\n")


def mostrar_aviso():
    """Cuadro de diálogo nativo de Windows; en otros sistemas no hace nada."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        # Cerrar pygame primero: si no, la ventana en pantalla completa tapa el aviso.
        try:
            import pygame
            pygame.quit()
        except Exception:
            pass
        mensaje = (
            "Pico Park tuvo un error inesperado y se va a cerrar.\n\n"
            f"Los detalles quedaron en:\n{RUTA_LOG}\n\n"
            "Enviá ese archivo a los autores para que puedan corregirlo."
        )
        ctypes.windll.user32.MessageBoxW(None, mensaje, "Pico Park - Error", 0x10)  # MB_ICONERROR
    except Exception:
        pass


def ejecutar_protegido(funcion):
    """Ejecuta la función principal del juego registrando cualquier error no controlado."""
    try:
        funcion()
    except SystemExit:
        raise
    except Exception:
        registrar_excepcion(*sys.exc_info())
        mostrar_aviso()
        sys.exit(1)
