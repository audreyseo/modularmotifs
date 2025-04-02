import { group } from 'console';
import { arrayRange } from '../../core/Util';
import RGBAColor from '../../core/RGBAColor';
import * as StringUtils from '../../util/StringUtils'

// Mostly translated from python by chatgpt

type Point = [number, number];

function bfs(
    x: number,
    y: number,
    s: Set<Point>,
    seen: Set<Point>,
    surrounding: (x: number, y: number) => Set<Point>
): void {
    const newPoints = surrounding(x, y);
    for (const [x0, y0] of newPoints) {
        if (!seen.has([x0, y0])) {
            seen.add([x0, y0]);
            s.add([x0, y0]);
            bfs(x0, y0, s, seen, surrounding);
        }
    }
}

class Edge {
    start: Point;
    end: Point;

    constructor(start: Point, end: Point) {
        if (start[0] > end[0] || (start[0] === end[0] && start[1] > end[1])) {
            [start, end] = [end, start];
        }
        this.start = start;
        this.end = end;
    }

    static fromPoints(x0: number, y0: number, x1: number, y1: number): Edge {
        return new Edge([x0, y0], [x1, y1]);
    }

    otherEnd(...args: any[]): Point | null {
        let x: number | null = null;
        let y: number | null = null;

        if (args.length === 2 && typeof args[0] === "number" && typeof args[1] === "number") {
            [x, y] = args as [number, number];
        } else if (args.length === 1 && Array.isArray(args[0]) && args[0].length === 2) {
            [x, y] = args[0] as [number, number];
        }

        if (x === null || y === null) {
            throw new Error(`Edge.otherEnd: Invalid arguments ${args}`);
        }

        const pt: Point = [x, y];

        if (this.start[0] === pt[0] && this.start[1] === pt[1]) return this.end;
        if (this.end[0] === pt[0] && this.end[1] === pt[1]) return this.start;

        return null;
    }

    toList(): Point[] {
        return [this.start, this.end];
    }

    equals(other: Edge): boolean {
        return this.start[0] === other.start[0] &&
               this.start[1] === other.start[1] &&
               this.end[0] === other.end[0] &&
               this.end[1] === other.end[1];
    }

    contains(elmt: any): boolean {
        return Array.isArray(elmt) &&
               elmt.length === 2 &&
               typeof elmt[0] === "number" &&
               typeof elmt[1] === "number" &&
               (this.start[0] === elmt[0] && this.start[1] === elmt[1] ||
                this.end[0] === elmt[0] && this.end[1] === elmt[1]);
    }

    *[Symbol.iterator](): Generator<Point, void, unknown> {
        yield this.start;
        yield this.end;
    }

    miny(): number {
        return Math.min(this.start[1], this.end[1]);
    }

    vector(): number[] {
        return [this.end[0] - this.start[0], this.end[1] - this.start[1]];
    }

    compare(other: Edge): boolean {
        function cmpCartesian(pt1: Point, pt2: Point): boolean {
            return pt1[1] < pt2[1] || (pt1[1] === pt2[1] && pt1[0] < pt2[0]);
        }

        return cmpCartesian(this.start, other.start) && cmpCartesian(this.end, other.end);
    }
}

export function unitVector(vector: number[]): number[] {
    const norm = Math.sqrt(vector.reduce((acc, val) => acc + val * val, 0));
    return vector.map(v => v / norm);
}

export function angleBetween(v1: number[], v2: number[]): number {
    const v1U = unitVector(v1);
    const v2U = unitVector(v2);
    return Math.acos(Math.min(1, Math.max(-1, v1U[0] * v2U[0] + v1U[1] * v2U[1])));
}

function fromImplicit(
    implicit: boolean[][] | number[][], 
    minx: number = 0, 
    miny: number = 0
): Point[] {
    if (Array.isArray(implicit)) {
        if (implicit.length === 0) {
            throw new Error("Selection.fromImplicit: implicit must be non-empty!");
        }
        const width = implicit[0].length;
        if (!implicit.every(row => row.length === width)) {
            throw new Error(`Selection.fromImplicit: implicit's rows must all be the same width ${width}`);
        }

        const selectedCells: [number, number][] = [];
        implicit.forEach((row, y) => {
            row.forEach((cell, x) => {
                if (cell) {
                    selectedCells.push([minx + x, miny + y]);
                }
            });
        });

        return selectedCells
    } else {
        throw new Error("Invalid input: 'implicit' must be a 2D array of boolean values.");
    }
}


export abstract class AbstractSelection {
    constructor() {
    }

    surrounding(x: number, y: number): Set<[number, number]> {
        const points: [number, number][] = [
            [x - 1, y - 1], [x - 1, y], [x - 1, y + 1],
            [x, y - 1], [x, y + 1],
            [x + 1, y - 1], [x + 1, y], [x + 1, y + 1]
        ];
        return new Set(points.filter(([px, py]) => this.getCells().has([px, py])));
    }

    isConnected(): boolean {
        const cells = this.getCells();
        const [x, y] = [...cells][0];
        const seen = new Set<[number, number]>([[x, y]]);
        const selection = new Set<[number, number]>([[x, y]]);
        this.bfs(x, y, selection, seen, this.surrounding.bind(this));
        return selection.size === cells.size;
    }

    minimum(): [number, number] {
        const xs = [...this.getCells()].map(([x]) => x);
        const ys = [...this.getCells()].map(([_, y]) => y);
        return [Math.min(...xs), Math.min(...ys)];
    }

    maximum(): [number, number] {
        const xs = [...this.getCells()].map(([x]) => x);
        const ys = [...this.getCells()].map(([_, y]) => y);
        return [Math.max(...xs), Math.max(...ys)];
    }

    bbox(): [number, number, number, number] {
        const [minX, maxX] = this.xLimits();
        const [minY, maxY] = this.yLimits();
        return [minX, minY, maxX + 1, maxY + 1];
    }

    static fromImplicit(
        implicit: boolean[][] | number[][],
        minX?: number,
        minY?: number
    ): AbstractSelection {
        throw new Error('Method not implemented! Use derived class');
    }

    invert(): AbstractSelection {
        const implicit = this.getImplicit();
        const inverted = implicit.map(row => row.map(cell => !cell));
        const [xmin] = this.xLimits();
        const [ymin] = this.yLimits();
        return AbstractSelection.fromImplicit(inverted, xmin, ymin);
    }

    protected _rowMajorCells(): Array<[number, number]> {
        // Flip (x, y) -> (y, x) since we want lower y values first
        let cells: Array<[number, number]> = Array.from(this.getCells()).map(([x, y]) => [y, x]);
    
        // Sorts in lexicographical order
        cells.sort(([y1, x1], [y2, x2]) => y1 - y2 || x1 - x2);
    
        // Flip back (y, x) -> (x, y)
        return cells.map(([y, x]) => [x, y]);
    }
    

    abstract getCells(): Set<[number, number]>;

    abstract getImplicit(): boolean[][];

    xLimits(): [number, number] {
        const xs = [...this.getCells()].map(([x]) => x);
        return [Math.min(...xs), Math.max(...xs)];
    }

    yLimits(): [number, number] {
        const ys = [...this.getCells()].map(([_, y]) => y);
        return [Math.min(...ys), Math.max(...ys)];
    }

    protected bfs(
        x: number,
        y: number,
        s: Set<[number, number]>,
        seen: Set<[number, number]>,
        surrounding: (x: number, y: number) => Set<[number, number]>
    ) {
        const newCells = surrounding(x, y);
        for (const [x0, y0] of newCells) {
            if (!seen.has([x0, y0])) {
                seen.add([x0, y0]);
                s.add([x0, y0]);
                this.bfs(x0, y0, s, seen, surrounding);
            }
        }
    }

    // Create an image of the selection
    toImage({
        squareSize = 30,
        onlyOuterBoundary = false,
        blankColor = new RGBAColor(255, 255, 255, 255),
        outlineColor = new RGBAColor(0, 0, 0, 0),
        selectColor = new RGBAColor(0, 0, 0, 255),
        insetX = 0,
        insetY = 0,
    }: {
        squareSize?: number;
        onlyOuterBoundary?: boolean;
        blankColor?: RGBAColor;
        outlineColor?: RGBAColor;
        selectColor?: RGBAColor;
        insetX?: number;
        insetY?: number;
    }): HTMLCanvasElement {
        // Implementation to create an image (canvas-based) here
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        // Set canvas dimensions based on selected cells (we will need to compute bounding box)
        const [minX, minY, maxX, maxY] = this.bbox();
        canvas.width = (maxX - minX + 1) * squareSize;
        canvas.height = (maxY - minY + 1) * squareSize;

        if (ctx === null) {
            throw new Error("context was null")
        }

        // Fill the background with blankColor
        ctx.fillStyle = blankColor.toString();
        ctx?.fillRect(0, 0, canvas.width, canvas.height);

        // Draw selected cells
        this.getCells().forEach(([x, y]) => {
            ctx.fillStyle = selectColor.toString();
            ctx.fillRect(
                (x - minX + insetX) * squareSize,
                (y - minY + insetY) * squareSize,
                squareSize,
                squareSize
            );
        });

        return canvas;
    }

    abstract equals(value: any): boolean;
    abstract notEquals(value: any): boolean;
    abstract contains(elmt: [number, number]): boolean;
}


// Adding a simple string hash function prototype extension (optional)
const string_hashCode = function (s: string): number {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
        const chr = s.charCodeAt(i);
        hash = (hash << 5) - hash + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};


export class ImmutableSelection extends AbstractSelection {
    private selectedCells: ReadonlySet<[number, number]>;

    constructor(selectedCells: Iterable<[number, number]>) {
        super();
        this.selectedCells = new Set(selectedCells);
    }

    override getCells(): Set<[number, number]> {
        return new Set(this.selectedCells);
    }

    override equals(value: any): boolean {
        if (value instanceof ImmutableSelection) {
            return this.selectedCells.size === value.selectedCells.size &&
                [...this.selectedCells].every(cell => value.selectedCells.has(cell));
        }
        return value instanceof Set && this.selectedCells.size === value.size &&
            [...this.selectedCells].every(cell => value.has(cell));
    }

    override notEquals(value: any): boolean {
        return !this.equals(value);
    }

    override contains(elmt: [number, number]): boolean {
        return this.selectedCells.has(elmt);
    }

    *[Symbol.iterator]() {
        yield* this._rowMajorCells();
    }

    override getImplicit(): boolean[][] {
        const [x_min, y_min, x_max, y_max] = this.bbox()
        const implicit: boolean[][] = arrayRange(y_min, y_max, 1).map<boolean[]>(() => arrayRange(x_min, x_max, 1).map<boolean>(() => false))
        for (const [cx, cy] of this.getCells()) {
            implicit[cy - y_min][cx - x_min] = true
        }
        return implicit
    }

    static fromImplicit(implicit: boolean[][] | number[][], minX = 0, minY = 0): ImmutableSelection {
        const cells: [number, number][] = [];
        implicit.forEach((row, y) => {
            row.forEach((cell, x) => {
                if (cell) cells.push([minX + x, minY + y]);
            });
        });
        return new ImmutableSelection(cells);
    }

    hashCode(): number {
        return ([...this.selectedCells]
            .map(([x, y]) => `${x},${y}`)
            .join('|')).hashCode(); // Custom hash function needed
    }
}

export class Selection extends AbstractSelection {
    /**
     * A basic selection class that stores selected coordinates. This version is mutable.
     *
     * Does not assume any particular shape of the selection. (i.e., these selections need not be rectangular)
     */

    selectedCells: Set<[number, number]>;

    constructor(selected: Array<[number, number]> = []) {
        super();
        this.selectedCells = new Set(selected);
    }

    add(x: number, y: number): this {
        this.selectedCells.add([x, y]);
        return this;
    }

    union(other: Selection | Set<[number, number]>): this {
        if (other instanceof Set) {
            this.selectedCells = new Set([...this.selectedCells, ...other]);
        } else {
            this.selectedCells = new Set([...this.selectedCells, ...other.selectedCells]);
        }
        return this;
    }

    static fromImplicit(
        implicit: boolean[][] | number[][], 
        minx = 0, 
        miny = 0
    ): Selection {
        return new Selection(fromImplicit(implicit, minx, miny));
    }

    override equals(value: any): boolean {
        if (value instanceof Set) {
            return this.isEqualSet(this.selectedCells, value);
        }
        if (value instanceof Selection) {
            return this.isEqualSet(this.selectedCells, value.selectedCells);
        }
        if (value instanceof AbstractSelection) {
            return this.isEqualSet(this.selectedCells, value.getCells());
        }
        return false;
    }

    override notEquals(value: any): boolean {
        return !this.equals(value)
    }

    override contains(item: [number, number]): boolean {
        return this.selectedCells.has(item);
    }

    override getCells(): Set<[number, number]> {
        return this.selectedCells;
    }

    private isEqualSet(a: Set<[number, number]>, b: Set<[number, number]>): boolean {
        if (a.size !== b.size) return false;
        for (const item of a) {
            if (!b.has(item)) return false;
        }
        return true;
    }

    override getImplicit(): boolean[][] {
        const [x_min, y_min, x_max, y_max] = this.bbox()
        const implicit: boolean[][] = arrayRange(y_min, y_max, 1).map<boolean[]>(() => arrayRange(x_min, x_max, 1).map<boolean>(() => false))
        for (const [cx, cy] of this.getCells()) {
            implicit[cy - y_min][cx - x_min] = true
        }
        return implicit
    }
}


class ManhattanSelection extends Selection {
    private edges: Set<Edge>;

    constructor(selected: [number, number][], edges: Set<Edge>) {
        super(selected);
        this.edges = edges;
    }

    // Equivalent of the 'surrounding' method in Python
    surrounding(x: number, y: number): Set<[number, number]> {
        const pts: [number, number][] = [
            [x - 1, y], [x, y - 1], [x, y + 1], [x + 1, y]
        ];

        const result = new Set<[number, number]>();
        pts.forEach(([x0, y0]) => {
            if (this.getCells().has([x0, y0]) && this.edges.has(new Edge([x, y], [x0, y0]))) {
                result.add([x0, y0]);
            }
        });

        return result;
    }
}

export class GridSelection extends Selection {
    private _start: [number, number];
    private _end: [number, number] | null;

    constructor(startx: number, starty: number) {
        super([]);
        this._start = [startx, starty];
        this._end = null;
    }

    complete(endx: number, endy: number): void {
        const [startx, starty] = this._start;
        this._end = [endx, endy];

        const xiter = startx < endx ? Array.from({ length: endx - startx + 1 }, (_, i) => startx + i) : Array.from({ length: startx - endx + 1 }, (_, i) => startx - i);
        const yiter = starty < endy ? Array.from({ length: endy - starty + 1 }, (_, i) => starty + i) : Array.from({ length: starty - endy + 1 }, (_, i) => starty - i);

        xiter.forEach(x => {
            yiter.forEach(y => {
                this.add(x, y);
            });
        });
    }

    isComplete(): boolean {
        return this._end !== null;
    }

    bbox(): [number, number, number, number] {
        if (!this.isComplete()) {
            throw new Error("Selection not completed");
        }

        const [x0, y0] = this._start;
        const [x1, y1] = this._end!;
        return [x0, y0, x1, y1];
    }

    // Overriding the string representation
    toString(): string {
        const end = this._end ? `, ${this._end}` : "";
        return `${this.constructor.name}(${this._start}${end})`;
    }
}

export function main() {
    const sel = new Selection();
    sel.add(0, 1).add(1, 0).add(2, 0).add(1, 2).add(0, 3);
    console.log(sel.getCells());

    // Iterate over selected cells
    for (const [x, y] of sel.getCells()) {
        console.log(`(${x}, ${y})`);
    }

    const sel1 = new Selection();
    sel1.add(0, 0).add(1, 0).add(0, 1);
    console.log(sel1.getCells());

    // Create an image from selection
    const img = sel1.toImage({ squareSize: 30 });
    document.body.appendChild(img); // Show the image in the browser

    // Create implicit array example
    const implicit6: boolean[][] = Array(10)
        .fill(null)
        .map(() => Array(10).fill(true));
    implicit6[2][2] = false;
    implicit6[5][5] = false;
    implicit6[4][4] = false;
    implicit6[4][5] = false;
    implicit6[4][6] = false;
    implicit6[9][0] = false;

    const sel6 = Selection.fromImplicit(implicit6);
    const img6 = sel6.toImage({ squareSize: 30 });
    document.body.appendChild(img6); // Show the image

    const implicit7 = Array.from({ length: 10 }, () => Array(10).fill(0));
    implicit7[2][2] = 1;
    implicit7[5][5] = 1;
    implicit7[4][4] = 1;
    implicit7[4][5] = 1;
    implicit7[4][6] = 1;
    implicit7[9][0] = 1;
    const sel7 = Selection.fromImplicit(implicit7.map(row => row.map(val => val === 0)));
    const img7 = sel7.toImage({ squareSize: 30 });
    document.body.appendChild(img7); // Show the image
}