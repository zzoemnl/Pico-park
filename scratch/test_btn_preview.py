import pygame
pygame.init()
s1 = pygame.image.load('Sprites/Botones/Menu/boton-continuar-cargar....png')
s2 = pygame.image.load('Sprites/Botones/mundos/boton-nueva-partida-reiniciar....png')

s1_small = pygame.transform.smoothscale(s1, (680, 160))
s2_small = pygame.transform.smoothscale(s2, (680, 160))
pygame.image.save(s1_small, 'scratch/s1_btn_preview.png')
pygame.image.save(s2_small, 'scratch/s2_btn_preview.png')
print("Saved previews")

