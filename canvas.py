"""A pixel canvas that can be saved as a 24-bit BMP image."""

Color = tuple[int, int, int]  # (red, green, blue), each from 0 to 255

WHITE: Color = (255, 255, 255)

BYTES_PER_PIXEL = 3
BMP_FILE_HEADER_SIZE = 14
BMP_INFO_HEADER_SIZE = 40
BMP_HEADER_SIZE = BMP_FILE_HEADER_SIZE + BMP_INFO_HEADER_SIZE
BMP_ROW_ALIGNMENT = 4  # every row in a BMP must be a multiple of 4 bytes


class Point:
    """An immutable position on the canvas."""

    def __init__(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y


class Canvas:
    """A grid of pixels. The origin (0, 0) is the top-left corner."""

    def __init__(self, width: int, height: int, background: Color = WHITE) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Canvas dimensions must be positive")
        self.__width = width
        self.__height = height
        self.__pixels = bytearray()
        self.fill(background)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    def fill(self, color: Color) -> None:
        """Paint every pixel with the given color."""
        self.__pixels = bytearray(self.__encode(color) * (self.__width * self.__height))

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        """Paint one pixel. Coordinates outside the canvas are ignored (clipping)."""
        if not (0 <= x < self.__width and 0 <= y < self.__height):
            return
        index = (y * self.__width + x) * BYTES_PER_PIXEL
        self.__pixels[index:index + BYTES_PER_PIXEL] = self.__encode(color)

    def save_bmp(self, path: str) -> None:
        """Write the canvas to disk as a BMP file."""
        pixel_data = self.__build_pixel_data()
        with open(path, "wb") as file:
            file.write(self.__build_header(len(pixel_data)))
            file.write(pixel_data)

    @staticmethod
    def __encode(color: Color) -> bytes:
        """BMP stores each pixel as blue, green, red."""
        red, green, blue = color
        return bytes((blue, green, red))

    def __build_pixel_data(self) -> bytes:
        row_size = self.__width * BYTES_PER_PIXEL
        padding = bytes(-row_size % BMP_ROW_ALIGNMENT)
        rows = []
        for y in reversed(range(self.__height)):  # BMP rows go bottom to top
            start = y * row_size
            rows.append(bytes(self.__pixels[start:start + row_size]) + padding)
        return b"".join(rows)

    def __build_header(self, pixel_data_size: int) -> bytes:
        def little_endian(value: int, size: int) -> bytes:
            return value.to_bytes(size, "little")

        return b"".join((
            b"BM",                                                  # signature
            little_endian(BMP_HEADER_SIZE + pixel_data_size, 4),    # file size
            bytes(4),                                               # reserved
            little_endian(BMP_HEADER_SIZE, 4),                      # where pixel data starts
            little_endian(BMP_INFO_HEADER_SIZE, 4),
            little_endian(self.__width, 4),
            little_endian(self.__height, 4),
            little_endian(1, 2),                                    # color planes
            little_endian(BYTES_PER_PIXEL * 8, 2),                  # bits per pixel
            bytes(24),                                              # no compression, defaults
        ))
