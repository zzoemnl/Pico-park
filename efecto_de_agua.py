import pygame
import sys
import math

pygame.init()

# Configuración de pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel de Agua WASD - Pico Park Style")
reloj = pygame.time.Clock()

# Colores
AZUL_FONDO = (30, 30, 60)
AZUL_AGUA = (0, 140, 240, 130)
ROJO_CUERPO = (245, 90, 85)
ROJO_OSCURO = (190, 50, 50)
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
AMARILLO_META = (255, 215, 0)

# Propiedades del Jugador
pos_x, pos_y = 100, 100
vel_x, vel_y = 0.0, 0.0
ancho_p, alto_p = 32, 32

# Variables de animación
frame_animacion = 0
mirando_derecha = True

# Zonas del nivel
zona_agua = pygame.Rect(0, 220, ANCHO, 380)
meta = pygame.Rect(700, 480, 50, 50)

def dibujar_personaje_nadando(pantalla, x, y, mirando_der, moviendose, en_agua, frame):
    """ Dibuja un personaje estilo Pico Park con animación de nado """
    rect_cuerpo = pygame.Rect(x, y, ancho_p, alto_p)
    
    # Animación de extremidades (pataleo)
    offset_patas = math.sin(frame * 0.3) * 6 if (moviendose and en_agua) else 0

    # 1. Patas / Aletas traseras (al nadar se mueven estilo pataleo)
    pata_izq_x = x + 6
    pata_der_x = x + ancho_p - 10
    pata_y = y + alto_p - 4
    
    pygame.draw.circle(pantalla, ROJO_OSCURO, (int(pata_izq_x), int(pata_y + offset_patas)), 5)
    pygame.draw.circle(pantalla, ROJO_OSCURO, (int(pata_der_x), int(pata_y - offset_patas)), 5)

    # 2. Cuerpo (cuadrado redondeado clásico de Pico Park)
    pygame.draw.rect(pantalla, ROJO_CUERPO, rect_cuerpo, border_radius=8)

    # 3. Ojos estilo Pico Park
    ojo_radio = 4
    pupila_radio = 2
    
    if mirando_der:
        ojo1_x, ojo2_x = x + 18, x + 26
    else:
        ojo1_x, ojo2_x = x + 6, x + 14
        
    ojo_y = y + 10

    # Ojos blancos
    pygame.draw.circle(pantalla, BLANCO, (ojo1_x, ojo_y), ojo_radio)
    pygame.draw.circle(pantalla, BLANCO, (ojo2_x, ojo_y), ojo_radio)
    
    # Pupilas
    offset_pupila = 1 if mirando_der else -1
    pygame.draw.circle(pantalla, NEGRO, (ojo1_x + offset_pupila, ojo_y), pupila_radio)
    pygame.draw.circle(pantalla, NEGRO, (ojo2_x + offset_pupila, ojo_y), pupila_radio)

    # 4. Brazos / Brazadas al nadar
    offset_brazo = math.cos(frame * 0.3) * 5 if (moviendose and en_agua) else 0
    brazo_x = (x + ancho_p - 2) if mirando_der else x + 2
    brazo_y = y + 18 + offset_brazo
    pygame.draw.circle(pantalla, ROJO_OSCURO, (int(brazo_x), int(brazo_y)), 4)


# Bucle Principal
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Lectura de Controles WASD
    teclas = pygame.key.get_pressed()
    tecla_w = teclas[pygame.K_w]
    tecla_a = teclas[pygame.K_a]
    tecla_s = teclas[pygame.K_s]
    tecla_d = teclas[pygame.K_d]

    # Crear Rect del jugador para colisiones
    rect_jugador = pygame.Rect(pos_x, pos_y, ancho_p, alto_p)
    en_agua = zona_agua.colliderect(rect_jugador)

    # Determinar orientación de mirada
    if tecla_d:
        mirando_derecha = True
    elif tecla_a:
        mirando_derecha = False

    moviendose = tecla_w or tecla_a or tecla_s or tecla_d

    # --- FÍSICA ---
    if en_agua:
        # Propiedades físicas dentro del agua
        gravedad = 0.15
        friccion_x = 0.88
        friccion_y = 0.90
        
        # Movimiento fluido en agua con WASD
        if tecla_a:
            vel_x -= 0.6
        if tecla_d:
            vel_x += 0.6
        if tecla_w:  # Nadar hacia arriba
            vel_y -= 0.9
        if tecla_s:  # Nadar / Bucear hacia abajo
            vel_y += 0.5
    else:
        # Propiedades físicas en el aire
        gravedad = 0.7
        friccion_x = 0.82
        friccion_y = 0.98
        
        if tecla_a:
            vel_x -= 1.0
        if tecla_d:
            vel_x += 1.0

    # Aplicar gravedad y fricción
    vel_y += gravedad
    vel_x *= friccion_x
    vel_y *= friccion_y

    # Actualizar posiciones
    pos_x += vel_x
    pos_y += vel_y

    # Limitar pantalla
    pos_x = max(0, min(ANCHO - ancho_p, pos_x))
    pos_y = max(0, min(ALTO - alto_p, pos_y))

    # Avanzar animación si se está moviendo
    if moviendose:
        frame_animacion += 1

    # --- DIBUJO ---
    pantalla.fill(AZUL_FONDO)

    # Dibujar Meta
    pygame.draw.rect(pantalla, AMARILLO_META, meta, border_radius=6)

    # Dibujar Agua con transparencia
    superficie_agua = pygame.Surface((zona_agua.width, zona_agua.height), pygame.SRCALPHA)
    superficie_agua.fill(AZUL_AGUA)
    pantalla.blit(superficie_agua, (zona_agua.x, zona_agua.y))

    # Dibujar Jugador Animado
    dibujar_personaje_nadando(
        pantalla, pos_x, pos_y, 
        mirando_derecha, moviendose, en_agua, frame_animacion
    )

    # Mensaje de Victoria
    if rect_jugador.colliderect(meta):
        fuente = pygame.font.SysFont(None, 40)
        texto = fuente.render("¡Nivel Completado!", True, BLANCO)
        pantalla.blit(texto, (ANCHO // 2 - 120, 80))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()