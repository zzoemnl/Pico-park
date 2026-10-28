import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import pantalla
import movimientos

artifact_dir = r"C:\Users\Malena\.gemini\antigravity-ide\brain\effb8b14-e88d-402a-8aae-c082111f922f"

# ==========================================================
# 1. CAPTURA NIVEL 3-4: LABERINTO OSCURO CON LINTERNAS Y FLECHAS
# ==========================================================
ancho_mundo = 2600
ALTO = 720
suelo = pygame.Rect(0, ALTO - 75, ancho_mundo, 75)
techo_agua = pygame.Rect(0, 0, ancho_mundo, 25)

datos_lab = pantalla.generar_laberinto_oscuro_m3_n4(ancho_mundo, ALTO, suelo.top, techo_agua.bottom, rng_seed=42)

mundo_3_4 = pygame.Surface((ancho_mundo, ALTO))
mundo_3_4.fill((10, 30, 60))

# 1. Dibujar escenario del laberinto
pantalla.dibujar_submarino_fondo_escenario(mundo_3_4, ancho_mundo, 15)
pantalla.dibujar_lecho_marino(mundo_3_4, suelo, ancho_mundo)
pantalla.dibujar_rocas_submarinas_escenario(mundo_3_4, datos_lab["rocas"])
pantalla.dibujar_barreras_algas_escenario(mundo_3_4, datos_lab["barreras"], 15)
pantalla.dibujar_flechas_indicadoras_escenario(mundo_3_4, datos_lab["flechas"], 15)
pantalla.dibujar_corales_escenario(mundo_3_4, datos_lab["corales"], 15)
pantalla.dibujar_peligros_marinos_escenario(mundo_3_4, datos_lab["pinchos"])

llave_3_4 = movimientos.crear_llave(datos_lab["llave_x"], datos_lab["llave_y"])
puerta_3_4 = movimientos.crear_puerta(datos_lab["puerta_x"], datos_lab["puerta_y"])
mundo_3_4.blit(llave_3_4["sprite"], llave_3_4["rect"])
mundo_3_4.blit(puerta_3_4["sprites"]["cerrada"], puerta_3_4["rect"])

# Personajes ubicados en pasillos cerca de flechas
p1_3_4 = movimientos.crear_personaje(datos_lab["p1_x"] + 120, datos_lab["p1_y"], "Celeste")
p2_3_4 = movimientos.crear_personaje(datos_lab["p1_x"] + 240, datos_lab["p1_y"], "Violeta")

surf_oscuridad_3_4 = pygame.Surface((ancho_mundo, ALTO), pygame.SRCALPHA)
surf_luz, surf_tenue = pantalla.obtener_superficies_luz_linterna(radio_linterna=165, radio_tenue=45)

# Aplicar oscuridad
pantalla.aplicar_oscuridad_submarina(
    mundo_3_4,
    [(p1_3_4, True, False), (p2_3_4, True, False)],
    surf_oscuridad_3_4,
    surf_luz,
    surf_tenue
)

# Dibujar personajes sobre la oscuridad
pantalla.dibujar_personaje(mundo_3_4, p1_3_4, None)
pantalla.dibujar_personaje(mundo_3_4, p2_3_4, None)
pantalla.dibujar_linterna_minero(mundo_3_4, p1_3_4, True)
pantalla.dibujar_linterna_minero(mundo_3_4, p2_3_4, True)

# Vista de cámara centrada en los personajes (1280x720)
cam_x_3_4 = max(0, min(p1_3_4["hitbox"].centerx - 640, ancho_mundo - 1280))
pantalla_3_4 = pygame.Surface((1280, 720))
pantalla_3_4.blit(mundo_3_4, (0, 0), pygame.Rect(cam_x_3_4, 0, 1280, 720))
pantalla._dibujar_hud_linternas_m3_n4(pantalla_3_4, True, True, "Celeste", "Violeta")

out_3_4 = os.path.join(artifact_dir, "preview_3_4_oscuridad_y_flechas.png")
pygame.image.save(pantalla_3_4, out_3_4)
print("Preview 3-4 guardada en:", out_3_4)

# ==========================================================
# 2. CAPTURA NIVEL 3-5: ABISMO SUBMARINO CON OSCURIDAD Y FLECHAS
# ==========================================================
mundo_3_5 = pygame.Surface((ancho_mundo, ALTO))
mundo_3_5.fill((10, 30, 60))

camaras_aire = [
    {"rect": pygame.Rect(40, 160, 200, 260), "nombre": "Cámara 1"},
    {"rect": pygame.Rect(860, 50, 190, 200), "nombre": "Cámara 2"},
    {"rect": pygame.Rect(1440, 420, 190, 225), "nombre": "Cámara 3"},
    {"rect": pygame.Rect(2020, 60, 190, 210), "nombre": "Cámara 4"},
]

corrientes_marinas = [
    {"rect": pygame.Rect(320, 300, 440, 240), "fuerza_x": 2.4, "fuerza_y": 0.0, "direccion": "derecha"},
    {"rect": pygame.Rect(780, 180, 120, 440), "fuerza_x": 0.0, "fuerza_y": -2.6, "direccion": "arriba"},
]

rocas_3_5 = [
    {"rect": pygame.Rect(260, 25, 90, 260)},
    {"rect": pygame.Rect(260, 560, 90, suelo.top - 560)},
    {"rect": pygame.Rect(460, 25, 180, 180)},
    {"rect": pygame.Rect(480, 560, 220, suelo.top - 560)},
    {"rect": pygame.Rect(720, 280, 70, suelo.top - 280)},
]

flechas_3_5 = [
    {"x": 200, "y": 320, "direccion": "derecha", "tipo": "ruta"},
    {"x": 540, "y": 380, "direccion": "derecha", "tipo": "ruta"},
    {"x": 750, "y": 480, "direccion": "arriba", "tipo": "oxigeno"},
]

pinchos_3_5 = [
    movimientos.crear_pincho(350, 25, 110, 24, direccion="abajo"),
    movimientos.crear_pincho(370, 560 - 24, 90, 24, direccion="arriba"),
]

pantalla.dibujar_submarino_fondo_escenario(mundo_3_5, ancho_mundo, 20)
pantalla.dibujar_lecho_marino(mundo_3_5, suelo, ancho_mundo)
pantalla.dibujar_corrientes_marinas_escenario(mundo_3_5, corrientes_marinas, 20)
pantalla.dibujar_camaras_aire_escenario(mundo_3_5, camaras_aire, 20)
pantalla.dibujar_rocas_submarinas_escenario(mundo_3_5, rocas_3_5)
pantalla.dibujar_flechas_indicadoras_escenario(mundo_3_5, flechas_3_5, 20)
pantalla.dibujar_peligros_marinos_escenario(mundo_3_5, pinchos_3_5)

p1_3_5 = movimientos.crear_personaje(210, 320, "Celeste")
p2_3_5 = movimientos.crear_personaje(380, 380, "Violeta")

surf_oscuridad_3_5 = pygame.Surface((ancho_mundo, ALTO), pygame.SRCALPHA)

pantalla.aplicar_oscuridad_submarina(
    mundo_3_5,
    [(p1_3_5, True, False), (p2_3_5, True, False)],
    surf_oscuridad_3_5,
    surf_luz,
    surf_tenue
)

pantalla.dibujar_personaje(mundo_3_5, p1_3_5, None)
pantalla.dibujar_personaje(mundo_3_5, p2_3_5, None)
pantalla.dibujar_linterna_minero(mundo_3_5, p1_3_5, True)
pantalla.dibujar_linterna_minero(mundo_3_5, p2_3_5, True)

pantalla_3_5 = pygame.Surface((1280, 720))
pantalla_3_5.blit(mundo_3_5, (0, 0), pygame.Rect(0, 0, 1280, 720))
pantalla._dibujar_hud_oxigeno_m3_n5(pantalla_3_5, 92.0, 85.0, "Celeste", "Violeta", 20)
pantalla._dibujar_hud_linternas_m3_n4(pantalla_3_5, True, True, "Celeste", "Violeta", y_base=60)

out_3_5 = os.path.join(artifact_dir, "preview_3_5_oscuridad_y_flechas.png")
pygame.image.save(pantalla_3_5, out_3_5)
print("Preview 3-5 guardada en:", out_3_5)

# ==========================================================
# 3. CAPTURA NIVEL 3-5 CON LINTERNA APAGADA (P1 OFF, P2 ON)
# ==========================================================
mundo_3_5_off = pygame.Surface((ancho_mundo, ALTO))
mundo_3_5_off.fill((10, 30, 60))

pantalla.dibujar_submarino_fondo_escenario(mundo_3_5_off, ancho_mundo, 20)
pantalla.dibujar_lecho_marino(mundo_3_5_off, suelo, ancho_mundo)
pantalla.dibujar_corrientes_marinas_escenario(mundo_3_5_off, corrientes_marinas, 20)
pantalla.dibujar_camaras_aire_escenario(mundo_3_5_off, camaras_aire, 20)
pantalla.dibujar_rocas_submarinas_escenario(mundo_3_5_off, rocas_3_5)
pantalla.dibujar_flechas_indicadoras_escenario(mundo_3_5_off, flechas_3_5, 20)
pantalla.dibujar_peligros_marinos_escenario(mundo_3_5_off, pinchos_3_5)

surf_oscuridad_3_5_off = pygame.Surface((ancho_mundo, ALTO), pygame.SRCALPHA)

# P1 linterna apagada (False), P2 encendida (True)
pantalla.aplicar_oscuridad_submarina(
    mundo_3_5_off,
    [(p1_3_5, False, False), (p2_3_5, True, False)],
    surf_oscuridad_3_5_off,
    surf_luz,
    surf_tenue
)

pantalla.dibujar_personaje(mundo_3_5_off, p1_3_5, None)
pantalla.dibujar_personaje(mundo_3_5_off, p2_3_5, None)
pantalla.dibujar_linterna_minero(mundo_3_5_off, p1_3_5, False)
pantalla.dibujar_linterna_minero(mundo_3_5_off, p2_3_5, True)

pantalla_3_5_off = pygame.Surface((1280, 720))
pantalla_3_5_off.blit(mundo_3_5_off, (0, 0), pygame.Rect(0, 0, 1280, 720))
pantalla._dibujar_hud_oxigeno_m3_n5(pantalla_3_5_off, 92.0, 85.0, "Celeste", "Violeta", 20)
pantalla._dibujar_hud_linternas_m3_n4(pantalla_3_5_off, False, True, "Celeste", "Violeta", y_base=60)

out_3_5_off = os.path.join(artifact_dir, "preview_3_5_linterna_apagada.png")
pygame.image.save(pantalla_3_5_off, out_3_5_off)
print("Preview 3-5 linterna apagada guardada en:", out_3_5_off)
