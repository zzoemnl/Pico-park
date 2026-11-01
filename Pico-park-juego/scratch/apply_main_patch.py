import os

with open("Pico-park-juego/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "def obtener_geometria_tarjeta_partida(rect_panel, idx_slot, alto_card=86, gap_cards=8):",
    "def obtener_geometria_tarjeta_partida(rect_panel, idx_slot, alto_card=90, gap_cards=6):"
)
content = content.replace(
    "rect_panel.top + 14 + idx_slot * (alto_card + gap_cards)",
    "rect_panel.top + 12 + idx_slot * (alto_card + gap_cards)"
)
content = content.replace(
    'altura optimizada 86 px',
    'altura optimizada 90 px'
)
content = content.replace(
    'f_datos = fuentes.get("sub_card") or obtener_fuente_pequena(30)',
    'f_datos = fuentes.get("sub_card") or obtener_fuente_pequena(28)'
)
content = content.replace(
    'fuente_card_sub = obtener_fuente_pequena(30)',
    'fuente_card_sub = obtener_fuente_pequena(28)'
)
content = content.replace(
    'y_fila2 = (r_card.top + 33) if tiene_fecha_hora else (r_card.top + 43)',
    'y_fila2 = (r_card.top + 35) if tiene_fecha_hora else (r_card.top + 45)'
)
content = content.replace(
    '_dibujar_icono_estrella_nivel(pantalla, cur_x2 + 5, y_fila2 + 11)',
    '_dibujar_icono_estrella_nivel(pantalla, cur_x2 + 5, y_fila2 + 14)'
)
content = content.replace(
    'pygame.draw.circle(pantalla, (180, 150, 120), (cur_x2, y_fila2 + 11), 2)',
    'pygame.draw.circle(pantalla, (180, 150, 120), (cur_x2, y_fila2 + 14), 2)'
)
content = content.replace(
    '_dibujar_icono_trofeo(pantalla, cur_x2 + 6, y_fila2 + 11)',
    '_dibujar_icono_trofeo(pantalla, cur_x2 + 6, y_fila2 + 14)'
)
content = content.replace(
    'y_fila3 = r_card.top + 57',
    'y_fila3 = r_card.top + 61'
)
content = content.replace(
    '_dibujar_icono_calendario(pantalla, cur_x3 + 6, y_fila3 + 11)',
    '_dibujar_icono_calendario(pantalla, cur_x3 + 6, y_fila3 + 14)'
)
content = content.replace(
    '_dibujar_icono_reloj(pantalla, cur_x3 + 6, y_fila3 + 11)',
    '_dibujar_icono_reloj(pantalla, cur_x3 + 6, y_fila3 + 14)'
)

with open("Pico-park-juego/main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updates applied to main.py!")
