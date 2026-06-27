import sys
from parse import parsing, ConfigError
from maze_generator import MazeGenerator


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid syntax")
        print('Try "python3 a_maze_ing.py <config>.txt"')
    else:
        try:
            with open(sys.argv[1], "r") as file:
                content: str = file.read()
                configs = parsing(content)
                maze = MazeGenerator(configs)
                grid = maze.generate()
                path = maze.solve()
                maze.display_terminal()
                maze.output(path)

        except ConfigError as c:
            print(f"Caught configuration error: {c}")
        except Exception as e:
            print(f"Caught exception: {e}")
