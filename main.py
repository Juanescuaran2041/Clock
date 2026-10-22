from app.clock_app import ClockApp
from app.console import ConsoleInterface
from app.live import LiveInterface

MODE_PROMPT = """RELOJ DE LISTA CIRCULAR

  1) Reloj en vivo en la terminal
  2) Paso a paso, guardando una imagen

Elige 1 o 2 (Enter para 1): """


def main() -> None:
    app = ClockApp()
    choice = ""
    while choice not in ("1", "2"):
        choice = input(MODE_PROMPT).strip() or "1"
    if choice == "2":
        ConsoleInterface(app).run()
    else:
        LiveInterface(app).run()


if __name__ == "__main__":
    main()
