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

## Demo

Example output:

```bash
poetry run sudoku-solver --file samples/input_easy.csv 
==== Input Board ====
1 6 _ | _ 7 _ | _ _ 3 
_ 5 9 | 4 _ _ | 6 _ _ 
3 _ _ | _ 9 8 | _ 5 _ 
---------------------
_ _ _ | 3 2 _ | 9 7 _ 
4 7 _ | _ _ _ | _ 8 5 
_ 3 6 | _ 8 5 | _ _ _ 
---------------------
_ 9 _ | 2 4 _ | _ _ 8 
_ _ 8 | _ _ 7 | 5 3 _ 
2 _ _ | _ 5 _ | _ 4 9 

There are 45 empty cells.

=== Complete Board ==
1 6 4 | 5 7 2 | 8 9 3 
8 5 9 | 4 3 1 | 6 2 7 
3 2 7 | 6 9 8 | 4 5 1 
---------------------
5 8 1 | 3 2 4 | 9 7 6 
4 7 2 | 1 6 9 | 3 8 5 
9 3 6 | 7 8 5 | 2 1 4 
---------------------
7 9 5 | 2 4 3 | 1 6 8 
6 4 8 | 9 1 7 | 5 3 2 
2 1 3 | 8 5 6 | 7 4 9
```
