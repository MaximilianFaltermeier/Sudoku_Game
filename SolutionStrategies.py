from global_constants import *


class SolutionStrategies:
    def __init__(self, game):
        self._grid = game.grid
        self._solution = game.get_solution()
        self._concerning_cells = []
        self._hint_type = ''  # type has to be SOLUTION or REMOVE_CANDIDATE
        self._suggestions = []
        self._method = []
        self._success = False
        self._message = ''

    def _check_with_sample_solution(self):
        no_error = True
        for i in range(9):
            for j in range(9):
                if self._grid[i, j].get_value() != 0:
                    if self._grid[i, j].get_value() != self._solution[i, j]:
                        self._grid[i, j].error = True
                        no_error = False
                        self._concerning_cells.append(self._grid[i, j])
                        self._hint_type = ERROR
                        self._message = 'Your solution contains an error! I have marked at for you'
                else:
                    if self._solution[i, j] not in self._grid[i, j].candidates:
                        no_error = False
                        self._concerning_cells.append(self._grid[i, j])
                        self._hint_type = ERROR
                        self._message = "Your solution contains an error!\nYou eliminated " \
                                        "the true value from the candidates list.\nI reset them for you"
        return no_error

    def _iterate_over_grid(self, func):
        for cell in self._grid:
            if cell.get_value() == 0:
                success = func(cell)
                if success:
                    return True
        return False

    def _return_strategy(self):
        self._solution_strategy = {
            'success': self._success,
            'concerning_cells': self._concerning_cells,
            'hint_type': self._hint_type,
            'suggestions': self._suggestions,
            'method': self._method,
            'message': self._message
        }
        return self._solution_strategy

    def give_strategy(self):
        if not self._check_with_sample_solution():
            return self._return_strategy()
        self._grid.reset_possible_solutions_of_cells()
        for method in dir(self):
            if method.startswith('_') is False and method.startswith('give') is False:
                method_to_be_applied = getattr(self, method)
                success = method_to_be_applied()
                if success:
                    self._method = method
                    self._success = True
                    break
        return self._return_strategy()

    '''--------------------------------strategies--------------------------------------------------'''

    def single_choice(self):
        return self._iterate_over_grid(self._single_choice)

    def _single_choice(self, cell):
        if len(cell.candidates) == 1:
            self._concerning_cells.append(cell)
            self._hint_type = SOLUTION
            self._suggestions = [cell.candidates[0]]
            self._message = 'According the single_choice rule, a {} is placed at cell ({}, {})'\
                .format(self._suggestions[0], cell.coordinates[0] + 1, cell.coordinates[1] + 1)
            return True
        return False

    def hidden_single(self):
        for grid_component in ['rows', 'columns', 'blocks']:
            for cell_list in getattr(self._grid, grid_component):
                for i in range(9):
                    for candidate in cell_list[i].candidates:
                        candidate_is_unique = True
                        for j in range(9):
                            if i != j and candidate in cell_list[j].candidates:
                                candidate_is_unique = False
                                break
                        if candidate_is_unique:
                            self._concerning_cells.append(cell_list[i])
                            self._hint_type = SOLUTION
                            self._suggestions = [candidate]
                            self._message = 'According the hidden_single rule, a {} is placed at cell ({}, {})' \
                                .format(self._suggestions[0], cell_list[i].coordinates[0] + 1,
                                        cell_list[i].coordinates[1] + 1)
                            return True
        return False
