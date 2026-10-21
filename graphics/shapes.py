from graphics.canvas import Canvas, Color, Point
from graphics.font import BLANK, GLYPHS, GLYPH_HEIGHT, GLYPH_SPACING, GLYPH_WIDTH


class Shape:
    def __init__(self, color: Color) -> None:
        self._color = color  

    def draw(self, canvas: Canvas) -> None:
        raise NotImplementedError("Each shape implements its own drawing")


class Line(Shape):
    def __init__(self, start: Point, end: Point, color: Color, thickness: int = 1) -> None:
        super().__init__(color)
        self.__start = start
        self.__end = end
        self.__thickness = thickness

    def draw(self, canvas: Canvas) -> None:
        x, y = self.__start.x, self.__start.y
        end_x, end_y = self.__end.x, self.__end.y

        dx = abs(end_x - x)
        dy = -abs(end_y - y)  # it simplifies the error math
        step_x = 1 if x < end_x else -1
        step_y = 1 if y < end_y else -1
        error = dx + dy

        while True:
            self.__paint(canvas, x, y)
            if x == end_x and y == end_y:
                break
            doubled_error = 2 * error
            if doubled_error >= dy:  # the line is drifting: step horizontally
                error += dy
                x += step_x
            if doubled_error <= dx:  # the line is drifting: step vertically
                error += dx
                y += step_y

    def __paint(self, canvas: Canvas, x: int, y: int) -> None:
        half = self.__thickness // 2
        for offset_y in range(-half, half + 1):
            for offset_x in range(-half, half + 1):
                canvas.set_pixel(x + offset_x, y + offset_y, self._color)

class Circle(Shape):
    """A circle outline drawn with the midpoint algorithm."""

    def __init__(self, center: Point, radius: int, color: Color, thickness: int = 1) -> None:
        super().__init__(color)
        self.__center = center
        self.__radius = radius
        self.__thickness = thickness

    def draw(self, canvas: Canvas) -> None:
        # a thick outline is several concentric one-pixel circles
        for radius in range(self.__radius, self.__radius - self.__thickness, -1):
            self.__draw_outline(canvas, radius)

    def __draw_outline(self, canvas: Canvas, radius: int) -> None:
        x = 0
        y = radius
        d = 1 - radius

        while x <= y:
            self.__paint(canvas, x, y)
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1

    def __paint(self, canvas: Canvas, x: int, y: int) -> None:
        """Mirror one point of the first octant into the eight octants."""
        center_x, center_y = self.__center.x, self.__center.y
        for offset_x, offset_y in ((x, y), (y, x), (-x, y), (-y, x),
                                   (x, -y), (y, -x), (-x, -y), (-y, -x)):
            canvas.set_pixel(center_x + offset_x, center_y + offset_y, self._color)


class FilledCircle(Shape):
    def __init__(self, center: Point, radius: int, color: Color) -> None:
        super().__init__(color)
        self.__center = center
        self.__radius = radius

    def draw(self, canvas: Canvas) -> None:
        radius = self.__radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    canvas.set_pixel(self.__center.x + dx, self.__center.y + dy, self._color)


class Rectangle(Shape):
    """A hollow frame."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 color: Color, thickness: int = 1) -> None:
        super().__init__(color)
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__thickness = thickness

    def draw(self, canvas: Canvas) -> None:
        for row in range(self.__height):
            for column in range(self.__width):
                if self.__is_on_border(column, row):
                    canvas.set_pixel(self.__x + column, self.__y + row, self._color)

    def __is_on_border(self, column: int, row: int) -> bool:
        t = self.__thickness
        return (column < t or row < t
                or column >= self.__width - t or row >= self.__height - t)


class Text(Shape):
    """Text built from the 5x7 bitmap font. `scale` multiplies every pixel."""

    def __init__(self, origin: Point, content: str, color: Color, scale: int = 1) -> None:
        super().__init__(color)
        self.__origin = origin
        self.__content = content
        self.__scale = scale

    @classmethod
    def centered_at(cls, center: Point, content: str, color: Color, scale: int = 1) -> "Text":
        width = cls.measure_width(content, scale)
        height = GLYPH_HEIGHT * scale
        return cls(Point(center.x - width // 2, center.y - height // 2), content, color, scale)

    @staticmethod
    def measure_width(content: str, scale: int) -> int:
        return len(content) * (GLYPH_WIDTH + GLYPH_SPACING) * scale - GLYPH_SPACING * scale

    def draw(self, canvas: Canvas) -> None:
        advance = (GLYPH_WIDTH + GLYPH_SPACING) * self.__scale
        for index, character in enumerate(self.__content):
            glyph = GLYPHS.get(character, BLANK)
            self.__draw_glyph(canvas, glyph, self.__origin.x + index * advance)

    def __draw_glyph(self, canvas: Canvas, glyph: tuple, left: int) -> None:
        scale = self.__scale
        for row, line in enumerate(glyph):
            for column, cell in enumerate(line):
                if cell == "#":
                    self.__fill_block(canvas, left + column * scale,
                                      self.__origin.y + row * scale)

    def __fill_block(self, canvas: Canvas, x: int, y: int) -> None:
        for offset_y in range(self.__scale):
            for offset_x in range(self.__scale):
                canvas.set_pixel(x + offset_x, y + offset_y, self._color)
