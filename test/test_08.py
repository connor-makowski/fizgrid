from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape
import random, math


class AMR(Entity):
    def __init__(self, *args, server, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server

    def on_realize(self, **kwargs):
        self.server.request_next_step(self.id)


class Order:
    def __init__(
        self,
        time,
        origin_x,
        origin_y,
        destination_x,
        destination_y,
    ):
        self.time = time
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.destination_x = destination_x
        self.destination_y = destination_y
        self.history = []
        self.set_status(time=time, status="arrived")

    def set_status(self, time, status):
        self.time = time
        self.status = status
        self.history.append({"time": time, "status": status})


class AssignedOrderHandler:
    def __init__(self, amr, order, server):
        self.amr = amr
        self.order = order
        self.server = server
        self.goal_x = None
        self.goal_y = None
        self.goal_tolerance = 1
        self.speed = 1

    def increment_status(self):
        if self.order.status == "in_queue":
            self.goal_x = self.order.origin_x
            self.goal_y = self.order.origin_y
            self.order.set_status(self.amr.get_time(), "waiting_pickup")
            self.handle_next_step()
        elif self.order.status == "waiting_pickup":
            self.goal_x = self.order.destination_x
            self.goal_y = self.order.destination_y
            self.order.set_status(self.amr.get_time(), "picked_up")
            self.handle_next_step()
        elif self.order.status == "picked_up":
            self.goal_x = None
            self.goal_y = None
            self.order.set_status(self.amr.get_time(), "delivered")
            self.server.order_handlers.pop(self.amr.id)
            self.server.add_available_amr(self.amr)
            self.server.completed_orders.append(self.order)

    def get_dist_from_goal(self):
        return (
            (self.goal_x - self.amr.x_coord) ** 2
            + (self.goal_y - self.amr.y_coord) ** 2
        ) ** 0.5

    def handle_next_step(self):
        if self.goal_x is None or self.goal_y is None:
            self.increment_status()
            return
        distance_from_goal = self.get_dist_from_goal()
        if distance_from_goal < self.goal_tolerance:
            self.increment_status()
            return
        goal_angle_rad = math.atan2(
            self.goal_y - self.amr.y_coord, self.goal_x - self.amr.x_coord
        )
        random_angle = random.normalvariate(goal_angle_rad, math.pi / 2)
        distance = random.uniform(0, min(distance_from_goal, 5))
        x_shift = distance * math.cos(random_angle)
        y_shift = distance * math.sin(random_angle)
        self.amr.add_route(
            waypoints=[
                (
                    self.amr.x_coord + x_shift,
                    self.amr.y_coord + y_shift,
                    distance / self.speed,
                ),
            ]
        )


class Server:
    def __init__(self, grid):
        self.grid = grid

        self.orders = []
        self.order_queue = []
        self.completed_orders = []

        self.available_amrs = []
        self.order_handlers = {}

    def schedule_order(
        self, time, origin_x, origin_y, destination_x, destination_y
    ):
        self.grid.add_event(
            time=time,
            object=self,
            method="receive_order",
            kwargs={
                "time": time,
                "origin_x": origin_x,
                "origin_y": origin_y,
                "destination_x": destination_x,
                "destination_y": destination_y,
            },
        )

    def create_amr(self, name, x_coord, y_coord):
        amr = grid.add_entity(
            AMR(
                name=name,
                shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
                x_coord=x_coord,
                y_coord=y_coord,
                server=self,
            )
        )
        self.add_available_amr(amr)
        return amr

    def receive_order(self, *args, **kwargs):
        order = Order(*args, **kwargs)
        self.order_queue.append(order)
        self.orders.append(order)
        order.set_status(order.time, "in_queue")
        self.try_assignment()

    def add_available_amr(self, amr):
        self.available_amrs.append(amr)
        self.try_assignment()

    def try_assignment(self):
        if len(self.order_queue) == 0 or len(self.available_amrs) == 0:
            return
        order_handler = AssignedOrderHandler(
            amr=self.available_amrs.pop(0),
            order=self.order_queue.pop(0),
            server=self,
        )
        self.order_handlers[order_handler.amr.id] = order_handler
        order_handler.handle_next_step()

    def request_next_step(self, amr_id):
        order_handler = self.order_handlers.get(amr_id)
        if order_handler is not None:
            order_handler.handle_next_step()


grid = Grid(
    name="test_grid",
    x_size=1000,
    y_size=1000,
    max_time=5000,
    add_exterior_walls=True,
)

# Create a server
server = Server(grid)

# Create AMRs
amr1 = server.create_amr(
    name="AMR1",
    x_coord=500,
    y_coord=400,
)

amr2 = server.create_amr(
    name="AMR2",
    x_coord=600,
    y_coord=500,
)

server.schedule_order(
    time=5,
    origin_x=450,
    origin_y=450,
    destination_x=500,
    destination_y=500,
)

server.schedule_order(
    time=10,
    origin_x=550,
    origin_y=550,
    destination_x=600,
    destination_y=600,
)

server.schedule_order(
    time=15,
    origin_x=650,
    origin_y=650,
    destination_x=700,
    destination_y=700,
)

# Run the sim
grid.simulate()

from pprint import pp


success = True
for order in server.orders:
    # Uncomment to see the order history
    # print(order.history)
    if order.history[-1]["status"] != "delivered":
        success = False
if success:
    print("test_08.py: passed")
else:
    print("test_08.py: failed")
