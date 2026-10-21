# Reloj con Python

Reloj analógico y digital hecho **solo con Python**, sin ningún import de la librería estándar ni de librerías externas. Los únicos imports son entre los módulos del propio proyecto. No usa HTML, CSS ni SVG.

La estructura de datos central es la **lista circular enlazada**: cada manecilla recorre un anillo de marcas (`Mark`) que vuelve al inicio al terminar la vuelta.

## Ejecución

```text
python main.py
```

Al iniciar se elige el modo:

1. **Reloj en vivo en la terminal.** Se escribe la hora de Bogotá una sola vez (`HH:MM:SS`) y el reloj corre solo, dibujado con bloques de color ANSI. Dibuja la esfera analógica con la zona y la hora a su lado, y el estado de la alarma debajo. Necesita una terminal de al menos 104 columnas por 24 filas; si es más pequeña, la imagen se desordena.
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

### Calibrar la velocidad

Sin `time` ni `datetime`, el programa no puede leer el reloj del sistema. Para esperar un segundo entre cuadros, `Pacer` recorre un bucle vacío un número fijo de veces, y ese número depende de la velocidad de cada computador.

Si el reloj va muy rápido o muy lento: `Ctrl+C`, `calibrate`, se cronometran los 10 cuadros que se ejecutan, se escriben los segundos medidos y se repite hasta que marque unos 10 segundos.

### Modo paso a paso

Comandos: `Enter` (avanza 1 segundo), `+ N` (avanza N segundos), `time`, `zone`, `alarm`, `clear`, `gif [N]` y `quit`. Se abre `output/clock.bmp` en un visor de imágenes y se mantiene abierto. El GIF se ve arrastrándolo a un navegador.

## Funcionalidad añadida

- **Zonas horarias:** Bogotá, Nueva York, Londres, Madrid y Tokio (con el horario de octubre de 2026).
- **Alarma:** al llegar a la hora, el borde se pone rojo, aparece el texto de aviso y suena el pitido de la terminal.
- **GIF animado** del reloj corriendo, generado con un codificador LZW propio.

## Estructura

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
  clock.py              tres Dial encadenados: segundos (60), minutos (60), horas (24)
  time_zone.py          zonas horarias
  alarm.py              alarma
  clock_reading.py      lectura inmutable que viaja a la pantalla
graphics/
  canvas.py             lienzo de píxeles, BMP
  math_utils.py         seno y coseno por serie de Taylor
  shapes.py             línea, círculo, rectángulo y texto
  font.py               fuente de mapa de bits 5x7
  hands.py              manecillas
  clock_view.py         esfera analógica y pantalla digital
  lzw.py, gif.py        compresión LZW y escritor de GIF
```

## Cómo funciona la lista circular

`Dial` es una lista circular enlazada de `Mark`. Cada `tick()` mueve el puntero a la siguiente marca, y devuelve `True` cuando da la vuelta completa. `Clock` encadena tres `Dial`: cuando los segundos completan la vuelta, hacen avanzar los minutos, y cuando estos la completan, hacen avanzar las horas.

## Notas de diseño

- Código en inglés, con type hints, docstrings y constantes con nombre.
- Atributos privados (`__x`) expuestos con `@property`.
- Jerarquías con herencia y polimorfismo: `Shape` (`Line`, `Circle`, `FilledCircle`, `Rectangle`, `Text`) y `Hand` (`HourHand`, `MinuteHand`, `SecondHand`).
- Seno y coseno propios, sin `math`.
