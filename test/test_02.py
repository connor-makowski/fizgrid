from fizgrid.grid import Grid
from fizgrid.utils import Shape

grid = Grid(
    name="test_grid",
    x_size=10,
    y_size=10,
)

agent_1 = grid.add_agent(
    name="Agent_1",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=5,
    y_coord=3,
)

agent_2 = grid.add_agent(
    name="Agent_2",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=3,
    y_coord=5,
)

# Add routes to the agents such that they will collide

agent_1.add_route(
    route_deltas=[
        {'x_shift': 0, 'y_shift': 4, 'time_shift': 1},
    ]
)

agent_2.add_route(
    route_deltas=[
        {'x_shift': 4, 'y_shift': 0, 'time_shift': 1},
    ]
)

# Run the sim
while grid.process_next_event():
    pass




