########################################
# CS63: Artificial Intelligence, Lab 5
# Spring 2024, Swarthmore College
########################################

#NOTE: You will probably want to use these imports. Feel free to add more.
from math import log, sqrt
from random import choice

class Node:
    """Node used in MCTS"""
    def __init__(self, state):
        self.state = state
        self.children = {} # maps moves to Nodes
        self.visits = 0    # number of times node was in select/expand path
        self.wins = 0      # number of wins for player +1
        self.losses = 0    # number of losses for player +1
        self.value = 0     # value (from player +1's perspective)
        self.untried_moves = list(state.availableMoves) # moves to try 
        
    def updateValue(self, outcome):
        """
        Increments self.visits.
        Updates self.wins or self.losses based on the outcome, and then
        updates self.value. 

        This function will be called during the backpropagation phase
        on each node along the path traversed in the selection and 
        expansion phases.

        outcome: Who won the game. 
                 +1 for a 1st player win
                 -1 for a 2nd player win
                  0 for a draw
        """

        # increment wins / losses accordingly
        if outcome == 1:
            self.wins += 1
        elif outcome == -1:
            self.losses += 1
        # increment visits
        self.visits += 1
        # calculate the value with updated data
        self.value = 1 + ((self.wins-self.losses)/self.visits)

    def UCBWeight(self, UCB_const, parent_visits, parent_turn):
        """
        Weight from the UCB formula used by parent to select a child.

        This function calculates the weight for JUST THIS NODE. The
        selection phase, implemented by the MCTSPlayer, is responsible
        for looping through the parent Node's children and calling
        UCBWeight on each.
        
        UCB_const: the C in the UCB formula.
        parent_visits: the N in the UCB formula.
        parent_turn: Which player is making a decision at the parent node.
           If parent_turn is +1, the stored value is already from the
           right perspective. If parent_turn is -1, value needs to be
           converted to -1's perspective.
        returns the UCB weight calculateduntried_moves[0]
        """

        # UCB Weight formula from https://mcts.ai/about/index.html
        exploration = UCB_const * sqrt(log(parent_visits)/self.visits)

        # adjust the exploitation value for +1 or -1 player
        if parent_turn == -1:
            exploitation = 2 - self.value
        else:
            exploitation = self.value
        
        weight = exploitation + exploration

        return weight

class MCTSPlayer:
    """Selects moves using Monte Carlo tree search."""
    def __init__(self, num_rollouts=1000, UCB_const=1.0):
        self.name = "MCTS"
        self.num_rollouts = int(num_rollouts)
        self.UCB_const = UCB_const
        self.nodes = {} # dictionary that maps states to their nodes

    def getMove(self, game_state):
        """Returns best move from the game_state after applying MCTS"""
        # find existing node in tree or create a node for game_state
        # and add it to the tree
        # call MCTS to perform rollouts
        # return the best move from the current player's perspective

        # find or create node for game_state
        key = str(game_state)
        # if key is already in nodes{}, it has been explored at least once
        if key in self.nodes:
            curr_node = self.nodes[key]
        # if key is not, add this untried move to the tree
        else:
            curr_node = Node(game_state)
            self.nodes[key] = curr_node

        # perform MCTS
        self.MCTS(curr_node)

        # determine the best move from that node
        bestValue = -float("inf")
        bestMove = None

        for move, child_node in curr_node.children.items():
            if curr_node.state.turn == 1: 
                value = child_node.value
            else:
                value = 2 - child_node.value

            if value > bestValue:
                bestValue = value
                bestMove = move

        return bestMove

    def status(self, node):
        """
        This method is used solely for debugging purposes. Given a 
        node in the MCTS tree, reports on the node's data (wins, losses,
        visits, values), as well as the data of all of its immediate
        children. Helps to verify that MCTS is working properly.
        Returns: None
        """
        print(f'root wins {node.wins}, losses {node.losses}, visits {node.visits}, value {node.value}\n')

        for move, child in node.children.items():
            print(f'    child wins {child.wins}, losses {child.losses}, visits {child.visits}, value {child.value} move {move}\n')
        
    # HELPER FUNCTIONS FOR MCTS

    # selection() takes in a node as a param and returns a list of nodes as a path
    def selection(self, node):
        # initialize path and add node to path
        path = []
        path.append(node)

        # if there are no untried moves left, that means the node has been expanded
        # add the node to path and look for the next node with the best UCB score
        while len(node.untried_moves) == 0 and not node.state.isTerminal:
            best_child = None
            # look through the child nodes to see who has the highest UCB value
            for child in node.children.values():
                if best_child == None:
                    best_child = child
                else:
                    if child.UCBWeight(self.UCB_const, node.visits, node.state.turn) > best_child.UCBWeight(self.UCB_const, node.visits, node.state.turn):
                        best_child = child
            # set the best child as the new node and add it to path
            node = best_child
            path.append(node)
        
        # if we made it out of the while loop, the node is not fully expanded
        return path

    # expansion() takes in a node as a param and returns a random untried move node
    def expansion(self, node):
        # randomly selects a move that has not been tried
        random_move = choice(node.untried_moves)
        idx = node.untried_moves.index(random_move)
        node.untried_moves.pop(idx) # pops the selected random move from untried_moves

        # make the random move a node
        random_move_node = Node(node.state.makeMove(random_move))

        # add the expanded node into the tree as well as node's children
        key = str(random_move_node.state)
        self.nodes[key] = random_move_node
        node.children[random_move] = random_move_node

        return random_move_node

    # simulation() takes in a starting game_state to start performing rollouts from and returns the outcome
    def simulation(self, game_state):
        # while the game is not finished
        while not game_state.isTerminal:
            # make a random move
            random_move = choice(game_state.availableMoves)
            new_game_state = game_state.makeMove(random_move)
            game_state = new_game_state
        
        # if we exit the while loop, that means the game finished
        return game_state.winner

    # backpropagation() takes in a path and the outcome of the rollout and updates all nodes in the path
    def backpropagation(self, path, outcome):
        for node in path:
            node.updateValue(outcome)
    
    def MCTS(self, current_node):
        """
        Plays out random games from the current node to a terminal state.
        Each rollout consists of four phases:
        1. Selection: Nodes are selected based on the max UCB weight.
                      Ends when a node is reached where not all children 
                      have been expanded.
        2. Expansion: A new node is created for a random unexpanded child.
        3. Simulation: Uniform random moves are played until end of game.
        4. Backpropagation: Values and visits are updated for each node
                     on the path traversed during selection and expansion.
        Returns: None
        """
        # Create helper functions for each phase: selection, expansion, simulation, backpropagation
        # after all rollouts completed, call status on current_node
        # to view a summary of results 

        for i in range(self.num_rollouts):
            path = self.selection(current_node)
            selected_node = path[-1]

            if selected_node.state.isTerminal:
                outcome = selected_node.state.winner
            else:
                next_node = self.expansion(selected_node)
                path.append(next_node)
                outcome = self.simulation(next_node.state)
            
            self.backpropagation(path, outcome)
        
        self.status(current_node)


