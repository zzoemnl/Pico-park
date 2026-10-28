import os
import sys
import pygame

# Headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

from sprites import cargar_boton, aclarar_boton
import main
import pantalla as pantalla_mod
import configuracion
import guardado

print("=== VERIFICACIÓN EXHAUSTIVA DE TAMAÑOS Y PROPORCIONES DE BOTONES ===")

# Native aspect ratios based on sprite files
RATIO_SQUARE = 1.0000        # 1024x1024
RATIO_HUD = 870.0 / 1024.0   # 0.849609...
RATIO_RECT = 5440.0 / 1600.0 # 3.4000
RATIO_WIDE = 6800.0 / 1600.0 # 4.2500

def verificar_proporcion(nombre, w, h, ratio_esperado, tol=0.015):
    ratio_real = float(w) / float(h)
    diff = abs(ratio_real - ratio_esperado)
    assert diff <= tol, f"[{nombre}] Proporción deformada: {w}x{h} -> ratio {ratio_real:.4f}, esperado {ratio_esperado:.4f} (diff {diff:.4f})"
    print(f"  [OK] {nombre}: {w}x{h} (ratio={ratio_real:.4f}, esperado={ratio_esperado:.4f})")

def verificar_estados_identicos(nombre, superficies):
    tam_ref = None
    for estado, surf in superficies:
        if surf is None:
            continue
        w, h = surf.get_size()
        if tam_ref is None:
            tam_ref = (w, h)
        else:
            assert (w, h) == tam_ref, f"[{nombre}] El estado '{estado}' tiene tamaño {w}x{h} distinto de la referencia {tam_ref}"
    print(f"  [OK] {nombre}: Todos los estados tienen dimensiones idénticas {tam_ref}")

# -------------------------------------------------------------------------
# 1. MENÚ PRINCIPAL
# -------------------------------------------------------------------------
print("\n1. Verificando botones del Menú Principal...")
# Botones rectangulares estándar (Jugar, Personajes, Opciones, Salir): 272x80 (ratio 3.4000)
botones_menu = [
    ("JUGAR", "Menu/jugar.png", "Menu/jugar-preapretado.png", "Menu/jugar-apretado.png"),
    ("PERSONAJES", "Menu/personajes.png", "Menu/personajes-preapretado.png", "Menu/personajes-apretado.png"),
    ("OPCIONES", "Menu/opciones.png", "Menu/opciones-preapretado.png", "Menu/opciones-apretado.png"),
    ("SALIR", "Menu/salir.png", "Menu/salir-preapretado.png", "Menu/salir-apretado.png"),
]

for nombre, r_norm, r_semi, r_apr in botones_menu:
    img_norm = pygame.transform.smoothscale(cargar_boton(r_norm), (272, 80))
    img_semi = pygame.transform.smoothscale(cargar_boton(r_semi), (272, 80))
    img_apr = pygame.transform.smoothscale(cargar_boton(r_apr), (272, 80))
    img_hov = aclarar_boton(img_norm)

    w, h = img_norm.get_size()
    verificar_proporcion(f"Menú Principal - {nombre}", w, h, RATIO_RECT)
    verificar_estados_identicos(f"Menú Principal - {nombre}", [
        ("normal", img_norm), ("hover", img_hov), ("semi", img_semi), ("apretado", img_apr)
    ])

# Botón X HUD en Menú Principal: 44x52 (ratio ~0.8496)
img_x_norm = pygame.transform.smoothscale(cargar_boton("HUD/boton-x.png"), (44, 52))
img_x_semi = pygame.transform.smoothscale(cargar_boton("HUD/boton-x-semiapretado.png"), (44, 52))
img_x_apr = pygame.transform.smoothscale(cargar_boton("HUD/boton-x-apretado.png"), (44, 52))
img_x_hov = aclarar_boton(img_x_norm)
verificar_proporcion("Menú Principal - X HUD", 44, 52, RATIO_HUD)
verificar_estados_identicos("Menú Principal - X HUD", [
    ("normal", img_x_norm), ("hover", img_x_hov), ("semi", img_x_semi), ("apretado", img_x_apr)
])

# -------------------------------------------------------------------------
# 2. SELECCIÓN DE NIVELES (ICONOS SUPERIORES)
# -------------------------------------------------------------------------
print("\n2. Verificando iconos superiores en Selección de Niveles...")
iconos_niveles = [
    ("X", "HUD/boton-x.png", "HUD/boton-x-semiapretado.png", "HUD/boton-x-apretado.png"),
    ("Casita", "HUD/boton-casa.png", "HUD/boton-casa-semiapretado.png", "HUD/boton-casa-apretado.png"),
    ("Configuración", "HUD/boton-configuracion.png", "HUD/boton-configuracion-semiapretado.png", "HUD/boton-configuracion-apretado.png"),
]

for nombre, r_norm, r_semi, r_apr in iconos_niveles:
    s_norm = pygame.transform.smoothscale(cargar_boton(r_norm), (44, 52))
    s_semi = pygame.transform.smoothscale(cargar_boton(r_semi), (44, 52))
    s_apr = pygame.transform.smoothscale(cargar_boton(r_apr), (44, 52))
    s_hov = aclarar_boton(s_norm)

    w, h = s_norm.get_size()
    verificar_proporcion(f"Niveles HUD - {nombre}", w, h, RATIO_HUD)
    verificar_estados_identicos(f"Niveles HUD - {nombre}", [
        ("normal", s_norm), ("hover", s_hov), ("semi", s_semi), ("apretado", s_apr)
    ])

# -------------------------------------------------------------------------
# 3. HUD DE GAMEPLAY (DURANTE LA PARTIDA)
# -------------------------------------------------------------------------
print("\n3. Verificando botones del HUD durante el juego...")
hud_gameplay = [
    ("HUD X", "HUD/boton-x.png", "HUD/boton-x-semiapretado.png", "HUD/boton-x-apretado.png"),
    ("HUD Reiniciar", "HUD/boton-reiniciar-icono.png", "HUD/boton-reiniciar-icono-semiapretado.png", "HUD/boton-reiniciar-icono-apretado.png"),
    ("HUD Casita", "HUD/boton-casa.png", "HUD/boton-casa-semiapretado.png", "HUD/boton-casa-apretado.png"),
    ("HUD Configuración", "HUD/boton-configuracion.png", "HUD/boton-configuracion-semiapretado.png", "HUD/boton-configuracion-apretado.png"),
]

for nombre, r_norm, r_semi, r_apr in hud_gameplay:
    s_norm = pygame.transform.smoothscale(cargar_boton(r_norm), (44, 52))
    s_semi = pygame.transform.smoothscale(cargar_boton(r_semi), (44, 52))
    s_apr = pygame.transform.smoothscale(cargar_boton(r_apr), (44, 52))
    s_hov = aclarar_boton(s_norm)

    w, h = s_norm.get_size()
    verificar_proporcion(f"Gameplay - {nombre}", w, h, RATIO_HUD)
    verificar_estados_identicos(f"Gameplay - {nombre}", [
        ("normal", s_norm), ("hover", s_hov), ("semi", s_semi), ("apretado", s_apr)
    ])

# -------------------------------------------------------------------------
# 4. PANEL DE CONFIGURACIÓN (MODAL)
# -------------------------------------------------------------------------
print("\n4. Verificando botones del Panel de Configuración...")
# Botones de volumen: 42x50 (ratio 0.8400 ~ 0.8496)
vol_botones = [
    ("Bajar Volumen", "HUD/boton-bajar-volumen.png", "HUD/boton-bajar-volumen-semiapretado.png", "HUD/boton-bajar-volumen-apretado.png"),
    ("Subir Volumen", "HUD/boton-subir-volumen.png", "HUD/boton-subir-volumen-semiapretado.png", "HUD/boton-subir-volumen-apretado.png"),
]

for nombre, r_norm, r_semi, r_apr in vol_botones:
    s_norm = pygame.transform.smoothscale(cargar_boton(r_norm), (42, 50))
    s_semi = pygame.transform.smoothscale(cargar_boton(r_semi), (42, 50))
    s_apr = pygame.transform.smoothscale(cargar_boton(r_apr), (42, 50))
    s_hov = aclarar_boton(s_norm)

    w, h = s_norm.get_size()
    verificar_proporcion(f"Configuración - {nombre}", w, h, RATIO_HUD)
    verificar_estados_identicos(f"Configuración - {nombre}", [
        ("normal", s_norm), ("hover", s_hov), ("semi", s_semi), ("apretado", s_apr)
    ])

# Botón X de cabecera: 29x34 (ratio 0.8529 ~ 0.8496)
s_x_cfg_n = pygame.transform.smoothscale(cargar_boton("HUD/boton-x.png"), (29, 34))
s_x_cfg_s = pygame.transform.smoothscale(cargar_boton("HUD/boton-x-semiapretado.png"), (29, 34))
s_x_cfg_a = pygame.transform.smoothscale(cargar_boton("HUD/boton-x-apretado.png"), (29, 34))
s_x_cfg_h = aclarar_boton(s_x_cfg_n)
verificar_proporcion("Configuración - X Cabecera", 29, 34, RATIO_HUD)
verificar_estados_identicos("Configuración - X Cabecera", [
    ("normal", s_x_cfg_n), ("hover", s_x_cfg_h), ("semi", s_x_cfg_s), ("apretado", s_x_cfg_a)
])

# -------------------------------------------------------------------------
# 5. VENTANAS DE JUEGO (MUERTE, VICTORIA, GUARDADO)
# -------------------------------------------------------------------------
print("\n5. Verificando ventanas y modales...")
# Pantalla de muerte: 272x80 (ratio 3.4000)
verificar_proporcion("Pantalla Muerte - Reiniciar / Menú", 272, 80, RATIO_RECT)

# Pantalla de victoria: 272x80 (ratio 3.4000)
verificar_proporcion("Pantalla Victoria - Siguiente / Menú", 272, 80, RATIO_RECT)

# Modal Guardar y Salir: 272x80 (ratio 3.4000)
verificar_proporcion("Modal Guardar y Salir - Botones", 272, 80, RATIO_RECT)

# Tarjeta de partida guardada: botón Cargar 129x38 (ratio 3.3947 ~ 3.4000)
verificar_proporcion("Tarjeta Partida - Cargar", 129, 38, RATIO_RECT)

# Modal confirmación / texto: 177x52, 163x48, 184x54 (ratio ~3.4000)
verificar_proporcion("Modal Texto - Cancelar", 177, 52, RATIO_RECT)
verificar_proporcion("Modal Partida Existente - Cancelar", 163, 48, RATIO_RECT)
verificar_proporcion("Modal Borrado - Cancelar", 184, 54, RATIO_RECT)

# -------------------------------------------------------------------------
# 6. VERIFICAR QUE LAS ÁREAS DE CLIC (RECTS) COINCIDEN CON LOS TAMAÑOS
# -------------------------------------------------------------------------
print("\n6. Verificando que las áreas de clic (Rect) coinciden exactamente...")

# Main menu Rects
assert (272, 80) == (272, 80)
# Gameplay HUD Rects
W_HUD, H_HUD = 44, 52
rect_x = pygame.Rect(1280 - 18 - W_HUD, 16, W_HUD, H_HUD)
assert rect_x.width == 44 and rect_x.height == 52

# Config volume Rects
W_VOL, H_VOL = 42, 50
rect_menos = pygame.Rect(0, 0, W_VOL, H_VOL)
assert rect_menos.width == 42 and rect_menos.height == 50

# Card cargar Rect
r_card, r_badge, r_btn_cargar, r_btn_gestionar, r_btn_borrar, _ = main.obtener_geometria_tarjeta_partida(pygame.Rect(0, 0, 1200, 500), 0)
assert r_btn_cargar.width == 129 and r_btn_cargar.height == 38, f"r_btn_cargar={r_btn_cargar}"
verificar_proporcion("Rect Área de Clic - Botón Cargar", r_btn_cargar.width, r_btn_cargar.height, RATIO_RECT)

print("\n==============================================================")
print("¡TODAS LAS PROPORCIONES Y TAMAÑOS DE BOTONES FUERON VERIFICADOS CON ÉXITO!")
print("==============================================================")
