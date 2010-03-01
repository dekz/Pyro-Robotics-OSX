def n_queens(n, width):
    if n == 0:
        return [[]] 
    else:
        return add_queen(n-1, width, n_queens(n-1, width))

def add_queen(new_row, width, previous_solutions):
    solutions = []
    for sol in previous_solutions:
        for new_col in range(width):
            if safe_queen(new_row, new_col, sol):
                solutions.append(sol + [new_col])
    return solutions

def safe_queen(new_row, new_col, sol):
    for row in range(new_row):
        if (sol[row] == new_col or
            sol[row] + row == new_col + new_row or
            sol[row] - row == new_col - new_row):
            return 0
    return 1

def check_solution(sol):
    set = []
    row = 0
    for col in sol:
        set.append( col )
        if not safe_queen( row, col, set):
            return 0
        row += 1
    return 1

def fitness(sol):
    set = []
    row = 0
    sum = 0
    for col in sol:
        set.append( col )
        if col < 0:
            return 0
        sum += safe_queen( row, col, set)
        row += 1
    return sum

if __name__ == '__main__':
    for sol in n_queens(8, 8):
        print sol
