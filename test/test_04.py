from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape

from pprint import pp as print

grid_x_size = 10
grid_y_size = 10

grid = Grid(
    name="test_grid",
    x_size=grid_x_size,
    y_size=grid_y_size,
)

grid.add_exterior_walls()

# Add some AMRs to the grid
amr1 = grid.add_entity(Entity(
    name="AMR1",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=5,
    y_coord=3,
))
amr2 = grid.add_entity(Entity(
    name="AMR2",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=3,
    y_coord=5,
))

# Add routes to the entities such that they will collide

amr1.add_route(
    route_deltas=[
        {'x_shift': 0, 'y_shift': 4, 'time_shift': 1},
    ]
)

amr2.add_route(
    route_deltas=[
        {'x_shift': 4, 'y_shift': 0, 'time_shift': 1},
    ]
)

# Run the sim
next_state_events = True
while next_state_events:
    next_state_events = grid.resolve_next_state()
    print(next_state_events)




