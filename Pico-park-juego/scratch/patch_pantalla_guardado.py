with open('Pico-park-juego/guardado.py', 'r', encoding='utf-8') as f:
    g_content = f.read()

old_g = '''        spr_canc_norm = _cargar_sprite_boton("Menu/boton-cancelar.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar.png", w_btn, h_btn)
        spr_canc_semi = _cargar_sprite_boton("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-semiapretado.png", w_btn, h_btn)
        spr_canc_apret = _cargar_sprite_boton("Menu/boton-cancelar-apretado.png", w_btn, h_btn) or _cargar_sprite_boton("boton-cancelar-apretado.png", w_btn, h_btn)
        spr_canc_hover = aclarar_boton(spr_canc_norm) if spr_canc_norm else None'''

new_g = '''        idm_g = obtener_idioma()
        spr_canc_norm = generar_boton_con_texto("Menu/boton-cancelar.png", w_btn, h_btn, t("cancelar"), (60, 45, 35), TAMANO_BOTON_MODAL, 0, idm_g)
        spr_canc_semi = generar_boton_con_texto("Menu/boton-cancelar-semiapretado.png", w_btn, h_btn, t("cancelar"), (60, 45, 35), TAMANO_BOTON_MODAL, 1, idm_g)
        spr_canc_apret = generar_boton_con_texto("Menu/boton-cancelar-apretado.png", w_btn, h_btn, t("cancelar"), (60, 45, 35), TAMANO_BOTON_MODAL, 2, idm_g)
        spr_canc_hover = aclarar_boton(spr_canc_norm) if spr_canc_norm else None'''

assert old_g in g_content, 'old_g not found in guardado.py'
g_content = g_content.replace(old_g, new_g)

with open('Pico-park-juego/guardado.py', 'w', encoding='utf-8') as f:
    f.write(g_content)
print('Successfully patched guardado.py')

with open('Pico-park-juego/pantalla.py', 'r', encoding='utf-8') as f:
    p_content = f.read()

# 1. Update pantalla_muerte
old_pm = '''    boton_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("salir.png", w_btn, h_btn)
    boton_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-preapretado.png", w_btn, h_btn)
    boton_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-apretado.png", w_btn, h_btn)

    boton_reiniciar_normal = cargar_boton_escalado("Ventanas/boton-reiniciar.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar.png", w_btn, h_btn)
    boton_reiniciar_semi = cargar_boton_escalado("Ventanas/boton-reiniciar-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-semiapretado.png", w_btn, h_btn)
    boton_reiniciar_apretado = cargar_boton_escalado("Ventanas/boton-reiniciar-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-apretado.png", w_btn, h_btn)'''

new_pm = '''    idm_muerte = obtener_idioma()
    if idm_muerte == "es":
        boton_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("salir.png", w_btn, h_btn)
        boton_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-preapretado.png", w_btn, h_btn)
        boton_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("salir-apretado.png", w_btn, h_btn)

        boton_reiniciar_normal = cargar_boton_escalado("Ventanas/boton-reiniciar.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar.png", w_btn, h_btn)
        boton_reiniciar_semi = cargar_boton_escalado("Ventanas/boton-reiniciar-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-semiapretado.png", w_btn, h_btn)
        boton_reiniciar_apretado = cargar_boton_escalado("Ventanas/boton-reiniciar-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-reiniciar-apretado.png", w_btn, h_btn)
    else:
        boton_menu_normal = generar_boton_con_texto("Ventanas/boton-menu.png", w_btn, h_btn, t("menu"), (255, 255, 255), 24, 0, idm_muerte)
        boton_menu_semi = generar_boton_con_texto("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn, t("menu"), (255, 255, 255), 24, 1, idm_muerte)
        boton_menu_apretado = generar_boton_con_texto("Ventanas/boton-menu-apretado.png", w_btn, h_btn, t("menu"), (255, 255, 255), 24, 2, idm_muerte)

        boton_reiniciar_normal = generar_boton_con_texto("Ventanas/boton-reiniciar.png", w_btn, h_btn, t("reiniciar"), (255, 255, 255), 24, 0, idm_muerte)
        boton_reiniciar_semi = generar_boton_con_texto("Ventanas/boton-reiniciar-semiapretado.png", w_btn, h_btn, t("reiniciar"), (255, 255, 255), 24, 1, idm_muerte)
        boton_reiniciar_apretado = generar_boton_con_texto("Ventanas/boton-reiniciar-apretado.png", w_btn, h_btn, t("reiniciar"), (255, 255, 255), 24, 2, idm_muerte)'''

assert old_pm in p_content, 'old_pm not found in pantalla.py'
p_content = p_content.replace(old_pm, new_pm)

# 2. Update mostrar_victoria_nivel
old_pv = '''    spr_sig_normal = cargar_boton_escalado("Ventanas/boton-siguiente.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente.png", w_btn, h_btn)
    spr_sig_semi = cargar_boton_escalado("Ventanas/boton-siguiente-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-semiapretado.png", w_btn, h_btn)
    spr_sig_apretado = cargar_boton_escalado("Ventanas/boton-siguiente-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-apretado.png", w_btn, h_btn)

    spr_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn)
    spr_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn)
    spr_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn)'''

new_pv = '''    idm_vic = obtener_idioma()
    if idm_vic == "es":
        spr_sig_normal = cargar_boton_escalado("Ventanas/boton-siguiente.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente.png", w_btn, h_btn)
        spr_sig_semi = cargar_boton_escalado("Ventanas/boton-siguiente-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-semiapretado.png", w_btn, h_btn)
        spr_sig_apretado = cargar_boton_escalado("Ventanas/boton-siguiente-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-siguiente-apretado.png", w_btn, h_btn)

        spr_menu_normal = cargar_boton_escalado("Ventanas/boton-menu.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu.png", w_btn, h_btn)
        spr_menu_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-semiapretado.png", w_btn, h_btn)
        spr_menu_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", w_btn, h_btn) or cargar_boton_escalado("boton-menu-apretado.png", w_btn, h_btn)
    else:
        spr_sig_normal = generar_boton_con_texto("Ventanas/boton-siguiente.png", w_btn, h_btn, txt_btn1, (255, 255, 255), 24, 0, idm_vic)
        spr_sig_semi = generar_boton_con_texto("Ventanas/boton-siguiente-semiapretado.png", w_btn, h_btn, txt_btn1, (255, 255, 255), 24, 1, idm_vic)
        spr_sig_apretado = generar_boton_con_texto("Ventanas/boton-siguiente-apretado.png", w_btn, h_btn, txt_btn1, (255, 255, 255), 24, 2, idm_vic)

        spr_menu_normal = generar_boton_con_texto("Ventanas/boton-menu.png", w_btn, h_btn, txt_btn2, (255, 255, 255), 20 if idm_vic == "en" else 22, 0, idm_vic)
        spr_menu_semi = generar_boton_con_texto("Ventanas/boton-menu-semiapretado.png", w_btn, h_btn, txt_btn2, (255, 255, 255), 20 if idm_vic == "en" else 22, 1, idm_vic)
        spr_menu_apretado = generar_boton_con_texto("Ventanas/boton-menu-apretado.png", w_btn, h_btn, txt_btn2, (255, 255, 255), 20 if idm_vic == "en" else 22, 2, idm_vic)'''

assert old_pv in p_content, 'old_pv not found in pantalla.py'
p_content = p_content.replace(old_pv, new_pv)

with open('Pico-park-juego/pantalla.py', 'w', encoding='utf-8') as f:
    f.write(p_content)
print('Successfully patched pantalla.py')

