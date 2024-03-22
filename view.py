from model import *

class CanvasButton():
    def __init__(self, master, x1, y1, x2, y2, text: str) -> None:
        self.coords = [x1,y1,x2,y2]
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.text = text
        self.canvas = master
        self.hover = False

    def draw(self) -> None:
        if self.hover:
            fill = '#888888'
            outline = '#555555'
        else:
            fill = '#bbbbbb'
            outline = '#888888'
        self.canvas.create_rectangle(self.coords, fill=fill, width=2,
                                outline=outline)
        x = (self.x1 + self.x2)//2
        y = (self.y1 + self.y2)//2
        self.canvas.create_text(x, y, text=self.text, fill='white',
                           font=('Helvetica 24 bold'))

'''
class MenuView():
    def __init__(self) -> None:
        self.buttons = []
'''
    
class WorldView(tk.Canvas):
    def __init__(self, master: tk.Tk, width: int, height: int) -> None:
        super().__init__(master, width=width, height=height, bg='sky blue')
        self.width = width
        self.height = height
        self.face_looked_at = None
        self.bg = 'sky blue'

    def set_bg(self, bg: str) -> None:
        self.bg = bg

    def draw_hotbar(self, current_colour: str) -> None:
        cell_width = self.width // 33
        y1 = self.height - cell_width - 10
        y2 = y1 + cell_width
        for i, colour in enumerate(HOTBAR_COLOURS):
            # top left is (self.width//2 - 5cell_width),(height - cell_width)
            x1 = int(self.width/2 + (i-5.5)*cell_width)
            x2 = x1 + cell_width
            colour_code = HOTBAR_COLOURS[colour]
            colour = COLOURS[colour_code]
            if current_colour == colour_code:
                index = i
            self.create_rectangle(x1, y1, x2, y2, fill=colour, width=4,
                                  outline='grey')
        x1 = int(self.width/2 + (index-5.5)*cell_width)
        x2 = x1 + cell_width
        self.create_rectangle(x1, y1, x2, y2, width=8, outline='light grey')

    def draw_snipe(self) -> None:
        diameter = self.height + 100
        r = diameter/2
        firstangle = asin(self.height / diameter)
        n = 20
        points = [int(self.width/2 + r*cos(firstangle)), 0]
        for i in range(n-1):
            angle = firstangle - (i+1)*(2*firstangle/n)
            x = self.width/2 + r*cos(angle)
            y = self.height/2 - r*sin(angle)
            points.append(int(x))
            points.append(int(y))
        points += [int(self.width/2 + r*cos(firstangle)), self.height,
                   self.width, self.height,
                   self.width, 0]
        mirrored_points = [a if i%2 else self.width - a for i, a in enumerate(points)]
        self.create_polygon(points, fill='black')
        #print(points)
        #print(mirrored_points)
        self.create_polygon(mirrored_points, fill='black')
        r = int(r)
        k = 40
        self.create_oval(self.width//2 - r + k, self.height//2 - r + k,
                         self.width//2 + r - k, self.height//2 + r - k, width = 3)
        self.create_line(self.width//2, 0, self.width//2, self.height, width=2)
        self.create_line(self.width//2, self.height//2 + 250,
                         self.width//2, self.height, width=8)
        self.create_line(self.width//2 - r + k, self.height//2,
                         self.width//2 + r - k, self.height//2, width=2)
        self.create_line(self.width//2 - r + k, self.height//2,
                         self.width//2 - r + k + 40, self.height//2, width=8)
        self.create_line(self.width//2 + r - k, self.height//2,
                         self.width//2 + r - k - 40, self.height//2, width=8)
        for i in range(4):
             self.create_line(self.width//2 - 5, self.height//2 + (i+1)*50-25,
                              self.width//2 + 5, self.height//2 + (i+1)*50-25,
                              width=2)
             self.create_line(self.width//2 - 15, self.height//2 + (i+1)*50,
                              self.width//2 + 15, self.height//2 + (i+1)*50,
                              width=2)
        a = 225
        self.create_rectangle(self.width//2 - a, self.height - 170,
                              self.width//2 + a, self.height - 145, fill='cornflower blue',
                              width=0)
        self.create_text(self.width//2 - a + 40, self.height - 158,
                           text='100', fill='white', font=('Helvetica 15 bold'))
        self.create_rectangle(self.width//2 - a, self.height - 140,
                              self.width//2 + a, self.height - 115, fill='lime',
                              width=0)
        self.create_text(self.width//2 - a + 40, self.height - 128,
                           text='100', fill='white', font=('Helvetica 15 bold'))

    def draw_menu(self, buttons) -> None:
        self.config(bg='saddle brown')
        self.create_text(self.width//2, 250, text='CUBE GAME', fill='white',
                         font=('Helvetica 96 bold'))
        for button in buttons:
            button.draw()
        
    def redraw(self, visible_faces: list[list[Face], str, float],
               face_looked_at: Face, camera: Camera, selected_colour: str,
               shooting=False) -> None:
        #self.delete('all')
        self.config(bg=self.bg)
        for cube in visible_faces:
            faces = cube[0]
            cube_type = cube[1]
            colour = COLOURS[cube_type]
            line_width = 0

            if face_looked_at in faces:
                line_width = 5

            '''
            for face in faces:
                if face is face_looked_at:
                    line_width = 5
            '''
            
            for face in faces:
                mapped_points = []
                coords = camera.window_coords(face)
                for coord_pair in coords:
                    x, y = coord_pair
                    x *= 10*self.width
                    y *= 10*self.width
                    x = self.width/2 + x
                    y = self.height/2 - y
                    mapped_points.append(x)
                    mapped_points.append(y)
                #draw quad on canvas
                if len(mapped_points) >= 6:
                    self.create_polygon(mapped_points, outline='black',
                                        fill=colour, width=line_width)
        if shooting:
            self.draw_snipe()
        else:
            self.draw_hotbar(selected_colour)
            self.create_line(self.width//2, self.height//2 - 20,
                             self.width//2, self.height//2 + 20,
                             fill='grey', width=4)
            self.create_line(self.width//2 - 20, self.height//2,
                             self.width//2 + 20, self.height//2,
                             fill='grey', width=4)
