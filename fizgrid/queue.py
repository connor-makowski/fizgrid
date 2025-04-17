import type_enforced, heapq

@type_enforced.Enforcer
class QueueEvent:
    def process(self):
        raise NotImplementedError("Subclasses should implement this method.")

@type_enforced.Enforcer
class TimeQueue:
    def __init__(self):
        self.heap = []
        self.data = {}
        self.time = 0
        self.next_id = 0

    def add_event(self, time:int|float, event:QueueEvent):
        assert time >= self.time, "Time must be greater than or equal to current time"
        id = self.next_id
        self.next_id += 1
        self.data[id] = event
        heapq.heappush(self.heap, (time, id))
        return id

    def remove_event(self, id:int):
        return self.data.pop(id,None)

    def get_next_event(self):
        while self.heap:
            time, id = heapq.heappop(self.heap)
            event = self.remove_event(id)
            if event is None:
                continue
            self.time = time
            return {
                'time': time,
                'id': id,
                'event': event
            }
        return None