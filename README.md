● Nombre del juego: pico park

● integrantes: Malena Albarracin, Zoe Mennella

● Descripción y objetivo: trabajar en equipo para conseguir la llave de cada nivel y hacer que todos los jugadores crucen la puerta de salida.

● Controles: 1° jugardor WASD y 2° jugador flechitas. F11 alterna entre pantalla completa y ventana.

El juego arranca en pantalla completa y se adapta a cualquier resolución de monitor: se dibuja a 1280x720 y pygame lo escala al tamaño real de la pantalla (con bandas negras si la proporción no es 16:9).

● Reglas: El grupo debe conseguir la llave del mapa y entrar todos los jugadores por la puerta de salida. Si alguien se queda afuera, no se gana.

● Niveles: 3 mundos (nieve, ruinas y submarino) de 6 niveles cada uno. El sexto nivel de cada mundo es un jefe:

- 1-6 El Muñeco de Nieve: lanza bolas que ruedan y matan al tocarlas. Para golpearlo hay que pisar los dos
  botones de colores AL MISMO TIEMPO y mantenerlos un instante; con cada golpe los botones cambian de lugar
  y las bolas se aceleran. Al tercer golpe se derrite y aparecen la llave y la puerta.
- 2-6 El Guardián de piedra (con soga): golpea el suelo y lanza una onda expansiva que hay que saltar, más
  rocas que caen sobre cada jugador (avisadas por una sombra). Después queda aturdido unos segundos con la
  runa del pecho brillando: está demasiado alta para un salto, hay que hacer la torre humana (uno salta
  desde la cabeza del otro) y tocarla. Tres toques y se desmorona.
- 3-6 El Kraken (jefe final, nadando, con oxígeno y cámaras de aire): tentáculos que suben del lecho
  (avisados con burbujas) y tinta a partir del segundo golpe. Aparece un orbe de luz: los dos jugadores
  tienen que meterse adentro al mismo tiempo y aguantar un segundo para cargarlo; el orbe vuela al ojo
  del Kraken. Tres golpes y se hunde.

La lógica y el dibujo de cada jefe están en Pico-park-juego\jefe_nieve.py, jefe_ruinas.py y jefe_kraken.py
(todo dibujado con código, como los fondos; se puede reemplazar por sprites a mano). jefes.py es el punto
de entrada común que usa pantalla.py. Las constantes de dificultad (tiempos, velocidades, posiciones) están
al principio de cada módulo. La cantidad de niveles por mundo se define en NIVELES_POR_MUNDO
(Pico-park-juego\guardado.py).

Si un solo jugador muere (cae a los picos, toca un láser o queda atrapado en el mapa), todo el equipo pierde y el nivel se reinicia desde el principio.

● Instrucciones de instalación y ejecución:

Clonar o descargar el repositorio:
Obtén los archivos del proyecto en tu equipo y abre la terminal en la carpeta raíz.

Instalar las dependencias:
Ejecuta el siguiente comando para instalar Pygame y cualquier otra librería requerida desde el archivo requirements.txt:
pip install -r requirements.txt

Ejecutar el proyecto:
Inicia el juego ejecutando el archivo principal main.py

● Dependencias:
pygame

● Organización general del proyecto (carpeta Pico-park-juego):
main.py            menús (principal, modo de juego, partidas, personajes, opciones) y arranque
pantalla.py        iniciar_mundo: loop de juego, física por frame, dibujo de cada mundo, cámara
niveles.py         definición de los 15 niveles, una función por nivel (nivel_1_1 … nivel_3_5)
movimientos.py     física de personajes, caja, soga, llave y puerta
sprites.py         carga y caché de sprites, botones y accesorios
menu_niveles.py    menú de selección de niveles y miniaturas
guardado.py        partidas guardadas (partidas.txt) y sus diálogos
configuracion.py   idiomas, audio, volumen, configuracion.json
fuentes.py         fuentes y caché de textos
rutas.py, ventana.py, errores.py   rutas de recursos, pantalla completa, registro de errores
herramientas/      scripts de mantenimiento: jugar_nivel.py, regresion_visual.py, reducir_botones.py


● Distribución de tareas entre integrantes:
male: documentacion, textual, teorico, ideas, niveles, etc
zoe: visual, codigo, sprites


Generar el ejecutable

Crear el entorno virtual:
python -m venv .venv

Activarlo:
.\.venv\Scripts\Activate.ps1

Instalar dependencias:
python -m pip install -r requirements.txt
python -m pip install pyinstaller

Empaquetar (desde la raíz del repositorio):
python -m PyInstaller --noconfirm --clean --windowed --name PicoPark `
  --add-data "Sprites;Sprites" `
  --add-data "sonidos;sonidos" `
  --add-data "assets;assets" `
  Pico-park-juego\main.py

El ejecutable queda en dist\PicoPark\PicoPark.exe. Para compartirlo hay que
enviar la carpeta dist\PicoPark completa (comprimida en zip), no solo el .exe.

Las rutas de recursos se resuelven en Pico-park-juego\rutas.py: en desarrollo
apuntan a la raíz del repo y dentro del .exe a la carpeta _internal. Las partidas
(partidas.txt) y la configuración (configuracion.json) se guardan al lado del .exe.

Si el juego falla con un error inesperado, se cierra mostrando un aviso y deja el
detalle en errores.log al lado del .exe (Pico-park-juego\errores.py). Pedirle ese
archivo a quien reporte el problema.
