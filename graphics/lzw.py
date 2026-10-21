"""LZW compression as the GIF format uses it."""

MAX_CODE_SIZE = 12
TABLE_LIMIT = 1 << MAX_CODE_SIZE  # codes 0 to 4095


class BitPacker:
    """Packs variable-width codes into bytes, least significant bit first."""

    def __init__(self) -> None:
        self.__buffer = 0
        self.__bit_count = 0
        self.__output = bytearray()

    def write(self, code: int, size: int) -> None:
        self.__buffer |= code << self.__bit_count
        self.__bit_count += size
        while self.__bit_count >= 8:
            self.__output.append(self.__buffer & 0xFF)
            self.__buffer >>= 8
            self.__bit_count -= 8

    def finish(self) -> bytes:
        """Flush the last partial byte and return everything written."""
        if self.__bit_count > 0:
            self.__output.append(self.__buffer & 0xFF)
            self.__buffer = 0
            self.__bit_count = 0
        return bytes(self.__output)


class LzwEncoder:
    def __init__(self, min_code_size: int) -> None:
        if not 2 <= min_code_size < MAX_CODE_SIZE:
            raise ValueError("Minimum code size must be between 2 and 11")
        self.__min_code_size = min_code_size
        self.__clear_code = 1 << min_code_size
        self.__end_code = self.__clear_code + 1

    def encode(self, indices: bytes) -> bytes:
        """Compress a sequence of palette indices."""
        packer = BitPacker()
        table: dict[tuple[int, int], int] = {}
        code_size = self.__min_code_size + 1
        next_code = self.__end_code + 1

        packer.write(self.__clear_code, code_size)
        prefix = indices[0]
        for pixel in indices[1:]:
            key = (prefix, pixel)
            if key in table:
                prefix = table[key]
                continue
            packer.write(prefix, code_size)
            if next_code < TABLE_LIMIT:
                table[key] = next_code
                if next_code == (1 << code_size):  # the decoder grows its codes here
                    code_size += 1
                next_code += 1
            else:  # table is full: tell the decoder to start over
                packer.write(self.__clear_code, code_size)
                table.clear()
                code_size = self.__min_code_size + 1
                next_code = self.__end_code + 1
            prefix = pixel

        packer.write(prefix, code_size)
        packer.write(self.__end_code, code_size)
        return packer.finish()
