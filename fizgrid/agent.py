import type_enforced, math


@type_enforced.Enforcer
class Agent:
    def __init__(
            self, 
            id:int, 
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
        self.id = id
        self.name = name
        self.shape = shape
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.grid = grid

    def __repr__(self):
        return f"Agent(id={self.id},name={self.name}"
        

    
    
    


        
    
    

    



