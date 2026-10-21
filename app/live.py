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
BOLD = "\033[1m"
RED = "\033[31m"
RESET = "\033[0m"
NEWLINE = chr(10)
BELL = chr(7)
MARGIN = 6  # columns left empty around the clock
PICTURE_WIDTH = 46

MENU = """Commands (Enter goes back to the clock):
  time HH:MM[:SS]    set the time (in Bogota time)
  zone NAME          BOGOTA, NUEVA YORK, LONDRES, MADRID, TOKIO
  alarm HH:MM        set the alarm (in the zone being shown)
  clear              cancel the alarm
  calibrate          adjust the speed with a stopwatch
  gif [N]            save N seconds (default 60) as an animated GIF
  quit               exit"""


class LiveInterface:
    """A clock that keeps running in the terminal. Ctrl+C pauses it and opens the menu."""

    def __init__(self, app: ClockApp) -> None:
        self.__app = app
        self.__view = TerminalView(MARGIN)
        self.__pacer = Pacer()

    def run(self) -> None:
        self.__ask_initial_time()
        print(CLEAR_SCREEN, end="")
        running = True
        while running:
            try:
                self.__show()
                self.__pacer.wait()
                self.__app.advance(1)
            except KeyboardInterrupt:
                running = self.__menu()

    def __ask_initial_time(self) -> None:
        while True:
            try:
                self.__app.set_time(*parse_time(input("Current time in Bogota (HH:MM:SS): ")))
                return
            except ValueError:
                print("Invalid format. Example: 14:30:15")

    def __show(self) -> None:
        reading = self.__app.reading()
        picture = self.__view.render(self.__app.render_dial())
        ringing = "*** ALARMA SONANDO ***" if reading.alarm_ringing else ""
        caption = (
            "",
            BOLD + self.__centered(reading.time_text()) + RESET,
            self.__centered(reading.zone_name),
            self.__centered(reading.alarm_label),
            RED + self.__centered(ringing) + RESET,
            "",
            self.__centered("Ctrl+C: menu"),
        )
        padding = " " * MARGIN
        text = NEWLINE.join(f"{padding}{line}{CLEAR_LINE}" for line in caption)
        bell = BELL if reading.alarm_ringing else ""
        print(f"{CURSOR_HOME}{NEWLINE}{picture}{NEWLINE}{text}{bell}", flush=True)

    @staticmethod
    def __centered(text: str) -> str:
        return text.center(PICTURE_WIDTH)

    def __menu(self) -> bool:
        """Returns False when the program should end."""
        print(CLEAR_SCREEN + MENU)
        while True:
            try:
                line = input("> ")
                if line.strip().lower() == "quit":
                    return False
                if line.strip() == "":
                    print(CLEAR_SCREEN, end="")
                    return True
                self.__execute(line)
            except ValueError as error:
                print(f"Invalid input: {error}")
            except (KeyboardInterrupt, EOFError):
                return False

    def __execute(self, line: str) -> None:
        command, _, argument = line.strip().partition(" ")
        command = command.lower()
        if command == "time":
            self.__app.set_time(*parse_time(argument))
        elif command == "zone":
            self.__app.select_zone(argument)
        elif command == "alarm":
            hours, minutes, _ = parse_time(argument)
            self.__app.set_alarm(hours, minutes)
        elif command == "clear":
            self.__app.cancel_alarm()
        elif command == "calibrate":
            self.__calibrate()
        elif command == "gif":
            self.__save_animation(int(argument) if argument else DEFAULT_ANIMATION_SECONDS)
        else:
            print(MENU)

    def __calibrate(self) -> None:
        input(f"Start a stopwatch and press Enter. {CALIBRATION_FRAMES} frames will run; "
              "stop it when they end.")
        for _ in range(CALIBRATION_FRAMES):
            self.__show()
            self.__pacer.wait()
        print(CLEAR_SCREEN, end="")
        self.__pacer.calibrate(CALIBRATION_FRAMES, float(input("Seconds on the stopwatch: ")))
        print(f"Done. Repeat until it reads {CALIBRATION_FRAMES} seconds. "
              f"Spins per frame: {self.__pacer.spins}")

    def __save_animation(self, seconds: int) -> None:
        if seconds <= 0:
            raise ValueError("Seconds must be positive")
        GifWriter(self.__app.record(seconds)).save(ANIMATION_FILE)
        print(f"Saved {ANIMATION_FILE}. Open it in a browser to watch it run.")
