import type_enforced
from fizgrid.utils import unique_id, RectangleMoverUtils
from fizgrid.events import RouteStart, RouteEnd

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
        self.history = []

        # Util Attributes
        self.__route_start_time__ = 0
        self.__route_end_time__ = 0
        self.__blocked_grid_cells__ = []
        self.__route_deltas__ = []
        self.__future_event_ids__ = {}

        # Initialize the agent in the grid
        self.__realize_route__(is_result_of_collision=False, raise_on_future_collision=True)

    def __repr__(self):
        return f"Agent(id={self.id},name={self.name}"

    def __initialize_route__(self, route_deltas:list[dict[str, float|int]], raise_on_future_collision:bool=False):
        """
        Sets the route for this agent given a set of route_deltas starting at the current time.

        Determines the cells this agent will block and checks for collisions with other agents.

        Adds events to the queue for the first collision with each colliding agent.

        Args:

            route_deltas(list[dict[str, float|int]]): A list of route deltas to be added to the grid queue.
                - A list of route deltas to be added to the grid queue.
                    - [{'x_shift': x_delta, 'y_shift': y_delta, 'time_shift': time}]
                    - EG; 
                        ```
                        route_deltas = [
                            {'x_shift': -2, 'y_shift': 0, 'time_shift': 10},
                            {'x_shift': 0, 'y_shift': 2, 'time_shift': 10}
                        ]
                        ```
                        - Move left 2 units on the y grid over 10 seconds
                        - Move up 2 units on the y grid over 10 seconds

                    - Note: x_shift and y_shift are the distance moved in the x and y directions respectively. They can be positive or negative.
                    - Note: time_shift is the time it takes to move the distance specified by x_shift and y_shift. It must be positive.

            raise_on_future_collision (bool): Whether to raise an exception if the agent is in a future collision.
        """
        # Raise an exception if the agent is already in a route
        if self.__route_end_time__ > self.grid.queue.time:
                raise Exception(f"Agent {self.name} is already in a route. Cannot set a new route until the current route is finished.")
        
        # Setup util attributes
        self.__clear_blocked_grid_cells__()
        self.__clear_future_events__()

        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.grid.queue.time
        collisions = {}
        total_route_time_shift = sum([delta['time_shift'] for delta in route_deltas])

        # Add a final route delta for with no x or y motion and occuring until the end of the simulation.
        # This allows us to lock in the position of the agent at the end of the route and block the grid cells accordingly.
        route_deltas.append({
            'x_shift': 0,
            'y_shift': 0,
            'time_shift': self.grid.max_time - t_tmp - total_route_time_shift
        })
        
        # Store the route deltas and start time for later use to determine the agent's position at a given time
        self.__route_deltas__ = route_deltas
        self.__route_start_time__ = self.grid.queue.time
        self.__route_end_time__ = min(self.grid.max_time, self.__route_start_time__ + total_route_time_shift)
        
        # For each route delta, calculate the blocks and collisions and add them to the grid
        for delta in route_deltas:
            assert delta['time_shift'] > 0, "Time shift must be positive"
            blocks = RectangleMoverUtils.moving_shape_overlap_intervals(
                x_coord=x_tmp,
                y_coord=y_tmp,
                x_shift = delta['x_shift'],
                y_shift = delta['y_shift'],
                t_start=t_tmp,
                t_end=t_tmp + delta['time_shift'],
                shape=self.shape,
            )
            x_tmp = x_tmp + delta['x_shift']
            y_tmp = y_tmp + delta['y_shift']
            t_tmp = t_tmp + delta['time_shift']
            for (x_cell, y_cell), (t_start, t_end) in blocks.items():
                # Store a unique block_id to allow for removal of the block later
                block_id = unique_id()
                # Get the relevant cell in the grid
                cell = self.grid.cells[y_cell][x_cell]
                # Check for collisions with other agents in the cell
                for (other_t_start, other_t_end, other_agent_id) in cell.values():
                    if t_start < other_t_end and t_end > other_t_start:
                        # Determine the time of the collision and store the most recent collision time with each colliding agent
                        collision_time = max(t_start, other_t_start)
                        previous_collision_time = collisions.get(other_agent_id)
                        if previous_collision_time is None or collision_time < previous_collision_time:
                            collisions[other_agent_id] = collision_time
                # Block the grid cell for the agent
                cell[block_id] = (t_start, t_end, self.id)
                # Store the blocked grid cell for later removal
                self.__blocked_grid_cells__.append((x_cell, y_cell, block_id))
        if raise_on_future_collision and len(collisions) > 0:
            raise Exception(f"Agent {self.name} collides with other agents and this route is set to raise an exception if there is a future collision detected.")
        # Create collision events for the first collision with each colliding agent
        for other_agent_id, collision_time in collisions.items():
            other_agent = self.grid.agents[other_agent_id]
            event_id = self.grid.queue.add_event(
                time=collision_time,
                event=RouteEnd(agent=self, is_result_of_collision=True, raise_on_future_collision=False),
            )
            other_event_id = self.grid.queue.add_event(
                time=collision_time,
                event=RouteEnd(agent=other_agent, is_result_of_collision=True, raise_on_future_collision=False),
            )
            # Store the event_id for each agent involved in the collision
            self.__future_event_ids__[event_id] = other_event_id
            other_agent.__future_event_ids__[other_event_id] = event_id

        if self.__route_end_time__ > self.grid.queue.time:
            # Add a route_end event for this agent at the timing of the end of the route
            event_id = self.grid.queue.add_event(
                time=self.__route_end_time__,
                event=RouteEnd(agent=self, is_result_of_collision=False, raise_on_future_collision=False),
            )
            self.__future_event_ids__[event_id] = None
        return {
            'has_collision': len(collisions) > 0,
        }

    def __clear_blocked_grid_cells__(self):
        """
        Clears the blocked grid cells for this agent.
        """
        for (x_cell, y_cell, block_id) in self.__blocked_grid_cells__:
            cell = self.grid.cells[y_cell][x_cell]
            cell.pop(block_id, None)
        self.__blocked_grid_cells__ = []

    def __clear_future_events__(self):
        """
        Clears the future events for this agent.
        """
        for this_event_id, related_event_id in self.__future_event_ids__.items():
            # If this event is a standard route_end event, it will not have an related event, so it will be removed with the remove_event call
            # remove_event might be called on an event that has already been taken out of the queue (processed or removed). This is ok.
            if related_event_id == None:
                self.grid.queue.remove_event(this_event_id)
            # If this event is a collision event, it will have an associated event
            else:
                event_obj = self.grid.queue.remove_event(this_event_id)
                # If the event_obj is None, then this event has already been processed or removed
                # If it returns an event_obj, then it has not yet been processed and the related event should be removed as well
                if event_obj != None:
                    self.grid.queue.remove_event(related_event_id)
        self.__future_event_ids__ = {}

    def __realize_route__(self, is_result_of_collision:bool=False, raise_on_future_collision:bool=False):
        """
        Realize the route for this agent at the current time.

        Args:

            is_result_of_collision (bool): Whether this route end is the result of a collision.
                - If True, the route end is the result of a collision and the agent should not be allowed to start a new route until the collision is resolved.
                - If False, the route end is not the result of a collision and the agent should be allowed to start a new route.
            raise_on_future_collision (bool): Whether to raise an exception if the agent is in a future collision.
                - Raises an exception if this event causes a future collision with another agent.
        """
        # Determeine Realized Route and update the agent's position / history
        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.__route_start_time__
        current_time = self.grid.queue.time
        for delta in self.__route_deltas__:
            # End the route realization if the time is greater than the current time
            if t_tmp >= current_time:
                break
            # Get partial shifts if the time is less than the time shift
            elif t_tmp + delta['time_shift'] > current_time:
                x_shift = (current_time - t_tmp) * delta['x_shift'] / delta['time_shift']
                y_shift = (current_time - t_tmp) * delta['y_shift'] / delta['time_shift']
                time_shift = current_time - t_tmp
            # Otherwise, use the full shifts
            else:
                x_shift = delta['x_shift']
                y_shift = delta['y_shift']
                time_shift = delta['time_shift']

            x_tmp += x_shift
            y_tmp += y_shift
            t_tmp += time_shift

            # TODO: Need to figure out how to handle some edge cases here
            self.history.append({
                'x_shift': x_shift,
                'y_shift': y_shift,
                'time_shift': time_shift,
            })

        # Set the agent's position to where they are at this point in time
        self.x_coord = x_tmp
        self.y_coord = y_tmp
        # Set the agent's route end time to the current time
        self.__route_end_time__ = current_time

        # Stop the agent at their current location and update the grid for their expected future
        return self.__initialize_route__(route_deltas=[], raise_on_future_collision=raise_on_future_collision)

    def add_route(
            self,
            route_deltas:list[dict[str, float|int]],
            time:int|float|None=None,
            raise_on_future_collision:bool=False,
        ):
        """
        Adds a route to the grid for this agent.

        Args:

            route_deltas (list[dict[str, float|int]]): A list of route deltas to be added to the grid queue.
                - A list of route deltas to be added to the grid queue.
                    - [{'x_shift': x_delta, 'y_shift': y_delta, 'time_shift': time}]
                    - EG; 
                        ```
                        route_deltas = [
                            {'x_shift': -2, 'y_shift': 0, 'time_shift': 10},
                            {'x_shift': 0, 'y_shift': 2, 'time_shift': 10}
                        ]
                        ```
                        - Move left 2 units on the y grid over 10 seconds
                        - Move up 2 units on the y grid over 10 seconds

                    - Note: x_shift and y_shift are the distance moved in the x and y directions respectively. They can be positive or negative.
                    - Note: time_shift is the time it takes to move the distance specified by x_shift and y_shift. It must be positive.

            time (int|float|None): The time at which to start the route. If None, the current time is used.
            raise_on_future_collision (bool): Whether to raise an exception if the agent is in a future collision.
        """
        if time is None:
            time = self.grid.queue.time        
        # Add the event to the queue
        self.grid.queue.add_event(
            time=time,
            event=RouteStart(
                agent=self,
                route_deltas=route_deltas,
                raise_on_future_collision=raise_on_future_collision,
            )
        )

    
    
    


        
    
    

    



