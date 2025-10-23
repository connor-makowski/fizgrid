from fizgrid.grid import Grid
from fizgrid.entities import Entity, StaticEntity, GhostEntity
from fizgrid.utils import Shape

# Create a grid with exterior walls
grid = Grid(
    name="living_room",
    x_size=10,
    y_size=10,
    add_exterior_walls=True,
    cell_density=1,
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

dog = grid.add_entity(
    Entity(
        name="dog",
        shape=Shape.rectangle(x_len=1, y_len=1),
        x_coord=5,
        y_coord=2,
    ),
    time=4,
)

# Safe create an entity on top of the robot
box = grid.add_entity(
    StaticEntity(
        name="box",
        shape=Shape.rectangle(x_len=1, y_len=1),
        x_coord=5,
        y_coord=2,
    ),
    safe_create=True,
)

# Attempt to move the robot through the sofa
# Starting at time=0, the robot will try to move to (5,8) over 5 seconds
# This will make way for the box to appear on the grid
robot.add_route(time=0, waypoints=[(5, 8, 5)])
dog.add_route(time=6, waypoints=[(3, 5, 5)])

# Simulate the grid
grid.simulate()

success = True
if robot.history[-1]["y"] != 8 and robot.history[-1]["c"] != True:
    success = False
if box.history[-1]["y"] != 2 and box.history[-1]["c"] != False:
    success = False

if success:
    print("test_17.py: passed")
else:
    print("test_17.py: failed")
