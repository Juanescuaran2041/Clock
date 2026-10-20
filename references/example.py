
# ==========================================================
#  PURE PYTHON CLOCK -> generates "clock.svg"
#  No imports, no HTML, no CSS. Opens in a web browser.
# ==========================================================

PI = 3.141592653589793

# ---------- Custom mathematics (without math) ----------
def sine(x):
    while x > PI:
        x -= 2 * PI
    while x < -PI:
        x += 2 * PI
    term = total = x
    for n in range(1, 12):
        term *= -x * x / ((2 * n) * (2 * n + 1))
        total += term
    return total

def cosine(x):
    return sine(x + PI / 2)

# ---------- Input ----------
def get_time(prompt, allow_empty=False):
    while True:
        text = input(prompt).strip()
        if allow_empty and text == "":
            return None
        parts = text.split(":")
        if 2 <= len(parts) <= 3 and all(p.isdigit() for p in parts):
            h, m = int(parts[0]), int(parts[1])
            s = int(parts[2]) if len(parts) == 3 else 0
            if h < 24 and m < 60 and s < 60:
                return h, m, s
        print("Invalid format. Example: 14:30 or 14:30:15")

# ---------- Geometry ----------
C = 200       # Clock center
R = 180       # Radius
Y_DIG = 450   # Digital clock baseline

def point(degrees, r):
    angle = degrees * PI / 180
    return round(C + sine(angle) * r, 2), round(C - cosine(angle) * r, 2)

# ---------- Drawing components ----------
def clock_face():
    parts = [f'<circle cx="{C}" cy="{C}" r="{R}" fill="#fdfdfd" '
             f'stroke="#333" stroke-width="8"/>']
    for i in range(60):  # Minute marks
        length = 18 if i % 5 == 0 else 8
        thickness = 4 if i % 5 == 0 else 1.5
        x1, y1 = point(i * 6, R - 10)
        x2, y2 = point(i * 6, R - 10 - length)
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                     f'stroke="#333" stroke-width="{thickness}"/>')
    for n in range(1, 13):  # Numbers
        x, y = point(n * 30, R - 50)
        parts.append(f'<text x="{x}" y="{y}" font-size="28" font-family="Arial" '
                     f'font-weight="bold" fill="#333" text-anchor="middle" '
                     f'dominant-baseline="central">{n}</text>')
    parts.append(f'<text x="{C}" y="{C + 70}" font-size="14" font-family="Arial" '
                 f'fill="#999" text-anchor="middle">PYTHON</text>')
    return "\n".join(parts)

def clock_hand(length, thickness, color, period, elapsed, stepwise=False):
    line = (f'<line x1="{C}" y1="{C + 20}" x2="{C}" y2="{C - length}" '
            f'stroke="{color}" stroke-width="{thickness}" stroke-linecap="round">')
    if stepwise:  # The second hand moves in 6-degree steps
        values = ";".join(f"{i * 6} {C} {C}" for i in range(60))
        animation = (f'<animateTransform attributeName="transform" type="rotate" '
                     f'values="{values}" calcMode="discrete" dur="{period}s" '
                     f'begin="{-elapsed}s" repeatCount="indefinite"/>')
    else:  # The minute and hour hands move smoothly
        animation = (f'<animateTransform attributeName="transform" type="rotate" '
                     f'from="0 {C} {C}" to="360 {C} {C}" dur="{period}s" '
                     f'begin="{-elapsed}s" repeatCount="indefinite"/>')
    return line + animation + "</line>"

def number_drum(x, texts, step, elapsed):
    """A column of numbers that moves up one row every 'step' seconds."""
    height = 50
    values = ";".join(f"0 {-i * height}" for i in range(len(texts)))
    parts = [f'<g><animateTransform attributeName="transform" type="translate" '
             f'values="{values}" calcMode="discrete" dur="{len(texts) * step}s" '
             f'begin="{-elapsed}s" repeatCount="indefinite"/>']
    for i, text in enumerate(texts):
        parts.append(f'<text x="{x}" y="{Y_DIG + i * height}" font-size="36" '
                     f'font-family="Courier New, monospace" font-weight="bold" '
                     f'fill="#00e676" text-anchor="middle" '
                     f'dominant-baseline="central">{text}</text>')
    parts.append("</g>")
    return "".join(parts)

def digital_clock(total_seconds):
    minutes, seconds = (total_seconds % 3600) // 60, total_seconds % 60
    hours = [f"{i:02d}" for i in range(24)]
    sixty = [f"{i:02d}" for i in range(60)]
    parts = [
        '<clipPath id="window"><rect x="90" y="425" width="220" height="50"/></clipPath>',
        '<rect x="90" y="425" width="220" height="50" rx="10" fill="#1b1b1b"/>',
        '<g clip-path="url(#window)">',
        number_drum(135, hours, 3600, total_seconds),
        number_drum(200, sixty, 60, minutes * 60 + seconds),
        number_drum(265, sixty, 1, seconds),
        "</g>",
    ]
    for x in (167, 233):  # Two blinking colons
        parts.append(f'<text x="{x}" y="{Y_DIG}" font-size="36" '
                     f'font-family="Courier New, monospace" fill="#00e676" '
                     f'text-anchor="middle" dominant-baseline="central">:'
                     f'<animate attributeName="opacity" values="1;0.2" '
                     f'calcMode="discrete" dur="1s" repeatCount="indefinite"/></text>')
    return "\n".join(parts)

def alarm_svg(alarm, total_seconds):
    if alarm is None:
        return (f'<text x="{C}" y="505" font-size="18" font-family="Arial" '
                f'fill="#888" text-anchor="middle">No alarm set</text>')
    alarm_hours, alarm_minutes = alarm
    remaining = (alarm_hours * 3600 + alarm_minutes * 60 - total_seconds) % 86400
    return (
        f'<text x="{C}" y="505" font-size="18" font-family="Arial" fill="#555" '
        f'text-anchor="middle">Alarm: {alarm_hours:02d}:{alarm_minutes:02d}</text>'
        f'<g visibility="hidden">'
        f'<set attributeName="visibility" to="visible" begin="{remaining}s" dur="60s"/>'
        f'<animate attributeName="opacity" values="1;0.15;1" dur="1s" repeatCount="indefinite"/>'
        f'<rect x="60" y="530" width="280" height="50" rx="12" fill="#e53935"/>'
        f'<text x="{C}" y="555" font-size="26" font-family="Arial" font-weight="bold" '
        f'fill="white" text-anchor="middle" dominant-baseline="central">'
        f'ALARM! {alarm_hours:02d}:{alarm_minutes:02d}</text></g>'
    )

# ---------- Main program ----------
print("=== Python Clock Generator ===")
h, m, s = get_time("EXACT time when you will open the clock (HH:MM:SS): ")
total_seconds = h * 3600 + m * 60 + s
result = get_time("Alarm time (HH:MM), or press Enter to skip: ", True)
alarm = None if result is None else (result[0], result[1])

svg = "\n".join([
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="400" height="600">',
    '<rect width="400" height="600" fill="#eceff1"/>',
    clock_face(),
    clock_hand(95, 10, "#333", 43200, (h % 12) * 3600 + m * 60 + s),  # Hour hand
    clock_hand(140, 6, "#333", 3600, m * 60 + s),                     # Minute hand
    clock_hand(150, 2.5, "#e53935", 60, s, stepwise=True),            # Second hand
    f'<circle cx="{C}" cy="{C}" r="9" fill="#333"/>',
    f'<circle cx="{C}" cy="{C}" r="4" fill="#e53935"/>',
    digital_clock(total_seconds),
    alarm_svg(alarm, total_seconds),
    "</svg>",
])

with open("clock.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print("Done! Open 'clock.svg' with Chrome, Edge, or Firefox.")
