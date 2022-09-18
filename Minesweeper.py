from tkinter import *
from tkinter import messagebox

import random

class MinesweeperCell(Label):
    '''represents a minesweeper cell'''

    def __init__(self, master, coord):
        '''MinesweeperCell(master, coord) -> MinesweeperCell
        creates an unclicked, unflagged minesweeper cell'''

        # set up the cell display
        Label.__init__(self, master, height=1, width=2, text='', bg='white', font=('Arial',24), relief=RAISED)
        # set up color map
        self.colormap = ['lightgray','blue','darkgreen','red','purple','maroon','cyan','black','dim gray']

        # set up instance variables
        self.coord = coord      # (row, column) coordinate tuple
        self.number = 0         # creates a number variable, starts at zero
        self.flagged = False    # starts as unflagged
        self.clicked = False    # starts as unclicked
        self.is_bomb = False    # starts as not a bomb

        # set up listeners
        self.bind('<Button-1>', self.click)
        self.bind('<Button-3>', self.toggle_flag)

    # accessor methods
    
    def get_coord(self):
        '''MinesweeperCell.get_coord() -> tuple
        returns the (row, column) coordinate of the cell'''
        return self.coord

    def get_number(self):
        '''MinesweeperCell.get_coord() -> int
        returns the number of the cell'''
        return self.number

    def get_flagged(self):
        '''MinesweeperCell.get_flagged() -> boolean
        returns the state of the flag of the cell'''
        return self.flagged

    def get_clicked(self):
        '''MinesweeperCell.get_clicked() -> boolean
        returns the state of the click of the cell'''
        return self.clicked

    def get_bomb(self):
        '''MinesweeperCell.get_bomb() -> boolean
        returns True if the cell is a bomb'''
        return self.is_bomb

    # mutator methods
    
    def add_one(self):
        '''MinesweeperCell.add_one()
        increases the number value by 1'''
        self.number += 1
        self.update_display()

    def become_bomb(self):
        '''MinesweeperCell.become_bomb()
        turns a cell into a bomb'''
        self.number = -1
        self.is_bomb = True

    def toggle_flag(self, event=False):
        '''MinesweeperCell.add_one()
        changes self.flagged from True to False, vice versa'''

        # change cell
        if self.flagged == True:
            self.master.remaining_flags += 1
        else:
            self.master.remaining_flags -= 1
        self.master.update_text()

        # toggles the flag and updates cell display
        self.flagged = not self.flagged
        self.update_display()

    def click(self, event):
        '''MinsweeperCell.click()
        turns a cell into a clicked cell and also checks if it is a bomb or not'''
        
        self.open()
        if self.is_bomb and not self.flagged:
            self.master.lose()

    def open(self):
        '''MinesweeperCell.open()
        sets clicked to true, displays, and calls itself recursively for empty cells'''
        
        if not self.clicked and not self.flagged:
            self.clicked = True
            self.update_display()
            if not self.is_bomb:
                self.master.remaining_cells -= 1
                self.master.check_status()

            if self.number == 0:
                for coord in self.master.get_neighboring_cells(self.coord):
                    self.master.cells[coord].open()

    def reveal_bomb(self):
        '''MinesweeperCell.open()
        displays the unflagged bombs after a loss'''
        
        if not self.flagged:
            self.clicked = True
            self.update_display()

    # other methods

    def update_display(self):
        '''MinesweeperCell.update_display()
        displays icon of a cell depending on the status
            - flagged cells have flags
            - clicked bomb cells have bombs and are red
            - clicked empty cells have no text
            - clicked numbered cells have text and a corresponding color'''
        
        if not self.clicked: # cell has not been clicked
            if self.flagged:
                self['fg'] = 'red'
                self['text'] = "🚩"
            else:
                self['text'] = ""
        else: # cell has been clicked
            self['relief']=SUNKEN
            self['bg']='lightgrey'
            if self.is_bomb:
                self['fg'] = 'black'
                self['text'] = "💣"
                self['bg'] = "red"
            else:
                self['fg'] = self.colormap[self.number]
                self['text'] = str(self.number)

    def unbind_keys(self):
        '''MinesweeperCell.unbind_keys()
        gets rid of the binds when the game is finished'''
        self.unbind('<Button-1>')
        self.unbind('<Button-3>')

    def reset(self):
        '''MinesweeperCell.reset()
        resets mutable variables back to their defaults'''
        
        self.flagged = False
        self.clicked = False    
        self.is_bomb = False

class MinesweeperGrid(Frame):
    '''object for a Minesweeper grid'''

    # initialize a new Minesweeper Grid
    def __init__(self, master, rows, columns, num_bombs):
        
        # initialize a new frame
        Frame.__init__(self, master)
        self.grid()

        # set up instance variables
        self.rows = rows                                # number of rows
        self.columns = columns                          # number of columns
        self.num_bombs = num_bombs                      # number of bombs
        self.remaining_cells = rows*columns-num_bombs   # remaining non-bomb cells to be clicked
        self.remaining_flags = num_bombs                # remaining flags

        # create a bottom section to count the flags
        self.buttonFrame = Frame(self,bg='black')
        self.flagLabel = Label(self.buttonFrame,text="Flags remaining: " + str(self.num_bombs),font=('Arial',18))
        self.flagLabel.grid(row=0, column=0)
        self.buttonFrame.grid(row=2*rows+1,column=0,columnspan=2*columns+1)

        # create cells
        self.create_cells()
        self.play_again_button = Button(self.buttonFrame, text='Play Again', font=('Arial',12), command=self.restart)

    def create_cells(self):
        '''MinesweeperGrid.create_cells()
        creates a grid of cells in the frame, used by the initializer and the restart method'''

        # create the cells
        self.cells = {}
        for row in range(self.rows):
            for column in range(self.columns):
                coord = (row, column)
                self.cells[coord] = MinesweeperCell(self, coord)
                self.cells[coord].grid(row=2*row,column=2*column)
        
        # randomly assign bombs and creates a list of coords
        self.list_of_bombs = []
        for coord in random.sample(list(self.cells), self.num_bombs):
            self.cells[coord].become_bomb()
            self.list_of_bombs.append(coord)

        # add one to the value of each minesweeper unit surrounding each bomb
        for coord in self.list_of_bombs:
            for new_coord in self.get_neighboring_cells(coord):
                self.cells[new_coord].add_one()

    def get_neighboring_cells(self, coord):
        '''MinesweeperGrid.get_neighboring_cells(coord) -> list
        returns a list of neighboring cells from the cell at the given coord'''
        # list of vectors to create neighboring coordinates
        vectors = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        neighboring_cells = []

        for vector in vectors:
            new_coord = (coord[0] + vector[0], coord[1] + vector[1]) # creates a new coordinate
            if new_coord in self.cells and self.cells[new_coord].get_bomb() == False:
                neighboring_cells.append(new_coord)    
        return neighboring_cells

    def check_status(self):
        '''MinesweeperGrid.check_status()
        eafter each click, checks if all cells have been clicked'''

        if self.remaining_cells == 0:
            self.win()

    def lose(self):
        '''MinesweeperGrid.lose()
        ends the game when the player hits a bomb'''

        # pop-up message indicating loss
        messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)

        # reveals bombs that are not flagged
        for coord in self.list_of_bombs:
            self.cells[coord].reveal_bomb()

        # removes flags that are false
        for coord in self.cells:
            if self.cells[coord].flagged and not self.cells[coord].is_bomb:
                self.cells[coord].toggle_flag()
        self.end_game()

    def win(self):
        '''MinesweeperGrid.win()
        ends the game when the player clears the board'''

        # pop-up message indicating a win
        messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)
        self.end_game()

    def end_game(self):
        '''MinesweeperGrid.end_game()
        final ending actions'''

        # removes the listeners for each cell so they can't be clicked
        for coord in self.cells:
            self.cells[coord].unbind_keys()

        # makes the play again button visible
        self.play_again_button.grid(row=0,column=1)
        # hides the flag text
        self.flagLabel.grid_remove()

    def update_text(self):
        '''MinesweeperGrid.update_text()
        updates the flag text at the bottom after each right click
        '''
        self.flagLabel['text'] = "Flags remaining: " + str(self.remaining_flags)

    def restart(self):
        # set up instance variables
        self.remaining_cells = self.rows*self.columns-self.num_bombs    # remaining non-bomb cells to be clicked
        self.remaining_flags = self.num_bombs                           # remaining flags
        
        # create the cells
        for key in self.cells:
            self.cells[key].destroy()
        self.create_cells()

        # hides the play again button
        self.play_again_button.grid_remove()
        # shows the flags again
        self.flagLabel.grid(row=0, column=0)
        # update the flag text
        self.update_text()
        
def minesweeper(row, column, bombs):
    '''minesweeper()
    plays minesweeper'''
    root = Tk()
    root.title('Minesweeper')
    mg = MinesweeperGrid(root, row, column, bombs)
    root.mainloop()

def start_game_inputs():
    '''start_game_inputs()
    asks the user for row, column, and bomb amounts, then starts the game'''
    
    row = input("Input the number of rows:")
    column = input("Input the number of columns:")
    bombs = input("Input the number of bombs:")

    minesweeper(int(row), int(column), int(bombs))

start_game_inputs()





