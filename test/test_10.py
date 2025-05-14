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
    )
)

# Add routes to the entities such that they will collide

amr1.add_route(
    waypoints=[
        (5, 7, 1),
    ],
)

amr2.add_route(
    waypoints=[
        (7, 5, 1),
    ],
)

amr1.add_route(
    time=0.1,
    waypoints=[
        (5, 3, 1),
    ],
)

amr1.cancel_route(
    time=0.1,
)

# Run the sim
next_state_events = True
while next_state_events:
    next_state_events = grid.resolve_next_state()

# Check if the entities resulted in a collision
try:
    success = amr2.history[-1]["x"] == 7.0 and amr1.history[-1]["c"] == False
except:
    success = False
if success:
    print("test_10.py: passed")
else:
    print("test_10.py: failed")
