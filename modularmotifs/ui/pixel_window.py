"""Superclass of windows that support any kind of pixel editing"""
import abc
from modularmotifs.core.pixel_grid import PixelGrid
from modularmotifs.core.rgb_color import RGBAColor
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Optional
from collections.abc import Callable
from modularmotifs.ui.grid_labels import GridLabels
import sys
from modularmotifs.ui.pixel_canvas import PixelCanvas
from PIL import Image, ImageTk
from modularmotifs.ui.modes import UIMode
from modularmotifs.ui.util.selection import Selection, GridSelection

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
    _mode: UIMode
    _modes: list[UIMode]
    _selection: Selection
    
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
        
        style = ttk.Style(self._root)
        style.configure("TLabel", padx=20, pady=20)
        style1 = ttk.Style(self._root)
        style.configure("selected.TLabel", padx=20, pady=20, relief="sunken", borderwidth=3)
        style.configure("unselected.TLabel", padx=20, pady=20, relief="flat", borderwidth=3)
        self._mode = UIMode.NORMAL
        self._modes = []
        
        self._selection_img = Image.new(mode="RGBA", size=(100, 100), color=(0, 255, 255, 50))
        # self._selection_img.save("blah.png")
        
        self._controls_frame = tk.Frame(self._root)
        self._controls_frame.pack(side="top")
        
        self._tools_frame = tk.Frame(self._root)
        self._tools_frame.pack(side="top")
        
        self._lower_frame = tk.Frame(self._root)
        self._lower_frame.pack(side="top", fill="x")
        
        self._library_frame = tk.Frame(self._lower_frame)
        # self._library_frame.grid(row=0, column=0)
        # self._library_frame.configure(borderwidth=5, relief="raised")
        self._library_frame.pack(side="left", padx=10, pady=10, fill="y")
        
        self._pixel_canvas = PixelCanvas(self._lower_frame, pixel_grid, pixel_size=20, line_width=1.5)
        self._pixel_canvas.get_toplevel().pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        self._pixel_frame = tk.Frame(self._lower_frame)
        
        # self._pixel_frame.grid(row=0, column=1, columnspan=20, sticky=tk.E + tk.W)
        # self._lower_frame.grid_columnconfigure(1, weight=2)
        self._pixel_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        self._cells = []
        self._grid_labels = GridLabels()
        self._pixel_grid = pixel_grid
        
        # set up saving keyboard shortcut
        is_mac = PixelWindow.is_mac()
        
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
        
        save_as_handknit = tk.Button(self._controls_frame, text="Save as Hand Knit", command=self._init_handknit_output())
        save_as_handknit.pack(side="right", padx=10)
        
        pass
    
    @classmethod
    def is_mac(cls) -> bool:
        return sys.platform == 'darwin'
    
    def get_root(self) -> tk.Tk:
        return self._root
    
    def _init_handknit_output(self) -> Callable:
        pass
    
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
        self._pixel_canvas.refresh()
        
        match self._mode:
            case UIMode.RECT_SELECTION:
                self._pixel_canvas.get_canvas().config(cursor="cross")
                pass
            case UIMode.PAINT_SELECTION:
                self._pixel_canvas.get_canvas().config(cursor="pencil")
                pass
            case UIMode.WAND_SELECTION:
                self._pixel_canvas.get_canvas().config(cursor="star")
                pass
            case UIMode.LASSO_SELECTION:
                self._pixel_canvas.get_canvas().config(cursor="cross")
                pass
            case _:
                self._pixel_canvas.get_canvas().config(cursor="arrow")
                pass
        
        
        """Queries the underlying object for new colors and displays them"""
        # for y, row in enumerate(self._cells):
        #     for x, cell in enumerate(row):
        #         if self._pixel_grid.in_range(x, y):
        #             cell.config(bg=self._pixel_grid.get_rgba(x, y).hex())
        #             pass
        #         pass
        #     pass
        pass
    
    def _reset_tools(self) -> None:
        for i in range(len(self._tools)):
            self._tools[i].config(style="unselected.TLabel")
            pass
        pass
    
    def _change_mode(self, mode: UIMode) -> None:
        self._modes.append(self._mode)
        self._mode = mode
        pass
    
    def _pop_mode(self) -> UIMode:
        current_mode = self._mode
        self._mode = self._modes.pop(-1)
        self._handle_hover_mode()
        return current_mode
    
    def _init_tools(self) -> None:
        self._tool_images = []
        self._tools = []
        images = ["icons/lasso_tool.png", "icons/select_rect.png", "icons/magic_wand.png", "icons/paint_select.png"]
        modes = [UIMode.LASSO_SELECTION, UIMode.RECT_SELECTION, UIMode.WAND_SELECTION, UIMode.PAINT_SELECTION]
        unselected_relief = "groove"
        
        
        
        def handler(column: int):
            def handle(event):
                old_mode = self._mode
                # print(column)
                new_mode = None
                for i in range(len(self._tools)):
                    relief = self._tools[i].config()["style"][-1]
                    print(i, relief)
                    if i != column:
                        # self._tools[i].config(relief=unselected_relief, borderwidth=2)
                        self._tools[i].config(style="unselected.TLabel")
                        pass
                    else:
                        # print(relief, str(relief), str(relief).startswith("sunken"))
                        if str(relief).startswith("selected"):
                            # self._tools[i].config(relief=unselected_relief, borderwidth=2)
                            self._tools[i].config(style="unselected.TLabel")
                            if self._mode == modes[i]:
                                self._pop_mode()
                                # self._mode = UIMode.NORMAL
                            pass
                        else:
                            # self._tools[i].config(relief="sunken", borderwidth=2)
                            self._tools[i].config(style="selected.TLabel")
                            new_mode = modes[i]
                            pass
                        pass
                    pass
                if new_mode and old_mode != new_mode:
                    self._change_mode(new_mode)
                    self._handle_hover_mode()
                self._refresh_pixels()
                pass
            return handle
        
        for x, f in enumerate(images):
            img = Image.open(f)
            scale = 25.0 / img.height
            img = img.resize((round(img.width * scale), round(img.height * scale)), resample=Image.LANCZOS)
            thumb = ImageTk.PhotoImage(img)
            self._tool_images.append(thumb)
            lasso = ttk.Label(self._tools_frame, image=thumb, style="unselected.TLabel")
            # lasso = ttk.Label(self._tools_frame, image=thumb, style="unselected.TLabel") borderwidth=2, relief=unselected_relief) #, padx=20, pady=20)
            # print(lasso.config())
            lasso.grid(row=0, column=x, padx=2)
            lasso.bind("<Button-1>", handler(x))
            self._tools.append(lasso)
    
    def _handle_hover_mode(self):
        def handle_grid_selection(x: int, y: int):
            if not self._selection:
                return
            assert isinstance(self._selection, GridSelection)
            print("Handle grid selection: ", x, y)
            sx, sy = self._selection._start
            x, y = (x, y) if not self._selection.is_complete() else self._selection._end
            pxs = self._pixel_canvas.pixel_size()
            rsx = sx * pxs
            rsy = sy * pxs
            rx = x * pxs
            ry = y * pxs
            # if not self._selection.is_complete():
                # sx, sy = self._selection._start
            self._pixel_canvas._add_old_id(
                self._pixel_canvas.create_rectangle(sx, sy, x, y, fill=None, width=2, outline="black")
            )
            if rsx != rx and rsy != ry:
                print(sx, sy, x, y, rsx, rsy, rx, ry)

                # img = Image.new(mode="RGBA", size=(abs(rsx - rx), abs(rsy-ry)), color=(0, 255, 255, 122))
                img = self._selection_img.resize(size=(abs(rsx - rx), abs(rsy - ry)), resample=Image.Resampling.NEAREST)
                self._temp_img = ImageTk.PhotoImage(img)
                print(img.width, img.height)
                
                # self._pixel_canvas._add_old_id(
                #     self._pixel_canvas.get_canvas().create_line(x - 3, y - 3, x + 3, y + 3, fill="black")
                # )
                
                self._pixel_canvas._add_old_id(
                    self._pixel_canvas.create_image(sx, sy, image=self._temp_img, anchor="nw")
                )
                pass
            # else:
        match self._mode:
            case UIMode.RECT_SELECTION:
                print("Setting hover function")
                self._pixel_canvas.set_hover_function(handle_grid_selection, should_reset_hover=False)
                self._pixel_canvas.set_motif(None)
                pass
            case UIMode.PLACE_MOTIF:
                print("Setting motif hover")
                self._pixel_canvas.set_motif_hover()
                if self._pixel_canvas.get_motif() is None:
                    self.set_pixel_canvas_motif()
            case _:
                pass
    
    @abc.abstractmethod
    def set_pixel_canvas_motif(self):
        pass
    
    def _init_pixels(self, click_color_listener: Callable) -> None:
        self._pixel_canvas.get_canvas().bind("<Button-1>", click_color_listener)
        # for row in range(self._MAX_HEIGHT):
        #     row_cells = []
        #     for col in range(self._MAX_WIDTH):
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
        #     pass
        # pass
    
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
    
    def _init_colors(self, colors: list[RGBAColor]) -> list:
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
        
        command_ctrl = self._key_names["Meta"] if PixelWindow.is_mac() else self._key_names["Ctrl"]
        self._root.bind(f"<{command_ctrl}-z>", lambda e: undo_listener()())
        self._root.bind(f"<{command_ctrl}-y>", lambda e: redo_listener()())

        self._undo_button = undoer
        self._redo_button = redoer

        self._disable_undo()
        self._disable_redo()

        pass
                
    def _remove_row(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        print(f"Remove row: {at_index}")
        self._pixel_canvas.remove_row()
        # if remove_labels:
        #     self._grid_labels.grid_remove_bottom()
        # for i in range(self._MAX_WIDTH):
        #     self._cells[at_index][i].grid_remove()
        #     if add_labels and i < self.width():
        #         self.grid(self._grid_labels.get_bottom_label(i), self.height(), i)
        #         pass
        #     pass
        # self._grid_labels.grid_remove_lr(at_index)
        pass
    
    def _remove_column(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        print(f"Remove column: {at_index}")
        self._pixel_canvas.remove_column()
        # if remove_labels:
        #     self._grid_labels.grid_remove_right()
        #     pass
        # for i in range(self._MAX_HEIGHT):
        #     if self._GLOBAL_GRID[i + self._TKINTER_OFFSET][at_index + self._TKINTER_OFFSET] is not None:
        #         self._GLOBAL_GRID[i + self._TKINTER_OFFSET][at_index + self._TKINTER_OFFSET].grid_remove()
        #     self._cells[i][at_index].grid_remove()
        #     if add_labels and i < self.height():
        #         self.grid(self._grid_labels.get_right_label(i), i, self.width())
        #         pass
        #     pass
        # self._grid_labels.grid_remove_tb(at_index)
        pass
    
    def _add_row(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        self._pixel_canvas.add_row(at_index)
        # if remove_labels:
        #     self._grid_labels.grid_remove_bottom()
        #     pass
        # for i in range(self.width()):
        #     self.grid(self._cells[at_index][i], at_index, i)
        #     if add_labels:
        #         self.grid(self._grid_labels.get_bottom_label(i), self.height(), i)
        #     pass
        # l, r = self._grid_labels.get_lr_labels(at_index)
        # self.grid(l, at_index, -1)
        # self.grid(r, at_index, self.width())
        pass
    
    def _add_column(self, at_index: int, remove_labels: bool = True, add_labels: bool = True) -> None:
        self._pixel_canvas.add_column(at_index)
        # if remove_labels:
        #     self._grid_labels.grid_remove_right()
        #     pass
        # for i in range(self.height()):
        #     self.grid(self._cells[i][at_index], i, at_index)
        #     if add_labels:
        #         self.grid(self._grid_labels.get_right_label(i), i, self.width())
        #     pass
        
        # t, b = self._grid_labels.get_tb_labels(at_index)
        # self.grid(t, -1, at_index)
        # self.grid(b, self.height(), at_index)
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