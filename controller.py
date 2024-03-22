from view import *

class CubeGame():
    def __init__(self, master: tk.Tk, world_file: str) -> None:
        self.master = master
        
        self.world_model = WorldModel(world_file)
        self.player = self.world_model.player
        self.camera = self.world_model.camera
        self.camera.update_visible_faces(self.world_model.cubes)
        self.pressed_keys = []
        self.height = master.winfo_screenheight()
        self.width = master.winfo_screenwidth()
        self.world_view = WorldView(master, self.width, self.height)
        self.world_view.pack()
        master.bind('<KeyPress>', self.handle_keypress)
        master.bind('<KeyRelease>', self.handle_keyrelease)
        master.bind('<Motion>', self.handle_mouse)
        master.bind('<Button-1>', self.handle_lclick)
        master.bind('<Button-3>', self.handle_rclick)
        self.oldx = self.width//2
        self.oldy = self.height//2
        pyautogui.moveTo(self.width//2, self.height//2)
        #master.set_cursor('None')
        self.selected_colour = 'R'
        self.shooting_mode = False
        self.menu = False

        midx = self.width//2
        midy = self.height//2
        self.buttons = []
        self.buttons.append(CanvasButton(self.world_view,
                                         midx-400,midy-50,
                                         midx+400,midy,
                                         'Back to Game'))
        self.buttons.append(CanvasButton(self.world_view,
                                         midx-400,midy+50,
                                         midx+400,midy+100,
                                         'Toggle Gamemode'))
        self.buttons.append(CanvasButton(self.world_view,
                                         midx-400,midy+150,
                                         midx-150,midy+200,
                                         'FOV 70'))
        self.buttons.append(CanvasButton(self.world_view,
                                         midx-125,midy+150,
                                         midx+125,midy+200,
                                         'FOV 80'))
        self.buttons.append(CanvasButton(self.world_view,
                                         midx+150,midy+150,
                                         midx+400,midy+200,
                                         'FOV 90'))
        self.buttons.append(CanvasButton(self.world_view,
                                         midx-400,midy+250,
                                         midx+400,midy+300,
                                         'Save World'))
        self.buttons.append(CanvasButton(self.world_view,
                                         midx-400,midy+350,
                                         midx+400,midy+400,
                                         'Quit Game'))
        self.update()
        #print('end of CubeGame init')

    def redraw(self) -> None:
        self.world_view.delete('all')
        if self.menu:
            self.world_view.draw_menu(self.buttons)
        else:
            visible_faces = self.camera.get_visible_faces()
            self.camera.update_face_looked_at(visible_faces)
            face_looked_at = self.camera.get_face_looked_at()
            self.world_view.redraw(visible_faces, face_looked_at, self.camera,
                               self.selected_colour, self.shooting_mode)

    def handle_keypress(self, event: tk.Event) -> None:
        #print(event.keysym)
        if event.keysym == 'Escape':
            self.menu = not self.menu
            if self.menu:
                #self.world_view.set_bg('brown')
                pyautogui.moveTo(self.width//2, self.height//2)
            else:
                self.shooting_mode = False
                self.world_view.set_bg('sky blue')
        if event.keysym in 'fF':
            self.player.set_flying(not self.player.is_flying())
            self.player.set_velocity(0)
        if event.keysym == 'space' and not self.player.is_flying():
            if not self.player.get_velocity():
                self.player.set_velocity(JUMP)
        if event.keysym in '1234567890' or event.keysym == 'minus':
            self.selected_colour = HOTBAR_COLOURS[event.keysym]
        key = event.keysym.lower()
        if not key in self.pressed_keys:
            self.pressed_keys.append(key)

    def handle_keyrelease(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        try:
            self.pressed_keys.remove(key)
        except:
            print(f'{key} not in list')

    def handle_keys(self) -> None:
        if 'control_l' in self.pressed_keys:
            self.player.set_speed(SPRINT_SPEED)
        else:
            self.player.set_speed(WALK_SPEED)
            
        new_cube = self.world_model.move_player(self.pressed_keys)
        if new_cube:
            self.camera.update_visible_faces(self.world_model.cubes)
            self.camera.update()
        self.redraw()

    def handle_mouse(self, event: tk.Event) -> None:
        x = event.x
        y = event.y
        dx = x - self.oldx
        dy = y - self.oldy
        if self.shooting_mode:
            dx *= 0.2
            dy *= 0.2
        self.oldx = x
        self.oldy = y
        if self.menu:
            #yes
            for button in self.buttons:
                if button.x1 < x < button.x2 and button.y1 < y < button.y2:
                    button.hover = True
                else:
                    button.hover = False
        else:
            self.camera.look(dx, dy)
            # reset cursor position when you reach the edge of the screen
            if (x < 10 or x > (self.width - 10) or
                y < 10 or y > (self.height - 10)):
                pyautogui.moveTo(self.width//2, self.height//2)
                self.oldx = self.width//2
                self.oldy = self.height//2

    def handle_lclick(self, event: tk.Event) -> None:
        #left click has occurred
        #print(self.world_view.face_looked_at)
        #print('lclick')
        if self.menu:
            x = event.x
            y = event.y
            button_name = ''
            for button in self.buttons:
                if button.x1 < x < button.x2 and button.y1 < y < button.y2:
                    button_name = button.text
            if button_name == 'Back to Game':
                self.menu = False
            if button_name == 'Toggle Gamemode':
                self.shooting_mode = not self.shooting_mode
                if self.shooting_mode:
                    self.camera.set_fov(40)
                    self.world_view.set_bg('royal blue')
                else:
                    self.camera.set_fov(80)
                    self.world_view.set_bg('sky blue')
            if button_name == 'FOV 70':
                self.camera.set_fov(70)
            if button_name == 'FOV 80':
                self.camera.set_fov(80)
            if button_name == 'FOV 90':
                self.camera.set_fov(90)
            if button_name == 'Save World':
                save_world(self.world_model.cubes)
            if button_name == 'Quit Game':
                self.master.destroy()
            return None
        
        if self.shooting_mode:
            to_remove = []
            for coords in self.world_model.cubes:
                cube = self.world_model.cubes[coords]
                #print(list(cube.get_faces().values()))
                #problem is that the faces are two separate identical faces, two instances
                #print(list(cube.get_faces().values())[1])
                #print(self.world_view.face_looked_at == list(cube.get_faces().values())[1])
                for face in list(cube.get_faces().values()):
                    if self.camera.looking_at(face):
                        #print(f'removing cube at {coords}')
                        to_remove.append(coords)
            for coords in to_remove:
                neighbours = Point(coords).get_adjacent()
                for neighbour in neighbours:
                    #print(f'removing neighbour of {coords} at {neighbour}')
                    self.world_model.remove_cube(neighbours[neighbour])
                self.world_model.remove_cube(coords)
            self.camera.update_visible_faces(self.world_model.cubes)
            return None

        face_looked_at = self.camera.get_face_looked_at()
        if face_looked_at:
            # camera is looking at a face
            for coords in self.world_model.cubes:
                cube = self.world_model.cubes[coords]
                for face in list(cube.get_faces().values()):
                    if face_looked_at == face:
                        #print(f'removing cube at {coords}')
                        self.world_model.remove_cube(coords)
                        self.camera.update_visible_faces(self.world_model.cubes)
                        return None
    
    def handle_rclick(self, event: tk.Event) -> None:
        face = self.camera.get_face_looked_at()
        #print('right click')
        if face:
            # get coord for new cube
            #print('am lookin at somethin rn')
            new_corner = face.get_facing()
            self.world_model.add_cube(Cube(new_corner, self.selected_colour))
            self.camera.update_visible_faces(self.world_model.cubes)
    
    def update(self) -> None:
        # do update stuff
        if not self.player.is_flying():
            v = self.player.get_velocity()
            self.player.set_velocity(v + GRAVITY)
            #print(v)
        self.handle_keys()
        self.master.after(20, self.update)
