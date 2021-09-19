from tkinter import Canvas, Frame, Button, TOP, Text, END, LEFT, Label, BOTTOM
from global_constants import *
from SolutionStrategies import SolutionStrategies


class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """

    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.__show_candidates = False
        self.__label_list = []
        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack()
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT, bg='white')
        self.canvas.pack(side=LEFT, pady='17', padx='15')

        clear_button = Button(self, text="Clear answers", command=self.__clear_answers, font=FONT_BUTTONS)
        check_button = Button(self, text="Check Sudoku", command=self.__find_errors, font=FONT_BUTTONS)
        candidate_button = Button(self, text="Show candidates",
                                  command=self.__allow_candidates_to_be_displayed, font=FONT_BUTTONS)
        hint_button = Button(self, text="Show hint", command=self.__get_hint, font=FONT_BUTTONS)

        clear_button.place(relx=RELX_BUTTON, rely=0.5 + RELY_OFFSET_BUTTON)
        check_button.place(relx=RELX_BUTTON, rely=0.6 + RELY_OFFSET_BUTTON)
        candidate_button.place(relx=RELX_BUTTON, rely=0.7 + RELY_OFFSET_BUTTON)
        hint_button.place(relx=RELX_BUTTON, rely=0.8 + RELY_OFFSET_BUTTON)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind('<Button-1>', self.__cell_clicked)
        self.canvas.bind('<Key>', self.__key_pressed)
        self.canvas.bind('<BackSpace>', self.__back_space_key_pressed)
        quote = 'If you want a hint, use the hint button\ngood luck :)\n'
        self.text_field = Text(self, height=15, width=60, padx=0)
        self.text_field.tag_configure('color', foreground='#476042', font=FONT_HINTS, justify='left')

        self.text_field.insert('1.0', quote, 'color')
        self.text_field.tag_add('initialText', 1.0, END)
        self.text_field.pack(side=TOP, pady='20', padx='10')

    """------------------------------------DRAWING---------------------------------------"""

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE + GRID_OFFSET
            y0 = MARGIN + GRID_OFFSET
            x1 = MARGIN + i * SIDE + GRID_OFFSET
            y1 = HEIGHT - MARGIN + GRID_OFFSET
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN + GRID_OFFSET
            y0 = MARGIN + i * SIDE + GRID_OFFSET
            x1 = WIDTH - MARGIN + GRID_OFFSET
            y1 = MARGIN + i * SIDE + GRID_OFFSET
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        """
        Draws the numbers of the grid. The colors black, red, sea green and grey mark the type of number:
        given number, colliding numbers, users guesses and number suggestions
        """
        self.canvas.delete("numbers")
        for label in self.__label_list:
            label.destroy()
        for i in range(9):
            for j in range(9):
                cell = self.game.grid[i, j]
                digit = cell.get_value()

                if digit != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    if cell.given:
                        color = "black"
                    elif cell.error:
                        color = "red"
                        cell.error = False
                    else:
                        color = "sea green"
                    self.canvas.create_text(x, y, text=digit, tags="numbers", fill=color, font=FONT_NUMBERS)
                elif self.__show_candidates:
                    self.update_labels_of_candidates(cell, i, j)

    def update_labels_of_candidates(self, cell, i, j):
        for candidate in range(1, 10):
            position_variable = candidate - 1
            x = MARGIN + j * SIDE + SIDE / 24 * (position_variable % 3 + 0.7) * 7 - 5
            y = MARGIN + i * SIDE + SIDE / 24 * (int(position_variable / 3)) * 7 + 3

            if candidate in cell.candidates:
                digit_color = '#777777'
            else:
                digit_color = '#E0E0E0'

            new_label = Label(self.canvas, text=candidate, cursor="hand2", font=FONT_SUGGESTIONS,
                              bg='white', fg=digit_color, padx=-1, pady=-20)
            new_label.place(x=x, y=y)
            # new_label.bind("<Button-3>", lambda _: self.__candidate_clicked(cell, candidate))
            if candidate == 1:
                new_label.bind("<Button-3>", lambda _: self.__label1(cell))
            elif candidate == 2:
                new_label.bind("<Button-3>", lambda _: self.__label2(cell))
            elif candidate == 3:
                new_label.bind("<Button-3>", lambda _: self.__label3(cell))
            elif candidate == 4:
                new_label.bind("<Button-3>", lambda _: self.__label4(cell))
            elif candidate == 5:
                new_label.bind("<Button-3>", lambda _: self.__label5(cell))
            elif candidate == 6:
                new_label.bind("<Button-3>", lambda _: self.__label6(cell))
            elif candidate == 7:
                new_label.bind("<Button-3>", lambda _: self.__label7(cell))
            elif candidate == 8:
                new_label.bind("<Button-3>", lambda _: self.__label8(cell))
            else:
                new_label.bind("<Button-3>", lambda _: self.__label9(cell))

            self.__label_list.append(new_label)

    def __draw_cursor(self):
        """
        Draws a red rectangle around selected cell
        """
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1 + GRID_OFFSET
            y0 = MARGIN + self.row * SIDE + 1 + GRID_OFFSET
            x1 = MARGIN + (self.col + 1) * SIDE - 1 + GRID_OFFSET
            y1 = MARGIN + (self.row + 1) * SIDE - 1 + GRID_OFFSET
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

    def __draw_text(self, text):
        self.text_field.tag_configure('message', foreground='#476042', font=FONT_HINTS, justify='left')
        self.text_field.insert(END, text + '\n', 'message')

    """----------------------------------KEYS---------------------------------------"""

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
            elif not self.game.grid[row, col].given:
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
            self.game.grid[self.row, self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.game.grid.update_candidates_of_cells()
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()

    def __back_space_key_pressed(self, _):
        """
        Deletes number if BackSpace is pressed
        """
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0:
            self.game.grid[self.row, self.col] = 0
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()

    def __candidate_clicked(self, cell, value_of_label):
        if value_of_label in cell.candidates:
            cell.candidates.remove(value_of_label)
        else:
            cell.candidates.append(value_of_label)

        self.update_labels_of_candidates(cell, cell.coordinates[0], cell.coordinates[1])

    def __label1(self, cell):
        self.__candidate_clicked(cell, 1)

    def __label2(self, cell):
        self.__candidate_clicked(cell, 2)

    def __label3(self, cell):
        self.__candidate_clicked(cell, 3)

    def __label4(self, cell):
        self.__candidate_clicked(cell, 4)

    def __label5(self, cell):
        self.__candidate_clicked(cell, 5)

    def __label6(self, cell):
        self.__candidate_clicked(cell, 6)

    def __label7(self, cell):
        self.__candidate_clicked(cell, 7)

    def __label8(self, cell):
        self.__candidate_clicked(cell, 8)

    def __label9(self, cell):
        self.__candidate_clicked(cell, 9)

    """----------------------------------BUTTONS---------------------------------------"""

    def __clear_answers(self):
        """
        Reset the board
        """
        self.game.reset_board()
        self.canvas.delete("victory")
        self.__draw_puzzle()

    def __find_errors(self):
        """
        Finds collisions and mark them red
        """
        self.game.grid.find_collisions()
        self.__draw_puzzle()

    def __allow_candidates_to_be_displayed(self):
        """
        Enables/Disables showing candidates. Resets all suggestions after turn off and on again
        """
        self.__show_candidates = not self.__show_candidates
        # if self.__show_candidates:
        #     self.game.grid.reset_candidates_of_cells()
        self.__draw_puzzle()

    def __get_hint(self):
        strategy = SolutionStrategies(self.game).give_strategy()
        self.game.grid.apply_hint(strategy)
        self.__draw_puzzle()
        self.__draw_text(strategy['message'])
