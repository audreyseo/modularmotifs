from PIL import Image
import argparse
import os
import sys


def parseargs():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("file", type=str, help="Name of the file to parse into an xbm -- X11 Bitmap")
    
    parser.add_argument("--output", "-o", type=str, help="Name of the file to save to.")

    return parser.parse_args()


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
    if img.mode == "LA":
        img = img.convert(mode="RGBA")
    print(img.mode)
    converted = img.convert(mode="P", palette=Image.Palette.ADAPTIVE)
    converted.save(args.output)
        
    