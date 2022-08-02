import time
import copy
import random
import pygame
import numpy as np
from simanneal import Annealer

# Board to be solved
board = np.array([
    0, 8, 0, 0, 0, 0, 0, 3, 2,
    4, 0, 0, 0, 0, 6, 5, 0, 0,
    0, 0, 0, 0, 3, 0, 1, 0, 0,
    0, 0, 3, 6, 0, 5, 4, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 6,
    0, 0, 4, 8, 0, 7, 9, 0, 0,
    0, 0, 9, 0, 5, 0, 0, 0, 0,
    0, 0, 8, 7, 0, 0, 0, 0, 9,
    6, 2, 0, 0, 0, 0, 0, 8, 0
])

original_board = np.reshape(copy.deepcopy(board), (9, 9))

# Backtracking methods ---------------------------------------------
def solve_backtracking(board):
    pos = find_empty(board)

    if not pos:
        return True
    else:
        row, column = pos

    for num in range(1, 10):
        if check_valid(board, num, (row, column)):
            board[row][column] = num
            update_display(board, False)

            if solve_backtracking(board):
                return True

            board[row][column] = 0

    return False

def check_valid(board, num, pos):
    for row in range(len(board[0])):
        if board[pos[0]][row] == num and pos[1] != row:
            return False

    for column in range(len(board)):
        if board[column][pos[1]] == num and pos[0] != column:
            return False

    sub_x = pos[1] // 3
    sub_y = pos[0] // 3

    for row in range(sub_y * 3, sub_y * 3 + 3):
        for column in range(sub_x * 3, sub_x * 3 + 3):
            if board[row][column] == num and (row, column) != pos:
                return False

    return True

def print_board(board):
    for i in range(len(board)):
        if i % 3 == 0 and i != 0:
            print('- - - - - - - - - - -')

        for n in range(len(board[i])):
            if n % 3 == 0 and n != 0 and n != 9:
                print('|' + ' ', end='')
            if n == 8:
                print(str(board[i][n]))
            else:
                print(str(board[i][n]) + ' ', end='')

def find_empty(board):
    for row in range(len(board)):
        for column in range(len(board[0])):
            if board[row][column] == 0:
                return (row, column)

    return None

def update_display(board, done):
    WIDTH = 550
    background_color = (251, 247, 245)
    original_element = (0, 0, 0)
    new_element = (0, 255, 0)
    pygame.init()
    window = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption('Sudoku')
    window.fill(background_color)
    myFont = pygame.font.SysFont('Comic Sans MS', 35)

    for i in range(10):
        if (i % 3 == 0):
            line_width = 4
        else:
            line_width = 2

        pygame.draw.line(window, (0, 0, 0), (50 + (50 * i), 50), (50 + (50 * i), 500), line_width)
        pygame.draw.line(window, (0, 0, 0), (50, 50 + (50 * i)), (500, 50 + (50 * i)), line_width)
        
    for row in range(9):
        for column in range(9):
            if (board[row][column] != 0):
                if (board[row][column] == original_board[row][column] or done):
                    value = myFont.render(str(board[row][column]), True, original_element)
                else:
                    value = myFont.render(str(board[row][column]), True, new_element)
                window.blit(value, (((column + 1) * 50 + 15), ((row + 1) * 50)))

    pygame.display.update()

# Annealing methods ------------------------------------------------
def print_sudoku(state):
    border = "------+-------+------"
    rows = [state[i:i+9] for i in range(0,81,9)]
    for i,row in enumerate(rows):
        if i % 3 == 0:
            print(border)
        three = [row[i:i+3] for i in range(0,9,3)]
        print(" | ".join(
            " ".join(str(x or "_") for x in one)
            for one in three
        ))
    print(border)

def coord(row, col):
    return row*9+col

def block_indices(block_num):
    # Returns linear array indices corresponding to the sq block, row major, 0-indexed.
    firstrow = (block_num // 3) * 3
    firstcol = (block_num % 3) * 3
    indices = [coord(firstrow+i, firstcol+j) for i in range(3) for j in range(3)]
    return indices

def initial_solution(problem):
    # Provide sudoku problem, generate an init solution by randomly filling
    # each sq block without considering row/col consistency
    solution = problem.copy()
    for block in range(9):
        indices = block_indices(block)
        block = problem[indices]
        zeros = [i for i in indices if problem[i] == 0]
        to_fill = [i for i in range(1, 10) if i not in block]
        random.shuffle(to_fill)
        for index, value in zip(zeros, to_fill):
            solution[index] = value
    return solution

class Sudoku_Sq(Annealer):
    def __init__(self, problem):
        self.problem = problem
        state = initial_solution(problem)
        super().__init__(state)
    def move(self):
         # Randomly swap two cells in a random square
        block = random.randrange(9)
        indices = [i for i in block_indices(block) if self.problem[i] == 0]
        m, n = random.sample(indices, 2)
        self.state[m], self.state[n] = self.state[n], self.state[m]
    def energy(self):
        # Calculate the number of violations: assume all rows are ok
        column_score = lambda n: -len(set(self.state[coord(i, n)] for i in range(9)))
        row_score = lambda n: -len(set(self.state[coord(n, i)] for i in range(9)))
        score = sum(column_score(n)+row_score(n) for n in range(9))
        # Early quit, we found a solution
        if score == -162:
            self.user_exit = True 
        return score

# Runs the backtracking solution
def backtracking(board):
    solve_backtracking(board)
    update_display(board, True)
    time.sleep(5)
    print('Solution:')
    print_board(board)

# Runs the annealing solution
def annealing():
    sudoku = Sudoku_Sq(board)
    sudoku.copy_strategy = "method"
    print_sudoku(sudoku.state)
    sudoku.Tmax = 0.5
    sudoku.Tmin = 0.05
    sudoku.steps = 100000
    sudoku.updates = 100
    state, e = sudoku.anneal()
    print("\n")
    print('Solution:')
    print_sudoku(state)
    print("E=%f (expect -162)" % e)

# Run the program
if __name__ == '__main__':
    solution = input('Do you want to solve Sudoku using backtracking (b) of simulated annealing (a): ')
    if solution == 'b':
        board = np.reshape(board,(9, 9))
        board = board.tolist()
        backtracking(board)
    elif solution == 'a':
        annealing()
    else:
        print('Invalid input entered!')
        exit()