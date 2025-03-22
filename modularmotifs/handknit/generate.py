from modularmotifs.core import Design, Motif
from modularmotifs.core.algo.fair_isle import (
    fair_isle_colorization_new,
    generate_changes,
)
from modularmotifs.core.colorization import PrettierTwoColorRows
from modularmotifs.core.pixel_grid import PixelGrid
from PIL import Image, ImageDraw, ImageFont
from modularmotifs.motiflibrary.examples import motifs
from modularmotifs.core.rgb_color import RGBAColor


def draw_grid(
    draw,
    thinner: int,
    thicker: int,
    width: int,
    height: int,
    w: int,
    h: int,
    cell_size: int,
    width_offset: int,
    height_offset: int,
    line_color: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> None:
    x = width_offset
    y0 = height_offset
    y1 = h - height_offset  # + thicker
    fontsize = cell_size * 0.6
    font_x_offset = int(cell_size * 0.1)
    font_y_offset = int(cell_size * 0.1)
    print(fontsize)
    font = ImageFont.truetype("Helvetica.ttc", size=fontsize)

    def x_text(i: int, x: int, y: int, anchor: str):
        draw.text(
            (w - x - (cell_size // 2), y),
            text=str(i + 1),
            fill=line_color,
            font=font,
            anchor=anchor,
        )

    def y_text(i: int, x: int, y: int, anchor: str):
        draw.text(
            (x, h - y - (cell_size // 2)),
            text=str(i + 1),
            fill=line_color,
            font=font,
            anchor=anchor,
        )

    outer_line_offset = thinner // 2
    thinner_line_offset = thinner

    # draw.line([(x, y0 - outer_line_offset), (x, y1 + outer_line_offset)], width=thicker, fill=line_color)
    # draw.text((w - x - (cell_size // 2), y0), text=str(1), fill=line_color, font=font, anchor="md")
    x_text(0, x, y0, anchor="md")
    x_text(0, x, y1 + font_y_offset, anchor="ma")
    x += thicker + cell_size  # + (1 if thinner > 1 else 0)
    for i in range(1, width):
        line_size = thicker if (width - i) % 5 == 0 else thinner_line_offset
        draw.line([(x, y0), (x, y1)], width=line_size, fill=line_color)
        x_text(i, x, y0, anchor="md")
        x_text(i, x, y1 + font_y_offset, anchor="ma")
        # draw.text((w - x - (cell_size // 2), y0), text=str(i + 1), fill=line_color, font=font, anchor="md")
        # draw.text((w - x - (cell_size // 2), y1), text=str(i+1), fill=line_color, font=font, anchor="ma")
        x += line_size + cell_size
        pass
    # draw.line([(x, y0 - outer_line_offset), (x, y1 + outer_line_offset)], width=thicker, fill=line_color)

    y = height_offset
    x0 = width_offset
    x1 = w - width_offset  # + thicker
    # draw.line([(x0 - outer_line_offset, y), (x1 + outer_line_offset, y)], width=thicker, fill=line_color)
    y_text(0, x0 - font_x_offset, y, anchor="rm")
    y_text(0, x1 + font_x_offset, y, anchor="lm")
    y += thicker + cell_size
    for i in range(1, height):
        line_size = thicker if (height - i) % 5 == 0 else thinner
        draw.line([(x0, y), (x1, y)], width=line_size, fill=line_color)
        y_text(i, x0 - font_x_offset, y, anchor="rm")
        y_text(i, x1 + font_x_offset, y, anchor="lm")
        y += (thicker if (height - i) % 5 == 0 else thinner_line_offset) + cell_size
        # y += line_size + cell_size
        pass
    # draw.line([(x0 - outer_line_offset, y), (x1 + outer_line_offset, y)], width=thicker, fill=line_color)

    outer_line = []
    outer_line.append((x0 - outer_line_offset, y0 - outer_line_offset))
    outer_line.append((x0 - outer_line_offset, y1 + outer_line_offset))
    outer_line.append((x1 + outer_line_offset, y1 + outer_line_offset))
    outer_line.append((x1 + outer_line_offset, y0 - outer_line_offset))
    draw.polygon(outer_line, fill=None, outline=line_color, width=thicker)

    pass


def handknitting_instructions(p: PixelGrid, cell_size=20, thicker=2, thinner=1):
    thicker_lines_w = p.width() // 5
    thinner_lines_num = thicker_lines_w * 4 + (p.width() % 5)
    thicker_lines_h = p.height() // 5
    thinner_lines_h_num = (thicker_lines_h * 4) + (p.height() % 5)

    width_offset = round(cell_size * 1.5)
    height_offset = round(cell_size * 1.5)

    w = (
        p.width() * cell_size
        + thicker * thicker_lines_w
        + thinner * thinner_lines_num
        + 2 * width_offset
    )
    h = (
        p.height() * (cell_size)
        + thicker * thicker_lines_h
        + thinner * thinner_lines_h_num
        + 2 * width_offset
    )
    im = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(im)

    modulus = 0

    def get_j(j: int):
        return p.width() - j - 1

    def get_i(i: int):
        return p.height() - i - 1

    # y = height_offset + thicker
    # y = h - height_offset - cell_size
    y = height_offset + (thicker // 2) + (thinner // 2)
    for i in range(p.height()):
        # x = w - width_offset - cell_size
        x = width_offset + (thicker // 2) + (thinner // 2)
        # x = width_offset + thicker
        for j in range(p.width()):
            x_line_width = thicker if (get_j(j)) % 5 == modulus else thinner
            draw.rectangle(
                [(x, y), (x + cell_size, y + cell_size)],
                fill=p.get_rgba(j, i).rgba_tuple(),
                width=0,
            )
            # x -= cell_size + (thicker if (p.width() - 1 - j) % 5 == 4 else thinner)
            print(j, get_j(j), x_line_width)
            x += (
                cell_size + x_line_width
            )  # (thicker if (p.width() - j) % 5 == 4 else thinner)
            pass
        y_line_width = thicker if get_i(i) % 5 == modulus else thinner
        print(i, get_i(i), y_line_width)
        # y -= cell_size + (thicker if (p.height() - 1 - i) % 5 == 4 else thinner)
        y += (
            cell_size + y_line_width
        )  # (thicker if (p.height() - i) % 5 == 1 else thinner)
        pass
    draw_grid(
        draw,
        thinner,
        thicker,
        p.width(),
        p.height(),
        w,
        h,
        cell_size,
        width_offset,
        height_offset,
    )
    return im


if __name__ == "__main__":
    import design_examples.deer_scene as ds
    import design_examples.blah as blah
    import design_examples.tester as tester

    design = Design(9, 9)
    for i in [0, 3, 6]:
        for j in [0, 3, 6]:
            design.add_motif(motifs["x-3x3"], i, j)
            pass
        pass

    colors = ["#574AE2", "#222A68", "#654597", "#AB81CD", "#E2ADF2"]
    colors = [RGBAColor.from_hex(c) for c in colors]
    pretty = PrettierTwoColorRows(blah.x0, colors, generate_changes(blah.x0))
    pretty = PrettierTwoColorRows(design, colors, generate_changes(design))
    fair_isle_colorization_new(pretty)
    img = handknitting_instructions(pretty, cell_size=80, thicker=8, thinner=4)
    img.save("test_color.png")
    # img = handknitting_instructions(tester.x0, cell_size=40, thicker=4, thinner=2)
    # img.save("test.png")
    # img1 = handknitting_instructions(tester.x0, cell_size=20, thicker=2, thinner=1)
    # img1.save("test1.png")
    # img2 = handknitting_instructions(tester.x0, cell_size=80, thicker=8, thinner=4)
    # img2.save("test2.png")
    # img3 = handknitting_instructions(tester.x0, cell_size=40, thicker=2, thinner=1)
    # img3.save("test3.png")
    # img4 = handknitting_instructions(tester.x0, cell_size=80, thicker=4, thinner=1)
    # img4.save("test4.png")
