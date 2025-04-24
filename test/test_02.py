# Testing for TimeQueue class
from fizgrid.queue import TimeQueue, QueueEvent

passing = True

try:
    # Creating a TimeQueue instance
    queue = TimeQueue()

    # Creating Empty QueueEvent classes
    event_0 = QueueEvent()
    event_1 = QueueEvent()
    event_2 = QueueEvent()
    event_3 = QueueEvent()

    # Populating some example events
    t0_id = queue.add_event(5, event_0)
    t1_id = queue.add_event(10, event_1)
    t2_id = queue.add_event(7, event_2)
    t3_id = queue.add_event(8, event_3)

    # Removing an event
    queue.remove_event(t3_id)

    # Checking the order of events
    if queue.get_next_event() != {'time': 5, 'id': t0_id, 'event': event_0}:
        passing = False
    if queue.get_next_event() != {'time': 7, 'id': t2_id, 'event': event_2}:
        passing = False
    if queue.get_next_event() != {'time': 10, 'id': t1_id, 'event': event_1}:
        passing = False
    if queue.get_next_event() != {'time': None, 'id': None, 'event': None}:
        passing = False
except:
    passing = False

if passing:
    print("test_03.py: passed")
else:
    print("test_03.py: failed")

