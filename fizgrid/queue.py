import type_enforced, heapq

from type_enforced.utils import WithSubclasses

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
        self.started=False

    def add_event(self, time:int|float, event:WithSubclasses(QueueEvent)):
        assert time >= self.time, "Time must be greater than or equal to current time"
        id = self.next_id
        self.next_id += 1
        self.data[id] = event
        heapq.heappush(self.heap, (time, id))
        return id

    def remove_event(self, id:int):
        return self.data.pop(id,None)
    
    def remove_next_event(self):
        self.remove_event(heapq.heappop(self.heap)[1])

    def get_next_event(self, peek=False):
        self.started=True
        while self.heap:
            if peek:
                time, id = self.heap[0]
                event = self.data.get(id, None)
                if event is None:
                    # Remove the event from the heap to avoid stale references
                    heapq.heappop(self.heap)
                    continue
            else:
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
        return {
            'time': None,
            'id': None,
            'event': None
        }
    
    def get_next_events(self):
        events = []
        event = self.get_next_event(peek=True)
        if event['event'] is not None:
            self.time = event['time']
            next_event = event
            while next_event['time'] == self.time:
                event = next_event
                self.remove_next_event()
                events.append(event)
                next_event = self.get_next_event(peek=True)
        return events