import argparse
from .solver import SudokuSolver

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="A command-line Sudoku solver.")
    parser.add_argument('--file', required=True, help='Path to the Sudoku puzzle file.')
    args = parser.parse_args()
    
    ss = SudokuSolver()
    ss.load_csv(args.file)
    
    print("\n==== Input Board ====")
    ss.display_board()
    
    number_of_blanks = ss.get_empty_cell_count()
    print(f"\nThere are {number_of_blanks} empty cells.")

    ss.solve()

    # display the result
    print("\n=== Complete Board ==")
    ss.display_board()

    # in case the board is invalid or impossible to solve
    if ss.get_empty_cell_count() != 0:
        print("\nCould not solve the puzzle completely.\n")

    return

if __name__ == '__main__':
    main()