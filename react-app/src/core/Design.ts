import Motif, {Color, color_sub, color_add} from './Motif';
import PixelGrid from './PixelGrid';
import RGBAColor from './RGBAColor';
import {Option, some, none} from 'fp-ts/Option';

import { arrayRange, enumerate } from './Util';
import { group } from 'console';
import { getgroups } from 'process';

class PlacedMotif {
    private _motif!: Motif
    private _x!: number
    private _y!: number

    constructor(x: number, y: number, motif: Motif) {
        this._x = x;
        this._y = y;
        this._motif = motif;
    }

    motif() {
        return this._motif
    }

    x(): number {
        return this._x
    }

    y(): number {
        return this._y
    }
}

class PixelData {
    col!: Color
    motifs!: Set<PlacedMotif>

    constructor(col: Color, motifs: Set<PlacedMotif>) {
        this.col = col
        this.motifs = motifs

        if (this.col !== Color.INVIS && this.motifs.size == 0) {
            throw new Error("Visible colors must be caused by motifs")
        }
    }

    toString(): string {
        return `PixelData(${this.col}, ${this.motifs})`
    }

    add(other: PixelData): PixelData {
        let new_color = color_add(this.col, other.col)
        let new_motifs = this.motifs.union(other.motifs)
        return new PixelData(new_color, new_motifs)
    }

    sub(other: PixelData): PixelData {
        let new_motifs = this.motifs.difference(other.motifs)
        let new_color = (new_motifs.size === 0) ? color_sub(this.col, other.col) : this.col
        return new PixelData(new_color, new_motifs)
    }

    motif(): Option<PlacedMotif> {
        if (this.col === Color.INVIS ){
            return none
        }
        let found = this.motifs.entries().next().value
        if (found === undefined) {
            return none
        }
        return some(found[0])
    }
}


class Design extends PixelGrid {
    __height!: number
    __width!: number
    __motifs!: Set<PlacedMotif>
    __canvas!: PixelData[][]
    fore_color!: RGBAColor
    back_color!: RGBAColor
    invis_color!: RGBAColor

    constructor(width: number, height: number) {
        super()
        this.__height = height
        this.__width = width
        this.__canvas = Array.from({length: height}, () => Array.from({length: width}, () => new PixelData(Color.INVIS, new Set())))
        this.fore_color = RGBAColor.Fore
        this.back_color = RGBAColor.Back
        this.invis_color = RGBAColor.Invis
        this.__motifs = new Set()
    }

    set_fore_color(color: RGBAColor) {
        this.fore_color = color
    }
    set_back_color(color: RGBAColor) {
        this.back_color = color
    }
    set_invis_color(color: RGBAColor) {
        this.invis_color = color
    }

    private new_row() : PixelData[] {
        return arrayRange(0, this.width(), 1).map<PixelData>(() => Design.default_pixel_data())
    }

    static default_pixel_data(): PixelData {
        return new PixelData(Color.INVIS, new Set())
    }

    get_color(x: number, y: number): Color {
        return this.__canvas[y][x].col
    }

    get_rgba(x: number, y: number): RGBAColor {
        switch (this.get_color(x, y)) {
            case Color.BACK:
                return this.back_color
            case Color.FORE:
                return this.fore_color
            case Color.INVIS:
                return this.invis_color
        }
    }

    get_motifs(x: number, y: number): Set<PlacedMotif> {
        return this.__canvas[y][x].motifs
    }

    get_motif(x: number, y: number): Option<PlacedMotif> {
        return this.__canvas[y][x].motif()
    }

    height(): number {
        return this.__height
    }

    width(): number {
        return this.__width
    }

    row_colors(y: number) : Color[] {
        return arrayRange(0, this.width(), 1).map(n => this.get_color(n, y))
    }

    [Symbol.iterator](): Iterator<Array<[Color, number, number]>> {
        return arrayRange(0, this.height(), 1).map(
            (y: number) => 
                arrayRange(0, this.width(), 1).map<[Color, number, number]>(
                    (x: number) => [this.get_color(x, y), x, y], 
                    this), 
            this)[Symbol.iterator]()
    }

    motifify(x0: number, y0: number, x1: number, y1: number): Motif {
        let colors: Color[][] = Array.from({length: (y1 + 1 - y0)}, () => Array.from({length: (x1 + 1 - x0)}))
        for (let y = y0; y < y1 + 1; y++) {
            for (let x = x0; x < x1 + 1; x++) {
                colors[y - y0][x - x0] = this.get_color(x, y)
            }
        }
        return new Motif(colors)
    }

    add_row(at_index: number=-1, contents?: Array<PixelData>): number {
        if (contents === undefined) {
            contents = this.new_row()
        }
        if (at_index == -1 || at_index == this.height()) {
            at_index = this.height()
            this.__canvas.push(contents)
        } else {
            this.__canvas.splice(at_index, 0, contents)
        }
        this.__height++
        return at_index
    }

    add_column(at_index: number = -1, contents?: Array<PixelData>): number {
        if (contents === undefined) {
            contents = arrayRange(0, this.height(), 1).map<PixelData>(() => Design.default_pixel_data())
        }

        if (at_index === -1 || at_index === this.width()) {
            at_index = this.width()
            for (let i = 0; i < this.height(); i++) {
                this.__canvas[i].push(contents[i])
            }
        } else {
            for (let i = 0; i < this.height(); i++) {
                this.__canvas[i].splice(at_index, 0, contents[i])
            }
        }
        this.__width++
        return at_index
    }

    remove_row(at_index: number = -1) : [number, PixelData[]] {
        this.__height --
        at_index = (at_index === -1) ? this.height() : at_index;
        let removed = this.__canvas.splice(at_index, 1)
        if (removed === undefined) {
            throw new Error(`Removed was undefined at index ${at_index}`)
        }
        return [at_index, removed[0]]
    }

    remove_column(at_index: number = -1) : [number, PixelData[]] {
        let column: PixelData[] = []
        at_index = (at_index === -1) ? this.width() : at_index
        for (let i = 0; i < this.height(); i++) {
            let removed = this.__canvas[i].splice(at_index, 1)
            if (removed === undefined) {
                throw new Error(`Removed was undefined at index ${at_index}`)
            }
            column.push(removed[0])
        }
        return [at_index, column]
    }

    complete() : boolean {
        for (const row of this.__canvas) {
            for (const px of row) {
                if (px.col === Color.INVIS) {
                    return false
                }
            }
        }
        return true
    }

    add_motif(m: Motif, x: number, y: number): PlacedMotif {
        if (m.height() + y > this.height() || m.width() + x > this.width() || Math.min(x, y) < 0) {
            throw new Error(`Motif is out of bounds: ${m.width()} x ${m.height()} vs (${x}, ${y}) and ${this.width()}, ${this.width()}`)
        }

        let p = new PlacedMotif(x, y, m)
        if (this.__motifs.has(p)) {
            throw new Error(`Motif overlap exception with motif ${m} at (${x}, ${y})`)
        }
        let successful_pixel_operations: number = 0
        try {
            for (const [iy, row] of enumerate(m)) {
                for (const [ix, col] of enumerate(row)) {
                    let pd = this.__canvas[y + iy][x + ix]
                    this.__canvas[y + iy][x + ix] = pd.add(new PixelData(col, new Set([p])))
                    successful_pixel_operations += 1
                }
            }
            this.__motifs.add(p)
        } catch (error: any) {
            for (const [iy, row] of enumerate(m)) {
                if (successful_pixel_operations === 0) {
                    break
                }
                for (const [ix, col] of enumerate(row)) {
                    if (successful_pixel_operations === 0) {
                        break
                    }
                    let pd = this.__canvas[y + iy][x + ix]
                    this.__canvas[y + iy][x + ix] = pd.sub(new PixelData(col, new Set([p])))
                    successful_pixel_operations -= 1
                }
            }
            throw new Error(`Motif Overlap Exception with motif ${m} at (${x}, ${y})`)
        }
        return p
    }

    remove_motif(p: PlacedMotif) {
        const y = p.y()
        const x = p.x()
        for (const [iy, row] of enumerate(p.motif())) {
            for (const [ix, col] of enumerate(row)) {
                let pd = this.__canvas[y + iy][x + ix]
                this.__canvas[y + iy][x + ix] = pd.sub(new PixelData(col, new Set([p])))
            }
        }
        this.__motifs.delete(p)
    }
}

export {}
export default Design