import sys
import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import movimientos
import pantalla

def generar_previews_salida():
    ancho_mundo = 2600
    alto = 720
    pygame.display.set_mode((1000, 720))
    mundo = pygame.Surface((ancho_mundo, alto)).convert()
    suelo = pygame.Rect(0, alto - 75, ancho_mundo, 75)
    techo_agua = pygame.Rect(0, 0, ancho_mundo, 25)

    camaras_aire = [
        {"rect": pygame.Rect(60, 60, 180, 200), "nombre": "Cámara 1: Inicio"},
        {"rect": pygame.Rect(890, 60, 180, 200), "nombre": "Cámara 2: Geiser"},
        {"rect": pygame.Rect(1440, 420, 190, 225), "nombre": "Cámara 3: Fosa de la Llave"},
        {"rect": pygame.Rect(2020, 60, 190, 210), "nombre": "Cámara 4: Refugio Final"},
    ]

    corrientes_marinas = [
        {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
        {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
        {"rect": pygame.Rect(1140, 140, 260, 380), "fuerza_x": 1.4, "fuerza_y": 2.4, "direccion": "abajo"},
        {"rect": pygame.Rect(1620, 360, 360, 280), "fuerza_x": -2.6, "fuerza_y": 0.0, "direccion": "izquierda"},
        {"rect": pygame.Rect(2180, 220, 240, 320), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
    ]

    rocas_submarinas = [
        {"rect": pygame.Rect(260, techo_agua.bottom, 90, 260)},
        {"rect": pygame.Rect(260, 560, 90, suelo.top - 560)},
        {"rect": pygame.Rect(460, techo_agua.bottom, 180, 180)},
        {"rect": pygame.Rect(480, 560, 220, suelo.top - 560)},
        {"rect": pygame.Rect(720, 280, 70, suelo.top - 280)},
        {"rect": pygame.Rect(890, 250, 150, 260)},
        {"rect": pygame.Rect(1040, techo_agua.bottom, 120, 280)},
        {"rect": pygame.Rect(1180, 520, 220, suelo.top - 520)},
        {"rect": pygame.Rect(1400, techo_agua.bottom, 220, 260)},
        {"rect": pygame.Rect(1640, techo_agua.bottom, 240, 230)},
        {"rect": pygame.Rect(1640, 480, 140, suelo.top - 480)},
        {"rect": pygame.Rect(1780, 590, 110, suelo.top - 590), "coral": True, "color_coral": (255, 135, 70)},
        {"rect": pygame.Rect(1980, 270, 110, suelo.top - 270)},
        {"rect": pygame.Rect(2210, techo_agua.bottom, 180, 170)},
        {"rect": pygame.Rect(2210, 540, 180, suelo.top - 540)},
        {"rect": pygame.Rect(2390, 440, 210, suelo.top - 440), "coral": True, "color_coral": (255, 140, 80)},
    ]

    pinchos = [
        movimientos.crear_pincho(350, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(780, techo_agua.bottom, 110, 24, direccion="abajo"),
        movimientos.crear_pincho(950, suelo.top - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(1200, 520 - 24, 140, 24, direccion="arriba"),
        movimientos.crear_pincho(1640, 480 - 24, 100, 24, direccion="arriba"),
        movimientos.crear_pincho(1890, suelo.top - 24, 90, 24, direccion="arriba"),
        movimientos.crear_pincho(2180, 540 - 24, 120, 24, direccion="arriba"),
        movimientos.crear_pincho(2210, techo_agua.bottom + 170, 100, 24, direccion="abajo"),
    ]

    flechas_indicadoras = [
        {"x": 200, "y": 320, "direccion": "derecha", "tipo": "ruta"},
        {"x": 540, "y": 380, "direccion": "derecha", "tipo": "ruta"},
        {"x": 810, "y": 480, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 820, "y": 240, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 850, "y": 200, "direccion": "abajo", "tipo": "ruta"},
        {"x": 850, "y": 520, "direccion": "derecha", "tipo": "ruta"},
        {"x": 1110, "y": 350, "direccion": "abajo", "tipo": "ruta"},
        {"x": 1360, "y": 480, "direccion": "derecha", "tipo": "oxigeno"},
        {"x": 1660, "y": 430, "direccion": "derecha", "tipo": "llave"},
        {"x": 1810, "y": 500, "direccion": "abajo", "tipo": "llave"},
        {"x": 1910, "y": 500, "direccion": "arriba", "tipo": "oxigeno"},
        {"x": 1940, "y": 230, "direccion": "derecha", "tipo": "oxigeno"},
        {"x": 2180, "y": 250, "direccion": "derecha", "tipo": "salida"},
        {"x": 2320, "y": 340, "direccion": "derecha", "tipo": "salida"},
        {"x": 2430, "y": 310, "direccion": "derecha", "tipo": "salida"},
    ]

    llave = movimientos.crear_llave(1820, 590 - 46)
    puerta = movimientos.crear_puerta(2460, 440 - 90)

    out_dir = r"C:\Users\Malena\.gemini\antigravity-ide\brain\effb8b14-e88d-402a-8aae-c082111f922f"

    for estado_abierta in [False, True]:
        mundo.fill((0, 0, 0))
        p1 = movimientos.crear_personaje(2340, 355, "Celeste")
        p2 = movimientos.crear_personaje(2390, 355, "Violeta")
        p1["en_agua"] = True
        p2["en_agua"] = True

        llave["recolectada"] = estado_abierta
        llave["portador"] = p1 if estado_abierta else None
        if estado_abierta:
            llave["rect"].center = p1["hitbox"].center
        else:
            llave["rect"].topleft = (1820, 590 - 46)
        puerta["abierta"] = estado_abierta

        tick = 40
        pantalla.dibujar_submarino_fondo_escenario(mundo, ancho_mundo, tick)
        pantalla.dibujar_lecho_marino(mundo, suelo, ancho_mundo)
        pantalla.dibujar_corrientes_marinas_escenario(mundo, corrientes_marinas, tick)
        pantalla.dibujar_camaras_aire_escenario(mundo, camaras_aire, tick)
        pantalla.dibujar_rocas_submarinas_escenario(mundo, rocas_submarinas)
        pantalla.dibujar_flechas_indicadoras_escenario(mundo, flechas_indicadoras, tick)
        pantalla.dibujar_peligros_marinos_escenario(mundo, pinchos)

        # Dibujar puerta
        estado_p = "abierta" if puerta["abierta"] else "cerrada"
        mundo.blit(puerta["sprites"][estado_p], puerta["rect"])
        if estado_abierta:
            mundo.blit(llave["sprite"], llave["rect"])

        # Aplicar oscuridad y linternas
        surf_oscuridad = pygame.Surface((ancho_mundo, alto), pygame.SRCALPHA)
        surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45)
        pantalla.aplicar_oscuridad_submarina(
            mundo,
            [(p1, True, False), (p2, True, False)],
            surf_oscuridad,
            surf_luz,
            surf_tenue
        )

        pantalla.dibujar_personaje(mundo, p1, None)
        pantalla.dibujar_linterna_minero(mundo, p1, True)
        pantalla.dibujar_personaje(mundo, p2, None)
        pantalla.dibujar_linterna_minero(mundo, p2, True)

        # Capturar vista de los últimos 900px
        cam_x = 1700
        vista = pygame.Surface((900, alto))
        vista.blit(mundo, (0, 0), pygame.Rect(cam_x, 0, 900, alto))

        nombre = "preview_3_5_puerta_abierta.png" if estado_abierta else "preview_3_5_puerta_cerrada.png"
        out_path = os.path.join(out_dir, nombre)
        pygame.image.save(vista, out_path)
        print(f"Guardado: {out_path}")

if __name__ == "__main__":
    generar_previews_salida()
