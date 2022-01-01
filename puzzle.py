import shapes
import graphics 
import time
import random
import datetime

board = [[0]*10 for _ in range(10)]
pieces = shapes.getAllShapes()
colors = {}

min_adjacency = 0 # higher number makes more "human" moves, but will miss all possible combinations 
show_board = False # displays board
save_image = False # saves image for gif, requires show_board to be True

for index,piece in enumerate(pieces):
    for orientation in shapes.getAllOrientations(piece):
        colors["".join([str(x) for x in orientation])] = index+1

def isPositionValid(x, y):
    # Checks if position is both in board and empty
    return x >= 0 and y >= 0 and x + y <= 9 and board[x][y] == 0

def isInBoard(x, y):
    # Similar to isPositionValid but only checks if (x,y) is within the constraint of the board
    return x >= 0 and y >= 0 and x + y <= 9

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
    # ? 1 1 1 ?      ? 1 1 1 ?
    # 5 0 0 0 ?  or  ? 0 0 0 5
    # ? 4 4 4 ?      ? 4 4 4 ?
    # or if there is a 5-long area like:
    # 1 1 1 1 1
    # 0 0 0 0 0
    # 4 4 4 4 4
    # This means we must need the line or long L.
    #
    # **WIP currently only checks for 5-long**

    horizontal_5 = True # this will be true iff five cols in a row go (from top to bottom) taken - not taken - taken
    vertical_5 = True 
    horizontal_3 = True # this will be true iff three cols in a row go (from top to bottom) taken - not taken - taken
    vertical_3 = True 
    for i in range(5):
        vertx, verty = x + i, y
        horzx, horzy = x, y + i
        # checks middle row for empty space
        if not isInBoard(vertx, verty) or board[vertx][verty] not in (0, "#"):
            if i < 3:
                vertical_3 = False
            vertical_5 = False
        if not isInBoard(horzx, horzy) or board[horzx][horzy] not in (0, "#"):
            if i < 3:
                horizontal_3 = False
            horizontal_5 = False
        # checks upper and lower row for taken space
        for direction in [(0,1), (0,-1)]:
            if isInBoard(vertx+direction[0], verty+direction[1]) and board[vertx+direction[0]][verty+direction[1]] in (0, "#"):
                if i < 3:
                    vertical_3 = False
                vertical_5 = False
            if isInBoard(horzx+direction[1], horzy+direction[0]) and board[horzx+direction[1]][horzy+direction[0]] in (0, "#"):
                if i < 3:
                    horizontal_3 = False
                horizontal_5 = False
    if vertical_5 or horizontal_5:
         return True
    # if horizontal_3:
    #     # check for at least one side (left or right) to be blocked
    #     if (not isInBoard(x, y-1) or board[x][y-1] not in (0, "#")) or (not isInBoard(x, y+3) or board[x][y+3] not in (0, "#")):
    #         return True
    # if vertical_3:
    #     # check for at least one side (top or bottom) to be blocked
    #     if (not isInBoard(x-1, y) or board[x-1][y] not in (0, "#")) or (not isInBoard(x+3, y) or board[x+3][y] not in (0, "#")):
    #         return True
    return False
        
def getAllSizes(pieces):
    counter = [0,0,0]
    for piece in pieces:
        if piece in shapes.shapes_by_size[0]:
            counter[0] += 1
        elif piece in shapes.shapes_by_size[1]:
            counter[1] += 1
        else:
            counter[2] += 1
    all_perms = set()
    getAllSizesHelper(0, counter, all_perms)
    return all_perms

def getAllSizesHelper(cur, counter, all_perms):
    all_perms.add(cur)
    for i in range(3):
        if counter[i] > 0:
            counter[i] -= 1
            getAllSizesHelper(cur+i+3, counter, all_perms)
            counter[i] += 1

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
                elif len(path) < 20:
                    # For X sized paths, the subset of the shapes we have must sum to it 
                    all_valid_sizes = getAllSizes([item for item in pieces if item not in seen])
                    if len(path) not in all_valid_sizes:
                        undoFloodFill()
                        return False, []
            # if hasLineArea(x,y) and (shapes.line not in pieces and shapes.long_l not in pieces):
            #     # If there is an enclosed line (see hasLineArea) then we must have a line or long L
            #     undoFloodFill()
            #     return False, []
    undoFloodFill()
    for i, (x, y, piece) in enumerate(seen_pieces):
        # Use the pieces when they are the only fit
        putValidPiece(piece, x, y)
        pieces.remove(seen[i])
    return True, seen_pieces

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
        if min_adjacency > 0:
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

    # isBoardValid sometimes places a piece automatically if it's the only one that fits,
    # so we keep track of these to backtrack later (add back to pieces list and remove)
    valid, placed_pieces = isBoardValid()
    if show_board:
        graphics.updateBoard(board, fig, lines, save_image=save_image)
    if not valid:
        # Backtrack immediately if board is invalid
        return
    if len(pieces) == 0:  
        # A solution must be found if there are no more pieces, since pieces can only be placed in valid locations
        print("found a solution")
        with open('solutions.txt', 'a') as f:
            f.write(str(datetime.datetime.now()) + "\n")
            f.write(str(board) + "\n")
        if show_board:
            time.sleep(5)
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
                        
    # Add back pieces placed by isBoardValid
    for x, y, piece in placed_pieces:
        pieces.append(piece)
        removePiece(piece, x, y)

if show_board:
    fig, lines = graphics.initializeBoard()

# board = [
# [0, 0, 0, 0,0, 10, 5, 5, 5, 5], 
# [0, 0, 0, 0, 10, 10, 8, 8, 5, 0], 
# [0, 0, 0, 0, 10, 8, 8, 8, 0, 0], 
# [0, 0, 0, 0, 10, 4, 4, 0, 0, 0], 
# [0, 0, 0, 0, 4, 4, 0, 0, 0, 0],
# [0, 0, 0, 0, 4, 0, 0, 0, 0, 0], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# real_pieces = []
# for piece in pieces:
#     if colors["".join([str(x) for x in piece])]  in [2,6,12,11,7,3,9]:
#         real_pieces.append(piece)
# pieces = real_pieces
backtrack()

