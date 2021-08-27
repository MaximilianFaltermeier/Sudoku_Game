from exception_class import SudokuError


class Cell:
    def __init__(self):
        # private variables
        self.__value = 0
        # public variables
        self.given = False
        self.row = None
        self.column = None
        self.block = None
        self.error = False
        self.candidates = list(range(1, 10))

    def __iter__(self):
        return self

    def __deepcopy__(self):
        pass

    def set_dependencies(self, row, column, block):
        self.row = row
        self.column = column
        self.block = block

    def set_value(self, number, given=False):
        if not (isinstance(number, int) and 0 <= number < 10):
            raise SudokuError('number must be a integer between 0 and 9')
        if given and number != 0:
            self.given = True
        elif self.given:
            raise SudokuError('given value cannot be overwritten')
        self.__value = number

    def get_value(self):
        return self.__value

    def update_candidates(self):
        """
        Deletes all numbers from the solution suggestion which are no longer possible. Deletes only numbers which
        collide with numbers in row, column or block. No more advanced techniques are used.
        """
        if self.__value != 0:
            self.candidates = []
            return 0
        to_be_removed_items = []
        for value in self.candidates:
            if value in [cell.get_value() for cell in self.row]:
                to_be_removed_items.append(value)
            elif value in [cell.get_value() for cell in self.column]:
                to_be_removed_items.append(value)
            elif value in [cell.get_value() for cell in self.block]:
                to_be_removed_items.append(value)

        # this special construction deals with the challenge to have no doubling in to_be_removed_items
        # else list.remove() throws an error
        to_be_removed_items = set(to_be_removed_items)
        to_be_removed_items = list(to_be_removed_items)

        for elem in to_be_removed_items:
            self.candidates.remove(elem)

    def reset_candidates(self):
        self.candidates = list(range(1, 10))
