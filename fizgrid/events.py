from fizgrid.queue import QueueEvent

class RouteStart(QueueEvent):
    def __init__(self, agent, route_deltas=list[list[int|float]], raise_on_future_collision=False):
        self.agent = agent
        self.route_deltas = route_deltas
        self.raise_on_future_collision = raise_on_future_collision

    def process(self):
        print("Route Start Process:", self.agent.name, "@T", self.agent.grid.queue.time)
        self.agent.__initialize_route__(self.route_deltas, self.raise_on_future_collision)
        

class RouteEnd(QueueEvent):
    def __init__(self, agent, is_result_of_collision=False, raise_on_future_collision=False):
        self.agent = agent
        self.is_result_of_collision = is_result_of_collision
        self.raise_on_future_collision = raise_on_future_collision

    def process(self):
        print("Route End Process:", self.agent.name,  "@T", self.agent.grid.queue.time, self.is_result_of_collision)
        self.agent.__realize_route__(self.is_result_of_collision, self.raise_on_future_collision)