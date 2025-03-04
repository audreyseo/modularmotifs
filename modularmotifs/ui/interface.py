"""User interface that uses Designs to model pixels"""

import tkinter as tk
from tkinter import filedialog
from typing import Any, List, Optional
from collections.abc import Callable
from PIL import ImageTk, Image

# import saved_motifs
from modularmotifs.core.design import Design, MotifOverlapException
from modularmotifs.core import RGBColor
from modularmotifs.core.motif import Motif
from modularmotifs.core.util import motif2png
from modularmotifs.motiflibrary.examples import motifs

from modularmotifs.ui.motif_saver import save_as_motif
from modularmotifs.ui.grid_selection import GridSelection
from modularmotifs.ui.grid_labels import GridLabels

from modularmotifs.dsl import DesignProgramBuilder, DesignInterpreter, parse
from modularmotifs.dsl._syntax import SizeOp, AddColumn, RemoveColumn, AddRow, RemoveRow


from modularmotifs.ui.pixel_window import PixelWindow

import os

# Default grid dimensions
# GRID_HEIGHT: int = 25
# GRID_WIDTH: int = 50
GRID_HEIGHT = 10
GRID_WIDTH = 10

# Maximum dimensions
MAX_HEIGHT: int = 200
MAX_WIDTH: int = 200

TKINTER_OFFSET: int = 1

WINDOW_TITLE: str = "Knitting Canvas"

# Cell size in pixels
CELL_SIZE: int = 20

DEFAULT_MOTIFS: list[Motif] = list(motifs.values())


class KnitWindow(PixelWindow):
    """Main window to fill out a design"""

    def __init__(self, design=None, title=None, save_as_motif: bool = True, program_builder=None) -> None:
        self._design: Design = design or Design(GRID_HEIGHT, GRID_WIDTH)

        super().__init__(MAX_WIDTH, MAX_HEIGHT, TKINTER_OFFSET, title or WINDOW_TITLE, self._design)
        self._selected_motif: Optional[tuple[str, Motif]] = None
        self._selected_motif_button = None


        self._program_builder: DesignProgramBuilder = program_builder or DesignProgramBuilder(self._design)
        self._program_builder.add_modularmotifs_motif_library()
        self._motifs: dict[Motif] = motifs
        self._interpreter: DesignInterpreter = self._program_builder.get_interpreter()

        self._init_pixels()
        self._refresh_pixels()
        self._init_labels()

        self._init_motifs()

        # Color picker for foreground, background, invis
        self._init_colors()

        # History actions: undo and redo
        self._init_history()

        # Add size increment entry
        self._init_sizes()

        # Add grid selection integration here:
        self.__grid_selector = GridSelection(self)
        if save_as_motif:
            save_button = tk.Button(self._controls_frame, text="Save as Motif", command=lambda: save_as_motif(self))
            save_button.pack(side="left", padx=10)
            pass

        # Starts the window
        self._root.mainloop()
        
    def _init_underlying(self, dpb: DesignProgramBuilder, interp: DesignInterpreter):
        self._program_builder = dpb
        self._interpreter = interp
        self._design = interp.design
        self._pixel_grid = self._design
    
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

        def click_color_listener(row: int, col: int):
            def handle(_):
                if self._selected_motif is not None:
                    try:
                        # add an op that builds the motif to the program currently being built
                        op = self._program_builder.add_motif(self._selected_motif[0], col, row)
                        print(op)
                        # interpret the operation, which will have an effect on the design
                        self._interpreter.interpret(op)

                        if self._redo_enabled():
                            self._disable_redo()
                            pass

                        if not self._undo_enabled():
                            self._enable_undo()
                            pass


                        # self._design.add_motif(self._selected_motif, col, row)
                        self._refresh_pixels()
                    except MotifOverlapException:
                        self.error("Placed motif overlaps with something else!")
                        self._program_builder.remove_last_action()
                    except IndexError:
                        self.error("Placed motif would be out of bounds!")
                        self._program_builder.remove_last_action()
                else:
                    self.error("No selected motif!")

            return handle
        super()._init_pixels(click_color_listener)


    def _init_colors(self) -> None:
        """Initializes the color viewer and picker at the bottom"""
        colors: list[RGBColor] = [
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
                bindable.bind("<Button-1>", pick_color)
                pass
            pass
        pass

    def _init_motifs(self) -> None:
        # motifs_frame = tk.Frame(self._root)
        # motifs_frame.pack(side="right", padx=10, fill="y")

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
        # inner_frame.configure(borderwidth=4, relief="raised")

        self._motif_images = []

        def pick_motif_listener(motif_name: str, motif: Motif, motif_button):
            def handle(_):
                if self._selected_motif_button is not None:
                    KnitWindow.deselect(self._selected_motif_button)
                if self._selected_motif == motif:
                    self._selected_motif = None
                    self._selected_motif_button = None
                else:
                    self._selected_motif_button = motif_button
                    self._selected_motif = (motif_name, motif) # motif
                    KnitWindow.select(self._selected_motif_button)

            return handle

        row = 0
        for motif_name, motif in self._program_builder._motifs.items():
            pil_image = motif2png(motif)
            scaling = 150 / pil_image.width
            newwidth = 150
            pil_image = pil_image.resize(
                (newwidth, int(pil_image.height * scaling)),
                resample=Image.NEAREST,
            )
            motif_thumbnail = ImageTk.PhotoImage(pil_image)
            self._motif_images.append(motif_thumbnail)

            motif_label = tk.Label(
                inner_frame, image=motif_thumbnail, borderwidth=1, relief="solid"
            )
            motif_label.pack(pady=5, padx=5)
            # motif_label.grid(row=row, column=0)
            row += 1

            motif_label.bind("<Button-1>", pick_motif_listener(motif_name, motif, motif_label))

            pass
        pass

    def _init_history(self) -> None:
        # initialize buttons that deal with the history manipulation -- i.e., undo, redo

        def handle_size(action):
            w = int(self._width_var.get())
            h = int(self._height_var.get())
            print(action)

            if isinstance(action, AddColumn):
                self._add_column(self.width())
                pass
            elif isinstance(action, AddRow):
                self._add_row(self.height())
                pass
            elif isinstance(action, RemoveColumn):
                self._remove_column(w)
                pass
            elif isinstance(action, RemoveRow):
                self._remove_row(h)

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
