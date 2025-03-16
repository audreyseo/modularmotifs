import tkinter as tk

from design_examples.deer_scene import x0 as deer_scene
from modularmotifs.core.design import Design
from modularmotifs.core.motif import Motif
from modularmotifs.core.util import motif2png
import modularmotifs.core.util as util
from modularmotifs.motiflibrary.examples import motifs
from PIL import Image, ImageTk

from modularmotifs.ui.grid_numbers import GridNumbers

class PixelCanvas:
    __canvas: tk.Canvas
    
    __old_ids: list
    
    
    def __init__(self, root: tk.Tk, d: Design, pixel_size: int = 10):
        self.__root = root
        self.__d = d
        self.__toplevel = tk.Frame(self.__root)
        self.__pixel_size = pixel_size

        
        self.__nums = GridNumbers(self.__toplevel, self.width(), self.height(), self.pixel_width(), self.pixel_height(), pixel_size, pixel_size)
        
        # self.__top_numbers = tk.Canvas(self.__toplevel)
        # self.__bottom_numbers = tk.Canvas(self.__toplevel)
        # self.__left_numbers = tk.Canvas(self.__toplevel)
        # self.__right_numbers = tk.Canvas(self.__toplevel)
        self.__canvas = tk.Canvas(self.__toplevel)
        
        
        self.__inner_frame = tk.Frame(self.__canvas)
        self.__canvas.create_window((0, 0), window=self.__inner_frame, anchor="nw")
        self.__canvas.configure(width=self.pixel_width(), height=self.pixel_height())
        
        self.__nums.get_top().grid(row=0, column=1)
        self.__nums.get_left().grid(row=1, column=0)
        self.__canvas.grid(row=1, column=1)
        self.__nums.get_right().grid(row=1, column=2)
        self.__nums.get_bottom().grid(row=2, column=1)
        
        self.__hover_motif = motifs["x-3x3"]
        self.__old_hover = None
        self.__old_ids = []
        self.__motif_image = None
        
        self.__canvas.bind("<Motion>", self.hover)
        self.__canvas.bind("<Leave>", lambda _: self.__reset_hover())
        self.init_draw()
        
        def add_motif(event):
            x, y = self.event_to_coords(event)
            self.__d.add_motif(self.__hover_motif, x, y)
            self.refresh()
        self.__canvas.bind("<Button-1>", add_motif)
        pass
    
    def init_draw(self):
        
        self.__init_design()
        self.__init_grid()
        pass
    
    
    def refresh_grid(self):
        for id in self.__hor_lines:
            self.__canvas.delete(id)
            pass
        for id in self.__ver_lines:
            self.__canvas.delete(id)
            pass
        self.__init_grid()
    
    def __init_grid(self):
        self.__hor_lines = []
        for i in range(self.height() + 1):
            y = i * self.__pixel_size
            self.__hor_lines.append(self.__canvas.create_line(0, y, self.pixel_width(), y, fill="black"))
            pass
        self.__ver_lines = []
        for i in range(self.width() + 1):
            x = i * self.__pixel_size
            self.__ver_lines.append(self.__canvas.create_line(x, 0, x, self.pixel_height(), fill="black"))
                
    
    def __add_old_id(self, id):
        self.__old_ids.append(id)
    
    def __init_design(self):
        self.__rects = []
        for i in range(self.height()):
            rects_row = []
            y0 = i * self.__pixel_size
            for j in range(self.width()):
                c = self.__d.get_rgba(j, i)
                x0 = j * self.__pixel_size
                
                rects_row.append(self.__canvas.create_rectangle(x0, y0, x0 + self.__pixel_size, y0 + self.__pixel_size, fill=c.hex(), width=0))
                pass
            self.__rects.append(rects_row)
            pass
        pass
    
    def refresh_design(self):
        print(self.__canvas.itemconfigure(self.__rects[0][0]))
        for i in range(len(self.__rects)):
            for j in range(len(self.__rects[i])):
                id = self.__rects[i][j]
                self.__canvas.itemconfigure(id, fill=self.__d.get_rgba(j, i).hex())
                pass
            pass
        pass
    
    def __remove_old_ids(self):
        for id in self.__old_ids:
            self.__canvas.delete(id)
            pass
        self.__old_ids = []
        pass
    
    def __reset_hover(self):
        self.__old_hover = None
        self.__remove_old_ids()
        pass
    
    def event_to_coords(self, event) -> tuple[int, int]:
        simple_x = min(self.width() - self.__hover_motif.width(), event.x // self.__pixel_size)
        simple_y = min(self.height() - self.__hover_motif.height(), event.y // self.__pixel_size)
        return simple_x, simple_y
    
    def hover(self, event):
        if not self.__hover_motif:
            return
        # print(event.x, event.y)
        simple_x, simple_y = self.event_to_coords(event)
        if self.__old_hover:
            old_x, old_y = self.__old_hover
            if old_x == simple_x and old_y == simple_y:
                return
            else:
                self.__old_hover = (simple_x, simple_y)
        else:
            self.__old_hover = (simple_x, simple_y)
        
        if self.__old_ids:
            self.__remove_old_ids()
        
        if not self.__motif_image:
            img = util.rgbcolors_to_image(util.motif_to_lol(self.__hover_motif), square_size = self.__pixel_size, mode="RGBA", opacity=127)
            self.__motif_image = ImageTk.PhotoImage(img)
            pass
        self.__add_old_id(self.__canvas.create_image(simple_x * self.__pixel_size, simple_y * self.__pixel_size, image=self.__motif_image, anchor="nw"))
        
        # put all added images below the horizontal lines
        for id in self.__old_ids:
            self.__canvas.tag_lower(id, self.__hor_lines[0])
            pass
        pass
    
    def set_motif(self, m: Motif):
        self.__hover_motif = m
        img = util.rgbcolors_to_image(util.motif_to_lol(self.__hover_motif), square_size = self.__pixel_size, mode="RGBA", opacity=127)
        self.__motif_image = ImageTk.PhotoImage(img)
        self.__reset_hover()
        pass
        
    def height(self) -> int:
        return self.__d.height()
    
    def width(self) -> int:
        return self.__d.width()
    
    def pixel_height(self) -> int:
        return self.height() * self.__pixel_size
    
    def pixel_width(self) -> int:
        return self.width() * self.__pixel_size
    
    def get_toplevel(self) -> tk.Frame:
        return self.__toplevel
    
    def get_canvas(self) -> tk.Canvas:
        return self.__canvas
    
    def __add_column(self, width: int) -> None:
        for i in range(len(self.__rects)):
            x0 = width * self.__pixel_size
            y0 = i * self.__pixel_size
            id = self.create_pixel(x0, y0)
            # id = self.__canvas.create_rectangle(x0, y0, x0 + self.__pixel_size, y0 + self.__pixel_size, width=0)
            self.__rects[i].append(id)
            pass
        
        pass
    
    def create_pixel(self, x0: int, y0: int, **kwargs):
        id = self.__canvas.create_rectangle(x0, y0, x0 + self.__pixel_size, y0 + self.__pixel_size, width=0, **kwargs)
        
        self.__canvas.tag_lower(id, self.__hor_lines[0])
        return id
    
    def __add_row(self, height: int) -> None:
        new_row = []
        for i in range(len(self.__rects[0])):
            x0 = i * self.__pixel_size
            y0 = height * self.__pixel_size
            id = self.create_pixel(x0, y0)
            new_row.append(id)
            pass
        self.__rects.append(new_row)
        pass
    
    def add_row(self, height: int) -> None:
        self.__nums.add_horizontals()
        self.__add_row(height)
        pass
    
    def add_column(self, width: int) -> None:
        self.__nums.add_verticals()
        self.__add_column(width)
        pass
    
    def remove_row(self) -> None:
        self.__nums.remove_horizontals()
        self.__remove_row()
        pass
    
    def remove_column(self) -> None:
        self.__nums.remove_verticals()
        self.__remove_column()
    
    def __remove_row(self) -> None:
        old_row = self.__rects.pop(-1)
        for tag in old_row:
            self.__canvas.delete(tag)
            pass
        pass
    
    def __remove_column(self) -> None:
        old_column = [self.__rects[i].pop(-1) for i in range(len(self.__rects))]
        for tag in old_column:
            self.__canvas.delete(tag)
            pass
        pass
        
        
        
    
    def add_numbers(self) -> None:
        self.__nums.add_horizontals()
        self.__nums.add_verticals()
        h = self.height()
        w = self.width()
        print(w, h)
        self.__add_column(w)
        self.__d.add_column()
        self.__add_row(h)
        self.__d.add_row()
        self.refresh()
        # self.__canvas.configure(width=self.pixel_width(), height=self.pixel_height())
        # self.refresh_grid()
        # self.refresh_design()
        print(self.width(), self.height())
        pass
    
    def refresh(self) -> None:
        self.__canvas.configure(width=self.pixel_width(), height=self.pixel_height())
        self.refresh_grid()
        self.refresh_design()
    
    def remove_numbers(self) -> None:
        self.__nums.remove_horizontals()
        self.__nums.remove_verticals()
        self.__d.remove_column()
        self.__remove_column()
        self.__d.remove_row()
        self.__remove_row()
        self.refresh()
        # self.__canvas.configure(width=self.pixel_width(), height=self.pixel_height())
        # self.refresh_grid()
        # self.refresh_design()
        
        pass
    pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Pixel Canvas")
    
    frame = tk.Frame(root)
    frame.pack()
    
    pc = PixelCanvas(root, deer_scene, pixel_size=20)
    button = tk.Button(frame, text="Add Numbers", command=pc.add_numbers)
    button.pack(side="left")
    button1 = tk.Button(frame, text="Remove Numbers", command=pc.remove_numbers)
    button1.pack(side="left")
    button2 = tk.Button(frame, text="Refresh", command=pc.refresh_design)
    button2.pack(side="left")
    
    pc.get_toplevel().pack()
    root.mainloop()
    
