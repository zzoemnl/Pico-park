import os
import sys
import pygame

sys.path.insert(0, "Pico-park-juego")
sys.path.insert(0, "Pico-park-juego/scratch")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

import main
import guardado
import sprites
from fuentes import (
    obtener_fuente,
    obtener_fuente_subtitulo,
    obtener_fuente_pequena,
    obtener_fuente_contador,
    obtener_fuente_boton,
    dibujar_texto_en_rect,
)

# Load real button sprites
dict_sprites = {
    "cargar_normal": sprites.cargar_boton_escalado("mundos/boton-cargar.png", 126, 38),
    "cargar_hover": None,
    "gestionar_normal": sprites.cargar_boton_escalado("mundos/boton-gestionar.png", 118, 38),
    "gestionar_hover": None,
    "borrar_normal": sprites.cargar_boton_escalado("mundos/boton-borrar.png", 96, 38),
    "borrar_hover": None,
}

from test_layout_partidas import (
    dibujar_icono_estrella,
    dibujar_icono_trofeo,
    dibujar_icono_calendario,
    dibujar_icono_reloj,
)

def render_test_tarjeta(pantalla, p, idx_slot, rect_panel, tam_meta=28, alto_card=86, gap_cards=8):
    r_card = pygame.Rect(
        rect_panel.left + 20,
        rect_panel.top + 14 + idx_slot * (alto_card + gap_cards),
        rect_panel.width - 40,
        alto_card,
    )
    
    # 1. Base card
    col_card = (253, 248, 238)
    borde_card = (185, 150, 110)
    pygame.draw.rect(pantalla, col_card, r_card, border_radius=12)
    pygame.draw.rect(pantalla, borde_card, r_card, width=2, border_radius=12)
    pygame.draw.rect(pantalla, (235, 220, 195), r_card.inflate(-6, -6), width=1, border_radius=8)
    # Lomo decorativo
    col_tira = (160, 120, 80)
    pygame.draw.rect(pantalla, col_tira, (r_card.left + 3, r_card.top + 8, 4, r_card.height - 16), border_radius=2)
    
    # 2. Sello Badge de Mundo
    w_badge, h_badge = 112, 50
    r_badge = pygame.Rect(r_card.left + 16, r_card.centery - (h_badge // 2), w_badge, h_badge)
    m_val = p.get("mundo_max", 1)
    info_b = main.COLORES_TABS.get(m_val, main.COLORES_TABS[1])
    pygame.draw.rect(pantalla, info_b["fondo"], r_badge, border_radius=8)
    pygame.draw.rect(pantalla, info_b["borde"], r_badge, width=2, border_radius=8)
    pygame.draw.rect(pantalla, (245, 235, 220), r_badge.inflate(-4, -4), width=1, border_radius=6)
    f_badge = obtener_fuente("badge", 13)
    t_badge = f_badge.render(f"MUNDO {m_val}", True, info_b["texto"])
    pantalla.blit(t_badge, t_badge.get_rect(center=r_badge.center))
    
    # 3. Botones a la derecha
    w_borrar = 96
    w_gestionar = 118
    w_cargar = 126
    h_btn = 38
    gap_btns = 10
    margin_der = 16
    
    r_btn_borrar = pygame.Rect(r_card.right - margin_der - w_borrar, r_card.centery - (h_btn // 2), w_borrar, h_btn)
    r_btn_gestionar = pygame.Rect(r_btn_borrar.left - gap_btns - w_gestionar, r_card.centery - (h_btn // 2), w_gestionar, h_btn)
    r_btn_cargar = pygame.Rect(r_btn_gestionar.left - gap_btns - w_cargar, r_card.centery - (h_btn // 2), w_cargar, h_btn)
    
    if dict_sprites["cargar_normal"]:
        pantalla.blit(dict_sprites["cargar_normal"], r_btn_cargar)
    if dict_sprites["gestionar_normal"]:
        pantalla.blit(dict_sprites["gestionar_normal"], r_btn_gestionar)
    if dict_sprites["borrar_normal"]:
        pantalla.blit(dict_sprites["borrar_normal"], r_btn_borrar)
        
    # 4. Zona de texto
    x_texto = r_badge.right + 18
    x_limite_texto = r_btn_cargar.left - 14
    ancho_max_texto = max(80, x_limite_texto - x_texto)
    
    nombre = p.get("nombre", f"Partida {p.get('id', 1)}")
    mundo_max = p.get("mundo_max", 1)
    nivel_max = p.get("nivel_max", 1)
    fecha = p.get("fecha", "")
    cant_comp = main.calcular_niveles_completados(p.get("niveles_desbloqueados", {}))
    tiene_pwd = p.get("tiene_password", False)
    
    # Símbolo decorativo de diamante
    diam_cx = x_texto + 4
    diam_cy = r_card.top + 16
    for d_diam in range(-4, 5):
        w_diam = 4 - abs(d_diam)
        for dx in range(-w_diam, w_diam + 1):
            c_d = (245, 215, 110) if (d_diam <= 0 and dx <= 0) else (210, 145, 35)
            pantalla.set_at((diam_cx + dx, diam_cy + d_diam), c_d)
            
    # FILA 1: Nombre de la partida
    cur_x_tit = x_texto + 16
    if tiene_pwd:
        main._dibujar_icono_candado(pantalla, cur_x_tit + 3, r_card.top + 16, abierto=False)
        cur_x_tit += 14
    rect_tit = pygame.Rect(cur_x_tit, r_card.top + 6, ancho_max_texto - (cur_x_tit - x_texto), 24)
    dibujar_texto_en_rect(pantalla, nombre, rect_tit, categoria="subtitulo", tamano=21, color=(55, 42, 30), negrita=True, alineacion="izquierda", padding=0)
    
    # FILA 2: Nivel alcanzado + Progreso (ampliados ~60-70% a tamaño tam_meta)
    f_meta = obtener_fuente_pequena(tam_meta)
    y_fila2 = r_card.top + 33
    cur_x = x_texto + 4
    
    # Gema nivel
    dibujar_icono_estrella(pantalla, cur_x + 5, y_fila2 + 10)
    cur_x += 16
    t_niv = f_meta.render(f"Nivel {mundo_max}-{nivel_max}", True, (90, 60, 40))
    pantalla.blit(t_niv, (cur_x, y_fila2))
    cur_x += t_niv.get_width() + 14
    
    # Separador sutil
    pygame.draw.circle(pantalla, (190, 160, 130), (cur_x, y_fila2 + 10), 2)
    cur_x += 10
    
    # Trofeo completados
    dibujar_icono_trofeo(pantalla, cur_x + 6, y_fila2 + 10)
    cur_x += 18
    t_comp = f_meta.render(f"{cant_comp}/15 completados", True, (105, 80, 55))
    pantalla.blit(t_comp, (cur_x, y_fila2))
    
    # FILA 3: Fecha + Hora
    partes_f = fecha.strip().split(" ") if fecha else []
    str_fecha = partes_f[0] if len(partes_f) > 0 else ""
    str_hora = partes_f[1] if len(partes_f) > 1 else ""
    
    if str_fecha or str_hora:
        y_fila3 = r_card.top + 57
        cur_x_f3 = x_texto + 4
        
        if str_fecha:
            dibujar_icono_calendario(pantalla, cur_x_f3 + 6, y_fila3 + 10)
            cur_x_f3 += 16
            t_fec = f_meta.render(str_fecha, True, (120, 95, 75))
            pantalla.blit(t_fec, (cur_x_f3, y_fila3))
            cur_x_f3 += t_fec.get_width() + 16
            
        if str_hora:
            dibujar_icono_reloj(pantalla, cur_x_f3 + 6, y_fila3 + 10)
            cur_x_f3 += 16
            t_hor = f_meta.render(str_hora, True, (120, 95, 75))
            pantalla.blit(t_hor, (cur_x_f3, y_fila3))

# Test render
pantalla = pygame.Surface((1280, 720))
pantalla.fill((230, 215, 195))
rect_panel, btn_v, btn_n, btn_p = main.obtener_geometria_panel_partidas(1280, 720, True)

# Draw panel
pygame.draw.rect(pantalla, (252, 246, 235), rect_panel, border_radius=16)
pygame.draw.rect(pantalla, (190, 160, 125), rect_panel, width=3, border_radius=16)
pygame.draw.rect(pantalla, (225, 200, 160), rect_panel.inflate(-8, -8), width=1, border_radius=12)

test_partidas = [
    {
        "id": 1,
        "nombre": "Todos los niveles desbloqueados",
        "mundo_max": 3,
        "nivel_max": 5,
        "fecha": "26/10/2026 12:00",
        "niveles_desbloqueados": {1: [True]*5, 2: [True]*5, 3: [True]*5},
        "tiene_password": False,
    },
    {
        "id": 2,
        "nombre": "Aventura en el Bosque",
        "mundo_max": 1,
        "nivel_max": 4,
        "fecha": "31/10/2026 16:45",
        "niveles_desbloqueados": {1: [True]*4},
        "tiene_password": True,
    },
    {
        "id": 3,
        "nombre": "Expedición Nieve y Hielo",
        "mundo_max": 2,
        "nivel_max": 3,
        "fecha": "30/10/2026 09:15",
        "niveles_desbloqueados": {1: [True]*5, 2: [True]*3},
        "tiene_password": False,
    },
    {
        "id": 4,
        "nombre": "Partida 4",
        "mundo_max": 1,
        "nivel_max": 1,
        "fecha": "31/10/2026 17:30",
        "niveles_desbloqueados": {1: [True]*1},
        "tiene_password": False,
    },
]

for sz in [26, 28, 30]:
    pantalla.fill((230, 215, 195))
    pygame.draw.rect(pantalla, (252, 246, 235), rect_panel, border_radius=16)
    pygame.draw.rect(pantalla, (190, 160, 125), rect_panel, width=3, border_radius=16)
    pygame.draw.rect(pantalla, (225, 200, 160), rect_panel.inflate(-8, -8), width=1, border_radius=12)
    
    for idx, p in enumerate(test_partidas):
        render_test_tarjeta(pantalla, p, idx, rect_panel, tam_meta=sz, alto_card=86, gap_cards=8)
        
    os.makedirs("scratch/test_layout_partidas", exist_ok=True)
    pygame.image.save(pantalla, f"scratch/test_layout_partidas/panel_partidas_tam{sz}.png")
    # Also save a zoom on card 0
    r_c0 = pygame.Rect(rect_panel.left + 20, rect_panel.top + 14, rect_panel.width - 40, 86)
    crop = pantalla.subsurface(r_c0)
    pygame.image.save(crop, f"scratch/test_layout_partidas/card_zoom_tam{sz}.png")
    print(f"Rendered panel at size {sz}!")
