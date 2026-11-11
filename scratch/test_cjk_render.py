import pygame
import os

pygame.init()
os.makedirs("scratch/test_cjk_render", exist_ok=True)

test_txt = "皮科在公园里的小冒险"

# 1. YaHei bold antialias=False
f_yahei_b = pygame.font.SysFont("Microsoft YaHei", 36, bold=True)
s_yahei_false = f_yahei_b.render(test_txt, False, (255, 255, 255))
pygame.image.save(s_yahei_false, "scratch/test_cjk_render/yahei_b36_aa_false.png")

# 2. YaHei bold antialias=True
s_yahei_true = f_yahei_b.render(test_txt, True, (255, 255, 255))
pygame.image.save(s_yahei_true, "scratch/test_cjk_render/yahei_b36_aa_true.png")

# 3. SimSun bold antialias=False
f_simsun_b = pygame.font.SysFont("SimSun", 36, bold=True)
s_simsun_false = f_simsun_b.render(test_txt, False, (255, 255, 255))
pygame.image.save(s_simsun_false, "scratch/test_cjk_render/simsun_b36_aa_false.png")

# 4. Pixelated / downscaled-upscaled YaHei (crisp retro pixel look)
f_yahei_big = pygame.font.SysFont("Microsoft YaHei", 18, bold=True)
s_yahei_small = f_yahei_big.render(test_txt, False, (255, 255, 255))
s_yahei_pix = pygame.transform.scale(s_yahei_small, (s_yahei_small.get_width() * 2, s_yahei_small.get_height() * 2))
pygame.image.save(s_yahei_pix, "scratch/test_cjk_render/yahei_pixel_scale2.png")

print("Generated CJK test renders!")

