from cell import Cell


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
                    self.cells[i].possible_error = True
                    self.cells[j].possible_error = True


class Grid:
    def __init__(self):
        self.rows = [GridComponent() for _ in range(9)]
        self.columns = [GridComponent() for _ in range(9)]
        self.blocks = [GridComponent() for _ in range(9)]

        for row in range(9):
            for column in range(9):
                cell = Cell()
                self.rows[row].cells.append(cell)
                self.columns[column].cells.append(cell)
                block = int(row / 3) * 3 + int(column / 3)
                self.blocks[block].cells.append(cell)
                cell.set_dependencies(self.rows[row], self.columns[column], self.blocks[block])

    def __getitem__(self, item):
        return self.rows[item[0]][item[1]]

    def __setitem__(self, key, value):
        self.rows[key[0]][key[1]].set_value(value)

    def update_possible_solutions_of_cells(self):
        for row in self.rows:
            for cell in row:
                cell.update_possible_solutions()

    def reset_possible_solutions_of_cells(self):
        for row in self.rows:
            for cell in row:
                cell.reset_possible_solutions()

    def search_for_identical_values_in_components(self, components):
        """
        Finds collisions in one component type (e.g. row, column, block)
        """
        for component in getattr(self, components):
            component.search_for_identical_values()

    def reset_possible_error(self):
        for row in self.rows:
            for cell in row:
                cell.possible_error = False
