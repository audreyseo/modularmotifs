@preprocessor typescript

@builtin "string.ne"
@builtin "number.ne"

@{%
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

%}

statements -> statement:*

statement -> design_op    {% id %}
           | set_variable {% id %}
           | import       {% id %}
           | from_import  {% id %}

set_variable -> variable "=" expr {% ([v, _, e]) => new Syntax.SetVariable(v, e) %}

import -> "import" module_access "as" IDENTIFIER {% ([_, ma, _0, i]) => new Syntax.Import(ma, i) %}
        | "import" module_access {% ([_, ma]) => new Syntax.Import(ma) %}

from_import -> "from" module_access "import" IDENTIFIER ("," IDENTIFIER):* {% (args) => new Syntax.FromImport(args[1], ...args.slice(3)) %}

# module -> IDENTIFIER

design_op -> variable "=" variable "." ADD_MOTIF "(" expr "," expr "," expr ")"
            {% ([v, _, d, _0, _1, _2, m, _3, x, _4, y, _5]) => new Syntax.AddMotif(v, d, m, x, y, fresh) %}
           | variable "." REMOVE_MOTIF "(" expr ")"
            {% ([d, _, _0, _1, pm, _2]) => new Syntax.RemoveMotif(d, pm, fresh) %}
           | variable "=" variable "." MOTIFIFY "(" expr "," expr "," expr "," expr ")"
            {% ([v, _, d, _0, _1, _2, x0, _3, y0, _4, x1, _5, y1, _6]) => new Syntax.Motifify(v, d, x0, y0, x1, y1, fresh) %}
           | size_op 
            {% id %}

size_op -> variable "=" variable "." ADD_ROW parenthesized_maybe_add_exprs
           {% (args) => new Syntax.AddRow(args[0], args[2], fresh, ...handle_undefined_add_exprs(args, 5)) %}
         | variable "," variable "=" variable "." REMOVE_ROW parenthesized_maybe_expr
           {% (args) => new Syntax.RemoveRow(args[0], args[2], args[4], args[7]) %}
         | variable "=" variable "." ADD_COLUMN parenthesized_maybe_add_exprs
           {% (args) => new Syntax.AddColumn(args[0], args[2], ...handle_undefined_add_exprs(args, 5)) %}
         | variable "," variable "=" variable "." REMOVE_COLUMN parenthesized_maybe_expr
           {% (args) => new Syntax.RemoveColumn(args[0], args[2], args[4], args[7]) %}

parenthesized_maybe_expr -> "(" expr:? ")" {% (args) => (args.length === 3) ? args[2] : undefined %}

parenthesized_maybe_add_exprs -> "(" add_exprs:? ")" {% (args) => (args.length === 3) ? args[2] : undefined %}

add_exprs -> expr ("," expr):* {% evens_only %}

# add_exprs -> expr "," expr
#            | expr


expr -> literal             {% id %}
      | variable            {% id %}
      | object_init         {% id %}
      | attr_access         {% id %}
      | module_ref          {% id %}
      | module_access       {% id %}
      | object_access       {% id %}
      | object_method_call  {% id %}
      | keyword_arg         {% id %}

literal -> int_number   {% id %}
         | float        {% id %}
         | str          {% id %}
         | list         {% id %}

int_number -> int   {% ([i]) => new Syntax.Literal(parseInt(i)) %}

float -> decimal    {% ([f]) => new Syntax.Literal(parseFloat(f)) %}

str -> dqstring     {% ([s]) => new Syntax.Literal(s) %}

list -> "[" literal_list "]"{% ([_, l, _0]) => l %}

literal_list -> expr ("," expr):* {% evens_only %}

variable -> IDENTIFIER  {% id %}

object_init -> class_name "(" args_list ")" {% ([cn, _, al, _0]) => new Syntax.ObjectInit(cn, ...al) %}

args_list -> expr ("," expr):* {% evens_only %}

attr_access -> expr "[" expr "]" {% ([obj, _, key, _0]) => new Syntax.AttrAccess(obj, key) %}

module_ref ->  IDENTIFIER {% ([i]) => new Syntax.ModuleRef(i) %}

module_access -> module_access "." IDENTIFIER {% ([ma, _, i]) => new Syntax.ModuleAccess(ma, i) %}
               | module_ref {% id %}

object_access -> expr "." IDENTIFIER {% ([e, _, i]) => new Syntax.ObjectAccess(e, i) %}

object_method_call -> expr "." IDENTIFIER "(" args_list:? ")" 
            {% ([e, _, name, _0, al, _1 ]) => new Syntax.ObjectMethodCall(e, name, ...((al === undefined) ?  [al] : [])) %}

keyword_arg -> IDENTIFIER "=" expr {% ([key, _, e]) => new Syntax.KeywordArg(key, e) %}

class_name -> CAPITAL_IDENTIFIER {% id %}



ADD_MOTIF -> "add_motif"
REMOVE_MOTIF -> "remove_motif"
ADD_ROW -> "add_row"
ADD_COLUMN -> "add_column"
REMOVE_ROW -> "remove_row"
REMOVE_COLUMN -> "remove_column"
MOTIFIFY -> "motifify"

IDENTIFIER -> CNAME {% id %}

CNAME -> [a-z_] [a-zA-Z0-9_]:* {% ([begin, end]) => begin + end.join("") %}

CAPITAL_IDENTIFIER -> [A-Z] [a-zA-Z0-9_]:* {% ([begin, end]) => begin + end.join("") %}

COMMENT -> "#" [^\n]:* NEWLINE {% () => [] %}

NEWLINE -> "\n"


