from fizgrid.grid import Grid
from fizgrid.agent import Agent

grid = Grid(
    name="test_grid",
    x_size=10,
    y_size=10,
    density=1
)

agent_1 = Agent(
    id=1,
    name="agent_1",
    shape=[[0, 0], [1, 0], [0, 1]],
    heading=45,
    grid=grid,
    x=5,
    y=5
)

print(agent_1.shape)