"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        Floor with no people arriving are not included in the dictionary.

        Precondition:
            round_num > 0
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.
    """
    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals, using the random algorithm.
        """
        if self.num_people is None:
            return {}
        elif self.num_people == 0:
            return {}
        else:
            d = {}
            i = 1
            while i <= self.num_people:
                while True:
                    p = Person(random.randint(1, self.max_floor),
                               random.randint(1, self.max_floor))
                    if p.start != p.target:
                        break
                if p.start in d:
                    d[p.start].append(p)
                else:
                    d[p.start] = []
                    d[p.start].append(p)
                i += 1
            return d


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.

    === Attributes ===
    record: A dictionary that maps round numbers to waiting passengers.
    """
    record: Dict[int, List[Person]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Preconditions:
            max_floor > 0
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)
        self.record = {}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.record[int(line[0])] = []
                for i in range(1, len(line), 2):
                    p = Person(int(line[i]), int(line[i + 1]))
                    self.record[int(line[0])].append(p)

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals, using the the data in record attribute,
        which takes and transforms data from given CSV file.
        """
        if round_num in self.record:
            record = self.record[round_num]
            g = {}
            for p in record:
                if p.start in g:
                    g[p.start].append(p)
                else:
                    g[p.start] = []
                    g[p.start].append(p)
            return g
        else:
            return {}


###############################################################################
# Elevator moving algorithms
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.

        Precondition:
            max_floor > 0
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        num_of_elevators = len(elevators)
        i = 0
        l = []
        while i < num_of_elevators:
            l.append(random.choice(list(Direction)))
            if 0 < elevators[i].position + l[i].value <= max_floor:
                i += 1
            else:
                del l[-1]
        return l


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """
    def _pushy_find(self, e: Elevator, waiting: Dict[int, List[Person]],
                    max_floor: int) -> Direction:
        """A helper function that returns a direction for an empty elevator.

        Should only be called inside PushyPassenger.move_elevator
        """
        least = -1
        for f in range(1, max_floor + 1):
            if f in waiting:
                if len(waiting[f]) > 0:
                    least = f
                    break
        if least == -1:
            return Direction.STAY
        else:
            if least > e.position:
                return Direction.UP
            else:
                return Direction.DOWN

    def _pushy_go(self, e: Elevator) -> Direction:
        """A helper function that returns a direction for an non-empty elevator.

        Should only be called inside PushyPassenger.move_elevator
        """
        if e.passengers[0].target > e.position:
            return Direction.UP
        else:
            return Direction.DOWN

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Using PushyPassenger algorithm, take in the current passengers and
        elevators' condition, return a list of movements for the according list
        of elevators.
        """
        l = []
        for e in elevators:
            if not e.passengers:
                d = self._pushy_find(e, waiting, max_floor)
            else:
                d = self._pushy_go(e)
            l.append(d)
        return l


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def _short_find(self, e: Elevator, waiting: Dict[int, List[Person]],
                    max_floor: int) -> Direction:
        """A helper function that returns a direction for an empty elevator.

        Should only be called inside ShortSighted.move_elevator
        """
        min_distance = 0
        target_floor = 0
        for f in range(1, max_floor + 1):
            if waiting[f]:
                if abs(f - e.position) < min_distance or target_floor == 0:
                    min_distance = abs(f - e.position)
                    target_floor = f
                elif abs(f - e.position) == min_distance:
                    if f < target_floor:
                        target_floor = f
        if target_floor == 0:
            return Direction.STAY
        elif target_floor > e.position:
            return Direction.UP
        else:
            return Direction.DOWN

    def _short_go(self, e: Elevator) -> Direction:
        """A helper function that returns a direction for an non-empty elevator.

        Should only be called inside ShortSighted.move_elevator
        """
        min_distance = -1
        target_floor = -1
        for p in e.passengers:
            if min_distance == -1 or \
                    abs(p.target - e.position) < min_distance:
                target_floor = p.target
            elif abs(p.target - e.position) == min_distance:
                if p.target < target_floor:
                    target_floor = p.target
            min_distance = abs(target_floor - e.position)
        if target_floor > e.position:
            return Direction.UP
        else:
            return Direction.DOWN

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Using ShortSighted algorithm, take in the current passengers and
        elevators' condition, return a list of movements for the according list
        of elevators.
        """
        l = []
        for e in elevators:
            if not e.passengers:
                d = self._short_find(e, waiting, max_floor)
            else:
                d = self._short_go(e)
            l.append(d)
        return l


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201']
    })
