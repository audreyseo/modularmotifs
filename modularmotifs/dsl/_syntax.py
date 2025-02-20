import abc
# TODO: I think we would want to replace TypeGuard with TypeIs if we were all using Python 3.13...
from typing import Union, TypeGuard, Self, Optional, Type
from types import ModuleType
from modularmotifs.core import Motif, Design
from modularmotifs.core.design import PlacedMotif
import modularmotifs.motiflibrary.examples as libexamples

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
    def __init__(self, mod: str, _as: Optional[str] = None):
        super().__init__()
        self.imported_module = mod
        self._as = _as
        pass

    def __repr__(self) -> str:
        return f"{self.cn}({self.imported_module})"

    def usename(self) -> str:
        if self._as:
            return self._as
        return self.mod

    def to_python(self) -> str:
        as_clause = ""
        if self._as is not None:
            as_clause = f" as {self._as}"
            pass
        return f"import {self.imported_module}{as_clause}"
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
    def __init__(self, className: str,  *args: Expr):
        super().__init__()
        self.className = className
        self.args = args
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

class DesignInterpreter:
    design: Design
    design_var: str
    _motifs: dict[str, Motif]
    _imports: list[Import]
    _placed_motifs: dict[str, PlacedMotif]
    _classes: set[str] = set([Motif.__name__, Design.__name__])

    def __init__(self, design: Design, design_var: str, motifs: dict[str, Motif], imports: list[Import]):
        self.cn = self.__class__.__qualname__
        self.design = design
        self.design_var = str
        self._motifs = motifs
        self._imports = imports
        self._placed_motifs = dict()
        
        pass

    def eval(self, e: Expr):
        def map_eval_over(itr: list[Expr]):
            return list(map(lambda x: self.eval(x), itr))
        
        if isinstance(e, Literal):
            return e.const
        if isinstance(e, Variable):
            n = e.name
            if n in self._motifs:
                return self._motifs[n]
            if n in self._placed_motifs:
                return self._placed_motifs[n]
            if n == self.design_var:
                return self.design
            assert False, f"{self.cn}.eval: no such name {n}"
            pass
        if isinstance(e, ObjectInit):
            assert e.className in self._classes, f"{self.cn}.eval: the class {e.className} is not supported for object initialization"
            args = map_eval_over(e.args)
            return eval(e.className)(*args)
            pass
        if isinstance(e, ObjectAccess):
            return getattr(self.eval(e.v), e.prop)
        if isinstance(e, ObjectMethodCall):
            args = map_eval_over(e.args)
            return getattr(self.eval(e.v), method)(*args)
        assert False, f"{self.cn}.eval: impossible kind of expr encountered '{e}'"

    def interpret(self, action: DesignOp):
        # TODO: Fix
        if isinstance(action, AddMotif):
            motif = self.eval(action.m)
            x = self.eval(action.x)
            y = self.eval(action.y)
            res = self.design.add_motif(motif, x, y)
            self._placed_motifs[action.v.name] = res
            return res
            pass
        pass
    

class DesignProgramBuilder:
    _imports: list[Import]
    _fresh: FreshVar
    _actions: list[DesignOp]
    _index: int

    _motifs: dict[str, Motif]
    _design_var: Variable
    cn: str = __qualname__
    base_design: Design
    

    def __init__(self, base_design: Design):
        self._imports = list()
        self._fresh = FreshVar()
        self._actions = list()
        self._index = -1
        self._design_var = self._get_fresh_var()
        self.base_design = base_design
        self._motifs = dict()
        pass

    def load_motif(self, name: str, m: Motif) -> Self:
        self._motifs[name] = m
        return self

    # def write(self, name

    def add_modularmotifs_motif_library(self) -> Self:
        print(libexamples.__name__)
        self.add_import(libexamples, _as="libexamples")

        for m in libexamples.motifs:
            self.load_motif(m, libexamples.motifs[m])
            pass
        
        return self

    def get_interpreter(self) -> DesignInterpreter:
        return DesignInterpreter(self.base_design, self._design_var.name, self._motifs, self._imports)

    def _get_fresh_var(self):
        return Variable(self._fresh.get_fresh())

    def add_import(self, m: ModuleType, _as: Optional[str] = None) -> Self:
        self._imports.append(Import(m.__name__, _as=_as))
        return self

    def _get_design_var(self) -> Variable:
        return self._design_var

    def get_latest_action(self) -> DesignOp:
        return self._actions[self._index]

    def _overwrite(self):
        """
        If at any point we add another action that overwrites past, undone actions, we overwrite the old history
        """
        if self._index < self.num_actions() - 1:
            self._actions = self._actions[:self_index + 1]
            pass
        pass
    

    def add_motif(self, name: str, x: int, y: int) -> DesignOp:
        assert name in self._motifs, f"{self.cn}.add_motif: could not find motif with name {name}, did you forget to load_motif it?"
        self._overwrite()
        self._actions.append(AddMotif(self._get_fresh_var(), self._design_var, Variable(name), Literal(x), Literal(y), self._fresh))
        self._index += 1
        return self._actions[self._index]

    def get_placed_motifs(self):
        placed_names = [a.v.name for a in self._actions if isinstance(a, AddMotif)]
        return placed_names

    def remove_motif(self, name: str) -> DesignOp:
        assert name in self.get_placed_motifs(), f"{self.cn}.remove_motif: could not find a placed motif with name {name}"
        self._overwrite()
        self._actions.append(RemoveMotif(Variable(name), self._fresh))
        self._index += 1
        return self._actions[self._index]

    def undo(self) -> Optional[DesignOp]:
        if self._index >= 0:
            old_index = self._index
            self._index -= 1
            return self._actions[old_index].inverse()
        return None

    def num_actions(self) -> int:
        return len(self._actions)

    def redo(self) -> Optional[DesignOp]:
        if self._index < self.num_actions() - 1:
            self._index += 1
            return self._actions[self._index]
        return None

    # def load_base_design(self) -> Self:
    #     # TODO: complete
    #     return self
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
        pass

    builder = DesignProgramBuilder(Design(10, 10))
    builder.add_modularmotifs_motif_library()
    interp = builder.get_interpreter()
    op = builder.add_motif("plus-3x3", 1, 1)
    
    print(op)
    res = interp.interpret(op)
    print(res)
    
    pass
