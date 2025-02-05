"""User interface that uses Designs to model pixels"""

import tkinter as tk

from modularmotifs.core.design import Design, RGBColor

# Default grid dimensions
GRID_HEIGHT: int = 25
GRID_WIDTH: int = 50

TKINTER_OFFSET: int = 1

WINDOW_TITLE: str = "Knitting Canvas"

# Cell size in pixels
CELL_SIZE: int = 20


class KnitWindow:
    """Main window to fill out a design"""

    def __init__(self):
        self.__design = Design(GRID_HEIGHT, GRID_WIDTH)

        self.__root = tk.Tk()
        self.__root.title(WINDOW_TITLE)

        # A frame holds the grid
        self.__frame = tk.Frame(self.__root)
        self.__frame.pack()

        self.__cells = []

        self.__init_pixels()
        self.__init_labels()

        # Color picker for foreground, background, invis
        self.__init_colors()

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

    def __init_pixels(self) -> None:
        """Initializes the array of visible pixels from the
        current design"""
        for row in range(self.height()):
            row_cells = []
            for col in range(self.width()):
                cell = tk.Label(
                    self.__frame,
                    bg=self.__design.get_rgb(col, row).hex(),
                    width=2,
                    height=1,
                    relief="solid",
                    borderwidth=1,
                )
                KnitWindow.grid(cell, row, col)
                row_cells.append(cell)
            self.__cells.append(row_cells)

    def __init_labels(self) -> None:
        """Initializes the labels for the pixel array"""
        # Create the column labels
        for row in [-1, self.height()]:
            for col in range(self.width()):
                label = tk.Label(
                    self.__frame, text=str(col), width=2, height=1, relief="flat"
                )
                KnitWindow.grid(label, row, col)
        # Create the row labels
        for col in [-1, self.width()]:
            for row in range(self.height()):
                label = tk.Label(
                    self.__frame, text=str(row), width=2, height=1, relief="flat"
                )
                KnitWindow.grid(label, row, col)

    def __init_colors(self) -> None:
        # Create a color palette for selecting colors
        palette_frame = tk.Frame(self.__root)
        palette_frame.pack(side="bottom", pady=10)

        colors: list[RGBColor] = [
            self.__design.fore_color,
            self.__design.back_color,
            self.__design.invis_color,
        ]
        names: list[str] = "Fore, Back, Invis".split(", ")
        for color, name in zip(colors, names):
            button_frame = tk.Frame(palette_frame, borderwidth=1, relief="solid")
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
                print(f"You clicked {name} {color.hex()} a color!")

            for bindable in [button_frame, color_button, name_label]:
                bindable.bind("<Button-1>", pick_color)

            # color_button = tk.Label(
            #     palette_frame,
            #     bg=color,
            #     width=4,
            #     height=2,
            #     relief="solid",
            #     borderwidth=1,
            # )
            # color_button.bind(
            #     "<Button-1>", lambda event, col=color, btn=color_button: select_color(col, btn)
            # )
            # color_button.pack(side="left", padx=5)
