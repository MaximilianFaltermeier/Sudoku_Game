from cell import Cell


class GridComponent:
    def __init__(self):
        self.cells = []

    def __iter__(self):
        return self.cells.__iter__()

    def __getitem__(self, item):
        return self.cells[item]


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
