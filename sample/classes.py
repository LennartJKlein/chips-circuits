"""
helpers.py
- Cell
- Board
- Gate
- Netlist
- Calculate path
"""

import settings

import colors as CLR
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ast import literal_eval
import collections
import heapq
import csv
      
class Board:
    """
    PLACEHOLDER
    """

    def __init__(self, width, height, depth):
        """
        :param width: How many columns the board uses
        :param height: How many rows the board uses
        :param depth: How many layers the board uses

        :return: Numpyboard filled with 0's for empty paths, 1's for gates and >2 for paths
        """

        self.width = width
        self.height = height
        self.depth = depth
        self.board = np.zeros((self.depth, self.height, self.width), dtype=int)
        self.paths = []
        self.gatesObjects = np.empty((self.depth, self.height, self.width), dtype=object)
        self.gatesNumbers = np.zeros((self.depth, self.height, self.width), dtype=int)

    def calculate_distance(self, a, b):
        """
        :param a: Starting coord
        :param b: Goal coord

        :return: The distance between two coords
        """

        dx = (a[2] - b[2]) ** 2
        dy = (a[1] - b[1]) ** 2
        dz = (a[0] - b[0]) ** 2
        return (dx + dy + dz) ** 0.5

    def calculate_delta(self, a, b):
        """
        :param a: Starting coord
        :param b: Goal coord

        :return: The delta distance between two coords
        """

        dx = abs(a[2] - b[2])
        dy = abs(a[1] - b[1])
        dz = abs(a[0] - b[0])
        return dx + dy + dz

    def get_coords(self, axes, label):
        """
        :param: axes: Devided coord into Z, Y, X
        :param: label: Give a coord in board the corresponding label

        :return: The current Z, Y, X of a coord in the numby board
        """

        labels = np.argwhere(self.board == label)
        coords = []

        for coord in labels:
            if axes == 'z':
                coords.append(coord[0])
            if axes == 'y':
                coords.append(coord[1])
            if axes == 'x':
                coords.append(coord[2])

        return coords

    def get_neighbors(self, coord):
        """
        :param: Current coord in queue

        :return: All valid neighbors of the current coord
        """

        (z, y, x) = coord
        is_valid = []
        neighbors = [[z, y, x+1], [z, y, x-1], [z, y+1, x], [z, y-1, x], [z+1, y, x], [z-1, y, x]]
        for neighbor in neighbors:
            if self.valid_coord(neighbor):
                is_valid.append(neighbor)
        return is_valid
    
    def get_score(self):
        """
        :return: Accumulated length of all the paths
        """

        return len(np.argwhere(self.board >= settings.SIGN_PATH_START))

    def print_score(self):
        """
        :return: Print the score
        """

        print(CLR.YELLOW + "Score: " + str(self.get_score()) + CLR.DEFAULT)
        print("")

    def plot_paths(self, graph, own_color):
        """
        :param graph: Plot a graph
        :param own_color: Seperate the paths with a color

        :return: Plot a graph with a score based on iterations
        """

        for path in self.paths:
            if own_color:
                graph.plot(
                  path.get_coords('x'),
                  path.get_coords('y'),
                  path.get_coords('z'),
                  zorder=-1,
                  color=path.color
                )
            else:
                graph.plot(
                  path.get_coords('x'),
                  path.get_coords('y'),
                  path.get_coords('z'),
                  zorder=-1
                )

    def plot(self):
        """
        :return: graph configurations
        """

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_zlim(self.depth, 0)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # Add paths to the graph
        self.plot_paths(plt, False)

        # Add gates to the graph
        ax.scatter(
          self.get_coords('x', settings.SIGN_GATE),
          self.get_coords('y', settings.SIGN_GATE),
          self.get_coords('z', settings.SIGN_GATE),
          color="black"
        )

        # Show the graph
        plt.show()

    def print_board(self):
        """
        :return: Show the numpyboard in ASCII
        """
        print(self.board)

    def set_gates(self, netlist):
        """
        :param netlist: Give the selected netlist in settings.py

        :return: Set all gates in the board
        """

        # Read a CSV file for gate tuples
        with open('data/gates'+ str(settings.FILE_GATES) + '.csv', 'r') as csvfile:
          reader = csv.reader(csvfile)

          # Skip the header
          next(reader, None)


          for row in reader:

              # Skip row if the data is commented
              if row[0][:1] != '#':

                  # Get the name of the gate
                  gateLabel = int(row[0])

                  # Fetch the coords X and Y
                  gateX = int(row[1])
                  gateY = int(row[2])
                  gateZ = int(row[3])

                  # Save gate object in gates list
                  new_gate = Gate(netlist, gateLabel, gateX, gateY, gateZ)

                  # Set a gate in the grid for every row in the file
                  self.gatesObjects[gateZ, gateY, gateX] = new_gate
                  self.gatesNumbers[gateZ, gateY, gateX] = gateLabel
                  self.board[gateZ, gateY, gateX] = settings.SIGN_GATE

    def valid_coord(self, coord):
        """
        :param coord: Currend coord in board

        :return: Checks if the coord is within the set boundaries
        """

        # Check if the coord is positive
        if any(axes < 0 for axes in coord):
            return False

        # Check if the coord falls within the board
        if coord[2] >= self.width or \
           coord[1] >= self.height or \
           coord[0] >= self.depth:
            return False    

        return True

class Experiment:
    """
    PLACEHOLDER
    """

    def __init__(self, iterations, show_results, show_data, show_plot):
        """
        :param iterations: The amount of iterations of the board
        :param show_results: Boolean option to print with the board number and the corresponding score
        :param show_data: Boolean option to print the ASCII board
        :param: show_plot: Boolean option to print the Numpy plot

        :return: list of boards, netlists and scores
        """
        self.boards = []
        self.netlists = []
        self.score_drawn_paths = []
        self.scores = []

        for i in range(iterations):

            # Initiate a board with a specified size
            board = Board(settings.BOARD_WIDTH, settings.BOARD_HEIGHT, settings.BOARD_DEPTH)
            self.add_board(board)

            # Create a netlist and calculate path
            netlist = Netlist(settings.FILE_GATES)
            self.add_netlist(netlist)

            # Create a set of gates on the board
            board.set_gates(netlist)

            # Calculate the connections in this netlist
            netlist.execute_connections(board)

            # Get the scores of this iteration
            self.score_drawn_paths.append(netlist.get_result("made"))
            self.scores.append(board.get_score())

            if show_results:
                # Print results of this execution
                print("------------ BOARD: " + str(i) + " --------------")
                netlist.print_result()
                board.print_score()

            if show_data:
                # Print the board data
                board.print_board()

            if show_plot:
                # Plot the board
                board.plot()

    def add_board(self, board):
        """
        :param board: State of current board

        :retrun: Add a board to the board list 
        """

        self.boards.append(board)

    def add_netlist(self, netlist):
        """
        :param netlist: State of current netlist

        :retrun: Add a netlist to the netlist list
        """

        self.netlists.append(netlist)

    def get_boards(self):
        """
        return: Get all boards in the board list
        """

        return self.boards

    def get_netlists(self):
        """
        :return: Get all netlists in the netlist list
        """

        return self.netlists

    def get_scores(self):
        """
        return: Get all scores in the scores list
        """

        scores = []
        for board in self.boards:
            scores.append(board.score())
        return scores

    def plot_score(self):
        """
        :return: Plot a graph to show the scores over the different iterations
        """

        fig = plt.figure()
        ax = fig.gca()
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Score")
        ax.plot(self.scores)
        plt.show()

class Gate:
    """
    PLACEHOLDER
    """
    def __init__(self, netlist, label, x, y, z):
        """
        :param netlist: Give the selected netlist in settings.py 
        :param label: Label for a gate
        :param x:     x-axis location
        :param y:     y-axis location
        :param y:     z-axis location 
        """

        self.label = label
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)
        self.spaces_needed = 0

        for connection in netlist.list:
            # Connection + 1 to match label of gate
            if (connection[0] + 1) == label or (connection[1] + 1) == label:
                self.spaces_needed += 1

    def get_free_spaces(self, board, coord):
        """
        :return: Interger with the amount of free spaces
        """

        free_spaces = 0

        for neighbor in board.get_neighbors(coord):
            # Count if neighbor is free on the board
            if board.board[neighbor[0], neighbor[1], neighbor[2]] == 0:
                counter += 1

        return free_spaces - self.spaces_needed

    def __str__(self):
        return self.label

class Netlist:
    """
    Netlist are tuples reperesenting the contecion between two gates. Al conections
    must be made to solve the case.

    :param: number:     id of the netlist
    """

    def __init__(self, number):
        self.filename = "data/netlist"
        self.filename += str(number)
        self.filename += ".txt"
        self.connections = 0
        self.connections_made = 0
        self.connections_broken = 0

        # Open netlist and read with literal evaluation
        with open(self.filename) as f:
            self.list = f.read()

        self.list = literal_eval(self.list)

    def execute_connections(self, board):
        '''
        Draw all the connections in this netlist. Saves the results of this execution
        :param board:  a threedimensional Numpy array
        '''
        path_number = settings.SIGN_PATH_START

        for connection in self.list:
            self.connections += 1

            # Get the coordinates of the two gates in this connection
            a = connection[0]
            b = connection[1]            
            coordGateA = np.argwhere(board.gatesNumbers == a + 1)
            coordGateB = np.argwhere(board.gatesNumbers == b + 1)

            # Create a new path object
            new_path = Path(coordGateA[0], coordGateB[0], path_number, "grey")

            # Add this path to the board object
            board.paths.append(new_path)

            # Calculate the route for this path
            result = new_path.calculate(settings.PATH_ALGORITHM, board)

            # Save the results of this execution
            if result == True:
                self.connections_made += 1
            else:
                self.connections_broken += 1

            # Set a new path_number for the next path
            path_number += 1

    def get_result(self, type):
        if type is "average":
            return self.connections_made / self.connections
        if type is "made":
            return self.connections_made
        if type is "broken":
            return self.connections_broken

    def print_result(self):
        print(CLR.YELLOW + "Paths drawn: " + str(self.connections_made) + " / " + str(self.connections) + CLR.DEFAULT)
        print(CLR.YELLOW + str(round(self.connections_made / self.connections * 100, 2)) + "%" + CLR.DEFAULT)
        print("")
    
    def switch_back_one(self, target):
        # Switch the target item with item before
        index = self.list.index(target)

        tmp = self.list[index - 1]
        self.list[index - 1] = self.list[index]
        self.list[index] = tmp
        return self.list


class Netlist_log:
    """
    :param fisrt_list: first list to be saved.
    Make a stack hostory of the used netlists
    """
    def __init__(self, number):
        # Make file name used.
        self.filename = "data/netlist"
        self.filename += str(number)
        self.filename += ".txt"

        # Open netlist and read with literal evaluation.
        with open(self.filename) as f:
            self.first_list = f.read()

        self.first_list = literal_eval(self.first_list)

        print("Using netlist #" + str(number))

        self.lists_log = [self.first_list]

    # Push en pop item to lists_log
    def push_list(self, netlist):
        self.lists_log.insert(0, netlist)

    def pop_list(self):
        poped_list = self.lists_log.pop(0)
        return poped_list

    def get_list(self):
        return self.lists_log[0]

    # Print compleet array of lists_log
    def print_lists_log(self):
        print(self.lists_log)

class Path:
    """
    Path from A to B
    :param coordA:     first point on the board (list of Z, Y, X coordinates)
    :param coordB:     second point on the board (list of  Z, Y, X coordinates)
    :param aLabel:     the ID of this path
    :param aColor:     the color for plotting
    """

    def __init__(self, coordA, coordB, aLabel, aColor):
        self.label = aLabel
        self.path = []
        self.a = coordA
        self.b = coordB
        self.color = aColor

    def add_coordinate(self, coord):
        '''
        Adds a new coordinate to self.path
        :param coord:       a list of [Z, Y, X]
        '''
        self.path.append(coord)

    def calculate(self, algorithm, board):
        '''
        Calculate route between two points
        :param board:       a threedimensional Numpy array
        :param algorithm:   algorithm to draw the path
        '''

        if algorithm == "DIJKSTRA":
            return self.calculate_DIJKSTRA(board)

        if algorithm == "ASTAR":
            return self.calculate_ASTAR(board)

    def calculate_ASTAR(self, board):
        '''
        Calculate route between two points with the A* algorithm
        :param board: a threedimensional Numpy array
        '''

        a_tpl = tuple(self.a)
        b_tpl = tuple(self.b)

        # Create data structures
        queue = QueuePriority()
        queue.push(a_tpl, 0)

        cost_archive = {}
        cost_archive[a_tpl] = 0
        
        path_archive = {}
        path_archive[a_tpl] = None

        found = False

        # Keep searching till queue is empty or target is found
        while not queue.empty():

            # Pop first coordinate from queue
            current = queue.pop()
            current_tpl = tuple(current)

            # Check if this is the target
            if current_tpl == b_tpl:
                found = True
                break

            # Create all neighbors of this coordinate
            for neighbor in board.get_neighbors(current):

                # Create a tuple
                neighbor = tuple(neighbor)

                # --------------- HEURISTICS ----------------

                # Check if this coordinate on the board is empty
                if board.board[neighbor[0], neighbor[1], neighbor[2]] != 0:
                    if neighbor != b_tpl:
                        continue

                # Save its distance from the start
                cost_depth = 1 - neighbor[0] * 2
                cost_neighbor = cost_archive[current_tpl] + 14 + cost_depth;

                # Sum surrounding gates
                if neighbor[0] < 2:
                    for next_neighbor in board.get_neighbors(neighbor):

                        # If next_neighbor is a gate
                        gate = board.gatesObjects[next_neighbor[0], next_neighbor[1], next_neighbor[2]]
                        if gate != None:

                            # Make the cost higher if gate has more connections
                            for i in range(gate.spaces_needed):
                                cost_neighbor += settings.ASTAR_WEIGHT

                # Check if this coordinate is new or has a lower cost than before
                if neighbor not in cost_archive \
                   or cost_neighbor < cost_archive[neighbor]:
                
                    # Calculate the cost and add it to the queue
                    cost_archive[neighbor] = cost_neighbor
                    prior = cost_neighbor + board.calculate_delta(neighbor, b_tpl)
                    queue.push(neighbor, prior)

                    # Remember where this neighbor came from
                    path_archive[neighbor] = current

                # -------------- / HEURISTICS ---------------

        # Backtracking the path        
        if found:

            # Add destination to the path route
            self.add_coordinate(self.b)

            cursor = path_archive[b_tpl]
            
            while cursor != a_tpl:
                # Put the ID in the Numpy board
                board.board[cursor[0], cursor[1], cursor[2]] = self.label

                # Remember this coord for this path
                self.add_coordinate([cursor[0], cursor[1], cursor[2]])
                
                cursor = path_archive[cursor]
            
            # Add A to the path
            self.add_coordinate(self.a)

            # Reduce the needed spaces for gate A and B
            board.gatesObjects[self.a[0], self.a[1], self.a[2]].spaces_needed -= 1
            board.gatesObjects[self.b[0], self.b[1], self.b[2]].spaces_needed -= 1

            return True
        
        else:
            return False

    def calculate_DIJKSTRA(self, board):
        '''
        Calculate route between two points with the Dijkstra algorithm
        :param board: a Numpy array
        '''

        # Initiate the dimantions of the board
        boardDimensions = board.board.shape
        boardDepth = boardDimensions[0]
        boardHeight = boardDimensions[1]
        boardWidth = boardDimensions[2]
        a_tpl = tuple(self.a)
        b_tpl = tuple(self.b)
        
        # Initiate counters
        loops = 0
        found = False

        # Initiate numpy data structures
        archive = np.zeros((boardDepth, boardHeight, boardWidth), dtype=int)

        # Add destination to the path route
        self.add_coordinate(self.b)

        queue = Queue()
        queue.push(self.a)

        # Algorithm core logic
        while not queue.empty() and found == False:

            # Track the distance
            loops += 1

            # Pick first coordinate from the queue
            current = queue.pop()
            current_tpl = tuple(current)

            # Create all neighbors of this coordinate
            for neighbor in board.get_neighbors(current):
                neighbor = tuple(neighbor)

                # Check if this is the target
                if neighbor == b_tpl:
                    found = True
                    break

                # --------------- HEURISTICS ----------------

                # Check if this coord is already in the archive
                if archive[neighbor[0], neighbor[1], neighbor[2]] != 0:
                    continue

                # Check if there are no obstacles on this coord
                if board.board[neighbor[0], neighbor[1], neighbor[2]] > 0:
                    continue

                # Check surrounding tiles for gates that need space
                for neighbor_next in board.get_neighbors(neighbor):
                    neighbor_next = tuple(neighbor_next)

                    # Check if this gate needs space around it
                    if board.gatesObjects[neighbor_next[0], neighbor_next[1], neighbor_next[2]] != None:

                        # Don't look at the own gates
                        if not (neighbor_next == a_tpl) or (neighbor_next == b_tpl):

                            # Get info from this gate
                            gate = board.gatesObjects[neighbor_next[0], neighbor_next[1], neighbor_next[2]]

                            # See if the path may pass
                            if gate.get_free_spaces(board, neighbor_next) == 0:
                                continue

                # -------------- / HEURISTICS ---------------

                # Add the coord to the queue
                queue.push(list(neighbor))

                # Save the iteration counter to this coordinate in the archive
                archive[neighbor[0], neighbor[1], neighbor[2]] = loops

        # Backtracking the shortest route
        if found:
            cursor = list(self.b)

            # Loop back the all the made steps
            for i in range(loops - 1, 0, -1):

                # Loop through all the neighbors of this tile
                for neighbor in board.get_neighbors(cursor):

                    neighbor = tuple(neighbor)

                    # Check if this cell is on the i'th position in the shortest path
                    if archive[neighbor[0], neighbor[1], neighbor[2]] == i:

                        # Put the ID in the Numpy board
                        board.board[neighbor[0], neighbor[1], neighbor[2]] = self.label

                        # Remember this coord for this path
                        self.add_coordinate([neighbor[0], neighbor[1], neighbor[2]])

                        # Move the cursor
                        cursor = list(neighbor)
                        break

            # Add the starting point to the end of the path-list
            self.add_coordinate(self.a)

            # Add 1 to the made connections for gate A and B
            board.gatesObjects[self.a[0], self.a[1], self.a[2]].spaces_needed -= 1
            board.gatesObjects[self.b[0], self.b[1], self.b[2]].spaces_needed -= 1

            return True

        else:
            print("Path " + str(self.label) + " ERROR. Could not be calculated.")

            return False

    def get_coords(self, axes):
        coords = []

        for coord in self.path:
            if axes == 'z':
                coords.append(coord[0])
            if axes == 'y':
                coords.append(coord[1])
            if axes == 'x':
                coords.append(coord[2])

        return coords

class Queue:
    '''
    Dequeue, append and count elements in a simple queue
    :param: none
    '''

    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self):
        return len(self.elements) == 0
    
    def pop(self):
        return self.elements.popleft()
    
    def push(self, x):
        self.elements.append(x)

class QueuePriority:
    '''
    Dequeue, append and count elements in a priority queue
    :param: none
    '''

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def pop(self):
        return heapq.heappop(self.elements)[1]

    def push(self, coord, prior):
        heapq.heappush(self.elements, (prior, coord))