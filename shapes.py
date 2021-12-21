import random
import copy
line = [(0,0), (1,0), (2,0), (3,0)]
long_l = [(0,0), (0,1), (1,0), (2,0), (3,0)]
short_l = [(0,0), (0,1), (1,0), (2,0)]
w = [(0,0), (1,0), (1,1), (2,1), (2,2)]
gun = [(0,0), (1,1), (1,0), (2,0), (3,0)]
square = [(0,0), (0,1), (1,0), (1,1)]
cross = [(1,0), (0,1), (1,1), (2,1), (1,2)]
b = [(0,0), (1,1), (1,0), (2,0), (2,1)]
c = [(0,0), (1,0), (2,0), (0,1), (2,1)]
z = [(0,0), (1,0), (2,0), (2,1), (3,1)]
small_v = [(0,0), (1,0), (1,1)]
big_v = [(0,0), (1,0), (2,0), (2,1), (2,2)]

# group shapes by size
shapes_by_size = [
    [sorted(x) for x in [small_v]], #3
    [sorted(x) for x in [square, short_l, line]], #4
    [sorted(x) for x in [long_l, w, gun, cross, b, c, z, big_v]] #5
]

def shift(shape):
    # Given a shape starting at any coordinate, will shift it so that it is as close to (0,0) as possible
    shifted_shape = []
    min_x = min_y = float('inf')
    for c in shape:
        min_x = min(min_x, c[0])
        min_y = min(min_y, c[1])
    for c in shape:
        shifted_shape.append((c[0] - min_x, c[1] - min_y))
    return sorted(shifted_shape)

def mirror_x(shape):
    mirrored_shape = []
    shift = 0
    for c in shape:
        mirrored_c = (-c[0], c[1])
        mirrored_shape.append(mirrored_c)
        shift = max(shift, abs(mirrored_c[0]))
    for i,c in enumerate(mirrored_shape):
        mirrored_shape[i] = (c[0] + shift, c[1])
    return mirrored_shape

def rotate_clockwise(shape):
    rotated_shape = []
    shift_x = float('inf')
    shift_y = 0
    for c in shape:
        rotated_c = (c[1], -c[0])
        rotated_shape.append(rotated_c)
        shift_x = min(shift_x, abs(rotated_c[0]))
        shift_y = max(shift_y, abs(rotated_c[1]))
    for i,c in enumerate(rotated_shape):
        rotated_shape[i] = (c[0] - shift_x, c[1] + shift_y)
    return rotated_shape
        
def isDuplicate(arr, shape):
    for a in arr:
        if sorted(a) == sorted(shape):
            return True
    return False

def getAllOrientations(shape):
    all_orientations = []
    mirrored_shape = mirror_x(shape)
    for _ in range(4):
        if not isDuplicate(all_orientations, shape):
            all_orientations.append(shape)
        if not isDuplicate(all_orientations, mirrored_shape):
            all_orientations.append(mirrored_shape)
        shape = rotate_clockwise(shape)
        mirrored_shape = rotate_clockwise(mirrored_shape)
    return [sorted(x) for x in all_orientations]

def getAllShapes():
    return [sorted(x) for x in [line, long_l, short_l, w, gun, square, cross, b, c, z, small_v, big_v]]

def getAllOrientationsOfShapes(shapes_list):
    all = []
    for shape in shapes_list:
        for orientation in getAllOrientations(shape):
            all.append(orientation)
    return all

def getShapesForAreaOfSizeN(n):
    # Returns list[list[shapes], list[shapes]] where each inner list represents a possible combination of shapes
    solutions = []
    def backtrack(shapes_by_size, cur, total):
        if total < 0:
            return
        if total == 0:
            if sorted(cur) not in solutions:
                solutions.append(sorted(cur.copy()))
        else:
            for i, shapes_of_size_n in enumerate(shapes_by_size):
                for shape in shapes_of_size_n:
                    shapes_of_size_n.remove(shape)
                    cur.append(shape)
                    backtrack(shapes_by_size, cur, total - i - 3)
                    shapes_of_size_n.insert(i, shape)
                    cur.pop()
    backtrack(shapes_by_size, [], n)
    return solutions
