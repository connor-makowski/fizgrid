from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape
import random, math

from pprint import pp as print

class SnifferAMR(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_goal = False
        self.goal_x = None
        self.goal_y = None
        self.tolerance = None
        self.speed = None

    def get_dist_from_goal(self):
        return ((self.goal_x - self.x_coord) ** 2 + (self.goal_y - self.y_coord) ** 2) ** 0.5

    def set_goal(self, x_coord, y_coord, tolerance=1, speed=1):
        self.has_goal = True
        self.goal_x = x_coord
        self.goal_y = y_coord
        self.tolerance = tolerance
        self.speed = speed  
        if self.is_available():
            self.add_next_route()
        else:
            raise ValueError("AMR is not available to set a goal.")

    def add_next_route(self):
        distance_from_goal = self.get_dist_from_goal()
        if distance_from_goal < self.tolerance:
            return
        goal_angle_rad = math.atan2(self.goal_y - self.y_coord, self.goal_x - self.x_coord)
        random_angle = random.normalvariate(goal_angle_rad, math.pi/2)
        distance = random.uniform(0, min(distance_from_goal,5))
        x_shift = distance * math.cos(random_angle)
        y_shift = distance * math.sin(random_angle)

        self.add_route(
            waypoints=[
                (self.x_coord + x_shift, self.y_coord + y_shift, distance * self.speed),
            ]
        )

    def on_realize(self, **kwargs):
        if self.has_goal:
            if self.get_dist_from_goal() > self.tolerance:
                self.add_next_route()
            else:
                self.has_goal = False


grid = Grid(
    name="test_grid",
    x_size=1000,
    y_size=1000,
    add_exterior_walls=True,
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

success = True

if amr1.get_dist_from_goal() > amr1.tolerance:
    success = False
if amr2.get_dist_from_goal() > amr2.tolerance:
    success = False

if success:
    print("test_05.py: passed")
else:
    print("test_05.py: failed")



