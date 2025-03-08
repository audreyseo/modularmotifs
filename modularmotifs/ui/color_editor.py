import tkinter as tk
import tkinter.ttk as ttk
from tkinter import colorchooser
from tktooltip import ToolTip
import tkinter.font as font

from modularmotifs.core.colorization import PrettierTwoColorRows, Change
from modularmotifs.core.design import Design
from modularmotifs.core.rgb_color import RGBAColor
from modularmotifs.dsl._colorops import ColorizationProgramBuilder
from modularmotifs.motiflibrary.examples import motifs

class ColorEditor:
    
    def __init__(self, pretty: PrettierTwoColorRows):
        self._pretty = pretty
        self._builder = ColorizationProgramBuilder(pretty)
        self._interpreter = self._builder.get_interpreter()
        
        
        
        self._default_button_style = "TButton"
        self._button_style = "custom.TButton"
        self._frame_style = "custom.TFrame"
        
        self._root = tk.Tk()
        self._root.title("Fair Isle Color Editor")
        s = ttk.Style(self._root)
        s.configure("custom.TFrame", padding=5)
        
        # bs = ttk.Style()
        s.configure("custom.TButton", font=('Helvetica', 5), padding=3)
        s.configure("TButton", font=('Helvetica', 10), padding=(0, 3, 0, 3))
        s.configure("updown.TButton", font=('Helvetica', 30), padding=(0, 10, 0, 3))
        
        self._updown_button_style = "updown.TButton"
        self._controls_frame = ttk.Frame(self._root, style=self._frame_style)
        self._controls_frame.grid(row=0, column=0, columnspan=2)
        
        self._colorgrid = ttk.Frame(self._root, style=self._frame_style)
        self._colorgrid.grid(row=1, column=0)
        self._pixels = list()
        
        self._colorframe = ttk.Frame(self._root, style=self._frame_style)
        self._colorframe.grid(row=1, column=1, padx=10)
        
        self.colors = pretty._colors
        
        self._saved_designs = ttk.Frame(self._root, style=self._frame_style)
        self._saved_designs.grid(row=2, column=0, columnspan=2)
        
        self._init_pixels()
        self._refresh_pixels()
        self._init_colors()
        self._init_add_color()
        self._root.mainloop()
        pass
    
    def start_window(self) -> None:
        print("Starting window")
        self._root.mainloop()
        pass
    
    def height(self) -> int:
        return self._pretty.height()
    
    def width(self) -> int:
        return self._pretty.width()
    
    def _init_colors(self):
        canvas = tk.Canvas(self._colorframe)
        canvas.grid(row=0, column=0, stick=tk.N + tk.S + tk.E + tk.W)
        scrollbar = tk.Scrollbar(self._colorframe, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        inner_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(width=200)
        
        def move_color_handler(color_index, up: bool):
            diff = -1 if up else 1
            def handler():
                canvas.grid_remove()
                op = self._builder.swap_colors(color_index, color_index + diff)
                self._interpreter.interpret(op)
                self._init_colors()
                pass
            return handler
        
        ROW = 2
        COLS = 3
        MOVECOL = 2
        REMOVECOL = 1
        for y, c in enumerate(self.colors):
            r, g, b = c.rgb_tuple()
            fontc = int(not round((((r + g + b) / 3.0) / 255)))
            fontccolor = RGBAColor(fontc * 255, fontc * 255, fontc * 255, 255)
            
            colorlabel = tk.Label(inner_frame, bg=c.hex(), foreground=fontccolor.hex(), text=c.hex(), relief="solid", borderwidth=1, font=('Helvetica', 20))
            colorlabel.grid(row=y * ROW, column=0, rowspan=ROW, sticky=tk.N + tk.E + tk.S + tk.W)
            moveup = ttk.Button(inner_frame, text="⬆️", command=move_color_handler(y, up=True), state="normal" if y != 0 else "disabled", style=self._updown_button_style)
            moveup.grid(row=y * ROW, column=MOVECOL)
            movedown = ttk.Button(inner_frame, text="⬇️", command=move_color_handler(y, up=False), state="normal" if y < len(self.colors) - 1 else "disabled", style=self._updown_button_style)
            movedown.grid(row=y * ROW + 1, column=MOVECOL)
            remove = ttk.Button(inner_frame, text="-")
            remove.grid(row=y * ROW, column=REMOVECOL, rowspan=ROW)
            pass
        
        pass
            
    def _init_add_color(self):
        def pick_color_callback():
            def callback():
                color_code = colorchooser.askcolor(color=(255, 255, 255), title =f"Choose a new color")
                if isinstance(color_code, tuple) and color_code:
                    if not color_code[0]:
                        return
                    pass
                print(color_code)
                c = RGBAColor.from_hex(color_code[1])
                print(type(color_code))
                
                op = self._builder.add_color(c)
                self._interpreter.interpret(op)
                
                self._init_colors()
                pass
            return callback
        add_color_button = ttk.Button(self._controls_frame, text="Add Color", command=pick_color_callback(), style=self._default_button_style)
        add_color_button.grid(row=0, column=5)
    
    def _init_pixels(self):
        for row in range(self.height()):
            row_cells = []
            for col in range(self.width()):
                cell = tk.Label(
                    self._colorgrid,
                    width=2,
                    height=1,
                    relief="solid",
                    borderwidth=1
                )
                cell.grid(row=row, column=col, padx=0, pady=0, sticky=tk.N + tk.S)
                row_cells.append(cell)
                pass
            self._pixels.append(row_cells)
            pass
        
        col = self.width()
        for row in range(self.height()):
            button = ttk.Button(self._colorgrid, text="+", style=self._button_style, padding=0)
            button.grid(row=row, column=col, padx=0, pady=0)
        pass
    
    def _refresh_pixels(self) -> None:
        for y, row in enumerate(self._pixels):
            for x, pixel in enumerate(row):
                pixel.config(bg=self._pretty.get_color(x, y).hex())
                pass
            pass
        pass
    pass

if __name__ == "__main__":
    design = Design(9, 9)
    for i in [0, 3, 6]:
        for j in [0, 3, 6]:
            design.add_motif(motifs["x-3x3"], i, j)
            pass
        pass
    colors = [RGBAColor.from_hex("#320E3B"),
              RGBAColor.from_hex("#E56399"),
              RGBAColor.from_hex("#7F96FF"),
              RGBAColor.from_hex("#A6CFD5"),
              RGBAColor.from_hex("#DBFCFF")]
    
    changes = [Change.from_ints(2, 1, 1),
               Change.from_ints(5, 3, 1),
               Change.from_ints(8, 4, 1)]
    pretty = PrettierTwoColorRows(design, colors, changes)
    
    ColorEditor(pretty)
    
    # editor.start_window()