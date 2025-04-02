
function rgba_bounded(n: number) {
    return Math.min(Math.max(0, Math.round(n)), 255)
}


export default class RGBAColor {
    readonly red: number = 0;
    readonly green: number = 0;
    readonly blue: number = 0;
    readonly alpha: number = 0;

    static Back: RGBAColor = new RGBAColor(0, 0, 0)
    static Fore: RGBAColor = new RGBAColor(255, 255, 255)
    static Invis: RGBAColor = new RGBAColor(128, 128, 128)

    constructor(red: number, green: number, blue: number, alpha: number = 255) {
        this.red = red;
        this.green = green;
        this.blue = blue;
        this.alpha = alpha;
    }

    hex(includeAlpha: boolean = true): string {
        return "#" + this.red.toString(16) + this.green.toString(16) + this.blue.toString(16) + ((includeAlpha) ? this.alpha.toString(16) : "")
    }
    
    static from_hex(hexstr: string): RGBAColor {
        const rgba_regex: RegExp = /#[0-9A-F]{7, 9}/i
        if (!hexstr.match(rgba_regex)) {
            console.log("doesn't match")
        }
        const r = parseInt(hexstr.slice(1, 3), 16)
        const g = parseInt(hexstr.slice(3, 5), 16)
        const b = parseInt(hexstr.slice(5, 7), 16)
        if (hexstr.length == 9) {
            const a = parseInt(hexstr.slice(7, 9), 16)
            return new RGBAColor(r, g, b, a)
        }
        return new RGBAColor(r, g, b)
    }

    toString(): string {
        return this.hex()
    }

    rgb_tuple(): [number, number, number] {
        return [this.red, this.green, this.blue]
    }

    rgba_tuple(): [number, number, number, number] {
        return [this.red, this.green, this.blue, this.alpha]
    }

    filtered(r: number=1.0, g:number=1.0, b: number=1.0, a: number=1.0): RGBAColor {
        return new RGBAColor(rgba_bounded(r * this.red), rgba_bounded(g * this.green), rgba_bounded(b * this.blue), rgba_bounded(a * this.alpha))
    }
}