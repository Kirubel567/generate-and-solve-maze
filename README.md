# Maze Generator and Solver
 
An interactive maze generator and solver built with Python, Pygame, and OpenGL. Watch a maze being carved out in real time, then solve it with a visual backtracking algorithm.
 
---
 
## How It Works
 
### Data Structure
 
The maze is represented using two 2D arrays:
 
```python
northWall[R][C]  # 1 = top wall intact, 0 = passage going up
eastWall[R][C]   # 1 = right wall intact, 0 = passage going right
```
 
Each cell only needs to track two of its four walls. The other two are covered by its neighbors:
- A cell's **bottom wall** is `northWall[r-1][c]` (the top wall of the row below)
- A cell's **left wall** is `eastWall[r][c-1]` (the right wall of the column to the left)
Both arrays are sized `(R+1) x (C+1)` to accommodate a phantom row (index 0) and phantom column (index 0). The phantom row's north walls form the bottom border of the maze; the phantom column's east walls form the left border.
 
---
 
### Maze Generation — Stack-Based DFS Mouse
 
The maze is generated using a **Depth-First Search (DFS)** algorithm driven by an invisible "mouse":
 
1. All walls start intact — the maze begins as a plain grid.
2. The mouse starts at cell `(1, 1)`.
3. At each step, the mouse looks at its four neighbors (North, South, East, West).
4. A neighbor is considered **unvisited** if all four of its walls are still intact.
5. If unvisited neighbors exist:
   - The current position is pushed onto a **stack**.
   - One unvisited neighbor is chosen **randomly**.
   - The wall between them is destroyed (set to `0`).
   - The mouse moves to the new cell.
6. If no unvisited neighbors exist (dead end), the mouse **pops** the stack and backtracks.
7. When the stack is empty, every cell has been visited and the maze is complete.
Because every cell is visited exactly once and connected by one unique path, the result is always a **perfect maze** — a spanning tree where every cell is reachable from every other cell.
 
#### Bonus: Cycle Creation (Addendum)
With a 1-in-20 chance (5%) on each step, the mouse eats one **extra random wall**. This creates loops/cycles in the maze graph, which defeats the classic "shoulder-to-the-wall" navigation method described in the assignment addendum.
 
---
 
### Maze Solving — Backtracking Algorithm
 
Once generation is complete, a solver mouse is placed at the **start cell** (left edge) and must reach the **end cell** (right edge):
 
1. At each step, the solver checks all four directions for open passages leading to unvisited cells.
2. If a valid move exists, the solver pushes its position onto a **solver stack**, moves forward, and marks the cell **red**.
3. If the solver hits a dead end (no valid moves), it marks the current cell **blue** and pops the stack to backtrack.
4. The solver succeeds when it reaches `end_cell`, and the final path is shown in red.
---
 
## Controls
 
| Key | Action |
|-----|--------|
| `S` | Start the solver (after generation completes) |
| `C` | Clear the solver path and reset to start |
| `R` | Generate a completely new maze |
 
---
 
## Configuration
 
Edit the top of `maze.py` to change maze size:
 
```python
R = 20  # Number of rows
C = 20  # Number of columns
```
 
---
 
## Requirements
 
```
pygame
PyOpenGL
PyOpenGL_accelerate  # optional, improves performance
```
 
Install with:
 
```bash
pip install pygame PyOpenGL PyOpenGL_accelerate
```
 
---
 
## Running
 
```bash
python maze.py
```
 
---
 
## Visual Guide
 
| Color | Meaning |
|-------|---------|
| White lines | Maze walls |
| Green (large) | Generation mouse current position |
| Dim blue (large) | Generation stack trail |
| Yellow (small dot) | Solver mouse current position |
| Red (small dot) | Active solution path |
| Blue (small dot) | Confirmed dead end |
| Green (small dot) | Exit cell when solved |
 
---
 
## Project Structure
 
```
maze-generator/
├── maze.py       # Main source file — generation, solving, rendering
└── README.md     # This file
```