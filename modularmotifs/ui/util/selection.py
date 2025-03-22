# Represents selected cells
from dataclasses import dataclass
from typing import Iterable, Self, Generator, Tuple, Union, override
import abc

class AbstractSelection(abc.ABC):
    def __init__(self):
        self.cn = self.__class__.__qualname__
    
    def surrounding(self, x: int, y: int) -> set[tuple[int, int]]:
        pts = [(x + i, y + j) for i, j in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]]
        pts = [(x, y) for x, y in pts if (x, y) in self.get_cells()]
        return set(pts)
    
    def contiguous_selections(self) -> set[frozenset[tuple[int, int]]]:
        def bfs(x, y, s: set[tuple[int, int]], seen: set[tuple[int, int]]):
            new = self.surrounding(x, y)
            print(new)
            for x0, y0 in new.difference(seen):
                seen.add((x0, y0))
                s.add((x0, y0))
                bfs(x0, y0, s, seen)
                pass
            pass
        
        selections = set()
        seen_points = set()
        cells = self.get_cells()
        
        for x, y in cells:
            if cells == seen_points:
                break
            if (x, y) not in seen_points:
                seen_points.add((x, y))
                s = set([(x, y)])
                bfs(x, y, s, seen_points)
                print(s)
                selections.add(frozenset(s))
                pass
            pass
        return selections
    
    def plot_selection(self) -> str:
        xmin, xmax = self.x_limits()
        ymin, ymax = self.y_limits()
        everything = [[(x, y) in self.get_cells() for x in range(xmax + 1)] for y in range(ymax + 1)]
        everything = [["1" if e else "0" for e in row] for row in everything]
        return "\n".join(list(map(lambda x: "".join(x), everything)))
    
    def x_limits(self) -> tuple[int, int]:
        xs = set([x for x, _ in self.get_cells()])
        return min(xs), max(xs)
    
    def y_limits(self) -> tuple[int, int]:
        ys = set([y for _, y in self.get_cells()])
        return min(ys), max(ys)
    
    def _row_major_cells(self) -> Iterable[tuple[int, int]]:
        # flip (x, y) -> (y, x) since we want lower y values first
        cells = [(y, x) for x, y in self.get_cells()]
        # sorts in lexicographical order
        cells.sort()
        # flip back (y, x) -> (x, y)
        cells = [(x, y) for y, x in cells]
        return cells
    
    def __iter__(self):
        return iter(self._row_major_cells())
    
    def __repr__(self) -> str:
        cells = self._row_major_cells()
        cellstring = ",".join(list(map(str, cells)))
        return f"{self.cn}([{cellstring}])"
    
    @abc.abstractmethod
    def __eq__(self, value) -> bool:
        pass
    
    @abc.abstractmethod
    def __ne__(self, value) -> bool:
        pass
    
    @abc.abstractmethod
    def get_cells(self) -> set[tuple[int, int]]:
        pass
    
    @abc.abstractmethod
    def __contains__(self, elmt) -> bool:
        pass
    
    
    
    pass


@dataclass
class ImmutableSelection(AbstractSelection):
    selected_cells: frozenset[tuple[int, int]]
    
    def __init__(self, selected_cells: Iterable[tuple[int, int]]):
        super().__init__()
        self.selected_cells = frozenset(selected_cells)
        pass
    
    def __hash__(self):
        return hash(self.selected_cells)
    
    @override
    def __eq__(self, value):
        match value:
            case ImmutableSelection(cells):
                return self.selected_cells == cells
            case _:
                return (isinstance(value, set) or isinstance(value, frozenset)) and self.selected_cells == value
    
    @override
    def __ne__(self, value):
        return not (self == value)
    
    @override
    def __iter__(self):
        return iter(self._row_major_cells())
    
    @override
    def get_cells(self):
        return self.selected_cells
    
    @override
    def __contains__(self, elmt):
        return elmt in self.selected_cells
    pass
    
    
    



class Selection(AbstractSelection):
    """
    A basic selection class that stores selected coordinates. This version is mutable.

    Does not assume any particular shape of the selection. (i.e., these selections need not be rectangular)
    """

    selected_cells: set[Tuple[int, int]]

    def __init__(self, selected: list[Tuple[int, int]] = None):
        super().__init__()
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
    
    @override
    def __eq__(self, value):
        if isinstance(value, set):
            return self.selected_cells == value
        if isinstance(value, Selection):
            return self.selected_cells == value.selected_cells
        if isinstance(value, AbstractSelection):
            return self.selected_cells == value.get_cells()
        return False
    
    @override
    def __ne__(self, value):
        return not (self == value)
    
    @override
    def __contains__(self, item):
        return item in self.selected_cells
    
    @override 
    def get_cells(self):
        return self.selected_cells

    # def _row_major_cells(self):
    #     # flip (x, y) -> (y, x) since we want lower y values first
    #     cells = [(y, x) for x, y in list(self.selected_cells)]
    #     # sorts in lexicographical order
    #     cells.sort()
    #     # flip back (y, x) -> (x, y)
    #     cells = [(x, y) for y, x in cells]
    #     return cells

    # def __iter__(self) -> Generator[Tuple[int, int], None, None]:
    #     """
    #     Returns an iterator that iterates through the selected cells in row major order
    #     """
    #     cells = self._row_major_cells()

    #     for x, y in cells:
    #         yield (x, y)
    #     pass

    
    
    # def __hash__(self):
    #     return hash(repr(self))
    
    # def surrounding(self, x, y) -> set[tuple[int, int]]:
    #     pts = [(x + i, y + j) for i, j in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]]
    #     pts = [(x, y) for x, y in pts if (x, y) in self]
    #     return set(pts)
    
    # def contiguous_selections(self) -> set[frozenset[tuple[int, int]]]:
        
    #     def bfs(x, y, s: set[tuple[int, int]], seen: set[tuple[int, int]]):
    #         new = self.surrounding(x, y)
    #         print(new)
    #         for x0, y0 in new.difference(seen):
    #             seen.add((x0, y0))
    #             s.add((x0, y0))
    #             bfs(x0, y0, s, seen)
    #             pass
    #         pass
        
    #     selections = set()
    #     seen_points = set()
    #     for x, y in self.selected_cells:
    #         if self.selected_cells == seen_points:
    #             break
    #         if (x, y) not in seen_points:
    #             seen_points.add((x, y))
    #             s = set([(x, y)])
    #             bfs(x, y, s, seen_points)
    #             print(s)
    #             selections.add(frozenset(s))
    #             pass
    #         pass
    #     return selections
                

    # pass

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
