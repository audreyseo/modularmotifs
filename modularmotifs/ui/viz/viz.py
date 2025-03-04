"""Supports exporting designs to PNGs and viewing them"""

from PIL import Image
from modularmotifs.core.design import Design


def export_square(d: Design, res: int = 27) -> Image:
    """Exports a design to an image, with each
    stitch a 27x27 square

    Args:
        d (Design): Design to be exported
        res (int, optional): Dimensions of a stitch. Defaults to 27.

    Returns:
        Image: Image representing the design
    """
    w, h = d.width(), d.height()
    img = Image.new("RGBA", (w*res, h*res))
    for x in range(w):
        for y in range(h):
            rgba = d.get_rgba(x, y).to_tuple()
            for xi in range(res):
                for yi in range(res):
                    img.putpixel((x*res + xi, y*res + yi), rgba)
    return img

HEART_HEIGHT = 1/3
HEART_WIDTH = 1/3

def export_heart(d: Design, res: int = 27) -> Image:
    """Exports a design to an image, with each
    stitch a 27x27 heart

    Args:
        d (Design): Design to be exported
        res (int, optional): Dimensions of a stitch. Defaults to 27.

    Returns:
        Image: Image representing the design
    """
    w, h = d.width(), d.height()
    img = Image.new("RGBA", (w*res, h*res))
    for x in range(w*res):
        for y in range(h*res):
            img.putpixel((x, y), (255, 0, 0, 255))
    for x in range(w):
        for y in range(h):
            rgba = d.get_rgba(x, y).to_tuple()
            for xi in range(res):
                for yi in range(int(res + res * HEART_HEIGHT)):
                    if y == h-1 and yi >= res:
                        continue # off the image

                    if y > 0 and res * HEART_WIDTH <= xi < res * HEART_WIDTH * 2 and yi < res * HEART_HEIGHT:
                        continue # TODO: this is not a heart
                    if yi >= res:
                        if xi < res * HEART_WIDTH or xi >= res * HEART_WIDTH * 2:
                            continue
                        else:
                            pass # TODO: this is not a heart

                    print(x, y, xi, yi)
                    img.putpixel((x*res + xi, y*res + yi), rgba)
                    # pixels[y*res + yi][x*res + xi] = ((255, 255, 0), 255)
    return img
