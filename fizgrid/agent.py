import type_enforced, math
from fizgrid.grid import Grid


@type_enforced.Enforcer
class Agent:
    def __init__(
            self, 
            id:int, 
            name:str, 
            shape:list[list[int|float]],
            heading:float|int,
            grid:Grid,
            x:int|float, 
            y:int|float,
        ):
        """
        Initializes an agent with a given shape, heading, and location in the grid.

        Args:

            id (int): The ID of the agent.
            name (str): The name of the agent.
            shape (list[list[int|float]]): The shape of the agent as a list of points centered around the shape origin.
                - The shape origin referenced here should be the center of the shape as the shape origin is used to determine how the shape is located on the grid.
                - The shape is a list of points, where each point is a list of two coordinates [x, y] relative to the shape origin.
            heading (float|int): The heading of the agent in degrees. (0 degrees is to the right, 90 degrees is up).
                - Note: This rotates the provided shape around the shape origin
            grid (Grid): The grid in which the agent is located.
            x (int|float): The x-coordinate of the agent in the grid.
            y (int|float): The y-coordinate of the agent in the grid.
        """
        self.id = id
        self.name = name
        self.root_shape = shape
        self.set_heading(heading) # Sets self.shape and self.heading
        self.grid = grid
        self.x = x
        self.y = y

        self.set_heading(heading)

    def __repr__(self):
        return f"Agent(id={self.id},name={self.name},grid={self.grid},x={self.x},y={self.y})"
    
    def set_location(self, x:int, y:int):
        """
        Sets the location of the agent in the grid.
        """
        self.x = x
        self.y = y
        
    def set_heading(self, heading:float|int):
        """
        Rotates the agent to a given heading in radians.
        
        The heading is the angle in degrees from the positive x-axis.
        The rotation is done around the origin (0,0) and applied to the root shape.
        The shape is then updated to reflect the new heading.

        Args:

            heading (float|int): The heading in degrees to rotate the agent.

        Returns:
            None
        """
        self.heading = heading
        heading_radians = math.radians(heading)
        self.shape = [[
            round(math.cos(heading_radians) * point[0] - math.sin(heading_radians) * point[1], 2),
            round(math.sin(heading_radians) * point[0] + math.cos(heading_radians) * point[1], 2)
        ] for point in self.root_shape]
    
    

    



