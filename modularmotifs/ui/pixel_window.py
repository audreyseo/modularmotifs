"""Superclass of windows that support any kind of pixel editing"""
import abc
from modularmotifs.core.pixel_grid import PixelGrid
from modularmotifs.core.rgb_color import RGBColor
import tkinter as tk
from typing import Any, Optional
from collections.abc import Callable
from modularmotifs.ui.grid_labels import GridLabels
import sys

class PixelWindow(abc.ABC):
    """A pixel display window"""
    
    _pixel_frame: tk.Frame
    _cells: list[list[Any]]
    _grid_labels: GridLabels
    _root: tk.Tk
    _MAX_WIDTH: int
    _MAX_HEIGHT: int
    _TKINTER_OFFSET: int
    _WINDOW_TITLE: str
    # The object we're trying to model
    _pixel_grid: PixelGrid
    _undo_button: tk.Button
    _redo_button: tk.Button
    
    def __init__(self, max_width: int, max_height: int, tkinter_offset: int, window_title: str, pixel_grid: PixelGrid):
        
        self._MAX_WIDTH = max_width
        self._MAX_HEIGHT = max_height
        self._TKINTER_OFFSET = tkinter_offset
        self._WINDOW_TITLE = window_title
        self._GLOBAL_GRID = [[None for _ in range(self._MAX_WIDTH + self._TKINTER_OFFSET * 2)] for _ in range(self._MAX_HEIGHT + self._TKINTER_OFFSET * 2)]
        self._current_file_name: Optional[str] = None
        
        self._root = tk.Tk()
        self._root.title(self._WINDOW_TITLE)
        # self._root.option_add("*Borderwidth", "3")
        # self._root.option_add("*Relief", "raised")
        
        self._controls_frame = tk.Frame(self._root)
        self._controls_frame.pack(side="top")
        
        self._lower_frame = tk.Frame(self._root)
        self._lower_frame.pack(side="top", fill="x")
        
        self._library_frame = tk.Frame(self._lower_frame)
        # self._library_frame.grid(row=0, column=0)
        # self._library_frame.configure(borderwidth=5, relief="raised")
        self._library_frame.pack(side="left", padx=10, pady=10, fill="y")
        
        self._pixel_frame = tk.Frame(self._lower_frame)
        # self._pixel_frame.grid(row=0, column=1, columnspan=20, sticky=tk.E + tk.W)
        # self._lower_frame.grid_columnconfigure(1, weight=2)
        self._pixel_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        self._cells = []
        self._grid_labels = GridLabels()
        self._pixel_grid = pixel_grid
        
        # set up saving keyboard shortcut
        is_mac = sys.platform == 'darwin'
        
        # Common metakeys
        self._key_names = {
            "Alt": "Option" if is_mac else "Alt",
            "Ctrl": "Control",
            "Meta": "Command" if is_mac else "Meta",
            "Shift": "Shift"
        }
        
        command_ctrl = self._key_names["Meta"] if is_mac else self._key_names["Ctrl"]
        
        self._root.bind(f"<{command_ctrl}-s>", self._init_save())
        self._root.bind(f"<{command_ctrl}-o>", self._init_open())
        pass
    
    def get_root(self) -> tk.Tk:
        return self._root
    
    @abc.abstractmethod
    def _init_save(self) -> Callable:
        """Initialize anything having to do with saving files

        Returns:
            Callable: the callback for the save file command
        """
        pass
    
    @abc.abstractmethod
    def _init_open(self) -> Callable:
        """Initialize anything having to do with opening files

        Returns:
            Callable: the callback for the open file command
        """
        pass
    
    
    def width(self) -> int:
        """Getter

        Returns:
            int: width of the stored object underlying the display
        """
        return self._pixel_grid.width()
    
    def height(self) -> int:
        """Getter

        Returns:
            int: height of the stored object underlying the display
        """
        return self._pixel_grid.height()
    
    def grid(self, griddable, row: int, col: int):
        """Calls tkinter's grid with a positive offset so
        we can use negative indices

        Args:
            griddable: Something in tkinter with the .grid method
            row (int): Logical row index
            col (int): Logical column index
        """
        r = row + self._TKINTER_OFFSET
        c = col + self._TKINTER_OFFSET
        griddable.grid(row=r, column=c)
        self._GLOBAL_GRID[r][c] = griddable
        pass
    
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
        pass
    
    def _refresh_pixels(self) -> None:
        """Queries the underlying object for new colors and displays them"""
        for y, row in enumerate(self._cells):
            for x, cell in enumerate(row):
                if self._pixel_grid.in_range(x, y):
                    cell.config(bg=self._pixel_grid.get_rgb(x, y).hex())
                    pass
                pass
            pass
        pass
    
    def _init_pixels(self, click_color_listener: Callable[[int, int], Callable[[Any], None]]) -> None:
        for row in range(self._MAX_HEIGHT):
            row_cells = []
            for col in range(self._MAX_WIDTH):
                cell = tk.Label(
                    self._pixel_frame,
                    width=2,
                    height=1,
                    relief="solid",
                    borderwidth=1,
                )
                self.grid(cell, row, col)
                if row >= self.height() or col >= self.width():
                    cell.grid_remove()
                cell.bind("<Button-1>", click_color_listener(row, col))
                row_cells.append(cell)
            self._cells.append(row_cells)
            pass
        pass
    
    def _init_labels(self) -> None:
        """Initializes the labels for the pixel array"""
        # Create the column labels
        
        for row in [-1, self.height()]:
            for col in range(self._MAX_WIDTH):
                label = tk.Label(
                    self._pixel_frame, text=str(col), width=2, height=1, relief="flat"
                )
                self._grid_labels.add_tb_label(label, row)
                self.grid(label, row, col)
        # Create the row labels
        for col in [-1, self.width()]:
            for row in range(self._MAX_HEIGHT):
                label = tk.Label(
                    self._pixel_frame, text=str(row), width=2, height=1, relief="flat"
                )
                self._grid_labels.add_lr_label(label, col)
                self.grid(label, row, col)
                pass
            pass
        for j in range(self.height(), self._MAX_HEIGHT):
            self._grid_labels.grid_remove_lr(j)
            pass
        for j in range(self.width(), self._MAX_WIDTH):
            self._grid_labels.grid_remove_tb(j)
            pass
        pass
    
    def _init_colors(self, colors: list[RGBColor]) -> list:
        """Initializes the color viewer and picker at the bottom"""
        palette_frame = tk.Frame(self._root)
        palette_frame.pack(side="bottom", pady=10)

        names: list[str] = "Fore, Back, Invis".split(", ")
        
        buttons = []
        
        for color, name in zip(colors, names):
            button_frame = tk.Frame(palette_frame)
            PixelWindow.deselect(button_frame)
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

            buttons.append((color, name, (button_frame, color_button, name_label)))
                

            pass
        return buttons
    
    def _init_history(self, undo_listener: Callable, redo_listener: Callable) -> None:
        # initialize buttons that deal with the history manipulation -- i.e., undo, redo

        history_frame = tk.Frame(self._controls_frame)
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
        for i in range(self._MAX_WIDTH):
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
        for i in range(self._MAX_HEIGHT):
            if self._GLOBAL_GRID[i + self._TKINTER_OFFSET][at_index + self._TKINTER_OFFSET] is not None:
                self._GLOBAL_GRID[i + self._TKINTER_OFFSET][at_index + self._TKINTER_OFFSET].grid_remove()
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