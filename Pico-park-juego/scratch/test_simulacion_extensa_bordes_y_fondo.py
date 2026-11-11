import os
import sys
import time
import unittest
import pygame

DIRECTORIO_JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRECTORIO_JUEGO not in sys.path:
    sys.path.insert(0, DIRECTORIO_JUEGO)

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1280, 720))

from personajes_menu import GestorPersonajesMenu, PLATAFORMAS_ESCENARIO

class TestSimulacionExtensaBordesYFondo(unittest.TestCase):
    def test_simulacion_larga_sin_vibraciones(self):
        """Prueba exhaustiva de 3600 frames (1 minuto completo a 60 FPS)."""
        gestor = GestorPersonajesMenu()
        
        # Contadores de acciones observadas
        acciones_borde = {
            "quieto": 0,
            "giro": 0,
            "salto": 0,
            "bajar": 0,
        }
        
        historial_sup = [[] for _ in range(5)]
        historial_dir = [[] for _ in range(5)]
        historial_x = [[] for _ in range(5)]
        
        ciclos_vibracion = 0
        oscilaciones_rapidas = 0
        superficies_visitadas = {i: set() for i in range(5)}
        
        t_inicio = time.perf_counter()
        
        for frame in range(3600):
            gestor.actualizar()
            
            # Verificar nubes
            self.assertEqual(len(gestor.nubes), 4)
            for nube in gestor.nubes:
                self.assertGreaterEqual(nube["x"], -nube["w"] - 25)
                self.assertLessEqual(nube["x"], gestor.ancho + 45)
            
            # Verificar copos de nieve (ambas capas)
            self.assertEqual(len(gestor.copos_nieve), 85)
            
            # Verificar partículas de humo
            self.assertEqual(len(gestor.particulas_humo), 5)
            
            # Monitorear a cada personaje
            for idx in range(5):
                p = gestor.personajes[idx]
                ai = gestor.ai_estados[idx]
                hb = p["hitbox"]
                sup = p["superficie"]
                direc = ai["direccion"]
                
                superficies_visitadas[idx].add(sup)
                historial_sup[idx].append(sup)
                historial_dir[idx].append(direc)
                historial_x[idx].append(hb.centerx)
                
                # Chequeo estricto de límites
                self.assertGreaterEqual(hb.left, gestor.x_pared_izq - 2)
                self.assertLessEqual(hb.right, gestor.x_pared_der + 2)
                self.assertGreaterEqual(hb.top, gestor.y_techo - 6)
                self.assertLessEqual(hb.bottom, gestor.y_suelo + 2)
                
                # Detectar ciclo vibratorio: plataforma -> aire -> plataforma en <= 3 frames
                if len(historial_sup[idx]) >= 3:
                    if (historial_sup[idx][-3] == "plataforma" and 
                        historial_sup[idx][-2] == "aire" and 
                        historial_sup[idx][-1] == "plataforma"):
                        ciclos_vibracion += 1
                
                # Detectar inversión consecutiva de dirección en <= 3 frames
                if len(historial_dir[idx]) >= 3:
                    d3, d2, d1 = historial_dir[idx][-3], historial_dir[idx][-2], historial_dir[idx][-1]
                    if d1 != 0 and d2 != 0 and d3 != 0 and d1 == -d2 and d2 == -d3:
                        oscilaciones_rapidas += 1
                
                # Registrar si está en borde y qué hace
                if sup == "plataforma":
                    plat = p.get("plat_actual")
                    if plat:
                        dist_izq = hb.left - plat.left
                        dist_der = plat.right - hb.right
                        if dist_izq <= 8 or dist_der <= 8:
                            if ai["estado"] == "quieto":
                                acciones_borde["quieto"] += 1
                            elif ai["estado"] == "caminar":
                                if (dist_izq <= 8 and direc > 0) or (dist_der <= 8 and direc < 0):
                                    acciones_borde["giro"] += 1
                elif sup == "aire":
                    if p.get("ignorar_plat"):
                        acciones_borde["bajar"] += 1
                    if ai.get("intentar_salto"):
                        acciones_borde["salto"] += 1
        
        t_total = time.perf_counter() - t_inicio
        fps_simulado = 3600 / t_total
        
        print(f"\nResultados de simulación (3600 frames):")
        print(f" - FPS de simulación: {fps_simulado:.1f} FPS (tiempo total: {t_total:.2f}s)")
        print(f" - Ciclos de vibración en bordes: {ciclos_vibracion}")
        print(f" - Oscilaciones rápidas de dirección: {oscilaciones_rapidas}")
        print(f" - Acciones en borde: quieto={acciones_borde['quieto']}, giro={acciones_borde['giro']}, bajar={acciones_borde['bajar']}")
        
        self.assertEqual(ciclos_vibracion, 0, "No debe haber ningún ciclo de vibración en bordes")
        self.assertEqual(oscilaciones_rapidas, 0, "No debe haber oscilaciones rápidas de dirección")
        self.assertGreater(fps_simulado, 200, "El rendimiento debe ser ampliamente superior a 60 FPS")

if __name__ == "__main__":
    unittest.main()
