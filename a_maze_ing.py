import sys
import os
from parse import parsing, ConfigError
from mazegen.maze_generator import MazeGenerator, MazeError


def clear_terminal() -> None:
    """Clear the terminal screen.

    Uses the correct command depending on the operating system:
    ``cls`` on Windows and ``clear`` on Linux/macOS.

    Returns:
        None.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    """Run the A-Maze-ing program.

    The program expects exactly one command-line argument: the path to a
    configuration file. It parses the configuration, generates a maze,
    solves it, writes the hexadecimal output file, and starts an interactive
    terminal menu.

    The menu allows the user to regenerate the maze, show or hide the
    shortest path, rotate wall colors, or quit the program.

    Returns:
        None.
    """
    if len(sys.argv) != 2:
        print("Invalid syntax")
        print('Try "python3 a_maze_ing.py <config>.txt"')
    else:
        try:
            with open(sys.argv[1], "r") as file:
                content: str = file.read()
                configs = parsing(content)
                maze = MazeGenerator(configs)
                maze.generate()
                path = maze.solve()
                maze.output(path)
                while True:
                    maze.display_terminal(path)
                    print("\n=== A-Maze-ing ===")
                    print("1. Re-generate a new maze")
                    print("2. Show/Hide path from entry to exit")
                    print("3. Rotate maze colors")
                    print("4. Quit")

                    choice: str = input("Choice? (1-4): ")
                    clear_terminal()

                    if choice == "1":
                        maze.reset()
                        maze.generate()
                        path = maze.solve()
                        maze.output(path)
                    elif choice == "2":
                        maze.show_path = not maze.show_path
                    elif choice == "3":
                        maze.change_color()
                    elif choice == "4":
                        break
                    else:
                        print("Invalid choice, please choose 1-4")

        except ConfigError as c:
            print(f"Caught configuration error: {c}")
        except MazeError as m:
            print(f"Caught maze error: {m}")
        except Exception as e:
            print(f"Caught exception: {e}")
