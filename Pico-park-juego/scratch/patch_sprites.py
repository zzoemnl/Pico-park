import re

with open('Pico-park-juego/sprites.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''        curr_sz = tamano_fuente
        if es_cjk:
            f_sys = obtener_fuente_cjk(curr_sz, negrita=True)
            txt_surf = f_sys.render(str(texto), True, color_texto)
            while txt_surf.get_width() > w - 16 and curr_sz > 8:
                curr_sz -= 1
                f_sys = obtener_fuente_cjk(curr_sz, negrita=True)
                txt_surf = f_sys.render(str(texto), True, color_texto)
        else:
            def _render_latin(sz):
                f = obtener_fuente_boton(sz, tamano_fallback=sz, idioma="es")
                if any(ch in "ÑñÁÉÍÓÚáéíóú" for ch in str(texto)):
                    txt_limpio = (
                        str(texto).replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
                                  .replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    )
                    ancho_t, alto_t = f.size(txt_limpio.replace("Ñ", "N").replace("ñ", "n"))
                    t_s = pygame.Surface((ancho_t, alto_t + 4), pygame.SRCALPHA)
                    curr_x = 0
                    for ch in txt_limpio:
                        if ch in ("Ñ", "ñ"):
                            letra = f.render("N" if ch == "Ñ" else "n", True, color_texto)
                            t_s.blit(letra, (curr_x, 3))
                            lw = letra.get_width()
                            pygame.draw.rect(t_s, color_texto, (curr_x + 2, 0, 3, 2))
                            pygame.draw.rect(t_s, color_texto, (curr_x + 5, 1, 3, 2))
                            curr_x += lw
                        else:
                            letra = f.render(ch, True, color_texto)
                            t_s.blit(letra, (curr_x, 3))
                            curr_x += letra.get_width()
                    return f, t_s
                else:
                    return f, f.render(str(texto), True, color_texto)

            f_lat, txt_surf = _render_latin(curr_sz)
            while txt_surf.get_width() > w - 16 and curr_sz > 8:
                curr_sz -= 1
                f_lat, txt_surf = _render_latin(curr_sz)'''

idx1 = content.find('        if es_cjk:\n            f_sys = obtener_fuente_cjk(tamano_fuente, negrita=True)')
idx2 = content.find('        rect_txt = txt_surf.get_rect(center=(w // 2, (h - 4) // 2 + offset_y))')

assert idx1 != -1 and idx2 != -1, f'Indices not found: {idx1}, {idx2}'
new_content = content[:idx1] + replacement + '\n\n' + content[idx2:]
with open('Pico-park-juego/sprites.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Successfully patched sprites.py')

