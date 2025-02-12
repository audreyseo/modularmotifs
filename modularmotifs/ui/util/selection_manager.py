# selection_manager.py

from modularmotifs.ui.util.selection import Selection

class SelectionManager:
    """
    Manages selected cells in the knitting interface.
    """

    def __init__(self):
        self.selection = Selection()

    def add_cell(self, x: int, y: int):
        """
        Adds a cell to the current selection.
        """
        self.selection.add(x, y)
        print(f"Added cell at ({x}, {y}). Current selection: {self.selection}")

    def clear_selection(self):
        """
        Clears all selected cells.
        """
        self.selection = Selection()
        print("Selection cleared.")

    def get_selected_cells(self):
        """
        Returns all selected cells.
        """
        return list(self.selection)

    def display_selection(self):
        """
        Prints the selected cells.
        """
        print("Current selected cells:")
        for x, y in self.selection:
            print(f"({x}, {y})")
