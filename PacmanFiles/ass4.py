# Giorgia Corrado (s1017255)
# Diego Garcia Cerdas (s1020485)

import ass2
from ass3 import AnyDotSearchRepresentation
from pacman.gamestate import Gamestate
from pacman import agents, gamestate, util


class BetterReflexAgent(agents.ReflexAgent):
    # Our evaluate function ranks moves in 5 categories, explained below
    def evaluate(self, gstate, move):
        successor = gstate.successor(self.id, move)  # get the successor derived from the given move
        for ghost_index in range(1, len(gstate.active_agents)):  # for each ghost index in the world
            ghost = gstate.active_agents[ghost_index]  # get the ghost with the index
            for ghost_move in util.Move.no_stop:  # get all possible moves of the ghost
                ghost_successor = ghost + ghost_move.vector  # calculate the next ghost position after the given move
                # if ghost will end up in the same position as Pac-man or Pac-man will die with this ghost
                if ghost_successor == successor.pacman or successor.pacman is None:
                    if gstate.timers[ghost_index - 1] > 1:  # if ghost is currently scared
                        return 5  # 5 points as this would be better than any other move
                    return 0  # 0 points as this would imply Pac-man to die
        if move == util.Move.stop:  # if the move implies Pac-man to remain still
            return 1  # 1 point as it is better to make a move (so it doesn't remain still all the time)
        for dot in gstate.dots.list():  # if the move implies Pac-man eating a food dot
            if dot == successor.pacman:
                return 3  # 3 points so Pac-Man is encouraged to eat it
        for pellet in gstate.pellets.list():  # if the move implies Pac-man eating a pellet
            if pellet == successor.pacman:
                return 4  # 4 points so Pac-man prefers pellets over food
        return 2  # 2 points fot moving to an empty space


class MinimaxAgent(agents.AdversarialAgent):
    def move(self, gstate):
        # Minimax function based on Poole&Mackworth pseudo-code (fig. 11.6 in ed.2)
        # is_max establishes a move for Pac-man (max) or for the ghost (min)
        # depth establishes the current ply, only increases after a min move
        def minimax(gstate: Gamestate, is_max: bool, depth):
            best_move = None  # Initialize the move to return
            if gstate.win or gstate.loss or depth == self.depth:  # If depth is reached or the game is over
                return self.evaluate(gstate)  # Evaluate this (leaf) node
            if is_max:  # If state is a max state
                best_score = -float('inf')  # Initialize best possible score
                for move in gstate.legal_moves_id(0):  # For each possible move for Pac-man
                    # Calculate the score recursively, getting the successor for the given move
                    # is_max is set to False (as next move is the ghost's) and depth stays the same
                    score = minimax(gstate.successor(0, move), False, depth)
                    if score > best_score:  # If this score is the current best, update best score and move
                        best_score = score
                        best_move = move
                if depth == 0:  # If this is the first Pac-man move
                    return best_move  # Return the move to make
                return best_score  # Else return the score for the max state
            else:  # If state is a min state
                best_score = float('inf')  # Initialize best possible score
                for successor in gstate.successors(1):  # For each successor of the min state (ghost move)
                    # Calculate the score recursively
                    # is_max is set to True (as next move is Pac-man's) and depth increases
                    score = minimax(successor, True, depth + 1)
                    best_score = min(best_score, score)  # Update the best score
                return best_score  # Return the score for the min state

        # Return the best first move by using minimax function, using True for max agent and starting depth 0
        return minimax(gstate, True, 0)


class AlphabetaAgent(agents.AdversarialAgent):
    def move(self, gstate):
        # Minimax alpha-beta function based on Poole&Mackworth pseudo-code (fig. 11.6 in ed.2)
        # is_max establishes a move for Pac-man (max) or for the ghost (min)
        # depth establishes the current ply, only increases after a min move
        def minimax_alpha_beta(gstate: Gamestate, is_max: bool, depth, alpha, beta):
            best_move = None  # Initialize the move to return
            if gstate.win or gstate.loss or depth == self.depth:  # If depth is reached or the game is over
                return self.evaluate(gstate)  # Evaluate this (leaf) node
            if is_max:  # If state is a max state
                for move in gstate.legal_moves_id(0):  # For each possible move for Pac-man
                    # Calculate the score recursively, getting the successor for the given move
                    # is_max is set to False (as next move is the ghost's) and depth stays the same
                    score = minimax_alpha_beta(gstate.successor(0, move), False, depth, alpha, beta)
                    if score >= beta:  # If score is greater or equal to beta, prune this branch
                        return score
                    elif score > alpha:  # Update alpha and best move
                        alpha = score
                        best_move = move
                if depth == 0:  # If this is the first Pac-man move
                    return best_move  # Return the move to make
                return alpha  # Else return the score for the max state (alpha value)
            else:  # If state is a min state
                for successor in gstate.successors(1):  # For each successor of the min state (ghost move)
                    # Calculate the score recursively
                    # is_max is set to True (as next move is Pac-man's) and depth increases
                    score = minimax_alpha_beta(successor, True, depth + 1, alpha, beta)
                    if score <= alpha:  # If score is less than or equal to alpha, prune this branch
                        return score
                    else:  # Update beta
                        beta = min(beta, score)
                return beta  # Return the score for the min state (beta value)

        # Return the best first move by using minimax_alpha_beta, using True for max agent and starting depth 0
        # Alpha is initialized to least possible value and beta to biggest possible value
        return minimax_alpha_beta(gstate, True, 0, -float('inf'), float('inf'))


def better_evaluate(gstate):
    if gstate.loss:  # if state is a loss, return the biggest possible value
        return -float('inf')  # this helps avoid collisions with active ghosts

    level = 100  # a level value high enough for weights not to influence each other

    def distance_closest_food(gstate):  # distance to closest dot, using uniform cost search
        if not gstate.dots.list():  # if there are no more dots, do not take this into account
            return 0
        representation = AnyDotSearchRepresentation(gstate)
        return len(ass2.uniformcost(representation))

    # The better_evaluate function has the following hierarchy:
    # - 3 - Prefer eating pellets over everything else, as it is possible to obtain much more points
    # - 2 - After eating a pellet, Pac-man will try to eat a scared ghost
    # - 1 - Approaching scared ghosts and eating food are evaluated on the same level, making the most appropriate move
    # - 0 - When nothing else is possible, Pac-man will eat the closest possible food dot

    def scared_ghost_value(gstate):  # a value for chasing scared ghosts when possible
        distance = float('inf')
        # list of scared ghosts
        scared = [gstate.ghosts[x] for x in range(len(gstate.ghosts)) if gstate.timers[x] != 0]
        if not scared:  # if there are no scare ghosts, do not take this into account
            return 0
        for ghost in scared:  # get the distance to closest scared ghost
            distance = min(distance, util.manhattan(gstate.pacman, ghost))
        # distance to closest scared ghost has level 1 weight
        # amount of scared ghosts has level 2 weight
        return -(distance * pow(level, 1) + len(scared) * pow(level, 2))

    def best_dot_value(gstate):  # a value for eating food and pellets
        food = len(gstate.dots.list()) * pow(level, 1)  # amount of remaining food has level 1 weight
        pellets = len(gstate.pellets.list()) * pow(level, 3)  # amount of remaining pellets has level 3 weight
        distance = distance_closest_food(gstate) * pow(level, 0)  # distance to closest dot has level 0 weight
        return -(food + distance + pellets)

    # return the weighted values for dots and scared ghosts
    return best_dot_value(gstate) + scared_ghost_value(gstate)


class MultiAlphabetaAgent(agents.AdversarialAgent):
    # The only thing that changes w.r.t. alpha-beta pruning above
    # is that we have an index for the agent rather than True/False,
    # where depth is only increased for the last ghost agent,
    # and we have a separate beta for each agent. We prune if any
    # agent's beta is smaller or equal than alpha.

    def move(self, gstate: gamestate.Gamestate):
        """
        Finds the next move.

        :param gstate: (gamestate.Gamestate) the current gamestate

        :returns: (enum<Move>) the move to make
        """
        alpha = float('-inf')
        beta = float('inf')
        move_values = []

        for move in gstate.legal_moves_id(0):
            if move != util.Move.stop:
                value = self.alphabeta(
                    gstate.successor(0, move), 0, alpha, beta, 1)
                move_values.append((move, value))
                alpha = max(alpha, value)

        return max(move_values, key=lambda x: x[1])[0]

    def alphabeta(self, gstate, depth: int, alpha: int, beta: float, agent_id: int) -> int:
        """
        Evaluates a potential move.

        :param state: (gamestate.Gamestate) gamestate if the move to be evaluated is made
        :param depth: (int) depth of the search
        :param alpha: (int) pruning alpha
        :param beta: (float) pruning beta
        :param agent_id: (int) recursion through ghosts

        :returns: (int) value of the move
        """
        if depth == self.depth or gstate.gameover:
            return self.evaluate(gstate)

        if agent_id == 0:
            best_value = float('-inf')
            for successor in gstate.successors(0):
                best_value = max(best_value, self.alphabeta(
                    successor, depth, alpha, beta, agent_id + 1))
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
        else:
            best_value = float('inf')
            for successor in gstate.successors(agent_id):
                best_value = min(best_value, self.alphabeta(successor, depth + (agent_id + 1) // len(gstate.agents),
                                                            alpha, beta, (agent_id + 1) % len(gstate.agents)))
                beta = min(beta, best_value)
                if alpha >= beta:
                    break
        return best_value

