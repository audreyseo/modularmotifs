from enum import Enum
from modularmotifs.core.design import RGBAColor
from modularmotifs.core.design import Design, Color, Motif
from modularmotifs.core.pixel_grid import PixelGrid
from modularmotifs.core.util import rgbcolors_to_image
import abc
from typing import Generator, Optional, Tuple, Self, Union
from PIL import Image
from dataclasses import dataclass

class Colorization(PixelGrid):
    """ Class that contains the information for how to colorize a particular design
    """
    # the design that this colorization colorizes
    _d: Design
    # the colors that this colorization uses
    _colors: list[RGBAColor]
    _cname: str

    def __init__(self, d: Design, colors: list[RGBAColor]):
        self._cname = self.__class__.__qualname__
        self._d = d
        self._colors = colors
        pass

    def width(self) -> int:
        return self._d.width()

    def height(self) -> int:
        return self._d.height()
    # @abc.abstractmethod
    # def assign_color(self, x: int, y: int) -> Self:
    #     assert (self._d.in_range(x, y)), f"Colorization.assign_color: coordinates ({x}, {y}) out of range of design {d}"
    #     return self

    @abc.abstractmethod
    def get_color(self, x: int, y: int) -> RGBAColor:
        assert self._d.in_range(x, y), f"{self.get_color.__qualname__}: coordinates ({x}, {y}) out of range of design {self._d}"
        pass

    @abc.abstractmethod
    def complete(self) -> bool:
        pass
    
    def get_rgba(self, x, y):
        return self.get_color(x, y)

    @abc.abstractmethod
    def to_image(self) -> Image.Image:
        pass
    
    def in_color_range(self, i: int) -> bool:
        return 0 <= i < len(self._colors)
    
    @abc.abstractmethod
    def _reassign_colors_from_indices(self) -> Self:
        pass
    
    def row_colors(self, row: int) -> list[Color]:
        return self._d.row_colors(row)
        
    def swap_colors(self, i: int, j: int) -> Self:
        assert self.in_color_range(i) and self.in_color_range(j), f"{self._cname}.swap_colors: color indices {i} and {j} may be out of range of colors {self._colors}"
        temp = self._colors[i]
        self._colors[i] = self._colors[j]
        self._colors[j] = temp
        self._reassign_colors_from_indices()
        return self
    
    def add_color(self, c: RGBAColor) -> int:
        self._colors.append(c)
        # returns the index of the newly added color
        return len(self._colors) - 1
    
    def remove_color(self, i: int) -> RGBAColor:
        return self._colors.pop(i)

    pass

class TwoColorsPerRow(Colorization):
    """ Allows assignment of two colors per row for a particular design
    """
    # print(__qualname__)
    # the colors for each row
    _foreground: list[RGBAColor]
    _fg: list[int]
    _background: list[RGBAColor]
    _bg: list[int]
    _treat_invis_as_bg: bool

    def __init__(self, d: Design, colors: list[RGBAColor]):
        super().__init__(d, colors)
        self._init_lists()
        self._treat_invis_as_bg = False
        pass
    
    def set_treat_invis_as_bg(self, b: bool) -> None:
        self._treat_invis_as_bg = b
        pass
    
    def _init_lists(self, _h=None):
        h = _h or self._d.height()
        # Initialize the foreground and background lists to be length h, one fg/bg color per row
        self._foreground = [ None for _ in range(h) ]
        self._background = [ None for _ in range(h) ]
        self._fg = [None for _ in range(h)]
        self._bg = [None for _ in range(h)]
        pass

    def set_fg(self, row: int, c: Union[int, RGBAColor]) -> Self:
        assert 0 <= row < self._d.height(), f"{self.set_fg.__qualname__}: row {row} is out of range of design {self._d}"
        assert isinstance(c, RGBAColor) or 0 <= c < len(self._colors), f"{self.set_fg.__qualname__}: color index {c} is out of range of color list {self._colors}"

        if isinstance(c, int):
            self._foreground[row] = self._colors[c]
            self._fg[row] = c
            pass
        else:
            self._foreground[row] = c
            self._fg[row] = self._colors.index(c)
        return self

    def set_bg(self, row: int, c: Union[int, RGBAColor]) -> Self:
        assert 0 <= row < self._d.height(), f"{self.set_bg.__qualname__}: row {row} is out of range of design {self._d}"
        assert isinstance(c, RGBAColor) or 0 <= c < len(self._colors), f"{self.set_bg.__qualname__}: color index {c} is out of range of color list {self._colors}"

        if isinstance(c, int):
            self._background[row] = self._colors[c]
            self._bg[row] = c
            pass
        else:
            self._background[row] = c
            self._bg[row] = self._colors.index(c)
            pass
        return self

    def set(self, row: int, fg: Union[int, RGBAColor], bg: Union[int, RGBAColor]) -> Self:
        return self.set_fg(row, fg).set_bg(row, bg)

    
    def complete(self) -> bool:
        super().complete()
        # need two colors per row
        return len(self._foreground) == self._d.height() and len(self._background) == self._d.height() and all(fg is not None for fg in self._foreground) and all(bg is not None for bg in self._background)

    def get_color(self, x: int, y: int) -> RGBAColor:
        super().get_color(x, y)
        
        c = self._d.get_color(x, y)
        if not self._treat_invis_as_bg:
            assert c != Color.INVIS, f"{self.get_color.__qualname__}: color of design {self._d} at ({x}, {y}) is invisible but should be either foreground or background"
            pass
        
        if c == Color.FORE:
            return self.get_fg(y)
        elif c == Color.BACK:
            return self.get_bg(y)
        elif c == Color.INVIS and self._treat_invis_as_bg:
            return self.get_bg(y)
        pass

    
    def _reassign_colors_from_indices(self) -> Self:
        for y, i in enumerate(self._fg):
            if i:
                self.set_fg(y, i)
            else:
                self._foreground[y] = None
            pass
        for y, i in enumerate(self._bg):
            if i:
                self.set_bg(y, i)
                pass
            else:
                self._background[y] = None
                pass
            pass
        
        return self
    
    # def to_image(self) -> Image.Image:
    #     img = Image.new

    def get_fg(self, row: int) -> RGBAColor:
        if not self._foreground[row]:
            return self._d.fore_color
        return self._foreground[row]
    
    def get_bg(self, row: int) -> RGBAColor:
        if not self._background[row]:
            return self._d.back_color
        return self._background[row]

    def __iter__(self) -> Generator[Tuple[RGBAColor, RGBAColor], None, None]:
        assert len(self._foreground) == len(self._background), f"{self.__iter__.__qualname__}: foreground and background list lengths should be the same, but they differ: {len(self._foreground)} vs. {len(self._background)}"
        for i in range(len(self._foreground)):
            yield (self._foreground[i], self._background[i])
            pass
        pass

    def to_image(self, square_size=10) -> Image.Image:
        colors = [[self._foreground[y] if c == Color.FORE else self._background[y] for c, x, y in r] for r in self._d]
        return rgbcolors_to_image(colors, square_size=square_size)
        
        # for r in self._d:
        # for c, x, y in r:
        # col = self._foreground[y] if c == Color.FORE else self._background[y]
        # print(col, x, y)
                

        
        # w, h = self._d.width(), self._d.height()
        # img = Image.new("RGB", (w * square_size, h * square_size))
        # pixels = img.load()
        # for y in range(h):
        #     col1 = self._foreground[y]
        #     col2 = self._background[y]
        #     for x in range(w):
        #         # default to the background color
        #         col = col2
        #         if self._d.get_color(x, y) == Color.FORE:
        #             # otherwise, make it the foreground color
        #             col = col1
        #             pass
        #         for i in range(square_size):
        #             for j in range(square_size):
        #                 pixels[x * square_size + i, y * square_size + j] = col.tuple()
        #                 pass
        #             pass
        #         pass
        #     pass
        # return img
                        
            
    pass

@dataclass
class Change:
    _perm_min = 1
    _perm_max = 6
    _necc_min = 1
    _necc_max = 2
    
    class Permissions(Enum):
        SAME = 1
        CHANGE_FG = 2
        CHANGE_BG = 3
        CHANGE_EITHER = 4
        CHANGE_OR = 5
        CHANGE_BOTH = 6
        
        
        def to_str(self) -> str:
            match self:
                case self.__class__.SAME:
                    return "SAME"
                case self.__class__.CHANGE_BG:
                    return "CHANGE_BG"
                case self.__class__.CHANGE_BOTH:
                    return "CHANGE_BOTH"
                case self.__class__.CHANGE_FG:
                    return "CHANGE_FG"
                case self.__class__.CHANGE_OR:
                    return "CHANGE_OR"
                case self.__class__.CHANGE_EITHER:
                    return "CHANGE_EITHER"
        
        def to_tuples(self) -> set[tuple[int, int]]:
            match self:
                case self.__class__.SAME:
                    return set([(0, 0)])
                case self.__class__.CHANGE_FG:
                    return set([(1, 0)])
                case self.__class__.CHANGE_BG:
                    return set([(0, 1)])
                case self.__class__.CHANGE_EITHER:
                    return set([(1, 0), (0, 1)])
                case self.__class__.CHANGE_OR:
                    return set([(1, 0), (0, 1), (1, 1)])
                case self.__class__.CHANGE_BOTH:
                    return set([(1, 1)])
        
        @classmethod
        def from_int(cls, i: int):
            assert Change._perm_min <= i <= Change._perm_max, f"Cannot convert {i} to {cls.__qualname__}"
            match i:
                case 1:
                    return cls.SAME
                case 2:
                    return cls.CHANGE_FG
                case 3:
                    return cls.CHANGE_BG
                case 4:
                    return cls.CHANGE_EITHER
                case 5:
                    return cls.CHANGE_OR
                case 6:
                    return cls.CHANGE_BOTH
        
        def __str__(self):
            match self.value:
                case 1:
                    return "Same(1)"
                case 2:
                    return "ChangeFG(2)"
                case 3:
                    return "ChangeBG(3)"
                case 4:
                    return "ChangeEither(4)"
                case 5:
                    return "ChangeOr(5)"
                case 6:
                    return "ChangeBoth(6)"
            pass
        
        def __repr__(self):
            return str(self)
        
    class Necessity(Enum):
        MUST = 1
        MAY = 2
        
        def to_str(self) -> str:
            match self:
                case self.__class__.MUST:
                    return "MUST"
                case self.__class__.MAY:
                    return "MAY"
                
        
        @classmethod
        def from_int(cls, i: int) -> Self:
            assert Change._necc_min <= i <= Change._necc_max, f"Cannot convert {i} to {cls.__qualname__}"
            match i:
                case 1:
                    return cls.MUST
                case 2:
                    return cls.MAY
        
        def __str__(self):
            match self.value:
                case 1:
                    return "Must(1)"
                case 2:
                    return "May(2)"
            pass
        
        def __repr__(self):
            return str(self)
    
    row: int
    perms: Permissions
    necc: Necessity
    
    def __init__(self, row: int, perms: Permissions, necc: Necessity):
        self.row = row
        self.perms = perms
        self.necc = necc
        pass
    
    def must(self):
        return self.necc == self.Necessity.MUST
    
    def possibilities(self):
        match self.necc:
            case self.Necessity.MUST:
                return self.perms.to_tuples()
            case self.Necessity.MAY:
                return set([(0, 0)]).union(self.perms.to_tuples())
    
    def change_fg_ok(self) -> bool:
        match self.perms:
            case self.Permissions.SAME:
                return False
            case self.Permissions.CHANGE_BG:
                return False
            case self.Permissions.CHANGE_FG:
                return True
            case self.Permissions.CHANGE_BOTH:
                return True
            case self.Permissions.CHANGE_OR:
                return True
            case self.Permissions.CHANGE_EITHER:
                return True
    
    def change_bg_ok(self) -> bool:
        match self.perms:
            case self.Permissions.SAME:
                return False
            case self.Permissions.CHANGE_BG:
                return True
            case self.Permissions.CHANGE_FG:
                return False
            case self.Permissions.CHANGE_BOTH:
                return True
            case self.Permissions.CHANGE_OR:
                return True
            case self.Permissions.CHANGE_EITHER:
                return True
            
                
    
    @classmethod
    def from_ints(cls, r: int, p: int, n: int) -> 'Change':
        # while n <= 1:
        #     n += cls._necc_max
        #     pass
        # while p <= 1:
        #     p += cls._necc_max
        n = ((n - 1) % cls._necc_max) + 1
        p = ((p - 1) % cls._perm_max) + 1
        return Change(r, cls.Permissions.from_int(p), cls.Necessity.from_int(n))

class PrettierTwoColorRows(TwoColorsPerRow):
    
    def __init__(self, d: Design, colors: list[RGBAColor], changes: list[Change]):
        self._changes = changes
        super().__init__(d, colors)
        pass
    
    def _init_lists(self):
        h = len(self._changes)
        super()._init_lists(_h = h)
        pass
    
    def reset(self):
        self._init_lists()
    
    def change_height(self) -> int:
        return len(self._changes)
    
    def recalculate(self) -> None:
        for i in range(self.height()):
            self._foreground[i] = self._colors[self._fg[i]]
            self._background[i] = self._colors[self._bg[i]]
            pass
    
    def last_fg(self, row: Optional[int] = None) -> int:
        row = row or (self.height() - 1)
        while self._fg[row] is None and row > 0:
            row -= 1
            pass
        return self._fg[row]
    
    def last_bg(self, row: Optional[int] = None) -> int:
        row = row or (self.height() - 1)
        while self._bg[row] is None and row > 0:
            row -= 1
            pass
        return self._bg[row]
    
    def last(self, row: Optional[int] = None) -> tuple[Optional[RGBAColor], Optional[RGBAColor]]:
        return self.last_fg(row), self.last_bg(row)
    
    # def get_color(self, x: int, y: int) -> RGBAColor:
    #     # TODO: FIX
    #     return self._d.get_rgba(x, y)
    
    def _insert_fg_bg(self, index: int, fg: Optional[RGBAColor] = None, bg: Optional[RGBAColor] = None):
        fg_index = None if fg is None else self._colors.index(fg)
        bg_index = None if bg is None else self._colors.index(bg)
        
        self._fg.insert(index, fg_index)
        self._bg.insert(index, bg_index)
        self._foreground.insert(index, fg)
        self._background.insert(index, bg)
        
    def _remove_fg_bg(self, index: int) -> tuple[int, int, Optional[RGBAColor], Optional[RGBAColor]]:
        return self._fg.pop(index), self._bg.pop(index), self._foreground.pop(index), self._background.pop(index)

    def get_change(self, row: int) -> Change:
        return self._changes[row]
    
    def set_changes(self, c: Change, row: int) -> Optional[Change]:
        old_change = self._changes[row]
        self._changes[row] = c
        return old_change
    
    def add_changes(self, c: Change, row: Optional[int] = None, fg: Optional[RGBAColor] = None, bg: Optional[RGBAColor] = None) -> int:
        last = row or len(self._changes)
        self._insert_fg_bg(last, fg, bg)
        
        if last < len(self._changes):
            self._changes.insert(last, c)
        else:
            self._changes.append(c)
            pass
        return last
        
    def remove_changes(self, row: Optional[int] = None) -> tuple[int, Change, Optional[RGBAColor], Optional[RGBAColor]]:
        last = row or len(self._changes) - 1
        _, _, fg, bg = self._remove_fg_bg(last)
        return last, self._changes.pop(last), fg, bg

    pass    
    
    
        
        

if __name__ == "__main__":
    twocols = TwoColorsPerRow(Design(1, 1), [RGBAColor.from_hex("#FFFF00")])
    twocols.set_bg(0, 0)
    
    change = [Change(0, Change.Permissions.from_int(2), Change.Necessity.MUST)] + [Change.from_ints(1, 1, 1), Change.from_ints(2, 2, 2)]
    print(change)
    print([c.possibilities() for c in change])
    prettier = PrettierTwoColorRows(Design(3, 3), [RGBAColor.from_hex("#FFFF00"), RGBAColor.from_hex("#FF00FF"), RGBAColor.from_hex("#00FFFF")], change)
    print(prettier)
    
    
