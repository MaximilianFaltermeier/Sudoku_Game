from exception_class import SudokuError
from grid import Grid
from SudokuSolver import SudokuSolver


class SudokuBoardReader(object):
    """
    Sudoku Board representation
    """
    def __init__(self, board_file):
        self.board = Grid()
        for line, row in zip(board_file, self.board.rows):
            line = line.strip()
            if len(line) != 9:
                raise SudokuError("Each line in the sudoku puzzle must be 9 chars long.")

            for c, index in zip(line, range(9)):
                if c.isdigit() and 0 <= int(c) <= 9:
                    row[index].set_value(int(c), given=True)
                else:
                    raise SudokuError("Valid characters for a sudoku puzzle must be in 0-9")


class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """

    def __init__(self, board_file):
        self.game_over = False
        self.grid = Grid()
        self.board_file = board_file
        self.start_puzzle = SudokuBoardReader(board_file).board
        self.__solution = []

    def start(self):
        """
        Init the game and starts it
        """
        self.game_over = False
        for i in range(9):
            for j in range(9):
                self.grid[i, j].set_value(self.start_puzzle[i, j].get_value(), given=True)

    def get_solution(self):
        if len(self.__solution) == 0:
            self.__solution = SudokuSolver(self.start_puzzle).get_solution()
        return self.__solution

    def check_win(self):
        """
        Checks if game is finished
        :return: True if finished else False
        """
        for row in self.grid.rows:
            if not self.__check_block(row):
                return False
        for column in self.grid.columns:
            if not self.__check_block(column):
                return False
        for block in self.grid.blocks:
            if not self.__check_block(block):
                return False
        self.game_over = True
        return True

    @staticmethod
    def __check_block(block):
        """
        Checks if one grid component contains all numbers 1-9
        :param block: grid component to be investigated
        :return: True if all 9 numbers are present else False
        """
        return set([value.get_value() for value in block.cells]) == set(range(1, 10))

    def reset_board(self):
        self.start()
        self.grid.reset_possible_solutions_of_cells()
        self.grid.reset_possible_error()
