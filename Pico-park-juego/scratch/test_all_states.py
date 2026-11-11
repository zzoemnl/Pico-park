import sys, os, pygame

sys.path.insert(0, 'Pico-park-juego')
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1280, 720))

import configuracion
from configuracion import cambiar_idioma, t
import sprites
import main

# Test main menu helper across languages and states
print("=== VERIFYING MAIN MENU BUTTON STATES ===")
for lang in ['es', 'en', 'zh']:
    cambiar_idioma(lang)
    for tipo in ['jugar', 'personajes', 'opciones', 'salir']:
        for est in ['normal', 'hover', 'semi', 'apretado']:
            surf = main._obtener_boton_menu_principal_estado(tipo, est, lang)
            assert surf is not None, f"Failed to get {tipo} {est} for {lang}"
            assert surf.get_size() == (272, 80), f"Wrong size {surf.get_size()} for {tipo} {est} in {lang}"
print("All main menu button states successfully verified for all 3 languages.")

# Test Modo Juego button helper across languages and states
print("=== VERIFYING MODO JUEGO BUTTON STATES ===")
for lang in ['es', 'en', 'zh']:
    cambiar_idioma(lang)
    for tipo in ['continuar', 'nueva_partida']:
        for est in ['normal', 'hover', 'semi', 'apretado']:
            surf = main._obtener_boton_modo(tipo, est, lang)
            assert surf is not None, f"Failed to get modo {tipo} {est} for {lang}"
            assert surf.get_size() == (280, 80), f"Wrong size {surf.get_size()} for modo {tipo} {est} in {lang}"
print("All modo juego button states successfully verified for all 3 languages.")

# Test Volver button helper across languages and states
print("=== VERIFYING VOLVER BUTTON STATES ===")
for lang in ['es', 'en', 'zh']:
    cambiar_idioma(lang)
    for est in ['normal', 'hover', 'semi', 'apretado']:
        surf = main._obtener_boton_volver(est, lang)
        assert surf is not None, f"Failed to get volver {est} for {lang}"
        assert surf.get_size() == (238, 70), f"Wrong size {surf.get_size()} for volver {est} in {lang}"
print("All volver button states successfully verified for all 3 languages.")

# Test Lista Partidas card buttons
print("=== VERIFYING CARD BUTTON STATES ===")
for lang in ['es', 'en', 'zh']:
    cambiar_idioma(lang)
    sp_card = main._obtener_sprites_tarjeta(lang)
    for key in ['cargar_normal', 'cargar_hover', 'cargar_semi', 'cargar_apretado',
                'gestionar_normal', 'gestionar_hover', 'gestionar_semi', 'gestionar_apretado',
                'borrar_normal', 'borrar_hover', 'borrar_semi', 'borrar_apretado']:
        assert key in sp_card and sp_card[key] is not None, f"Missing {key} in card sprites for {lang}"
print("All card button states successfully verified for all 3 languages.")

# Test nueva desde lista & primera partida
print("=== VERIFYING NUEVA LISTA & PRIMERA PARTIDA STATES ===")
for lang in ['es', 'en', 'zh']:
    cambiar_idioma(lang)
    for est in ['normal', 'hover', 'semi', 'apretado']:
        surf_nl = main._obtener_boton_nueva_lista(est, lang)
        assert surf_nl is not None, f"Failed to get nueva lista {est} for {lang}"
        surf_pr = main._obtener_boton_primera_partida(est, lang)
        assert surf_pr is not None, f"Failed to get primera partida {est} for {lang}"
print("All nueva lista & primera partida states successfully verified.")

print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

