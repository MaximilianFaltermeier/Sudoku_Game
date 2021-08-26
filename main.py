from tkinter import Tk
from SudokuGame import SudokuGame
from interface import SudokuUI, WIDTH, HEIGHT

BOARDS = ['debug', 'n00b', 'l33t', 'error']  # Available sudoku boards
INITIAL_BOARD = 'n00b'

if __name__ == '__main__':
    with open('sudokus/%s.sudoku' % INITIAL_BOARD, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH+380, HEIGHT + 40))
        root.mainloop()
