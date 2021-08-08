from tkinter import Canvas, Frame, Button, TOP

MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board


class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """

    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.__show_possibilities = False
        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack()
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(side=TOP)
        clear_button = Button(self,
                              text="Clear answers",
                              command=self.__clear_answers)
        clear_button.pack(fill='y', side='left', pady='5', padx='40')
        check_button = Button(self,
                              text="Check Sudoku",
                              command=self.__find_errors)
        check_button.pack(fill='y', side='left', pady='5', padx='40')
        possibility_button = Button(self,
                                    text="Show possibilities",
                                    command=self.__allow_possibilities_to_be_displayed)
        possibility_button.pack(fill='y', side='left', pady='5', padx='28')
        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind('<Button-1>', self.__cell_clicked)
        self.canvas.bind('<Key>', self.__key_pressed)
        self.canvas.bind('<BackSpace>', self.__backSpace_key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        """
        Draws the numbers of the grid. The colors black, red, sea green and grey mark the type of number:
        given number, colliding numbers, users guesses and number suggestions
        """
        self.canvas.delete("numbers")
        self.canvas.delete("possibilities")
        for i in range(9):
            for j in range(9):
                cell = self.game.puzzle[i, j]
                digit = cell.get_value()

                if digit != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    if cell.given:
                        color = "black"
                    elif cell.possible_error:
                        color = "red"
                        cell.possible_error = False
                    else:
                        color = "sea green"
                    self.canvas.create_text(x, y, text=digit, tags="numbers", fill=color)
                elif self.__show_possibilities:
                    for possibility in cell.possible_solutions:
                        normalized_possibility = possibility-1
                        x = MARGIN + j * SIDE + SIDE / 24 * (normalized_possibility % 3 + 0.7) * 7
                        y = MARGIN + i * SIDE + SIDE / 24 * (int(normalized_possibility / 3) + 0.8) * 7
                        self.canvas.create_text(x, y, text=possibility, tags="possibilities", fill='grey',
                                                font=("Purisa", 10))

    def __draw_cursor(self):
        """
        Draws a red rectangle around selected cell
        """
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tags="cursor")

    def __draw_victory(self):
        """
        Draws a message for the user when he has won
        """
        # create a  a circle
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(x0, y0, x1, y1, tags="victory", fill="dark orange", outline="orange")
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(x, y, text="You win!", tags="victory", fill="white", font=("Arial", 32))

    def __cell_clicked(self, event):
        """
        Select clicked cell
        :param event: contains information (e.g. position) about the triggering event
        """
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = int((y - MARGIN) / SIDE), int((x - MARGIN) / SIDE)

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif not self.game.puzzle[row, col].given:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_pressed(self, event):
        """
        Adds number to grid if a number key is pressed
        :param event: contains information (e.g. pressed key) about the triggering event
        """
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row, self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.game.puzzle.update_possible_solutions_of_cells()
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()

    def __backSpace_key_pressed(self, event):
        """
        Deletes number if BackSpace is pressed
        """
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0:
            self.game.puzzle[self.row, self.col] = 0
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()

    def __clear_answers(self):
        """
        Reset the board
        """
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()

    def __find_errors(self):
        """
        Finds collisions and mark them red
        """
        self.__search_for_identical_values_in_list(self.game.puzzle.columns)
        self.__search_for_identical_values_in_list(self.game.puzzle.rows)
        self.__search_for_identical_values_in_list(self.game.puzzle.blocks)
        self.__draw_puzzle()

    def __search_for_identical_values_in_list(self, components):
        """
        Finds collisions in one grid component
        :param components: to be searched grid component
        """
        for component in components:
            for i in range(8):
                for j in range(i + 1, 9):
                    if component[i].get_value() == component[j].get_value():
                        component[i].possible_error = True
                        component[j].possible_error = True

    def __allow_possibilities_to_be_displayed(self):
        """
        Enables/Disables showing possible solutions. Resets all suggestions after turn off and on again
        """
        self.__show_possibilities = not self.__show_possibilities
        if self.__show_possibilities:
            self.game.puzzle.reset_possible_solutions_of_cells()
            self.game.puzzle.update_possible_solutions_of_cells()
        self.__draw_puzzle()

