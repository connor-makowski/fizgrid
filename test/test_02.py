# Testing for TimeQueue class
from fizgrid.queue import TimeQueue

passing = True


class EventClass:
    def custom_event(self, string: str):
        print(string)


eventMaker = EventClass()


# Creating a TimeQueue instance
queue = TimeQueue()

# Creating Empty QueueEvent classes
event_0 = {"callable": eventMaker.custom_event, "string": "Event 0"}
event_1 = {"callable": eventMaker.custom_event, "string": "Event 1"}
event_2 = {"callable": eventMaker.custom_event, "string": "Event 2"}
event_3 = {"callable": eventMaker.custom_event, "string": "Event 3"}

# Populating some example events
t0_id = queue.add_event(time=5, event=event_0)
t1_id = queue.add_event(time=10, event=event_1)
t2_id = queue.add_event(time=7, event=event_2)
t3_id = queue.add_event(time=8, event=event_3)

# Removing an event
queue.remove_event(t3_id)

# Checking the order of events
if queue.get_next_event() != {"id": t0_id, "time": 5, "event": event_0}:
    passing = False
if queue.get_next_event() != {"id": t2_id, "time": 7, "event": event_2}:
    passing = False
if queue.get_next_event() != {"id": t1_id, "time": 10, "event": event_1}:
    passing = False
if queue.get_next_event() != {"id": None, "time": None, "event": None}:
    passing = False

if passing:
    print("test_02.py: passed")
else:
    print("test_02.py: failed")
