from fizgrid.grid import Grid
from fizgrid.entities import Entity, StaticEntity
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

# Attempt to move the robot through the sofa
# Starting at time=0, the robot will try to move to (5,8) over 12 seconds
# This will bump into the sofa
robot.add_route(time=0, waypoints=[(5, 8, 12)])

# Simulate the grid
grid.simulate()

# # Sho the history of the robot
# print(robot.history)

print("test_07.py: passed")
