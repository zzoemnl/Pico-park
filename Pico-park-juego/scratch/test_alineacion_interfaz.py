import os
import sys
import pygame

# Set headless mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

import sprites
import configuracion

print("=== INICIANDO PRUEBAS DE ALINEACION DE INTERFAZ ===")

# -------------------------------------------------------------------------
# 1. TEST DE ALINEACION DE ACCESORIOS (PERSONALIZACION DE PERSONAJES)
# -------------------------------------------------------------------------
print("\n[TEST 1] Verificando alineación y simetría de accesorios...")

w_frame, h_frame = 470, 276
y_frame = 295
cx_p1 = 360
cx_p2 = 920

rect_f1 = pygame.Rect(cx_p1 - w_frame // 2, y_frame, w_frame, h_frame)
rect_f2 = pygame.Rect(cx_p2 - w_frame // 2, y_frame, w_frame, h_frame)

accesorios_disp = sprites.obtener_accesorios_disponibles()
assert len(accesorios_disp) == 6, f"Se esperaban 6 accesorios, encontrados {len(accesorios_disp)}"

w_acc, h_acc, gap_acc_x, gap_acc_y = 126, 88, 16, 14
ancho_fila_acc = 3 * w_acc + 2 * gap_acc_x  # 410 px
x_offset_acc = (w_frame - ancho_fila_acc) // 2  # 30 px
alto_filas_acc = 2 * h_acc + gap_acc_y  # 190 px
y_offset_acc = 34 + ((h_frame - 34) - alto_filas_acc) // 2  # 60 px

# Comprobar que ambas filas (r=0 y r=1) están perfectamente alineadas horizontalmente
coords_f1 = []
coords_f2 = []
for idx_a, acc in enumerate(accesorios_disp):
    r = idx_a // 3
    c = idx_a % 3
    x_offset_rel = x_offset_acc + c * (w_acc + gap_acc_x)
    y_card_a = y_frame + y_offset_acc + r * (h_acc + gap_acc_y)

    ra1 = pygame.Rect(rect_f1.left + x_offset_rel, y_card_a, w_acc, h_acc)
    ra2 = pygame.Rect(rect_f2.left + x_offset_rel, y_card_a, w_acc, h_acc)

    coords_f1.append((r, c, ra1))
    coords_f2.append((r, c, ra2))

# 1.1 Simetría horizontal de la fila 0 y fila 1 en P1
fila_0_p1 = [rect for r, c, rect in coords_f1 if r == 0]
fila_1_p1 = [rect for r, c, rect in coords_f1 if r == 1]

assert len(fila_0_p1) == 3 and len(fila_1_p1) == 3, "Cada fila debe contener 3 tarjetas"

# Los márgenes izquierdo y derecho de fila 0 respecto al frame deben ser idénticos
margen_izq_f0 = fila_0_p1[0].left - rect_f1.left
margen_der_f0 = rect_f1.right - fila_0_p1[-1].right
assert margen_izq_f0 == margen_der_f0 == 30, f"Fila 0 descentrada: izq={margen_izq_f0}, der={margen_der_f0}"

# Los márgenes izquierdo y derecho de fila 1 respecto al frame deben ser idénticos
margen_izq_f1 = fila_1_p1[0].left - rect_f1.left
margen_der_f1 = rect_f1.right - fila_1_p1[-1].right
assert margen_izq_f1 == margen_der_f1 == 30, f"Fila 1 descentrada: izq={margen_izq_f1}, der={margen_der_f1}"

# Ambas filas deben tener exactamente las mismas coordenadas X
for i in range(3):
    assert fila_0_p1[i].left == fila_1_p1[i].left, f"Tarjeta {i} no está alineada verticalmente entre filas"

# 1.2 Simetría vertical de las filas respecto al espacio útil debajo del título
linea_separadora_y = rect_f1.top + 34
espacio_arriba = fila_0_p1[0].top - linea_separadora_y
espacio_abajo = rect_f1.bottom - fila_1_p1[0].bottom
assert espacio_arriba == espacio_abajo == 26, f"Filas descentradas verticalmente: arriba={espacio_arriba}, abajo={espacio_abajo}"

# 1.3 Comprobar que P1 y P2 tienen exactamente el mismo ancho y márgenes
for i in range(len(accesorios_disp)):
    _, _, r1 = coords_f1[i]
    _, _, r2 = coords_f2[i]
    rel_x_p1 = r1.left - rect_f1.left
    rel_x_p2 = r2.left - rect_f2.left
    assert rel_x_p1 == rel_x_p2, f"Discrepancia entre P1 y P2 en accesorio {i}"

print("[OK] Test 1 superado: Accesorios perfectamente centrados y simétricos en P1 y P2.")

# -------------------------------------------------------------------------
# 2. TEST DE ALINEACION DE PANEL DE VOLUMEN
# -------------------------------------------------------------------------
print("\n[TEST 2] Verificando alineación y centrado del panel de volumen...")

W_MODAL = 520
H_MODAL = 400
rect_modal = pygame.Rect((1280 - W_MODAL) // 2, (720 - H_MODAL) // 2, W_MODAL, H_MODAL)

w_btn_lang, h_btn_lang, gap_lang = 136, 42, 14
total_w_content = 3 * w_btn_lang + 2 * gap_lang
x_margen_contenido = rect_modal.left + (W_MODAL - total_w_content) // 2

W_BTN_VOL, H_BTN_VOL = 42, 50
gap_vol = 14
w_barra = total_w_content - (2 * W_BTN_VOL + 2 * gap_vol)
h_barra = 28
cy_vol_fila = rect_modal.top + 130

rect_btn_menos = pygame.Rect(x_margen_contenido, 0, W_BTN_VOL, H_BTN_VOL)
rect_btn_menos.centery = cy_vol_fila

rect_barra_bg = pygame.Rect(rect_btn_menos.right + gap_vol, 0, w_barra, h_barra)
rect_barra_bg.centery = cy_vol_fila

rect_btn_mas = pygame.Rect(rect_barra_bg.right + gap_vol, 0, W_BTN_VOL, H_BTN_VOL)
rect_btn_mas.centery = cy_vol_fila

# 2.1 Centros alineados en una misma línea horizontal
assert rect_btn_menos.centery == rect_barra_bg.centery == rect_btn_mas.centery == cy_vol_fila, "Los centros de los controles de volumen deben ser idénticos"

# 2.2 Márgenes horizontales del panel de volumen equilibrados
margen_izq_vol = rect_btn_menos.left - rect_modal.left
margen_der_vol = rect_modal.right - rect_btn_mas.right
assert margen_izq_vol == margen_der_vol == 42, f"Márgenes de volumen no equilibrados: izq={margen_izq_vol}, der={margen_der_vol}"

# 2.3 Coincidencia de márgenes entre la fila de volumen y la fila de idiomas
assert total_w_content == (rect_btn_mas.right - rect_btn_menos.left) == 436, "El ancho total de volumen debe coincidir con el de idiomas"

# 2.4 Centrado del botón X de cabecera
W_X_CFG, H_X_CFG = 29, 34
rect_x_header = pygame.Rect(rect_modal.right - W_X_CFG - 14, rect_modal.top + (54 - H_X_CFG) // 2, W_X_CFG, H_X_CFG)
header_cy = rect_modal.top + 27
assert rect_x_header.centery == header_cy, "El botón X debe estar centrado verticalmente en la cabecera"

print("[OK] Test 2 superado: Panel de volumen matemáticamente alineado y centrado.")

print("\n==============================================================")
print("¡TODAS LAS PRUEBAS DE ALINEACION DE INTERFAZ FUERON EXITOSAS!")
print("==============================================================")
