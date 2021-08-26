SOLUTION = 1
REMOVE_CANDIDATE = 0


class SolutionStrategies:
    def __init__(self, grid):
        self._grid = grid
        self._concerning_cells = []
        self._hint_type = None  # type has to be SOLUTION or REMOVE_CANDIDATE
        self._suggestions = []
        self._method = []
        self._success = False

    def _iterate_over_grid(self, func):
        for cell in self._grid:
            if not cell.given:
                success = func(cell)
                if success:
                    return True
        return False

    def _return_strategy(self):
        self.solution = {
            'success': self._success,
            'concerning_cells': self._concerning_cells,
            'hint_type': self._hint_type,
            'suggestions': self._suggestions
        }
        return self.solution

    def _give_strategy(self):
        for method in dir(self):
            if method.startswith('_') is False:
                method_to_be_applied = getattr(self, method)
                success = method_to_be_applied()
                if success:
                    self._method = method
                    self._success = True
                    break
        return self._return_strategy()

    '''--------------------------------strategies--------------------------------------------------'''

    def single_choice(self):
        return self._iterate_over_grid(self.single_choice)

    def _single_choice(self, cell):
        if len(cell.candidates) == 1:
            self._concerning_cells.append(cell)
            self._hint_type = SOLUTION
            self._suggestions = [cell.candidates[0]]
            return True
        return False
