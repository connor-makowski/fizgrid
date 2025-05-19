import math


def get_distance(pt1: tuple, pt2: tuple):
    """
    Returns the Euclidean distance between two points.

    Args:

    - pt1: The first point (x, y).
    - pt2: The second point (x, y).

    Returns:

    - float: The distance between the two points.
    """
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5


def get_angle(pt1: tuple, pt2: tuple, pt3: tuple):
    """
    Calculates the angle when going from pt1 to pt2 to pt3.

    Returns the angle in degrees.

    Args:

    - pt1: The first point (x, y).
    - pt2: The second point (x, y).
    - pt3: The third point (x, y).

    Returns:

    - float: The angle in degrees.

    Examples:

    EG: (0, 0) -> (1, 0) -> (2, 0) => 180
    EG: (0, 0) -> (1, 0) -> (1, 1) => 90
    """
    v1 = (pt1[0] - pt2[0], pt1[1] - pt2[1])
    v2 = (pt3[0] - pt2[0], pt3[1] - pt2[1])
    if v1 == (0, 0) or v2 == (0, 0):
        return 0.0
    magnitude_v1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5
    magnitude_v2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
    cos_theta_clamp = max(-1, min(1, (cos_theta)))
    return math.acos(cos_theta_clamp) / math.pi * 180


def get_acceleration_distance(
    start_speed: int | float, end_speed: int | float, acceleration: int | float
):
    """
    Calculates the distance required to accelerate/decelerate from start_speed to end_speed
    given a constant acceleration.

    Args:

    - start_speed: The speed at which the object is currently traveling.
    - end_speed: The speed at which the object will be traveling.
    - acceleration: The acceleration of the object (should always be positive as start and end speeds determine if it is accelerating or decelerating).

    Returns:

    - float: The distance required to accelerate/decelerate from start_speed to end_speed.
        - If start_speed and end_speed are equal, 0 is returned.
        - If start_speed is greater than end_speed, the function will return the distance required to decelerate from start_speed to end_speed.
        - If start_speed is less than end_speed, the function will return the distance required to accelerate from start_speed to end_speed.
    """
    if start_speed == end_speed:
        return 0.0
    if start_speed > end_speed:
        start_speed, end_speed = end_speed, start_speed
    return (end_speed**2 - start_speed**2) / (2 * abs(acceleration))


def get_end_speed(
    start_speed: int | float, distance: int | float, acceleration: int | float
):
    """
    Calculates the speed at wich an object will be traveling after a given distance
    given a constant acceleration.

    Args:

    - start_speed: The speed at which the object is currently traveling.
    - distance: The distance over which the object will be traveling.
    - acceleration: The acceleration/deceleration of the object (positive for acceleration, negative for deceleration).

    Returns:

    - float: The speed at which the object will be traveling after the given distance.
    """
    if acceleration == 0 or distance == 0:
        return start_speed
    return (start_speed**2 + 2 * acceleration * distance) ** 0.5


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
