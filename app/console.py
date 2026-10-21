from app.clock_app import ClockApp
from app.parsing import parse_time

OUTPUT_FILE = "output/clock.bmp"

HELP = """Commands:
  (Enter)            advance 1 second
  + N                advance N seconds
  time HH:MM[:SS]    set the time (in Bogota time)
  zone NAME          BOGOTA, NUEVA YORK, LONDRES, MADRID, TOKIO
  alarm HH:MM        set the alarm (in the zone being shown)
  clear              cancel the alarm
  quit               exit"""


class ConsoleInterface:
    """Reads commands from the keyboard and refreshes the image after each one."""

    def __init__(self, app: ClockApp) -> None:
        self.__app = app

    def run(self) -> None:
        print(f"Open {OUTPUT_FILE} in an image viewer and keep it open.")
        self.__ask_initial_time()
        self.__refresh()
        print(HELP)
        running = True
        while running:
            try:
                running = self.__execute(input("> "))
            except ValueError as error:
                print(f"Invalid input: {error}")

    def __ask_initial_time(self) -> None:
        while True:
            try:
                self.__app.set_time(*parse_time(input("Current time in Bogota (HH:MM:SS): ")))
                return
            except ValueError:
                print("Invalid format. Example: 14:30:15")

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
        else:
            print(HELP)
            return True
        self.__refresh()
        return True

    def __refresh(self) -> None:
        self.__app.render().save_bmp(OUTPUT_FILE)
        reading = self.__app.reading()
        print(f"[{reading.zone_name}] {reading.time_text()}")
        if reading.alarm_ringing:
            print("\a*** ALARM RINGING ***")
