from graphics.canvas import Canvas, Color
from graphics.lzw import LzwEncoder

MAX_PALETTE_COLORS = 256
MAX_SUBBLOCK_SIZE = 255  # GIF data travels in blocks of at most 255 bytes
DO_NOT_DISPOSE = 1 << 2  # keep the previous frame under the next one


def _little_endian(value: int, size: int) -> bytes:
    return value.to_bytes(size, "little")


class GifWriter:
    """Writes canvases as an endlessly looping animated GIF, one canvas per frame."""

    def __init__(self, frames: list[Canvas], delay_seconds: float = 1.0) -> None:
        if not frames:
            raise ValueError("At least one frame is needed")
        if any(f.width != frames[0].width or f.height != frames[0].height for f in frames):
            raise ValueError("All frames must have the same size")
        self.__frames = frames
        self.__delay = round(delay_seconds * 100)  # GIF counts in hundredths of a second

    def save(self, path: str) -> None:
        palette = self.__build_palette()
        bits = max(1, (len(palette) - 1).bit_length())
        lookup = {color: index for index, color in enumerate(palette)}
        encoder = LzwEncoder(max(2, bits))

        with open(path, "wb") as file:
            file.write(self.__header(palette, bits))
            for frame in self.__frames:
                file.write(self.__frame_block(frame, lookup, encoder, max(2, bits)))
            file.write(b";")  # trailer

    def __build_palette(self) -> list[Color]:
        colors: set[Color] = set()
        for frame in self.__frames:
            rgb = frame.rgb_bytes()
            colors.update(zip(rgb[0::3], rgb[1::3], rgb[2::3]))
        if len(colors) > MAX_PALETTE_COLORS:
            raise ValueError("A GIF supports at most 256 different colors")
        return sorted(colors)

    def __header(self, palette: list[Color], bits: int) -> bytes:
        table_size = 1 << bits
        padded = palette + [(0, 0, 0)] * (table_size - len(palette))
        table = b"".join(bytes(color) for color in padded)
        first = self.__frames[0]
        return b"".join((
            b"GIF89a",
            _little_endian(first.width, 2),
            _little_endian(first.height, 2),
            bytes((0x80 | ((bits - 1) << 4) | (bits - 1), 0, 0)),  # global color table flags
            table,
            b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00",  # loop forever
        ))

    def __frame_block(self, frame: Canvas, lookup: dict, encoder: LzwEncoder,
                      min_code_size: int) -> bytes:
        rgb = frame.rgb_bytes()
        indices = bytes(map(lookup.__getitem__, zip(rgb[0::3], rgb[1::3], rgb[2::3])))
        return b"".join((
            b"\x21\xF9\x04", bytes((DO_NOT_DISPOSE,)), _little_endian(self.__delay, 2),
            b"\x00\x00",  # no transparent color, end of extension
            b"\x2C", _little_endian(0, 2), _little_endian(0, 2),
            _little_endian(frame.width, 2), _little_endian(frame.height, 2), b"\x00",
            bytes((min_code_size,)),
            self.__sub_blocks(encoder.encode(indices)),
        ))

    @staticmethod
    def __sub_blocks(data: bytes) -> bytes:
        blocks = bytearray()
        for start in range(0, len(data), MAX_SUBBLOCK_SIZE):
            chunk = data[start:start + MAX_SUBBLOCK_SIZE]
            blocks.append(len(chunk))
            blocks += chunk
        blocks.append(0)  # terminator
        return bytes(blocks)
