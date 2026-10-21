from app.clock_app import ClockApp
from app.console import ConsoleInterface
from app.live import LiveInterface


def main() -> None:
    app = ClockApp()
    choice = input("1) Live clock in the terminal  2) Step by step with an image file: ")
    if choice.strip() == "2":
        ConsoleInterface(app).run()
    else:
        LiveInterface(app).run()


if __name__ == "__main__":
    main()
