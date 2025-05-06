from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape

# from pprint import pp as print

grid = Grid(
    name="test_grid",
    x_size=10,
    y_size=10,
    add_exterior_walls=True,
)

# Add some AMRs to the grid
amr1 = grid.add_entity(
    Entity(
        name="AMR1",
        shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
        x_coord=5,
        y_coord=3,
    )
)
amr2 = grid.add_entity(
    Entity(
        name="AMR2",
        shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
        x_coord=3,
        y_coord=5,
    ),
    time=5,
)

# Add routes to the entities such that they will collide

amr1.add_route(
    waypoints=[
        (5, 7, 1),
    ],
)

# Note: We need to wait for this AMR to be in the grid before it can move
amr2.add_route(
    waypoints=[
        (7, 5, 1),
    ],
    time=5,
)

# Run the sim
grid.simulate()

# Check if the entities resulted in a collision
try:
    success = amr2.history[-1]["x"] == 7 and amr2.history[-1]["y"] == 5 and amr2.history[-1]["c"] == False
except:
    success = False
if success:
    print("test_09.py: passed")
else:
    print("test_09.py: failed")
