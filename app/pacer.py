DEFAULT_SPINS = 100_000_000  # a guess; every computer needs its own value


class Pacer:
    """Waits about one second per frame without a system clock, by burning empty loop turns."""

    def __init__(self, spins: int = DEFAULT_SPINS) -> None:
        self.__spins = spins

    @property
    def spins(self) -> int:
        return self.__spins

    def wait(self) -> None:
        for _ in range(self.__spins):
            pass

    def calibrate(self, frames: int, real_seconds: float) -> None:
        """Scale the wait using a stopwatch: `frames` frames took `real_seconds` for real."""
        if frames <= 0 or real_seconds <= 0:
            raise ValueError("Frames and seconds must be positive")
        self.__spins = max(1, round(self.__spins * frames / real_seconds))
