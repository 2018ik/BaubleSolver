import ast
import graphics 
import time
lines = []
with open('solutions.txt') as f:
    lines = f.readlines()
solutions = []
for x in range(1, len(lines), 2):
    board = ast.literal_eval(lines[x])
    if board not in solutions:
        solutions.append(board)


print(len(solutions))

# confirm that all solutions are actually found
# def mirror(board):
#     for x in range(len(board)):
#         for y in range(x, len(board)-x):
#             board[x][y], board[y][x] = board[y][x], board[x][y]

# for x in range(1, len(lines), 2):
#     board = ast.literal_eval(lines[x])
#     mirror(board)
#     if board not in solutions:
#         solutions.append(board)
#         print("mirrored solution found")

fig, lines = graphics.initializeBoard()
for board in solutions:
    graphics.updateBoard(board, fig, lines, save_image=True)  