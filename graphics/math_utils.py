PI = 3.141592653589793
FULL_TURN = 2 * PI
TAYLOR_TERMS = 12


def degrees_to_radians(degrees: float) -> float:
    return degrees * PI / 180


def sin(angle: float) -> float:
    angle = _wrap_angle(angle)
    term = angle
    total = angle
    for n in range(1, TAYLOR_TERMS):
        term *= -angle * angle / ((2 * n) * (2 * n + 1))
        total += term
    return total


def cos(angle: float) -> float:
    return sin(angle + PI / 2)


def _wrap_angle(angle: float) -> float:
    angle -= FULL_TURN * int(angle / FULL_TURN)
    if angle > PI:
        angle -= FULL_TURN
    elif angle < -PI:
        angle += FULL_TURN
    return angle
