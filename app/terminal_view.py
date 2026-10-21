from graphics.canvas import Canvas

UPPER_HALF_BLOCK = "\u2580"
RESET = "\033[0m"


class TerminalView:
    """Draws a canvas as text. Each character shows two stacked pixels."""

    def __init__(self, margin: int = 0) -> None:
        self.__margin = margin  # blank columns to the left of the picture

    def render(self, canvas: Canvas) -> str:
        rgb = canvas.rgb_bytes()
        lines = []
        for top in range(0, canvas.height - 1, 2):
            line = [" " * self.__margin]
            previous = None
            for x in range(canvas.width):
                pair = (self.__pixel(rgb, canvas.width, x, top),
                        self.__pixel(rgb, canvas.width, x, top + 1))
                if pair != previous:  # repeat the escape codes only when the colors change
                    line.append("\033[38;2;{};{};{}m\033[48;2;{};{};{}m".format(*pair[0], *pair[1]))
                    previous = pair
                line.append(UPPER_HALF_BLOCK)
            lines.append("".join(line) + RESET)
        return "\n".join(lines)

    @staticmethod
    def __pixel(rgb: bytes, width: int, x: int, y: int) -> tuple[int, int, int]:
        start = (y * width + x) * 3
        return rgb[start], rgb[start + 1], rgb[start + 2]
