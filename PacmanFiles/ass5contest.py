# Giorgia Corrado (s1017255)
# Diego Garcia Cerdas (s1020485)

from pacman import agents, gamestate, util, distancer
from pacman.util import Vector


class ContestAgent(agents.PacmanAgent):
    dist = distancer.Distancer
    searching = bool  # indicates whether Pac-man is searching for scared ghosts
    dead_ends = set()  # contains all the dead-ends in the game layout
    ghost_load = int  # stores the amount of ghosts in the layout

    LAYER = 100  # value to separate layers in the evaluation hierarchy
    BIG_VALUE = -pow(LAYER, 5)  # value to return for relatively bad game states

    def prepare(self, g_state: gamestate.Gamestate):
        """
        This method initializes the attributes of the class.
        """

        def get_dead_ends():
            """
            This method initializes the set of dead-ends for the layout.
            """
            for x in range(g_state.shape.x):
                for y in range(g_state.shape.y):
                    pos = util.Vector(x, y)  # for every coordinate in the layout
                    # if the coordinate is not a wall and has only two legal moves (is a dead-end)
                    if pos not in g_state.walls.list() and len(g_state.legal_moves_vector(pos)) == 2:
                        self.dead_ends.add(pos)  # add the dead-end to the set
            if self.ghost_load != 3:
                # for ghost_loads different than three, add the corners as dead-ends
                # this helps avoid being trapped or losing in open layouts
                self.dead_ends.add(util.Vector(1, 1))
                self.dead_ends.add(util.Vector(1, g_state.shape[1] - 2))
                self.dead_ends.add(util.Vector(g_state.shape[0] - 2, 1))
                self.dead_ends.add(util.Vector(g_state.shape[0] - 2, g_state.shape[1] - 2))

        self.dist = distancer.Distancer(g_state)  # initialize distance calculator
        distancer.Distancer.precompute_distances(self.dist)
        self.searching = False  # Pac-man is not looking for scared ghosts at the start
        self.ghost_load = len(g_state.ghosts)  # Obtain the amount of ghosts in the game state
        get_dead_ends()  # initialize the set containing dead-ends
        super().prepare(g_state)

    def move(self, g_state: gamestate.Gamestate) -> util.Move:
        """
        This method gets called every turn, asking the agent
        what move they want to make based on the current game state.
        """

        # scared stored all the currently scared ghosts in the game state
        scared = {(ghost, index) for index, ghost in enumerate(g_state.ghosts) if g_state.timers[index] != 0}
        # if there is at least one scared ghost, Pac-man will search for it
        if scared:
            self.searching = True
        else:
            self.searching = False

        # search for the move that yields the direct successor with the highest evaluation and return it
        moves = [move for move in g_state.legal_moves_id(0) if move != util.Move.stop]
        return max(moves, key=lambda x: self.evaluate(g_state.successor(0, x), 0, scared, g_state.pellets.list()))

    def evaluate(self, g_state: gamestate.Gamestate, depth: int, scared: set, pellets: list) -> float:
        """
        This method is used by the contest agent to determine
        the value of a given game state.
        :param g_state: game state to evaluate
        :param depth: current depth of the evaluation
        :param scared: set of scared ghosts
        :param pellets: pellets in the parent game state
        """

        def distance_closest_ghost() -> float:
            """
            This method returns the distance to the closest non-scared ghost in the game state.
            """
            # obtain a set of non-scared ghosts in the current game state
            not_scared = set(g_state.ghosts) - {ghost[0] for ghost in local_scared}
            if not not_scared:
                return 0
            # if Pac-man is not eaten by a ghost, return the inverse of the distance to closest ghost
            # inverse is calculated so that a higher distance results in a better score
            distance = min(self.dist.get_distance(g_state.pacman, ghost) for ghost in not_scared)
            return float('-inf') if distance == 0 else 1 / distance

        def best_pellet_value() -> float:
            """
            This method returns the weighted score for eating pellets.
            """
            if not g_state.pellets.list():
                return 0
            # obtain the distance to the closest pellet
            distance = min(self.dist.get_distance(g_state.pacman, pellet) for pellet in g_state.pellets.list())
            distance *= pow(self.LAYER, 1)  # distance is in layer 1 of the score hierarchy
            amount = len(g_state.pellets.list())  # obtain amount of remaining pellets
            amount *= pow(self.LAYER, 2)  # amount is in layer 2 of the score hierarchy
            return -(distance + amount)  # smaller distances and amounts yield a better score

        def best_dot_value() -> float:
            """
            This method returns the weighted score for eating dots.
            """
            if not g_state.dots.list():
                return 0
            # obtain the distance to the closest dot (in layer 0 of the score hierarchy)
            distance = min(self.dist.get_distance(g_state.pacman, dot) for dot in g_state.dots.list())
            amount = len(g_state.dots.list())  # obtain amount of remaining dots
            amount *= pow(self.LAYER, 1)  # amount is in layer 1 of the score hierarchy
            return -(distance + amount)  # smaller distances and amounts yield a better score

        def best_scared_ghost_value() -> float:
            """
            This method returns the weighted score for eating scared ghosts.
            """
            if not local_scared:
                return 0
            # obtain the distance to the closest scared ghost (in layer 0 of the score hierarchy)
            distance = min(self.dist.get_distance(g_state.pacman, ghost[0]) for ghost in local_scared)
            amount = len(local_scared)  # obtain amount of remaining scared ghosts
            amount *= pow(self.LAYER, 2)  # amount is in layer 2 of the score hierarchy
            return -(distance + amount)  # smaller distances and amounts yield a better score

        def crossroad_value() -> float:
            """
            This method returns the number of accessible crossroads from the current Pac-man position.
            Mostly based on the worked-out assignment 2 (bonus) uploaded to Brightspace.
            """

            def legal_moves(pos: Vector, state: gamestate.Gamestate):
                """
                This method returns the legal moves from a given position, excluding stop.
                """
                moves = []
                # for every move (except stop) add it to moves list if next position is not a wall
                for move in util.Move.no_stop:
                    vector = pos + move.vector
                    if vector not in state.walls.list():
                        moves.append(move)
                return moves

            # obtain a list of non scared ghosts
            ghosts = set(g_state.ghosts) - {ghost[0] for ghost in local_scared}
            successors = []
            # look for crossroads by following a path from the current position
            # if a ghost or dead end is found, the crossroad is discarded
            for first_move in legal_moves(g_state.pacman, g_state):
                dead = False
                position = g_state.pacman + first_move.vector
                if position in ghosts or position in self.dead_ends:
                    dead = True
                path = [first_move]
                next_moves = [move for move in legal_moves(position, g_state) if move != path[-1].opposite]
                while not dead and len(next_moves) == 1:
                    position = position + next_moves[0].vector
                    if position in ghosts or position in self.dead_ends:
                        dead = True
                        break
                    path.append(next_moves[0])
                    next_moves = [move for move in legal_moves(position, g_state) if move != path[-1].opposite]
                if not dead:
                    successors.append(position)
            return len(successors)  # return the amount of crossroads from the current position

        def get_addition() -> float:
            """
            This method returns the additional value fine-tuned to each ghost load in the layout.
            """
            if self.ghost_load == 3:
                # for a ghost load of three, calculate how restricted is Pac-man in the current position
                value = len(g_state.legal_moves_id(0))
                # in a shallow depth, calculate the amount of accessible crossroads
                if depth == 0:
                    value += crossroad_value()
            elif self.ghost_load >= 4:
                # for a ghost load higher or equal to four, Pac-man will try to avoid approaching ghosts
                value = -distance_closest_ghost()
            else:
                # for any other ghost load, simply calculate the score of the current game state
                value = g_state.score
            return value

        def get_deep_value() -> float:
            """
            This method returns the minimum score for the successors of the current game state.
            """
            if depth < 1:
                # if current is not the deepest level accessible, get minimum successor score
                return min(
                    self.evaluate(g_state.successor(0, move), depth + 1, local_scared, g_state.pellets.list()) for move
                    in g_state.legal_moves_id(0))
            return 0

        if g_state.loss:  # if Pac-man is destined to lose in this state, return lowest possible score
            return float('-inf')

        # make a copy of the scared ghosts set to modify locally
        local_scared = scared.copy()
        for ghost_pos, index in local_scared:  # for each scared ghost, if Pac-man is eating it,
            if ghost_pos == g_state.pacman:
                # if Pac-man will die after eating it, return a high negative score
                if ghost_pos == g_state.starts[index + 1] and self.ghost_load == 3:
                    return self.BIG_VALUE
                g_state.kill(index + 1)  # kill the ghost in the current game state
                # update list of scared ghosts
                local_scared = {(ghost, index) for index, ghost in enumerate(g_state.ghosts) if
                                g_state.timers[index] != 0}

        # check if Pac-man is currently eating a pellet
        ate_pellet_searching = self.searching and g_state.pacman in pellets
        # check if Pac-man is trapped in a dead-end
        is_trapped = distance_closest_ghost() == 1 and g_state.pacman in self.dead_ends
        # if one of these happens, return a high negative value
        if ate_pellet_searching or is_trapped:
            return self.BIG_VALUE

        deep_value = get_deep_value()  # calculate deeper score
        addition = get_addition()  # calculate additional score

        if self.searching:
            # if Pac-man is searching for ghosts, return value for best scared ghost, plus additional ones
            return best_scared_ghost_value() + deep_value + addition
        # in any other occasion, return value for best pellet and dot, plus additional ones
        return best_pellet_value() + best_dot_value() + deep_value + addition
