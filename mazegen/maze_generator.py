import random
from collections import deque


class MazeError(Exception):
    """the Class containing the error message that handles the error
    messages concerning maze generating
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MazeGenerator:
    """Generate, solve, and render a grid-based maze.

    The maze is represented as a 2D grid where each cell stores a
    4-bit value encoding which of its walls (North, East, South,
    West) are closed. Generation uses a recursive backtracker, and
    solving uses breadth-first search to find the shortest path.

    Attributes:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        entry: (x, y) coordinates of the maze entrance.
        exit: (x, y) coordinates of the maze exit.
        output_file: Path to write the generated maze to.
        perfect: If True, the maze has exactly one path between
            entry and exit. If False, extra connections are added.
        seed: Seed used for reproducible random generation.
        grid: 2D list of integers, one per cell, encoding wall state.
    """
    def __init__(self,
                 config:
                 dict[str, str | int | bool | tuple[int, int]]) -> None:
        """Initialize a maze generator from a configuration dictionary.

        Args:
            config: Dictionary containing the maze configuration. The
                expected keys are:

                - ``WIDTH``: Maze width in cells.
                - ``HEIGHT``: Maze height in cells.
                - ``ENTRY``: Entrance coordinates as ``(x, y)``.
                - ``EXIT``: Exit coordinates as ``(x, y)``.
                - ``OUTPUT_FILE``: Path to the output file.
                - ``PERFECT``: Whether to generate a perfect maze.
                - ``SEED``: Random seed for deterministic generation.
        """
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
        self.show_path: bool = True
        self.wallcolor: str = "\033[0m"
        self.resetcolor: str = "\033[0m"

    def remove_wall(self, current: tuple[int, int], neighbor: tuple[
            str, int, int]) -> None:
        """Remove the shared wall between two adjacent cells.

        Updates both cells so that the maze representation remains
        consistent.

        Args:
            current: (x, y) coordinates of the current cell.
            neighbor: A tuple of (direction, x, y) describing the
                neighboring cell and the direction to reach it from
                current, where direction is one of "N", "E", "S", "W".
        """
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
        """Check whether a coordinate lies inside the maze grid.

        Args:
            x: Column index to check.
            y: Row index to check.

        Returns:
            True if (x, y) is within the maze dimensions, False
            otherwise.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return True

    def find_neighbors(self, visited: list[list[bool]], point: tuple[
            int, int]) -> list[tuple[str, int, int]]:
        """Return all unvisited neighboring cells.

        Neighbors are returned together with the direction required to
        reach them from the current cell.

        Args:
            visited: Grid indicating which cells have already been visited.
            point: Coordinates of the current cell.

        Returns:
            A list of tuples in the form ``(direction, x, y)`` for every
            adjacent unvisited cell.
        """
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
        """Return the cells used to display the '42' obstacle pattern.

        The pattern is centered within the maze whenever the maze is large
        enough. If the maze is too small to contain the pattern, an empty
        set is returned.

        Returns:
            A set containing the coordinates of every blocked cell that
            forms the decorative pattern.
        """
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

    def generate(self) -> None:
        """Generate the maze using recursive backtracking.

        Starting from the entrance, neighboring cells are visited in a
        randomized depth-first order while walls are removed to create
        passages. If configured as a non-perfect maze, additional openings
        are added after generation.

        Raises:
            MazeError: If the entry or exit overlaps the blocked pattern.
        """
        visited: list[list[bool]] = [
            [False] * self.width for i in range(self.height)]
        blocked_cells = self.get_42_cells()
        if self.entry in blocked_cells or self.exit in blocked_cells:
            raise MazeError(
                "ENTRY and Exit points can not overlap with 42 pattern")
        for x, y in blocked_cells:
            visited[y][x] = True
            self.grid[y][x] = 15
        current: tuple[int, int] = self.entry
        stack: list[tuple[int, int]] = []
        random.seed(self.seed)
        visited[current[1]][current[0]] = True
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

    def find_path(self, parent: dict[
            tuple[int, int], tuple[str, int, int]]) -> str:
        """Reconstruct the solution path from a parent map.

        Args:
            parent: Mapping produced during breadth-first search that
                records the predecessor of each visited cell.

        Returns:
            A string containing the movement sequence from the entrance to
            the exit.

        Raises:
            MazeError: If no path exists between the entry and exit.
        """
        path = ""
        current = self.exit
        while current != self.entry:
            if current not in parent:
                raise MazeError("No path between entry and exit")
            direction, x, y = parent[current]
            current = (x, y)
            path += direction
        return path[::-1]

    def find_open_neighbors(self, point: tuple[
            int, int]) -> list[tuple[str, int, int]]:
        """Return all reachable neighboring cells.

        Only neighbors connected by an open passage are included.

        Args:
            point: Coordinates of the current cell.

        Returns:
            A list of reachable neighboring cells represented as
            ``(direction, x, y)`` tuples.
        """
        x, y = point
        walls: int = self.grid[y][x]
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
        """Solve the maze using breadth-first search.

        Breadth-first search guarantees the shortest path in an unweighted
        maze.

        Returns:
            A string describing the shortest path from the entrance to the
            exit using the characters ``N``, ``E``, ``S``, and ``W``.

        Raises:
            MazeError: If no path exists between the entry and exit.
        """
        queue: deque[tuple[int, int]] = deque([self.entry])
        visited: set[tuple[int, int]] = set()
        parent: dict[tuple[int, int], tuple[str, int, int]] = {}

        visited.add(self.entry)
        while queue:
            vertex = queue.popleft()
            if vertex == self.exit:
                break
            neighbors = self.find_open_neighbors(vertex)
            for direction, x, y in neighbors:
                neighbor = (x, y)
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = (direction, vertex[0], vertex[1])
        return self.find_path(parent)

    def output(self, path: str) -> None:
        """Write the maze and its solution to the output file.

        The file contains the hexadecimal wall representation of the maze,
        followed by the entry position, exit position, and solution path.

        Args:
            path: Solution path returned by :meth:`solve`.
        """
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
            file.write(path + "\n")

    def path_cells(self, path: str) -> set[tuple[int, int]]:
        """Convert a movement sequence into visited cell coordinates.

        Args:
            path: Sequence of movement directions.

        Returns:
            A set containing every cell visited while following the path,
            including the entry cell.
        """
        x, y = self.entry
        cells = {(x, y)}
        for move in path:
            if move == "N":
                y -= 1
            elif move == "S":
                y += 1
            elif move == "E":
                x += 1
            elif move == "W":
                x -= 1
            cells.add((x, y))
        return cells

    def print_helper(self, string: str, ending: str = "") -> None:
        print(f"{self.wallcolor}{string}{self.resetcolor}",  end=ending)

    def display_terminal(self, path: str = "") -> None:
        """Render the maze as ASCII art.

        Optionally highlights a solution path using ``*`` characters while
        marking the entrance, exit, and blocked cells.

        Args:
            path: Optional solution path to display.
        """
        N = 1
        E = 2
        S = 4
        W = 8
        path_cells = self.path_cells(path) if path else set()
        for y in range(self.height):
            for x in range(self.width):
                self.print_helper("+")
                if self.grid[y][x] & N:
                    self.print_helper("---")
                else:
                    print("   ", end="")
            self.print_helper("+", "\n")
            for x in range(self.width):
                if self.grid[y][x] & W:
                    self.print_helper("|")
                else:
                    print(" ", end="")
                if (x, y) == self.entry:
                    print(" E ", end="")
                elif (x, y) == self.exit:
                    print(" X ", end="")
                elif (x, y) in path_cells and self.show_path:
                    print(" * ", end="")
                elif self.grid[y][x] == 15:
                    print("###", end="")
                else:
                    print("   ", end="")

            if self.grid[y][self.width - 1] & E:
                self.print_helper("|", "\n")
            else:
                print(" ")

        for x in range(self.width):
            self.print_helper("+")
            if self.grid[self.height - 1][x] & S:
                self.print_helper("---")
            else:
                print("   ", end="")
        self.print_helper("+", "\n")

    def build_wall(self, current: tuple[int, int], neighbor: tuple[
            str, int, int]) -> None:
        """Close the shared wall between two adjacent cells.

        Restores the corresponding wall bits in both cells to maintain a
        consistent maze representation.

        Args:
            current: Coordinates of the current cell.
            neighbor: Neighbor description as
                ``(direction, x, y)``.
        """
        cx, cy = current
        direction, nx, ny = neighbor
        N: int = 1
        E: int = 2
        S: int = 4
        W: int = 8
        if direction == "N":
            self.grid[ny][nx] |= S
            self.grid[cy][cx] |= N
        elif direction == "S":
            self.grid[ny][nx] |= N
            self.grid[cy][cx] |= S
        if direction == "E":
            self.grid[ny][nx] |= W
            self.grid[cy][cx] |= E
        elif direction == "W":
            self.grid[ny][nx] |= E
            self.grid[cy][cx] |= W

    def is_3x3_open(self, x: int, y: int) -> bool:
        """Check whether a 3x3 region contains no internal walls.

        The supplied coordinates represent the upper-left corner of the
        region.

        Args:
            x: Leftmost column of the region.
            y: Top row of the region.

        Returns:
            True if the region forms a completely open 3x3 area, otherwise
            False.
        """
        for row in range(y, y + 3):
            if self.grid[row][x] & 2 or self.grid[row][x + 1] & 2:
                return False
        for column in range(x, x + 3):
            if self.grid[y][column] & 4 or self.grid[y + 1][column] & 4:
                return False
        return True

    def creates_3x3(self) -> bool:
        """Determine whether the maze contains an open 3x3 area.

        Returns:
            True if any completely open 3x3 region exists, otherwise False.
        """
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                if self.is_3x3_open(x, y):
                    return True
        return False

    def not_perfect(self, blocked_cells: set[tuple[int, int]]) -> None:
        """Introduce additional passages into the maze.

        Random walls are removed to create loops while ensuring that no
        fully open 3x3 area is introduced. Any wall removal that violates
        this constraint is reverted.

        Args:
            blocked_cells: Cells reserved for the decorative obstacle
                pattern and excluded from modification.
        """
        attempts: int = (self.width * self.height) // 3

        if self.width < 3 or self.height < 3:
            return

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
            if self.creates_3x3():
                self.build_wall((x, y), (direction, nx, ny))

    def reset(self) -> None:
        self.grid = [[15] * self.width for i in range(self.height)]
        self.seed = random.randint(1, 1000)

    def change_color(self) -> None:
        colors = [
            "\033[30m",
            "\033[31m",
            "\033[32m",
            "\033[33m",
            "\033[34m",
            "\033[35m",
            "\033[36m",
            "\033[37m",
        ]
        color: str = random.choice(colors)
        while color == self.wallcolor:
            color = random.choice(colors)
        self.wallcolor = color
