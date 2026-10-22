from app.clock_app import ClockApp
from app.pacer import Pacer
from app.parsing import parse_time
from app.terminal_view import TerminalView
from graphics.gif import GifWriter

ANIMATION_FILE = "output/clock.gif"
DEFAULT_ANIMATION_SECONDS = 60
CALIBRATION_FRAMES = 10
CLEAR_SCREEN = "\033[2J\033[H"
CURSOR_HOME = "\033[H"
CLEAR_LINE = "\033[K"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
NEWLINE = chr(10)
BELL = chr(7)
MARGIN = 2  # columns left empty before the picture

WELCOME = f"""{BOLD}RELOJ DE LISTA CIRCULAR{RESET}

Escribe la hora actual de Bogota y el reloj correra solo desde ahi.
  - Ctrl+C en cualquier momento pausa el reloj y abre el menu.
  - La ventana debe medir al menos 104 columnas por 24 filas.
"""

MENU = f"""{BOLD}Comandos{RESET} (Enter vuelve al reloj)
  time HH:MM[:SS]   cambia la hora (hora de Bogota)       {DIM}ej: time 14:30{RESET}
  zone NOMBRE       {{zones}}  {DIM}ej: zone tokio{RESET}
  alarm HH:MM       programa la alarma en la zona actual  {DIM}ej: alarm 07:15{RESET}
  clear             cancela la alarma
  calibrate         ajusta la velocidad con un cronometro
  gif [N]           guarda N segundos (60 por defecto) como GIF animado
  quit              salir"""

TIME_FORMAT_HINT = "usa el formato HH:MM o HH:MM:SS, por ejemplo 14:30"


class LiveInterface:
    """A clock that keeps running in the terminal. Ctrl+C pauses it and opens the menu."""

    def __init__(self, app: ClockApp) -> None:
        self.__app = app
        self.__view = TerminalView(MARGIN)
        self.__pacer = Pacer()

    def run(self) -> None:
        print(CLEAR_SCREEN + WELCOME)
        try:
            self.__ask_initial_time()
        except (KeyboardInterrupt, EOFError):
            print("Hasta luego.")
            return
        print(CLEAR_SCREEN + HIDE_CURSOR, end="")
        try:
            running = True
            while running:
                try:
                    self.__show()
                    self.__pacer.wait()
                    self.__app.advance(1)
                except KeyboardInterrupt:
                    running = self.__menu()
        finally:
            print(f"{SHOW_CURSOR}{CLEAR_SCREEN}Hasta luego.")

    def __ask_initial_time(self) -> None:
        while True:
            try:
                self.__app.set_time(*parse_time(input("Hora actual en Bogota (HH:MM:SS): ")))
                return
            except ValueError:
                print(f"{RED}Formato no valido:{RESET} {TIME_FORMAT_HINT}")

    def __show(self) -> None:
        """Redraws in place. It must fit the window, or every frame would scroll it."""
        reading = self.__app.reading()
        picture = self.__view.render(self.__app.render_compact())
        if reading.alarm_ringing:
            status = f"{RED}{BOLD}*** ALARMA SONANDO ***{RESET}  Ctrl+C: menu{BELL}"
        else:
            status = f"{reading.alarm_label}   {DIM}Ctrl+C: menu{RESET}"
        print(f"{CURSOR_HOME}{picture}{NEWLINE}{' ' * MARGIN}{status}{CLEAR_LINE}",
              end="", flush=True)

    def __menu(self) -> bool:
        """Returns False when the program should end."""
        reading = self.__app.reading()
        print(f"{SHOW_CURSOR}{CLEAR_SCREEN}{BOLD}PAUSA{RESET}  [{reading.zone_name}] "
              f"{reading.time_text()}  {reading.alarm_label}{NEWLINE}")
        print(MENU.replace("{zones}", ", ".join(self.__app.zone_names).lower()))
        while True:
            try:
                line = input(f"{NEWLINE}> ")
                if line.strip().lower() in ("quit", "q", "exit"):
                    return False
                if line.strip() == "":
                    print(CLEAR_SCREEN + HIDE_CURSOR, end="")
                    return True
                print(f"{GREEN}{self.__execute(line)}{RESET}")
            except ValueError as error:
                print(f"{RED}No se pudo:{RESET} {error}")
            except (KeyboardInterrupt, EOFError):
                return False

    def __execute(self, line: str) -> str:
        """Run one menu command. Returns what to tell the user, or raises ValueError."""
        command, _, argument = line.strip().partition(" ")
        command = command.lower()
        if command == "time":
            self.__app.set_time(*self.__parse(argument))
            return f"Hora cambiada a {argument.strip()}."
        if command == "zone":
            return self.__change_zone(argument.strip())
        if command == "alarm":
            hours, minutes, _ = self.__parse(argument)
            self.__app.set_alarm(hours, minutes)
            return f"Alarma programada a las {hours:02d}:{minutes:02d}."
        if command == "clear":
            self.__app.cancel_alarm()
            return "Alarma cancelada."
        if command == "calibrate":
            return self.__calibrate()
        if command == "gif":
            return self.__save_animation(argument)
        raise ValueError(f"no conozco el comando '{command}'. Escribe uno de la lista de arriba")

    @staticmethod
    def __parse(text: str) -> tuple[int, int, int]:
        try:
            return parse_time(text)
        except ValueError:
            raise ValueError(TIME_FORMAT_HINT)

    def __change_zone(self, name: str) -> str:
        try:
            self.__app.select_zone(name)
        except ValueError:
            raise ValueError(f"zona desconocida. Opciones: {', '.join(self.__app.zone_names)}")
        return f"Zona cambiada a {self.__app.reading().zone_name}."

    def __calibrate(self) -> str:
        input(f"Prepara un cronometro y pulsa Enter para empezar. Se muestran "
              f"{CALIBRATION_FRAMES} cuadros: detenlo cuando terminen.")
        print(HIDE_CURSOR + CLEAR_SCREEN, end="")
        for _ in range(CALIBRATION_FRAMES):
            self.__show()
            self.__pacer.wait()
        print(SHOW_CURSOR + CLEAR_SCREEN, end="")
        try:
            seconds = float(input("Segundos que marco el cronometro: "))
            self.__pacer.calibrate(CALIBRATION_FRAMES, seconds)
        except ValueError:
            raise ValueError("escribe un numero de segundos mayor que cero, por ejemplo 12.5")
        return (f"Velocidad ajustada. Repite hasta que marque unos {CALIBRATION_FRAMES} "
                f"segundos (vueltas por cuadro: {self.__pacer.spins}).")

    def __save_animation(self, argument: str) -> str:
        try:
            seconds = int(argument) if argument.strip() else DEFAULT_ANIMATION_SECONDS
        except ValueError:
            raise ValueError("escribe un numero entero de segundos, por ejemplo gif 30")
        if seconds <= 0:
            raise ValueError("los segundos deben ser mayores que cero")
        GifWriter(self.__app.record(seconds)).save(ANIMATION_FILE)
        return f"Guardado en {ANIMATION_FILE}. Arrastralo a un navegador para verlo correr."
