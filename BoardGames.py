########################################
# CS63: Artificial Intelligence, Lab 5
# Spring 2024, Swarthmore College
########################################
# NOTE: you should not need to modify this file.
########################################


class _base_game:
    """Base 'game' type, intended as an abstract class
    interface for 2-player deterministic board games.

    This class is not intended to be directly instanciated!  
    """

    # unicode characters for pretty-printing games
    EMPTY = u"\u00B7"
    RED   = u"\033[1;31m"
    BLUE  = u"\033[1;34m"
    RESET = u"\033[0;0m"

    CIRCLE = u"\u25CF"
    SQUARE = u"\u2588"

    RED_DISK = RED + CIRCLE + RESET
    BLUE_DISK = BLUE + CIRCLE + RESET


    def __repr__(self):
        """A unicode representation of the board state."""
        if self._repr is None:
            self._repr = "\n".join(" ".join(map(self._print_char, row)) for row in self.board)
            self._repr += "   " + self._print_char(self.turn) + " to move\n"
        return self._repr

    def __hash__(self):
        """use __repr__ as a hashing function"""
        if self._hash is None:
            self._hash = hash(repr(self))
        return self._hash

    def _print_char(self, i):
        if i > 0:
            return self.BLUE_DISK
        if i < 0:
            return self.RED_DISK
        return self.EMPTY # empty cell


    """
    remaining 'methods' just serve as prototypes that must by overriden
    by subclasses
    """
    def makeMove(self, move):
        """Returns a new game instance in which move has been played.
        """
        raise NotImplementedError("Interface class, should not be instanciated")

    @property
    def availableMoves(self):
        """List of legal moves for the current player."""
        raise NotImplementedError("Interface class, should not be instanciated")

    @property
    def isTerminal(self):
        """Boolean indicating whether the game has ended."""
        raise NotImplementedError("Interface class, should not be instanciated")

    @property
    def winner(self):
        """+1 if the first player (maximizer) has won. -1 if the second player
        (minimizer) has won. 0 if the game is a draw. Raises an AttributeError
        if accessed on a non-terminal state."""
        raise NotImplementedError("Interface class, should not be instanciated")

