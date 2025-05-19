from fizgrid.helpers.waypoint_timing.utils import (
    get_distance,
    get_angle,
    get_acceleration_distance,
    get_end_speed,
)


def get_max_corner_speeds(
    waypoints: list[tuple], max_speed: float | int, acceleration: int | float
):
    """
    Calculates the maximum speeds that can be taken at each corner in a set of waypoints
    given a constant acceleration / deceleration between 0 and max_speed.

    The first and last waypoints are always 0 speed.

    args:

    - waypoints: A list of tuples representing the waypoints (x, y).
    - max_speed: The maximum speed of the entity.
    - acceleration: The acceleration/deceleration of the entity.
    """
    # Create a list of speeds that offer the max speed for each corner based on the angle
    speeds = []
    for idx, waypoint in enumerate(waypoints):
        if idx == 0 or idx == len(waypoints) - 1:
            speeds.append(0.0)  # Must start and end at 0 speed
        else:
            angle = get_angle(waypoints[idx - 1], waypoint, waypoints[idx + 1])
            # Map tighter angles to lower allowable speeds
            if angle > 178:
                corner_speed = max_speed
            elif angle > 170:
                corner_speed = max_speed * 0.8
            elif angle > 160:
                corner_speed = max_speed * 0.6
            elif angle > 150:
                corner_speed = max_speed * 0.4
            elif angle > 140:
                corner_speed = max_speed * 0.2
            else:
                corner_speed = max_speed * 0.1
            speeds.append(corner_speed)

    # Go backwards to update the maximum speed at each corner based on the deceleration
    # distance needed to not exceed the speed limit on any corner
    for idx in range(
        len(waypoints) - 1
    ):  # Minus 1 to avoid the index out of range error
        distance = get_distance(waypoints[-idx - 1], waypoints[-idx - 2])
        speeds[-idx - 2] = min(
            speeds[-idx - 2],
            get_end_speed(speeds[-idx - 1], distance, acceleration),
        )

    return speeds


def partition_distance(
    distance: int | float,
    start_speed: int | float,
    max_end_speed: int | float,
    max_speed: int | float,
    acceleration: int | float,
):
    """
    Partitions a distance into time and distance for acceleration, cruise and deceleration

    args:

    - distance: The distance to be traveled.
    - start_speed: The speed at which the entity is currently traveling.
    - max_end_speed: The maximum ending speed that the entity can travel at.
    - max_speed: The maximum speed of the entity.
    - acceleration: The acceleration/deceleration of the entity.

    Returns a tuple
    - 0: list of dictionaries with the following keys:
        - end_pct: The percentage of the distance at which the partition ends.
        - time: The time it takes to travel the distance in the partition.
    - 1: int or float: The ending speed

    """
    # Compute peak speed possible within distance
    max_speed_possible_in_distance = get_end_speed(
        start_speed=start_speed, distance=distance, acceleration=acceleration
    )
    max_end_speed = min(max_end_speed, max_speed_possible_in_distance)
    peak_speed = min(
        ((2 * acceleration * distance + start_speed**2 + max_end_speed**2) / 2)
        ** 0.5,
        max_speed,
    )

    end_speed = min(max_end_speed, peak_speed)
    partitions = []
    accel_end_pct = 0
    cruise_end_pct = 1

    # Compute distances and times for acceleration, cruise and deceleration
    if peak_speed > start_speed:
        accel_time = (peak_speed - start_speed) / acceleration
        accel_dist = get_acceleration_distance(
            start_speed, peak_speed, acceleration
        )
        accel_end_pct = accel_dist / distance
        partitions.append({"end_pct": accel_end_pct, "time": accel_time})
    if peak_speed > max_end_speed:
        decel_time = (peak_speed - max_end_speed) / acceleration
        decel_dist = get_acceleration_distance(
            peak_speed, max_end_speed, acceleration
        )
        cruise_end_pct = (distance - decel_dist) / distance
        partitions.append({"end_pct": 1, "time": decel_time})
    if peak_speed == max_speed:
        cruise_dist = (cruise_end_pct - accel_end_pct) * distance
        cruise_time = cruise_dist / peak_speed
        partitions.append({"end_pct": cruise_end_pct, "time": cruise_time})
    return sorted(partitions, key=lambda x: x["end_pct"]), end_speed


def acceleration_waypoint_time_approximation(
    start_x,
    start_y,
    waypoints: list[tuple],
    max_speed: int | float,
    acceleration: int | float,
    round_time_to: int | float = 4,
):
    """
    Partitions a set of waypoints (list of tuples(x,y)) into a list of (x,y,time_delta) tuples
    given a constant acceleration / deceleration between 0 and max_speed.

    Each waypoint can be partitioned into an acceleration, cruise and deceleration phase (as applicable).

    args:

    - start_x: The x coordinate of the starting point.
    - start_y: The y coordinate of the starting point.
    - waypoints: A list of tuples representing the waypoints (x, y).
    - max_speed: The maximum speed of the entity.
    - acceleration: The acceleration/deceleration of the entity.
    - round_time_to: The number of decimal places to round the time to. Default is 4.

    Returns

    - list of tuples:  representing the waypoints (x, y, time_delta).
    """
    partitioned_waypoints = []
    # Add the starting point to the list of waypoints
    waypoints = [(start_x, start_y)] + waypoints
    waypoint_speeds = get_max_corner_speeds(waypoints, max_speed, acceleration)
    current_speed = 0
    for idx in range(len(waypoints) - 1):
        start_point = waypoints[idx]
        end_point = waypoints[idx + 1]

        distance = get_distance(start_point, end_point)
        partitions, current_speed = partition_distance(
            distance=distance,
            start_speed=current_speed,
            max_end_speed=waypoint_speeds[idx + 1],
            max_speed=max_speed,
            acceleration=acceleration,
        )
        for partition in partitions:
            partitioned_waypoints.append(
                (
                    start_point[0]
                    + (end_point[0] - start_point[0]) * partition["end_pct"],
                    start_point[1]
                    + (end_point[1] - start_point[1]) * partition["end_pct"],
                    round(partition["time"], round_time_to),
                )
            )
    return partitioned_waypoints
