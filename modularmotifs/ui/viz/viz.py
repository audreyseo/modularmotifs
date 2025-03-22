"""Supports exporting designs to PNGs and viewing them"""

import matplotlib.pyplot as plt
import numpy as np
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
    img = Image.new("RGBA", (w * res, h * res))
    for x in range(w):
        for y in range(h):
            rgba = d.get_rgba(x, y).rgba_tuple()
            for xi in range(res):
                for yi in range(res):
                    img.putpixel((x * res + xi, y * res + yi), rgba)
    return img


HEART_HEIGHT = 1 / 3
HEART_WIDTH = 1 / 3


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
    img = Image.new("RGBA", (w * res, h * res))
    for x in range(w * res):
        for y in range(h * res):
            img.putpixel((x, y), (255, 0, 0, 255))
    for x in range(w):
        for y in range(h):
            rgba = d.get_rgba(x, y).rgba_tuple()
            for xi in range(res):
                for yi in range(int(res + res * HEART_HEIGHT)):
                    if y == h - 1 and yi >= res:
                        continue  # off the image

                    if (
                        y > 0
                        and res * HEART_WIDTH <= xi < res * HEART_WIDTH * 2
                        and yi < res * HEART_HEIGHT
                    ):
                        continue  # TODO: this is not exactly a heart
                    if yi >= res:
                        if xi < res * HEART_WIDTH or xi >= res * HEART_WIDTH * 2:
                            continue
                        else:
                            pass  # TODO: this is not exactly a heart
                    img.putpixel((x * res + xi, y * res + yi), rgba)
    return img


def show_design(d: Design) -> None:
    bg_color = (128, 128, 128)
    img = export_heart(d)

    # Create a solid background image
    print(img.size)
    print(bg_color)
    # bg = Image.new("RGBA", img.size, bg_color + (255,))  # Solid gray background

    # # Composite the image onto the background
    # img = Image.alpha_composite(bg, img)

    # # Convert back to RGB (to avoid issues with alpha in matplotlib)
    # img = img.convert("RGB")

    # Display the image
    plt.imshow(img)
    plt.axis("off")  # Remove axes
    plt.show()

    plt.show()

    img = export_heart(d, res=9)

    wrap_image_around_cylinder(img)


def wrap_image_around_cylinder(img):
    """Wrap an RGBA image around a 3D cylinder."""
    img_array = np.array(img) / 255.0

    # Get image dimensions
    img_h, img_w, _ = img_array.shape

    radius = img_w / (2 * np.pi)
    height = img_h

    gran_x = img_w
    gran_y = img_h

    # Create cylinder mesh
    theta = np.linspace(0, 2 * np.pi, gran_x)  # Wrap full circle
    z = np.linspace(-height / 2, height / 2, gran_y)  # Height range
    theta, z = np.meshgrid(theta, z)  # Create 2D meshgrid
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    # Create figure
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")

    # Map the image texture onto the cylinder
    ax.plot_surface(x, y, z, facecolors=img_array, rstride=1, cstride=1)

    ax.set_box_aspect([1, 1, height / (2 * radius)])

    # Adjust view and remove axis for clean rendering
    ax.set_xlim([-radius, radius])
    ax.set_ylim([-radius, radius])
    ax.set_zlim([-height / 2, height / 2])
    ax.axis("off")

    plt.show()
