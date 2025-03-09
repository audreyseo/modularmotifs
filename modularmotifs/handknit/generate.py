from modularmotifs.core import Design, Motif
from modularmotifs.core.algo.fair_isle import fair_isle_colorization_new, generate_changes
from modularmotifs.core.colorization import PrettierTwoColorRows
from modularmotifs.core.pixel_grid import PixelGrid
from PIL import Image, ImageDraw, ImageFont
from modularmotifs.motiflibrary.examples import motifs
from modularmotifs.core.rgb_color import RGBAColor



def draw_grid(draw, thinner: int, thicker: int, width: int, height: int, w: int, h: int, cell_size: int, width_offset: int, height_offset: int, line_color: tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
    x = width_offset
    y0 = height_offset
    y1 = h - height_offset + thicker
    fontsize = cell_size * 0.6
    font_x_offset = int(cell_size * 0.1)
    font_y_offset = int(cell_size * 0.1)
    print(fontsize)
    font = ImageFont.truetype("Helvetica.ttc", size=fontsize)
    
    def x_text(i: int, x: int, y: int, anchor: str):
        draw.text((w - x - (cell_size // 2), y), text=str(i + 1), fill=line_color, font=font, anchor=anchor)
    def y_text(i: int, x: int, y: int, anchor: str):
        draw.text((x, h - y - (cell_size // 2)), text=str(i + 1), fill=line_color, font=font, anchor=anchor)
    
    draw.line([(x, y0), (x, y1)], width=thicker, fill=line_color)
    # draw.text((w - x - (cell_size // 2), y0), text=str(1), fill=line_color, font=font, anchor="md")
    x_text(0, x, y0, anchor="md")
    x_text(0, x, y1 + font_y_offset, anchor="ma")
    x += thicker + cell_size
    for i in range(1, width):
        line_size = thicker if (width - i) % 5 == 0 else thinner
        draw.line([(x, y0), (x, y1)], width=line_size, fill=line_color)
        x_text(i, x, y0, anchor="md")
        x_text(i, x, y1 + font_y_offset, anchor="ma")
        # draw.text((w - x - (cell_size // 2), y0), text=str(i + 1), fill=line_color, font=font, anchor="md")
        # draw.text((w - x - (cell_size // 2), y1), text=str(i+1), fill=line_color, font=font, anchor="ma")
        x += line_size + cell_size
        pass
    draw.line([(x, y0), (x, y1)], width=thicker, fill=line_color)
    
    y = height_offset
    x0 = width_offset
    x1 = w - width_offset + thicker
    draw.line([(x0, y), (x1, y)], width=thicker, fill=line_color)
    y_text(0, x0 - font_x_offset, y, anchor="rm")
    y_text(0, x1 + font_x_offset, y, anchor="lm")
    y += thicker + cell_size
    for i in range(1, height):
        line_size = thicker if (height - i) % 5 == 0 else thinner
        draw.line([(x0, y), (x1, y)], width=line_size, fill=line_color)
        y_text(i, x0 - font_x_offset, y, anchor="rm")
        y_text(i, x1 + font_x_offset, y, anchor="lm")
        y += line_size + cell_size
        pass
    draw.line([(x0, y), (x1, y)], width=thicker, fill=line_color)
    
    pass
    

def handknitting_instructions(p: PixelGrid, cell_size=20, thicker=2, thinner=1):
    thicker_lines_w = p.width() // 5
    thinner_lines_num = thicker_lines_w * 4 + (p.width() % 5)
    thicker_lines_h = p.height() // 5
    thinner_lines_h_num = (thicker_lines_h * 4) + (p.height() % 5)
    
    width_offset = round(cell_size * 1.5)
    height_offset = round(cell_size * 1.5)
    
    w = p.width() * cell_size + thicker * thicker_lines_w + thinner * thinner_lines_num + 2 * width_offset
    h = p.height() * (cell_size) + thicker * thicker_lines_h + thinner * thinner_lines_h_num + 2 * width_offset
    im = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(im)
    
    y = height_offset + thicker
    for i in range(p.height()):
        x = width_offset + thicker
        for j in range(p.width()):
            draw.rectangle([(x, y), (x + cell_size, y + cell_size)],
                           fill=p.get_rgba(j, i).rgba_tuple(),
                           width=0)
            x += cell_size + (thicker if (p.width() - 1 - j) % 5 == 4 else thinner)
            pass
        y += cell_size + (thicker if (p.height() - 1 - i) % 5 == 4 else thinner)
        pass
    draw_grid(draw, thinner, thicker, p.width(), p.height(), w, h, cell_size, width_offset, height_offset)
    return im

if __name__ == "__main__":
    import design_examples.deer_scene as ds
    design = Design(9, 9)
    for i in [0, 3, 6]:
        for j in [0, 3, 6]:
            design.add_motif(motifs["x-3x3"], i, j)
            pass
        pass
    
    colors = ["#574AE2", "#222A68", "#654597", "#AB81CD", "#E2ADF2"]
    colors = [RGBAColor.from_hex(c) for c in colors]
    pretty = PrettierTwoColorRows(design, colors, generate_changes(design))
    fair_isle_colorization_new(pretty)
    img = handknitting_instructions(pretty, cell_size=40, thicker=4, thinner=2)
    img.save("test.png")
    
