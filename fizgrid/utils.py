import math, type_enforced

@type_enforced.Enforcer
def Circle(radius:int, points:int=6, round_to:int=2) -> list:
    """
    Returns a list of addative coordinates that form a circle around a given point.
    """
    return [[round(radius * math.cos(2 * math.pi / points * i),round_to), round(radius * math.sin(2 * math.pi / points * i),round_to)] for i in range(points)]

@type_enforced.Enforcer
def Rectangle(x_len:float|int, y_len:float|int, round_to:int=2) -> list:
    """
    Returns a list of addative coordinates that form a rectangle around a given point.
    """
    return [[round(x_len/2, round_to), round(y_len/2, round_to)],
            [round(-x_len/2, round_to), round(y_len/2, round_to)],
            [round(-x_len/2, round_to), round(-y_len/2, round_to)],
            [round(x_len/2, round_to), round(-y_len/2, round_to)]]