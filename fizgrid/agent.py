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

        # Util Attributes
        self.__in_route__ = False
        self.__blocked_grid_cells__ = []
        self.__route_deltas__ = []
        self.__route_start_time__ = 0
        self.__future_collision_event_ids__ = []
        self.__realized_delta_history__ = []

        # Place the agent on the grid for cell blocking purposes
        self.grid.queue.add_event(time=0, event=RouteEnd(agent=self, raise_on_future_collision=True))

    def __repr__(self):
        return f"Agent(id={self.id},name={self.name}"

    def __route__(self, route_deltas:list[dict[str, float|int]], is_end:bool=False):
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
        """
        if self.__in_route__:
            raise Exception(f"Agent {self.name} is already in a route. Cannot set a new route until the current route is finished.")
        
        # Setup util attributes
        self.__in_route__ = not is_end
        self.__route_deltas__ = route_deltas
        self.__route_start_time__ = self.grid.queue.time
        self.__clear_blocked_grid_cells__()
        self.__clear_future_collision_events__()

        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.grid.queue.time
        collisions = {}

        # Add a final route delta for with no x or y motion and occuring until the end of the simulation.
        route_deltas.append({
            'x_shift': 0,
            'y_shift': 0,
            'time_shift': self.grid.max_time - t_tmp - sum([delta['time_shift'] for delta in route_deltas]),
        })
        
        # Store the route deltas and start time for later use to determine the agent's position at a given time
        self.__route_deltas__ = route_deltas
        self.__route_start_time__ = self.grid.queue.time
        
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
        # Create collision events for the first collision with each colliding agent
        for other_agent_id, collision_time in collisions.items():
            other_agent = self.grid.agents[other_agent_id]
            event_id = self.grid.queue.add_event(
                time=collision_time,
                event=RouteEnd(agent=self, is_result_of_collision=True, raise_on_future_collision=True),
            )
            other_event_id = self.grid.queue.add_event(
                time=collision_time,
                event=RouteEnd(agent=other_agent, is_result_of_collision=True, raise_on_future_collision=True),
            )
            # Store the event_id for each agent involved in the collision
            self.__future_collision_event_ids__ += [event_id, other_event_id]
            other_agent.__future_collision_event_ids__ += [event_id, other_event_id]
        return {
            'has_collisions': len(collisions) > 0,
        }

    def __clear_blocked_grid_cells__(self):
        """
        Clears the blocked grid cells for this agent.
        """
        for (x_cell, y_cell, block_id) in self.__blocked_grid_cells__:
            cell = self.grid.cells[y_cell][x_cell]
            cell.pop(block_id, None)
        self.__blocked_grid_cells__ = []

    def __clear_future_collision_events__(self):
        """
        Clears the future collision events for this agent.
        """
        # TODO: Do not remove collisions at the same time as now to avoid removing an event for another agent before ic can be processed
        for event_id in self.__future_collision_event_ids__:
            self.grid.queue.remove_event(event_id)
        self.__future_collision_event_ids__ = []

    def __end_route__(self):
        """
        End the route for this agent.

        Realize the route for this agent at the current time.

        Starts a new route (that is not blocking) at the current time to block the grid cells for this agent's shape at its current location until the end of the simulation.
        This can be interrupted when a new route is created.
        """
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
                is_end = True
            # Otherwise, use the full shifts
            else:
                x_shift = delta['x_shift']
                y_shift = delta['y_shift']
                time_shift = delta['time_shift']

            x_tmp += x_shift
            y_tmp += y_shift
            t_tmp += time_shift

            # TODO: Need to figure out how to handle some edge cases here
            self.__realized_delta_history__.append({
                'x_shift': x_shift,
                'y_shift': y_shift,
                'time_shift': time_shift,
            })

        # Set the agent's position to where they are at this point in time
        self.x_coord = x_tmp
        self.y_coord = y_tmp

        # Start a new route that 
        return self.__route__(route_deltas=[], is_end=True)

        

    
    
    


        
    
    

    



