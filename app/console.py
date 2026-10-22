from app.clock_app import ClockApp
from app.parsing import parse_time
from graphics.gif import GifWriter

OUTPUT_FILE = "output/clock.bmp"
ANIMATION_FILE = "output/clock.gif"
DEFAULT_ANIMATION_SECONDS = 60

HELP = """Comandos:
  (Enter)            avanza 1 segundo
  + N                avanza N segundos
  time HH:MM[:SS]    cambia la hora (hora de Bogotá)
  zone NOMBRE        BOGOTA, NUEVA YORK, LONDRES, MADRID, TOKIO
  alarm HH:MM        programa la alarma en la zona que se muestra
  clear              cancela la alarma
  gif [N]            guarda N segundos (60 por defecto) como GIF animado
  quit               salir"""

INVALID_INPUT = "Dato no válido. Revisa el comando, la zona o el formato de la hora (HH:MM[:SS])."


class ConsoleInterface:
    """Reads commands from the keyboard and refreshes the image after each one."""

    def __init__(self, app: ClockApp) -> None:
        self.__app = app

    def run(self) -> None:
        print(f"Abre {OUTPUT_FILE} en un visor de imágenes y déjalo abierto.")
        self.__ask_initial_time()
        self.__refresh()
        print(HELP)
        running = True
        while running:
            try:
                running = self.__execute(input("> "))
            except ValueError:
                print(INVALID_INPUT)

    def __ask_initial_time(self) -> None:
        while True:
            try:
                self.__app.set_time(*parse_time(input("Hora actual en Bogotá (HH:MM:SS): ")))
                return
            except ValueError:
                print("Formato no válido. Ejemplo: 14:30:15")

    def __execute(self, line: str) -> bool:
        """Run one command. Returns False when the program should end."""
        command, _, argument = line.strip().partition(" ")
        command = command.lower()
        if command == "quit":
            return False
        if command == "":
            self.__app.advance(1)
        elif command == "+":
            self.__app.advance(int(argument))
        elif command == "time":
            self.__app.set_time(*parse_time(argument))
        elif command == "zone":
            self.__app.select_zone(argument)
        elif command == "alarm":
            hours, minutes, _ = parse_time(argument)
            self.__app.set_alarm(hours, minutes)
        elif command == "clear":
            self.__app.cancel_alarm()
        elif command == "gif":
            self.__save_animation(int(argument) if argument else DEFAULT_ANIMATION_SECONDS)
        else:
            print(HELP)
            return True
        self.__refresh()
        return True

    def __save_animation(self, seconds: int) -> None:
        if seconds <= 0:
            raise ValueError("Seconds must be positive")
        GifWriter(self.__app.record(seconds)).save(ANIMATION_FILE)
        print(f"Guardado en {ANIMATION_FILE}. Arrástralo a un navegador para verlo correr.")

    def __refresh(self) -> None:
        self.__app.render().save_bmp(OUTPUT_FILE)
        reading = self.__app.reading()
        print(f"[{reading.zone_name}] {reading.time_text()}")
        if reading.alarm_ringing:
            print("\a*** ALARMA SONANDO ***")
