from app.clock_app import ClockApp
from app.console import ConsoleInterface


def main() -> None:
    ConsoleInterface(ClockApp()).run()


if __name__ == "__main__":
    main()
