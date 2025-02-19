import tkinter as tk
from tkinter import colorchooser
from enum import Enum


class UIMode(Enum):
    SELECT = 1
    PREVIEW = 2
    ADD_COLOR = 3

    @classmethod
    def get_ui_mode_string(cls, uimode):
        if uimode.value == UIMode.SELECT:
            return "Select Mode"
        elif uimode.value == UIMode.PREVIEW:
            return "Preview Mode"
        return "Add Color Mode"


class UICallbacks:
    """A class for managing all of the callbacks and state.

    It's only slightly better than having global variables.
    Sorry. Agile development and all.
    """

    # Define grid dimensions
    GRID_WIDTH = 50  # Number of columns
    GRID_HEIGHT = 25  # Number of rows
    CELL_SIZE = 20  # Size of each cell in pixels

    # Initialize colors
    DEFAULT_COLOR = "white"  # Default cell color
    ACTIVE_COLOR = "black"  # Default selected drawing color
    HIGHLIGHT_COLOR = "lightyellow"  # Highlight color for selection
    color_palette = [DEFAULT_COLOR, ACTIVE_COLOR]  # List of available colors
    current_color = ACTIVE_COLOR  # Active drawing color (default to black)

    # Variable to store the currently selected button
    selected_button = None

    # State variables for modes and selection
    select_mode_active = False
    selection_start = None
    selection_end = None
    selected_cells = []  # List of selected cells
    ui_mode = UIMode.PREVIEW

    # add preview the motif functionality:
    preview_color = "#A9A9A9"  # Light black for preview
    painted_cells = set()  # Store permanently painted cells to avoid clearing them

    ui_elements = {}

    """A bunch of helper functions for the ui elements
    """

    def add_ui_element(self, name: str, element):
        self.ui_elements[name] = element
        return self

    def has_ui_element(self, name: str) -> bool:
        return name in self.ui_elements

    def get_ui_element(self, name: str):
        return self.ui_elements[name]

    def get(self, name: str):
        assert self.has_ui_element(name), f"UI does not have ui element `{name}`"

        return self.get_ui_element(name)

    def get_repeat_x_button(self):
        return self.get("repeat_x_button")

    def get_repeat_y_button(self):
        return self.get("repeat_y_button")

    def get_repeat_buttons(self):
        return self.get_repeat_x_button(), self.get_repeat_y_button()

    ##Adding the plus motif pattern
    # Function to toggle cell color (Draw Mode)
    def toggle_color(self, event):
        """Color a cell and create a plus (+) pattern around it."""
        cell = event.widget
        row = cell.grid_info()["row"]
        col = cell.grid_info()["column"]

        # Define a plus pattern: center + top, bottom, left, right
        pattern_offsets = [
            (0, 0),  # Center (clicked cell)
            (-1, 0),  # Top
            (1, 0),  # Bottom
            (0, -1),  # Left
            (0, 1),  # Right
        ]

        cells = self.get("cells")

        for dr, dc in pattern_offsets:
            r, c = row + dr, col + dc
            if 1 <= r <= self.GRID_HEIGHT and 1 <= c <= self.GRID_WIDTH:
                cells[r - 1][c - 1].config(bg=self.current_color)
                self.painted_cells.add((r, c))  # Mark cell as permanently colored
                pass
            pass
        pass

    ##Adding the plus motif while keeping the left click on
    # Function to paint cells while moving the mouse with the left button held down (Draw Mode)
    def paint_color(self, event):
        """Paint a plus (+) pattern as the mouse moves with the left button held down."""
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if (
            isinstance(widget, tk.Label)
            and widget not in palette_frame.winfo_children()
        ):
            row = widget.grid_info()["row"]
            col = widget.grid_info()["column"]

            # Define a plus pattern: center + top, bottom, left, right
            pattern_offsets = [
                (0, 0),  # Center (current cell)
                (-1, 0),  # Top
                (1, 0),  # Bottom
                (0, -1),  # Left
                (0, 1),  # Right
            ]
            cells = self.get("cells")

            for dr, dc in pattern_offsets:
                r, c = row + dr, col + dc
                if 1 <= r <= self.GRID_HEIGHT and 1 <= c <= self.GRID_WIDTH:
                    cells[r - 1][c - 1].config(bg=self.current_color)
                    pass
                pass
            pass
        pass

    # Function to reset the canvas to the default color and clear selection
    def reset_canvas(self):
        """Reset all cells to the default color and clear any active selection."""
        # global selected_cells, selection_start, selection_end

        cells = self.get("cells")
        # Reset all grid cells to the default color
        for row_cells in cells:
            for cell in row_cells:
                cell.config(bg=self.DEFAULT_COLOR, borderwidth=1, relief="solid")
                pass
            pass

        # Clear the selection
        self.clear_selection()

        # Reset selection variables
        self.selection_start = None
        self.selection_end = None

        # Safely hide the repeat buttons if they exist
        if self.has_ui_element("repeat_x_button"):
            repeat_x_button = self.get_ui_element("repeat_x_button")
            if repeat_x_button.winfo_exists():
                repeat_x_button.pack_forget()
                pass
            pass
        if self.has_ui_element("repeat_y_button"):
            repeat_y_button = self.get_ui_element("repeat_y_button")
            if repeat_y_button.winfo_exists():
                repeat_y_button.pack_forget()
                pass
            pass
        pass

    # Function to set the current active color
    def select_color(self, new_color, color_button):
        """Set the current active color and highlight the selected color."""
        self.current_color = new_color
        # Reset the border for the previously selected button
        if self.selected_button:
            self.selected_button.config(relief="solid", borderwidth=1)
            pass
        # Highlight the newly selected button
        color_button.config(relief="ridge", borderwidth=3)
        self.selected_button = color_button
        pass

    # Function to add a new color to the palette
    def add_color(self, event):
        """Open a color chooser dialog and add the selected color to the palette."""
        # global color_palette, plus_button, selected_button
        if len(self.color_palette) < 6:  # Allow up to 5 additional colors
            # Open the color chooser dialog
            color_code = colorchooser.askcolor(title="Choose a color")[1]
            if color_code:  # If a color is selected
                self.color_palette.append(color_code)
                palette_frame = self.get("palette_frame")
                # Create a new color button
                new_color_button = tk.Label(
                    palette_frame,
                    bg=color_code,
                    width=4,
                    height=2,
                    relief="solid",
                    borderwidth=1,
                )
                new_color_button.bind(
                    "<Button-1>",
                    lambda col=color_code, btn=new_color_button: self.select_color(
                        col, btn
                    ),
                )
                new_color_button.pack(side="left", padx=5)

                # Automatically select the newly added color
                self.select_color(color_code, new_color_button)

                # Move the plus button to the right
                if self.has_ui_element("plus_button"):
                    plus_button = self.get_ui_element("plus_button")
                    plus_button.pack_forget()
                    plus_button.pack(side="left", padx=5)
                pass
            pass
        pass

    # Function to toggle between Select Mode and Draw Mode
    def toggle_select_mode(self):
        """Toggle between Select Mode and Draw Mode."""
        # global select_mode_active
        self.select_mode_active = not self.select_mode_active
        if self.has_ui_element("select_button") and self.has_ui_element("root"):
            select_button = self.get_ui_element("select_button")
            root = self.get_ui_element("root")
            if self.select_mode_active:

                select_button.config(
                    bg="yellow",  # Bright yellow background
                    relief="ridge",  # Raised border style
                    borderwidth=5,  # Thick border
                    font=("Arial", 12, "bold"),  # Bold and larger font
                )
                root.config(cursor="plus")
                self.update_grid_bindings(select_mode=True)
                pass
            else:
                # Switch to Draw Mode
                select_button.config(
                    bg="lightgray",  # Light gray background
                    relief="solid",  # Flat border style
                    borderwidth=1,  # Thin border
                    font=("Arial", 10, "normal"),  # Regular font size
                )
                root.config(cursor="arrow")
                self.clear_selection()  # Clear the selection boundary
                self.update_grid_bindings(select_mode=False)
                pass
            pass
        pass

    # Function to start the selection (Select Mode)
    def start_selection(self, event):
        """Start selecting an area on the grid."""
        self.selection_start = event.widget
        pass

    # Function to update the selection dynamically (Select Mode)
    def update_selection(self, event):
        """Update the selection dynamically as the mouse moves."""
        # global selection_end
        if self.selection_start:
            current_widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if isinstance(current_widget, tk.Label):
                self.selection_end = current_widget
                self.highlight_area()
                pass
            pass
        pass

    # Function to finalize the selection (Select Mode)
    def finalize_selection(self, event):
        """Finalize the selection on mouse release."""

        # Mark the selected cells with a visible boundary
        for cell in self.selected_cells:
            cell.config(borderwidth=2, relief="solid", highlightbackground="yellow")
            pass

        repeat_x_button, repeat_y_button = self.get_repeat_buttons()

        # Dynamically show the repeat buttons
        if not repeat_x_button.winfo_ismapped():
            repeat_x_button.pack(side="left", padx=5)
            pass
        if not repeat_y_button.winfo_ismapped():
            repeat_y_button.pack(side="left", padx=5)
            pass
        pass

    # Function to highlight the selected area dynamically (Select Mode)
    def highlight_area(self):
        """Highlight the selected area dynamically without overwriting cell colors."""
        # global selected_cells
        self.clear_selection()  # Clear previous selection overlay
        if self.selection_start and self.selection_end:
            start_row, start_col, end_row, end_col = self.selection_rows_cols()
            row_start, row_end = sorted([start_row, end_row])
            col_start, col_end = sorted([start_col, end_col])

            cells = self.get("cells")

            for row in range(row_start, row_end + 1):
                for col in range(col_start, col_end + 1):
                    if 1 <= row <= self.GRID_HEIGHT and 1 <= col <= self.GRID_WIDTH:
                        cell = cells[row - 1][col - 1]
                        # Add transparent overlay without changing the original color
                        cell.config(
                            borderwidth=2,
                            relief="solid",
                            highlightbackground="lightyellow",
                        )
                        self.selected_cells.append(cell)
                        pass
                    pass
                pass
            pass
        pass

    # Function to clear the current selection
    def clear_selection(self):
        """Clear the current selection."""
        # global selected_cells
        for cell in self.selected_cells:
            cell.config(borderwidth=1, relief="solid")  # Restore to default appearance
            pass
        self.selected_cells = []
        pass

    # Function to update event bindings for the grid cells based on mode
    def update_grid_bindings(self, select_mode):
        """Update grid cell event bindings based on the current mode."""
        cells = self.get("cells")
        for row_cells in cells:
            for cell in row_cells:
                cell.unbind("<Button-1>")
                cell.unbind("<B1-Motion>")
                cell.unbind("<ButtonRelease-1>")
                if select_mode:
                    # Bind events for Select Mode
                    cell.bind("<Button-1>", self.start_selection)
                    cell.bind("<B1-Motion>", self.update_selection)
                    cell.bind("<ButtonRelease-1>", self.finalize_selection)
                    pass
                else:
                    # Bind events for Draw Mode
                    cell.bind("<Button-1>", self.toggle_color)
                    cell.bind("<B1-Motion>", self.paint_color)
                    pass
                pass
            pass
        pass

    def selection_rows_cols(self):
        start_row, start_col = (
            self.selection_start.grid_info()["row"],
            self.selection_start.grid_info()["column"],
        )
        end_row, end_col = (
            self.selection_end.grid_info()["row"],
            self.selection_end.grid_info()["column"],
        )
        return start_row, start_col, end_row, end_col

    # Function to repeat the selected area along the x-axis
    def repeat_x(self):
        """Repeat the selected grid area along the x-axis."""
        if not self.selection_start or not self.selection_end:
            return  # No selection to repeat

        start_row, start_col, end_row, end_col = self.selection_rows_cols()

        pattern_width = end_col - start_col + 1
        cells = self.get("cells")

        for row_idx in range(start_row, end_row + 1):
            for col_idx in range(end_col + 1, self.GRID_WIDTH + 1, pattern_width):
                for pattern_col_offset in range(pattern_width):
                    if col_idx + pattern_col_offset > self.GRID_WIDTH:
                        break
                    color = cells[row_idx - 1][start_col + pattern_col_offset - 1].cget(
                        "bg"
                    )
                    cells[row_idx - 1][col_idx + pattern_col_offset - 1].config(
                        bg=color
                    )
                    pass
                pass
            pass
        pass

    # Function to repeat the selected area along the y-axis
    def repeat_y(self):
        """Repeat the selected grid area along the y-axis."""
        if not self.selection_start or not self.selection_end:
            return  # No selection to repeat

        cells = self.get("cells")

        start_row, start_col, end_row, end_col = self.selection_rows_cols()
        pattern_height = end_row - start_row + 1

        for col_idx in range(start_col, end_col + 1):
            for row_idx in range(end_row + 1, self.GRID_HEIGHT + 1, pattern_height):
                for pattern_row_offset in range(pattern_height):
                    if row_idx + pattern_row_offset > self.GRID_HEIGHT:
                        break
                    color = cells[start_row + pattern_row_offset - 1][col_idx - 1].cget(
                        "bg"
                    )
                    cells[row_idx + pattern_row_offset - 1][col_idx - 1].config(
                        bg=color
                    )
                    pass
                pass
            pass
        pass

    def preview_motif(self, event):
        """Preview the plus (+) pattern in light black when hovering over a cell."""
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        palette_frame = self.get("palette_frame")
        if (
            isinstance(widget, tk.Label)
            and widget not in palette_frame.winfo_children()
        ):
            row = widget.grid_info()["row"]
            col = widget.grid_info()["column"]

            # Define a plus pattern: center + top, bottom, left, right
            pattern_offsets = [
                (0, 0),  # Center (current cell)
                (-1, 0),  # Top
                (1, 0),  # Bottom
                (0, -1),  # Left
                (0, 1),  # Right
            ]
            cells = self.get("cells")

            for dr, dc in pattern_offsets:
                r, c = row + dr, col + dc
                if 1 <= r <= self.GRID_HEIGHT and 1 <= c <= self.GRID_WIDTH:
                    cell = cells[r - 1][c - 1]
                    if (
                        r,
                        c,
                    ) not in self.painted_cells:  # Don't overwrite painted cells
                        cell.config(bg=self.preview_color)
                        pass
                    pass
                pass
            pass
        pass

    def clear_preview(self, event):
        """Clear the motif preview without affecting permanently colored cells."""
        cells = self.get("cells")
        for row_cells in cells:
            for cell in row_cells:
                row, col = cell.grid_info()["row"], cell.grid_info()["column"]
                if (
                    cell.cget("bg") == self.preview_color
                    and (row, col) not in self.painted_cells
                ):
                    cell.config(bg=self.DEFAULT_COLOR)  # Restore only previewed cells
                    pass
                pass
            pass
        pass
