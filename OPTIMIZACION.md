# Optimización de Pico Park — noviembre 2026

Registro de las mejoras de rendimiento aplicadas al juego y de la preparación
del ejecutable, con las mediciones antes y después.

## 1. Resumen

| Métrica | Antes | Después | Mejora |
|---|---|---|---|
| RAM del `PicoPark.exe` en el menú principal | 2.093 MB | 284 MB | **−86 %** |
| Tiempo de `precargar_botones_comunes()` (arranque) | 10,75 s | 0,62 s | **17× más rápido** |
| RAM del proceso tras la precarga (modo desarrollo) | 1.718 MB | 234 MB | −86 % |
| RAM con los 72 botones cargados | 2.171 MB | 273 MB | −87 % |
| Tiempo de cargar los 72 botones | 5,31 s | 0,13 s | 40× más rápido |
| `Sprites/Botones` en disco | 32,3 MB | 4,2 MB | −87 % |
| Carpeta `dist/PicoPark` | 87 MB | 59 MB | −32 % |
| `dist/PicoPark-windows.zip` | 54 MB | 37 MB | −31 % |

Sin cambios visibles en pantalla: los botones se siguen dibujando a 272×80 px
(o menos) con `smoothscale`, y la fuente ahora es 4× ese tamaño, suficiente
para que el reescalado no pierda calidad.

## 2. Diagnóstico

### 2.1 Causa raíz: los PNG de los botones

Los botones del menú se dibujan como máximo a 272×80 px, pero los archivos de
`Sprites/Botones` estaban guardados a **5440×1600** y **6800×1600** píxeles.
Un PNG pesa poco en disco porque está comprimido, pero en memoria pygame lo
guarda descomprimido en RGBA (4 bytes por píxel):

| Imagen | Píxeles | RAM por imagen |
|---|---|---|
| `boton-nueva-partida-reiniciar....png` | 6800×1600 | 43,5 MB |
| `boton-volver.png`, `boton-nueva-partida.png`, etc. | 5440×1600 | 34,8 MB |
| Las 72 imágenes de `Sprites/Botones` juntas | | **1.721 MB** |

### 2.2 Agravante: el caché retenía los originales

`cargar_boton()` guardaba la imagen a tamaño completo en `_CACHE_BOTONES`
(`sprites.py`), y `cargar_boton_escalado()` generaba la versión de 272×80 pero
nunca liberaba la grande. `precargar_botones_comunes()` carga decenas de botones
al arrancar, así que el menú principal ya partía con ~1,7 GB retenidos que no se
volvían a usar.

Además, `smoothscale` de 6800×1600 a 272×80 es una operación costosa: era la
causa de los 10 s de arranque y del "tirón" al abrir cada pantalla nueva.

### 2.3 Lo que no era problema

- `Sprites/Personajes` (272 archivos de 440×527): `cargar_sprites()` los reduce
  a 70×85 en el momento y no retiene el original. Solo cuestan tiempo de carga
  (0,7 s por 4 colores), no RAM. No se tocaron.
- `sonidos/` (17 MB de mp3): se reproducen en streaming, no se cargan enteros.
- Objetos, miniaturas y accesorios: menos de 20 MB en total.

## 3. Cambios aplicados

### 3.1 Reducción de los PNG en disco

Script nuevo `herramientas/reducir_botones.py`: recorre `Sprites/Botones` y
reescala con `smoothscale` todo PNG con ancho mayor a 1088 px (4× los 272 px de
dibujo), manteniendo la proporción. Se aplicó a 45 de los 72 archivos
(5440×1600 → 1088×320 y 6800×1600 → 1088×256). Los 27 restantes ya eran chicos.

```powershell
python herramientas/reducir_botones.py --dry-run   # muestra qué haría
python herramientas/reducir_botones.py             # aplica
```

Los originales en alta resolución quedan en el historial de git (commit
`2bb272f` y anteriores) por si alguna vez hacen falta.

### 3.2 Límite de tamaño al cargar (`Pico-park-juego/sprites.py`)

Nueva constante `ANCHO_MAX_BOTON = 1088`. En `cargar_boton()`, si el PNG
cargado es más ancho que eso, se reduce antes de guardarlo en caché. Así, si en
el futuro alguien agrega un botón en alta resolución, el juego no vuelve a
consumir gigabytes: el costo queda acotado a ~1,4 MB por botón.

### 3.3 Rutas de recursos para el ejecutable (`Pico-park-juego/rutas.py`)

No es una optimización, pero fue necesario para que el `.exe` funcione: todo el
código buscaba los recursos con `os.path.join(DIRECTORIO_ACTUAL, "..", ...)`,
que dentro de PyInstaller apunta fuera de la carpeta de recursos. `rutas.py`
centraliza la resolución:

- `ruta_recurso(...)`: raíz del repo en desarrollo; `sys._MEIPASS` (carpeta
  `_internal`) dentro del `.exe`.
- `ruta_datos(...)`: para `partidas.txt` y `configuracion.json`. En el `.exe`
  se guardan al lado de `PicoPark.exe`, para que las partidas persistan.

## 4. Cómo se midió

- **Modo desarrollo**: script de benchmark con `SDL_VIDEODRIVER=dummy` que
  importa `sprites`, ejecuta `precargar_botones_comunes()`, carga 4 colores de
  personajes y luego los 72 botones a 272×80, midiendo tiempo con
  `time.perf_counter()` y RAM con `GetProcessMemoryInfo` (Working Set).
- **Ejecutable**: se lanzó `dist\PicoPark\PicoPark.exe`, se esperó 12 s en el
  menú principal y se leyó el uso de memoria con `tasklist`.
- Entorno: Windows 11, Python 3.14.7, pygame-ce 2.5.8, PyInstaller 6.22.3.

## 5. Segunda ronda (24/11/2026): costo por frame

Medido en headless con el límite de 60 fps desactivado (menos ms por frame = más
margen en máquinas lentas). Sin cambios de gameplay ni de imagen: las capturas del
frame 100 de las 15 escenas y del menú, más pantalla dividida y transición de
victoria, son píxel a píxel idénticas antes y después (`herramientas/regresion_visual.py`).

| Escena | Antes | Después |
|---|---|---|
| Menú principal | 14,6 ms (68 fps máx) | 2,9 ms (344 fps máx) |
| Nivel 3-5 (oscuridad + oxígeno) | 14,6 ms (69 fps máx) | 9,6 ms (104 fps máx) |
| Nivel 3-4 | ~12 ms | ~8 ms |
| Nivel 3-1 | ~9 ms | 7,3 ms |
| Niveles 1-x / 2-x | 2–3 ms | 2–3 ms |

(En el arnés determinista, sin ruido del sistema: 3-5 de 9,2 a 6,2 ms; 3-4 de 8,3 a 5,0 ms;
menú de 4,4 a 1,8 ms.)

Qué se cambió:

1. **Menú: el caché de anclajes de accesorios nunca acertaba.** `dibujar_personaje`
   creaba con `transform.flip` una superficie nueva por frame, y `calcular_anclaje_sprite`
   cachea por superficie, así que escaneaba los 5950 píxeles del sprite con `get_at` 60
   veces por segundo. Ahora el reflejo, el tintado, el recorte de piernas del equipo de
   buceo y el tinte de agua se memorizan por sprite base (`sprites.py`), y el anclaje
   se calcula una sola vez.
2. **Mundo 3: se dibuja solo lo que la cámara muestra.** La cámara se calcula una vez por
   frame en `calcular_vistas_camara()` (una vista, o dos en pantalla dividida) y la usan
   tanto el dibujo como el blit final. El fondo, los rayos de sol, las ondas, la capa de
   agua y la oscuridad se pintan solo en esos tramos en vez de en los 2600 px del mundo.
3. **Menú: `reproducir_musica("menu")` iba al disco en cada frame.** Si la pista pedida es
   la que ya suena, solo se vuelve a mirar el disco cada 2 s (`configuracion.py`).
4. **Textos y miniaturas.** Las fuentes del caché quedan envueltas en `_FuenteConCache`
   (`fuentes.py`), que memoriza `render()` por (texto, color); el menú rasterizaba unos
   38 textos estáticos por frame. Las miniaturas de personajes del menú se escalan una
   vez (`escalar_cacheado`) y el HUD del nivel copia el fondo de sus botones solo cuando
   el mouse está cerca (antes 4 copias por frame).
5. **Mundo 3: capas estáticas.** Lecho, rocas y erizos (~700 llamadas a `pygame.draw` por
   frame que nunca cambian) se dibujan una vez por nivel en una superficie con color llave
   (`obtener_capa_estatica_m3`) y después solo se copia el tramo visible. Nota: la primera
   versión usó superficies con canal alfa y el blit resultó más caro que los dibujos que
   reemplazaba; con color llave + RLE el blit es varias veces más rápido.
6. **Robustez (sin efecto visible):** `configuracion.json` se escribe en un archivo temporal
   y se reemplaza con `os.replace` (antes un corte a mitad lo dejaba corrupto), y los errores
   de lectura/escritura de `partidas.txt` van a `errores.log` con `errores.registrar_error`
   (antes un `print` que el `.exe` sin consola perdía).

Para repetir la verificación después de cualquier cambio:

```powershell
python herramientas\regresion_visual.py capturar capturas_antes      # con el código viejo
python herramientas\regresion_visual.py capturar capturas_despues    # con el código nuevo
python herramientas\regresion_visual.py comparar capturas_antes capturas_despues
```

## 6. Pendientes sugeridos (no aplicados)

Por orden de valor. Ninguno es urgente para la entrega.

1. **Cargar botones por pantalla en lugar de precargar todo.** Con los PNG
   reducidos la precarga tarda 0,6 s, así que ya no molesta; se puede eliminar
   para simplificar código.
2. **Reducir `Sprites/Personajes` a 2× el tamaño de dibujo** (140×170). Ahorra
   ~0,5 s de carga al cambiar de color. Requiere verificar que los accesorios
   (sombreros, buceo) sigan anclados bien: `calcular_anclaje_sprite()` escanea
   píxeles del sprite ya reducido, así que debería ser transparente.
3. **Refactor estructural** (no es rendimiento): `iniciar_mundo()` en
   `pantalla.py` tiene ~3.200 líneas y los 15 niveles están escritos a mano en
   una cadena de `if numero_mundo == X and numero_nivel == Y`. Pasar los niveles
   a datos (JSON o listas) facilitaría agregar niveles sin tocar el loop.
4. **Firmar el `.exe`** o documentar el aviso de SmartScreen para quien lo
   reciba ("Más información" → "Ejecutar de todas formas").
