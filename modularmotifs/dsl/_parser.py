import lark
from lark import ast_utils, Transformer, v_args
# from modularmotifs.dsl._syntax import *
from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum
import sys
from modularmotifs.dsl._grammar import grammar



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
class RemoveMotif(_DesignOp):
    d: str
    pm: _Expr

class _SizeOp(_DesignOp):
    # skipped
    pass
    

@dataclass
class AddRow(_SizeOp):
    v: str
    d: str
    at_index: Optional[_Expr]
    contents: Optional[_Expr]
    
@dataclass
class AddColumn(_SizeOp):
    v: str
    d: str
    at_index: Optional[_Expr]
    contents: Optional[_Expr]

@dataclass
class RemoveRow(_SizeOp):
    i: str
    r: str
    at_index: Optional[_Expr]

@dataclass
class RemoveColumn(_SizeOp):
    i: str
    r: str
    at_index: Optional[_Expr]

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

@dataclass
class KeywordArg(_Expr):
    key: str 
    e: _Expr

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
        return Literal(int(d))
    
    def FLOAT_NUMBER(self, f):
        return Literal(float(f))
    
    def STRING(self, s):
        return Literal(s[1:-1])
    
    def literal_list(self, l):
        return Literal(l)
    
    def args_list(self, args):
        return args
    
    def add_exprs(self, args):
        return args
    
    def design_op(self, args):
        print(repr(args))
        # print(len(args))
        print(Ops.ADD_MOTIF in args)
        if Ops.ADD_MOTIF in args:
            assert len(args) == 6
            return AddMotif(args[0], args[1], args[3], args[4], args[5])
        elif Ops.REMOVE_MOTIF in args:
            # assert len(args) == 
            pass
        return args
    
    def size_op(self, args):
        def deal_with_optionals(args):
            if len(args) == 3:
                return None, None
            optional_args = args[3]
            
            if not isinstance(optional_args, list):
                optional_args = [optional_args]
            def get_first(listy):
                if listy:
                    return listy[0]
                return None
            if not optional_args:
                return None, None
            
            assert all(isinstance(n, KeywordArg) for n in optional_args)
            
            at_index = get_first(list(filter(lambda n: n.key == "at_index", optional_args)))
            contents = get_first(list(filter(lambda n: n.key == "column_contents" or n.key == "row_contents", optional_args)))
            return at_index, contents
        
        print(repr(args))
        print(Ops.ADD_ROW in args)
        if Ops.ADD_ROW in args:
            assert len(args) >= 3
            at_index, contents = deal_with_optionals(args)
            return AddRow(args[0], args[1], at_index, contents)
        elif Ops.ADD_COLUMN in args:
            assert len(args) >= 3
            at_index, contents = deal_with_optionals(args)
            
            return AddColumn(args[0], args[1], at_index, contents)
        elif Ops.REMOVE_ROW in args:
            assert len(args) >= 4
            at_index, _ = deal_with_optionals(args[1:])
            return RemoveRow(args[0], args[1], at_index)
            pass
        elif Ops.REMOVE_COLUMN in args:
            assert len(args) >= 4
            at_index, _ = deal_with_optionals(args[1:])
            return RemoveColumn(args[0], args[1], at_index)
            pass
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
        print(f"Could not find file \"{args.file}\"", file=sys.stderr)
        exit(1)
        pass
    with open(args.file, "r") as f:
        text = f.read()
        pass
    parsed = parse(text)
    print(parsed.pretty())
    print(transformer.transform(parsed))