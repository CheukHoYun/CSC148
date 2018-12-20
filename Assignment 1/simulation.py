"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    num_iterations: a record of how many rounds we simulated
    total_people: a record of how many people are generated and put into the
                  simulation
    people_completed: a record of how many people actually arrive their target
                      floor by the end of the simulation
    max_time: a record of the longest time taken for one to get to his target
              floor during the simulation.
    min_time: a record of the minimum time taken for one to get to his target
              floor during the simulation.
    total_time: a record of how much time in total is used for all people who
                arrive at their target floor. Used to calculate average time for
                stats.

    === Representation Invariants ===
    - num_floors > 0
    - len(elevators) > 0
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    num_iterations: int
    total_people: int
    people_completed: int
    max_time: int
    min_time: int
    total_time: float

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""
        self.num_floors = config['num_floors']
        self.elevators = []
        for i in range(0, config['num_elevators']):
            self.elevators.append(Elevator(config['elevator_capacity']))
        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']
        self.waiting = {}
        for i in range(1, self.num_floors + 1):
            self.waiting[i] = []
        self.num_iterations = 0
        self.total_people = 0
        self.people_completed = 0
        self.max_time = -1
        self.min_time = -1
        self.total_time = 0.0
        self.visualizer = Visualizer(self.elevators,
                                     self.num_floors,
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        for i in range(num_rounds):
            self.num_iterations += 1

            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

        return self._calculate_stats()

    def _angrier(self) -> None:
        """Make all passengers (either waiting or on elevator) get angrier
        for one level.
        """
        for e in self.elevators:
            for p in e.passengers:
                p.wait_time += 1
        for f in range(1, self.num_floors + 1):
            for p in self.waiting[f]:
                p.wait_time += 1

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals.

        For each arrival, add one to the total people record. This will be
        used for stats calculation.
        """
        g = self.arrival_generator.generate(round_num)
        for i in range(1, self.num_floors + 1):
            if i in g:
                self.waiting[i].extend(g[i])
                self.total_people += len(g[i])
        self.visualizer.show_arrivals(self.waiting)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators.

        Record the max and minimum wait time for people who leave. These will
        be used for stats calculation.
        """
        for e in self.elevators:
            remove_list = []
            for p in e.passengers:
                if p.target == e.position:
                    if p.wait_time < self.min_time or self.min_time == -1:
                        self.min_time = p.wait_time
                    if p.wait_time > self.max_time or self.max_time == -1:
                        self.max_time = p.wait_time
                    self.total_time += p.wait_time
                    remove_list.append(p)
                    self.people_completed += 1
            for p in remove_list:
                e.passengers.remove(p)
                self.visualizer.show_disembarking(p, e)

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for f in range(1, self.num_floors + 1):
            for e in self.elevators:
                while len(self.waiting[f]) > 0 and e.position == f and \
                        len(e.passengers) < e.capacity:
                    e.passengers.append(self.waiting[f][0])
                    self.visualizer.show_boarding(self.waiting[f][0], e)
                    del self.waiting[f][0]

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.

        Moving elevators is a sign of the end of a round. When it is done,
        all passengers (either in elevator or waiting for one) get angrier
        by one level (increment their wait time for 1 second).
        """
        alg = self.moving_algorithm
        moves = alg.move_elevators(self.elevators,
                                   self.waiting,
                                   self.num_floors)
        self.visualizer.show_elevator_moves(self.elevators, moves)
        i = 0
        for e in self.elevators:
            if moves[i] == Direction.UP:
                e.position += 1
            elif moves[i] == Direction.DOWN:
                e.position -= 1
            i += 1
        self._angrier()

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        avg_time = int(self.total_time / self.people_completed) \
            if self.people_completed > 0 else -1
        return {
            'num_iterations': self.num_iterations,
            'total_people': self.total_people,
            'people_completed': self.people_completed,
            'max_time': self.max_time,
            'min_time': self.min_time,
            'avg_time': avg_time
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 5,
        'num_elevators': 1,
        'elevator_capacity': 3,
        # This is likely not used.
        'num_people_per_round': 2,
        'arrival_generator': algorithms.FileArrivals(5,
                                                     'test_algorithms_10.csv'),
        'moving_algorithm': algorithms.ShortSighted(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
