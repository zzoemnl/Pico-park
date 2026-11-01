import pygame

pygame.init()
surf = pygame.image.load("scratch/captura_juego_main_real.png")
# Crop title area around the hat and the "AS" of AVENTURILLAS
# Title is centered at 1280 // 2 = 640, top = 40
crop_rect = pygame.Rect(800, 30, 260, 150)
crop = surf.subsurface(crop_rect)
pygame.image.save(crop, "scratch/captura_detalle_gorro_y_s.png")
print("Detalle guardado en scratch/captura_detalle_gorro_y_s.png")
