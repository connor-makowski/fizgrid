from fizgrid.grid import Grid
from fizgrid.entities import Entity, StaticEntity, GhostEntity
from fizgrid.utils import Shape

# Create a grid with exterior walls
grid = Grid(
    name="living_room",
    x_size=10,
    y_size=10,
    add_exterior_walls=True,
)

# Add some static entities
sofa = grid.add_entity(
    StaticEntity(
        name="sofa",
        shape=Shape.rectangle(x_len=2, y_len=1),
        x_coord=5,
        y_coord=5.5,
    )
)

# Add a dynamic entity
robot = grid.add_entity(
    Entity(
        name="robot",
        shape=Shape.rectangle(x_len=1, y_len=1),
        x_coord=5,
        y_coord=2,
    )
)

# Add a dynamic entity that can pass through other entities
ghost = grid.add_entity(
    GhostEntity(
        name="ghost",
        shape=Shape.rectangle(x_len=1, y_len=1),
        x_coord=5,
        y_coord=2,
    )
)

# Attempt to move the robot through the sofa
# Starting at time=0, the robot will try to move to (5,8) over 12 seconds
# This will bump into the sofa and stop
robot.add_route(time=0, waypoints=[(5, 8, 12)])


# Attempt to move the ghost through the sofa
# Starting at time=0, the ghost will try to move to (5,8) over 12 seconds
# This will not bump into the sofa and complete its route
ghost.add_route(time=0, waypoints=[(5, 8, 12)])

# Simulate the grid
grid.simulate()

# Show the history of the robot
# print(robot.history)
# [{'x': 5, 'y': 2, 't': 0, 'c': False}, {'x': 5.0, 'y': 4.5, 't': 5.0, 'c': True}]
# This means that the robot started at (5,2) at time=0 and moved to (5,4.5) at time=5 where it collided with the sofa
# Since there is no additional logic to handle the collision, the robot just stopped moving at time 5 and waited for the end of the simulation


# Show the history of the ghost
# print(ghost.history)
# [{'x': 5, 'y': 2, 't': 0, 'c': False}, {'x': 5, 'y': 8, 't': 12, 'c': False}]
# This means that the ghost started at (5,2) at time=0 and moved to (5,8) at time=12 without any collisions

success = True
if robot.history[-1]["y"] != 4.5 and robot.history[-1]["c"] != True:
    success = False
if ghost.history[-1]["y"] != 8 and ghost.history[-1]["c"] != False:
    success = False

if success:
    print("test_07.py: passed")
else:
    print("test_07.py: failed")
