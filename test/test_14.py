from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape

# from pprint import pp as print

grid = Grid(
    name="test_grid",
    x_size=10,
    y_size=10,
    add_exterior_walls=True,
    cell_density=2,
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

# Add routes to the entities such that they will collide

amr1.add_route(
    waypoints=[
        (5, 7, 1),
    ],
)

amr1.add_route(
    waypoints=[
        (7, 5, 1),
    ],
    time=0.5,
)

# Run the sim and check if an exception is raised since we are trying to add a route to an entity that is already on a route
try:
    next_state_events = True
    while next_state_events:
        next_state_events = grid.resolve_next_state()
    success = False
except:
    success = True
if success:
    print("test_14.py: passed")
else:
    print("test_14.py: failed")
