# Reloj con Python

Reloj analógico y digital hecho **solo con Python y sin ningún import** de la librería estándar ni de librerías externas. Los únicos imports son entre los módulos del propio proyecto. No usa HTML, CSS, XML ni SVG.

La estructura de datos central es la **lista circular enlazada**: cada manecilla es un anillo de marcas (`Mark`) que vuelve al inicio al terminar la vuelta, y los tres anillos están encadenados como los engranajes de un reloj.

> **Otra versión del reloj:** [Clock-using-custom-library](https://github.com/Juanescuaran2041/Clock-using-custom-library.git) es otro reloj, hecho con una librería propia construida en C.

- [Ejecución](#ejecución)
- [Limitaciones y decisiones de diseño](#limitaciones-y-decisiones-de-diseño)
- [La estructura de datos: lista circular enlazada](#la-estructura-de-datos-lista-circular-enlazada)
- [Funcionalidad añadida](#funcionalidad-añadida)
- [Estructura del proyecto](#estructura-del-proyecto)

## Ejecución

```text
python main.py
```

Requiere Python 3.10 o superior. Al iniciar se elige el modo:

1. **Reloj en vivo en la terminal.** Se escribe la hora de Bogotá una sola vez (`HH:MM:SS`) y el reloj corre solo. Dibuja la esfera analógica con la zona y la hora a su lado, y el estado de la alarma debajo. Necesita una terminal de al menos **104 columnas por 24 filas**; si es más pequeña, la imagen se desordena.
2. **Paso a paso con archivo de imagen.** Se avanza con comandos y se guarda `output/clock.bmp`.

### Menú del reloj en vivo

`Ctrl+C` pausa el reloj y abre el menú. `Enter` vuelve al reloj.

| Comando | Qué hace |
|---|---|
| `time HH:MM[:SS]` | Cambia la hora (en hora de Bogotá) |
| `zone NOMBRE` | `BOGOTA`, `NUEVA YORK`, `LONDRES`, `MADRID`, `TOKIO` |
| `alarm HH:MM` | Programa la alarma en la zona que se está mostrando |
| `clear` | Cancela la alarma |
| `calibrate` | Ajusta la velocidad con un cronómetro |
| `gif [N]` | Guarda N segundos (60 por defecto) como GIF animado en `output/clock.gif` |
| `quit` | Sale |

### Modo paso a paso

Comandos: `Enter` (avanza 1 segundo), `+ N` (avanza N segundos), `time`, `zone`, `alarm`, `clear`, `gif [N]` y `quit`. Se abre `output/clock.bmp` en un visor de imágenes y se mantiene abierto. El GIF se ve arrastrándolo a un navegador.

## Limitaciones y decisiones de diseño

La regla del proyecto es **Python puro: ningún import**. Esa sola regla elimina casi todas las herramientas con las que normalmente se hace un reloj, y cada decisión de abajo es la consecuencia de una limitación.

### 1. Interfaz gráfica

Una ventana necesita una librería: `tkinter`, `pygame`, etc. Sin imports, Python no puede abrir ni dibujar una ventana. Las únicas formas de mostrar algo son escribir texto en la terminal o escribir un archivo.

**Decisión:** el frontend es la propia terminal. Se dibuja el reloj con caracteres `▀` (medio bloque) y secuencias de color ANSI de 24 bits. Cada carácter muestra dos píxeles apilados, así que una esfera de 100×44 píxeles ocupa 22 filas. El modo 2 es la alternativa en archivos: un BMP escrito byte a byte y un GIF animado con compresión LZW propia.


### 2. Leer la hora del sistema

`time` y `datetime` son imports. Sin ellos Python no tiene forma portable de saber qué hora es. En Linux se podría leer `/proc/uptime`, pero no existe en Windows ni en Mac.

**Decisión:** el usuario escribe la hora inicial, y a partir de ahí el reloj la lleva por su cuenta con la lista circular. Esto es una limitación real: el reloj es tan exacto como la hora que se le escribe.

### 3. No se puede esperar un segundo con `time.sleep`

**Decisión:** `Pacer` espera con un bucle vacío que se repite un número fijo de veces. Ese número depende de la velocidad de cada computador, así que el reloj puede ir más rápido o más lento hasta que se calibre.

Para calibrar: `Ctrl+C`, `calibrate`, se cronometran los 10 cuadros que se ejecutan, se escriben los segundos medidos, y se repite hasta que marque unos 10 segundos. Cada vez la velocidad se escala con `vueltas × cuadros / segundos medidos`.

### 4. Sonido para la alarma

Sin librerías no se puede reproducir audio. **Decisión:** la alarma usa el carácter de campana de la terminal (`BEL`, código 7). Python solo escribe ese byte; la terminal decide si suena el pitido del sistema, hace un destello o no hace nada, según su configuración. Por eso el aviso visual siempre está: el borde pasa a rojo y aparece `*** ALARMA SONANDO ***`.

### 5. Zonas horarias fijas

Sin `datetime` tampoco hay base de datos de zonas ni horario de verano automático. **Decisión:** las zonas son desplazamientos fijos respecto a Bogotá, correspondientes a octubre de 2026 (Nueva York −4, Londres +1, Madrid +2, Tokio +9). No cambian solas si cambia la fecha.

### Resumen

| Limitación (por no tener imports) | Lo que se haría normalmente | Lo que se hace aquí |
|---|---|---|
| Sin ventana | `tkinter` | Terminal con color ANSI, o BMP y GIF |
| Sin marcado (SVG, HTML) | Un archivo SVG o una página web | Dibujo píxel a píxel en Python |
| Sin `math` | `math.sin`, `math.cos` | Serie de Taylor propia |
| Sin reloj del sistema | `datetime.now()` | El usuario escribe la hora |
| Sin `time.sleep` | `time.sleep(1)` | Bucle vacío calibrable |
| Sin audio | Una librería de sonido | Carácter `BEL` de la terminal |

## La estructura de datos: lista circular enlazada

Un reloj es cíclico: después del segundo 59 viene el 0, después del minuto 59 el 0, y después de la hora 23 el 0. Una lista enlazada normal termina en `None`, así que habría que escribir una comparación especial cada vez que se llega al final. En una **lista circular** el último nodo apunta al primero y esa comparación desaparece: avanzar es siempre "ir al siguiente".

### Los nodos y el anillo

`Mark` es el nodo: guarda un valor y la referencia a la siguiente marca. `Dial` es el anillo, y guarda el primero, el último, el tamaño y un cursor `__current` que es la posición actual.

```text
 Dial de segundos (60 marcas)

   ┌───┐   ┌───┐   ┌───┐         ┌────┐
   │ 0 ├──►│ 1 ├──►│ 2 ├──► ... ─►│ 59 │
   └─▲─┘   └───┘   └───┘         └──┬─┘
     │                              │
     └──────────────────────────────┘   la última marca apunta a la primera
```

Al agregar una marca (`add_mark`), la última nueva queda apuntando otra vez a la primera. Una marca que está sola se apunta a sí misma.

### Tres anillos encadenados

`Clock` tiene tres `Dial`: segundos (60 marcas), minutos (60 marcas) y horas (24 marcas). Cada `tick()` mueve el cursor un paso. `Dial.tick()` además **avisa si dio la vuelta completa**: devuelve `True` cuando el cursor vuelve a la primera marca.

```python
def tick(self) -> None:
    if self.__seconds_dial.tick() and self.__minutes_dial.tick():
        self.__hours_dial.tick()
```

El `and` encadena los anillos como engranajes. Las horas solo avanzan si los minutos acaban de dar la vuelta, y los minutos solo avanzan si los segundos acaban de dar la vuelta. Si los segundos no dieron la vuelta, el `and` ni siquiera mira los minutos.

Ejemplo, de 23:59:59 al siguiente segundo:

| Paso | Dial | Cursor pasa de → a | ¿Dio la vuelta? |
|---|---|---|---|
| 1 | segundos | 59 → **0** | sí, avisa a los minutos |
| 2 | minutos | 59 → **0** | sí, avisa a las horas |
| 3 | horas | 23 → **0** | sí (el día termina) |

## Funcionalidades añadidas

- **Zonas horarias:** Bogotá, Nueva York, Londres, Madrid y Tokio.
- **Alarma:** al llegar a la hora (en la zona que se está mostrando) el borde se pone rojo, aparece el aviso en rojo y suena el `BEL` de la terminal.
- **GIF animado** del reloj corriendo, con un codificador LZW propio.

## Estructura del proyecto

```text
main.py                 punto de entrada
app/
  clock_app.py          une la lógica del reloj con la pantalla
  live.py               reloj en vivo en la terminal
  console.py            modo paso a paso (BMP / GIF)
  pacer.py              espera de ~1 segundo sin reloj del sistema
  terminal_view.py      dibuja el lienzo como texto con color
  parsing.py            lectura de "HH:MM[:SS]"
core/
  dial.py               Mark y Dial: la lista circular enlazada
  clock.py              tres Dial encadenados: segundos, minutos y horas
  time_zone.py          zonas horarias
  alarm.py              alarma
  clock_reading.py      lectura inmutable que viaja a la pantalla
graphics/
  canvas.py             lienzo de píxeles, BMP
  math_utils.py         seno y coseno por serie de Taylor
  shapes.py             línea, círculo, rectángulo y texto
  font.py               fuente de mapa de bits 5x7
  hands.py              manecillas
  clock_view.py         esfera analógica, pantalla digital y vista compacta
  scaling.py            tamaños mínimos para dibujos pequeños
  lzw.py, gif.py        compresión LZW y escritor de GIF
```

## Notas de diseño
- Herencia y polimorfismo: `Shape` (`Line`, `Circle`, `FilledCircle`, `Rectangle`, `Text`) y `Hand` (`HourHand`, `MinuteHand`, `SecondHand`), donde cada manecilla define su propio ángulo.
