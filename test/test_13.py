# Testing for TimeQueue class
from fizgrid.helpers.waypoint_timing.simple import (
    simple_waypoint_time_approximation,
)
from fizgrid.helpers.waypoint_timing.acceleration import (
    acceleration_waypoint_time_approximation,
)

passing = True

test_case_1 = [(1, 0), (2, 0), (2, 1)]

simple_timed_waypoints = simple_waypoint_time_approximation(
    start_x=0, start_y=0, waypoints=test_case_1, speed=1
)

if simple_timed_waypoints != [(1, 0, 1.0), (2, 0, 1.0), (2, 1, 1.0)]:
    print("test_13.py: simple_waypoint_time_approximation failed")
    passing = False

acceleration_timed_waypoints = acceleration_waypoint_time_approximation(
    start_x=0, start_y=0, waypoints=test_case_1, max_speed=1, acceleration=1
)

if acceleration_timed_waypoints != [
    (0.5, 0.0, 1.0),
    (1, 0, 0.5),
    (1.505, 0.0, 0.505),
    (2, 0, 0.9),
    (2.0, 0.495, 0.9),
    (2.0, 0.5, 0.005),
    (2, 1, 1.0),
]:
    print("test_13.py: acceleration_waypoint_time_approximation failed")
    passing = False


if passing:
    print("test_13.py: passed")
else:
    print("test_13.py: failed")
