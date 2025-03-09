import os
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from tkinter import colorchooser
from tktooltip import ToolTip
import tkinter.font as font

from modularmotifs.core.colorization import PrettierTwoColorRows, Change
from modularmotifs.core.design import Design
from modularmotifs.core.rgb_color import RGBAColor
from modularmotifs.dsl._colorops import ColorOp, ColorizationProgramBuilder
from modularmotifs.motiflibrary.examples import motifs
from modularmotifs.ui.modes.color_editor_button_modes import ChangeButtonState
from modularmotifs.core.algo.fair_isle import fair_isle_colorization_new, generate_changes
from modularmotifs.handknit.generate import handknitting_instructions
import sys

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
        s.configure("updown.TButton", font=('Helvetica', 10), padding=(0, 6, 0, 3))
        
        
        self._updown_button_style = "updown.TButton"
        self._controls_frame = ttk.Frame(self._root, style=self._frame_style)
        self._controls_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W + tk.E)
        
        self._colorgrid = ttk.Frame(self._root, style=self._frame_style)
        self._colorgrid.grid(row=1, column=0, padx=20)
        self._pixels = list()
        
        self._colorframe = ttk.Frame(self._root, style=self._frame_style)
        self._colorframe.grid(row=1, column=1, padx=10)
        
        self.colors = pretty._colors
        
        self._saved_designs = ttk.Frame(self._root, style=self._frame_style)
        self._saved_designs.grid(row=2, column=0, columnspan=2)
        self._init_fair_isle()
        self._init_pixels()
        self._init_keyboard_shortcuts()
        self._refresh_pixels()
        self._init_colors()
        self._init_add_color()
        self._init_history()
        self._init_save()
        # self._root.mainloop()
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
                self._pretty.recalculate()
                self._refresh_pixels()
                pass
            return handler
        
        def remove_color_handler(color_index: int):
            def handler():
                canvas.grid_remove()
                self._do_action(self._builder.remove_color(color_index))
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
            remove = ttk.Button(inner_frame, text="-", command=remove_color_handler(y))
            remove.grid(row=y * ROW, column=REMOVECOL, rowspan=ROW)
            pass
        
        pass
    
    def _init_fair_isle(self):
        def fair_isle_handler():
            def handler():
                self._pretty.reset()
                fair_isle_colorization_new(self._pretty)
                self._refresh_pixels()
                pass
            return handler
        
        reset_constraints_button = ttk.Button(self._controls_frame, text="Reset Row Constraints", style=self._default_button_style)
        reset_constraints_button.grid(row=0, column=3, padx=10)
        
        fair_isle_button = ttk.Button(self._controls_frame, text="Generate Fair Isle", style=self._default_button_style, command=fair_isle_handler())
        fair_isle_button.grid(row=0, column=4, sticky=tk.E + tk.W, columnspan=2, padx=10)
            
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
                
                self._do_action(self._builder.add_color(c))
                # op = self._builder.add_color(c)
                # self._interpreter.interpret(op)
                
                self._init_colors()
                pass
            return callback
        add_color_button = ttk.Button(self._controls_frame, text="Add Color", command=pick_color_callback(), style=self._default_button_style)
        add_color_button.grid(row=0, column=6, sticky=tk.E)
        # print(add_color_button.configure().keys())
    
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
        
        def button_callback(row: int, s: ChangeButtonState):
            def handler():
                c = ChangeButtonState.toggle(s.change())
                self._do_action(self._builder.set_changes(c, row))
                # s._update_string()
                pass
            return handler

        self._change_button_states = []
        col = self.width()
        for row in range(self.height()):
            buttonstring = tk.StringVar()
            state = ChangeButtonState(buttonstring, row, self._pretty)
            self._change_button_states.append(state)
            button = ttk.Button(self._colorgrid, textvariable=buttonstring, style=self._button_style, padding=0, command=button_callback(row, state))
            button.grid(row=row, column=col, padx=0, pady=0)
        pass
    
    def _init_keyboard_shortcuts(self):
        # set up saving keyboard shortcut
        is_mac = sys.platform == 'darwin'
        
        # Common metakeys
        self._key_names = {
            "Alt": "Option" if is_mac else "Alt",
            "Ctrl": "Control",
            "Meta": "Command" if is_mac else "Meta",
            "Shift": "Shift"
        }
        
        self.command_ctrl = self._key_names["Meta"] if is_mac else self._key_names["Ctrl"]
        
    
    def _do_action(self, op: ColorOp):
        print(op)
        self._interpreter.interpret(op)
        self._update_history()
        self._refresh_pixels()
        self._init_colors()
    
    def _refresh_pixels(self) -> None:
        for y, row in enumerate(self._pixels):
            for x, pixel in enumerate(row):
                pixel.config(bg=self._pretty.get_color(x, y).hex())
                pass
            pass
        
        for y, s in enumerate(self._change_button_states):
            # print(y)
            s._update_string()
        pass
    
    def _update_history(self) -> None:
        if self._builder.can_undo():
            self._undo_button["state"] = "normal"
        else:
            self._undo_button["state"] = "disabled"
            pass
        
        if self._builder.can_redo():
            self._redo_button["state"] = "normal"
        else:
            self._redo_button["state"] = "disabled"
            pass
        pass
    
    def _undo(self) -> None:
        if self._builder.can_undo():
            self._do_action(self._builder.undo())
            pass
        pass
    
    def _redo(self) -> None:
        if self._builder.can_redo():
            self._do_action(self._builder.redo())
            pass
        pass
            
    
    def _init_history(self) -> None:
        
        
        self._undo_button = ttk.Button(self._controls_frame, text="Undo", style=self._default_button_style, state="disabled", command=self._undo)
        self._redo_button = ttk.Button(self._controls_frame, text="Redo", style=self._default_button_style, state="disabled", command=self._redo)
        
        self._undo_button.grid(row=0, column=0, padx=5, sticky=tk.W)
        self._redo_button.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        shift = self._key_names["Shift"]
        ctrl = self._key_names["Ctrl"]
        self._root.bind(f"<{self.command_ctrl}-z>", lambda e: self._undo())
        self._root.bind(f"<{self.command_ctrl}-y>", lambda e: self._redo())
        pass
    
    def _init_save(self) -> None:
        def save():
            f = filedialog.asksaveasfile(mode="wb", defaultextension=".png")
            filename = os.path.abspath(str(f.name))
            print(filename)
            if f is None:
                return
            img = handknitting_instructions(self._pretty, cell_size=40, thicker=4, thinner=2)
            img.save(f)
            f.close()
            pass
            
        
        self._save_button = ttk.Button(self._controls_frame, text="Save Image", style=self._default_button_style, command=save)
        self._save_button.grid(row=0, column=7, padx=5, sticky=tk.E)
        
        self._root.bind(f"<{self.command_ctrl}-s>", lambda e: save())
        
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
    
    # changes = [Change.from_ints(row, 1, 1) for row in range(9)]
    changes = generate_changes(design)
    
    # changes = [Change.from_ints(2, 1, 1),
    #            Change.from_ints(5, 3, 1),
    #            Change.from_ints(8, 4, 1)]
    pretty = PrettierTwoColorRows(design, colors, changes)
    
    editor = ColorEditor(pretty)
    
    editor.start_window()