"""
Resolución de rutas compatible con desarrollo y con el ejecutable de PyInstaller.

- directorio_base(): raíz de recursos de solo lectura (Sprites, sonidos, assets).
  En desarrollo es la carpeta padre del código; en el .exe es sys._MEIPASS.
- directorio_datos(): carpeta donde se escriben archivos del usuario
  (partidas.txt, configuracion.json). En el .exe queda al lado del ejecutable
  para que las partidas persistan y no se pierdan al reempaquetar.
"""
import os
import sys

_CONGELADO = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def directorio_base():
    if _CONGELADO:
        return os.path.abspath(sys._MEIPASS)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def directorio_datos():
    if _CONGELADO:
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def ruta_recurso(*partes):
    return os.path.join(directorio_base(), *partes)


def ruta_datos(*partes):
    return os.path.join(directorio_datos(), *partes)
