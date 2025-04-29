import type_enforced
from type_enforced.utils import WithSubclasses
from fizgrid.entities import Entity, StaticEntity
from fizgrid.queue import TimeQueue

@type_enforced.Enforcer
class Grid:
    def __init__(self, name:str, x_size:int, y_size:int, max_time:int=1000):
        # Passed Attributes
        self.name = name
        self.x_size = x_size
        self.y_size = y_size
        self.max_time = max_time

        # Calculated Attributes
        self.entities = {}
        self.plans = {}
        self.queue = TimeQueue()
        self.cells = [[{} for _ in range(x_size)] for _ in range(y_size)]

    def __repr__(self):
        return f"Grid({self.name} {self.x_size}x{self.y_size})"
    
    def add_entity(
        self,
        entity,
    ):
        """
        Adds an entity to the grid.
        This method creates an entity with the specified parameters and adds it to the grid.
        """
        self.entities[entity.id] = entity
        entity.__assign_to_grid__(self)
        return entity
    
    def add_event(self, time:int|float, object, method:str, kwargs:dict=dict()):
        """
        Adds an event to the queue.
        This method schedules an event for a specific object at a specific time.

        Args:

            time (int|float): The time at which the event should occur.
            object: The object on which the event will occur.
            method (str): The name of the method to be called on the object.
            kwargs (dict): The keyword arguments to be passed to the method.
        """
        return self.queue.add_event(
            time = time, 
            event = {
                'object':object, 
                'method':method, 
                'kwargs':kwargs
            }
        )
            
    def resolve_next_state(self):
        """
        Resolves the next state of the grid.
        This method processes the next event in the queue and updates the grid accordingly.
        """
        event_items = self.queue.get_next_events()
        for event_item in event_items:
            event = event_item.get('event')
            object = event.get('object')
            method = event.get('method')
            kwargs = event.get('kwargs')
            if object is None:
                continue
            getattr(object, method)(**kwargs)
        return event_items

    def add_exterior_walls(self):
        """
        Adds exterior walls to the grid.
        This method creates walls around the grid to prevent entities from moving outside the grid.
        """
        self.add_entity(StaticEntity(
            name="Left Wall",
            shape=[[0, 0], [0, self.y_size], [1,self.y_size], [1,0]],
            x_coord=0,
            y_coord=0,
        ))

        self.add_entity(StaticEntity(
            name="Right Wall",
            shape=[[0, 0], [0, self.y_size], [-1,self.y_size], [-1,0]],
            x_coord=self.x_size,
            y_coord=0,
        ))

        self.add_entity(StaticEntity(
            name="Top Wall",
            shape=[[0, 0], [self.x_size-2, 0], [self.x_size-2, -1], [0, -1]],
            x_coord=1,
            y_coord=self.y_size,
        ))

        self.add_entity(StaticEntity(
            name="Bottom Wall",
            shape=[[0, 0], [self.x_size-2, 0], [self.x_size-2, 1], [0,1]],
            x_coord=1,
            y_coord=0,
        ))
