# Represents selected cells
from typing import Self, Generator, Tuple


class Selection:
    """
    A basic selection class that stores selected coordinates.

    Does not assume any particular shape of the selection. (i.e., these selections need not be rectangular)
    """

    selected_cells: set[Tuple[int, int]]

    def __init__(self, selected: list[Tuple[int, int]] = None):
        if not selected:
            self.selected_cells = set()
        else:
            self.selected_cells = set(selected)
        pass

    def add(self, x: int, y: int) -> Self:
        self.selected_cells.add((x, y))
        return self

    def _row_major_cells(self):
        # flip (x, y) -> (y, x) since we want lower y values first
        cells = [(y, x) for x, y in list(self.selected_cells)]
        # sorts in lexicographical order
        cells.sort()
        # flip back (y, x) -> (x, y)
        cells = [(x, y) for y, x in cells]
        return cells

    def __iter__(self) -> Generator[Tuple[int, int], None, None]:
        """
        Returns an iterator that iterates through the selected cells in row major order
        """
        cells = self._row_major_cells()

        for x, y in cells:
            yield (x, y)
        pass

    def __repr__(self) -> str:
        cells = self._row_major_cells()
        cellstring = ",".join(list(map(str, cells)))
        return f"Selection([{cellstring}])"

    pass


# Might want a specific subclass that does selections too, but this is probably good for now?
# class GridSelection:


if __name__ == "__main__":
    sel = Selection()
    sel.add(0, 1).add(1, 0).add(2, 0).add(1, 2).add(0, 3)
    print(sel)

    for x, y in sel:
        print((x, y))
