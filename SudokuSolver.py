import numpy as np
from exception_class import SudokuError


class SudokuSolver:
    def __init__(self, grid):
        self._sudoku = np.zeros((9, 9))
        for i in range(9):
            for j in range(9):
                if grid[i, j].given:
                    self._sudoku[i, j] = grid[i, j].get_value()
        self._state = self._sudoku.copy()

    def get_solution(self):
        """
        Tree like search for solution of sudoku.
        Search-tree is here a list:
        -> makes depth-first-search (DFS) in this use case more efficient.
        -> no actual tree is build
        :return: np.array of finished sudoku
        """
        frontier = [self._state]
        while not len(frontier) == 0:
            self._state = frontier.pop()
            if self.__check_if_finished():
                return self._state

            idx, idy = self.__find_zero()
            for digit in range(1, 10):
                state_copy = self._state.copy()
                state_copy[idx, idy] = digit
                if self.__check_if_valid(state_copy, idx, idy):
                    frontier.append(state_copy)
        raise SudokuError("SudokuSolver couldn't find a solution")

    @staticmethod
    def __check_if_valid(state_copy, current_row, current_column):
        new_entry = state_copy[current_row, current_column]
        # checks validity of row
        for column in range(9):
            if column == current_column:
                pass
            elif new_entry == state_copy[current_row, column]:
                return False
        # checks validity of column
        for row in range(9):
            if row == current_row:
                pass
            elif new_entry == state_copy[row, current_column]:
                return False
        # checks validity of block
        for i in range(int(current_row / 3)*3, int(current_row / 3)*3 + 3):
            for j in range(int(current_column / 3)*3, int(current_column / 3)*3 + 3):
                if i != current_row or j != current_column:
                    if new_entry == state_copy[i, j]:
                        return False
        return True

    def __check_if_finished(self):
        valid = [set(self._state[i, ...].tolist()) == set(range(1, 10)) for i in range(9)]
        valid = valid + [set(self._state[..., i].tolist()) == set(range(1, 10)) for i in range(9)]
        for i in range(3):
            for j in range(3):
                block = self._state[i * 3:(i + 1) * 3, j * 3:(j + 1) * 3].tolist()
                block = block[0] + block[1] + block[2]
                valid.append(set(block) == set(range(1, 10)))
        return all(valid)

    def __find_zero(self):
        for i in range(9):
            for j in range(9):
                if self._state[i, j] == 0:
                    return i, j
        raise SudokuError("SudokuSolver couldn't find zero although sudoku isn't finished")
