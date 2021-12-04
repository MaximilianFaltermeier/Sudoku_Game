import pytest
from main import SudokuGame
from SolutionStrategies import SolutionStrategies
from cell import Cell


@pytest.fixture
def setup_sudoku(request):
    with open('sudokus/%s.sudoku' % request.param, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()
        game.grid.reset_candidates_of_cells()
        strategy = SolutionStrategies(game)
        yield game.grid, strategy


@pytest.mark.parametrize('setup_sudoku', ['n00b'], indirect=["setup_sudoku"])
def test_single_choice(setup_sudoku):
    grid, strategy = setup_sudoku
    strategy.single_choice()
    solution_dict = strategy._return_strategy()
    assert id(solution_dict['concerning_cells'][0]) == id(grid[5, 8])
    assert solution_dict['hint_type'] == 1
    assert solution_dict['suggestions'][0] == 6


@pytest.mark.parametrize('setup_sudoku', ['n00b'], indirect=["setup_sudoku"])
def test_hidden_single(setup_sudoku):
    grid, strategy = setup_sudoku
    strategy.hidden_single()
    solution_dict = strategy._return_strategy()
    assert id(solution_dict['concerning_cells'][0]) == id(grid[0, 2])
    assert solution_dict['hint_type'] == 1
    assert solution_dict['suggestions'][0] == 7


def test_from_naked_group_n_cells_same_n_candidates():
    cell_list = [Cell(i, 1) for i in range(9)]
    cell_list[2].set_value(5, True)
    cell_list[3].set_value(4, True)
    cell_list[1].set_candidates([1, 2])
    cell_list[4].set_candidates([1, 2])
    cell_list[5].set_candidates([1, 6])
    cell_list[7].set_candidates([7, 2, 3])
    cell_list[6].set_candidates([7, 2, 3])
    cell_list[8].set_candidates([7, 6, 8])
    result_n2, cell_intersection = SolutionStrategies._n_cells_same_n_candidates(cell_list, 2)
    result_n3, cell_intersection = SolutionStrategies._n_cells_same_n_candidates(cell_list, 3)
    assert len(result_n2) == 2
    assert len(result_n3) == 0
    assert cell_list[1] in result_n2
    assert cell_list[4] in result_n2
    assert result_n3 == []


def test_from_naked_group_get_candidate_with_n_appearances():
    cell_list = [Cell(i, 1) for i in range(9)]
    cell_list[2].set_value(5, True)
    cell_list[3].set_value(4, True)
    cell_list[1].set_candidates([1, 2])
    cell_list[4].set_candidates([1, 2])
    cell_list[5].set_candidates([1, 2])
    cell_list[7].set_candidates([7, 2, 3, 8])
    cell_list[6].set_candidates([7, 2, 3, 8])
    cell_list[8].set_candidates([6, 9])
    result_n2, suggestion_n2 = SolutionStrategies._get_candidate_with_n_appearances(cell_list, 2)
    result_n3, suggestion_n3 = SolutionStrategies._get_candidate_with_n_appearances(cell_list, 3)
    assert suggestion_n2 == {6, 9}
    assert suggestion_n3 == {3, 7, 8}
    assert len(result_n2) == 2
    assert len(result_n3) == 3
    assert cell_list[0] in result_n3
    assert cell_list[7] in result_n3
    assert cell_list[0] in result_n2
    assert cell_list[8] in result_n2
