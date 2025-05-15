from fizgrid.grid import Grid
from fizgrid.entities import Entity, StaticEntity

# This test is special. It creates rounding errors in python that create a permanent collision
# This is fixed in the code using `location_precision` for each entity to fix any rounding errors before they cause issues.

# from pprint import pp as print
grid = Grid(
    name="test_grid",
    x_size=10,
    y_size=20,
    add_exterior_walls=True,
)

amr = grid.add_entity(
    Entity(
        name="AMR2",
        shape=[[-1.5, -0.5], [-1.5, 0.5], [1.5, 0.5], [1.5, -0.5]],
        x_coord=5,
        y_coord=5,
    )
)

wall = grid.add_entity(
    StaticEntity(
        name="Wall1",
        shape=[[8, 0], [0, 0], [0, 1], [8, 1]],
        x_coord=1,
        y_coord=10,
    )
)

amr.add_route(
    waypoints=[
        (5, 15, 1),
    ],
    time=5,
)

# Run the sim
grid.simulate()

# Check if a collision is loggged
success = True
try:
    if not amr.history[-1]["c"]:
        success = False
except:
    success = False
if success:
    print("test_12.py: passed")
else:
    print("test_12.py: failed")
