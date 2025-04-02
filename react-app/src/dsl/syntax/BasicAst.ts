import * as StringUtils from '../../util/StringUtils';

// Define types
type Primitive = number | string | boolean | null | undefined;
// type Expr = Syntax;
type LiteralType = number | string | boolean | Expr[];

// FreshVar class for generating unique variable names
class FreshVar {
  private current: number;
  private baseName: string;
  private namesToAvoid: Set<string>;

  constructor(baseName: string = "x", namesToAvoid: Set<string> = new Set()) {
    this.current = 0;
    this.baseName = baseName;
    this.namesToAvoid = namesToAvoid;
  }

  getFresh(): string {
    let fresh = `${this.baseName}${this.current}`;
    this.current += 1;
    while (this.namesToAvoid.has(fresh)) {
      fresh = `${this.baseName}${this.current}`;
      this.current += 1;
    }
    return fresh;
  }
}

// Base class for all syntactic elements in the DSL
abstract class Syntax {
  // class name for reference in the __repr__ method
  cn: string;

  constructor() {
    this.cn = this.constructor.name;
  }

  abstract toPython(): string;

  toString(): string {
    return this.toPython();
  }

  // Equality check based on Python representation
  equals(other: Syntax): boolean {
    return this.toPython() === other.toPython();
  }

  // Hash code based on the Python representation
  hashCode(): number {
    return this.toPython().hashCode();
  }
}

abstract class Expr extends Syntax {

}

// Import statement class
class Import extends Syntax {
  importedModule: string;
  private _as: string | null;

  constructor(mod: string, _as: string | null = null) {
    super();
    this.importedModule = mod;
    this._as = _as;
  }

  toPython(): string {
    return `import ${this.importedModule}${this._as ? ` as ${this._as}` : ""}`;
  }

  usename(): string {
    return this._as || this.importedModule;
  }
}

// FromImport statement class
class FromImport extends Import {
  imports: string[];

  constructor(mod: string, ...imports: string[]) {
    super(mod);
    this.imports = imports;
  }

  toPython(): string {
    return `from ${this.importedModule} import ${this.imports.join(", ")}`;
  }
}

// Literal expression class
class Literal extends Syntax {
  const: LiteralType;

  constructor(constant: LiteralType) {
    super();
    this.const = constant;
  }

  isInt(): this is {const: number} {
    return typeof this.const === "number" && Number.isInteger(this.const);
  }

  isStr(): this is {const: string} {
    return typeof this.const === "string";
  }

  isFloat(): this is {const: number} {
    return typeof this.const === "number" && !Number.isInteger(this.const);
  }

  isList(): this is {const: Expr[]} {
    return Array.isArray(this.const);
  }

  toPython(): string {
    if (this.isStr()) {
      return `"${this.const}"`;
    }
    if (this.isList()) {
      return `[${this.const.map((e) => e.toPython()).join(", ")}]`;
    }
    return String(this.const);
  }
}

// Variable expression class
class Variable extends Syntax {
  name: string;

  constructor(name: string) {
    super();
    this.name = name;
  }

  toPython(): string {
    return this.name;
  }
}

// Object initialization expression class
class ObjectInit extends Syntax {
  className: string;
  args: Expr[];

  constructor(className: string, ...args: Expr[]) {
    super();
    this.className = className;
    this.args = args;
  }

  toPython(): string {
    return `${this.className}(${this.args.map((e) => e.toPython()).join(", ")})`;
  }
}

// Attribute access expression class
class AttrAccess extends Syntax {
  obj: Expr;
  key: Expr;

  constructor(obj: Expr, key: Expr) {
    super();
    this.obj = obj;
    this.key = key;
  }

  toPython(): string {
    return `${this.obj.toPython()}[${this.key.toPython()}]`;
  }
}

// Module reference expression class
class ModuleRef extends Syntax {
  module: string;

  constructor(module: string) {
    super();
    this.module = module;
  }

  toPython(): string {
    return this.module;
  }
}

// Module access expression class
class ModuleAccess extends Syntax {
  module: Expr;
  attr: string;

  constructor(module: Expr, attr: string) {
    super();
    this.module = module;
    this.attr = attr;
  }

  toPython(): string {
    return `${this.module.toPython()}.${this.attr}`;
  }
}

// Object access expression class
class ObjectAccess extends Syntax {
  e: Expr;
  prop: string;

  constructor(e: Expr, prop: string) {
    super();
    this.e = e;
    this.prop = prop;
  }

  toPython(): string {
    return `${this.e.toPython()}.${this.prop}`;
  }
}

// Object method call expression class
class ObjectMethodCall extends Syntax {
  v: Variable;
  method: string;
  args: Expr[];

  constructor(v: Variable, method: string, ...args: Expr[]) {
    super();
    this.v = v;
    this.method = method;
    this.args = args;
  }

  toPython(): string {
    return `${this.v.toPython()}.${this.method}(${this.args.map((e) => e.toPython()).join(", ")})`;
  }
}

// Keyword argument expression class
class KeywordArg extends Syntax {
  key: string;
  e: Expr;

  constructor(key: string, e: Expr) {
    super();
    this.key = key;
    this.e = e;
  }

  toPython(): string {
    return `${this.key}=${this.e.toPython()}`;
  }
}

// Base class for all statements
abstract class Statement extends Syntax {}


export type {Primitive, LiteralType}
export {FreshVar, Syntax, Expr, Import, FromImport, Literal, Variable, ObjectInit, AttrAccess, ModuleRef, ModuleAccess, ObjectAccess, ObjectMethodCall, KeywordArg, Statement}