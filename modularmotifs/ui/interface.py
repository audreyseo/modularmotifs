"""User interface that uses Designs to model pixels"""

import tkinter as tk
from tkinter import Image, filedialog
from tkinter import colorchooser
from tktooltip import ToolTip
from typing import Any, List, Optional
from collections.abc import Callable
# import numpy as np

from PIL import ImageTk, Image

# import saved_motifs
from modularmotifs.core.design import Design, MotifOverlapException
from modularmotifs.core import RGBAColor
from modularmotifs.core.motif import Motif
from modularmotifs.core.util import motif2png
from modularmotifs.motiflibrary.examples import motifs, int_lol_to_motif
from modularmotifs.motiflibrary.saved_motifs import saved_motifs
from modularmotifs.handknit.generate import handknitting_instructions


from modularmotifs.ui.motif_saver import save_as_motif
from modularmotifs.ui.grid_selection import GridSelection
from modularmotifs.ui.grid_labels import GridLabels

from modularmotifs.dsl import DesignProgramBuilder, DesignInterpreter, parse
from modularmotifs.dsl._syntax import SizeOp, AddColumn, RemoveColumn, AddRow, RemoveRow, Literal


from modularmotifs.ui.pixel_canvas import PixelCanvas
from modularmotifs.ui.pixel_window import PixelWindow

import os

from modularmotifs.ui.viz.viz import export_heart, show_design

# Default grid dimensions
# GRID_HEIGHT: int = 25
# GRID_WIDTH: int = 50
GRID_HEIGHT = 30
GRID_WIDTH = 30

# Maximum dimensions
MAX_HEIGHT: int = 200
MAX_WIDTH: int = 200

TKINTER_OFFSET: int = 1

WINDOW_TITLE: str = "Knitting Canvas"

# Cell size in pixels
CELL_SIZE: int = 20

DEFAULT_MOTIFS: list[Motif] = list(motifs.values())

def trim_empty_rows_both(motif_data: list[list[int]]) -> list[list[int]]:
    """
    Remove any rows at the top or bottom that are entirely 'invisible' (all values equal to 3).
    """
    if not motif_data:
        return motif_data
    first = None
    last = None
    for i, row in enumerate(motif_data):
        if any(val != 3 for val in row):
            if first is None:
                first = i
            last = i
    if first is None:
        return []  # All rows are empty
    return motif_data[first:last+1]


def trim_empty_columns_both(motif_data: list[list[int]]) -> list[list[int]]:
    """
    Remove any columns at the left or right that are entirely 'invisible' (all values equal to 3).
    """
    if not motif_data or not motif_data[0]:
        return motif_data
    first = None
    last = None
    num_cols = len(motif_data[0])
    for j in range(num_cols):
        if any(row[j] != 3 for row in motif_data):
            if first is None:
                first = j
            last = j
    if first is None:
        return motif_data
    return [row[first:last+1] for row in motif_data]


def clean_motif_data(motif_data: list[list[int]]) -> list[list[int]]:
    """
    Cleans the motif data by trimming any leading and trailing rows and columns that are entirely invisible.
    """
    data = trim_empty_rows_both(motif_data)
    data = trim_empty_columns_both(data)
    return data


class KnitWindow(PixelWindow):
    """Main window to fill out a design"""


    def __init__(self, design=None, title=None, save_motif: bool = True, program_builder=None) -> None:
        self._motif_images = []
        self._design: Design = design or Design(GRID_HEIGHT, GRID_WIDTH)

        super().__init__(MAX_WIDTH, MAX_HEIGHT, TKINTER_OFFSET, title or WINDOW_TITLE, self._design)
        self._selected_motif: Optional[tuple[str, Motif]] = None
        self._selected_motif_button = None


        self._program_builder: DesignProgramBuilder = program_builder or DesignProgramBuilder(self._design)
        self._program_builder.add_modularmotifs_motif_library()

        # --- New code: Load saved motifs into the design program builder ---
        # For each saved motif, clean and convert it, then register it as a DSL literal.
        for saved_name, saved_data in saved_motifs.items():
            cleaned_data = clean_motif_data(saved_data)
            motif_obj = int_lol_to_motif(cleaned_data)
            # Wrap the motif in a Literal so that the DSL interpreter can evaluate it.
            # TODO: FIX, this is incorrect -- this should be an ObjectInit at the very least, not a Literal!
            self._program_builder._motif_name_to_expr[saved_name] = Literal(motif_obj)
        # ---------------------------------------------------------------------

        self._motifs: dict[Motif] = motifs
        self._interpreter: DesignInterpreter = self._program_builder.get_interpreter()

        self._init_pixels()
        self._refresh_pixels()
        # self._init_labels()

        self._init_motifs()

        # Color picker for foreground, background, invis
        self._init_colors()

        # History actions: undo and redo
        self._init_history()

        # Add size increment entry
        self._init_sizes()
        self._init_tools()

        # Add grid selection integration here:
        self.__grid_selector = GridSelection(self)
        if save_motif:
            save_button = tk.Button(self._controls_frame, text="Save as Motif", command=lambda: save_as_motif(self))
            save_button.pack(side="left", padx=10)
            pass

        view_button = tk.Button(self._controls_frame, text="View knitted object", command=lambda: self.show())
        view_button.pack(side="left", padx=10)

        # Starts the window
        self._root.mainloop()


    def _populate_motif_buttons(self, parent_frame):
        """Populate the motif buttons inside the given frame without affecting the window location."""
        def pick_motif_listener(motif_name: str, motif: Motif, motif_button):
            def handle(_):
                if self._selected_motif_button is not None:
                    KnitWindow.deselect(self._selected_motif_button)
                if self._selected_motif == motif:
                    self._selected_motif = None
                    self._selected_motif_button = None
                else:
                    self._selected_motif_button = motif_button
                    self._selected_motif = (motif_name, motif)
                    KnitWindow.select(self._selected_motif_button)
            return handle

        merged_motifs = self._program_builder._motifs.copy()

        for motif_name, motif_data in merged_motifs.items():
            if isinstance(motif_data, list):
                cleaned_data = clean_motif_data(motif_data)
                motif_obj = int_lol_to_motif(cleaned_data)
            else:
                motif_obj = motif_data

            pil_image = motif2png(motif_obj)
            scaling = 150 // pil_image.width
            pil_image = pil_image.resize((pil_image.width * scaling, pil_image.height * scaling), resample=Image.NEAREST)
            motif_thumbnail = ImageTk.PhotoImage(pil_image)
            self._motif_images.append(motif_thumbnail)

            motif_label = tk.Label(parent_frame, image=motif_thumbnail, borderwidth=1, relief="solid")
            motif_label.pack(pady=5, padx=5)
            motif_label.bind("<Button-1>", pick_motif_listener(motif_name, motif_obj, motif_label))


    def show(self) -> None:
        """Shows the knitted object in a new window"""
        show_design(self._design)
        pass
    
    def _init_handknit_output(self) -> Callable:
        def handler():
            f = filedialog.asksaveasfile(mode="wb", defaultextension=".png")
            if f is None:
                print("Handknit output aborted")
                return
            filename = os.path.abspath(str(f.name))
            print(filename)
            img = handknitting_instructions(self._design, cell_size=40, thicker=4, thinner=2)
            img.save(f)
            f.close()
            pass
        return handler

    def _init_underlying(self, dpb: DesignProgramBuilder, interp: DesignInterpreter):
        self._program_builder = dpb
        self._interpreter = interp
        self._design = interp.design
        self._pixel_grid = self._design
        self._pixel_canvas.get_toplevel().pack_forget()
        self._pixel_canvas = PixelCanvas(self._lower_frame, self._pixel_grid, pixel_size=20, line_width=1.5)
        self._pixel_canvas.get_toplevel().pack(side="left", padx=10, pady=10, fill="both", expand=True)
    

    def _init_save(self) -> Callable:
        def save_handler(e):
            if not self._current_file_name:
                # need to save-as
                f = filedialog.asksaveasfile(mode='w', defaultextension='.py')
                self._current_file_name = os.path.abspath(str(f.name))
                print(self._current_file_name)
                if f is None:
                    return
                f.write(self._program_builder.to_python())
                f.close()
                pass
            else:
                with open(self._current_file_name, "w") as f:
                    f.write(self._program_builder.to_python())
                    pass
                pass
            pass
        return save_handler


    def _adjust_width_height(self):
        w = int(self._width_var.get())
        h = int(self._height_var.get())

        if w < self.width():
            while w < self.width():
                self._add_column(at_index=w)
                w += 1
                pass
            pass
        else:
            while w > self.width():
                self._remove_column(at_index=w)
                w -= 1
                pass
            pass

        if h < self.height():
            while h < self.height():
                self._add_row(at_index=h)
                h += 1
                pass
            pass
        else:
            while h > self.height():
                self._remove_row(at_index=h)
                h -= 1
                pass
            pass


        self._width_var.set(str(self.width()))
        self._height_var.set(str(self.height()))


    def _init_open(self) -> Callable:
        def open_handler(e):
            ftypes = [('Python files', '*.py'), ('All files', '*')]
            f = filedialog.askopenfile(mode='r', filetypes=ftypes)
            text = f.read()
            if not self._current_file_name:
                self._current_file_name = os.path.abspath(str(f.name))
                pass
            f.close()

            # TODO: Actually open the file
            print("Opened file:")
            print(text)

            try:
                dpb, interp = parse(text)
                self._init_underlying(dpb, interp)
                # self._program_builder = dpb
                # print(dpb.to_python())
                # self._intepreter = interp
                # self._design = interp.design
                # self._pixel_grid = self._design

                # add rows and columns
                self._adjust_width_height()

                # now refresh the display
                self._refresh_pixels()
                pass
            except Exception as e:
                print(e)
                pass
            pass
        return open_handler



    def _init_pixels(self) -> None:
        """Initializes the array of visible pixels from the
        current design's dimensions. Does not set colors"""
        
        def add_motif(event):
            if self._selected_motif is not None:
                try:
                    x, y = self._pixel_canvas.event_to_coords(event)
                    op = self._program_builder.add_motif(self._selected_motif[0], x, y)
                    print(op)
                    self._interpreter.interpret(op)
                    if self._redo_enabled():
                        self._disable_redo()
                        pass
                    
                    if not self._undo_enabled():
                        self._enable_undo()
                        pass
                    self._refresh_pixels()
                    pass
                except MotifOverlapException:
                    self.error("Placed motif overlaps with something else!")
                    self._program_builder.remove_last_action()
                    pass
                except IndexError:
                    self.error("Placed motif would be out of bounds!")
                    self._program_builder.remove_last_action()
                    pass
                pass
            else:
                self.error("No selected motif!")
                pass
            pass
        self._pixel_canvas.get_canvas().bind("<Button-1>", add_motif)
                

        # def click_color_listener(row: int, col: int):
        #     def handle(_):
        #         if self._selected_motif is not None:
        #             try:
        #                 # add an op that builds the motif to the program currently being built
        #                 op = self._program_builder.add_motif(self._selected_motif[0], col, row)
        #                 print(op)
        #                 # interpret the operation, which will have an effect on the design
        #                 self._interpreter.interpret(op)

        #                 if self._redo_enabled():
        #                     self._disable_redo()
        #                     pass

        #                 if not self._undo_enabled():
        #                     self._enable_undo()
        #                     pass


        #                 # self._design.add_motif(self._selected_motif, col, row)
        #                 self._refresh_pixels()
        #             except MotifOverlapException:
        #                 self.error("Placed motif overlaps with something else!")
        #                 self._program_builder.remove_last_action()
        #             except IndexError:
        #                 self.error("Placed motif would be out of bounds!")
        #                 self._program_builder.remove_last_action()
        #         else:
        #             self.error("No selected motif!")

        #     return handle
        # super()._init_pixels(click_color_listener)


    def _init_colors(self) -> None:
        
        def pick_color_callback(color: RGBAColor, name: str, frame_color_label: tuple):
            frame, color_button, name_label = frame_color_label
            def callback(event):
                print(f"You clicked {name} {color.hex()}")
                color_code = colorchooser.askcolor(color=color.rgb_tuple(), title =f"Choose {name} color")
                if isinstance(color_code, tuple) and color_code:
                    if not color_code[0]:
                        return
                    pass
                print(color_code)
                c = RGBAColor.from_hex(color_code[1])
                color_button.configure(bg=color_code[1])
                print(type(color_code))
                for bindable in frame_color_label:
                    bindable.bind("<Button-1>", pick_color_callback(c, name, frame_color_label))
                    pass
                match name:
                    case "Fore":
                        self._design.set_fore_color(c)
                        pass
                    case "Back":
                        self._design.set_back_color(c)
                        pass
                    case "Invis":
                        self._design.set_invis_color(c)
                        pass
                self._refresh_pixels()
                pass
            return callback
        
        """Initializes the color viewer and picker at the bottom"""
        colors: list[RGBAColor] = [
            self._design.fore_color,
            self._design.back_color,
            self._design.invis_color,
        ]
        buttons = super()._init_colors(colors)


        for color, name, parts in buttons:
            # TODO: make this functional. Pull up a color picker, set the color in Design,
            # refresh the view
            def pick_color(_, color=color, name=name):
                print(f"You clicked {name} {color.hex()}!")
                pass
            for bindable in parts:
                bindable.bind("<Button-1>", pick_color_callback(color, name, parts))
                pass
            pass
        pass

    def _init_motifs(self) -> None:
        """Initialize the motif selection panel."""
        # self._motifs_frame = tk.Frame(self._root)
        # self._motifs_frame.pack(side="right", padx=10, fill="y")

        # self._motif_canvas = tk.Canvas(self._motifs_frame)
        # self._motif_canvas.pack(side="left", fill="both", expand=True)

        # scrollbar = tk.Scrollbar(self._motifs_frame, orient="vertical", command=self._motif_canvas.yview)
        # scrollbar.pack(side="right", fill="y")
        # self._motif_canvas.configure(yscrollcommand=scrollbar.set)

        # self._motif_inner_frame = tk.Frame(self._motif_canvas)
        # self._motif_canvas.create_window((0, 0), window=self._motif_inner_frame, anchor="nw")

        # # Populate motif buttons using the new helper method.
        # self._populate_motif_buttons(self._motif_inner_frame)

        # self._motif_inner_frame.bind("<Configure>", lambda event: self._motif_canvas.configure(scrollregion=self._motif_canvas.bbox("all")))
        canvas = tk.Canvas(self._library_frame)
        
        # canvas.pack(side="left", fill="y")
        canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        # canvas.configure(borderwidth=3, relief="raised")

        scrollbar = tk.Scrollbar(self._library_frame, orient="vertical", command=canvas.yview)
        # scrollbar.pack(side="left", fill="y")
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        # scrollbar.configure(borderwidth=4, relief="raised")
        canvas.configure(yscrollcommand=scrollbar.set)
        print(canvas.grid_info())
        print(scrollbar.grid_info())

        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        inner_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.configure(width=160)


        def pick_motif_listener(motif_name: str, motif: Motif, motif_button):
            def handle(_):
                if self._selected_motif_button is not None:
                    KnitWindow.deselect(self._selected_motif_button)
                if self._selected_motif == motif:
                    print("Deselecting motif")
                    self._pixel_canvas.set_motif(None)
                    self._selected_motif = None
                    self._selected_motif_button = None
                else:
                    print("Selecting Motif")
                    self._selected_motif_button = motif_button
                    self._selected_motif = (motif_name, motif) # motif
                    self._pixel_canvas.set_motif(motif)
                    KnitWindow.select(self._selected_motif_button)

            return handle

        # Merge predefined motifs with saved motifs.
        merged_motifs = self._program_builder._motifs.copy()

        for motif_name, motif_data in merged_motifs.items():
            if isinstance(motif_data, list):
                cleaned_data = clean_motif_data(motif_data)
                motif_obj = int_lol_to_motif(cleaned_data)
            else:
                motif_obj = motif_data
            pil_image = motif2png(motif_obj)
            scaling = 150 // pil_image.width
            pil_image = pil_image.resize((pil_image.width * scaling, pil_image.height * scaling), resample=Image.NEAREST)
            motif_thumbnail = ImageTk.PhotoImage(pil_image)
            self._motif_images.append(motif_thumbnail)

            motif_label = tk.Label(inner_frame, image=motif_thumbnail, borderwidth=1, relief="solid")

            motif_label.pack(pady=5, padx=5)
            ToolTip(motif_label, msg=motif_name, delay=1.0)
            # motif_label.grid(row=row, column=0)
            # row += 1

            motif_label.bind("<Button-1>", pick_motif_listener(motif_name, motif_obj, motif_label))

            pass
        pass

    def _refresh_motif_library(self):
        """Refresh the motif library to include newly saved motifs without changing window location."""
        from importlib import reload
        import modularmotifs.motiflibrary.saved_motifs as saved_motifs_module
        reload(saved_motifs_module)
        new_saved_motifs = saved_motifs_module.saved_motifs

        # Update the motif dictionary
        self._program_builder._motifs.update(new_saved_motifs)

        # *** NEW CODE: Update the DSL mapping for saved motifs ***
        for saved_name, saved_data in new_saved_motifs.items():
            cleaned_data = clean_motif_data(saved_data)
            motif_obj = int_lol_to_motif(cleaned_data)
            self._program_builder._motif_name_to_expr[saved_name] = Literal(motif_obj)
        # *** End of new code ***

        # Find the canvas inside the motifs frame and its inner frame
        for widget in self._motifs_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                canvas = widget
                break
        else:
            return  # Exit if no canvas found

        inner_frame = canvas.winfo_children()[0]

        # Remove existing motif labels
        for widget in inner_frame.winfo_children():
            widget.destroy()

        # Clear selected motif references
        self._selected_motif = None
        self._selected_motif_button = None

        # Re-add motif buttons using the helper method
        self._populate_motif_buttons(inner_frame)



    def _init_history(self) -> None:
        # initialize buttons that deal with the history manipulation -- i.e., undo, redo

        def handle_size(action):
            w = int(self._width_var.get())
            h = int(self._height_var.get())
            print(action)

            if isinstance(action, AddColumn):
                self._add_column(self.width() - 1)
                pass
            elif isinstance(action, AddRow):
                self._add_row(self.height() - 1)
                pass
            elif isinstance(action, RemoveColumn):
                self._remove_column(w)
                pass
            elif isinstance(action, RemoveRow):
                self._remove_row(h)
            self._pixel_canvas.refresh()
            self._width_var.set(str(self.width()))
            self._height_var.set(str(self.height()))

        def undo_listener():
            def handle():
                undo_action = self._program_builder.undo()
                if undo_action:
                    self._interpreter.interpret(undo_action)
                    if isinstance(undo_action, SizeOp):
                        handle_size(undo_action)
                        pass
                    if not self._program_builder.can_undo():
                        self._disable_undo()
                        pass
                    self._enable_redo()
                    self._refresh_pixels()
                    pass
                pass
            return handle

        def redo_listener():
            def handle():
                redo_action = self._program_builder.redo()
                if redo_action:
                    self._interpreter.interpret(redo_action)
                    if isinstance(redo_action, SizeOp):
                        handle_size(redo_action)
                    if not self._program_builder.can_redo():
                        self._disable_redo()
                        pass
                    self._enable_undo()
                    self._refresh_pixels()
                    pass
                pass
            return handle

        super()._init_history(undo_listener, redo_listener)
        pass

    def _init_sizes(self) -> None:
        sizes_frame = tk.Frame(self._controls_frame)
        sizes_frame.pack(side="left", padx=10, fill="y")

        height_var = tk.StringVar()
        height_var.set(str(self.height()))

        width_var = tk.StringVar()
        width_var.set(str(self.width()))


        width_frame = tk.Frame(sizes_frame)
        width_frame.pack(side="left", padx=10)

        height_frame = tk.Frame(sizes_frame)
        height_frame.pack(side="left")

        def refresher():
            if self._redo_enabled():
                self._disable_redo()
                pass
            if not self._undo_enabled():
                self._enable_undo()
                pass
            self._pixel_canvas.refresh()
            self._refresh_pixels()
            pass

        def height_handler():
            print("Height: " + self._height_var.get())
            h = int(self._height_var.get())
            dheight = self.height()
            if h < self.height():
                for i in range(dheight - 1, h-1, -1):
                    op = self._program_builder.remove_row(i)
                    self._interpreter.interpret(op)
                    # self._design.remove_row()
                    self._remove_row(i,
                                    remove_labels=self.height() == dheight - 1,
                                    add_labels=h == self.height())
                    pass
                pass
            elif h > dheight:
                for i in range(dheight, h):
                    # self._design.add_row()
                    op = self._program_builder.add_row()
                    self._interpreter.interpret(op)
                    self._add_row(i,
                                remove_labels=self.height() == dheight + 1, add_labels=h == self.height())
                    pass
                pass
            if h < dheight or h > dheight:
                refresher()
                pass
            pass

        def width_handler():
            print("Width: " + self._width_var.get())
            w = int(self._width_var.get())
            dwidth = self._design.width()
            if w < dwidth:
                for i in range(dwidth - 1, w-1, -1):
                    # self._design.remove_column()
                    op = self._program_builder.remove_column(i)
                    print(op)
                    self._interpreter.interpret(op)
                    self._remove_column(i,
                                            remove_labels=self.width() == dwidth - 1,
                                            add_labels=w == self.width())
                pass
            elif w > dwidth:
                for i in range(dwidth, w):
                    # self._design.add_column()
                    op = self._program_builder.add_column()
                    print(op)
                    self._interpreter.interpret(op)
                    self._add_column(i, remove_labels=self.width() == dwidth + 1, add_labels=w== self.width())
                    pass
                pass
            if w < dwidth or w > dwidth:
                refresher()
                pass
            pass
        hlabel = tk.Label(height_frame, text="Height")
        hspinbox = tk.Spinbox(height_frame, from_=1, to=MAX_HEIGHT, width=3, textvariable=height_var, command=height_handler)
        hlabel.pack(side="left")
        hspinbox.pack(side="left")

        wlabel = tk.Label(width_frame, text="Width")
        wspinbox = tk.Spinbox(width_frame, from_=1, to=MAX_WIDTH, width=3, textvariable=width_var, command=width_handler)
        wlabel.pack(side="left")
        wspinbox.pack(side="left")

        def height_entry_handler(e):
            self._root.focus()
            height_handler()

        def width_entry_handler(e):
            self._root.focus()
            width_handler()



        hspinbox.bind("<Return>", height_entry_handler)
        wspinbox.bind("<Return>", width_entry_handler)

        self._height_var = height_var
        self._width_var = width_var

        # self._height_handler = height_handler
        # self._weight_handler = weight_handler

        pass
