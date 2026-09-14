import pygame
import sys

pygame.init()

# Configuración de pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pico Park - Apilamiento Estable")
reloj = pygame.time.Clock()

# Colores
AZUL_FONDO = (30, 30, 60)
GRIS_SUELO = (80, 80, 100)
BLANCO = (255, 255, 255)
NEGRO = (20, 20, 20)
MARRON_PUERTA = (120, 70, 30)
AMARILLO_POMO = (255, 215, 0)

ROJO_CUERPO = (245, 90, 85)
ROJO_OSCURO = (190, 50, 50)
VERDE_CUERPO = (85, 220, 120)
VERDE_OSCURO = (40, 160, 70)


class Jugador:
    def __init__(self, x, y, color_cuerpo, color_oscuro):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.ancho = 32
        self.alto = 32
        self.color_cuerpo = color_cuerpo
        self.color_oscuro = color_oscuro
        self.mirando_derecha = True
        self.en_suelo = False
        self.activo = True

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)

    def actualizar_movimiento(self, arriba, izquierda, derecha):
        if not self.activo:
            return

        if derecha:
            self.mirando_derecha = True
        elif izquierda:
            self.mirando_derecha = False

        if izquierda:
            self.vel_x -= 1.0
        if derecha:
            self.vel_x += 1.0

        if arriba and self.en_suelo:
            self.vel_y = -11.0

        gravedad = 0.7
        friccion_x = 0.80

        self.vel_y += gravedad
        self.vel_x *= friccion_x

    def aplicar_movimiento_x(self):
        if self.activo:
            self.x += self.vel_x

    def aplicar_movimiento_y(self):
        if self.activo:
            self.y += self.vel_y

    def dibujar(self, pantalla):
        if not self.activo:
            return

        x, y = int(self.x), int(self.y)

        # Patas
        pygame.draw.circle(pantalla, self.color_oscuro, (x + 8, y + self.alto - 2), 5)
        pygame.draw.circle(pantalla, self.color_oscuro, (x + self.ancho - 8, y + self.alto - 2), 5)

        # Cuerpo
        pygame.draw.rect(pantalla, self.color_cuerpo, (x, y, self.ancho, self.alto), border_radius=8)

        # Ojos
        ojo1_x = x + 18 if self.mirando_derecha else x + 6
        ojo2_x = x + 26 if self.mirando_derecha else x + 14
        ojo_y = y + 10

        pygame.draw.circle(pantalla, BLANCO, (ojo1_x, ojo_y), 4)
        pygame.draw.circle(pantalla, BLANCO, (ojo2_x, ojo_y), 4)

        offset_p = 1 if self.mirando_derecha else -1
        pygame.draw.circle(pantalla, NEGRO, (ojo1_x + offset_p, ojo_y), 2)
        pygame.draw.circle(pantalla, NEGRO, (ojo2_x + offset_p, ojo_y), 2)


def resolver_colisiones(p1, p2, suelo, puerta):
    p1.en_suelo = False
    p2.en_suelo = False

    # 1. MOVIMIENTO EN X
    p1.aplicar_movimiento_x()
    p2.aplicar_movimiento_x()

    if p1.activo and p2.activo:
        rect1 = p1.get_rect()
        rect2 = p2.get_rect()

        # Detección de alineación vertical
        alineados_x = (rect1.left < rect2.right and rect1.right > rect2.left)
        estan_apilados = alineados_x and (abs((p1.y + p1.alto) - p2.y) < 12 or abs((p2.y + p2.alto) - p1.y) < 12)

        # Bloquear colisión lateral si están uno encima del otro
        if rect1.colliderect(rect2) and not estan_apilados:
            if p1.x < p2.x:
                p1.x = p2.x - p1.ancho
            else:
                p1.x = p2.x + p2.ancho

    # Límites de pantalla
    for p in [p1, p2]:
        if p.activo:
            p.x = max(0, min(ANCHO - p.ancho, p.x))

    # 2. MOVIMIENTO EN Y
    p1.aplicar_movimiento_y()
    p2.aplicar_movimiento_y()

    if p1.activo and p2.activo:
        rect1 = p1.get_rect()
        rect2 = p2.get_rect()

        if rect1.colliderect(rect2):
            # CASO 1: P1 esta SOBRE P2
            if (p1.y + p1.alto - p1.vel_y) <= (p2.y - p2.vel_y + 12):
                p1.y = p2.y - p1.alto  # Pegar posición exacta a la cabeza de P2
                p1.vel_y = p2.vel_y    # Mantener exactamente la misma velocidad vertical (al subir y al caer)
                p1.en_suelo = True
                p1.x += p2.vel_x       # Seguir movimiento horizontal de P2

            # CASO 2: P2 esta SOBRE P1
            elif (p2.y + p2.alto - p2.vel_y) <= (p1.y - p1.vel_y + 12):
                p2.y = p1.y - p2.alto  # Pegar posición exacta a la cabeza de P1
                p2.vel_y = p1.vel_y    # Mantener exactamente la misma velocidad vertical (al subir y al caer)
                p2.en_suelo = True
                p2.x += p1.vel_x       # Seguir movimiento horizontal de P1

            # Golpes de cabeza desde abajo
            elif p1.vel_y < 0 and p1.y > p2.y:
                p1.y = p2.y + p2.alto
                p1.vel_y = 0
            elif p2.vel_y < 0 and p2.y > p1.y:
                p2.y = p1.y + p1.alto
                p2.vel_y = 0

    # 3. COLISIÓN CON EL SUELO
    for p in [p1, p2]:
        if p.activo:
            rect_p = p.get_rect()
            if rect_p.colliderect(suelo):
                if p.vel_y >= 0:
                    p.y = suelo.top - p.alto
                    p.vel_y = 0
                    p.en_suelo = True

    # 4. ENTRADA A LA PUERTA
    for p in [p1, p2]:
        if p.activo and p.get_rect().colliderect(puerta):
            p.activo = False


# Inicialización
j1 = Jugador(200, 400, ROJO_CUERPO, ROJO_OSCURO)
j2 = Jugador(260, 400, VERDE_CUERPO, VERDE_OSCURO)

suelo = pygame.Rect(0, 500, ANCHO, 100)
puerta = pygame.Rect(700, 430, 45, 70)

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    teclas = pygame.key.get_pressed()

    # Controles J1 (WASD) y J2 (Flechas)
    w, a, d = teclas[pygame.K_w], teclas[pygame.K_a], teclas[pygame.K_d]
    arriba, izq, der = teclas[pygame.K_UP], teclas[pygame.K_LEFT], teclas[pygame.K_RIGHT]

    j1.actualizar_movimiento(w, a, d)
    j2.actualizar_movimiento(arriba, izq, der)

    resolver_colisiones(j1, j2, suelo, puerta)

    # Renderizado
    pantalla.fill(AZUL_FONDO)
    pygame.draw.rect(pantalla, GRIS_SUELO, suelo)
    pygame.draw.rect(pantalla, MARRON_PUERTA, puerta, border_radius=4)
    pygame.draw.circle(pantalla, AMARILLO_POMO, (puerta.x + 8, puerta.y + 35), 4)

    j1.dibujar(pantalla)
    j2.dibujar(pantalla)

    if not j1.activo and not j2.activo:
        fuente = pygame.font.SysFont(None, 48)
        texto = fuente.render("¡Nivel Completado!", True, BLANCO)
        pantalla.blit(texto, (ANCHO // 2 - 150, 200))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()

#no deja q el personaje de arriba salte y esta medio bugeado