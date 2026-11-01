import os
import sys
import pygame

sys.path.insert(0, "Pico-park-juego")
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

dict_sprites = {
    "cargar_normal": sprites.cargar_boton_escalado("mundos/boton-cargar.png", 126, 38),
    "cargar_hover": None,
    "gestionar_normal": sprites.cargar_boton_escalado("mundos/boton-gestionar.png", 118, 38),
    "gestionar_hover": None,
    "borrar_normal": sprites.cargar_boton_escalado("mundos/boton-borrar.png", 96, 38),
    "borrar_hover": None,
}

from scratch.test_layout_partidas import (
    dibujar_icono_estrella,
    dibujar_icono_trofeo,
    dibujar_icono_calendario,
    dibujar_icono_reloj,
)

def render_tarjeta_ajustada(pantalla, p, idx_slot, rect_panel, tam_meta=28, alto_card=90, gap_cards=6):
    r_card = pygame.Rect(
        rect_panel.left + 20,
        rect_panel.top + 12 + idx_slot * (alto_card + gap_cards),
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

    # CARGAR
    if dict_sprites.get("cargar_normal"):
        pantalla.blit(dict_sprites["cargar_normal"], r_btn_cargar)
    else:
        pygame.draw.rect(pantalla, (65, 138, 72), r_btn_cargar, border_radius=8)
        pygame.draw.rect(pantalla, (22, 45, 24), r_btn_cargar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, "CARGAR", r_btn_cargar, categoria="boton", tamano=14, color=(255, 255, 255), padding=4)

    # GESTIONAR
    if dict_sprites.get("gestionar_normal"):
        pantalla.blit(dict_sprites["gestionar_normal"], r_btn_gestionar)
    else:
        pygame.draw.rect(pantalla, (246, 238, 224), r_btn_gestionar, border_radius=8)
        pygame.draw.rect(pantalla, (185, 155, 120), r_btn_gestionar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, "GESTIONAR", r_btn_gestionar, categoria="boton", tamano=13, color=(65, 45, 30), padding=4)

    # BORRAR
    if dict_sprites.get("borrar_normal"):
        pantalla.blit(dict_sprites["borrar_normal"], r_btn_borrar)
    else:
        pygame.draw.rect(pantalla, (205, 80, 70), r_btn_borrar, border_radius=8)
        pygame.draw.rect(pantalla, (150, 50, 45), r_btn_borrar, width=2, border_radius=8)
        dibujar_texto_en_rect(pantalla, "BORRAR", r_btn_borrar, categoria="boton", tamano=14, color=(255, 250, 245), padding=4)

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

    # Diamante decorativo
    diam_cx = x_texto + 4
    diam_cy = r_card.top + 18
    for d_diam in range(-4, 5):
        w_diam = 4 - abs(d_diam)
        for dx in range(-w_diam, w_diam + 1):
            c_d = (245, 215, 110) if (d_diam <= 0 and dx <= 0) else (210, 145, 35)
            pantalla.set_at((diam_cx + dx, diam_cy + d_diam), c_d)

    # FILA 1: Nombre de la partida
    cur_x_tit = x_texto + 16
    if tiene_pwd:
        main._dibujar_icono_candado(pantalla, cur_x_tit + 3, r_card.top + 18, abierto=False)
        cur_x_tit += 14
    rect_tit = pygame.Rect(cur_x_tit, r_card.top + 8, ancho_max_texto - (cur_x_tit - x_texto), 22)
    dibujar_texto_en_rect(pantalla, nombre, rect_tit, categoria="subtitulo", tamano=21, color=(55, 42, 30), negrita=True, alineacion="izquierda", padding=0)

    partes_f = fecha.strip().split(" ") if fecha else []
    str_fecha = partes_f[0] if len(partes_f) > 0 else ""
    str_hora = partes_f[1] if len(partes_f) > 1 else ""
    tiene_fecha_hora = bool(str_fecha or str_hora)

    # Tipografía para metadatos (tamaño 28)
    f_meta = obtener_fuente_pequena(tam_meta)

    # FILA 2: Nivel alcanzado + Progreso
    y_fila2 = (r_card.top + 35) if tiene_fecha_hora else (r_card.top + 45)
    cur_x2 = x_texto + 4

    # Gema nivel (centrada con el centro de la tinta en y_fila2 + 14)
    dibujar_icono_estrella(pantalla, cur_x2 + 5, y_fila2 + 14)
    cur_x2 += 16
    t_niv = f_meta.render(f"Nivel {mundo_max}-{nivel_max}", True, (75, 48, 30))
    pantalla.blit(t_niv, (cur_x2, y_fila2))
    cur_x2 += t_niv.get_width() + 14

    # Separador sutil
    pygame.draw.circle(pantalla, (180, 150, 120), (cur_x2, y_fila2 + 14), 2)
    cur_x2 += 10

    # Trofeo completados
    dibujar_icono_trofeo(pantalla, cur_x2 + 6, y_fila2 + 14)
    cur_x2 += 18
    t_comp = f_meta.render(f"{cant_comp}/15 completados", True, (90, 65, 45))
    pantalla.blit(t_comp, (cur_x2, y_fila2))

    # FILA 3: Fecha + Hora
    if tiene_fecha_hora:
        y_fila3 = r_card.top + 61
        cur_x3 = x_texto + 4

        if str_fecha:
            dibujar_icono_calendario(pantalla, cur_x3 + 6, y_fila3 + 14)
            cur_x3 += 16
            t_fec = f_meta.render(str_fecha, True, (105, 80, 60))
            pantalla.blit(t_fec, (cur_x3, y_fila3))
            cur_x3 += t_fec.get_width() + 16

        if str_hora:
            dibujar_icono_reloj(pantalla, cur_x3 + 6, y_fila3 + 14)
            cur_x3 += 16
            t_hor = f_meta.render(str_hora, True, (105, 80, 60))
            pantalla.blit(t_hor, (cur_x3, y_fila3))

# Test
pantalla = pygame.Surface((1280, 720))
pantalla.blit(main._obtener_fondo_partidas(1280, 720), (0, 0))
rect_panel, btn_v, btn_n, btn_p = main.obtener_geometria_panel_partidas(1280, 720, True)

pygame.draw.rect(pantalla, (252, 246, 235), rect_panel, border_radius=16)
pygame.draw.rect(pantalla, (190, 160, 125), rect_panel, width=3, border_radius=16)
pygame.draw.rect(pantalla, (225, 200, 160), rect_panel.inflate(-8, -8), width=1, border_radius=12)

partidas = [
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
        "mundo_max": 2,
        "nivel_max": 4,
        "fecha": "31/10/2026 16:45",
        "niveles_desbloqueados": {1: [True]*5, 2: [True]*4},
        "tiene_password": True,
    },
]

for idx, p in enumerate(partidas):
    render_tarjeta_ajustada(pantalla, p, idx, rect_panel, tam_meta=28, alto_card=90, gap_cards=6)

os.makedirs("scratch/capturas_perfeccion", exist_ok=True)
r_c0 = pygame.Rect(rect_panel.left + 20, rect_panel.top + 12, rect_panel.width - 40, 90)
crop0 = pantalla.subsurface(r_c0)
pygame.image.save(crop0, "scratch/capturas_perfeccion/tarjeta_0_zoom_h90.png")

r_c1 = pygame.Rect(rect_panel.left + 20, rect_panel.top + 12 + 96, rect_panel.width - 40, 90)
crop1 = pantalla.subsurface(r_c1)
pygame.image.save(crop1, "scratch/capturas_perfeccion/tarjeta_1_zoom_h90.png")
print("Saved h90 cards!")

