from core.alarm import Alarm
from core.clock import Clock
from core.clock_reading import ClockReading
from core.time_zone import ZONES, find_zone
from graphics.canvas import Canvas
from graphics.clock_view import ClockView

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 300


class ClockApp:
    """Ties the clock logic to the screen. It knows nothing about input or files."""

    def __init__(self) -> None:
        self.__clock = Clock()
        self.__home_zone = ZONES[0]  # the zone the user types the time in
        self.__zone = self.__home_zone
        self.__alarm = Alarm()
        self.__canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.__view = ClockView(CANVAS_WIDTH, CANVAS_HEIGHT)

    @property
    def zone_names(self) -> list[str]:
        return [zone.name for zone in ZONES]

    def set_time(self, hours: int, minutes: int, seconds: int) -> None:
        self.__clock.set_time(hours, minutes, seconds)

    def advance(self, seconds: int = 1) -> None:
        for _ in range(seconds):
            self.__clock.tick()

    def select_zone(self, name: str) -> None:
        zone = find_zone(name)
        if zone is None:
            raise ValueError(f"Unknown time zone: {name}")
        self.__zone = zone

    def set_alarm(self, hours: int, minutes: int) -> None:
        self.__alarm.set(hours, minutes)

    def cancel_alarm(self) -> None:
        self.__alarm.cancel()

    def reading(self) -> ClockReading:
        offset = self.__zone.utc_offset - self.__home_zone.utc_offset
        hours = self.__clock.hours_shifted(offset)
        minutes = self.__clock.minutes
        return ClockReading(hours, minutes, self.__clock.seconds, self.__zone.name,
                            self.__alarm.label(), self.__alarm.is_ringing(hours, minutes))

    def render(self) -> Canvas:
        self.__view.render(self.__canvas, self.reading())
        return self.__canvas

    def record(self, seconds: int) -> list[Canvas]:
        """One frame per second, starting now. The clock ends `seconds` later."""
        frames = []
        for _ in range(seconds):
            frames.append(self.render().copy())
            self.advance(1)
        return frames
