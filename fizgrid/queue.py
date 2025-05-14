import type_enforced, heapq


@type_enforced.Enforcer(enabled=True)
class TimeQueue:
    def __init__(self):
        """
        Initializes a TimeQueue instance.
        This class is used to manage a queue of events that occur at specific times.
        It uses a min-heap to efficiently manage the events based on their scheduled times.
        """
        self.__heap__ = []
        self.__data__ = {}
        self.__time__ = 0
        self.__next_id__ = 0

    def add_event(
        self, time: int | float, event: dict = dict(), priority: int = 0
    ) -> int:
        """
        Adds an event to the queue.

        Args:

        - time (int|float): The time at which the event should occur.
        - event (dict): The event to be added to the queue.
            - Default: {}
            - This have any dictionary strucutre, depending on your queue needs
        - priority (int): The priority of the event.
            - Default: 0
            - Higher values indicate higher priority.
            - This is used to determine the order of events with the same time.
            - If two events have the same time, the one with the higher priority will be processed first.
            - If the priority is the same, the event with the lower ID will be processed first.

        Returns:

        - int: The ID of the added event.
            - This ID is used to reference the event in the queue.
        """
        assert (
            time >= self.__time__
        ), "Time must be greater than or equal to current time"
        id = self.__next_id__
        self.__next_id__ += 1
        self.__data__[id] = event
        heapq.heappush(self.__heap__, (time, -priority, id))
        return id

    def remove_event(self, id: int) -> dict | None:
        """
        Removes an event from the queue using its ID.

        Args:

            - id (int): The ID of the event to be removed.
                - This ID is used to reference the event in the queue.
        Returns:
            - dict: The removed event.
                - If the event is not found, None is returned.
        """
        return self.__data__.pop(id, None)

    def remove_next_event(self) -> dict | None:
        """
        Removes the next event from the queue.
        This method is used to get the next event in the queue and remove it from the heap.

        Returns:

        - dict: The removed event.
            - If the queue is empty, None is returned.
        """
        self.remove_event(heapq.heappop(self.__heap__)[2])

    def get_next_event(self, peek: bool = False):
        """
        Retrieves the next event from the queue without removing it.
        This method is used to get the next event in the queue

        Args:

        - peek (bool): If True, the event is not removed from the queue.
            - Default: False
            - If False, the event is removed from the queue.

        Returns:

        - dict: The next event in the queue.
            - If the queue is empty, None is returned.
        """
        while self.__heap__:
            if peek:
                time, priority, id = self.__heap__[0]
                event = self.__data__.get(id, None)
                if event is None:
                    # Remove the event from the heap to avoid stale references
                    heapq.heappop(self.__heap__)
                    continue
            else:
                time, priority, id = heapq.heappop(self.__heap__)
                event = self.remove_event(id)
                if event is None:
                    continue
                self.__time__ = time
            return {
                "id": id,
                "time": time,
                "event": event,
            }
        return {
            "id": None,
            "time": None,
            "event": None,
        }

    def get_next_events(self) -> list[dict]:
        """
        Retrieves all events that occur at the same time as the next event.
        This method is used to get all events that occur at the same time as the next event in the queue.
        It removes these events from the queue.

        Returns:

        - list: A list of events that occur at the same time as the next event.
            - If the queue is empty, an empty list is returned.
        """
        events = []
        event = self.get_next_event(peek=True)
        if event["time"] != None:
            self.__time__ = event["time"]
            next_event = event
            while next_event["time"] == self.__time__:
                event = next_event
                self.remove_next_event()
                events.append(event)
                next_event = self.get_next_event(peek=True)
        return events
