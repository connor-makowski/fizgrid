from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape
import random, math

# from pprint import pp as print


class Scheduler:
    def __init__(self, grid):
        self.grid = grid
        self.orders = []
        self.processors = []

    def add_order(self, order):
        self.orders.append(order)
        order.set_status(order.time, "in_queue")
        self.try_assignment()

    def add_processor(self, processor):
        self.processors.append(processor)
        self.try_assignment()

    def try_assignment(self):
        if len(self.orders) == 0 or len(self.processors) == 0:
            return
        order = self.orders.pop(0)
        processor = self.processors.pop(0)
        order.set_status(processor.get_time(), "scheduled")
        processor.add_order(order)


class Order:
    def __init__(
        self,
        time,
        origin_x,
        origin_y,
        destination_x,
        destination_y,
        scheduler: Scheduler,
    ):
        self.time = time
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.destination_x = destination_x
        self.destination_y = destination_y
        self.status = "none"
        self.scheduler = scheduler
        self.history = []

        # Add this order to the event stream
        self.scheduler.grid.add_event(
            time=time,
            object=self,
            method="arrive",
            kwargs={},
        )

    def set_status(self, time, status):
        self.time = time
        self.status = status
        self.history.append({"time": time, "status": status})

    def arrive(self):
        self.set_status(self.time, "order_arrived")
        self.scheduler.add_order(self)


class SnifferAMR(Entity):
    def __init__(self, *args, scheduler: Scheduler, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = None
        self.speed = 1
        self.scheduler = scheduler
        self.scheduler.add_processor(self)

    def add_order(self, order: Order):
        self.order = order
        self.handle_order_state()

    def handle_order_state(self):
        if self.order.status == "scheduled":
            self.set_goal(
                x_coord=self.order.origin_x,
                y_coord=self.order.origin_y,
            )
            self.order.set_status(self.get_time(), "waiting_pickup")
        elif self.order.status == "waiting_pickup":
            self.set_goal(
                x_coord=self.order.destination_x,
                y_coord=self.order.destination_y,
            )
            self.order.set_status(self.get_time(), "picked_up")
        elif self.order.status == "picked_up":
            self.order.set_status(self.get_time(), "delivered")
            self.order = None
            self.scheduler.add_processor(self)

    def get_dist_from_goal(self):
        return (
            (self.goal_x - self.x_coord) ** 2
            + (self.goal_y - self.y_coord) ** 2
        ) ** 0.5

    def set_goal(self, x_coord, y_coord, tolerance=1):
        self.goal_x = x_coord
        self.goal_y = y_coord
        self.tolerance = tolerance
        self.add_next_route()

    def add_next_route(self):
        distance_from_goal = self.get_dist_from_goal()
        if distance_from_goal < self.tolerance:
            self.handle_order_state()
        else:
            goal_angle_rad = math.atan2(
                self.goal_y - self.y_coord, self.goal_x - self.x_coord
            )
            random_angle = random.normalvariate(goal_angle_rad, math.pi / 2)
            distance = random.uniform(0, min(distance_from_goal, 5))
            x_shift = distance * math.cos(random_angle)
            y_shift = distance * math.sin(random_angle)
            self.add_route(
                waypoints=[
                    (
                        self.x_coord + x_shift,
                        self.y_coord + y_shift,
                        distance * self.speed,
                    ),
                ]
            )

    def on_realize(self, **kwargs):
        if self.order:
            self.add_next_route()


grid = Grid(
    name="test_grid",
    x_size=1000,
    y_size=1000,
    max_time=5000,
    add_exterior_walls=True,
)

scheduler = Scheduler(grid)

# Add some AMRs to the grid
amr1 = grid.add_entity(
    SnifferAMR(
        name="AMR1",
        shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
        x_coord=500,
        y_coord=400,
        scheduler=scheduler,
    )
)

amr2 = grid.add_entity(
    SnifferAMR(
        name="AMR2",
        shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
        x_coord=600,
        y_coord=500,
        scheduler=scheduler,
    )
)

orders = [
    Order(
        time=5,
        origin_x=450,
        origin_y=450,
        destination_x=500,
        destination_y=500,
        scheduler=scheduler,
    ),
    Order(
        time=10,
        origin_x=550,
        origin_y=550,
        destination_x=600,
        destination_y=600,
        scheduler=scheduler,
    ),
    Order(
        time=15,
        origin_x=650,
        origin_y=650,
        destination_x=700,
        destination_y=700,
        scheduler=scheduler,
    ),
]

# Run the sim
next_state_events = True
while next_state_events:
    next_state_events = grid.resolve_next_state()

success = True
for order in orders:
    # Uncomment to see the order history
    # print(order.history)
    if order.history[-1]["status"] != "delivered":
        success = False
        break
if success:
    print("test_06.py: passed")
else:
    print("test_06.py: failed")
