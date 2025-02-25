import lark
from lark import ast_utils, Transformer, v_args
# from modularmotifs.dsl._syntax import *
from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum
import sys

grammar = r"""
?statements : statement*

?statement : design_op
           | set_variable
           | import
           | from_import

?set_variable : variable "=" expr

?import : "import" module_access "as" IDENTIFIER
        | "import" module_access

?from_import : "from" module_access "import" IDENTIFIER ("," IDENTIFIER)*

?module : IDENTIFIER

?design_op : variable "=" variable "." ADD_MOTIF "(" expr "," expr "," expr ")"
           | variable "." REMOVE_MOTIF "(" variable ")"
           | size_op

?size_op : variable "=" variable "." ADD_ROW "(" add_exprs? ")"
         | variable "," variable "=" variable "." REMOVE_ROW "(" expr? ")"
         | variable "=" variable "." ADD_COLUMN "(" add_exprs ")"
         | variable "," variable "=" variable "." REMOVE_COLUMN "(" expr? ")"

?add_exprs : expr "," expr
           | expr


?expr : literal
      | variable
      | object_init
      | attr_access
      | module_ref
      | module_access
      | object_access
      | object_method_call
      | keyword_arg

?literal : int
         | float
         | str
         | list

?int : INT_NUMBER

?float : FLOAT_NUMBER

?str : STRING

?list : "[" args_list "]"

?variable : IDENTIFIER

?object_init : class_name "(" args_list ")"

?args_list : [expr ("," expr)*]

?attr_access : expr "[" expr "]"

?module_ref :  IDENTIFIER

?module_access : module_access "." IDENTIFIER
               | module_ref

?object_access : expr "." IDENTIFIER

?object_method_call : expr "." IDENTIFIER "(" args_list ")"

?keyword_arg : IDENTIFIER "=" expr

?class_name : CAPITAL_IDENTIFIER


ADD_MOTIF : "add_motif"
REMOVE_MOTIF : "remove_motif"
ADD_ROW : "add_row"
ADD_COLUMN : "add_column"
REMOVE_ROW : "remove_row"
REMOVE_COLUMN : "remove_column"

IDENTIFIER : CNAME

CAPITAL_IDENTIFIER : /[A-Z][a-zA-Z0-9_]*/

COMMENT: "#" /[^\n]*/ NEWLINE

NEWLINE: /[\n]/
INT_NUMBER : /-?\d+/
FLOAT_NUMBER : /-?\d+\.\d+/

%import common.ESCAPED_STRING   -> STRING


%import common.CNAME
%import common.WS

%ignore WS
%ignore COMMENT
%ignore NEWLINE

"""


# following this tutorial https://github.com/lark-parser/lark/blob/master/examples/advanced/create_ast.py

class _Ast(ast_utils.Ast):
    # skipped
    pass


class _Statement(_Ast):
    # skipped
    pass

class _Expr(_Ast):
    # skipped
    pass

@dataclass
class ModuleAccess(_Expr):
    ma: 'ModuleAccess'
    accessed: str
    
@dataclass
class Statements(_Ast, ast_utils.AsList):
    statements: list[_Statement]
    pass

@dataclass
class Import(_Statement):
    ma: ModuleAccess
    as_clause: Optional[_Expr]

@dataclass
class FromImport(_Statement):
    ma: ModuleAccess
    imports: list[str]
    pass

@dataclass
class SetVariable(_Statement):
    v: str
    e: _Expr

class _DesignOp(_Statement):
    # skipped
    pass

@dataclass
class AddMotif(_DesignOp):
    v: str
    d: str
    m: _Expr
    x: _Expr
    y: _Expr

@dataclass
class Literal(_Expr):
    c: Union[int, float, str, list]

@dataclass
class ObjectInit(_Expr):
    className: str
    args: list[_Expr]
    
@dataclass
class AttrAccess(_Expr):
    obj: _Expr
    key: _Expr
# class 


class Ops(Enum):
    ADD_MOTIF = 1
    REMOVE_MOTIF = 2
    ADD_ROW = 3
    ADD_COLUMN = 4
    REMOVE_ROW = 5
    REMOVE_COLUMN = 6

class ToAst(Transformer):
    
    def ADD_MOTIF(self, x):
        return Ops.ADD_MOTIF
    
    def REMOVE_MOTIF(self, x):
        return Ops.REMOVE_MOTIF
    
    def ADD_ROW(self, x):
        return Ops.ADD_ROW
    
    def ADD_COLUMN(self, x):
        return Ops.ADD_COLUMN
    
    def REMOVE_ROW(self, x):
        return Ops.REMOVE_ROW
    
    def REMOVE_COLUMN(self, x):
        return Ops.REMOVE_COLUMN
    
    def IDENTIFIER(self, x):
        return str(x)
    
    def CAPITAL_IDENTIFIER(self, x):
        return str(x)
    
    def INT_NUMBER(self, d):
        return int(d)
    
    def FLOAT_NUMBER(self, f):
        return float(f)
    
    def STRING(self, s):
        return s[1:-1]
    
    def args_list(self, *args):
        return args
    
    
    def design_op(self, *args):
        print(repr(args))
        if Ops.ADD_MOTIF in args:
            assert len(args) == 6
            return AddMotif(args[0], args[1], args[3], args[4], args[5])
        return args
    
    def from_imports(self, module, *imports):
        return FromImport(module, imports)
    pass

parser = lark.Lark(grammar, start="statements")

this_module = sys.modules[__name__]
transformer = ast_utils.create_transformer(this_module, ToAst())

def parse(f: str):
    return parser.parse(f)

if __name__ == "__main__":
    import argparse
    import os
    import sys
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=str, help="A file name to parse")
    args = ap.parse_args()
    if not os.path.exists(args.file):
        print(f"Could not find file {args.file}", file=sys.stderr)
        pass
    with open(args.file, "r") as f:
        text = f.read()
        pass
    parsed = parse(text)
    print(parsed.pretty())
    print(transformer.transform(parsed))