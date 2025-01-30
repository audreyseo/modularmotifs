import tkinter as tk
from tkinter import colorchooser
from modularmotifs.core.motif import MOTIFS, Color  # Import from core folder

#import sys
#sys.path.append('/path/to/motif/directory')

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

# State variables for modes and selection
select_mode_active = False
selection_start = None
selection_end = None
selected_cells = []  # List of selected cells
painted_cells = set()
selected_motif = MOTIFS["plus-3x3"]  # Default motif from motif.py


## **Updated Function to Use Motif Library**
def toggle_color(event):
    """Apply the selected motif to the grid."""
    global selected_motif
    cell = event.widget
    row = cell.grid_info()["row"]
    col = cell.grid_info()["column"]

    # Apply motif pattern dynamically
    for r_offset, row_data in enumerate(selected_motif):
        for c_offset, col_data in enumerate(row_data):
            r, c = row + r_offset - 1, col + c_offset - 1
            if 1 <= r <= GRID_HEIGHT and 1 <= c <= GRID_WIDTH:
                if col_data == Color.FORE:
                    cells[r - 1][c - 1].config(bg=current_color)
                    painted_cells.add((r, c))


## **Updated Function to Paint Using Motifs**
def paint_color(event):
    """Paint the selected motif while moving the mouse."""
    widget = event.widget.winfo_containing(event.x_root, event.y_root)
    if isinstance(widget, tk.Label):
        toggle_color(event)


## **Function to Select Different Motifs**
def select_motif(motif_name):
    """Change the selected motif."""
    global selected_motif
    selected_motif = MOTIFS[motif_name]



# Function to reset the canvas to the default color and clear selection
def reset_canvas():
    """Reset all cells to the default color and clear any active selection."""
    global selected_cells, selection_start, selection_end

    # Reset all grid cells to the default color
    for row_cells in cells:
        for cell in row_cells:
            cell.config(bg=DEFAULT_COLOR, borderwidth=1, relief="solid")

    # Clear the selection
    clear_selection()

    # Reset selection variables
    selection_start = None
    selection_end = None

    # Safely hide the repeat buttons if they exist
    if "repeat_x_button" in globals() and repeat_x_button.winfo_exists():
        repeat_x_button.pack_forget()
    if "repeat_y_button" in globals() and repeat_y_button.winfo_exists():
        repeat_y_button.pack_forget()


# Function to set the current active color
def select_color(new_color, color_button):
    """Set the current active color and highlight the selected color."""
    global current_color, selected_button
    current_color = new_color
    # Reset the border for the previously selected button
    if selected_button:
        selected_button.config(relief="solid", borderwidth=1)
    # Highlight the newly selected button
    color_button.config(relief="ridge", borderwidth=3)
    selected_button = color_button


# Function to add a new color to the palette
def add_color():
    """Open a color chooser dialog and add the selected color to the palette."""
    global color_palette, plus_button, selected_button
    if len(color_palette) < 6:  # Allow up to 5 additional colors
        # Open the color chooser dialog
        color_code = colorchooser.askcolor(title="Choose a color")[1]
        if color_code:  # If a color is selected
            color_palette.append(color_code)
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
                lambda event, col=color_code, btn=new_color_button: select_color(
                    col, btn
                ),
            )
            new_color_button.pack(side="left", padx=5)

            # Automatically select the newly added color
            select_color(color_code, new_color_button)

            # Move the plus button to the right
            plus_button.pack_forget()
            plus_button.pack(side="left", padx=5)


# Function to toggle between Select Mode and Draw Mode
def toggle_select_mode():
    """Toggle between Select Mode and Draw Mode."""
    global select_mode_active
    select_mode_active = not select_mode_active
    if select_mode_active:
        # Activate Select Mode
        select_button.config(
            bg="yellow",  # Bright yellow background
            relief="ridge",  # Raised border style
            borderwidth=5,  # Thick border
            font=("Arial", 12, "bold"),  # Bold and larger font
        )
        root.config(cursor="plus")
        update_grid_bindings(select_mode=True)
    else:
        # Switch to Draw Mode
        select_button.config(
            bg="lightgray",  # Light gray background
            relief="solid",  # Flat border style
            borderwidth=1,  # Thin border
            font=("Arial", 10, "normal"),  # Regular font size
        )
        root.config(cursor="arrow")
        clear_selection()  # Clear the selection boundary
        update_grid_bindings(select_mode=False)


# Function to start the selection (Select Mode)
def start_selection(event):
    """Start selecting an area on the grid."""
    global selection_start
    selection_start = event.widget


# Function to update the selection dynamically (Select Mode)
def update_selection(event):
    """Update the selection dynamically as the mouse moves."""
    global selection_end
    if selection_start:
        current_widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if isinstance(current_widget, tk.Label):
            selection_end = current_widget
            highlight_area()


# Function to finalize the selection (Select Mode)
def finalize_selection(event):
    """Finalize the selection on mouse release."""
    global selected_cells

    # Mark the selected cells with a visible boundary
    for cell in selected_cells:
        cell.config(borderwidth=2, relief="solid", highlightbackground="yellow")

    # Dynamically show the repeat buttons
    if not repeat_x_button.winfo_ismapped():
        repeat_x_button.pack(side="left", padx=5)
    if not repeat_y_button.winfo_ismapped():
        repeat_y_button.pack(side="left", padx=5)


# Function to highlight the selected area dynamically (Select Mode)
def highlight_area():
    """Highlight the selected area dynamically without overwriting cell colors."""
    global selected_cells
    clear_selection()  # Clear previous selection overlay
    if selection_start and selection_end:
        start_row, start_col = (
            selection_start.grid_info()["row"],
            selection_start.grid_info()["column"],
        )
        end_row, end_col = (
            selection_end.grid_info()["row"],
            selection_end.grid_info()["column"],
        )
        row_start, row_end = sorted([start_row, end_row])
        col_start, col_end = sorted([start_col, end_col])

        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                if 1 <= row <= GRID_HEIGHT and 1 <= col <= GRID_WIDTH:
                    cell = cells[row - 1][col - 1]
                    # Add transparent overlay without changing the original color
                    cell.config(
                        borderwidth=2, relief="solid", highlightbackground="lightyellow"
                    )
                    selected_cells.append(cell)


# Function to clear the current selection
def clear_selection():
    """Clear the current selection."""
    global selected_cells
    for cell in selected_cells:
        cell.config(borderwidth=1, relief="solid")  # Restore to default appearance
    selected_cells = []


# Function to update event bindings for the grid cells based on mode
def update_grid_bindings(select_mode):
    """Update grid cell event bindings based on the current mode."""
    for row_cells in cells:
        for cell in row_cells:
            cell.unbind("<Button-1>")
            cell.unbind("<B1-Motion>")
            cell.unbind("<ButtonRelease-1>")
            if select_mode:
                # Bind events for Select Mode
                cell.bind("<Button-1>", start_selection)
                cell.bind("<B1-Motion>", update_selection)
                cell.bind("<ButtonRelease-1>", finalize_selection)
            else:
                # Bind events for Draw Mode
                cell.bind("<Button-1>", toggle_color)
                cell.bind("<B1-Motion>", paint_color)


# Function to repeat the selected area along the x-axis
def repeat_x():
    """Repeat the selected grid area along the x-axis."""
    if not selection_start or not selection_end:
        return  # No selection to repeat

    start_row, start_col = (
        selection_start.grid_info()["row"],
        selection_start.grid_info()["column"],
    )
    end_row, end_col = (
        selection_end.grid_info()["row"],
        selection_end.grid_info()["column"],
    )
    pattern_width = end_col - start_col + 1

    for row_idx in range(start_row, end_row + 1):
        for col_idx in range(end_col + 1, GRID_WIDTH + 1, pattern_width):
            for pattern_col_offset in range(pattern_width):
                if col_idx + pattern_col_offset > GRID_WIDTH:
                    break
                color = cells[row_idx - 1][start_col + pattern_col_offset - 1].cget(
                    "bg"
                )
                cells[row_idx - 1][col_idx + pattern_col_offset - 1].config(bg=color)


# Function to repeat the selected area along the y-axis
def repeat_y():
    """Repeat the selected grid area along the y-axis."""
    if not selection_start or not selection_end:
        return  # No selection to repeat

    start_row, start_col = (
        selection_start.grid_info()["row"],
        selection_start.grid_info()["column"],
    )
    end_row, end_col = (
        selection_end.grid_info()["row"],
        selection_end.grid_info()["column"],
    )
    pattern_height = end_row - start_row + 1

    for col_idx in range(start_col, end_col + 1):
        for row_idx in range(end_row + 1, GRID_HEIGHT + 1, pattern_height):
            for pattern_row_offset in range(pattern_height):
                if row_idx + pattern_row_offset > GRID_HEIGHT:
                    break
                color = cells[start_row + pattern_row_offset - 1][col_idx - 1].cget(
                    "bg"
                )
                cells[row_idx + pattern_row_offset - 1][col_idx - 1].config(bg=color)



preview_color = "#A9A9A9"  # Light gray for preview
painted_cells = set()  # Store permanently painted cells to avoid clearing them

def preview_motif(event):
    """Preview the selected motif dynamically when hovering over a cell."""
    global selected_motif
    widget = event.widget.winfo_containing(event.x_root, event.y_root)

    if isinstance(widget, tk.Label) and widget not in palette_frame.winfo_children():
        row = widget.grid_info()["row"]
        col = widget.grid_info()["column"]

        # Get the motif shape dynamically from selected_motif
        for r_offset, row_data in enumerate(selected_motif):
            for c_offset, col_data in enumerate(row_data):
                r, c = row + r_offset - 1, col + c_offset - 1  # Adjust position
                if 1 <= r <= GRID_HEIGHT and 1 <= c <= GRID_WIDTH:
                    cell = cells[r - 1][c - 1]
                    if col_data == Color.FORE and (r, c) not in painted_cells:
                        cell.config(bg=preview_color)  # Show preview color

def clear_preview(event):
    """Clear the motif preview without affecting permanently colored cells."""
    for row_cells in cells:
        for cell in row_cells:
            row, col = cell.grid_info()["row"], cell.grid_info()["column"]
            if cell.cget("bg") == preview_color and (row, col) not in painted_cells:
                cell.config(bg=DEFAULT_COLOR)  # Restore only previewed cells




# Create the main Tkinter window
root = tk.Tk()
root.title("Knitting Canvas")

# Create a frame to hold the grid
frame = tk.Frame(root)
frame.pack()

# Create the grid with numbers on all four sides
cells = []  # Store references to all cells
for row in range(GRID_HEIGHT + 2):  # Include extra rows for top and bottom numbers
    row_cells = []
    for col in range(
        GRID_WIDTH + 2
    ):  # Include extra columns for left and right numbers
        if row == 0:
            if col == 0 or col == GRID_WIDTH + 1:
                label = tk.Label(
                    frame, text="", width=2, height=1
                )  # Empty corner cells
            else:
                # Column numbers (top row)
                label = tk.Label(frame, text=str(col), width=2, height=1, relief="flat")
        elif row == GRID_HEIGHT + 1:
            if col == 0 or col == GRID_WIDTH + 1:
                label = tk.Label(
                    frame, text="", width=2, height=1
                )  # Empty corner cells
            else:
                # Column numbers (bottom row)
                label = tk.Label(frame, text=str(col), width=2, height=1, relief="flat")
        elif col == 0:
            # Row numbers (left column)
            label = tk.Label(frame, text=str(row), width=2, height=1, relief="flat")
        elif col == GRID_WIDTH + 1:
            # Row numbers (right column)
            label = tk.Label(frame, text=str(row), width=2, height=1, relief="flat")
        else:
            # Create grid cells
            cell = tk.Label(
                frame,
                bg=DEFAULT_COLOR,
                width=2,
                height=1,
                relief="solid",
                borderwidth=1,
            )
            cell.grid(row=row, column=col)
            row_cells.append(cell)
            continue
        label.grid(row=row, column=col)  # Place labels for numbers
    if 0 < row <= GRID_HEIGHT:
        cells.append(row_cells)

# Create a color palette for selecting colors
palette_frame = tk.Frame(root)
palette_frame.pack(side="bottom", pady=10)

# Variable to store the currently selected button
selected_button = None

# Create squares for color selection
for color in color_palette:
    color_button = tk.Label(
        palette_frame,
        bg=color,
        width=4,
        height=2,
        relief="solid",
        borderwidth=1,
    )
    color_button.bind(
        "<Button-1>", lambda event, col=color, btn=color_button: select_color(col, btn)
    )
    color_button.pack(side="left", padx=5)
    # Highlight black color by default
    if color == ACTIVE_COLOR:
        select_color(ACTIVE_COLOR, color_button)

# Add the plus sign button for adding new colors
plus_button = tk.Label(
    palette_frame,
    text="+",
    bg="lightgray",
    width=4,
    height=2,
    relief="solid",
    borderwidth=1,
    font=("Arial", 14, "bold"),
)
plus_button.bind("<Button-1>", lambda event: add_color())
plus_button.pack(side="left", padx=5)

# Add a Reset Button
reset_button = tk.Button(root, text="Reset Canvas", command=reset_canvas)
reset_button.pack(pady=10)

# Add a Select Button
select_button = tk.Button(
    root,
    text="Select",
    command=toggle_select_mode,
    bg="lightgray",
    borderwidth=1,
    relief="solid",
)
select_button.pack(side="left", padx=5, pady=10)

# Initialize repeat buttons
repeat_x_button = tk.Button(root, text="Repeat along x-axis", command=repeat_x)
repeat_y_button = tk.Button(root, text="Repeat along y-axis", command=repeat_y)

# Set initial bindings for Draw Mode
update_grid_bindings(select_mode=False)



#Adding to the UI option for the user selecting the motifs
motif_frame = tk.Frame(root)
motif_frame.pack(pady=10)

plus_button = tk.Button(motif_frame, text="Plus", command=lambda: select_motif("plus-3x3"))
plus_button.pack(side="left", padx=5)

x_button = tk.Button(motif_frame, text="X", command=lambda: select_motif("x-3x3"))
x_button.pack(side="left", padx=5)

crosshair_button = tk.Button(motif_frame, text="Crosshair", command=lambda: select_motif("crosshair-3x3"))
crosshair_button.pack(side="left", padx=5)


##Add motif hovering
for row_cells in cells:
    for cell in row_cells:
        cell.bind("<Enter>", preview_motif)  # Hover to preview
        cell.bind("<Leave>", clear_preview)  # Remove preview when leaving

# Run the Tkinter event loop
root.mainloop()
