import random
import pyperclip
from collections import deque
from buildlogic import BuildLogicEngine, BEAM_MAP, MATERIAL_MAP

CONFIG = {
    "SEED": 314159256,
    "WIDTH": 35,
    "LENGTH": 35,
    "HALL_WIDTH": 7,
    "WALL_HEIGHT": 7,
    "BASE_Y": 1,
    "CEILING_ENABLED": True,
    "WALL_MAT": "marble",
    "WALL_COLOR": (235, 235, 240),
    "FLOOR_MAT": "concrete",
    "FLOOR_COLOR": (180, 185, 180),
    "CEILING_MAT": "glass",
    "CEILING_COLOR": (190, 225, 245),
}

random.seed(CONFIG["SEED"])

class Colors:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    BG_DARK = "\033[40m"

def generate_dfs_maze(w, l):
    grid = [[1 for _ in range(l)] for _ in range(w)]
    stack = [(1, 1)]
    grid[1][1] = 0

    while stack:
        cx, cz = stack[-1]
        neighbors = []
        for dx, dz in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, nz = cx + dx, cz + dz
            if 0 < nx < w - 1 and 0 < nz < l - 1 and grid[nx][nz] == 1:
                neighbors.append((nx, nz))

        if neighbors:
            nx, nz = random.choice(neighbors)
            grid[(cx + nx) // 2][(cz + nz) // 2] = 0
            grid[nx][nz] = 0
            stack.append((nx, nz))
        else:
            stack.pop()

    return grid

def farthest_cell(grid, sx, sz):
    w, l = len(grid), len(grid[0])
    q = deque([(sx, sz, 0)])
    visited = [[False] * l for _ in range(w)]
    visited[sx][sz] = True
    far = (sx, sz)
    max_d = 0

    while q:
        x, z, d = q.popleft()
        if d > max_d:
            max_d, far = d, (x, z)
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, nz = x + dx, z + dz
            if 0 <= nx < w and 0 <= nz < l and not visited[nx][nz] and grid[nx][nz] == 0:
                visited[nx][nz] = True
                q.append((nx, nz, d + 1))

    return far

def find_path(grid, sx, sz, gx, gz):
    w, l = len(grid), len(grid[0])
    q = deque([(sx, sz, [(sx, sz)])])
    visited = [[False] * l for _ in range(w)]
    visited[sx][sz] = True

    while q:
        x, z, path = q.popleft()
        if (x, z) == (gx, gz):
            return path
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, nz = x + dx, z + dz
            if 0 <= nx < w and 0 <= nz < l and not visited[nx][nz] and grid[nx][nz] == 0:
                visited[nx][nz] = True
                q.append((nx, nz, path + [(nx, nz)]))

    return None

def center_farthest(grid):
    w, l = len(grid), len(grid[0])
    corners = [(1, 1), (1, l - 2), (w - 2, 1), (w - 2, l - 2)]
    best = None
    best_dist = -1

    for x in range(1, w - 1):
        for z in range(1, l - 1):
            if grid[x][z] == 0:
                d = min(abs(x - cx) + abs(z - cz) for cx, cz in corners)
                if d > best_dist:
                    best_dist, best = d, (x, z)

    return best

def cell_center(idx, hw):
    if hw % 2 == 1:
        return [idx * hw + hw // 2]
    base = idx * hw
    return [base + hw // 2 - 1, base + hw // 2]

def beam_token(length):
    for l, t in BEAM_MAP:
        if l == length:
            return t
    return "G"

def print_maze(grid, path, spawn, goal):
    w, l = len(grid), len(grid[0])
    bg = Colors.BG_DARK
    wall = Colors.WHITE + "██"
    path_ch = Colors.CYAN + "██"
    spawn_ch = Colors.GREEN + Colors.BOLD + "S" + Colors.RESET + bg
    goal_ch = Colors.YELLOW + Colors.BOLD + "G" + Colors.RESET + bg
    highlight = Colors.MAGENTA + Colors.BOLD + "██" + Colors.RESET + bg

    render = [['#' if c == 1 else ' ' for c in row] for row in grid]

    if spawn:
        sx, sz = spawn
        if 0 <= sx < w and 0 <= sz < l:
            render[sx][sz] = 'S'
    if goal:
        gx, gz = goal
        if 0 <= gx < w and 0 <= gz < l:
            render[gx][gz] = 'G'

    for px, pz in path or []:
        if render[px][pz] not in ('S', 'G'):
            render[px][pz] = '*'

    print("\n" + bg + "=" * (l * 2 + 2) + Colors.RESET)
    for row in render:
        line = bg
        for cell in row:
            if cell == '#':
                line += wall
            elif cell == 'S':
                line += spawn_ch
            elif cell == 'G':
                line += goal_ch
            elif cell == '*':
                line += highlight
            else:
                line += path_ch
        line += Colors.RESET
        print(line)

    print(bg + "=" * (l * 2 + 2) + Colors.RESET)
def build_maze(builder):
    cfg = CONFIG
    hw = cfg["HALL_WIDTH"]
    w = (cfg["WIDTH"] - 1) * hw + 1
    l = (cfg["LENGTH"] - 1) * hw + 1

    raw = generate_dfs_maze(cfg["WIDTH"], cfg["LENGTH"])
    scaled = [[1] * l for _ in range(w)]

    for bx in range(cfg["WIDTH"]):
        for bz in range(cfg["LENGTH"]):
            if raw[bx][bz] == 0:
                mx, mz = bx * hw, bz * hw
                for dx in range(hw):
                    for dz in range(hw):
                        if mx + dx < w and mz + dz < l:
                            scaled[mx + dx][mz + dz] = 0

    if hw > 2:
        for x in range(1, w - 1):
            for z in range(1, l - 1):
                if scaled[x][z] == 1 and all(scaled[x + dx][z + dz] in (1, 2)
                       for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    scaled[x][z] = 2

    fr, fg, fb = cfg["FLOOR_COLOR"]
    for x in range(w):
        z = 0
        while z < l:
            if scaled[x][z] == 2:
                z += 1
                continue
            run = 1
            while z + run < l and run < 8 and scaled[x][z + run] != 2:
                run += 1
            builder.add_block(x, cfg["BASE_Y"], z, "A", fr, fg, fb, cfg["FLOOR_MAT"], beam_token(run))
            z += run

    wr, wg, wb = cfg["WALL_COLOR"]
    for h in range(cfg["WALL_HEIGHT"]):
        y = cfg["BASE_Y"] + 1 + h
        covered = [[False] * l for _ in range(w)]

        for x in range(w):
            for z in range(l):
                if scaled[x][z] != 1 or covered[x][z]:
                    continue

                zr = 1
                while z + zr < l and zr < 8 and scaled[x][z + zr] == 1 and not covered[x][z + zr]:
                    zr += 1

                xr = 1
                while x + xr < w and xr < 8 and scaled[x + xr][z] == 1 and not covered[x + xr][z]:
                    xr += 1

                if xr > zr:
                    for i in range(xr):
                        covered[x + i][z] = True
                    builder.add_block(x, y, z, "E", wr, wg, wb, cfg["WALL_MAT"], beam_token(xr))
                else:
                    for i in range(zr):
                        covered[x][z + i] = True
                    builder.add_block(x, y, z, "A", wr, wg, wb, cfg["WALL_MAT"], beam_token(zr))

    if cfg["CEILING_ENABLED"]:
        cr, cg, cb = cfg["CEILING_COLOR"]
        cy = cfg["BASE_Y"] + 1 + cfg["WALL_HEIGHT"]

        for x in range(w):
            z = 0
            while z < l:
                if scaled[x][z] == 2:
                    z += 1
                    continue
                run = 1
                while z + run < l and run < 8 and scaled[x][z + run] != 2:
                    run += 1
                builder.add_block(x, cy, z, "A", cr, cg, cb, cfg["CEILING_MAT"], beam_token(run))
                z += run

    spawn_cell = center_farthest(raw)
    goal_cell = farthest_cell(raw, *spawn_cell)

    sx_vals = cell_center(spawn_cell[0], hw)
    sz_vals = cell_center(spawn_cell[1], hw)
    gx_vals = cell_center(goal_cell[0], hw)
    gz_vals = cell_center(goal_cell[1], hw)

    sy = cfg["BASE_Y"] + 1

    for sx in sx_vals:
        for sz in sz_vals:
            builder.add_block(sx, sy, sz, "A", 248, 248, 248, "plastic", "#s")

    for gx in gx_vals:
        for gz in gz_vals:
            builder.add_block(gx, sy, gz, "A", 255, 215, 0, "metal", "%g")

    path = find_path(raw, *spawn_cell, *goal_cell)
    print_maze(raw, path, spawn_cell, goal_cell)

if __name__ == "__main__":
    builder = BuildLogicEngine()
    build_maze(builder)

    try:
        pyperclip.copy(builder.export_blueprint())
        print("Maze copied to clipboard.")
    except Exception as e:
        print(f"Clipboard copy failed: {e}")