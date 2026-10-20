from graphics.canvas import Canvas, Color, Point


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
