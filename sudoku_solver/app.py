import argparse
import os

from .solver import SudokuSolver

def main():
    parser = argparse.ArgumentParser(description="A command-line Sudoku solver.")
    parser.add_argument('--file', required=True, help='Path to the Sudoku puzzle file.')
    parser.add_argument("-v", "--verbose", default=False, help="Enable verbose output.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("-m", "--model", default="mnist.onnx", help="Path to the ONNX model file.")
    args = parser.parse_args()

    solver = SudokuSolver()
    if (args.file.endswith('.csv')):
        solver.load_csv(args.file)
    else:
        # attempt to load it as image
        from . import image_process
        # Download and load the deep learning model
        model_path = image_process.download_model(args.model)
        if model_path is None:
            print("Could not download or find the model. Exiting.")
            return

        extracted_board = image_process.extract_sudoku_board(args.file, model_path, args.debug)
        if extracted_board is None:
            print("Failed to extract Sudoku board from image")
            return
        solver.load_board(extracted_board)
    
    print("\n==== Input Board ====")
    solver.display_board()
    
    number_of_blanks = solver.get_empty_cell_count()
    print(f"\nThere are {number_of_blanks} empty cells.")
    if number_of_blanks == 9*9:
        print("Empty Sudoku board cannot be solved!")
        return

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