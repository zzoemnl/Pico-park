"""
_EstadoMenu: estado compartido de las pantallas del menú y su inicialización (sprites, fuentes, geometría).
"""
import pygame
import copy
import os
from configuracion import obtener_idioma, reproducir_musica, seleccionar_musica_menu_aleatoria, t
from fuentes import (
    TAMANO_BADGE,
    TAMANO_BOTON,
    TAMANO_BOTON_GRANDE,
    TAMANO_CARD,
    TAMANO_CONTADOR,
    TAMANO_DECORATIVA,
    TAMANO_DIALOGOS,
    TAMANO_ITEM_TITULO,
    TAMANO_PEQUENA,
    TAMANO_SUBTITULO_GRANDE,
    TAMANO_TEXTO_GRANDE,
    TAMANO_TITULO,
    TAMANO_TITULO_GRANDE,
    TAMANO_TITULO_MODAL,
    obtener_fuente_boton,
    obtener_fuente_botones,
    obtener_fuente_cjk,
    obtener_fuente_contador,
    obtener_fuente_decorativa,
    obtener_fuente_dialogos,
    obtener_fuente_para_texto,
    obtener_fuente_pequena,
    obtener_fuente_subtitulo,
    obtener_fuente_texto,
    obtener_fuente_titulo,
)
from guardado import crear_desbloqueados_inicial, hay_progreso_sin_guardar
from menus.dialogos import mostrar_dialogo_guardar_salir
from menus.comunes import ESTADO_MENU_PRINCIPAL, _seleccionar_accesorios_sesion_aleatorios
from menus.modo_juego import _init_copos_modo
from menus.partidas import obtener_geometria_panel_partidas
from personajes_menu import GestorPersonajesMenu
from sprites import (
    aclarar_boton,
    cargar_boton_escalado,
    generar_boton_con_texto,
    obtener_accesorios_disponibles,
    precargar_botones_comunes,
    renderizar_texto_pixamuse,
)
from ventana import crear_ventana


class _EstadoMenu:
    """
    Estado compartido de las pantallas del menú (antes eran variables locales de main()).
    Cada pantalla tiene su función de eventos y de dibujo que reciben este objeto; main()
    hace la configuración inicial y el loop. Los atributos se crean en main() a medida que
    se inicializan; las funciones auxiliares anidadas también quedan colgadas acá.
    """
    def __init__(self):
        """Carga sprites, fuentes y geometría de todas las pantallas (antes era el inicio de main())."""
        import os
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        self.pantalla = crear_ventana()
        pygame.display.set_caption("Pico Park")
        precargar_botones_comunes()
        self.reloj = pygame.time.Clock()
        seleccionar_musica_menu_aleatoria()
        reproducir_musica("menu")
        self.fuente_pixel_titulo = obtener_fuente_titulo(TAMANO_TITULO, tamano_fallback=55)
        self.fuente_pixel_btn_grande = obtener_fuente_botones(TAMANO_BOTON_GRANDE, tamano_fallback=32)
        self.fuente_pixel_btn = obtener_fuente_botones(TAMANO_BOTON, tamano_fallback=32)
        self.fuente_pixel_sub_btn = obtener_fuente_botones(TAMANO_ITEM_TITULO, tamano_fallback=24)
        self.fuente_pixel_card_btn = obtener_fuente_botones(TAMANO_ITEM_TITULO, tamano_fallback=25)
        self.fuente_pixel_badge = obtener_fuente_botones(TAMANO_BADGE, tamano_fallback=28)

        self.fuente_titulo = obtener_fuente_titulo(TAMANO_TITULO_GRANDE, tamano_fallback=55)
        self.fuente_subtitulo = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
        self.fuente_btn = obtener_fuente_botones(TAMANO_BOTON_GRANDE, tamano_fallback=32)
        self.fuente_texto = obtener_fuente_texto(TAMANO_TEXTO_GRANDE)
        self.fuente_sub_btn = obtener_fuente_pequena(TAMANO_PEQUENA)
        self.fuente_contador = obtener_fuente_contador(TAMANO_CONTADOR)
        self.fuente_dialogos = obtener_fuente_dialogos(TAMANO_DIALOGOS)
        self.fuente_decorativa = obtener_fuente_decorativa(TAMANO_DECORATIVA)
        self.fuentes_menu = {
            "titulo": self.fuente_pixel_titulo,
            "tab": obtener_fuente_titulo(TAMANO_TITULO_MODAL, tamano_fallback=34),
            "card": obtener_fuente_boton(TAMANO_CARD, tamano_fallback=28),
        }
        self.fuente_card_titulo = obtener_fuente_subtitulo(TAMANO_SUBTITULO_GRANDE)
        self.fuente_card_sub = obtener_fuente_pequena(28)

        self.ANCHO_MENU = self.pantalla.get_width()
        self.ALTO_MENU = self.pantalla.get_height()
        _init_copos_modo(self.ANCHO_MENU, self.ALTO_MENU)

        self.niveles_desbloqueados = crear_desbloqueados_inicial()
        self.partida_actual_id = None
        self.partida_actual_nombre = None
        self.partida_actual_password = None
        self.snapshot_guardado = copy.deepcopy(self.niveles_desbloqueados)
        self.sesion_activa = False
        self.partida_cargada_flag = False
        self.partida_creada_flag = False

        self.W_BOTON_HUD, self.H_BOTON_HUD = 44, 52
        self.MARGEN_DER, self.MARGEN_SUP = 18, 16
        self.rect_btn_x = pygame.Rect(self.ANCHO_MENU - self.MARGEN_DER - self.W_BOTON_HUD, self.MARGEN_SUP, self.W_BOTON_HUD, self.H_BOTON_HUD)

        # Carga anticipada exclusiva de lo indispensable para el Menú Principal
        self.spr_x_normal = cargar_boton_escalado("boton-x.png", self.W_BOTON_HUD, self.H_BOTON_HUD)
        self.spr_x_hover = aclarar_boton(self.spr_x_normal)
        self.spr_x_semi = None
        self.spr_x_apretado = None

        self.fondo_btn_x = None

        # Botones principales con proporción nativa exacta 3.4000 (5440x1600 -> 272x80)
        self.ANCHO_BOTON, self.ALTO_BOTON, self.ESPACIO = 272, 80, 14
        self.x_centro = (self.ANCHO_MENU - self.ANCHO_BOTON) // 2
        self.total_h_menu = (self.ALTO_BOTON * 4) + (self.ESPACIO * 3)
        self.y_inicio_principal = (self.ALTO_MENU - self.total_h_menu) // 2 + 35

        self.spr_jugar_normal = cargar_boton_escalado("Menu/jugar.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("jugar.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_jugar_hover = aclarar_boton(self.spr_jugar_normal)
        self.spr_jugar_semi = cargar_boton_escalado("Menu/jugar-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("jugar-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_jugar_apretado = cargar_boton_escalado("Menu/jugar-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("jugar-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)

        self.spr_personajes_normal = cargar_boton_escalado("Menu/personajes.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("personajes.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_personajes_hover = aclarar_boton(self.spr_personajes_normal)
        self.spr_personajes_semi = cargar_boton_escalado("Menu/personajes-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("personajes-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_personajes_apretado = cargar_boton_escalado("Menu/personajes-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("personajes-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)

        self.spr_opciones_normal = cargar_boton_escalado("Menu/opciones.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("opciones.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_opciones_hover = aclarar_boton(self.spr_opciones_normal)
        self.spr_opciones_semi = cargar_boton_escalado("Menu/opciones-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("opciones-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_opciones_apretado = cargar_boton_escalado("Menu/opciones-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("opciones-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)

        self.spr_salir_normal = cargar_boton_escalado("Menu/salir.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("salir.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_salir_hover = aclarar_boton(self.spr_salir_normal)
        self.spr_salir_semi = cargar_boton_escalado("Menu/salir-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("salir-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
        self.spr_salir_apretado = cargar_boton_escalado("Menu/salir-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON) or cargar_boton_escalado("salir-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)

        self.btn_jugar = pygame.Rect(self.x_centro, self.y_inicio_principal, self.ANCHO_BOTON, self.ALTO_BOTON)
        self.btn_personajes = pygame.Rect(self.x_centro, self.y_inicio_principal + (self.ALTO_BOTON + self.ESPACIO), self.ANCHO_BOTON, self.ALTO_BOTON)
        self.btn_config = pygame.Rect(self.x_centro, self.y_inicio_principal + (self.ALTO_BOTON + self.ESPACIO) * 2, self.ANCHO_BOTON, self.ALTO_BOTON)
        self.btn_salir = pygame.Rect(self.x_centro, self.y_inicio_principal + (self.ALTO_BOTON + self.ESPACIO) * 3, self.ANCHO_BOTON, self.ALTO_BOTON)

        self.fondo_limpio_btn = pygame.Surface((self.ANCHO_BOTON, self.ALTO_BOTON))
        self.fondo_limpio_btn.fill((30, 30, 30))

        self.color_p1 = "Celeste"
        self.color_p2 = "Violeta"
        self.accesorio_p1, self.accesorio_p2 = _seleccionar_accesorios_sesion_aleatorios(self.color_p1, self.color_p2)
        self.personalizacion_modificada_en_menu = False
        self.tab_personajes_actual = "colores"
        self.items_por_pag = 6
        self.disp_p1_todos = [a["id"] for a in obtener_accesorios_disponibles(self.color_p1)]
        self.disp_p2_todos = [a["id"] for a in obtener_accesorios_disponibles(self.color_p2)]
        self.pagina_acc_p1 = (self.disp_p1_todos.index(self.accesorio_p1) // self.items_por_pag) if self.accesorio_p1 in self.disp_p1_todos else 0
        self.pagina_acc_p2 = (self.disp_p2_todos.index(self.accesorio_p2) // self.items_por_pag) if self.accesorio_p2 in self.disp_p2_todos else 0

        self.W_VOLVER, self.H_VOLVER = 238, 70
        self.btn_volver_personajes = pygame.Rect((self.ANCHO_MENU - self.W_VOLVER) // 2, self.ALTO_MENU - 75, self.W_VOLVER, self.H_VOLVER)
        self.btn_guardar = self.btn_volver_personajes
        self.btn_volver_config = pygame.Rect((self.ANCHO_MENU - self.W_VOLVER) // 2, self.ALTO_MENU - 75, self.W_VOLVER, self.H_VOLVER)
        self.btn_volver_creditos = pygame.Rect((self.ANCHO_MENU - self.W_VOLVER) // 2, self.ALTO_MENU - 85, self.W_VOLVER, self.H_VOLVER)

        self.seccion_opciones_actual = "configuracion"
        self.rect_btn_sec_cfg = pygame.Rect(70, 120, 240, 64)
        self.rect_btn_sec_ctrl = pygame.Rect(70, 200, 240, 64)
        self.rect_btn_sec_inst = pygame.Rect(70, 280, 240, 64)
        self.rect_btn_x_opciones = pygame.Rect(self.ANCHO_MENU - 62, 16, 44, 52)

        # Iconos superiores exclusivos de Selección de Niveles (Configuración, Casita y X) con proporción nativa 0.8496
        self.W_ICONO_NIVELES, self.H_ICONO_NIVELES = 44, 52
        self.rect_btn_x_niveles = pygame.Rect(self.ANCHO_MENU - self.MARGEN_DER - self.W_ICONO_NIVELES, self.MARGEN_SUP, self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
        self.rect_btn_casa_niveles = pygame.Rect(self.rect_btn_x_niveles.left - 12 - self.W_ICONO_NIVELES, self.MARGEN_SUP, self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
        self.rect_btn_config_niveles = pygame.Rect(self.rect_btn_casa_niveles.left - 12 - self.W_ICONO_NIVELES, self.MARGEN_SUP, self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)

        # Botones interactivos para Modo de Juego (Continuar vs Nueva Partida)
        self.W_MODO, self.H_MODO = 425, 100
        self.x_modo = (self.ANCHO_MENU - self.W_MODO) // 2
        self.btn_continuar = pygame.Rect(self.x_modo, (self.ALTO_MENU // 2) - 85, self.W_MODO, self.H_MODO)
        self.btn_nueva_partida = pygame.Rect(self.x_modo, (self.ALTO_MENU // 2) + 35, self.W_MODO, self.H_MODO)
        self.btn_volver_modo = pygame.Rect((self.ANCHO_MENU - self.W_VOLVER) // 2, self.ALTO_MENU - 85, self.W_VOLVER, self.H_VOLVER)

        # Variables de sprites de submenús (inicialmente None, carga bajo demanda)
        self.spr_casa_normal = None
        self.spr_casa_hover = None
        self.spr_casa_semi = None
        self.spr_casa_apretado = None

        self.spr_confign_normal = None
        self.spr_confign_hover = None
        self.spr_confign_semi = None
        self.spr_confign_apretado = None

        self.spr_xn_normal = None
        self.spr_xn_hover = None
        self.spr_xn_semi = None
        self.spr_xn_apretado = None

        self.spr_volver_normal = None
        self.spr_volver_hover = None
        self.spr_volver_semi = None
        self.spr_volver_apretado = None

        self.spr_volver_modo_normal = None
        self.spr_volver_modo_hover = None
        self.spr_volver_modo_semi = None
        self.spr_volver_modo_apretado = None

        self.spr_menu_nav_normal = None
        self.spr_menu_nav_hover = None
        self.spr_menu_nav_semi = None
        self.spr_menu_nav_apretado = None

        self.spr_continuar_normal = None
        self.spr_continuar_hover = None
        self.spr_continuar_semi = None
        self.spr_continuar_apretado = None

        self.spr_nueva_modo_normal = None
        self.spr_nueva_modo_hover = None
        self.spr_nueva_modo_semi = None
        self.spr_nueva_modo_apretado = None

        self.spr_nueva_lista_normal = None
        self.spr_nueva_lista_hover = None
        self.spr_nueva_lista_semi = None
        self.spr_nueva_lista_apretado = None

        self.spr_volver_partidas_normal = None
        self.spr_volver_partidas_hover = None
        self.spr_volver_partidas_semi = None
        self.spr_volver_partidas_apretado = None

        self.spr_nueva_primera_normal = None
        self.spr_nueva_primera_hover = None
        self.spr_nueva_primera_semi = None
        self.spr_nueva_primera_apretado = None

        self.spr_cargar_normal = None
        self.spr_cargar_hover = None
        self.spr_cargar_semi = None
        self.spr_cargar_apretado = None

        self.dict_sprites_tarjeta = {
            "cargar_normal": None,
            "cargar_hover": None,
            "cargar_semi": None,
            "cargar_apretado": None,
            "gestionar_normal": None,
            "gestionar_hover": None,
            "gestionar_semi": None,
            "gestionar_apretado": None,
            "borrar_normal": None,
            "borrar_hover": None,
            "borrar_semi": None,
            "borrar_apretado": None,
        }

        self.TAM_CTRL = 54
        self.spr_ctrl_w = None
        self.spr_ctrl_a = None
        self.spr_ctrl_s = None
        self.spr_ctrl_d = None
        self.spr_ctrl_arr = None
        self.spr_ctrl_izq = None
        self.spr_ctrl_aba = None
        self.spr_ctrl_der = None

        def _asegurar_semi_apretados_menu():
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            if self.spr_jugar_semi is None:
                self.spr_jugar_semi = cargar_boton_escalado("jugar-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_jugar_apretado = cargar_boton_escalado("jugar-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_personajes_semi = cargar_boton_escalado("personajes-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_personajes_apretado = cargar_boton_escalado("personajes-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_opciones_semi = cargar_boton_escalado("opciones-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_opciones_apretado = cargar_boton_escalado("opciones-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_salir_semi = cargar_boton_escalado("salir-preapretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_salir_apretado = cargar_boton_escalado("salir-apretado.png", self.ANCHO_BOTON, self.ALTO_BOTON)
                self.spr_x_semi = cargar_boton_escalado("boton-x-semiapretado.png", self.W_BOTON_HUD, self.H_BOTON_HUD)
                self.spr_x_apretado = cargar_boton_escalado("boton-x-apretado.png", self.W_BOTON_HUD, self.H_BOTON_HUD)
        self._asegurar_semi_apretados_menu = _asegurar_semi_apretados_menu

        def _cargar_recursos_volver():
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            if self.spr_volver_normal is None:
                self.spr_volver_normal = cargar_boton_escalado("mundos/boton-volver.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_volver_hover = aclarar_boton(self.spr_volver_normal)
                self.spr_volver_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_volver_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", self.W_VOLVER, self.H_VOLVER)

                self.spr_menu_nav_normal = cargar_boton_escalado("Ventanas/boton-menu.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_menu_nav_hover = aclarar_boton(self.spr_menu_nav_normal)
                self.spr_menu_nav_semi = cargar_boton_escalado("Ventanas/boton-menu-semiapretado.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_menu_nav_apretado = cargar_boton_escalado("Ventanas/boton-menu-apretado.png", self.W_VOLVER, self.H_VOLVER)
        self._cargar_recursos_volver = _cargar_recursos_volver

        def _cargar_recursos_modo_juego():
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            self._cargar_recursos_volver()
            if self.spr_continuar_normal is None:
                # Botones oficiales de la carpeta Sprites/Botones
                self.spr_continuar_normal = cargar_boton_escalado("Menu/boton-continuar-cargar....png", self.W_MODO, self.H_MODO) or cargar_boton_escalado("boton-continuar-cargar....png", self.W_MODO, self.H_MODO)
                self.spr_continuar_hover = aclarar_boton(self.spr_continuar_normal)
                self.spr_continuar_semi = cargar_boton_escalado("Menu/boton-continuar-cargar...-semiapretado.png", self.W_MODO, self.H_MODO) or cargar_boton_escalado("boton-continuar-cargar...-semiapretado.png", self.W_MODO, self.H_MODO)
                self.spr_continuar_apretado = cargar_boton_escalado("Menu/boton-continuar-cargar...-apretado.png", self.W_MODO, self.H_MODO) or cargar_boton_escalado("boton-continuar-cargar...-apretado.png", self.W_MODO, self.H_MODO)

                self.spr_nueva_modo_normal = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", self.W_MODO, self.H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar....png", self.W_MODO, self.H_MODO)
                self.spr_nueva_modo_hover = aclarar_boton(self.spr_nueva_modo_normal)
                self.spr_nueva_modo_semi = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar...-semiapretado.png", self.W_MODO, self.H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar...-semiapretado.png", self.W_MODO, self.H_MODO)
                self.spr_nueva_modo_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar...-apretado.png", self.W_MODO, self.H_MODO) or cargar_boton_escalado("boton-nueva-partida-reiniciar...-apretado.png", self.W_MODO, self.H_MODO)

                self.spr_volver_modo_normal = cargar_boton_escalado("mundos/boton-volver.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-volver.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_volver_modo_hover = aclarar_boton(self.spr_volver_modo_normal)
                self.spr_volver_modo_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-volver-semiapretado.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_volver_modo_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-volver-apretado.png", self.W_VOLVER, self.H_VOLVER)
        self._cargar_recursos_modo_juego = _cargar_recursos_modo_juego

        def _cargar_recursos_partidas():
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            self._cargar_recursos_volver()
            if self.spr_nueva_lista_normal is None:
                # Botones oficiales para la lista de partidas guardadas
                self.spr_nueva_lista_normal = cargar_boton_escalado("mundos/boton-nueva-partida.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-nueva-partida.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_nueva_lista_hover = aclarar_boton(self.spr_nueva_lista_normal)
                self.spr_nueva_lista_semi = cargar_boton_escalado("mundos/boton-nueva-partida-semiapretado.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-nueva-partida-semiapretado.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_nueva_lista_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-apretado.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-nueva-partida-apretado.png", self.W_VOLVER, self.H_VOLVER)

                self.spr_volver_partidas_normal = cargar_boton_escalado("mundos/boton-volver.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-volver.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_volver_partidas_hover = aclarar_boton(self.spr_volver_partidas_normal)
                self.spr_volver_partidas_semi = cargar_boton_escalado("mundos/boton-volver-semiapretado.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-volver-semiapretado.png", self.W_VOLVER, self.H_VOLVER)
                self.spr_volver_partidas_apretado = cargar_boton_escalado("mundos/boton-volver-apretado.png", self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("boton-volver-apretado.png", self.W_VOLVER, self.H_VOLVER)

                self.spr_nueva_primera_normal = cargar_boton_escalado("mundos/boton-nueva-partida.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida.png", 272, 80)
                self.spr_nueva_primera_hover = aclarar_boton(self.spr_nueva_primera_normal)
                self.spr_nueva_primera_semi = cargar_boton_escalado("mundos/boton-nueva-partida-semiapretado.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida-semiapretado.png", 272, 80)
                self.spr_nueva_primera_apretado = cargar_boton_escalado("mundos/boton-nueva-partida-apretado.png", 272, 80) or cargar_boton_escalado("boton-nueva-partida-apretado.png", 272, 80)

                # Botón oficial CARGAR en tarjetas de partida
                self.spr_cargar_normal = cargar_boton_escalado("mundos/boton-cargar.png", 126, 38) or cargar_boton_escalado("boton-cargar.png", 126, 38)
                self.spr_cargar_hover = aclarar_boton(self.spr_cargar_normal)
                self.spr_cargar_semi = cargar_boton_escalado("mundos/boton-cargar-semiapretado.png", 126, 38) or cargar_boton_escalado("boton-cargar-semiapretado.png", 126, 38)
                self.spr_cargar_apretado = cargar_boton_escalado("mundos/boton-cargar-apretado.png", 126, 38) or cargar_boton_escalado("boton-cargar-apretado.png", 126, 38)

                # Botones temáticos GESTIONAR y BORRAR basados en los marcos oficiales de Sprites/Botones
                spr_gest_normal = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 0)
                spr_gest_hover = aclarar_boton(spr_gest_normal)
                spr_gest_semi = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 1)
                spr_gest_apretado = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, "GESTIONAR", (82, 83, 83), 13, 2)

                spr_borrar_normal = generar_boton_con_texto("Menu/salir.png", 96, 38, "BORRAR", (125, 48, 17), 14, 0)
                spr_borrar_hover = aclarar_boton(spr_borrar_normal)
                spr_borrar_semi = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, "BORRAR", (125, 48, 17), 14, 1)
                spr_borrar_apretado = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, "BORRAR", (125, 48, 17), 14, 2)

                self.dict_sprites_tarjeta["cargar_normal"] = self.spr_cargar_normal
                self.dict_sprites_tarjeta["cargar_hover"] = self.spr_cargar_hover
                self.dict_sprites_tarjeta["cargar_semi"] = self.spr_cargar_semi
                self.dict_sprites_tarjeta["cargar_apretado"] = self.spr_cargar_apretado

                self.dict_sprites_tarjeta["gestionar_normal"] = spr_gest_normal
                self.dict_sprites_tarjeta["gestionar_hover"] = spr_gest_hover
                self.dict_sprites_tarjeta["gestionar_semi"] = spr_gest_semi
                self.dict_sprites_tarjeta["gestionar_apretado"] = spr_gest_apretado

                self.dict_sprites_tarjeta["borrar_normal"] = spr_borrar_normal
                self.dict_sprites_tarjeta["borrar_hover"] = spr_borrar_hover
                self.dict_sprites_tarjeta["borrar_semi"] = spr_borrar_semi
                self.dict_sprites_tarjeta["borrar_apretado"] = spr_borrar_apretado
        self._cargar_recursos_partidas = _cargar_recursos_partidas

        def _cargar_recursos_niveles():
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            if self.spr_casa_normal is None:
                self.spr_casa_normal = cargar_boton_escalado("HUD/boton-casa.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
                self.spr_casa_hover = aclarar_boton(self.spr_casa_normal)
                self.spr_casa_semi = cargar_boton_escalado("HUD/boton-casa-semiapretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa-semiapretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
                self.spr_casa_apretado = cargar_boton_escalado("HUD/boton-casa-apretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-casa-apretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)

                self.spr_confign_normal = cargar_boton_escalado("HUD/boton-configuracion.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
                self.spr_confign_hover = aclarar_boton(self.spr_confign_normal)
                self.spr_confign_semi = cargar_boton_escalado("HUD/boton-configuracion-semiapretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion-semiapretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
                self.spr_confign_apretado = cargar_boton_escalado("HUD/boton-configuracion-apretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-configuracion-apretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)

                self.spr_xn_normal = cargar_boton_escalado("HUD/boton-x.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-x.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
                self.spr_xn_hover = aclarar_boton(self.spr_xn_normal)
                self.spr_xn_semi = cargar_boton_escalado("HUD/boton-x-semiapretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-x-semiapretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
                self.spr_xn_apretado = cargar_boton_escalado("HUD/boton-x-apretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES) or cargar_boton_escalado("boton-x-apretado.png", self.W_ICONO_NIVELES, self.H_ICONO_NIVELES)
        self._cargar_recursos_niveles = _cargar_recursos_niveles

        def _cargar_recursos_controles():
            pass  # (antes: nonlocal; ahora son atributos de m)
            pass  # (antes: nonlocal; ahora son atributos de m)
            self._cargar_recursos_volver()
            if self.spr_ctrl_w is None:
                self.spr_ctrl_w = cargar_boton_escalado("Controles/boton-w.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_a = cargar_boton_escalado("Controles/boton-a.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_s = cargar_boton_escalado("Controles/boton-s.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_d = cargar_boton_escalado("Controles/boton-d.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_arr = cargar_boton_escalado("Controles/boton-arriba.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_izq = cargar_boton_escalado("Controles/boton-izquierda.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_aba = cargar_boton_escalado("Controles/boton-abajo.png", self.TAM_CTRL, self.TAM_CTRL)
                self.spr_ctrl_der = cargar_boton_escalado("Controles/boton-derecha.png", self.TAM_CTRL, self.TAM_CTRL)
        self._cargar_recursos_controles = _cargar_recursos_controles

        # Cargar y preparar de forma anticipada todos los recursos de botones para todas las pantallas
        self._asegurar_semi_apretados_menu()
        self._cargar_recursos_volver()
        self._cargar_recursos_modo_juego()
        self._cargar_recursos_partidas()
        self._cargar_recursos_niveles()
        self._cargar_recursos_controles()

        # Funciones de soporte dinámico multiidioma para botones
        self._cache_botones_modo = {}
        self._cache_botones_volver = {}
        self._cache_botones_nueva_lista = {}
        self._cache_botones_primera = {}
        self._cache_sprites_tarjeta = {}
        self._cache_botones_menu = {}

        def _obtener_boton_modo(tipo, estado, idioma):
            tipo_norm = "nueva" if tipo in ("nueva", "nueva_partida") else tipo
            if idioma == "es":
                if tipo_norm == "continuar":
                    if estado == "hover": return self.spr_continuar_hover
                    if estado == "semi": return self.spr_continuar_semi
                    if estado == "apretado": return self.spr_continuar_apretado
                    return self.spr_continuar_normal
                else:
                    if estado == "hover": return self.spr_nueva_modo_hover
                    if estado == "semi": return self.spr_nueva_modo_semi
                    if estado == "apretado": return self.spr_nueva_modo_apretado
                    return self.spr_nueva_modo_normal

            clave = (tipo_norm, estado, idioma)
            if clave in self._cache_botones_modo:
                return self._cache_botones_modo[clave]

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

            w, h = self.W_MODO, self.H_MODO
            btn_base = cargar_boton_escalado(base_path, w, h)
            if not btn_base:
                btn_base = cargar_boton_escalado("mundos/boton-nueva-partida-reiniciar....png", w, h)
            surf = btn_base.copy()

            # Limpiar suavemente solo la cara interior manteniendo intactos los bordes y biseles 3D
            shift_y = 10 if estado == 'apretado' else (5 if estado == 'semi' else 0)
            pad_top = 6 + shift_y
            h_int = 68
            rect_interior = pygame.Rect(6, pad_top, w - 12, h_int)
            pygame.draw.rect(surf, col_bg, rect_interior)

            if idioma == "zh":
                f_tit = obtener_fuente_cjk(24, negrita=True)
                f_sub = obtener_fuente_cjk(14, negrita=False)
                t_tit = f_tit.render(tit, True, col_tit)
            else:
                _, t_tit = renderizar_texto_pixamuse(tit, 20, col_tit, max_w=w - 24)
                f_sub = obtener_fuente_para_texto(sub, categoria="texto", tamano=12, negrita=False)

            t_sub = f_sub.render(sub, True, col_sub)

            offset_y = shift_y
            bbox_tit = t_tit.get_bounding_rect()
            if bbox_tit.width > 0 and bbox_tit.height > 0:
                surf.blit(t_tit, (round(w / 2.0 - (bbox_tit.left + bbox_tit.width / 2.0)), round(30 + offset_y - (bbox_tit.top + bbox_tit.height / 2.0))))
            else:
                surf.blit(t_tit, t_tit.get_rect(center=(w // 2, 30 + offset_y)))

            r_sub = t_sub.get_rect(center=(w // 2, 59 + offset_y))
            surf.blit(t_sub, r_sub)

            if estado == "hover":
                surf = aclarar_boton(surf)

            self._cache_botones_modo[clave] = surf
            return surf
        self._obtener_boton_modo = _obtener_boton_modo

        def _obtener_boton_volver(estado, idioma, w=self.W_VOLVER, h=self.H_VOLVER):
            if idioma == "es":
                if w == self.W_VOLVER and h == self.H_VOLVER:
                    if estado == "hover": return self.spr_volver_modo_hover
                    if estado == "semi": return self.spr_volver_modo_semi
                    if estado == "apretado": return self.spr_volver_modo_apretado
                    return self.spr_volver_modo_normal
                base_p = "mundos/boton-volver.png"
                if estado == "semi": base_p = "mundos/boton-volver-semiapretado.png"
                elif estado == "apretado": base_p = "mundos/boton-volver-apretado.png"
                btn = cargar_boton_escalado(base_p, w, h) or cargar_boton_escalado("mundos/boton-volver.png", w, h)
                if estado == "hover":
                    btn = aclarar_boton(btn)
                return btn

            clave = (estado, idioma, w, h)
            if clave in self._cache_botones_volver:
                return self._cache_botones_volver[clave]

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
            shift_y = 7 if estado == 'apretado' else (3 if estado == 'semi' else 0)
            pad_top = 5 + shift_y
            h_face = 44
            rect_interior = pygame.Rect(6, pad_top, w - 12, h_face)
            pygame.draw.rect(surf, col_interior, rect_interior)

            txt_v = t("volver")
            if idioma == "zh":
                f_v = obtener_fuente_cjk(min(24, max(12, int(round(h * 0.40)))), negrita=True)
                t_v = f_v.render(txt_v, True, (60, 60, 60))
            else:
                _, t_v = renderizar_texto_pixamuse(txt_v, max(10, int(round(h * 0.29))), (60, 60, 60), max_w=w - 20)

            cy_v = round(h * 0.42) + shift_y
            bbox_v = t_v.get_bounding_rect()
            if bbox_v.width > 0 and bbox_v.height > 0:
                surf.blit(t_v, (round(w / 2.0 - (bbox_v.left + bbox_v.width / 2.0)), round(cy_v - (bbox_v.top + bbox_v.height / 2.0))))
            else:
                surf.blit(t_v, t_v.get_rect(center=(w // 2, cy_v)))

            if estado == "hover":
                surf = aclarar_boton(surf)

            self._cache_botones_volver[clave] = surf
            return surf
        self._obtener_boton_volver = _obtener_boton_volver

        def _obtener_boton_nueva_lista(estado, idioma):
            if idioma == "es":
                if estado == "hover": return self.spr_nueva_lista_hover
                if estado == "semi": return self.spr_nueva_lista_semi
                if estado == "apretado": return self.spr_nueva_lista_apretado
                return self.spr_nueva_lista_normal

            clave = (estado, idioma)
            if clave in self._cache_botones_nueva_lista:
                return self._cache_botones_nueva_lista[clave]

            base_path = "mundos/boton-nueva-partida.png"
            offset_y = 0
            if estado == "semi":
                base_path = "mundos/boton-nueva-partida-semiapretado.png"
                offset_y = 1
            elif estado == "apretado":
                base_path = "mundos/boton-nueva-partida-apretado.png"
                offset_y = 2

            btn_base = cargar_boton_escalado(base_path, self.W_VOLVER, self.H_VOLVER) or cargar_boton_escalado("mundos/boton-nueva-partida.png", self.W_VOLVER, self.H_VOLVER)
            surf = btn_base.copy()

            col_interior = (255, 159, 99) if estado not in ("semi", "apretado") else ((242, 148, 91) if estado == "semi" else (223, 132, 79))
            shift_y = 7 if estado == 'apretado' else (3 if estado == 'semi' else 0)
            pad_top = 5 + shift_y
            h_face = 44
            rect_interior = pygame.Rect(6, pad_top, self.W_VOLVER - 12, h_face)
            pygame.draw.rect(surf, col_interior, rect_interior)

            txt_nl = t("nueva_partida")
            if idioma == "zh":
                f_nl = obtener_fuente_cjk(20, negrita=True)
                t_nl = f_nl.render(txt_nl, True, (115, 35, 20))
            else:
                _, t_nl = renderizar_texto_pixamuse(txt_nl, max(10, int(round(self.H_VOLVER * 0.28))), (115, 35, 20), max_w=self.W_VOLVER - 20)

            cy_nl = round(self.H_VOLVER * 0.42) + shift_y
            bbox_nl = t_nl.get_bounding_rect()
            if bbox_nl.width > 0 and bbox_nl.height > 0:
                surf.blit(t_nl, (round(self.W_VOLVER / 2.0 - (bbox_nl.left + bbox_nl.width / 2.0)), round(cy_nl - (bbox_nl.top + bbox_nl.height / 2.0))))
            else:
                surf.blit(t_nl, t_nl.get_rect(center=(self.W_VOLVER // 2, cy_nl)))

            if estado == "hover":
                surf = aclarar_boton(surf)

            self._cache_botones_nueva_lista[clave] = surf
            return surf
        self._obtener_boton_nueva_lista = _obtener_boton_nueva_lista

        def _obtener_boton_primera_partida(estado, idioma):
            if idioma == "es":
                if estado == "hover": return self.spr_nueva_primera_hover
                if estado == "semi": return self.spr_nueva_primera_semi
                if estado == "apretado": return self.spr_nueva_primera_apretado
                return self.spr_nueva_primera_normal

            clave = (estado, idioma)
            if clave in self._cache_botones_primera:
                return self._cache_botones_primera[clave]

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
            shift_y = 8 if estado == 'apretado' else (4 if estado == 'semi' else 0)
            pad_top = 6 + shift_y
            h_face = 50
            rect_interior = pygame.Rect(6, pad_top, 272 - 12, h_face)
            pygame.draw.rect(surf, col_interior, rect_interior)

            txt_p = t("comenzar_aventura")
            if idioma == "zh":
                f_p = obtener_fuente_cjk(22, negrita=True)
                t_p = f_p.render(txt_p, True, (115, 35, 20))
            else:
                _, t_p = renderizar_texto_pixamuse(txt_p, 22, (115, 35, 20), max_w=272 - 24)

            cy_p = 33 + shift_y
            bbox_p = t_p.get_bounding_rect()
            if bbox_p.width > 0 and bbox_p.height > 0:
                surf.blit(t_p, (round(136 - (bbox_p.left + bbox_p.width / 2.0)), round(cy_p - (bbox_p.top + bbox_p.height / 2.0))))
            else:
                surf.blit(t_p, t_p.get_rect(center=(136, cy_p)))

            if estado == "hover":
                surf = aclarar_boton(surf)

            self._cache_botones_primera[clave] = surf
            return surf
        self._obtener_boton_primera_partida = _obtener_boton_primera_partida

        def _obtener_sprites_tarjeta(idioma):
            if idioma == "es":
                return self.dict_sprites_tarjeta
            if idioma in self._cache_sprites_tarjeta:
                return self._cache_sprites_tarjeta[idioma]

            sp_c_n = generar_boton_con_texto("mundos/boton-cargar.png", 126, 38, t("cargar"), (26, 83, 29), 14, 0, idioma)
            sp_c_h = aclarar_boton(sp_c_n)
            sp_c_s = generar_boton_con_texto("mundos/boton-cargar-semiapretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 1, idioma)
            sp_c_a = generar_boton_con_texto("mundos/boton-cargar-apretado.png", 126, 38, t("cargar"), (26, 83, 29), 14, 2, idioma)

            sp_g_n = generar_boton_con_texto("mundos/boton-volver.png", 118, 38, t("gestionar"), (82, 83, 83), 13, 0, idioma)
            sp_g_h = aclarar_boton(sp_g_n)
            sp_g_s = generar_boton_con_texto("mundos/boton-volver-semiapretado.png", 118, 38, t("gestionar"), (82, 83, 83), 13, 1, idioma)
            sp_g_a = generar_boton_con_texto("mundos/boton-volver-apretado.png", 118, 38, t("gestionar"), (82, 83, 83), 13, 2, idioma)

            sp_b_n = generar_boton_con_texto("Menu/salir.png", 96, 38, t("borrar"), (125, 48, 17), 14, 0, idioma)
            sp_b_h = aclarar_boton(sp_b_n)
            sp_b_s = generar_boton_con_texto("Menu/salir-preapretado.png", 96, 38, t("borrar"), (125, 48, 17), 14, 1, idioma)
            sp_b_a = generar_boton_con_texto("Menu/salir-apretado.png", 96, 38, t("borrar"), (125, 48, 17), 14, 2, idioma)

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
            self._cache_sprites_tarjeta[idioma] = res
            return res
        self._obtener_sprites_tarjeta = _obtener_sprites_tarjeta

        def _obtener_boton_menu_principal_estado(tipo, estado, idioma):
            if idioma == "es":
                if tipo == "jugar":
                    if estado == "hover": return self.spr_jugar_hover
                    if estado == "semi": return self.spr_jugar_semi
                    if estado == "apretado": return self.spr_jugar_apretado
                    return self.spr_jugar_normal
                elif tipo == "personajes":
                    if estado == "hover": return self.spr_personajes_hover
                    if estado == "semi": return self.spr_personajes_semi
                    if estado == "apretado": return self.spr_personajes_apretado
                    return self.spr_personajes_normal
                elif tipo == "opciones":
                    if estado == "hover": return self.spr_opciones_hover
                    if estado == "semi": return self.spr_opciones_semi
                    if estado == "apretado": return self.spr_opciones_apretado
                    return self.spr_opciones_normal
                elif tipo == "salir":
                    if estado == "hover": return self.spr_salir_hover
                    if estado == "semi": return self.spr_salir_semi
                    if estado == "apretado": return self.spr_salir_apretado
                    return self.spr_salir_normal

            clave = (tipo, estado, idioma)
            if clave in self._cache_botones_menu:
                return self._cache_botones_menu[clave]

            cfg_botones = {
                "jugar": ("Menu/jugar", (27, 82, 36), 26),
                "personajes": ("Menu/personajes", (42, 68, 124), 22 if idioma == "en" else 24),
                "opciones": ("Menu/opciones", (115, 67, 16), 26),
                "salir": ("Menu/salir", (127, 49, 19), 26),
            }
            base_name, col_txt, sz = cfg_botones[tipo]

            if estado == "normal":
                sprite_path = f"{base_name}.png"
                offset_y = 0
                surf = generar_boton_con_texto(sprite_path, self.ANCHO_BOTON, self.ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
            elif estado == "hover":
                norm = self._obtener_boton_menu_principal_estado(tipo, "normal", idioma)
                surf = aclarar_boton(norm)
            elif estado == "semi":
                pre_name = f"{base_name}-preapretado.png"
                sprite_path = pre_name
                offset_y = 4
                surf = generar_boton_con_texto(sprite_path, self.ANCHO_BOTON, self.ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
            elif estado == "apretado":
                apr_name = f"{base_name}-apretado.png"
                sprite_path = apr_name
                offset_y = 8
                surf = generar_boton_con_texto(sprite_path, self.ANCHO_BOTON, self.ALTO_BOTON, t(tipo), col_txt, sz, offset_y, idioma)
            else:
                surf = None

            self._cache_botones_menu[clave] = surf
            return surf
        self._obtener_boton_menu_principal_estado = _obtener_boton_menu_principal_estado

        def _obtener_botones_menu_principal(idioma):
            return [
                (self.btn_jugar, self._obtener_boton_menu_principal_estado("jugar", "normal", idioma), self._obtener_boton_menu_principal_estado("jugar", "hover", idioma)),
                (self.btn_personajes, self._obtener_boton_menu_principal_estado("personajes", "normal", idioma), self._obtener_boton_menu_principal_estado("personajes", "hover", idioma)),
                (self.btn_config, self._obtener_boton_menu_principal_estado("opciones", "normal", idioma), self._obtener_boton_menu_principal_estado("opciones", "hover", idioma)),
                (self.btn_salir, self._obtener_boton_menu_principal_estado("salir", "normal", idioma), self._obtener_boton_menu_principal_estado("salir", "hover", idioma)),
            ]
        self._obtener_botones_menu_principal = _obtener_botones_menu_principal

        # Instanciar el gestor del escenario interactivo y personajes autónomos del Menú Principal
        self.gestor_personajes_menu = GestorPersonajesMenu(
            ancho=self.ANCHO_MENU,
            alto=self.ALTO_MENU,
            color_p1=self.color_p1,
            accesorio_p1=self.accesorio_p1,
            color_p2=self.color_p2,
            accesorio_p2=self.accesorio_p2,
        )

        # Renderizar el primer fotograma del Menú Principal con todos los botones e interfaz completamente listos
        self.pantalla.fill((30, 30, 30))
        self.pos_mouse_inicial = pygame.mouse.get_pos()
        self.botones_menu_datos_ini = self._obtener_botones_menu_principal(obtener_idioma())
        self.gestor_personajes_menu.dibujar_menu_completo(
            self.pantalla,
            botones_menu_datos=self.botones_menu_datos_ini,
            pos_mouse=self.pos_mouse_inicial,
            spr_x=self.spr_x_normal,
            rect_x=self.rect_btn_x,
            fuente_titulo=self.fuente_pixel_titulo,
        )
        pygame.display.flip()

        # Geometría y variables para la Lista de Partidas Guardadas
        self.pagina_partidas = 0
        self.MAX_PARTIDAS_POR_PAGINA = 4
        self.rect_panel_partidas, self.btn_volver_partidas, self.btn_nueva_desde_lista, self.btn_iniciar_primera = (
            obtener_geometria_panel_partidas(self.ANCHO_MENU, self.ALTO_MENU)
        )

        self.fondo_btn_config_niveles = None
        self.fondo_btn_casa_niveles = None
        self.fondo_btn_x_niveles = None
        self.fondo_btn_x_main = None

        self.estado_actual = ESTADO_MENU_PRINCIPAL
        self.mundo_seleccionado = 1
        self.ejecutando = True
        self._ultimo_idioma_menu = obtener_idioma()

        def intentar_salir():
            pass  # (antes: nonlocal; ahora son atributos de m)
            if self.sesion_activa and hay_progreso_sin_guardar(self.niveles_desbloqueados, self.snapshot_guardado, id_partida=self.partida_actual_id):
                resp = mostrar_dialogo_guardar_salir(
                    self.pantalla, self.reloj,
                    niveles_desbloqueados=self.niveles_desbloqueados,
                    id_partida=self.partida_actual_id,
                    nombre_partida=self.partida_actual_nombre,
                    password_partida=self.partida_actual_password,
                    color_p1=self.color_p1,
                    color_p2=self.color_p2,
                    accesorio_p1=self.accesorio_p1,
                    accesorio_p2=self.accesorio_p2,
                )
                if resp == "guardar_salir":
                    self.snapshot_guardado = copy.deepcopy(self.niveles_desbloqueados)
                    self.ejecutando = False
                elif resp == "salir_sin_guardar":
                    self.ejecutando = False
                elif resp == "cancelar":
                    pass
            else:
                self.ejecutando = False
        self.intentar_salir = intentar_salir
