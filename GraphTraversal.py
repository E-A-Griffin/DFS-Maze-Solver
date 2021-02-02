#!/usr/bin/env python3
# Error numbers for file I/O
import errno
import functools
import operator
from enum import Enum
# from numpy import array
from sys import argv


def read_file(file_name):
    """
    Read 'file_name' and return a list of strings of the words separated
    by whitespace in 'file_name'.
    """
    # try to read file
    try:
        with open(file_name) as f:
            # file->array of words(strings) in file
            return functools.reduce(operator.iconcat, map(str.split,
                                                          f.readlines()))
    except IOError as e:
        print(file_name,
              ('doesn\'t exist' if e.errno == errno.ENOENT
               else 'cannot be read' if e.errno == errno.EACCES
               else 'produced an unknown error'))


def write_file(file_name, s):
    """
    Read 'file_name' and return a list of strings of the words separated
    by whitespace in 'file_name'.
    """
    # try to write to file
    try:
        with open(file_name, 'w') as f:
            # print('Writing',s,'to',file_name)
            f.write(s)
    except IOError as e:
        print(file_name, 'couldn\'t be written to')


def partition(n, l):
    """
    Yield partition of list l into a list of n-sized lists
    ex:
    list(partition(5, [1,2,3,4,5,6,7,8,9,10]))->[[1,2,3,4,5],[6,7,8,9,10]]
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]


Dir = Enum('Dir', 'N S E W NE NW SE SW')
Dir_Dict = Dir.__members__
bullseye_sym = 'O'


def is_bullseye(v):
    """
    True iff v is the bullseye.
    """
    return v[0] == bullseye_sym


def is_red(v):
    """
    True iff v is red. Does not perform string validation to ensure v is either
    red or blue.
    """
    return v[0] == 'R'


def get_dir(v):
    """
    Takes in a string representing a graph vertex v and returns it's cardinal
    direction
    """
    chars = v[2:]
    if chars in Dir_Dict:
        return Dir[chars]
    else:
        print('Invalid direction')
        exit()


inc = functools.partial(operator.add, 1)
def dec(y): return y-1


def identity(x):
    """x->x"""
    return x


# dict that takes in a Dir and returns a pair of functions to be applied to the
# x and y coordinates of a vertex respectively to move in that direction
dir_to_fn = {Dir.N: [dec, identity],
             Dir.NE: [dec, inc],
             Dir.NW: [dec, dec],
             Dir.E: [identity, inc],
             Dir.S: [inc, identity],
             Dir.SE: [inc, inc],
             Dir.SW: [inc, dec],
             Dir.W: [identity, dec]}


def neighborhood(G, x, y):
    """
    Given a list of lists G of elements of a graph and a vertex v ∈ G, return
    the neighborhood of v.
    """
    v = G[x][y]
    v_is_red = is_red(v)
    v_dir = get_dir(v)

    # neighborhood
    N = []
    # Change in x and change in y functions
    Δx, Δy = dir_to_fn[v_dir]
    cur_x = x
    cur_y = y

    while(0 <= Δx(cur_x) < len(G) and 0 <= Δy(cur_y) < len(G[0])):
        cur_x = Δx(cur_x)
        cur_y = Δy(cur_y)
        # if coordinate has opposite color to v
        if (is_bullseye(G[cur_x][cur_y]) or v_is_red != is_red(G[cur_x][cur_y])):
            N.append([cur_x, cur_y])

    return {'red?': v_is_red, 'dir': v_dir, 'coord': [x, y],
            'neighborhood': None if not N else N}


def build_graph(s_arr):
    """
    Takes in a list of strings 's_arr' where the first and second elements are
    the number of columns and number of rows respectively and builds a graph
    based on this list.
    """
    row_n = int(s_arr[0])
    col_n = int(s_arr[1])

    coords = list(partition(col_n, s_arr[2:]))

    G = []

    for i in range(row_n):
        G.append([])
        for j in range(col_n):
            if i != row_n-1 or j != col_n-1:
                G[i].append(neighborhood(coords, i, j))
            # handle bullseye
            else:
                G[i].append({'red?': None, 'dir': None, 'coord': [row_n-1, col_n-1],
                             'neighborhood': None})

    return G, [row_n-1, col_n-1]


def find_bullseye(G, bullseye, v=None, path=[], explored=set()):
    """
    Performs a DFS on G to find a path from v->bullseye. If v is not supplied
    explicitly, v is calculated as the top left (G[0][0]) position of G.
    """
    # Start search at top-left corner
    if v == None:
        v = G[0][0]

    # add v to path iff path is empty
    if not path:
        path.append(v['coord'])

    if v['coord'] == bullseye:
        return path

    # prevent cycles
    if str(v['coord']) in explored:
        return None

    explored.add(str(v['coord']))
    if v['neighborhood']:
        for neighbor in v['neighborhood']:
            if str(neighbor) not in explored:
                u = G[neighbor[0]][neighbor[1]]
                temp = find_bullseye(G, bullseye, u, path+[neighbor], explored)
                if temp:
                    return temp

    return None


def path_to_disp(path, disp=''):
    """
    Takes a list of coordinates representing a path and converts it to an
    equivalent string of displacements from the starting position to the final
    position.

    ex:
    [[0, 0], [2, 0], [7, 5], [4, 5], [2, 7], [1, 7], [0, 6], [7, 6], [6, 7],
     [1, 2], [1, 0], [4, 3], [2, 5], [4, 7], [7, 7]] ->
    '2S 5SE 7N 2W 1W 1SE 1NE 2E 7S 1NE 5NW 2W 3SE 2NE 2SE 3S'
    """
    if len(path) <= 1:
        return disp + '\n'

    Δx = path[1][0] - path[0][0]
    Δy = path[1][1] - path[0][1]
    dir_x = 'S' if Δx > 0 else 'N' if Δx < 0 else ''
    dir_y = 'E' if Δy > 0 else 'W' if Δy < 0 else ''
    s = str(max(abs(Δx), abs(Δy))) + dir_x + dir_y

    return path_to_disp(path[1:], disp + s + ' ')


# Do it all
G, bullseye = build_graph(read_file(argv[1]))
write_file(argv[2], path_to_disp(find_bullseye(G, bullseye)))

# Debugging


def parse_path(path, G):
    """
    Traverse path (if possible) on G from first coordinate to last.
    """
    x1, y1 = path[0]
    v = G[x1][y1]
    line_count = 0
    print([x1, y1], end='')
    for x, y in path[1:]:
        line_count += 1
        # Check that next element in path is viable
        if [x, y] in v['neighborhood']:
            print(' ->', [x, y], end='')
            if line_count % 7 == 0:
                print()
        else:
            print('bad!')
            exit()

        v = G[x][y]

    print()
