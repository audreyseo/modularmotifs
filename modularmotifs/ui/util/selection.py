# Represents selected cells
from collections.abc import Callable
from dataclasses import dataclass
from typing import Iterable, Optional, Self, Generator, Tuple, Union, override
import abc
from PIL import Image, ImageDraw
from modularmotifs.core.util import rgbcolors_to_image
from itertools import chain
import numpy as np

from modularmotifs.core.rgb_color import RGBAColor


def bfs(
    x,
    y,
    s: set[tuple[int, int]],
    seen: set[tuple[int, int]],
    surrounding: Callable[[int, int], set[tuple[int, int]]],
):
    new = surrounding(x, y)
    # print(new)
    for x0, y0 in new.difference(seen):
        seen.add((x0, y0))
        s.add((x0, y0))
        bfs(x0, y0, s, seen, surrounding)
        pass
    pass


@dataclass
class Edge:
    start: tuple[int, int]
    end: tuple[int, int]

    def __init__(self, start: tuple[int, int], end: tuple[int, int]):
        assert (
            start != end
        ), f"{self.__class__.__qualname__}.__init__: start and end must be different but received {start} for both"
        sx, sy = start
        ex, ey = end
        if sx > ex or (sx == ex and sy > ey):
            temp = start
            start = end
            end = temp
            pass
        self.start = start
        self.end = end
        pass

    @classmethod
    def from_points(cls, x0: int, y0: int, x1: int, y1: int) -> "Edge":
        return Edge((x0, y0), (x1, y1))

    def other_end(self, *args) -> Optional[tuple[int, int]]:
        x = None
        y = None
        if len(args) == 2 and all(isinstance(arg, int) for arg in args):
            x = args[0]
            y = args[1]
            pass
        elif (
            len(args) == 1
            and isinstance(args[0], tuple)
            and all(isinstance(a, int) for a in args[0])
        ):
            x, y = args[0]
            pass
        assert (
            x is not None and y is not None
        ), f"{self.__class__.__qualname__}.other_end: x and y must either be given as a tuple or two ints but received args {args}"
        pt = (x, y)
        if pt == self.start:
            return self.end
        elif pt == self.end:
            return self.start
        else:
            return None

    def to_list(self) -> list[tuple[int, int]]:
        return list(self)

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __eq__(self, value):
        return (
            isinstance(value, Edge)
            and self.start == value.start
            and self.end == value.end
        )

    def __contains__(self, elmt) -> bool:
        return (
            isinstance(elmt, tuple)
            and len(elmt) == 2
            and all(isinstance(e, int) for e in elmt)
            and (self.start == elmt or self.end == elmt)
        )

    def __iter__(self) -> Generator[tuple[int, int], None, None]:
        for pt in [self.start, self.end]:
            yield pt
            pass
        pass

    def miny(self) -> int:
        _, y0 = self.start
        _, y1 = self.end
        return min(y0, y1)

    def vector(self) -> np.ndarray:
        start = np.array(self.start)
        end = np.array(self.end)
        return end - start

    def __lt__(self, other) -> bool:
        assert isinstance(
            other, self.__class__
        ), f"{self.__class__.__qualname__}.__lt__: cannot compare {self} to {other} of type {type(other)}"

        def cmp_cartesian(pt1: tuple[int, int], pt2: tuple[int, int]) -> bool:
            pt3 = (pt1[1], pt1[0])
            pt4 = (pt2[1], pt2[0])
            return pt3 < pt4

        return cmp_cartesian(self.start, other.start) and cmp_cartesian(
            self.end, other.end
        )

    pass


def unit_vector(vector):
    """Returns the unit vector of the vector."""
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """Returns the angle in radians between vectors 'v1' and 'v2'::

    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


class AbstractSelection(abc.ABC):
    def __init__(self):
        self.cn = self.__class__.__qualname__

    def surrounding(self, x: int, y: int) -> set[tuple[int, int]]:
        pts = [
            (x + i, y + j)
            for i, j in [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]
        ]
        pts = [(x, y) for x, y in pts if (x, y) in self.get_cells()]
        return set(pts)

    def is_connected(self) -> bool:
        cells = self.get_cells()
        x, y = next(iter(cells))
        seen = set([(x, y)])
        selection = set([(x, y)])
        bfs(x, y, selection, seen, self.surrounding)
        return selection == cells

    @classmethod
    @abc.abstractmethod
    def from_implicit(
        cls, implicit: Union[list[list[bool]], np.ndarray], minx=0, miny=0
    ) -> Self:
        pass

    def invert(self) -> Self:
        implicit = self.get_implicit()
        inverted = [[not cell for cell in row] for row in implicit]
        xmin, _ = self.x_limits()
        ymin, _ = self.y_limits()
        return self.__class__.from_implicit(inverted, minx=xmin, miny=ymin)

    def get_edge_counts(self) -> dict[frozenset[Edge], int]:
        def edges(x, y) -> set[frozenset[Edge]]:
            es = set()
            for i, j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                es.add(Edge((x, y), (x + i, y + j)))
                # [(x, y), (x + i, y + j)]))
                x = x + i
                y = y + j
                pass
            return es

        edge_counts = {}

        for x, y in self.get_cells():
            xy_edges = edges(x, y)
            for e in xy_edges:
                if e not in edge_counts:
                    edge_counts[e] = 0
                    pass
                edge_counts[e] += 1
                pass
            pass
        return edge_counts

    def get_outer_boundary(self) -> Optional[list[tuple[int, int]]]:
        """Gives a line that would draw a boundary around the given selection, assuming that cell (x, y) is bounded by box

        (x, y) ------ (x + 1, y)
           |                |
           |  cell (x, y)   |
           |                |
        (x, y + 1) -- (x + 1, y + 1)

        Returns:
            Optional[list[tuple[int, int]]]: a list of points that make up the boundary
        """
        if not self.is_connected():
            return None

        edge_counts = self.get_edge_counts()
        single_edges = set(e for e, count in edge_counts.items() if count == 1)
        # print(single_edges)
        edge_verts = set(chain.from_iterable([e.to_list() for e in single_edges]))
        # print("Edge verts:", edge_verts)

        edge_selection = ManhattanSelection(edge_verts, single_edges)
        boundaries = edge_selection.contiguous_selections()
        # print("Boundaries", boundaries, len(boundaries))
        arry = np.array([s for s in boundaries])
        # get the contiguous boundary with the largest number of points -- necessarily any holes must have less points
        sorting = np.argsort(np.array([len(s) for s in arry]))
        sarry = arry[sorting]
        # print("Array", sarry)
        return self._boundary(single_edges, sarry, -1)

    def get_boundaries(self) -> Optional[list[list[tuple[int, int]]]]:
        if not self.is_connected():
            return None

        edge_counts = self.get_edge_counts()
        single_edges = set(e for e, count in edge_counts.items() if count == 1)
        edge_verts = set(chain.from_iterable([e.to_list() for e in single_edges]))
        edge_selection = ManhattanSelection(edge_verts, single_edges)
        boundary_edges = edge_selection.contiguous_selections()
        boundarrays = np.array([s for s in boundary_edges])
        # sort in descending order of length
        sorting = np.argsort(np.array([-len(s) for s in boundarrays]))
        boundarrays = boundarrays[sorting]

        boundaries = []
        for i in range(len(boundarrays)):
            boundary = self._boundary(single_edges, boundarrays, i)
            if boundary is not None:
                boundaries.append(boundary)
                pass
            pass
        return boundaries

    def _boundary(self, _single_edges, sarry, index):
        edge_verts = sarry[index]
        single_edges = {
            e for e in _single_edges if e.start in edge_verts and e.end in edge_verts
        }
        # if len(boundaries) == 1:
        y, x = min([(y, x) for x, y in edge_verts])
        line = []
        line.append((x, y))
        x0, y0 = x, y
        seen = set(line)
        seen_edges = set()
        last_edge = None
        while seen_edges != single_edges:
            try:
                next_edges = np.array(
                    [e for e in single_edges if (x0, y0) in e and e not in seen_edges]
                )
                if len(next_edges) == 1:
                    next_edge = next_edges[0]
                elif last_edge and len(next_edges) > 0:
                    sorting = np.argsort(
                        np.array(
                            [
                                angle_between(last_edge.vector(), e.vector())
                                for e in next_edges
                            ]
                        )
                    )
                    next_edges = next_edges[sorting]
                    next_edge = next_edges[0]
                    pass
                elif not last_edge and len(next_edges) > 0:
                    sorting = np.argsort(np.array([e.miny() for e in next_edges]))
                    next_edges = next_edges[sorting]
                    next_edge = next_edges[0]
                    pass
                elif len(next_edges) == 0:
                    break
                pass
            except ValueError:
                break
            seen_edges.add(next_edge)
            other_end = next_edge.other_end(x0, y0)
            seen.add(other_end)
            line.append(other_end)
            x0, y0 = other_end
            last_edge = next_edge
            pass
        return line

    def contiguous_selections(self) -> set[frozenset[tuple[int, int]]]:
        selections = set()
        seen_points = set()
        cells = self.get_cells()

        for x, y in cells:
            if cells == seen_points:
                break
            if (x, y) not in seen_points:
                seen_points.add((x, y))
                s = set([(x, y)])
                bfs(x, y, s, seen_points, self.surrounding)
                # print(s)
                selections.add(frozenset(s))
                pass
            pass
        return selections

    def get_implicit(self) -> list[list[bool]]:
        xmin, xmax = self.x_limits()
        ymin, ymax = self.y_limits()
        cells = self.get_cells()
        return [
            [(x, y) in cells for x in range(xmin, xmax + 1)]
            for y in range(ymin, ymax + 1)
        ]

    def to_image(
        self,
        square_size=10,
        only_outer_boundary: bool = True,
        blank_color: RGBAColor = RGBAColor.from_hex("#FFFFFF"),
        select_color: RGBAColor = RGBAColor.from_hex("#69edff"),
        outline_color: RGBAColor = RGBAColor.from_hex("#000000"),
        selection_outline_color: RGBAColor = RGBAColor.from_hex("#00ffbf"),
        insetx: int = 15,
        insety: int = 15,
    ) -> Image.Image:
        implicit = self.get_implicit()
        # blank_color = RGBAColor.from_hex("#FFFFFF")
        # select_color = RGBAColor.from_hex("#69edff")
        # print(implicit)
        rgb_colors = [
            [select_color if selected else blank_color for selected in row]
            for row in implicit
        ]
        img = rgbcolors_to_image(rgb_colors, square_size=square_size, mode="RGBA")
        full_image = Image.new(
            mode="RGBA",
            size=(img.width + insetx * 2, img.height + insety * 2),
            color=blank_color.rgba_tuple(),
        )
        full_image.paste(img, box=(insetx, insety))
        draw = ImageDraw.Draw(full_image)

        draw.rectangle(
            [(insetx, insety), (insetx + img.width, insety + img.height)],
            outline=outline_color.rgba_tuple(),
        )

        def resize_points(line):
            return [
                (x * square_size + insetx, y * square_size + insety) for x, y in line
            ]

        # selection_outline_color = RGBAColor.from_hex("#00ffbf")
        if only_outer_boundary:
            line = self.get_outer_boundary()
            if line:
                # line = [(x * square_size + 15, y * square_size + 15) for x, y in line]
                draw.line(
                    resize_points(line),
                    fill=selection_outline_color.rgba_tuple(),
                    width=1,
                )
                pass
            pass
        else:
            lines = self.get_boundaries()
            if lines:
                for line in lines:

                    draw.line(
                        resize_points(line),
                        fill=selection_outline_color.rgba_tuple(),
                        width=1,
                    )

        return full_image

    def plot_selection(self) -> str:
        xmin, xmax = self.x_limits()
        ymin, ymax = self.y_limits()
        everything = [
            [(x, y) in self.get_cells() for x in range(xmax + 1)]
            for y in range(ymax + 1)
        ]
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


def from_implicit(cls, implicit: Union[list[list[bool]], np.ndarray], minx=0, miny=0):
    if isinstance(implicit, list):
        assert (
            implicit
        ), f"{cls.__qualname__}.from_implicit: implicit must be non-empty!"
        width = len(implicit[0])
        assert all(
            len(row) == width for row in implicit
        ), f"{cls.__qualname__}.from_implicit: implicit's rows must all be the same width {width}"
        height = len(implicit)
    # # must be an np.ndarray
    # width, height = implicit.shape
    # print(list(enumerate(implicit)))
    return cls(
        [
            (minx + x, miny + y)
            for y, row in enumerate(implicit)
            for x, cell in enumerate(row)
            if cell
        ]
    )


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
                return (
                    isinstance(value, set) or isinstance(value, frozenset)
                ) and self.selected_cells == value

        pass

    @classmethod
    def from_implicit(
        cls, implicit: Union[list[list[bool]], np.ndarray], minx=0, miny=0
    ):
        # if isinstance(implicit, list):
        #     assert implicit, f"{cls.__qualname__}.from_implicit: implicit must be non-empty!"
        #     width = len(implicit[0])
        #     assert all(len(row) == width for row in implicit), f"{cls.__qualname__}.from_implicit: implicit's rows must all be the same width {width}"
        #     height = len(implicit)
        # else:
        #     # must be an np.ndarray
        #     width, height = implicit.shape
        #     print(enumerate(implicit))
        #     pass
        # return ImmutableSelection([(minx + x, miny + y) for y, row in enumerate(implicit) for x, cell in enumerate(row) if cell])
        return from_implicit(cls, implicit, minx=minx, miny=miny)

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

    def union(self, other: Union["Selection", set[tuple[int, int]]]) -> Self:
        if isinstance(other, set):
            self.selected_cells = self.selected_cells.union(other)
            pass
        else:
            self.selected_cells = self.selected_cells.union(other.selected_cells)
            pass
        return self

    @classmethod
    def from_implicit(
        cls, implicit: Union[list[list[bool]], np.ndarray], minx=0, miny=0
    ):
        # if isinstance(implicit, list):
        #     assert implicit, f"{cls.__qualname__}.from_implicit: implicit must be non-empty!"
        #     width = len(implicit[0])
        #     assert all(len(row) == width for row in implicit), f"{cls.__qualname__}.from_implicit: implicit's rows must all be the same width {width}"
        #     height = len(implicit)
        # # # must be an np.ndarray
        # # width, height = implicit.shape
        # # print(list(enumerate(implicit)))
        # return Selection([(minx + x, miny + y) for y, row in enumerate(implicit) for x, cell in enumerate(row) if cell])
        return from_implicit(Selection, implicit, minx=minx, miny=miny)

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


class ManhattanSelection(Selection):
    # Manhattan selection where you can only move N, S, E, W and only some edges exist
    # Mostly for calculating boundaries
    def __init__(self, selected, edges: set[Edge]):
        super().__init__(selected)
        self.edges = edges

    @override
    def surrounding(self, x, y):
        # print("ManhattanSelection")
        pts = [(x + i, y + j) for i, j in [(-1, 0), (0, -1), (0, 1), (1, 0)]]
        pts = [
            (x0, y0)
            for x0, y0 in pts
            if (x0, y0) in self.get_cells() and Edge((x, y), (x0, y0)) in self.edges
        ]
        return set(pts)


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
        return f"{self.cn}({self._start}{end})"


# Might want a specific subclass that does selections too, but this is probably good for now?
# class GridSelection:


if __name__ == "__main__":
    sel = Selection()
    sel.add(0, 1).add(1, 0).add(2, 0).add(1, 2).add(0, 3)
    print(sel)

    for x, y in sel:
        print((x, y))
        pass

    sel1 = Selection()
    sel1.add(0, 0)
    sel1.add(1, 0)
    sel1.add(0, 1)
    print(sel1)
    print(sel1.get_outer_boundary())
    print(sel1.get_edge_counts())

    img = sel1.to_image(square_size=30, only_outer_boundary=False)
    img.save("test_selection.png")

    sel2 = Selection()
    sel2.add(0, 0)
    sel2.add(1, 1)

    print(sel2.get_outer_boundary())
    print(sel2.get_edge_counts())

    img = sel2.to_image(square_size=30, only_outer_boundary=False)
    img.save("test_selection2.png")

    sel3 = sel2.invert()
    print(sel3.get_outer_boundary())
    print(sel3.get_edge_counts())

    sel4 = Selection()
    sel4.add(0, 0)
    sel4.add(1, 0)
    sel4.add(2, 0)
    sel4.add(0, 1)
    sel4.add(2, 1)
    sel4.add(0, 2)
    sel4.add(1, 2)
    sel4.add(2, 2)
    img = sel4.to_image(square_size=30, only_outer_boundary=False)
    img.save("test_selection4.png")

    sel5 = Selection()
    sel5.add(0, 0)
    sel5.add(2, 0)
    sel5.add(1, 1)
    sel5.add(0, 2)
    sel5.add(2, 2)
    img = sel5.to_image(square_size=30, only_outer_boundary=False)
    img.save("test_selection5.png")

    img = sel5.to_image(
        square_size=30,
        only_outer_boundary=False,
        blank_color=RGBAColor(0, 0, 0, 0),
        outline_color=RGBAColor(0, 0, 0, 0),
        select_color=RGBAColor(0, 0, 0, 0),
        insetx=1,
        insety=1,
    )
    img.save("test_selection5_1.png")
    implicit6 = [[True for _ in range(10)] for _ in range(10)]
    implicit6[2][2] = False
    implicit6[5][5] = False
    implicit6[4][4] = False
    implicit6[4][5] = False
    implicit6[4][6] = False
    implicit6[9][0] = False
    sel6 = Selection.from_implicit(implicit6)
    img = sel6.to_image(square_size=30, only_outer_boundary=False)
    img.save("test_selection6.png")

    implicit7 = np.zeros((10, 10))
    implicit7[2, 2] = 1
    implicit7[5, 5] = 1
    implicit7[4, 4:7] = 1
    implicit7[9, 0] = 1
    implicit7 = implicit7 == 0
    sel7 = Selection.from_implicit(implicit7)
    img = sel7.to_image(square_size=30, only_outer_boundary=False)
    img.save("test_selection7.png")
