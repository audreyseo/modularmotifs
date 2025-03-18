from collections.abc import Callable
from enum import Enum
import tkinter as tk
from typing import Any, Optional

from design_examples.deer_scene import x0 as deer_scene
from modularmotifs.core.design import Design
from modularmotifs.core.motif import Motif
from modularmotifs.core.pixel_grid import PixelGrid
from modularmotifs.core.util import motif2png
import modularmotifs.core.util as util
from modularmotifs.motiflibrary.examples import motifs
from PIL import Image, ImageTk

from modularmotifs.ui.grid_numbers import GridNumbers

class ViewMode(Enum):
    GRID = 1
    KNIT = 2

# def flatten_points(l: list[tuple[Any, Any]]) -> list[Any]:
#     flat = []
#     for x, y in l:
#         flat.append(x)
#         flat.append(y)
#         pass
#     return flat

class PixelCanvas:
    __canvas: tk.Canvas
    
    __old_ids: list
    
    
    def __init__(self, root: tk.Tk, d: PixelGrid, pixel_size: int = 10, line_width: float=2.0):
        self.__root = root
        self.__d = d
        self.__toplevel = tk.Frame(self.__root)
        self.__pixel_size = pixel_size
        self.__line_width = line_width

        
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
        self.__nums.get_left().grid(row=1, column=0, rowspan=self.__d.height())
        self.__canvas.grid(row=1, column=1, rowspan=self.__d.height())
        self.__nums.get_right().grid(row=1, column=2, rowspan=self.__d.height())
        self.__nums.get_bottom().grid(row=1 + self.__d.height() + 1, column=1)
        # self.__mode = ViewMode.GRID
        self.__mode = ViewMode.KNIT
        
        self._should_reset_hover = True
        self.__hover_motif = None
        # motifs["x-3x3"]
        self.__old_hover = None
        self.__old_ids = []
        self.__motif_image = None
        
        self.set_motif_hover()
        
        self.__canvas.bind("<Motion>", self.hover)

        self.__canvas.bind("<Leave>", lambda _: self.__reset_hover())
        self.init_draw()
        
        # def add_motif(event):
        #     x, y = self.event_to_coords(event)
        #     self.__d.add_motif(self.__hover_motif, x, y)
        #     self.refresh()
        # self.__canvas.bind("<Button-1>", add_motif)
        pass
    
    def is_grid_mode(self):
        return self.__mode == ViewMode.GRID
    
    def is_knit_mode(self):
        return self.__mode == ViewMode.KNIT
    
    def set_mode(self, new_mode: ViewMode) -> None:
        if self.__mode != new_mode:
            self.__mode = new_mode
            self._reset()
            self.init_draw()
            pass
        pass
    
    def init_draw(self):
        
        self.__init_design()
        self.__init_grid()
        pass
    
    def _reset(self):
        self._reset_design()
        self._reset_grid()
    
    def _reset_grid(self):
        for id in self.__hor_lines:
            self.__canvas.delete(id)
            pass
        for id in self.__ver_lines:
            self.__canvas.delete(id)
            pass
        pass
    
    
    def refresh_grid(self):
        self._reset_grid()
        self.__init_grid()
    
    def create_knit_horizontal_line(self, y0: int, **kwargs) -> int:
        points = [(0, 0)]
        for i in range(self.width()):
            points.append(((i + 0.5) * self.__pixel_size, 0.5 * self.__pixel_size))
            points.append(((i + 1) * self.__pixel_size, 0))
            pass
        points = [(x, y + y0) for x, y in points]
        
        flat = util.flatten_points(points)
        
        i = self.__canvas.create_line(*flat, **kwargs)
        return i
    
    def __init_grid(self):
        self.__hor_lines = []
        for i in range(self.height() + 1):
            y = i * self.__pixel_size
            match self.__mode:
                case ViewMode.GRID:
                    self.__hor_lines.append(self.__canvas.create_line(0, y, self.pixel_width(), y, fill="#707070", width=self.__line_width))
                    pass
                case ViewMode.KNIT:
                    self.__hor_lines.append(self.create_knit_horizontal_line(y, fill="#707070", width=self.__line_width))
            pass
        self.__ver_lines = []
        for i in range(self.width() + 1):
            x = i * self.__pixel_size
            self.__ver_lines.append(self.__canvas.create_line(x, 0, x, self.pixel_height(), fill="#707070", width=self.__line_width))
                
    
    def _add_old_id(self, id):
        self.__old_ids.append(id)
    
    def __init_design(self):
        self.__rects = []
        for i in range(self.height()):
            rects_row = []
            y0 = i * self.__pixel_size
            for j in range(self.width()):
                c = self.__d.get_rgba(j, i)
                x0 = j * self.__pixel_size
                match self.__mode:
                    case ViewMode.GRID:
                        rects_row.append(self.__canvas.create_rectangle(x0, y0, x0 + self.__pixel_size, y0 + self.__pixel_size, fill=c.hex(), width=0))
                        pass
                    case ViewMode.KNIT:
                        rects_row.append(self.create_knit(x0, y0, needs_multiply=False, fill=c.hex(), width=0))
                        pass
                pass
            self.__rects.append(rects_row)
            pass
        pass
    
    
    
    def create_knit(self, x0: int, y0: int, needs_multiply=True, **kwargs):
        if needs_multiply:
            x0 *= self.__pixel_size
            y0 *= self.__pixel_size
        points = [
            (0, 0),
            (self.__pixel_size * 0.5, self.__pixel_size * 0.5),
            (self.__pixel_size, 0),
            (self.__pixel_size, self.__pixel_size),
            (self.__pixel_size * 0.5, self.__pixel_size * 1.5),
            (0, self.__pixel_size)
        ]
        points = [(x0 + x, y0 + y) for x, y in points]
        flat = util.flatten_points(points)
        
        id = self.__canvas.create_polygon(*flat, **kwargs)
        return id
    
    def _reset_design(self):
        for row in self.__rects:
            for r in self.__rects:
                self.__canvas.delete(r)
                pass
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
        if self._should_reset_hover:
            self._end_hover()
        pass
    
    def _end_hover(self):
        self.__old_hover = None
        self.__remove_old_ids()
    
    def _set_reset_hover(self, b: bool):
        self._should_reset_hover = b
        pass
    
    def event_to_coords(self, event) -> tuple[int, int]:
        if self.__hover_motif:
            simple_x = min(self.width() - self.__hover_motif.width(), event.x // self.__pixel_size)
            simple_y = min(self.height() - self.__hover_motif.height(), event.y // self.__pixel_size)
            pass
        else:
            simple_x = event.x // self.__pixel_size
            simple_y = event.y // self.__pixel_size
        return simple_x, simple_y
    
    def _reset_motion(self):
        self.__canvas.unbind("<Motion>")
        self.__canvas.bind("<Motion>", self.hover)
    
    def set_hover_function(self, c: Callable[[int, int], Any], should_reset_hover: bool = True):
        self._hover_function = c
        self._set_reset_hover(should_reset_hover)
        self._reset_motion()
        pass
    def set_motif_hover(self):
        def motif_hover(simple_x: int, simple_y: int):
            if not self.__hover_motif:
                return
            if not self.__motif_image:
                img = util.rgbcolors_to_image(util.motif_to_lol(self.__hover_motif), square_size = self.__pixel_size, mode="RGBA", opacity=127)
                self.__motif_image = ImageTk.PhotoImage(img)
                pass
            self._add_old_id(self.create_image(simple_x, simple_y, image=self.__motif_image, anchor="nw"))
            self._lower_old_ids()
            pass
        self._hover_function = motif_hover
        self._set_reset_hover(True)
        self._reset_motion()
        pass
    
    def hover(self, event):
        # if not self.__hover_motif:
        #     return
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
        
        self._hover_function(simple_x, simple_y)
        
        
        pass
    
    def _lower_old_ids(self):
        # put all added images below the horizontal lines
        for id in self.__old_ids:
            self.__canvas.tag_lower(id, self.__hor_lines[0])
            pass
        pass
    
    def set_motif(self, m: Motif):
        self.__hover_motif = m
        if m is not None:
            shape = "rect"
            if self.__mode == ViewMode.KNIT:
                shape = [
                    (0, 0),
                    (0.5, 0.5),
                    (1, 0),
                    (1, 1),
                    (0.5, 1.5),
                    (0, 1)
                ]
            img = util.rgbcolors_to_image(util.motif_to_lol(self.__hover_motif), square_size = self.__pixel_size, mode="RGBA", opacity=127, shape=shape)
            self.__motif_image = ImageTk.PhotoImage(img)
            # self.__reset_hover()
            pass
        else:
            self.__motif_image = None
            pass
        self.__reset_hover()
        pass
    
    def get_motif(self) -> Optional[Motif]:
        return self.__hover_motif
        
    def height(self) -> int:
        return self.__d.height()
    
    def width(self) -> int:
        return self.__d.width()
    
    def pixel_height(self) -> int:
        return self.height() * self.__pixel_size
    
    def pixel_width(self) -> int:
        return self.width() * self.__pixel_size
    
    def pixel_size(self) -> int:
        return self.__pixel_size
    
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
    
    def create_image(self, x, y, image=None, anchor="nw", **kwargs) -> int:
        ident = self.__canvas.create_image(x * self.__pixel_size, y * self.__pixel_size, image=image, anchor=anchor, **kwargs)
        return ident
    
    def create_rectangle(self, x0: int, y0: int, x1: int, y1: int, **kwargs):
        x0 *= self.pixel_size()
        x1 *= self.pixel_size()
        y0 *= self.pixel_size()
        y1 *= self.pixel_size()
        id = self.__canvas.create_rectangle(x0, y0, x1, y1, **kwargs)
        return id
    
    def create_pixel(self, x0: int, y0: int, **kwargs):
        id = self.__canvas.create_rectangle(x0, y0, x0 + self.__pixel_size, y0 + self.__pixel_size, width=0, **kwargs)
        if self.__hor_lines:
            self.__canvas.tag_lower(id, self.__hor_lines[0])
            pass
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
        self.__nums.add_verticals()
        self.__add_row(height)
        pass
    
    def add_column(self, width: int) -> None:
        self.__nums.add_horizontals()
        self.__add_column(width)
        pass
    
    def remove_row(self) -> None:
        self.__nums.remove_verticals()
        self.__remove_row()
        pass
    
    def remove_column(self) -> None:
        self.__nums.remove_horizontals()
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
    
