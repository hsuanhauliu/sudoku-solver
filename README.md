# Sudoku Solver

A simple script that solves Sudoku.

## Installation

```bash
git clone https://github.com/hsuanhauliu/sudoku-solver.git
cd sudoku-solver
poetry install
```

## Usage

Create a CSV file that contains the Sudoku board. Use 0 to indicate empty cells. The puzzle must be solvable.

See [samples](samples/) for examples.

```bash
poetry run sudoku-solver --file <input_file_name>
```

### Screenshot

![screenshot](assets/screenshot.jpg "screenshot")
