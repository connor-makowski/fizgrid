# Testing for TimeQueue class
from fizgrid.queue import TimeQueue
from fizgrid.utils import Thunk

passing = True

class EventClass:
    def custom_event(self, string:str):
        print(string)

eventMaker = EventClass()


# Creating a TimeQueue instance
queue = TimeQueue()

# Creating Empty QueueEvent classes
event_0 = {"time":5, 'callable':eventMaker.custom_event , "kwargs":{'string': "Event 0"}}
event_1 = {"time":10, 'callable':eventMaker.custom_event , "kwargs":{'string': "Event 1"}}
event_2 = {"time":7, 'callable':eventMaker.custom_event , "kwargs":{'string': "Event 2"}}
event_3 = {"time":8, 'callable':eventMaker.custom_event , "kwargs":{'string': "Event 3"}}

# Populating some example events
t0_id = queue.add_event(**event_0)
t1_id = queue.add_event(**event_1)
t2_id = queue.add_event(**event_2)
t3_id = queue.add_event(**event_3)

# Removing an event
queue.remove_event(t3_id)

# Checking the order of events
if queue.get_next_event() != {"id": t0_id, **event_0}:
    passing = False
if queue.get_next_event() != {'id': t2_id, **event_2}:
    passing = False
if queue.get_next_event() != {'id': t1_id, **event_1}:
    passing = False
if queue.get_next_event() != {'id': None, "time":None, 'callable': None, 'kwargs': None}:
    passing = False

if passing:
    print("test_02.py: passed")
else:
    print("test_02.py: failed")

