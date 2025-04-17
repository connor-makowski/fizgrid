import type_enforced
from fizgrid.utils import unique_id

@type_enforced.Enforcer
class Plan:
    def __init__(self, agent, start_time, path):
        """
        Initializes a plan for an agent.

        Args:
            id (int): The ID of the plan.
            agent (Agent): The agent associated with this plan.
            start_time (int|float): The time at which the plan starts.
            path (list[dict[int|float]]): A list of steps in the plan, each step is a dictionary with x_delta, y_delta, and time_delta.
        """
        self.id = unique_id()
        self.agent = agent
        self.start_time = start_time
        self.path = path


@type_enforced.Enforcer
class Agent:
    def __init__(
            self,
            name:str, 
            shape:list[list[int|float]],
            x_coord:int|float, 
            y_coord:int|float,
            grid
        ):
        """
        Initializes an agent with a given shape and location in the grid.

        Args:

            id (int): The ID of the agent.
            name (str): The name of the agent.
            shape (list[list[int|float]]): The shape of the agent as a list of points centered around the shape origin.
                - The shape origin referenced here should be the center of the shape as the shape origin is used to determine how the shape is located on the grid.
                - The shape is a list of points, where each point is a list of two coordinates [x, y] relative to the shape origin.
            x_coord (int|float): The starting x-coordinate of the agent in the grid.
            y_coord (int|float): The starting y-coordinate of the agent in the grid.
            grid (Grid): The grid the agent is in.
        """
        self.id = unique_id()
        self.name = name
        self.shape = shape
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.grid = grid

    def __repr__(self):
        return f"Agent(id={self.id},name={self.name}"
        

    
    
    


        
    
    

    



