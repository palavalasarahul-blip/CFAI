import random
from collections import deque

class CleaningRobot:
    def __init__(self, grid, start):
        self.grid = grid
        self.position = start
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.cleaned = 0
        self.steps = 0

    def display_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) == self.position:
                    print("R", end=" ")
                else:
                    print(self.grid[i][j], end=" ")
            print()
        print()

    def find_dirty_cells(self):
        dirty = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == "D":
                    dirty.append((i, j))
        return dirty

    def bfs_path(self, target):
        queue = deque()
        queue.append((self.position, []))
        visited = set()
        visited.add(self.position)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            (x, y), path = queue.popleft()

            if (x, y) == target:
                return path

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if self.grid[nx][ny] != "X" and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))

        return None

    def nearest_dirty_cell(self):
        dirty_cells = self.find_dirty_cells()
        best_cell = None
        best_path = None

        for cell in dirty_cells:
            path = self.bfs_path(cell)
            if path is not None:
                if best_path is None or len(path) < len(best_path):
                    best_cell = cell
                    best_path = path

        return best_cell, best_path

    def clean_cell(self):
        x, y = self.position
        if self.grid[x][y] == "D":
            self.grid[x][y] = "."
            self.cleaned += 1
            print("Cleaned dirt at:", self.position)

    def move_and_clean(self):
        print("Initial Room Layout:")
        self.display_grid()

        while self.find_dirty_cells():
            target, path = self.nearest_dirty_cell()

            if target is None:
                print("Some dirty cells cannot be reached due to obstacles.")
                break

            print("Moving to dirty cell:", target)

            for step in path:
                self.position = step
                self.steps += 1
                self.display_grid()

            self.clean_cell()
            self.display_grid()

        print("Cleaning Completed")
        print("Total cleaned cells:", self.cleaned)
        print("Total steps taken:", self.steps)


def create_room(rows, cols, dirt_count, obstacle_count):
    grid = [["." for _ in range(cols)] for _ in range(rows)]

    for _ in range(obstacle_count):
        x = random.randint(0, rows - 1)
        y = random.randint(0, cols - 1)
        grid[x][y] = "X"

    for _ in range(dirt_count):
        x = random.randint(0, rows - 1)
        y = random.randint(0, cols - 1)
        if grid[x][y] == ".":
            grid[x][y] = "D"

    return grid


rows = 5
cols = 5
dirt_count = 6
obstacle_count = 5

room = create_room(rows, cols, dirt_count, obstacle_count)
start_position = (0, 0)

room[0][0] = "."

robot = CleaningRobot(room, start_position)
robot.move_and_clean()