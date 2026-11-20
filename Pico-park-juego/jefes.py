"""
Punto de entrada común para los jefes de cada mundo.

pantalla.py solo habla con este módulo; cada jefe vive en su propio archivo con la
misma interfaz (crear_jefe, reiniciar_jefe, actualizar_jefe, dibujar_jefe,
dibujar_proyectiles y la constante CLAVE_PISTA con el texto de ayuda).
"""
import pygame

import jefe_nieve
import jefe_ruinas
import jefe_kraken

MODULOS = {
    "nieve": jefe_nieve,     # 1-6
    "ruinas": jefe_ruinas,   # 2-6
    "kraken": jefe_kraken,   # 3-6
}
MUSICA = {"nieve": "jefe1", "ruinas": "jefe1", "kraken": "jefe final"}
FRAMES_PISTA = 420   # la pista se muestra los primeros 7 s, hasta el primer golpe


def crear_jefe(tipo, suelo, ancho_mundo):
    jefe = MODULOS[tipo].crear_jefe(suelo, ancho_mundo)
    jefe["tipo"] = tipo
    return jefe


def crear_botones_jefe(suelo, fase=0):
    return jefe_nieve.crear_botones_jefe(suelo, fase)


def reiniciar_jefe(jefe, botones_colores, suelo):
    MODULOS[jefe["tipo"]].reiniciar_jefe(jefe, botones_colores, suelo)


def actualizar_jefe(jefe, botones_colores, jugadores, suelo, plataformas):
    return MODULOS[jefe["tipo"]].actualizar_jefe(jefe, botones_colores, jugadores, suelo, plataformas)


def dibujar_jefe(surf, jefe, suelo):
    MODULOS[jefe["tipo"]].dibujar_jefe(surf, jefe, suelo)


def dibujar_proyectiles(surf, jefe):
    MODULOS[jefe["tipo"]].dibujar_proyectiles(surf, jefe)


def dibujar_pista_jefe(surf, jefe, ancho_mundo):
    """Cartel con la instrucción del jefe, traducido, centrado en la parte alta de la pantalla."""
    if jefe["derrotado"] or jefe["fase"] > 0 or jefe["tick"] > FRAMES_PISTA:
        return
    from configuracion import t
    from fuentes import obtener_fuente_para_texto
    texto = t(MODULOS[jefe["tipo"]].CLAVE_PISTA)
    fuente = obtener_fuente_para_texto(texto, categoria="texto", tamano=26, tamano_fallback=26)
    render = fuente.render(texto, True, (255, 255, 255))
    alpha = 255 if jefe["tick"] < FRAMES_PISTA - 60 else int(255 * (FRAMES_PISTA - jefe["tick"]) / 60)
    render.set_alpha(alpha)
    caja = render.get_rect(center=(ancho_mundo // 2, 440)).inflate(28, 16)
    fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
    pygame.draw.rect(fondo, (30, 40, 70, int(alpha * 0.8)), fondo.get_rect(), border_radius=10)
    surf.blit(fondo, caja.topleft)
    surf.blit(render, render.get_rect(center=caja.center))
