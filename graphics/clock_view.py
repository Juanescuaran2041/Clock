from core.clock_reading import ClockReading
from graphics.canvas import Canvas, Point
from graphics.hands import HourHand, MinuteHand, SecondHand
from graphics.math_utils import cos, degrees_to_radians, sin
from graphics.palette import BACKGROUND, NAVY, ORANGE, PURPLE, RED
from graphics.scaling import scaled
from graphics.shapes import Circle, FilledCircle, Line, Rectangle, Text

MINUTES_ON_DIAL = 60
HOURS_ON_DIAL = 12
DEGREES_PER_MINUTE = 6
DEGREES_PER_HOUR = 30


class AnalogFace:
    def __init__(self, center: Point, radius: int, detail: float = 1.0) -> None:
        """`detail` shrinks the line widths and numbers when the face is drawn small."""
        self.__center = center
        self.__radius = radius
        self.__detail = detail
        self.__hands = (HourHand(), MinuteHand(), SecondHand())

    def draw(self, canvas: Canvas, reading: ClockReading) -> None:
        Circle(self.__center, self.__radius, NAVY, scaled(3, self.__detail)).draw(canvas)
        self.__draw_ticks(canvas)
        self.__draw_numbers(canvas)
        for hand in self.__hands:
            hand.draw(canvas, self.__center, self.__radius, reading, self.__detail)
        FilledCircle(self.__center, scaled(5, self.__detail), NAVY).draw(canvas)

    def __point_on_dial(self, degrees: float, radius_ratio: float) -> Point:
        radians = degrees_to_radians(degrees)
        distance = self.__radius * radius_ratio
        return Point(round(self.__center.x + distance * sin(radians)),
                     round(self.__center.y - distance * cos(radians)))

    def __draw_ticks(self, canvas: Canvas) -> None:
        for minute in range(MINUTES_ON_DIAL):
            is_hour_mark = minute % 5 == 0
            inner_ratio = 0.86 if is_hour_mark else 0.92
            degrees = minute * DEGREES_PER_MINUTE
            Line(self.__point_on_dial(degrees, inner_ratio),
                 self.__point_on_dial(degrees, 0.96),
                 NAVY, scaled(2 if is_hour_mark else 1, self.__detail)).draw(canvas)

    def __draw_numbers(self, canvas: Canvas) -> None:
        for hour in range(1, HOURS_ON_DIAL + 1):
            position = self.__point_on_dial(hour * DEGREES_PER_HOUR, 0.74)
            Text.centered_at(position, str(hour), NAVY, scaled(2, self.__detail)).draw(canvas)


class DigitalDisplay:
    def __init__(self, left: int) -> None:
        self.__left = left

    def draw(self, canvas: Canvas, reading: ClockReading) -> None:
        left = self.__left
        Text(Point(left, 50), reading.zone_name, PURPLE, 3).draw(canvas)
        Text(Point(left, 110), reading.time_text(), NAVY, 5).draw(canvas)
        Text(Point(left, 190), reading.alarm_label, NAVY, 2).draw(canvas)
        if reading.alarm_ringing:
            Text(Point(left, 225), "SONANDO", RED, 4).draw(canvas)


class ClockView:
    """Composes the analog face, the digital display and the alarm frame."""

    def __init__(self, width: int, height: int) -> None:
        self.__width = width
        self.__height = height
        self.__face = AnalogFace(Point(150, height // 2), 130)
        self.__digital = DigitalDisplay(330)

    def render(self, canvas: Canvas, reading: ClockReading) -> None:
        canvas.fill(BACKGROUND)
        self.__face.draw(canvas, reading)
        self.__digital.draw(canvas, reading)
        if reading.alarm_ringing:
            Rectangle(0, 0, self.__width, self.__height, RED, 6).draw(canvas)
        else:
            Rectangle(0, 0, self.__width, self.__height, ORANGE, 2).draw(canvas)
