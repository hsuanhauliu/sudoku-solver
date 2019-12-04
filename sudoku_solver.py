import os

class SudokuSolver(object):
    
    def __init__(self):
        self.board = []
        self.possible_moves = {}

    # Load the game from text file
    def load_game(self, filename):
        if os.path.isfile(filename):
            rFile = open(filename, "r")
            lines = rFile.readlines()

            r, c = 9, 9
            self.board = [[0 for x in range(c)] for y in range(r)]
            row = 0
            col = 0
     
            for l in lines:
                currLine = l.split(" ")
                for num in currLine:
                    self.board[row][col] = int(num)
                    col += 1
                col = 0
                row += 1
            rFile.close()
        else:
            print "Can't find the file."

        return

    # Display current board
    def display_board(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    print '_',
                else:
                    print self.board[row][col],
                if col == 2 or col == 5:
                    print '|',
            print '\n',
            if row == 2 or row == 5:
                print '---------------------'

        return

    # Try to use all three approaches to solve the game.
    def solve(self):
        self.solve1()
        if self.count_blank() != 0:
            self.solve2()
        if self.count_blank() != 0:
            self.solve3()

        return

    # Method 1: using heuristic (possible moves) to fill in the easy ones.
    def solve1(self):
        """
            Calculate lists of possible moves (heuristic) for each empty cell and fill in when
            there is only one possible move for that cell. Backtrack and update the ones that
            we have already checked and affected by our move.
        """
        # Go through rows
        for row in xrange(9):
            # Go through column
            for col in xrange(9):
                if self.board[row][col] == 0:    # if the block is empty
                    valid_moves = self.calculate_moves((row, col))    # get all valid moves
                    
                    if len(valid_moves) == 1:   # if there's only one possible move
                        move = valid_moves[0]   # fill in the blank with that number
                        self.board[row][col] = move
                        self.reexamine((row, col), move)  # check other blocks affected by this move

                    else:
                        self.possible_moves[(row, col)] = valid_moves    # otherwise remember possible moves for this block

        self.clean() # get rid of the cells that have been solved
        return

    # Method 2: for each row, column, block, check if there exists a number that is only valid
    #           if we fill it in one of the cells.
    def solve2(self):
        """
            Use this method if the previous method does not solve the game.

            Now that we have a list of blank cells with possible moves, we can use them
            to help us find the only possible move for a cell by checking blank cells in
            its row, column, and section.
        """

        # Go through each blank cell
        for key_1 in self.possible_moves.keys():
            # A cell is 0 if it has been checked
            if self.possible_moves[key_1][0] != 0:
                # Check rows first
                union_set = []
                for key_2 in self.possible_moves.keys():
                    if key_1[0] == key_2[0]:
                        if key_2 != key_1:
                            union_set.append(set(self.possible_moves[key_2]))

                check = list(set(self.possible_moves[key_1]) - set.union(*union_set))

                if len(check) == 1 and check[0] != 0:
                    move = check[0]
                    self.board[key_1[0]][key_1[1]] = move
                    del self.possible_moves[key_1] # remove key since it's done
                    self.reexamine(key_1, move)
                    continue

                # Check col next
                union_set2 = []
                for key_2 in self.possible_moves.keys():
                    if key_1[1] == key_2[1]:
                        if key_2 != key_1:
                            union_set2.append(set(self.possible_moves[key_2]))

                check2 = list(set(self.possible_moves[key_1]) - set.union(*union_set2))

                if len(check2) == 1 and check2[0] != 0:
                    move = check2[0]
                    self.board[key_1[0]][key_1[1]] = move
                    del self.possible_moves[key_1] # remove key since it's done
                    self.reexamine(key_1, move)
                    continue

                # Check block
                union_set3 = []
                block_row = key_1[0] / 3
                block_col = key_1[1] / 3
                for key_2 in self.possible_moves.keys():
                    if key_2 != key_1:
                        br = key_2[0] / 3
                        bc = key_2[1] / 3
                        if block_row == br and block_col == bc:
                            union_set3.append(set(self.possible_moves[key_2]))

                check3 = list(set(self.possible_moves[key_1]) - set.union(*union_set3))

                if len(check3) == 1 and check3[0] != 0:
                    move = check3[0]
                    self.board[key_1[0]][key_1[1]] = move
                    del self.possible_moves[key_1]
                    self.reexamine(key_1, move)
        
        return

    # Method 3: brute force approach. Try every possible move until the entire board is valid.
    def solve3(self):
        """
            DFS/brute force method. The easiest but most inefficient way to solve Sudoku.
        """
        blank_cells = [] # a list of blank cells

        for r in xrange(9):
            for c in xrange(9):
                if self.board[r][c] == 0:
                    blank_cells.append((r, c))
        self.solve_next(blank_cells)

        return

    def solve_next(self, blank_cells):
        """
            Recurrence method for solving each cell.
        """
        # return true when we reach the leave node
        if blank_cells == []:
            return True

        cell = blank_cells.pop() # get next cell
        moves = self.calculate_moves(cell) # get a list of possible moves for this cell

        # try every move
        while moves:
            self.board[cell[0]][cell[1]] = moves.pop()
            if self.check_board(cell):
                if self.solve_next(blank_cells):
                    return True

        # none of the cell works, so we reset this cell go back to the parent node
        self.board[cell[0]][cell[1]] = 0
        blank_cells.append(cell)
        return False

    def check_board(self, (row, col)):
        """
            Check if the move is valid by finding duplicates in row, column, and section.
        """
        checklist = []

        # check row
        for c in xrange(9):
            number = self.board[row][c]
            if number != 0:
                if number in checklist:
                    #print "duplicate in row"
                    return False
                else:
                    checklist.append(number)

        del checklist[:] # clear list

        # check column
        for r in xrange(9):
            number = self.board[r][col]
            if number != 0:
                if number in checklist:
                    #print "duplicate in column"
                    return False
                else:
                    checklist.append(number)
            
        del checklist[:] # clear list

        # check section
        temp_r = row / 3 * 3
        section_c = col / 3 * 3
        for r in xrange(3):
            section_r = temp_r + r
            for c in xrange(3):
                number = self.board[section_r][section_c + c]
                if number != 0:
                    if number in checklist:
                        #print "duplicate in section"
                        return False
                    else:
                        checklist.append(number)
                
        return True

    # Clean up the possible moves
    def clean(self):
        """
            Delete cells that have already been solved.
        """
        for key in self.possible_moves.keys():
            if self.possible_moves[key][0] == 0:
                del self.possible_moves[key]
        return

    def reexamine(self, position, move):
        """
            Update the neighboring blank cells that have been affected by the move.
        """
        # find which section we're in
        cell_row = position[0] / 3
        cell_col = position[1] / 3
 
        for key, value in self.possible_moves.iteritems():
            # if it's on the same row, column, or section
            if key[0] == position[0] or key[1] == position[1] or (key[0] / 3 == cell_row and key[1] / 3 == cell_col):
                # if the move affect this current cell
                if move in value:
                    value.remove(move)
                    if len(value) == 1 and value != 0:
                        new_move = value[0]
                        self.board[key[0]][key[1]] = new_move
                        value[0] = 0
                        self.reexamine(key, new_move)

        return

    def calculate_moves(self, position):
        """
            Return a list of valid/possible moves for a cell.
        """
        invalid_moves = [] # list of numbers that are already in the neighboring row, column, section
        valid_moves = [1, 2, 3, 4, 5, 6, 7, 8, 9] # return variable

        # check row
        for c in xrange(9):
            current = self.board[position[0]][c]
            if current != 0:
                invalid_moves.append(current)

        # check col
        for r in xrange(9):
            current = self.board[r][position[1]]
            if current != 0 and current not in invalid_moves:
                invalid_moves.append(current)

        # check block
        start_row = position[0] - position[0] % 3
        start_col = position[1] - position[1] % 3
        for r in xrange(3):
            curr_row = start_row + r
            for c in xrange(3):
                curr_col = start_col + c
                current = self.board[curr_row][curr_col]
                if current != 0 and current not in invalid_moves:
                    invalid_moves.append(current)

        # remove invalid_moves
        for n in invalid_moves:
            valid_moves.remove(n)

        return valid_moves

    def count_blank(self):
        """
            Count the number of blank cells.
        """
        num_of_blanks = 0
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    num_of_blanks += 1
        return num_of_blanks

def main():
    input_file = raw_input("Enter file name: ")
    ss = SudokuSolver()
    ss.load_game(input_file)
    print "\n== Initialize Board =="
    ss.display_board()
    number_of_blanks = ss.count_blank()
    print "\nThere are", number_of_blanks, "blanks."
    temp = raw_input("\nPress enter to solve...")

    # solving algorithm
    ss.solve()

    # display the result
    print "\n=== Current Board ==="
    ss.display_board()

    print "\nYayyyy I solved it!!! I'm the best ;D\n"

    return

if __name__ == '__main__':
    import sys
    main()
