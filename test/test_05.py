from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape
import random, math

from pprint import pp as print

grid_x_size = 1000
grid_y_size = 1000

grid = Grid(
    name="test_grid",
    x_size=grid_x_size,
    y_size=grid_y_size,
)

grid.add_exterior_walls()


class SnifferAMR(Entity):
    def set_goal(self, x_coord, y_coord, tolerance=1, speed=1):
        self.goal_x = x_coord
        self.goal_y = y_coord
        self.tolerance = tolerance
        self.speed = speed
        self.add_next_route()

    def add_next_route(self):
        if self.get_in_route():
            return
        distance_from_goal = ((self.goal_x - self.x_coord) ** 2 + (self.goal_y - self.y_coord) ** 2) ** 0.5
        if distance_from_goal < self.tolerance:
            return
        
        goal_angle_rad = math.atan2(self.goal_y - self.y_coord, self.goal_x - self.x_coord)
        random_angle = random.normalvariate(goal_angle_rad, math.pi/2)
        distance = random.uniform(0, min(distance_from_goal,5))
        x_shift = distance * math.cos(random_angle)
        y_shift = distance * math.sin(random_angle)

        self.add_route(
            route_deltas=[
                {'x_shift': x_shift, 'y_shift': y_shift, 'time_shift': distance * self.speed},
            ]
        )



# Add some AMRs to the grid
amr1 = grid.add_entity(SnifferAMR(
    name="AMR1",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=450,
    y_coord=500,
))
amr2 = grid.add_entity(SnifferAMR(
    name="AMR2",
    shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
    x_coord=500,
    y_coord=450,
))

amr1.set_goal(
    x_coord=550,
    y_coord=500,
)

amr2.set_goal(
    x_coord=500,
    y_coord=550,
)

# Run the sim
next_state_events = True
while next_state_events:
    next_state_events = grid.resolve_next_state()
    for event in next_state_events:
        if isinstance(event['object'], SnifferAMR):
            if not event['object'].get_in_route():
                event['object'].add_next_route()

print(amr1.history)




