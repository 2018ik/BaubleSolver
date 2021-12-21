import shapes
import graphics 
import time
import random
import datetime

board = [[0]*10 for _ in range(10)]
pieces = shapes.getAllShapes()
colors = {}
min_adjacency = 5

for index,piece in enumerate(pieces):
    for orientation in shapes.getAllOrientations(piece):
        colors["".join([str(x) for x in orientation])] = index+1

def isPositionValid(x, y):
    # Checks if position is both in board and empty
    return x >= 0 and y >= 0 and x + y <= 9 and board[x][y] == 0

def floodfill(x, y, path):
    # Helper function for isBoardValid, fills an enclosed space and returns coordinates 
    if isPositionValid(x,y):
        path.append((x,y))
        board[x][y] = "#"
        for direction in [(1,0), (0,1), (-1,0), (0,-1)]:
            floodfill(x+direction[0], y+direction[1], path)

def undoFloodFill():
    # Helper function for isBoardValid, undos floodfill
    for x in range(len(board)):
        for y in range(len(board)-x): 
            if board[x][y] == "#":
                board[x][y] = 0

def putValidPiece(piece, x, y):
    # Removes piece from board, used to backtrack
    for piece_x, piece_y, in piece:
        board[x + piece_x][y + piece_y] = colors["".join([str(x) for x in piece])]

def hasLineArea(x, y):
    # Check if there is a 3-long enclosed area like:
    # 1 1 1 1
    # 5 0 0 0
    # 4 4 4 4
    # or if there is a 5-long area like:
    # 1 1 1 1 1
    # 0 0 0 0 0
    # 4 4 4 4 4
    # This means we must need the line or long L
    vertical_enclosed = True
    horizontal_enclosed = True
    vertical_open = True
    horizontal_open = True
    for edges in [(-1, 0), (3, 0)]:
        if isInBoard(x+edges[0], y) and board[x+edges[0]][y] not in (0, "#"):
            vertical_open = False
    for edges in [(0, -1), (0, 3)]:
        if isInBoard(x, y+edges[1]) and board[x][y+edges[1]] not in (0, "#"):
            horizontal_open = False
    for i in range(3):
        vertx, verty = x + i, y
        horzx, horzy = x, y + i
        if not isInBoard(vertx, verty) or board[vertx][verty] not in (0, "#"):
            vertical_enclosed = False
        if not isInBoard(horzx, horzy) or board[horzx][horzy] not in (0, "#"):
            horizontal_enclosed = False
        for direction in [(0,1), (0,-1)]:
            if isInBoard(vertx+direction[0], verty+direction[1]) and board[vertx+direction[0]][verty+direction[1]] in (0, "#"):
                vertical_enclosed = False
        for direction in [(1,0), (-1,0)]:
            if isInBoard(horzx+direction[0], horzy+direction[1]) and board[horzx+direction[0]][horzy+direction[1]] in (0, "#"):
                horizontal_enclosed = False
    return (vertical_enclosed and not vertical_open) or (horizontal_enclosed and not horizontal_open)
        
def isBoardValid():
    # Very rudimentary checks for board validity
    # If a pieces are placed during this process, they are returned
    seen = []
    seen_pieces = []
    for x in range(len(board)):
        for y in range(len(board)-x):  
            if board[x][y] == 0:
                path = []
                floodfill(x, y, path)
                if len(path) < 7:
                    # If path is 6 or less, it must actually be a shape
                    true_y = min([y for _,y in path])
                    path = shapes.shift(path)
                    success = False
                    for piece in pieces:
                        orientations = shapes.getAllOrientations(piece)
                        if sorted(path) in orientations and piece not in seen:
                            success = True
                            seen.append(piece)
                            seen_pieces.append((x, true_y, sorted(path)))
                    if not success:
                        undoFloodFill()
                        return False, []
                elif len(path) < 14:
                    # For X sized paths, we can calculate the shapes required
                    all_valid_moves = shapes.getShapesForAreaOfSizeN(len(path))
                    at_least_one_works = False
                    for possible_combination in all_valid_moves:
                        this_one_works = True
                        for shape in possible_combination:
                            if shape not in pieces:
                                this_one_works = False
                        if this_one_works:
                            at_least_one_works = True
                            break
                    if not at_least_one_works:
                        undoFloodFill()
                        return False, []
            if hasLineArea(x,y) and (shapes.line not in pieces and shapes.long_l not in pieces):
                # If there is an enclosed line (see function) then we must have a line or long L
                undoFloodFill()
                return False, []
    undoFloodFill()
    for i, (x, y, piece) in enumerate(seen_pieces):
        # Use the pieces when they are the only fit
        putValidPiece(piece, x, y)
        pieces.remove(seen[i])
    return True, seen_pieces

def isInBoard(x, y):
    # Similar to isValid but only checks if (x,y) is within the constraint of the board
    return x >= 0 and y >= 0 and x + y <= 9

def getAdjacency(x, y):
    # Gets the adjacency heuristic of (x,y)
    # Directly adjacent = 2 pts, diagonal = 1 pts, if border = 1 pts
    adjacency = 0
    isBorder = 0
    for direction in [(1,0), (0,1), (-1,0), (0,-1)]:
        if isInBoard(x+direction[0], y+direction[1]) and board[x+direction[0]][y+direction[1]] != 0:
            adjacency += 2
        elif not isInBoard(x+direction[0], y+direction[1]):
            isBorder = 1
    for direction in [(1,0), (0,1), (-1,0), (0,-1)]:
        if isInBoard(x+direction[0], y+direction[1]) and board[x+direction[0]][y+direction[1]] != 0:
            adjacency += 1
        elif not isInBoard(x+direction[0], y+direction[1]):
            isBorder = 1
    return adjacency + isBorder

def putPiece(piece, x, y):
    # Attempts to place piece. Piece is only placed if 
    # 1) the position is valid - all spaces must be in the board and occupied by "0"
    # 2) there is a minimum threshold of adjacency for the placed piece.
    total_adjacency = 0
    for piece_x, piece_y, in piece:
        if not isPositionValid(x + piece_x, y + piece_y):
            return False
        total_adjacency += getAdjacency(x + piece_x, y + piece_y)
    if total_adjacency < min_adjacency and len(pieces) < 12:
        return False
    putValidPiece(piece, x, y)
    return True

def removePiece(piece, x, y):
    # Removes piece from board, used to backtrack
    for piece_x, piece_y, in piece:
        board[x + piece_x][y + piece_y] = 0

def backtrack():
    # Solves the puzzle
    # print(board)
    valid, seen_pieces = isBoardValid()
    # graphics.updateBoard(board, fig, lines) #uncomment this for fancy animation
    if not valid:
        # Backtrack immediately if board is invalid
        return
    if len(pieces) == 0:  
        # A solution must be found if there are no more pieces, since pieces can only be placed in valid locations
        print("found a solution")
        with open('solutions.txt', 'a') as f:
            f.write(str(datetime.datetime.now()) + "\n")
            f.write(str(board) + "\n")
        # time.sleep(5) # for animation purposes
    else:
        # The order of the pieces does not matter; if going ...cross, gun, b does not work, 
        # then going ...gun, b, cross will not work either. Therefore, we can simply choose
        # a random piece for each level of recursion.
        piece = random.choice(pieces)
        for orientation in shapes.getAllOrientations(piece):
            for x in range(len(board)):
                for y in range(len(board)-x):  
                    if putPiece(orientation, x, y):
                        pieces.remove(piece)
                        backtrack()
                        removePiece(orientation, x, y)
                        pieces.append(piece)
    for x, y, piece in seen_pieces:
        pieces.append(piece)
        removePiece(piece, x, y)
#fig, lines = graphics.initializeBoard() #uncomment this for fancy animation

# board = [[2, 2, 2, 2, 0, 0, 0, 0, 0, 0], 
# [2, 10, 10, 10, 0, 0, 0, 0, 0, 0], 
#  [10, 10, 0, 0, 0, 0, 0, 0, 0, 0], 
#  [9, 9, 9, 0, 0, 0, 0, 0, 0, 0], 
#  [9, 7, 9, 0, 0, 0, 0, 0, 0, 0],
#  [7, 7, 7, 0, 0, 0, 0, 0, 0, 0], 
#  [1, 7, 4, 4, 0, 0, 0, 0, 0, 0], 
#  [1, 4, 4, 0, 0, 0, 0, 0, 0, 0], 
#  [1, 4, 0, 0, 0, 0, 0, 0, 0, 0], 
#  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# real_pieces = []
# for piece in pieces:
#     if colors["".join([str(x) for x in piece])] not in  [2,10,9,7,4,1]:
#         real_pieces.append(piece)

# pieces = real_pieces
# print(isBoardValid())
# while 1:
#     graphics.updateBoard(board, fig, lines)
backtrack()

