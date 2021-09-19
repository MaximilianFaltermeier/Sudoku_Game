from cell import Cell
from global_constants import *

class GridComponent:
    def __init__(self):
        self.cells = []

    def __iter__(self):
        return self.cells.__iter__()

    def __getitem__(self, item):
        return self.cells[item]

    def search_for_identical_values(self):
        """
        Finds collisions in self.cells
        """
        for i in range(8):
            for j in range(i + 1, 9):
                if self.cells[i].get_value() == self.cells[j].get_value():
                    self.cells[i].error = True
                    self.cells[j].error = True


class GridIterator:
    def __init__(self, grid):
        self._grid = grid
        self._index = 0

    def __next__(self):
        if self._index < 81:
            cell = self._grid[int(self._index / 9), self._index % 9]
            self._index += 1
            return cell
        raise StopIteration


class Grid:
    def __init__(self):
        self.rows = [GridComponent() for _ in range(9)]
        self.columns = [GridComponent() for _ in range(9)]
        self.blocks = [GridComponent() for _ in range(9)]

        for row in range(9):
            for column in range(9):
                cell = Cell(row, column)
                self.rows[row].cells.append(cell)
                self.columns[column].cells.append(cell)
                block = int(row / 3) * 3 + int(column / 3)
                self.blocks[block].cells.append(cell)
                cell.set_dependencies(self.rows[row], self.columns[column], self.blocks[block])

    def __getitem__(self, item):
        return self.rows[item[0]][item[1]]

    def __setitem__(self, key, value):
        self.rows[key[0]][key[1]].set_value(value)

    def __iter__(self):
        return GridIterator(self)

    def update_possible_solutions_of_cells(self):
        for row in self.rows:
            for cell in row:
                cell.update_candidates()

    def reset_possible_solutions_of_cells(self):
        for row in self.rows:
            for cell in row:
                cell.reset_candidates()
                cell.update_candidates()

    def search_for_identical_values_in_components(self, components):
        """
        Finds collisions in one component type (e.g. row, column, block)
        """
        for component in getattr(self, components):
            component.search_for_identical_values()

    def reset_possible_error(self):
        for row in self.rows:
            for cell in row:
                cell.error = False

    def find_collisions(self):
        self.search_for_identical_values_in_components('columns')
        self.search_for_identical_values_in_components('rows')
        self.search_for_identical_values_in_components('blocks')

    def apply_hint(self, strategy):
        if strategy['hint_type'] == ERROR:
            for cell in strategy['concerning_cells']:
                cell.reset_candidates()
        elif strategy['hint_type'] == SOLUTION:
            strategy['concerning_cells'].pop().set_value(strategy['suggestions'].pop())
        self.update_possible_solutions_of_cells()
