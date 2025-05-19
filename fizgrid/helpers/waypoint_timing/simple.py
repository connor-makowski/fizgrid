def simple_waypoint_time_approximation(
    start_x: int | float,
    start_y: int | float,
    waypoints: list[tuple],
    speed: int | float,
):
    """
    A helper function to approximate waypoint times assuming a constant entity speed
    Returns the waypoints with the time it would take to travel between them given the constant speed.

    Args:

    - start_x: The x coordinate of the starting point.
    - start_y: The y coordinate of the starting point.
    - waypoints: A list of tuples representing the waypoints to be traversed by the moving entity.
    - speed: The constant speed of the moving entity.

    Returns:

    - A list of tuples representing the waypoints with the time it would take to travel between them given the constant speed.
        - Each tuple contains the x and y coordinates of the original waypoint as well as the time delta to travel to said waypoint.
    """
    # Store output to return
    output = []
    tmp_x = start_x
    tmp_y = start_y
    for waypoint in waypoints:
        distance_traveled = (
            (waypoint[0] - tmp_x) ** 2 + (waypoint[1] - tmp_y) ** 2
        ) ** 0.5
        time_to_travel = distance_traveled / speed
        tmp_x = waypoint[0]
        tmp_y = waypoint[1]
        output.append((tmp_x, tmp_y, time_to_travel))

    return output
