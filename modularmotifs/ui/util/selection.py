# Represents selected cells
from typing import Self, Generator, Tuple, Union


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
    
    def union(self, other: Union['Selection', set[tuple[int, int]]]) -> Self:
        if isinstance(other, set):
            self.selected_cells = self.selected_cells.union(other)
            pass
        else:
            self.selected_cells = self.selected_cells.union(other.selected_cells)
            pass
        return self
    
    def __eq__(self, value):
        if isinstance(value, set):
            return self.selected_cells == value
        if isinstance(value, Selection):
            return self.selected_cells == value.selected_cells
        return False
    
    def __ne__(self, value):
        return not (self == value)
    
    def __contains__(self, item):
        return item in self.selected_cells

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

class GridSelection(Selection):
    def __init__(self, startx: int, starty: int):
        self._start = (startx, starty)
        self._end = None
        super().__init__()
        pass
    
    def complete(self, endx: int, endy: int):
        startx, starty = self._start
        self._end = (endx, endy)
        for x in range(startx, endx + 1):
            for y in range(starty, endy + 1):
                self.add(x, y)
                pass
            pass
        pass
    
    def is_complete(self) -> bool:
        return self._end is not None
    
    def bbox(self) -> tuple[int, int, int, int]:
        assert self.is_complete(), f"Selection not completed"
        x0, y0 = self._start
        x1, y1 = self._end
        return (x0, y0, x1, y1)
    
    def __repr__(self):
        end = "" if not self._end else f", {self._end}"
        return f"GridSelection({self._start}{end})"
    

# Might want a specific subclass that does selections too, but this is probably good for now?
# class GridSelection:


if __name__ == "__main__":
    sel = Selection()
    sel.add(0, 1).add(1, 0).add(2, 0).add(1, 2).add(0, 3)
    print(sel)

    for x, y in sel:
        print((x, y))
