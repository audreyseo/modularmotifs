import {Statement, FreshVar, Variable, Expr, ObjectMethodCall, KeywordArg} from './BasicAst';


abstract class Operation extends Statement {
    fresh: FreshVar;
    op_name: string;

    constructor(op_name: string, fresh: FreshVar) {
        super();
        this.op_name = op_name;
        this.fresh = fresh;
    }

    abstract inverse(): Operation;
}

abstract class DesignOp extends Statement {
    static cn = "DesignOp"; // Equivalent to __qualname__

    d: Variable;
    op_name: string;
    fresh: FreshVar;

    constructor(d: Variable, op_name: string, fresh: FreshVar) {
        super();
        this.d = d;
        this.op_name = op_name;
        this.fresh = fresh;
    }

    abstract inverse(): DesignOp;
}

class SetVariable extends Statement {
    x: Variable;
    expr: Expr;

    constructor(x: Variable, expr: Expr) {
        super();
        this.x = x;
        this.expr = expr;
    }

    toPython(): string {
        return `${this.x} = ${this.expr}`;
    }
}

class AddMotif extends DesignOp {
    static cn = "AddMotif";

    v: Variable;
    m: Expr;
    x: Expr;
    y: Expr;

    constructor(v: Variable, d: Variable, m: Expr, x: Expr, y: Expr, fresh: FreshVar) {
        super(d, "add_motif", fresh);
        this.v = v;
        this.m = m;
        this.x = x;
        this.y = y;
    }

    inverse(): DesignOp {
        return new RemoveMotif(this.d, this.v, this.fresh);
    }

    toPython(): string {
        return `${this.v} = ${this.d}.${this.op_name}(${this.m}, ${this.x}, ${this.y})`;
    }
}

class RemoveMotif extends DesignOp {
    placed_motif: Variable;

    constructor(d: Variable, placedMotif: Variable, fresh: FreshVar) {
        super(d, "remove_motif", fresh);
        this.placed_motif = placedMotif;
    }

    inverse(): DesignOp {
        return new AddMotif(
            new Variable(this.fresh.getFresh()),
            this.d,
            new ObjectMethodCall(this.placed_motif, "motif"),
            new ObjectMethodCall(this.placed_motif, "x"),
            new ObjectMethodCall(this.placed_motif, "y"),
            this.fresh
        );
    }

    toPython(): string {
        return `${this.d}.${this.op_name}(${this.placed_motif})`;
    }
}

abstract class SizeOp extends DesignOp {
    at_index?: Expr;
    contents?: Expr;

    constructor(
        d: Variable,
        op_name: string,
        fresh: FreshVar,
        at_index?: Expr,
        contents?: Expr
    ) {
        super(d, op_name, fresh);
        this.at_index = at_index;
        this.contents = contents;
    }

    getAtIndex(): string {
        if (!this.at_index) return "";
        return this.at_index instanceof KeywordArg
            ? this.at_index.toPython()
            : `at_index=${this.at_index.toPython()}`;
    }

    getArgsToPython(): string[] {
        const args: string[] = [];
        const atIndex = this.getAtIndex();
        if (atIndex) args.push(atIndex);
        const contents = this.contents ? this.contents.toPython() : "";
        if (contents) args.push(contents);
        return args;
    }
}

class AddRow extends SizeOp {
    v: Variable;

    constructor(
        v: Variable,
        d: Variable,
        fresh: FreshVar,
        at_index?: Expr,
        contents?: Expr
    ) {
        super(d, "add_row", fresh, at_index, contents);
        this.v = v;
    }

    inverse(): DesignOp {
        return new RemoveRow(
            new Variable(this.fresh.getFresh()),
            new Variable(this.fresh.getFresh()),
            this.d,
            this.fresh,
            this.v
        );
    }

    toPython(): string {
        const args = this.getArgsToPython();
        return `${this.v} = ${this.d}.${this.op_name}(${args.join(", ")})`;
    }
}

class RemoveRow extends SizeOp {
    indexVar: Variable;
    removed: Variable;

    constructor(
        indexVar: Variable,
        removed: Variable,
        d: Variable,
        fresh: FreshVar,
        at_index?: Expr
    ) {
        super(d, "remove_row", fresh, at_index);
        this.indexVar = indexVar;
        this.removed = removed;
    }

    inverse(): DesignOp {
        return new AddRow(
            new Variable(this.fresh.getFresh()),
            this.d,
            this.fresh,
            this.indexVar,
            this.removed
        );
    }

    toPython(): string {
        return `${this.indexVar}, ${this.removed} = ${this.d}.${this.op_name}(${this.getAtIndex()})`;
    }
}

class AddColumn extends SizeOp {
    v: Variable;

    constructor(
        v: Variable,
        d: Variable,
        fresh: FreshVar,
        at_index?: Expr,
        contents?: Expr
    ) {
        super(d, "add_column", fresh, at_index, contents);
        this.v = v;
    }

    inverse(): DesignOp {
        return new RemoveColumn(
            new Variable(this.fresh.getFresh()),
            new Variable(this.fresh.getFresh()),
            this.d,
            this.fresh,
            this.v
        );
    }

    toPython(): string {
        const args = this.getArgsToPython();
        return `${this.v} = ${this.d}.${this.op_name}(${args.join(", ")})`;
    }
}

class RemoveColumn extends SizeOp {
    indexVar: Variable;
    removed: Variable;

    constructor(
        indexVar: Variable,
        removed: Variable,
        d: Variable,
        fresh: FreshVar,
        at_index?: Expr
    ) {
        super(d, "remove_column", fresh, at_index);
        this.indexVar = indexVar;
        this.removed = removed;
    }

    inverse(): DesignOp {
        return new AddColumn(
            new Variable(this.fresh.getFresh()),
            this.d,
            this.fresh,
            this.indexVar,
            this.removed
        );
    }

    toPython(): string {
        return `${this.indexVar}, ${this.removed} = ${this.d}.${this.op_name}(${this.getAtIndex()})`;
    }
}

class Motifify extends DesignOp {
    v: Variable;
    x0: Expr;
    y0: Expr;
    x1: Expr;
    y1: Expr;

    constructor(
        v: Variable,
        d: Variable,
        x0: Expr,
        y0: Expr,
        x1: Expr,
        y1: Expr,
        fresh: FreshVar
    ) {
        super(d, "motifify", fresh);
        this.v = v;
        this.x0 = x0;
        this.y0 = y0;
        this.x1 = x1;
        this.y1 = y1;
    }

    inverse(): DesignOp {
        return new UnMotifify(this.v, this.d, this.x0, this.y0, this.x1, this.y1, this.fresh);
    }

    toPython(): string {
        return `${this.v} = ${this.d}.${this.op_name}(${this.x0}, ${this.y0}, ${this.x1}, ${this.y1})`;
    }
}

class UnMotifify extends DesignOp {
    v: Variable;
    x0: Expr;
    y0: Expr;
    x1: Expr;
    y1: Expr;

    constructor(
        v: Variable,
        d: Variable,
        x0: Expr,
        y0: Expr,
        x1: Expr,
        y1: Expr,
        fresh: FreshVar
    ) {
        super(d, "unmotifify", fresh);
        this.v = v;
        this.x0 = x0;
        this.y0 = y0;
        this.x1 = x1;
        this.y1 = y1;
    }

    inverse(): DesignOp {
        return new Motifify(this.v, this.d, this.x0, this.y0, this.x1, this.y1, this.fresh);
    }

    toPython(): string {
        return `${this.v} = None`;
    }
}

export {Operation, DesignOp, SetVariable, AddMotif, RemoveMotif, SizeOp, AddRow, RemoveRow, AddColumn, RemoveColumn, Motifify, UnMotifify}