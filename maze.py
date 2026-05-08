import random 
import math 
import pygame 
from pygame.locals import * 
from OpenGL.GL import * 
from OpenGL.GLU import * 

# number of rows and columns
R = 20 
C = 20 

# Initialize the northWall array, It is of size (R+1) x (C+1).
# Index 0 is the phantom row, making up the bottom edge.
northWall = [[1 for _ in range(C + 1)] for _ in range(R + 1)]

# Initialize the eastWall array. It is of size (R+1) x (C+1).
# Index 0 is the phantom column, making up the left edge.
eastWall = [[1 for _ in range(C + 1)] for _ in range(R + 1)]

current_r = 1 
current_c = 1 
stack = [] 
generation_complete = False 


start_cell = None 
end_cell = None 
solver_stack = [] 
solver_current = None 

# solver_state: a 2D array tracking each cell's status in the solver:
solver_state = [[0 for _ in range(C + 1)] for _ in range(R + 1)]
solver_complete = False 
solver_started = False 


def reset_solver():
    global solver_stack, solver_current, solver_state, solver_complete, solver_started

    solver_state = [[0 for _ in range(C + 1)] for _ in range(R + 1)]
    solver_stack = []
    solver_complete = False 
    solver_started = False 
    
    if start_cell: 
        solver_current = start_cell 
        solver_state[start_cell[0]][start_cell[1]] = 1 
        print("Solver cleared! Press 'S' to start solving.") 

def reset_maze():
    global northWall, eastWall 
    global current_r, current_c, stack, generation_complete 
    global start_cell, end_cell 
    
    #re-initialize all the walls to one
    northWall = [[1 for _ in range(C + 1)] for _ in range(R + 1)]
    eastWall = [[1 for _ in range(C + 1)] for _ in range(R + 1)]
    
    current_r = 1 
    current_c = 1 
    stack = [] #clear the generation stack
    generation_complete = False 
    
    start_cell = None 
    end_cell = None 
    
    reset_solver() # Call reset_solver to clear all solver variables too
    print("\nMaze completely reset! Generating a new maze") 

    
