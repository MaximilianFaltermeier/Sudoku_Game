import pytest
from main import SudokuGame
from SolutionStrategies import SolutionStrategies


@pytest.fixture
def setup_sudoku(request):
    with open('sudokus/%s.sudoku' % request.param, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()
        game.grid.reset_candidates_of_cells()
        strategy = SolutionStrategies(game.grid)
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
