● Nombre del juego: pico park

● integrantes: Malena Albarracin, Zoe Mennella

● Descripción y objetivo: trabajar en equipo para conseguir la llave de cada nivel y hacer que todos los jugadores crucen la puerta de salida.

● Controles: 1° jugardor WASD y 2° jugador flechitas. F11 alterna entre pantalla completa y ventana.

El juego arranca en pantalla completa y se adapta a cualquier resolución de monitor: se dibuja a 1280x720 y pygame lo escala al tamaño real de la pantalla (con bandas negras si la proporción no es 16:9).

● Reglas: El grupo debe conseguir la llave del mapa y entrar todos los jugadores por la puerta de salida. Si alguien se queda afuera, no se gana.

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

● Organización general del proyecto:
main.py
niveles.py


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
