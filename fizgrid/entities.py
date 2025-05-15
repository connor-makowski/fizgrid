import type_enforced
from fizgrid.utils import unique_id, ShapeMoverUtils, Shape


@type_enforced.Enforcer(enabled=True)
class Entity:
    def __init__(
        self,
        name: str,
        shape: list[list[int | float]],
        x_coord: int | float,
        y_coord: int | float,
        auto_rotate: bool = False,
        location_precision: int = 4,
    ):
        """
        Initializes an entity with a given shape and location in the grid.

        Args:

        - id (int): The ID of the entity.
        - name (str): The name of the entity.
        - shape (list[list[int|float]]): The shape of the entity as a list of points centered around the shape origin.
            - The shape origin referenced here should be the center of the shape as the shape origin is used to determine how the shape is located on the grid.
            - The shape is a list of points, where each point is a list of two coordinates [x, y] relative to the shape origin.
        - x_coord (int|float): The starting x-coordinate of the entity in the grid.
        - y_coord (int|float): The starting y-coordinate of the entity in the grid.
        - auto_rotate (bool): Whether to automatically rotate the shape based on the direction of movement.
            - Note: The default assumption is that the shape is facing right (0 radians).
        - location_precision (int): The precision of the location coordinates. This is used to round the coordinates to a specific number of decimal places.
        """
        self.id = unique_id()
        """The ID of the entity."""
        self.name = name
        """The name of the entity."""
        self.shape = shape
        """The shape of the entity as a list of points centered around the shape the current (x, y) coordinates."""
        self.x_coord = x_coord
        """
        The x-coordinate of the entity in the grid. This is the last known location of the entity.
        
        - Note: This is only updated when events realize the route. This means that a route in progress would not have the correct
            location until the route is realized (either completed or interrupted by a cancellation or collision).
        """
        self.y_coord = y_coord
        """
        The y-coordinate of the entity in the grid. This is the last known location of the entity.
        
        - Note: This is only updated when events realize the route. This means that a route in progress would not have the correct
            location until the route is realized (either completed or interrupted by a cancellation or collision).
        """
        self.history = []
        """
        The history of the entity's location and collision status. 
        This is a list of dictionaries containing the x, y, t, and c values.

        - x (int|float): The x-coordinate of the entity in the grid.
        - y (int|float): The y-coordinate of the entity in the grid.
        - t (int|float): The time at which the entity was at this location.
        - c (bool): Whether the entity was in a collision at this time.

        - Note: This is only updated when events realize the route. This means that a route in progress would not have history until the
            route is realized (either completed or interrupted by a cancellation or collision).
        """

        # Util Attributes
        self.__grid__ = None
        self.__on_grid__ = False
        self.__route_start_time__ = None
        self.__route_end_time__ = 0
        self.__blocked_grid_cells__ = []
        self.__planned_waypoints__ = []
        self.__future_event_ids__ = {}
        self.__shape_current__ = shape
        self.__auto_rotate__ = auto_rotate
        self.__location_precision__ = location_precision

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __assoc_grid__(self, grid) -> None:
        """
        Associate the grid to this entity.
        Creates a reference in both the grid and the entity to allow easy access from both directions.

        Args:

        - grid (Grid): The grid to assign to this entity.
        """
        if self.__grid__ is not None:
            raise Exception(
                f"Entity {self.name} is already associated with a grid. Cannot associate with a new grid."
            )
        self.__grid__ = grid

    def __place_on_grid__(self) -> None:
        """
        Place this entity on the grid and claim the grid cells it will block.

        This allows the entity to take up space and move around the grid.

        Args:

        - grid (Grid): The grid to assign to this entity.
        """
        if self.__grid__ is None:
            raise Exception(
                f"Entity {self.name} is not associated with a grid. Cannot place on grid."
            )
        self.__on_grid__ = True
        self.__route_start_time__ = self.get_time()
        self.history.append(
            {
                "x": self.x_coord,
                "y": self.y_coord,
                "t": self.get_time(),
                "c": False,
            }
        )
        self.__realize_route__(
            is_result_of_collision=False,
            raise_on_future_collision=True,
            is_result_of_dissoc_grid=False,
        )

    def __dissoc_grid__(self) -> None:
        """
        Dissociate the grid from this entity.
        This method removes the entity from the grid and clears any blocked grid cells and future events.
        """
        if self.__grid__ is None:
            raise Exception(
                f"Entity {self.name} is not associated with a grid. Cannot dissociate from grid."
            )
        if self.__on_grid__:
            self.__realize_route__(
                is_result_of_collision=False,
                raise_on_future_collision=False,
                is_result_of_dissoc_grid=True,
            )
        # Clear the blocked grid cells and future events
        self.__clear_blocked_grid_cells__()
        self.__clear_future_events__()
        self.__route_start_time__ = None
        self.__grid__ = None
        self.__on_grid__ = False

    def __clear_blocked_grid_cells__(self) -> None:
        """
        Clears the blocked grid cells for this entity.
        """
        for x_cell, y_cell, block_id in self.__blocked_grid_cells__:
            cell = self.__grid__.__cells__[y_cell][x_cell]
            cell.pop(block_id, None)
        self.__blocked_grid_cells__ = []

    def __clear_future_events__(self) -> None:
        """
        Clears the future events for this entity.
        """
        for (
            this_event_id,
            related_event_id,
        ) in self.__future_event_ids__.items():
            # Remove the event from the queue
            event_obj = self.__grid__.__queue__.remove_event(this_event_id)
            # If this event is a standard route_end event, it will not have an related event, so we can be done here
            # If the event_obj is None, it has already been processed or removed so we can skip any further processing
            # If this event is a collision event, it will have an associated event and should be removed too
            if related_event_id != None and event_obj != None:
                self.__grid__.__queue__.remove_event(related_event_id)
        self.__future_event_ids__ = {}

    def __waypoint_check__(self, waypoints) -> None:
        """
        Checks the waypoints for validity.
        Raises an exception if the waypoints are not valid.

        Args:

        - waypoints (list[tuple[int|float,int|float,int|float]]): A list of waypoints to be added to the grid queue.
        """
        for waypoint in waypoints:
            if len(waypoint) != 3:
                raise Exception(
                    f"Waypoint must be a tuple of (x_coord, y_coord, time_shift). Waypoint: {waypoint}"
                )
            if waypoint[0] < 0 or waypoint[1] < 0 or waypoint[2] < 0:
                raise Exception(
                    f"Waypoint coordinates and times must be positive. Waypoint: {waypoint}"
                )
            if (
                waypoint[0] > self.__grid__.__x_size__
                or waypoint[1] > self.__grid__.__y_size__
            ):
                raise Exception(
                    f"Waypoint coordinates must be within the grid. Waypoint: {waypoint}"
                )

    def __plan_route__(
        self,
        waypoints: list[
            tuple[int | float, int | float, int | float, int | float]
        ],
        raise_on_future_collision: bool = False,
    ) -> dict:
        """
        Sets the route for this entity given a set of waypoints starting at the current time.
        Determines the cells this entity will block and at which times it will block them.
        Checks for collisions with other entities.
        Adds events to the queue for the first collision with each colliding entity.
          - Note: Not all events will occur, and future events will be cleared when the first event occurs.

        Args:

        - waypoints (list[tuple[int|float,int|float,int|float]]): A list of waypoints to be added to the grid queue.
            - A list of tuples where each tuple is (x_coord, y_coord, time_shift).
            - EG:
                ```
                waypoints = [
                    (5, 3, 10),
                    (3, 5, 10)
                ]
                ```
                - Move to (5, 3) over 10 seconds
                - Move to (3, 5) over 10 seconds
            - Note: x_coord and y_coord are the coordinates of the waypoint. They must both be positive.
            - Note: time_shift is the time it takes to move to the waypoint. It must be positive.
            - Optionally, you can use a 4th element to specify the orientation of the shape.
                - This orientation is always relative to the original shape
                - This is in radians where 0 is facing right (equivalent to the initial shape orientation) and pi is facing left.
                - Note: The last used orientation is used until it is changed again (or auto_rotate is set to True).
            - Note: x_coord and y_coord are the coordinates of the waypoint. They must both be positive.
            - Note: time_shift is the time it takes to move to the waypoint. It must be positive.
        - raise_on_future_collision (bool): Whether to raise an exception if the entity has any future plans that result in a collision.
            - Note: This will raise an exception even if the future collision would not happen due to another event occurring first.
            - Note: This is mostly used when initially placing entities on the grid to ensure they are not placed in a collision.

        Returns:

        - dict: A dictionary containing the following keys:
            - has_collision (bool): Whether the route has a collision with another entity.
        """
        if not self.__on_grid__:
            raise Exception(
                "Entity is not on this grid yet, but is attempting to plan a route. Either it has not been assigned to this grid, or the time it will be placed on the grid is in the future."
            )
        # Raise an exception if the entity is already in a route
        if not self.is_available():
            raise Exception(
                f"entity {self.name} is not available for a new route. Cannot set a new route until the current route is finished."
            )

        # Check for valid waypoints
        self.__waypoint_check__(waypoints)

        # Setup util attributes
        self.__clear_blocked_grid_cells__()
        self.__clear_future_events__()

        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.get_time()

        collisions = {}
        total_route_time_shift = sum([waypoint[2] for waypoint in waypoints])

        # Add a final waypoint occuring until the end of the simulation.
        # This allows us to lock in the position of the entity at the end of the route and block the grid cells accordingly.
        if len(waypoints) > 0:
            waypoints.append(
                (
                    waypoints[-1][0],
                    waypoints[-1][1],
                    self.__grid__.__max_time__ - t_tmp - total_route_time_shift,
                )
            )
        else:
            waypoints.append(
                (
                    self.x_coord,
                    self.y_coord,
                    self.__grid__.__max_time__ - t_tmp - total_route_time_shift,
                )
            )

        # Store the route waypoints and start time for later use to determine the entity's position at a given time
        self.__planned_waypoints__ = waypoints
        self.__route_start_time__ = self.get_time()
        self.__route_end_time__ = min(
            self.__grid__.__max_time__,
            self.__route_start_time__ + total_route_time_shift,
        )

        # For each route waypoint, calculate the blocks and collisions and add them to the grid
        for waypoint in waypoints:
            x_shift = waypoint[0] - x_tmp
            y_shift = waypoint[1] - y_tmp
            if len(waypoint) == 4:
                orientation = waypoint[3]
                self.__shape_current__ = Shape.rotate(
                    radians=orientation, shape=self.shape
                )
            elif self.__auto_rotate__:
                if x_shift != 0 or y_shift != 0:
                    self.__shape_current__ = Shape.get_rotated_shape(
                        shape=self.shape, x_shift=x_shift, y_shift=y_shift
                    )
            blocks = ShapeMoverUtils.moving_shape_overlap_intervals(
                x_coord=x_tmp,
                y_coord=y_tmp,
                x_shift=x_shift,
                y_shift=y_shift,
                t_start=t_tmp,
                t_end=t_tmp + waypoint[2],
                shape=self.__shape_current__,
            )
            x_tmp = waypoint[0]
            y_tmp = waypoint[1]
            t_tmp = t_tmp + waypoint[2]
            for (x_cell, y_cell), (t_start, t_end) in blocks.items():
                # Check if the cell is within the grid bounds
                if (
                    x_cell < 0
                    or y_cell < 0
                    or x_cell >= self.__grid__.__x_size__
                    or y_cell >= self.__grid__.__y_size__
                ):
                    # Note: Shape coords outside of the grid raise an exception, but this this would indicate that the shape may have an overlap over the edge.
                    # Note: If there are exterior walls, no exception here is necessary
                    # TODO: Determine if this should be an exception or just a warning
                    # print(f"Warning: Entity {self.name} is outside of the grid bounds is outside of the grid bounds based on its shape.")
                    continue
                # Store a unique block_id to allow for removal of the block later
                block_id = unique_id()
                # Get the relevant cell in the grid
                cell = self.__grid__.__cells__[y_cell][x_cell]
                # Check for collisions with other entities in the cell
                for (
                    other_t_start,
                    other_t_end,
                    other_entity_id,
                ) in cell.values():
                    if t_start < other_t_end and t_end > other_t_start:
                        # Determine the time of the collision and store the most recent collision time with each colliding entity
                        collision_time = max(t_start, other_t_start)
                        previous_collision_time = collisions.get(
                            other_entity_id
                        )
                        if (
                            previous_collision_time is None
                            or collision_time < previous_collision_time
                        ):
                            collisions[other_entity_id] = collision_time
                # Block the grid cell for the entity
                cell[block_id] = (t_start, t_end, self.id)
                # Store the blocked grid cell for later removal
                self.__blocked_grid_cells__.append((x_cell, y_cell, block_id))
        if raise_on_future_collision and len(collisions) > 0:
            raise Exception(
                f"{self.__repr__()} collides with other entities now or in the future. "
            )
        # Create collision events for the first collision with each colliding entity
        for other_entity_id, collision_time in collisions.items():
            other_entity = self.__grid__.__entities__[other_entity_id]
            event_id = self.__grid__.add_event(
                time=collision_time,
                object=self,
                method="__realize_route__",
                kwargs={
                    "is_result_of_collision": True,
                },
                priority=3,
            )
            other_event_id = self.__grid__.add_event(
                time=collision_time,
                object=other_entity,
                method="__realize_route__",
                kwargs={
                    "is_result_of_collision": True,
                },
                priority=3,
            )
            # Store the event_id for each entity involved in the collision
            self.__future_event_ids__[event_id] = other_event_id
            other_entity.__future_event_ids__[other_event_id] = event_id

        if self.__route_end_time__ > self.get_time():
            # Add a route_end event for this entity at the timing of the end of the route
            event_id = self.__grid__.add_event(
                time=self.__route_end_time__,
                object=self,
                method="__realize_route__",
                kwargs={
                    "is_result_of_collision": False,
                },
                priority=2,
            )
            self.__future_event_ids__[event_id] = None
        return {
            "has_collision": len(collisions) > 0,
        }

    def __realize_route__(
        self,
        is_result_of_collision: bool = False,
        raise_on_future_collision: bool = False,
        is_result_of_dissoc_grid: bool = False,
    ) -> dict:
        """
        Realize the route for this entity at the current time.

        Args:

        - is_result_of_collision (bool): Whether this route end is the result of a collision.
        - raise_on_future_collision (bool): Whether to raise an exception if the entity is in a future collision.
            - Raises an exception if this event causes a future collision with another entity.
        - is_result_of_dissoc_grid (bool): Whether the entity will be removed from the grid after this event.

        Returns:

        - dict: A dictionary containing the following keys:
            - has_collision (bool): Whether the route has a collision with another entity.
        """
        # Determeine Realized Route and update the entity's position / history
        x_tmp = self.x_coord
        y_tmp = self.y_coord
        t_tmp = self.__route_start_time__
        current_time = self.get_time()
        for waypoint in self.__planned_waypoints__:
            # End the route realization if the time is greater than the current time
            if t_tmp >= current_time:
                if t_tmp > current_time:
                    # TODO: Remove this
                    print("This should never happen.")
                break
            # Get partial location if interrupted by the current time
            elif t_tmp + waypoint[2] > current_time:
                pct_complete = (current_time - t_tmp) / waypoint[2]
                x_tmp = (waypoint[0] - x_tmp) * pct_complete + x_tmp
                y_tmp = (waypoint[1] - y_tmp) * pct_complete + y_tmp
                t_tmp = current_time
            # Otherwise, update the tmp location
            else:
                x_tmp = waypoint[0]
                y_tmp = waypoint[1]
                t_tmp = t_tmp + waypoint[2]

            # This rounding is needed to ensure that rounding errors in python do not create a permanent collisions between entities
            x_tmp = round(x_tmp, self.__location_precision__)
            y_tmp = round(y_tmp, self.__location_precision__)
            self.history.append(
                {
                    "x": x_tmp,
                    "y": y_tmp,
                    "t": t_tmp,
                    "c": is_result_of_collision,
                }
            )

        # Set the entity's position to where they are at this point in time
        self.x_coord = x_tmp
        self.y_coord = y_tmp
        # Set the entity's route end time to the current time
        self.__route_end_time__ = current_time

        if is_result_of_dissoc_grid:
            return {"is_result_of_collision": False}
        # Stop the entity at their current location and update the grid for their expected future
        planned_route = self.__plan_route__(
            waypoints=[],
            raise_on_future_collision=raise_on_future_collision,
        )
        self.on_realize(is_result_of_collision=is_result_of_collision)
        return planned_route

    def get_time(self) -> int | float:
        """
        Returns the current time of the grid queue.
        This method retrieves the current time from the grid queue.

        Returns:

        - int|float: The current time of the grid queue.
        """
        return self.__grid__.__queue__.__time__

    def is_available(self) -> bool:
        """
        Returns whether this entity is available for a new route.

        Returns:

        - bool: True if the entity is available for a new route, False otherwise.
        """
        return self.__route_end_time__ <= self.get_time()

    def add_route(
        self,
        waypoints: list[tuple[int | float, int | float, int | float]],
        time: int | float | None = None,
    ) -> None:
        """
        Adds a route to the grid for this entity.

        Args:

        - waypoints (list[tuple[int|float,int|float,int|float]]): A list of waypoints to be added to the grid queue.
            - A list of tuples where each tuple is (x_coord, y_coord, time_shift).
            - EG:
                ```
                waypoints = [
                    (5, 3, 10),
                    (3, 5, 10)
                ]
                ```
                - Move to (5, 3) over 10 seconds
                - Move to (3, 5) over 10 seconds
            - Note: x_coord and y_coord are the coordinates of the waypoint. They must both be positive.
            - Note: time_shift is the time it takes to move to the waypoint. It must be positive.
            - Optionally, you can use a 4th element to specify the orientation of the shape.
                - This orientation is always relative to the original shape
                - This is in radians where 0 is facing right (equivalent to the initial shape orientation) and pi is facing left.
                - Note: The last used orientation is used until it is changed again (or auto_rotate is set to True).
        - time (int|float|None): The time at which to start the route. If None, the current time is used.
        """
        if self.__grid__ is None:
            raise Exception(
                "Entity is not assigned to a grid. Cannot add a route."
            )
        if time is None:
            time = self.get_time()
        # Add the event to the queue
        self.__grid__.add_event(
            time=time,
            object=self,
            method="__plan_route__",
            kwargs={"waypoints": waypoints},
            priority=0,
        )

    def cancel_route(
        self,
        time: int | float | None = None,
    ) -> None:
        """
        Cancels the route for this entity.

        Args:

        - time (int|float|None): The time at which to cancel the route. If None, the current time is used.
        """
        if self.__grid__ is None:
            raise Exception(
                "Entity is not assigned to a grid. Cannot cancel a route."
            )
        if time is None:
            time = self.get_time()
        # Add the event to the queue
        self.__grid__.add_event(
            time=time,
            object=self,
            method="__realize_route__",
            kwargs={},
            priority=4,
        )

    def on_realize(self, **kwargs):
        """
        Called when the route is realized to allow for custom behavior.
        This method should be overridden by subclasses to implement custom behavior.

        Args:

        - **kwargs: Additional arguments passed to the method. Subclasses may use this or add their own arguments.
        """


class StaticEntity(Entity):
    """
    This class is used to represent entities that do not move, such as walls or other static objects.

    This is an extension of the Entity class that represents a static entity.

    To improve efficiency, many events and logic are avoided as a static entity does not move or respond to events.
    """

    def __realize_route__(
        self,
        is_result_of_collision: bool = False,
        raise_on_future_collision: bool = False,
        is_result_of_dissoc_grid: bool = False,
    ) -> dict:
        """
        Realize the route for this entity at the current time.

        Args:

        - is_result_of_collision (bool): Whether this route end is the result of a collision.
            - If True, the route end is the result of a collision and the entity should not be allowed to start a new route until the collision is resolved.
            - If False, the route end is not the result of a collision and the entity should be allowed to start a new route.
        - raise_on_future_collision (bool): Whether to raise an exception if the entity is in a future collision.
            - Raises an exception if this event causes a future collision with another entity.
        - is_result_of_dissoc_grid (bool): Whether the entity will be removed from the grid after this event.

        Returns:

        - dict: A dictionary containing the following keys:
            - has_collision (bool): Whether the route has a collision with another entity.
        """
        # Since this is a static entity, we don't need to do anything here.
        if is_result_of_collision:
            return
        if is_result_of_dissoc_grid:
            super().__realize_route__(
                is_result_of_collision=False,
                raise_on_future_collision=False,
                is_result_of_dissoc_grid=True,
            )
        # Since this is a static entity, the route end time is the current time when the entity is created (should normally be 0)
        self.__route_end_time__ = self.get_time()
        # Since this object does not move, we don't need to plan a route and will never interrupt it.
        return self.__plan_route__(
            waypoints=[], raise_on_future_collision=raise_on_future_collision
        )


class GhostEntity(Entity):
    """
    This class is used to represent entities that do not collide with other entities.

    It is an extension of the Entity class that represents a ghost entity.

    Essentially, these entities can move freely without worrying about collisions. Using them avoids substantial overhead in the simulation and can dramatically improve performance if collisions are irrelevant.
    """

    def __plan_route__(
        self,
        waypoints: list[tuple[int | float, int | float, int | float]],
        raise_on_future_collision: bool = False,
    ) -> dict:
        """
        Overrides the __plan_route__ method to allow for a ghost entity to be placed on the grid that never collides with other entities because it does not check for collisions.

        Sets the route for this entity given a set of waypoints starting at the current time.

        Args:

        - waypoints (list[tuple[int|float,int|float,int|float]]): A list of waypoints to be added to the grid queue.
            - A list of tuples where each tuple is (x_coord, y_coord, time_shift).
            - EG:
                ```
                waypoints = [
                    (5, 3, 10),
                    (3, 5, 10)
                ]
                ```
                - Move to (5, 3) over 10 seconds
                - Move to (3, 5) over 10 seconds
            - Note: x_coord and y_coord are the coordinates of the waypoint. They must both be positive.
            - Note: time_shift is the time it takes to move to the waypoint. It must be positive.
            - Optionally, you can use a 4th element to specify the orientation of the shape.
                - This orientation is always relative to the original shape
                - This is in radians where 0 is facing right (equivalent to the initial shape orientation) and pi is facing left.
                - Note: The last used orientation is used until it is changed again (or auto_rotate is set to True).
        - raise_on_future_collision (bool): Whether to raise an exception if the entity has any future plans that result in a collision.
            - Note: This is not used for ghost entities, but is included for consistency with the parent class.

        Returns:

        - dict: A dictionary containing the following keys:
            - has_collision (bool): Whether the route has a collision with another entity.
                - Note: This will always be False for ghost entities.
        """
        # Raise an exception if the entity is already in a route
        if not self.is_available():
            raise Exception(
                f"entity {self.name} is not available for a new route. Cannot set a new route until the current route is finished."
            )

        # Check for valid waypoints
        self.__waypoint_check__(waypoints)

        # Setup util attributes
        self.__clear_future_events__()

        total_route_time_shift = sum([waypoint[2] for waypoint in waypoints])

        self.__route_start_time__ = self.get_time()

        # Add a final waypoint occuring until the end of the simulation.
        # This allows us to lock in the position of the entity at the end of the route and block the grid cells accordingly.
        if len(waypoints) > 0:
            waypoints.append(
                (
                    waypoints[-1][0],
                    waypoints[-1][1],
                    self.__grid__.__max_time__
                    - self.__route_start_time__
                    - total_route_time_shift,
                )
            )
        else:
            waypoints.append(
                (
                    self.x_coord,
                    self.y_coord,
                    self.__grid__.__max_time__
                    - self.__route_start_time__
                    - total_route_time_shift,
                )
            )

        # Store the route waypoints and start time for later use to determine the entity's position at a given time
        self.__planned_waypoints__ = waypoints
        self.__route_end_time__ = min(
            self.__grid__.__max_time__,
            self.__route_start_time__ + total_route_time_shift,
        )

        # Add a route_end event for this entity at the timing of the end of the route
        if self.__route_start_time__ < self.__route_end_time__:
            event_id = self.__grid__.add_event(
                time=self.__route_end_time__,
                object=self,
                method="__realize_route__",
                kwargs={
                    "is_result_of_collision": False,
                },
                priority=2,
            )
            self.__future_event_ids__[event_id] = None
        return {"has_collision": False}
