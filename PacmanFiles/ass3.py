# Giorgia Corrado (s1017255)
# Diego Garcia Cerdas (s1020485)

from pacman import agents, search, util
from typing import NamedTuple, FrozenSet
import exceptions
import ass2
import itertools

# State includes a vector with the current position and a list of remaining corners
CornerSearchState = NamedTuple('CornerSearchState', [('vector', util.Vector), ('corners', FrozenSet[util.Vector])])


class CornersSearchRepresentation(search.SearchRepresentation):
    def __init__(self, gstate):
        super().__init__(gstate)
        self.walls = gstate.walls
        self.start_position = gstate.pacman
        left, bottom = 1, 1
        right, top = gstate.shape - 2 * util.Vector.unit
        self.corners = frozenset([util.Vector(left, bottom),
                                  util.Vector(left, top),
                                  util.Vector(right, bottom),
                                  util.Vector(right, top)])

    @property
    def start(self):
        return CornerSearchState(self.start_position, self.corners)  # create a new starting CornerSearchState

    def is_goal(self, state):
        super().is_goal(state.vector)
        return not state.corners  # check if there is no remaining corner

    def successors(self, state):
        successors = []
        for move in util.Move.no_stop:  # for every possible move
            new_vector = state.vector + move.vector  # create a new vector
            if not self.walls[new_vector]:  # if new vector is not a wall
                new_corners = state.corners - {new_vector}  # remove a possible corner
                successor = (CornerSearchState(new_vector, new_corners), [move], 1)  # create successor state
                successors.append(successor)  # add successor to the list
        return successors

    def pathcost(self, path):
        return search.standard_pathcost(path, self.start_position, self.walls)


# Many choices are possible here, as long as they are admissible.
# Examples include the Manhattan distance to the closest corner, fastest corner, etc.
# It is also possible to use the costs of Manhattan paths from the player through
# all remaining corners, but admissibility must be ensured.
# An often-chosen but *inadmissible* heuristic is choosing a Manhattan path greedily.
# By trying all possible corner orders, we can ensure that there is no path
# with less cost than the returned heuristic value.
def corners_heuristic(state: tuple, representation: CornersSearchRepresentation) -> int:
    """
    Calculates the heuristic to the closest unvisited corner for a given position.

    :param state: (tuple) the vector of the position in question and a tuple of bools for the visited corners.
    :param representation: (CornersSearchRepresentation) the search representation.

    :returns: (int) the heuristic value to the closest corner.
    """
    position, visited = state
    corners = [c for c, vis in zip(representation.corners, visited) if not vis]
    return min(manhattan_path_cost((position,) + corner_path) for corner_path in itertools.permutations(corners))


# Again, many choices possible, as long as they are admissible
# and not prohibitively inefficient. This heuristic is the same
# as the corners heuristic above, but for the foods closest to each corner
# rather than the corners themselves.
def dots_heuristic(state: tuple, representation: CornersSearchRepresentation) -> int:
    """
    Calculates the heuristic to the foods closest to each corner.

    :param state: (tuple) the vector of the position in question and a tuple of bools for the visited corners.
    :param representation: (CornersSearchRepresentation) the search representation.

    :returns: (int) the heuristic value to the closest corner.
    """
    if state.dots:
        left, bottom = 1, 1
        right, top = representation.walls.shape - 2 * util.Vector.unit
        corners = frozenset([util.Vector(left, bottom), util.Vector(left, top),
                             util.Vector(right, bottom), util.Vector(right, top)])

        def closest_dot(corner):
            return min(state.dots, key=lambda dot: sum(abs(dot - corner)))

        closest_to_corners = {closest_dot(corner) for corner in corners}
        return min(manhattan_path_cost((state.vector,) + corner_path) for corner_path in itertools.permutations(closest_to_corners))
    else:
        return 0


def manhattan_path_cost(path: tuple) -> int:
    """
    Manhattan cost for a path

    :param path: (tuple) the path for which to calculate a cost

    :returns: (int) the cost
    """
    position = path[0]
    cost = 0
    for next_position in path[1:]:
        cost += util.manhattan(next_position, position)
        position = next_position
    return cost


class ClosestDotSearchAgent(agents.SearchAgent):
    def prepare(self, gstate):
        self.actions = []
        pacman = gstate.pacman
        while gstate.dots:
            next_segment = self.path_to_closest_dot(gstate)
            self.actions += next_segment
            for move in next_segment:
                if move not in gstate.legal_moves_vector(gstate.agents[self.id]):
                    raise Exception('path_to_closest_dot returned an illegal move: {}, {}'.format(move, gstate))
                gstate.apply_move(self.id, move)

        print(f'[ClosestDotSearchAgent] path found with length {len(self.actions)}'
              f' and pathcost {search.standard_pathcost(self.actions, pacman, gstate.walls)}')

    @staticmethod
    def path_to_closest_dot(gstate):
        representation = AnyDotSearchRepresentation(gstate)  # Create a new representation
        return ass2.uniformcost(representation)  # Use a uniform cost search


class AnyDotSearchRepresentation(search.PositionSearchRepresentation):
    def __init__(self, gstate):
        super().__init__(gstate)
        self.dots = gstate.dots

    def is_goal(self, state):
        super().is_goal(state)
        return state in self.dots.list()  # Pacman is currently in a dot position


class ApproximateSearchAgent(agents.SearchAgent):
    def prepare(self, gstate):
        pass

    def move(self, gstate):
        raise exceptions.EmptyBonusAssignmentError
