import random
from collections import deque


class MazeGenerator:
    def __init__(self, config: dict[str, str | int | bool | tuple[int, int]]):
        width = config["WIDTH"]
        height = config["HEIGHT"]
        entry = config["ENTRY"]
        exit = config["EXIT"]
        output_file = config["OUTPUT_FILE"]
        perfect = config["PERFECT"]
        seed = config["SEED"]

        assert isinstance(width, int)
        assert isinstance(height, int)
        assert isinstance(entry, tuple)
        assert isinstance(exit, tuple)
        assert isinstance(output_file, str)
        assert isinstance(perfect, bool)
        assert isinstance(seed, int)

        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.output_file: str = output_file
        self.perfect: bool = perfect
        self.seed: int = seed
        self.grid: list[list[int]] = [
                [15] * self.width for i in range(self.height)
            ]

    def remove_wall(self, current: tuple[int, int], neighbor: tuple[
            str, int, int]) -> None:
        cx, cy = current
        direction, nx, ny = neighbor
        N: int = 1
        E: int = 2
        S: int = 4
        W: int = 8
        if direction == "N":
            self.grid[ny][nx] &= ~S
            self.grid[cy][cx] &= ~N
        elif direction == "S":
            self.grid[ny][nx] &= ~N
            self.grid[cy][cx] &= ~S
        if direction == "E":
            self.grid[ny][nx] &= ~W
            self.grid[cy][cx] &= ~E
        elif direction == "W":
            self.grid[ny][nx] &= ~E
            self.grid[cy][cx] &= ~W

    def within_bounds(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return True

    def find_neighbors(self, visited: list[list[bool]], point: tuple[
            int, int]) -> list[tuple[str, int, int]]:
        neighbors: list[tuple[str, int, int]] = []
        x, y = point
        if self.within_bounds(x, y - 1) and not visited[y - 1][x]:
            neighbors.append(("N", x, y - 1))
        if self.within_bounds(x, y + 1) and not visited[y + 1][x]:
            neighbors.append(("S", x, y + 1))
        if self.within_bounds(x - 1, y) and not visited[y][x - 1]:
            neighbors.append(("W", x - 1, y))
        if self.within_bounds(x + 1, y) and not visited[y][x + 1]:
            neighbors.append(("E", x + 1, y))
        return neighbors

    def get_42_cells(self) -> set[tuple[int, int]]:
        pattern = [
            "X X XXX",
            "X X   X",
            "XXX XXX",
            "  X X  ",
            "  X XXX",
        ]

        pattern_height = len(pattern)
        pattern_width = len(pattern[0])

        if self.width < pattern_width or self.height < pattern_height:
            print("Error: maze is too small to display 42 pattern")
            return set()

        start_y = (self.height - pattern_height) // 2
        start_x = (self.width - pattern_width) // 2

        cells = set()

        for y in range(pattern_height):
            for x in range(pattern_width):
                if pattern[y][x] == "X":
                    cells.add((start_x + x, start_y + y))

        return cells

    def generate(self) -> list[list[int]]:
        visited: list[list[bool]] = [
            [False] * self.width for i in range(self.height)]
        blocked_cells = self.get_42_cells()
        for x, y in blocked_cells:
            visited[y][x] = True
            self.grid[y][x] = 15
        current: tuple[int, int] = self.entry
        stack: list[tuple[int, int]] = []
        # print("current: ", current)
        random.seed(self.seed)
        visited[current[1]][current[0]] = True
        print(self.find_neighbors(visited, current))
        while True:
            neighbors = self.find_neighbors(visited, current)
            if not neighbors and not stack:
                break
            if not neighbors:
                current = stack.pop()
            else:
                neighbor = random.choice(neighbors)
                self.remove_wall(current, neighbor)
                stack.append(current)
                visited[neighbor[2]][neighbor[1]] = True
                current = (neighbor[1], neighbor[2])
        if not self.perfect:
            self.not_perfect(blocked_cells)
        for x, y in blocked_cells:
            self.grid[y][x] = 15

    def find_path(self, parent: dict[
            tuple[int, int], tuple[str, int, int]]) -> str:
        path = ""
        current = self.exit
        while current != self.entry:
            direction, x, y = parent.get(current)
            current = (x, y)
            path += direction
        return path[::-1]

    def find_open_neighbors(self, point: tuple[
            int, int]) -> list[tuple[str, int, int]]:
        x, y = point
        walls: int = self.grid[y][x]
        # print(walls)
        neighbors = []
        if not (walls & 1) and self.within_bounds(x, y - 1):
            neighbors.append(("N", x, y - 1))
        if not (walls & 2) and self.within_bounds(x + 1, y):
            neighbors.append(("E", x + 1, y)) 
        if not (walls & 4) and self.within_bounds(x, y + 1):
            neighbors.append(("S", x, y + 1))
        if not (walls & 8) and self.within_bounds(x - 1, y):
            neighbors.append(("W", x - 1, y))
        return neighbors

    def solve(self) -> str:
        queue = deque([self.entry])
        visited = set()
        parent = {}

        visited.add(self.entry)
        while queue:
            vertex = queue.popleft()
            if vertex == self.exit:
                break
            neighbors = self.find_open_neighbors(vertex)
            # print(f"neighbors of {vertex}: {neighbors}")
            for direction, x, y in neighbors:
                # print(direction, x, y)
                neighbor = (x, y)
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = (direction, vertex[0], vertex[1])
        return self.find_path(parent)

    def output(self, path: str) -> None:
        base: str = "0123456789ABCDEF"
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        with open(self.output_file, "w") as file:
            for row in range(self.height):
                for column in range(self.width):
                    file.write(base[self.grid[row][column]])
                file.write("\n")
            file.write(f"\n{entry_x},{entry_y}")
            file.write(f"\n{exit_x},{exit_y}\n")
            file.write(path)

    def display_terminal(self) -> None:
        N = 1
        E = 2
        S = 4
        W = 8
        for y in range(self.height):
            for x in range(self.width):
                print("+", end="")
                if self.grid[y][x] & N:
                    print("---",  end="")
                else:
                    print("   ", end="")
            print("+")
            for x in range(self.width):
                if self.grid[y][x] & W:
                    print("|", end="")
                else:
                    print(" ", end="")
                if (x, y) == self.entry:
                    print(" E ", end="")
                elif (x, y) == self.exit:
                    print(" X ", end="")
                elif self.grid[y][x] == 15:
                    print("###", end="")
                else:
                    print("   ", end="")

            if self.grid[y][self.width - 1] & E:
                print("|")
            else:
                print(" ")

        for x in range(self.width):
            print("+", end="")
            if self.grid[self.height - 1][x] & S:
                print("---", end="")
            else:
                print("   ", end="")
        print("+")

    def not_perfect(self, blocked_cells: set[tuple[int, int]]) -> None:
        attempts: int = (self.width * self.width) // 3

        directions: list[tuple[str, int, int]] = [
            ("N", 0, -1),
            ("S", 0, 1),
            ("E", 1, 0),
            ("W", -1, 0)
        ]

        for _ in range(attempts):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)

            if (x, y) in blocked_cells:
                continue

            direction, dx, dy = random.choice(directions)

            nx = x + dx
            ny = y + dy


            if not self.within_bounds(nx, ny):
                continue
            if (nx, ny) in blocked_cells:
                continue

            self.remove_wall((x, y), (direction, nx, ny))
