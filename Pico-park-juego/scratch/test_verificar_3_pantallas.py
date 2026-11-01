import os
import sys
import pygame

sys.path.insert(0, "Pico-park-juego")
sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import main
import configuracion
from configuracion import fijar_volumen, cambiar_idioma, mostrar_pestana_configuracion
import guardado
import sprites
from fuentes import obtener_fuente_titulo, obtener_fuente_subtitulo

os.makedirs("scratch/capturas_verificacion_3", exist_ok=True)
pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()

# =========================================================================
# 1. PANTALLA: MODO DE JUEGO
# =========================================================================
pantalla.blit(main._obtener_fondo_modo_juego(1280, 720), (0, 0))
main._dibujar_copos_modo(pantalla)

w_placa = min(680, 1280 - 40)
h_placa = 106
x_placa = (1280 - w_placa) // 2
y_placa = 45

surf_placa = pygame.Surface((w_placa, h_placa), pygame.SRCALPHA)
pygame.draw.rect(surf_placa, (252, 242, 228, 225), (0, 0, w_placa, h_placa), border_radius=16)
pygame.draw.rect(surf_placa, (85, 28, 48, 240), (0, 0, w_placa, h_placa), width=3, border_radius=16)
pygame.draw.rect(surf_placa, (235, 142, 72, 180), (3, 3, w_placa - 6, h_placa - 6), width=1, border_radius=14)
for cx_d, cy_d in [(12, 12), (w_placa - 12, 12), (12, h_placa - 12), (w_placa - 12, h_placa - 12)]:
    pygame.draw.circle(surf_placa, (215, 110, 42), (cx_d, cy_d), 4)
    pygame.draw.circle(surf_placa, (255, 240, 200), (cx_d, cy_d), 2)
pantalla.blit(surf_placa, (x_placa, y_placa))

f_tit = main.obtener_fuente_titulo(28)
txt_tit = "MODO DE JUEGO"
t_somb = f_tit.render(txt_tit, True, (225, 205, 185))
t_tit = f_tit.render(txt_tit, True, (68, 20, 42))
rect_tit = t_tit.get_rect(center=(1280 // 2, y_placa + 38))
pantalla.blit(t_somb, (rect_tit.x + 2, rect_tit.y + 2))
pantalla.blit(t_tit, rect_tit)

# Subtítulo ajustado
txt_sub = "Selecciona cómo deseas comenzar tu aventura"
ancho_max_sub = w_placa - 70
from fuentes import ajustar_tamano_fuente, TAMANO_SUBTITULO
f_sub_modo, _ = ajustar_tamano_fuente(
    txt_sub,
    categoria="subtitulo",
    tamano_inicial=TAMANO_SUBTITULO,
    ancho_max=ancho_max_sub,
    tamano_min=13
)
t_sub_s = f_sub_modo.render(txt_sub, True, (255, 255, 255))
t_sub = f_sub_modo.render(txt_sub, True, (108, 52, 45))
rect_sub = t_sub.get_rect(center=(1280 // 2, y_placa + 78))
pantalla.blit(t_sub_s, (rect_sub.x + 1, rect_sub.y + 1))
pantalla.blit(t_sub, rect_sub)

# Botones
W_MODO, H_MODO = 425, 100
W_VOLVER, H_VOLVER = 238, 70
x_modo = (1280 - W_MODO) // 2
btn_continuar = pygame.Rect(x_modo, (720 // 2) - 85, W_MODO, H_MODO)
btn_nueva = pygame.Rect(x_modo, (720 // 2) + 35, W_MODO, H_MODO)
btn_volver_modo = pygame.Rect((1280 - W_VOLVER) // 2, 720 - 85, W_VOLVER, H_VOLVER)

spr_cont = sprites.cargar_boton_escalado("Menu/boton-continuar-cargar....png", W_MODO, H_MODO)
spr_nueva_m = sprites.cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", W_MODO, H_MODO)
spr_vol_m = sprites.cargar_boton_escalado("mundos/boton-volver.png", W_VOLVER, H_VOLVER)
if spr_cont: pantalla.blit(spr_cont, btn_continuar)
if spr_nueva_m: pantalla.blit(spr_nueva_m, btn_nueva)
if spr_vol_m: pantalla.blit(spr_vol_m, btn_volver_modo)

spr_x = sprites.cargar_boton_escalado("HUD/boton-x.png", 40, 40)
if spr_x: pantalla.blit(spr_x, pygame.Rect(1280 - 40 - 24, 24, 40, 40))

pygame.image.save(pantalla, "scratch/capturas_verificacion_3/1_modo_juego.png")
print("1. Modo de Juego guardado!")

# =========================================================================
# 2. PANTALLA: PARTIDAS GUARDADAS
# =========================================================================
pantalla.blit(main._obtener_fondo_partidas(1280, 720), (0, 0))
rect_panel, btn_v, btn_n, btn_p = main.obtener_geometria_panel_partidas(1280, 720, True)

# Fondo diario
pygame.draw.rect(pantalla, (252, 246, 235), rect_panel, border_radius=16)
pygame.draw.rect(pantalla, (190, 160, 125), rect_panel, width=3, border_radius=16)
pygame.draw.rect(pantalla, (225, 200, 160), rect_panel.inflate(-8, -8), width=1, border_radius=12)

# Título y subtítulo
f_tit_p = main.obtener_fuente_titulo(28)
t_tit_p = f_tit_p.render("PARTIDAS GUARDADAS", True, (58, 38, 24))
pantalla.blit(t_tit_p, t_tit_p.get_rect(center=(1280 // 2, 46)))

f_dec = main.obtener_fuente_decorativa(22)
subt_p = f_dec.render("Registro de expediciones y progreso de aventura", True, (125, 95, 65))
pantalla.blit(subt_p, subt_p.get_rect(center=(1280 // 2, 78)))

# Partidas
partidas = guardado.cargar_partidas()
# Ensure we display 3 sample cards representing various states
if len(partidas) < 3:
    partidas.append({
        "id": 1,
        "nombre": "Aventura en el Bosque",
        "mundo_max": 2,
        "nivel_max": 4,
        "fecha": "31/10/2026 16:45",
        "niveles_desbloqueados": {1: [True]*5, 2: [True]*4},
        "tiene_password": True,
    })
    partidas.append({
        "id": 2,
        "nombre": "Expedición Inicial",
        "mundo_max": 1,
        "nivel_max": 1,
        "fecha": "30/10/2026 10:15",
        "niveles_desbloqueados": {1: [True]*1},
        "tiene_password": False,
    })

dict_sprites = {
    "cargar_normal": sprites.cargar_boton_escalado("mundos/boton-cargar.png", 126, 38),
    "cargar_hover": None,
    "gestionar_normal": sprites.cargar_boton_escalado("mundos/boton-gestionar.png", 118, 38),
    "gestionar_hover": None,
    "borrar_normal": sprites.cargar_boton_escalado("mundos/boton-borrar.png", 96, 38),
    "borrar_hover": None,
}
fuentes_tarjetas = {
    "titulo_card": main.obtener_fuente_subtitulo(21),
    "sub_card": main.obtener_fuente_pequena(30),
    "btn_card": main.obtener_fuente_boton(15),
    "badge": main.obtener_fuente_pequena(13),
}

for idx, p in enumerate(partidas[:3]):
    main.dibujar_tarjeta_partida(pantalla, p, idx, rect_panel, (0, 0), fuentes_tarjetas, dict_sprites)

# Volver y Nueva partida
spr_v_p = sprites.cargar_boton_escalado("mundos/boton-volver.png", btn_v.w, btn_v.h)
spr_n_p = sprites.cargar_boton_escalado("Menu/boton-nueva-partida....png", btn_n.w, btn_n.h)
if spr_v_p: pantalla.blit(spr_v_p, btn_v)
if spr_n_p: pantalla.blit(spr_n_p, btn_n)
if spr_x: pantalla.blit(spr_x, pygame.Rect(1280 - 40 - 24, 24, 40, 40))

pygame.image.save(pantalla, "scratch/capturas_verificacion_3/2_partidas_guardadas.png")

# Crop tarjeta 0 (con nombre largo y todos los datos)
r_c0 = main.obtener_geometria_tarjeta_partida(rect_panel, 0)[0]
crop_card0 = pantalla.subsurface(r_c0)
pygame.image.save(crop_card0, "scratch/capturas_verificacion_3/2_tarjeta_0_zoom.png")

# Crop tarjeta 1 (con candado de password)
r_c1 = main.obtener_geometria_tarjeta_partida(rect_panel, 1)[0]
crop_card1 = pantalla.subsurface(r_c1)
pygame.image.save(crop_card1, "scratch/capturas_verificacion_3/2_tarjeta_1_zoom.png")

print("2. Partidas Guardadas guardado!")

# =========================================================================
# 3. PANTALLA: CONFIGURACIÓN (Prueba a 0%, 25%, 50%, 75%, 100%)
# =========================================================================
for vol, lang in [(0, "zh"), (25, "es"), (50, "es"), (75, "en"), (100, "es")]:
    fijar_volumen(vol)
    cambiar_idioma(lang)

    orig_flip = pygame.display.flip
    flip_count = [0]
    def hook_flip(v=vol, l=lang):
        flip_count[0] += 1
        if flip_count[0] == 2:
            pygame.image.save(pantalla, f"scratch/capturas_verificacion_3/3_config_{l}_vol{v}.png")
            crop_modal = pantalla.subsurface(pygame.Rect((1280 - 520) // 2, (720 - 310) // 2, 520, 310))
            pygame.image.save(crop_modal, f"scratch/capturas_verificacion_3/3_modal_{l}_vol{v}_zoom.png")
            # Close modal
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
        orig_flip()

    pygame.display.flip = hook_flip
    try:
        mostrar_pestana_configuracion(pantalla, reloj)
    finally:
        pygame.display.flip = orig_flip
    print(f"3. Configuración ({lang}, {vol}%) guardado!")

# Restore default config
fijar_volumen(70)
cambiar_idioma("es")
print("Todas las pruebas finalizadas con éxito!")
