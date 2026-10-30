"""
Prueba de diversidad y distribución de superficies para los 5 personajes.
Mide durante 1200 frames que no todos estén en el techo o paredes al mismo tiempo,
y que utilicen suelo, plataformas, paredes y techo de forma orgánica.
"""
import random
import sys
import os

# Configuración de prueba de simulación de estados
class MockCharacter:
    def __init__(self, idx, sup_ini, x_ini, y_ini):
        self.idx = idx
        self.superficie = sup_ini
        self.x = x_ini
        self.y = y_ini
        self.accion = "caminar"
        self.tiempo = random.randint(30, 90)

# Probabilidades de transición equilibradas
def simular_decision(c):
    rnd = random.random()
    sup = c.superficie

    if sup == "suelo":
        if rnd < 0.28:
            c.accion = "quieto"
            c.tiempo = random.randint(40, 110)
        elif rnd < 0.65:
            c.accion = "caminar"
            c.tiempo = random.randint(50, 140)
        elif rnd < 0.85:
            # Subir a plataforma
            c.superficie = "plataforma"
            c.accion = "caminar"
            c.tiempo = random.randint(40, 100)
        else:
            # Trepar pared
            c.superficie = "pared_izq" if random.random() < 0.5 else "pared_der"
            c.accion = "trepar"
            c.tiempo = random.randint(40, 80)

    elif sup == "plataforma":
        if rnd < 0.32:
            c.accion = "quieto"
            c.tiempo = random.randint(35, 95)
        elif rnd < 0.62:
            c.accion = "caminar"
            c.tiempo = random.randint(45, 110)
        elif rnd < 0.82:
            # Bajar al suelo
            c.superficie = "suelo"
            c.accion = "caminar"
            c.tiempo = random.randint(40, 90)
        else:
            # Ir a pared o saltar
            c.superficie = "pared_izq" if random.random() < 0.5 else "pared_der"
            c.accion = "trepar"
            c.tiempo = random.randint(35, 75)

    elif sup in ("pared_izq", "pared_der"):
        if rnd < 0.35:
            # Bajar al suelo
            c.superficie = "suelo"
            c.accion = "caminar"
            c.tiempo = random.randint(40, 90)
        elif rnd < 0.65:
            # Saltar a plataforma
            c.superficie = "plataforma"
            c.accion = "caminar"
            c.tiempo = random.randint(40, 80)
        elif rnd < 0.85:
            c.accion = "quieto"
            c.tiempo = random.randint(25, 60)
        else:
            # Llegar al techo
            c.superficie = "techo"
            c.accion = "caminar"
            c.tiempo = random.randint(40, 80)

    elif sup == "techo":
        if rnd < 0.55:
            # Descolgarse al suelo o plataforma
            c.superficie = "suelo" if random.random() < 0.6 else "plataforma"
            c.accion = "caminar"
            c.tiempo = random.randint(40, 90)
        elif rnd < 0.80:
            # Bajar por pared
            c.superficie = "pared_izq" if random.random() < 0.5 else "pared_der"
            c.accion = "bajar"
            c.tiempo = random.randint(40, 80)
        else:
            c.accion = "quieto"
            c.tiempo = random.randint(25, 60)

personajes = [
    MockCharacter(0, "suelo", 200, 650),
    MockCharacter(1, "plataforma", 90, 380),
    MockCharacter(2, "pared_izq", 28, 280),
    MockCharacter(3, "techo", 740, 34),
    MockCharacter(4, "suelo", 980, 650),
]

conteo_superficies = {"suelo": 0, "plataforma": 0, "pared": 0, "techo": 0}
frames_todos_pared_o_techo = 0

for f in range(1200):
    for p in personajes:
        p.tiempo -= 1
        if p.tiempo <= 0:
            simular_decision(p)

        s_key = "pared" if p.superficie in ("pared_izq", "pared_der") else p.superficie
        conteo_superficies[s_key] += 1

    num_pared_techo = sum(1 for p in personajes if p.superficie in ("pared_izq", "pared_der", "techo"))
    if num_pared_techo >= 4:
        frames_todos_pared_o_techo += 1

total_ticks = 1200 * 5
print("Resultados de simulación 1200 frames (20 segundos):")
for s, count in conteo_superficies.items():
    pct = (count / total_ticks) * 100
    print(f"  Superficie {s.upper()}: {pct:.1f}%")

print(f"Frames con 4 o más personajes en pared/techo: {frames_todos_pared_o_techo} / 1200 ({(frames_todos_pared_o_techo/1200)*100:.1f}%)")
