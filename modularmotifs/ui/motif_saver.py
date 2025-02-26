import os
import datetime

def save_as_motif(knit_window):
    """
    Converts the currently selected grids into a motif and stores it in a Python file.
    The motifs are saved in a file named 'saved_motifs.py' as a dictionary variable
    'saved_motifs', where each key is a generated motif name and each value is a 2D list
    of integers representing the color coding (1 for foreground, 2 for background, 3 for invisible).
    """
    # Retrieve the selected grid coordinates from the GridSelection instance.
    coords = knit_window._KnitWindow__grid_selector.get_selected_coords()
    if not coords:
        print("No grids selected to save as motif!")
        return

    design = knit_window._KnitWindow__design
    # Compute the bounding box of the selection.
    cols = [col for (col, row) in coords]
    rows = [row for (col, row) in coords]
    min_col, max_col = min(cols), max(cols)
    min_row, max_row = min(rows), max(rows)
    width = max_col - min_col + 1
    height = max_row - min_row + 1

    # Build a 2D list representing the motif.
    # Initialize all cells with the invisible value (3).
    motif_data = [[3 for _ in range(width)] for _ in range(height)]
    for (col, row) in coords:
        rel_col = col - min_col
        rel_row = row - min_row
        # Retrieve the color code at (col, row); its .value is assumed to be 1 (fore), 2 (back), or 3 (invis).
        motif_data[rel_row][rel_col] = design.get_color(col, row).value

    # Generate a motif name using the current timestamp.
    motif_name = "motif_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # File where motifs are saved.
    saved_file = "modularmotifs/motiflibrary/saved_motifs.py"

    # Load existing motifs from the file if it exists.
    if os.path.exists(saved_file):
        context = {}
        with open(saved_file, "r") as f:
            file_content = f.read()
        try:
            exec(file_content, context)
            saved = context.get("saved_motifs", {})
        except Exception as e:
            print("Error reading saved motifs file. Starting fresh.", e)
            saved = {}
    else:
        saved = {}

    # Add the new motif to the dictionary.
    saved[motif_name] = motif_data

    # Write the updated motifs dictionary back to the file.
    with open(saved_file, "w") as f:
        f.write("# This file is auto-generated. Do not edit manually.\n")
        f.write("saved_motifs = ")
        f.write(repr(saved))
        f.write("\n")
    print(f"Saved motif '{motif_name}' to {saved_file}")
