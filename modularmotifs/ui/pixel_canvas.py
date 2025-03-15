import tkinter as tk

from design_examples.deer_scene import x0 as deer_scene
from modularmotifs.core.design import Design
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
        
        self.__canvas.bind("<Motion>", self.paint)
        self.__canvas.bind("<Leave>", lambda _: self.__reset_hover())
        self.init_draw()
        pass
    
    def init_draw(self):
        
        self.__init_design()
        self.__init_grid()
        pass
    
    
    
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
    
    
    def paint(self, event):
        if not self.__hover_motif:
            return
        # print(event.x, event.y)
        simple_x = min(self.width() - self.__hover_motif.width(), event.x // self.__pixel_size)
        simple_y = min(self.height() - self.__hover_motif.height(), event.y // self.__pixel_size)
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
        
        # Colour
        Colour = "#000fff000"
        if not self.__motif_image:
            img = util.rgbcolors_to_image(util.motif_to_lol(self.__hover_motif), square_size = self.__pixel_size, mode="RGBA", opacity=127)
            self.__motif_image = ImageTk.PhotoImage(img)
            pass
        self.__add_old_id(self.__canvas.create_image(simple_x * self.__pixel_size, simple_y * self.__pixel_size, image=self.__motif_image, anchor="nw"))
        
        # put all added images below the horizontal lines
        for id in self.__old_ids:
            self.__canvas.tag_lower(id, self.__hor_lines[0])
        
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
    pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Pixel Canvas")
    button = tk.Button(root, text="Button")
    button.pack()
    pc = PixelCanvas(root, deer_scene, pixel_size=20)
    pc.get_toplevel().pack()
    root.mainloop()
    
