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

# Run check route function to make sure it does not affect the history.
route_check = amr1.check_route(
    waypoints=[
        (5, 0.5, 1),
    ],
)

amr1.add_route(
    waypoints=[
        (5, 7, 1),
    ],
    time=1,
)

# Check if the history is updated correctly and that the route check did not affect it.
success = True
try:
    grid.simulate()
    if amr1.history != [
        {"x": 5, "y": 3, "t": 0, "c": False},
        {"x": 5, "y": 3, "t": 1, "c": False},
        {"x": 5, "y": 7, "t": 2, "c": False},
    ]:
        success = False
    if set(route_check.keys()) != {"has_collision", "collisions"}:
        success = False
    if not route_check["has_collision"]:
        success = False
    if list(route_check["collisions"].values())[0] != 0.8:
        success = False
except:
    success = False
if success:
    print("test_15.py: passed")
else:
    print("test_15.py: failed")
