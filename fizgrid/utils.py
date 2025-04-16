import math, type_enforced, heapq


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

@type_enforced.Enforcer
class TimeQueue:
    def __init__(self):
        self.heap = []
        self.data = {}
        self.time = 0
        self.next_id = 0

    def add_item(self, time:int|float, obj):
        assert time >= self.time, "Time must be greater than or equal to current time"
        id = self.next_id
        self.next_id += 1
        self.data[id] = obj
        heapq.heappush(self.heap, (time, id))
        return id

    def remove_item(self, id:int):
        return self.data.pop(id,None)

    def get_next_item(self):
        while self.heap:
            time, id = heapq.heappop(self.heap)
            obj = self.remove_item(id)
            if obj is None:
                continue
            self.time = time
            return {
                'time': time,
                'id': id,
                'obj': obj
            }
        return None