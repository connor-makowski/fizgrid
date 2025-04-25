import type_enforced
from fizgrid.utils import unique_id, RectangleMoverUtils, Thunk

@type_enforced.Enforcer
class Entity:
    def __init__(
            self,
            name:str, 
            shape:list[list[int|float]],
            x_coord:int|float, 
            y_coord:int|float,
        ):
        """
        Initializes an entity with a given shape and location in the grid.

        Args:

            id (int): The ID of the entity.
            name (str): The name of the entity.
            shape (list[list[int|float]]): The shape of the entity as a list of points centered around the shape origin.
                - The shape origin referenced here should be the center of the shape as the shape origin is used to determine how the shape is located on the grid.
                - The shape is a list of points, where each point is a list of two coordinates [x, y] relative to the shape origin.
            x_coord (int|float): The starting x-coordinate of the entity in the grid.
            y_coord (int|float): The starting y-coordinate of the entity in the grid.
            grid (Grid): The grid the entity is in.
        """
        self.id = unique_id()
        self.name = name
        self.shape = shape
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.history = []

        # Util Attributes
        self.__grid__=None
        self.__route_start_time__ = 0
        self.__route_end_time__ = 0
        self.__blocked_grid_cells__ = []
        self.__route_deltas__ = []
        self.__future_event_ids__ = {}

    def __repr__(self):
        return f"Entity({self.name})"
    
    def assign_to_grid(self, grid):
        """
        Assigns the grid to this entity.
        """
        self.__grid__ = grid
        self.realize_route(is_result_of_collision=False, raise_on_future_collision=True)

    def __clear_blocked_grid_cells__(self):
        """
        Clears the blocked grid cells for this entity.
        """
        for (x_cell, y_cell, block_id) in self.__blocked_grid_cells__:
            cell = self.__grid__.cells[y_cell][x_cell]
            cell.pop(block_id, None)
        self.__blocked_grid_cells__ = []

    def __clear_future_events__(self):
        """
        Clears the future events for this entity.
        """
        for this_event_id, related_event_id in self.__future_event_ids__.items():
            # If this event is a standard route_end event, it will not have an related event, so it will be removed with the remove_event call
            # remove_event might be called on an event that has already been taken out of the queue (processed or removed). This is ok.
            if related_event_id == None:
                self.__grid__.queue.remove_event(this_event_id)
            # If this event is a collision event, it will have an associated event
            else:
                event_obj = self.__grid__.queue.remove_event(this_event_id)
                # If the event_obj is None, then this event has already been processed or removed
                # If it returns an event_obj, then it has not yet been processed and the related event should be removed as well
                if event_obj != None:
                    self.__grid__.queue.remove_event(related_event_id)
        self.__future_event_ids__ = {}

    def get_in_route(self):
        """
        Returns whether this entity is in a route.
        """
        return self.__route_end_time__ > self.__grid__.queue.time

    def plan_route(self, route_deltas:list[dict[str, float|int]], raise_on_future_collision:bool=False):
        """
        Sets the route for this entity given a set of route_deltas starting at the current time.

        Determines the cells this entity will block and checks for collisions with other entities.

        Adds events to the queue for the first collision with each colliding entity.

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

            raise_on_future_collision (bool): Whether to raise an exception if the entity is in a future collision.
        """
        # Raise an exception if the entity is already in a route
        if self.get_in_route():
                raise Exception(f"entity {self.name} is already in a route. Cannot set a new route until the current route is finished.")
        
        # Setup util attributes
        self.__clear_blocked_grid_cells__()
        self.__clear_future_events__()

        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.__grid__.queue.time
        collisions = {}
        total_route_time_shift = sum([delta['time_shift'] for delta in route_deltas])

        # Add a final route delta for with no x or y motion and occuring until the end of the simulation.
        # This allows us to lock in the position of the entity at the end of the route and block the grid cells accordingly.
        route_deltas.append({
            'x_shift': 0,
            'y_shift': 0,
            'time_shift': self.__grid__.max_time - t_tmp - total_route_time_shift
        })
        
        # Store the route deltas and start time for later use to determine the entity's position at a given time
        self.__route_deltas__ = route_deltas
        self.__route_start_time__ = self.__grid__.queue.time
        self.__route_end_time__ = min(self.__grid__.max_time, self.__route_start_time__ + total_route_time_shift)
        
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
                cell = self.__grid__.cells[y_cell][x_cell]
                # Check for collisions with other entities in the cell
                for (other_t_start, other_t_end, other_entity_id) in cell.values():
                    if t_start < other_t_end and t_end > other_t_start:
                        # Determine the time of the collision and store the most recent collision time with each colliding entity
                        collision_time = max(t_start, other_t_start)
                        previous_collision_time = collisions.get(other_entity_id)
                        if previous_collision_time is None or collision_time < previous_collision_time:
                            collisions[other_entity_id] = collision_time
                # Block the grid cell for the entity
                cell[block_id] = (t_start, t_end, self.id)
                # Store the blocked grid cell for later removal
                self.__blocked_grid_cells__.append((x_cell, y_cell, block_id))
        if raise_on_future_collision and len(collisions) > 0:
            raise Exception(f"entity {self.name} collides with other entities and this route is set to raise an exception if there is a future collision detected.")
        # Create collision events for the first collision with each colliding entity
        for other_entity_id, collision_time in collisions.items():
            other_entity = self.__grid__.entities[other_entity_id]
            event_id = self.__grid__.queue.add_event(
                time=collision_time,
                object=self,
                method="realize_route",
                kwargs = {
                    'is_result_of_collision': True,
                },
            )
            other_event_id = self.__grid__.queue.add_event(
                time=collision_time,
                object=other_entity,
                method="realize_route",
                kwargs = {
                    'is_result_of_collision': True,
                }
            )
            # Store the event_id for each entity involved in the collision
            self.__future_event_ids__[event_id] = other_event_id
            other_entity.__future_event_ids__[other_event_id] = event_id

        if self.__route_end_time__ > self.__grid__.queue.time:
            # Add a route_end event for this entity at the timing of the end of the route
            event_id = self.__grid__.queue.add_event(
                time=self.__route_end_time__,
                object=self,
                method="realize_route",
                kwargs={
                    'is_result_of_collision': False,
                },
            )
            self.__future_event_ids__[event_id] = None
        return {
            'has_collision': len(collisions) > 0,
        }

    def realize_route(self, is_result_of_collision:bool=False, raise_on_future_collision:bool=False):
        """
        Realize the route for this entity at the current time.

        Args:

            is_result_of_collision (bool): Whether this route end is the result of a collision.
                - If True, the route end is the result of a collision and the entity should not be allowed to start a new route until the collision is resolved.
                - If False, the route end is not the result of a collision and the entity should be allowed to start a new route.
            raise_on_future_collision (bool): Whether to raise an exception if the entity is in a future collision.
                - Raises an exception if this event causes a future collision with another entity.
        """
        # Determeine Realized Route and update the entity's position / history
        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.__route_start_time__
        current_time = self.__grid__.queue.time
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

        # Set the entity's position to where they are at this point in time
        self.x_coord = x_tmp
        self.y_coord = y_tmp
        # Set the entity's route end time to the current time
        self.__route_end_time__ = current_time

        # Stop the entity at their current location and update the grid for their expected future
        return self.plan_route(route_deltas=[], raise_on_future_collision=raise_on_future_collision)

    def add_route(
            self,
            route_deltas:list[dict[str, float|int]],
            time:int|float|None=None,
            raise_on_future_collision:bool=False,
        ):
        """
        Adds a route to the grid for this entity.

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
            raise_on_future_collision (bool): Whether to raise an exception if the entity is in a future collision.
        """
        if self.__grid__ is None:
            raise Exception("Entity is not assigned to a grid. Cannot add a route.")
        if time is None:
            time = self.__grid__.queue.time        
        # Add the event to the queue
        self.__grid__.queue.add_event(
            time=time,
            object=self,
            method="plan_route",
            kwargs={
                'route_deltas': route_deltas,
                'raise_on_future_collision': raise_on_future_collision,
            },
        )

    
class StaticEntity(Entity):
    def realize_route(self, is_result_of_collision:bool=False, raise_on_future_collision:bool=False):
        """
        Realize the route for this entity at the current time.

        Args:

            is_result_of_collision (bool): Whether this route end is the result of a collision.
                - If True, the route end is the result of a collision and the entity should not be allowed to start a new route until the collision is resolved.
                - If False, the route end is not the result of a collision and the entity should be allowed to start a new route.
            raise_on_future_collision (bool): Whether to raise an exception if the entity is in a future collision.
                - Raises an exception if this event causes a future collision with another entity.
        """
        if is_result_of_collision:
            return 
        self.__route_end_time__ = self.__grid__.queue.time
        return self.plan_route(route_deltas=[], raise_on_future_collision=raise_on_future_collision)


