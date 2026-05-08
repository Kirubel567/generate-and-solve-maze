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

#dfs backtracking solver
def solve_step():
    global solver_current, solver_stack, solver_complete
    
    if not solver_started or solver_complete:
        return
        
    r, c = solver_current
    
    if (r, c) == end_cell:
        solver_complete = True
        print("Maze Solved! Press 'R' to generate a new maze, or 'C' to clear and solve this one again.")
        return
        
    valid_moves = []
    
    if r < R and northWall[r][c] == 0 and solver_state[r+1][c] == 0:
        valid_moves.append((r+1, c))

    if r > 1 and northWall[r-1][c] == 0 and solver_state[r-1][c] == 0:
        valid_moves.append((r-1, c))

    if c < C and eastWall[r][c] == 0 and solver_state[r][c+1] == 0:
        valid_moves.append((r, c+1))

    if c > 1 and eastWall[r][c-1] == 0 and solver_state[r][c-1] == 0:
        valid_moves.append((r, c-1))
        
    if valid_moves:
        solver_stack.append(solver_current)
        next_cell = random.choice(valid_moves)
        solver_current = next_cell
        solver_state[next_cell[0]][next_cell[1]] = 1

    elif solver_stack:
        solver_state[r][c] = 2
        solver_current = solver_stack.pop()

    else:
        solver_complete = True
        print("No solution found!")

#drawing functions
def draw_maze():
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    
    for r in range(R + 1):
        for c in range(1, C + 1):
            if northWall[r][c] == 1:
                glVertex2f(c - 1, r)
                glVertex2f(c, r)
                
    for r in range(1, R + 1):
        for c in range(C + 1):
            if eastWall[r][c] == 1:
                glVertex2f(c, r - 1)
                glVertex2f(c, r)
    glEnd()

def draw_mouse(r, c, color=(0.0, 1.0, 0.0), size="full"):
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_QUADS)
    
    if size == "full":
        glVertex2f(c - 1, r - 1)
        glVertex2f(c, r - 1)
        glVertex2f(c, r)
        glVertex2f(c - 1, r)
    else:
        glVertex2f(c - 0.7, r - 0.7)
        glVertex2f(c - 0.3, r - 0.7)
        glVertex2f(c - 0.3, r - 0.3)
        glVertex2f(c - 0.7, r - 0.3)
    glEnd()

def draw_stack():
    for sr, sc in stack:
        draw_mouse(sr, sc, color=(0.2, 0.2, 0.6))

def draw_solver():
    glBegin(GL_QUADS)

    for r in range(1, R + 1):
        for c in range(1, C + 1):

            if solver_state[r][c] == 1:
                glColor3f(1.0, 0.0, 0.0)
                glVertex2f(c - 0.6, r - 0.6)
                glVertex2f(c - 0.4, r - 0.6)
                glVertex2f(c - 0.4, r - 0.4)
                glVertex2f(c - 0.6, r - 0.4)

            elif solver_state[r][c] == 2:
                glColor3f(0.0, 0.0, 1.0)
                glVertex2f(c - 0.6, r - 0.6)
                glVertex2f(c - 0.4, r - 0.6)
                glVertex2f(c - 0.4, r - 0.4)
                glVertex2f(c - 0.6, r - 0.4)

    glEnd()

def main():
    pygame.init()
    window_size = (500, 600)

    pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Maze Generator and Solver")

    gluPerspective(45, (window_size[0] / window_size[1]), 0.1, 150.0)
    glTranslatef(0.0, 0.0, -10)

    max_dim = max(C, R)
    scale_factor = 6.0 / max_dim

    print("Generating Initial Maze...")

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    reset_maze()

                elif event.key == pygame.K_s:

                    if generation_complete and not solver_complete:
                        print("Solver Started!")
                        global solver_started
                        solver_started = True

                elif event.key == pygame.K_c:

                    if generation_complete:
                        reset_solver()

        if not generation_complete:
            generate_step()
            generate_step()

        elif solver_started and not solver_complete:
            solve_step()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glScalef(scale_factor, scale_factor, 1.0)
        glTranslatef(-C / 2.0, -R / 2.0, 0.0)

        if not generation_complete:
            draw_stack()
            draw_mouse(current_r, current_c, color=(0.0, 1.0, 0.0))

        else:
            draw_solver()

            if not solver_complete and solver_current:
                draw_mouse(solver_current[0], solver_current[1], color=(1.0, 1.0, 0.0), size="small")

            elif solver_complete:
                draw_mouse(end_cell[0], end_cell[1], color=(0.0, 1.0, 0.0), size="small")

        draw_maze()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()