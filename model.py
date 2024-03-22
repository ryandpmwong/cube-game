import pyautogui
import tkinter as tk
from constants import *
from support import *

class Point():
    def __init__(self, coords: tuple[float, float, float]):
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.z = coords[2]

    def get_class_name(self) -> str:
        """ Returns the name of this class """
        return type(self).__name__

    def get_coords(self) -> tuple[float, float, float]:
        return self.coords

    def get_adjacent(self) -> dict[tuple[int, int, int], tuple[int, int, int]]:
        """ Returns the corner points of the six adjacent cubes to self """
        neighbours = {}
        for delta in DELTAS:
            neighbour = self + Point(delta)
            neighbours[delta] = neighbour.coords
        return neighbours

    def get_intersect(self, other: 'Point', x: float) -> tuple[float, float]:
        """ Return the y and z coordinates of the intersection of the following:
        - The line joining self and other,
        - The yz plane with x coordinate x """
        y = (other.y - self.y) * (x - self.x) / (other.x - self.x) + self.y
        z = (other.z - self.z) * (x - self.x) / (other.x - self.x) + self.z
        return (y, z)
        
    def scale(self, a: float) -> 'Point':
        return self * Point((a,a,a))

    def get_magnitude(self) -> float:
        """ Return the magnitude of self """
        return self.distance(Point((0,0,0)))

    def get_unit(self) -> 'Point':
        """ Return the unit vector with the same direction as self """
        r = self.get_magnitude()
        return self.scale(1/r)

    def __add__(self, other: 'Point') -> 'Point':
        """ Returns the vector sum of self and other """
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point((x,y,z))

    def __mul__(self, other: 'Point') -> 'Point':
        """ Performs element-wise multiplication """
        x = self.x * other.x
        y = self.y * other.y
        z = self.z * other.z
        return Point((x,y,z))

    def __sub__(self, other: 'Point') -> 'Point':
        return self + other.scale(-1)

    def __eq__(self, other: 'Point') -> bool:
        return self.coords == other.coords

    def distance(self, other: 'Point') -> float:
        return ((self.x-other.x)**2 +
                (self.y-other.y)**2 +
                (self.z-other.z)**2)**0.5

    def __str__(self) -> str:
        return str(self.coords)

    def __repr__(self) -> str:
        """ Returns the text that would be required to create a new instance of
        this class identical to self."""
        return f'{self.get_class_name()}({self.coords})'

class Face():
    """ A 2D rectangle defined by two corner points

    Attributes:
        corners: A tuple containing two opposite corners of the rectangle
        plane: The plane which this face is parallel to
        facing: 1 if facing the positing direction, -1 otherwise
        exposed: True if adjacent to empty space
    """
    
    def __init__(self, corner1: Point, corner2: Point, facing: int) -> None:
        self.corners = (corner1, corner2)
        self.plane_type = None
        self.plane_type = self.get_plane_type()
        self.plane = self.get_plane()
        self.facing = facing
        self.exposed = True

    def set_exposed(self, exposed: bool) -> None:
        self.exposed = exposed

    def is_exposed(self) -> bool:
        return self.exposed

    def get_facing(self) -> Point:
        """ Returns the corner of the cube which this face is facing """
        if self.facing == 1:
            return self.corners[0]
        return self.corners[0] - self.get_normal()

    def get_plane_type(self) -> list[tuple[float, float, float]]:
        if self.plane_type:
            return self.plane_type
        c1, c2 = self.corners
        if c1.x == c2.x:
            return YZ
        elif c1.y == c2.y:
            return XZ
        elif c1.z == c2.z:
            return XY
        else:
            raise Exception(f'Invalid face corners: {c1}, {c2}')

    def get_normal(self) -> Point:
        """ Returns the positive unit vector normal to face's plane """
        a, b = self.plane_type
        return Point((1,1,1)) - Point(a) - Point(b)

    def get_plane(self) -> Point:
        """ Returns the plane that this face lies within described as a point.
        E.g. Plane with equation y = 5 returns Point((0,5,0))"""
        return self.get_normal() * self.corners[0]
        
    def get_vertices(self) -> list[Point]:
        c1, c2 = self.corners
        diff = c2 - c1
        vertices = []
        vertices.append(self.corners[0])
        vertices.append(c1 + diff*Point(self.plane_type[0]))
        vertices.append(self.corners[1])
        vertices.append(c1 + diff*Point(self.plane_type[1]))
        return vertices

    def __eq__(self, other: 'Face') -> bool:
        return (type(other).__name__ == 'Face' and
                self.corners == other.corners and
                self.facing == other.facing)

    def __str__(self) -> str:
        return f'Face bounded by {self.corners[0]} and {self.corners[1]}'

    def __repr__(self) -> str:
        # self.corners[0] and [1] print str representation instead of repr
        return f'Face({self.corners[0]}, {self.corners[1]}, {self.facing})'
    
class Cube():
    def __init__(self, corner: Point, cube_type: str = 'W') -> None:
        self.corner = corner
        self.cube_type = cube_type
        self.vertices = self.get_vertices()
        self.faces = self.get_faces()    

    def get_vertices(self) -> list[Point]:
        #bottom back left vertex is coords
        vertices = []
        for i in range(8):
            dx = i // 1 % 2
            dy = i // 2 % 2
            dz = i // 4 % 2
            new_vertex = self.corner + Point((dx,dy,dz))
            vertices.append(new_vertex)
        return vertices

    def get_faces(self) -> dict[tuple[int, int, int], Face]:
        faces = {}
        corner_deltas = [(0,0,1), (0,1,0), (1,0,0)]
        planes = [(1,1,0), (1,0,1), (0,1,1)]
        for i in range(6):
            if i % 2:
                corner_delta = corner_deltas[i//2]
            else:
                corner_delta = (0,0,0)
            corner = self.corner + Point(corner_delta)
            plane = planes[i//2]
            corner2 = corner + Point(plane)
            facing = (-1) ** (i % 2 + 1)
            new_face = Face(corner, corner2, facing)
            faces[DELTAS[i]] = new_face
        return faces

    def get_exposed(self) -> list[Face]:
        exposed_faces = []
        for key in self.faces:
            face = self.faces[key]
            if face.is_exposed():
                exposed_faces.append(face)
        return exposed_faces
        
    def distance(self, other: 'Cube') -> float:
        """ Returns the distance between the centres of self and other """
        return self.corner.distance(other.corner)

class Camera():
    def __init__(self):
        self.speed = 0.4
        self.pos = Point((4.5,4.5,2.62))
        self.cube_corner = self.get_cube_corner()
        self.cube = Cube(Point(self.cube_corner))
        # set fov between 30 degrees and 110 degrees
        self.fov = 80
        # for a window of width 0.1, calculate distance to window for this fov
        d = 1 / (20 * tan(radians(self.fov)/2))
        self.direction = (d,315,0)
        self.matrix = self.get_rotation_matrix()
        self.visible_faces = None
        self.face_looked_at = None

    def set_fov(self, fov: float) -> None:
        self.fov = fov
        d = 1 / (20 * tan(radians(self.fov)/2))
        _, x, y = self.direction
        self.direction = (d,x,y)

    def set_pos(self, position: Point) -> None:
        self.pos = position
        '''
        self.cube_corner = self.get_cube_corner()
        self.cube = Cube(Point(self.cube_corner))
        '''

    def update(self) -> None:
        self.cube_corner = self.get_cube_corner()
        self.cube = Cube(Point(self.cube_corner))
        #self.matrix = self.get_rotation_matrix()

    def update_face_looked_at(self, faces: list[list[Face], str, float]
                              ) -> None:
        face_looked_at = None
        #change this to filter visible_faces to only the ones in the radius

        
        close_cubes = filter(lambda x: x[2] <= 6, faces)
        for cube in close_cubes:
            for face in cube[0]:
                distance = self.looking_at(face)
                if distance and distance < 5:
                    #get distance to face
                    face_looked_at = face
        
        self.face_looked_at = face_looked_at

    def get_face_looked_at(self) -> Face:
        return self.face_looked_at

    def get_intersect(self, face: Face) -> Point | None:
        """ Gets the intersection of the camera's line of sight and the plane
        that face lies within """
        #maybe rewrite to only give 2 output numbers???
        #actually no bc I need distance from intersect to camera
        #works but is ugly
        #note: there is slight imprecision which causes errors when the value
        #should be an integer but is instead like 0.99999999998 or whatever
        plane_type = face.plane_type
        thingo = Point(plane_type[0]) + Point(plane_type[1])
        plane = face.plane
        c = sum(plane.coords)  # true bc two values are always 0
        #unit = face.plane * (1/magnitude)
        d_coords = pol_to_cart(self.direction)
        normal = face.get_normal()
        d = Point(d_coords) * normal #point
        a = self.pos * normal #point
        if sum(d.coords) == 0:
            return None
        k = (c - sum(a.coords)) / sum(d.coords)
        if k < 0:
            return None
        imprecise_point = self.pos + (Point((k,k,k)) * Point(d_coords))
        # this fixes imprecision:
        abcd = imprecise_point * thingo + plane
        return abcd

    def looking_at(self, face: Face) -> float | None:
        intersect = self.get_intersect(face)
        if not intersect:
            return None
        boolean = True
        c1, c2 = face.corners
        c1 = c1.coords
        c2 = c2.coords
        a = intersect.coords
        for i in range(3):
            if boolean:
                boolean = ((c1[i] - a[i]) * (c2[i] - a[i]) <= 0)
        if boolean:
            return self.pos.distance(intersect)
        
    def get_cube_corner(self) -> tuple[int, int, int]:
        x, y, z = self.pos.coords
        x = x//1
        y = y//1
        z = z//1
        return (x,y,z)

    def look(self, dx: int, dy: int) -> None:
        """ Changes the camera's direction vector

        horizontal angle is changed by dx
        vertical angle is changed by dy """
        new_h = self.direction[1] - dx*0.3
        new_v = max(min(self.direction[2] - dy*0.3, 90), -90)
        new_dir = (self.direction[0], new_h % 360, new_v)
        self.direction = new_dir
        self.matrix = self.get_rotation_matrix()
        
    def can_see(self, face: Face) -> bool:
        """ True if the camera can see face i.e. camera is not behind face"""
        return (((face.get_plane_type() == XY) and
                (face.corners[0].z - self.pos.z) * face.facing < 0) or
               ((face.get_plane_type() == XZ) and
                (face.corners[0].y - self.pos.y) * face.facing < 0) or
               ((face.get_plane_type() == YZ) and
                (face.corners[0].x - self.pos.x) * face.facing < 0))

    def get_visible_faces(self) -> list:
        return self.visible_faces

    def update_visible_faces(self, cubes: dict) -> list:
        """ Returns all faces that could be seen from the camera's cube
        i.e. exposed faces that are facing the camera """
        # structure of output should be
        # dict[coord: list[list[Face], type, distance]]
        all_faces = []
        for coord in cubes:
            this_cube = cubes[coord]
            faces = []
            for face in this_cube.get_exposed():
                if self.can_see(face):
                    faces.append(face)
            cube_type = this_cube.cube_type
            distance = self.cube.distance(this_cube)
            if faces:
                all_faces.append([faces, cube_type, distance])
        all_faces.sort(key = lambda x: x[2], reverse = True)
        self.visible_faces = all_faces

    def get_rotation_matrix(self) -> list[list[float]]:
        _, h_angle, v_angle = self.direction
        a = radians(h_angle)
        b = radians(v_angle)
        sin_a = sin(a)
        cos_a = cos(a)
        sin_b = sin(b)
        cos_b = cos(b)
        matrix = [[cos_a*cos_b, -sin_a*cos_b, sin_b],
                  [sin_a, cos_a, 0],
                  [-cos_a*sin_b, sin_a*sin_b, cos_b]]
        return matrix

    def translate_point(self, point: Point) -> Point:
        return point - self.pos

    def rotate_point(self, point: Point) -> Point:
        coords = point.coords
        out = tuple()
        for row in self.matrix:
            new_entry = 0
            for i in range(3):
                new_entry += row[i]*coords[i]
            out += (new_entry,)
        return Point(out)

    def transform_point(self, point: Point) -> Point:
        """ Translates and then rotates point """
        translated_point = self.translate_point(point)
        rotated_point = self.rotate_point(translated_point)
        return rotated_point

    def window_coords(self, face: Face) -> list[tuple[float, float]]:
        #10/10 style marks for sure definitely great identifier names
        x = self.direction[0]
        points = []
        for vertex in face.get_vertices():
            new_point = self.transform_point(vertex)
            points.append(new_point)

        coord_list = []
        for i, point in enumerate(points):
            if point.x <= 0:
                if points[(i-1)%4].x > x:
                    #generate point between i-1 and i
                    coords = point.get_intersect(points[(i-1)%4], x)
                    coord_list.append(coords)
                if points[(i+1)%4].x > x:
                    #generate point between i and i+1
                    coords = point.get_intersect(points[(i+1)%4], x)
                    coord_list.append(coords)
            else:
                #this works lovely
                y = x * point.y / point.x
                z = x * point.z / point.x
                #coords = point.get_intersect(Point((0,0,0)), x)
                coord_list.append((y,z))
        return coord_list

class Player():
    def __init__(self) -> None:
        self.camera = Camera()
        self.speed = WALK_SPEED
        self.flying = False
        self.v = 0

    def set_speed(self, speed: float) -> None:
        self.speed = speed

    def set_flying(self, flying: bool) -> None:
        self.flying = flying

    def set_velocity(self, v: float) -> None:
        self.v = v

    def is_flying(self) -> bool:
        return self.flying

    def get_velocity(self) -> float:
        return self.v

class WorldModel():
    def __init__(self, map_file) -> None:
        self.cubes = {}
        world = read_map(map_file)
        for z, layer in enumerate(world):
            for y, row in enumerate(layer):
                for x, cube_type in enumerate(row):
                    if not cube_type == '.':
                        new_cube = Cube(Point((x,y,z)), cube_type)
                        self.cubes[(x,y,z)] = new_cube
        for cube in self.cubes:
            self.update(cube)
        self.player = Player()
        self.camera = self.player.camera

    def update_adjacent(self, coords: tuple[int, int, int]) -> None:
        neighbours = Point(coords).get_adjacent()
        for delta in neighbours:
            if neighbours[delta] in self.cubes:
                self.update(neighbours[delta])

    def update(self, coords: tuple[int, int, int]) -> None:
        # this seems to work lovely
        if not coords in self.cubes:
            # no cube to update
            print(f'No cube to update at {coords}')
            return None
        cube = self.cubes[coords]
        neighbours = Point(coords).get_adjacent()
        for delta in neighbours:
            if neighbours[delta] in self.cubes:
                cube.faces[delta].set_exposed(False)
            else:
                cube.faces[delta].set_exposed(True)

    def collision(self, new: Point) -> bool:
        """ True if moving player to new_pos causes a collision """
        vertices = [(new.x-0.3, new.y-0.3, new.z-1.62),
                    (new.x+0.3, new.y-0.3, new.z-1.62),
                    (new.x-0.3, new.y+0.3, new.z-1.62),
                    (new.x+0.3, new.y+0.3, new.z-1.62),
                    (new.x-0.3, new.y-0.3, new.z-0.72),
                    (new.x+0.3, new.y-0.3, new.z-0.72),
                    (new.x-0.3, new.y+0.3, new.z-0.72),
                    (new.x+0.3, new.y+0.3, new.z-0.72),
                    (new.x-0.3, new.y-0.3, new.z+0.18),
                    (new.x+0.3, new.y-0.3, new.z+0.18),
                    (new.x-0.3, new.y+0.3, new.z+0.18),
                    (new.x+0.3, new.y+0.3, new.z+0.18)]
        for vertex in vertices:
            x, y, z = vertex
            cube_corner = (x//1, y//1, z//1)
            if cube_corner in self.cubes:
                return True
        return False

    def move_player(self, keys: list[str]) -> bool:
        direction = Point((0,0,0))
        move_deltas = {'w': (1, 0, 0),
                       'a': (0, -1, 0),
                       's': (-1, 0, 0),
                       'd': (0, 1, 0),
                       'space': (0, 0, 1),
                       'shift_l': (0, 0, -1)}
        for key in move_deltas:
            if key in keys:
                direction += Point(move_deltas[key])


        if self.player.is_flying():
            #yes
            if direction.coords == (0,0,0):
                return False
            unit = direction.get_unit()
        else:
            #no
            x, y, z = direction.get_coords()
            if x or y:
                #some horizontal movement yay
                unit = Point((x,y,0)).get_unit()
            else:
                unit = Point((0,0,0))
            unit += Point((0,0,self.player.get_velocity()))

            
        a = radians(self.camera.direction[1])
        deltas = [(cos(a), -sin(a), 0),
                  (sin(a), cos(a), 0),
                  (0, 0, 1)]
        delta = Point((0,0,0))
        for i, coord in enumerate(unit.coords):
            if i == 2 and not self.player.is_flying():
                delta += Point(deltas[i]).scale(coord)
            else:
                delta += Point(deltas[i]).scale(coord*self.player.speed)
        dx, dy, dz = delta.coords
        deltas = [(dx,0,0), (0,dy,0), (0,0,dz)]
        for i, delta in enumerate(deltas):
            new_pos = self.camera.pos + Point(delta)
            if not self.collision(new_pos):
                self.camera.set_pos(new_pos)
            elif not self.player.is_flying() and i == 2:
                self.player.set_velocity(0)
        if not self.camera.get_cube_corner() == self.camera.cube_corner:
            # player has entered new cube
            return True
        return False
        
    def add_cube(self, cube: Cube) -> None:
        coords = cube.corner.coords
        if coords in self.cubes:
            raise Exception(f'Cube already exists at {cube.corner.coords}')
        self.cubes[coords] = cube
        # update this cube and its neighbours
        self.update(coords)
        self.update_adjacent(coords)

    def remove_cube(self, coords: tuple[int, int, int]) -> None:
        if coords in self.cubes:
            self.cubes.pop(coords)
            self.update_adjacent(coords)
