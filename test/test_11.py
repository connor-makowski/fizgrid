from fizgrid.grid import Grid
from fizgrid.entities import Entity, StaticEntity
from fizgrid.utils import Shape

# from pprint import pp as print

grid = Grid(
    name="test_grid",
    x_size=20,
    y_size=20,
    add_exterior_walls=True,
)

# Add some AMRs to the grid
amr1 = grid.add_entity(
    Entity(
        name="AMR1",
        shape=[[-1.5, -0.5], [-1.5, 0.5], [1.5, 0.5], [1.5, -0.5]],
        x_coord=5,
        y_coord=5,
        auto_rotate=True,
    )
)

amr2 = grid.add_entity(
    Entity(
        name="AMR2",
        shape=[[-1.5, -0.5], [-1.5, 0.5], [1.5, 0.5], [1.5, -0.5]],
        x_coord=15,
        y_coord=5,
    )
)

wall1 = grid.add_entity(
    StaticEntity(
        name="Wall1",
        shape=[[8, 0], [0, 0], [0, 1], [8, 1]],
        x_coord=11,
        y_coord=10,
    )
)

wall2 = grid.add_entity(
    StaticEntity(
        name="Wall2",
        shape=[[-8, 0], [0, 0], [0, 1], [-8, 1]],
        x_coord=9,
        y_coord=10,
    )
)

amr1.add_route(
    waypoints=[
        (10, 5, 1),
        (10, 15, 1),
        (5, 15, 1),
    ],
)

amr2.add_route(
    waypoints=[
        (10, 5, 1),
        (10, 15, 1),
        (15, 15, 1),
    ],
    time=5,
)

# Run the sim
grid.simulate()

# Check if the auto rotated AMR clears the gap
success = True
try:
    if amr1.history[-1]["y"] != 15:
        success = False
    if amr2.history[-1]["y"] != 9.5:
        success = False
except:
    success = False
if success:
    print("test_11.py: passed")
else:
    print("test_11.py: failed")
