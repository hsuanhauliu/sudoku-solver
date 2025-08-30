import argparse
from .solver import SudokuSolver

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="A command-line Sudoku solver.")
    parser.add_argument('--file', required=True, help='Path to the Sudoku puzzle file.')
    parser.add_argument("-v", "--verbose", default=False, help="Enable verbose output.")
    args = parser.parse_args()

    solver = SudokuSolver()
    if (args.file.endswith('.csv')):
        solver.load_csv(args.file)
    else:
        # attempt to load it as image
        from .image_process import extract_sudoku_board
        extracted_board = extract_sudoku_board(args.file)
        if extracted_board is None:
            print("Failed to extract Sudoku board from image")
            return # Tesseract error occurred
        solver.load_board(extracted_board)
    
    print("\n==== Input Board ====")
    solver.display_board()
    
    number_of_blanks = solver.get_empty_cell_count()
    print(f"\nThere are {number_of_blanks} empty cells.")

    solver.solve()

    # display the result
    print("\n=== Complete Board ==")
    solver.display_board()

    # in case the board is invalid or imposolverible to solve
    if solver.get_empty_cell_count() != 0:
        print("\nCould not solve the puzzle completely. The input could be invalid.\n")

    return

if __name__ == '__main__':
    main()