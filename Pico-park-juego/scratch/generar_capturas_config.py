import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import configuracion
from configuracion import (
    mostrar_pestana_configuracion,
    obtener_volumen,
    fijar_volumen,
    obtener_idioma,
    cambiar_idioma,
    t
)
from personajes_menu import GestorPersonajesMenu
from sprites import cargar_boton_escalado

pygame.init()
ANCHO_MENU, ALTO_MENU = 1280, 720
pantalla = pygame.display.set_mode((ANCHO_MENU, ALTO_MENU))
reloj = pygame.time.Clock()

# --- 1. RENDERIZAR MENÚ PRINCIPAL CON MODAL DE CONFIGURACIÓN ---
fijar_volumen(70)
cambiar_idioma("es")

gestor = GestorPersonajesMenu(ANCHO_MENU, ALTO_MENU)
# Update several frames for characters to be in natural positions
for _ in range(60):
    gestor.actualizar()

from fuentes import obtener_fuente_titulo, obtener_fuente_boton
fuente_pixel_titulo = obtener_fuente_titulo(56)

ANCHO_BOTON_MENU = 272
ALTO_BOTON_MENU = 80
X_CENTRO_BOTONES = (ANCHO_MENU - ANCHO_BOTON_MENU) // 2
Y_INICIO_BOTONES = 168
ESPACIO_BOTONES = 18

btn_jugar = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
btn_personajes = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES + (ALTO_BOTON_MENU + ESPACIO_BOTONES), ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
btn_config = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES + (ALTO_BOTON_MENU + ESPACIO_BOTONES) * 2, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
btn_salir = pygame.Rect(X_CENTRO_BOTONES, Y_INICIO_BOTONES + (ALTO_BOTON_MENU + ESPACIO_BOTONES) * 3, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)

from sprites import cargar_boton
spr_jugar_normal = cargar_boton("jugar.png")
spr_jugar_hover = cargar_boton("jugar.png")
spr_personajes_normal = cargar_boton("personajes.png")
spr_personajes_hover = cargar_boton("personajes.png")
spr_opciones_normal = cargar_boton("opciones.png")
spr_opciones_hover = cargar_boton("opciones.png")
spr_salir_normal = cargar_boton("salir.png")
spr_salir_hover = cargar_boton("salir.png")

rect_btn_x = pygame.Rect(ANCHO_MENU - 40 - 24, 24, 40, 40)
spr_x_normal = cargar_boton_escalado("HUD/boton-x.png", 40, 40)

botones_menu_datos = [
    (btn_jugar, spr_jugar_normal, spr_jugar_hover),
    (btn_personajes, spr_personajes_normal, spr_personajes_hover),
    (btn_config, spr_opciones_normal, spr_opciones_hover),
    (btn_salir, spr_salir_normal, spr_salir_hover),
]
pos_mouse = (0, 0)
gestor.dibujar_menu_completo(
    pantalla,
    botones_menu_datos=botones_menu_datos,
    pos_mouse=pos_mouse,
    spr_x=spr_x_normal,
    rect_x=rect_btn_x,
    fuente_titulo=fuente_pixel_titulo,
)

# Modal parameters
W_MODAL, H_MODAL = 520, 310
rect_modal = pygame.Rect((ANCHO_MENU - W_MODAL) // 2, (ALTO_MENU - H_MODAL) // 2, W_MODAL, H_MODAL)
W_X_CFG, H_X_CFG = 29, 34
rect_x_header = pygame.Rect(rect_modal.right - W_X_CFG - 14, rect_modal.top + (54 - H_X_CFG) // 2, W_X_CFG, H_X_CFG)

# Post ESC so modal renders 1 frame and closes cleanly
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))

# Before showing modal, let's inject a capture save inside or hook into flip
# Actually, we can run mostrar_pestana_configuracion and save right before it exits, OR simulate the draw:
# Better yet, let's make a function that renders the modal on top of pantalla and saves!
capa_oscura = pygame.Surface((ANCHO_MENU, ALTO_MENU), pygame.SRCALPHA)
capa_oscura.fill((0, 0, 0, 150))
pantalla.blit(capa_oscura, (0, 0))

# Modal Shadow & Body
pygame.draw.rect(pantalla, (15, 18, 25), rect_modal.move(6, 8), border_radius=18)
pygame.draw.rect(pantalla, (36, 40, 52), rect_modal, border_radius=18)
pygame.draw.rect(pantalla, (255, 160, 100), rect_modal, width=3, border_radius=18)

# Header
rect_header = pygame.Rect(rect_modal.left, rect_modal.top, W_MODAL, 54)
pygame.draw.rect(pantalla, (46, 52, 68), rect_header, border_top_left_radius=18, border_top_right_radius=18)
pygame.draw.line(pantalla, (70, 78, 100), (rect_modal.left, rect_header.bottom), (rect_modal.right, rect_header.bottom), 2)
rect_tit_h = pygame.Rect(rect_modal.left + 50, rect_header.top + 8, rect_modal.width - 100, 38)
from fuentes import dibujar_texto_en_rect, obtener_fuente_subtitulo, obtener_fuente_contador
dibujar_texto_en_rect(pantalla, t("configuracion"), rect_tit_h, categoria="subtitulo", tamano=22, color=(255, 235, 195), negrita=True, padding=4)

# X Button
spr_x_norm = cargar_boton_escalado("HUD/boton-x.png", W_X_CFG, H_X_CFG)
if spr_x_norm: pantalla.blit(spr_x_norm, rect_x_header)

# Volume row
w_btn_lang, h_btn_lang, gap_lang = 136, 42, 14
total_w_content = 3 * w_btn_lang + 2 * gap_lang
x_margen_contenido = rect_modal.left + (W_MODAL - total_w_content) // 2
gap_vol = 14
W_BTN_VOL, H_BTN_VOL = 42, 50
w_barra = total_w_content - (2 * W_BTN_VOL + 2 * gap_vol)
h_barra = 28
y_seccion_vol = rect_modal.top + 72
cy_vol_fila = rect_modal.top + 122

rect_btn_menos = pygame.Rect(x_margen_contenido, 0, W_BTN_VOL, H_BTN_VOL)
rect_btn_menos.centery = cy_vol_fila
rect_barra_bg = pygame.Rect(rect_btn_menos.right + gap_vol, 0, w_barra, h_barra)
rect_barra_bg.centery = cy_vol_fila
rect_btn_mas = pygame.Rect(rect_barra_bg.right + gap_vol, 0, W_BTN_VOL, H_BTN_VOL)
rect_btn_mas.centery = cy_vol_fila

fuente_seccion = obtener_fuente_subtitulo(18, negrita=True, tamano_fallback=18)
t_vol_lbl = fuente_seccion.render(t("volumen"), True, (255, 195, 140))
pantalla.blit(t_vol_lbl, (x_margen_contenido, y_seccion_vol))

# Load volume buttons
spr_menos_norm = cargar_boton_escalado("HUD/boton-bajar-volumen.png", W_BTN_VOL, H_BTN_VOL)
spr_mas_norm = cargar_boton_escalado("HUD/boton-subir-volumen.png", W_BTN_VOL, H_BTN_VOL)

if spr_menos_norm: pantalla.blit(spr_menos_norm, rect_btn_menos)
if spr_mas_norm: pantalla.blit(spr_mas_norm, rect_btn_mas)

# Volume bar
pygame.draw.rect(pantalla, (22, 24, 32), rect_barra_bg, border_radius=8)
vol_val = obtener_volumen()
ancho_relleno = int((rect_barra_bg.width - 4) * (vol_val / 100.0))
if ancho_relleno > 0:
    rect_relleno = pygame.Rect(rect_barra_bg.left + 2, rect_barra_bg.top + 2, ancho_relleno, rect_barra_bg.height - 4)
    pygame.draw.rect(pantalla, (255, 160, 100), rect_relleno, border_radius=6)
pygame.draw.rect(pantalla, (80, 88, 110), rect_barra_bg, width=2, border_radius=8)

fuente_pct = obtener_fuente_contador(16, negrita=True, tamano_fallback=16)
t_pct = fuente_pct.render(f"{vol_val} %", True, (255, 255, 255))
rect_pct = t_pct.get_rect(center=rect_barra_bg.center)
t_pct_sombra = fuente_pct.render(f"{vol_val} %", True, (20, 20, 20))
pantalla.blit(t_pct_sombra, rect_pct.move(1, 1))
pantalla.blit(t_pct, rect_pct)

# Language row
y_seccion_idioma = rect_modal.top + 172
y_btns_lang = y_seccion_idioma + 30
rect_lang_es = pygame.Rect(x_margen_contenido, y_btns_lang, w_btn_lang, h_btn_lang)
rect_lang_en = pygame.Rect(rect_lang_es.right + gap_lang, y_btns_lang, w_btn_lang, h_btn_lang)
rect_lang_zh = pygame.Rect(rect_lang_en.right + gap_lang, y_btns_lang, w_btn_lang, h_btn_lang)

t_lang_lbl = fuente_seccion.render(t("idioma"), True, (255, 195, 140))
pantalla.blit(t_lang_lbl, (x_margen_contenido, y_seccion_idioma))

opciones_idioma = [
    ("es", "Español", rect_lang_es),
    ("en", "English", rect_lang_en),
    ("zh", "简体中文", rect_lang_zh),
]
fuente_btn_lang = obtener_fuente_subtitulo(16, negrita=True, tamano_fallback=16)
for cod, etiqueta, rect_btn in opciones_idioma:
    es_activo = (obtener_idioma() == cod)
    col_bg = (210, 115, 60) if es_activo else (46, 52, 68)
    col_borde = (255, 220, 150) if es_activo else (75, 82, 104)
    col_txt = (255, 255, 255) if es_activo else (195, 200, 215)
    grosor_borde = 3 if es_activo else 2
    pygame.draw.rect(pantalla, col_bg, rect_btn, border_radius=10)
    pygame.draw.rect(pantalla, col_borde, rect_btn, width=grosor_borde, border_radius=10)
    f_actual = pygame.font.SysFont("Microsoft YaHei", 16, bold=True) if cod == "zh" else fuente_btn_lang
    t_lbl = f_actual.render(etiqueta, True, col_txt)
    pantalla.blit(t_lbl, t_lbl.get_rect(center=rect_btn.center))

# Save screenshot of Menu Principal + Configuracion
ruta_menu_cfg = os.path.join(os.path.dirname(__file__), "captura_menu_configuracion.png")
pygame.image.save(pantalla, ruta_menu_cfg)
print("Guardada captura:", ruta_menu_cfg)

# Zoomed in crop of the volume controls area
rect_zoom = pygame.Rect(rect_btn_menos.left - 15, rect_btn_menos.top - 15, (rect_btn_mas.right - rect_btn_menos.left) + 30, H_BTN_VOL + 30)
sub_zoom = pantalla.subsurface(rect_zoom)
surf_zoom_scaled = pygame.transform.scale(sub_zoom, (rect_zoom.width * 2, rect_zoom.height * 2))
ruta_zoom = os.path.join(os.path.dirname(__file__), "captura_zoom_botones_volumen.png")
pygame.image.save(surf_zoom_scaled, ruta_zoom)
print("Guardada captura zoom:", ruta_zoom)

# --- 2. RENDERIZAR SELECCIÓN DE NIVELES CON CONFIGURACIÓN ---
from menu_niveles import dibujar_menu_niveles
pantalla.fill((255, 240, 195))
fuentes_m = {
    "titulo": fuente_pixel_titulo,
    "tab": obtener_fuente_titulo(34, tamano_fallback=34),
    "card": obtener_fuente_boton(28, tamano_fallback=28),
}
niveles_desbloqueados = {1: [True, True, True, False, False, False, False, False]}
dibujar_menu_niveles(pantalla, 1, niveles_desbloqueados, (0, 0), fuentes_m)

# Apply same modal overlay
pantalla.blit(capa_oscura, (0, 0))
pygame.draw.rect(pantalla, (15, 18, 25), rect_modal.move(6, 8), border_radius=18)
pygame.draw.rect(pantalla, (36, 40, 52), rect_modal, border_radius=18)
pygame.draw.rect(pantalla, (255, 160, 100), rect_modal, width=3, border_radius=18)
pygame.draw.rect(pantalla, (46, 52, 68), rect_header, border_top_left_radius=18, border_top_right_radius=18)
pygame.draw.line(pantalla, (70, 78, 100), (rect_modal.left, rect_header.bottom), (rect_modal.right, rect_header.bottom), 2)
dibujar_texto_en_rect(pantalla, t("configuracion"), rect_tit_h, categoria="subtitulo", tamano=22, color=(255, 235, 195), negrita=True, padding=4)
if spr_x_norm: pantalla.blit(spr_x_norm, rect_x_header)

pantalla.blit(t_vol_lbl, (x_margen_contenido, y_seccion_vol))
if spr_menos_norm: pantalla.blit(spr_menos_norm, rect_btn_menos)
if spr_mas_norm: pantalla.blit(spr_mas_norm, rect_btn_mas)
pygame.draw.rect(pantalla, (22, 24, 32), rect_barra_bg, border_radius=8)
if ancho_relleno > 0:
    pygame.draw.rect(pantalla, (255, 160, 100), rect_relleno, border_radius=6)
pygame.draw.rect(pantalla, (80, 88, 110), rect_barra_bg, width=2, border_radius=8)
pantalla.blit(t_pct_sombra, rect_pct.move(1, 1))
pantalla.blit(t_pct, rect_pct)

pantalla.blit(t_lang_lbl, (x_margen_contenido, y_seccion_idioma))
for cod, etiqueta, rect_btn in opciones_idioma:
    es_activo = (obtener_idioma() == cod)
    col_bg = (210, 115, 60) if es_activo else (46, 52, 68)
    col_borde = (255, 220, 150) if es_activo else (75, 82, 104)
    col_txt = (255, 255, 255) if es_activo else (195, 200, 215)
    grosor_borde = 3 if es_activo else 2
    pygame.draw.rect(pantalla, col_bg, rect_btn, border_radius=10)
    pygame.draw.rect(pantalla, col_borde, rect_btn, width=grosor_borde, border_radius=10)
    f_actual = pygame.font.SysFont("Microsoft YaHei", 16, bold=True) if cod == "zh" else fuente_btn_lang
    t_lbl = f_actual.render(etiqueta, True, col_txt)
    pantalla.blit(t_lbl, t_lbl.get_rect(center=rect_btn.center))

ruta_niv_cfg = os.path.join(os.path.dirname(__file__), "captura_niveles_configuracion.png")
pygame.image.save(pantalla, ruta_niv_cfg)
print("Guardada captura niveles:", ruta_niv_cfg)
