import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((800, 600))

from sprites import cargar_boton
from configuracion import (
    obtener_volumen, fijar_volumen, cambiar_volumen,
    obtener_idioma, cambiar_idioma, t
)
from fuentes import (
    obtener_fuente_titulo, obtener_fuente_texto, obtener_fuente_boton,
    obtener_fuente_subtitulo
)

print('--- TEST 1: CARGA DE SPRITES ---')
sprites_a_probar = [
    'boton-configuracion.png',
    'boton-configuracion-semiapretado.png',
    'boton-configuracion-apretado.png',
    'boton-subir-volumen.png',
    'boton-subir-volumen-semiapretado.png',
    'boton-subir-volumen-apretado.png',
    'boton-bajar-volumen.png',
    'boton-bajar-volumen-semiapretado.png',
    'boton-bajar-volumen-apretado.png',
    'boton-casa.png',
    'boton-casa-semiapretado.png',
    'boton-casa-apretado.png',
    'boton-reiniciar-icono.png',
    'boton-reiniciar-icono-semiapretado.png',
    'boton-reiniciar-icono-apretado.png',
    'boton-x.png',
    'boton-x-semiapretado.png',
    'boton-x-apretado.png',
]
for s in sprites_a_probar:
    img = cargar_boton(s)
    assert img is not None, f'Error cargando {s}'
    print(f'OK: {s} -> {img.get_size()}')

print('--- TEST 2: GESTION DE VOLUMEN (0% a 100%) ---')
fijar_volumen(50)
assert obtener_volumen() == 50, f'Esperado 50, obtenido {obtener_volumen()}'
cambiar_volumen(60)
assert obtener_volumen() == 100, f'Esperado 100, obtenido {obtener_volumen()}'
cambiar_volumen(-150)
assert obtener_volumen() == 0, f'Esperado 0, obtenido {obtener_volumen()}'
cambiar_volumen(70)
assert obtener_volumen() == 70, f'Esperado 70, obtenido {obtener_volumen()}'
print('OK: Control de volumen verificado correctamente.')

print('--- TEST 3: INTERNACIONALIZACION (ES, EN, ZH) ---')
for lang in ['es', 'en', 'zh']:
    cambiar_idioma(lang)
    assert obtener_idioma() == lang
    print(f'Idioma: {lang}')
    print('  configuracion:', t('configuracion'))
    print('  volumen:', t('volumen'))
    print('  idioma:', t('idioma'))
    print('  te_moriste:', t('te_moriste'))
    print('  nivel_completado:', t('nivel_completado'))
    print('  seleccion_nivel:', t('seleccion_nivel'))
    m_txt = t('mundo')
    n_txt = t('nivel')
    print(f'  mundo / nivel: {m_txt} 1 - {n_txt} 2')

    # Renderizado con fuentes sin excepción
    f_tit = obtener_fuente_titulo(24)
    s_tit = f_tit.render(t('configuracion'), True, (255, 255, 255))
    assert s_tit.get_width() > 0

print('OK: Internacionalizacion y fuentes verificadas correctamente.')
