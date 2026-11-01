import re

with open('Pico-park-juego/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace button helper functions (lines 1860 - 2068)
old_helpers = '''    _cache_botones_modo = {}

    def _obtener_boton_modo(tipo, estado, idioma):
        tipo_norm = "nueva" if tipo in ("nueva", "nueva_partida") else tipo
        if idioma != "zh":
            if tipo_norm == "continuar":
                if estado == "hover": return spr_continuar_hover
                if estado == "semi": return spr_continuar_semi
                if estado == "apretado": return spr_continuar_apretado
                return spr_continuar_normal
            else:
                if estado == "hover": return spr_nueva_modo_hover
                if estado == "semi": return spr_nueva_modo_semi
                if estado == "apretado": return spr_nueva_modo_apretado
                return spr_nueva_modo_normal

        clave = (tipo_norm, estado, idioma)
        if clave in _cache_botones_modo:
            return _cache_botones_modo[clave]

        if tipo_norm == "continuar":
            base_path = "Menu/boton-continuar-cargar....png"
            if estado == "semi": base_path = "Menu/boton-continuar-cargar...-semiapretado.png"
            elif estado == "apretado": base_path = "Menu/boton-continuar-cargar...-apretado.png"
            col_bg = (155, 255, 124)
            col_tit = (18, 55, 24)
            col_sub = (25, 75, 30)
            tit = t("continuar")
            sub = t("sub_continuar")
        else:
            base_path = "mundos/boton-nueva-partida-reiniciar....png"
            if estado == "semi": base_path = "mundos/boton-nueva-partida-reiniciar...-semiapretado.png"
            elif estado == "apretado": base_path = "mundos/boton-nueva-partida-reiniciar...-apretado.png"
            col_bg = (254, 137, 134)
            col_tit = (95, 25, 35)
            col_sub = (115, 30, 42)
            tit = t("nueva_partida")
            sub = t("sub_nueva_partida")

        w, h = W_MODO, H_MODO
        btn_base = cargar_boton_escalado(base_path, w, h)
        if not btn_base:
            btn_base = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", w, h)
        surf = btn_base.copy()

        # Limpiar suavemente solo la cara interior manteniendo intactos los bordes y biseles 3D
        rect_interior = pygame.Rect(6, 6, w - 12, 68)
        pygame.draw.rect(surf, col_bg, rect_interior)

        f_tit = obtener_fuente_cjk(28, negrita=True)
        f_sub = obtener_fuente_cjk(14, negrita=False)
        t_tit = f_tit.render(tit, True, col_tit)
        t_sub = f_sub.render(sub, True, col_sub)

        offset_y = 1 if estado == "semi" else (2 if estado == "apretado" else 0)
        r_tit = t_tit.get_rect(center=(w // 2, 33 + offset_y))
        surf.blit(t_tit, r_tit)

        r_sub = t_sub.get_rect(center=(w // 2, 59 + offset_y))
        surf.blit(t_sub, r_sub)

        if estado == "hover":
            surf = aclarar_boton(surf)

        _cache_botones_modo[clave] = surf
        return surf

    def _obtener_boton_volver(estado, idioma, w=W_VOLVER, h=H_VOLVER):
        if idioma != "zh":
            if w == W_VOLVER and h == H_VOLVER:
                if estado == "hover": return spr_volver_modo_hover
                if estado == "semi": return spr_volver_modo_semi
                if estado == "apretado": return spr_volver_modo_apretado
                return spr_volver_modo_normal
            base_p = "mundos/boton-volver.png"
            if estado == "semi": base_p = "mundos/boton-volver-semiapretado.png"
            elif estado == "apretado": base_p = "mundos/boton-volver-apretado.png"
            btn = cargar_boton_escalado(base_p, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
            if estado == "hover":
                btn = aclarar_boton(btn)
            return btn

        base_path = "mundos/boton-volver.png"
        if estado == "semi": base_path = "mundos/boton-volver-semiapretado.png"
        elif estado == "apretado": base_path = "mundos/boton-volver-apretado.png"
        btn_base = cargar_boton_escalado(base_path, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
        surf = btn_base.copy()

        col_interior = (212, 212, 212) if estado != "semi" and estado != "apretado" else ((200, 200, 200) if estado == "semi" else (181, 181, 181))
        h_face = max(20, int(h * 0.65))
        pygame.draw.rect(surf, col_interior, (6, 6, w - 12, h_face))

        f_zh = obtener_fuente_cjk(18, negrita=True)
        t_zh = f_zh.render(t("volver"), True, (60, 60, 60))
        offset_y = 1 if estado == "semi" else (2 if estado == "apretado" else 0)
        r_zh = t_zh.get_rect(center=(w // 2, (h_face // 2 + 6) + offset_y))
        surf.blit(t_zh, r_zh)
        if estado == "hover":
            surf = aclarar_boton(surf)
        return surf

    def _obtener_boton_nueva_lista(estado, idioma):
        if idioma != "zh":
            if estado == "hover": return spr_nueva_lista_hover
            if estado == "semi": return spr_nueva_lista_semi
            if estado == "apretado": return spr_nueva_lista_apretado
            return spr_nueva_lista_normal
        base_path = "mundos/boton-nueva-partida.png"
        if estado == "semi": base_path = "mundos/boton-nueva-partida-semiapretado.png"
        elif estado == "apretado": base_path = "mundos/boton-nueva-partida-apretado.png"
        btn_base = cargar_boton_escalado(base_path, W_VOLVER, H_VOLVER) or cargar_boton_escalado("mundos/boton-nueva-partida.png", W_VOLVER, H_VOLVER)
        surf = btn_base.copy()

        col_interior = (255, 159, 99) if estado != "semi" and estado != "apretado" else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        pygame.draw.rect(surf, col_interior, (6, 6, W_VOLVER - 12, 45))

        f_zh = obtener_fuente_cjk(18, negrita=True)
        t_zh = f_zh.render(t("nueva_partida"), True, (115, 35, 20))
        offset_y = 1 if estado == "semi" else (2 if estado == "apretado" else 0)
        r_zh = t_zh.get_rect(center=(W_VOLVER // 2, 28 + offset_y))
        surf.blit(t_zh, r_zh)
        if estado == "hover":
            surf = aclarar_boton(surf)
        return surf

    def _obtener_boton_primera_partida(estado, idioma):
        if idioma != "zh":
            if estado == "hover": return spr_nueva_primera_hover
            if estado == "semi": return spr_nueva_primera_semi
            if estado == "apretado": return spr_nueva_primera_apretado
            return spr_nueva_primera_normal
        base_path = "mundos/boton-nueva-partida.png"
        if estado == "semi": base_path = "mundos/boton-nueva-partida-semiapretado.png"
        elif estado == "apretado": base_path = "mundos/boton-nueva-partida-apretado.png"
        btn_base = cargar_boton_escalado(base_path, 272, 80) or cargar_boton_escalado("mundos/boton-nueva-partida.png", 272, 80)
        surf = btn_base.copy()
        col_interior = (255, 159, 99) if estado != "semi" and estado != "apretado" else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        pygame.draw.rect(surf, col_interior, (6, 6, 272 - 12, 52))
        f_zh = obtener_fuente_cjk(20, negrita=True)
        t_zh = f_zh.render(t("comenzar_aventura"), True, (115, 35, 20))
        offset_y = 1 if estado == "semi" else (2 if estado == "apretado" else 0)
        surf.blit(t_zh, t_zh.get_rect(center=(136, 32 + offset_y)))
        if estado == "hover":
            surf = aclarar_boton(surf)
        return surf

    _cache_sprites_tarjeta = {}

    def _obtener_sprites_tarjeta(idioma):
        if idioma == "es":
            return dict_sprites_tarjeta
        if idioma in _cache_sprites_tarjeta:
            return _cache_sprites_tarjeta[idioma]

        sp_c_n = generar_boton_con_texto("mundos/boton-cargar.png", 126, 38, t("cargar"), (26, 83, 29), 14, 0, idioma)
        sp_c_h = aclarar_boton(sp_c_n)
        sp_c_s = generar_boton_con_texto("mundos/boton-cargar-semiapretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 1, idioma)
        sp_c_a = generar_boton_con_texto("mundos/boton-cargar-apretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 2, idioma)

        sp_g_n = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, t("gestionar"), (60, 45, 30), 13, 0, idioma)
        sp_g_h = aclarar_boton(sp_g_n)
        sp_g_s = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, t("gestionar"), (60, 45, 30), 13, 1, idioma)
        sp_g_a = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, t("gestionar"), (60, 45, 30), 13, 2, idioma)

        sp_b_n = generar_boton_con_texto("Menu/salir.png", 96, 38, t("borrar"), (255, 255, 255), 14, 0, idioma)
        sp_b_h = aclarar_boton(sp_b_n)
        sp_b_s = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, t("borrar"), (255, 255, 255), 14, 1, idioma)
        sp_b_a = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, t("borrar"), (255, 255, 255), 14, 2, idioma)

        res = {
            "cargar_normal": sp_c_n,
            "cargar_hover": sp_c_h,
            "cargar_semi": sp_c_s,
            "cargar_apretado": sp_c_a,
            "gestionar_normal": sp_g_n,
            "gestionar_hover": sp_g_h,
            "gestionar_semi": sp_g_s,
            "gestionar_apretado": sp_g_a,
            "borrar_normal": sp_b_n,
            "borrar_hover": sp_b_h,
            "borrar_semi": sp_b_s,
            "borrar_apretado": sp_b_a,
        }
        _cache_sprites_tarjeta[idioma] = res
        return res

    def _obtener_botones_menu_principal(idioma):
        if idioma != "zh":
            return [
                (btn_jugar, spr_jugar_normal, spr_jugar_hover),
                (btn_personajes, spr_personajes_normal, spr_personajes_hover),
                (btn_config, spr_opciones_normal, spr_opciones_hover),
                (btn_salir, spr_salir_normal, spr_salir_hover),
            ]
        bj_n = generar_boton_con_texto("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON, t("jugar"), (27, 82, 36), 26, 0, idioma)
        bj_h = aclarar_boton(bj_n)
        bp_n = generar_boton_con_texto("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON, t("personajes"), (42, 68, 124), 24, 0, idioma)
        bp_h = aclarar_boton(bp_n)
        bc_n = generar_boton_con_texto("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON, t("opciones"), (115, 67, 16), 26, 0, idioma)
        bc_h = aclarar_boton(bc_n)
        bs_n = generar_boton_con_texto("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON, t("salir"), (255, 255, 255), 26, 0, idioma)
        bs_h = aclarar_boton(bs_n)
        return [
            (btn_jugar, bj_n, bj_h),
            (btn_personajes, bp_n, bp_h),
            (btn_config, bc_n, bc_h),
            (btn_salir, bs_n, bs_h),
        ]'''

new_helpers = '''    _cache_botones_modo = {}
    _cache_botones_volver = {}
    _cache_botones_nueva_lista = {}
    _cache_botones_primera = {}
    _cache_sprites_tarjeta = {}
    _cache_botones_menu = {}

    def _obtener_boton_modo(tipo, estado, idioma):
        tipo_norm = "nueva" if tipo in ("nueva", "nueva_partida") else tipo
        if idioma == "es":
            if tipo_norm == "continuar":
                if estado == "hover": return spr_continuar_hover
                if estado == "semi": return spr_continuar_semi
                if estado == "apretado": return spr_continuar_apretado
                return spr_continuar_normal
            else:
                if estado == "hover": return spr_nueva_modo_hover
                if estado == "semi": return spr_nueva_modo_semi
                if estado == "apretado": return spr_nueva_modo_apretado
                return spr_nueva_modo_normal

        clave = (tipo_norm, estado, idioma)
        if clave in _cache_botones_modo:
            return _cache_botones_modo[clave]

        if tipo_norm == "continuar":
            base_path = "Menu/boton-continuar-cargar....png"
            if estado == "semi": base_path = "Menu/boton-continuar-cargar...-semiapretado.png"
            elif estado == "apretado": base_path = "Menu/boton-continuar-cargar...-apretado.png"
            col_bg = (155, 255, 124) if estado not in ("semi", "apretado") else ((142, 237, 115) if estado == "semi" else (124, 211, 103))
            col_tit = (18, 55, 24)
            col_sub = (25, 75, 30)
            tit = t("continuar")
            sub = t("sub_continuar")
        else:
            base_path = "mundos/boton-nueva-partida-reiniciar....png"
            if estado == "semi": base_path = "mundos/boton-nueva-partida-reiniciar...-semiapretado.png"
            elif estado == "apretado": base_path = "mundos/boton-nueva-partida-reiniciar...-apretado.png"
            col_bg = (254, 137, 134) if estado not in ("semi", "apretado") else ((242, 126, 123) if estado == "semi" else (225, 114, 112))
            col_tit = (95, 25, 35)
            col_sub = (115, 30, 42)
            tit = t("nueva_partida")
            sub = t("sub_nueva_partida")

        w, h = W_MODO, H_MODO
        btn_base = cargar_boton_escalado(base_path, w, h)
        if not btn_base:
            btn_base = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", w, h)
        surf = btn_base.copy()

        # Limpiar suavemente solo la cara interior manteniendo intactos los bordes y biseles 3D
        rect_interior = pygame.Rect(6, 6, w - 12, 68)
        pygame.draw.rect(surf, col_bg, rect_interior)

        if idioma == "zh":
            f_tit = obtener_fuente_cjk(28, negrita=True)
            f_sub = obtener_fuente_cjk(14, negrita=False)
        else:
            f_tit = obtener_fuente_para_texto(tit, categoria="boton", tamano=24, negrita=True)
            f_sub = obtener_fuente_para_texto(sub, categoria="texto", tamano=12, negrita=False)

        t_tit = f_tit.render(tit, True, col_tit)
        t_sub = f_sub.render(sub, True, col_sub)

        offset_y = 1 if estado == "semi" else (2 if estado == "apretado" else 0)
        r_tit = t_tit.get_rect(center=(w // 2, 33 + offset_y))
        surf.blit(t_tit, r_tit)

        r_sub = t_sub.get_rect(center=(w // 2, 59 + offset_y))
        surf.blit(t_sub, r_sub)

        if estado == "hover":
            surf = aclarar_boton(surf)

        _cache_botones_modo[clave] = surf
        return surf

    def _obtener_boton_volver(estado, idioma, w=W_VOLVER, h=H_VOLVER):
        if idioma == "es":
            if w == W_VOLVER and h == H_VOLVER:
                if estado == "hover": return spr_volver_modo_hover
                if estado == "semi": return spr_volver_modo_semi
                if estado == "apretado": return spr_volver_modo_apretado
                return spr_volver_modo_normal
            base_p = "mundos/boton-volver.png"
            if estado == "semi": base_p = "mundos/boton-volver-semiapretado.png"
            elif estado == "apretado": base_p = "mundos/boton-volver-apretado.png"
            btn = cargar_boton_escalado(base_p, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
            if estado == "hover":
                btn = aclarar_boton(btn)
            return btn

        clave = (estado, idioma, w, h)
        if clave in _cache_botones_volver:
            return _cache_botones_volver[clave]

        base_path = "mundos/boton-volver.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-volver-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-volver-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
        surf = btn_base.copy()

        col_interior = (212, 212, 212) if estado not in ("semi", "apretado") else ((200, 200, 200) if estado == "semi" else (181, 181, 181))
        h_face = max(20, int(h * 0.65))
        pygame.draw.rect(surf, col_interior, (6, 6, w - 12, h_face))

        txt_v = t("volver")
        if idioma == "zh":
            f_v = obtener_fuente_cjk(18, negrita=True)
        else:
            f_v = obtener_fuente_para_texto(txt_v, categoria="boton", tamano=18, negrita=True)

        t_v = f_v.render(txt_v, True, (60, 60, 60))
        r_v = t_v.get_rect(center=(w // 2, (h_face // 2 + 6) + offset_y))
        surf.blit(t_v, r_v)

        if estado == "hover":
            surf = aclarar_boton(surf)

        _cache_botones_volver[clave] = surf
        return surf

    def _obtener_boton_nueva_lista(estado, idioma):
        if idioma == "es":
            if estado == "hover": return spr_nueva_lista_hover
            if estado == "semi": return spr_nueva_lista_semi
            if estado == "apretado": return spr_nueva_lista_apretado
            return spr_nueva_lista_normal

        clave = (estado, idioma)
        if clave in _cache_botones_nueva_lista:
            return _cache_botones_nueva_lista[clave]

        base_path = "mundos/boton-nueva-partida.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-nueva-partida-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-nueva-partida-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, W_VOLVER, H_VOLVER) or cargar_boton_escalado("mundos/boton-nueva-partida.png", W_VOLVER, H_VOLVER)
        surf = btn_base.copy()

        col_interior = (255, 159, 99) if estado not in ("semi", "apretado") else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        pygame.draw.rect(surf, col_interior, (6, 6, W_VOLVER - 12, 45))

        txt_nl = t("nueva_partida")
        if idioma == "zh":
            f_nl = obtener_fuente_cjk(18, negrita=True)
        else:
            f_nl = obtener_fuente_para_texto(txt_nl, categoria="boton", tamano=16, negrita=True)

        t_nl = f_nl.render(txt_nl, True, (115, 35, 20))
        r_nl = t_nl.get_rect(center=(W_VOLVER // 2, 28 + offset_y))
        surf.blit(t_nl, r_nl)

        if estado == "hover":
            surf = aclarar_boton(surf)

        _cache_botones_nueva_lista[clave] = surf
        return surf

    def _obtener_boton_primera_partida(estado, idioma):
        if idioma == "es":
            if estado == "hover": return spr_nueva_primera_hover
            if estado == "semi": return spr_nueva_primera_semi
            if estado == "apretado": return spr_nueva_primera_apretado
            return spr_nueva_primera_normal

        clave = (estado, idioma)
        if clave in _cache_botones_primera:
            return _cache_botones_primera[clave]

        base_path = "mundos/boton-nueva-partida.png"
        offset_y = 0
        if estado == "semi":
            base_path = "mundos/boton-nueva-partida-semiapretado.png"
            offset_y = 1
        elif estado == "apretado":
            base_path = "mundos/boton-nueva-partida-apretado.png"
            offset_y = 2

        btn_base = cargar_boton_escalado(base_path, 272, 80) or cargar_boton_escalado("mundos/boton-nueva-partida.png", 272, 80)
        surf = btn_base.copy()
        col_interior = (255, 159, 99) if estado not in ("semi", "apretado") else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
        pygame.draw.rect(surf, col_interior, (6, 6, 272 - 12, 52))

        txt_p = t("comenzar_aventura")
        if idioma == "zh":
            f_p = obtener_fuente_cjk(20, negrita=True)
        else:
            f_p = obtener_fuente_para_texto(txt_p, categoria="boton", tamano=18, negrita=True)

        t_p = f_p.render(txt_p, True, (115, 35, 20))
        offset_y_val = 1 if estado == "semi" else (2 if estado == "apretado" else 0)
        surf.blit(t_p, t_p.get_rect(center=(136, 32 + offset_y_val)))

        if estado == "hover":
            surf = aclarar_boton(surf)

        _cache_botones_primera[clave] = surf
        return surf

    def _obtener_sprites_tarjeta(idioma):
        if idioma == "es":
            return dict_sprites_tarjeta
        if idioma in _cache_sprites_tarjeta:
            return _cache_sprites_tarjeta[idioma]

        sp_c_n = generar_boton_con_texto("mundos/boton-cargar.png", 126, 38, t("cargar"), (26, 83, 29), 14, 0, idioma)
        sp_c_h = aclarar_boton(sp_c_n)
        sp_c_s = generar_boton_con_texto("mundos/boton-cargar-semiapretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 1, idioma)
        sp_c_a = generar_boton_con_texto("mundos/boton-cargar-apretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 2, idioma)

        sp_g_n = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, t("gestionar"), (60, 45, 30), 13, 0, idioma)
        sp_g_h = aclarar_boton(sp_g_n)
        sp_g_s = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, t("gestionar"), (60, 45, 30), 13, 1, idioma)
        sp_g_a = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, t("gestionar"), (60, 45, 30), 13, 2, idioma)

        sp_b_n = generar_boton_con_texto("Menu/salir.png", 96, 38, t("borrar"), (255, 255, 255), 14, 0, idioma)
        sp_b_h = aclarar_boton(sp_b_n)
        sp_b_s = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, t("borrar"), (255, 255, 255), 14, 1, idioma)
        sp_b_a = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, t("borrar"), (255, 255, 255), 14, 2, idioma)

        res = {
            "cargar_normal": sp_c_n,
            "cargar_hover": sp_c_h,
            "cargar_semi": sp_c_s,
            "cargar_apretado": sp_c_a,
            "gestionar_normal": sp_g_n,
            "gestionar_hover": sp_g_h,
            "gestionar_semi": sp_g_s,
            "gestionar_apretado": sp_g_a,
            "borrar_normal": sp_b_n,
            "borrar_hover": sp_b_h,
            "borrar_semi": sp_b_s,
            "borrar_apretado": sp_b_a,
        }
        _cache_sprites_tarjeta[idioma] = res
        return res

    def _obtener_boton_menu_principal_estado(tipo, estado, idioma):
        if idioma == "es":
            if tipo == "jugar":
                if estado == "hover": return spr_jugar_hover
                if estado == "semi": return spr_jugar_semi
                if estado == "apretado": return spr_jugar_apretado
                return spr_jugar_normal
            elif tipo == "personajes":
                if estado == "hover": return spr_personajes_hover
                if estado == "semi": return spr_personajes_semi
                if estado == "apretado": return spr_personajes_apretado
                return spr_personajes_normal
            elif tipo == "opciones":
                if estado == "hover": return spr_opciones_hover
                if estado == "semi": return spr_opciones_semi
                if estado == "apretado": return spr_opciones_apretado
                return spr_opciones_normal
            elif tipo == "salir":
                if estado == "hover": return spr_salir_hover
                if estado == "semi": return spr_salir_semi
                if estado == "apretado": return spr_salir_apretado
                return spr_salir_normal

        clave = (tipo, estado, idioma)
        if clave in _cache_botones_menu:
            return _cache_botones_menu[clave]

        cfg_botones = {
            "jugar": ("Menu/jugar", (27, 82, 36), 26),
            "personajes": ("Menu/personajes", (42, 68, 124), 22 if idioma == "en" else 24),
            "opciones": ("Menu/opciones", (115, 67, 16), 26),
            "salir": ("Menu/salir", (255, 255, 255), 26),
        }
        base_name, col_txt, sz = cfg_botones[tipo]

        if estado == "normal":
            sprite_path = f"{base_name}.png"
            offset_y = 0
            surf = generar_boton_con_texto(sprite_path, ANCHO_BOTON, ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        elif estado == "hover":
            norm = _obtener_boton_menu_principal_estado(tipo, "normal", idioma)
            surf = aclarar_boton(norm)
        elif estado == "semi":
            pre_name = f"{base_name}-preapretado.png"
            sprite_path = pre_name
            offset_y = 1
            surf = generar_boton_con_texto(sprite_path, ANCHO_BOTON, ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        elif estado == "apretado":
            apr_name = f"{base_name}-apretado.png"
            sprite_path = apr_name
            offset_y = 2
            surf = generar_boton_con_texto(sprite_path, ANCHO_BOTON, ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
        else:
            surf = None

        _cache_botones_menu[clave] = surf
        return surf

    def _obtener_botones_menu_principal(idioma):
        return [
            (btn_jugar, _obtener_boton_menu_principal_estado("jugar", "normal", idioma), _obtener_boton_menu_principal_estado("jugar", "hover", idioma)),
            (btn_personajes, _obtener_boton_menu_principal_estado("personajes", "normal", idioma), _obtener_boton_menu_principal_estado("personajes", "hover", idioma)),
            (btn_config, _obtener_boton_menu_principal_estado("opciones", "normal", idioma), _obtener_boton_menu_principal_estado("opciones", "hover", idioma)),
            (btn_salir, _obtener_boton_menu_principal_estado("salir", "normal", idioma), _obtener_boton_menu_principal_estado("salir", "hover", idioma)),
        ]'''

assert old_helpers in content, 'old_helpers not found!'
content = content.replace(old_helpers, new_helpers)

# 2. Add _ultimo_idioma_menu before the main while loop
old_state_def = '    estado_actual = ESTADO_MENU_PRINCIPAL\n    mundo_seleccionado = 1\n    ejecutando = True'
new_state_def = '    estado_actual = ESTADO_MENU_PRINCIPAL\n    mundo_seleccionado = 1\n    ejecutando = True\n    _ultimo_idioma_menu = obtener_idioma()'
assert old_state_def in content, 'old_state_def not found'
content = content.replace(old_state_def, new_state_def)

# 3. In the while loop, check if language changed to clear caches
old_tick = '    while ejecutando:\n        reloj.tick(FPS)\n        reproducir_musica("menu")'
new_tick = '''    while ejecutando:
        reloj.tick(FPS)
        reproducir_musica("menu")

        idm_act = obtener_idioma()
        if idm_act != _ultimo_idioma_menu:
            _cache_botones_menu.clear()
            _cache_botones_modo.clear()
            _cache_botones_volver.clear()
            _cache_botones_nueva_lista.clear()
            _cache_botones_primera.clear()
            _cache_sprites_tarjeta.clear()
            _ultimo_idioma_menu = idm_act'''
assert old_tick in content, 'old_tick not found'
content = content.replace(old_tick, new_tick)

# 4. In ESTADO_MENU_PRINCIPAL, animate with localized sprites
old_menu_clicks = '''                if estado_actual == ESTADO_MENU_PRINCIPAL:
                    _asegurar_semi_apretados_menu()
                    if btn_jugar.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_jugar)
                        if animar_pulsacion_boton(pantalla, btn_jugar, spr_jugar_semi, spr_jugar_apretado, f_limp, spr_jugar_normal):
                            estado_actual = ESTADO_MODO_JUEGO
                    elif btn_personajes.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_personajes)
                        if animar_pulsacion_boton(pantalla, btn_personajes, spr_personajes_semi, spr_personajes_apretado, f_limp, spr_personajes_normal):
                            estado_actual = ESTADO_PERSONAJES
                    elif btn_config.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_config)
                        if animar_pulsacion_boton(pantalla, btn_config, spr_opciones_semi, spr_opciones_apretado, f_limp, spr_opciones_normal):
                            mostrar_pestana_configuracion(pantalla, reloj)
                            break
                    elif btn_salir.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_salir)
                        if animar_pulsacion_boton(pantalla, btn_salir, spr_salir_semi, spr_salir_apretado, f_limp, spr_salir_normal):
                            intentar_salir()'''

new_menu_clicks = '''                if estado_actual == ESTADO_MENU_PRINCIPAL:
                    _asegurar_semi_apretados_menu()
                    idm_act = obtener_idioma()
                    if btn_jugar.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_jugar)
                        sp_s = _obtener_boton_menu_principal_estado("jugar", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("jugar", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("jugar", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_jugar, sp_s, sp_a, f_limp, sp_n):
                            estado_actual = ESTADO_MODO_JUEGO
                    elif btn_personajes.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_personajes)
                        sp_s = _obtener_boton_menu_principal_estado("personajes", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("personajes", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("personajes", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_personajes, sp_s, sp_a, f_limp, sp_n):
                            estado_actual = ESTADO_PERSONAJES
                    elif btn_config.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_config)
                        sp_s = _obtener_boton_menu_principal_estado("opciones", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("opciones", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("opciones", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_config, sp_s, sp_a, f_limp, sp_n):
                            mostrar_pestana_configuracion(pantalla, reloj)
                            break
                    elif btn_salir.collidepoint(evento.pos):
                        f_limp = gestor_personajes_menu.fondo_estatico.subsurface(btn_salir)
                        sp_s = _obtener_boton_menu_principal_estado("salir", "semi", idm_act)
                        sp_a = _obtener_boton_menu_principal_estado("salir", "apretado", idm_act)
                        sp_n = _obtener_boton_menu_principal_estado("salir", "normal", idm_act)
                        if animar_pulsacion_boton(pantalla, btn_salir, sp_s, sp_a, f_limp, sp_n):
                            intentar_salir()'''

assert old_menu_clicks in content, 'old_menu_clicks not found'
content = content.replace(old_menu_clicks, new_menu_clicks)

# 5. In ESTADO_CONFIGURACION and ESTADO_CREDITOS, use localized volver
old_volver_cfg = '''                elif estado_actual == ESTADO_CONFIGURACION:
                    if btn_volver_config.collidepoint(evento.pos):
                        pulsado = True
                        if spr_volver_semi and spr_volver_apretado:
                            pulsado = animar_pulsacion_boton(pantalla, btn_volver_config, spr_volver_semi, spr_volver_apretado, (30, 30, 30), spr_volver_normal)
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual == ESTADO_CREDITOS:
                    if btn_volver_creditos.collidepoint(evento.pos):
                        pulsado = True
                        if spr_volver_semi and spr_volver_apretado:
                            pulsado = animar_pulsacion_boton(pantalla, btn_volver_creditos, spr_volver_semi, spr_volver_apretado, (30, 30, 30), spr_volver_normal)
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL'''

new_volver_cfg = '''                elif estado_actual == ESTADO_CONFIGURACION:
                    idm_act = obtener_idioma()
                    if btn_volver_config.collidepoint(evento.pos):
                        sp_v_s = _obtener_boton_volver("semi", idm_act)
                        sp_v_a = _obtener_boton_volver("apretado", idm_act)
                        sp_v_n = _obtener_boton_volver("normal", idm_act)
                        pulsado = animar_pulsacion_boton(pantalla, btn_volver_config, sp_v_s, sp_v_a, (30, 30, 30), sp_v_n)
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL

                elif estado_actual == ESTADO_CREDITOS:
                    idm_act = obtener_idioma()
                    if btn_volver_creditos.collidepoint(evento.pos):
                        sp_v_s = _obtener_boton_volver("semi", idm_act)
                        sp_v_a = _obtener_boton_volver("apretado", idm_act)
                        sp_v_n = _obtener_boton_volver("normal", idm_act)
                        pulsado = animar_pulsacion_boton(pantalla, btn_volver_creditos, sp_v_s, sp_v_a, (30, 30, 30), sp_v_n)
                        if pulsado:
                            estado_actual = ESTADO_MENU_PRINCIPAL'''

assert old_volver_cfg in content, 'old_volver_cfg not found'
content = content.replace(old_volver_cfg, new_volver_cfg)

# 6. In drawing ESTADO_CONFIGURACION and ESTADO_CREDITOS, use localized volver
old_draw_cfg = '''            # Botón Volver al Menú (mundos/boton-volver)
            hov_vcfg = btn_volver_config.collidepoint(pos_mouse)
            spr_vcfg = spr_volver_hover if (hov_vcfg and spr_volver_hover) else spr_volver_normal
            if spr_vcfg:
                pantalla.blit(spr_vcfg, btn_volver_config)

        elif estado_actual == ESTADO_CREDITOS:
            pos_mouse = pygame.mouse.get_pos()
            titulo = fuente_pixel_titulo.render("CREDITOS", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            cred = fuente_texto.render("Desarrollado para Pico Park Fan Project", True, (200, 200, 200))
            pantalla.blit(cred, cred.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2)))

            # Botón Volver al Menú (mundos/boton-volver)
            hov_vcr = btn_volver_creditos.collidepoint(pos_mouse)
            spr_vcr = spr_volver_hover if (hov_vcr and spr_volver_hover) else spr_volver_normal
            if spr_vcr:
                pantalla.blit(spr_vcr, btn_volver_creditos)'''

new_draw_cfg = '''            # Botón Volver al Menú (mundos/boton-volver)
            idm_act = obtener_idioma()
            hov_vcfg = btn_volver_config.collidepoint(pos_mouse)
            spr_vcfg_norm = _obtener_boton_volver("normal", idm_act)
            spr_vcfg_hov = _obtener_boton_volver("hover", idm_act)
            spr_vcfg = spr_vcfg_hov if (hov_vcfg and spr_vcfg_hov) else spr_vcfg_norm
            if spr_vcfg:
                pantalla.blit(spr_vcfg, btn_volver_config)

        elif estado_actual == ESTADO_CREDITOS:
            pos_mouse = pygame.mouse.get_pos()
            idm_act = obtener_idioma()
            titulo = fuente_pixel_titulo.render("CREDITOS", True, (255, 255, 255))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_MENU // 2, 100)))

            cred = fuente_texto.render("Desarrollado para Pico Park Fan Project", True, (200, 200, 200))
            pantalla.blit(cred, cred.get_rect(center=(ANCHO_MENU // 2, ALTO_MENU // 2)))

            # Botón Volver al Menú (mundos/boton-volver)
            hov_vcr = btn_volver_creditos.collidepoint(pos_mouse)
            spr_vcr_norm = _obtener_boton_volver("normal", idm_act)
            spr_vcr_hov = _obtener_boton_volver("hover", idm_act)
            spr_vcr = spr_vcr_hov if (hov_vcr and spr_vcr_hov) else spr_vcr_norm
            if spr_vcr:
                pantalla.blit(spr_vcr, btn_volver_creditos)'''

assert old_draw_cfg in content, 'old_draw_cfg not found'
content = content.replace(old_draw_cfg, new_draw_cfg)

with open('Pico-park-juego/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully patched main.py!')

