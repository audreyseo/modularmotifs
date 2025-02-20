"""User interface that uses Designs to model pixels"""

import tkinter as tk
from typing import Any, List, Optional
from PIL import ImageTk, Image

from modularmotifs.core.design import Design, MotifOverlapException, RGBColor
from modularmotifs.core.motif import Motif
from modularmotifs.core.util import motif2png
from modularmotifs.motiflibrary.examples import motifs

from modularmotifs.ui.grid_selection import GridSelection

from modularmotifs.dsl import DesignProgramBuilder, DesignInterpreter

# Default grid dimensions
GRID_HEIGHT: int = 25
GRID_WIDTH: int = 50

TKINTER_OFFSET: int = 1

WINDOW_TITLE: str = "Knitting Canvas"

# Cell size in pixels
CELL_SIZE: int = 20

DEFAULT_MOTIFS: list[Motif] = list(motifs.values())


class KnitWindow:
    """Main window to fill out a design"""

    def __init__(self) -> None:
        self.__selected_motif: Optional[tuple[str, Motif]] = None
        self.__selected_motif_button = None

        self.__design: Design = Design(GRID_HEIGHT, GRID_WIDTH)
        self.__program_builder: DesignProgramBuilder = DesignProgramBuilder(self.__design)
        self.__program_builder.add_modularmotifs_motif_library()
        self.__motifs: dict[Motif] = motifs
        self.__interpreter: DesignInterpreter = self.__program_builder.get_interpreter()

        self.__root = tk.Tk()
        self.__root.title(WINDOW_TITLE)

        self.__pixel_frame = tk.Frame(self.__root)
        self.__pixel_frame.pack()

        self.__cells: List[List[Any]] = []

        self.__init_pixels()
        self.__refresh_pixels()
        self.__init_labels()

        self.__init_motifs()

        # Color picker for foreground, background, invis
        self.__init_colors()

        # History actions: undo and redo
        self.__init_history()

        # Add grid selection integration here:
        grid_selector = GridSelection(self)


        # Starts the window
        self.__root.mainloop()

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

    @staticmethod
    def grid(griddable, row: int, col: int):
        """Calls tkinter's grid with a positive offset so
        we can use negative indices

        Args:
            griddable: Something in tkinter with the .grid method
            row (int): Logical row index
            col (int): Logical column index
        """
        griddable.grid(row=row + TKINTER_OFFSET, column=col + TKINTER_OFFSET)

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

    def __refresh_pixels(self) -> None:
        """Queries the Design for new colors and displays them"""
        for y, row in enumerate(self.__cells):
            for x, cell in enumerate(row):
                cell.config(bg=self.__design.get_rgb(x, y).hex())

    def __init_pixels(self) -> None:
        """Initializes the array of visible pixels from the
        current design's dimensions. Does not set colors"""

        def click_color_listener(row: int, col: int):
            def handle(_):
                if self.__selected_motif is not None:
                    try:
                        # add an op that builds the motif to the program currently being built
                        op = self.__program_builder.add_motif(self.__selected_motif[0], col, row)
                        # interpret the operation, which will have an effect on the design
                        self.__interpreter.interpret(op)

                        if self.__redo_enabled():
                            self.__disable_redo()
                            pass

                        if not self.__undo_enabled():
                            self.__enable_undo()
                            pass

                        
                        # self.__design.add_motif(self.__selected_motif, col, row)
                        self.__refresh_pixels()
                    except MotifOverlapException:
                        self.error("Placed motif overlaps with something else!")
                    except IndexError:
                        self.error("Placed motif would be out of bounds!")
                else:
                    self.error("No selected motif!")

            return handle

        for row in range(self.height()):
            row_cells = []
            for col in range(self.width()):
                cell = tk.Label(
                    self.__pixel_frame,
                    width=2,
                    height=1,
                    relief="solid",
                    borderwidth=1,
                )
                KnitWindow.grid(cell, row, col)
                cell.bind("<Button-1>", click_color_listener(row, col))
                row_cells.append(cell)
            self.__cells.append(row_cells)

    def __init_labels(self) -> None:
        """Initializes the labels for the pixel array"""
        # Create the column labels
        for row in [-1, self.height()]:
            for col in range(self.width()):
                label = tk.Label(
                    self.__pixel_frame, text=str(col), width=2, height=1, relief="flat"
                )
                KnitWindow.grid(label, row, col)
        # Create the row labels
        for col in [-1, self.width()]:
            for row in range(self.height()):
                label = tk.Label(
                    self.__pixel_frame, text=str(row), width=2, height=1, relief="flat"
                )
                KnitWindow.grid(label, row, col)

    def __init_colors(self) -> None:
        """Initializes the color viewer and picker at the bottom"""
        palette_frame = tk.Frame(self.__root)
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

    def __init_motifs(self) -> None:
        motifs_frame = tk.Frame(self.__root)
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

        self.__motif_images = []

        def pick_motif_listener(motif_name: str, motif: Motif, motif_button):
            def handle(_):
                if self.__selected_motif_button is not None:
                    KnitWindow.deselect(self.__selected_motif_button)
                if self.__selected_motif == motif:
                    self.__selected_motif = None
                    self.__selected_motif_button = None
                else:
                    self.__selected_motif_button = motif_button
                    self.__selected_motif = (motif_name, motif) # motif
                    KnitWindow.select(self.__selected_motif_button)

            return handle

        for motif_name, motif in self.__program_builder._motifs.items():
            pil_image = motif2png(motif)
            scaling = 150 // pil_image.width
            pil_image = pil_image.resize(
                (pil_image.width * scaling, pil_image.height * scaling),
                resample=Image.NEAREST,
            )
            motif_thumbnail = ImageTk.PhotoImage(pil_image)
            self.__motif_images.append(motif_thumbnail)

            motif_label = tk.Label(
                inner_frame, image=motif_thumbnail, borderwidth=1, relief="solid"
            )
            motif_label.pack(pady=5, padx=5)

            motif_label.bind("<Button-1>", pick_motif_listener(motif_name, motif, motif_label))

            pass
        pass

    def __undo_enabled(self) -> bool:
        return self.__undo_button["state"] == "normal"

    def __redo_enabled(self) -> bool:
        return self.__undo_button["state"] == "normal"

    def __disable_undo(self) -> None:
        self.__undo_button["state"] = "disabled"
        pass

    def __disable_redo(self) -> None:
        self.__redo_button["state"] = "disabled"
        pass

    def __enable_redo(self) -> None:
        self.__redo_button["state"] = "normal"
        pass

    def __enable_undo(self) -> None:
        self.__undo_button["state"] = "normal"
        

    def __init_history(self) -> None:
        # initialize buttons that deal with the history manipulation -- i.e., undo, redo

        def undo_listener():
            def handle():
                undo_action = self.__program_builder.undo()
                if undo_action:
                    self.__interpreter.interpret(undo_action)
                    if not self.__program_builder.can_undo():
                        self.__disable_undo()
                        pass
                    self.__enable_redo()
                    self.__refresh_pixels()
                    pass
                pass
            return handle

        def redo_listener():
            def handle():
                redo_action = self.__program_builder.redo()
                if redo_action:
                    self.__interpreter.interpret(redo_action)
                    if not self.__program_builder.can_redo():
                        self.__disable_redo()
                        pass
                    self.__enable_undo()
                    self.__refresh_pixels()
                    pass
                pass
            return handle

        history_frame = tk.Frame(self.__root)
        history_frame.pack(side="left", padx=10, fill="y")

        # Create the buttons. They start out as being disabled because you haven't done anything to the designs...yet
        undoer = tk.Button(history_frame, text="Undo", command=undo_listener())
        undoer.pack(side="left", padx=5)
        
        redoer = tk.Button(history_frame, text="Redo", command=redo_listener())
        redoer.pack(side="left", padx=5)

        self.__undo_button = undoer
        self.__redo_button = redoer

        self.__disable_undo()
        self.__disable_redo()

        
