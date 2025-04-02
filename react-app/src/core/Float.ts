/**
 * Data structure to capture the essence of a float in stranded colorwork knitting.
 * Floats are horizontal lengths of yarn that occur because of color changes.
 */

import { Color } from "./Motif";

class FloatStrand {
    // Length of the float
    private length: number;
    // The x coordinate where the float begins
    private start: number;
    // The row where the float occurred
    private rownum: number;
    // Color of the float
    private color?: Color;

    /**
     * Create an instance of a FloatStrand
     * 
     * @param start - The left x coordinate of this float (i.e., the last stitch knit with this color)
     * @param length - The number of stitches in between that were knit in the other color.
     *                 The right x coordinate of this float (i.e., the next stitch knit with this color) should be at start + length + 1
     * @param row - The row where this float occurs (optional, defaults to -1)
     * @param color - The color of this float (optional, must not be Color.INVIS if provided)
     */
    constructor(start: number, length: number, row: number = -1, color?: Color) {
        if (color !== undefined && color === Color.INVIS) {
            throw new Error(`FloatStrand: color ${color} should be undefined or not 'invisible'`);
        }
        this.length = length;
        this.start = start;
        this.rownum = row;
        this.color = color;
    }

    hasRow(): boolean {
        return this.rownum !== -1;
    }

    getRow(): number {
        return this.rownum;
    }

    hasColor(): boolean {
        return this.color !== undefined;
    }

    getColor(): Color | undefined {
        return this.color;
    }

    getLength(): number {
        return this.length;
    }

    xLeft(): number {
        return this.start;
    }

    xRight(): number {
        return this.start + this.length + 1;
    }

    xs(): [number, number] {
        return [this.xLeft(), this.xRight()];
    }

    toString(): string {
        return `Float(row ${this.rownum}, ${this.start}-${this.xRight()}, ${this.length}, ${this.color})`;
    }
}
