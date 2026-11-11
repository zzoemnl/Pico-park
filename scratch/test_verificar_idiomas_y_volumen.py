import os
import sys
import pygame

sys.path.insert(0, "Pico-park-juego")
sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import configuracion
from configuracion import fijar_volumen, cambiar_idioma, mostrar_pestana_configuracion, obtener_volumen, obtener_idioma
import fuentes
import sprites

os.makedirs("scratch/capturas_idiomas_verificacion", exist_ok=True)
pantalla = pygame.display.set_mode((1280, 720))
reloj = pygame.time.Clock()

casos_prueba = [
    # 1. Ciclo inicial
    ("es", 50, "1_es_vol50"),
    ("en", 75, "2_en_vol75"),
    ("zh", 0,  "3_zh_vol0"),
    ("zh", 50, "4_zh_vol50"),
    ("zh", 100,"5_zh_vol100"),
    # 2. Alternancia rápida para verificar que el caché no se envenena
    ("es", 0,  "6_retorno_es_vol0"),
    ("zh", 25, "7_retorno_zh_vol25"),
    ("en", 50, "8_retorno_en_vol50"),
    ("es", 100,"9_retorno_es_vol100"),
]

for lang, vol, nombre in casos_prueba:
    cambiar_idioma(lang)
    fijar_volumen(vol)

    orig_flip = pygame.display.flip
    flip_count = [0]
    def hook_flip(n=nombre):
        flip_count[0] += 1
        if flip_count[0] == 2:
            # Captura completa
            pygame.image.save(pantalla, f"scratch/capturas_idiomas_verificacion/{n}_full.png")
            # Zoom al modal de configuración
            crop_modal = pantalla.subsurface(pygame.Rect((1280 - 520) // 2, (720 - 310) // 2, 520, 310))
            pygame.image.save(crop_modal, f"scratch/capturas_idiomas_verificacion/{n}_modal.png")
            # Cerrar modal
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
        orig_flip()

    pygame.display.flip = hook_flip
    try:
        mostrar_pestana_configuracion(pantalla, reloj)
    finally:
        pygame.display.flip = orig_flip
    print(f"Probado {nombre}: idioma={lang}, vol={vol}% OK")

# Restaurar estado por defecto
cambiar_idioma("es")
fijar_volumen(70)
print("Todas las pruebas de cambio de idioma y volumen completadas con éxito!")

