import pygame
pygame.init()

test_str = "皮科在公园里的小冒险"

fonts_to_test = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "NSimSun",
    "FangSong",
    "KaiTi",
    "DengXian",
    "Segoe UI",
    "Arial Unicode MS",
    "Yu Gothic",
    "Meiryo",
    "Malgun Gothic"
]

results = []
for name in fonts_to_test:
    try:
        f = pygame.font.SysFont(name, 36, bold=True)
        # Render and check if width > 0 and rendered surface is not empty
        s = f.render(test_str, False, (255, 255, 255))
        w, h = s.get_size()
        results.append((name, w, h, True))
    except Exception as e:
        results.append((name, 0, 0, False))

for name, w, h, ok in results:
    if ok and w > 100:
        print(f"Font '{name}': {w}x{h} OK")

