import abc

# TODO: I think we would want to replace TypeGuard with TypeIs if we were all using Python 3.13...
from typing import Union, TypeGuard, Self, Optional, Type, Any, List
from types import ModuleType
from modularmotifs.core import Motif, Design, Color, CompositeMotif
from modularmotifs.core.design import PlacedMotif
import modularmotifs.motiflibrary.examples as libexamples

# from pathlib import Path


class FreshVar:
    """A source of fresh variable names"""

    def __init__(self, base_name="x", names_to_avoid: Optional[set[str]] = None):
        """Initialize a new FreshVar instance

        Args:
            base_name (str, optional): the prefix for variable names. Defaults to "x".
            names_to_avoid (Optional[set[str]], optional): a set of variable names to avoid (i.e., because it would result in overwriting a previously defined variable). Defaults to None.
        """
        self.current = 0
        self.base_name = base_name
        self.names_to_avoid = names_to_avoid
        pass

    def get_fresh(self) -> str:
        fresh = f"{self.base_name}{self.current}"
        self.current += 1
        if self.names_to_avoid:
            while fresh in self.names_to_avoid:
                fresh = f"{self.base_name}{self.current}"
                self.current += 1
                pass
            pass
        return fresh


class Syntax(abc.ABC):
    """An immutable type that represents the syntax of the DSL"""

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

    def __eq__(self, other: "Syntax"):
        # TODO: Find out what type other should have
        # if it returns the same code, it's the same
        return self.to_python() == other.to_python()

    def __hash__(self):
        # as a bare minimum, let's treat anything that returns the same code as the same
        return hash(self.to_python())

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
        return self.imported_module

    def to_python(self) -> str:
        as_clause = ""
        if self._as is not None:
            as_clause = f" as {self._as}"
            pass
        return f"import {self.imported_module}{as_clause}"

    pass


class FromImport(Import):
    imports: list[str]

    def __init__(self, mod: str, *imports):
        super().__init__(mod)
        self.imports = imports
        pass

    def to_python(self) -> str:
        return f"from {self.imported_module} import {", ".join(self.imports)}"


class Expr(Syntax):
    cn = __qualname__
    pass


primitive = Union[int, float, str]


class Literal(Expr):
    # cn = __qualname__
    def __init__(self, const: Union[primitive, list[Expr]]):
        super().__init__()
        self.const = const
        # if isinstance(const, primitive):
        #     print("primitive")
        #     pass
        # else:
        #     print("list")
        #     pass
        pass

    def is_int(self) -> TypeGuard[int]:
        return isinstance(self.const, int)

    def is_str(self) -> TypeGuard[str]:
        return isinstance(self.const, str)

    def is_float(self) -> TypeGuard[float]:
        return isinstance(self.const, float)

    def is_list(self) -> TypeGuard[list]:
        return isinstance(self.const, List)

    def __repr__(self) -> str:
        return f"{self.cn}({self.to_python()})"

    def to_python(self) -> str:
        if self.is_str():
            return '"' + self.const + '"'
        if self.is_list():
            print(self.const)
            return f"[{", ".join(list(map(lambda x: x.to_python(), self.const)))}]"
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

    def __str__(self) -> str:
        return self.to_python()


class ObjectInit(Expr):
    cn = __qualname__

    def __init__(self, className: str, *args: Expr):
        super().__init__()
        self.className = className
        self.args = args
        pass

    def to_python(self) -> str:
        args = ", ".join(list(map(lambda x: x.to_python(), self.args)))
        return f"{self.className}({args})"

    pass


class AttrAccess(Expr):
    def __init__(self, obj: Expr, key: Expr):
        super().__init__()
        self.obj = obj
        self.key = key
        pass

    def to_python(self) -> str:
        return f"{self.obj}[{self.key}]"

    pass


class ModuleRef(Expr):
    def __init__(self, module: str):
        super().__init__()
        self.module = module
        pass

    def to_python(self) -> str:
        return self.module


class ModuleAccess(Expr):
    def __init__(self, module: Expr, attr: str):
        super().__init__()
        self.module = module
        self.attr = attr
        pass

    def to_python(self) -> str:
        return f"{self.module.to_python()}.{self.attr}"


class ObjectAccess(Expr):
    def __init__(self, e: Expr, prop: str):
        super().__init__()
        self.e = e
        self.prop = prop
        pass

    def to_python(self) -> str:
        return f"{self.e}.{self.prop}"

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


class KeywordArg(Expr):
    def __init__(self, key: str, e: Expr):
        super().__init__()
        self.key = key
        self.e = e
        pass

    def to_python(self) -> str:
        return f"{self.key}={self.e.to_python()}"


class Statement(Syntax):
    pass
