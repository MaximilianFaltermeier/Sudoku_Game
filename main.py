import tkinter
from tkinter import Tk, Frame
from grid import Grid
from exception_class import SudokuError
from interface import SudokuUI, WIDTH, HEIGHT

BOARDS = ['debug', 'n00b', 'l33t', 'error']  # Available sudoku boards


class SudokuBoard(object):
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
        self.puzzle = Grid()
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        for i in range(9):
            for j in range(9):
                self.puzzle[i, j].set_value(self.start_puzzle[i, j].get_value(), given=True)
        self.puzzle.update_possible_solutions_of_cells()

    def check_win(self):
        for row in self.puzzle.rows:
            if not self.__check_block(row):
                return False
        for column in self.puzzle.columns:
            if not self.__check_block(column):
                return False
        for block in self.puzzle.blocks:
            if not self.__check_block(block):
                return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set([value.get_value() for value in block.cells]) == set(range(1, 10))


if __name__ == '__main__':
    board_name = 'n00b'
    with open('sudokus/%s.sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 50))
        root.mainloop()
