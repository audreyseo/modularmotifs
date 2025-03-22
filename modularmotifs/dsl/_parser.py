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


def _set(s: str) -> set[str]:
    # Just creates the singleton set
    return set([s])


class _Ast(ast_utils.Ast):
    # skipped

    def to_syntax(self, fresh: syn.FreshVar) -> syn.Syntax:
        pass

    def get_idents(self) -> set[str]:
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

    def get_idents(self) -> set[str]:
        return _set(self.name)

    pass


@dataclass
class ModuleRef(_Expr):
    name: str

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ModuleRef(self.name)

    def get_idents(self) -> set[str]:
        return _set(self.name)


@dataclass
class ModuleAccess(_Expr):
    ma: "ModuleAccess"
    accessed: str

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ModuleAccess(self.ma.to_syntax(fresh), self.accessed)

    def get_idents(self) -> set[str]:
        return self.ma.get_idents().union(_set(self.accessed))


@dataclass
class Statements(_Ast, ast_utils.AsList):
    statements: list[_Statement]

    def to_syntax(self, fresh: syn.FreshVar):
        return list(map(lambda x: x.to_syntax(fresh), self.statements))

    def get_idents(self) -> set[str]:
        idents = set()
        for stmt in self.statements:
            idents = idents.union(stmt.get_idents())
            pass
        return idents

    pass


@dataclass
class Import(_Statement):
    ma: ModuleAccess
    as_clause: Optional[str]

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.Import(self.ma.to_syntax(fresh), self.as_clause)

    def get_idents(self) -> set[str]:
        return self.ma.get_idents().union(
            _set(self.as_clause) if self.as_clause else set()
        )


@dataclass
class FromImport(_Statement):
    ma: ModuleAccess
    imports: list[str]

    def __init__(self, ma: ModuleAccess, *imports):
        self.ma = ma
        self.imports = imports

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.FromImport(self.ma.to_syntax(fresh), *self.imports)

    def get_idents(self) -> set[str]:
        return self.ma.get_idents().union(set(self.imports))

    pass


@dataclass
class SetVariable(_Statement):
    v: Variable
    e: _Expr

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.SetVariable(self.v.to_syntax(fresh), self.e.to_syntax(fresh))

    def get_idents(self) -> set[str]:
        return self.v.get_idents().union(self.e.get_idents())


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
        return syn.AddMotif(
            self.v.to_syntax(fresh),
            self.d.to_syntax(fresh),
            self.m.to_syntax(fresh),
            self.x.to_syntax(fresh),
            self.y.to_syntax(fresh),
            fresh,
        )

    def get_idents(self) -> set[str]:
        return (
            self.v.get_idents()
            .union(self.d.get_idents())
            .union(self.m.get_idents())
            .union(self.x.get_idents())
            .union(self.y.get_idents())
        )


@dataclass
class RemoveMotif(_DesignOp):
    d: Variable
    pm: _Expr

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.RemoveMotif(self.d.to_syntax(fresh), self.pm.to_syntax(fresh), fresh)

    def get_idents(self) -> set[str]:
        return self.d.get_idents().union(self.pm.get_idents())

    pass


@dataclass
class Motifify(_DesignOp):
    v: Variable
    d: Variable
    x0: _Expr
    y0: _Expr
    x1: _Expr
    y1: _Expr

    def to_syntax(self, fresh):
        return syn.Motifify(
            self.v.to_syntax(fresh),
            self.d.to_syntax(fresh),
            self.x0.to_syntax(fresh),
            self.y0.to_syntax(fresh),
            self.x1.to_syntax(fresh),
            self.y1.to_syntax(fresh),
            fresh,
        )

    def get_idents(self):
        s = self.v.get_idents()
        s = s.union(self.d.get_idents())
        s = s.union(self.x0.get_idents()).union(self.y0.get_idents())
        s = s.union(self.x1.get_idents()).union(self.y1.get_idents())
        return s


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
        return syn.AddRow(
            self.v.to_syntax(fresh),
            self.d.to_syntax(fresh),
            fresh,
            at_index=self.at_index.to_syntax(fresh) if self.at_index else None,
            contents=self.contents.to_syntax(fresh) if self.contents else None,
        )

    def get_idents(self) -> set[str]:
        idents = self.v.get_idents().union(self.d.get_idents())
        if self.at_index:
            idents = idents.union(self.at_index.get_idents())
            pass
        if self.contents:
            idents = idents.union(self.contents.get_idents())
            pass
        return idents


@dataclass
class AddColumn(_SizeOp):
    v: Variable
    d: Variable
    at_index: Optional[_Expr]
    contents: Optional[_Expr]

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.AddColumn(
            self.v.to_syntax(fresh),
            self.d.to_syntax(fresh),
            fresh,
            at_index=self.at_index.to_syntax(fresh) if self.at_index else None,
            contents=self.contents.to_syntax(fresh) if self.contents else None,
        )

    def get_idents(self) -> set[str]:
        idents = self.v.get_idents().union(self.d.get_idents())
        if self.at_index:
            idents = idents.union(self.at_index.get_idents())
            pass
        if self.contents:
            idents = idents.union(self.contents.get_idents())
            pass
        return idents


@dataclass
class RemoveRow(_SizeOp):
    i: Variable
    r: Variable
    d: Variable
    at_index: Optional[_Expr]

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.RemoveRow(
            self.i.to_syntax(fresh),
            self.r.to_syntax(fresh),
            self.d.to_syntax(fresh),
            fresh,
            at_index=self.at_index.to_syntax(fresh) if self.at_index else None,
        )

    def get_idents(self) -> set[str]:
        idents = self.at_index.get_idents() if self.at_index else set()
        return (
            idents.union(self.i.get_idents())
            .union(self.r.get_idents())
            .union(self.d.get_idents())
        )


@dataclass
class RemoveColumn(_SizeOp):
    i: Variable
    r: Variable
    d: Variable
    at_index: Optional[_Expr]

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.RemoveColumn(
            self.i.to_syntax(fresh),
            self.r.to_syntax(fresh),
            self.d.to_syntax(fresh),
            fresh,
            at_index=self.at_index.to_syntax(fresh) if self.at_index else None,
        )

    def get_idents(self) -> set[str]:
        idents = self.at_index.get_idents() if self.at_index else set()
        return (
            idents.union(self.i.get_idents())
            .union(self.r.get_idents())
            .union(self.d.get_idents())
        )


def _expr_list_to_idents(exprs):
    assert isinstance(exprs, list)

    idents = set()
    for e in exprs:
        if isinstance(e, _Expr):
            idents = idents.union(e.get_idents())
            pass
        pass
    return idents


@dataclass
class Literal(_Expr):
    c: Union[int, float, str, list[_Expr]]

    def to_syntax(self, fresh: syn.FreshVar):
        if isinstance(self.c, list):
            return syn.Literal(list(map(lambda x: x.to_syntax(fresh), self.c)))
        return syn.Literal(self.c)

    def get_idents(self) -> set[str]:
        if isinstance(self.c, list):
            return _expr_list_to_idents(self.c)
        return set()


@dataclass
class ObjectInit(_Expr):
    className: str
    args: list[_Expr]

    def to_syntax(self, fresh: syn.FreshVar):
        args = (
            list(map(lambda x: x.to_syntax(fresh), self.args))
            if isinstance(self.args, list)
            else self.args.to_syntax(fresh)
        )
        if isinstance(self.args, list):
            return syn.ObjectInit(self.className, *args)
        return syn.ObjectInit(self.className, args)

    def get_idents(self) -> set[str]:
        return _set(self.className).union(_expr_list_to_idents(self.args))


@dataclass
class ObjectAccess(_Expr):
    v: Variable
    prop: str

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ObjectAccess(self.v.to_syntax(fresh), self.prop)

    def get_idents(self) -> set[str]:
        return self.v.get_idents()


@dataclass
class ObjectMethodCall(_Expr):
    v: Variable
    method: str
    args: list[_Expr]

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.ObjectMethodCall(
            self.v.to_syntax(fresh),
            self.method,
            *list(map(lambda x: x.to_syntax(fresh), self.args)),
        )

    def get_idents(self) -> set[str]:
        return self.v.get_idents().union(_expr_list_to_idents(self.args))


@dataclass
class AttrAccess(_Expr):
    obj: _Expr
    key: _Expr

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.AttrAccess(self.obj.to_syntax(fresh), self.key.to_syntax(fresh))

    def get_idents(self) -> set[str]:
        return self.obj.get_idents().union(self.key.get_idents())


# class


@dataclass
class KeywordArg(_Expr):
    key: str
    e: _Expr

    def to_syntax(self, fresh: syn.FreshVar):
        return syn.KeywordArg(self.key, self.e.to_syntax(fresh))

    def get_idents(self) -> set[str]:
        return self.e.get_idents()


class Ops(Enum):
    ADD_MOTIF = 1
    REMOVE_MOTIF = 2
    ADD_ROW = 3
    ADD_COLUMN = 4
    REMOVE_ROW = 5
    REMOVE_COLUMN = 6
    MOTIFIFY = 7


class ToAst(Transformer):

    def ADD_MOTIF(self, x):
        return Ops.ADD_MOTIF

    def REMOVE_MOTIF(self, x):
        return Ops.REMOVE_MOTIF

    def MOTIFIFY(self, x):
        return Ops.MOTIFIFY

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
        elif Ops.MOTIFIFY in args:
            assert len(args) == 7
            return Motifify(args[0], args[1], args[3], args[4], args[5], args[6])
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

            at_index = get_first(
                list(filter(lambda n: n.key == "at_index", optional_args))
            )
            contents = get_first(
                list(
                    filter(
                        lambda n: n.key == "contents" or n.key == "contents",
                        optional_args,
                    )
                )
            )
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


def parse(f: str) -> tuple[syn.DesignProgramBuilder, syn.DesignInterpreter]:
    ast = transformer.transform(parser.parse(f))
    used_idents = ast.get_idents()
    fresh = syn.FreshVar(names_to_avoid=used_idents)
    syntax_list = ast.to_syntax(fresh)
    return syn.DesignProgramBuilder.init_list(syntax_list, fresh)


if __name__ == "__main__":
    import argparse
    import os
    import sys

    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=str, help="A file name to parse")
    args = ap.parse_args()
    if not os.path.exists(args.file):
        print(f'Could not find file "{args.file}"', file=sys.stderr)
        exit(1)
        pass
    with open(args.file, "r") as f:
        text = f.read()
        pass
    parsed = transformer.transform(parser.parse(text))

    print(parsed)
    fresher = syn.FreshVar(base_name="z", names_to_avoid=parsed.get_idents())
    print("\n".join(list(map(lambda x: x.to_python(), parsed.to_syntax(fresher)))))
    # print(parsed.get_idents())
    dpb, interp = syn.DesignProgramBuilder.init_list(parsed.to_syntax(fresher), fresher)
    print(dpb.to_python())
    print(interp.design)
