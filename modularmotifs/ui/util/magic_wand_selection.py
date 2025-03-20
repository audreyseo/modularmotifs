from modularmotifs.core.design import Design
from modularmotifs.core.pixel_grid import PixelGrid
from modularmotifs.core.rgb_color import RGBAColor
from modularmotifs.ui.util.selection import Selection

def magic_wand_select(p: PixelGrid, x: int, y: int) -> Selection:
    s = Selection()
    def bfs(c: RGBAColor, x: int, y: int, seen: set[tuple[int, int]]):
        new = set()
        for i in [-1, 0, 1]:
            x0 = x + i
            for j in [-1, 0, 1]:
                if (j == 0 and i == 0):
                    continue
                y0 = y + j
                if (x0, y0) not in seen and p.in_range(x0, y0) and p.get_rgba(x0, y0) == c:
                    new.add((x0, y0))
                    pass
                pass
            pass
        s.union(new)
        seen = seen.union(new)
        for x1, y1 in new:
            seen = bfs(c, x1, y1, seen)
            pass
        return seen
    if not p.in_range(x, y):
        return s
    c = p.get_rgba(x, y)
    s.add(x, y)
    seen = set()
    bfs(c, x, y, seen)
    
    return s

if __name__ == "__main__":
    from modularmotifs.motiflibrary.examples import motifs
    d = Design(10, 10)
    """
1010000000
0100000000
1010000000
0001010000
0000100000
0001010000
0000000000
0000000000
0000000000
0000000000
"""
    
    d.add_motif(motifs["x-3x3"], 0, 0)
    d.add_motif(motifs["x-3x3"], 3, 3)
    
    print(magic_wand_select(d, 0, 0))
    print(magic_wand_select(d, 1, 0))
                