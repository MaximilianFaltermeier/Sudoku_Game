from global_constants import *
from copy import copy


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

    def _iterate_over_grid_components(self, *args):
        for grid_component in ['rows', 'columns', 'blocks']:
            for cell_list in getattr(self._grid, grid_component):
                func_output = args[0](cell_list, *args[1:])
                if func_output:
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
        self._grid.reset_candidates_of_cells()
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
        """
        One cell has one single candidate left
        :return:
        """
        return self._iterate_over_grid(self._single_choice)

    def _single_choice(self, cell):
        if len(cell.candidates) == 1:
            self._concerning_cells.append(cell)
            self._hint_type = SOLUTION
            self._suggestions = [cell.candidates[0]]
            self._message = 'According the single_choice rule, a {} is placed at cell ({}, {})' \
                .format(self._suggestions[0], cell.coordinates[0] + 1, cell.coordinates[1] + 1)
            return True
        return False

    def hidden_single(self):
        """
        Number can be in just one cell of a grid component
        :return:
        """
        return self._iterate_over_grid_components(self._hidden_single)

    def _hidden_single(self, cell_list, *args):
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

    # TODO: test naked_pair and naked_triple + sub-methods
    def naked_pair(self):
        """
        There are two numbers which can be only in a cell pair
        :return:
        """
        number_of_appearances = 2
        return self._iterate_over_grid_components(self._naked_group, number_of_appearances)

    def naked_triple(self):
        """
        There are three numbers which can be only in a cell pair
        :return:
        """
        number_of_appearances = 3
        return self._iterate_over_grid_components(self._naked_group, number_of_appearances)

    def _naked_group(self, cell_list, number_of_appearances):
        candidate_list = self._get_digit_with_n_appearances_as_candidate(cell_list, number_of_appearances)
        self._n_digits_have_same_n_possible_positions(candidate_list, number_of_appearances)
        for i in range(len(candidate_list)):
            for j in range(i + 1, len(candidate_list)):
                if candidate_list[i] == candidate_list[j]:
                    break
                if number_of_appearances == 2:
                    if all([elem1 == elem2 for elem1, elem2 in zip(candidate_list[i][1], candidate_list[j][1])]):
                        concerning_cells = [candidate_list[i], candidate_list[j]]
                        self._prepare_output_for_naked_group_as_solution(concerning_cells)
                        return True
                elif number_of_appearances == 3:
                    for k in range(j + 1, len(candidate_list)):
                        if candidate_list[k] == candidate_list[j]:
                            break
                        if all([elem1 == elem2 and elem2 == elem3 for elem1, elem2, elem3 in
                                (zip(candidate_list[i][1], candidate_list[j][1]), candidate_list[k][1])]):
                            concerning_cells = [candidate_list[i], candidate_list[j], candidate_list[k]]
                            self._prepare_output_for_naked_group_as_solution(concerning_cells)
                            return True
        return False

    def _prepare_output_for_naked_group_as_solution(self, concerning_cells):
        cells_with_obsolete_digits, candidates_can_be_removed = self._get_cells_with_obsolete_digits(concerning_cells)
        if not candidates_can_be_removed:
            # checks if candidates even can be removed else found group is useless
            return False
        self._concerning_cells.extend(concerning_cells)
        self._hint_type = REMOVE_CANDIDATE
        self._suggestions.extend(cells_with_obsolete_digits)
        self._message = 'According the naked-group rule several obsolete candidates are removed'

    def _n_digits_have_same_n_possible_positions(self, candidate_list, number_of_appearances):
        new_candidates = []
        for grid_component in ['rows', 'columns', 'blocks']:
            for cell_list in getattr(self._grid, grid_component):
                for i in range(len(cell_list)):
                    for j in range(i, len(cell_list)):
                        if len(set(cell_list[i].candidates).intersection(
                                set(cell_list[j].candidates))) == number_of_appearances:
                            if number_of_appearances == 3:
                                for k in range(j, len(cell_list)):
                                    if len(set(cell_list[k].candidates).intersection(
                                            set(cell_list[j].candidates))) == number_of_appearances:
                                        new_candidates.extend([cell_list[i], cell_list[j], cell_list[k]])
                            else:
                                new_candidates.extend([cell_list[i], cell_list[j]])
        if new_candidates:
            for digit in new_candidates[0].candidates:
                candidate_list.append((digit, new_candidates))

    def _get_cells_with_obsolete_digits(self, concerning_cells):
        cell_candidates = []
        set_concerning_cells_list = set([item for sublist in concerning_cells for item in sublist[1]])
        list_concerning_digits = [elem[0] for elem in concerning_cells]
        for grid_component in ['rows', 'columns', 'blocks']:
            for cell_list in getattr(self._grid, grid_component):
                if len(set(cell_list).intersection(set_concerning_cells_list)) == len(concerning_cells):
                    cell_candidates.extend(list(set(cell_list).symmetric_difference(set_concerning_cells_list)))
                    cell_candidates = [cell for cell in cell_candidates if
                                       set(list_concerning_digits) & set(cell.candidates)]
        for cell in concerning_cells:
            if set(cell.candidates).symmetric_difference(set(list_concerning_digits)):
                return cell_candidates, True
        return cell_candidates, len(cell_candidates) > 0

    @staticmethod
    def _get_digit_with_n_appearances_as_candidate(cell_list, n):
        candidate_list = []
        for digit in range(9):
            cell_appearance_list = []
            for cell in cell_list:
                if digit in cell.candidates:
                    cell_appearance_list.append(cell)
                    if len(cell_appearance_list) > n:
                        break
            if len(cell_appearance_list) == n:
                candidate_list.append((digit, copy(cell_appearance_list)))
        return candidate_list
