import tkinter as tk
from constants import *
from math import *

def read_map(map_file: str) -> list[list[str]]:
    """ Reads the map file and returns a list of layers, where each layer is
    a list of strings.

    Parameters:
        map_file: The path to the map file.

    Returns:
        A list of layers representing the world.
    """
    with open(map_file, 'r') as file:
        layers = []
        new_layer = []
        for line in file.readlines():
            if line.strip():
                new_layer.append(line.strip())
            else:
                layers.append(new_layer)
                new_layer = []
        layers.append(new_layer)
        return layers

def save_world(cubes: dict) -> None:
    with open('worlds/new_world.txt', 'x') as file:
        for z in range(32):
            for y in range(32):
                this_line = ''
                for x in range(32):
                    if (x,y,z) in cubes:
                        this_line += cubes[(x,y,z)].cube_type
                    else:
                        this_line += '.'
                file.write(this_line)
                file.write('\n')
            file.write('\n')

def pol_to_cart(polar_vector: tuple[float, float, float]
                ) -> tuple[float, float, float]:
    r, h, v = polar_vector
    h = radians(h)
    v = radians(v)
    x = r*cos(h)*cos(v)
    y = -r*sin(h)*cos(v)
    z = r*sin(v)
    return (x,y,z)
