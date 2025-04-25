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
        entity.assign_to_grid(self)
        return entity
        

    def get_open_entities(self):
        """
        Returns a list of all entities in the grid that are not currently in a task.
        """
        return [entity for entity in self.entities.values() if entity.__route_end_time__ <= self.queue.time]

        
    def resolve_next_state(self):
        """
        Resolves the next state of the grid.
        This method processes the next event in the queue and updates the grid accordingly.
        """
        events = self.queue.get_next_events()
        for event in events:
            if event['object'] is None:
                continue
            object = event['object']
            getattr(object, event['method'])(**event['kwargs'])
        return events
    
    

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
