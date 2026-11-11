import pygame
import os
import sys

pygame.init()
f = pygame.font.Font("assets/fuentes/Super Mario Bros. 2.ttf", 18)
print("English size:", f.size("English"))
print("ENGLISH size:", f.size("ENGLISH"))
print("Espanol size:", f.size("Espanol"))
print("ESPANOL size:", f.size("ESPANOL"))

# Render sample images
s_lower = f.render("English", True, (255, 255, 255))
pygame.image.save(s_lower, "scratch/test_english_lower.png")
s_upper = f.render("ENGLISH", True, (255, 255, 255))
pygame.image.save(s_upper, "scratch/test_english_upper.png")

