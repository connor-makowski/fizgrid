from fizgrid.queue import QueueEvent

class RouteCollision(QueueEvent):
    def __init__(self, agent_1, agent_2):
        self.agent_1 = agent_1
        self.agent_2 = agent_2

    def process(self):
        # Add a RouteEnd (collison=true) event for each agent at this point in time
        pass

class RouteStart(QueueEvent):
    def __init__(self, agent, route_deltas=list[list[int|float]], raise_on_future_collision=False):
        self.agent = agent
        self.route_deltas = route_deltas
        self.raise_on_future_collision = raise_on_future_collision

    def process(self):
        # Cancel out any other future events related to this agent (routes and / or collisions - this cancels collisions for the other agent involved as well)
        # Clear out any route blocks for this agent
        # Given route_deltas Block the grid cells for the agent's shape for the duration that the agent is in each cell
        # Check for collisions with other agents in the grid
            # Add events to the queue for the first collision with each colliding agent
        # Add a RouteEnd event for this agent at the timing of the end of the route
        pass
        

class RouteEnd(QueueEvent):
    def __init__(self, agent, is_result_of_collision=False, raise_on_future_collision=False):
        self.agent = agent
        self.is_result_of_collision = is_result_of_collision
        self.raise_on_future_collision = raise_on_future_collision

    def process(self):
        # Set the agent's position to where they are at this point in time
        # Cancel out any other future events related to this agent (routes and / or collisions - this cancels collisions for the other agent involved as well)
        # Remove the route blocks from the grid cells to keep things clean
        # Block the grid cells for this agent's shape at its current location until the end of the simulation
        # Check for collisions with other ageents in the grid
            # Add events to the queue for the first collision with each colliding agent
        pass