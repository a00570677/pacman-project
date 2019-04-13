# Giorgia Corrado (s1017255)
# Diego Garcia Cerdas (s1020485)

from pacman import search, util
import queue


def depthfirst(representation: search.PositionSearchRepresentation) -> list:
    """
    Search the deepest nodes in the tree first.

    Any Pacman search representation should provide the three functions below.
    To get started, you might want to try them out in order to understand the search representation that is being passed in:

    print("Start:", representation.start)
    print("Is the start a goal?", representation.is_goal(representation.start))
    print("Start's successors:", representation.successors(representation.start))

    For Pacman search problems, a search state is a position tuple (x,y), representation.start() returns such a state
    (but correct search code should be able to work with any (hashable) search state).
    The function representation.successors(state) returns a list of successors of state,
    where each successor is a tuple of the successor state, the list of action(s) to get from the parent state to the successor state,
    and the cost of that/those action(s).

    :param representation: (search.PositionSearchRepresentation) the search representation being passed in.
    :returns: (list) of actions comprising the found path
    """

    frontier = queue.LifoQueue()  # Stack frontier
    explored = set()  # Set of explored nodes
    frontier.put((representation.start, [], 0))  # Initialize frontier with start node
    while frontier:  # while the frontier is not empty
        node_vector, node_action, node_cost = frontier.get()  # get next element in frontier and remove it
        if node_vector in explored:  # if node has already been explored, continue
            continue
        explored.add(node_vector)  # else, add node to the explored list
        if representation.is_goal(node_vector):  # if goal state is found
            return node_action
        for x, y, z in representation.successors(node_vector):  # for each successor of the node
            if x not in explored:  # if successor has not yet been explored
                frontier.put((x, node_action + y, node_cost + z))  # add it to the frontier
    return None


def breadthfirst(representation: search.PositionSearchRepresentation) -> list:
    """
    Search the shallowest nodes in the search tree first

    :param representation: (search.PositionSearchRepresentation) the search representation being passed in.
    :returns: (list) of actions comprising the found path
    """

    # Same algorithm, but now frontier is a Queue
    frontier = queue.Queue()
    explored = set()
    frontier.put((representation.start, [], 0))
    while frontier:
        node_vector, node_action, node_cost = frontier.get()
        if node_vector in explored:
            continue
        explored.add(node_vector)
        if representation.is_goal(node_vector):
            return node_action
        for x, y, z in representation.successors(node_vector):
            if x not in explored:
                frontier.put((x, node_action + y, node_cost + z))
    return None


def uniformcost(representation: search.PositionSearchRepresentation) -> list:
    """
    Search the node of least total cost first.

    :param representation: (search.PositionSearchRepresentation) the search representation being passed in.
    :returns: (list) of actions comprising the found path
    """

    # Same algorithm, but now frontier is a Priority Queue
    frontier = queue.PriorityQueue()
    explored = set()
    frontier.put((0, (representation.start, [], 0)))
    while frontier:
        node_vector, node_action, node_cost = frontier.get()[1]
        if node_vector in explored:
            continue
        explored.add(node_vector)
        if representation.is_goal(node_vector):
            return node_action
        for x, y, z in representation.successors(node_vector):
            if x not in explored:
                frontier.put((node_cost + z, (x, node_action + y, node_cost + z)))
    return None


def astar(representation: search.PositionSearchRepresentation, heuristic: 'Callable' = search.null) -> list:
    """
    Search the node that has the lowest combined cost and heuristic first.

    :param representation: (search.PositionSearchRepresentation) the search representation being passed in.
    :param heuristic: This heuristic is a function with the following arguments: heuristic(position, representation)
    :returns: (list) of actions comprising the found path
    """

    frontier = util.PriorityFunctionQueue(
        lambda search_state: heuristic(search_state[0], representation) + search_state[2])
    explored = set()
    frontier.put((representation.start, [], 0))
    while frontier:
        node_vector, node_action, node_cost = frontier.get()
        if node_vector in explored:
            continue
        explored.add(node_vector)
        if representation.is_goal(node_vector):
            return node_action
        for x, y, z in representation.successors(node_vector):
            if x not in explored:
                frontier.put((x, node_action + y, node_cost + z))
    return None


class CrossroadSearchRepresentation(search.PositionSearchRepresentation):
    def successors(self, state):
        """
        Returns a list of successors, which are (position, moves, cost) tuples.
        """
        successors = []
        for first_move in self.legal_moves(state):
            position = state + first_move.vector
            path = [first_move]
            next_moves = [move for move in self.legal_moves(position) if move != path[-1].opposite]
            while len(next_moves) == 1:
                position = position + next_moves[0].vector
                path.append(next_moves[0])
                next_moves = [move for move in self.legal_moves(position) if move != path[-1].opposite]
            successors.append((position, path, len(path)))
        return successors

    def legal_moves(self, position):
        moves = []
        for move in util.Move.no_stop:
            vector = position + move.vector
            if not self.walls[vector]:
                moves.append(move)
        return moves
