import pygame
pygame.init()
f1 = pygame.font.Font("assets/fuentes/Nanoplex.ttf", 42)
s1 = f1.render("50 %", True, (255, 255, 255))
pygame.image.save(s1, "scratch/test_nanoplex_nobold.png")

f2 = pygame.font.Font("assets/fuentes/Nanoplex.ttf", 42)
f2.set_bold(True)
s2 = f2.render("50 %", True, (255, 255, 255))
pygame.image.save(s2, "scratch/test_nanoplex_withbold.png")
print("s1 size:", s1.get_size(), "s2 size:", s2.get_size())

