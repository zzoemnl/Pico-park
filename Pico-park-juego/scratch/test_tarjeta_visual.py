import os
import sys
import pygame

sys.path.insert(0, ".")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from main import (
    obtener_geometria_panel_partidas,
    obtener_geometria_tarjeta_partida,
    _dibujar_icono_candado,
    _dibujar_icono_calendario,
    calcular_niveles_completados,
    COLORES_TABS,
)
from fuentes import (
    obtener_fuente,
    obtener_fuente_subtitulo,
    obtener_fuente_pequena,
    obtener_fuente_contador,
    dibujar_texto_en_rect
)
from guardado import cargar_partidas

def _dibujar_icono_reloj(s, cx, cy):
    """Dibuja un pequeño reloj pixel art (9x9 px)."""
    col_cuerpo = (248, 242, 228)
    col_borde = (95, 75, 55)
    col_agujas = (65, 45, 30)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            d2 = dx * dx + dy * dy
            if 10 <= d2 <= 16:
                s.set_at((cx + dx, cy + dy), col_borde)
            elif d2 < 10:
                s.set_at((cx + dx, cy + dy), col_cuerpo)
    s.set_at((cx, cy), col_agujas)
    s.set_at((cx, cy - 1), col_agujas)
    s.set_at((cx, cy - 2), col_agujas)
    s.set_at((cx + 1, cy), col_agujas)
    s.set_at((cx + 2, cy), col_agujas)

def _dibujar_icono_trofeo(s, cx, cy):
    """Dibuja un pequeño trofeo pixel art (9x9 px) para niveles completados."""
    col_oro = (245, 195, 55)
    col_luz = (255, 235, 130)
    col_borde = (115, 80, 25)
    col_base = (140, 100, 45)
    # Copa
    for dy in range(-4, 0):
        w = 3 - abs(dy + 2) // 2
        for dx in range(-w, w + 1):
            s.set_at((cx + dx, cy + dy), col_oro)
    s.set_at((cx - 1, cy - 3), col_luz)
    # Asas
    s.set_at((cx - 3, cy - 3), col_borde)
    s.set_at((cx - 3, cy - 2), col_borde)
    s.set_at((cx + 3, cy - 3), col_borde)
    s.set_at((cx + 3, cy - 2), col_borde)
    # Tallo y base
    s.set_at((cx, cy), col_borde)
    s.set_at((cx, cy + 1), col_base)
    for dx in range(-2, 3):
        s.set_at((cx + dx, cy + 2), col_base)

def _dibujar_icono_estrella_nivel(s, cx, cy):
    """Dibuja una pequeña estrella / gema de nivel (7x7 px)."""
    col_gema = (235, 140, 50)
    col_luz = (255, 215, 120)
    col_borde = (120, 65, 20)
    for dy in range(-3, 4):
        w = 3 - abs(dy)
        for dx in range(-w, w + 1):
            col = col_luz if (dy <= 0 and dx <= 0) else col_gema
            s.set_at((cx + dx, cy + dy), col)

def render_test_card(pantalla, p, idx_slot, rect_panel, tam_det=18, tam_nom=21):
    r_card, r_badge, r_btn_cargar, r_btn_gestionar, r_btn_borrar, (x_texto, ancho_max_texto) = obtener_geometria_tarjeta_partida(rect_panel, idx_slot)
    
    # Fondo card
    col_card = (253, 248, 238)
    borde_card = (185, 150, 110)
    pygame.draw.rect(pantalla, col_card, r_card, border_radius=12)
    pygame.draw.rect(pantalla, borde_card, r_card, width=2, border_radius=12)
    pygame.draw.rect(pantalla, (235, 220, 195), r_card.inflate(-6, -6), width=1, border_radius=8)
    pygame.draw.rect(pantalla, (160, 120, 80), (r_card.left + 3, r_card.top + 8, 4, r_card.height - 16), border_radius=2)

    # Badge mundo
    m_val = p.get("mundo_max", 1)
    info_b = COLORES_TABS.get(m_val, COLORES_TABS[1])
    pygame.draw.rect(pantalla, info_b["fondo"], r_badge, border_radius=8)
    pygame.draw.rect(pantalla, info_b["borde"], r_badge, width=2, border_radius=8)
    pygame.draw.rect(pantalla, (245, 235, 220), r_badge.inflate(-4, -4), width=1, border_radius=6)
    fuente_badge = obtener_fuente("badge", 13)
    t_badge = fuente_badge.render(f"MUNDO {m_val}", True, info_b["texto"])
    pantalla.blit(t_badge, t_badge.get_rect(center=r_badge.center))

    # Botones a la derecha
    for r, txt, col, col_b in [
        (r_btn_cargar, "CARGAR", (65, 138, 72), (22, 45, 24)),
        (r_btn_gestionar, "GESTIONAR", (246, 238, 224), (185, 155, 120)),
        (r_btn_borrar, "BORRAR", (205, 80, 70), (150, 50, 45))
    ]:
        pygame.draw.rect(pantalla, col, r, border_radius=8)
        pygame.draw.rect(pantalla, col_b, r, width=2, border_radius=8)
        c_txt = (255, 255, 255) if txt != "GESTIONAR" else (65, 45, 30)
        dibujar_texto_en_rect(pantalla, txt, r, categoria="boton", tamano=14, color=c_txt, padding=4)

    # Metadatos
    nombre = p.get("nombre", f"Partida {p.get('id', 1)}")
    mundo_max = p.get("mundo_max", 1)
    nivel_max = p.get("nivel_max", 1)
    fecha_full = p.get("fecha", "")
    cant_comp = calcular_niveles_completados(p.get("niveles_desbloqueados", {}))
    tiene_pwd = p.get("tiene_password", False)

    # Nombre con jerarquía clara (tamano 21-22)
    rect_tit_card = pygame.Rect(x_texto + 14, r_card.top + 10, ancho_max_texto - 14, 28)
    dibujar_texto_en_rect(pantalla, nombre, rect_tit_card, categoria="subtitulo", tamano=tam_nom, color=(55, 42, 30), negrita=True, alineacion="izquierda", padding=0)

    # Candado antes de nombre o en la línea de datos
    _dibujar_icono_candado(pantalla, x_texto + 4, r_card.top + 23, abierto=(not tiene_pwd))

    # Línea 2 de datos: considerablemente más grande (+25% a +35%, tamano=18)
    # Desglosar fecha y hora
    partes_f = fecha_full.strip().split(" ")
    str_fecha = partes_f[0] if len(partes_f) > 0 else ""
    str_hora = partes_f[1] if len(partes_f) > 1 else ""

    f_datos = obtener_fuente_pequena(tam_det)
    y_datos = r_card.top + 45
    cur_x = x_texto + 4

    # 1. Nivel
    _dibujar_icono_estrella_nivel(pantalla, cur_x + 4, y_datos + 8)
    cur_x += 12
    t_niv = f_datos.render(f"Nivel {mundo_max}-{nivel_max}", True, (90, 60, 40))
    pantalla.blit(t_niv, (cur_x, y_datos))
    cur_x += t_niv.get_width() + 14

    # Separador sutil
    pygame.draw.circle(pantalla, (190, 160, 130), (cur_x, y_datos + 8), 2)
    cur_x += 10

    # 2. Niveles completados
    _dibujar_icono_trofeo(pantalla, cur_x + 5, y_datos + 8)
    cur_x += 14
    t_comp = f_datos.render(f"{cant_comp}/15 completados", True, (105, 80, 55))
    pantalla.blit(t_comp, (cur_x, y_datos))
    cur_x += t_comp.get_width() + 14

    # Separador sutil
    if str_fecha:
        pygame.draw.circle(pantalla, (190, 160, 130), (cur_x, y_datos + 8), 2)
        cur_x += 10

        # 3. Fecha
        _dibujar_icono_calendario(pantalla, cur_x + 5, y_datos + 8)
        cur_x += 14
        t_fec = f_datos.render(str_fecha, True, (120, 95, 75))
        pantalla.blit(t_fec, (cur_x, y_datos))
        cur_x += t_fec.get_width() + 12

    # 4. Hora
    if str_hora:
        _dibujar_icono_reloj(pantalla, cur_x + 5, y_datos + 8)
        cur_x += 14
        t_hor = f_datos.render(str_hora, True, (120, 95, 75))
        pantalla.blit(t_hor, (cur_x, y_datos))

# Run test render
pantalla = pygame.Surface((1280, 720))
pantalla.fill((230, 215, 195))
rect_panel, btn_v, btn_n, btn_p = obtener_geometria_panel_partidas(1280, 720, True)
pygame.draw.rect(pantalla, (252, 246, 235), rect_panel, border_radius=16)

partidas_test = [
    {'id': 1, 'nombre': 'Aventura en la Nieve', 'mundo_max': 2, 'nivel_max': 3, 'fecha': '31/10/2026 16:45', 'niveles_desbloqueados': {1: [True]*5, 2: [True]*3}, 'tiene_password': True},
    {'id': 2, 'nombre': 'Todos los niveles desbloqueados', 'mundo_max': 3, 'nivel_max': 5, 'fecha': '26/10/2026 12:00', 'niveles_desbloqueados': {1: [True]*5, 2: [True]*5, 3: [True]*5}, 'tiene_password': False},
]

for idx, p in enumerate(partidas_test):
    render_test_card(pantalla, p, idx, rect_panel, tam_det=18, tam_nom=21)

crop = pantalla.subsurface(rect_panel)
os.makedirs("scratch/test_cards", exist_ok=True)
pygame.image.save(crop, "scratch/test_cards/preview_cards_tam18.png")
print("Card preview saved!")
