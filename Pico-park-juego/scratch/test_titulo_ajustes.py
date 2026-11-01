import os, sys, pygame

sys.path.insert(0, os.path.abspath('.'))
import main, sprites
from personajes_menu import GestorPersonajesMenu
from fuentes import obtener_fuente_matrix

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pantalla = pygame.display.set_mode((1280, 720))

# Test different hat right offsets:
# The right edge of 'LAS AVENTURILLAS' is at x_txt + pad_c + tw.
# Let's test x_gorro = x_txt + pad_c + tw - offset
# offsets to test: 20, 16, 12, 8, 4, 0
# y_gorro offsets: -24, -26, -28, -30

os.makedirs('scratch/test_banner_v2', exist_ok=True)

gestor = GestorPersonajesMenu(1280, 720)

ANCHO_BOTON, ALTO_BOTON, ESPACIO = 272, 80, 14
x_centro = (1280 - ANCHO_BOTON) // 2
y_inicio = (720 - ((ALTO_BOTON * 4) + (ESPACIO * 3))) // 2 + 35
btn_jugar = pygame.Rect(x_centro, y_inicio, ANCHO_BOTON, ALTO_BOTON)
btn_personajes = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO), ANCHO_BOTON, ALTO_BOTON)
btn_config = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO) * 2, ANCHO_BOTON, ALTO_BOTON)
btn_salir = pygame.Rect(x_centro, y_inicio + (ALTO_BOTON + ESPACIO) * 3, ANCHO_BOTON, ALTO_BOTON)
spr_j = sprites.cargar_boton_escalado("Menu/jugar.png", ANCHO_BOTON, ALTO_BOTON)
spr_p = sprites.cargar_boton_escalado("Menu/personajes.png", ANCHO_BOTON, ALTO_BOTON)
spr_o = sprites.cargar_boton_escalado("Menu/opciones.png", ANCHO_BOTON, ALTO_BOTON)
spr_s = sprites.cargar_boton_escalado("Menu/salir.png", ANCHO_BOTON, ALTO_BOTON)
spr_x = sprites.cargar_boton_escalado("HUD/boton-x.png", 44, 52)
rect_btn_x = pygame.Rect(1280 - 16 - 44, 16, 44, 52)
botones_menu_datos = [
    (btn_jugar, spr_j, sprites.aclarar_boton(spr_j)),
    (btn_personajes, spr_p, sprites.aclarar_boton(spr_p)),
    (btn_config, spr_o, sprites.aclarar_boton(spr_o)),
    (btn_salir, spr_s, sprites.aclarar_boton(spr_s)),
]
fuente_tit = main.obtener_fuente_titulo(main.TAMANO_TITULO, negrita=True, tamano_fallback=48)

for off_x in [16, 12, 8, 4, 0]:
    for off_y in [-26, -28, -30]:
        # Temporarily mock banner generation
        ancho_cinta = 660
        alto_cinta = 46
        f_sub = obtener_fuente_matrix(23)
        cinta_surf = gestor._crear_cinta_roja(ancho_cinta, alto_cinta, "DE PICO EN EL PARQUE", f_sub)
        
        f_main = obtener_fuente_matrix(38)
        tw, th = f_main.render("LAS AVENTURILLAS", False, (255, 255, 255)).get_size()
        pad_c = 10
        txt_con_borde = pygame.Surface((tw + pad_c * 2, th + pad_c * 2 + 6), pygame.SRCALPHA)
        # Render letters
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
            txt_con_borde.blit(f_main.render("LAS AVENTURILLAS", False, (38, 16, 12)), (pad_c + dx, pad_c + dy))
        txt_con_borde.blit(f_main.render("LAS AVENTURILLAS", False, (255, 204, 105)), (pad_c, pad_c))
        
        ancho_total = max(txt_con_borde.get_width() + 70, ancho_cinta + 40)
        alto_total = txt_con_borde.get_height() + cinta_surf.get_height() + 8
        banner = pygame.Surface((ancho_total, alto_total), pygame.SRCALPHA)
        
        x_txt = (ancho_total - txt_con_borde.get_width()) // 2
        y_txt = 10
        banner.blit(txt_con_borde, (x_txt, y_txt))
        
        x_cinta = (ancho_total - cinta_surf.get_width()) // 2
        y_cinta = y_txt + txt_con_borde.get_height() - 14
        banner.blit(cinta_surf, (x_cinta, y_cinta))
        
        gorro = gestor._obtener_gorro_navideno_pixel_art(52, inclinacion=-4)
        x_gorro = x_txt + pad_c + tw - off_x
        y_gorro = y_txt + pad_c + off_y
        banner.blit(gorro, (x_gorro, y_gorro))
        
        surf = pygame.Surface((1280, 720))
        gestor.dibujar_menu_completo(surf, botones_menu_datos=botones_menu_datos, pos_mouse=(0, 0), spr_x=spr_x, rect_x=rect_btn_x, fuente_titulo=fuente_tit)
        r_banner = banner.get_rect(centerx=1280 // 2, top=56)
        surf.blit(banner, r_banner)
        
        zoom = surf.subsurface((780, 35, 300, 130)).copy()
        pygame.image.save(zoom, f"scratch/test_banner_v2/hat_offx{off_x}_offy{off_y}_zoom.png")

print("Generated banner v2 variations successfully!")
