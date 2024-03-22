# from tkinter import filedialog # For masters task
# from typing import Callable, Union, Optional
from model import *
from view import *
from controller import *

def play_game(root: tk.Tk, world_file: str) -> None:
    CubeGame(root, world_file)
    root.mainloop()

def main() -> None:
    """ Constructs the root window and calls the play_game function. """
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    world_file = 'worlds/new_world.txt'
    play_game(root, world_file)

if __name__ == '__main__':
    main()
