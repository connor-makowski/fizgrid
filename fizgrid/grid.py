import type_enforced
from fizgrid.agent import Agent
from fizgrid.queue import TimeQueue
from fizgrid.events import RouteStart

@type_enforced.Enforcer
class Grid:
    def __init__(self, name:str, x_size:int, y_size:int, max_time:int=1000):
        # Passed Attributes
        self.name = name
        self.x_size = x_size
        self.y_size = y_size
        self.max_time = max_time

        # Calculated Attributes
        self.agents = {}
        self.plans = {}
        self.queue = TimeQueue()
        self.cells = [[{} for _ in range(x_size)] for _ in range(y_size)]


    def __repr__(self):
        return f"Grid({self.name} {self.x_size}x{self.y_size})"
    
    def add_agent(
        self,
        name:str,
        shape:list[list[int|float]],
        x_coord:int|float,
        y_coord:int|float,
    ):
        """
        Adds an agent to the grid.
        This method creates an agent with the specified parameters and adds it to the grid.
        """
        agent = Agent(
            name=name,
            shape=shape,
            x_coord=x_coord,
            y_coord=y_coord,
            grid=self,
        )
        self.agents[agent.id] = agent
        return agent
        

    def get_open_agents(self):
        """
        Returns a list of all agents in the grid that are not currently in a task.
        """
        return [agent for agent in self.agents.values() if agent.__route_end_time__ <= self.queue.time]

        
    def process_next_event(self):
        """
        Processes the next event in the queue.
        This method retrieves the next event from the queue and processes it.
        """
        event = self.queue.get_next_event()
        if event is None:
            return None
        event['event'].process()
        return True

    



    