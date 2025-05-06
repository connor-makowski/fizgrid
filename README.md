# Fizgrid
[![PyPI version](https://badge.fury.io/py/fizgrid.svg)](https://badge.fury.io/py/fizgrid)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simulate entities that take up space over time in grid based environments. 


# Overview
This package introduces a new approach to simulating physical movement within a grid. Rather than following the traditional method of discretizing time and iterating over spatial configurations, this simulation inverts the model: space is discretized, and time is continuous.

Events are scheduled into a priority queue, ordered by their occurrence time. The simulation processes events in chronological order, updating only the relevant entities and grid cells affected by each event. This design allows for highly efficient simulation of large numbers of entities over long periods of simulated time.

## Entity Movement and Scheduling

Entity movements are planned in advance but only realized when an associated event is triggered. When a route is assigned to an entity, each grid cell along its path is reserved for the time the entity is expected to occupy it. During this reservation process, the system checks for potential conflicts. For example, whether another entity is scheduled to occupy the same cell at the same time.

If a conflict is detected, a collision event is added to the queue for both entities. Only the first potential collision between any pair of entities is added to avoid redundancy. Additionally, an end-of-route event is queued for the entity to signal the completion of its movement.

## Event Handling

When an end-of-route event is processed:

- The entity’s position is updated to where it would be at that time.
- All pending events related to its previous route are removed from the queue.
- A placeholder (blank) route is assigned to the entity to occupy its current position until a new route is defined.
    - This may trigger new collisions, which will be resolved in their own time.

When a collision event is processed:

- The entity is moved to its calculated position at the collision time.
- All future events tied to its current route are removed.
- Collision events for other entities that would have involved this entity are also removed.
    - The counterpart entity in the current collision still processes its corresponding event.
- A blank route is assigned to the entity to mark its occupancy of the current cell until reassigned.
    - This may trigger new collisions will be resolved in their own time.

# Setup

Make sure you have Python 3.10.x (or higher) installed on your system. You can download it [here](https://www.python.org/downloads/).

## Installation

```
pip install fizgrid
```

## Basic Usage

### Technical Docs
The technical documentation is available at [https://connor-makowski.github.io/fizgrid/index.html](https://connor-makowski.github.io/fizgrid/index.html).

### Example
```py
from fizgrid.grid import Grid
from fizgrid.entities import Entity, StaticEntity, GhostEntity
from fizgrid.utils import Shape

# Create a grid with exterior walls
grid = Grid(
    name="living_room",
    x_size=10,
    y_size=10,
    add_exterior_walls=True,
)

# Add some static entities
sofa = grid.add_entity(
    StaticEntity(
        name="sofa",
        shape=Shape.rectangle(x_len=2, y_len=1),
        x_coord=5,
        y_coord=5.5,
    )
)

# Add a dynamic entity
robot = grid.add_entity(
    Entity(
        name="robot",
        shape=Shape.rectangle(x_len=1, y_len=1),
        x_coord=5,
        y_coord=2,
    )
)

# Add a dynamic entity that can pass through other entities
ghost = grid.add_entity(
    GhostEntity(
        name="ghost",
        shape=Shape.rectangle(x_len=1, y_len=1),
        x_coord=5,
        y_coord=2,
    )
)

# Attempt to move the robot through the sofa
# Starting at time=0, the robot will try to move to (5,8) over 12 seconds
# This will bump into the sofa and stop
robot.add_route(time=0, waypoints=[(5, 8, 12)])


# Attempt to move the ghost through the sofa
# Starting at time=0, the ghost will try to move to (5,8) over 12 seconds
# This will not bump into the sofa and complete its route
ghost.add_route(time=0, waypoints=[(5, 8, 12)])

# Simulate the grid
grid.simulate()

# Show the history of the robot
print(robot.history)
# [{'x': 5, 'y': 2, 't': 0, 'c': False}, {'x': 5.0, 'y': 4.5, 't': 5.0, 'c': True}]
# This means that the robot started at (5,2) at time=0 and moved to (5,4.5) at time=5 where it collided with the sofa
# Since there is no additional logic to handle the collision, the robot just stopped moving at time 5 and waited for the end of the simulation


# Show the history of the ghost
print(ghost.history)
# [{'x': 5, 'y': 2, 't': 0, 'c': False}, {'x': 5, 'y': 8, 't': 12, 'c': False}]
# This means that the ghost started at (5,2) at time=0 and moved to (5,8) at time=12 without any collisions
```

# More Comprehensive Examples

## Create a basic sniffer entity
Create a Truffle Pig that sniffs out truffles on a grid. 
```py
from fizgrid.grid import Grid
from fizgrid.entities import Entity
from fizgrid.utils import Shape
import random, math


class Sniffer(Entity):
    def __init__(self, *args, **kwargs):
        # Override the init method of the Entity class to extend the functionality and add custom attributes.
        super().__init__(*args, **kwargs)
        self.goal_x = None
        self.goal_y = None
        self.tolerance = None
        self.speed = 1

    def get_dist_from_goal(self):
        # A function to calculate the distance from the entity to the goal.
        return (
            (self.goal_x - self.x_coord) ** 2
            + (self.goal_y - self.y_coord) ** 2
        ) ** 0.5

    def set_goal(self, x_coord, y_coord, tolerance=1):
        # Set the goal for the entity to reach and start the routing process.
        self.goal_x = x_coord
        self.goal_y = y_coord
        self.tolerance = tolerance
        self.add_next_route()

    def add_next_route(self):
        # Determine the next route for the entity to take.

        # This route is randomly calculated based on the angle and distance to the goal.
        #     - If the entity is within the tolerance of the goal, it will stop.
        #     - If the entity is not within the tolerance
        #         - It will calculate the target angle towards the goal.
        #         - It will calculate the target distance to the goal.
        #         - A random angle is generated by using a normal distribution centered on the goal angle.
        #         - A random distance is generated between 0 and the minimum of the distance to the goal and 5.
        distance_from_goal = self.get_dist_from_goal()
        if distance_from_goal < self.tolerance:
            return
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
        # This method is a blank method that should be overridden by the user.
        # It is called when an event for the entity is realized.

        # In this case, it is used to implment the goal checking logic and continuously add routes until the goal is reached.

        # The method checks if the entity has a goal set and if it is within the tolerance of the goal.
        # If the entity is not within the tolerance, it will add the next route.
        # If the entity is within the tolerance, it will set the goal to None.
        if self.goal_x is not None and self.goal_y is not None:
            if self.get_dist_from_goal() > self.tolerance:
                self.add_next_route()
            else:
                self.goal_x = None
                self.goal_y = None


forest = Grid(
    name="forest",
    x_size=1000,
    y_size=1000,
    add_exterior_walls=True,
)

# Add some pigs to the forest
truffle_pig_1 = forest.add_entity(
    Sniffer(
        name="Truffle_Pig_1",
        shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
        x_coord=450,
        y_coord=500,
    )
)
truffle_pig_2 = forest.add_entity(
    Sniffer(
        name="Truffle_Pig_2",
        shape=Shape.rectangle(x_len=1, y_len=1, round_to=2),
        x_coord=500,
        y_coord=450,
    )
)

truffle_pig_1.set_goal(
    x_coord=550,
    y_coord=500,
)

truffle_pig_2.set_goal(
    x_coord=500,
    y_coord=550,
)

# Run the sim
forest.simulate()

print({
    'Name': truffle_pig_1.name,
    'x_coord': truffle_pig_1.x_coord,
    'y_coord': truffle_pig_1.y_coord,
})
print({
    'Name': truffle_pig_2.name,
    'x_coord': truffle_pig_2.x_coord,
    'y_coord': truffle_pig_2.y_coord,
})

# Example Output
# {'Name': 'Truffle_Pig_1', 'x_coord': 550.6344767270211, 'y_coord': 499.90150976359365}
# {'Name': 'Truffle_Pig_2', 'x_coord': 499.2754299204255, 'y_coord': 550.6818320798665}
```


# Development
## Running Tests, Prettifying Code, and Updating Docs

Make sure Docker is installed and running on a Unix system (Linux, MacOS, WSL2).

- Create a docker container and drop into a shell
    - `./run.sh`
- Run all tests (see ./utils/test.sh)
    - `./run.sh test`
- Prettify the code (see ./utils/prettify.sh)
    - `./run.sh prettify`
- Update the docs (see ./utils/docs.sh)
    - `./run.sh docs`

- Note: You can and should modify the `Dockerfile` to test different python versions.
