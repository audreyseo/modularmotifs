// Generated automatically by nearley, version 2.20.1
// http://github.com/Hardmath123/nearley
// Bypasses TS6133. Allow declared but unused functions.
// @ts-ignore
function id(d: any[]): any { return d[0]; }

import * as Syntax from './syntax';
const fresh: Syntax.FreshVar = new Syntax.FreshVar("x");
const undefined_add_exprs: [any, any] = [undefined, undefined];
const handle_undefined_add_exprs: (args: any[], indeX: number) => [any, any] = (args: any[], index: number) => {
    if (args[index] === undefined) {
        return undefined_add_exprs
    } else if (Array.isArray(args[index]) && args[index].length === 2) {
        return [args[index][0], args[index][1]]
    } else {
        throw new Error(`handle_undefined_add_exprs given something that is neither undefined nor an array: ${args} at index ${index}`)
    }
}

const evens_only = (args: Syntax.Expr[]) => {
    if (args.length === 0) {
        return args
    } else if (args.length === 1) {
        return args
    } else {
        const new_args: Syntax.Expr[] = []
        args.forEach((e: Syntax.Expr, i: number) => {
            if (i % 2 === 0) {
                new_args.push(e)
            }
        })
        return new_args
    }
}


interface NearleyToken {
  value: any;
  [key: string]: any;
};

interface NearleyLexer {
  reset: (chunk: string, info: any) => void;
  next: () => NearleyToken | undefined;
  save: () => any;
  formatError: (token: never) => string;
  has: (tokenType: string) => boolean;
};

interface NearleyRule {
  name: string;
  symbols: NearleySymbol[];
  postprocess?: (d: any[], loc?: number, reject?: {}) => any;
};

type NearleySymbol = string | { literal: any } | { test: (token: any) => boolean };

interface Grammar {
  Lexer: NearleyLexer | undefined;
  ParserRules: NearleyRule[];
  ParserStart: string;
};

const grammar: Grammar = {
  Lexer: undefined,
  ParserRules: [
    {"name": "dqstring$ebnf$1", "symbols": []},
    {"name": "dqstring$ebnf$1", "symbols": ["dqstring$ebnf$1", "dstrchar"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "dqstring", "symbols": [{"literal":"\""}, "dqstring$ebnf$1", {"literal":"\""}], "postprocess": function(d) {return d[1].join(""); }},
    {"name": "sqstring$ebnf$1", "symbols": []},
    {"name": "sqstring$ebnf$1", "symbols": ["sqstring$ebnf$1", "sstrchar"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "sqstring", "symbols": [{"literal":"'"}, "sqstring$ebnf$1", {"literal":"'"}], "postprocess": function(d) {return d[1].join(""); }},
    {"name": "btstring$ebnf$1", "symbols": []},
    {"name": "btstring$ebnf$1", "symbols": ["btstring$ebnf$1", /[^`]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "btstring", "symbols": [{"literal":"`"}, "btstring$ebnf$1", {"literal":"`"}], "postprocess": function(d) {return d[1].join(""); }},
    {"name": "dstrchar", "symbols": [/[^\\"\n]/], "postprocess": id},
    {"name": "dstrchar", "symbols": [{"literal":"\\"}, "strescape"], "postprocess": 
        function(d) {
            return JSON.parse("\""+d.join("")+"\"");
        }
        },
    {"name": "sstrchar", "symbols": [/[^\\'\n]/], "postprocess": id},
    {"name": "sstrchar", "symbols": [{"literal":"\\"}, "strescape"], "postprocess": function(d) { return JSON.parse("\""+d.join("")+"\""); }},
    {"name": "sstrchar$string$1", "symbols": [{"literal":"\\"}, {"literal":"'"}], "postprocess": (d) => d.join('')},
    {"name": "sstrchar", "symbols": ["sstrchar$string$1"], "postprocess": function(d) {return "'"; }},
    {"name": "strescape", "symbols": [/["\\/bfnrt]/], "postprocess": id},
    {"name": "strescape", "symbols": [{"literal":"u"}, /[a-fA-F0-9]/, /[a-fA-F0-9]/, /[a-fA-F0-9]/, /[a-fA-F0-9]/], "postprocess": 
        function(d) {
            return d.join("");
        }
        },
    {"name": "unsigned_int$ebnf$1", "symbols": [/[0-9]/]},
    {"name": "unsigned_int$ebnf$1", "symbols": ["unsigned_int$ebnf$1", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "unsigned_int", "symbols": ["unsigned_int$ebnf$1"], "postprocess": 
        function(d) {
            return parseInt(d[0].join(""));
        }
        },
    {"name": "int$ebnf$1$subexpression$1", "symbols": [{"literal":"-"}]},
    {"name": "int$ebnf$1$subexpression$1", "symbols": [{"literal":"+"}]},
    {"name": "int$ebnf$1", "symbols": ["int$ebnf$1$subexpression$1"], "postprocess": id},
    {"name": "int$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "int$ebnf$2", "symbols": [/[0-9]/]},
    {"name": "int$ebnf$2", "symbols": ["int$ebnf$2", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "int", "symbols": ["int$ebnf$1", "int$ebnf$2"], "postprocess": 
        function(d) {
            if (d[0]) {
                return parseInt(d[0][0]+d[1].join(""));
            } else {
                return parseInt(d[1].join(""));
            }
        }
        },
    {"name": "unsigned_decimal$ebnf$1", "symbols": [/[0-9]/]},
    {"name": "unsigned_decimal$ebnf$1", "symbols": ["unsigned_decimal$ebnf$1", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "unsigned_decimal$ebnf$2$subexpression$1$ebnf$1", "symbols": [/[0-9]/]},
    {"name": "unsigned_decimal$ebnf$2$subexpression$1$ebnf$1", "symbols": ["unsigned_decimal$ebnf$2$subexpression$1$ebnf$1", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "unsigned_decimal$ebnf$2$subexpression$1", "symbols": [{"literal":"."}, "unsigned_decimal$ebnf$2$subexpression$1$ebnf$1"]},
    {"name": "unsigned_decimal$ebnf$2", "symbols": ["unsigned_decimal$ebnf$2$subexpression$1"], "postprocess": id},
    {"name": "unsigned_decimal$ebnf$2", "symbols": [], "postprocess": () => null},
    {"name": "unsigned_decimal", "symbols": ["unsigned_decimal$ebnf$1", "unsigned_decimal$ebnf$2"], "postprocess": 
        function(d) {
            return parseFloat(
                d[0].join("") +
                (d[1] ? "."+d[1][1].join("") : "")
            );
        }
        },
    {"name": "decimal$ebnf$1", "symbols": [{"literal":"-"}], "postprocess": id},
    {"name": "decimal$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "decimal$ebnf$2", "symbols": [/[0-9]/]},
    {"name": "decimal$ebnf$2", "symbols": ["decimal$ebnf$2", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "decimal$ebnf$3$subexpression$1$ebnf$1", "symbols": [/[0-9]/]},
    {"name": "decimal$ebnf$3$subexpression$1$ebnf$1", "symbols": ["decimal$ebnf$3$subexpression$1$ebnf$1", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "decimal$ebnf$3$subexpression$1", "symbols": [{"literal":"."}, "decimal$ebnf$3$subexpression$1$ebnf$1"]},
    {"name": "decimal$ebnf$3", "symbols": ["decimal$ebnf$3$subexpression$1"], "postprocess": id},
    {"name": "decimal$ebnf$3", "symbols": [], "postprocess": () => null},
    {"name": "decimal", "symbols": ["decimal$ebnf$1", "decimal$ebnf$2", "decimal$ebnf$3"], "postprocess": 
        function(d) {
            return parseFloat(
                (d[0] || "") +
                d[1].join("") +
                (d[2] ? "."+d[2][1].join("") : "")
            );
        }
        },
    {"name": "percentage", "symbols": ["decimal", {"literal":"%"}], "postprocess": 
        function(d) {
            return d[0]/100;
        }
        },
    {"name": "jsonfloat$ebnf$1", "symbols": [{"literal":"-"}], "postprocess": id},
    {"name": "jsonfloat$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "jsonfloat$ebnf$2", "symbols": [/[0-9]/]},
    {"name": "jsonfloat$ebnf$2", "symbols": ["jsonfloat$ebnf$2", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "jsonfloat$ebnf$3$subexpression$1$ebnf$1", "symbols": [/[0-9]/]},
    {"name": "jsonfloat$ebnf$3$subexpression$1$ebnf$1", "symbols": ["jsonfloat$ebnf$3$subexpression$1$ebnf$1", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "jsonfloat$ebnf$3$subexpression$1", "symbols": [{"literal":"."}, "jsonfloat$ebnf$3$subexpression$1$ebnf$1"]},
    {"name": "jsonfloat$ebnf$3", "symbols": ["jsonfloat$ebnf$3$subexpression$1"], "postprocess": id},
    {"name": "jsonfloat$ebnf$3", "symbols": [], "postprocess": () => null},
    {"name": "jsonfloat$ebnf$4$subexpression$1$ebnf$1", "symbols": [/[+-]/], "postprocess": id},
    {"name": "jsonfloat$ebnf$4$subexpression$1$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "jsonfloat$ebnf$4$subexpression$1$ebnf$2", "symbols": [/[0-9]/]},
    {"name": "jsonfloat$ebnf$4$subexpression$1$ebnf$2", "symbols": ["jsonfloat$ebnf$4$subexpression$1$ebnf$2", /[0-9]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "jsonfloat$ebnf$4$subexpression$1", "symbols": [/[eE]/, "jsonfloat$ebnf$4$subexpression$1$ebnf$1", "jsonfloat$ebnf$4$subexpression$1$ebnf$2"]},
    {"name": "jsonfloat$ebnf$4", "symbols": ["jsonfloat$ebnf$4$subexpression$1"], "postprocess": id},
    {"name": "jsonfloat$ebnf$4", "symbols": [], "postprocess": () => null},
    {"name": "jsonfloat", "symbols": ["jsonfloat$ebnf$1", "jsonfloat$ebnf$2", "jsonfloat$ebnf$3", "jsonfloat$ebnf$4"], "postprocess": 
        function(d) {
            return parseFloat(
                (d[0] || "") +
                d[1].join("") +
                (d[2] ? "."+d[2][1].join("") : "") +
                (d[3] ? "e" + (d[3][1] || "+") + d[3][2].join("") : "")
            );
        }
        },
    {"name": "statements$ebnf$1", "symbols": []},
    {"name": "statements$ebnf$1", "symbols": ["statements$ebnf$1", "statement"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "statements", "symbols": ["statements$ebnf$1"]},
    {"name": "statement", "symbols": ["design_op"], "postprocess": id},
    {"name": "statement", "symbols": ["set_variable"], "postprocess": id},
    {"name": "statement", "symbols": ["import"], "postprocess": id},
    {"name": "statement", "symbols": ["from_import"], "postprocess": id},
    {"name": "set_variable", "symbols": ["variable", {"literal":"="}, "expr"], "postprocess": ([v, _, e]) => new Syntax.SetVariable(v, e)},
    {"name": "import$string$1", "symbols": [{"literal":"i"}, {"literal":"m"}, {"literal":"p"}, {"literal":"o"}, {"literal":"r"}, {"literal":"t"}], "postprocess": (d) => d.join('')},
    {"name": "import$string$2", "symbols": [{"literal":"a"}, {"literal":"s"}], "postprocess": (d) => d.join('')},
    {"name": "import", "symbols": ["import$string$1", "module_access", "import$string$2", "IDENTIFIER"], "postprocess": ([_, ma, _0, i]) => new Syntax.Import(ma, i)},
    {"name": "import$string$3", "symbols": [{"literal":"i"}, {"literal":"m"}, {"literal":"p"}, {"literal":"o"}, {"literal":"r"}, {"literal":"t"}], "postprocess": (d) => d.join('')},
    {"name": "import", "symbols": ["import$string$3", "module_access"], "postprocess": ([_, ma]) => new Syntax.Import(ma)},
    {"name": "from_import$string$1", "symbols": [{"literal":"f"}, {"literal":"r"}, {"literal":"o"}, {"literal":"m"}], "postprocess": (d) => d.join('')},
    {"name": "from_import$string$2", "symbols": [{"literal":"i"}, {"literal":"m"}, {"literal":"p"}, {"literal":"o"}, {"literal":"r"}, {"literal":"t"}], "postprocess": (d) => d.join('')},
    {"name": "from_import$ebnf$1", "symbols": []},
    {"name": "from_import$ebnf$1$subexpression$1", "symbols": [{"literal":","}, "IDENTIFIER"]},
    {"name": "from_import$ebnf$1", "symbols": ["from_import$ebnf$1", "from_import$ebnf$1$subexpression$1"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "from_import", "symbols": ["from_import$string$1", "module_access", "from_import$string$2", "IDENTIFIER", "from_import$ebnf$1"], "postprocess": (args) => new Syntax.FromImport(args[1], ...args.slice(3))},
    {"name": "design_op", "symbols": ["variable", {"literal":"="}, "variable", {"literal":"."}, "ADD_MOTIF", {"literal":"("}, "expr", {"literal":","}, "expr", {"literal":","}, "expr", {"literal":")"}], "postprocess": ([v, _, d, _0, _1, _2, m, _3, x, _4, y, _5]) => new Syntax.AddMotif(v, d, m, x, y, fresh)},
    {"name": "design_op", "symbols": ["variable", {"literal":"."}, "REMOVE_MOTIF", {"literal":"("}, "expr", {"literal":")"}], "postprocess": ([d, _, _0, _1, pm, _2]) => new Syntax.RemoveMotif(d, pm, fresh)},
    {"name": "design_op", "symbols": ["variable", {"literal":"="}, "variable", {"literal":"."}, "MOTIFIFY", {"literal":"("}, "expr", {"literal":","}, "expr", {"literal":","}, "expr", {"literal":","}, "expr", {"literal":")"}], "postprocess": ([v, _, d, _0, _1, _2, x0, _3, y0, _4, x1, _5, y1, _6]) => new Syntax.Motifify(v, d, x0, y0, x1, y1, fresh)},
    {"name": "design_op", "symbols": ["size_op"], "postprocess": id},
    {"name": "size_op", "symbols": ["variable", {"literal":"="}, "variable", {"literal":"."}, "ADD_ROW", "parenthesized_maybe_add_exprs"], "postprocess": (args) => new Syntax.AddRow(args[0], args[2], fresh, ...handle_undefined_add_exprs(args, 5))},
    {"name": "size_op", "symbols": ["variable", {"literal":","}, "variable", {"literal":"="}, "variable", {"literal":"."}, "REMOVE_ROW", "parenthesized_maybe_expr"], "postprocess": (args) => new Syntax.RemoveRow(args[0], args[2], args[4], args[7])},
    {"name": "size_op", "symbols": ["variable", {"literal":"="}, "variable", {"literal":"."}, "ADD_COLUMN", "parenthesized_maybe_add_exprs"], "postprocess": (args) => new Syntax.AddColumn(args[0], args[2], ...handle_undefined_add_exprs(args, 5))},
    {"name": "size_op", "symbols": ["variable", {"literal":","}, "variable", {"literal":"="}, "variable", {"literal":"."}, "REMOVE_COLUMN", "parenthesized_maybe_expr"], "postprocess": (args) => new Syntax.RemoveColumn(args[0], args[2], args[4], args[7])},
    {"name": "parenthesized_maybe_expr$ebnf$1", "symbols": ["expr"], "postprocess": id},
    {"name": "parenthesized_maybe_expr$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "parenthesized_maybe_expr", "symbols": [{"literal":"("}, "parenthesized_maybe_expr$ebnf$1", {"literal":")"}], "postprocess": (args) => (args.length === 3) ? args[2] : undefined},
    {"name": "parenthesized_maybe_add_exprs$ebnf$1", "symbols": ["add_exprs"], "postprocess": id},
    {"name": "parenthesized_maybe_add_exprs$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "parenthesized_maybe_add_exprs", "symbols": [{"literal":"("}, "parenthesized_maybe_add_exprs$ebnf$1", {"literal":")"}], "postprocess": (args) => (args.length === 3) ? args[2] : undefined},
    {"name": "add_exprs$ebnf$1", "symbols": []},
    {"name": "add_exprs$ebnf$1$subexpression$1", "symbols": [{"literal":","}, "expr"]},
    {"name": "add_exprs$ebnf$1", "symbols": ["add_exprs$ebnf$1", "add_exprs$ebnf$1$subexpression$1"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "add_exprs", "symbols": ["expr", "add_exprs$ebnf$1"], "postprocess": evens_only},
    {"name": "expr", "symbols": ["literal"], "postprocess": id},
    {"name": "expr", "symbols": ["variable"], "postprocess": id},
    {"name": "expr", "symbols": ["object_init"], "postprocess": id},
    {"name": "expr", "symbols": ["attr_access"], "postprocess": id},
    {"name": "expr", "symbols": ["module_ref"], "postprocess": id},
    {"name": "expr", "symbols": ["module_access"], "postprocess": id},
    {"name": "expr", "symbols": ["object_access"], "postprocess": id},
    {"name": "expr", "symbols": ["object_method_call"], "postprocess": id},
    {"name": "expr", "symbols": ["keyword_arg"], "postprocess": id},
    {"name": "literal", "symbols": ["int_number"], "postprocess": id},
    {"name": "literal", "symbols": ["float"], "postprocess": id},
    {"name": "literal", "symbols": ["str"], "postprocess": id},
    {"name": "literal", "symbols": ["list"], "postprocess": id},
    {"name": "int_number", "symbols": ["int"], "postprocess": ([i]) => new Syntax.Literal(parseInt(i))},
    {"name": "float", "symbols": ["decimal"], "postprocess": ([f]) => new Syntax.Literal(parseFloat(f))},
    {"name": "str", "symbols": ["dqstring"], "postprocess": ([s]) => new Syntax.Literal(s)},
    {"name": "list", "symbols": [{"literal":"["}, "literal_list", {"literal":"]"}], "postprocess": ([_, l, _0]) => l},
    {"name": "literal_list$ebnf$1", "symbols": []},
    {"name": "literal_list$ebnf$1$subexpression$1", "symbols": [{"literal":","}, "expr"]},
    {"name": "literal_list$ebnf$1", "symbols": ["literal_list$ebnf$1", "literal_list$ebnf$1$subexpression$1"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "literal_list", "symbols": ["expr", "literal_list$ebnf$1"], "postprocess": evens_only},
    {"name": "variable", "symbols": ["IDENTIFIER"], "postprocess": id},
    {"name": "object_init", "symbols": ["class_name", {"literal":"("}, "args_list", {"literal":")"}], "postprocess": ([cn, _, al, _0]) => new Syntax.ObjectInit(cn, ...al)},
    {"name": "args_list$ebnf$1", "symbols": []},
    {"name": "args_list$ebnf$1$subexpression$1", "symbols": [{"literal":","}, "expr"]},
    {"name": "args_list$ebnf$1", "symbols": ["args_list$ebnf$1", "args_list$ebnf$1$subexpression$1"], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "args_list", "symbols": ["expr", "args_list$ebnf$1"], "postprocess": evens_only},
    {"name": "attr_access", "symbols": ["expr", {"literal":"["}, "expr", {"literal":"]"}], "postprocess": ([obj, _, key, _0]) => new Syntax.AttrAccess(obj, key)},
    {"name": "module_ref", "symbols": ["IDENTIFIER"], "postprocess": ([i]) => new Syntax.ModuleRef(i)},
    {"name": "module_access", "symbols": ["module_access", {"literal":"."}, "IDENTIFIER"], "postprocess": ([ma, _, i]) => new Syntax.ModuleAccess(ma, i)},
    {"name": "module_access", "symbols": ["module_ref"], "postprocess": id},
    {"name": "object_access", "symbols": ["expr", {"literal":"."}, "IDENTIFIER"], "postprocess": ([e, _, i]) => new Syntax.ObjectAccess(e, i)},
    {"name": "object_method_call$ebnf$1", "symbols": ["args_list"], "postprocess": id},
    {"name": "object_method_call$ebnf$1", "symbols": [], "postprocess": () => null},
    {"name": "object_method_call", "symbols": ["expr", {"literal":"."}, "IDENTIFIER", {"literal":"("}, "object_method_call$ebnf$1", {"literal":")"}], "postprocess": ([e, _, name, _0, al, _1 ]) => new Syntax.ObjectMethodCall(e, name, ...((al === undefined) ?  [al] : []))},
    {"name": "keyword_arg", "symbols": ["IDENTIFIER", {"literal":"="}, "expr"], "postprocess": ([key, _, e]) => new Syntax.KeywordArg(key, e)},
    {"name": "class_name", "symbols": ["CAPITAL_IDENTIFIER"], "postprocess": id},
    {"name": "ADD_MOTIF$string$1", "symbols": [{"literal":"a"}, {"literal":"d"}, {"literal":"d"}, {"literal":"_"}, {"literal":"m"}, {"literal":"o"}, {"literal":"t"}, {"literal":"i"}, {"literal":"f"}], "postprocess": (d) => d.join('')},
    {"name": "ADD_MOTIF", "symbols": ["ADD_MOTIF$string$1"]},
    {"name": "REMOVE_MOTIF$string$1", "symbols": [{"literal":"r"}, {"literal":"e"}, {"literal":"m"}, {"literal":"o"}, {"literal":"v"}, {"literal":"e"}, {"literal":"_"}, {"literal":"m"}, {"literal":"o"}, {"literal":"t"}, {"literal":"i"}, {"literal":"f"}], "postprocess": (d) => d.join('')},
    {"name": "REMOVE_MOTIF", "symbols": ["REMOVE_MOTIF$string$1"]},
    {"name": "ADD_ROW$string$1", "symbols": [{"literal":"a"}, {"literal":"d"}, {"literal":"d"}, {"literal":"_"}, {"literal":"r"}, {"literal":"o"}, {"literal":"w"}], "postprocess": (d) => d.join('')},
    {"name": "ADD_ROW", "symbols": ["ADD_ROW$string$1"]},
    {"name": "ADD_COLUMN$string$1", "symbols": [{"literal":"a"}, {"literal":"d"}, {"literal":"d"}, {"literal":"_"}, {"literal":"c"}, {"literal":"o"}, {"literal":"l"}, {"literal":"u"}, {"literal":"m"}, {"literal":"n"}], "postprocess": (d) => d.join('')},
    {"name": "ADD_COLUMN", "symbols": ["ADD_COLUMN$string$1"]},
    {"name": "REMOVE_ROW$string$1", "symbols": [{"literal":"r"}, {"literal":"e"}, {"literal":"m"}, {"literal":"o"}, {"literal":"v"}, {"literal":"e"}, {"literal":"_"}, {"literal":"r"}, {"literal":"o"}, {"literal":"w"}], "postprocess": (d) => d.join('')},
    {"name": "REMOVE_ROW", "symbols": ["REMOVE_ROW$string$1"]},
    {"name": "REMOVE_COLUMN$string$1", "symbols": [{"literal":"r"}, {"literal":"e"}, {"literal":"m"}, {"literal":"o"}, {"literal":"v"}, {"literal":"e"}, {"literal":"_"}, {"literal":"c"}, {"literal":"o"}, {"literal":"l"}, {"literal":"u"}, {"literal":"m"}, {"literal":"n"}], "postprocess": (d) => d.join('')},
    {"name": "REMOVE_COLUMN", "symbols": ["REMOVE_COLUMN$string$1"]},
    {"name": "MOTIFIFY$string$1", "symbols": [{"literal":"m"}, {"literal":"o"}, {"literal":"t"}, {"literal":"i"}, {"literal":"f"}, {"literal":"i"}, {"literal":"f"}, {"literal":"y"}], "postprocess": (d) => d.join('')},
    {"name": "MOTIFIFY", "symbols": ["MOTIFIFY$string$1"]},
    {"name": "IDENTIFIER", "symbols": ["CNAME"], "postprocess": id},
    {"name": "CNAME$ebnf$1", "symbols": []},
    {"name": "CNAME$ebnf$1", "symbols": ["CNAME$ebnf$1", /[a-zA-Z0-9_]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "CNAME", "symbols": [/[a-z_]/, "CNAME$ebnf$1"], "postprocess": ([begin, end]) => begin + end.join("")},
    {"name": "CAPITAL_IDENTIFIER$ebnf$1", "symbols": []},
    {"name": "CAPITAL_IDENTIFIER$ebnf$1", "symbols": ["CAPITAL_IDENTIFIER$ebnf$1", /[a-zA-Z0-9_]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "CAPITAL_IDENTIFIER", "symbols": [/[A-Z]/, "CAPITAL_IDENTIFIER$ebnf$1"], "postprocess": ([begin, end]) => begin + end.join("")},
    {"name": "COMMENT$ebnf$1", "symbols": []},
    {"name": "COMMENT$ebnf$1", "symbols": ["COMMENT$ebnf$1", /[^\n]/], "postprocess": (d) => d[0].concat([d[1]])},
    {"name": "COMMENT", "symbols": [{"literal":"#"}, "COMMENT$ebnf$1", "NEWLINE"], "postprocess": () => []},
    {"name": "NEWLINE", "symbols": [{"literal":"\n"}]}
  ],
  ParserStart: "statements",
};

export default grammar;
