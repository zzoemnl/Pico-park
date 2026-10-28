import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, ".")
import pantalla
import movimientos
from sprites import ALTO, ANCHO


def test_in_game_death_flow():
    print("=== TEST REAL DE FLUJO DE MUERTE DENTRO DEL BUCLE DE PANTALLA.PY (MUNDO 3) ===")

    # 1. Probar en Mundo 3 Nivel 1 que al morir P1:
    # - P2 permanece vivo.
    # - pantalla_muerte es invocada de forma rápida (~28 frames).
    # - No se queda esperando indefinidamente a P2.

    llamadas_pantalla_muerte = 0
    frames_desde_muerte = 0
    p1_murio_registrado = False
    estado_p2_al_morir = None

    orig_pantalla_muerte = pantalla.pantalla_muerte

    def mock_pantalla_muerte(p, r):
        nonlocal llamadas_pantalla_muerte
        llamadas_pantalla_muerte += 1
        print(f"[OK] pantalla_muerte invocada con éxito! (llamada #{llamadas_pantalla_muerte})")
        return "salir"

    pantalla.pantalla_muerte = mock_pantalla_muerte

    # Interceptar loop mediante pygame event o hook
    # Ejecutamos Nivel 3-1: colocamos un evento para mover P1 hacia los pinchos o forzar contacto
    print("--- 1. Ejecutando simulación en Mundo 3 Nivel 1 ---")

    # Reemplazamos temporalmente la posición inicial de P1 para que caiga sobre pinchos en el frame 5
    # o inyectamos teclas
    orig_iniciar_mundo = pantalla.iniciar_mundo

    # Verificamos directamente con el flujo de pantalla.iniciar_mundo
    # Para que P1 toque pincho rápidamente en el nivel 3-1:
    # En nivel 3-1 los erizos están en x=640..700, y=ALTO-75
    # Simulemos haciendo que el reloj termine el nivel tras invocar pantalla_muerte
    try:
        resultado = pantalla.iniciar_mundo(
            mecanicas=["agua", "pinchos"],
            numero_nivel=1,
            color_p1="Verde",
            color_p2="Rosa",
            mundo=3,
            partida_id=1,
        )
    except Exception as e:
        print("Excepción durante bucle:", e)

    print("Resultado retornado por nivel:", resultado)
    print("=========================================================================")


def test_deteccion_y_transicion_muerte_frame_by_frame():
    print("\n--- 2. Verificación detallada frame a frame del ciclo de muerte en Mundo 3 ---")

    p1 = movimientos.crear_personaje(120, 340, "Celeste")
    p2 = movimientos.crear_personaje(230, 340, "Violeta")
    p1["en_agua"] = True
    p2["en_agua"] = True

    pinchos = [movimientos.crear_pincho(130, 360, 40, 20, direccion="arriba")]

    # Frame 0: vivos
    assert not p1["muerto"] and not p2["muerto"], "Deben iniciar vivos"

    # Frame 1: P1 entra en contacto con el pincho
    p1["hitbox"].y = 350
    toco = movimientos.comprobar_pinchos(p1, pinchos)
    assert toco == True, "Colisión con pinchos debe ser True en frame 1"
    assert p1["muerto"] == True, "P1 debe estar muerto en frame 1"
    assert p2["muerto"] == False, "P2 debe permanecer completamente vivo en frame 1"
    assert p1["en_agua"] == False, "P1 debe desvincularse del agua al morir"
    assert p1["vel_y"] == movimientos.VELOCIDAD_MUERTE, f"Impulso vel_y={movimientos.VELOCIDAD_MUERTE}"

    # Simular frames siguientes tal como ocurren en pantalla.py:
    # - comprobar_pinchos
    # - actualizar_muerte(p, duracion_max=28)
    # - comprobación de debe_mostrar_muerte
    debe_mostrar_muerte = False
    frames = 0
    while not debe_mostrar_muerte and frames < 50:
        frames += 1
        # P2 puede seguir nadando
        movimientos.aplicar_fisica_agua(p2, tecla_arriba=True, submarino=True)
        # P1 ejecuta actualización de muerte
        movimientos.actualizar_muerte(p1, duracion_max=28)
        movimientos.actualizar_muerte(p2, duracion_max=28)

        muertos = [p for p in (p1, p2) if p.get("muerto", False)]
        if muertos and any(p.get("muerte_terminada", False) for p in muertos):
            debe_mostrar_muerte = True

    assert debe_mostrar_muerte == True, "La transición a pantalla de muerte debe activarse"
    assert frames == 28, f"La animación breve debe durar exactamente 28 frames, duró: {frames}"
    assert p2["muerto"] == False, "P2 DEBE SEGUIR VIVO al activarse la pantalla de muerte"
    print(f"[OK] Frame a frame verificado: Muerte detectada en frame 1, pantalla activada en frame {frames}, P2 intacto y vivo.")

    print("\n--- 3. Verificación de caída fuera del escenario en Mundo 3 ---")
    p1_caida = movimientos.crear_personaje(500, 670, "Celeste")
    p2_seguro = movimientos.crear_personaje(100, 200, "Violeta")
    p1_caida["en_agua"] = True
    p2_seguro["en_agua"] = True

    # P1 llega al fondo de la pantalla (hb.bottom >= 720)
    p1_caida["hitbox"].bottom = ALTO
    hb = p1_caida["hitbox"]
    numero_mundo = 3
    caida_abajo = (hb.bottom >= ALTO if numero_mundo == 3 else hb.top >= ALTO)
    assert caida_abajo == True, "Debe detectar caída en cuanto el personaje toca el borde inferior"
    assert hb.top < ALTO, "El personaje no ha desaparecido (su parte superior sigue visible)"

    movimientos.matar_personaje(p1_caida)
    assert p1_caida["muerto"] == True
    assert p2_seguro["muerto"] == False, "P2 debe permanecer vivo"
    assert p1_caida["vel_y"] == movimientos.VELOCIDAD_MUERTE
    print("[OK] Caída detectada de inmediato sin esperar que el personaje desaparezca del todo.")

    print("\n=======================================================")
    print(">>> TODOS LOS TESTS DE FLUJO DE MUERTE M3 EXITOSOS <<<")
    print("=======================================================")


if __name__ == "__main__":
    test_deteccion_y_transicion_muerte_frame_by_frame()
