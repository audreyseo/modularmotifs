import tkinter as tk
from tkinter import colorchooser
from modularmotifs.motiflibrary.examples import motifs
from modularmotifs.ui.callbacks import UICallbacks

# instantiate the class that has all of the callbacks and global state
callbacks = UICallbacks()

# Create the main Tkinter window
root = tk.Tk()
root.title("Knitting Canvas")

# Create a frame to hold the grid
frame = tk.Frame(root)
frame.pack()

# Create the grid with numbers on all four sides
cells = []  # Store references to all cells
for row in range(callbacks.GRID_HEIGHT + 2):  # Include extra rows for top and bottom numbers
    row_cells = []
    for col in range(
        callbacks.GRID_WIDTH + 2
    ):  # Include extra columns for left and right numbers
        if row == 0:
            if col == 0 or col == callbacks.GRID_WIDTH + 1:
                label = tk.Label(
                    frame, text="", width=2, height=1
                )  # Empty corner cells
            else:
                # Column numbers (top row)
                label = tk.Label(frame, text=str(col), width=2, height=1, relief="flat")
        elif row == callbacks.GRID_HEIGHT + 1:
            if col == 0 or col == callbacks.GRID_WIDTH + 1:
                label = tk.Label(
                    frame, text="", width=2, height=1
                )  # Empty corner cells
            else:
                # Column numbers (bottom row)
                label = tk.Label(frame, text=str(col), width=2, height=1, relief="flat")
        elif col == 0:
            # Row numbers (left column)
            label = tk.Label(frame, text=str(row), width=2, height=1, relief="flat")
        elif col == callbacks.GRID_WIDTH + 1:
            # Row numbers (right column)
            label = tk.Label(frame, text=str(row), width=2, height=1, relief="flat")
        else:
            # Create grid cells
            cell = tk.Label(
                frame,
                bg=callbacks.DEFAULT_COLOR,
                width=2,
                height=1,
                relief="solid",
                borderwidth=1,
            )
            cell.grid(row=row, column=col)
            row_cells.append(cell)
            continue
        label.grid(row=row, column=col)  # Place labels for numbers
    if 0 < row <= callbacks.GRID_HEIGHT:
        cells.append(row_cells)

# Create a color palette for selecting colors
palette_frame = tk.Frame(root)
palette_frame.pack(side="bottom", pady=10)


# Create squares for color selection
for color in callbacks.color_palette:
    color_button = tk.Label(
        palette_frame,
        bg=color,
        width=4,
        height=2,
        relief="solid",
        borderwidth=1,
    )
    color_button.bind(
        "<Button-1>", lambda event, col=color, btn=color_button: callbacks.select_color(col, btn)
    )
    color_button.pack(side="left", padx=5)
    # Highlight black color by default
    if color == callbacks.ACTIVE_COLOR:
        callbacks.select_color(callbacks.ACTIVE_COLOR, color_button)

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
plus_button.bind("<Button-1>", lambda event: callbacks.add_color(event))
plus_button.pack(side="left", padx=5)

# Add a Reset Button
reset_button = tk.Button(root, text="Reset Canvas", command=callbacks.reset_canvas)
reset_button.pack(pady=10)

# Add a Select Button
select_button = tk.Button(
    root,
    text="Select",
    command=lambda: callbacks.toggle_select_mode(),
    bg="lightgray",
    borderwidth=1,
    relief="solid",
)
select_button.pack(side="left", padx=5, pady=10)

# Initialize repeat buttons
repeat_x_button = tk.Button(root, text="Repeat along x-axis", command=lambda: callbacks.repeat_x())
repeat_y_button = tk.Button(root, text="Repeat along y-axis", command=lambda: callbacks.repeat_y())

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, height=10, width=30)
for motif in motifs:
    # for now, just put the names of the motifs in the list
    listbox.insert(tk.END, motif)
    pass

scrollbar.config(command=listbox.yview)

listbox.pack(side=tk.LEFT)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)



callbacks.add_ui_element("cells", cells)
callbacks.add_ui_element("repeat_x_button", repeat_x_button)
callbacks.add_ui_element("repeat_y_button", repeat_y_button)
callbacks.add_ui_element("select_button", select_button)
callbacks.add_ui_element("plus_button", plus_button)
callbacks.add_ui_element("root", root)
callbacks.add_ui_element("palette_frame", palette_frame)





# Set initial bindings for Draw Mode
callbacks.update_grid_bindings(select_mode=False)

##Add motif hovering
for row_cells in cells:
    for cell in row_cells:
        cell.bind("<Enter>", callbacks.preview_motif)  # Hover to preview
        cell.bind("<Leave>", callbacks.clear_preview)  # Remove preview when leaving
        pass
    pass


# Run the Tkinter event loop
root.mainloop()
