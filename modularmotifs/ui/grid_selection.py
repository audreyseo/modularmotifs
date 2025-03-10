# grid_selection.py
"""
Grid Selection Module

This module adds mouse-based grid selection functionality to the interface.
It adds two buttons:
  - "Select Mode": activates selection mode so that hovering over grid cells
    shows a preview highlight and clicking/draging selects cells.
  - "Reset": deactivates selection mode.
//in the previous version, reset button functionality was not as intended since it was
erasing the grid content. This one corrected that flaw.

Usage (in interface.py):
    from grid_selection import GridSelection
    ...
    window = KnitWindow()
    grid_selector = GridSelection(window)
    # Now the UI will include the new buttons and selection mode behavior.
"""

import tkinter as tk

#Constants for the overlay effect.
HOVER_OVERLAY_COLOR = "#d3d3d3"  # Light grey overlay color.
HOVER_ALPHA = 0.5                # Transparency factor (0: fully transparent, 1: opaque).

def blend_colors(bg_color, overlay_color, alpha, tk_root):
    """
    Blend bg_color with overlay_color using the given alpha.
    Colors (bg_color and overlay_color) may be hex strings or standard color names.
    tk_root is used to convert color names to RGB values.
    Returns a hex string representing the blended color.
    """
    # Get RGB values in the 0-65535 range, then scale to 0-255.
    bg_rgb = tuple(int(c/256) for c in tk_root.winfo_rgb(bg_color))
    ov_rgb = tuple(int(c/256) for c in tk_root.winfo_rgb(overlay_color))
    blended = tuple(int(alpha * ov_rgb[i] + (1 - alpha) * bg_rgb[i]) for i in range(3))
    return "#%02x%02x%02x" % blended

class GridSelection:
    def __init__(self, knit_window):
        # Access the main window and grid cells from the KnitWindow instance.
        self.knit_window = knit_window
        self.root = knit_window._root  # access the Tk instance
        self.cells = knit_window._cells  # 2D list of cell widgets

        # Internal state for selection mode.
        self.selection_mode = False
        self.dragging = False
        self.start_cell = None  # Will hold (col, row) of first cell clicked.
        self.selected_coords = set()  # Set of (col, row) tuples.

        # For convenience, tag each cell with its grid position and default background.
        for row_index, row in enumerate(self.cells):
            for col_index, cell in enumerate(row):
                cell.grid_pos = (col_index, row_index)
                cell.default_bg = cell.cget("bg")

        self.create_ui_buttons()

    def create_ui_buttons(self):
        # Create a frame at the top to hold the new buttons.
        self.selection_frame = tk.Frame(self.knit_window._controls_frame)
        self.selection_frame.pack(side="left", pady=5)

        # "Select Mode" button activates grid selection.
        self.select_mode_button = tk.Button(
            self.selection_frame, text="Select Mode", command=self.activate_selection_mode
        )
        self.select_mode_button.pack(side="left", padx=5)

        # "Reset" button deactivates selection mode.
        self.reset_button = tk.Button(
            self.selection_frame, text="Reset Selection", command=self.reset_selection
        )
        self.reset_button.pack(side="left", padx=5)

    def activate_selection_mode(self):
        if not self.selection_mode:
            self.selection_mode = True
            self.select_mode_button.config(relief="sunken")
            # Add a custom bindtag "GridSelection" to every cell so that our event
            # handlers run before the cell’s own click binding.
            for row in self.cells:
                for cell in row:
                    tags = list(cell.bindtags())
                    if "GridSelection" not in tags:
                        tags.insert(0, "GridSelection")
                        cell.bindtags(tuple(tags))
            # Bind our selection events to the custom bindtag.
            self.root.bind_class("GridSelection", "<Enter>", self.on_cell_enter, add="+")
            self.root.bind_class("GridSelection", "<Leave>", self.on_cell_leave, add="+")
            self.root.bind_class("GridSelection", "<ButtonPress-1>", self.on_cell_press, add="+")
            self.root.bind_class("GridSelection", "<B1-Motion>", self.on_cell_motion, add="+")
            self.root.bind_class("GridSelection", "<ButtonRelease-1>", self.on_cell_release, add="+")

    def deactivate_selection_mode(self):
        if self.selection_mode:
            self.selection_mode = False
            self.select_mode_button.config(relief="raised")
            # Unbind our custom events from the "GridSelection" bindtag.
            self.root.unbind_class("GridSelection", "<Enter>")
            self.root.unbind_class("GridSelection", "<Leave>")
            self.root.unbind_class("GridSelection", "<ButtonPress-1>")
            self.root.unbind_class("GridSelection", "<B1-Motion>")
            self.root.unbind_class("GridSelection", "<ButtonRelease-1>")
            # Remove the custom bindtag from every cell.
            for row in self.cells:
                for cell in row:
                    tags = list(cell.bindtags())
                    if "GridSelection" in tags:
                        tags.remove("GridSelection")
                        cell.bindtags(tuple(tags))

    def reset_selection(self):
        # Modified behavior: only deactivate selection mode.
        self.deactivate_selection_mode()
        print("Selection mode deactivated.")

    def on_cell_enter(self, event):
        if not self.selection_mode:
            return
        cell = event.widget
        # If the cell is already finalized as selected, do nothing.
        if cell.grid_pos in self.selected_coords:
            return "break"
        if not self.dragging:
            # Save the cell’s current (design/motif) background if not already saved.
            if not hasattr(cell, '_orig_bg'):
                cell._orig_bg = cell.cget("bg")
            new_color = blend_colors(cell._orig_bg, HOVER_OVERLAY_COLOR, HOVER_ALPHA, self.root)
            cell.config(bg=new_color)
        return "break"

    def on_cell_leave(self, event):
        if not self.selection_mode:
            return
        cell = event.widget
        if cell.grid_pos in self.selected_coords:
            return "break"
        if not self.dragging:
            if hasattr(cell, '_orig_bg'):
                cell.config(bg=cell._orig_bg)
                del cell._orig_bg
        return "break"

    def on_cell_press(self, event):
        if not self.selection_mode:
            return
        self.dragging = True
        cell = event.widget
        self.start_cell = cell.grid_pos
        # Start with just the clicked cell selected.
        self.selected_coords = {cell.grid_pos}
        self.highlight_selection_area(self.start_cell, self.start_cell)
        return "break"

    def on_cell_motion(self, event):
        if not self.selection_mode or not self.dragging:
            return
        # Determine which cell is currently under the mouse.
        cell = event.widget.winfo_containing(event.x_root, event.y_root)
        if cell is None or not hasattr(cell, "grid_pos"):
            return "break"
        current_cell = cell.grid_pos
        # Compute the rectangle defined by the start cell and current cell.
        self.selected_coords = self.compute_rectangle(self.start_cell, current_cell)
        self.highlight_selection_area(self.start_cell, current_cell)
        return "break"

    def on_cell_release(self, event):
        if not self.selection_mode or not self.dragging:
            return
        self.dragging = False
        # Finalize the selection by blending each selected cell’s original background
        # with the semi-transparent light grey overlay.
        for row in self.cells:
            for cell in row:
                if cell.grid_pos in self.selected_coords:
                    if not hasattr(cell, '_orig_bg'):
                        cell._orig_bg = cell.cget("bg")
                    final_color = blend_colors(cell._orig_bg, HOVER_OVERLAY_COLOR, HOVER_ALPHA, self.root)
                    cell.config(bg=final_color)
                else:
                    if hasattr(cell, '_orig_bg'):
                        cell.config(bg=cell._orig_bg)
                        del cell._orig_bg
        print("Selected grids:", sorted(list(self.selected_coords)))

        #--- New Functionality: Capture color and motif information ---
        #Access the design instance from the KnitWindow.
        design = self.knit_window._design
        selected_details = []
        for (col, row) in sorted(list(self.selected_coords)):
            # Get the effective RGB color at this grid cell.
            cell_rgb = design.get_rgba(col, row)
            # Get the motif (if any) associated with this grid cell.
            cell_motif = design.get_motif(col, row)
            selected_details.append({
                "coords": (col, row),
                "color": cell_rgb.hex(),
                "motif": repr(cell_motif) if cell_motif is not None else None
            })
        print("Selected grid details:", selected_details)
        #--- End New Functionality ---

        self.start_cell = None
        return "break"

    def compute_rectangle(self, start, end):
        """Given two (col, row) tuples, return a set of all grid positions
        within the rectangular area spanned by them."""
        col1, row1 = start
        col2, row2 = end
        min_col, max_col = min(col1, col2), max(col1, col2)
        min_row, max_row = min(row1, row2), max(row1, row2)
        selected = {(c, r) for r in range(min_row, max_row + 1)
                            for c in range(min_col, max_col + 1)}
        return selected

    def highlight_selection_area(self, start, current):
        """Temporarily highlight all cells in the rectangle from start to current
        by blending their original background with a transparent light grey overlay."""
        selected = self.compute_rectangle(start, current)
        for row in self.cells:
            for cell in row:
                if cell.grid_pos in selected:
                    if not hasattr(cell, '_orig_bg'):
                        cell._orig_bg = cell.cget("bg")
                    new_color = blend_colors(cell._orig_bg, HOVER_OVERLAY_COLOR, HOVER_ALPHA, self.root)
                    cell.config(bg=new_color)
                else:
                    if hasattr(cell, '_orig_bg'):
                        cell.config(bg=cell._orig_bg)
                        del cell._orig_bg

    def get_selected_coords(self):
        return self.selected_coords

#If desired, you can add a simple test routine here.
if __name__ == "__main__":
    # For testing outside of the main interface, you might create a dummy window
    # with a simple grid. (In practice, this module is imported and used in interface.py.)
    root = tk.Tk()
    root.title("Grid Selection Test")

    # Create a simple grid of labels.
    cells = []
    rows, cols = 10, 10
    frame = tk.Frame(root)
    frame.pack()
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            lbl = tk.Label(frame, text=f"{c},{r}", width=4, height=2, borderwidth=1, relief="solid")
            lbl.grid(row=r, column=c)
            row_cells.append(lbl)
        cells.append(row_cells)

    # Mimic a minimal KnitWindow-like object.
    class DummyKnitWindow:
        pass

    dummy = DummyKnitWindow()
    dummy._root = root
    dummy._cells = cells

    # Activate grid selection.
    gs = GridSelection(dummy)

    root.mainloop()
