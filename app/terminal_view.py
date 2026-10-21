from graphics.canvas import BYTES_PER_PIXEL, Canvas, Color
from graphics.palette import BACKGROUND

CELL_SIZE = 6  # canvas pixels covered by one half block, in each direction
UPPER_HALF_BLOCK = "▀"
RESET = "\033[0m"


class TerminalView:
    """Shrinks a canvas into text. Each character shows two stacked cells of the canvas."""

    def __init__(self, cell_size: int = CELL_SIZE) -> None:
        self.__cell = cell_size

    def render(self, canvas: Canvas) -> str:
        rgb = canvas.rgb_bytes()
        columns = canvas.width // self.__cell
        lines = []
        for top in range(0, canvas.height // self.__cell - 1, 2):
            line = []
            previous = None
            for column in range(columns):
                x = column * self.__cell
                pair = (self.__sample(rgb, canvas.width, x, top * self.__cell),
                        self.__sample(rgb, canvas.width, x, (top + 1) * self.__cell))
                if pair != previous:  # repeat the escape codes only when the colors change
                    line.append(self.__colors(*pair))
                    previous = pair
                line.append(UPPER_HALF_BLOCK)
            lines.append("".join(line) + RESET)
        return "\n".join(lines)

    def __sample(self, rgb: bytes, width: int, x: int, y: int) -> Color:
        """The first pixel in the cell that is not background, so thin hands survive."""
        blank = bytes(BACKGROUND) * self.__cell
        for row in range(y, y + self.__cell):
            start = (row * width + x) * BYTES_PER_PIXEL
            chunk = rgb[start:start + self.__cell * BYTES_PER_PIXEL]
            if chunk != blank:
                for offset in range(0, len(chunk), BYTES_PER_PIXEL):
                    pixel = chunk[offset:offset + BYTES_PER_PIXEL]
                    if pixel != bytes(BACKGROUND):
                        return pixel[0], pixel[1], pixel[2]
        return BACKGROUND

    @staticmethod
    def __colors(top: Color, bottom: Color) -> str:
        return "\033[38;2;{};{};{}m\033[48;2;{};{};{}m".format(*top, *bottom)
