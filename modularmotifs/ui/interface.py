"""User interface that uses Designs to model pixels"""

import tkinter as tk
from typing import Any, List, Optional
from PIL import ImageTk, Image

from modularmotifs.core.design import Design, MotifOverlapException
from modularmotifs.core import RGBColor
from modularmotifs.core.motif import Motif
from modularmotifs.core.util import motif2png
from modularmotifs.motiflibrary.examples import motifs

from modularmotifs.ui.grid_selection import GridSelection
from modularmotifs.ui.grid_labels import GridLabels

from modularmotifs.dsl import DesignProgramBuilder, DesignInterpreter
from modularmotifs.dsl._syntax import SizeOp, AddColumn, RemoveColumn, AddRow, RemoveRow

from modularmotifs.ui.pixel_window import PixelWindow

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

    def __init__(self) -> None:
        self.__design: Design = Design(GRID_HEIGHT, GRID_WIDTH)

        super().__init__(MAX_WIDTH, MAX_HEIGHT, TKINTER_OFFSET, WINDOW_TITLE, self.__design)
        self._selected_motif: Optional[tuple[str, Motif]] = None
        self._selected_motif_button = None
        self._GLOBAL_GRID = [[None for _ in range(MAX_WIDTH + TKINTER_OFFSET * 2)] for _ in range(MAX_HEIGHT + TKINTER_OFFSET * 2)]

        self._program_builder: DesignProgramBuilder = DesignProgramBuilder(self.__design)
        self._program_builder.add_modularmotifs_motif_library()
        self._motifs: dict[Motif] = motifs
        self._interpreter: DesignInterpreter = self._program_builder.get_interpreter()

        # self._root = tk.Tk()
        # self._root.title(WINDOW_TITLE)

        # self._pixel_frame = tk.Frame(self._root)
        # self._pixel_frame.pack()

        # self._cells: List[List[Any]] = []
        # self._grid_labels = GridLabels()
        

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
        grid_selector = GridSelection(self)


        # Starts the window
        self._root.mainloop()

    def width(self) -> int:
        """Getter

        Returns:
            int: width of the stored design
        """
        return self.__design.width()

    def height(self) -> int:
        """Getter

        Returns:
            int: height of the stored design
        """
        return self.__design.height()

    # @staticmethod
    def grid(self, griddable, row: int, col: int):
        """Calls tkinter's grid with a positive offset so
        we can use negative indices

        Args:
            griddable: Something in tkinter with the .grid method
            row (int): Logical row index
            col (int): Logical column index
        """
        r = row + TKINTER_OFFSET
        c = col + TKINTER_OFFSET
        # if self._GLOBAL_GRID[r][c] is not None and self._GLOBAL_GRID[r][c] != griddable:
        #     self._GLOBAL_GRID[r][c].grid_remove()
        #     pass
        griddable.grid(row=r, column=c)
        self._GLOBAL_GRID[r][c] = griddable
        

    @staticmethod
    def deselect(configable) -> None:
        """For some tkinter element that has the .config
        method, make the border not-thick

        Args:
            configable: Something with the .config method
        """
        configable.config(borderwidth=1, relief="solid")

    @staticmethod
    def select(configable) -> None:
        """For some tkinter element that has the .config
        method, make the border thick

        Args:
            configable: Something with the .config method
        """
        configable.config(borderwidth=3, relief="ridge")

    def error(self, message: str) -> None:
        """Raises an error message to the user

        Args:
            message (str): Message to be sent
        """
        # TODO: make this visual, not console output.
        print(message)

    def _refresh_pixels(self) -> None:
        """Queries the Design for new colors and displays them"""
        for y, row in enumerate(self._cells):
            for x, cell in enumerate(row):
                if self.__design.in_range(x, y):
                    cell.config(bg=self.__design.get_rgb(x, y).hex())
                    pass
                pass
            pass
        pass
    
                
                

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

                        
                        # self.__design.add_motif(self._selected_motif, col, row)
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
        # for row in range(MAX_HEIGHT):
        #     row_cells = []
        #     for col in range(MAX_WIDTH):
        #         cell = tk.Label(
        #             self._pixel_frame,
        #             width=2,
        #             height=1,
        #             relief="solid",
        #             borderwidth=1,
        #         )
        #         self.grid(cell, row, col)
        #         if row >= self.height() or col >= self.width():
        #             cell.grid_remove()
        #         cell.bind("<Button-1>", click_color_listener(row, col))
        #         row_cells.append(cell)
        #     self._cells.append(row_cells)

    # def _init_labels(self) -> None:
    #     """Initializes the labels for the pixel array"""
    #     # Create the column labels
        
    #     for row in [-1, self.height()]:
    #         for col in range(MAX_WIDTH):
    #             label = tk.Label(
    #                 self._pixel_frame, text=str(col), width=2, height=1, relief="flat"
    #             )
    #             self._grid_labels.add_tb_label(label, row)
    #             self.grid(label, row, col)
    #     # Create the row labels
    #     for col in [-1, self.width()]:
    #         for row in range(MAX_HEIGHT):
    #             label = tk.Label(
    #                 self._pixel_frame, text=str(row), width=2, height=1, relief="flat"
    #             )
    #             self._grid_labels.add_lr_label(label, col)
    #             self.grid(label, row, col)
    #             pass
    #         pass
    #     for j in range(self.height(), MAX_HEIGHT):
    #         self._grid_labels.grid_remove_lr(j)
    #         pass
    #     for j in range(self.width(), MAX_WIDTH):
    #         self._grid_labels.grid_remove_tb(j)

    def _init_colors(self) -> None:
        """Initializes the color viewer and picker at the bottom"""
        palette_frame = tk.Frame(self._root)
        palette_frame.pack(side="bottom", pady=10)

        colors: list[RGBColor] = [
            self.__design.fore_color,
            self.__design.back_color,
            self.__design.invis_color,
        ]
        names: list[str] = "Fore, Back, Invis".split(", ")
        for color, name in zip(colors, names):
            button_frame = tk.Frame(palette_frame)
            KnitWindow.deselect(button_frame)
            button_frame.pack(side="left")

            color_button = tk.Label(
                button_frame,
                bg=color.hex(),
                width=4,
                height=2,
            )
            color_button.pack()

            name_label = tk.Label(button_frame, text=name, font=("Arial", 8))
            name_label.pack()

            # TODO: make this functional. Pull up a color picker, set the color in Design,
            # refresh the view
            def pick_color(_, color=color, name=name):
                print(f"You clicked {name} {color.hex()}!")

            for bindable in [button_frame, color_button, name_label]:
                bindable.bind("<Button-1>", pick_color)

    def _init_motifs(self) -> None:
        motifs_frame = tk.Frame(self._root)
        motifs_frame.pack(side="right", padx=10, fill="y")

        canvas = tk.Canvas(motifs_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(motifs_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        inner_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

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

        for motif_name, motif in self._program_builder._motifs.items():
            pil_image = motif2png(motif)
            scaling = 150 // pil_image.width
            pil_image = pil_image.resize(
                (pil_image.width * scaling, pil_image.height * scaling),
                resample=Image.NEAREST,
            )
            motif_thumbnail = ImageTk.PhotoImage(pil_image)
            self._motif_images.append(motif_thumbnail)

            motif_label = tk.Label(
                inner_frame, image=motif_thumbnail, borderwidth=1, relief="solid"
            )
            motif_label.pack(pady=5, padx=5)

            motif_label.bind("<Button-1>", pick_motif_listener(motif_name, motif, motif_label))

            pass
        pass

    def _undo_enabled(self) -> bool:
        return self._undo_button["state"] == "normal"

    def _redo_enabled(self) -> bool:
        return self._undo_button["state"] == "normal"

    def _disable_undo(self) -> None:
        self._undo_button["state"] = "disabled"
        pass

    def _disable_redo(self) -> None:
        self._redo_button["state"] = "disabled"
        pass

    def _enable_redo(self) -> None:
        self._redo_button["state"] = "normal"
        pass

    def _enable_undo(self) -> None:
        self._undo_button["state"] = "normal"
        

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

        history_frame = tk.Frame(self._root)
        history_frame.pack(side="left", padx=10, fill="y")

        # Create the buttons. They start out as being disabled because you haven't done anything to the designs...yet
        undoer = tk.Button(history_frame, text="Undo", command=undo_listener())
        undoer.pack(side="left", padx=5)
        
        redoer = tk.Button(history_frame, text="Redo", command=redo_listener())
        redoer.pack(side="left", padx=5)

        self._undo_button = undoer
        self._redo_button = redoer

        self._disable_undo()
        self._disable_redo()

        pass
    
    def _remove_row(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        print(f"Remove row: {at_index}")
        if remove_labels:
            self._grid_labels.grid_remove_bottom()
        for i in range(MAX_WIDTH):
            self._cells[at_index][i].grid_remove()
            if add_labels and i < self.width():
                self.grid(self._grid_labels.get_bottom_label(i), self.height(), i)
                pass
            pass
        self._grid_labels.grid_remove_lr(at_index)
        pass
    
    def _remove_column(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        print(f"Remove column: {at_index}")
        if remove_labels:
            self._grid_labels.grid_remove_right()
            pass
        for i in range(MAX_HEIGHT):
            if self._GLOBAL_GRID[i + TKINTER_OFFSET][at_index + TKINTER_OFFSET] is not None:
                self._GLOBAL_GRID[i + TKINTER_OFFSET][at_index + TKINTER_OFFSET].grid_remove()
            self._cells[i][at_index].grid_remove()
            if add_labels and i < self.height():
                self.grid(self._grid_labels.get_right_label(i), i, self.width())
                pass
            pass
        self._grid_labels.grid_remove_tb(at_index)
        pass
    
    def _add_row(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        if remove_labels:
            self._grid_labels.grid_remove_bottom()
            pass
        for i in range(self.width()):
            self.grid(self._cells[at_index][i], at_index, i)
            if add_labels:
                self.grid(self._grid_labels.get_bottom_label(i), self.height(), i)
            pass
        l, r = self._grid_labels.get_lr_labels(at_index)
        self.grid(l, at_index, -1)
        self.grid(r, at_index, self.width())
        pass
    
    def _add_column(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        if remove_labels:
            self._grid_labels.grid_remove_right()
            pass
        for i in range(self.height()):
            self.grid(self._cells[i][at_index], i, at_index)
            if add_labels:
                self.grid(self._grid_labels.get_right_label(i), i, self.width())
            pass
        
        t, b = self._grid_labels.get_tb_labels(at_index)
        self.grid(t, -1, at_index)
        self.grid(b, self.height(), at_index)
        pass
    
    def _init_sizes(self) -> None:
        sizes_frame = tk.Frame(self._root)
        sizes_frame.pack(side="left", padx=10, fill="y")
        
        height_var = tk.StringVar()
        height_var.set(str(self.height()))
        
        width_var = tk.StringVar()
        width_var.set(str(self.width()))
        
        
        height_frame = tk.Frame(sizes_frame)
        height_frame.pack()
        
        width_frame = tk.Frame(sizes_frame)
        width_frame.pack()
        
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
                    # self.__design.remove_row()
                    self._remove_row(i,
                                    remove_labels=self.height() == dheight - 1,
                                    add_labels=h == self.height())
                    pass
                pass
            elif h > dheight:
                for i in range(dheight, h):
                    # self.__design.add_row()
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
            dwidth = self.__design.width()
            if w < dwidth:
                for i in range(dwidth - 1, w-1, -1):
                    # self.__design.remove_column()
                    op = self._program_builder.remove_column(i)
                    print(op)
                    self._interpreter.interpret(op)
                    self._remove_column(i,
                                            remove_labels=self.width() == dwidth - 1,
                                            add_labels=w == self.width())
                pass
            elif w > dwidth:
                for i in range(dwidth, w):
                    # self.__design.add_column()
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
        hspinbox = tk.Spinbox(height_frame, from_=1, to=MAX_HEIGHT, width=5, textvariable=height_var, command=height_handler)
        hlabel.pack()
        hspinbox.pack()
        
        wlabel = tk.Label(width_frame, text="Width")
        wspinbox = tk.Spinbox(width_frame, from_=1, to=MAX_WIDTH, width=5, textvariable=width_var, command=width_handler)
        wlabel.pack()
        wspinbox.pack()
        
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
        
