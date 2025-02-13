import abc
# TODO: I think we would want to replace TypeGuard with TypeIs if we were all using Python 3.13...
from typing import Union, TypeGuard, Self

class FreshVar:
    """A source of fresh variable names
    """
    def __init__(self, base_name="x"):
        self.current = 0
        self.base_name = base_name
        pass

    def get_fresh(self) -> str:
        fresh = f"{self.base_name}{self.current}"
        self.current += 1
        return fresh
        

class Syntax(abc.ABC):
    cn = __qualname__
    
    def __init__(self):
        self.cn = self.__class__.__qualname__
        pass

    def __repr__(self) -> str:
        return f"{self.cn}"

    @abc.abstractmethod
    def to_python(self) -> str:
        return ""

    def __str__(self) -> str:
        return self.to_python()
    pass


class Import(Syntax):
    # cn = __qualname__
    imported_module: str
    def __init__(self, mod: str):
        super().__init__()
        self.imported_module = mod
        pass

    def __repr__(self) -> str:
        return f"{self.cn}({self.imported_module})"

    def to_python(self) -> str:
        return f"import {self.imported_module}"
    pass

class Expr(Syntax):
    cn = __qualname__
    pass

primitive = Union[int, float, str]

class Literal(Expr):
    # cn = __qualname__
    def __init__(self, const: Union[primitive, list[primitive]]):
        super().__init__()
        self.const = const
        if isinstance(const, primitive):
            print("primitive")
            pass
        else:
            print("list")
            pass
        pass

    def is_int(self) -> TypeGuard[int]:
        return isinstance(self.const, int)

    def is_str(self) -> TypeGuard[str]:
        return isinstance(self.const, str)

    def is_float(self) -> TypeGuard[float]:
        return isinstance(self.const, float)

    def is_list(self) -> TypeGuard[list[primitive]]:
        return isinstance(self.const, list[primitive])


    def __repr__(self) -> str:
        return f"{self.cn}({self.to_python()})"

    def to_python(self) -> str:
        if self.is_str():
            return "\"" + self.const + "\""
        return str(self.const)
    pass

class Variable(Expr):
    # cn = __qualname__
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        pass

    def __repr__(self) -> str:
        return f"{self.cn}({self.name})"
    
    def to_python(self) -> str:
        return self.name

class ObjectInit(Expr):
    cn = __qualname__
    def __init__(self, *args: Expr):
        super().__init__()
        pass
    pass

class ObjectAccess(Expr):
    def __init__(self, v: Variable, prop: str):
        super().__init__()
        self.v = v
        self.prop = p
        pass

    def to_python(self) -> str:
        return f"{self.v}.{self.prop}"
    pass

class ObjectMethodCall(Expr):
    def __init__(self, v: Variable, method: str, *args: Expr):
        super().__init__()
        self.v = v
        self.method = method
        self.args = args
        pass

    def to_python(self) -> str:
        args = ", ".join(list(map(lambda x: x.to_python(), self.args)))
        return f"{self.v}.{self.method}({args})"

    pass

class Statement(Syntax):
    pass
    
class DesignOp(Statement):
    cn = __qualname__

    def __init__(self, d: Variable, op_name: str):
        super().__init__()
        self.d = d
        self.op_name = op_name

    @abc.abstractmethod
    def inverse(self) -> 'DesignOp':
        pass
    pass

class SetVariable(Statement):
    def __init__(self, x: Variable, expr: Expr):
        super().__init__()
        self.x = x
        self.expr = expr
        pass

    def to_python(self) -> str:
        return f"{self.x} = {self.expr}"


class AddMotif(DesignOp):
    cn = __qualname__

    def __init__(self, v: Variable, d: Variable, m: Expr, x: Expr, y: Expr, fresh: FreshVar):
        super().__init__(d, "add_motif")
        # where the placed motif is stored -- should be a fresh variable
        self.v = v
        # the motif to be added
        self.m = m
        # the x and y coordinates
        self.x = x
        self.y = y
        # source of fresh variable names
        self.fresh = fresh
        pass

    def inverse(self) -> DesignOp:
        return RemoveMotif(self.d, self.v, self.fresh)

    def to_python(self) -> str:
        return f"{self.v} = {self.d}.{self.op_name}({self.m}, {self.x}, {self.y})"

    pass

class RemoveMotif(DesignOp):
    def __init__(self, d: Variable, placedmotif: Variable, fresh: FreshVar):
        super().__init__(d, "remove_motif")
        # self.d = d
        self.placed_motif = placedmotif
        self.fresh = fresh
        pass

    def inverse(self) -> DesignOp:
        return AddMotif(Variable(self.fresh.get_fresh()),
                        self.d,
                        ObjectMethodCall(self.placed_motif, "motif"),
                        ObjectMethodCall(self.placed_motif, "x"),
                        ObjectMethodCall(self.placed_motif, "y"),
                        self.fresh)
    def to_python(self) -> str:
        return f"{self.d}.{self.op_name}({self.placed_motif})"
    pass


if __name__ == "__main__":
    c1 = Literal(1)
    c2 = Literal(3.0)
    c3 = Literal([1, 3.0])
    c4 = Literal([1, 1, 1])
    c5 = Literal("constant")

    fresh = FreshVar()
    
    c6 = AddMotif(Variable(fresh.get_fresh()), Variable(fresh.get_fresh()), Variable(fresh.get_fresh()), Literal(10), Literal(11), fresh)

    syntax = [c1, c2, c3, c4, c5, c6, c6.inverse(), c6.inverse().inverse()]

    for c in syntax:
        print(repr(c))
        print(c.to_python())
    
    
