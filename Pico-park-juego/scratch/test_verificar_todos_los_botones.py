import os
import sys
import copy
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.font.init()

import main
import menu_niveles
import guardado
import configuracion
import sprites

os.makedirs('scratch/capturas_botones', exist_ok=True)
pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()
sprites.precargar_botones_comunes()

# -------------------------------------------------------------
# 1. MENÚ PRINCIPAL
# -------------------------------------------------------------
ANCHO_BOTON, ALTO_BOTON, ESPACIO = 272, 80, 14
x_centro = (1280 - ANCHO_BOTON) // 2
total_h_menu = (ALTO_BOTON * 4) + (ESPACIO * 3)
y_inicio = (720 - total_h_menu) // 2 + 35

btn_jugar = pygame.Rect(x_centro, y_inicio, ANCHO_BOTON, ALTO_BOTON)
btn_personajes = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO), ANCHO_BOTON, ALTO_BOTON)
btn_config = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON)
btn_salir = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON)
rect_btn_x = pygame.Rect(1280 - 16 - 44, 16, 44, 52)

spr_j = sprites.cargar_boton_escalado("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON)
spr_p = sprites.cargar_boton_escalado("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON)
spr_o = sprites.cargar_boton_escalado("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON)
spr_s = sprites.cargar_boton_escalado("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON)
spr_x = sprites.cargar_boton_escalado("HUD/boton-x.png", 44, 52)

gestor_menu = main.GestorPersonajesMenu(1280, 720)
botones_menu_datos = [
    (btn_jugar, spr_j, sprites.aclarar_boton(spr_j)),
    (btn_personajes, spr_p, sprites.aclarar_boton(spr_p)),
    (btn_config, spr_o, sprites.aclarar_boton(spr_o)),
    (btn_salir, spr_s, sprites.aclarar_boton(spr_s)),
]
fuente_tit = main.obtener_fuente_titulo(main.TAMANO_TITULO, negrita=True, tamano_fallback=48)
gestor_menu.dibujar_menu_completo(pantalla, botones_menu_datos=botones_menu_datos, pos_mouse=(0, 0), spr_x=spr_x, rect_x=rect_btn_x, fuente_titulo=fuente_tit)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_1_menu_principal.png")
print("1. Menú principal capturado")

# -------------------------------------------------------------
# 2. MODO DE JUEGO
# -------------------------------------------------------------
pantalla.blit(main._obtener_fondo_modo_juego(1280, 720), (0, 0))
W_MODO, H_MODO = 425, 100
W_VOLVER, H_VOLVER = 238, 70
x_modo = (1280 - W_MODO) // 2
btn_continuar = pygame.Rect(x_modo, (720 // 2) - 85, W_MODO, H_MODO)
btn_nueva = pygame.Rect(x_modo, (720 // 2) + 35, W_MODO, H_MODO)
btn_volver_modo = pygame.Rect((1280 - W_VOLVER) // 2, 720 - 85, W_VOLVER, H_VOLVER)

spr_cont = sprites.cargar_boton_escalado("Menu/boton-continuar-cargar....png", W_MODO, H_MODO)
spr_nueva_m = sprites.cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", W_MODO, H_MODO)
spr_vol_m = sprites.cargar_boton_escalado("mundos/boton-volver.png", W_VOLVER, H_VOLVER)

pantalla.blit(spr_cont, btn_continuar)
pantalla.blit(spr_nueva_m, btn_nueva)
pantalla.blit(spr_vol_m, btn_volver_modo)
pantalla.blit(spr_x, rect_btn_x)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_2_modo_juego.png")
print("2. Modo de juego capturado")

# -------------------------------------------------------------
# 3. PARTIDAS GUARDADAS
# -------------------------------------------------------------
pantalla.blit(main._obtener_fondo_partidas(1280, 720), (0, 0))
rect_panel_partidas, btn_volver_partidas, btn_nueva_desde_lista, btn_iniciar_primera = (
    main.obtener_geometria_panel_partidas(1280, 720, True)
)

col_pagina = (252, 246, 235)
col_borde_pag = (190, 160, 125)
pygame.draw.rect(pantalla, col_pagina, rect_panel_partidas, border_radius=16)
pygame.draw.rect(pantalla, col_borde_pag, rect_panel_partidas, width=3, border_radius=16)

partidas = guardado.cargar_partidas()
if not partidas:
    # Dummy save for visual test
    partidas = [{
        "id": 1,
        "nombre": "Aventura Principal",
        "mundo_max": 2,
        "nivel_max": 3,
        "fecha": "31/10/2026",
        "niveles_desbloqueados": {1: [True]*5, 2: [True]*3 + [False]*2},
        "tiene_password": False,
    }]

spr_c_n = sprites.cargar_boton_escalado("mundos/boton-cargar.png", 126, 38)
spr_g_n = sprites.generar_boton_con_texto("mundos/boton-volver.png", 118, 38, "GESTIONAR", (60, 45, 30), 13)
spr_b_n = sprites.generar_boton_con_texto("Menu/salir.png", 96, 38, "BORRAR", (255, 255, 255), 14)

dict_btn_cards = {
    "cargar_normal": spr_c_n,
    "gestionar_normal": spr_g_n,
    "borrar_normal": spr_b_n,
}
fuentes_t = {
    "titulo_card": main.obtener_fuente_subtitulo(18, negrita=True),
    "sub_card": main.obtener_fuente_pequena(14),
    "badge": main.obtener_fuente_pequena(14),
    "btn": main.obtener_fuente_pequena(14),
}
for idx, p in enumerate(partidas[:3]):
    main.dibujar_tarjeta_partida(pantalla, p, idx, rect_panel_partidas, (0, 0), fuentes_t, dict_btn_cards)

spr_vol_p = sprites.cargar_boton_escalado("mundos/boton-volver.png", W_VOLVER, 68)
spr_nuev_p = sprites.cargar_boton_escalado("mundos/boton-nueva-partida.png", W_VOLVER, 68)
pantalla.blit(spr_vol_p, btn_volver_partidas)
pantalla.blit(spr_nuev_p, btn_nueva_desde_lista)
pantalla.blit(spr_x, rect_btn_x)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_3_partidas_guardadas.png")
print("3. Partidas guardadas capturado")

# -------------------------------------------------------------
# 4. PERSONAJES
# -------------------------------------------------------------
pantalla.fill((255, 240, 195))
pygame.draw.rect(pantalla, (225, 110, 80), pygame.Rect(0, 720 - 80, 1280, 80))
btn_vol_pj = pygame.Rect((1280 - W_VOLVER) // 2, 720 - 85, W_VOLVER, H_VOLVER)
pantalla.blit(spr_vol_m, btn_vol_pj)
pantalla.blit(spr_x, rect_btn_x)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_4_personajes.png")
print("4. Personajes capturado")

# -------------------------------------------------------------
# 5. SELECCIÓN DE NIVELES
# -------------------------------------------------------------
pantalla.fill((244, 238, 226))
fuentes_menu = {
    "titulo": main.obtener_fuente_titulo(36),
    "subtitulo": main.obtener_fuente_subtitulo(16),
}
desbloqueados = {1: [True, True, True, False, False], 2: [False]*5, 3: [False]*5}
menu_niveles.dibujar_menu_niveles(pantalla, 1, desbloqueados, (0, 0), fuentes_menu)

rect_btn_x_n = pygame.Rect(1280 - 16 - 44, 16, 44, 52)
rect_btn_casa_n = pygame.Rect(rect_btn_x_n.left - 12 - 44, 16, 44, 52)
rect_btn_cfg_n = pygame.Rect(rect_btn_casa_n.left - 12 - 44, 16, 44, 52)

spr_casa = sprites.cargar_boton_escalado("HUD/boton-casa.png", 44, 52)
spr_cfg = sprites.cargar_boton_escalado("HUD/boton-configuracion.png", 44, 52)
pantalla.blit(spr_cfg, rect_btn_cfg_n)
pantalla.blit(spr_casa, rect_btn_casa_n)
pantalla.blit(spr_x, rect_btn_x_n)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_5_seleccion_niveles.png")
print("5. Selección de niveles capturado")

# -------------------------------------------------------------
# 6. CONFIGURACIÓN (Idiomas + Volumen)
# -------------------------------------------------------------
pantalla.fill((30, 30, 30))
# Let's draw the configuration modal frame
w_card, h_card = 600, 390
rect_card = pygame.Rect((1280 - w_card) // 2, (720 - h_card) // 2, w_card, h_card)
pygame.draw.rect(pantalla, (24, 26, 34), rect_card, border_radius=20)
pygame.draw.rect(pantalla, (75, 82, 104), rect_card, width=2, border_radius=20)

spr_vol_down = sprites.cargar_boton_escalado("HUD/boton-bajar-volumen.png", 42, 50)
spr_vol_up = sprites.cargar_boton_escalado("HUD/boton-subir-volumen.png", 42, 50)
spr_x_cfg = sprites.cargar_boton_escalado("HUD/boton-x.png", 29, 34)

rect_x_head = pygame.Rect(rect_card.right - 29 - 18, rect_card.top + 16, 29, 34)
pantalla.blit(spr_x_cfg, rect_x_head)

r_down = pygame.Rect(rect_card.left + 50, rect_card.top + 150, 42, 50)
r_up = pygame.Rect(rect_card.right - 50 - 42, rect_card.top + 150, 42, 50)
pantalla.blit(spr_vol_down, r_down)
pantalla.blit(spr_vol_up, r_up)

# Language buttons
w_btn_lang, h_btn_lang, gap_lang = 136, 42, 14
x_lang_start = rect_card.left + 50
y_lang = rect_card.top + 260
opciones_lang = [
    ("es", "ESPAÑOL", pygame.Rect(x_lang_start, y_lang, w_btn_lang, h_btn_lang), True),
    ("en", "ENGLISH", pygame.Rect(x_lang_start + w_btn_lang + gap_lang, y_lang, w_btn_lang, h_btn_lang), False),
    ("zh", "中文", pygame.Rect(x_lang_start + (w_btn_lang + gap_lang)*2, y_lang, w_btn_lang, h_btn_lang), False),
]
for cod, lbl, r_b, act in opciones_lang:
    base = "mundos/boton-cargar.png" if act else "mundos/boton-volver.png"
    col = (26, 83, 29) if act else (60, 45, 30)
    if cod == "zh":
        marco = sprites.generar_marco_boton(base, r_b.w, r_b.h)
        btn_s = marco.copy()
        f_zh = pygame.font.SysFont("Microsoft YaHei", 16, bold=True)
        t_l = f_zh.render(lbl, True, col)
        btn_s.blit(t_l, t_l.get_rect(center=(r_b.w // 2, r_b.h // 2)))
    else:
        btn_s = sprites.generar_boton_con_texto(base, r_b.w, r_b.h, lbl, col, 16)
    pantalla.blit(btn_s, r_b)

pygame.image.save(pantalla, "scratch/capturas_botones/captura_6_configuracion.png")
print("6. Configuración capturado")

# -------------------------------------------------------------
# 7. MODAL ADMINISTRAR PERFIL
# -------------------------------------------------------------
pantalla.fill((30, 30, 30))
w_card, h_card = 560, 335
rect_card = pygame.Rect((1280 - w_card) // 2, (720 - h_card) // 2, w_card, h_card)
pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=16)
pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=16)
pantalla.blit(spr_x_cfg, pygame.Rect(rect_card.right - 29 - 16, rect_card.top + 16, 29, 34))

w_b, h_b = 360, 48
x_b = rect_card.centerx - (w_b // 2)
y_base = rect_card.top + 114
gap_b = 14
btn_ren = pygame.Rect(x_b, y_base, w_b, h_b)
btn_pwd = pygame.Rect(x_b, y_base + (h_b + gap_b), w_b, h_b)
btn_eli = pygame.Rect(x_b, y_base + (h_b + gap_b) * 2, w_b, h_b)

pantalla.blit(sprites.generar_boton_con_texto("mundos/boton-volver.png", w_b, h_b, "CAMBIAR NOMBRE", (60, 45, 30), 16), btn_ren)
pantalla.blit(sprites.generar_boton_con_texto("mundos/boton-volver.png", w_b, h_b, "AGREGAR CONTRASEÑA", (60, 45, 30), 16), btn_pwd)
pantalla.blit(sprites.generar_boton_con_texto("Menu/salir.png", w_b, h_b, "ELIMINAR PERFIL", (255, 255, 255), 16), btn_eli)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_7_modal_administrar.png")
print("7. Modal administrar capturado")

# -------------------------------------------------------------
# 8. MODAL CONFIRMAR BORRADO
# -------------------------------------------------------------
pantalla.fill((30, 30, 30))
w_card, h_card = 540, 290
rect_card = pygame.Rect((1280 - w_card) // 2, (720 - h_card) // 2, w_card, h_card)
pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=18)
pygame.draw.rect(pantalla, (225, 110, 80), rect_card, width=3, border_radius=18)

w_btn, h_btn = 184, 54
gap_btn = 22
total_w = w_btn * 2 + gap_btn
x_c = rect_card.centerx - total_w // 2
x_b = x_c + w_btn + gap_btn
y_btns = rect_card.bottom - 74
btn_can = pygame.Rect(x_c, y_btns, w_btn, h_btn)
btn_bor = pygame.Rect(x_b, y_btns, w_btn, h_btn)

pantalla.blit(sprites.cargar_boton_escalado("Menu/boton-cancelar.png", w_btn, h_btn), btn_can)
pantalla.blit(sprites.generar_boton_con_texto("Menu/salir.png", w_btn, h_btn, "BORRAR PERFIL", (255, 255, 255), 16), btn_bor)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_8_modal_borrar.png")
print("8. Modal borrar capturado")

# -------------------------------------------------------------
# 9. MODAL GUARDAR Y SALIR
# -------------------------------------------------------------
pantalla.fill((30, 30, 30))
w_card, h_card = 460, 440
rect_card = pygame.Rect((1280 - w_card) // 2, (720 - h_card) // 2, w_card, h_card)
pygame.draw.rect(pantalla, (253, 246, 233), rect_card, border_radius=20)
pygame.draw.rect(pantalla, (195, 168, 138), rect_card, width=3, border_radius=20)

w_b9, h_b9 = 272, 80
x_b9 = rect_card.centerx - (w_b9 // 2)
y_b9 = rect_card.top + 140
esp_b9 = 14

btn_g = pygame.Rect(x_b9, y_b9, w_b9, h_b9)
btn_s = pygame.Rect(x_b9, y_b9 + h_b9 + esp_b9, w_b9, h_b9)
btn_c = pygame.Rect(x_b9, y_b9 + (h_b9 + esp_b9)*2, w_b9, h_b9)

pantalla.blit(sprites.cargar_boton_escalado("Ventanas/boton-guardar-y-salir.png", w_b9, h_b9), btn_g)
pantalla.blit(sprites.cargar_boton_escalado("Ventanas/boton-salir-sin-guardar.png", w_b9, h_b9), btn_s)
pantalla.blit(sprites.cargar_boton_escalado("Menu/boton-cancelar.png", w_b9, h_b9), btn_c)
pygame.image.save(pantalla, "scratch/capturas_botones/captura_9_modal_guardar_salir.png")
print("9. Modal guardar y salir capturado")

print("All screenshots saved successfully in scratch/capturas_botones!")
