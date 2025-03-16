from PIL import Image
import argparse
import os
import sys


def parseargs():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("file", type=str, help="Name of the file to parse into an xbm -- X11 Bitmap")
    
    parser.add_argument("--output", "-o", type=str, help="Name of the file to save to.")

    return parser.parse_args()

def to_xbm(name: str, img: Image.Image) -> str:
    """ #define hand_width 16
 #define hand_height 16
 #define hand_x_hot 6
 #define hand_y_hot 0
 static unsigned char panPointer_bits[] = {
    0x00, 0x00, 0x80, 0x01, 0x58, 0x0e, 0x64, 0x12, 0x64, 0x52, 0x48, 0xb2,
    0x48, 0x92, 0x16, 0x90, 0x19, 0x80, 0x11, 0x40, 0x02, 0x40, 0x04, 0x40,
    0x04, 0x20, 0x08, 0x20, 0x10, 0x10, 0x20, 0x10 };"""
    
    pixels = img.load()
    
    bits = []
    for i in range(img.height):
        for j in range(img.width):
            # print(pixels[j, i])
            r, g, b, a = pixels[j, i]
            bit = 1 - round(float(a) / 255.0)
            bits.append(bit)
            pass
        pass
    
    bites = []
    for i in range(len(bits) // 8):
        bite = 0
        for j in range(8):
            bite = ((bite) << 1) + bits[i * 8 + j]
            pass
        bites.append(bite)
    
    
    return f"""#define {name}_width {img.width}
#define {name}_height {img.height}
#define {name}_x_hot 8
#define {name}_y_hot 8
static unsigned char {name}_bits[] = {"{"}
    {", ".join(list(map(lambda value: f"{value:#04x}", bites)))}
{"}"};"""


if __name__ == "__main__":
    args = parseargs()
    if not os.path.exists(args.file):
        print(f"Cannot find image file {args.file}", file=sys.stderr)
        exit(1)
        pass
    img = Image.open(args.file)
    scaling = 32.0 / img.width
    img = img.resize((round(img.width * scaling), round(img.height * scaling)), resample=Image.Resampling.LANCZOS)
    name, _ = os.path.splitext(os.path.basename(args.file))
    xbm_text = to_xbm(name, img)
    print(xbm_text)
    with open(args.output, "w") as f:
        f.write(xbm_text)
        f.write("\n")
        f.flush()
        pass
    pass
        
    