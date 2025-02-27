import lark
from lark import ast_utils, Transformer, v_args
# from modularmotifs.dsl._syntax import *
from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum
import sys
from modularmotifs.dsl._grammar import grammar
import modularmotifs.dsl._syntax as syn


# following this tutorial https://github.com/lark-parser/lark/blob/master/examples/advanced/create_ast.py

class _Ast(ast_utils.Ast):
    # skipped
    
    def to_syntax(self, fresh: syn.FreshVar) -> syn.Syntax:
        pass
    pass


class _Statement(_Ast):
    # skipped
    pass

class _Expr(_Ast):
    # skipped
    pass

@dataclass
class Variable(_Expr):
    name: str
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.Variable(self.name)
    pass

@dataclass
class ModuleRef(_Expr):
    name: str
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ModuleRef(self.name)

@dataclass
class ModuleAccess(_Expr):
    ma: 'ModuleAccess'
    accessed: str
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ModuleAccess(self.ma.to_syntax(fresh), self.accessed)
    
@dataclass
class Statements(_Ast, ast_utils.AsList):
    statements: list[_Statement]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return list(map(lambda x: x.to_syntax(fresh), self.statements))
    pass

@dataclass
class Import(_Statement):
    ma: ModuleAccess
    as_clause: Optional[str]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.Import(self.ma.to_syntax(fresh),
                          self.as_clause)
    

@dataclass
class FromImport(_Statement):
    ma: ModuleAccess
    imports: list[str]
    
    def __init__(self, ma: ModuleAccess, *imports):
        self.ma = ma
        self.imports = imports
        
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.FromImport(self.ma.to_syntax(fresh), *self.imports)
    pass

@dataclass
class SetVariable(_Statement):
    v: Variable
    e: _Expr
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.SetVariable(self.v.to_syntax(fresh), self.e.to_syntax(fresh))

class _DesignOp(_Statement):
    # skipped
    pass

@dataclass
class AddMotif(_DesignOp):
    v: Variable
    d: Variable
    m: _Expr
    x: _Expr
    y: _Expr
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.AddMotif(self.v.to_syntax(fresh),
                            self.d.to_syntax(fresh),
                            self.m.to_syntax(fresh),
                            self.x.to_syntax(fresh),
                            self.y.to_syntax(fresh),
                            fresh)

@dataclass
class RemoveMotif(_DesignOp):
    d: Variable
    pm: _Expr
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.RemoveMotif(self.d.to_syntax(fresh),
                               self.pm.to_syntax(fresh),
                               fresh)

class _SizeOp(_DesignOp):
    # skipped
    pass
    

@dataclass
class AddRow(_SizeOp):
    v: Variable
    d: Variable
    at_index: Optional[_Expr]
    contents: Optional[_Expr]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.AddRow(self.v.to_syntax(fresh),
                          self.d.to_syntax(fresh),
                          fresh,
                          at_index=self.at_index.to_syntax(fresh) if self.at_index else None,
                          contents=self.contents.to_syntax(fresh) if self.contents else None
                          )
    
@dataclass
class AddColumn(_SizeOp):
    v: Variable
    d: Variable
    at_index: Optional[_Expr]
    contents: Optional[_Expr]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.AddColumn(self.v.to_syntax(fresh),
                             self.d.to_syntax(fresh),
                             fresh,
                             at_index=self.at_index.to_syntax(fresh) if self.at_index else None,
                             contents=self.contents.to_syntax(fresh) if self.contents else None
                             )

@dataclass
class RemoveRow(_SizeOp):
    i: Variable
    r: Variable
    d: Variable
    at_index: Optional[_Expr]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.RemoveRow(self.i.to_syntax(fresh),
                             self.r.to_syntax(fresh),
                             self.d.to_syntax(fresh),
                             fresh,
                             at_index=self.at_index.to_syntax(fresh) if self.at_index else None
                             )

@dataclass
class RemoveColumn(_SizeOp):
    i: Variable
    r: Variable
    d: Variable
    at_index: Optional[_Expr]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.RemoveColumn(self.i.to_syntax(fresh),
                                self.r.to_syntax(fresh),
                                self.d.to_syntax(fresh),
                                fresh,
                                at_index=self.at_index.to_syntax(fresh) if self.at_index else None
                                )

@dataclass
class Literal(_Expr):
    c: Union[int, float, str, list[_Expr]]
    
    def to_syntax(self, fresh: syn.FreshVar):
        if isinstance(self.c, list):
            return syn.Literal(list(map(lambda x: x.to_syntax(fresh), self.c)))
        return syn.Literal(self.c)

@dataclass
class ObjectInit(_Expr):
    className: str
    args: list[_Expr]
    
    def to_syntax(self, fresh: syn.FreshVar):
        args = list(map(lambda x: x.to_syntax(fresh), self.args)) if isinstance(self.args, list) else self.args.to_syntax(fresh)
        if isinstance(self.args, list):
            return syn.ObjectInit(self.className, *args)
        return syn.ObjectInit(self.className,
                              args)
        
@dataclass
class ObjectAccess(_Expr):
    v: Variable
    prop: str
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ObjectAccess(self.v.to_syntax(fresh),
                                self.prop)

@dataclass
class ObjectMethodCall(_Expr):
    v: Variable
    method: str
    args: list[_Expr]
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ObjectMethodCall(self.v.to_syntax(fresh),
                                    self.method,
                                    *list(map(lambda x: x.to_syntax(fresh),
                                              self.args)))
    
@dataclass
class AttrAccess(_Expr):
    obj: _Expr
    key: _Expr
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.AttrAccess(self.obj.to_syntax(fresh),
                              self.key.to_syntax(fresh))
# class 

@dataclass
class KeywordArg(_Expr):
    key: str 
    e: _Expr
    
    def to_syntax(self, fresh: syn.FreshVar):
        return syn.KeywordArg(self.key,
                              self.e.to_syntax(fresh))

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
    # def variable(self, args):
    #     print("Variable: ", args)
    #     return Variable(args[0])
    
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
            return RemoveRow(args[0], args[1], args[2], at_index)
            pass
        elif Ops.REMOVE_COLUMN in args:
            assert len(args) >= 4
            at_index, _ = deal_with_optionals(args[1:])
            return RemoveColumn(args[0], args[1], args[2], at_index)
            pass
        return args
    
    def from_import(self, module, *imports):
        return FromImport(module, imports)
    pass

parser = lark.Lark(grammar, start="statements")

this_module = sys.modules[__name__]
transformer = ast_utils.create_transformer(this_module, ToAst())

def parse(f: str):
    return transformer.transform(parser.parse(f))

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
    print(parsed)
    fresher = syn.FreshVar(base_name="z")
    print("\n".join(list(map(lambda x: x.to_python(), parsed.to_syntax(fresher)))))