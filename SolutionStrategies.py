from global_constants import *
from itertools import product


def _index_product(length):
    x = []
    y = []
    for i, j in product(range(length), repeat=2):
        if i < j:
            x.append(i)
            y.append(j)
    return zip(x, y)


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
                        self._message = 'Your solution contains an error! I have marked it for you'
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

    # TODO: replace dict through class solution_strategy
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

    def naked_pair(self):
        """
        There are two numbers which can be only in a cell pair
        :return:
        """
        number_of_appearances = 2
        return self._iterate_over_grid_components(self._naked_group, number_of_appearances)

    def naked_triple(self):
        """
        There are three numbers which can be only in a group of three cells
        :return:
        """
        number_of_appearances = 3
        return self._iterate_over_grid_components(self._naked_group, number_of_appearances)

    def _naked_group(self, cell_list, group_size):
        candidate_list, suggestion = SolutionStrategies._get_candidate_with_n_appearances(cell_list, group_size)
        if not candidate_list or not self._test_if_suggestion_gives_new_information(cell_list, candidate_list,
                                                                                    suggestion):
            candidate_list, suggestion = SolutionStrategies._n_cells_same_n_candidates(cell_list, group_size)
        if candidate_list and self._test_if_suggestion_gives_new_information(cell_list, candidate_list, suggestion):
            self._concerning_cells = cell_list
            self._hint_type = REMOVE_CANDIDATE
            self._suggestions = self._get_suggestion(cell_list, candidate_list, suggestion)
            self._message = 'According the naked_group rule candidates have been removed (group_size = {})' \
                .format(group_size)
        else:
            return False

    @staticmethod
    def _get_candidate_with_n_appearances(cell_list, group_size):
        filtered_cell_list, digit_set = SolutionStrategies._get_digits_with_n_appearance(cell_list, group_size)
        return SolutionStrategies._propose_candidate(filtered_cell_list, group_size, digit_set)

    @staticmethod
    def _propose_candidate(filtered_cell_list, group_size, digit_set):
        len_cache = len(filtered_cell_list)
        cell_cache = []

        for i, j in _index_product(len_cache):
            jth_cell = filtered_cell_list[j]
            jth_cell_candidates_set = set(jth_cell.candidates)
            ith_cell = filtered_cell_list[i]

            candidates_intersection = set(ith_cell.candidates).intersection(jth_cell_candidates_set)
            intersection_digit_candidates = candidates_intersection.intersection(digit_set)

            if len(intersection_digit_candidates) == group_size:
                cell_cache = [ith_cell, jth_cell]
                if group_size == 3:
                    for k in range(j + 1, len_cache):
                        kth_cell = filtered_cell_list[k]
                        k_cell_candidates_set = set(kth_cell.candidates)
                        candidates_intersection_2 = k_cell_candidates_set.intersection(digit_set)
                        if candidates_intersection_2 == intersection_digit_candidates:
                            cell_cache.append(kth_cell)
                            return cell_cache, intersection_digit_candidates
                    cell_cache = []
                else:
                    return cell_cache, intersection_digit_candidates
        return cell_cache, {}

    @staticmethod
    def _get_digits_with_n_appearance(cell_list, number_of_appearances):
        digit_list = []
        filtered_cell_list = []

        for digit in range(1, 10):
            counter = 0
            for cell in cell_list:
                if digit in cell.candidates:
                    counter += 1
                if counter > number_of_appearances:
                    break
            if counter == number_of_appearances:
                digit_list.append(digit)

        digit_set = set(digit_list)
        for cell in cell_list:
            if len(set(cell.candidates).intersection(digit_set)) >= number_of_appearances:
                filtered_cell_list.append(cell)
        return filtered_cell_list, digit_set

    @staticmethod
    def _n_cells_same_n_candidates(cell_list, number_of_appearances):
        cell_list_cache = [cell for cell in cell_list if len(cell.candidates) == number_of_appearances]
        len_cache = len(cell_list_cache)

        for i in range(len_cache):
            for j in range(i + 1, len_cache):

                j_cell_to_set = set(cell_list_cache[j].candidates)
                cell_intersection = set(cell_list_cache[i].candidates).intersection(j_cell_to_set)
                if len(cell_intersection) == number_of_appearances:
                    cell_cache = [cell_list_cache[i], cell_list_cache[j]]

                    if number_of_appearances == 3:
                        for k in range(j + 1, len_cache):
                            if set(cell_list_cache[k].candidates).intersection(j_cell_to_set) == cell_intersection:
                                cell_cache.append(cell_list_cache[k])
                                return cell_cache, cell_intersection
                        break
                    else:
                        return cell_cache, cell_intersection
        return [], {}

    @staticmethod
    def _test_if_suggestion_gives_new_information(cell_list, candidate_list, suggestion):
        for cell in cell_list:
            if cell in candidate_list:
                if len(set(cell.candidates).intersection(suggestion)) < len(cell.candidates):
                    return True
            else:
                if len(set(cell.candidates).intersection(suggestion)) > 0:
                    return True
        return False

    @staticmethod
    def _get_suggestion(cell_list, candidate_list, suggestion):
        list_cache = []
        for cell in cell_list:
            if cell in candidate_list:
                list_cache.append(list(suggestion))
            else:
                list_cache.append(list(set(cell.candidates).difference(suggestion)))
        return list_cache
