import os
import sys
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()

def resolver_ruta_matrix():
    candidatas = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Sprites", "Fuentes", "Matrix_Mono.ttf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Sprites", "Fuentes", "Matrix_Mono.ttf"),
        os.path.join(os.getcwd(), "Sprites", "Fuentes", "Matrix_Mono.ttf"),
        os.path.join(os.getcwd(), "..", "Sprites", "Fuentes", "Matrix_Mono.ttf"),
    ]
    for c in candidatas:
        if os.path.isfile(c):
            return os.path.normpath(c)
    from fuentes import _resolver_ruta_fuente
    r = _resolver_ruta_fuente("Matrix_Mono.ttf")
    if r and os.path.isfile(r):
        return r
    raise FileNotFoundError("Tipografía matrix_mono no encontrada en las carpetas del proyecto.")

FONT_PATH = resolver_ruta_matrix()


def crear_gorrito_navideno(ancho=44, alto=36):
    """
    Dibuja un gorrito de Papá Noel en pixel art auténtico con borde blanco y pompón.
    """
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    
    # Colores
    c_borde = (38, 12, 16)
    c_rojo = (215, 34, 42)
    c_rojo_luz = (245, 75, 85)
    c_rojo_sombra = (150, 20, 28)
    c_blanco = (255, 255, 255)
    c_blanco_sombra = (205, 218, 232)
    
    # 1. Cuerpo rojo del gorro (cono curvado hacia la izquierda)
    # Relleno rojo
    puntos_gorro = [
        (8, 24),   # Base izq
        (36, 24),  # Base der
        (33, 16),
        (28, 10),
        (20, 6),
        (13, 9),
        (8, 15),
    ]
    pygame.draw.polygon(surf, c_rojo, puntos_gorro)
    
    # Sombras y luces del cono
    # Luz en la cresta derecha
    pygame.draw.line(surf, c_rojo_luz, (31, 23), (25, 12), 2)
    # Sombra en la base y pliegue izquierdo
    pygame.draw.line(surf, c_rojo_sombra, (10, 23), (12, 16), 2)
    pygame.draw.line(surf, c_rojo_sombra, (12, 23), (32, 23), 1)
    
    # Contorno del cono
    pygame.draw.polygon(surf, c_borde, puntos_gorro, 2)
    
    # 2. Pompón blanco en la punta caída (izq)
    # Borde y relleno del pompón
    pygame.draw.circle(surf, c_borde, (6, 17), 6)
    pygame.draw.circle(surf, c_blanco, (6, 17), 5)
    pygame.draw.circle(surf, c_blanco_sombra, (5, 19), 3)
    surf.set_at((6, 15), c_blanco)
    
    # 3. Manto / borde inferior blanco de peluche
    rect_borde = pygame.Rect(4, 22, 36, 10)
    # Sombra de peluche
    pygame.draw.rect(surf, c_borde, (3, 21, 38, 12), border_radius=4)
    pygame.draw.rect(surf, c_blanco, (4, 22, 36, 10), border_radius=4)
    pygame.draw.rect(surf, c_blanco_sombra, (4, 28, 36, 4), border_radius=2)
    
    # Puntos de textura en el peluche
    for px, py in [(8, 24), (16, 25), (24, 24), (32, 25)]:
        surf.set_at((px, py), c_blanco_sombra)
        
    return surf


def dibujar_estrella_pixel(superficie, cx, cy, col_centro=(255, 255, 230), col_borde=(255, 215, 60)):
    """Dibuja una pequeña estrella pixel art de 4 puntas."""
    # Núcleo y puntas
    superficie.set_at((cx, cy), col_centro)
    superficie.set_at((cx - 1, cy), col_borde)
    superficie.set_at((cx + 1, cy), col_borde)
    superficie.set_at((cx, cy - 1), col_borde)
    superficie.set_at((cx, cy + 1), col_borde)
    # Puntas exteriores
    superficie.set_at((cx - 2, cy), col_borde)
    superficie.set_at((cx + 2, cy), col_borde)
    superficie.set_at((cx, cy - 2), col_borde)
    superficie.set_at((cx, cy + 2), col_borde)


def crear_cinta_roja(ancho_total, alto, texto, fuente_sub):
    """
    Crea una cinta roja retro con extremos doblados estilo videojuego,
    y el texto centrado en color crema.
    """
    surf = pygame.Surface((ancho_total, alto + 12), pygame.SRCALPHA)
    
    w_cola = 30
    h_cinta = alto
    y_cinta = 4
    w_cuerpo = ancho_total - 2 * w_cola
    x_cuerpo = w_cola
    
    # Colores
    c_borde = (38, 10, 16)
    c_fondo = (205, 30, 40)
    c_luz = (240, 72, 82)
    c_sombra = (135, 18, 25)
    c_doblez = (95, 12, 18)
    c_oro = (255, 215, 75)
    
    # 1. Colas izquierda y derecha (dobladas por detrás y hacia abajo)
    y_cola = y_cinta + 5
    
    # Cola izquierda (con muesca en V)
    pts_cola_izq = [
        (0, y_cola),
        (w_cola + 4, y_cola),
        (w_cola + 4, y_cola + h_cinta),
        (0, y_cola + h_cinta),
        (10, y_cola + h_cinta // 2),
    ]
    pygame.draw.polygon(surf, c_borde, pts_cola_izq)
    # Relleno
    pts_cola_izq_in = [
        (2, y_cola + 2),
        (w_cola + 2, y_cola + 2),
        (w_cola + 2, y_cola + h_cinta - 2),
        (2, y_cola + h_cinta - 2),
        (11, y_cola + h_cinta // 2),
    ]
    pygame.draw.polygon(surf, c_sombra, pts_cola_izq_in)
    
    # Cola derecha (con muesca en V)
    x_cola_der = ancho_total - w_cola
    pts_cola_der = [
        (x_cola_der - 4, y_cola),
        (ancho_total, y_cola),
        (ancho_total - 10, y_cola + h_cinta // 2),
        (ancho_total, y_cola + h_cinta),
        (x_cola_der - 4, y_cola + h_cinta),
    ]
    pygame.draw.polygon(surf, c_borde, pts_cola_der)
    # Relleno
    pts_cola_der_in = [
        (x_cola_der - 2, y_cola + 2),
        (ancho_total - 2, y_cola + 2),
        (ancho_total - 11, y_cola + h_cinta // 2),
        (ancho_total - 2, y_cola + h_cinta - 2),
        (x_cola_der - 2, y_cola + h_cinta - 2),
    ]
    pygame.draw.polygon(surf, c_sombra, pts_cola_der_in)
    
    # 2. Triángulos oscuros de pliegue/doblez donde la cinta gira hacia atrás
    # Izquierda
    pygame.draw.polygon(surf, c_doblez, [
        (x_cuerpo, y_cola),
        (x_cuerpo + 6, y_cinta + h_cinta),
        (x_cuerpo, y_cinta + h_cinta)
    ])
    # Derecha
    pygame.draw.polygon(surf, c_doblez, [
        (x_cuerpo + w_cuerpo, y_cola),
        (x_cuerpo + w_cuerpo - 6, y_cinta + h_cinta),
        (x_cuerpo + w_cuerpo, y_cinta + h_cinta)
    ])
    
    # 3. Sombra inferior del cuerpo central
    rect_sombra_cuerpo = pygame.Rect(x_cuerpo, y_cinta + 3, w_cuerpo, h_cinta)
    pygame.draw.rect(surf, (20, 8, 12, 160), rect_sombra_cuerpo, border_radius=4)
    
    # 4. Borde y cuerpo central
    rect_borde_cuerpo = pygame.Rect(x_cuerpo - 1, y_cinta - 1, w_cuerpo + 2, h_cinta + 2)
    pygame.draw.rect(surf, c_borde, rect_borde_cuerpo, border_radius=4)
    
    rect_cuerpo = pygame.Rect(x_cuerpo, y_cinta, w_cuerpo, h_cinta)
    pygame.draw.rect(surf, c_fondo, rect_cuerpo, border_radius=3)
    
    # Bisel de luz superior y bisel de sombra inferior
    pygame.draw.line(surf, c_luz, (x_cuerpo + 2, y_cinta + 1), (x_cuerpo + w_cuerpo - 3, y_cinta + 1), 2)
    pygame.draw.line(surf, c_sombra, (x_cuerpo + 2, y_cinta + h_cinta - 2), (x_cuerpo + w_cuerpo - 3, y_cinta + h_cinta - 2), 2)
    
    # Ribetes dorados finos en los extremos del cuerpo
    pygame.draw.line(surf, c_oro, (x_cuerpo + 6, y_cinta + 3), (x_cuerpo + 6, y_cinta + h_cinta - 4), 2)
    pygame.draw.line(surf, c_oro, (x_cuerpo + w_cuerpo - 7, y_cinta + 3), (x_cuerpo + w_cuerpo - 7, y_cinta + h_cinta - 4), 2)
    
    # 5. Texto «DE PICO EN EL PARQUE» centrado en la cinta
    col_txt = (255, 248, 228)
    col_sombra_txt = (60, 10, 16)
    
    txt_s = fuente_sub.render(texto, False, col_sombra_txt)
    txt_f = fuente_sub.render(texto, False, col_txt)
    
    r_txt = txt_f.get_rect(center=(ancho_total // 2, y_cinta + h_cinta // 2))
    surf.blit(txt_s, r_txt.move(1, 1))
    surf.blit(txt_f, r_txt)
    
    return surf


def generar_banner_titulo_completo():
    """
    Construye la composición completa del título con:
    - «LAS AVENTURILLAS» en dos tonos (crema y naranja cálido), contorno marrón oscuro,
      sombra de profundidad y copos/bloques de nieve acumulada.
    - Gorrito de Papá Noel sobre la esquina superior izquierda.
    - Estrellitas navideñas sutiles.
    - Cinta roja inferior con «DE PICO EN EL PARQUE».
    """
    f_main = pygame.font.Font(FONT_PATH, 38)
    f_sub = pygame.font.Font(FONT_PATH, 16)
    
    texto_principal = "LAS AVENTURILLAS"
    texto_secundario = "DE PICO EN EL PARQUE"
    
    # Medir texto principal
    txt_raw = f_main.render(texto_principal, False, (255, 255, 255))
    tw, th = txt_raw.get_size()
    
    # Crear relleno degradado crema-naranja cálido
    txt_relleno = pygame.Surface((tw, th), pygame.SRCALPHA)
    for y in range(th):
        ratio = y / max(1, th - 1)
        if ratio < 0.42:
            col = (255, 248, 222)   # Crema brillante
        elif ratio < 0.54:
            col = (255, 204, 105)   # Transición dorada
        elif ratio < 0.80:
            col = (248, 126, 34)    # Naranja cálido
        else:
            col = (215, 88, 22)     # Sombra naranja inferior
            
        for x in range(tw):
            if txt_raw.get_at((x, y))[:3] != (0, 0, 0):
                txt_relleno.set_at((x, y), (*col, 255))
                
    # Superficie para el texto con contorno y sombra
    pad_c = 8
    txt_con_borde = pygame.Surface((tw + pad_c * 2, th + pad_c * 2 + 6), pygame.SRCALPHA)
    
    c_borde = (38, 16, 12)
    c_sombra = (20, 10, 16, 200)
    
    # 1. Sombra desplazada (+4, +5)
    for dx in range(2, 6):
        for dy in range(3, 7):
            txt_con_borde.blit(f_main.render(texto_principal, False, (18, 10, 15)), (pad_c + dx, pad_c + dy))
            
    # 2. Contorno grueso de 2-3 px
    desplazamientos_borde = [
        (-2, 0), (2, 0), (0, -2), (0, 2),
        (-2, -1), (-2, 1), (2, -1), (2, 1),
        (-1, -2), (1, -2), (-1, 2), (1, 2),
        (-1, -1), (1, -1), (-1, 1), (1, 1),
        (-2, -2), (2, -2), (-2, 2), (2, 2),
    ]
    for dx, dy in desplazamientos_borde:
        txt_con_borde.blit(f_main.render(texto_principal, False, c_borde), (pad_c + dx, pad_c + dy))
        
    # 3. Blit del texto relleno dos tonos
    txt_con_borde.blit(txt_relleno, (pad_c, pad_c))
    
    # 4. Detalles de nieve acumulada sobre la parte superior de las letras
    c_nieve = (255, 255, 255)
    c_nieve_sombra = (208, 226, 246)
    
    # Encontrar bordes superiores de letras y colocar parches de nieve
    for col_x in range(pad_c + 4, pad_c + tw - 4):
        # Buscar el píxel más alto de la letra
        primer_y = None
        for row_y in range(pad_c, pad_c + th):
            if txt_con_borde.get_at((col_x, row_y)).a > 200:
                primer_y = row_y
                break
        if primer_y is not None and primer_y < pad_c + 12:
            # Colocar nieve según posición para formar montículos naturales
            if (col_x % 9) in (0, 1, 2, 3, 4):
                alt_nieve = 2 + (col_x % 3)
                for ny in range(alt_nieve):
                    col_p = c_nieve if ny < alt_nieve - 1 else c_nieve_sombra
                    txt_con_borde.set_at((col_x, primer_y - ny), col_p)
                    # Contorno superior sutil de nieve
                    if ny == alt_nieve - 1:
                        txt_con_borde.set_at((col_x, primer_y - ny - 1), (180, 205, 230))
                        
    # 5. Cinta roja inferior para «DE PICO EN EL PARQUE»
    ancho_cinta = 480
    alto_cinta = 32
    cinta_surf = crear_cinta_roja(ancho_cinta, alto_cinta, texto_secundario, f_sub)
    
    # 6. Composición final en una superficie global
    ancho_total = max(txt_con_borde.get_width() + 60, ancho_cinta + 40)
    alto_total = txt_con_borde.get_height() + cinta_surf.get_height() + 8
    
    banner = pygame.Surface((ancho_total, alto_total), pygame.SRCALPHA)
    
    # Blit del texto principal
    x_txt = (ancho_total - txt_con_borde.get_width()) // 2
    y_txt = 8
    banner.blit(txt_con_borde, (x_txt, y_txt))
    
    # Blit de la cinta roja debajo (solapando ligeramente 4px con la sombra inferior)
    x_cinta = (ancho_total - cinta_surf.get_width()) // 2
    y_cinta = y_txt + txt_con_borde.get_height() - 14
    banner.blit(cinta_surf, (x_cinta, y_cinta))
    
    # 7. Gorrito de Papá Noel en la esquina superior izquierda (sobre la "L")
    gorro = crear_gorrito_navideno(42, 34)
    banner.blit(gorro, (x_txt + pad_c - 14, y_txt + pad_c - 20))
    
    # 8. Estrellitas navideñas pequeñas alrededor
    dibujar_estrella_pixel(banner, x_txt + pad_c + 18, y_txt + 4)
    dibujar_estrella_pixel(banner, x_txt + txt_con_borde.get_width() - pad_c - 8, y_txt + 12)
    dibujar_estrella_pixel(banner, x_cinta + 16, y_cinta + 26)
    dibujar_estrella_pixel(banner, x_cinta + cinta_surf.get_width() - 16, y_cinta + 26)
    
    return banner


if __name__ == "__main__":
    banner = generar_banner_titulo_completo()
    os.makedirs("scratch", exist_ok=True)
    pygame.image.save(banner, "scratch/test_banner_titulo.png")
    print(f"Banner guardado exitosamente. Tamaño: {banner.get_size()}")
