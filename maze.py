import random
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# number of rows and columns
R = 15
C = 15

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

# bonus_mode: when True, generation has a 1-in-20 chance to eat an extra wall (creates cycles).
# Toggled with the B key before or during generation.
bonus_mode = False

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

def reset_maze():
    global northWall, eastWall
    global current_r, current_c, stack, generation_complete
    global start_cell, end_cell

    northWall = [[1 for _ in range(C + 1)] for _ in range(R + 1)]
    eastWall = [[1 for _ in range(C + 1)] for _ in range(R + 1)]

    current_r = 1
    current_c = 1
    stack = []
    generation_complete = False

    start_cell = None
    end_cell = None

    reset_solver()

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

        if bonus_mode and random.random() < 0.05:
            extra_walls = []

            if current_r < R and northWall[current_r][current_c] == 1: extra_walls.append(("N", current_r, current_c))
            if current_r > 1 and northWall[current_r - 1][current_c] == 1: extra_walls.append(("S", current_r - 1, current_c))
            if current_c < C and eastWall[current_r][current_c] == 1: extra_walls.append(("E", current_r, current_c))
            if current_c > 1 and eastWall[current_r][current_c - 1] == 1: extra_walls.append(("W", current_r, current_c - 1))

            if extra_walls:
                ew_dir, ew_r, ew_c = random.choice(extra_walls)

                if ew_dir == "N": northWall[ew_r][ew_c] = 0
                elif ew_dir == "S": northWall[ew_r - 1][ew_c] = 0
                elif ew_dir == "E": eastWall[ew_r][ew_c] = 0
                elif ew_dir == "W": eastWall[ew_r][ew_c - 1] = 0

        current_r, current_c = next_r, next_c

    elif len(stack) > 0:
        current_r, current_c = stack.pop()

    else:
        if not generation_complete:
            generation_complete = True

            start_r = random.randint(1, R)
            end_r = random.randint(1, R)

            start_cell = (start_r, 1)
            end_cell = (end_r, C)

            eastWall[start_r][0] = 0
            eastWall[end_r][C] = 0

            solver_current = start_cell
            solver_state[start_r][1] = 1

#dfs backtracking solver
def solve_step():
    global solver_current, solver_stack, solver_complete

    if not solver_started or solver_complete:
        return

    r, c = solver_current

    if (r, c) == end_cell:
        solver_complete = True
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


#drawing functions
def draw_circle_gl(cx, cy, radius, r, g, b, segments=20):
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        glVertex2f(cx + radius * math.cos(angle),
                   cy + radius * math.sin(angle))
    glEnd()

def draw_maze():
    glLineWidth(2.5)
    glColor3f(0.1, 0.1, 0.1)
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
    glLineWidth(1.0)

def draw_mouse(r, c, color=(0.1, 0.85, 0.3)):
    cx = c - 0.5
    cy = r - 0.5
    draw_circle_gl(cx, cy, 0.38, color[0], color[1], color[2])

def draw_stack():
    for sr, sc in stack:
        cx = sc - 0.5
        cy = sr - 0.5
        draw_circle_gl(cx, cy, 0.30, 0.55, 0.65, 0.95, segments=16)

def draw_solver():
    for r in range(1, R + 1):
        for c in range(1, C + 1):
            cx = c - 0.5
            cy = r - 0.5
            if solver_state[r][c] == 1:
                draw_circle_gl(cx, cy, 0.32, 0.95, 0.18, 0.18, segments=18)
            elif solver_state[r][c] == 2:
                draw_circle_gl(cx, cy, 0.32, 0.25, 0.45, 0.95, segments=18)


def make_hud_texture(font_large, font_small, window_w, window_h):
    # Render the key guide and status onto a transparent Pygame surface,
    # then upload it as an OpenGL texture to draw on top of the maze.
    surf = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))

    # top status bar
    top_bar = pygame.Surface((window_w, 42), pygame.SRCALPHA)
    top_bar.fill((255, 255, 255, 215))
    surf.blit(top_bar, (0, 0))

    # bottom key guide panel
    guide_h = 54
    bot_bar = pygame.Surface((window_w, guide_h), pygame.SRCALPHA)
    bot_bar.fill((255, 255, 255, 210))
    surf.blit(bot_bar, (0, window_h - guide_h))

    # --- top bar: status message ---
    if not generation_complete:
        if bonus_mode:
            status = "Generating maze...   [extra walls / cycles enabled]"
            scol = (150, 70, 0)
        else:
            status = "Generating maze..."
            scol = (30, 30, 30)
    elif solver_complete:
        status = "SOLVED!"
        scol = (10, 130, 10)
    elif solver_started:
        status = "Solving..."
        scol = (160, 40, 10)
    else:
        status = "Ready — press S to start solving"
        scol = (20, 20, 140)

    s_surf = font_large.render(status, True, scol)
    surf.blit(s_surf, s_surf.get_rect(center=(window_w // 2, 21)))

    # --- bottom panel: key guide ---
    y = window_h - guide_h + 9

    if not generation_complete:
        line1 = "R: New maze"
        if bonus_mode:
            line2 = "B: Bonus cycles  [ ON ]  — press to turn OFF"
            c2 = (150, 70, 0)
        else:
            line2 = "B: Bonus cycles  [ OFF ]  — press to turn ON"
            c2 = (90, 90, 90)
    elif solver_complete:
        line1 = "R: New maze                    C: Solve again"
        line2 = ""
        c2 = (90, 90, 90)
    elif solver_started:
        line1 = "R: New maze                    C: Clear path"
        line2 = ""
        c2 = (90, 90, 90)
    else:
        line1 = "S: Start solving     R: New maze     C: Clear"
        if bonus_mode:
            line2 = "R: Bonus cycles  [ ONN ]  — press R and B to turn OFF  (regenerates with no cycles)"
            c2 = (150, 70, 0)
        else:
            line2 = "R: Bonus cycles  [ OFF ]  — press R and B to turn ON  (regenerates with cycles)"
            c2 = (90, 90, 90)

    l1 = font_small.render(line1, True, (40, 40, 40))
    surf.blit(l1, l1.get_rect(center=(window_w // 2, y + 8)))

    if line2:
        l2 = font_small.render(line2, True, c2)
        surf.blit(l2, l2.get_rect(center=(window_w // 2, y + 27)))

    # upload to an OpenGL texture
    tex_data = pygame.image.tostring(surf, "RGBA", True)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 window_w, window_h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


def draw_hud_texture(tex_id, window_w, window_h):
    # Switch to a flat 2D orthographic projection to draw the HUD quad fullscreen,
    # then restore the original 3D perspective projection.
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_w, 0, window_h, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1, 1, 1, 1)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(window_w, 0)
    glTexCoord2f(1, 1); glVertex2f(window_w, window_h)
    glTexCoord2f(0, 1); glVertex2f(0, window_h)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDeleteTextures([tex_id])

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


def main():
    global solver_started, bonus_mode

    pygame.init()
    window_w, window_h = 600, 640
    window_size = (window_w, window_h)

    pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Maze Generator and Solver")

    font_large = pygame.font.SysFont("Consolas", 14, bold=True)
    font_small = pygame.font.SysFont("Consolas", 13, bold=False)

    gluPerspective(45, (window_size[0] / window_size[1]), 0.1, 150.0)
    glTranslatef(0.0, 0.0, -10)

    glClearColor(1.0, 1.0, 1.0, 1.0)

    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    max_dim = max(C, R)
    scale_factor = 5.2 / max_dim

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
                        solver_started = True

                elif event.key == pygame.K_c:
                    if generation_complete:
                        reset_solver()

                elif event.key == pygame.K_b:
                    if not generation_complete:
                        bonus_mode = not bonus_mode

        if not generation_complete:
            generate_step()
            # generate_step()

        elif solver_started and not solver_complete:
            solve_step()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glScalef(scale_factor, scale_factor, 1.0)
        glTranslatef(-C / 2.0, -R / 2.0 - 0.3, 0.0)

        if not generation_complete:
            draw_stack()
            draw_mouse(current_r, current_c, color=(0.1, 0.85, 0.3))
        else:
            draw_solver()

            if not solver_complete and solver_current:
                draw_mouse(solver_current[0], solver_current[1], color=(1.0, 0.85, 0.0))

            elif solver_complete:
                draw_mouse(end_cell[0], end_cell[1], color=(0.1, 0.85, 0.3))

        draw_maze()
        glPopMatrix()

        tex_id = make_hud_texture(font_large, font_small, window_w, window_h)
        draw_hud_texture(tex_id, window_w, window_h)

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()