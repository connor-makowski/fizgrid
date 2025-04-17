import math, type_enforced, uuid


def unique_id():
    """
    Generates a unique identifier.
    """
    return str(uuid.uuid4())

@type_enforced.Enforcer
class Shape:
    @staticmethod
    def circle(radius:int, points:int=6, round_to:int=2) -> list:
        """
        Returns a list of addative coordinates that form a circle around a given point.
        """
        return [[round(radius * math.cos(2 * math.pi / points * i),round_to), round(radius * math.sin(2 * math.pi / points * i),round_to)] for i in range(points)]

    @staticmethod
    def rectangle(x_len:float|int, y_len:float|int, round_to:int=2) -> list:
        """
        Returns a list of addative coordinates that form a rectangle around a given point.
        """
        return [[round(x_len/2, round_to), round(y_len/2, round_to)],
                [round(-x_len/2, round_to), round(y_len/2, round_to)],
                [round(-x_len/2, round_to), round(-y_len/2, round_to)],
                [round(x_len/2, round_to), round(-y_len/2, round_to)]]