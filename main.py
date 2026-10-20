# ==========================================================
#  RELOJ EN PYTHON PURO -> genera "reloj.svg"
#  Sin import, sin HTML, sin CSS. Se abre con el navegador.
# ==========================================================

PI = 3.141592653589793

# ---------- Matemáticas propias (sin math) ----------
def seno(x):
    while x > PI:
        x -= 2 * PI
    while x < -PI:
        x += 2 * PI
    termino = suma = x
    for n in range(1, 12):
        termino *= -x * x / ((2 * n) * (2 * n + 1))
        suma += termino
    return suma

def coseno(x):
    return seno(x + PI / 2)

# ---------- Entrada de datos ----------
def pedir_hora(mensaje, permitir_vacio=False):
    while True:
        texto = input(mensaje).strip()
        if permitir_vacio and texto == "":
            return None
        partes = texto.split(":")
        if 2 <= len(partes) <= 3 and all(p.isdigit() for p in partes):
            h, m = int(partes[0]), int(partes[1])
            s = int(partes[2]) if len(partes) == 3 else 0
            if h < 24 and m < 60 and s < 60:
                return h, m, s
        print("Formato inválido. Ejemplo: 14:30 o 14:30:15")

# ---------- Geometría ----------
C = 200   # centro del reloj
R = 180   # radio
Y_DIG = 450  # línea del reloj digital

def punto(grados, r):
    a = grados * PI / 180
    return round(C + seno(a) * r, 2), round(C - coseno(a) * r, 2)

# ---------- Piezas del dibujo ----------
def esfera():
    partes = [f'<circle cx="{C}" cy="{C}" r="{R}" fill="#fdfdfd" '
              f'stroke="#333" stroke-width="8"/>']
    for i in range(60):  # marcas de minutos
        largo = 18 if i % 5 == 0 else 8
        grosor = 4 if i % 5 == 0 else 1.5
        x1, y1 = punto(i * 6, R - 10)
        x2, y2 = punto(i * 6, R - 10 - largo)
        partes.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                      f'stroke="#333" stroke-width="{grosor}"/>')
    for n in range(1, 13):  # números
        x, y = punto(n * 30, R - 50)
        partes.append(f'<text x="{x}" y="{y}" font-size="28" font-family="Arial" '
                      f'font-weight="bold" fill="#333" text-anchor="middle" '
                      f'dominant-baseline="central">{n}</text>')
    partes.append(f'<text x="{C}" y="{C + 70}" font-size="14" font-family="Arial" '
                  f'fill="#999" text-anchor="middle">PYTHON</text>')
    return "\n".join(partes)

def manecilla(largo, grosor, color, periodo, transcurrido, saltos=False):
    linea = (f'<line x1="{C}" y1="{C + 20}" x2="{C}" y2="{C - largo}" '
             f'stroke="{color}" stroke-width="{grosor}" stroke-linecap="round">')
    if saltos:  # el segundero avanza a saltos de 6°
        valores = ";".join(f"{i * 6} {C} {C}" for i in range(60))
        anim = (f'<animateTransform attributeName="transform" type="rotate" '
                f'values="{valores}" calcMode="discrete" dur="{periodo}s" '
                f'begin="{-transcurrido}s" repeatCount="indefinite"/>')
    else:       # minutero y horario avanzan suave
        anim = (f'<animateTransform attributeName="transform" type="rotate" '
                f'from="0 {C} {C}" to="360 {C} {C}" dur="{periodo}s" '
                f'begin="{-transcurrido}s" repeatCount="indefinite"/>')
    return linea + anim + "</line>"

def tambor(x, textos, paso, transcurrido):
    """Columna de números que sube un renglón cada 'paso' segundos."""
    alto = 50
    valores = ";".join(f"0 {-i * alto}" for i in range(len(textos)))
    partes = [f'<g><animateTransform attributeName="transform" type="translate" '
              f'values="{valores}" calcMode="discrete" dur="{len(textos) * paso}s" '
              f'begin="{-transcurrido}s" repeatCount="indefinite"/>']
    for i, t in enumerate(textos):
        partes.append(f'<text x="{x}" y="{Y_DIG + i * alto}" font-size="36" '
                      f'font-family="Courier New, monospace" font-weight="bold" '
                      f'fill="#00e676" text-anchor="middle" '
                      f'dominant-baseline="central">{t}</text>')
    partes.append("</g>")
    return "".join(partes)

def digital(total):
    m, s = (total % 3600) // 60, total % 60
    horas = [f"{i:02d}" for i in range(24)]
    sesenta = [f"{i:02d}" for i in range(60)]
    partes = [
        '<clipPath id="ventana"><rect x="90" y="425" width="220" height="50"/></clipPath>',
        '<rect x="90" y="425" width="220" height="50" rx="10" fill="#1b1b1b"/>',
        '<g clip-path="url(#ventana)">',
        tambor(135, horas, 3600, total),
        tambor(200, sesenta, 60, m * 60 + s),
        tambor(265, sesenta, 1, s),
        "</g>",
    ]
    for x in (167, 233):  # dos puntos que parpadean
        partes.append(f'<text x="{x}" y="{Y_DIG}" font-size="36" '
                      f'font-family="Courier New, monospace" fill="#00e676" '
                      f'text-anchor="middle" dominant-baseline="central">:'
                      f'<animate attributeName="opacity" values="1;0.2" '
                      f'calcMode="discrete" dur="1s" repeatCount="indefinite"/></text>')
    return "\n".join(partes)

def alarma_svg(alarma, total):
    if alarma is None:
        return (f'<text x="{C}" y="505" font-size="18" font-family="Arial" '
                f'fill="#888" text-anchor="middle">Sin alarma</text>')
    ah, am = alarma
    faltan = (ah * 3600 + am * 60 - total) % 86400  # segundos hasta la alarma
    return (
        f'<text x="{C}" y="505" font-size="18" font-family="Arial" fill="#555" '
        f'text-anchor="middle">Alarma: {ah:02d}:{am:02d}</text>'
        f'<g visibility="hidden">'
        f'<set attributeName="visibility" to="visible" begin="{faltan}s" dur="60s"/>'
        f'<animate attributeName="opacity" values="1;0.15;1" dur="1s" repeatCount="indefinite"/>'
        f'<rect x="60" y="530" width="280" height="50" rx="12" fill="#e53935"/>'
        f'<text x="{C}" y="555" font-size="26" font-family="Arial" font-weight="bold" '
        f'fill="white" text-anchor="middle" dominant-baseline="central">'
        f'¡ALARMA! {ah:02d}:{am:02d}</text></g>'
    )

# ---------- Programa principal ----------
print("=== Generador del Reloj en Python ===")
h, m, s = pedir_hora("Hora EXACTA en la que abrirás el reloj (HH:MM:SS): ")
total = h * 3600 + m * 60 + s
r = pedir_hora("Hora de la alarma (HH:MM), o Enter para no poner: ", True)
alarma = None if r is None else (r[0], r[1])

svg = "\n".join([
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="400" height="600">',
    '<rect width="400" height="600" fill="#eceff1"/>',
    esfera(),
    manecilla(95, 10, "#333", 43200, (h % 12) * 3600 + m * 60 + s),  # horario
    manecilla(140, 6, "#333", 3600, m * 60 + s),                      # minutero
    manecilla(150, 2.5, "#e53935", 60, s, saltos=True),               # segundero
    f'<circle cx="{C}" cy="{C}" r="9" fill="#333"/>',
    f'<circle cx="{C}" cy="{C}" r="4" fill="#e53935"/>',
    digital(total),
    alarma_svg(alarma, total),
    "</svg>",
])

with open("reloj.svg", "w", encoding="utf-8") as archivo:
    archivo.write(svg)

print("¡Listo! Abre 'reloj.svg' con Chrome, Edge o Firefox.")