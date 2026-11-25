# Pico Park

Juego de plataformas **cooperativo para dos jugadores** en la misma computadora, inspirado en
Pico Park. Hecho en Python con pygame-ce.

- **Integrantes:** Malena Albarracin (documentación, diseño de niveles, ideas) y Zoe Mennella
(código, arte, sprites).
- **Objetivo:** trabajar en equipo para conseguir la llave de cada nivel y hacer que los dos
jugadores crucen la puerta de salida. Si uno se queda afuera, no se gana.
- Para entender cómo está construido el juego por dentro, qué se optimizó y cómo se verifica:
[`COMO_SE_HIZO.md`](COMO_SE_HIZO.md).


## Controles


|                             | Jugador 1      | Jugador 2                        |
| --------------------------- | -------------- | -------------------------------- |
| Moverse / saltar / nadar    | W A S D        | Flechas                          |
| Linterna (mundo 3)          | E, F o Espacio | L, Enter, Shift der. o Ctrl der. |
| Reiniciar el nivel          | R              |                                  |
| Pantalla completa / ventana | F11            |                                  |


El juego arranca en pantalla completa y se adapta a cualquier monitor: se dibuja a 1280×720 y
se escala al tamaño real (con bandas negras si la proporción no es 16:9).

## Reglas y niveles

Hay que conseguir la llave y entrar **los dos** por la puerta. Si un jugador muere (pinchos,
láser, caer fuera del mapa o quedarse sin oxígeno), pierde el equipo y el nivel se reinicia;
en el mundo submarino la muerte es individual.

3 mundos de 5 niveles, cada uno con su mecánica cooperativa:


| Mundo         | Mecánica                                                                   | Niveles                                                                                                               |
| ------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 1 — Nieve     | Torre humana, caja que empuja botones, láser, paredes y botones de colores | Tutorial · La torre humana · La caja y el botón · El láser y la caja · Las cuatro paredes de colores                  |
| 2 — Ruinas    | Los dos jugadores unidos por una soga                                      | El arrastre básico · La plataforma móvil · El péndulo · Las plataformas que se derrumban · Las plataformas alternadas |
| 3 — Submarino | Natación, oxígeno, oscuridad con linternas, corrientes                     | El jardín de algas · El laberinto de coral · Las rocas peligrosas · El laberinto oscuro · El abismo submarino         |


Los niveles se van desbloqueando al completar el anterior y el progreso se guarda en
partidas con nombre (y contraseña opcional). Se puede elegir el color de cada personaje y un
accesorio. Idiomas: español, inglés y chino.

## Cómo ejecutarlo desde el código

Requiere Python 3.12 o superior.

```powershell
git clone https://github.com/zzoemnl/Pico-park.git
cd Pico-park
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python Pico-park-juego\main.py
```

Dependencia: `pygame-ce` (fork mantenido de pygame; se importa como `pygame` y tiene versiones
compiladas para Python 3.12+, el `pygame` original no).

Para abrir un nivel directo, sin pasar por el menú ni desbloquearlo:

```powershell
python herramientas\jugar_nivel.py 2 3        # mundo 2, nivel 3
```

## Cómo generar el ejecutable

Desde la raíz del repositorio, con el entorno virtual activado:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name PicoPark --add-data "Sprites;Sprites" --add-data "sonidos;sonidos" --add-data "assets;assets" Pico-park-juego\main.py
```

El ejecutable queda en `dist\PicoPark\PicoPark.exe`. Para compartirlo hay que enviar la carpeta
`dist\PicoPark` completa (comprimida en zip), no solo el `.exe`. Windows SmartScreen puede
mostrar un aviso porque no está firmado: "Más información" → "Ejecutar de todas formas".

- Las partidas (`partidas.txt`) y la configuración (`configuracion.json`) se guardan al lado del
`.exe`, así que sobreviven a regenerarlo.
- Si el juego falla con un error inesperado, muestra un aviso y deja el detalle en
`errores.log` al lado del `.exe`. Pedirle ese archivo a quien reporte el problema.

## Organización del código (carpeta `Pico-park-juego`)


| Archivo                                  | Qué hace                                                                                                                                             |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`                                | Arranque: crea el estado de los menús y corre el loop que despacha a la pantalla activa.                                                            |
| `menus/`                                 | Un módulo por pantalla: `principal`, `modo_juego`, `partidas`, `personajes`, `opciones`, `seleccion_nivel`; `estado.py` (estado compartido e inicialización), `comunes.py` (constantes, iconos) y `dialogos.py` (diálogos de partidas: nombre, contraseña, guardar al salir, borrar). |
| `pantalla.py`                            | `EstadoNivel` (estado y preparación de un nivel), las seis fases del cuadro (`_procesar_eventos`, `_actualizar_jugadores`, `_actualizar_mecanicas`, `_resolver_interacciones`, `_dibujar_frame`, `_comprobar_fin_de_nivel`), `iniciar_mundo` (el loop) y el dibujo de los tres mundos. |
| `niveles.py`                             | Definición de los 15 niveles, una función por nivel (`nivel_1_1` … `nivel_3_5`).                                                                     |
| `movimientos.py`                         | Física de personajes, caja, soga, natación, llave y puerta.                                                                                          |
| `sprites.py`                             | Carga y caché de sprites, botones y accesorios.                                                                                                      |
| `menu_niveles.py`                        | Menú de selección de nivel y miniaturas.                                                                                                             |
| `guardado.py`                            | Partidas guardadas (`partidas.txt`): lectura, escritura atómica, contraseñas, progreso.                                                              |
| `configuracion.py` · `idiomas.py`        | Traducción `t()`, música, efectos, volumen, `configuracion.json`; `idiomas.py` tiene los 226 textos en es/en/zh.                                      |
| `fuentes.py`                             | Fuentes pixel art, caracteres chinos y caché de textos.                                                                                              |
| `rutas.py` · `ventana.py` · `errores.py` | Rutas de recursos (código y `.exe`), pantalla completa, registro de errores.                                                                         |


Recursos: `Sprites/` (personajes, botones, objetos, accesorios, miniaturas), `sonidos/` (música),
`assets/fuentes/`.

Tamaño del código: unas 23.900 líneas de Python. El archivo más grande es `pantalla.py` (5.600); los
módulos de `menus/` tienen entre 100 y 1.600 líneas; `main.py` tiene 174.

## Herramientas (carpeta `herramientas`)


| Script                                                        | Para qué                                                                                                                                                                                      |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `jugar_nivel.py <mundo> <nivel>`                              | Abre un nivel directo, para probarlo.                                                                                                                                                         |
| `regresion_visual.py capturar <carpeta>` / `comparar <a> <b>` | Corre 35 escenas sin ventana, de forma determinista, captura la pantalla y mide ms por cuadro. Comparando las capturas de antes y después de un cambio se verifica que no cambió ni un píxel. |
| `reducir_botones.py [--dry-run]`                              | Reduce los PNG de botones que estén a más de 1088 px de ancho.                                                                                                                                |


Antes de cambiar algo en el código, conviene correr `regresion_visual.py capturar antes`, hacer el
cambio, `capturar despues` y `comparar antes despues`.