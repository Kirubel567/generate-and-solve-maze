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

def generate_step():
    global current_r, current_c, stack, generation_complete 
    global start_cell, end_cell, solver_current 
    
    if generation_complete: 
        return 
        
    unvisited_neighbors = [] 
    
    def is_unvisited(r, c):
        return (northWall[r][c] == 1 and 
                northWall[r-1][c] == 1 and 
                eastWall[r][c] == 1 and 
                eastWall[r][c-1] == 1) 
    

    if current_r < R and is_unvisited(current_r + 1, current_c):
        unvisited_neighbors.append((current_r + 1, current_c, "N")) 
    
    if current_r > 1 and is_unvisited(current_r - 1, current_c): 
        unvisited_neighbors.append((current_r - 1, current_c, "S")) 
    
    if current_c < C and is_unvisited(current_r, current_c + 1): 
        unvisited_neighbors.append((current_r, current_c + 1, "E"))
    
    if current_c > 1 and is_unvisited(current_r, current_c - 1): 
        unvisited_neighbors.append((current_r, current_c - 1, "W")) 
            
    if len(unvisited_neighbors) > 0: 
        stack.append((current_r, current_c)) 
        next_r, next_c, direction = random.choice(unvisited_neighbors) 
        
        if direction == "N": northWall[current_r][current_c] = 0 
        elif direction == "S": northWall[current_r - 1][current_c] = 0 
        elif direction == "E": eastWall[current_r][current_c] = 0 
        elif direction == "W": eastWall[current_r][current_c - 1] = 0 

        if random.random() < 0.05:
            extra_walls = []

            if current_r < R and northWall[current_r][current_c] == 1: extra_walls.append(("N", current_r, current_c))
            if current_r > 1 and northWall[current_r - 1][current_c] == 1: extra_walls.append(("S", current_r - 1, current_c))
            if current_c < C and eastWall[current_r][current_c] == 1: extra_walls.append(("E", current_r, current_c))
            if current_c > 1 and eastWall[current_r][current_c - 1] == 1: extra_walls.append(("W", current_r, current_c - 1))

            if extra_walls:
                ew_dir, ew_r, ew_c = random.choice(extra_walls)

                if ew_dir == "N": northWall[ew_r][ew_c] = 0
                elif ew_dir == "S": northWall[ew_r][ew_c] = 0
                elif ew_dir == "E": eastWall[ew_r][ew_c] = 0
                elif ew_dir == "W": eastWall[ew_r][ew_c] = 0
                
        current_r, current_c = next_r, next_c
        
    elif len(stack) > 0:
        current_r, current_c = stack.pop() 
        
    else: 
        if not generation_complete: 
            generation_complete = True 
            print("Maze Generation Complete!") 
           
            start_r = random.randint(1, R)
            end_r = random.randint(1, R)
            
            start_cell = (start_r, 1) 
            end_cell = (end_r, C) 
            
            
            eastWall[start_r][0] = 0 
            eastWall[end_r][C] = 0 
            
            solver_current = start_cell 
            solver_state[start_r][1] = 1 
            print(f"Start at {start_cell}, End at {end_cell}") 
            print(">>> Press 'S' to start solving! <<<") 
            print(">>> Press 'C' to clear the solver path. <<<") 
            print(">>> Press 'R' to generate a completely new maze. <<<") 


