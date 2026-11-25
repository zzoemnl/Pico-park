# Cómo se hizo Pico Park

Documento para entender y explicar el proyecto: qué es, cómo está construido por dentro,
qué decisiones se tomaron y cómo se verifica. Está pensado para presentarlo o defenderlo:
cada sección se puede leer sola.

---

## 1. Qué es

Pico Park es un juego de plataformas **cooperativo para dos personas en la misma
computadora**, inspirado en el Pico Park original. Los dos jugadores comparten el teclado
(WASD y flechas) y tienen que **conseguir la llave de cada nivel y entrar los dos por la
puerta**. Si uno muere, pierden los dos (salvo en el mundo submarino, donde la muerte es
individual) y el nivel se reinicia.

- 3 mundos con 5 niveles cada uno: **nieve** (mundo 1), **ruinas** (mundo 2) y **submarino**
  (mundo 3). Cada mundo introduce una mecánica: cajas y botones, soga entre los jugadores,
  natación con oxígeno.
- 13 colores de personaje y decenas de accesorios (sombreros, orejas, gorros, equipo de buceo).
- Partidas guardadas con contraseña, 3 idiomas (español, inglés, chino), música por mundo.
- Se distribuye como un ejecutable de Windows que no necesita Python instalado.

**Tecnología**: Python 3 + pygame-ce (fork mantenido de pygame). Sin motor de juego ni
librerías adicionales: la física, las animaciones, los menús y el guardado están hechos a
mano. Unas 23.900 líneas de Python en 20 archivos (12 módulos más el paquete `menus/`).

---

## 2. Arquitectura general

```
main.py ──────────► menus/ (una pantalla por módulo)            ┐
   │                                                            │ usan
   └─ jugar_niveles_desde() ──► pantalla.iniciar_mundo()        │
                                   │  loop de un nivel          │
                                   ├─ niveles.py   (qué hay en cada nivel)
                                   ├─ movimientos.py (física)   │
                                   ├─ sprites.py   (imágenes)   │
                                   └─ configuracion.py (idioma, audio)
guardado.py (partidas.txt)   menu_niveles.py (selección de nivel)   fuentes.py (textos)
rutas.py (dónde están los recursos)   ventana.py (pantalla completa)   errores.py (log)
```

| Módulo | Qué hace | Tamaño |
|---|---|---|
| `main.py` | Arranque: crea el estado de los menús (`_EstadoMenu`) y corre el loop que despacha eventos y dibujo a la pantalla activa. | 170 líneas |
| `menus/` | Un módulo por pantalla (`principal`, `modo_juego`, `partidas`, `personajes`, `opciones`, `seleccion_nivel`), cada uno con su función de eventos, su función de dibujo y su fondo dibujado con código; `estado.py` tiene `_EstadoMenu` con la inicialización, `comunes.py` las constantes e iconos compartidos y `dialogos.py` los diálogos modales de partidas (nombre, contraseña, guardar al salir, borrar, atuendos). | 6.200 en 9 archivos |
| `pantalla.py` | `EstadoNivel` (estado de un nivel y su preparación), una función por fase del cuadro (eventos, jugadores, mecánicas, interacciones, dibujo, fin de nivel), `iniciar_mundo()` que las encadena en el loop, y el dibujo de los tres mundos. | 5.600 |
| `niveles.py` | Los 15 niveles, una función por nivel (`nivel_1_1` … `nivel_3_5`) que devuelve plataformas, jugadores, llave, puerta y mecánicas. | 1.400 |
| `movimientos.py` | Física: gravedad, salto, colisiones, empujar la caja, torre humana, soga, natación, llave y puerta, pinchos. | 1.500 |
| `sprites.py` | Carga y caché de todas las imágenes (personajes, botones, objetos, accesorios), dibujo del personaje con su accesorio. | 1.600 |
| `menu_niveles.py` | Pantalla de selección de nivel y las miniaturas de cada nivel (dibujadas con código). | 1.350 |
| `guardado.py` | `partidas.txt`: leer, escribir de forma atómica, crear, borrar, contraseñas, progreso. Solo datos; sin interfaz. | 535 |
| `configuracion.py` | Traducción `t()`, música por mundo, efectos de interfaz, volumen, `configuracion.json`. | 1.260 |
| `idiomas.py` | Los 226 textos del juego en español, inglés y chino (solo datos). | 825 |
| `fuentes.py` | Fuentes pixel art, soporte de caracteres chinos, caché de textos renderizados. | 700 |
| `rutas.py`, `ventana.py`, `errores.py` | Rutas de recursos (desarrollo y `.exe`), pantalla completa adaptativa, registro de errores. | 150 |

Hay un solo **estado global de pantalla**: el juego está en el menú (`main.py`) o dentro de
un nivel (`pantalla.iniciar_mundo`). `main` llama a `iniciar_mundo` y espera que devuelva
`"siguiente"`, `"menu"` o `"salir"`.

---

## 3. Recorrido guiado: qué pasa cuando abrís el juego

Esta sección explica el código como si lo recorriéramos con el dedo, para poder contarlo.

### 3.1 Del doble clic al menú

1. **`main.py` es el punto de entrada.** Al final del archivo hay un `if __name__ == "__main__":`.
   Esa línea significa "esto se ejecuta solo si abrís este archivo directamente, no si otro
   módulo lo importa". Ahí se llama a `ejecutar_protegido(main)` (de `errores.py`), que corre
   `main()` y, si algo explota, escribe el error en `errores.log` y muestra un aviso.
2. **`main()` crea el estado de los menús**: `m = _EstadoMenu()`. Esa línea carga todos los
   sprites de botones, las fuentes y calcula dónde va cada botón en la pantalla (ver
   `menus/estado.py`). Es lo que antes se hacía con cientos de variables sueltas.
3. **Después entra al loop**: `while m.ejecutando:`. Un loop de juego es un `while` que da una
   vuelta por cada cuadro de la pantalla. `m.reloj.tick(FPS)` lo frena a 60 vueltas por segundo.
   En cada vuelta:
   - se asegura de que suene la música del menú y de que el idioma no haya cambiado;
   - carga bajo demanda los recursos de la pantalla actual (`m._cargar_recursos_partidas()`…);
   - **lee los eventos** (`for evento in pygame.event.get()`): clics, teclas, cerrar ventana.
     Según en qué pantalla estemos (`m.estado_actual`), le pasa el clic a la función de esa
     pantalla: `_eventos_menu_principal(m, evento)`, `_eventos_lista_partidas(m, evento)`, etc.
     Esas funciones cambian el estado (por ejemplo, `m.estado_actual = ESTADO_MODO_JUEGO` al
     apretar JUGAR);
   - **dibuja** la pantalla actual con `_dibujar_<pantalla>(m)` y la muestra con
     `pygame.display.flip()`.
4. **Cuando el jugador elige un nivel**, `_eventos_seleccion_nivel` llama a
   `jugar_niveles_desde(...)`, que llama a `pantalla.iniciar_mundo(...)`. Ahí el menú queda
   "congelado" esperando; el nivel tiene su propio loop (sección 4). Cuando el nivel termina,
   `iniciar_mundo` devuelve `"siguiente"`, `"menu"` o `"salir"`, y el menú sigue desde ahí.

Es decir: hay **dos loops** en el juego, el del menú (`main.py`) y el del nivel
(`pantalla.iniciar_mundo`), y nunca corren al mismo tiempo.

### 3.2 Por qué está organizado así

**Por qué hay varios archivos en vez de uno.** Cada archivo tiene una responsabilidad:
`movimientos.py` sabe de física, `sprites.py` de imágenes, `guardado.py` de partidas. Cuando
algo falla o hay que cambiarlo, se sabe adónde ir. Y dos personas pueden trabajar a la vez
sin pisarse (la que hace niveles toca `niveles.py`; la que hace arte, `sprites.py`).

**Por qué `menus/` es una carpeta (un "paquete").** Las seis pantallas del menú son parecidas
entre sí: cada una tiene una función de eventos, una de dibujo y un fondo. Agruparlas en una
carpeta con un archivo por pantalla hace que el patrón se vea de un vistazo. El archivo
`menus/__init__.py` (casi vacío) es lo que le dice a Python que esa carpeta se puede importar
como `from menus.partidas import ...`.

**Por qué funciones y no un bloque largo.** `main()` tenía 2.500 líneas con todo mezclado.
Ahora el loop se lee en 15 líneas y cada pantalla es una función con nombre. Una función es
un bloque con nombre, entradas y salida: se puede leer sola, probar sola y buscar por nombre.
Lo mismo con el nivel: `iniciar_mundo` llama a seis funciones, una por fase del cuadro.

**Por qué un objeto de estado (`_EstadoMenu`, `EstadoNivel`).** Las funciones de una pantalla
necesitan compartir datos: qué partida está cargada, qué color eligió cada jugador, dónde
están los botones. Las opciones eran variables globales (desordenado), pasar cincuenta
parámetros (imposible de leer) o un objeto que las agrupe. El objeto se crea una vez y se pasa
como `m` (menú) o `n` (nivel); cada función lee y escribe `m.lo_que_necesite`.

**Por qué `niveles.py` devuelve diccionarios.** Un nivel es "qué hay y dónde": plataformas,
jugadores, llave, puerta, mecánicas. Una función por nivel que devuelve eso en un diccionario
permite agregar un nivel sin tocar el loop, y leer un nivel de arriba a abajo como una lista.

**Por qué los recursos están fuera del código.** `Sprites/`, `sonidos/` y `assets/` son
imágenes, música y fuentes: no son Python y los edita la persona que hace arte, con otras
herramientas. `rutas.py` es el único lugar que sabe dónde están (en desarrollo, en la carpeta
del repositorio; dentro del `.exe`, en `_internal`).

**Por qué `herramientas/` está aparte.** Son scripts para quien desarrolla (probar un nivel,
correr la regresión, reducir imágenes), no parte del juego. No se empaquetan en el `.exe`.

**Convenciones que se ven en el código.**
- Nombres que empiezan con `_` (`_dibujar_frame`, `_cache_botones`): uso interno del módulo,
  no pensados para importar desde afuera.
- `MAYÚSCULAS` (`FPS`, `ANCHO`, `ESTADO_MODO_JUEGO`): constantes, valores que no cambian.
- Todo texto que ve el jugador pasa por `t("clave")`, nunca va escrito directo: así existe en
  los tres idiomas.
- `import` al principio de cada archivo: declara de qué otros módulos depende. Si `A` importa
  `B` y `B` importa `A` hay un ciclo y Python falla; por eso `pantalla.py` importa `niveles.py`
  recién cuando lo necesita.

### 3.3 "Si quiero cambiar X, ¿adónde voy?"

| Quiero… | Archivo |
|---|---|
| Cambiar o agregar un texto / traducción | `idiomas.py` |
| Que el salto sea más alto o la caída más rápida | `movimientos.py` (`GRAVEDAD`, `fuerza_salto`) |
| Agregar o modificar un nivel | `niveles.py` (y su miniatura en `menu_niveles.py`) |
| Cambiar cómo se ve o se comporta una pantalla del menú | `menus/<pantalla>.py` |
| Agregar un sombrero o accesorio | `sprites.py` (`_ACCESORIOS_REGISTRADOS`) y su PNG en `Sprites/Accesorios` |
| Cambiar la música de un mundo | poner el mp3 en `sonidos/mundoN/` |
| Cambiar qué guarda una partida | `guardado.py` |
| Tocar cómo se dibuja un mundo (fondo, nieve, agua) | `pantalla.py` (funciones `dibujar_*`) |
| Cambiar la lógica de muerte, llave o puerta | `pantalla.py` (`_resolver_interacciones`) |

---

## 4. El loop de juego

Todo corre a **60 cuadros por segundo** en una ventana lógica de **1280×720** (pygame la
escala a la pantalla real). `iniciar_mundo` crea un `EstadoNivel` (carga el nivel, los sprites y
el HUD) y después, en cada cuadro, llama a seis funciones en este orden:

1. **Eventos**: teclado (mover, saltar, nadar, linterna, reiniciar con R), botones del HUD
   (configuración, menú, reiniciar, salir) y cierre de ventana.
2. **Física de cada jugador** (`movimientos.py`): aplicar velocidad y gravedad, resolver
   colisiones con suelo y plataformas, empujar la caja, torre humana, soga.
3. **Mecánicas del nivel**: botones que suben paredes, láser bloqueado por la caja, plataformas
   móviles o que se derrumban, corrientes, oxígeno, linternas.
4. **Llave y puerta**: el que toca la llave la lleva; al tocar la puerta con la llave, se abre;
   cada jugador que entra queda "completado".
5. **Muerte**: pinchos, láser, caer fuera del mundo, quedarse sin oxígeno. En los mundos 1 y 2
   la muerte es compartida; en el 3, individual.
6. **Dibujo**: fondo del mundo, escenario, objetos, jugadores, oscuridad (3-4 y 3-5), HUD.
7. **Cámara**: el nivel es más ancho que la pantalla (hasta 2.600 px). La cámara sigue el
   punto medio entre los dos jugadores; si se separan más de 850 px, la pantalla **se divide
   en dos** y cada mitad sigue a un jugador.
8. **Victoria**: con los dos adentro de la puerta, animación de nivel completado y pantalla con
   "Siguiente" / "Menú".

---

## 5. Física (movimientos.py)

Los personajes son diccionarios con posición (`hitbox`, un `Rect` de 50×85), velocidades,
estado (`en_suelo`, `en_agua`, `muerto`) y animación. Constantes principales:

| Constante | Valor | Efecto |
|---|---|---|
| `GRAVEDAD` | 0,85 px/frame² | Caída |
| `fuerza_salto` | −15,5 px/frame | Salto de ~125 px de alto |
| `velocidad_mov` | 6 px/frame | Caminar |
| `TAMANO_CAJA` | 60 px | La caja se empuja, no se levanta |
| `DISTANCIA_SOGA_REPOSO / MAXIMA` | 140 / 160 px | La soga tira del compañero si se aleja |
| Oxígeno | baja ~0,08 % por frame (~20 s) | Se recarga en cámaras de aire |

Mecánicas cooperativas construidas sobre eso:

- **Torre humana**: un jugador puede pararse sobre la cabeza del otro y saltar desde ahí con
  impulso extra. Es la forma de llegar a lugares a los que un salto solo no llega (nivel 1-2).
- **Caja**: se empuja con el cuerpo; sirve para pisar botones y bloquear el láser (1-3, 1-4).
- **Botones y paredes de colores** (1-5): los botones rojos abren las paredes rojas mientras
  alguien los pisa; uno pisa y el otro pasa.
- **Soga** (mundo 2): los dos jugadores están unidos; la soga limita la distancia y permite
  colgarse y balancearse como péndulo (2-3) o cruzar plataformas que se derrumban (2-4).
- **Natación** (mundo 3): sin gravedad, se nada en 4 direcciones; oxígeno limitado (3-5),
  corrientes que empujan, laberintos generados al azar (3-2, 3-4) y oscuridad con linternas (3-4).

---

## 6. Los niveles (niveles.py)

Cada nivel es una función que devuelve un diccionario con todo lo que existe en ese nivel:
ancho del mundo, suelo, plataformas, posición inicial de los jugadores, caja, pinchos, llave,
puerta y qué mecánicas usa. Agregar un nivel es escribir una función más y registrarla.

| Nivel | Nombre | Enseña |
|---|---|---|
| 1-1 | Tutorial | Moverse, saltar, llave y puerta |
| 1-2 | La torre humana | Subirse al compañero |
| 1-3 | La caja y el botón | Empujar la caja hasta el botón que levanta la pared |
| 1-4 | El láser y la caja | Bloquear el láser con la caja |
| 1-5 | Las cuatro paredes de colores | Uno pisa botones, el otro avanza |
| 2-1 | El arrastre básico | Moverse unidos por la soga |
| 2-2 | La plataforma móvil | Coordinar el salto sobre el abismo |
| 2-3 | El péndulo | Balancearse colgado de la soga |
| 2-4 | Las plataformas que se derrumban | Caen 1 s después de pisarlas |
| 2-5 | Las plataformas alternadas | Zigzag ascendente |
| 3-1 | El jardín de algas | Nadar |
| 3-2 | El laberinto de coral | Laberinto aleatorio |
| 3-3 | Las rocas peligrosas | Pasillos con erizos |
| 3-4 | El laberinto oscuro | Linternas: solo se ve alrededor de cada jugador |
| 3-5 | El abismo submarino | Oxígeno, cámaras de aire y corrientes |

---

## 7. Gráficos

- **Personajes**: PNG dibujados a mano, 13 colores, con 20 estados de animación (quieto,
  8 cuadros de caminar, saltar, 8 de empujar, muerto…). Se cargan a 440×527 y se reducen a
  70×85. Los accesorios se "anclan" a la cabeza y a los ojos del sprite: el juego escanea
  los píxeles del sprite una vez para encontrar dónde está la cabeza, así cualquier sombrero
  queda bien puesto en cualquier cuadro de animación.
- **Botones del menú**: PNG en tres estados (normal, semi-apretado, apretado) más una versión
  "iluminada" para el hover que se genera por código.
- **Fondos, escenarios, miniaturas de los niveles y efectos** (nieve, polvo, burbujas, rayos de
  sol, oscuridad): dibujados con primitivas de pygame, no con imágenes. Esto hace el paquete
  chico y permite animarlos.
- **Oscuridad** (3-4, 3-5): una capa negra casi opaca sobre el nivel a la que se le "restan"
  círculos de luz alrededor de cada jugador con la linterna encendida.

---

## 8. Menús y partidas

`main.py` y el paquete `menus/` forman una máquina de estados: menú principal → modo de juego → lista de partidas o
nueva partida → selección de mundo y nivel → jugar. Cada pantalla tiene su función de eventos
(`_eventos_<pantalla>`) y de dibujo (`_dibujar_<pantalla>`); el estado compartido (partida
actual, colores elegidos, página de la lista, rectángulos de los botones…) vive en un objeto
`_EstadoMenu`.

**Partidas** (`guardado.py`): `partidas.txt` es un archivo de texto con una línea por partida:

```
ID|Nombre|MundoMax|NivelMax|Fecha|NivelesDesbloqueados|PasswordHash|PasswordSalt|Personalización
```

- Los niveles desbloqueados se guardan como bits (`1:11100,2:00000,3:00000`).
- La contraseña no se guarda: se guarda un hash **PBKDF2-SHA256 con 100.000 iteraciones y
  salt**, como en una aplicación real.
- La escritura es **atómica**: se escribe a un archivo temporal y se reemplaza, así un corte
  de luz no deja la partida corrupta.

**Idiomas** (`configuracion.py`): todos los textos pasan por `t("clave")`, con 226 claves en
español, inglés y chino. Para el chino se usa una fuente del sistema con caracteres CJK.

**Audio**: una pista de música por mundo y para el menú (mp3 en `sonidos/`); los sonidos de
interfaz se sintetizan por código.

---

## 9. Del código al ejecutable

- `rutas.py` resuelve dónde están los recursos: en desarrollo, en la raíz del repositorio;
  dentro del `.exe`, en la carpeta `_internal` que crea PyInstaller. Las partidas y la
  configuración se guardan **al lado del `.exe`**, para que no se pierdan.
- `ventana.py`: el juego dibuja siempre a 1280×720 y `pygame.SCALED` lo escala a pantalla
  completa en cualquier monitor; F11 alterna con ventana.
- `errores.py`: el `.exe` no tiene consola, así que si algo falla se escribe el error en
  `errores.log` y se muestra un aviso. Sin esto, un fallo se vería como "el juego se cerró
  solo".
- Empaquetado con PyInstaller en una línea (ver README); el resultado es una carpeta de
  59 MB que se comprime a 37 MB.

---

## 10. Rendimiento: problemas encontrados y cómo se resolvieron

Medido con un arnés que corre el juego sin ventana y sin límite de 60 fps (menos milisegundos
por cuadro = más margen en máquinas lentas). Los números se pueden reproducir con
`herramientas/regresion_visual.py capturar <carpeta>`, que imprime los ms por cuadro de cada escena.

| Problema | Causa | Solución | Resultado |
|---|---|---|---|
| 2,1 GB de RAM y 11 s de arranque | Los PNG de los botones estaban a 6800×1600 px para dibujarse a 272×80, y se retenían en caché | Reducirlos a 1088 px y limitar el tamaño al cargar | 200 MB, 0,5 s |
| Menú a 14,6 ms/cuadro | El caché de anclajes de accesorios recibía una superficie nueva por cuadro (`flip`) y re-escaneaba el sprite píxel a píxel | Memorizar reflejos y tintados por sprite base | 2,9 ms |
| Mundo 3 a 14,6 ms/cuadro | Se dibujaban los 2.600 px del mundo aunque se ven 1.280; capas estáticas redibujadas cada cuadro | Dibujar solo los tramos visibles; lecho, rocas y erizos pre-renderizados | 9,6 ms |
| Lectura de disco 60 veces por segundo | `reproducir_musica("menu")` resolvía la ruta del mp3 en cada cuadro | Re-chequear el disco cada 2 s | — |

Una lección concreta: la primera versión de las capas pre-renderizadas usó superficies con
canal alfa y resultó **más lenta** que lo que reemplazaba (un blit alfa de 1280×720 cuesta
más que 700 líneas dibujadas). Con color llave fue 8 veces más rápida. Siempre medir.

---

## 11. Cómo se verifica que nada se rompe

`herramientas/regresion_visual.py` corre el juego sin ventana, de forma **determinista**
(reloj, tiempo y azar fijados), y captura la pantalla en cuadros concretos de 35 escenas:
los 15 niveles, pantalla dividida, victoria, reinicio, muerte y las 8 pantallas del menú
(navegando con clics sintéticos). Comparando las capturas de antes y después de un cambio
se demuestra que **no cambió ni un píxel**. Así se hicieron todas las optimizaciones y los
dos refactors grandes (niveles a `niveles.py`, menús a una función por pantalla), sin que el
juego cambiara en nada visible.

También mide los milisegundos por cuadro de cada escena, así que sirve para detectar si un
cambio hizo más lento algo.

---

## 12. Decisiones que vale la pena explicar

- **Sin motor, sin librerías**: pygame solo da ventana, imágenes y eventos; todo lo demás es
  propio. Más trabajo, pero se entiende cada línea.
- **Diccionarios en vez de clases para los personajes y objetos**: simple y rápido de iterar
  para un proyecto de este tamaño; el costo es que la estructura no está declarada en un solo
  lugar.
- **Fondos y miniaturas dibujados con código**: evita decenas de imágenes grandes y permite
  animar (nieve, burbujas). Los personajes y botones sí son arte a mano, porque ahí importa.
- **Resolución lógica fija (1280×720) + escalado**: el código nunca tiene que pensar en el
  tamaño real del monitor.
- **Refactors mecánicos con verificación**: los cambios estructurales grandes (niveles a
  `niveles.py`, menús a un objeto de estado y después al paquete `menus/`) se hicieron con
  scripts que analizan el código (AST) y lo mueven tal cual, comentarios incluidos, y se
  validaron con las capturas. Reescribir a mano 4.000 líneas habría metido errores seguro.

---

## 13. Qué se podría mejorar

- `EstadoNivel.__init__` tiene ~960 líneas de preparación (HUD, sprites, primer cuadro,
  animación de apertura); se puede repartir en métodos (`_cargar_hud`, `_dibujar_primer_cuadro`…).
- Las fases del nivel (`_actualizar_mecanicas`, `_dibujar_frame`) todavía tienen un `if` por
  mecánica y por mundo; el paso siguiente sería que cada mecánica sea un objeto con `actualizar()`
  y `dibujar()`.
- Los personajes y objetos podrían ser clases con sus métodos (`mover`, `dibujar`).
- Un editor de niveles o un formato de datos (JSON) para que diseñar niveles no requiera
  programar.
- Pruebas automáticas de la física (saltos, colisiones) además de las visuales.
- Que el juego solo genere las miniaturas que faltan en vez de regenerar y sobrescribir las 15
  cuando una no carga.

---

## 14. Historial de lo que se hizo sobre la versión original

Para que quede claro qué era "el juego" y qué se agregó después, en orden:

1. **Ejecutable**: `rutas.py` para que los recursos se encuentren dentro del `.exe`, partidas y
   configuración al lado del ejecutable, `errores.log` para fallos sin consola.
2. **Memoria y arranque**: botones de 6800 px reducidos; de 2,1 GB a 200 MB de RAM y de 11 s a
   0,5 s de arranque.
3. **Pantalla completa adaptativa** con `pygame.SCALED` y F11.
4. **Limpieza del repositorio**: scripts de prueba viejos y datos de usuario fuera del control de
   versiones.
5. **Suite de regresión visual** (`herramientas/regresion_visual.py`): 35 escenas deterministas.
6. **Rendimiento por cuadro**: menú de 14,6 a 2,9 ms; mundo 3 de 14,6 a 9,6 ms; sin cambios de
   imagen.
7. **Estructura**: los 15 niveles a `niveles.py`; los menús a `_EstadoMenu` y al paquete
   `menus/` (`main.py` pasó de 4.585 a 174 líneas); los textos a `idiomas.py` y los diálogos de
   partidas a `menus/dialogos.py`; `iniciar_mundo` (1.992 líneas) a `EstadoNivel` más seis
   funciones, una por fase del cuadro. Todo verificado con la suite.
