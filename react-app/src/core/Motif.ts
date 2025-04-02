import PixelGrid from "./PixelGrid";
import RGBAColor from "./RGBAColor";

enum Color {
    FORE = 1,
    BACK = 2,
    INVIS = 3
}

function color_add(c1: Color, c2: Color) {
    switch (c1) {
        case Color.INVIS:
            return c2
        case Color.BACK:
            if (c2 === Color.BACK) {
                return c1
            }
            break
        default:
            switch (c2) {
                case Color.INVIS:
                    return c1
                default: break
            }
    }
    throw new Error("Color Overflow Exception")
}

function color_sub(c1: Color, c2: Color): Color {
    if (c1 === Color.INVIS && c2 !== Color.INVIS) {
        throw new Error("Color Underflow Exception")
    }
    if (c2 === Color.INVIS) {
        return c1
    }
    if (c1 === c2) {
        return Color.INVIS
    }
    throw new Error("Color Underflow Exception")
}

class Motif extends PixelGrid implements Iterable<Color[]> {
    readonly w: number = 0
    readonly h: number = 0
    readonly data!: Color[][]
    
    constructor(bbox: Color[][]) {
        super();
        this.data = bbox;
        this.h = this.data.length;
        this.w = this.data[0].length;
    }

    width(): number {
        return this.w
    }

    height(): number {
        return this.h
    }

    get_color(x: number, y: number): Color {
        return this.data[y][x]
    }

    get_rgba(x: number, y: number): RGBAColor {
        switch (this.get_color(x, y)) {
            case Color.FORE:
                return RGBAColor.Fore
            case Color.BACK:
                return RGBAColor.Back
            case Color.INVIS:
                return RGBAColor.Invis
        }
    }

    [Symbol.iterator](): Iterator<Color[]> {
        return this.data[Symbol.iterator]()
    }

    dims(): [number, number] {
        return [this.w, this.h]
    }
}

export { Color, color_sub, color_add }

export default Motif