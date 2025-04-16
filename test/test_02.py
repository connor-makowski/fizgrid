from fizgrid.grid import Grid
from fizgrid.utils import Shape

grid = Grid(
    name="test_grid",
    x_size=10,
    y_size=10,
)

agent_1= grid.add_agent(
    name="Agent_1",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=5,
    y_coord=5,
)

# grid.add_plan(
#     agent_id=1,
#     start_time=5,
#     path=[
#         {'x_delta': 0, 'y_delta': 1, 'time_delta': 5},
#         {'x_delta': 1, 'y_delta': 0, 'time_delta': 5},
#     ]
# )
